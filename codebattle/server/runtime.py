"""Fail closed: this working tree is an explicit local preview, not a release build."""
import os


def preview_mode(environ=None):
    env = os.environ if environ is None else environ
    mode = env.get('CODEBATTLE_MODE', '').strip().lower()
    node_env = env.get('NODE_ENV', '').strip().lower()
    if mode not in ('development', 'demo', 'test') or node_env not in ('', 'development', 'test'):
        raise RuntimeError(
            'CodeBattle is a local preview; staging/production startup is disabled. '
            'For local use run: CODEBATTLE_MODE=development python3 server/server.py. '
            'Tests must set CODEBATTLE_MODE=test. No production fallback is available.'
        )
    return mode
