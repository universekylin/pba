# backend/routes/teams.py
from __future__ import annotations

import os
from datetime import datetime, date, time as dtime, timedelta
from typing import Tuple, Optional

from flask import Blueprint, jsonify, request
from sqlalchemy import text

from db import SessionLocal

bp = Blueprint("teams", __name__, url_prefix="/api/teams")

# -----------------------------
# 工具：赛季 code -> id
# -----------------------------
def get_season_id(s, code: Optional[str]):
    if not code:
        return None
    row = s.execute(text("SELECT id FROM seasons WHERE code = :c"), {"c": code}).first()
    return row[0] if row else None

# -----------------------------
# Division 归一
# -----------------------------
def normalize_div_code(code: Optional[str]) -> Optional[str]:
    v = (code or "").strip().lower()
    if v in ("d1", "division 1", "1"):
        return "d1"
    if v in ("d2", "division 2", "2"):
        return "d2"
    if v in ("champion", "champ", "c", "冠军"):
        return "champion"
    return v or None

def div_label(code: Optional[str]) -> Optional[str]:
    return {"d1": "Division 1", "d2": "Division 2", "champion": "Champion"}.get(code, code)

# -----------------------------
# 某队在某赛季（或最近赛季）的 division
# -----------------------------
def get_division_for_team(s, team_id: int, season_code: Optional[str]) -> Tuple[Optional[str], Optional[str]]:
    # 指定赛季
    if season_code:
        season_id = get_season_id(s, season_code)
        if season_id:
            row = s.execute(
                text("""
                    SELECT d.code
                    FROM team_season_division tsd
                    JOIN divisions d ON d.id = tsd.division_id
                    WHERE tsd.team_id = :tid AND tsd.season_id = :sid
                    LIMIT 1
                """),
                {"tid": team_id, "sid": season_id}
            ).first()
            code = normalize_div_code(row[0]) if row else None
            return code, season_code

    # 最近赛季
    row = s.execute(
        text("""
            SELECT d.code, s.code AS season_code
            FROM team_season_division tsd
            JOIN divisions d ON d.id = tsd.division_id
            JOIN seasons   s ON s.id = tsd.season_id
            WHERE tsd.team_id = :tid
            ORDER BY tsd.season_id DESC
            LIMIT 1
        """),
        {"tid": team_id}
    ).first()
    if row:
        return normalize_div_code(row[0]), row[1]
    return None, None

# -----------------------------
# 联盟“当前时间”（用环境变量的分钟偏移校准：UTC+10=600，UTC+8=480）
# -----------------------------
# 联盟“当前时间”：
# - 若设置了 LEAGUE_TZ_OFFSET_MIN（单位：分钟，UTC+8=480），用 UTC+偏移
# - 否则兜底用服务器本地时间（datetime.now()），避免没配环境变量时落到 UTC
def league_now() -> datetime:
    v = os.getenv("LEAGUE_TZ_OFFSET_MIN", "").strip()
    if not v:                               # 没配环境变量 → 用本地时间兜底
        return datetime.now()
    try:
        return datetime.utcnow() + timedelta(minutes=int(v))
    except Exception:
        return datetime.now()


# -----------------------------
# 统一的比赛状态计算（服务端判定）
# - 返回: 'scheduled' | 'ongoing' | 'finished'
# -----------------------------
KNOWN_DONE = {"finished", "final", "done"}
KNOWN_LIVE = {"ongoing", "live"}
KNOWN_SCHED = {"scheduled", "not started", ""}

def _to_dt(local_date, local_time) -> Optional[datetime]:
    """把 DB 里的 date/time（或字符串）拼成一个**联盟本地** naive datetime。"""
    if local_date is None and local_time is None:
        return None
    try:
        d: Optional[date]
        t: Optional[dtime]
        # date
        if isinstance(local_date, date):
            d = local_date
        elif isinstance(local_date, str) and local_date:
            d = datetime.strptime(local_date, "%Y-%m-%d").date()
        else:
            d = None
        # time
        if isinstance(local_time, dtime):
            t = local_time
        elif isinstance(local_time, str) and local_time:
            fmt = "%H:%M:%S" if len(local_time.split(":")) == 3 else "%H:%M"
            t = datetime.strptime(local_time, fmt).time()
        else:
            t = None

        if d and t:
            return datetime.combine(d, t)     # 视为联盟本地时间
        if d and not t:
            return datetime.combine(d, dtime(0, 0, 0))
        if t and not d:
            today = league_now().date()
            return datetime.combine(today, t)
    except Exception:
        return None
    return None

def compute_status(raw_status: Optional[str],
                   match_date,
                   match_time,
                   home_pts: int,
                   away_pts: int,
                   ongoing_window_minutes: int = 60) -> str:
    """
    规则：
    1) 原始状态 finished/final/done => finished
    2) 原始状态 ongoing/live        => ongoing
    3) 若时间缺失（date 或 time 任一为空）=> scheduled
    4) 否则根据联盟时间判断（now = UTC + 偏移），开球后 <= 60 分钟算 Ongoing：
       - now < start                           => scheduled
       - start <= now <= start+ongoing_window  => ongoing
       - now > start+window                    => finished
    """
    v = (raw_status or "").strip().lower()
    if v in KNOWN_DONE:
        return "finished"
    if v in KNOWN_LIVE:
        return "ongoing"

    start_dt = _to_dt(match_date, match_time)
    if start_dt is None:
        return "scheduled"

    now = league_now()
    if now < start_dt:
        return "scheduled"

    window_end = start_dt + timedelta(minutes=ongoing_window_minutes)
    if now <= window_end:
        return "ongoing"

    return "finished"

# -----------------------------
# GET: 球队列表 (?season=2025-S8)
# -----------------------------
@bp.get("")
def list_teams():
    season_code = request.args.get("season")
    with SessionLocal() as s:
        if season_code:
            season_id = get_season_id(s, season_code)
            if not season_id:
                return jsonify([])

            sql = text("""
                SELECT
                  t.id,
                  t.name,
                  t.logo_url,
                  CASE
                    WHEN LOWER(d.code) IN ('d1','division 1','1') THEN 'D1'
                    WHEN LOWER(d.code) IN ('d2','division 2','2') THEN 'D2'
                    WHEN LOWER(d.code) IN ('champion','c','冠军') THEN 'champion'
                    ELSE d.code
                  END AS division,
                  t.note
                FROM team_season_division tsd
                JOIN teams t     ON t.id = tsd.team_id
                JOIN divisions d ON d.id = tsd.division_id
                WHERE tsd.season_id = :sid
                ORDER BY t.id ASC
            """)
            rows = s.execute(sql, {"sid": season_id}).mappings().all()
            return jsonify([dict(r) for r in rows])

        rows = s.execute(
            text("SELECT id, name, logo_url, NULL AS division, note FROM teams ORDER BY id ASC")
        ).mappings().all()
        return jsonify([dict(r) for r in rows])

# -----------------------------
# GET: 单队（可带 ?season=）
# -----------------------------
@bp.get("/<int:team_id>")
def get_team(team_id: int):
    season_code = request.args.get("season")
    with SessionLocal() as s:
        row = s.execute(
            text("SELECT id, name, logo_url, note FROM teams WHERE id = :id"),
            {"id": team_id}
        ).mappings().first()
        if not row:
            return jsonify({"error": "Team not found"}), 404

        data = dict(row)
        code, scode = get_division_for_team(s, team_id, season_code)
        data["division"] = {
            "code": code,
            "name": div_label(code),
            "season": scode
        } if code else None
        return jsonify(data)

# -----------------------------
# POST: 新增球队 + 映射
# -----------------------------
@bp.post("")
def create_team():
    data = request.get_json(silent=True) or {}

    raw_name = data.get("name")
    name = str(raw_name).strip() if raw_name is not None else ""
    division_code = (data.get("division") or "").strip()
    season_code = (data.get("season") or "").strip()
    note = data.get("note")
    logo_url = data.get("logo_url")

    if not name or not division_code or not season_code:
        return jsonify({"error": "name/season/division cannot be empty"}), 400

    with SessionLocal() as s:
        season_id = get_season_id(s, season_code)
        if not season_id:
            return jsonify({"error": "season not found"}), 400

        drow = s.execute(text("SELECT id FROM divisions WHERE code = :c"), {"c": division_code}).first()
        if not drow:
            return jsonify({"error": "division not found"}), 400
        division_id = drow[0]

        trow = s.execute(text("SELECT id FROM teams WHERE name = :n"), {"n": name}).first()
        if trow:
            team_id = trow[0]
            s.execute(
                text("UPDATE teams SET logo_url = :logo, note = :note WHERE id = :id"),
                {"logo": logo_url, "note": note, "id": team_id}
            )
        else:
            ins = s.execute(
                text("INSERT INTO teams (name, logo_url, note) VALUES (:n,:l,:no)"),
                {"n": name, "l": logo_url, "no": note}
            )
            team_id = ins.lastrowid

        s.execute(text("""
            INSERT INTO team_season_division (season_id, division_id, team_id)
            VALUES (:sid, :did, :tid)
            ON DUPLICATE KEY UPDATE division_id = VALUES(division_id)
        """), {"sid": season_id, "did": division_id, "tid": team_id})

        s.commit()
        return jsonify({
            "id": team_id,
            "name": name,
            "logo_url": logo_url,
            "division": division_code,
            "note": note
        }), 201

# -----------------------------
# PATCH: 更新球队 + 映射 UPSERT
# -----------------------------
@bp.patch("/<int:team_id>")
def update_team(team_id: int):
    data = request.get_json(silent=True) or {}
    name = data.get("name")
    division_code = data.get("division")
    season_code = data.get("season")
    logo_url = data.get("logo_url")

    if not any([name, division_code, logo_url, season_code]):
        return jsonify({"error": "No fields to update"}), 400

    with SessionLocal() as s:
        fields, params = [], {"id": team_id}
        if name:
            fields.append("name = :name")
            params["name"] = name.strip()
        if logo_url:
            fields.append("logo_url = :logo_url")
            params["logo_url"] = logo_url
        if fields:
            s.execute(text(f"UPDATE teams SET {', '.join(fields)} WHERE id = :id"), params)

        if division_code and season_code:
            season_id = get_season_id(s, season_code)
            if not season_id:
                return jsonify({"error": "season not found"}), 400
            drow = s.execute(text("SELECT id FROM divisions WHERE code = :c"), {"c": division_code}).first()
            if not drow:
                return jsonify({"error": "division not found"}), 400
            division_id = drow[0]
            s.execute(text("""
                INSERT INTO team_season_division (season_id, division_id, team_id)
                VALUES (:sid, :did, :tid)
                ON DUPLICATE KEY UPDATE division_id = VALUES(division_id)
            """), {"sid": season_id, "did": division_id, "tid": team_id})

        s.commit()
        return jsonify({"ok": True, "message": "updated"})

# -----------------------------
# DELETE: 删除
# -----------------------------
@bp.delete("/<int:team_id>")
def delete_team(team_id: int):
    with SessionLocal() as s:
        r = s.execute(text("DELETE FROM teams WHERE id = :id"), {"id": team_id})
        s.commit()
        if r.rowcount == 0:
            return jsonify({"error": "Team not found"}), 404
        return jsonify({"ok": True})

# =========================================================
# 公开接口 - 球队赛程
# =========================================================
@bp.get("/<int:team_id>/schedule")
def team_schedule(team_id: int):
    r_from = request.args.get("from", default=1, type=int)
    r_to   = request.args.get("to",   default=11, type=int)
    season_code = request.args.get("season")
    use_raw = request.args.get("use_raw", default=0, type=int)   # 1=直接用DB原始status

    def date_to_str(v):
        if v is None:
            return None
        if hasattr(v, "isoformat"):
            return v.isoformat()
        return str(v)

    def time_to_str(v):
        if v is None:
            return None
        if hasattr(v, "isoformat"):
            return v.isoformat()
        try:
            total = int(v.total_seconds())
            hh = total // 3600
            mm = (total % 3600) // 60
            ss = total % 60
            return f"{hh:02d}:{mm:02d}:{ss:02d}"
        except Exception:
            return str(v)

    def has_column(session, table: str, col: str) -> bool:
        try:
            row = session.execute(text(f"SHOW COLUMNS FROM {table} LIKE :c"), {"c": col}).first()
            return bool(row)
        except Exception:
            return False

    with SessionLocal() as s:
        try:
            trow = s.execute(
                text("SELECT id, name, logo_url FROM teams WHERE id = :tid"),
                {"tid": team_id}
            ).mappings().first()
            team_data = dict(trow) if trow else None

            div_code, div_season = get_division_for_team(s, team_id, season_code)

            court_col = None
            for c in ("court_no", "court", "court_num", "courtid", "court_id"):
                if has_column(s, "matches", c):
                    court_col = c
                    break
            venue_col = None
            for c in ("venue", "place", "location", "gym", "stadium"):
                if has_column(s, "matches", c):
                    venue_col = c
                    break

            court_sql = f"m.{court_col} AS court_no," if court_col else "NULL AS court_no,"
            venue_sql = f"m.{venue_col} AS venue,"   if venue_col else "NULL AS venue,"

            sql = text(f"""
                SELECT
                  m.id, m.round_no, m.stage, m.status, m.date, m.time,
                  {court_sql}
                  {venue_sql}
                  m.home_team_id, m.away_team_id,
                  COALESCE(
                    (SELECT SUM(s.points) FROM match_player_stats s
                      WHERE s.match_id = m.id AND s.team_id = m.home_team_id),
                    m.home_score, 0) AS home_pts,
                  COALESCE(
                    (SELECT SUM(s.points) FROM match_player_stats s
                      WHERE s.match_id = m.id AND s.team_id = m.away_team_id),
                    m.away_score, 0) AS away_pts,
                  th.id AS home_id, th.name AS home_name, th.logo_url AS home_logo,
                  ta.id AS away_id, ta.name AS away_name, ta.logo_url AS away_logo
                FROM matches m
                LEFT JOIN teams th ON th.id = m.home_team_id
                LEFT JOIN teams ta ON ta.id = m.away_team_id
                WHERE (m.home_team_id = :tid OR m.away_team_id = :tid)
                  AND (m.round_no BETWEEN :r1 AND :r2)
                ORDER BY m.round_no ASC, m.id ASC
            """)
            rows = s.execute(sql, {"tid": team_id, "r1": r_from, "r2": r_to}).mappings().all()

            matches = []
            for r in rows:
                is_home = (r["home_team_id"] == team_id)

                # 原始 DB 状态
                raw_db_status = (r["status"] or "").strip()

                # 服务端统一状态（带时区 & 60分钟窗口）
                normalized_status = compute_status(
                    raw_status=raw_db_status,
                    match_date=r["date"],
                    match_time=r["time"],
                    home_pts=int(r["home_pts"] or 0),
                    away_pts=int(r["away_pts"] or 0),
                    ongoing_window_minutes=60,
                )

                final_status = raw_db_status if use_raw == 1 else normalized_status

                matches.append({
                    "id": r["id"],
                    "round_no": r["round_no"],
                    "stage": r["stage"],
                    "status": final_status,          # 前端显示用这个
                    "raw_status": raw_db_status,     # 调试可见
                    "date": date_to_str(r["date"]),
                    "time": time_to_str(r["time"]),
                    "court_no": r.get("court_no"),
                    "venue": r.get("venue"),
                    "home_score": int(r["home_pts"] or 0),
                    "away_score": int(r["away_pts"] or 0),
                    "home_team": {
                        "id": r["home_id"], "name": r["home_name"], "logo_url": r["home_logo"]
                    },
                    "away_team": {
                        "id": r["away_id"], "name": r["away_name"], "logo_url": r["away_logo"]
                    },
                    "is_home": is_home,
                    "opponent": {
                        "id": (r["away_id"] if is_home else r["home_id"]),
                        "name": (r["away_name"] if is_home else r["home_name"]) or "TBD",
                        "logo_url": (r["away_logo"] if is_home else r["home_logo"]),
                    }
                })

            return jsonify({
                "team": team_data,
                "division": {
                    "code": div_code,
                    "name": div_label(div_code),
                    "season": div_season
                } if div_code else None,
                "matches": matches
            })
        except Exception as e:
            print("Failed to fetch team schedule:", e)
            return jsonify({"ok": False, "error": "Failed to fetch schedule"}), 500
