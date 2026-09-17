class SubmissionService {
  async executeCode({ code, language, problem, isSubmission = false, stdin = '' }) {
    if (!code.trim()) throw new Error('Write some code before running or submitting.');
    const response = await fetch(isSubmission ? '/api/submit' : '/api/run', {
      method: 'POST', credentials: 'same-origin',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ code, language, problem_id: problem?.id, isSubmission, stdin })
    });
    const result = await response.json();
    if (!response.ok) {
      const error = new Error(result.error || 'Unable to grade this submission.');
      error.status = response.status;
      throw error;
    }
    return result;
  }
}
if (typeof window !== 'undefined') window.SubmissionService = SubmissionService;
if (typeof module !== 'undefined' && module.exports) module.exports = SubmissionService;
