const express = require('express');
const { z } = require('zod');
const Player = require('../models/Player');
const { auth, allowRoles } = require('../middleware/auth');
const { validateBody } = require('../middleware/validate');

const router = express.Router();

const playerSchema = z.object({
  name: z.string().min(2),
  phone: z.string().min(8),
  role: z.enum(['BATSMAN', 'BOWLER', 'ALL_ROUNDER']),
  type: z.enum(['MEMBER', 'GUEST']).optional(),
  join_date: z.coerce.date().optional()
});

router.get('/players', auth, async (req, res) => {
  const players = await Player.find({ active: true }).sort({ name: 1 });
  res.json(players);
});

router.post('/players', auth, allowRoles('ADMIN'), validateBody(playerSchema), async (req, res) => {
  const player = await Player.create(req.body);
  res.status(201).json(player);
});

router.put('/players/:id', auth, allowRoles('ADMIN'), validateBody(playerSchema), async (req, res) => {
  const updated = await Player.findByIdAndUpdate(req.params.id, req.body, { new: true });
  if (!updated) return res.status(404).json({ message: 'Player not found' });
  return res.json(updated);
});

router.delete('/players/:id', auth, allowRoles('ADMIN'), async (req, res) => {
  const deleted = await Player.findByIdAndUpdate(req.params.id, { active: false }, { new: true });
  if (!deleted) return res.status(404).json({ message: 'Player not found' });
  return res.json({ message: 'Player deleted' });
});

module.exports = router;
