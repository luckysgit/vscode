"""End-to-end Run/Submit and viewport regression with real Monaco and isolated data."""
import os
from pathlib import Path
import subprocess
import tempfile
import time
from urllib.request import urlopen
from playwright.sync_api import sync_playwright, expect
from test_runner import SOLUTION

ROOT = Path(__file__).resolve().parents[1]
with tempfile.TemporaryDirectory() as directory:
    server = subprocess.Popen(['python3', '-u', 'server/server.py'], cwd=ROOT,
        env=dict(os.environ, CODEBATTLE_MODE='test', PORT='5103', CODEBATTLE_DB=str(Path(directory)/'accounts.sqlite3')),
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        for _ in range(100):
            try:
                with urlopen('http://localhost:5103/api/health', timeout=1): break
            except OSError: time.sleep(.1)
        with sync_playwright() as p:
            browser = p.chromium.launch(executable_path='/Applications/Google Chrome.app/Contents/MacOS/Google Chrome', headless=True)
            page = browser.new_page(viewport={'width':1440, 'height':900})
            errors = []
            page.on('pageerror', lambda e: errors.append(str(e)))
            page.goto('http://localhost:5103/', wait_until='domcontentloaded')
            page.locator('#btn-continue-guest').click()
            expect(page.locator('#auth-welcome')).to_be_hidden()
            for _ in range(150):
                if page.evaluate('!!state.monacoEditor'): break
                page.wait_for_timeout(200)
            assert page.evaluate('!!state.monacoEditor')
            page.locator('#main-nav-links [data-target="view-problems"]').click()
            page.locator('.btn-solve-solo').first.click()
            page.wait_for_timeout(1500)
            before = page.locator('.battle-workspace').bounding_box()['height']
            page.wait_for_timeout(1000)
            assert abs(page.locator('.battle-workspace').bounding_box()['height'] - before) < 2
            box = page.locator('#btn-run-code').bounding_box()
            assert box['y'] + box['height'] <= 900, box
            page.evaluate('state.monacoEditor.setValue(\'print("nums")\')')
            page.locator('#btn-run-code').click()
            expect(page.locator('#console-summary-text')).to_contain_text('Run completed', timeout=10000)
            expect(page.locator('#code-output')).to_have_text('nums\n')
            page.locator('#btn-submit-code').click()
            expect(page.locator('#modal-sign-up')).to_be_visible()
            expect(page.locator('#modal-sign-up .submission-auth-notice')).to_be_visible()
            page.locator('#btn-close-sign-up').click()
            assert page.evaluate('state.monacoEditor.getValue()') == 'print("nums")'
            page.locator('#btn-submit-code').click()
            page.locator('#signup-username').fill('RunnerCustomer')
            page.locator('#signup-email').fill('runner@example.com')
            page.locator('#signup-password').fill('runner test password')
            page.locator('#form-sign-up button[type=submit]').click()
            expect(page.locator('#modal-sign-up')).to_be_hidden()
            expect(page.locator('#view-battle')).to_be_visible()
            assert page.evaluate('state.monacoEditor.getValue()') == 'print("nums")'
            page.locator('#btn-submit-code').click()
            expect(page.locator('#console-summary-text')).to_contain_text('Wrong answer', timeout=10000)
            page.evaluate('code => state.monacoEditor.setValue(code)', SOLUTION)
            page.locator('#btn-run-code').click()
            expect(page.locator('#console-summary-text')).to_contain_text('Run completed', timeout=10000)
            expect(page.locator('#code-output')).to_have_text('0 1\n')
            page.locator('#btn-submit-code').click()
            expect(page.locator('#console-summary-text')).to_contain_text('Accepted · 5/5 tests passed', timeout=15000)
            page.screenshot(path='/tmp/codebattle-run-submit.png', full_page=True)
            page.evaluate('state.monacoEditor.setValue("print(")')
            page.locator('#btn-run-code').click()
            expect(page.locator('#console-summary-text')).to_contain_text('Runtime error', timeout=10000)
            expect(page.locator('#code-output')).to_contain_text('SyntaxError')
            page.evaluate('state.monacoEditor.setValue("while True: pass")')
            page.locator('#btn-run-code').click()
            expect(page.locator('#console-summary-text')).to_contain_text('Time limit exceeded', timeout=10000)
            expect(page.locator('#btn-submit-code')).to_be_enabled()
            page.evaluate('code => state.monacoEditor.setValue(code)', SOLUTION)
            page.reload()
            expect(page.locator('#modal-entry-options')).to_be_visible()
            page.keyboard.press('Escape')
            expect(page.locator('#auth-welcome')).to_be_hidden()
            for _ in range(150):
                if page.evaluate('!!state.monacoEditor'): break
                page.wait_for_timeout(200)
            page.locator('#main-nav-links [data-target="view-problems"]').click()
            page.locator('.btn-solve-solo').first.click()
            assert page.evaluate('state.monacoEditor.getValue()') == SOLUTION
            page.evaluate('document.getElementById("btn-drop-sign-out").click()')
            expect(page.locator('#auth-welcome')).to_be_visible()
            page.locator('#btn-continue-guest').click()
            expect(page.locator('#auth-welcome')).to_be_hidden()
            page.locator('#main-nav-links [data-target="view-problems"]').click()
            page.locator('.btn-solve-solo').first.click()
            page.evaluate('code => state.monacoEditor.setValue(code)', 'print("keep my code")')
            page.locator('#btn-submit-code').click()
            page.locator('#modal-sign-up [data-open-auth="modal-sign-in"]').click()
            expect(page.locator('#modal-sign-in')).to_be_visible()
            page.locator('#signin-email').fill('runner@example.com')
            page.locator('#signin-password').fill('incorrect password')
            page.locator('#form-sign-in button[type=submit]').click()
            expect(page.locator('#signin-error')).not_to_be_empty()
            assert page.evaluate('state.monacoEditor.getValue()') == 'print("keep my code")'
            page.locator('#signin-password').fill('runner test password')
            page.locator('#form-sign-in button[type=submit]').click()
            expect(page.locator('#modal-sign-in')).to_be_hidden()
            expect(page.locator('#view-battle')).to_be_visible()
            assert page.evaluate('state.monacoEditor.getValue()') == 'print("keep my code")'
            page.set_viewport_size({'width':390, 'height':844})
            page.locator('#btn-run-code').scroll_into_view_if_needed()
            page.wait_for_timeout(500)
            assert page.evaluate('document.documentElement.scrollWidth <= innerWidth'), 'Mobile horizontal overflow'
            page.screenshot(path='/tmp/codebattle-run-mobile.png', full_page=True)
            assert not errors, errors
            browser.close()
            print('PASS: visible stable editor; Run stdout, wrong/accepted Submit, syntax error, timeout, draft reload, mobile layout')
    finally:
        server.terminate()
        server.wait(timeout=10)
