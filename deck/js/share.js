// Share button: the deck link as set up here (?lang=, ?skip=), at this slide or from the
// start, handed to the system share sheet or copied.
(function () {
  'use strict';

  // The address bar already carries the language and the section toggles.
  function link(fromStart) {
    const url = new URL(window.location.href);
    if (fromStart) url.hash = '';
    return url.href;
  }

  function copy(url) {
    if (!navigator.clipboard) return Promise.resolve('manual');
    return navigator.clipboard.writeText(url).then(() => 'copied', () => 'manual');
  }

  // Resolves to 'shared', 'copied', 'cancelled' (the share sheet was closed) or 'manual'
  // (nothing could take the link, so it has to be copied by hand).
  function send(url) {
    if (!navigator.share) return copy(url);
    return navigator.share({title: document.title, url}).then(
        () => 'shared',
        (error) => error && error.name === 'AbortError' ? 'cancelled' : copy(url));
  }

  window.YabShare = {link, send};
})();
