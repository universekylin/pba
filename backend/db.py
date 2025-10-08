# backend/db.py
import os
from contextlib import contextmanager
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# =========================
# 环境变量加载
#   - 优先：.env.<FLASK_ENV>（development / production）
#   - 兜底：.env
# =========================
try:
    from dotenv import load_dotenv
except Exception:
    load_dotenv = None

BACKEND_DIR = Path(__file__).resolve().parent
ENV_NAME = os.getenv("FLASK_ENV", "development").strip().lower()
env_files = [BACKEND_DIR / f".env.{ENV_NAME}", BACKEND_DIR / ".env"]

loaded_flag = False
if load_dotenv is not None:
    for p in env_files:
        if p.exists():
            loaded_flag = load_dotenv(dotenv_path=str(p), override=True) or loaded_flag
            print(f"[env] path={p} loaded=True")
        else:
            print(f"[env] path={p} loaded=False")
else:
    print("[env] python-dotenv not installed; skipping .env load")

# =========================
# 数据库环境变量
# =========================
DB_HOST = os.getenv("DB_HOST", "127.0.0.1")
DB_PORT = os.getenv("DB_PORT", "3306")
DB_USER = os.getenv("DB_USER", "root")
# 兼容 DB_PASS / DB_PASSWORD
DB_PASS = os.getenv("DB_PASS", os.getenv("DB_PASSWORD", ""))
DB_NAME = os.getenv("DB_NAME", "pba")
SQL_ECHO = os.getenv("SQL_ECHO", "0") == "1"

print(f"[env] DB_HOST={DB_HOST}")
print(f"[env] DB_USER={DB_USER}")
print(f"[env] DB_NAME={DB_NAME}")

# =========================
# 连接 URL（MySQL + PyMySQL）
# =========================
DATABASE_URL = (
    f"mysql+pymysql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}?charset=utf8mb4"
)

# =========================
# Engine & Session
# =========================
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,   # 探测断线
    future=True,
    echo=SQL_ECHO,
)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False,
    future=True,
)

@contextmanager
def get_session():
    """
    用法:
      with get_session() as s:
          s.query(...).all()
    """
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()

# =========================
# Base 导出（尽量与 models 里的保持同一个 Base）
#   - 若 models 可导入：把 models.Base 作为 db.Base 导出（推荐）
#   - 若此时导入 models 会循环：降级为占位 Base，仅用于类型提示；
#     真正建表时会在 init_db() 再 import models
# =========================
try:
    from models import Base as _ModelsBase  # type: ignore
    Base = _ModelsBase
except Exception:
    # 占位，防止 from db import Base 出错；不要用这个去 create_all
    try:
        from sqlalchemy.orm import declarative_base
        Base = declarative_base()
    except Exception:
        Base = None  # 最差兜底

# =========================
# 初始化数据库：只建不存在的表
# =========================
def init_db():
    """
    一次性建表（仅建不存在的表）。
    必须在保证 models 已加载（从而注册了所有 ORM 映射）后调用。
    """
    # 延迟导入避免循环
    from models import Base as ModelsBase  # 确保使用 models 里的 Base
    ModelsBase.metadata.create_all(bind=engine)

# 允许命令行直接执行：python db.py
if __name__ == "__main__":
    print(f"[init_db] Creating tables on {DATABASE_URL} ...")
    init_db()
    print("[init_db] Done.")
