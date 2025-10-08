# backend/routes/ladder.py
from flask import Blueprint, jsonify, request
from sqlalchemy import func, case, or_, select
from db import get_session
from models import (
    Team,
    Division,
    Season,
    TeamSeasonDivision,
    Match,
    MatchPlayerStats,
)

ladder_api = Blueprint("ladder_api", __name__, url_prefix="/api")

# ---- 基础积分（可改） ----
POINTS_RULE = {"win": 3, "draw": 2, "loss": 1}


@ladder_api.get("/divisions/<code>/ladder")
@ladder_api.get("/divisions/<code>/ladder")
def get_ladder(code: str):
    """
    Ladder (只统计常规赛 regular)：
      - 胜平负根据比分判定（先用 matches，缺失用 stats 求和）
      - 不强依赖 status/stage，只要这场“常规赛”确实有得分
      - 轮空：常规赛总轮数 - 该队参与轮数 = byes；若 byes >= 2，第二次轮空加 2 分
    """
    debug_flag = request.args.get("debug") in ("1", "true", "yes")

    with get_session() as s:
        # 1) Division
        div = s.query(Division).filter(Division.code == code).first()
        if not div:
            return jsonify({"error": "Division not found"}), 404

        # 2) Season 选择
        season_arg = request.args.get("season")
        season_all = False
        season_id = None
        auto_mode = False

        if season_arg:
            if season_arg.lower() in ("all", "any", "*"):
                season_all = True
            else:
                season = s.query(Season).filter(Season.code == season_arg).first()
                if not season:
                    return jsonify({"error": "Season not found"}), 404
                season_id = season.id
        else:
            auto_mode = True
            season_id = (
                s.query(func.max(Match.season_id))
                 .filter(Match.division_id == div.id)
                 .scalar()
            )
            if season_id is None:
                season_id = (
                    s.query(func.max(TeamSeasonDivision.season_id))
                     .filter(TeamSeasonDivision.division_id == div.id)
                     .scalar()
                )

        # 3) 参赛队
        tsd = TeamSeasonDivision
        team_q = (
            s.query(Team.id, Team.name, Team.logo_url)
             .join(tsd, tsd.team_id == Team.id)
             .filter(tsd.division_id == div.id)
        )
        if (season_id is not None) and (not season_all):
            team_q = team_q.filter(tsd.season_id == season_id)
        team_rows = team_q.all()
        if not team_rows:
            season_code_res = None
            if (season_id is not None) and (not season_all):
                season_code_res = s.query(Season.code).filter(Season.id == season_id).scalar()
            payload = {
                "division": code,
                "season": ("all" if season_all else (season_code_res or season_arg)),
                "ladder": [],
            }
            if debug_flag:
                payload["debug"] = {"teams": 0}
            return jsonify(payload)

        tid_rows = (
            s.query(Team.id)
             .join(tsd, tsd.team_id == Team.id)
             .filter(tsd.division_id == div.id)
             .filter(True if season_all else (True if season_id is None else (tsd.season_id == season_id)))
             .all()
        )
        team_ids = [int(r[0]) for r in tid_rows]

        # 4) 参与比赛（基础过滤）
        m = Match
        involves = or_(m.home_team_id.in_(team_ids), m.away_team_id.in_(team_ids))
        base_filters = [involves]
        if not season_all and season_id is not None:
            if auto_mode:
                base_filters.append(or_(m.season_id == season_id, m.season_id.is_(None)))
            else:
                base_filters.append(m.season_id == season_id)

        # ⭐ 只统计常规赛
        regular_filter = or_(func.lower(m.stage) == "regular", m.stage.is_(None))
        filters_regular = base_filters + [regular_filter]

        # 5) 比分兜底（stats）
        pts = (
            s.query(
                MatchPlayerStats.match_id.label("mid"),
                MatchPlayerStats.team_id.label("tid"),
                func.coalesce(func.sum(MatchPlayerStats.points), 0).label("pts"),
            )
            .group_by(MatchPlayerStats.match_id, MatchPlayerStats.team_id)
            .subquery()
        )

        def team_pts_expr(team_id_col):
            return (
                select(pts.c.pts)
                .where(pts.c.mid == m.id, pts.c.tid == team_id_col)
                .scalar_subquery()
            )

        home_score = func.coalesce(m.home_score, func.coalesce(team_pts_expr(m.home_team_id), 0))
        away_score = func.coalesce(m.away_score, func.coalesce(team_pts_expr(m.away_team_id), 0))

        # 必须有真实得分（避免 0-0 当平局）
        valid_match = or_(m.home_score.isnot(None), m.away_score.isnot(None), (home_score + away_score) > 0)
        filters_with_valid_regular = filters_regular + [valid_match]

        # 6) 胜平负聚合（只看常规赛）
        home_rows = (
            s.query(
                m.home_team_id.label("team_id"),
                case((home_score > away_score, 1), else_=0).label("wins"),
                case((home_score == away_score, 1), else_=0).label("draws"),
                case((home_score < away_score, 1), else_=0).label("losses"),
                func.coalesce(home_score, 0).label("pf"),
                func.coalesce(away_score, 0).label("pa"),
            ).filter(*filters_with_valid_regular, m.home_team_id.isnot(None))
        )
        away_rows = (
            s.query(
                m.away_team_id.label("team_id"),
                case((away_score > home_score, 1), else_=0).label("wins"),
                case((away_score == home_score, 1), else_=0).label("draws"),
                case((away_score < home_score, 1), else_=0).label("losses"),
                func.coalesce(away_score, 0).label("pf"),
                func.coalesce(home_score, 0).label("pa"),
            ).filter(*filters_with_valid_regular, m.away_team_id.isnot(None))
        )

        match_count = s.query(func.count(m.id)).filter(*filters_with_valid_regular).scalar() or 0
        per_team = home_rows.union_all(away_rows).subquery()

        rows = (
            s.query(
                Team.id.label("team_id"),
                Team.name.label("team_name"),
                Team.logo_url.label("logo_url"),
                func.coalesce(func.sum(per_team.c.wins), 0).label("wins"),
                func.coalesce(func.sum(per_team.c.draws), 0).label("draws"),
                func.coalesce(func.sum(per_team.c.losses), 0).label("losses"),
                func.coalesce(func.sum(per_team.c.pf), 0).label("points_for"),
                func.coalesce(func.sum(per_team.c.pa), 0).label("points_against"),
            )
            .outerjoin(per_team, per_team.c.team_id == Team.id)
            .filter(Team.id.in_(team_ids))
            .group_by(Team.id, Team.name, Team.logo_url)
            .all()
        )

        # 7) —— 轮空规则（常规赛） —— #
        regular_stage = regular_filter
        round_filters = [regular_stage, involves, m.round_no.isnot(None)]
        if not season_all and season_id is not None:
            if auto_mode:
                round_filters.append(or_(m.season_id == season_id, m.season_id.is_(None)))
            else:
                round_filters.append(m.season_id == season_id)

        rounds_total = (
            s.query(func.count(func.distinct(m.round_no)))
             .filter(*round_filters)
             .scalar()
            or 0
        )

        home_r = (
            s.query(m.home_team_id.label("team_id"), m.round_no.label("round_no"))
             .filter(*round_filters, m.home_team_id.isnot(None))
        )
        away_r = (
            s.query(m.away_team_id.label("team_id"), m.round_no.label("round_no"))
             .filter(*round_filters, m.away_team_id.isnot(None))
        )
        rounds_per_team_sub = home_r.union_all(away_r).subquery()
        rounds_played_rows = (
            s.query(
                rounds_per_team_sub.c.team_id,
                func.count(func.distinct(rounds_per_team_sub.c.round_no)).label("played")
            )
            .group_by(rounds_per_team_sub.c.team_id)
            .all()
        )
        rounds_played = {int(tid): int(cnt) for tid, cnt in rounds_played_rows}

        # 8) 组装 + 轮空加分
        items = []
        debug_byes = {}

        for r in rows:
            wins   = int(r.wins or 0)
            draws  = int(r.draws or 0)
            losses = int(r.losses or 0)
            pf     = int(r.points_for or 0)
            pa     = int(r.points_against or 0)

            pts_total = (
                POINTS_RULE["win"]  * wins +
                POINTS_RULE["draw"] * draws +
                POINTS_RULE["loss"] * losses
            )

            played = rounds_played.get(int(r.team_id), 0)
            byes = max(0, rounds_total - played)
            bye_bonus = 2 if byes >= 2 else 0
            pts_total += bye_bonus

            items.append({
                "team_id": int(r.team_id),
                "name": r.team_name,
                "logo_url": r.logo_url,
                "wins": wins,
                "draws": draws,
                "losses": losses,
                "points": pts_total,
                "points_for": pf,
                "points_against": pa,
                "point_diff": pf - pa,
            })

            if debug_flag:
                debug_byes[int(r.team_id)] = {"played": played, "byes": byes, "bonus": bye_bonus}

        # 排序 & 排名
        items.sort(key=lambda x: (-x["points"], -x["point_diff"], -x["points_for"], x["name"].lower()))
        for i, it in enumerate(items, start=1):
            it["rank"] = i

        season_code_res = None
        if (season_id is not None) and (not season_all):
            season_code_res = s.query(Season.code).filter(Season.id == season_id).scalar()

        payload = {
            "division": code,
            "season": ("all" if season_all else (season_code_res or season_arg)),
            "ladder": items,
        }
        if debug_flag:
            payload["debug"] = {
                "team_ids": team_ids[:50],
                "match_count": int(match_count),
                "rounds_total": int(rounds_total),
                "byes": debug_byes,
                "season_id": (None if season_id is None else int(season_id)),
                "season_all": bool(season_all),
                "auto_mode": bool(auto_mode),
            }
        return jsonify(payload)
