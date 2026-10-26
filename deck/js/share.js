// Share button: the deck link as set up here (?lang=, ?skip=), at this slide or from the
// start, handed to the system share sheet or copied.
(function () {
  'use strict';

  // The address bar carries the language and the section toggles. The slide comes from
  // reveal.js (its slide path, null for the start), which writes it to the address bar up
  // to a second late.
  function link(slidePath) {
    const url = new URL(window.location.href);
    url.hash = slidePath && slidePath !== '/' ? slidePath : '';
    return url.href;
  }

  function copy(url) {
    if (!navigator.clipboard) return Promise.resolve('manual');
    return navigator.clipboard.writeText(url).then(() => 'copied', () => 'manual');
  }

  // A closed share sheet, or one still open from an earlier pick (desktop browsers keep the
  // page clickable behind it), leaves the link alone.
  const NOT_SENT = ['AbortError', 'InvalidStateError'];

  // Resolves to 'shared', 'copied', 'cancelled' or 'manual' (nothing could take the link, so
  // it has to be copied by hand).
  function send(url) {
    if (!navigator.share) return copy(url);
    return navigator.share({title: document.title, url}).then(
        () => 'shared',
        (error) => error && NOT_SENT.includes(error.name) ? 'cancelled' : copy(url));
  }

  window.YabShare = {link, send};
})();
