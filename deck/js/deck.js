// Starts reveal.js and wires the section menu and its toggles, the language switch, the
// night mode, full-screen and share buttons.
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

  // The share button opens a panel with two links: this slide, or the deck from the start.
  const shareButton = document.querySelector('.yab-share');
  const sharePanel = document.getElementById('yab-share-panel');
  const shareChoices = Array.from(sharePanel.querySelectorAll('[data-share]'));
  const shareNote = sharePanel.querySelector('.yab-share-note span');
  const shareField = sharePanel.querySelector('.yab-share-link');
  const inShare = (element) => shareButton.contains(element) || sharePanel.contains(element);
  let shareTimer = null;

  function resetShare() {
    clearTimeout(shareTimer);
    shareNote.hidden = true;
    shareField.hidden = true;
  }

  // Closing with focus inside the panel hands it back to the button.
  function setShareOpen(open) {
    resetShare();
    if (!open && sharePanel.contains(document.activeElement)) shareButton.focus();
    sharePanel.hidden = !open;
    shareButton.setAttribute('aria-expanded', String(open));
  }

  shareButton.addEventListener('click', (event) => {
    const open = sharePanel.hidden;
    setShareOpen(open);
    if (open && event.detail === 0) shareChoices[0].focus();
    if (!open) releaseFocus(event, shareButton);
  });
  shareChoices.forEach((choice) => {
    choice.addEventListener('click', (event) => {
      const url = window.YabShare.link(choice.dataset.share === 'start');
      resetShare();
      releaseFocus(event, choice);
      window.YabShare.send(url).then((result) => {
        if (result === 'shared') {
          setShareOpen(false);
        } else if (result === 'copied') {
          shareNote.hidden = false;
          shareTimer = setTimeout(() => setShareOpen(false), 2000);
        } else if (result === 'manual') {
          shareField.value = url;
          shareField.hidden = false;
          shareField.focus();
          shareField.select();
        }
      });
    });
  });
  // Escape, a click elsewhere (the section menu too) or tabbing away closes the panel.
  document.addEventListener('keydown', (event) => {
    if (event.key !== 'Escape' || sharePanel.hidden) return;
    event.stopImmediatePropagation();
    event.preventDefault();
    setShareOpen(false);
  }, true);
  document.addEventListener('click', (event) => {
    if (!sharePanel.hidden && !inShare(event.target)) setShareOpen(false);
  });
  sharePanel.addEventListener('focusout', (event) => {
    if (event.relatedTarget && !inShare(event.relatedTarget)) setShareOpen(false);
  });

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

  // Section toggles: a section switched off is skipped when clicking through. The menu
  // stays open while they are switched; the click is inside it.
  const sectionToggles = Array.from(menuList.querySelectorAll('.yab-section-toggle'));
  function syncToggles() {
    sectionToggles.forEach((toggle) => {
      const on = window.YabSections.isOn(toggle.dataset.section);
      toggle.setAttribute('aria-checked', String(on));
      toggle.closest('li').classList.toggle('is-skipped', !on);
    });
  }
  sectionToggles.forEach((toggle) => {
    toggle.addEventListener('click', (event) => {
      window.YabSections.set(toggle.dataset.section,
          toggle.getAttribute('aria-checked') !== 'true');
      syncToggles();
      syncControls();
      releaseFocus(event, toggle);
    });
  });
  syncToggles();

  const sectionLabels = Array.from(document.querySelectorAll('.yab-section [data-section]'));

  // A section runs from its opener to the slide before the next section's opener; the
  // contents slide counts as its own. Reveal.getSlides() also works in the scroll view
  // reveal.js uses on narrow screens.
  function menuLinkOf(slide) {
    const slides = window.Reveal.getSlides();
    const index = slides.indexOf(slide);
    let section = null;
    menuLinks.forEach((link) => {
      const opener = document.getElementById(link.hash.slice(2));
      if (opener && slides.indexOf(opener) <= index) section = link;
    });
    return section;
  }

  // The section id a slide belongs to, or null for the contents slide.
  function sectionOf(slide) {
    const link = menuLinkOf(slide);
    if (!link || link.closest('.yab-menu-contents')) return null;
    return link.hash.slice(2);
  }

  // The menu marks the current section, and the label beside the menu names it (nothing
  // on the contents slide, which has no label).
  function markCurrentSection() {
    const section = menuLinkOf(window.Reveal.getCurrentSlide());
    menuLinks.forEach((link) => link.removeAttribute('aria-current'));
    if (section) section.setAttribute('aria-current', 'location');
    const name = section ? section.hash.slice(2) : null;
    sectionLabels.forEach((label) => {
      label.hidden = label.dataset.section !== name;
    });
  }

  // Clicking through skips switched-off sections; going to a slide by its link (the menu,
  // a contents card, the address bar) or picking it in the overview or on the progress bar
  // still opens it. reveal.js moves on a link either before or after the hash changes, so
  // the clicked target is remembered as well; it moves on a pick within the click itself.
  let linkTarget = null;
  let picking = false;
  document.addEventListener('click', (event) => {
    const link = event.target.closest('a[href^="#/"]');
    if (link) {
      linkTarget = link.hash.slice(2).split('/')[0];
    } else if (event.target.closest('.reveal .progress') ||
        (window.Reveal.isOverview() && event.target.closest('.reveal .slides section'))) {
      picking = true;
      setTimeout(() => {
        picking = false;
      }, 0);
    }
  }, true);

  function isOnAt(slide) {
    return window.YabSections.isOn(sectionOf(slide));
  }

  // The first slide from index on, in the given direction, whose section is on.
  function nextOnSlide(slides, index, direction) {
    for (let i = index; i >= 0 && i < slides.length; i += direction) {
      if (isOnAt(slides[i])) return i;
    }
    return -1;
  }

  let redirecting = false;
  window.Reveal.on('beforeslidechange', (event) => {
    if (redirecting || picking || window.Reveal.isOverview()) return;
    const slides = window.Reveal.getSlides();
    const from = window.Reveal.getIndices().h;
    const to = event.indexh;
    const target = slides[to];
    if (Math.abs(to - from) !== 1 || !target) return;
    const hashTarget = window.location.hash.slice(2).split('/')[0];
    if (target.id === linkTarget || target.id === hashTarget) return;
    const section = sectionOf(target);
    if (window.YabSections.isOn(section) || section === sectionOf(slides[from])) return;
    event.preventDefault();
    const found = nextOnSlide(slides, to, to - from);
    if (found < 0) {
      // Nothing on ahead: stay, as at the end of the deck.
      syncControls();
      return;
    }
    redirecting = true;
    try {
      window.Reveal.slide(found);
    } finally {
      redirecting = false;
    }
  });

  // The right arrow is off when nothing that is on lies ahead. reveal.js updates its
  // controls after its own events and on every key press, so this runs a moment later.
  function syncControls() {
    setTimeout(() => {
      const slides = window.Reveal.getSlides();
      const ahead = window.Reveal.availableFragments().next ||
          nextOnSlide(slides, window.Reveal.getIndices().h + 1, 1) >= 0;
      document.querySelectorAll('.reveal .controls .navigate-right').forEach((arrow) => {
        arrow.classList.toggle('enabled', ahead);
        arrow.disabled = !ahead;
      });
    }, 0);
  }

  window.Reveal.on('ready', markCurrentSection);
  window.Reveal.on('slidechanged', () => {
    markCurrentSection();
    linkTarget = null;
  });
  ['ready', 'slidechanged', 'fragmentshown', 'fragmenthidden', 'overviewhidden'].forEach((type) => {
    window.Reveal.on(type, syncControls);
  });

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
