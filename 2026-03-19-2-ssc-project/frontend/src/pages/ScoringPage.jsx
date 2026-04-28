import { useEffect, useMemo, useState } from 'react';
import { io } from 'socket.io-client';
import { MobileShell } from '../components/MobileShell';
import { useAppStore } from '../store/useAppStore';
import { API_BASE } from '../lib/api';

const socketBase = API_BASE.replace('/api', '');

export function ScoringPage() {
  const { matches, score, loadMatches, loadScore, sendBall, undoBall } = useAppStore();
  const [matchId, setMatchId] = useState('');
  const [ball, setBall] = useState({
    runs_off_bat: 0,
    extra_type: 'NONE',
    extra_runs: 0,
    is_wicket: false,
    wicket_type: null,
    striker: '',
    nonStriker: ''
  });

  useEffect(() => {
    loadMatches();
  }, [loadMatches]);

  useEffect(() => {
    if (!matchId) return;
    loadScore(matchId);

    const socket = io(socketBase);
    socket.emit('score:join', matchId);
    socket.on('score:update', () => {
      loadScore(matchId);
    });

    return () => socket.disconnect();
  }, [matchId, loadScore]);

  const selectedMatch = useMemo(() => matches.find((m) => m._id === matchId), [matches, matchId]);

  return (
    <MobileShell title="Live Score">
      <div className="card space-y-3">
        <select className="input" value={matchId} onChange={(e) => setMatchId(e.target.value)}>
          <option value="">Select match</option>
          {matches.map((m) => (
            <option value={m._id} key={m._id}>
              {new Date(m.date).toLocaleDateString()} ({m.status})
            </option>
          ))}
        </select>

        {selectedMatch && (
          <p className="text-xs text-slate-500">
            Match: {selectedMatch.overs} overs • Status {selectedMatch.status}
          </p>
        )}
      </div>

      {matchId && (
        <>
          <div className="card grid grid-cols-3 gap-3 text-center">
            <div>
              <p className="text-xs text-slate-500">Runs</p>
              <p className="text-3xl font-black">{score?.score?.runs ?? 0}</p>
            </div>
            <div>
              <p className="text-xs text-slate-500">Wkts</p>
              <p className="text-3xl font-black">{score?.score?.wickets ?? 0}</p>
            </div>
            <div>
              <p className="text-xs text-slate-500">Overs</p>
              <p className="text-3xl font-black">{score?.overs ?? '0.0'}</p>
            </div>
          </div>

          <div className="card space-y-3">
            <div className="grid grid-cols-4 gap-2">
              {[0, 1, 2, 3, 4, 6].map((r) => (
                <button
                  key={r}
                  onClick={() => setBall((prev) => ({ ...prev, runs_off_bat: r }))}
                  className={`rounded-xl p-3 font-bold ${
                    ball.runs_off_bat === r ? 'bg-ember text-white' : 'bg-slate-200 dark:bg-slate-700'
                  }`}
                >
                  {r}
                </button>
              ))}
            </div>

            <select className="input" value={ball.extra_type} onChange={(e) => setBall({ ...ball, extra_type: e.target.value })}>
              <option value="NONE">None</option>
              <option value="WIDE">Wide</option>
              <option value="NO_BALL">No Ball</option>
              <option value="BYE">Bye</option>
              <option value="LEG_BYE">Leg Bye</option>
            </select>

            <input
              className="input"
              type="number"
              min="0"
              value={ball.extra_runs}
              onChange={(e) => setBall({ ...ball, extra_runs: Number(e.target.value) })}
              placeholder="Extra runs"
            />

            <div className="grid grid-cols-2 gap-2">
              <input className="input" placeholder="Striker ID (first ball only)" value={ball.striker} onChange={(e) => setBall({ ...ball, striker: e.target.value })} />
              <input className="input" placeholder="Non-striker ID" value={ball.nonStriker} onChange={(e) => setBall({ ...ball, nonStriker: e.target.value })} />
            </div>

            <label className="flex items-center gap-2 text-sm">
              <input type="checkbox" checked={ball.is_wicket} onChange={(e) => setBall({ ...ball, is_wicket: e.target.checked })} />
              Wicket
            </label>

            {ball.is_wicket && (
              <select className="input" value={ball.wicket_type || 'BOWLED'} onChange={(e) => setBall({ ...ball, wicket_type: e.target.value })}>
                <option value="BOWLED">Bowled</option>
                <option value="CAUGHT">Caught</option>
                <option value="RUNOUT">Runout</option>
              </select>
            )}

            <button className="btn-primary w-full" onClick={() => sendBall(matchId, ball)}>
              Submit Ball
            </button>
            <button className="w-full rounded-xl bg-slate-300 py-3 text-sm font-bold dark:bg-slate-700" onClick={() => undoBall(matchId)}>
              Undo Last Ball
            </button>
          </div>

          <div className="card">
            <h3 className="mb-2 font-bold">Recent Balls</h3>
            <div className="grid grid-cols-6 gap-2 text-center text-xs">
              {(score?.recentBalls || []).slice(-12).map((b) => (
                <div key={b._id} className="rounded-lg bg-slate-200 p-2 dark:bg-slate-800">
                  {b.total_runs}
                  {b.is_wicket ? 'W' : ''}
                </div>
              ))}
            </div>
          </div>
        </>
      )}
    </MobileShell>
  );
}
