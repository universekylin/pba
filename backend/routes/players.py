# backend/routes/players.py
from __future__ import annotations

from flask import Blueprint, jsonify, request
from sqlalchemy import select, delete
from sqlalchemy.exc import SQLAlchemyError

from db import SessionLocal
from models import Player

bp = Blueprint("players", __name__, url_prefix="/api")

# 兼容：有的环境 Player 可能没有 note 字段
_HAS_NOTE = hasattr(Player, "note")


def _to_dict(p: Player) -> dict:
    """ORM -> dict（无 note 时返回 None）"""
    return {
        "id": p.id,
        "team_id": p.team_id,
        "name": p.name,
        "number": p.number,
        "note": getattr(p, "note", None) if _HAS_NOTE else None,
    }


def _normalize_number(value):
    """把 '' 或不合法字符串转为 None；合法数字字符串/数字转 int"""
    if value is None:
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, str):
        v = value.strip()
        return int(v) if v.isdigit() else None
    return None


# ========================
# 列表：按 team_id 查询
# ========================
@bp.get("/teams/<int:team_id>/players")
def list_players(team_id: int):
    """按球队列出球员"""
    with SessionLocal() as s:
        rows = (
            s.execute(
                select(Player)
                .where(Player.team_id == team_id)
                .order_by(
                    Player.number.is_(None),  # 号码为空的排前
                    Player.number.asc(),
                    Player.id.asc(),
                )
            )
            .scalars()
            .all()
        )
        return jsonify([_to_dict(p) for p in rows])


# （可选）支持 /api/players?team_id=xx 的查询方式
@bp.get("/players")
def list_players_by_query():
    team_id = request.args.get("team_id", type=int)
    if not team_id:
        return jsonify({"error": "team_id 参数必填"}), 400
    with SessionLocal() as s:
        rows = (
            s.execute(
                select(Player)
                .where(Player.team_id == team_id)
                .order_by(
                    Player.number.is_(None),
                    Player.number.asc(),
                    Player.id.asc(),
                )
            )
            .scalars()
            .all()
        )
        return jsonify([_to_dict(p) for p in rows])


# ========================
# 新增
# ========================
@bp.post("/players")
def create_player():
    """新增球员"""
    data = request.get_json(silent=True) or {}
    name = (data.get("name") or "").strip()
    team_id = data.get("team_id")
    number = _normalize_number(data.get("number"))
    note = (data.get("note") or "").strip() or None if _HAS_NOTE else None

    if not name or not team_id:
        return jsonify({"error": "name 和 team_id 不能为空"}), 400

    try:
        with SessionLocal() as s:
            kwargs = {"name": name, "team_id": int(team_id), "number": number}
            if _HAS_NOTE:
                kwargs["note"] = note

            p = Player(**kwargs)
            s.add(p)
            s.commit()
            s.refresh(p)
            return jsonify(_to_dict(p)), 201
    except SQLAlchemyError as e:
        print("create_player error:", repr(e))
        return jsonify({"error": "数据库错误"}), 500


# ========================
# 更新（方案 D）
# ========================
@bp.put("/players/<int:player_id>")
def update_player(player_id: int):
    """更新球员：前端 PUT /api/players/:id，body 可含 name/number/note/team_id"""
    data = request.get_json(silent=True) or {}

    # 允许部分字段更新
    name = data.get("name")
    number = _normalize_number(data.get("number"))
    team_id = data.get("team_id")
    note = (data.get("note") or "").strip() or None if _HAS_NOTE and "note" in data else None
    has_note_in_payload = _HAS_NOTE and ("note" in data)

    try:
        with SessionLocal() as s:
            p: Player | None = s.get(Player, player_id)
            if not p:
                return jsonify({"error": "球员不存在"}), 404

            if name is not None:
                name = name.strip()
                if not name:
                    return jsonify({"error": "name 不能为空"}), 400
                p.name = name

            # number 可置空（None）
            if "number" in data:
                p.number = number

            if team_id is not None:
                p.team_id = int(team_id)

            if has_note_in_payload:
                setattr(p, "note", note)

            s.commit()
            s.refresh(p)
            return jsonify(_to_dict(p))
    except SQLAlchemyError as e:
        print("update_player error:", repr(e))
        return jsonify({"error": "数据库错误"}), 500


# ========================
# 删除
# ========================
@bp.delete("/players/<int:player_id>")
def delete_player(player_id: int):
    """删除球员"""
    with SessionLocal() as s:
        r = s.execute(delete(Player).where(Player.id == player_id))
        s.commit()
        if r.rowcount == 0:
            return jsonify({"error": "球员不存在"}), 404
        return jsonify({"ok": True})
