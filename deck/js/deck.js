// Starts reveal.js and wires the section menu, the language switch, the night mode and
// full-screen buttons.
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

  // Night mode is on while the deck is dark, whether picked here or by the system.
  const nightMode = document.querySelector('.yab-theme');
  const syncNightMode = () => {
    nightMode.setAttribute('aria-pressed', String(window.YabTheme.current() === 'dark'));
  };
  nightMode.addEventListener('click', (event) => {
    window.YabTheme.toggle();
    syncNightMode();
    releaseFocus(event, nightMode);
  });
  window.YabTheme.system.addEventListener('change', syncNightMode);
  syncNightMode();

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

  // The hint to turn a phone sideways can be waved away for the rest of the visit.
  document.querySelector('.yab-rotate-dismiss').addEventListener('click', () => {
    document.documentElement.classList.add('yab-rotate-dismissed');
  });

  // The section menu: a list of the sections, the one being shown marked as current.
  const menu = document.querySelector('.yab-menu');
  const menuToggle = menu.querySelector('.yab-menu-toggle');
  const menuList = menu.querySelector('.yab-menu-list');
  const menuLinks = Array.from(menuList.querySelectorAll('a'));

  function setMenuOpen(open) {
    menuList.hidden = !open;
    menuToggle.setAttribute('aria-expanded', String(open));
  }

  menuToggle.addEventListener('click', (event) => {
    const open = menuList.hidden;
    setMenuOpen(open);
    if (open && event.detail === 0) menuLinks[0].focus();
    if (!open) releaseFocus(event, menuToggle);
  });
  menuLinks.forEach((link) => {
    link.addEventListener('click', (event) => {
      setMenuOpen(false);
      if (window.Reveal.isOverview()) window.Reveal.toggleOverview(false);
      releaseFocus(event, link);
    });
  });
  // Escape closes an open menu wherever focus is (Safari and Firefox don't focus clicked
  // buttons); capturing it first keeps reveal.js from also opening the overview.
  document.addEventListener('keydown', (event) => {
    if (event.key !== 'Escape' || menuList.hidden) return;
    event.stopImmediatePropagation();
    event.preventDefault();
    const hadFocus = menu.contains(document.activeElement);
    setMenuOpen(false);
    if (hadFocus) menuToggle.focus();
  }, true);
  document.addEventListener('click', (event) => {
    if (!menu.contains(event.target)) setMenuOpen(false);
  });
  // Tabbing out of the menu closes it.
  menu.addEventListener('focusout', (event) => {
    if (event.relatedTarget && !menu.contains(event.relatedTarget)) setMenuOpen(false);
  });

  const sectionLabels = Array.from(document.querySelectorAll('.yab-section [data-section]'));

  // A section runs from its opener to the slide before the next section's opener; the
  // contents slide counts as its own. The menu marks it, and the label beside the menu
  // names it (nothing on the contents slide, which has no label).
  function markCurrentSection() {
    // Reveal.getSlides() also works in the scroll view reveal.js uses on narrow screens.
    const slides = window.Reveal.getSlides();
    const current = slides.indexOf(window.Reveal.getCurrentSlide());
    let section = null;
    menuLinks.forEach((link) => {
      const opener = document.getElementById(link.hash.slice(2));
      if (opener && slides.indexOf(opener) <= current) section = link;
      link.removeAttribute('aria-current');
    });
    if (section) section.setAttribute('aria-current', 'location');
    const name = section ? section.hash.slice(2) : null;
    sectionLabels.forEach((label) => {
      label.hidden = label.dataset.section !== name;
    });
  }

  window.Reveal.on('ready', markCurrentSection);
  window.Reveal.on('slidechanged', markCurrentSection);

  window.Reveal.initialize({
    // Leave keys on the menu and the buttons at the top right to those controls.
    keyboardCondition: (event) =>
      !event.target.closest('.yab-controls, .yab-menu'),
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
