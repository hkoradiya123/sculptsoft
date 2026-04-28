const mongoose = require('mongoose');

const matchSchema = new mongoose.Schema(
  {
    date: { type: Date, required: true },
    teamA: [{ type: mongoose.Schema.Types.ObjectId, ref: 'Player' }],
    teamB: [{ type: mongoose.Schema.Types.ObjectId, ref: 'Player' }],
    overs: { type: Number, required: true, min: 1 },
    status: { type: String, enum: ['LIVE', 'COMPLETED'], default: 'LIVE' },
    batting: {
      striker: { type: mongoose.Schema.Types.ObjectId, ref: 'Player', default: null },
      nonStriker: { type: mongoose.Schema.Types.ObjectId, ref: 'Player', default: null }
    },
    scoreState: {
      runs: { type: Number, default: 0 },
      wickets: { type: Number, default: 0 },
      legalBalls: { type: Number, default: 0 },
      extras: { type: Number, default: 0 },
      runRate: { type: Number, default: 0 },
      nextBallFreeHit: { type: Boolean, default: false }
    }
  },
  { timestamps: true }
);

module.exports = mongoose.model('Match', matchSchema);
