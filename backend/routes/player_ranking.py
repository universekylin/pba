# backend/routes/player_ranking.py
from __future__ import annotations
from typing import Dict, Any, List

from flask import Blueprint, jsonify, request
from sqlalchemy import func, or_
from db import get_session
from models import (
    Division, Season, Team, TeamSeasonDivision,
    Match, MatchPlayerStats, Player
)

player_ranking_api = Blueprint("player_ranking_api", __name__, url_prefix="/api")

def _latest_regular_season_id(session, division_id: int):
    """优先取【常规赛】里最新的 season_id；取不到再退到所有比赛、再退到 TSD。"""
    m = Match
    regular_expr = func.lower(func.coalesce(m.stage, "regular")) == "regular"
    sid = (
        session.query(func.max(m.season_id))
        .filter(m.division_id == division_id)
        .filter(regular_expr)
        .scalar()
    )
    if sid is None:
        sid = (
            session.query(func.max(m.season_id))
            .filter(m.division_id == division_id)
            .scalar()
        )
    if sid is None:
        sid = (
            session.query(func.max(TeamSeasonDivision.season_id))
            .filter(TeamSeasonDivision.division_id == division_id)
            .scalar()
        )
    return sid


@player_ranking_api.get("/divisions/<string:code>/player-rankings")
def player_rankings(code: str):
    """
    公共排行榜（仅常规赛）：
      - champion: 5 项（points / rebounds / assists / steals / blocks）
      - d1 / d2: 仅 points（其他直接空数组）
    """
    topn = max(1, min(50, int(request.args.get("top", 10))))
    debug = request.args.get("debug") in ("1", "true", "yes")

    # 标准化 division code
    norm = (code or "").strip().lower()
    if norm in ("champ", "champion", "championship"):
        norm = "champion"
    elif norm in ("d1", "div1", "division1"):
        norm = "d1"
    elif norm in ("d2", "div2", "division2"):
        norm = "d2"

    only_points = norm in ("d1", "d2")

    with get_session() as s:
        # ===== Division =====
        div = s.query(Division).filter(func.lower(Division.code) == norm).first()
        if not div:
            return jsonify({"error": "division not found"}), 404

        # ===== Season =====
        season_arg = request.args.get("season")
        if season_arg:
            season = s.query(Season).filter(Season.code == season_arg).first()
            if not season:
                return jsonify({"error": "season not found"}), 404
            season_id = season.id
        else:
            season_id = _latest_regular_season_id(s, div.id)

        # ===== Teams in this division+season =====
        tsd = TeamSeasonDivision
        team_q = (
            s.query(Team.id)
            .join(tsd, tsd.team_id == Team.id)
            .filter(tsd.division_id == div.id)
        )
        if season_id is not None:
            team_q = team_q.filter(tsd.season_id == season_id)
        team_ids = [int(r[0]) for r in team_q.all()]

        # ===== Matches 过滤 =====
        m = Match
        regular_expr = func.lower(func.trim(func.coalesce(m.stage, "regular"))) == "regular"

        # 关键点：两条路都接受
        # A) 比赛记录里的 division_id 就是当前分区
        # B) 或者比赛是当前分区的队伍参与的（来自 TSD）
        involves_by_team = or_(m.home_team_id.in_(team_ids), m.away_team_id.in_(team_ids)) if team_ids else False
        matches_in_division = (m.division_id == div.id)
        scope_expr = or_(matches_in_division, involves_by_team)

        base_filters = [regular_expr, scope_expr]
        if season_id is not None:
            base_filters.append(or_(m.season_id == season_id, m.season_id.is_(None)))

        matches_count = s.query(func.count(m.id)).filter(*base_filters).scalar() or 0

        # ===== 聚合球员数据 =====
        ms = MatchPlayerStats
        joined = (
            s.query(
                ms.player_id.label("player_id"),
                ms.team_id.label("team_id"),
                func.count(func.distinct(ms.match_id)).label("games"),
                func.coalesce(func.sum(ms.points),   0).label("PTS"),
                func.coalesce(func.sum(ms.rebounds), 0).label("REB"),
                func.coalesce(func.sum(ms.assists),  0).label("AST"),
                func.coalesce(func.sum(ms.steals),   0).label("STL"),
                func.coalesce(func.sum(ms.blocks),   0).label("BLK"),
            )
            .join(m, m.id == ms.match_id)
            .filter(*base_filters)
            .group_by(ms.player_id, ms.team_id)
        ).subquery()

        rows = (
            s.query(
                joined.c.player_id,
                Player.name.label("player_name"),
                joined.c.team_id,
                Team.name.label("team_name"),
                Team.logo_url.label("logo_url"),
                joined.c.games,
                joined.c.PTS, joined.c.REB, joined.c.AST, joined.c.STL, joined.c.BLK,
            )
            .outerjoin(Player, Player.id == joined.c.player_id)
            .outerjoin(Team,   Team.id == joined.c.team_id)
            .all()
        )

        def make_board(metric_key: str) -> List[Dict[str, Any]]:
            items: List[Dict[str, Any]] = []
            for r in rows:
                total = int(getattr(r, metric_key) or 0)
                games = int(r.games or 0)
                if games <= 0 or total <= 0:
                    continue
                avg = total / games
                items.append({
                    "player_id": int(r.player_id) if r.player_id is not None else None,
                    "player": r.player_name or f"Player #{r.player_id}",
                    "team_id": int(r.team_id) if r.team_id is not None else None,
                    "team": r.team_name or "-",
                    "logo_url": r.logo_url,
                    "total": total,
                    "games": games,
                    "avg": round(avg, 1),
                })
            items.sort(key=lambda x: (-x["avg"], -x["total"], -x["games"], x["player"].lower()))
            for i, it in enumerate(items, start=1):
                it["rank"] = i
            return items[:topn]

        season_code = s.query(Season.code).filter(Season.id == season_id).scalar() if season_id else None

        payload = {
            "division": norm,
            "season": season_code,
            "top": {
                "points":   make_board("PTS"),
                "rebounds": [] if only_points else make_board("REB"),
                "assists":  [] if only_points else make_board("AST"),
                "steals":   [] if only_points else make_board("STL"),
                "blocks":   [] if only_points else make_board("BLK"),
            },
        }
        if debug:
            payload["debug"] = {
                "division_id": int(div.id),
                "season_id": None if season_id is None else int(season_id),
                "matches_count": int(matches_count),
                "teams_in_division": team_ids[:50],
                "row_count_after_join": len(rows),
            }
        return jsonify(payload)
