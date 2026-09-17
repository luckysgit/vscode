"""Bounded, macOS-sandboxed Python execution for the localhost preview only.
No fallback to unsandboxed execution. Deployment requires a separate container runner.
"""
import json
import os
from pathlib import Path
import selectors
import signal
import subprocess
import sys
import tempfile
import threading
import time

GATE = threading.BoundedSemaphore(2)
MAX_OUTPUT = 16000
TIMEOUT = 3
BOOTSTRAP = '''import io, json, sys
request = json.load(sys.stdin)
sys.stdin = io.StringIO(request['stdin'])
exec(compile(request['code'], '<submission>', 'exec'), {'__name__': '__main__'})
'''


class RunnerError(Exception):
    def __init__(self, message, status=503):
        super().__init__(message)
        self.status = status


def execute(code, language, stdin=''):
    if language not in ('python', 'python3'):
        raise RunnerError('Only Python is enabled in this local preview.', 400)
    if sys.platform != 'darwin' or not Path('/usr/bin/sandbox-exec').is_file():
        raise RunnerError('The isolated Python runner requires macOS. No unsafe execution fallback is enabled.')
    if not GATE.acquire(blocking=False):
        raise RunnerError('The runner is busy. Please try again shortly.', 429)
    try:
        return _execute(code, stdin)
    finally:
        GATE.release()


def _execute(code, stdin):
    runtime = str(Path(sys.base_prefix).resolve())
    executable = str(Path(sys.executable).resolve())
    # Metadata is needed by dyld/realpath; document contents remain denied.
    reads = [runtime, '/System/Library', '/usr/lib', '/private/var/db/dyld']
    profile = ('(version 1)(deny default)(allow file-read-metadata)(allow sysctl-read)'
               '(allow process-exec (literal ' + json.dumps(executable) + ') (literal ' + json.dumps(runtime + '/Resources/Python.app/Contents/MacOS/Python') + '))'
               '(allow file-read-data ' + ' '.join('(subpath ' + json.dumps(p) + ')' for p in reads)
               + ' (literal "/dev/null") (literal "/dev/urandom"))')
    started = time.monotonic()
    output = {'stdout': bytearray(), 'stderr': bytearray()}
    status = 'completed'
    with tempfile.TemporaryFile() as request, selectors.DefaultSelector() as selector:
        request.write(json.dumps({'code': code, 'stdin': stdin}).encode())
        request.seek(0)
        try:
            proc = subprocess.Popen([executable, '-I', str(Path(__file__).with_name('runner_limits.py')), '-p', profile, executable, '-I', '-B', '-u', '-c', BOOTSTRAP],
                stdin=request, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd='/',
                env={'PATH': '/usr/bin:/bin', 'LANG': 'en_US.UTF-8'}, start_new_session=True)
        except OSError as error:
            raise RunnerError('The isolated runner could not start.') from error
        try:
            for name in output:
                stream = getattr(proc, name)
                os.set_blocking(stream.fileno(), False)
                selector.register(stream, selectors.EVENT_READ, name)
            last_memory_check = 0
            while selector.get_map():
                if time.monotonic() - last_memory_check > 0.1 and proc.poll() is None:
                    # macOS rejects RLIMIT_AS/DATA; bound resident memory from the parent.
                    memory = subprocess.run(['/bin/ps', '-o', 'rss=', '-p', str(proc.pid)],
                                            capture_output=True, text=True, timeout=1)
                    last_memory_check = time.monotonic()
                    if memory.stdout.strip().isdigit() and int(memory.stdout) > 262144:
                        status = 'memory_limit'
                        break
                if time.monotonic() - started > TIMEOUT:
                    status = 'time_limit'
                    break
                for key, _ in selector.select(0.05):
                    chunk = os.read(key.fd, 4096)
                    if not chunk:
                        selector.unregister(key.fileobj)
                        continue
                    remaining = MAX_OUTPUT - sum(map(len, output.values()))
                    output[key.data].extend(chunk[:remaining])
                    if len(chunk) > remaining:
                        status = 'output_limit'
                        break
                if status != 'completed':
                    break
            if status == 'completed':
                try:
                    proc.wait(timeout=max(0.01, TIMEOUT - (time.monotonic() - started)))
                except subprocess.TimeoutExpired:
                    status = 'time_limit'
        finally:
            if proc.poll() is None:
                os.killpg(proc.pid, signal.SIGKILL)
            proc.wait()
            proc.stdout.close()
            proc.stderr.close()
    if status == 'completed' and proc.returncode:
        status = 'time_limit' if proc.returncode in (-signal.SIGKILL, -signal.SIGXCPU) else 'runtime_error'
    decoded = {key: value.decode('utf-8', errors='replace') for key, value in output.items()}
    if status == 'runtime_error' and decoded['stderr'].startswith('sandbox-exec:'):
        raise RunnerError('macOS denied runner startup. Start the app outside a nested sandbox.')
    return {'status': status, **decoded, 'execution_time_ms': round((time.monotonic() - started) * 1000)}
