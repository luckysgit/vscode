/* ==========================================================================
   CODEBATTLE — MAIN CLIENT CONTROLLER
   Location: web/app.js
   ========================================================================== */

// Instantiate Modular Services
const authService = new AuthService();
const problemService = new ProblemService();
const roomService = new RoomService();
const dashboardService = new DashboardService();
const submissionService = new SubmissionService();
const leaderboardService = new LeaderboardService();
const profileService = new ProfileService();
const adminService = new AdminService();
const notificationService = new NotificationService();
const orgService = new OrgService();

// Local State
const state = {
  currentUser: authService.getCurrentUser(),
  activeRoom: null,
  activeProblem: null,
  monacoEditor: null,
  soundEnabled: true,
  battleTimer: null,
  timeRemaining: 900
};

// APPLICATION INITIALIZATION ENGINE
function initApp() {
  initNavigation();
  initAuthSystem();
  renderDashboardHistory();
  renderRooms();
  renderProblemBank();
  renderLeaderboard();
  renderProfile();
  initRoomCreationForm();
  initMonacoEditor();
  initBattleActions();
  initMatchmaking();
  initConnections();
  initDailyChallenge();
  initSettingsForm();
  initExtraInteractions();
}

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', initApp);
} else {
  initApp();
}

// NAVIGATION CONTROLLER
function initNavigation() {
  const navLinks = document.querySelectorAll('.nav-link, .mobile-nav-item');
  navLinks.forEach(link => {
    link.addEventListener('click', (e) => {
      e.preventDefault();
      const targetView = link.getAttribute('data-target');
      if (targetView) switchView(targetView);
    });
  });

  const brand = document.getElementById('nav-brand');
  if (brand) brand.addEventListener('click', () => switchView('view-dashboard'));
}

function hideAllModals() {
  document.querySelectorAll('.modal-overlay').forEach(modal => {
    modal.classList.add('hidden');
  });
}

function switchView(viewId) {
  hideAllModals();

  const views = document.querySelectorAll('.app-view');
  const navLinks = document.querySelectorAll('.nav-link, .mobile-nav-item');

  views.forEach(v => v.classList.remove('active'));
  navLinks.forEach(l => l.classList.remove('active'));

  const target = document.getElementById(viewId);
  if (target) target.classList.add('active');

  navLinks.forEach(l => {
    if (l.getAttribute('data-target') === viewId) l.classList.add('active');
  });

  if (viewId === 'view-dashboard') renderDashboardHistory();
  if (viewId === 'view-problems') renderProblemBank();
  if (viewId === 'view-leaderboard') renderLeaderboard();
  if (viewId === 'view-profile') renderProfile();
  if (viewId === 'view-rooms') renderRooms();
}

// DASHBOARD HISTORY RENDERER
function renderDashboardHistory() {
  const body = document.getElementById('dashboard-history-table-body');
  if (!body) return;
  const history = dashboardService.getPastRoomsHistory();
  body.innerHTML = '';

  history.forEach(item => {
    const tr = document.createElement('tr');
    tr.innerHTML = `
      <td><strong>${item.roomTitle}</strong><br><span class="text-subtle">${item.joinedAt}</span></td>
      <td><strong>${item.problemTitle}</strong></td>
      <td><span class="badge badge-info">${item.opponents.join(', ')}</span></td>
      <td><code>${item.language}</code></td>
      <td><span class="badge badge-success">${item.result}</span></td>
      <td><strong style="color:var(--cyan);">${item.xpEarned} XP</strong></td>
    `;
    body.appendChild(tr);
  });
}

// AUTH SYSTEM
function initAuthSystem() {
  const trigger = document.getElementById('user-pill-trigger');
  const menu = document.getElementById('account-dropdown-menu');
  if (trigger && menu) {
    trigger.addEventListener('click', (e) => {
      e.stopPropagation();
      menu.classList.toggle('hidden');
    });
    document.addEventListener('click', () => menu.classList.add('hidden'));
  }

  const btnSignIn = document.getElementById('btn-nav-sign-in');
  const btnSignUp = document.getElementById('btn-nav-sign-up');
  const modalSignIn = document.getElementById('modal-sign-in');
  const modalSignUp = document.getElementById('modal-sign-up');
  const closeSignIn = document.getElementById('btn-close-sign-in');
  const closeSignUp = document.getElementById('btn-close-sign-up');

  document.querySelectorAll('.modal-overlay').forEach(modal => {
    modal.addEventListener('click', (e) => {
      if (e.target === modal) modal.classList.add('hidden');
    });
  });

  if (btnSignIn && modalSignIn) btnSignIn.addEventListener('click', () => modalSignIn.classList.remove('hidden'));
  if (btnSignUp && modalSignUp) btnSignUp.addEventListener('click', () => modalSignUp.classList.remove('hidden'));
  if (closeSignIn && modalSignIn) closeSignIn.addEventListener('click', () => modalSignIn.classList.add('hidden'));
  if (closeSignUp && modalSignUp) closeSignUp.addEventListener('click', () => modalSignUp.classList.add('hidden'));

  const formSignIn = document.getElementById('form-sign-in');
  if (formSignIn) {
    formSignIn.addEventListener('submit', async (e) => {
      e.preventDefault();
      const email = document.getElementById('signin-email').value;
      await authService.login(email, "password");
      state.currentUser = authService.getCurrentUser();
      const handleElem = document.getElementById('global-user-handle');
      if (handleElem) handleElem.innerText = state.currentUser.username;
      if (modalSignIn) modalSignIn.classList.add('hidden');
      switchView('view-dashboard');
    });
  }

  const formSignUp = document.getElementById('form-sign-up');
  if (formSignUp) {
    formSignUp.addEventListener('submit', async (e) => {
      e.preventDefault();
      const username = document.getElementById('signup-username').value;
      const email = document.getElementById('signup-email').value;
      await authService.register(username, email, "password");
      state.currentUser = authService.getCurrentUser();
      const handleElem = document.getElementById('global-user-handle');
      if (handleElem) handleElem.innerText = state.currentUser.username;
      if (modalSignUp) modalSignUp.classList.add('hidden');
      switchView('view-dashboard');
    });
  }

  const btnSignOut = document.getElementById('btn-drop-sign-out');
  if (btnSignOut) {
    btnSignOut.addEventListener('click', () => {
      authService.logout();
      switchView('view-rooms');
    });
  }
}

// ROOM CREATION FORM
function initRoomCreationForm() {
  const btnDashCreate = document.getElementById('btn-dash-create-room');
  const btnCreateModal = document.getElementById('btn-create-room-modal');
  const modalCreate = document.getElementById('modal-create-room');
  const btnClose = document.getElementById('btn-close-create-room');
  const btnCancel = document.getElementById('btn-cancel-create-room');
  const selectSource = document.getElementById('select-problem-source');
  const pickerBank = document.getElementById('section-picker-bank');
  const pickerCustom = document.getElementById('section-picker-custom');
  const formCreate = document.getElementById('form-create-room');

  const openModal = () => {
    populateProblemBankSelect();
    if (modalCreate) modalCreate.classList.remove('hidden');
  };

  if (btnDashCreate) btnDashCreate.addEventListener('click', openModal);
  if (btnCreateModal) btnCreateModal.addEventListener('click', openModal);
  if (btnClose && modalCreate) btnClose.addEventListener('click', () => modalCreate.classList.add('hidden'));
  if (btnCancel && modalCreate) btnCancel.addEventListener('click', () => modalCreate.classList.add('hidden'));

  if (selectSource && pickerBank && pickerCustom) {
    selectSource.addEventListener('change', (e) => {
      if (e.target.value === 'custom') {
        pickerBank.classList.add('hidden');
        pickerCustom.classList.remove('hidden');
      } else {
        pickerBank.classList.remove('hidden');
        pickerCustom.classList.add('hidden');
      }
    });
  }

  if (formCreate) {
    formCreate.addEventListener('submit', (e) => {
      e.preventDefault();
      const title = document.getElementById('input-room-title').value;
      const source = selectSource ? selectSource.value : 'bank';
      const timeMode = document.getElementById('select-time-mode').value;
      const hasTimeLimit = timeMode === 'timed';

      let selectedProblem = null;

      if (source === 'custom') {
        const customTitle = document.getElementById('input-custom-prob-title').value || "Custom Challenge";
        const customDesc = document.getElementById('input-custom-prob-desc').value || "Solve the challenge.";
        const customIn = document.getElementById('input-custom-prob-tc-in').value || "Sample Input";
        const customOut = document.getElementById('input-custom-prob-tc-out').value || "Sample Output";

        selectedProblem = problemService.createProblem({
          title: customTitle,
          difficulty: "Medium",
          category: "Custom User Problem",
          description: customDesc,
          testCases: [{ input: customIn, expected: customOut, isHidden: false }],
          author: state.currentUser.username
        });
      } else {
        const bankSelect = document.getElementById('select-problem-bank-item');
        const probId = bankSelect ? bankSelect.value : "p1";
        selectedProblem = problemService.getProblemById(probId);
      }

      const room = roomService.createRoom({
        title: title,
        host: state.currentUser.username,
        problemId: selectedProblem.id,
        customProblem: selectedProblem,
        hasTimeLimit: hasTimeLimit,
        timeLimitMins: 15
      });

      if (modalCreate) modalCreate.classList.add('hidden');
      renderRooms();
      joinRoom(room.id);
    });
  }
}

function populateProblemBankSelect() {
  const bankSelect = document.getElementById('select-problem-bank-item');
  if (!bankSelect) return;
  const problems = problemService.getAllProblems();
  bankSelect.innerHTML = '';
  problems.forEach(p => {
    const opt = document.createElement('option');
    opt.value = p.id;
    opt.innerText = `${p.title} (${p.difficulty}) — v${p.version || 1}`;
    bankSelect.appendChild(opt);
  });
}

// ROOMS GRID & LOBBY
function renderRooms() {
  const grid = document.getElementById('rooms-grid-container');
  if (!grid) return;
  grid.innerHTML = '';
  const rooms = roomService.getRooms();

  rooms.forEach(room => {
    const card = document.createElement('div');
    card.className = 'glass-card room-card';
    card.innerHTML = `
      <div>
        <div class="room-card-header">
          <span class="status-pill status-waiting">${room.status}</span>
          <span class="badge diff-medium">${room.diff}</span>
        </div>
        <h3 class="room-title">${room.title}</h3>
        <p class="text-subtle">Host: <strong>${room.host}</strong> • Code: <code class="code-badge">${room.code}</code></p>
      </div>
      <div class="room-card-footer">
        <span class="player-count-icon">👥 ${room.players}/${room.max} Players</span>
        <button class="btn btn-primary btn-sm btn-join-action" data-id="${room.id}">Join Room</button>
      </div>
    `;
    grid.appendChild(card);
  });

  document.querySelectorAll('.btn-join-action').forEach(btn => {
    btn.addEventListener('click', (e) => {
      const roomId = e.target.getAttribute('data-id');
      joinRoom(roomId);
    });
  });
}

function joinRoom(roomId) {
  const room = roomService.getRoomByCode(roomId);
  state.activeRoom = room;
  state.activeProblem = problemService.getProblemById(room.problemId);

  const titleElem = document.getElementById('lobby-room-title');
  const hostElem = document.getElementById('lobby-host-name');
  const codeElem = document.getElementById('lobby-room-code');

  if (titleElem) titleElem.innerText = room.title;
  if (hostElem) hostElem.innerText = room.host;
  if (codeElem) codeElem.innerText = room.code;

  if (window.QRCode) {
    const container = document.getElementById('lobby-qr-render-area');
    if (container) {
      container.innerHTML = '';
      new QRCode(container, { text: `https://codebattle.app/join?code=${room.code}`, width: 90, height: 90 });
    }
  }

  switchView('view-room-lobby');
}

// BATTLE ARENA & EXECUTION
function initBattleActions() {
  const btnStart = document.getElementById('btn-host-start-battle');
  const btnLeave = document.getElementById('btn-leave-room');
  const btnRun = document.getElementById('btn-run-code');
  const btnSubmit = document.getElementById('btn-submit-code');
  const consoleSummary = document.getElementById('console-summary-text');
  const btnBack = document.getElementById('btn-back-to-dashboard');
  const btnOpenQR = document.getElementById('btn-open-qr');
  const modalQR = document.getElementById('modal-qr-connect');
  const btnCloseQR = document.getElementById('btn-close-qr-modal');

  if (btnStart) {
    btnStart.addEventListener('click', () => {
      switchView('view-battle');
      setupBattleArena();
    });
  }

  if (btnLeave) btnLeave.addEventListener('click', () => switchView('view-rooms'));

  if (btnRun && consoleSummary) {
    btnRun.addEventListener('click', async () => {
      consoleSummary.innerText = "▶ Executing code in micro-container sandbox...";
      const res = await submissionService.executeCode({ code: "", language: "python", problem: state.activeProblem });
      consoleSummary.innerHTML = `<span style="color:var(--success)">✔ Visible Test Cases Passed (${res.passedCount}/${res.totalCount})</span>`;
    });
  }

  if (btnSubmit && consoleSummary) {
    btnSubmit.addEventListener('click', async () => {
      consoleSummary.innerText = "⚡ Evaluating solution...";
      const res = await submissionService.executeCode({ code: "", language: "python", problem: state.activeProblem, isSubmission: true });

      const langSelect = document.getElementById('editor-lang-select');
      dashboardService.recordRoomSubmission({
        roomId: state.activeRoom ? state.activeRoom.id : "r1",
        roomTitle: state.activeRoom ? state.activeRoom.title : "Algo Challenge",
        opponents: [state.activeRoom ? state.activeRoom.host : "DevNinja", "DevNinja"],
        problemTitle: state.activeProblem ? state.activeProblem.title : "Challenge",
        language: langSelect ? langSelect.value : "Python",
        result: "Correct Answer (Fastest #1)",
        status: "Accepted",
        execTimeMs: res.executionTimeMs,
        xpEarned: 60
      });

      authService.updateXP(60);
      switchView('view-results');
    });
  }

  if (btnBack) btnBack.addEventListener('click', () => switchView('view-dashboard'));

  if (btnOpenQR && modalQR) {
    btnOpenQR.addEventListener('click', () => {
      modalQR.classList.remove('hidden');
      if (window.QRCode) {
        const container = document.getElementById('modal-qr-render-area');
        if (container) {
          container.innerHTML = '';
          new QRCode(container, { text: `https://codebattle.app/connect?code=${state.currentUser.mutualCode || 'CK-8819'}`, width: 160, height: 160 });
        }
      }
    });
  }

  if (btnCloseQR && modalQR) btnCloseQR.addEventListener('click', () => modalQR.classList.add('hidden'));

  // Tab switching in Battle Arena
  document.querySelectorAll('.tab-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
      document.querySelectorAll('.tab-pane').forEach(p => p.classList.remove('active'));
      btn.classList.add('active');
      const tabId = btn.getAttribute('data-tab');
      const pane = document.getElementById(tabId);
      if (pane) pane.classList.add('active');
    });
  });
}

function setupBattleArena() {
  const p = state.activeProblem || problemService.getAllProblems()[0];
  const titleElem = document.getElementById('battle-problem-title');
  const diffElem = document.getElementById('battle-diff-badge');
  const descElem = document.getElementById('problem-description-body');

  if (titleElem) titleElem.innerText = p.title;
  if (diffElem) diffElem.innerText = p.difficulty;
  if (descElem) descElem.innerHTML = `<p>${p.description}</p>`;

  const timerLabel = document.getElementById('timer-mode-label');
  const timerClock = document.getElementById('battle-timer-clock');

  if (timerLabel && timerClock) {
    if (state.activeRoom && !state.activeRoom.hasTimeLimit) {
      timerLabel.innerText = "TIME MODE";
      timerClock.innerText = "☕ Relaxed (No Limit)";
    } else {
      timerLabel.innerText = "TIME REMAINING";
      timerClock.innerText = "14:59";
    }
  }
}

// PROBLEM BANK RENDERER
function renderProblemBank() {
  const tbody = document.getElementById('problems-table-body');
  if (!tbody) return;
  tbody.innerHTML = '';
  const problems = problemService.getAllProblems();

  problems.forEach(p => {
    const tr = document.createElement('tr');
    tr.innerHTML = `
      <td><strong>${p.title}</strong></td>
      <td><span class="badge diff-medium">${p.difficulty}</span></td>
      <td>${p.category}</td>
      <td><code>v${p.version || 1} (${p.commits ? p.commits.length : 1} commits)</code></td>
      <td><button class="btn btn-outline btn-sm btn-solve-solo" data-id="${p.id}">Solve Solo</button></td>
    `;
    tbody.appendChild(tr);
  });

  document.querySelectorAll('.btn-solve-solo').forEach(btn => {
    btn.addEventListener('click', (e) => {
      const pid = e.target.getAttribute('data-id');
      state.activeProblem = problemService.getProblemById(pid);
      state.activeRoom = { title: state.activeProblem.title, host: "Solo Practice", code: "SOLO-01", hasTimeLimit: false };
      switchView('view-battle');
      setupBattleArena();
    });
  });
}

// MONACO EDITOR INITIALIZER
function initMonacoEditor() {
  if (window.require) {
    window.require.config({ paths: { 'vs': 'https://cdnjs.cloudflare.com/ajax/libs/monaco-editor/0.45.0/min/vs' } });
    window.require(['vs/editor/editor.main'], function() {
      const container = document.getElementById('monaco-editor-instance');
      if (!container) return;
      state.monacoEditor = monaco.editor.create(container, {
        value: typeof STARTER_CODE_TEMPLATES !== 'undefined' ? STARTER_CODE_TEMPLATES.python : "class Solution:\n    def solve(self, nums, target):\n        pass",
        language: 'python',
        theme: 'vs-dark',
        automaticLayout: true,
        fontSize: 14,
        fontFamily: "'SF Mono', ui-monospace, monospace",
        minimap: { enabled: false },
        lineNumbers: 'on'
      });
    });
  }
}

// LEADERBOARD RENDERER
function renderLeaderboard() {
  const tbody = document.getElementById('leaderboard-table-body');
  if (!tbody) return;
  tbody.innerHTML = '';
  const rankings = leaderboardService.getRankings();

  rankings.forEach(r => {
    const tr = document.createElement('tr');
    tr.innerHTML = `
      <td><strong>#${r.rank}</strong></td>
      <td><strong>${r.handle}</strong></td>
      <td><span class="badge badge-master">${r.tier}</span></td>
      <td>🔥 ${r.solves % 10 + 3} Days</td>
      <td><strong style="color:var(--cyan);">${r.xp.toLocaleString()} XP</strong></td>
    `;
    tbody.appendChild(tr);
  });
}

// PROFILE RENDERER
function renderProfile() {
  const user = state.currentUser || authService.getCurrentUser();
  const handleDisp = document.getElementById('prof-handle-display');
  const emailDisp = document.getElementById('prof-email-display');
  const codeDisp = document.getElementById('prof-code-display');
  const xpDisp = document.getElementById('prof-xp-val');
  const streakBadge = document.getElementById('prof-streak-badge');

  if (handleDisp) handleDisp.innerText = user.username || user.handle || "CodeKnight";
  if (emailDisp) emailDisp.innerHTML = `${user.email} • Mutual Code: <code class="code-badge">${user.mutualCode || 'CK-8819'}</code>`;
  if (codeDisp) codeDisp.innerText = user.mutualCode || "CK-8819";
  if (xpDisp) xpDisp.innerText = `${(user.xp || 2840).toLocaleString()} XP`;
  if (streakBadge) streakBadge.innerText = `🔥 ${user.streak || 5} Day Streak`;
}

// MATCHMAKING CONTROLLER
function initMatchmaking() {
  const btnStart = document.getElementById('btn-start-matchmaking');
  const boxSearch = document.getElementById('mm-searching-box');
  const quickMatchBtn = document.getElementById('btn-dash-quick-match');

  const triggerMatch = () => {
    if (boxSearch) boxSearch.classList.remove('hidden');
    setTimeout(() => {
      if (boxSearch) boxSearch.classList.add('hidden');
      const room = roomService.createRoom({
        title: "Speed Algo Sprint",
        host: "DevNinja",
        problemId: "p1",
        hasTimeLimit: true,
        timeLimitMins: 15
      });
      renderRooms();
      joinRoom(room.id);
    }, 1500);
  };

  if (btnStart) btnStart.addEventListener('click', triggerMatch);
  if (quickMatchBtn) quickMatchBtn.addEventListener('click', () => {
    switchView('view-matchmaking');
    triggerMatch();
  });
}

// MUTUAL CONNECTIONS CONTROLLER
function initConnections() {
  const btnAdd = document.getElementById('btn-submit-connection-code');
  const inputCode = document.getElementById('input-add-connection-code');
  const tbody = document.getElementById('connections-table-body');
  const btnShowQR = document.getElementById('btn-show-my-qr');
  const modalQR = document.getElementById('modal-qr-connect');

  if (btnAdd && inputCode) {
    btnAdd.addEventListener('click', () => {
      const val = inputCode.value.trim();
      if (!val) return;
      if (tbody) {
        const tr = document.createElement('tr');
        tr.innerHTML = `
          <td><strong>ConnectedUser_${val}</strong></td>
          <td><code>${val}</code></td>
          <td><span class="badge badge-success">Online</span></td>
          <td><button class="btn btn-outline btn-sm btn-challenge-user">⚔️ Challenge</button></td>
        `;
        tbody.appendChild(tr);
      }
      inputCode.value = '';
      alert(`Mutual connection established with code: ${val}`);
    });
  }

  if (btnShowQR && modalQR) {
    btnShowQR.addEventListener('click', () => {
      modalQR.classList.remove('hidden');
      if (window.QRCode) {
        const container = document.getElementById('modal-qr-render-area');
        if (container) {
          container.innerHTML = '';
          new QRCode(container, { text: `https://codebattle.app/connect?code=${state.currentUser.mutualCode || 'CK-8819'}`, width: 160, height: 160 });
        }
      }
    });
  }
}

// DAILY CHALLENGE CONTROLLER
function initDailyChallenge() {
  const btnStartDaily = document.getElementById('btn-start-daily-challenge');
  if (btnStartDaily) {
    btnStartDaily.addEventListener('click', () => {
      const p = problemService.getProblemById("p1");
      state.activeProblem = p;
      state.activeRoom = { title: "Daily Challenge", host: "CodeBattle", code: "DAILY-01", hasTimeLimit: true };
      switchView('view-battle');
      setupBattleArena();
    });
  }
}

// SETTINGS FORM CONTROLLER
function initSettingsForm() {
  const form = document.getElementById('form-update-settings');
  if (form) {
    form.addEventListener('submit', (e) => {
      e.preventDefault();
      const newUsername = document.getElementById('settings-username').value;
      if (newUsername) {
        state.currentUser.username = newUsername;
        const handleElem = document.getElementById('global-user-handle');
        if (handleElem) handleElem.innerText = newUsername;
      }
      alert('Preferences saved successfully!');
      switchView('view-dashboard');
    });
  }
}

// EXTRA INTERACTION BINDINGS
function initExtraInteractions() {
  // Account Dropdown View Links
  const btnDropProfile = document.getElementById('btn-drop-profile');
  if (btnDropProfile) btnDropProfile.addEventListener('click', () => switchView('view-profile'));

  const btnDropSettings = document.getElementById('btn-drop-settings');
  if (btnDropSettings) btnDropSettings.addEventListener('click', () => switchView('view-settings'));

  const btnDropAdmin = document.getElementById('btn-drop-admin');
  if (btnDropAdmin) btnDropAdmin.addEventListener('click', () => switchView('view-admin'));

  // Sound FX Toggle Button
  const btnSound = document.getElementById('btn-toggle-sound');
  if (btnSound) {
    btnSound.addEventListener('click', () => {
      state.soundEnabled = !state.soundEnabled;
      const icon = document.getElementById('sound-icon');
      if (icon) icon.innerText = state.soundEnabled ? '🔊' : '🔇';
    });
  }

  // Problists Track Solve Buttons
  document.querySelectorAll('.btn-solve-problist').forEach(btn => {
    btn.addEventListener('click', () => {
      switchView('view-problems');
    });
  });

  // Launch Interview Session Button
  const btnStartInterview = document.getElementById('btn-start-interview-session');
  if (btnStartInterview) {
    btnStartInterview.addEventListener('click', () => {
      const p = problemService.getProblemById("p1");
      state.activeProblem = p;
      state.activeRoom = { title: "Live Pair Interview", host: "Interviewer", code: "INT-99", hasTimeLimit: false };
      switchView('view-battle');
      setupBattleArena();
    });
  }
}
