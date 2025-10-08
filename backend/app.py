import os
import smtplib
from email.message import EmailMessage

from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from werkzeug.utils import secure_filename
from sqlalchemy import func

# 蓝图（你自己的技术统计路由）
from routes.match_stats import bp as match_stats_bp

from db import init_db, get_session
from models import Match, Player, MatchPlayerStats

# ===== 读取 backend/.env =====
load_dotenv()

# ===== 创建 Flask 应用 =====
app = Flask(__name__)  # ./static 自动映射到 /static
app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024  # 5MB
CORS(app, resources={r"/api/*": {"origins": "*"}})

# =========================================================
# 注册业务蓝图（保持你原有结构）
# =========================================================
try:
    from routes.teams import bp as teams_bp
    app.register_blueprint(teams_bp)
    app.logger.info("[init] Teams blueprint loaded successfully.")
except Exception:
    app.logger.exception("[init] Teams blueprint not loaded")

try:
    from routes.players import bp as players_bp
    app.register_blueprint(players_bp)
    app.logger.info("[init] Players blueprint loaded successfully.")
except Exception:
    app.logger.exception("[init] Players blueprint not loaded")

try:
    from routes.divisions import bp as divisions_bp
    app.register_blueprint(divisions_bp)
    app.logger.info("[init] Divisions blueprint loaded successfully.")
except Exception:
    app.logger.exception("[init] Divisions blueprint not loaded")

try:
    from routes.ladder import ladder_api
    app.register_blueprint(ladder_api)
    app.logger.info("[init] Ladder blueprint loaded successfully.")
except Exception:
    app.logger.exception("[init] Ladder blueprint not loaded")

try:
    from routes.matches import bp as matches_bp
    app.register_blueprint(matches_bp)
    app.logger.info("[init] Matches blueprint loaded successfully.")
except Exception:
    app.logger.exception("[init] Matches blueprint not loaded")

# =========================================================
# 上传接口（PNG/JPG）
# =========================================================
ALLOWED_EXTS = {"png", "jpg", "jpeg"}
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_DIR = os.path.join(BASE_DIR, "static", "team-logos")
os.makedirs(UPLOAD_DIR, exist_ok=True)

def _allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTS

@app.post("/api/uploads")
def upload_logo():
    """
    表单字段：file  (PNG/JPG)
    返回：
    {
      "ok": true,
      "url":  "<host>/static/team-logos/xxx.png",
      "path": "/static/team-logos/xxx.png"
    }
    """
    try:
        if "file" not in request.files:
            return jsonify({"ok": False, "error": "没有检测到文件字段 file"}), 400

        f = request.files["file"]
        if f.filename == "":
            return jsonify({"ok": False, "error": "文件名为空"}), 400

        if not _allowed_file(f.filename):
            return jsonify({"ok": False, "error": "仅支持 PNG 或 JPG 图片"}), 400

        from werkzeug.utils import secure_filename
        filename = secure_filename(f.filename)
        name, ext = os.path.splitext(filename)

        save_name = filename
        i = 1
        save_path = os.path.join(UPLOAD_DIR, save_name)
        while os.path.exists(save_path):
            save_name = f"{name}_{i}{ext}"
            save_path = os.path.join(UPLOAD_DIR, save_name)
            i += 1

        f.save(save_path)

        base = os.getenv("PUBLIC_BASE_URL") or request.host_url.rstrip("/")
        abs_url = f"{base}/static/team-logos/{save_name}"
        rel_path = f"/static/team-logos/{save_name}"

        return jsonify({"ok": True, "url": abs_url, "path": rel_path})
    except Exception:
        app.logger.exception("upload_logo failed")
        return jsonify({"ok": False, "error": "upload failed"}), 500

# =========================================================
# 健康检查 & 路由查看器
# =========================================================
@app.get("/api/health")
def health():
    return jsonify({"ok": True, "message": "Backend running"})

@app.get("/api/_routes")
def _routes():
    return jsonify(sorted(
        str(r) for r in app.url_map.iter_rules() if str(r).startswith("/api/")
    ))

# =========================================================
# 比赛技术统计 - 记分接口（同步写回 matches.home_score/away_score）
# =========================================================

FIELD_MAP = {
    "one":   "one_pt_made",
    "two":   "two_pt_made",
    "three": "three_pt_made",
    "foul":  "fouls",
}

def recompute_points(row: MatchPlayerStats) -> int:
    return row.one_pt_made + 2 * row.two_pt_made + 3 * row.three_pt_made

def compute_match_totals(match_id: int):
    """
    汇总某场比赛两队总分/犯规，并且**同步把总分写回 matches 表**：
      - m.home_score = 主队总分
      - m.away_score = 客队总分
    """
    with get_session() as s:
        m = s.get(Match, match_id)
        if not m:
            return {"light": {"pts": 0, "fouls": 0}, "dark": {"pts": 0, "fouls": 0}}

        rows = (
            s.query(
                MatchPlayerStats.team_id,
                func.coalesce(func.sum(MatchPlayerStats.points), 0),
                func.coalesce(func.sum(MatchPlayerStats.fouls), 0),
            )
            .filter(MatchPlayerStats.match_id == match_id)
            .group_by(MatchPlayerStats.team_id)
            .all()
        )

        totals = {
            m.home_team_id: {"pts": 0, "fouls": 0},
            m.away_team_id: {"pts": 0, "fouls": 0},
        }
        for team_id, pts, fouls in rows:
            if team_id in totals:
                totals[team_id] = {"pts": int(pts), "fouls": int(fouls)}

        # —— 关键：把总分落库到 matches —— #
        home_pts = totals.get(m.home_team_id, {"pts": 0})["pts"]
        away_pts = totals.get(m.away_team_id, {"pts": 0})["pts"]
        m.home_score = home_pts
        m.away_score = away_pts
        # 退出 with get_session() 会提交

        return {"light": totals[m.home_team_id], "dark": totals[m.away_team_id]}

@app.post("/api/matches/<int:match_id>/stat")
def post_stat_delta(match_id: int):
    """
    请求体:
    {
        "player_id": 1,
        "field": "one" | "two" | "three" | "foul",
        "delta": 1   # +1 或 -1
    }
    """
    data = request.get_json(force=True)
    player_id = int(data["player_id"])
    field = data["field"]
    delta = int(data.get("delta", 1))

    if field not in FIELD_MAP:
        return jsonify({"error": "invalid field"}), 400

    with get_session() as s:
        row = (
            s.query(MatchPlayerStats)
             .filter(MatchPlayerStats.match_id == match_id,
                     MatchPlayerStats.player_id == player_id)
             .one_or_none()
        )
        if row is None:
            player = s.get(Player, player_id)
            if not player:
                return jsonify({"error": "player not found"}), 404
            row = MatchPlayerStats(
                match_id=match_id,
                player_id=player_id,
                team_id=player.team_id,
            )
            s.add(row)
            s.flush()

        # 更新字段，避免负数
        attr = FIELD_MAP[field]
        new_val = max(0, getattr(row, attr) + delta)
        setattr(row, attr, new_val)

        # 同步总得分（points）
        row.points = recompute_points(row)

        # 提交在上下文退出时完成
        updated = {
            "player_id": row.player_id,
            "one": row.one_pt_made,
            "two": row.two_pt_made,
            "three": row.three_pt_made,
            "foul": row.fouls,
            "points": row.points,
            "field": field,
            "value": new_val,
        }

    # —— 每次记分后：回写 matches 的 home_score/away_score —— #
    totals = compute_match_totals(match_id)
    return jsonify({"updated": updated, "totals": totals})

@app.get("/api/matches/<int:match_id>/boxscore")
def get_boxscore(match_id: int):
    with get_session() as s:
        match = s.get(Match, match_id)
        if not match:
            return jsonify({"error": "match not found"}), 404

        home_id, away_id = match.home_team_id, match.away_team_id

        rows = (
            s.query(MatchPlayerStats)
             .filter(MatchPlayerStats.match_id == match_id)
             .all()
        )

        players = [{
            "player_id": r.player_id,
            "team_id": r.team_id,
            "one": r.one_pt_made,
            "two": r.two_pt_made,
            "three": r.three_pt_made,
            "foul": r.fouls,
            "points": r.points,
        } for r in rows]

    totals = compute_match_totals(match_id)
    return jsonify({
        "players": players,
        "totals": totals,
        "home_team_id": home_id,
        "away_team_id": away_id,
    })

# =========================================================
# 批量补齐历史比赛比分（把已结束比赛的总分写回 matches）
# 调用一次即可：POST /api/admin/recompute-scores
# =========================================================
@app.post("/api/admin/recompute-scores")
def recompute_scores():
    updated = 0
    with get_session() as s:
        matches = (
            s.query(Match)
             .filter(func.lower(Match.status) == "finished")
             .all()
        )
        for m in matches:
            # 汇总该场两队总分
            rows = (
                s.query(
                    MatchPlayerStats.team_id,
                    func.coalesce(func.sum(MatchPlayerStats.points), 0),
                )
                .filter(MatchPlayerStats.match_id == m.id)
                .group_by(MatchPlayerStats.team_id)
                .all()
            )
            by_team = {tid: int(pts) for tid, pts in rows}
            m.home_score = by_team.get(m.home_team_id, 0)
            m.away_score = by_team.get(m.away_team_id, 0)
            updated += 1
    return jsonify({"ok": True, "updated": updated})

# =========================================================
# 发送报名邮件（可选）
# =========================================================
SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASS = os.getenv("SMTP_PASS")
DEFAULT_TO = os.getenv("MAIL_TO", "director@perfectballers.com")

@app.post("/api/send-registration")
def send_registration():
    try:
        order_id = request.form.get("orderId", "")
        to_raw = request.form.get("to") or DEFAULT_TO or ""
        subject = request.form.get("subject", f"PBA Registration - {order_id}")
        text = request.form.get("text", "New registration attached.")

        # ✅ 多收件人解析（逗号或分号分隔）
        recipients = [x.strip() for x in to_raw.replace(";", ",").split(",") if x.strip()]
        if not recipients:
            return jsonify({"ok": False, "error": "Recipient missing"}), 400

        # ✅ 检查 SMTP 凭证
        if not SMTP_USER or not SMTP_PASS:
            return jsonify({"ok": False, "error": "SMTP not configured"}), 500

        msg = EmailMessage()
        msg["From"] = SMTP_USER
        msg["To"] = ", ".join(recipients)
        msg["Subject"] = subject
        msg.set_content(text)

        # ✅ 读取所有附件
        files = request.files.getlist("attachments") or []
        total_bytes = 0
        safe_files = []

        for f in files:
            data = f.read()
            total_bytes += len(data)
            f.stream.seek(0)
            safe_files.append(f)

        MAX_TOTAL = 18 * 1024 * 1024  # 18MB 限制
        if total_bytes > MAX_TOTAL:
            only_pdf = []
            for f in safe_files:
                if (f.filename or "").lower().endswith(".pdf"):
                    only_pdf.append(f)
            safe_files = only_pdf

        # ✅ 附件写入
        for f in safe_files:
            data = f.read()
            maintype, subtype = ("application", "octet-stream")
            if f.mimetype and "/" in f.mimetype:
                maintype, subtype = f.mimetype.split("/", 1)
            msg.add_attachment(data, maintype=maintype, subtype=subtype, filename=f.filename or "file")

        # ✅ 调试日志输出
        app.logger.info(f"[MAIL] Sending to {recipients}, attachments={len(safe_files)}, total={total_bytes/1024/1024:.2f} MB")

        # ✅ 连接 Gmail SMTP（带调试输出）
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=30) as smtp:
            smtp.set_debuglevel(1)  # 打印 SMTP 对话日志（在终端可见）
            smtp.ehlo()
            smtp.starttls()
            smtp.ehlo()
            smtp.login(SMTP_USER, SMTP_PASS)
            resp = smtp.send_message(msg)

        app.logger.info(f"[MAIL] Sent successfully. SMTP response: {resp}")
        return jsonify({"ok": True, "recipients": recipients, "resp": resp})

    except Exception as e:
        app.logger.exception("send_registration failed")
        return jsonify({"ok": False, "error": str(e)}), 500
    
    
# 你原有的统计蓝图
app.register_blueprint(match_stats_bp)

# =========================================================
# 启动服务
# =========================================================
if __name__ == "__main__":
    init_db()  # 只建不存在的表
    app.run(host="0.0.0.0", port=3001, debug=True)
