"""Persistent account and session storage for the local CodeBattle app."""
from contextlib import contextmanager
import hashlib
import hmac
import re
import secrets
import sqlite3
import time
from pathlib import Path


class AuthError(Exception):
    def __init__(self, message, status=400):
        super().__init__(message)
        self.status = status


class AuthStore:
    SESSION_SECONDS = 7 * 86400

    def __init__(self, path):
        self.path = str(path)
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        with self.connect() as db:
            db.executescript('''
                CREATE TABLE IF NOT EXISTS accounts (
                    id TEXT PRIMARY KEY, username TEXT NOT NULL COLLATE NOCASE UNIQUE,
                    email TEXT COLLATE NOCASE UNIQUE, password_hash TEXT,
                    guest INTEGER NOT NULL, created_at REAL NOT NULL
                );
                CREATE TABLE IF NOT EXISTS sessions (
                    token_hash TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL REFERENCES accounts(id), expires_at REAL NOT NULL
                );
                CREATE INDEX IF NOT EXISTS sessions_user ON sessions(user_id);
                CREATE TABLE IF NOT EXISTS auth_limits (
                    key TEXT PRIMARY KEY, count INTEGER NOT NULL, resets_at REAL NOT NULL
                );
            ''')

    @contextmanager
    def connect(self):
        db = sqlite3.connect(self.path, timeout=10)
        db.row_factory = sqlite3.Row
        db.execute('PRAGMA foreign_keys = ON')
        try:
            with db:
                yield db
        finally:
            db.close()

    @staticmethod
    def digest(token):
        return hashlib.sha256(token.encode()).hexdigest()

    @staticmethod
    def hash_password(password, salt=None):
        salt = salt or secrets.token_hex(16)
        derived = hashlib.scrypt(password.encode(), salt=bytes.fromhex(salt), n=16384, r=8, p=1)
        return salt + ':' + derived.hex()

    @staticmethod
    def public(row):
        return dict(id=row['id'], username=row['username'], email=row['email'] or '',
                    isGuest=bool(row['guest']), xp=0, rank='Bronze', rankTier='Bronze',
                    streak=0, tier='guest' if row['guest'] else 'free',
                    mutualCode='CB-' + row['id'][:12].upper())

    def me(self, token):
        if not token:
            return None
        with self.connect() as db:
            row = db.execute('''SELECT a.* FROM accounts a JOIN sessions s ON a.id=s.user_id
                WHERE s.token_hash=? AND s.expires_at>?''', (self.digest(token), time.time())).fetchone()
        return self.public(row) if row else None

    def _session(self, db, user_id, previous):
        token = secrets.token_urlsafe(32)
        db.execute('DELETE FROM sessions WHERE token_hash=? OR expires_at<=?',
                   (self.digest(previous or ''), time.time()))
        db.execute('INSERT INTO sessions VALUES (?, ?, ?)',
                   (self.digest(token), user_id, time.time() + self.SESSION_SECONDS))
        return token

    def guest(self, previous):
        current = self.me(previous)
        if current:
            return current, previous
        with self.connect() as db:
            user_id = secrets.token_hex(16)
            db.execute('INSERT INTO accounts VALUES (?, ?, NULL, NULL, 1, ?)',
                       (user_id, 'Guest_' + user_id[:10], time.time()))
            token = self._session(db, user_id, previous)
        return self.me(token), token

    def register(self, body, previous):
        username, email, password = (body.get(k, '') for k in ('username', 'email', 'password'))
        if not all(isinstance(v, str) for v in (username, email, password)):
            raise AuthError('Enter a valid username, email and password.')
        username, email = username.strip(), email.strip().lower()
        if not re.fullmatch(r'[A-Za-z0-9_]{3,24}', username):
            raise AuthError('Username must contain 3–24 letters, numbers or underscores.')
        if len(email) > 254 or not re.fullmatch(r'[^\s@]+@[^\s@]+\.[^\s@]+', email):
            raise AuthError('Enter a valid email address.')
        if not 12 <= len(password) <= 128:
            raise AuthError('Password must contain 12–128 characters.')
        password_hash = self.hash_password(password)
        current = self.me(previous)
        if current and not current['isGuest']:
            raise AuthError('Sign out before creating another account.', 409)
        user_id = current['id'] if current else secrets.token_hex(16)
        try:
            with self.connect() as db:
                if current:
                    changed = db.execute('''UPDATE accounts SET username=?, email=?, password_hash=?, guest=0
                        WHERE id=? AND guest=1''', (username, email, password_hash, user_id)).rowcount
                    if not changed:
                        raise AuthError('This guest account has already been upgraded.', 409)
                    db.execute('DELETE FROM sessions WHERE user_id=?', (user_id,))
                else:
                    db.execute('INSERT INTO accounts VALUES (?, ?, ?, ?, 0, ?)',
                               (user_id, username, email, password_hash, time.time()))
                token = self._session(db, user_id, previous)
        except sqlite3.IntegrityError:
            raise AuthError('That email or username is already registered.', 409)
        return self.me(token), token

    def login(self, body, previous):
        email, password = body.get('email', ''), body.get('password', '')
        if not isinstance(email, str) or not isinstance(password, str) or len(email) > 254 or len(password) > 128:
            raise AuthError('Invalid email or password.', 401)
        with self.connect() as db:
            row = db.execute('SELECT * FROM accounts WHERE email=? AND guest=0', (email.strip().lower(),)).fetchone()
            stored = row['password_hash'] if row else '0' * 32 + ':' + '0' * 128
            candidate = self.hash_password(password, stored.split(':')[0])
            if not hmac.compare_digest(stored, candidate):
                raise AuthError('Invalid email or password.', 401)
            token = self._session(db, row['id'], previous)
        return self.me(token), token

    def logout(self, token):
        with self.connect() as db:
            db.execute('DELETE FROM sessions WHERE token_hash=?', (self.digest(token or ''),))

    def rate_limit(self, ip):
        # Hash the address; persist throttling across process restarts.
        key, now = self.digest(ip), time.time()
        with self.connect() as db:
            db.execute('BEGIN IMMEDIATE')
            db.execute('DELETE FROM auth_limits WHERE resets_at<=?', (now,))
            row = db.execute('SELECT count FROM auth_limits WHERE key=?', (key,)).fetchone()
            if row and row['count'] >= 30:
                raise AuthError('Too many attempts. Try again in 15 minutes.', 429)
            db.execute('''INSERT INTO auth_limits VALUES (?, 1, ?)
                ON CONFLICT(key) DO UPDATE SET count=count+1''', (key, now + 900))
