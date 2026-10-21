Reveal.initialize({
  hash: true,
  slideNumber: 'c/t',
  transition: 'slide',
  autoAnimateDuration: 0.8,
  width: 1280,
  height: 720,
});

const fullscreenButton = document.getElementById('fullscreen');
fullscreenButton?.addEventListener('click', () => {
  if (document.fullscreenElement) {
    document.exitFullscreen();
  } else {
    document.documentElement.requestFullscreen();
  }
});

// Keep the current slide when switching language.
document.querySelectorAll('[data-lang-link]').forEach((link) => {
  link.addEventListener('click', () => {
    link.href = link.getAttribute('href').split('#')[0] + window.location.hash;
  });
});
