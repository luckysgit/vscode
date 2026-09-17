/* Persistent authoring API. Author responses stay in memory, never localStorage. */
class ProblemBankAPI {
  async request(path = '', method = 'GET', body) {
    const response = await fetch(`/api/problems${path}`, {
      method, credentials: 'same-origin', headers: {'Content-Type': 'application/json'},
      ...(body === undefined ? {} : {body: JSON.stringify(body)})
    });
    const data = await response.json();
    if (!response.ok) {
      const error = new Error(data.error || 'Unable to complete this problem action.');
      error.status = response.status;
      throw error;
    }
    return data;
  }
  list(scope, filters = {}) {
    const query = new URLSearchParams(Object.entries(filters).filter(([, value]) => value !== '' && value != null));
    return this.request(`${scope === 'my' ? '/my' : ''}?${query}`);
  }
  get(id, manage = false, versionId) {
    return this.request(`/${encodeURIComponent(id)}${manage ? '/manage' : ''}${versionId ? `?versionId=${encodeURIComponent(versionId)}` : ''}`);
  }
  create(data) { return this.request('', 'POST', data); }
  edit(id, data) { return this.request(`/${encodeURIComponent(id)}`, 'PATCH', data); }
  action(id, action, data) { return this.request(`/${encodeURIComponent(id)}/${action}`, 'POST', data); }
  versions(id) { return this.request(`/${encodeURIComponent(id)}/versions`); }
}
window.ProblemBankAPI = ProblemBankAPI;
