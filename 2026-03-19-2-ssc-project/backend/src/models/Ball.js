const mongoose = require('mongoose');

const ballSchema = new mongoose.Schema(
  {
    match_id: { type: mongoose.Schema.Types.ObjectId, ref: 'Match', required: true, index: true },
    over: { type: Number, required: true },
    ball_number: { type: Number, required: true },
    runs_off_bat: { type: Number, required: true, min: 0, max: 6 },
    extra_type: {
      type: String,
      enum: ['NONE', 'WIDE', 'NO_BALL', 'BYE', 'LEG_BYE'],
      default: 'NONE'
    },
    extra_runs: { type: Number, default: 0, min: 0 },
    is_wicket: { type: Boolean, default: false },
    wicket_type: {
      type: String,
      enum: ['BOWLED', 'CAUGHT', 'RUNOUT', null],
      default: null
    },
    is_free_hit: { type: Boolean, default: false },
    striker_before: { type: mongoose.Schema.Types.ObjectId, ref: 'Player', default: null },
    non_striker_before: { type: mongoose.Schema.Types.ObjectId, ref: 'Player', default: null },
    total_runs: { type: Number, required: true },
    legal_delivery: { type: Boolean, required: true }
  },
  { timestamps: true }
);

module.exports = mongoose.model('Ball', ballSchema);
