import { useEffect } from 'react';
import { Bar, BarChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts';
import { MobileShell } from '../components/MobileShell';
import { useAppStore } from '../store/useAppStore';

export function AnalyticsPage() {
  const { analytics, loadAnalytics } = useAppStore();

  useEffect(() => {
    loadAnalytics();
  }, [loadAnalytics]);

  const revenueData = analytics
    ? [
        { name: 'Monthly', amount: analytics.revenue.monthly },
        { name: 'Guest', amount: analytics.revenue.guest }
      ]
    : [];

  return (
    <MobileShell title="Analytics">
      <div className="card">
        <p className="text-xs text-slate-500">Total Revenue</p>
        <p className="text-3xl font-black">INR {analytics?.revenue?.total || 0}</p>
      </div>

      <div className="card h-64">
        <h3 className="mb-2 font-bold">Revenue Mix</h3>
        <ResponsiveContainer width="100%" height="90%">
          <BarChart data={revenueData}>
            <XAxis dataKey="name" />
            <YAxis />
            <Tooltip />
            <Bar dataKey="amount" fill="#ff6b35" radius={[8, 8, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>

      <div className="card">
        <h3 className="mb-2 font-bold">Top Players</h3>
        <div className="space-y-2">
          {(analytics?.topPlayers || []).map((p) => (
            <div key={p.playerId} className="rounded-xl bg-slate-100 p-3 text-sm dark:bg-slate-800">
              <p className="font-bold">{p.name}</p>
              <p className="text-xs text-slate-500">Runs: {p.runs} • SR: {p.strikeRate}</p>
            </div>
          ))}
        </div>
      </div>
    </MobileShell>
  );
}
