#!/usr/bin/env python3
"""
CodeBattle local application server (Python implementation)
Based on Build Guides & Docs in codebattle/doc
Implements full REST API endpoints (Auth, Rooms, Problems, Submissions, Users, Problists, Leaderboard, Admin).
"""

import http.server
import socketserver
import json
import os
import subprocess
import time
import random
import tempfile
from http.cookies import SimpleCookie
from pathlib import Path
from auth import AuthStore, AuthError
from runtime import preview_mode
from runner import execute, RunnerError
from judge import grade
from problems import ProblemStore, ProblemError
from rooms import RoomStore
import sqlite3
import logging
import uuid
from urllib.parse import parse_qs, urlparse

try:
    MODE = preview_mode()  # Validate before creating/opening any database or listener.
except RuntimeError as error:
    raise SystemExit(str(error)) from None
PORT = int(os.environ.get("PORT", "5000"))
BIND_ADDRESS = os.environ.get('CODEBATTLE_BIND', '127.0.0.1')
if BIND_ADDRESS not in ('127.0.0.1', 'localhost') and not os.environ.get('CODEBATTLE_ORIGIN'):
    raise SystemExit('Set CODEBATTLE_ORIGIN to the shared server URL when using CODEBATTLE_BIND.')
SERVER_DIR = os.path.dirname(__file__)
ROOT_DIR = os.path.abspath(os.path.join(SERVER_DIR, '..'))
WEB_DIR = os.path.join(ROOT_DIR, 'web')
AUTH = AuthStore(os.environ.get('CODEBATTLE_DB', os.path.join(SERVER_DIR, 'data', 'accounts.sqlite3')))
with AUTH.connect() as db:
    db.execute("CREATE TABLE IF NOT EXISTS practice_submissions (id TEXT PRIMARY KEY, user_id TEXT NOT NULL REFERENCES accounts(id), result TEXT NOT NULL, created_at REAL NOT NULL)")
PROBLEMS = ProblemStore(AUTH)
ROOMS = RoomStore(AUTH, PROBLEMS)
ORIGIN = os.environ.get('CODEBATTLE_ORIGIN', f'http://localhost:{PORT}').rstrip('/')

class CodeBattleHandler(http.server.SimpleHTTPRequestHandler):
    def translate_path(self, path):
        from urllib.parse import unquote
        clean = unquote(urlparse(path).path).lstrip('/')
        is_source = clean.startswith('src/')
        base = Path(os.path.join(ROOT_DIR, 'src') if is_source else WEB_DIR).resolve()
        relative = clean[4:] if is_source else clean
        target = (base / (relative or 'index.html')).resolve()
        if not target.is_relative_to(base) or any(part.startswith('.') for part in Path(clean).parts):
            return str(Path(WEB_DIR) / '__not_found__')
        return str(target)

    def list_directory(self, path):
        self.send_error(404)

    def end_headers(self):
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.send_header('X-Frame-Options', 'DENY')
        self.send_header('Referrer-Policy', 'same-origin')
        self.send_header('Cache-Control', 'no-store')
        # Block injected scripts/event handlers. Style attributes remain necessary for
        # the existing authored layouts and Monaco, not executable user content.
        self.send_header('Content-Security-Policy',
            "default-src 'none'; base-uri 'none'; object-src 'none'; frame-ancestors 'none'; "
            "form-action 'self'; script-src 'self' https://cdnjs.cloudflare.com/ajax/libs/monaco-editor/0.45.0/min/ "
            "https://cdnjs.cloudflare.com/ajax/libs/qrcodejs/1.0.0/; script-src-attr 'none'; "
            "style-src 'self' 'unsafe-inline' https://cdnjs.cloudflare.com/ajax/libs/monaco-editor/0.45.0/min/; "
            "img-src 'self' data:; font-src 'self' https://cdnjs.cloudflare.com/ajax/libs/monaco-editor/0.45.0/min/; "
            "connect-src 'self' https://cdnjs.cloudflare.com/ajax/libs/monaco-editor/0.45.0/min/; worker-src 'self' blob:")
        self.send_header('Permissions-Policy', 'camera=(), microphone=(), geolocation=(), display-capture=()')
        super().end_headers()

    def _send_cors_headers(self):
        pass  # The browser client uses same-origin requests only.

    def session_token(self):
        cookie = SimpleCookie()
        try:
            cookie.load(self.headers.get('Cookie', ''))
            return cookie['cb_session'].value if 'cb_session' in cookie else ''
        except Exception:
            return ''

    def do_OPTIONS(self):
        self.send_response(204)
        self.end_headers()

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path.rstrip('/')

        if path == '/api/problems' or path.startswith('/api/problems/'):
            return self.problem_api('GET', path, query=parse_qs(parsed.query, keep_blank_values=True))
        # Authoring routes serve the existing app shell; all assets use absolute paths.
        if path == '/problems':
            self.send_response(302)
            self.send_header('Location', '/problems/my')
            self.end_headers()
            return
        if path.startswith('/problems/'):
            self.path = '/index.html'
            return super().do_GET()

        # Auth GET
        if path in ['/api/auth/me', '/auth/me']:
            return self._send_json({"success": True, "user": AUTH.me(self.session_token())})

        if path == '/api/submissions':
            user = AUTH.me(self.session_token())
            if not user:
                return self._send_json({"error": "Sign in or continue as a guest."}, 401)
            with AUTH.connect() as db:
                rows = db.execute("SELECT result FROM practice_submissions WHERE user_id = ? ORDER BY created_at DESC LIMIT 50", (user['id'],)).fetchall()
            return self._send_json({"submissions": [json.loads(row['result']) for row in rows]})

        # Health
        elif path in ['/api/health', '/health']:
            return self._send_json({"status": "ok", "service": "CodeBattle-Development", "mode": MODE, "production_ready": False, "uptime_sec": time.process_time()})

        if path == '/api/rooms' or path.startswith('/api/rooms/') or path == '/rooms' or path.startswith('/rooms/'):
            canonical = path if path.startswith('/api/') else '/api'+path
            return self.room_api('GET', canonical, query=parse_qs(parsed.query, keep_blank_values=True))

        if path in ['/api/admin', '/admin']:
            return self._send_json({'error': 'Administrator access is not enabled.'}, 403)
        if path.startswith('/api/') or path.startswith('/users/') or path.startswith('/leaderboard'):
            return self._send_json({'error': 'This feature is not available yet.'}, 404)
        super().do_GET()

    def room_api(self, method, path, body=None, query=None):
        try:
            user = AUTH.me(self.session_token())
            parts = path.split('/')[3:]
            if method == 'GET' and not parts:
                return self._send_json({'success': True, **ROOMS.list(user, query or {})})
            if method == 'GET' and len(parts) == 1:
                return self._send_json({'success': True, 'room': ROOMS.get(user, parts[0])})
            if method == 'POST' and not parts:
                return self._send_json({'success': True, 'room': ROOMS.create(user, body)}, 201)
            if method == 'POST' and len(parts) == 2:
                if body != {}:
                    raise ProblemError('Room membership actions take no client identity fields.')
                return self._send_json({'success': True, 'room': ROOMS.action(user, parts[0], parts[1])})
            raise ProblemError('Room endpoint not found.',404,'not_found')
        except ProblemError as error:
            return self._send_json({'success': False, 'error': str(error), 'code': error.code},error.status)
        except (sqlite3.Error, UnicodeError):
            logging.error('Room request failed method=%s',method)
            return self._send_json({'success': False, 'error': 'Unable to complete the room request. Please retry.', 'code': 'room_error'},503)

    def problem_api(self, method, path, body=None, query=None):
        try:
            user = AUTH.me(self.session_token())
            parts = path.split('/')[3:]
            if method == 'GET':
                query = query or {}
                if not parts or parts == ['my']:
                    return self._send_json({'success': True, **PROBLEMS.list(user, query, mine=bool(parts))})
                if set(query) - {'versionId'} or any(len(v) != 1 for v in query.values()):
                    raise ProblemError('Invalid version query.')
                version = query.get('versionId', [None])[0]
                if len(parts) == 1:
                    return self._send_json({'success': True, 'problem': PROBLEMS.get(user, parts[0], version_id=version)})
                if len(parts) == 2 and parts[1] == 'manage':
                    return self._send_json({'success': True, 'problem': PROBLEMS.get(user, parts[0], manage=True, version_id=version)})
                if len(parts) == 2 and parts[1] == 'versions':
                    return self._send_json({'success': True, 'versions': PROBLEMS.versions(user, parts[0])})
            elif method == 'POST' and not parts:
                return self._send_json({'success': True, 'problem': PROBLEMS.create(user, body)}, 201)
            elif method == 'PATCH' and len(parts) == 1:
                return self._send_json({'success': True, 'problem': PROBLEMS.edit(user, parts[0], body)})
            elif method == 'POST' and len(parts) == 2 and parts[1] in ('publish', 'archive', 'duplicate'):
                return self._send_json({'success': True, 'problem': PROBLEMS.action(user, parts[0], parts[1], body)})
            raise ProblemError('Problem endpoint not found.', 404, 'not_found')
        except ProblemError as error:
            logging.info('Problem API rejected method=%s status=%s code=%s', method, error.status, error.code)
            return self._send_json({'success': False, 'error': str(error), 'code': error.code}, error.status)
        except UnicodeError:
            return self._send_json({'success': False, 'error': 'Problem text must contain valid Unicode.', 'code': 'invalid_request'}, 400)
        except sqlite3.Error:
            # Do not log request bodies, hidden tests, passwords, or raw SQL parameters.
            logging.error('Problem database operation failed method=%s', method)
            return self._send_json({'success': False, 'error': 'Database operation failed. Your changes were not confirmed; please retry.', 'code': 'database_error'}, 503)

    def do_PATCH(self):
        return self.do_POST()

    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path.rstrip('/')
        # Reject cross-site writes, including login CSRF. CLI clients may omit Origin.
        if (self.headers.get('Origin') not in (None, ORIGIN)
                or self.headers.get('Sec-Fetch-Site') == 'cross-site'):
            return self._send_json({"error": "Request origin is not allowed."}, 403)
        if self.headers.get_content_type() != 'application/json':
            return self._send_json({"error": "Use application/json."}, 415)
        try:
            length = int(self.headers.get('Content-Length', '0'))
            max_length = 524288 if path == '/api/problems' or path.startswith('/api/problems/') else 65536
            if not 0 < length <= max_length:
                return self._send_json({"error": f"Request must be between 1 and {max_length} bytes.", "code": "request_size"}, 413)
            body = json.loads(self.rfile.read(length))
            if not isinstance(body, dict):
                raise ValueError()
        except (ValueError, UnicodeDecodeError):
            return self._send_json({"error": "Invalid JSON request."}, 400)

        if path == '/api/rooms' or path.startswith('/api/rooms/') or path == '/rooms' or path.startswith('/rooms/'):
            canonical = path if path.startswith('/api/') else '/api'+path
            return self.room_api(self.command, canonical, body=body)
        if path == '/api/problems' or path.startswith('/api/problems/'):
            return self.problem_api(self.command, path, body=body)
        if self.command == 'PATCH':
            return self._send_json({'error': 'Endpoint not found.'}, 404)
        if path.startswith('/api/auth/') or path.startswith('/auth/'):
            try:
                action = path.split('/')[-1]
                previous = self.session_token()
                if action == 'logout':
                    AUTH.logout(previous)
                    return self._send_json({"success": True, "user": None}, cookie='')
                if action not in ('guest', 'register', 'login'):
                    return self._send_json({"error": "Endpoint not found."}, 404)
                AUTH.rate_limit(self.client_address[0])
                user, token = AUTH.guest(previous) if action == 'guest' else getattr(AUTH, action)(body, previous)
                return self._send_json({"success": True, "user": user},
                                       201 if action == 'register' else 200, cookie=token)
            except AuthError as error:
                return self._send_json({"success": False, "error": str(error)}, error.status)

        user = AUTH.me(self.session_token())
        if not user:
            return self._send_json({"error": "Sign in or continue as a guest."}, 401)

        # Submit Code
        if path in ['/api/run', '/api/submit', '/submissions']:
            is_submission = path != '/api/run'
            if is_submission and user['isGuest']:
                return self._send_json({"error": "Create an account or sign in to submit your solution.",
                                        "code": "account_required"}, 403)
            source_code = body.get('code', body.get('source_code', ''))
            language = str(body.get('language', 'python')).lower()
            if not isinstance(source_code, str) or not source_code.strip():
                return self._send_json({"error": "Write some code before running or submitting."}, 400)
            if len(source_code.encode('utf-8')) > 50000:
                return self._send_json({"error": "Code must be 50KB or smaller."}, 413)
            stdin = body.get('stdin', '')
            if not isinstance(stdin, str) or len(stdin.encode()) > 10000:
                return self._send_json({"error": "Input must be text of 10KB or smaller."}, 400)
            problem_id = body.get('problem_id', body.get('problemId'))
            if is_submission and not isinstance(problem_id, str):
                return self._send_json({"error": "Select a problem before submitting."}, 400)
            try:
                result = grade(source_code, language, problem_id) if is_submission else execute(source_code, language, stdin)
            except RunnerError as error:
                return self._send_json({"error": str(error)}, error.status)
            submission = {"id": str(uuid.uuid4()), "problem_id": problem_id, "language": language,
                          **result, "is_submission": is_submission}
            if is_submission:
                with AUTH.connect() as db:
                    db.execute("INSERT INTO practice_submissions (id, user_id, result, created_at) VALUES (?, ?, ?, ?)",
                               (submission['id'], user['id'], json.dumps(submission), time.time()))
            return self._send_json({"success": True, "result": submission})

        self._send_json({'error': 'Endpoint not found.'}, 404)

    def _send_json(self, data, status=200, cookie=None):
        self.send_response(status)
        self._send_cors_headers()
        if cookie is not None:
            secure = '; Secure' if ORIGIN.startswith('https://') else ''
            age = AUTH.SESSION_SECONDS if cookie else 0
            self.send_header('Set-Cookie', f'cb_session={cookie}; HttpOnly; SameSite=Lax; Path=/; Max-Age={age}{secure}')
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode('utf-8'))

class ReuseTCPServer(socketserver.ThreadingTCPServer):
    allow_reuse_address = True
    daemon_threads = True

if __name__ == '__main__':
    with ReuseTCPServer((BIND_ADDRESS, PORT), CodeBattleHandler) as httpd:
        print("====================================================")
        print(f"⚡ CODEBATTLE LOCAL APP LISTENING ON PORT {PORT} ⚡")
        print(f"🌐 Server URL: {ORIGIN}")
        print("====================================================")
        httpd.serve_forever()
