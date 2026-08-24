/* ==========================================================================
   CODEBATTLE — MODULE: PROFILE SERVICE
   Location: src/modules/profile/profile.service.js
   ========================================================================== */

class ProfileService {
  getUserProfile(username = "CodeKnight") {
    return {
      username: username,
      xp: 2840,
      rank: "Master",
      streak: 5,
      mutualCode: "CK-8819",
      badges: ["First Solve", "Clean Code", "Streak Master"],
      weakspots: [
        { category: "Arrays & Hashes", rate: "57%", recommendation: "Practice two-pointer hash lookups under countdown pressure." },
        { category: "Dynamic Programming", rate: "37%", recommendation: "Focus on 1D DP tabulation and memoization patterns." }
      ]
    };
  }
}

if (typeof window !== 'undefined') {
  window.ProfileService = ProfileService;
}

if (typeof module !== 'undefined' && module.exports) {
  module.exports = ProfileService;
}
