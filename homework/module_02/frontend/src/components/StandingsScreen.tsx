import type { StandingsRow } from "../types";
import { initials } from "../utils";

export function StandingsScreen({ rows }: { rows: StandingsRow[] }) {
  return (
    <section className="screen">
      <div className="panel-head">
        <div>
          <h2 className="h2">Standings</h2>
          <p className="sub">Ranked by points · win 3 · draw 1 · loss 0</p>
        </div>
      </div>
      <div className="board">
        <table className="table">
          <thead>
            <tr>
              <th className="th" style={{ width: 36 }} />
              <th className="th">Team</th>
              <th className="th num">P</th>
              <th className="th num">W</th>
              <th className="th num">D</th>
              <th className="th num">L</th>
              <th className="th num">Pts</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((r, i) => (
              <tr className="tr" key={r.name}>
                <td className="td num"><span className="rank">{i + 1}</span></td>
                <td className="td team-cell">
                  <span className="crest" style={{ background: r.color }}>{initials(r.name)}</span>
                  {r.name}
                </td>
                <td className="td num">{r.played}</td>
                <td className="td num">{r.won}</td>
                <td className="td num">{r.drawn}</td>
                <td className="td num">{r.lost}</td>
                <td className="td num pts">{r.points}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}
