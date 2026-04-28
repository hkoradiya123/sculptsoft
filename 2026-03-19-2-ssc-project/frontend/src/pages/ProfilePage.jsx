import { MobileShell } from '../components/MobileShell';
import { useAppStore } from '../store/useAppStore';

export function ProfilePage() {
  const { user, logout, theme, setTheme } = useAppStore();

  return (
    <MobileShell title="Profile">
      <div className="card">
        <p className="text-xs text-slate-500">Logged in as</p>
        <p className="text-lg font-bold">{user?.email}</p>
        <p className="text-sm">Role: {user?.role}</p>
      </div>

      <div className="card">
        <h3 className="mb-3 font-bold">Appearance</h3>
        <div className="grid grid-cols-2 gap-2">
          <button
            onClick={() => setTheme('light')}
            className={`rounded-xl p-3 text-sm font-bold ${theme === 'light' ? 'bg-ember text-white' : 'bg-slate-200 dark:bg-slate-700'}`}
          >
            Light
          </button>
          <button
            onClick={() => setTheme('dark')}
            className={`rounded-xl p-3 text-sm font-bold ${theme === 'dark' ? 'bg-ember text-white' : 'bg-slate-200 dark:bg-slate-700'}`}
          >
            Dark
          </button>
        </div>
      </div>

      <button className="btn-primary w-full" onClick={logout}>
        Logout
      </button>
    </MobileShell>
  );
}
