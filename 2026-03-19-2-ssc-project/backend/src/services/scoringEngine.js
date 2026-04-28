function isLegalDelivery(extraType) {
  return !['WIDE', 'NO_BALL'].includes(extraType);
}

function overFromLegalBalls(legalBalls) {
  return `${Math.floor(legalBalls / 6)}.${legalBalls % 6}`;
}

function calculateRunRate(runs, legalBalls) {
  if (legalBalls === 0) return 0;
  return Number((runs / (legalBalls / 6)).toFixed(2));
}

function applyBall(match, input) {
  const legalDelivery = isLegalDelivery(input.extra_type);
  const baseExtra = ['WIDE', 'NO_BALL'].includes(input.extra_type) ? 1 : 0;
  const totalRuns = input.runs_off_bat + input.extra_runs + baseExtra;

  const ballIsFreeHit = Boolean(match.scoreState.nextBallFreeHit);
  const isRunout = input.is_wicket && input.wicket_type === 'RUNOUT';
  const wicketAllowed = !ballIsFreeHit || isRunout;
  const wicketCounts = input.is_wicket && wicketAllowed;

  let legalBalls = match.scoreState.legalBalls + (legalDelivery ? 1 : 0);
  let runs = match.scoreState.runs + totalRuns;
  let extras = match.scoreState.extras + input.extra_runs + baseExtra;
  let wickets = match.scoreState.wickets + (wicketCounts ? 1 : 0);

  let striker = match.batting.striker;
  let nonStriker = match.batting.nonStriker;

  if (totalRuns % 2 === 1) {
    [striker, nonStriker] = [nonStriker, striker];
  }

  if (legalDelivery && legalBalls % 6 === 0) {
    [striker, nonStriker] = [nonStriker, striker];
  }

  let nextBallFreeHit = false;
  if (input.extra_type === 'NO_BALL') {
    nextBallFreeHit = true;
  }

  const currentOver = Math.floor((legalBalls - (legalDelivery ? 1 : 0)) / 6) + 1;
  const currentBallInOver = legalDelivery ? ((legalBalls - 1) % 6) + 1 : (legalBalls % 6) + 1;

  return {
    scoring: {
      over: currentOver,
      ball_number: currentBallInOver,
      total_runs: totalRuns,
      legal_delivery: legalDelivery,
      is_free_hit: ballIsFreeHit,
      is_wicket: wicketCounts,
      wicket_type: wicketCounts ? input.wicket_type : null
    },
    matchUpdate: {
      scoreState: {
        runs,
        wickets,
        legalBalls,
        extras,
        runRate: calculateRunRate(runs, legalBalls),
        nextBallFreeHit
      },
      batting: {
        striker,
        nonStriker
      },
      derived: {
        oversText: overFromLegalBalls(legalBalls)
      }
    }
  };
}

module.exports = { applyBall, overFromLegalBalls };
