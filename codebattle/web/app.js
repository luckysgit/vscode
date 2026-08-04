/* ==========================================================================
   CODEBATTLE — MAIN CLIENT CONTROLLER (Modular src Integration)
   Location: web/app.js
   ========================================================================== */

// Instantiate Modular Services
const authService = new AuthService();
const problemService = new ProblemService();
const roomService = new RoomService();
const dashboardService = new DashboardService();
const submissionService = new SubmissionService();

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

// DOM ELEMENTS
const DOM = {
  views: document.querySelectorAll('.app-view'),
  navLinks: document.querySelectorAll('.nav-link, .mobile-nav-item'),
  dashboardHistoryBody: document.getElementById('dashboard-history-table-body'),
  roomsGrid: document.getElementById('rooms-grid-container'),
  problemsTableBody: document.getElementById('problems-table-body'),
  
  // Modals & Triggers
  modalCreateRoom: document.getElementById('modal-create-room'),
  btnDashCreateRoom: document.getElementById('btn-dash-create-room'),
  btnCreateRoomModal: document.getElementById('btn-create-room-modal'),
  btnCloseCreateRoom: document.getElementById('btn-close-create-room'),
  btnCancelCreateRoom: document.getElementById('btn-cancel-create-room'),
  formCreateRoom: document.getElementById('form-create-room'),
  selectProblemSource: document.getElementById('select-problem-source'),
  sectionPickerBank: document.getElementById('section-picker-bank'),
  sectionPickerCustom: document.getElementById('section-picker-custom'),
  selectProblemBankItem: document.getElementById('select-problem-bank-item'),

  // Auth Modals
  modalSignIn: document.getElementById('modal-sign-in'),
  modalSignUp: document.getElementById('modal-sign-up'),
  btnNavSignIn: document.getElementById('btn-nav-sign-in'),
  btnNavSignUp: document.getElementById('btn-nav-sign-up'),
  btnCloseSignIn: document.getElementById('btn-close-sign-in'),
  btnCloseSignUp: document.getElementById('btn-close-sign-up'),
  formSignIn: document.getElementById('form-sign-in'),
  formSignUp: document.getElementById('form-sign-up'),
  userPillTrigger: document.getElementById('user-pill-trigger'),
  accountDropdownMenu: document.getElementById('account-dropdown-menu'),
  btnDropSignOut: document.getElementById('btn-drop-sign-out'),

  // Battle Arena & Code Execution
  btnHostStartBattle: document.getElementById('btn-host-start-battle'),
  btnLeaveRoom: document.getElementById('btn-leave-room'),
  btnRunCode: document.getElementById('btn-run-code'),
  btnSubmitCode: document.getElementById('btn-submit-code'),
  editorLangSelect: document.getElementById('editor-lang-select'),
  consoleSummaryText: document.getElementById('console-summary-text'),
  btnBackToDashboard: document.getElementById('btn-back-to-dashboard'),
  btnOpenQR: document.getElementById('btn-open-qr'),
  modalQRConnect: document.getElementById('modal-qr-connect'),
  btnCloseQRModal: document.getElementById('btn-close-qr-modal')
};

// INITIALIZATION
document.addEventListener('DOMContentLoaded', () => {
  initNavigation();
  initAuthSystem();
  renderDashboardHistory();
  renderRooms();
  renderProblemBank();
  initRoomCreationForm();
  initMonacoEditor();
  initBattleActions();
});

// NAVIGATION
function initNavigation() {
  DOM.navLinks.forEach(link => {
    link.addEventListener('click', () => {
      const targetView = link.getAttribute('data-target');
      if (targetView) switchView(targetView);
    });
  });

  document.getElementById('nav-brand').addEventListener('click', () => switchView('view-dashboard'));
}

function switchView(viewId) {
  DOM.views.forEach(v => v.classList.remove('active'));
  DOM.navLinks.forEach(l => l.classList.remove('active'));

  const target = document.getElementById(viewId);
  if (target) target.classList.add('active');

  DOM.navLinks.forEach(l => {
    if (l.getAttribute('data-target') === viewId) l.classList.add('active');
  });

  if (viewId === 'view-dashboard') renderDashboardHistory();
  if (viewId === 'view-problems') renderProblemBank();
}

// DASHBOARD HISTORY RENDERER
function renderDashboardHistory() {
  if (!DOM.dashboardHistoryBody) return;
  const history = dashboardService.getPastRoomsHistory();
  DOM.dashboardHistoryBody.innerHTML = '';

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
    DOM.dashboardHistoryBody.appendChild(tr);
  });
}

// AUTH SYSTEM
function initAuthSystem() {
  if (DOM.userPillTrigger) {
    DOM.userPillTrigger.addEventListener('click', (e) => {
      e.stopPropagation();
      DOM.accountDropdownMenu.classList.toggle('hidden');
    });
    document.addEventListener('click', () => DOM.accountDropdownMenu.classList.add('hidden'));
  }

  if (DOM.btnNavSignIn) DOM.btnNavSignIn.addEventListener('click', () => DOM.modalSignIn.classList.remove('hidden'));
  if (DOM.btnNavSignUp) DOM.btnNavSignUp.addEventListener('click', () => DOM.modalSignUp.classList.remove('hidden'));
  if (DOM.btnCloseSignIn) DOM.btnCloseSignIn.addEventListener('click', () => DOM.modalSignIn.classList.add('hidden'));
  if (DOM.btnCloseSignUp) DOM.btnCloseSignUp.addEventListener('click', () => DOM.modalSignUp.classList.add('hidden'));

  if (DOM.formSignIn) {
    DOM.formSignIn.addEventListener('submit', async (e) => {
      e.preventDefault();
      const email = document.getElementById('signin-email').value;
      await authService.login(email, "password");
      state.currentUser = authService.getCurrentUser();
      document.getElementById('global-user-handle').innerText = state.currentUser.username;
      DOM.modalSignIn.classList.add('hidden');
      switchView('view-dashboard');
    });
  }

  if (DOM.formSignUp) {
    DOM.formSignUp.addEventListener('submit', async (e) => {
      e.preventDefault();
      const username = document.getElementById('signup-username').value;
      const email = document.getElementById('signup-email').value;
      await authService.register(username, email, "password");
      state.currentUser = authService.getCurrentUser();
      document.getElementById('global-user-handle').innerText = state.currentUser.username;
      DOM.modalSignUp.classList.add('hidden');
      switchView('view-dashboard');
    });
  }

  if (DOM.btnDropSignOut) {
    DOM.btnDropSignOut.addEventListener('click', () => {
      authService.logout();
      switchView('view-rooms');
    });
  }
}

// ROOM CREATION & PROBLEM SOURCE PICKER
function initRoomCreationForm() {
  if (DOM.btnDashCreateRoom) DOM.btnDashCreateRoom.addEventListener('click', () => openCreateRoomModal());
  if (DOM.btnCreateRoomModal) DOM.btnCreateRoomModal.addEventListener('click', () => openCreateRoomModal());
  if (DOM.btnCloseCreateRoom) DOM.btnCloseCreateRoom.addEventListener('click', () => DOM.modalCreateRoom.classList.add('hidden'));
  if (DOM.btnCancelCreateRoom) DOM.btnCancelCreateRoom.addEventListener('click', () => DOM.modalCreateRoom.classList.add('hidden'));

  // Toggle between Past Problem Bank vs New Custom Inline Problem
  if (DOM.selectProblemSource) {
    DOM.selectProblemSource.addEventListener('change', (e) => {
      if (e.target.value === 'custom') {
        DOM.sectionPickerBank.classList.add('hidden');
        DOM.sectionPickerCustom.classList.remove('hidden');
      } else {
        DOM.sectionPickerBank.classList.remove('hidden');
        DOM.sectionPickerCustom.classList.add('hidden');
      }
    });
  }

  // Submit Room Creation Form
  if (DOM.formCreateRoom) {
    DOM.formCreateRoom.addEventListener('submit', (e) => {
      e.preventDefault();
      const title = document.getElementById('input-room-title').value;
      const source = DOM.selectProblemSource.value;
      const timeMode = document.getElementById('select-time-mode').value;
      const hasTimeLimit = timeMode === 'timed';

      let selectedProblem = null;

      if (source === 'custom') {
        // Create problem right now and save to database!
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
        const probId = DOM.selectProblemBankItem.value;
        selectedProblem = problemService.getProblemById(probId);
      }

      // Launch Room linked with problem and unique join code + QR!
      const room = roomService.createRoom({
        title: title,
        host: state.currentUser.username,
        problemId: selectedProblem.id,
        customProblem: selectedProblem,
        hasTimeLimit: hasTimeLimit,
        timeLimitMins: 15
      });

      DOM.modalCreateRoom.classList.add('hidden');
      renderRooms();
      joinRoom(room.id);
    });
  }
}

function openCreateRoomModal() {
  populateProblemBankSelect();
  DOM.modalCreateRoom.classList.remove('hidden');
}

function populateProblemBankSelect() {
  if (!DOM.selectProblemBankItem) return;
  const problems = problemService.getAllProblems();
  DOM.selectProblemBankItem.innerHTML = '';
  problems.forEach(p => {
    const opt = document.createElement('option');
    opt.value = p.id;
    opt.innerText = `${p.title} (${p.difficulty}) — v${p.version || 1}`;
    DOM.selectProblemBankItem.appendChild(opt);
  });
}

// ROOMS GRID & LOBBY
function renderRooms() {
  if (!DOM.roomsGrid) return;
  DOM.roomsGrid.innerHTML = '';
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
    DOM.roomsGrid.appendChild(card);
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

  document.getElementById('lobby-room-title').innerText = room.title;
  document.getElementById('lobby-host-name').innerText = room.host;
  document.getElementById('lobby-room-code').innerText = room.code;

  if (window.QRCode) {
    const container = document.getElementById('lobby-qr-render-area');
    container.innerHTML = '';
    new QRCode(container, { text: `https://codebattle.app/join?code=${room.code}`, width: 90, height: 90 });
  }

  switchView('view-room-lobby');
}

// BATTLE ARENA & EXECUTION
function initBattleActions() {
  if (DOM.btnHostStartBattle) {
    DOM.btnHostStartBattle.addEventListener('click', () => {
      switchView('view-battle');
      setupBattleArena();
    });
  }

  if (DOM.btnLeaveRoom) DOM.btnLeaveRoom.addEventListener('click', () => switchView('view-rooms'));

  if (DOM.btnRunCode) {
    DOM.btnRunCode.addEventListener('click', async () => {
      DOM.consoleSummaryText.innerText = "▶ Executing code in micro-container sandbox...";
      const res = await submissionService.executeCode({ code: "", language: "python", problem: state.activeProblem });
      DOM.consoleSummaryText.innerHTML = `<span style="color:var(--success)">✔ Visible Test Cases Passed (${res.passedCount}/${res.totalCount})</span>`;
    });
  }

  if (DOM.btnSubmitCode) {
    DOM.btnSubmitCode.addEventListener('click', async () => {
      DOM.consoleSummaryText.innerText = "⚡ Evaluating solution...";
      const res = await submissionService.executeCode({ code: "", language: "python", problem: state.activeProblem, isSubmission: true });

      // Save to Dashboard History!
      dashboardService.recordRoomSubmission({
        roomId: state.activeRoom.id,
        roomTitle: state.activeRoom.title,
        opponents: [state.activeRoom.host, "DevNinja"],
        problemTitle: state.activeProblem ? state.activeProblem.title : "Challenge",
        language: DOM.editorLangSelect ? DOM.editorLangSelect.value : "Python",
        result: "Correct Answer (Fastest #1)",
        status: "Accepted",
        execTimeMs: res.executionTimeMs,
        xpEarned: 60
      });

      authService.updateXP(60);
      switchView('view-results');
    });
  }

  if (DOM.btnBackToDashboard) {
    DOM.btnBackToDashboard.addEventListener('click', () => switchView('view-dashboard'));
  }

  if (DOM.btnOpenQR) {
    DOM.btnOpenQR.addEventListener('click', () => {
      DOM.modalQRConnect.classList.remove('hidden');
      if (window.QRCode) {
        const container = document.getElementById('modal-qr-render-area');
        container.innerHTML = '';
        new QRCode(container, { text: `https://codebattle.app/connect?code=${state.currentUser.mutualCode}`, width: 160, height: 160 });
      }
    });
  }

  if (DOM.btnCloseQRModal) DOM.btnCloseQRModal.addEventListener('click', () => DOM.modalQRConnect.classList.add('hidden'));
}

function setupBattleArena() {
  const p = state.activeProblem || problemService.getAllProblems()[0];
  document.getElementById('battle-problem-title').innerText = p.title;
  document.getElementById('battle-diff-badge').innerText = p.difficulty;
  document.getElementById('problem-description-body').innerHTML = `<p>${p.description}</p>`;

  const timerLabel = document.getElementById('timer-mode-label');
  const timerClock = document.getElementById('battle-timer-clock');

  if (state.activeRoom && !state.activeRoom.hasTimeLimit) {
    timerLabel.innerText = "TIME MODE";
    timerClock.innerText = "☕ Relaxed (No Limit)";
  } else {
    timerLabel.innerText = "TIME REMAINING";
    timerClock.innerText = "14:59";
  }
}

// PROBLEM BANK TABLE RENDERER
function renderProblemBank() {
  if (!DOM.problemsTableBody) return;
  DOM.problemsTableBody.innerHTML = '';
  const problems = problemService.getAllProblems();

  problems.forEach(p => {
    const tr = document.createElement('tr');
    tr.innerHTML = `
      <td><strong>${p.title}</strong></td>
      <td><span class="badge diff-medium">${p.difficulty}</span></td>
      <td>${p.category}</td>
      <td><code>v${p.version || 1} (${p.commits ? p.commits.length : 1} commits)</code></td>
      <td><button class="btn btn-outline btn-sm">View Question</button></td>
    `;
    DOM.problemsTableBody.appendChild(tr);
  });
}

// MONACO EDITOR
function initMonacoEditor() {
  if (window.require) {
    window.require.config({ paths: { 'vs': 'https://cdnjs.cloudflare.com/ajax/libs/monaco-editor/0.45.0/min/vs' } });
    window.require(['vs/editor/editor.main'], function() {
      const container = document.getElementById('monaco-editor-instance');
      if (!container) return;
      state.monacoEditor = monaco.editor.create(container, {
        value: STARTER_CODE_TEMPLATES.python,
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
