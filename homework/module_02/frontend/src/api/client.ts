import type { Team, Game, StandingsRow } from "../types";
import { seedTeams, seedGames } from "./mockData";

/**
 * Every "backend" call the app makes goes through this module.
 * Nothing else in the app touches the data directly — when the real
 * FastAPI backend exists, this is the only file that changes
 * (mock in-memory store -> fetch() against the real API).
 */

const LATENCY_MS = 220;
const PALETTE = ["#6ee7a0", "#f5b942", "#7fb3f0", "#c98fe0", "#f2607a", "#8fa89a"];

function wait<T>(value: T): Promise<T> {
  return new Promise((resolve) => setTimeout(() => resolve(value), LATENCY_MS));
}

let teams: Team[] = seedTeams.map((t) => ({ ...t }));
let games: Game[] = seedGames.map((g) => ({ ...g }));
let nextGameId = Math.max(...games.map((g) => g.id)) + 1;

function computeStandings(): StandingsRow[] {
  const rows = teams.map((t) => {
    let played = 0, won = 0, drawn = 0, lost = 0;
    games.forEach((g) => {
      if (g.status !== "done" || g.homeScore == null || g.awayScore == null) return;
      if (g.home === t.name) {
        played++;
        if (g.homeScore > g.awayScore) won++;
        else if (g.homeScore === g.awayScore) drawn++;
        else lost++;
      } else if (g.away === t.name) {
        played++;
        if (g.awayScore > g.homeScore) won++;
        else if (g.homeScore === g.awayScore) drawn++;
        else lost++;
      }
    });
    return { name: t.name, color: t.color, played, won, drawn, lost, points: won * 3 + drawn };
  });
  return rows.sort((a, b) => b.points - a.points);
}

export const api = {
  listTeams(): Promise<Team[]> {
    return wait(teams.map((t) => ({ ...t })));
  },

  addTeam(name: string): Promise<Team> {
    const team: Team = { name, color: PALETTE[teams.length % PALETTE.length] };
    teams = [...teams, team];
    return wait(team);
  },

  listGames(): Promise<Game[]> {
    return wait(games.map((g) => ({ ...g })));
  },

  scheduleGame(input: { home: string; away: string; date: string }): Promise<Game> {
    const game: Game = { id: nextGameId++, home: input.home, away: input.away, date: input.date, status: "scheduled" };
    games = [game, ...games];
    return wait(game);
  },

  recordScore(gameId: number, homeScore: number, awayScore: number): Promise<Game> {
    let updated: Game | undefined;
    games = games.map((g) => {
      if (g.id !== gameId) return g;
      updated = { ...g, status: "done", homeScore, awayScore };
      return updated;
    });
    if (!updated) throw new Error(`No game with id ${gameId}`);
    return wait(updated);
  },

  getStandings(): Promise<StandingsRow[]> {
    return wait(computeStandings());
  },
};
