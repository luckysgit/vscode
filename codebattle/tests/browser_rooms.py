"""Two isolated device sessions share real persisted rooms and membership."""
import json
import os
from pathlib import Path
import subprocess
import tempfile
import time
from urllib.request import urlopen
from playwright.sync_api import sync_playwright, expect
from test_problems import payload
ROOT=Path(__file__).resolve().parents[1];BASE='http://localhost:5106'
with tempfile.TemporaryDirectory() as directory:
    server=subprocess.Popen(['python3','server/server.py'],cwd=ROOT,env=dict(os.environ,CODEBATTLE_MODE='test',PORT='5106',CODEBATTLE_DB=str(Path(directory)/'db')),stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    try:
        for _ in range(100):
            try:
                with urlopen(BASE+'/api/health',timeout=1):break
            except OSError:time.sleep(.1)
        with sync_playwright() as p:
            browser=p.chromium.launch(executable_path='/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',headless=True)
            host=browser.new_context();other=browser.new_context();pages=[];errors=[]
            for index,context in enumerate([host,other]):
                assert context.request.post(BASE+'/api/auth/register',data={'username':f'RealUser{index}','email':f'real{index}@example.com','password':'real account password'}).status==201
                page=context.new_page();page.route('https://**/*',lambda route:route.abort());page.on('pageerror',lambda error:errors.append(str(error)))
                page.add_init_script("localStorage.setItem('cb_rooms_history', JSON.stringify([{title:'FAKE LEGACY ROOM',host:'DevNinja'}]));")
                page.goto(BASE);page.locator('#btn-continue-account').click();page.locator('#main-nav-links [data-target="view-rooms"]').click();pages.append(page)
            a,b=pages
            expect(a.locator('#rooms-status')).to_contain_text('No rooms found')
            expect(b.locator('#rooms-grid-container')).not_to_contain_text('DevNinja')
            # Create a real published problem owned by A; author-only test data must not reach B.
            response=host.request.post(BASE+'/api/problems',data=payload())
            assert response.status==201,response.text()
            problem=response.json()['problem']
            assert host.request.post(BASE+f"/api/problems/{problem['id']}/publish",data={'revision':problem['revision']}).status==200
            a.locator('#btn-create-room-modal').click()
            a.locator('#input-room-title').fill('My Real Shared Room')
            a.locator('#room-problem-selector').get_by_role('button',name='Select',exact=True).click()
            a.locator('#btn-save-room').click()
            expect(a.locator('#lobby-room-title')).to_have_text('My Real Shared Room')
            code=a.locator('#lobby-room-code').inner_text()
            expect(a.locator('#lobby-members')).to_contain_text('RealUser0 (Host)')
            b.locator('#room-search').fill(code)
            b.locator('#room-search-form').get_by_role('button',name='Search',exact=True).click()
            expect(b.locator('.room-card')).to_have_count(1)
            expect(b.locator('.room-title')).to_have_text('My Real Shared Room')
            b.locator('.btn-join-action').click()
            expect(b.locator('#lobby-room-title')).to_have_text('My Real Shared Room')
            expect(b.locator('#lobby-members')).to_contain_text('RealUser1')
            expect(a.locator('#lobby-members')).to_contain_text('RealUser1',timeout=12000)
            expect(b.locator('#btn-close-room')).to_be_hidden()
            expect(b.locator('#lobby-problem')).not_to_contain_text('SECRET')
            details=other.request.get(BASE+'/api/rooms/'+code).json()['room']
            assert details['players']==2 and 'SECRET' not in json.dumps(details)
            assert other.request.get(BASE+f"/api/problems/{problem['id']}/manage").status==403
            assert other.request.post(BASE+'/api/rooms/'+code+'/close',data={}).status==403
            a.screenshot(path='/tmp/codebattle-real-room.png',full_page=True)
            b.locator('#btn-leave-room').click()
            expect(a.locator('#lobby-status')).to_contain_text('1/20',timeout=12000)
            # Reloaded clients still see persisted shared records, never browser-generated rooms.
            b.reload();b.locator('#btn-continue-account').click();b.locator('#main-nav-links [data-target="view-rooms"]').click()
            expect(b.locator('.room-card')).to_have_count(1)
            a.once('dialog',lambda dialog:dialog.accept());a.locator('#btn-close-room').click()
            b.locator('#btn-refresh-rooms').click()
            expect(b.locator('#rooms-status')).to_contain_text('No rooms found')
            b.set_viewport_size({'width':390,'height':844})
            assert b.evaluate('document.documentElement.scrollWidth <= innerWidth')
            assert not errors,errors
            browser.close()
            print('PASS: two isolated accounts, empty bank, real create/search/join, host membership updates, private tests withheld, leave, reload persistence, host-only close, old fake cache ignored')
    finally:
        server.terminate();server.wait(timeout=10)
