"""Optional real-CDN smoke check under the enforced content security policy. Requires network access."""
import os, subprocess, tempfile, time
from pathlib import Path
from urllib.request import urlopen
from playwright.sync_api import sync_playwright, expect
root=Path(__file__).resolve().parents[1]
with tempfile.TemporaryDirectory() as directory:
    server=subprocess.Popen(['python3','-u','server/server.py'],cwd=root,env=dict(os.environ,CODEBATTLE_MODE='test',PORT='5102',CODEBATTLE_DB=str(Path(directory)/'accounts.sqlite3')),stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    try:
        for _ in range(100):
            try:
                with urlopen('http://localhost:5102/api/health',timeout=1):break
            except OSError:time.sleep(.1)
        with sync_playwright() as p:
            browser=p.chromium.launch(executable_path=os.environ.get('CODEBATTLE_TEST_CHROME', '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'),headless=True)
            page=browser.new_page()
            messages=[]
            page.on('console',lambda m: messages.append(m.text) if m.type=='error' else None)
            page.on('pageerror',lambda e: messages.append(str(e)))
            page.goto('http://localhost:5102/',wait_until='domcontentloaded')
            try:
                for _ in range(150):
                    if page.evaluate("typeof state !== 'undefined' && !!state.monacoEditor && typeof QRCode !== 'undefined'"): break
                    page.wait_for_timeout(200)
                assert page.evaluate("typeof state !== 'undefined' && !!state.monacoEditor && typeof QRCode !== 'undefined'"), 'Assets failed to initialize' 
                page.locator('#btn-continue-guest').click()
                expect(page.locator('#auth-welcome')).to_be_hidden()
                page.evaluate("() => { const node = document.createElement('div'); node.id='asset-qr-test'; document.body.append(node); new QRCode(node, {text:'asset smoke test',width:90,height:90}); }")
                expect(page.locator('#asset-qr-test canvas')).to_have_count(1)
                print('PASS: Monaco and QR loaded with real CDN and enforced CSP')
            finally:
                print('Browser errors:', messages)
                browser.close()
    finally:
        server.terminate(); server.wait(timeout=10)
