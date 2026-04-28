import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAppStore } from '../store/useAppStore';

export function LoginPage() {
  const login = useAppStore((s) => s.login);
  const [email, setEmail] = useState('admin@ssc.local');
  const [password, setPassword] = useState('admin123456');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const submit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      await login(email, password);
      navigate('/');
    } catch (err) {
      setError(err.message || 'Login failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="mx-auto flex min-h-screen max-w-md items-center justify-center bg-gradient-to-b from-ink to-slate px-6 text-white">
      <form onSubmit={submit} className="w-full rounded-3xl bg-white/10 p-6 backdrop-blur">
        <h1 className="mb-2 text-2xl font-black">SSC Cricket</h1>
        <p className="mb-6 text-sm text-slate-200">Sign in to manage matches, players and scoring</p>
        <label className="mb-3 block text-sm">Email</label>
        <input className="input mb-4 text-slate-900" value={email} onChange={(e) => setEmail(e.target.value)} />
        <label className="mb-3 block text-sm">Password</label>
        <input
          type="password"
          className="input mb-4 text-slate-900"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
        />
        {error && <p className="mb-3 text-sm text-red-300">{error}</p>}
        <button className="btn-primary w-full" disabled={loading}>
          {loading ? 'Signing in...' : 'Login'}
        </button>
      </form>
    </div>
  );
}
