"""Real authoring workflow and hidden-test boundaries using temporary accounts/data."""
import json
import os
from pathlib import Path
import subprocess
import tempfile
import time
from urllib.request import urlopen
from playwright.sync_api import sync_playwright, expect

ROOT=Path(__file__).resolve().parents[1]
BASE='http://localhost:5104'
with tempfile.TemporaryDirectory() as directory:
    server=subprocess.Popen(['python3','-u','server/server.py'],cwd=ROOT,env=dict(os.environ,CODEBATTLE_MODE='test',PORT='5104',CODEBATTLE_DB=str(Path(directory)/'db.sqlite3')),stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    try:
        for _ in range(100):
            try:
                with urlopen(BASE+'/api/health',timeout=1):break
            except OSError:time.sleep(.1)
        with sync_playwright() as p:
            browser=p.chromium.launch(executable_path='/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',headless=True)
            context=browser.new_context(viewport={'width':1440,'height':1000})
            page=context.new_page();errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
            page.route('https://**/*',lambda route:route.abort())
            page.goto(BASE+'/problems/my')
            page.locator('#modal-entry-options [data-open-auth="modal-sign-up"]').click()
            page.locator('#signup-username').fill('ProblemAuthor')
            page.locator('#signup-email').fill('problem-author@example.com')
            page.locator('#signup-password').fill('secure author password')
            page.locator('#form-sign-up button[type=submit]').click()
            root=page.locator('#view-my-problems')
            expect(root).to_be_visible()
            expect(root.get_by_role('heading',name='My Problems',exact=True)).to_be_visible()
            root.get_by_role('button',name='+ Create Problem',exact=True).click()
            page.locator('#pb-title').fill('Sum of Two Numbers')
            page.locator('#pb-description').fill('Given A and B, print their sum. <img src=x onerror="window.__xss=1">')
            root.get_by_label('Tags',exact=True).fill('Math, array')
            root.get_by_label('Visibility',exact=True).select_option('Public')
            root.get_by_role('button',name='Next step',exact=True).click()
            page.locator('#pb-inputFormat').fill('Two space-separated integers A B.')
            page.locator('#pb-outputFormat').fill('Print A+B.')
            page.locator('#pb-constraints').fill('-100 <= A, B <= 100')
            root.get_by_role('button',name='Next step',exact=True).click()
            root.get_by_role('button',name='+ Add Test Case',exact=True).click()
            page.locator('#pb-case-0-input').fill('2 3')
            page.locator('#pb-case-0-expectedOutput').fill('5')
            root.get_by_role('button',name='+ Add Test Case',exact=True).click()
            page.locator('#pb-case-1-input').fill('HIDDEN-INPUT-925')
            page.locator('#pb-case-1-expectedOutput').fill('HIDDEN-ANSWER-739')
            # Duplicate, reorder, and delete actual test records.
            root.locator('.pb-test').last.get_by_role('button',name='Duplicate',exact=True).click()
            expect(root.locator('.pb-test')).to_have_count(3)
            root.locator('.pb-test').last.get_by_role('button',name='Move Up',exact=True).click()
            root.locator('.pb-test').nth(1).get_by_role('button',name='Delete',exact=True).click()
            expect(root.locator('.pb-test')).to_have_count(2)
            root.get_by_role('button',name='Preview',exact=True).click()
            expect(root.locator('.pb-preview')).to_contain_text('2 3')
            expect(root.locator('.pb-preview')).not_to_contain_text('HIDDEN')
            assert root.locator('img,script,[onerror]').count()==0
            assert page.evaluate('window.__xss === undefined')
            root.get_by_role('button',name='Save Draft',exact=True).click()
            expect(page.locator('#pb-save-status')).to_have_text('Draft saved to your Problem Bank.')
            problem_id=page.url.split('/')[-2]
            root.get_by_role('button',name='Publish',exact=True).click()
            expect(page.locator('#pb-save-status')).to_have_text('Published version 1.')
            original=context.request.get(BASE+f'/api/problems/{problem_id}/manage').json()['problem']
            first_id=original['problemVersionId']
            root.get_by_role('button',name='Back to My Problems',exact=True).click()
            root.get_by_role('textbox',name='Search my problems',exact=True).fill('Sum of Two')
            root.get_by_role('button',name='Search',exact=True).click()
            expect(root.locator('article')).to_have_count(1)
            root.get_by_role('button',name='Open',exact=True).click()
            expect(root.get_by_role('heading',name='Student preview',exact=True)).to_be_visible()
            root.get_by_role('button',name='Edit problem',exact=True).click()
            page.locator('#pb-title').fill('Sum of Two Numbers v2')
            root.get_by_role('button',name='Publish',exact=True).click()
            expect(page.locator('#pb-save-status')).to_have_text('Published version 2.')
            versions=context.request.get(BASE+f'/api/problems/{problem_id}/versions').json()['versions']
            assert len(versions)==2
            old=context.request.get(BASE+f'/api/problems/{problem_id}/manage?versionId={first_id}').json()['problem']
            assert old['title']=='Sum of Two Numbers' and old['testCases']==original['testCases']
            root.get_by_role('button',name='Back to My Problems',exact=True).click()
            root.get_by_role('button',name='Open',exact=True).click()
            root.get_by_role('button',name='Version history',exact=True).click()
            root.get_by_role('button',name='View version',exact=True).last.click()
            expect(root.get_by_role('heading',name='Version 1 (read only)',exact=True)).to_be_visible()
            root.get_by_role('button',name='Back to problem',exact=True).click()
            root.get_by_role('button',name='Back to My Problems',exact=True).click()
            root.get_by_role('button',name='Select a problem',exact=True).click()
            root.get_by_role('button',name='Select',exact=True).click()
            expect(root.locator('.pb-selected')).to_have_text('Selected: Sum of Two Numbers v2 · Version 2')
            selected=page.evaluate('problemBankUI.selector.value')
            assert selected['problemId']==problem_id and selected['problemVersionId']!=first_id
            root.get_by_label('Problem source',exact=True).select_option('public')
            expect(root.locator('.pb-row')).to_have_count(1)
            root.get_by_role('button',name='Back to My Problems',exact=True).click()
            root.get_by_role('button',name='Duplicate',exact=True).click()
            expect(page.locator('#pb-title')).to_have_value('Sum of Two Numbers v2 - Copy')
            copy_id=page.url.split('/')[-2]
            assert copy_id!=problem_id
            # Failed saves retain all entered values and never claim success.
            page.locator('#pb-title').fill('Keep this unsaved draft')
            page.route('**/api/problems/'+copy_id,lambda route:route.fulfill(status=503,content_type='application/json',body=json.dumps({'error':'Database temporarily unavailable'})))
            root.get_by_role('button',name='Save Draft',exact=True).click()
            expect(page.locator('#pb-save-status')).to_have_text('Database temporarily unavailable')
            expect(page.locator('#pb-title')).to_have_value('Keep this unsaved draft')
            page.unroute('**/api/problems/'+copy_id)
            page.once('dialog',lambda dialog:dialog.dismiss())
            root.get_by_role('button',name='Back to My Problems',exact=True).click()
            expect(page.locator('#pb-title')).to_have_value('Keep this unsaved draft')
            root.get_by_role('button',name='Save Draft',exact=True).click()
            expect(page.locator('#pb-save-status')).to_have_text('Draft saved to your Problem Bank.')
            page.reload()
            expect(page.locator('#modal-entry-options')).to_be_visible()
            page.keyboard.press('Escape')
            expect(page.locator('#pb-title')).to_have_value('Keep this unsaved draft')
            root.get_by_role('button',name='Back to My Problems',exact=True).click()
            root.get_by_role('textbox',name='Search my problems',exact=True).fill('Sum of Two')
            root.get_by_role('button',name='Search',exact=True).click()
            expect(root.locator('article')).to_have_count(1)
            page.once('dialog',lambda dialog:dialog.accept())
            root.get_by_role('button',name='Archive',exact=True).click()
            expect(root).to_contain_text('Problem archived.')
            root.get_by_label('Status filter',exact=True).select_option('ARCHIVED')
            root.get_by_role('button',name='Search',exact=True).click()
            expect(root.locator('article')).to_have_count(1)
            # Another account cannot manage, edit, archive, or read hidden tests.
            other=browser.new_context()
            signup=other.request.post(BASE+'/api/auth/register',data=dict(username='OtherAuthor',email='other-author@example.com',password='secure other password'))
            assert signup.status==201
            for suffix in ['/manage','/versions']:
                assert other.request.get(BASE+f'/api/problems/{problem_id}'+suffix).status==403
            assert other.request.patch(BASE+f'/api/problems/{problem_id}',data={'revision':5,'title':'stolen'}).status==403
            assert other.request.post(BASE+f'/api/problems/{problem_id}/archive',data={'revision':5}).status==403
            # Public data from the published version was sample-only (archive now denies access).
            assert other.request.get(BASE+f'/api/problems/{copy_id}').status==403
            public=other.request.get(BASE+'/api/problems').text()
            assert 'HIDDEN-' not in public
            assert page.evaluate("Object.values(localStorage).every(value => !value.includes('HIDDEN-ANSWER-739'))")
            page.set_viewport_size({'width':390,'height':844})
            page.screenshot(path='/tmp/codebattle-problem-bank-mobile.png',full_page=True)
            assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
            assert not errors,errors
            browser.close()
            print('PASS: create, samples/hidden, preview XSS, draft, publish v1/v2, history, pinned selector, duplicate, failed save, discard protection, reload, archive, cross-user authorization, mobile')
    finally:
        server.terminate();server.wait(timeout=10)
