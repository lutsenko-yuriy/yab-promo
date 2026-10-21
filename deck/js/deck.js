// Starts reveal.js and wires the language switch and the full-screen button.
(function () {
  'use strict';

  const reduceMotion =
      window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  // Fill in the text before reveal.js measures the first layout.
  window.YabI18n.apply(window.YabI18n.current());

  // After a mouse click, give focus back to the deck so Space keeps advancing the
  // slides; keyboard users keep focus on the control they used.
  function releaseFocus(event, button) {
    if (event.detail > 0) button.blur();
  }

  document.querySelectorAll('[data-lang]').forEach((button) => {
    button.addEventListener('click', (event) => {
      window.YabI18n.switchTo(button.dataset.lang);
      releaseFocus(event, button);
    });
  });

  // Safari before 16.4 only has the webkit-prefixed API; iPhone has neither.
  const root = document.documentElement;
  const fullscreenElement = () =>
      document.fullscreenElement || document.webkitFullscreenElement;
  const fullscreen = document.querySelector('.yab-fullscreen');
  if (document.fullscreenEnabled || document.webkitFullscreenEnabled) {
    fullscreen.addEventListener('click', (event) => {
      const request = fullscreenElement() ?
          (document.exitFullscreen || document.webkitExitFullscreen).call(document) :
          (root.requestFullscreen || root.webkitRequestFullscreen).call(root);
      // Embedded without allowfullscreen, or refused by the browser: stay windowed.
      if (request) request.catch(() => {});
      releaseFocus(event, fullscreen);
    });
    const syncIcon = () => {
      fullscreen.classList.toggle('is-active', Boolean(fullscreenElement()));
    };
    document.addEventListener('fullscreenchange', syncIcon);
    document.addEventListener('webkitfullscreenchange', syncIcon);
  } else {
    fullscreen.hidden = true;
  }

  window.Reveal.initialize({
    // Leave keys on the language switch and full-screen button to the buttons.
    keyboardCondition: (event) => !event.target.closest('.yab-controls'),
    hash: true,
    width: 1280,
    height: 720,
    margin: 0.06,
    controls: true,
    progress: true,
    slideNumber: 'c/t',
    transition: reduceMotion ? 'none' : 'slide',
    autoAnimate: !reduceMotion,
    autoAnimateDuration: 0.7,
  });
})();
