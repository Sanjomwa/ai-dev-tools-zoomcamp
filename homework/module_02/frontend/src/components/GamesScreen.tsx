import { useState } from "react";
import type { Team, Game } from "../types";

interface Props {
  teams: Team[];
  games: Game[];
  onSchedule: (input: { home: string; away: string; date: string }) => Promise<void>;
  onRecord: (gameId: number, homeScore: number, awayScore: number) => Promise<void>;
}

export function GamesScreen({ teams, games, onSchedule, onRecord }: Props) {
  const [schedulePanelOpen, setSchedulePanelOpen] = useState(false);
  const [scheduleHome, setScheduleHome] = useState(teams[0]?.name ?? "");
  const [scheduleAway, setScheduleAway] = useState(teams[1]?.name ?? "");
  const [scheduleDate, setScheduleDate] = useState("2026-09-27");

  const [recordGameId, setRecordGameId] = useState<number | null>(null);
  const [recordHomeScore, setRecordHomeScore] = useState(0);
  const [recordAwayScore, setRecordAwayScore] = useState(0);

  const recordingGame = games.find((g) => g.id === recordGameId) ?? null;

  async function submitSchedule() {
    if (!scheduleHome || !scheduleAway || scheduleHome === scheduleAway) return;
    await onSchedule({ home: scheduleHome, away: scheduleAway, date: scheduleDate });
    setSchedulePanelOpen(false);
  }

  async function submitRecord() {
    if (recordGameId == null) return;
    await onRecord(recordGameId, recordHomeScore, recordAwayScore);
    setRecordGameId(null);
  }

  return (
    <section className="screen">
      <div className="panel-head">
        <div>
          <h2 className="h2">Games</h2>
          <p className="sub">Scheduled and completed, most recent first</p>
        </div>
        <button
          className="btn-primary"
          onClick={() => {
            setSchedulePanelOpen((open) => !open);
            setRecordGameId(null);
          }}
        >
          + Schedule game
        </button>
      </div>

      <div className="games-list">
        {games.map((g) => (
          <div className="game-row" key={g.id}>
            <div className="game-teams">
              {g.home}
              <span className="vs-label">at</span>
              {g.away}
            </div>
            <span className="game-score">
              {g.status === "done" ? `${g.homeScore} – ${g.awayScore}` : "vs"}
            </span>
            <div className="game-meta">
              <span className={`chip ${g.status === "done" ? "done" : "scheduled"}`}>
                {g.status === "done" ? "Final" : "Scheduled"}
              </span>
              {g.date}
            </div>
            {g.status === "scheduled" && (
              <button
                className="btn-ghost"
                onClick={() => {
                  setRecordGameId(g.id);
                  setRecordHomeScore(0);
                  setRecordAwayScore(0);
                  setSchedulePanelOpen(false);
                }}
              >
                Record score
              </button>
            )}
          </div>
        ))}
      </div>

      {schedulePanelOpen && (
        <div className="action-panel">
          <h3 className="h3">Schedule a game</h3>
          <p className="hint">Both teams must already exist in the league — status starts as Scheduled.</p>
          <div className="form-row">
            <div className="field">
              <label className="label">Home team</label>
              <select className="input" value={scheduleHome} onChange={(e) => setScheduleHome(e.target.value)}>
                {teams.map((t) => (
                  <option key={t.name} value={t.name}>{t.name}</option>
                ))}
              </select>
            </div>
            <div className="field">
              <label className="label">Away team</label>
              <select className="input" value={scheduleAway} onChange={(e) => setScheduleAway(e.target.value)}>
                {teams.map((t) => (
                  <option key={t.name} value={t.name}>{t.name}</option>
                ))}
              </select>
            </div>
            <div className="field">
              <label className="label">Date</label>
              <input className="input" type="date" value={scheduleDate} onChange={(e) => setScheduleDate(e.target.value)} />
            </div>
          </div>
          <div className="action-buttons">
            <button className="btn-primary" onClick={submitSchedule}>Add to schedule</button>
            <button className="btn-ghost" onClick={() => setSchedulePanelOpen(false)}>Cancel</button>
          </div>
        </div>
      )}

      {recordingGame && (
        <div className="action-panel">
          <h3 className="h3">Record score — {recordingGame.home} vs {recordingGame.away}</h3>
          <p className="hint">Marking a result recomputes standings immediately.</p>
          <div className="form-row">
            <div className="field grow">
              <label className="label">Home</label>
              <div className="static-value">{recordingGame.home}</div>
            </div>
            <div className="field score-field">
              <label className="label">Score</label>
              <input
                className="input score-input"
                type="number"
                min={0}
                value={recordHomeScore}
                onChange={(e) => setRecordHomeScore(parseInt(e.target.value || "0", 10))}
              />
            </div>
            <span className="dash">–</span>
            <div className="field score-field">
              <label className="label">Score</label>
              <input
                className="input score-input"
                type="number"
                min={0}
                value={recordAwayScore}
                onChange={(e) => setRecordAwayScore(parseInt(e.target.value || "0", 10))}
              />
            </div>
            <div className="field grow">
              <label className="label">Away</label>
              <div className="static-value">{recordingGame.away}</div>
            </div>
          </div>
          <div className="action-buttons">
            <button className="btn-primary" onClick={submitRecord}>Save result</button>
            <button className="btn-ghost" onClick={() => setRecordGameId(null)}>Cancel</button>
          </div>
        </div>
      )}
    </section>
  );
}
