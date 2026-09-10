import type { Team, Game } from "../types";

export const seedTeams: Team[] = [
  { name: "Ironclad FC", color: "#6ee7a0" },
  { name: "Dockside United", color: "#f5b942" },
  { name: "Harbor Rovers", color: "#7fb3f0" },
  { name: "Maple Street AC", color: "#c98fe0" },
  { name: "Northgate Athletic", color: "#f2607a" },
  { name: "The Wanderers", color: "#8fa89a" },
];

export const seedGames: Game[] = [
  { id: 7, home: "Harbor Rovers", away: "Maple Street AC", status: "scheduled", date: "2026-09-20" },
  { id: 8, home: "The Wanderers", away: "Northgate Athletic", status: "scheduled", date: "2026-09-20" },
  { id: 9, home: "Ironclad FC", away: "Dockside United", status: "scheduled", date: "2026-09-13" },
  { id: 1, home: "Ironclad FC", away: "Northgate Athletic", status: "done", date: "2026-09-06", homeScore: 3, awayScore: 1 },
  { id: 2, home: "Dockside United", away: "Harbor Rovers", status: "done", date: "2026-09-06", homeScore: 2, awayScore: 2 },
  { id: 3, home: "Maple Street AC", away: "Ironclad FC", status: "done", date: "2026-08-30", homeScore: 0, awayScore: 2 },
  { id: 4, home: "The Wanderers", away: "Dockside United", status: "done", date: "2026-08-30", homeScore: 1, awayScore: 3 },
  { id: 5, home: "Harbor Rovers", away: "The Wanderers", status: "done", date: "2026-08-23", homeScore: 4, awayScore: 0 },
  { id: 6, home: "Northgate Athletic", away: "Maple Street AC", status: "done", date: "2026-08-23", homeScore: 1, awayScore: 1 },
];
