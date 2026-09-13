import os
from collections.abc import Iterator

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.db import make_session_factory
from app.schemas import Game, GameCreate, ScoreInput, StandingsRow, Team, TeamCreate
from app.store import DuplicateTeamNameError, GameNotFoundError, LeagueStore, ScoreAlreadyRecordedError

# Actual frontend dev origin, confirmed against frontend/vite.config.ts by
# running `npm run dev` (see homework/module_02/AGENTS.md status section).
FRONTEND_ORIGIN = "http://localhost:5173"

DEFAULT_DATABASE_URL = "sqlite:///./leagueboard.db"


def create_app(database_url: str | None = None) -> FastAPI:
    app = FastAPI(title="Leagueboard API", version="0.1.0")
    resolved_url = database_url or os.environ.get("DATABASE_URL", DEFAULT_DATABASE_URL)
    session_factory = make_session_factory(resolved_url)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=[FRONTEND_ORIGIN],
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
        message = "; ".join(f"{'.'.join(str(loc) for loc in e['loc'])}: {e['msg']}" for e in exc.errors())
        return JSONResponse(status_code=422, content={"detail": message})

    def get_store() -> Iterator[LeagueStore]:
        db = session_factory()
        try:
            yield LeagueStore(db)
        finally:
            db.close()

    @app.get("/api/teams", response_model=list[Team], tags=["teams"])
    def list_teams(s: LeagueStore = Depends(get_store)) -> list[Team]:
        return s.list_teams()

    @app.post("/api/teams", response_model=Team, status_code=201, tags=["teams"])
    def add_team(payload: TeamCreate, s: LeagueStore = Depends(get_store)) -> Team:
        try:
            return s.add_team(payload.name)
        except DuplicateTeamNameError:
            raise HTTPException(status_code=422, detail=f"A team named '{payload.name}' already exists")

    @app.get("/api/games", response_model=list[Game], tags=["games"])
    def list_games(s: LeagueStore = Depends(get_store)) -> list[Game]:
        return s.list_games()

    @app.post("/api/games", response_model=Game, status_code=201, tags=["games"])
    def schedule_game(payload: GameCreate, s: LeagueStore = Depends(get_store)) -> Game:
        if not s.team_exists(payload.home):
            raise HTTPException(status_code=404, detail=f"No team named '{payload.home}'")
        if not s.team_exists(payload.away):
            raise HTTPException(status_code=404, detail=f"No team named '{payload.away}'")
        return s.schedule_game(payload.home, payload.away, payload.date)

    @app.post("/api/games/{game_id}/score", response_model=Game, tags=["games"])
    def record_score(game_id: int, payload: ScoreInput, s: LeagueStore = Depends(get_store)) -> Game:
        try:
            return s.record_score(game_id, payload.homeScore, payload.awayScore)
        except GameNotFoundError:
            raise HTTPException(status_code=404, detail=f"No game with id {game_id}")
        except ScoreAlreadyRecordedError:
            raise HTTPException(status_code=409, detail=f"Game {game_id} already has a recorded score")

    @app.get("/api/standings", response_model=list[StandingsRow], tags=["standings"])
    def get_standings(s: LeagueStore = Depends(get_store)) -> list[StandingsRow]:
        return s.get_standings()

    return app
