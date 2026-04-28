const mongoose = require('mongoose');

const playerSchema = new mongoose.Schema(
  {
    name: { type: String, required: true, trim: true },
    phone: { type: String, required: true, trim: true },
    role: {
      type: String,
      enum: ['BATSMAN', 'BOWLER', 'ALL_ROUNDER'],
      required: true
    },
    type: { type: String, enum: ['MEMBER', 'GUEST'], default: 'MEMBER' },
    join_date: { type: Date, default: Date.now },
    active: { type: Boolean, default: true }
  },
  { timestamps: true }
);

module.exports = mongoose.model('Player', playerSchema);
