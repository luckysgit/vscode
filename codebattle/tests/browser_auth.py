"""Run with Python Playwright and locally installed Chrome. Uses temporary account data."""
import os
import subprocess
import tempfile
import time
from pathlib import Path
from urllib.request import urlopen
from playwright.sync_api import sync_playwright, expect

root = Path(__file__).resolve().parents[1]
with tempfile.TemporaryDirectory() as temp:
    env = dict(os.environ, CODEBATTLE_MODE='test', PORT='5099', CODEBATTLE_DB=str(Path(temp) / 'browser.sqlite3'))
    process = subprocess.Popen(['python3', '-u', 'server/server.py'], cwd=root, env=env,
                               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        for _ in range(50):
            try:
                with urlopen('http://localhost:5099/api/health', timeout=1):
                    break
            except OSError:
                time.sleep(.1)
        with sync_playwright() as p:
            browser = p.chromium.launch(executable_path='/Applications/Google Chrome.app/Contents/MacOS/Google Chrome', headless=True)
            context = browser.new_context()
            page = context.new_page()
            errors = []
            page.on('pageerror', lambda error: errors.append(str(error)))
            # Account entry must work even if optional CDN editor/QR libraries are unavailable.
            page.route('https://**/*', lambda route: route.abort())
            page.goto('http://localhost:5099/')
            page.screenshot(path='/tmp/codebattle-welcome.png', full_page=True)
            expect(page.locator('#btn-continue-guest')).to_be_enabled()
            page.locator('#btn-continue-guest').click()
            expect(page.locator('#auth-welcome')).to_be_hidden()
            expect(page.locator('.app-view:visible')).to_have_count(1)
            page.screenshot(path='/tmp/codebattle-dashboard.png', full_page=True)
            page.locator('#main-nav-links [data-target="view-problems"]').click()
            expect(page.locator('#view-problems')).to_be_visible()
            expect(page.locator('#view-dashboard')).to_be_hidden()
            page.locator('#main-nav-links [data-target="view-rooms"]').click()
            expect(page.locator('#view-rooms')).to_be_visible()
            page.screenshot(path='/tmp/codebattle-rooms.png', full_page=True)
            guest = page.locator('#global-user-handle').inner_text()
            assert guest.startswith('Guest_')
            page.reload()
            expect(page.locator('#modal-entry-options')).to_be_visible()
            page.keyboard.press('Escape')
            expect(page.locator('#global-user-handle')).to_have_text(guest)
            page.locator('#btn-nav-sign-up').click()
            page.locator('#signup-username').fill('BrowserCoder')
            page.locator('#signup-email').fill('browser@example.com')
            page.locator('#signup-password').fill('browser test password')
            page.locator('#form-sign-up button[type=submit]').click()
            expect(page.locator('#global-user-handle')).to_have_text('BrowserCoder')
            expect(page.locator('#auth-actions-logged-out')).to_be_hidden()
            page.reload()
            expect(page.locator('#modal-entry-options')).to_be_visible()
            page.keyboard.press('Escape')
            expect(page.locator('#global-user-handle')).to_have_text('BrowserCoder')
            page.locator('#user-pill-trigger').click()
            page.locator('#btn-drop-sign-out').click()
            expect(page.locator('#auth-welcome')).to_be_visible()
            page.locator('#modal-entry-options [data-open-auth="modal-sign-in"]').click()
            page.locator('#signin-email').fill('browser@example.com')
            page.locator('#signin-password').fill('wrong password')
            page.locator('#form-sign-in button[type=submit]').click()
            expect(page.locator('#signin-error')).to_have_text('Invalid email or password.')
            page.locator('#signin-password').fill('browser test password')
            page.locator('#form-sign-in button[type=submit]').click()
            expect(page.locator('#auth-welcome')).to_be_hidden()
            expect(page.locator('#global-user-handle')).to_have_text('BrowserCoder')
            assert 'cb_session' not in page.evaluate('document.cookie')
            second = browser.new_context(viewport={'width': 390, 'height': 844})
            mobile = second.new_page()
            mobile.route('https://**/*', lambda route: route.abort())
            mobile.goto('http://localhost:5099/')
            expect(mobile.locator('#btn-continue-guest')).to_be_enabled()
            expect(mobile.locator('#auth-welcome')).to_be_visible()
            assert mobile.evaluate('document.documentElement.scrollWidth <= innerWidth')
            mobile.screenshot(path='/tmp/codebattle-mobile.png', full_page=True)
            mobile.locator('#btn-continue-guest').click()
            expect(mobile.locator('#auth-welcome')).to_be_hidden()
            assert mobile.locator('#global-user-handle').inner_text() != 'BrowserCoder'
            assert not errors, errors
            browser.close()
            print('PASS: guest, reload, signup, logout, wrong password, login, HttpOnly cookie, isolated mobile session, no JavaScript errors')
    finally:
        process.terminate()
        process.wait(timeout=10)
