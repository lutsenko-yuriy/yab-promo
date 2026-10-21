// Starts reveal.js and wires the language switch and the full-screen button.
(function () {
  'use strict';

  const reduceMotion =
      window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  // Fill in the text before reveal.js measures the first layout.
  window.YabI18n.apply(window.YabI18n.current());

  document.querySelectorAll('[data-lang]').forEach((button) => {
    button.addEventListener('click', () => {
      window.YabI18n.switchTo(button.dataset.lang);
      // Give focus back to the deck so Space keeps advancing the slides.
      button.blur();
    });
  });

  const fullscreen = document.querySelector('.yab-fullscreen');
  fullscreen.addEventListener('click', () => {
    if (document.fullscreenElement) {
      document.exitFullscreen();
    } else {
      document.documentElement.requestFullscreen();
    }
    fullscreen.blur();
  });
  document.addEventListener('fullscreenchange', () => {
    fullscreen.classList.toggle('is-active', Boolean(document.fullscreenElement));
  });

  window.Reveal.initialize({
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
