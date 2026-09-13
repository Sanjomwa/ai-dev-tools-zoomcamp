"""Repository over the SQLite-backed domain tables.

Seeded with data shaped like frontend/src/api/mockData.ts so manual
testing against the frontend looks the same as it does against the mock.
Seeding only happens once, on first use of an empty database, so restarts
against a persistent file don't duplicate data.
"""

import colorsys
from datetime import date

from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models import GameRow, TeamRow
from app.schemas import Game, StandingsRow, Team

# Same 6-color palette the reference frontend (client.ts) cycles through
# when assigning a new team's display color.
PALETTE = [
    "#6ee7a0",
    "#f5b942",
    "#7fb3f0",
    "#c98fe0",
    "#f2607a",
    "#8fa89a",
]

SEED_TEAM_NAMES = [
    "Ironclad FC",
    "Dockside United",
    "Harbor Rovers",
    "Maple Street AC",
    "Northgate Athletic",
    "The Wanderers",
]

# (id, home, away, status, date, homeScore, awayScore) — mirrors mockData.ts
# seedGames order exactly, so listGames returns games in the same
# most-recently-scheduled-first order the reference frontend does.
SEED_GAMES = [
    (7, "Harbor Rovers", "Maple Street AC", "scheduled", date(2026, 9, 20), None, None),
    (8, "The Wanderers", "Northgate Athletic", "scheduled", date(2026, 9, 20), None, None),
    (9, "Ironclad FC", "Dockside United", "scheduled", date(2026, 9, 13), None, None),
    (1, "Ironclad FC", "Northgate Athletic", "done", date(2026, 9, 6), 3, 1),
    (2, "Dockside United", "Harbor Rovers", "done", date(2026, 9, 6), 2, 2),
    (3, "Maple Street AC", "Ironclad FC", "done", date(2026, 8, 30), 0, 2),
    (4, "The Wanderers", "Dockside United", "done", date(2026, 8, 30), 1, 3),
    (5, "Harbor Rovers", "The Wanderers", "done", date(2026, 8, 23), 4, 0),
    (6, "Northgate Athletic", "Maple Street AC", "done", date(2026, 8, 23), 1, 1),
]


def _generate_color(index: int) -> str:
    """Deterministic fallback color once the base palette is exhausted.

    Spaces hues by the golden-ratio conjugate so consecutive indexes land
    far apart on the color wheel, keeping generated colors visually distinct.
    """
    hue = (index * 0.6180339887) % 1.0
    r, g, b = colorsys.hsv_to_rgb(hue, 0.55, 0.85)
    return "#{:02x}{:02x}{:02x}".format(int(r * 255), int(g * 255), int(b * 255))


class GameNotFoundError(Exception):
    pass


class ScoreAlreadyRecordedError(Exception):
    pass


class DuplicateTeamNameError(Exception):
    pass


class LeagueStore:
    def __init__(self, db: Session) -> None:
        self.db = db
        self._seed_if_empty()

    def _seed_if_empty(self) -> None:
        if self.db.query(TeamRow).first() is not None:
            return
        for name in SEED_TEAM_NAMES:
            self.db.add(TeamRow(name=name, color=self._assign_color()))
        game_count = len(SEED_GAMES)
        for index, (game_id, home, away, status, game_date, home_score, away_score) in enumerate(SEED_GAMES):
            self.db.add(
                GameRow(
                    id=game_id,
                    home=home,
                    away=away,
                    status=status,
                    date=game_date,
                    home_score=home_score,
                    away_score=away_score,
                    rank=game_count - index,
                )
            )
        self.db.commit()

    def _assign_color(self) -> str:
        used = {row.color for row in self.db.query(TeamRow.color).all()}
        for color in PALETTE:
            if color not in used:
                return color
        index = self.db.query(TeamRow).count()
        while True:
            color = _generate_color(index)
            if color not in used:
                return color
            index += 1

    def list_teams(self) -> list[Team]:
        rows = self.db.query(TeamRow).order_by(TeamRow.seq).all()
        return [Team(name=r.name, color=r.color) for r in rows]

    def team_exists(self, name: str) -> bool:
        return self.db.query(TeamRow).filter(TeamRow.name == name).first() is not None

    def add_team(self, name: str) -> Team:
        row = TeamRow(name=name, color=self._assign_color())
        self.db.add(row)
        try:
            self.db.commit()
        except IntegrityError:
            self.db.rollback()
            raise DuplicateTeamNameError(name)
        return Team(name=row.name, color=row.color)

    def _to_game(self, row: GameRow) -> Game:
        return Game(
            id=row.id,
            home=row.home,
            away=row.away,
            status=row.status,
            date=row.date,
            homeScore=row.home_score,
            awayScore=row.away_score,
        )

    def list_games(self) -> list[Game]:
        rows = self.db.query(GameRow).order_by(GameRow.rank.desc()).all()
        return [self._to_game(r) for r in rows]

    def schedule_game(self, home: str, away: str, game_date: date) -> Game:
        max_rank = self.db.query(func.max(GameRow.rank)).scalar() or 0
        row = GameRow(home=home, away=away, status="scheduled", date=game_date, rank=max_rank + 1)
        self.db.add(row)
        self.db.commit()
        return self._to_game(row)

    def get_game(self, game_id: int) -> Game | None:
        row = self.db.query(GameRow).filter(GameRow.id == game_id).first()
        return self._to_game(row) if row else None

    def record_score(self, game_id: int, home_score: int, away_score: int) -> Game:
        row = self.db.query(GameRow).filter(GameRow.id == game_id).first()
        if row is None:
            raise GameNotFoundError(game_id)
        if row.status == "done":
            raise ScoreAlreadyRecordedError(game_id)
        row.status = "done"
        row.home_score = home_score
        row.away_score = away_score
        self.db.commit()
        return self._to_game(row)

    def get_standings(self) -> list[StandingsRow]:
        teams = self.db.query(TeamRow).order_by(TeamRow.seq).all()
        games = self.db.query(GameRow).filter(GameRow.status == "done").all()

        stats = {t.name: {"played": 0, "won": 0, "drawn": 0, "lost": 0} for t in teams}
        for g in games:
            if g.home_score is None or g.away_score is None:
                continue
            if g.home in stats:
                row = stats[g.home]
                row["played"] += 1
                if g.home_score > g.away_score:
                    row["won"] += 1
                elif g.home_score == g.away_score:
                    row["drawn"] += 1
                else:
                    row["lost"] += 1
            if g.away in stats:
                row = stats[g.away]
                row["played"] += 1
                if g.away_score > g.home_score:
                    row["won"] += 1
                elif g.away_score == g.home_score:
                    row["drawn"] += 1
                else:
                    row["lost"] += 1

        rows = []
        for t in teams:
            s = stats[t.name]
            points = s["won"] * 3 + s["drawn"]
            rows.append(
                StandingsRow(
                    name=t.name,
                    color=t.color,
                    played=s["played"],
                    won=s["won"],
                    drawn=s["drawn"],
                    lost=s["lost"],
                    points=points,
                )
            )
        rows.sort(key=lambda r: r.points, reverse=True)
        return rows
