// Fills every [data-i18n] element from the string tables in deck/i18n/ and switches
// language in place, so reveal.js keeps the current slide and fragment.
(function () {
  'use strict';

  const FALLBACK = 'en';
  const tables = window.YAB_I18N || {};

  function current() {
    const lang = new URLSearchParams(window.location.search).get('lang');
    return tables[lang] ? lang : FALLBACK;
  }

  function apply(lang) {
    const table = tables[lang] || tables[FALLBACK];
    document.querySelectorAll('[data-i18n]').forEach((el) => {
      const value = table[el.dataset.i18n];
      if (value !== undefined) el.innerHTML = value;
    });
    document.querySelectorAll('[data-i18n-aria]').forEach((el) => {
      const value = table[el.dataset.i18nAria];
      if (value === undefined) return;
      el.setAttribute('aria-label', value);
      el.title = value;
    });
    document.querySelectorAll('[data-i18n-alt]').forEach((el) => {
      const value = table[el.dataset.i18nAlt];
      if (value !== undefined) el.alt = value;
    });
    document.documentElement.lang = lang;
    document.querySelectorAll('[data-lang]').forEach((button) => {
      button.setAttribute('aria-pressed', String(button.dataset.lang === lang));
    });
  }

  function switchTo(lang) {
    apply(lang);
    const url = new URL(window.location.href);
    if (lang === FALLBACK) {
      url.searchParams.delete('lang');
    } else {
      url.searchParams.set('lang', lang);
    }
    try {
      window.history.replaceState(null, '', url);
    } catch (e) {
      // Some browsers refuse URL changes on file:// pages; the switch still works.
    }
    if (window.Reveal && window.Reveal.isReady()) window.Reveal.layout();
  }

  window.YabI18n = {current, apply, switchTo};
})();
