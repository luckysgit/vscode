"""Every-visit entry dialog, restored sessions, guest switching, and mobile focus."""
import os
from pathlib import Path
import subprocess
import tempfile
import time
from urllib.request import urlopen
from playwright.sync_api import sync_playwright, expect
ROOT=Path(__file__).resolve().parents[1]
BASE='http://localhost:5105'
with tempfile.TemporaryDirectory() as directory:
    server=subprocess.Popen(['python3','server/server.py'],cwd=ROOT,env=dict(os.environ,CODEBATTLE_MODE='test',PORT='5105',CODEBATTLE_DB=str(Path(directory)/'db')),stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    try:
        for _ in range(100):
            try:
                with urlopen(BASE+'/api/health',timeout=1):break
            except OSError:time.sleep(.1)
        with sync_playwright() as p:
            browser=p.chromium.launch(executable_path='/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',headless=True)
            page=browser.new_page(viewport={'width':390,'height':844})
            page.route('https://**/*',lambda route:route.abort())
            errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
            page.goto(BASE)
            popup=page.locator('#modal-entry-options')
            expect(popup).to_be_visible()
            expect(popup.get_by_role('button',name='Create account',exact=True)).to_be_visible()
            expect(popup.get_by_role('button',name='Sign in',exact=True)).to_be_visible()
            expect(popup.get_by_role('button',name='Continue as guest',exact=False)).to_be_visible()
            page.locator('#btn-continue-guest').focus();page.keyboard.press('Tab')
            expect(popup.get_by_role('button',name='Create account',exact=True)).to_be_focused()
            page.screenshot(path='/tmp/codebattle-entry-popup.png',full_page=True)
            popup.get_by_role('button',name='Create account',exact=True).click()
            expect(popup).to_be_hidden()
            page.locator('#signup-username').fill('EntryCustomer')
            page.locator('#signup-email').fill('entry@example.com')
            page.locator('#signup-password').fill('entry secure password')
            page.locator('#form-sign-up button[type=submit]').click()
            expect(page.locator('#auth-welcome')).to_be_hidden()
            page.reload()
            expect(popup).to_be_visible()
            expect(page.locator('#btn-continue-account')).to_have_text('Continue as EntryCustomer')
            page.locator('#btn-continue-account').click()
            expect(popup).to_be_hidden()
            expect(page.locator('#global-user-handle')).to_have_text('EntryCustomer')
            page.reload()
            expect(popup).to_be_visible()
            page.locator('#btn-continue-guest').click()
            expect(popup).to_be_hidden()
            expect(page.locator('#global-user-handle')).to_contain_text('Guest_')
            guest=page.locator('#global-user-handle').inner_text()
            page.reload()
            expect(popup).to_be_visible()
            page.locator('#btn-continue-guest').click()
            expect(page.locator('#global-user-handle')).to_have_text(guest)
            page.reload()
            expect(popup).to_be_visible()
            popup.get_by_role('button',name='Sign in',exact=True).click()
            page.locator('#signin-email').fill('entry@example.com')
            page.locator('#signin-password').fill('entry secure password')
            page.locator('#form-sign-in button[type=submit]').click()
            expect(page.locator('#global-user-handle')).to_have_text('EntryCustomer')
            assert not errors,errors
            browser.close()
            print('PASS: popup on every opening/reload; all entry choices; restored account; explicit guest switch; guest identity retained; mobile keyboard focus')
    finally:
        server.terminate();server.wait(timeout=10)
