"""Server-owned tests for the two built-in practice problems."""
from runner import execute, RunnerError

# Never served as static files. Public examples first, fresh private edge cases after.
CASES = {
    'p1': [('2 7 11 15\n9', '0 1'), ('3 2 4\n6', '1 2'),
           ('-8 5 12 1\n4', '0 2'), ('6 6 3\n12', '0 1'), ('0 9 4\n4', '0 2')],
    'p2': [('()[]{}', 'true'), ('(]', 'false'), ('{[()]}', 'true'),
           ('([)]', 'false'), (']', 'false'), ('\n', 'true')],
}


def grade(code, language, problem_id):
    if problem_id not in CASES:
        raise RunnerError('Submit is available for the two built-in problems. You can still Run custom problem code.', 400)
    cases = CASES[problem_id]
    passed = 0
    duration = 0
    for index, (stdin, expected) in enumerate(cases):
        result = execute(code, language, stdin)
        duration += result['execution_time_ms']
        if result['status'] != 'completed':
            # Private input/output/errors must not leak through a failed test.
            return dict(status=result['status'], passed=passed, total=len(cases), execution_time_ms=duration,
                        stdout='', stderr=result['stderr'] if index < 2 else 'Execution failed on a private test.')
        actual = result['stdout'].split()
        wanted = expected.split()
        if problem_id == 'p1':
            actual, wanted = sorted(actual), sorted(wanted)
        if actual != wanted:
            return dict(status='wrong_answer', passed=passed, total=len(cases), execution_time_ms=duration,
                        stdout=result['stdout'] if index < 2 else '',
                        stderr=f'Example {index + 1}: expected {expected}' if index < 2 else 'A private test did not pass.')
        passed += 1
    return dict(status='accepted', passed=passed, total=len(cases), execution_time_ms=duration, stdout='', stderr='')
