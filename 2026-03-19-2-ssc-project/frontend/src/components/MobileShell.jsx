import { BottomNav } from './BottomNav';

export function MobileShell({ title, actions, children }) {
  return (
    <div className="min-h-screen bg-gradient-to-b from-sand to-white text-slate-900 dark:from-ink dark:to-slate dark:text-white">
      <div className="mx-auto w-full max-w-md px-4 pb-24 pt-4 md:max-w-3xl md:px-6 md:pt-24 lg:max-w-6xl lg:px-8 lg:pb-10">
      <header className="mb-4 flex items-center justify-between md:mb-6">
        <h1 className="text-xl font-black tracking-tight md:text-2xl">{title}</h1>
        <div>{actions}</div>
      </header>
      <main className="space-y-4 md:space-y-5">{children}</main>
      </div>
      <BottomNav />
    </div>
  );
}
