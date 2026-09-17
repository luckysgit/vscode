"""P0 regression checks in isolated browser profiles and temporary SQLite data.
Run with Python Playwright and local Chrome; optional CODEBATTLE_TEST_CHROME overrides it.
"""
import os
import uuid
from test_problems import payload
from pathlib import Path
import subprocess
import tempfile
import time
from urllib.request import urlopen
from playwright.sync_api import sync_playwright, expect

ROOT = Path(__file__).resolve().parents[1]
BASE = 'http://localhost:5101'
PAYLOAD = '<img src="/missing-audit-image" onerror="window.__xss=1">'
with tempfile.TemporaryDirectory() as directory:
    env = dict(os.environ, CODEBATTLE_MODE='test', PORT='5101', CODEBATTLE_DB=str(Path(directory) / 'accounts.sqlite3'))
    with open(Path(directory) / 'server.log', 'w+') as log:
        server = subprocess.Popen(['python3', '-u', 'server/server.py'], cwd=ROOT, env=env, stdout=log, stderr=log)
        try:
            ready = False
            for _ in range(100):
                if server.poll() is not None:
                    log.seek(0)
                    raise AssertionError(log.read())
                try:
                    with urlopen(BASE + '/api/health', timeout=1):
                        ready = True
                        break
                except OSError:
                    time.sleep(.1)
            assert ready, 'Test server did not become ready'
            with sync_playwright() as p:
                browser = p.chromium.launch(executable_path=os.environ.get('CODEBATTLE_TEST_CHROME', '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'), headless=True)
                # Removing CSP only from this test profile proves DOM fixes do not rely on CSP.
                context = browser.new_context(bypass_csp=True)
                page = context.new_page()
                errors = []
                page.on('pageerror', lambda error: errors.append(str(error)))
                page.on('dialog', lambda dialog: dialog.accept())
                page.route('https://**/*', lambda route: route.abort())
                page.goto(BASE)
                page.locator('#btn-continue-guest').click()
                expect(page.locator('#auth-welcome')).to_be_hidden()
                registered = context.request.post(BASE+'/api/auth/register', data=dict(username='SecurityAuthor',email='security@example.com',password='security test password'))
                assert registered.status == 201
                problem = context.request.post(BASE+'/api/problems', data=payload()).json()['problem']
                published = context.request.post(BASE+f"/api/problems/{problem['id']}/publish",data={'revision':problem['revision']}).json()['problem']
                room = context.request.post(BASE+'/api/rooms',data=dict(title=PAYLOAD,problemVersionId=published['problemVersionId'],requestId=str(uuid.uuid4()))).json()['room']
                page.evaluate("payload => problemService.createProblem({title:payload,description:payload})",PAYLOAD)
                page.reload()
                expect(page.locator('#modal-entry-options')).to_be_visible()
                page.locator('#btn-continue-account').click()
                page.locator('#main-nav-links [data-target="view-rooms"]').click()
                expect(page.locator('.room-title').first).to_have_text(PAYLOAD)
                assert page.locator('.room-title img').count() == 0
                page.locator('#main-nav-links [data-target="view-problems"]').click()
                expect(page.locator('#problems-table-body tr').first).to_contain_text(PAYLOAD)
                assert page.locator('#problems-table-body img').count() == 0
                # Exercise attribute payloads and other dynamic renderers through their data sources.
                page.evaluate('''payload => {
                  problemService.problems[0].id = '\" onfocus=\"window.__xss=1';
                  renderProblemBank();
                  dashboardService.history = [{roomTitle: payload, joinedAt: payload, problemTitle: payload,
                    opponents: [payload], language: payload, result: payload, xpEarned: payload}];
                  renderDashboardHistory();
                  leaderboardService.getRankings = () => [{rank: payload, handle: payload, tier: payload, solves: 0, xp: 0}];
                  renderLeaderboard();
                }''', PAYLOAD)
                assert page.locator('[onfocus], [onerror], #dashboard-history-table-body img, #leaderboard-table-body img').count() == 0
                assert page.evaluate('window.__xss === undefined')
                # Old practice samples are sanitized; legacy room caches are discarded.
                page.evaluate('''() => {
                  const problem = {id: 'cached', title: 'Cache migration', testCases: [
                    {input: 'public', expected: 'ok', isHidden: false},
                    {input: 'HIDDEN-SENTINEL', expected: 'secret', isHidden: true}]};
                  localStorage.setItem('cb_custom_problems_bank', JSON.stringify([problem]));
                  localStorage.setItem('cb_rooms_history', JSON.stringify([{id:'cached-room', title:'cached room', customProblem:problem}]));
                }''')
                page.reload()
                expect(page.locator('#modal-entry-options')).to_be_visible()
                page.keyboard.press('Escape')
                expect(page.locator('#auth-welcome')).to_be_hidden()
                cache = page.evaluate("[localStorage.getItem('cb_custom_problems_bank'), localStorage.getItem('cb_rooms_history')]")
                assert 'HIDDEN-SENTINEL' not in cache[0] and 'public' in cache[0]
                assert cache[1] is None, 'Legacy room data must no longer be read or retained'
                # A quota/storage write failure must not replace the user's loaded records with seeds.
                preserved = page.evaluate("""() => {
                  const original = Storage.prototype.setItem;
                  const cached = {id:'kept', title:'Keep my problem', testCases:[
                    {input:'visible',expected:'ok',isHidden:false}, {input:'private',expected:'no',isHidden:true}]};
                  localStorage.setItem('cb_custom_problems_bank', JSON.stringify([cached]));
                  Storage.prototype.setItem = () => { throw new Error('Storage unavailable'); };
                  try { return new ProblemService().getAllProblems()[0]; }
                  finally { Storage.prototype.setItem = original; }
                }""")
                assert preserved['id'] == 'kept' and len(preserved['testCases']) == 1
                assert not errors, errors
                # Independent context retains the real CSP. Inline events/scripts must be blocked.
                protected = browser.new_context()
                secured = protected.new_page()
                secured.route('https://**/*', lambda route: route.abort())
                response = secured.goto(BASE)
                assert "script-src-attr 'none'" in response.headers['content-security-policy']
                secured.evaluate('''() => {
                  const button = document.createElement('button');
                  button.setAttribute('onclick', 'window.__inlineRan = true');
                  document.body.append(button); button.click();
                  const script = document.createElement('script');
                  script.textContent = 'window.__inlineRan = true'; document.body.append(script);
                }''')
                assert secured.evaluate('window.__inlineRan === undefined')
                browser.close()
                print('PASS: text-only renderers (CSP bypassed), reload safety, safe attributes, legacy cache cleanup, enforced CSP')
        finally:
            server.terminate()
            server.wait(timeout=10)
