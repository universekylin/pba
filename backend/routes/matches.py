from __future__ import annotations
from typing import List, Dict, Any, Optional
from datetime import datetime, time as dt_time, timedelta

from flask import Blueprint, jsonify, request
from sqlalchemy import select, and_, text
from sqlalchemy.orm import joinedload

from db import SessionLocal
from models import Match, Team, Player, MatchPlayerStats

bp = Blueprint("matches_api", __name__, url_prefix="/api/matches")

# ---------- helpers ----------
# 增加三列 *_pt_made，前端才能拿到 1/2/3 分
FIELDS = (
    "points", "rebounds", "steals", "assists", "blocks", "fouls",
    "one_pt_made", "two_pt_made", "three_pt_made",
)

FINAL_SET = {"final", "finished", "done"}
LIVE_SET  = {"live", "ongoing"}

def compute_match_status(d: Optional[datetime.date],
                         t: Optional[datetime.time],
                         raw_status: Optional[str],
                         live_window_min: int = 60) -> str:
    """
    统一赛况判定：
      - raw_status 在 final/done 或 live/ongoing 时优先返回（尊重人工设置）
      - 否则按时间推断：
          now < start_time            -> upcoming
          start_time <= now <= +60min -> ongoing
          now > start_time + 60min    -> final
    """
    v = (raw_status or "").strip().lower()
    if v in FINAL_SET:
        return "final"
    if v in LIVE_SET:
        return "ongoing"

    if not d and not t:
        # 没有时间信息，尽量保持原值/兜底
        return v or "upcoming"

    # 补齐 time（若没有就当 00:00）
    if not t:
        t = dt_time(0, 0, 0)
    try:
        start = datetime.combine(d, t)
        now = datetime.now()
        if now < start:
            return "upcoming"
        if now <= start + timedelta(minutes=live_window_min):
            return "ongoing"
        return "final"
    except Exception:
        return v or "upcoming"


def team_dict(t: Team) -> Dict[str, Any]:
    if not t:
        return {}
    return {"id": t.id, "name": t.name, "logo_url": t.logo_url}

def player_base(p: Player) -> Dict[str, Any]:
    return {"id": p.id, "name": p.name, "number": p.number or 0, "team_id": p.team_id}

def stat_zero() -> Dict[str, int]:
    return {k: 0 for k in FIELDS}

def has_column(session, table: str, col: str) -> bool:
    try:
        row = session.execute(text(f"SHOW COLUMNS FROM {table} LIKE :c"), {"c": col}).first()
        return bool(row)
    except Exception:
        return False

# ---------- 1) GET lineup + per-game stats ----------
@bp.get("/<int:match_id>/lineup")
def get_match_lineup(match_id: int):
    """
    Response:
    {
      "match": {... date, time, venue, court_no, status ...},
      "home": {"team": {...}, "players": [ {player + stats}, ... ]},
      "away": {"team": {...}, "players": [...]}
    }
    """
    with SessionLocal() as s:
        m: Match | None = (
            s.execute(
                select(Match)
                .options(
                    joinedload(Match.home_team),
                    joinedload(Match.away_team),
                )
                .where(Match.id == match_id)
            ).scalars().first()
        )
        if not m:
            return jsonify({"error": "match not found"}), 404

        # detect court/venue columns if needed
        court_no = None
        venue = getattr(m, "venue", None)
        for c in ("court_no", "court", "court_num"):
            if hasattr(m, c) and getattr(m, c) is not None:
                court_no = getattr(m, c); break
        if venue is None:
            with SessionLocal() as s2:
                if has_column(s2, "matches", "venue"):
                    venue = s2.execute(text("SELECT venue FROM matches WHERE id=:id"), {"id": m.id}).scalar()

        # rosters
        home_players: List[Player] = []
        away_players: List[Player] = []
        if m.home_team_id:
            home_players = s.execute(
                select(Player).where(Player.team_id == m.home_team_id).order_by(Player.number.asc(), Player.id.asc())
            ).scalars().all()
        if m.away_team_id:
            away_players = s.execute(
                select(Player).where(Player.team_id == m.away_team_id).order_by(Player.number.asc(), Player.id.asc())
            ).scalars().all()

        # per-game stats
        stats_rows = s.execute(
            select(MatchPlayerStats).where(MatchPlayerStats.match_id == match_id)
        ).scalars().all()
        stats_map: Dict[int, MatchPlayerStats] = {r.player_id: r for r in stats_rows}

        def attach(players: List[Player]) -> List[Dict[str, Any]]:
            out = []
            for p in players:
                st = stats_map.get(p.id)
                row = {
                    **player_base(p),
                    **(stat_zero() if not st else {
                        "points":   st.points,
                        "rebounds": st.rebounds,
                        "steals":   st.steals,
                        "assists":  st.assists,
                        "blocks":   st.blocks,
                        "fouls":    st.fouls,
                        # 1/2/3 分
                        "one_pt_made":   getattr(st, "one_pt_made", 0),
                        "two_pt_made":   getattr(st, "two_pt_made", 0),
                        "three_pt_made": getattr(st, "three_pt_made", 0),
                        # 兼容别名
                        "one_points":    getattr(st, "one_pt_made", 0),
                        "two_points":    getattr(st, "two_pt_made", 0),
                        "three_points":  getattr(st, "three_pt_made", 0),
                    }),
                }
                out.append(row)
            return out

        computed_status = compute_match_status(
            getattr(m, "date", None),
            getattr(m, "time", None),
            getattr(m, "status", None),
            live_window_min=60,
        )

        resp = {
            "match": {
                "id": m.id,
                "date": m.date.isoformat() if getattr(m, "date", None) else None,
                "time": (m.time.strftime("%H:%M:%S") if getattr(m, "time", None) else None),
                "venue": venue,
                "court_no": court_no,
                "status": computed_status,   # ✅ 用统一计算后的状态
                "home_team": team_dict(m.home_team),
                "away_team": team_dict(m.away_team),
            },
            "home": {"team": team_dict(m.home_team), "players": attach(home_players)},
            "away": {"team": team_dict(m.away_team), "players": attach(away_players)},
        }
        return jsonify(resp)

# ---------- 2) batch upsert ----------
@bp.post("/<int:match_id>/stats/batch-upsert")
def batch_upsert_stats(match_id: int):
    """
    body: { items: [ {player_id, team_id, points, rebounds, steals, assists, blocks, fouls, one_pt_made, two_pt_made, three_pt_made}, ... ] }
    """
    data = request.get_json(silent=True) or {}
    items = data.get("items") or []
    if not isinstance(items, list):
        return jsonify({"ok": False, "error": "items must be a list"}), 400

    with SessionLocal() as s:
        for it in items:
            pid = int(it.get("player_id") or 0)
            tid = int(it.get("team_id") or 0)
            if not pid or not tid:
                continue

            row: MatchPlayerStats | None = s.execute(
                select(MatchPlayerStats).where(
                    and_(
                        MatchPlayerStats.match_id == match_id,
                        MatchPlayerStats.player_id == pid,
                    )
                )
            ).scalars().first()

            values = {k: int(it.get(k) or 0) for k in FIELDS}
            if row:
                for k, v in values.items():
                    setattr(row, k, v)
            else:
                s.add(MatchPlayerStats(
                    match_id=match_id,
                    player_id=pid,
                    team_id=tid,
                    **values
                ))
        s.commit()
        return jsonify({"ok": True})

# ---------- 3) increment one field ----------
@bp.post("/<int:match_id>/stats/incr")
def incr_stat(match_id: int):
    """
    body: { player_id, team_id (optional), field, delta }   # delta: +1 / -1
    field 可为 points/…/fouls 以及 one_pt_made/two_pt_made/three_pt_made
    """
    data = request.get_json(silent=True) or {}
    pid = int(data.get("player_id") or 0)
    tid = data.get("team_id")
    field = str(data.get("field") or "").lower()
    delta = int(data.get("delta") or 0)

    if not pid or field not in FIELDS or delta == 0:
        return jsonify({"ok": False, "error": "invalid params"}), 400

    with SessionLocal() as s:
        row: MatchPlayerStats | None = s.execute(
            select(MatchPlayerStats).where(
                and_(
                    MatchPlayerStats.match_id == match_id,
                    MatchPlayerStats.player_id == pid,
                )
            )
        ).scalars().first()

        # create row if missing
        if not row:
            if not tid:
                pl = s.execute(select(Player).where(Player.id == pid)).scalars().first()
                if not pl:
                    return jsonify({"ok": False, "error": "player not found"}), 404
                tid = pl.team_id
            row = MatchPlayerStats(
                match_id=match_id, player_id=pid, team_id=int(tid or 0), **{k: 0 for k in FIELDS}
            )
            s.add(row)
            s.flush()

        newv = max(0, int(getattr(row, field)) + delta)
        setattr(row, field, newv)
        s.commit()
        return jsonify({"ok": True, "value": newv})

# ---------- 4) compatibility: GET /api/matches/<id> ----------
@bp.get("/<int:match_id>")
def get_match_root(match_id: int):
    """Return the same structure as /lineup for the main GET."""
    return get_match_lineup(match_id)
