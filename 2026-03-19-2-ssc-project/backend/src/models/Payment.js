const mongoose = require('mongoose');

const paymentSchema = new mongoose.Schema(
  {
    player_id: { type: mongoose.Schema.Types.ObjectId, ref: 'Player', required: true },
    type: { type: String, enum: ['MONTHLY', 'MATCH'], required: true },
    amount: { type: Number, required: true },
    match_id: { type: mongoose.Schema.Types.ObjectId, ref: 'Match', default: null },
    date: { type: Date, default: Date.now }
  },
  { timestamps: true }
);

module.exports = mongoose.model('Payment', paymentSchema);
