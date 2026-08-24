/* ==========================================================================
   CODEBATTLE — MODULE: ADMIN SERVICE
   Location: src/modules/admin/admin.service.js
   ========================================================================== */

class AdminService {
  getSystemStats() {
    return {
      totalUsers: 1482,
      totalSubmissions: 12490,
      activeRooms: 412,
      pendingFlagReports: 0
    };
  }
}

if (typeof window !== 'undefined') {
  window.AdminService = AdminService;
}

if (typeof module !== 'undefined' && module.exports) {
  module.exports = AdminService;
}
