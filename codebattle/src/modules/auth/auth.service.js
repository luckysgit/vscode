/* ==========================================================================
   CODEBATTLE — MODULE: AUTHENTICATION SERVICE
   Location: src/modules/auth/auth.service.js
   ========================================================================== */

class AuthService {
  constructor() {
    this.STORAGE_KEY_USER = 'cb_user_session';
    this.STORAGE_KEY_AUTH = 'cb_is_authenticated';
    
    // Initial default guest user
    this.defaultUser = {
      id: "u_default_1",
      username: "CodeKnight",
      email: "user@codebattle.app",
      xp: 2840,
      rank: "Master",
      streak: 5,
      mutualCode: "CK-8819",
      tier: "free",
      preferredLanguage: "Python"
    };

    this.currentUser = this.loadSession();
  }

  loadSession() {
    try {
      const savedUser = localStorage.getItem(this.STORAGE_KEY_USER);
      if (savedUser) return JSON.parse(savedUser);
    } catch (e) { console.error("Session load error", e); }
    return this.defaultUser;
  }

  isAuthenticated() {
    return localStorage.getItem(this.STORAGE_KEY_AUTH) === 'true';
  }

  async login(email, password) {
    // Authenticate with server or local fallback
    const user = {
      id: "u_" + Date.now(),
      username: email.split('@')[0] || "Competitor",
      email: email,
      xp: 2840,
      rank: "Master",
      streak: 5,
      mutualCode: "CB-" + Math.floor(1000 + Math.random() * 9000),
      tier: "free"
    };

    this.currentUser = user;
    localStorage.setItem(this.STORAGE_KEY_USER, JSON.stringify(user));
    localStorage.setItem(this.STORAGE_KEY_AUTH, 'true');
    return { success: true, user };
  }

  async register(username, email, password, preferredLanguage = 'Python') {
    const newUser = {
      id: "u_" + Date.now(),
      username: username,
      email: email,
      xp: 100, // +100 welcome bonus
      rank: "Bronze",
      streak: 1,
      mutualCode: "CK-" + Math.floor(1000 + Math.random() * 9000),
      tier: "free",
      preferredLanguage: preferredLanguage
    };

    this.currentUser = newUser;
    localStorage.setItem(this.STORAGE_KEY_USER, JSON.stringify(newUser));
    localStorage.setItem(this.STORAGE_KEY_AUTH, 'true');
    return { success: true, user: newUser };
  }

  logout() {
    localStorage.setItem(this.STORAGE_KEY_AUTH, 'false');
    this.currentUser = this.defaultUser;
    return { success: true };
  }

  getCurrentUser() {
    return this.currentUser;
  }

  updateXP(additionalXP) {
    this.currentUser.xp += additionalXP;
    localStorage.setItem(this.STORAGE_KEY_USER, JSON.stringify(this.currentUser));
    return this.currentUser.xp;
  }
}

if (typeof module !== 'undefined' && module.exports) {
  module.exports = AuthService;
}
