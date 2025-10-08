from __future__ import annotations
from flask import Blueprint, jsonify, request
from sqlalchemy import text
from db import SessionLocal

bp = Blueprint("match_stats", __name__, url_prefix="/api/matches")

def nz(x, default=0):
    try:
        return int(x)
    except Exception:
        return default

def pick(data: dict, keys: list[str], default=None):
    for k in keys:
        if k in data and data[k] is not None:
            return data[k]
    return default

def has_col(s, table: str, col: str) -> bool:
    try:
        row = s.execute(text(f"SHOW COLUMNS FROM {table} LIKE :c"), {"c": col}).first()
        return bool(row)
    except Exception:
        return False

@bp.post("/<int:match_id>/player-stats")
def upsert_player_stats(match_id: int):
    """
    兼容多种前端字段：
    - 1分:  one_pt_made / one_points / ones / p1
    - 2分:  two_pt_made / two_points / twos / p2
    - 3分:  three_pt_made / three_points / threes / p3
    其它：points / rebounds / assists / steals / blocks / fouls / number / name
    最终写库字段：points, rebounds, assists, steals, blocks, fouls,
               one_pt_made, two_pt_made, three_pt_made
    """
    data = request.get_json(silent=True) or {}

    player_id = data.get("player_id")
    team_id   = data.get("team_id")
    if not match_id or not player_id:
        return jsonify({"error": "match_id/player_id required"}), 400

    # 读取三类得分（兼容不同命名）
    p1 = nz(pick(data, ["one_pt_made", "one_points", "ones", "p1"], 0))
    p2 = nz(pick(data, ["two_pt_made", "two_points", "twos", "p2"], 0))
    p3 = nz(pick(data, ["three_pt_made", "three_points", "threes", "p3"], 0))

    # points 如果没传则用 1/2/3 分计算
    points = pick(data, ["points", "pts"])
    if points is None:
        points = 1 * p1 + 2 * p2 + 3 * p3
    points = nz(points, 0)

    payload = {
        "match_id": match_id,
        "player_id": player_id,
        "team_id": team_id,
        "points": points,
        "rebounds": nz(pick(data, ["rebounds", "reb"]), 0),
        "assists":  nz(pick(data, ["assists", "ast"]), 0),
        "steals":   nz(pick(data, ["steals", "stl"]), 0),
        "blocks":   nz(pick(data, ["blocks", "blk"]), 0),
        "fouls":    nz(pick(data, ["fouls", "pf"]), 0),
        # ✅ 最终统一写库到 *_pt_made 三列
        "one_pt_made":   p1,
        "two_pt_made":   p2,
        "three_pt_made": p3,
        "number": data.get("number"),
        "name":   data.get("name"),
    }

    with SessionLocal() as s:
        # 列存在性（做兼容；你的表就用 *_pt_made 这套）
        cols = {
            c: has_col(s, "match_player_stats", c)
            for c in (
                "points","rebounds","assists","steals","blocks","fouls",
                "one_pt_made","two_pt_made","three_pt_made"
            )
        }

        # 组装 INSERT / UPDATE
        insert_cols = ["match_id","player_id","team_id","points"]
        insert_vals = [":match_id",":player_id",":team_id",":points"]
        updates     = ["team_id = VALUES(team_id)", "points = VALUES(points)"]

        for k in ("rebounds","assists","steals","blocks","fouls",
                  "one_pt_made","two_pt_made","three_pt_made"):
            if cols.get(k):
                insert_cols.append(k)
                insert_vals.append(f":{k}")
                updates.append(f"{k} = VALUES({k})")

        sql = text(f"""
            INSERT INTO match_player_stats ({", ".join(insert_cols)})
            VALUES ({", ".join(insert_vals)})
            ON DUPLICATE KEY UPDATE {", ".join(updates)}
        """)
        s.execute(sql, payload)

        # 可选：把号码/名字同步回 players 表
        if payload.get("number") is not None or payload.get("name"):
            sets, params = [], {"pid": player_id}
            if payload.get("number") is not None:
                sets.append("number = :num"); params["num"] = payload["number"]
            if payload.get("name"):
                sets.append("name = :pname"); params["pname"] = payload["name"]
            if sets:
                try:
                    s.execute(text(f"UPDATE players SET {', '.join(sets)} WHERE id = :pid"), params)
                except Exception:
                    pass

        s.commit()
        return jsonify({"ok": True, "saved": payload})
