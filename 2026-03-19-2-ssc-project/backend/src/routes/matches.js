const express = require('express');
const { z } = require('zod');
const Match = require('../models/Match');
const Payment = require('../models/Payment');
const Ball = require('../models/Ball');
const { auth, allowRoles } = require('../middleware/auth');
const { validateBody } = require('../middleware/validate');
const { hasMonthlyPayment } = require('../services/paymentService');
const { overFromLegalBalls } = require('../services/scoringEngine');

const router = express.Router();

const createMatchSchema = z.object({
  date: z.coerce.date(),
  teamA: z.array(z.string()).min(1),
  teamB: z.array(z.string()).min(1),
  overs: z.number().int().min(1),
  guestPlayerIds: z.array(z.string()).optional().default([]),
  striker: z.string().optional(),
  nonStriker: z.string().optional()
});

router.get('/matches', auth, async (req, res) => {
  const matches = await Match.find().populate('teamA', 'name').populate('teamB', 'name').sort({ date: -1 });
  res.json(matches);
});

router.post('/matches', auth, allowRoles('ADMIN'), validateBody(createMatchSchema), async (req, res) => {
  const payload = req.body;
  const allPlayerIds = [...payload.teamA, ...payload.teamB];
  const guestSet = new Set(payload.guestPlayerIds || []);

  const unpaid = [];
  for (const playerId of allPlayerIds) {
    const monthlyPaid = await hasMonthlyPayment(playerId, payload.date);
    if (!monthlyPaid && !guestSet.has(String(playerId))) {
      unpaid.push(playerId);
    }
  }

  if (unpaid.length > 0) {
    return res.status(402).json({
      message: 'Some players are unpaid. Pay monthly or mark as guest to charge INR 200.',
      unpaid
    });
  }

  const match = await Match.create({
    date: payload.date,
    teamA: payload.teamA,
    teamB: payload.teamB,
    overs: payload.overs,
    batting: {
      striker: payload.striker || null,
      nonStriker: payload.nonStriker || null
    }
  });

  if (guestSet.size > 0) {
    const docs = Array.from(guestSet).map((playerId) => ({
      player_id: playerId,
      type: 'MATCH',
      amount: 200,
      match_id: match._id,
      date: payload.date
    }));
    await Payment.insertMany(docs);
  }

  return res.status(201).json(match);
});

router.get('/matches/:id/score', auth, async (req, res) => {
  const match = await Match.findById(req.params.id).populate('batting.striker batting.nonStriker', 'name');
  if (!match) return res.status(404).json({ message: 'Match not found' });

  const balls = await Ball.find({ match_id: match._id }).sort({ createdAt: 1 });

  return res.json({
    matchId: match._id,
    score: match.scoreState,
    overs: overFromLegalBalls(match.scoreState.legalBalls),
    striker: match.batting.striker,
    nonStriker: match.batting.nonStriker,
    recentBalls: balls.slice(-18)
  });
});

module.exports = router;
