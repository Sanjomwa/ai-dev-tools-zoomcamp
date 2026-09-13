from datetime import date as DateType

from sqlalchemy import Date, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base


class TeamRow(Base):
    __tablename__ = "teams"
    __table_args__ = (UniqueConstraint("name"),)

    # Surrogate PK purely for stable insertion-order listing; the domain
    # identifier is `name` (see Team.name in schemas.py / openapi.yaml).
    seq: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    color: Mapped[str] = mapped_column(String(7), nullable=False)


class GameRow(Base):
    __tablename__ = "games"
    __table_args__ = (UniqueConstraint("rank"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    home: Mapped[str] = mapped_column(String, nullable=False)
    away: Mapped[str] = mapped_column(String, nullable=False)
    status: Mapped[str] = mapped_column(String, nullable=False)
    date: Mapped[DateType] = mapped_column(Date, nullable=False)
    home_score: Mapped[int | None] = mapped_column(Integer, nullable=True)
    away_score: Mapped[int | None] = mapped_column(Integer, nullable=True)
    # Higher rank = scheduled more recently; list_games orders by this
    # descending so it matches the reference frontend's "prepend on
    # schedule" behavior without depending on id ordering.
    rank: Mapped[int] = mapped_column(Integer, nullable=False)
