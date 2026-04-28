const express = require('express');
const Payment = require('../models/Payment');
const Ball = require('../models/Ball');
const Player = require('../models/Player');
const { auth } = require('../middleware/auth');

const router = express.Router();

router.get('/analytics', auth, async (req, res) => {
  const [payments, balls, players] = await Promise.all([
    Payment.find().populate('player_id', 'name'),
    Ball.find(),
    Player.find({ active: true })
  ]);

  const revenue = payments.reduce(
    (acc, p) => {
      acc.total += p.amount;
      if (p.type === 'MONTHLY') acc.monthly += p.amount;
      if (p.type === 'MATCH') acc.guest += p.amount;
      return acc;
    },
    { total: 0, monthly: 0, guest: 0 }
  );

  const statsMap = new Map();
  for (const player of players) {
    statsMap.set(String(player._id), {
      playerId: player._id,
      name: player.name,
      runs: 0,
      wickets: 0,
      ballsFaced: 0,
      ballsBowled: 0,
      runsConceded: 0
    });
  }

  for (const ball of balls) {
    const strikerId = String(ball.striker_before || '');
    if (statsMap.has(strikerId)) {
      const s = statsMap.get(strikerId);
      const runsToBatsman = ['BYE', 'LEG_BYE', 'WIDE'].includes(ball.extra_type) ? 0 : ball.runs_off_bat;
      s.runs += runsToBatsman;
      if (ball.legal_delivery) s.ballsFaced += 1;
    }
  }

  const playerStats = Array.from(statsMap.values()).map((s) => ({
    ...s,
    strikeRate: s.ballsFaced > 0 ? Number(((s.runs / s.ballsFaced) * 100).toFixed(2)) : 0,
    economy: s.ballsBowled > 0 ? Number((s.runsConceded / (s.ballsBowled / 6)).toFixed(2)) : 0
  }));

  const topPlayers = [...playerStats].sort((a, b) => b.runs - a.runs).slice(0, 5);

  res.json({
    revenue,
    topPlayers,
    playerStats
  });
});

module.exports = router;
