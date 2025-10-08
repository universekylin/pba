# backend/routes/uploads.py
import os
from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename

bp = Blueprint("uploads", __name__, url_prefix="/api")

ALLOWED_EXTS = {"png", "jpg", "jpeg"}

# 以 backend 为基准，保存到 backend/static/team-logos
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UPLOAD_DIR = os.path.join(BASE_DIR, "static", "team-logos")
os.makedirs(UPLOAD_DIR, exist_ok=True)

def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTS

@bp.post("/uploads")
def upload_logo():
    """
    接收前端 FormData: form.append('file', 文件)
    返回:
    {
      "ok": true,
      "url":  "http(s)://<host>/static/team-logos/xxx.png",  # 绝对地址（方便立即预览）
      "path": "/static/team-logos/xxx.png"                   # 相对路径（建议写库）
    }
    """
    try:
        if "file" not in request.files:
            return jsonify({"ok": False, "error": "没有检测到文件"}), 400

        f = request.files["file"]
        if f.filename == "":
            return jsonify({"ok": False, "error": "文件名为空"}), 400

        if not allowed_file(f.filename):
            return jsonify({"ok": False, "error": "仅支持 PNG 或 JPG"}), 400

        filename = secure_filename(f.filename)
        name, ext = os.path.splitext(filename)

        # 同名自动加序号
        save_name = filename
        i = 1
        save_path = os.path.join(UPLOAD_DIR, save_name)
        while os.path.exists(save_path):
            save_name = f"{name}_{i}{ext}"
            save_path = os.path.join(UPLOAD_DIR, save_name)
            i += 1

        f.save(save_path)

        # 绝对 URL: 优先环境变量 PUBLIC_BASE_URL，其次当前请求域名
        base = os.getenv("PUBLIC_BASE_URL") or request.host_url.rstrip("/")
        abs_url = f"{base}/static/team-logos/{save_name}"
        rel_path = f"/static/team-logos/{save_name}"
        return jsonify({"ok": True, "url": abs_url, "path": rel_path})
    except Exception as e:
        # 打日志并返回 500
        print("[upload_logo] error:", e)
        return jsonify({"ok": False, "error": str(e)}), 500
