import { useEffect, useState, useCallback } from "react";
import type { Team, Game, StandingsRow } from "./types";
import { api } from "./api/client";
import { TabNav } from "./components/TabNav";
import { StandingsScreen } from "./components/StandingsScreen";
import { GamesScreen } from "./components/GamesScreen";
import { TeamsScreen } from "./components/TeamsScreen";
import "./App.css";

type Tab = "standings" | "games" | "teams";

export default function App() {
  const [tab, setTab] = useState<Tab>("standings");
  const [teams, setTeams] = useState<Team[]>([]);
  const [games, setGames] = useState<Game[]>([]);
  const [rows, setRows] = useState<StandingsRow[]>([]);
  const [loading, setLoading] = useState(true);

  const refresh = useCallback(async () => {
    const [t, g, s] = await Promise.all([api.listTeams(), api.listGames(), api.getStandings()]);
    setTeams(t);
    setGames(g);
    setRows(s);
  }, []);

  useEffect(() => {
    refresh().finally(() => setLoading(false));
  }, [refresh]);

  async function handleSchedule(input: { home: string; away: string; date: string }) {
    await api.scheduleGame(input);
    await refresh();
  }

  async function handleRecord(gameId: number, homeScore: number, awayScore: number) {
    await api.recordScore(gameId, homeScore, awayScore);
    await refresh();
  }

  async function handleAddTeam(name: string) {
    await api.addTeam(name);
    await refresh();
  }

  return (
    <div className="app">
      <div className="head">
        <div className="brand">
          <span className="mark">LEAGUEBOARD</span>
          <span className="league">Riverside Sunday League</span>
        </div>
        <div className="meta">
          Matchweek 8
          <span className="meta-sub">No login · anyone with the link can edit</span>
        </div>
      </div>

      <TabNav active={tab} onChange={setTab} />

      {loading ? (
        <p className="sub">Loading…</p>
      ) : (
        <>
          {tab === "standings" && <StandingsScreen rows={rows} />}
          {tab === "games" && (
            <GamesScreen teams={teams} games={games} onSchedule={handleSchedule} onRecord={handleRecord} />
          )}
          {tab === "teams" && <TeamsScreen teams={teams} rows={rows} onAddTeam={handleAddTeam} />}
        </>
      )}

      <p className="footnote">
        Backend calls are mocked in <code>src/api/client.ts</code> — swap that file for real fetch() calls later; nothing else changes.
      </p>
    </div>
  );
}
