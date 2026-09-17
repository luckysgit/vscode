"""HTTP contract tests using an isolated database and ephemeral port."""
import http.client
import json
import os
import sys
import tempfile
import threading
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'server'))
from auth import AuthStore


class HttpTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory()
        os.environ['CODEBATTLE_MODE'] = 'test'
        os.environ['CODEBATTLE_DB'] = str(Path(cls.temp.name) / 'test.sqlite3')
        import server
        cls.module = server
        cls.httpd = server.ReuseTCPServer(('127.0.0.1', 0), server.CodeBattleHandler)
        cls.port = cls.httpd.server_address[1]
        server.ORIGIN = f'http://localhost:{cls.port}'
        cls.thread = threading.Thread(target=cls.httpd.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.httpd.shutdown()
        cls.httpd.server_close()
        cls.thread.join()
        cls.temp.cleanup()

    def request(self, path, data=None, cookie=None, origin=None, method=None):
        connection = http.client.HTTPConnection('127.0.0.1', self.port)
        headers = {'Content-Type': 'application/json'}
        if cookie:
            headers['Cookie'] = cookie
        if origin:
            headers['Origin'] = origin
        connection.request(method or ('GET' if data is None else 'POST'), path,
                           None if data is None else json.dumps(data), headers)
        response = connection.getresponse()
        result = response.status, dict(response.getheaders()), response.read()
        connection.close()
        return result

    def test_account_journey_and_cookie_revocation(self):
        status, headers, body = self.request('/api/auth/guest', {})
        self.assertEqual(status, 200)
        guest = json.loads(body)['user']
        cookie = headers['Set-Cookie'].split(';')[0]
        self.assertIn('HttpOnly', headers['Set-Cookie'])
        self.assertIn('SameSite=Lax', headers['Set-Cookie'])
        status, headers, body = self.request('/api/auth/register', dict(username='HttpCoder', email='http@example.com', password='correct long password'), cookie)
        self.assertEqual(status, 201)
        self.assertEqual(json.loads(body)['user']['id'], guest['id'])
        self.assertIsNone(json.loads(self.request('/api/auth/me', cookie=cookie)[2])['user'])
        cookie = headers['Set-Cookie'].split(';')[0]
        self.assertFalse(json.loads(self.request('/api/auth/me', cookie=cookie)[2])['user']['isGuest'])
        self.request('/api/auth/logout', {}, cookie)
        self.assertIsNone(json.loads(self.request('/api/auth/me', cookie=cookie)[2])['user'])

    def test_origin_validation_and_private_files(self):
        self.assertEqual(self.request('/api/auth/guest', {}, origin='https://evil.example')[0], 403)
        for path in ['/server/auth.py', '/server/data/accounts.sqlite3', '/schema.sql', '/src/../../server/auth.py', '/src/../server/auth.py', '/src/%2e%2e/server/data/accounts.sqlite3', '/%2e%2e/server/auth.py', '/src/']:
            self.assertEqual(self.request(path)[0], 404, path)
        self.assertEqual(self.request('/')[0], 200)
        self.assertEqual(self.request('/src/modules/auth/auth.service.js')[0], 200)

    def test_api_validation(self):
        self.assertEqual(self.request('/api/auth/register', [1])[0], 400)
        self.assertEqual(self.request('/api/rooms', {})[0], 401)
        self.assertEqual(self.request('/api/admin')[0], 403)
        _, headers, _ = self.request('/api/auth/guest', {})
        cookie = headers['Set-Cookie'].split(';')[0]
        status, _, body = self.request('/api/run', {'code': 'print(1)'}, cookie)
        self.assertEqual(status, 200)
        result = json.loads(body)['result']
        self.assertEqual(result['status'], 'completed')
        self.assertEqual(result['stdout'], '1\n')

        status, _, body = self.request('/api/run', {'code': 'raise ValueError("no")'}, cookie)
        self.assertEqual(status, 200)
        self.assertEqual(json.loads(body)['result']['status'], 'runtime_error')

        self.assertEqual(self.request('/api/run', {'code': '   '}, cookie)[0], 400)

    def test_grading_and_owner_history(self):
        from test_runner import SOLUTION
        _, headers, _ = self.request('/api/auth/guest', {})
        cookie = headers['Set-Cookie'].split(';')[0]
        for path in ['/api/submit', '/submissions']:
            status, _, body = self.request(path, {'code': SOLUTION, 'problem_id': 'p1', 'isSubmission': False}, cookie)
            self.assertEqual(status, 403)
            self.assertEqual(json.loads(body)['code'], 'account_required')
        self.assertEqual(self.request('/api/submit', {'code': SOLUTION, 'problem_id': 'p1'})[0], 401)
        _, headers, _ = self.request('/api/auth/register', dict(username='SubmitCoder', email='submit@example.com', password='correct long password'), cookie)
        cookie = headers['Set-Cookie'].split(';')[0]
        self.assertEqual(self.request('/api/submit', {'code': SOLUTION}, cookie)[0], 400)
        status, _, body = self.request('/api/submit', {'code': SOLUTION, 'problem_id': 'p1'}, cookie)
        self.assertEqual(status, 200)
        result = json.loads(body)['result']
        self.assertEqual(result['status'], 'accepted')
        history = json.loads(self.request('/api/submissions', cookie=cookie)[2])['submissions']
        self.assertEqual(history[0]['id'], result['id'])
        _, headers, _ = self.request('/api/auth/guest', {})
        other = headers['Set-Cookie'].split(';')[0]
        self.assertEqual(json.loads(self.request('/api/submissions', cookie=other)[2])['submissions'], [])
        self.assertEqual(self.request('/api/submissions')[0], 401)

    def test_problem_bank_http_security(self):
        from test_problems import payload
        _, headers, _ = self.request('/api/auth/register', dict(username='BankAuthor', email='bank@example.com', password='correct long password'))
        author = headers['Set-Cookie'].split(';')[0]
        _, headers, _ = self.request('/api/auth/register', dict(username='BankOther', email='otherbank@example.com', password='correct long password'))
        other = headers['Set-Cookie'].split(';')[0]
        self.assertEqual(self.request('/api/problems', payload())[0], 401)
        data = payload(visibility='Public')
        status, _, body = self.request('/api/problems', data, author)
        self.assertEqual(status, 201, body)
        problem = json.loads(body)['problem']
        base = '/api/problems/' + problem['id']
        self.assertEqual(self.request(base)[0], 403)
        self.assertEqual(self.request(base+'/manage', cookie=other)[0], 403)
        self.assertEqual(self.request(base, {'revision':1,'title':'stolen'}, other, method='PATCH')[0], 403)
        self.assertEqual(self.request(base+'/archive', {'revision':1}, other)[0], 403)
        self.assertEqual(self.request(base, {'revision':1,'title':'CSRF'}, author, origin='https://evil.example',method='PATCH')[0],403)
        status,_,body=self.request(base+'/publish',{'revision':1},author)
        self.assertEqual(status,200,body)
        public = self.request(base)[2]
        self.assertNotIn(b'SECRET',public)
        self.assertNotIn(b'isHidden',public)
        self.assertIn(b'visibleTestCases',public)
        self.assertNotIn(b'SECRET', self.request('/api/problems')[2])
        self.assertNotIn(b'SECRET', self.request('/api/problems/my',cookie=author)[2])
        self.assertEqual(self.request('/api/problems/my')[0],401)
        self.assertEqual(self.request('/problems/my')[0],200)
        self.assertEqual(self.request('/server/problems.py')[0],404)
        self.assertEqual(self.request('/server/migrations/001_problem_bank.sql')[0],404)
        self.assertEqual(self.request('/api/problems?difficulty=Invalid')[0],400)
        for key in ['owner_id','userId','status']:
            bad=payload();bad[key]='forged'
            self.assertEqual(self.request('/api/problems',bad,author)[0],400)
        # A database error must be an honest structured failure without SQL/body leakage.
        from unittest.mock import patch
        import sqlite3
        with patch.object(self.module.PROBLEMS, 'create', side_effect=sqlite3.OperationalError('private SQL details')):
            status,_,body=self.request('/api/problems',payload(),author)
            self.assertEqual(status,503)
            self.assertEqual(json.loads(body)['code'],'database_error')
            self.assertNotIn(b'private SQL',body)

    def test_headers_and_preview_identity(self):
        status, headers, body = self.request('/api/health')
        self.assertEqual(status, 200)
        self.assertEqual(json.loads(body)['mode'], 'test')
        self.assertFalse(json.loads(body)['production_ready'])
        csp = headers['Content-Security-Policy']
        script_policy = next(part for part in csp.split(';') if part.strip().startswith('script-src '))
        self.assertNotIn("'unsafe-inline'", script_policy)
        self.assertNotIn("'unsafe-eval'", script_policy)
        self.assertIn("script-src-attr 'none'", csp)
        self.assertIn("frame-ancestors 'none'", csp)
        self.assertIn('camera=()', headers['Permissions-Policy'])

    def test_hidden_fixture_not_public(self):
        status, _, body = self.request('/src/modules/problems/problem.service.js')
        self.assertEqual(status, 200)
        self.assertNotIn(b'isHidden: true', body)
        self.assertNotIn(b'3 3\\n6', body)
        for path in ('/server/fixtures/hidden-tests.json', '/fixtures/hidden-tests.json',
                     '/lib/problemBank.js', '/codebattle-mvp/database/seed.sql', '/codebattle-mvp.zip'):
            self.assertEqual(self.request(path)[0], 404, path)


if __name__ == '__main__':
    unittest.main()
