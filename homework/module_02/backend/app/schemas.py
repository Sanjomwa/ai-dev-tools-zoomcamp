from datetime import date as DateType
from typing import Literal, Optional

from pydantic import BaseModel, Field

GameStatus = Literal["scheduled", "done"]

HEX_COLOR_PATTERN = r"^#[0-9a-fA-F]{6}$"


class Team(BaseModel):
    name: str
    color: str = Field(pattern=HEX_COLOR_PATTERN)


class TeamCreate(BaseModel):
    name: str = Field(min_length=1)


class Game(BaseModel):
    id: int
    home: str
    away: str
    status: GameStatus
    date: DateType
    homeScore: Optional[int] = Field(default=None, ge=0)
    awayScore: Optional[int] = Field(default=None, ge=0)


class GameCreate(BaseModel):
    home: str
    away: str
    date: DateType


class ScoreInput(BaseModel):
    homeScore: int = Field(ge=0)
    awayScore: int = Field(ge=0)


class StandingsRow(BaseModel):
    name: str
    color: str = Field(pattern=HEX_COLOR_PATTERN)
    played: int = Field(ge=0)
    won: int = Field(ge=0)
    drawn: int = Field(ge=0)
    lost: int = Field(ge=0)
    points: int = Field(ge=0)


class Error(BaseModel):
    detail: str
