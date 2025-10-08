# backend/models.py
from __future__ import annotations
from typing import List, Optional

from sqlalchemy.orm import declarative_base, Mapped, mapped_column, relationship
from sqlalchemy import (
    String,
    Integer,
    SmallInteger,
    BigInteger,
    ForeignKey,
    Date,
    Time,
    UniqueConstraint,
)
from sqlalchemy.dialects.mysql import INTEGER as MYSQL_INTEGER  # MySQL 无符号整型

Base = declarative_base()

# ===========================
# 分区：Champion / D1 / D2
# ===========================
class Division(Base):
    __tablename__ = "divisions"

    # 与现有库一致：SMALLINT
    id: Mapped[int] = mapped_column(SmallInteger, primary_key=True)
    code: Mapped[str] = mapped_column(String(16), unique=True, nullable=False)  # champion / d1 / d2
    name: Mapped[str] = mapped_column(String(64), nullable=False)

    teams: Mapped[List["TeamSeasonDivision"]] = relationship(
        "TeamSeasonDivision", back_populates="division"
    )


# ===========================
# 赛季：如 2025-S8
# ===========================
class Season(Base):
    __tablename__ = "seasons"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(32), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(64), nullable=False)

    teams: Mapped[List["TeamSeasonDivision"]] = relationship(
        "TeamSeasonDivision", back_populates="season"
    )


# ===========================
# 球队
# ===========================
class Team(Base):
    __tablename__ = "teams"

    # 与库一致：INT UNSIGNED
    id: Mapped[int] = mapped_column(MYSQL_INTEGER(unsigned=True), primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    logo_url: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    note: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    seasons: Mapped[List["TeamSeasonDivision"]] = relationship(
        "TeamSeasonDivision", back_populates="team"
    )
    players: Mapped[List["Player"]] = relationship(
        "Player", back_populates="team", cascade="all, delete-orphan"
    )
    # 本队在各比赛里的球员技术统计（便于联查）
    stats: Mapped[List["MatchPlayerStats"]] = relationship(
        "MatchPlayerStats", back_populates="team", cascade="all, delete-orphan"
    )


# ===========================
# 球员
# ===========================
class Player(Base):
    __tablename__ = "players"

    id: Mapped[int] = mapped_column(MYSQL_INTEGER(unsigned=True), primary_key=True, autoincrement=True)
    team_id: Mapped[int] = mapped_column(ForeignKey("teams.id"), nullable=False)  # 对齐 teams.id (unsigned)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    number: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    team: Mapped["Team"] = relationship("Team", back_populates="players")
    stats: Mapped[List["MatchPlayerStats"]] = relationship(
        "MatchPlayerStats", back_populates="player", cascade="all, delete-orphan"
    )


# ===========================
# 赛季-分区-球队 归属关系
# ===========================
class TeamSeasonDivision(Base):
    """
    每个赛季下，每支球队属于一个分区。
    """
    __tablename__ = "team_season_division"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    team_id: Mapped[int] = mapped_column(ForeignKey("teams.id"), nullable=False)         # teams.id -> unsigned int
    season_id: Mapped[int] = mapped_column(ForeignKey("seasons.id"), nullable=False)     # seasons.id -> int
    division_id: Mapped[int] = mapped_column(ForeignKey("divisions.id"), nullable=False) # divisions.id -> smallint

    team: Mapped["Team"] = relationship("Team", back_populates="seasons")
    season: Mapped["Season"] = relationship("Season", back_populates="teams")
    division: Mapped["Division"] = relationship("Division", back_populates="teams")


# ===========================
# 比赛（常规赛/季后赛）
# - stage/status 用 String(16)
# - 日期时间两列：Date / Time
# ===========================
class Match(Base):
    __tablename__ = "matches"

    id: Mapped[int] = mapped_column(MYSQL_INTEGER(unsigned=True), primary_key=True, autoincrement=True)
    season_id: Mapped[int] = mapped_column(ForeignKey("seasons.id"), nullable=False)
    division_id: Mapped[int] = mapped_column(ForeignKey("divisions.id"), nullable=False)

    stage: Mapped[str] = mapped_column(String(16), nullable=False, server_default="regular")  # 'regular' / 'playoff'
    round_no: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    date: Mapped[Optional[Date]] = mapped_column(Date, nullable=True)
    time: Mapped[Optional[Time]] = mapped_column(Time, nullable=True)

    venue: Mapped[Optional[str]] = mapped_column(String(120), nullable=True)
    status: Mapped[str] = mapped_column(String(16), nullable=False, server_default="scheduled")

    home_team_id: Mapped[Optional[int]] = mapped_column(ForeignKey("teams.id"), nullable=True)
    away_team_id: Mapped[Optional[int]] = mapped_column(ForeignKey("teams.id"), nullable=True)

    home_score: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    away_score: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    home_team = relationship("Team", foreign_keys=[home_team_id])
    away_team = relationship("Team", foreign_keys=[away_team_id])

    player_stats: Mapped[List["MatchPlayerStats"]] = relationship(
        "MatchPlayerStats", back_populates="match", cascade="all, delete-orphan"
    )

    def to_dict(self):
        def t(team):
            if team is None:
                return None
            return {"id": team.id, "name": team.name, "logo_url": team.logo_url}

        return {
            "id": self.id,
            "round_no": self.round_no,
            "stage": self.stage,
            "status": self.status,
            "date": self.date.isoformat() if self.date else None,
            "time": self.time.strftime("%H:%M:%S") if self.time else None,
            "venue": self.venue,
            "home_score": self.home_score,
            "away_score": self.away_score,
            "home_team": t(self.home_team),
            "away_team": t(self.away_team),
        }


# ===========================
# 比赛-球员 技术统计（含 team_id）
# ===========================
class MatchPlayerStats(Base):
    __tablename__ = "match_player_stats"
    __table_args__ = (
        UniqueConstraint("match_id", "player_id", name="uq_match_player"),
    )

    # 主键：INT UNSIGNED
    id: Mapped[int] = mapped_column(MYSQL_INTEGER(unsigned=True), primary_key=True, autoincrement=True)

    # 外键全部与被引用表对齐（matches/players/teams 的 id 均为 INT UNSIGNED）
    match_id: Mapped[int] = mapped_column(
        MYSQL_INTEGER(unsigned=True),
        ForeignKey("matches.id", ondelete="CASCADE"),
        nullable=False,
    )
    player_id: Mapped[int] = mapped_column(
        MYSQL_INTEGER(unsigned=True),
        ForeignKey("players.id", ondelete="CASCADE"),
        nullable=False,
    )
    team_id: Mapped[int] = mapped_column(
        MYSQL_INTEGER(unsigned=True),
        ForeignKey("teams.id", ondelete="CASCADE"),
        nullable=False,
    )

    # —— 新增：命中次数 —— #
    one_pt_made:   Mapped[int] = mapped_column(SmallInteger, nullable=False, default=0, server_default="0")
    two_pt_made:   Mapped[int] = mapped_column(SmallInteger, nullable=False, default=0, server_default="0")
    three_pt_made: Mapped[int] = mapped_column(SmallInteger, nullable=False, default=0, server_default="0")

    # —— 保留：常规统计 —— #
    points:   Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")
    rebounds: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")
    steals:   Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")
    assists:  Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")
    blocks:   Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")
    fouls:    Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")

    match:  Mapped["Match"]  = relationship("Match",  back_populates="player_stats")
    player: Mapped["Player"] = relationship("Player", back_populates="stats")
    team:   Mapped["Team"]   = relationship("Team",   back_populates="stats")
