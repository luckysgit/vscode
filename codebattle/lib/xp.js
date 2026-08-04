/* ==========================================================================
   CODEBATTLE — XP CALCULATION & BADGE ENGINE
   Based on Build Guide: codebattle_build_guide.md & codebattle_build_quide_raw.txt
   ========================================================================== */

const XP_REWARDS = {
  solve_easy: 30,
  solve_medium: 60,
  solve_hard: 120,
  daily_solve: 50,
  first_in_room: 25,
  clean_first_try: 20,
  room_win: 40,
  publish_problem: 15
};

const BADGE_DEFINITIONS = [
  { id: "first_solve", title: "First Solve", emoji: "⚡", description: "Solved your first coding problem" },
  { id: "clean_code", title: "Clean Code", emoji: "✨", description: "Passed 100% of test cases on 1st submission" },
  { id: "comeback", title: "Comeback King", emoji: "🚀", description: "Won top 3 after starting in last position" },
  { id: "speed_demon", title: "Speed Demon", emoji: "🏎️", description: "Won 3 competitive room speed battles" },
  { id: "streak_7", title: "Streak Master (7 Days)", emoji: "🔥", description: "Maintained a 7-day solving streak" },
  { id: "streak_30", title: "Legendary Streak (30 Days)", emoji: "👑", description: "Maintained a 30-day solving streak" },
  { id: "social", title: "Networker", emoji: "📱", description: "Added 5+ mutual connections via QR/code" },
  { id: "publisher", title: "Problem Creator", emoji: "📚", description: "Published a custom problem to the bank" },
  { id: "room_host", title: "Battle Host", emoji: "🏰", description: "Hosted 5+ competitive battle rooms" },
  { id: "perfectionist", title: "Perfectionist", emoji: "🎯", description: "Achieved 100% accuracy on 10 problems" },
  { id: "polyglot", title: "Polyglot Coder", emoji: "🌐", description: "Solved problems across 3+ programming languages" }
];

function getRankFromXP(xp) {
  if (xp >= 15000) return "Master";
  if (xp >= 9000) return "Diamond";
  if (xp >= 6000) return "Platinum";
  if (xp >= 3000) return "Gold";
  if (xp >= 1000) return "Silver";
  return "Bronze";
}

function calculateSolveXP(difficulty, isFirstTry = false, isDaily = false) {
  let xp = XP_REWARDS[`solve_${difficulty}`] || 30;
  if (isFirstTry) xp += XP_REWARDS.clean_first_try;
  if (isDaily) xp += XP_REWARDS.daily_solve;
  return xp;
}

function checkBadgeEligibility(userStats) {
  const earned = [];
  
  if (userStats.solves >= 1) earned.push("first_solve");
  if (userStats.cleanSubmissions >= 1) earned.push("clean_code");
  if (userStats.wins >= 3) earned.push("speed_demon");
  if (userStats.streak >= 7) earned.push("streak_7");
  if (userStats.streak >= 30) earned.push("streak_30");
  if (userStats.connections >= 5) earned.push("social");
  if (userStats.publishedProblems >= 1) earned.push("publisher");
  if (userStats.hostedRooms >= 5) earned.push("room_host");
  if (userStats.languagesUsed && userStats.languagesUsed.length >= 3) earned.push("polyglot");

  return BADGE_DEFINITIONS.filter(b => earned.includes(b.id));
}

if (typeof module !== 'undefined' && module.exports) {
  module.exports = {
    XP_REWARDS,
    BADGE_DEFINITIONS,
    getRankFromXP,
    calculateSolveXP,
    checkBadgeEligibility
  };
}
