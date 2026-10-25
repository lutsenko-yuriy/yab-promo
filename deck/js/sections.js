// Section toggles: which sections clicking through skips. The choices are carried in the
// link (?skip=cases+limits), so a tailored talk can be shared or bookmarked; a link
// without them has every section on.
(function () {
  'use strict';

  const SECTIONS = ['purpose', 'values', 'example', 'cases', 'limits', 'get-yab'];
  const PARAM = 'skip';

  // Hand-typed links may use commas too; unknown ids are dropped.
  const value = new URLSearchParams(window.location.search).get(PARAM) || '';
  const skipped = new Set(value.split(/[\s,]+/).filter((id) => SECTIONS.includes(id)));

  // The contents slide (no section) is always on.
  function isOn(id) {
    return id === null || !skipped.has(id);
  }

  // Rewrites only the skip parameter, so ?lang= and reveal.js's #/slide stay as they are.
  function set(id, on) {
    if (on) {
      skipped.delete(id);
    } else {
      skipped.add(id);
    }
    const url = new URL(window.location.href);
    if (skipped.size) {
      url.searchParams.set(PARAM, SECTIONS.filter((s) => skipped.has(s)).join(' '));
    } else {
      url.searchParams.delete(PARAM);
    }
    try {
      window.history.replaceState(null, '', url);
    } catch (e) {
      // Some browsers refuse URL changes on file:// pages; the toggles still work.
    }
  }

  window.YabSections = {SECTIONS, isOn, set};
})();
