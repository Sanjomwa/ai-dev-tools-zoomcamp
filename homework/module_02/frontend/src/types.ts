export type GameStatus = "scheduled" | "done";

export interface Team {
  name: string;
  color: string;
}

export interface Game {
  id: number;
  home: string;
  away: string;
  status: GameStatus;
  date: string;
  homeScore?: number;
  awayScore?: number;
}

export interface StandingsRow {
  name: string;
  color: string;
  played: number;
  won: number;
  drawn: number;
  lost: number;
  points: number;
}
