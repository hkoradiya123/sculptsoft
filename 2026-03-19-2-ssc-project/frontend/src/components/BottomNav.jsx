import { NavLink } from 'react-router-dom';

const nav = [
  { to: '/', label: 'Home' },
  { to: '/matches', label: 'Matches' },
  { to: '/score', label: 'Score' },
  { to: '/players', label: 'Players' },
  { to: '/profile', label: 'Profile' }
];

export function BottomNav() {
  return (
    <nav className="fixed bottom-0 left-0 right-0 z-30 mx-auto w-full max-w-md border-t border-slate-200 bg-white/95 px-2 py-2 backdrop-blur md:top-4 md:bottom-auto md:max-w-3xl md:rounded-2xl md:border lg:max-w-4xl dark:border-slate-800 dark:bg-slate-950/95">
      <div className="grid grid-cols-5 gap-1 md:gap-2">
        {nav.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            className={({ isActive }) =>
              `rounded-xl px-2 py-3 text-center text-xs font-semibold transition md:text-sm ${
                isActive
                  ? 'bg-ember text-white'
                  : 'bg-slate-100 text-slate-600 dark:bg-slate-900 dark:text-slate-300'
              }`
            }
          >
            {item.label}
          </NavLink>
        ))}
      </div>
    </nav>
  );
}
