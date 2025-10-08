# backend/routes/divisions.py
from __future__ import annotations
from typing import List, Tuple, Optional

from flask import Blueprint, jsonify, request
from sqlalchemy import select, and_, delete, func
from sqlalchemy.orm import joinedload
from datetime import date as D, time as T  # 用于解析/构造日期时间

from db import SessionLocal
from models import Division, Team, TeamSeasonDivision, Match, Player, Season, MatchPlayerStats
bp = Blueprint("divisions", __name__, url_prefix="/api")

# ------------------ 圆圈法单循环 + 拉伸/裁剪到 11 轮 ------------------
def _round_robin_pairs(team_ids: List[int]) -> List[List[Tuple[Optional[int], Optional[int]]]]:
    teams = list(team_ids)
    if not teams:
        return []
    if len(teams) % 2 == 1:
        teams.append(None)  # BYE

    n = len(teams)
    half = n // 2
    arr = teams[:]
    rounds: List[List[Tuple[Optional[int], Optional[int]]]] = []

    for r in range(n - 1):
        pairs: List[Tuple[Optional[int], Optional[int]]] = []
        for i in range(half):
            a = arr[i]
            b = arr[n - 1 - i]
            if r % 2 == 0:
                pairs.append((a, b))
            else:
                pairs.append((b, a))
        rounds.append(pairs)
        arr = [arr[0]] + [arr[-1]] + arr[1:-1]
    return rounds

def _ensure_exact_rounds(
    base_rounds: List[List[Tuple[Optional[int], Optional[int]]]], target: int = 11
) -> List[List[Tuple[Optional[int], Optional[int]]]]:
    if not base_rounds and target > 0:
        return [[] for _ in range(target)]
    out = list(base_rounds)
    i = 0
    while len(out) < target and base_rounds:
        mirrored = [(b, a) for (a, b) in base_rounds[i]]
        out.append(mirrored)
        i = (i + 1) % len(base_rounds)
    return out[:target]

def _match_time_to_str(m: Match) -> Optional[str]:
    # 兼容老结构（如果以后有 scheduled_at 字段）
    val = getattr(m, "scheduled_at", None)
    if val is not None:
        try:
            return val.isoformat()
        except Exception:
            return str(val)
    # 正式使用 date + time
    if m.date and m.time:
        return f"{m.date.isoformat()} {m.time.strftime('%H:%M:%S')}"
    if m.date:
        return m.date.isoformat()
    if m.time:
        return m.time.strftime("%H:%M:%S")
    return None

# ------------------ 基础：分区/球队 ------------------
@bp.get("/divisions")
def list_divisions():
    with SessionLocal() as s:
        rows = s.execute(select(Division)).scalars().all()
        order = {"champion": 0, "d1": 1, "d2": 2}
        rows.sort(key=lambda d: (order.get(d.code, 99), d.id))
        return jsonify([{"id": d.id, "code": d.code, "name": d.name} for d in rows])

@bp.get("/divisions/<string:code>/teams")
def list_division_teams(code: str):
    season_id = request.args.get("season_id", type=int)
    if not season_id:
        return jsonify({"error": "season_id 参数必填"}), 400

    with SessionLocal() as s:
        div = s.execute(
            select(Division).where(func.lower(Division.code) == code.lower())
        ).scalar_one_or_none()
        if not div:
            return jsonify({"error": f"division '{code}' 不存在"}), 404

        q = (
            select(Team.id, Team.name, Team.logo_url)
            .join(TeamSeasonDivision, TeamSeasonDivision.team_id == Team.id)
            .where(
                and_(
                    TeamSeasonDivision.season_id == season_id,
                    TeamSeasonDivision.division_id == div.id,
                )
            )
            .order_by(Team.name.asc(), Team.id.asc())
        )
        rows = s.execute(q).all()
        return jsonify([{"id": r.id, "name": r.name, "logo_url": r.logo_url} for r in rows])

# ------------------ 赛程：读取/生成/清空（常规赛+季后赛） ------------------
@bp.get("/divisions/<string:code>/schedule")
def get_division_schedule(code: str):
    season_id = request.args.get("season_id", type=int)
    if not season_id:
        return jsonify({"error": "season_id is required"}), 400

    with SessionLocal() as s:
        div = s.execute(
            select(Division).where(func.lower(Division.code) == code.lower())
        ).scalar_one_or_none()
        if not div:
            return jsonify({"error": f"division '{code}' not found"}), 404

        # ------ Regular ------
        q_regular = (
            select(Match)
            .where(
                and_(
                    Match.season_id == season_id,
                    Match.division_id == div.id,
                    Match.stage == "regular",
                )
            )
            .order_by(Match.round_no.asc(), Match.id.asc())
        )
        ms_regular = s.execute(q_regular).scalars().all()

        reg_buckets: dict[int, list] = {}
        for m in ms_regular:
            rn = int(m.round_no or 0)
            reg_buckets.setdefault(rn, []).append({
                "id": m.id,
                "home_team_id": m.home_team_id if m.home_team_id is not None else -1,
                "away_team_id": m.away_team_id if m.away_team_id is not None else -1,
                "scheduled_at": _match_time_to_str(m),
                "venue": getattr(m, "venue", None),
            })
        regular = [{"round_no": k, "matches": reg_buckets[k]} for k in sorted(reg_buckets.keys())]

        # ------ Playoffs ------
        q_playoffs = (
            select(Match)
            .where(
                and_(
                    Match.season_id == season_id,
                    Match.division_id == div.id,
                    Match.stage == "playoff",
                )
            )
            .order_by(Match.round_no.asc(), Match.id.asc())
        )
        ms_playoffs = s.execute(q_playoffs).scalars().all()

        # 三个阶段：1/2/3 -> r1/r2/final（超过 3 轮则动态 r{n}）
        stage_map = {
            1: {"key": "r1",    "name": "Playoff Round 1", "matches": []},
            2: {"key": "r2",    "name": "Playoff Round 2", "matches": []},
            3: {"key": "final", "name": "Final",           "matches": []},
        }
        for m in ms_playoffs:
            rn = int(m.round_no or 0)
            bucket = stage_map.get(rn)
            if not bucket:
                bucket = stage_map[rn] = {"key": f"r{rn}", "name": f"Playoff Round {rn}", "matches": []}
            bucket["matches"].append({
                "id": m.id,
                "home_team_id": m.home_team_id if m.home_team_id is not None else -1,
                "away_team_id": m.away_team_id if m.away_team_id is not None else -1,
                "scheduled_at": _match_time_to_str(m),
                "venue": getattr(m, "venue", None),
            })

        playoffs = list(stage_map.values())
        playoffs.sort(key=lambda x: ({"r1": 1, "r2": 2, "final": 3}.get(x["key"], 99), x["key"]))

        return jsonify({"regular": regular, "playoffs": playoffs})

@bp.post("/divisions/<string:code>/schedule/generate")
def generate_regular_schedule(code: str):
    data = request.get_json(silent=True) or {}
    season_id = int(data.get("season_id") or 0)
    if not season_id:
        return jsonify({"error": "season_id 参数必填"}), 400

    SKIP_BYE = True  # True=不写入 BYE 对阵

    with SessionLocal() as s:
        div = s.execute(
            select(Division).where(func.lower(Division.code) == code.lower())
        ).scalar_one_or_none()
        if not div:
            return jsonify({"error": f"division '{code}' 不存在"}), 404

        rows = s.execute(
            select(Team.id)
            .join(TeamSeasonDivision, TeamSeasonDivision.team_id == Team.id)
            .where(
                and_(
                    TeamSeasonDivision.season_id == season_id,
                    TeamSeasonDivision.division_id == div.id,
                )
            )
            .order_by(Team.id.asc())
        ).all()
        team_ids = [r.id for r in rows]

        # 清空旧常规赛
        s.execute(
            delete(Match).where(
                and_(
                    Match.season_id == season_id,
                    Match.division_id == div.id,
                    Match.stage == "regular",
                )
            )
        )

        if len(team_ids) < 2:
            s.commit()
            return jsonify({"ok": True, "created": 0, "message": "参赛队不足 2 支，已清空常规赛"})

        base = _round_robin_pairs(team_ids)
        rounds = _ensure_exact_rounds(base, target=11)

        created = 0
        for round_no, pairs in enumerate(rounds, start=1):
            for (h, a) in pairs:
                if SKIP_BYE and (h is None or a is None):
                    continue
                s.add(
                    Match(
                        season_id=season_id,
                        division_id=div.id,
                        stage="regular",
                        round_no=round_no,
                        home_team_id=h,
                        away_team_id=a,
                    )
                )
                created += 1

        s.commit()
        return jsonify({"ok": True, "created": created, "rounds": len(rounds)})

@bp.delete("/divisions/<string:code>/schedule")
def clear_schedule(code: str):
    season_id = request.args.get("season_id", type=int)
    if not season_id:
        return jsonify({"error": "season_id 参数必填"}), 400

    with SessionLocal() as s:
        div = s.execute(
            select(Division).where(func.lower(Division.code) == code.lower())
        ).scalar_one_or_none()
        if not div:
            return jsonify({"error": f"division '{code}' 不存在"}), 404

        r = s.execute(
            delete(Match).where(
                and_(
                    Match.season_id == season_id,
                    Match.division_id == div.id,
                    Match.stage == "regular",
                )
            )
        )
        s.commit()
        return jsonify({"ok": True, "deleted": r.rowcount or 0})

# ------------------ 轮次详情（联表返回队名+Logo） ------------------
@bp.get("/divisions/<string:code>/rounds/<int:round_no>")
def get_division_round(code: str, round_no: int):
    """
    获取指定分区、指定轮次的所有比赛（含 home_team/away_team 的 name 和 logo_url）
    前端：GET /api/divisions/d1/rounds/1?season_id=1
    """
    season_id = request.args.get("season_id", type=int)
    if not season_id:
        return jsonify({"error": "season_id 参数必填"}), 400

    with SessionLocal() as s:
        div = s.execute(
            select(Division).where(func.lower(Division.code) == code.lower())
        ).scalar_one_or_none()
        if not div:
            return jsonify({"error": f"division '{code}' 不存在"}), 404

        q = (
            select(Match)
            .options(
                joinedload(Match.home_team),  # 预加载主队
                joinedload(Match.away_team),  # 预加载客队
            )
            .where(
                and_(
                    Match.season_id == season_id,
                    Match.division_id == div.id,
                    Match.stage == "regular",
                    Match.round_no == round_no,
                )
            )
            .order_by(Match.id.asc())
        )
        ms = s.execute(q).scalars().all()
        return jsonify([m.to_dict() for m in ms])

# —— 单场比赛：更新/删除 ————————————————————————————————————————
@bp.patch("/matches/<int:match_id>")
def update_match(match_id: int):
    """
    部分更新：date(YYYY-MM-DD), time(HH:MM[:SS]), venue, status,
            home_team_id, away_team_id 任选
    """
    data = request.get_json(silent=True) or {}
    with SessionLocal() as s:
        m = s.get(Match, match_id)
        if not m:
            return jsonify({"error": f"match {match_id} 不存在"}), 404

        if "date" in data:
            m.date = None if not data["date"] else __import__("datetime").date.fromisoformat(data["date"])
        if "time" in data:
            if not data["time"]:
                m.time = None
            else:
                hh, mm, *rest = str(data["time"]).split(":")
                ss = int(rest[0]) if rest else 0
                m.time = __import__("datetime").time(int(hh), int(mm), ss)
        if "venue" in data:
            m.venue = data["venue"] or None
        if "status" in data:
            m.status = str(data["status"] or "scheduled")

        if "home_team_id" in data:
            m.home_team_id = int(data["home_team_id"]) if data["home_team_id"] else None
        if "away_team_id" in data:
            m.away_team_id = int(data["away_team_id"]) if data["away_team_id"] else None

        s.commit()
        s.refresh(m)
        return jsonify(m.to_dict())

@bp.delete("/matches/<int:match_id>")
def delete_match(match_id: int):
    with SessionLocal() as s:
        m = s.get(Match, match_id)
        if not m:
            return jsonify({"error": f"match {match_id} 不存在"}), 404
        s.delete(m)
        s.commit()
        return jsonify({"ok": True, "deleted": match_id})

# —— 在指定分区/轮次下新增一场比赛（常规赛） ——————————————————————
@bp.post("/divisions/<string:code>/rounds/<int:round_no>/matches")
def create_match(code: str, round_no: int):
    """
    body: { season_id, home_team_id, away_team_id, date?, time?, venue? }
    """
    data = request.get_json(silent=True) or {}
    season_id = int(data.get("season_id") or 0)
    if not season_id:
        return jsonify({"error": "season_id 必填"}), 400
    home_team_id = data.get("home_team_id")
    away_team_id = data.get("away_team_id")
    if not home_team_id or not away_team_id:
        return jsonify({"error": "home_team_id/away_team_id 必填"}), 400

    with SessionLocal() as s:
        div = s.execute(
            select(Division).where(func.lower(Division.code) == code.lower())
        ).scalar_one_or_none()
        if not div:
            return jsonify({"error": f"division '{code}' 不存在"}), 404

        dt = data.get("date")
        tm = data.get("time")
        m = Match(
            season_id=season_id,
            division_id=div.id,
            stage="regular",
            round_no=round_no,
            home_team_id=int(home_team_id),
            away_team_id=int(away_team_id),
            date=D.fromisoformat(dt) if dt else None,
            time=(lambda hhmm: T(int(hhmm.split(':')[0]), int(hhmm.split(':')[1])) if tm else None)(tm),
            venue=(data.get("venue") or None),
        )
        s.add(m)
        s.commit()
        s.refresh(m)
        return jsonify(m.to_dict()), 201

# —— 新增季后赛一场比赛 ————————————————————————————————————————
@bp.post("/divisions/<string:code>/playoffs")
def create_playoff_match(code: str):
    """
    body:
    {
      season_id: int,
      round_no: 1|2|3,
      date: "YYYY-MM-DD",
      time: "HH:MM" | "HH:MM:SS",
      venue?: str,
      home_team_id: int,
      away_team_id: int,
      status?: "scheduled"|"ongoing"|"finished"
    }
    """
    data = request.get_json(silent=True) or {}

    season_id = int(data.get("season_id") or 0)
    round_no  = int(data.get("round_no")  or 0)
    home_id   = data.get("home_team_id")
    away_id   = data.get("away_team_id")
    date_str  = (data.get("date") or "").replace("/", "-")
    time_str  = data.get("time") or ""
    venue     = data.get("venue") or None
    status    = (data.get("status") or "scheduled").lower()

    if not season_id or not round_no or not home_id or not away_id:
        return jsonify({"error": "season_id, round_no, home_team_id, away_team_id are required"}), 400
    if str(home_id) == str(away_id):
        return jsonify({"error": "home_team_id and away_team_id cannot be the same"}), 400

    # 解析日期/时间（容错）
    dt = None
    tm = None
    if date_str:
        try:
            dt = D.fromisoformat(date_str)
        except Exception:
            return jsonify({"error": "invalid date format, expected YYYY-MM-DD"}), 400
    if time_str:
        if len(time_str) == 5:  # HH:MM -> HH:MM:00
            time_str += ":00"
        try:
            hh, mm, ss = [int(x) for x in time_str.split(":")]
            tm = T(hh, mm, ss)
        except Exception:
            return jsonify({"error": "invalid time format, expected HH:MM or HH:MM:SS"}), 400

    with SessionLocal() as s:
        div = s.execute(
            select(Division).where(func.lower(Division.code) == code.lower())
        ).scalar_one_or_none()
        if not div:
            return jsonify({"error": f"division '{code}' not found"}), 404

        m = Match(
            season_id   = season_id,
            division_id = div.id,
            stage       = "playoff",     # ✅ 季后赛
            round_no    = round_no,
            home_team_id= int(home_id),
            away_team_id= int(away_id),
            date        = dt,
            time        = tm,
            venue       = venue,
            status      = status,
        )
        s.add(m)
        s.commit()
        s.refresh(m)
        return jsonify({"id": m.id, "message": "created"}), 

# === 放在 backend/routes/divisions.py 顶部的 import 区域里，补充这几行 ===
from models import Player, Season, MatchPlayerStats  # 原文件已引入 Division/Team/Match 等

# === 放在 divisions.py 文件末尾，bp 已经是这个文件顶部定义的 Blueprint('/api') ===
@bp.get("/divisions/<string:code>/player-rankings")
def player_rankings(code: str):
    """
    Player rankings for a division (REGULAR season only, exclude playoffs).
    GET /api/divisions/<code>/player-rankings?season_id=1&top=10
    返回五个榜单：points / rebounds / assists / steals / blocks（总计、场次、场均）
    """
    from sqlalchemy import func, or_, and_, select

    top_n = request.args.get("top", type=int) or request.args.get("limit", type=int) or 10
    season_id = request.args.get("season_id", type=int)

    with SessionLocal() as s:
        # division
        div = s.execute(
            select(Division).where(func.lower(Division.code) == code.lower())
        ).scalar_one_or_none()
        if not div:
            return jsonify({"error": f"division '{code}' not found"}), 404

        # season：没传则取该分区最新有比赛的赛季
        if not season_id:
            season_id = (
                s.execute(
                    select(func.max(Match.season_id))
                    .where(Match.division_id == div.id)
                ).scalar()
                or s.execute(
                    select(func.max(TeamSeasonDivision.season_id))
                    .where(TeamSeasonDivision.division_id == div.id)
                ).scalar()
            )

        # 只算常规赛
        only_regular = or_(func.lower(Match.stage) == "regular", Match.stage.is_(None))

        # 关联常规赛比赛 + 个人技术统计
        mp = MatchPlayerStats
        m = Match

        q = (
            select(
                mp.player_id.label("player_id"),
                Player.name.label("player_name"),
                mp.team_id.label("team_id"),
                Team.name.label("team_name"),
                func.count(func.distinct(mp.match_id)).label("games"),
                func.coalesce(func.sum(mp.points), 0).label("PTS"),
                func.coalesce(func.sum(mp.rebounds), 0).label("REB"),
                func.coalesce(func.sum(mp.assists), 0).label("AST"),
                func.coalesce(func.sum(mp.steals), 0).label("STL"),
                func.coalesce(func.sum(mp.blocks), 0).label("BLK"),
            )
            .join(m, m.id == mp.match_id)
            .join(Player, Player.id == mp.player_id)
            .join(Team, Team.id == mp.team_id, isouter=True)
            .where(
                m.division_id == div.id,
                only_regular,
                m.home_team_id.isnot(None),
                m.away_team_id.isnot(None),
            )
            .group_by(mp.player_id, Player.name, mp.team_id, Team.name)
        )
        if season_id:
            q = q.where(or_(m.season_id == season_id, m.season_id.is_(None)))

        rows = s.execute(q).all()

        def take_top(metric_key: str):
            data = []
            for r in rows:
                games = int(r.games or 0)
                total = int(getattr(r, metric_key) or 0)
                per_game = (total / games) if games > 0 else 0.0
                data.append({
                    "player_id": int(r.player_id),
                    "player": r.player_name,
                    "team_id": (int(r.team_id) if r.team_id is not None else None),
                    "team": r.team_name,
                    "total": total,
                    "games": games,
                    "avg": round(per_game, 1),
                })
            # 排序规则：场均 ↓，总数 ↓，场次 ↑，名字
            data.sort(key=lambda x: (-x["avg"], -x["total"], x["games"], (x["player"] or "").lower()))
            # 排名并截断
            out = []
            for i, it in enumerate(data[:top_n], start=1):
                it2 = dict(it)
                it2["rank"] = i
                out.append(it2)
            return out

        payload = {
            "division": code,
            "season_id": season_id,
            "top": top_n,
            "points":   take_top("PTS"),
            "rebounds": take_top("REB"),
            "assists":  take_top("AST"),
            "steals":   take_top("STL"),
            "blocks":   take_top("BLK"),
        }
        return jsonify(payload)

