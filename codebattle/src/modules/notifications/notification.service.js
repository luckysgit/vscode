/* ==========================================================================
   CODEBATTLE — MODULE: NOTIFICATIONS SERVICE
   Location: src/modules/notifications/notification.service.js
   ========================================================================== */

class NotificationService {
  showToast(message) {
    const container = document.getElementById('toast-container');
    if (!container) return;
    const toast = document.createElement('div');
    toast.className = 'toast';
    toast.innerText = message;
    container.appendChild(toast);
    setTimeout(() => {
      toast.style.opacity = '0';
      setTimeout(() => toast.remove(), 300);
    }, 2500);
  }
}

if (typeof module !== 'undefined' && module.exports) {
  module.exports = NotificationService;
}
