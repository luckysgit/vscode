/* Run before styles load so a saved preference does not flash the wrong theme. */
(() => {
  const key = 'cb_theme';
  const system = window.matchMedia('(prefers-color-scheme: dark)');
  let preference;
  try { preference = localStorage.getItem(key); } catch (_) { /* Storage is optional. */ }
  if (!['light', 'dark'].includes(preference)) preference = null;

  function apply(theme) {
    document.documentElement.dataset.theme = theme;
    const label = theme === 'dark' ? 'Switch to light mode' : 'Switch to dark mode';
    const button = document.getElementById('btn-toggle-theme');
    if (button) {
      button.setAttribute('aria-label', label);
      button.title = label;
      document.getElementById('theme-icon').innerHTML = theme === 'dark'
        ? '<circle cx="12" cy="12" r="4"/><path d="M12 2v2m0 16v2M2 12h2m16 0h2M5 5l1.5 1.5m11 11L19 19M5 19l1.5-1.5m11-11L19 5"/>'
        : '<path d="M20.9 13A9 9 0 0 1 11 3.1 9 9 0 1 0 20.9 13Z"/>';
    }
    if (window.monaco?.editor) window.monaco.editor.setTheme(theme === 'dark' ? 'vs-dark' : 'vs');
  }

  apply(preference || (system.matches ? 'dark' : 'light'));
  document.addEventListener('DOMContentLoaded', () => {
    apply(document.documentElement.dataset.theme);
    document.getElementById('btn-toggle-theme').addEventListener('click', () => {
      preference = document.documentElement.dataset.theme === 'dark' ? 'light' : 'dark';
      try { localStorage.setItem(key, preference); } catch (_) { /* Still switch for this visit. */ }
      apply(preference);
    });
  });
  system.addEventListener('change', () => {
    if (!preference) apply(system.matches ? 'dark' : 'light');
  });
  window.addEventListener('storage', event => {
    if (event.key !== key && event.key !== null) return;
    preference = ['light', 'dark'].includes(event.newValue) ? event.newValue : null;
    apply(preference || (system.matches ? 'dark' : 'light'));
  });
})();
