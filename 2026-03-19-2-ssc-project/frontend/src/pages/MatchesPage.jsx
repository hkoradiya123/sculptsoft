import { useEffect, useState } from 'react';
import { MobileShell } from '../components/MobileShell';
import { useAppStore } from '../store/useAppStore';

export function MatchesPage() {
  const { players, matches, loadPlayers, loadMatches, createMatch } = useAppStore();
  const [form, setForm] = useState({ date: '', teamA: [], teamB: [], overs: 10, guestPlayerIds: [] });
  const [error, setError] = useState('');

  useEffect(() => {
    loadPlayers();
    loadMatches();
  }, [loadPlayers, loadMatches]);

  const toggleTeam = (teamKey, playerId) => {
    setForm((prev) => ({
      ...prev,
      [teamKey]: prev[teamKey].includes(playerId)
        ? prev[teamKey].filter((id) => id !== playerId)
        : [...prev[teamKey], playerId]
    }));
  };

  const toggleGuest = (playerId) => {
    setForm((prev) => ({
      ...prev,
      guestPlayerIds: prev.guestPlayerIds.includes(playerId)
        ? prev.guestPlayerIds.filter((id) => id !== playerId)
        : [...prev.guestPlayerIds, playerId]
    }));
  };

  const submit = async (e) => {
    e.preventDefault();
    setError('');
    try {
      await createMatch({ ...form, date: form.date || new Date().toISOString() });
      await loadMatches();
    } catch (err) {
      setError(err.payload?.message || err.message);
    }
  };

  return (
    <MobileShell title="Matches">
      <form onSubmit={submit} className="card space-y-3">
        <input type="date" className="input" value={form.date} onChange={(e) => setForm({ ...form, date: e.target.value })} />
        <input type="number" min="1" className="input" value={form.overs} onChange={(e) => setForm({ ...form, overs: Number(e.target.value) })} />

        <div>
          <p className="mb-2 text-sm font-bold">Team A</p>
          <div className="grid grid-cols-2 gap-2">
            {players.map((p) => {
              const isInTeamB = form.teamB.includes(p._id);
              const isSelected = form.teamA.includes(p._id);
              return (
                <button
                  key={`a-${p._id}`}
                  type="button"
                  disabled={isInTeamB}
                  onClick={() => toggleTeam('teamA', p._id)}
                  className={`rounded-lg p-2 text-xs font-semibold transition ${
                    isSelected
                      ? 'bg-ember text-white'
                      : isInTeamB
                        ? 'cursor-not-allowed bg-slate-300 text-slate-400 dark:bg-slate-600'
                        : 'bg-slate-200 dark:bg-slate-700'
                  }`}
                >
                  {p.name}
                </button>
              );
            })}
          </div>
        </div>

        <div>
          <p className="mb-2 text-sm font-bold">Team B</p>
          <div className="grid grid-cols-2 gap-2">
            {players.map((p) => {
              const isInTeamA = form.teamA.includes(p._id);
              const isSelected = form.teamB.includes(p._id);
              return (
                <button
                  key={`b-${p._id}`}
                  type="button"
                  disabled={isInTeamA}
                  onClick={() => toggleTeam('teamB', p._id)}
                  className={`rounded-lg p-2 text-xs font-semibold transition ${
                    isSelected
                      ? 'bg-mint text-ink'
                      : isInTeamA
                        ? 'cursor-not-allowed bg-slate-300 text-slate-400 dark:bg-slate-600'
                        : 'bg-slate-200 dark:bg-slate-700'
                  }`}
                >
                  {p.name}
                </button>
              );
            })}
          </div>
        </div>

        <div>
          <p className="mb-2 text-sm font-bold">Guest Players (INR 200)</p>
          <div className="grid grid-cols-2 gap-2">
            {players.map((p) => {
              const isInAnyTeam = form.teamA.includes(p._id) || form.teamB.includes(p._id);
              const isSelected = form.guestPlayerIds.includes(p._id);
              return (
                <button
                  key={`g-${p._id}`}
                  type="button"
                  disabled={isInAnyTeam}
                  onClick={() => toggleGuest(p._id)}
                  className={`rounded-lg p-2 text-xs font-semibold transition ${
                    isSelected
                      ? 'bg-slate-900 text-white dark:bg-white dark:text-slate-900'
                      : isInAnyTeam
                        ? 'cursor-not-allowed bg-slate-300 text-slate-400 dark:bg-slate-600'
                        : 'bg-slate-200 dark:bg-slate-700'
                  }`}
                >
                  {p.name}
                </button>
              );
            })}
          </div>
        </div>

        {error && <p className="text-sm text-red-500">{error}</p>}
        <button className="btn-primary w-full">Create Match</button>
      </form>

      <div className="space-y-2">
        {matches.map((m) => (
          <div key={m._id} className="card text-sm">
            <p className="font-bold">{new Date(m.date).toLocaleDateString()}</p>
            <p className="text-xs text-slate-500">{m.overs} overs • {m.status}</p>
          </div>
        ))}
      </div>
    </MobileShell>
  );
}
