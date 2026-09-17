import concurrent.futures
import sys
import tempfile
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'server'))
from auth import AuthError, AuthStore


class AuthTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.store = AuthStore(Path(self.temp.name) / 'accounts.sqlite3')
        self.body = dict(username='TestCoder', email='test@example.com', password='long secret password')

    def test_registration_persistence_and_hashing(self):
        user, token = self.store.register(self.body, '')
        self.assertFalse(user['isGuest'])
        self.assertNotIn('password_hash', user)
        self.assertEqual(AuthStore(self.store.path).me(token), user)
        with self.store.connect() as db:
            row = db.execute('SELECT password_hash FROM accounts').fetchone()
            self.assertNotIn(self.body['password'], row['password_hash'])
            session = db.execute('SELECT token_hash FROM sessions').fetchone()
            self.assertNotEqual(token, session['token_hash'])
        again, _ = self.store.login({**self.body, 'email': 'TEST@EXAMPLE.COM'}, '')
        self.assertEqual(user['id'], again['id'])

    def test_wrong_password_unknown_email(self):
        self.store.register(self.body, '')
        for body in [{**self.body, 'password': 'wrong'}, {**self.body, 'email': 'missing@example.com'}]:
            with self.assertRaises(AuthError) as error:
                self.store.login(body, '')
            self.assertEqual(error.exception.status, 401)
            self.assertEqual(str(error.exception), 'Invalid email or password.')

    def test_guest_upgrade_rotates_session_and_preserves_identity(self):
        guest, old = self.store.guest('')
        self.assertTrue(guest['isGuest'])
        same, same_token = self.store.guest(old)
        self.assertEqual((guest, old), (same, same_token))
        user, new = self.store.register(self.body, old)
        self.assertEqual(guest['id'], user['id'])
        self.assertNotEqual(old, new)
        self.assertIsNone(self.store.me(old))
        self.assertFalse(user['isGuest'])

    def test_logout_expiry_and_forged_token(self):
        _, token = self.store.register(self.body, '')
        self.assertIsNone(self.store.me('fake'))
        self.store.logout(token)
        self.assertIsNone(self.store.me(token))
        _, token = self.store.login(self.body, '')
        with self.store.connect() as db:
            db.execute('UPDATE sessions SET expires_at=0')
        self.assertIsNone(self.store.me(token))

    def test_duplicate_and_validation(self):
        self.store.register(self.body, '')
        with self.assertRaises(AuthError) as error:
            self.store.register({**self.body, 'email': 'TEST@example.com'}, '')
        self.assertEqual(error.exception.status, 409)
        for body in [dict(self.body, password='short'), dict(self.body, username='<script>'),
                     dict(self.body, email='bad'), dict(self.body, password=3)]:
            with self.assertRaises(AuthError):
                self.store.register(body, '')

    def test_sessions_do_not_cross_accounts(self):
        first, one = self.store.register(self.body, '')
        second, two = self.store.register(dict(self.body, username='Second', email='second@example.com'), '')
        self.store.logout(one)
        self.assertEqual(second, self.store.me(two))
        self.assertNotEqual(first['id'], second['id'])

    def test_concurrent_duplicate_registration(self):
        def register(_):
            try:
                return self.store.register(self.body, '')[0]['id']
            except AuthError:
                return None
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
            results = list(pool.map(register, range(2)))
        self.assertEqual(sum(value is not None for value in results), 1)

    def test_rate_limit_persists(self):
        for _ in range(30):
            self.store.rate_limit('127.0.0.1')
        with self.assertRaises(AuthError) as error:
            AuthStore(self.store.path).rate_limit('127.0.0.1')
        self.assertEqual(error.exception.status, 429)


if __name__ == '__main__':
    unittest.main()
