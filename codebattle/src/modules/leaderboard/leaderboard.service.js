/* ==========================================================================
   CODEBATTLE — MODULE: LEADERBOARD SERVICE
   Location: src/modules/leaderboard/leaderboard.service.js
   ========================================================================== */

class LeaderboardService {
  getRankings() {
    return [
      { rank: 1, handle: "RustAce", tier: "💎 Master", solves: 412, winRate: "89%", xp: 14200 },
      { rank: 2, handle: "DevNinja", tier: "💎 Master", solves: 388, winRate: "84%", xp: 12950 },
      { rank: 3, handle: "CodeKnight", tier: "💎 Master", solves: 310, winRate: "78%", xp: 9840 },
      { rank: 4, handle: "CyberCoder", tier: "🥇 Platinum", solves: 245, winRate: "71%", xp: 7600 },
      { rank: 5, handle: "AlgoWiz", tier: "🥇 Platinum", solves: 198, winRate: "68%", xp: 6200 }
    ];
  }
}

if (typeof module !== 'undefined' && module.exports) {
  module.exports = LeaderboardService;
}
