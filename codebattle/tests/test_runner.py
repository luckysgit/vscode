import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'server'))
from runner import execute, RunnerError
from judge import grade

SOLUTION = '''nums = list(map(int, input().split()))
target = int(input())
seen = {}
for i, n in enumerate(nums):
    if target-n in seen:
        print(seen[target-n], i)
        break
    seen[n] = i
'''

@unittest.skipUnless(sys.platform == 'darwin', 'Local runner requires macOS')
class RunnerTests(unittest.TestCase):
    def test_output_input_and_errors(self):
        self.assertEqual(execute('print(input())', 'python', 'hello')['stdout'], 'hello\n')
        self.assertEqual(execute('print(', 'python')['status'], 'runtime_error')
        self.assertEqual(execute('raise ValueError("oops")', 'python')['status'], 'runtime_error')
        with self.assertRaises(RunnerError): execute('print(1)', 'javascript')

    def test_limits(self):
        self.assertEqual(execute('while True: pass', 'python')['status'], 'time_limit')
        result = execute('print("x"*100000)', 'python')
        self.assertEqual(result['status'], 'output_limit')
        self.assertLessEqual(len(result['stdout']) + len(result['stderr']), 16000)

    def test_sandbox_denies_sensitive_access(self):
        for code in [
            'open("/etc/passwd").read()',
            f'open({str(Path(__file__).resolve().parents[1] / "server/auth.py")!r}).read()',
            'open("/tmp/codebattle-escape", "w").write("bad")',
            'import socket; socket.create_connection(("127.0.0.1", 5000), timeout=1)',
            'import os; os.fork()',
            'import subprocess; subprocess.run(["/bin/echo", "bad"])',
        ]:
            with self.subTest(code=code):
                result = execute(code, 'python')
                self.assertEqual(result['status'], 'runtime_error', result)
                self.assertIn('Operation not permitted', result['stderr'])
        result = execute('import os; print(os.environ.get("HOME", "absent"))', 'python')
        self.assertEqual(result['stdout'], 'absent\n')

    def test_actual_grading(self):
        self.assertEqual(grade(SOLUTION, 'python', 'p1')['status'], 'accepted')
        self.assertEqual(grade('print("0 1")', 'python', 'p1')['status'], 'wrong_answer')
        private_failure = grade('s=input(); print("0 1" if s.startswith("2") else "1 2")', 'python', 'p1')
        self.assertEqual(private_failure['passed'], 2)
        self.assertEqual(private_failure['stdout'], '')
        self.assertEqual(private_failure['stderr'], 'A private test did not pass.')
        with self.assertRaises(RunnerError): grade(SOLUTION, 'python', 'unknown')

    def test_empty_parentheses_input(self):
        code = """s=input()
stack=[]
pairs={')':'(',']':'[','}':'{'}
valid=True
for c in s:
    if c in pairs:
        if not stack or stack.pop()!=pairs[c]:
            valid=False
            break
    else:
        stack.append(c)
print(str(valid and not stack).lower())
"""
        self.assertEqual(grade(code, 'python', 'p2')['status'], 'accepted')

    def test_memory_watchdog(self):
        code = 'import time\na=[]\nwhile True:\n a.append(bytearray(16*1024*1024))\n time.sleep(.01)'
        self.assertEqual(execute(code, 'python')['status'], 'memory_limit')
