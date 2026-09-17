/* Migrate previously exposed demo cases out of browser caches, keeping public examples.
   This is cleanup, not a security boundary: real hidden cases must never reach the client. */
function publicProblem(problem) {
  const copy = { ...problem };
  if (Array.isArray(copy.testCases)) {
    copy.testCases = copy.testCases
      .filter(test => test && typeof test === 'object' && test.isHidden !== true && test.hidden !== true)
      .map(test => ({ input: String(test.input ?? ''), expected: String(test.expected ?? ''), isHidden: false }));
  }
  return copy;
}
if (typeof module !== 'undefined' && module.exports) module.exports = { publicProblem };
