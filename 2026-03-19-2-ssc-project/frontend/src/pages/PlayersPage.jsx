import { useEffect, useState } from 'react';
import { MobileShell } from '../components/MobileShell';
import { useAppStore } from '../store/useAppStore';

const initialForm = { name: '', phone: '', role: 'BATSMAN', type: 'MEMBER' };

export function PlayersPage() {
  const { players, loadPlayers, savePlayer, deletePlayer } = useAppStore();
  const [form, setForm] = useState(initialForm);
  const [editingId, setEditingId] = useState('');

  useEffect(() => {
    loadPlayers();
  }, [loadPlayers]);

  const submit = async (e) => {
    e.preventDefault();
    await savePlayer(form, editingId || undefined);
    setForm(initialForm);
    setEditingId('');
  };

  const togglePlayerType = async (player) => {
    const newType = player.type === 'MEMBER' ? 'GUEST' : 'MEMBER';
    await savePlayer({ name: player.name, phone: player.phone, role: player.role, type: newType }, player._id);
  };

  return (
    <MobileShell title="Players">
      <form onSubmit={submit} className="card space-y-3">
        <input className="input" placeholder="Name" value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} />
        <input className="input" placeholder="Phone" value={form.phone} onChange={(e) => setForm({ ...form, phone: e.target.value })} />
        <select className="input" value={form.role} onChange={(e) => setForm({ ...form, role: e.target.value })}>
          <option value="BATSMAN">Batsman</option>
          <option value="BOWLER">Bowler</option>
          <option value="ALL_ROUNDER">All-rounder</option>
        </select>
        <select className="input" value={form.type} onChange={(e) => setForm({ ...form, type: e.target.value })}>
          <option value="MEMBER">Member</option>
          <option value="GUEST">Guest</option>
        </select>
        <button className="btn-primary w-full">{editingId ? 'Update Player' : 'Add Player'}</button>
      </form>

      <div className="space-y-3">
        {players.map((player) => (
          <div key={player._id} className="card">
            <div className="flex items-center justify-between">
              <div>
                <p className="font-bold">{player.name}</p>
                <p className="text-xs text-slate-500">
                  {player.phone} • {player.role} • <span className={player.type === 'GUEST' ? 'text-orange-500' : 'text-green-600'}>{player.type}</span>
                </p>
              </div>
              <div className="flex gap-2">
                <button
                  className={`rounded-lg px-3 py-2 text-xs font-bold transition ${
                    player.type === 'GUEST' ? 'bg-orange-100 text-orange-700 dark:bg-orange-900 dark:text-orange-200' : 'bg-green-100 text-green-700 dark:bg-green-900 dark:text-green-200'
                  }`}
                  onClick={() => togglePlayerType(player)}
                >
                  {player.type === 'GUEST' ? 'Guest' : 'Member'}
                </button>
                <button
                  className="rounded-lg bg-slate-200 px-3 py-2 text-xs font-bold dark:bg-slate-700"
                  onClick={() => {
                    setEditingId(player._id);
                    setForm({ name: player.name, phone: player.phone, role: player.role, type: player.type });
                  }}
                >
                  Edit
                </button>
                <button className="rounded-lg bg-red-500 px-3 py-2 text-xs font-bold text-white" onClick={() => deletePlayer(player._id)}>
                  Delete
                </button>
              </div>
            </div>
          </div>
        ))}
      </div>
    </MobileShell>
  );
}
