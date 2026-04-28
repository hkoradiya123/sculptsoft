const Payment = require('../models/Payment');

function getMonthRange(inputDate) {
  const date = new Date(inputDate);
  const start = new Date(date.getFullYear(), date.getMonth(), 1);
  const end = new Date(date.getFullYear(), date.getMonth() + 1, 0, 23, 59, 59, 999);
  return { start, end };
}

async function hasMonthlyPayment(playerId, forDate) {
  const { start, end } = getMonthRange(forDate);
  const payment = await Payment.findOne({
    player_id: playerId,
    type: 'MONTHLY',
    date: { $gte: start, $lte: end },
    amount: { $gte: 1000 }
  });
  return Boolean(payment);
}

module.exports = { hasMonthlyPayment };
