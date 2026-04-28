import { Link } from 'react-router-dom';
import { useEffect } from 'react';
import { MobileShell } from '../components/MobileShell';
import { useAppStore } from '../store/useAppStore';

export function DashboardPage() {
  const loadPlayers = useAppStore((s) => s.loadPlayers);
  const loadMatches = useAppStore((s) => s.loadMatches);
  const players = useAppStore((s) => s.players);
  const matches = useAppStore((s) => s.matches);

  useEffect(() => {
    loadPlayers();
    loadMatches();
  }, [loadPlayers, loadMatches]);

  return (
    <MobileShell title="Dashboard">
      <div className="grid grid-cols-2 gap-3 fade-in">
        <div className="card">
          <p className="text-xs text-slate-500">Players</p>
          <p className="text-3xl font-black">{players.length}</p>
        </div>
        <div className="card">
          <p className="text-xs text-slate-500">Matches</p>
          <p className="text-3xl font-black">{matches.length}</p>
        </div>
      </div>
      <div className="card fade-in">
        <h2 className="mb-3 text-lg font-bold">Quick Actions</h2>
        <div className="grid grid-cols-2 gap-3">
          <Link to="/matches" className="btn-primary text-center">
            Create Match
          </Link>
          <Link to="/score" className="btn-secondary text-center">
            Start Scoring
          </Link>
          <Link to="/players" className="rounded-xl bg-slate-200 px-4 py-3 text-center text-sm font-bold dark:bg-slate-700">
            Players
          </Link>
          <Link to="/analytics" className="rounded-xl bg-slate-200 px-4 py-3 text-center text-sm font-bold dark:bg-slate-700">
            Analytics
          </Link>
        </div>
      </div>
      <div className="card fade-in">
        <h2 className="mb-2 text-lg font-bold">Recent Matches</h2>
        <div className="space-y-2">
          {matches.slice(0, 5).map((m) => (
            <div key={m._id} className="rounded-xl bg-slate-100 p-3 text-sm dark:bg-slate-800">
              {new Date(m.date).toLocaleDateString()} • {m.overs} overs • {m.status}
            </div>
          ))}
          {matches.length === 0 && <p className="text-sm text-slate-500">No matches yet.</p>}
        </div>
      </div>
    </MobileShell>
  );
}
