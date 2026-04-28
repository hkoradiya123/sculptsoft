import { create } from 'zustand';
import { api } from '../lib/api';

const savedTheme = localStorage.getItem('ssc_theme') || 'light';
if (savedTheme === 'dark') {
  document.documentElement.classList.add('dark');
}

export const useAppStore = create((set, get) => ({
  token: localStorage.getItem('ssc_token') || '',
  user: JSON.parse(localStorage.getItem('ssc_user') || 'null'),
  players: [],
  matches: [],
  score: null,
  analytics: null,
  loading: false,
  theme: savedTheme,

  setTheme: (theme) => {
    if (theme === 'dark') document.documentElement.classList.add('dark');
    else document.documentElement.classList.remove('dark');
    localStorage.setItem('ssc_theme', theme);
    set({ theme });
  },

  login: async (email, password) => {
    const data = await api('/login', {
      method: 'POST',
      body: JSON.stringify({ email, password })
    });
    localStorage.setItem('ssc_token', data.token);
    localStorage.setItem('ssc_user', JSON.stringify(data.user));
    set({ token: data.token, user: data.user });
  },

  logout: () => {
    localStorage.removeItem('ssc_token');
    localStorage.removeItem('ssc_user');
    set({ token: '', user: null, players: [], matches: [], score: null, analytics: null });
  },

  loadPlayers: async () => {
    const { token } = get();
    const players = await api('/players', { token });
    set({ players });
  },

  savePlayer: async (payload, id) => {
    const { token } = get();
    if (id) {
      await api(`/players/${id}`, { method: 'PUT', token, body: JSON.stringify(payload) });
    } else {
      await api('/players', { method: 'POST', token, body: JSON.stringify(payload) });
    }
    await get().loadPlayers();
  },

  deletePlayer: async (id) => {
    const { token } = get();
    await api(`/players/${id}`, { method: 'DELETE', token });
    await get().loadPlayers();
  },

  loadMatches: async () => {
    const { token } = get();
    const matches = await api('/matches', { token });
    set({ matches });
  },

  createMatch: async (payload) => {
    const { token } = get();
    return api('/matches', { method: 'POST', token, body: JSON.stringify(payload) });
  },

  loadScore: async (matchId) => {
    const { token } = get();
    const score = await api(`/matches/${matchId}/score`, { token });
    set({ score });
    return score;
  },

  sendBall: async (matchId, payload) => {
    const { token } = get();
    const data = await api(`/matches/${matchId}/ball`, {
      method: 'POST',
      token,
      body: JSON.stringify(payload)
    });
    set({ score: { ...get().score, ...data } });
    return data;
  },

  undoBall: async (matchId) => {
    const { token } = get();
    await api(`/matches/${matchId}/ball/last`, { method: 'DELETE', token });
    await get().loadScore(matchId);
  },

  addPayment: async (payload) => {
    const { token } = get();
    return api('/payments', { method: 'POST', token, body: JSON.stringify(payload) });
  },

  loadAnalytics: async () => {
    const { token } = get();
    const analytics = await api('/analytics', { token });
    set({ analytics });
  }
}));
