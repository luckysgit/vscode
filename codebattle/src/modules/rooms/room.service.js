/* ==========================================================================
   CODEBATTLE — MODULE: ROOMS SERVICE
   Location: src/modules/rooms/room.service.js
   ========================================================================== */

class RoomService {
  constructor() {
    this.STORAGE_KEY_ROOMS = 'cb_rooms_history';

    this.defaultRooms = [
      { id: "r1", title: "Python Algo Sprint #42", host: "DevNinja", code: "PY-9921", lang: "Python", format: "Speed Coding", diff: "Medium", players: 14, max: 100, status: "LOBBY", problemId: "p1", hasTimeLimit: true, timeLimitMins: 15 },
      { id: "r2", title: "Cross-Lang Code Golf (All 10 Allowed)", host: "RustAce", code: "GOLF-881", lang: "Any (10)", format: "Code Golf", diff: "Hard", players: 42, max: "Unlimited", status: "ACTIVE", problemId: "p2", hasTimeLimit: false },
      { id: "r3", title: "JavaScript Debugging Race", host: "FrontendKing", code: "JS-1002", lang: "JavaScript", format: "Debugging Race", diff: "Easy", players: 8, max: 100, status: "LOBBY", problemId: "p1", hasTimeLimit: true, timeLimitMins: 10 }
    ];

    this.rooms = this.loadRooms();
  }

  loadRooms() {
    try {
      const saved = localStorage.getItem(this.STORAGE_KEY_ROOMS);
      if (saved) return JSON.parse(saved);
    } catch (e) { console.error("Rooms load error", e); }
    return this.defaultRooms;
  }

  saveRooms() {
    try {
      localStorage.setItem(this.STORAGE_KEY_ROOMS, JSON.stringify(this.rooms));
    } catch (e) { console.error("Rooms save error", e); }
  }

  // Create room with custom problem OR past problem bank selection
  createRoom({ title, host, lang, format, diff, problemId, customProblem, hasTimeLimit, timeLimitMins }) {
    const code = "CB-" + Math.floor(1000 + Math.random() * 9000);
    const newRoom = {
      id: "r_" + Date.now(),
      title: title || "Custom Battle Room",
      host: host || "CodeKnight",
      code: code,
      lang: lang || "Any (10)",
      format: format || "Speed Coding",
      diff: diff || "Medium",
      players: 1,
      max: 100,
      status: "LOBBY",
      problemId: problemId || (customProblem ? customProblem.id : "p1"),
      customProblem: customProblem || null,
      hasTimeLimit: hasTimeLimit !== undefined ? hasTimeLimit : false, // No forced time boundation unless requested!
      timeLimitMins: timeLimitMins || 15,
      qrUrl: `https://codebattle.app/join?code=${code}`
    };

    this.rooms.unshift(newRoom);
    this.saveRooms();
    return newRoom;
  }

  getRooms() {
    return this.rooms;
  }

  getRoomByCode(code) {
    return this.rooms.find(r => r.code === code || r.id === code) || this.rooms[0];
  }
}

if (typeof window !== 'undefined') {
  window.RoomService = RoomService;
}

if (typeof module !== 'undefined' && module.exports) {
  module.exports = RoomService;
}
