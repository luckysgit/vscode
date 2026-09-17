/* Identity comes from the server's HttpOnly session cookie. */
class AuthService {
  constructor() {
    this.currentUser = null;
    // Remove the old prototype's browser-trusted identities.
    try {
      localStorage.removeItem('cb_user_session');
      localStorage.removeItem('cb_is_authenticated');
    } catch (_) { /* Browsing still works when storage is disabled. */ }
  }

  async request(action, body) {
    const response = await fetch(`/api/auth/${action}`, {
      method: body === undefined ? 'GET' : 'POST',
      credentials: 'same-origin',
      headers: body === undefined ? {} : { 'Content-Type': 'application/json' },
      body: body === undefined ? undefined : JSON.stringify(body)
    });
    const result = await response.json();
    if (!response.ok) throw new Error(result.error || 'Unable to complete request. Try again.');
    this.currentUser = result.user;
    return result;
  }

  restore() { return this.request('me'); }
  login(email, password) { return this.request('login', { email, password }); }
  register(username, email, password) { return this.request('register', { username, email, password }); }
  guest() { return this.request('guest', {}); }
  logout() { return this.request('logout', {}); }
  isAuthenticated() { return !!this.currentUser && !this.currentUser.isGuest; }
  getCurrentUser() {
    return this.currentUser || { username: 'Visitor', email: '', xp: 0, streak: 0, rank: 'Bronze', mutualCode: '', isGuest: true };
  }
}
if (typeof window !== 'undefined') window.AuthService = AuthService;
if (typeof module !== 'undefined' && module.exports) module.exports = AuthService;
