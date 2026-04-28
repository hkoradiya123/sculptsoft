const express = require('express');
const { z } = require('zod');
const Payment = require('../models/Payment');
const { auth, allowRoles } = require('../middleware/auth');
const { validateBody } = require('../middleware/validate');

const router = express.Router();

const paymentSchema = z.object({
  player_id: z.string(),
  type: z.enum(['MONTHLY', 'MATCH']),
  amount: z.number().positive(),
  match_id: z.string().optional(),
  date: z.coerce.date().optional()
});

router.get('/payments', auth, async (req, res) => {
  const payments = await Payment.find().populate('player_id', 'name role').populate('match_id');
  res.json(payments);
});

router.post('/payments', auth, allowRoles('ADMIN'), validateBody(paymentSchema), async (req, res) => {
  const payment = await Payment.create(req.body);
  res.status(201).json(payment);
});

module.exports = router;
