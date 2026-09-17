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
const roomsUI = new RoomsUI();
const problemBankUI = new ProblemBankUI(document.getElementById('view-my-problems'));

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
async function initApp() {
  problemBankUI.init();
  initNavigation();
  initAuthSystem();
  renderDashboardHistory();
  renderRooms();
  renderProblemBank();
  renderLeaderboard();
  renderProfile();
  roomsUI.init();
  initMonacoEditor();
  initBattleActions();



  initSettingsForm();
  initExtraInteractions();
  try {
    await authService.restore();
    syncAuthUI();
    if (location.pathname.startsWith('/problems/')) problemBankUI.route(location.pathname);
  } catch (_) {
    document.getElementById('welcome-error').textContent = 'Cannot connect to the server. Please retry.';
  }
  document.querySelectorAll('[data-auth-action]').forEach(button => { button.disabled = false; });
  document.dispatchEvent(new Event('entry-options-requested'));
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
      if (targetView === 'view-my-problems') problemBankUI.navigate('/problems/my');
      else if (targetView) switchView(targetView);
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
  if (!problemBankUI.canLeave(viewId)) return;
  if (!authService.currentUser) {
    document.getElementById('auth-welcome').classList.remove('hidden');
    return;
  }
  hideAllModals();

  const views = document.querySelectorAll('.app-view');
  const navLinks = document.querySelectorAll('.nav-link, .mobile-nav-item');

  views.forEach(v => v.classList.remove('active'));
  document.querySelectorAll('.nav-link').forEach(link => link.removeAttribute('aria-current'));
  navLinks.forEach(l => l.classList.remove('active'));

  const target = document.getElementById(viewId);
  if (target) target.classList.add('active');

  navLinks.forEach(l => {
    if (l.getAttribute('data-target') === viewId) { l.classList.add('active'); l.setAttribute('aria-current', 'page'); }
  });

  if (viewId === 'view-dashboard') renderDashboardHistory();
  if (viewId === 'view-problems') renderProblemBank();
  if (viewId === 'view-leaderboard') renderLeaderboard();
  if (viewId === 'view-profile') renderProfile();
  if (viewId === 'view-rooms') renderRooms();
}

// Dynamic content is always text, never parsed markup. Class names are caller-owned constants.
function uiElement(tag, className = '', text = '') {
  const node = document.createElement(tag);
  if (className) node.className = className;
  node.textContent = String(text ?? '');
  return node;
}

function tableCell(...children) {
  const cell = document.createElement('td');
  cell.append(...children);
  return cell;
}

// DASHBOARD HISTORY RENDERER
function renderDashboardHistory() {
  const body = document.getElementById('dashboard-history-table-body');
  if (!body) return;
  const history = []; // Competition results are not recorded until competition execution exists.
  body.replaceChildren();
  if (!history.length) {
    const row = document.createElement('tr'); const cell = tableCell(uiElement('span', 'text-subtle', 'No completed competitions yet.')); cell.colSpan = 6; row.append(cell); body.append(row);
  }

  history.forEach(item => {
    const tr = document.createElement('tr');
    const points = uiElement('strong', '', `${item.xpEarned} XP`);
    points.style.color = 'var(--cyan)';
    tr.append(
      tableCell(uiElement('strong', '', item.roomTitle), document.createElement('br'), uiElement('span', 'text-subtle', item.joinedAt)),
      tableCell(uiElement('strong', '', item.problemTitle)),
      tableCell(uiElement('span', 'badge badge-info', Array.isArray(item.opponents) ? item.opponents.join(', ') : '')),
      tableCell(uiElement('code', '', item.language)),
      tableCell(uiElement('span', 'badge badge-success', item.result)),
      tableCell(points)
    );
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
      trigger.setAttribute('aria-expanded', String(!menu.classList.contains('hidden')));
    });
    document.addEventListener('click', () => { menu.classList.add('hidden'); trigger.setAttribute('aria-expanded', 'false'); });
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

  if (btnSignIn && modalSignIn) btnSignIn.addEventListener('click', () => openAuth('modal-sign-in'));
  if (btnSignUp && modalSignUp) btnSignUp.addEventListener('click', () => openAuth('modal-sign-up'));
  if (closeSignIn && modalSignIn) closeSignIn.addEventListener('click', () => modalSignIn.classList.add('hidden'));
  if (closeSignUp && modalSignUp) closeSignUp.addEventListener('click', () => modalSignUp.classList.add('hidden'));

  let authOpener = null;
  document.addEventListener('keydown', event => {
    const dialog = document.querySelector('#modal-sign-in:not(.hidden), #modal-sign-up:not(.hidden), #modal-entry-options:not(.hidden)');
    if (!dialog) return;
    if (event.key === 'Escape') {
      dialog.classList.add('hidden');
      authOpener?.focus();
    }
    if (event.key === 'Tab') {
      const controls = [...dialog.querySelectorAll('button:not(:disabled), input:not(:disabled)')].filter(control => control.getClientRects().length);
      const first = controls[0], last = controls[controls.length - 1];
      if (event.shiftKey && document.activeElement === first) { event.preventDefault(); last.focus(); }
      if (!event.shiftKey && document.activeElement === last) { event.preventDefault(); first.focus(); }
    }
  });
  function openAuth(id) {
    authOpener = document.activeElement;
    hideAllModals();
    document.getElementById(id).classList.remove('hidden');
    document.querySelector(`#${id} input`)?.focus();
  }
  function showEntryOptions() {
    const resume = document.getElementById('btn-continue-account');
    resume.classList.toggle('hidden', !authService.isAuthenticated());
    resume.textContent = `Continue as ${authService.getCurrentUser().username}`;
    openAuth('modal-entry-options');
    document.querySelector('#modal-entry-options button:not(.hidden):not(:disabled)')?.focus();
  }
  document.addEventListener('entry-options-requested', showEntryOptions);
  document.getElementById('btn-open-entry').addEventListener('click', showEntryOptions);
  document.getElementById('btn-continue-account').addEventListener('click', () => {
    hideAllModals();
    syncAuthUI();
    document.getElementById('main-view-container').focus();
  });
  document.addEventListener('submission-auth-required', () => {
    state.submissionAuthRequested = true;
    document.querySelectorAll('.submission-auth-notice').forEach(node => node.classList.remove('hidden'));
    openAuth('modal-sign-up');
  });
  document.querySelectorAll('[data-open-auth]').forEach(button => {
    button.addEventListener('click', () => openAuth(button.dataset.openAuth));
  });

  async function perform(button, errorId, action, form) {
    const error = document.getElementById(errorId);
    error.textContent = '';
    if (problemBankUI.busy || roomsUI.busy) { error.textContent = 'Please wait for the current save to finish.'; return; }
    if (problemBankUI.dirty && !confirm('Discard unsaved problem changes before changing accounts?')) return;
    button.disabled = true;
    const keepWorkspace = !!form && document.getElementById('view-battle').classList.contains('active')
      && (state.submissionAuthRequested || !authService.isAuthenticated());
    const draft = keepWorkspace ? state.monacoEditor?.getValue() : null;
    try {
      await action();
      state.currentUser = authService.getCurrentUser();
      if (form) form.reset();
      if (keepWorkspace && authService.isAuthenticated()) {
        // Transfer only the code visible during this explicit authentication flow.
        state.editorDraftKey = null;
        loadProblemEditor(state.activeProblem);
        if (draft != null) state.monacoEditor?.setValue(draft);
        syncAuthUI();
        hideAllModals();
        document.getElementById('console-summary-text').textContent = 'You are signed in. Submit your solution when ready.';
        document.getElementById('btn-submit-code').focus();
      } else {
        state.editorDraftKey = null;
        state.monacoEditor?.setValue('');
        state.activeRoom = null;
        state.activeProblem = null;
        clearInterval(state.battleTimer);
        syncAuthUI();
        hideAllModals();
        if (authService.currentUser) {
          if (location.pathname.startsWith('/problems/')) problemBankUI.route(location.pathname);
          else switchView('view-dashboard');
        }
      }
      if (!authService.currentUser) showEntryOptions();
      state.submissionAuthRequested = false;
      document.querySelectorAll('.submission-auth-notice').forEach(node => node.classList.add('hidden'));
    } catch (err) {
      error.textContent = err.message || 'Unable to connect. Please try again.';
    } finally {
      button.disabled = false;
    }
  }

  const formSignIn = document.getElementById('form-sign-in');
  formSignIn.addEventListener('submit', e => {
    e.preventDefault();
    perform(formSignIn.querySelector('[type=submit]'), 'signin-error', () => authService.login(
      document.getElementById('signin-email').value,
      document.getElementById('signin-password').value), formSignIn);
  });
  const formSignUp = document.getElementById('form-sign-up');
  formSignUp.addEventListener('submit', e => {
    e.preventDefault();
    perform(formSignUp.querySelector('[type=submit]'), 'signup-error', () => authService.register(
      document.getElementById('signup-username').value,
      document.getElementById('signup-email').value,
      document.getElementById('signup-password').value), formSignUp);
  });
  const guestButton = document.getElementById('btn-continue-guest');
  guestButton.addEventListener('click', () => perform(guestButton, 'welcome-error', async () => {
    // Choosing guest explicitly switches away from a restored registered session.
    if (authService.isAuthenticated()) await authService.logout();
    return authService.guest();
  }));
  const signOut = document.getElementById('btn-drop-sign-out');
  signOut.addEventListener('click', () => perform(signOut, 'session-error', () => authService.logout()));
}

function syncAuthUI() {
  const user = authService.getCurrentUser();
  problemBankUI.identityChanged(authService.currentUser);
  roomsUI.identityChanged(authService.currentUser);
  state.currentUser = user;
  const hasSession = !!authService.currentUser;
  document.body.classList.toggle('has-session', hasSession);
  document.getElementById('auth-welcome').classList.toggle('hidden', hasSession);
  document.getElementById('main-view-container').inert = !hasSession;
  document.getElementById('auth-actions-logged-out').classList.toggle('hidden', authService.isAuthenticated());
  document.getElementById('auth-user-wrapper').classList.toggle('hidden', !hasSession);
  document.getElementById('global-user-handle').textContent = user.username;
  document.getElementById('dropdown-user-email').textContent = user.isGuest ? 'Guest session — create an account to keep access' : user.email;
  document.getElementById('global-user-streak').textContent = `${user.streak}`;
  document.getElementById('user-xp-bar').style.width = '0%';
  document.getElementById('user-rank-icon').textContent = user.username.slice(0, 1).toUpperCase();
  document.getElementById('dash-welcome-handle').textContent = user.username;
  document.getElementById('dash-xp-val').textContent = `${user.xp} XP`;
  document.getElementById('dash-streak-val').textContent = `${user.streak} days`;
  document.getElementById('btn-drop-admin').classList.add('hidden');
  renderProfile();

}

// Room listing and joining use the shared server database.
function renderRooms() { return roomsUI.load(); }
function joinRoom(key) { return roomsUI.join(key); }

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

  for (const button of [btnRun, btnSubmit]) {
    if (!button || !consoleSummary) continue;
    button.addEventListener('click', async () => {
      if (button === btnSubmit && !authService.isAuthenticated()) {
        document.dispatchEvent(new Event('submission-auth-required'));
        return;
      }
      btnRun.disabled = btnSubmit.disabled = true;
      const outputPanel = document.getElementById('code-output');
      outputPanel.textContent = '';
      consoleSummary.textContent = button === btnSubmit ? 'Checking tests…' : 'Running code…';
      try {
        const response = await submissionService.executeCode({
          code: state.monacoEditor?.getValue() || '',
          language: document.getElementById('editor-lang-select').value,
          stdin: document.getElementById('code-stdin').value,
          problem: state.activeProblem, isSubmission: button === btnSubmit
        });
        const result = response.result || {};
        const labels = {completed: 'Run completed', accepted: 'Accepted', wrong_answer: 'Wrong answer',
          memory_limit: 'Memory limit exceeded', runtime_error: 'Runtime error', time_limit: 'Time limit exceeded', output_limit: 'Output limit exceeded'};
        const count = result.total ? ` · ${result.passed}/${result.total} tests passed` : '';
        consoleSummary.textContent = `${labels[result.status] || result.status}${count} · ${result.execution_time_ms} ms${result.is_submission ? ' · Result saved' : ''}`;
        outputPanel.textContent = [result.stdout, result.stderr].filter(Boolean).join('\n') || (result.is_submission ? '' : '(No output. Use print() to display a result.)');
      } catch (error) {
        consoleSummary.textContent = error.message;
        if (button === btnSubmit && (error.status === 401 || error.status === 403)) {
          document.dispatchEvent(new Event('submission-auth-required'));
        }
      } finally {
        btnRun.disabled = btnSubmit.disabled = false;
      }
    });
  }

  if (btnBack) btnBack.addEventListener('click', () => switchView('view-dashboard'));

  if (btnOpenQR && modalQR) {
    btnOpenQR.addEventListener('click', () => {
      modalQR.classList.remove('hidden');
      if (window.QRCode) {
        const container = document.getElementById('modal-qr-render-area');
        if (container) {
          container.replaceChildren();
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
  state.activeProblem = p;
  loadProblemEditor(p);
  const samples = document.getElementById('testcase-results-list');
  samples.replaceChildren();
  (p.testCases || []).forEach((test, index) => samples.append(uiElement('pre', 'code-block',
    `Example ${index + 1}\nInput:\n${test.input}\nExpected output:\n${test.expected}`)));
  document.getElementById('code-stdin').value = p.testCases?.[0]?.input || '';
  document.getElementById('code-output').textContent = '';
  document.getElementById('console-summary-text').textContent = 'Run uses standard input. Submit checks the built-in problem tests.';
  const titleElem = document.getElementById('battle-problem-title');
  const diffElem = document.getElementById('battle-diff-badge');
  const descElem = document.getElementById('problem-description-body');

  if (titleElem) titleElem.innerText = p.title;
  if (diffElem) diffElem.innerText = p.difficulty;
  if (descElem) descElem.textContent = `${p.description}\n\nInput format\n${p.inputFormat || 'Standard input'}\n\nOutput format\n${p.outputFormat || 'Standard output'}\n\nWrite a complete Python program. Read with input() and print your answer.`;

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
  tbody.replaceChildren();
  const problems = problemService.getAllProblems();

  problems.forEach(p => {
    const tr = document.createElement('tr');
    const solve = uiElement('button', 'btn btn-outline btn-sm btn-solve-solo', 'Solve Solo');
    solve.type = 'button';
    solve.dataset.id = String(p.id);
    tr.append(
      tableCell(uiElement('strong', '', p.title)),
      tableCell(uiElement('span', 'badge diff-medium', p.difficulty)),
      tableCell(uiElement('span', '', p.category)),
      tableCell(uiElement('code', '', `v${p.version || 1} (${Array.isArray(p.commits) ? p.commits.length : 1} commits)`)),
      tableCell(solve)
    );
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

function loadProblemEditor(problem) {
  if (!state.monacoEditor || !problem) return;
  const key = `cb_draft:${state.currentUser?.id}:${problem.id}:python`;
  if (state.editorDraftKey === key) return;
  state.editorDraftKey = key;
  let draft = null;
  try { draft = localStorage.getItem(key); } catch (_) { /* Storage may be unavailable. */ }
  const starter = problem.id === 'p1'
    ? '# Read the numbers and target, then print two space-separated indices.\nnums = list(map(int, input().split()))\ntarget = int(input())\n\n# Write your solution here\n'
    : '# Read standard input with input() and print your answer.\n# Write your solution here\n';
  state.monacoEditor.setValue(draft ?? starter);
}

// MONACO EDITOR INITIALIZER
function initMonacoEditor() {
  if (window.require) {
    window.require.config({ paths: { 'vs': 'https://cdnjs.cloudflare.com/ajax/libs/monaco-editor/0.45.0/min/vs' } });
    window.require(['vs/editor/editor.main'], function() {
      const container = document.getElementById('monaco-editor-instance');
      if (!container) return;
      state.monacoEditor = monaco.editor.create(container, {
        value: '# Read standard input and print your answer.\n# Two Sum input: numbers on line 1, target on line 2.\nnums = list(map(int, input().split()))\ntarget = int(input())\n\n# Write your solution here\n',
        language: 'python',
        theme: document.documentElement.dataset.theme === 'dark' ? 'vs-dark' : 'vs',
        automaticLayout: true,
        fontSize: 14,
        fontFamily: "'SF Mono', ui-monospace, monospace",
        minimap: { enabled: false },
        lineNumbers: 'on'
      });
      loadProblemEditor(state.activeProblem);
      state.monacoEditor.onDidChangeModelContent(() => {
        if (state.editorDraftKey) {
          try { localStorage.setItem(state.editorDraftKey, state.monacoEditor.getValue()); }
          catch (_) { /* Running code must remain possible without storage. */ }
        }
      });
    });
  }
}

// LEADERBOARD RENDERER
function renderLeaderboard() {
  const tbody = document.getElementById('leaderboard-table-body');
  if (!tbody) return;
  tbody.replaceChildren();
  const rankings = leaderboardService.getRankings();

  rankings.forEach(r => {
    const tr = document.createElement('tr');
    const points = uiElement('strong', '', `${Number(r.xp || 0).toLocaleString()} XP`);
    points.style.color = 'var(--cyan)';
    tr.append(
      tableCell(uiElement('strong', '', `#${r.rank}`)),
      tableCell(uiElement('strong', '', r.handle)),
      tableCell(uiElement('span', 'badge badge-master', r.tier)),
      tableCell(uiElement('span', '', `🔥 ${Number(r.solves) % 10 + 3} Days`)),
      tableCell(points)
    );
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
  if (emailDisp) emailDisp.textContent = user.isGuest ? 'Guest session — sign up to keep access to this identity.' : user.email;
  if (codeDisp) codeDisp.innerText = user.mutualCode || '';
  document.getElementById('prof-rank-badge').textContent = user.isGuest ? 'Guest' : 'Bronze Rank';
  document.getElementById('profile-badges-container').textContent = 'No earned badges yet.';
  document.getElementById('profile-weakspots-container').textContent = 'No graded submissions yet.';
  if (xpDisp) xpDisp.innerText = `${(user.xp || 0).toLocaleString()} XP`;
  if (streakBadge) streakBadge.innerText = `🔥 ${user.streak || 0} Day Streak`;
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
        const challenge = uiElement('button', 'btn btn-outline btn-sm btn-challenge-user', 'Challenge');
        challenge.type = 'button';
        tr.append(
          tableCell(uiElement('strong', '', `ConnectedUser_${val}`)),
          tableCell(uiElement('code', '', val)),
          tableCell(uiElement('span', 'badge badge-success', 'Online')),
          tableCell(challenge)
        );
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
          container.replaceChildren();
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
      alert('Account preferences are not available yet. Your account has not been changed.');
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
      if (icon) icon.innerText = state.soundEnabled ? '♪' : '×';
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
