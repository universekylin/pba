# backend/routes/__init__.py
from flask import Blueprint
from .divisions import bp as divisions_bp
from .ladder import ladder_api
from .player_ranking import player_ranking_api   # ← 新增

api_bp = Blueprint("api_bp", __name__)
api_bp.register_blueprint(divisions_bp)
api_bp.register_blueprint(ladder_api)
api_bp.register_blueprint(player_ranking_api)    # ← 新增
