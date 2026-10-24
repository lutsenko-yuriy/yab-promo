// Night mode. Runs in <head>, before the stylesheet, so the first paint already has the
// viewer's saved choice; with nothing saved the CSS follows the system setting.
(function () {
  'use strict';

  const KEY = 'yab-theme';
  const root = document.documentElement;
  const system = window.matchMedia('(prefers-color-scheme: dark)');

  // Private windows and some file:// pages throw on any storage access; the choice then
  // lasts for the visit only.
  function saved() {
    try {
      const theme = window.localStorage.getItem(KEY);
      return theme === 'dark' || theme === 'light' ? theme : null;
    } catch (e) {
      return null;
    }
  }

  function current() {
    return root.dataset.theme || (system.matches ? 'dark' : 'light');
  }

  function toggle() {
    const theme = current() === 'dark' ? 'light' : 'dark';
    root.dataset.theme = theme;
    try {
      window.localStorage.setItem(KEY, theme);
    } catch (e) {
      // Not remembered, but switched for this visit.
    }
  }

  const theme = saved();
  if (theme) root.dataset.theme = theme;

  window.YabTheme = {current, toggle, system};
})();
