import type { Team, Game, StandingsRow } from "../types";

/**
 * Every "backend" call the app makes goes through this module.
 * Nothing else in the app touches the data directly — this is the only
 * file that changed when the mock in-memory store was swapped for
 * fetch() calls against the real FastAPI backend.
 */

const BASE_URL = "http://localhost:8000/api";

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE_URL}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!res.ok) {
    const body = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(typeof body.detail === "string" ? body.detail : res.statusText);
  }
  return res.json();
}

export const api = {
  listTeams(): Promise<Team[]> {
    return request<Team[]>("/teams");
  },

  addTeam(name: string): Promise<Team> {
    return request<Team>("/teams", {
      method: "POST",
      body: JSON.stringify({ name }),
    });
  },

  listGames(): Promise<Game[]> {
    return request<Game[]>("/games");
  },

  scheduleGame(input: { home: string; away: string; date: string }): Promise<Game> {
    return request<Game>("/games", {
      method: "POST",
      body: JSON.stringify(input),
    });
  },

  recordScore(gameId: number, homeScore: number, awayScore: number): Promise<Game> {
    return request<Game>(`/games/${gameId}/score`, {
      method: "POST",
      body: JSON.stringify({ homeScore, awayScore }),
    });
  },

  getStandings(): Promise<StandingsRow[]> {
    return request<StandingsRow[]>("/standings");
  },
};
