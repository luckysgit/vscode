"""Production guards must reject unsafe configuration before creating any state."""
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'server'))
from runtime import preview_mode

ROOT = Path(__file__).resolve().parents[1]


class RuntimeTests(unittest.TestCase):
    def test_requires_explicit_local_mode(self):
        for mode in ('', 'production', 'staging', 'unknown'):
            with self.subTest(mode=mode), self.assertRaises(RuntimeError):
                preview_mode({'CODEBATTLE_MODE': mode})
        for mode in ('development', 'demo', 'test'):
            self.assertEqual(preview_mode({'CODEBATTLE_MODE': mode}), mode)

    def test_no_node_env_production_override(self):
        for mode in ('development', 'demo', 'test'):
            for node_env in ('production', 'staging', 'Production', 'unknown'):
                with self.subTest(mode=mode, node_env=node_env), self.assertRaises(RuntimeError):
                    preview_mode({'CODEBATTLE_MODE': mode, 'NODE_ENV': node_env})

    def test_startup_fails_before_database_creation(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'must-not-exist.sqlite3'
            env = dict(os.environ, CODEBATTLE_MODE='demo', NODE_ENV='production', CODEBATTLE_DB=str(path))
            result = subprocess.run([sys.executable, 'server/server.py'], cwd=ROOT, env=env,
                                    capture_output=True, text=True, timeout=10)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('staging/production startup is disabled', result.stderr)
            self.assertFalse(path.exists())

    def test_shared_bind_requires_explicit_origin(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'not-created.sqlite3'
            env = dict(os.environ, CODEBATTLE_MODE='development', CODEBATTLE_BIND='0.0.0.0', CODEBATTLE_DB=str(path))
            env.pop('CODEBATTLE_ORIGIN', None)
            result = subprocess.run([sys.executable, 'server/server.py'], cwd=ROOT, env=env,
                                    capture_output=True, text=True, timeout=10)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('Set CODEBATTLE_ORIGIN', result.stderr)
            self.assertFalse(path.exists())


class LegacyLauncherTests(unittest.TestCase):
    def test_quarantined_node_entrypoints_cannot_start(self):
        import shutil
        node = os.environ.get('CODEBATTLE_TEST_NODE') or shutil.which('node')
        if not node:
            self.skipTest('Node runtime unavailable; set CODEBATTLE_TEST_NODE to test quarantined launchers.')
        for entry in ('server/server.js', 'codebattle-mvp/backend/src/server.js'):
            for mode in ('development', 'production'):
                with self.subTest(entry=entry, mode=mode):
                    result = subprocess.run([node, entry], cwd=ROOT,
                                            env=dict(os.environ, NODE_ENV=mode),
                                            capture_output=True, text=True, timeout=10)
                    self.assertNotEqual(result.returncode, 0)
                    self.assertIn('is disabled: unsafe demo APIs/execution', result.stderr)
                    self.assertNotIn('Cannot find module', result.stderr)
