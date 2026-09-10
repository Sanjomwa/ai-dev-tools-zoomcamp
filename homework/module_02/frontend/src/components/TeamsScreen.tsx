import { useState } from "react";
import type { Team, StandingsRow } from "../types";
import { initials } from "../utils";

interface Props {
  teams: Team[];
  rows: StandingsRow[];
  onAddTeam: (name: string) => Promise<void>;
}

export function TeamsScreen({ teams, rows, onAddTeam }: Props) {
  const [panelOpen, setPanelOpen] = useState(false);
  const [name, setName] = useState("");

  async function submit() {
    const trimmed = name.trim();
    if (!trimmed) return;
    await onAddTeam(trimmed);
    setName("");
    setPanelOpen(false);
  }

  return (
    <section className="screen">
      <div className="panel-head">
        <div>
          <h2 className="h2">Teams</h2>
          <p className="sub">{teams.length} teams in this league</p>
        </div>
        <button className="btn-primary" onClick={() => setPanelOpen((o) => !o)}>+ Add team</button>
      </div>

      <div className="teams-grid">
        {teams.map((t) => {
          const row = rows.find((r) => r.name === t.name);
          return (
            <div className="team-card" key={t.name}>
              <div className="team-top">
                <span className="crest" style={{ background: t.color }}>{initials(t.name)}</span>
                <span className="team-name">{t.name}</span>
              </div>
              <div className="team-stats">
                <span><b>{row?.played ?? 0}</b> played</span>
                <span><b>{row?.points ?? 0}</b> pts</span>
              </div>
            </div>
          );
        })}
      </div>

      {panelOpen && (
        <div className="action-panel">
          <h3 className="h3">Add a team</h3>
          <p className="hint">Name only — joins the standings at 0 played.</p>
          <div className="form-row">
            <div className="field grow">
              <label className="label">Team name</label>
              <input
                className="input"
                type="text"
                placeholder="e.g. Foxglove Athletic"
                value={name}
                onChange={(e) => setName(e.target.value)}
              />
            </div>
          </div>
          <div className="action-buttons">
            <button className="btn-primary" onClick={submit}>Add team</button>
            <button className="btn-ghost" onClick={() => setPanelOpen(false)}>Cancel</button>
          </div>
        </div>
      )}
    </section>
  );
}
