const express = require('express');
const { z } = require('zod');
const Match = require('../models/Match');
const Ball = require('../models/Ball');
const { auth, allowRoles } = require('../middleware/auth');
const { validateBody } = require('../middleware/validate');
const { applyBall, overFromLegalBalls } = require('../services/scoringEngine');

const router = express.Router();

const ballSchema = z.object({
  runs_off_bat: z.number().int().min(0).max(6),
  extra_type: z.enum(['NONE', 'WIDE', 'NO_BALL', 'BYE', 'LEG_BYE']).default('NONE'),
  extra_runs: z.number().int().min(0).default(0),
  is_wicket: z.boolean().default(false),
  wicket_type: z.enum(['BOWLED', 'CAUGHT', 'RUNOUT']).nullable().optional(),
  striker: z.string().optional(),
  nonStriker: z.string().optional()
});

router.post('/matches/:id/ball', auth, allowRoles('ADMIN'), validateBody(ballSchema), async (req, res) => {
  const match = await Match.findById(req.params.id);
  if (!match) return res.status(404).json({ message: 'Match not found' });

  if (!match.batting.striker || !match.batting.nonStriker) {
    if (!req.body.striker || !req.body.nonStriker) {
      return res.status(400).json({ message: 'Initial striker and non-striker are required.' });
    }
    match.batting.striker = req.body.striker;
    match.batting.nonStriker = req.body.nonStriker;
  }

  const result = applyBall(match, req.body);

  const ball = await Ball.create({
    match_id: match._id,
    over: result.scoring.over,
    ball_number: result.scoring.ball_number,
    runs_off_bat: req.body.runs_off_bat,
    extra_type: req.body.extra_type,
    extra_runs: req.body.extra_runs,
    is_wicket: result.scoring.is_wicket,
    wicket_type: result.scoring.wicket_type,
    is_free_hit: result.scoring.is_free_hit,
    striker_before: match.batting.striker,
    non_striker_before: match.batting.nonStriker,
    total_runs: result.scoring.total_runs,
    legal_delivery: result.scoring.legal_delivery
  });

  match.scoreState = result.matchUpdate.scoreState;
  match.batting = result.matchUpdate.batting;

  if (match.scoreState.legalBalls >= match.overs * 6) {
    match.status = 'COMPLETED';
  }

  await match.save();

  const payload = {
    matchId: match._id,
    score: match.scoreState,
    overs: overFromLegalBalls(match.scoreState.legalBalls),
    striker: match.batting.striker,
    nonStriker: match.batting.nonStriker,
    latestBall: ball
  };

  req.io.to(String(match._id)).emit('score:update', payload);

  return res.status(201).json(payload);
});

router.delete('/matches/:id/ball/last', auth, allowRoles('ADMIN'), async (req, res) => {
  const match = await Match.findById(req.params.id);
  if (!match) return res.status(404).json({ message: 'Match not found' });

  const lastBall = await Ball.findOne({ match_id: match._id }).sort({ createdAt: -1 });
  if (!lastBall) return res.status(400).json({ message: 'No ball to undo' });

  await Ball.deleteOne({ _id: lastBall._id });

  const balls = await Ball.find({ match_id: match._id }).sort({ createdAt: 1 });

  match.scoreState = {
    runs: 0,
    wickets: 0,
    legalBalls: 0,
    extras: 0,
    runRate: 0,
    nextBallFreeHit: false
  };

  for (const b of balls) {
    match.scoreState.runs += b.total_runs;
    match.scoreState.extras += ['WIDE', 'NO_BALL', 'BYE', 'LEG_BYE'].includes(b.extra_type)
      ? b.extra_runs + (['WIDE', 'NO_BALL'].includes(b.extra_type) ? 1 : 0)
      : 0;
    match.scoreState.wickets += b.is_wicket ? 1 : 0;
    match.scoreState.legalBalls += b.legal_delivery ? 1 : 0;
    match.scoreState.nextBallFreeHit = b.extra_type === 'NO_BALL';
  }

  match.scoreState.runRate =
    match.scoreState.legalBalls > 0
      ? Number((match.scoreState.runs / (match.scoreState.legalBalls / 6)).toFixed(2))
      : 0;

  match.status = 'LIVE';
  await match.save();

  const payload = {
    matchId: match._id,
    score: match.scoreState,
    overs: overFromLegalBalls(match.scoreState.legalBalls)
  };

  req.io.to(String(match._id)).emit('score:update', payload);

  return res.json(payload);
});

module.exports = router;
