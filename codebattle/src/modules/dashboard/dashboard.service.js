/* ==========================================================================
   CODEBATTLE — MODULE: DASHBOARD SERVICE (Past Room History & Performance)
   Location: src/modules/dashboard/dashboard.service.js
   ========================================================================== */

class DashboardService {
  constructor() {
    this.STORAGE_KEY_HISTORY = 'cb_joined_rooms_history';

    this.defaultHistory = [
      {
        roomId: "r101",
        roomTitle: "Python Algo Sprint #42",
        joinedAt: "2026-07-28 22:30",
        opponents: ["DevNinja", "RustAce"],
        problemTitle: "Two Sum: Hash Strategy",
        language: "Python 3.11",
        result: "Correct Answer (Fastest #1)",
        status: "Accepted",
        execTimeMs: 12,
        xpEarned: 60
      },
      {
        roomId: "r102",
        roomTitle: "Cross-Lang Code Golf",
        joinedAt: "2026-07-28 20:15",
        opponents: ["RustAce", "CyberCoder"],
        problemTitle: "Valid Parentheses Stack",
        language: "Rust 1.75",
        result: "Correct Answer (2nd Place)",
        status: "Accepted",
        execTimeMs: 18,
        xpEarned: 40
      },
      {
        roomId: "r103",
        roomTitle: "Debugging Race #8",
        joinedAt: "2026-07-27 18:40",
        opponents: ["FrontendKing"],
        problemTitle: "Reverse String In-Place",
        language: "JavaScript",
        result: "Correct Answer (Fastest #1)",
        status: "Accepted",
        execTimeMs: 8,
        xpEarned: 60
      }
    ];

    this.history = this.loadHistory();
  }

  loadHistory() {
    try {
      const saved = localStorage.getItem(this.STORAGE_KEY_HISTORY);
      if (saved) return JSON.parse(saved);
    } catch (e) { console.error("History load error", e); }
    return this.defaultHistory;
  }

  saveHistory() {
    try {
      localStorage.setItem(this.STORAGE_KEY_HISTORY, JSON.stringify(this.history));
    } catch (e) { console.error("History save error", e); }
  }

  // Record a completed room submission in dashboard history
  recordRoomSubmission({ roomId, roomTitle, opponents, problemTitle, language, result, status, execTimeMs, xpEarned }) {
    const entry = {
      roomId: roomId || "r_" + Date.now(),
      roomTitle: roomTitle || "Battle Room",
      joinedAt: new Date().toISOString().replace('T', ' ').substring(0, 16),
      opponents: opponents || ["DevNinja"],
      problemTitle: problemTitle || "Challenge",
      language: language || "Python",
      result: result || "Correct Answer",
      status: status || "Accepted",
      execTimeMs: execTimeMs || 15,
      xpEarned: xpEarned || 60
    };

    this.history.unshift(entry);
    this.saveHistory();
    return entry;
  }

  getPastRoomsHistory() {
    return this.history;
  }
}

if (typeof module !== 'undefined' && module.exports) {
  module.exports = DashboardService;
}
