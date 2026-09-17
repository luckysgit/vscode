/* Competition results will be populated by the server when competition execution ships. */
class DashboardService {
  constructor() {
    this.history = [];
    try { localStorage.removeItem('cb_joined_rooms_history'); } catch (_) {}
  }
  getPastRoomsHistory() { return this.history; }
}
if (typeof window !== 'undefined') window.DashboardService = DashboardService;
if (typeof module !== 'undefined' && module.exports) module.exports = DashboardService;
