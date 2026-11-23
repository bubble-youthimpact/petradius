/* PetRadius — site behaviour */
(function () {
  'use strict';

  /* ---------- Clean-URL fallback ----------
     GitHub Pages serves /about/ → about/index.html automatically.
     If the site is opened somewhere that needs the file name (e.g. a
     local preview showing ".../index.html"), point folder links at it. */
  if (/\.html?$/i.test(location.pathname) || location.protocol === 'file:') {
    document.querySelectorAll('a[href]').forEach(function (a) {
      var h = a.getAttribute('href');
      if (/^(https?:|mailto:|tel:|#)/i.test(h)) return;
      if (h === './' || h === '' ) a.setAttribute('href', 'index.html');
      else if (/\/$/.test(h)) a.setAttribute('href', h + 'index.html');
    });
  }

  /* ---------- Mobile menu ---------- */
  var toggle = document.querySelector('.menu-toggle');
  var menu = document.getElementById('mobile-menu');

  function setMenu(open) {
    if (!toggle || !menu) return;
    toggle.setAttribute('aria-expanded', open ? 'true' : 'false');
    toggle.setAttribute('aria-label', open ? 'Close menu' : 'Open menu');
    menu.classList.toggle('is-open', open);
    menu.setAttribute('aria-hidden', open ? 'false' : 'true');
    if ('inert' in menu) menu.inert = !open;
    document.body.classList.toggle('menu-open', open);
    if (open) {
      var first = menu.querySelector('a');
      if (first) setTimeout(function () { first.focus(); }, 50);
    }
  }

  if (toggle && menu) {
    setMenu(false);
    toggle.addEventListener('click', function () {
      setMenu(toggle.getAttribute('aria-expanded') !== 'true');
    });
    menu.addEventListener('click', function (e) {
      if (e.target.closest('a')) setMenu(false);
    });
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && menu.classList.contains('is-open')) {
        setMenu(false);
        toggle.focus();
      }
    });
    var mq = window.matchMedia('(min-width: 861px)');
    var onChange = function () { if (mq.matches) setMenu(false); };
    if (mq.addEventListener) mq.addEventListener('change', onChange); else mq.addListener(onChange);
  }

  /* ---------- Pet search + filters ---------- */
  var searchForm = document.getElementById('pet-search');
  if (searchForm) {
    var input = searchForm.querySelector('input');
    var cards = Array.prototype.slice.call(document.querySelectorAll('[data-search]'));
    var empty = document.getElementById('no-results');
    var count = document.getElementById('results-count');
    var ageSel = document.getElementById('f-age');
    var shelterSel = document.getElementById('f-shelter');
    var statusSel = document.getElementById('f-status');
    var locSel = document.getElementById('f-loc');
    var typeCounts = Array.prototype.slice.call(document.querySelectorAll('[data-count-type]'));
    var chips = Array.prototype.slice.call(document.querySelectorAll('[data-type-filter]'));
    var type = '';
    var PAGE = 12;
    var limit = PAGE;
    var moreBtn = document.getElementById('show-more');
    var render = function () {
      var q = input.value.trim().toLowerCase();
      var age = ageSel ? ageSel.value : '';
      var shelter = shelterSel ? shelterSel.value : '';
      var status = statusSel ? statusSel.value : '';
      var loc = locSel ? locSel.value : '';
      var matches = 0, visible = 0, perType = { '': 0, dog: 0, cat: 0 };
      cards.forEach(function (card) {
        var base = (!q || card.getAttribute('data-search').indexOf(q) !== -1) &&
          (!status || card.getAttribute('data-status') === status) &&
          (!age || card.getAttribute('data-age') === age) &&
          (!shelter || card.getAttribute('data-shelter') === shelter) &&
          (!loc || (loc.charAt(0) === 'r' ? card.getAttribute('data-region') : card.getAttribute('data-city')) === loc.slice(2));
        if (base) { perType['']++; perType[card.getAttribute('data-type')] = (perType[card.getAttribute('data-type')] || 0) + 1; }
        var match = base && (!type || card.getAttribute('data-type') === type);
        var show = match && matches < limit;
        if (match) matches++;
        if (show) visible++;
        card.hidden = !show;
      });
      if (empty) empty.classList.toggle('show', matches === 0);
      if (count) count.textContent = matches === 0 ? 'No pets found'
        : 'Showing ' + visible + (visible < matches ? ' of ' + matches : '') + (matches === 1 ? ' pet' : ' pets');
      if (moreBtn) moreBtn.hidden = visible >= matches;
      typeCounts.forEach(function (el) { el.textContent = perType[el.getAttribute('data-count-type')] || 0; });
    };
    // Any filter change starts again from the first page
    var filter = function () { limit = PAGE; render(); };
    if (moreBtn) moreBtn.addEventListener('click', function () {
      var firstNew = limit;
      limit += PAGE;
      render();
      var shownCards = cards.filter(function (c) { return !c.hidden; });
      var focusCard = shownCards[firstNew];
      if (focusCard) { var link = focusCard.querySelector('a'); if (link) link.focus({ preventScroll: true }); }
    });
    render();
    chips.forEach(function (chip) {
      chip.addEventListener('click', function () {
        type = chip.getAttribute('data-type-filter');
        chips.forEach(function (c) { c.setAttribute('aria-pressed', c === chip ? 'true' : 'false'); });
        filter();
      });
    });
    [statusSel, locSel, ageSel, shelterSel].forEach(function (el) { if (el) el.addEventListener('change', filter); });
    input.addEventListener('input', filter);
    searchForm.addEventListener('submit', function (e) { e.preventDefault(); filter(); });
    var clear = document.getElementById('clear-filters');
    if (clear) clear.addEventListener('click', function () {
      input.value = ''; type = '';
      if (ageSel) ageSel.value = '';
      if (shelterSel) shelterSel.value = '';
      if (locSel) locSel.value = '';
      if (statusSel) statusSel.value = 'available';
      chips.forEach(function (c, i) { c.setAttribute('aria-pressed', i === 0 ? 'true' : 'false'); });
      filter();
    });
  }

  /* ---------- Show the last known account state right away (account.js confirms it) ---------- */
  try {
    var hint = JSON.parse(localStorage.getItem('petradius-user-hint') || 'null');
    if (hint) {
      document.querySelectorAll('[data-auth="out"]').forEach(function (el) { el.hidden = true; });
      document.querySelectorAll('[data-auth="in"]').forEach(function (el) { el.hidden = false; });
      document.querySelectorAll('[data-user-name]').forEach(function (el) { el.textContent = hint.n || 'My account'; });
      document.querySelectorAll('[data-user-email]').forEach(function (el) { el.textContent = hint.e || ''; });
      document.querySelectorAll('[data-user-first]').forEach(function (el) {
        el.textContent = (hint.n || '').trim().split(/\s+/)[0] || 'Account';
      });
    }
  } catch (e) {}

  /* ---------- Helpers for forms ---------- */
  function note(el, msg, ok) {
    if (!el) return;
    el.textContent = msg;
    el.className = 'form-note show ' + (ok ? 'ok' : 'err');
  }
  function validate(form) {
    var valid = true;
    form.querySelectorAll('[required]').forEach(function (f) {
      var bad = !f.value.trim() || (f.type === 'email' && !/^\S+@\S+\.\S+$/.test(f.value.trim()));
      f.setAttribute('aria-invalid', bad ? 'true' : 'false');
      if (bad) valid = false;
    });
    return valid;
  }

  /* ---------- Contact form → FormSubmit (https://formsubmit.co) ----------
     Paste your FormSubmit random code below (from the activation email).
     Using the code instead of an email address keeps the inbox private. */
  var FORMSUBMIT_ID = '';

  var contact = document.getElementById('contact-form');
  if (contact) {
    var out = document.getElementById('contact-note');
    var publicEmail = contact.getAttribute('data-public-email');
    contact.addEventListener('submit', function (e) {
      e.preventDefault();
      if (contact._honey && contact._honey.value) return;            // bot trap
      if (!validate(contact)) { note(out, 'Please fill in every field with a valid email address.', false); return; }
      if (!FORMSUBMIT_ID) {
        note(out, 'Our contact form isn\u2019t connected yet. Please email us at ' + publicEmail + '.', false);
        return;
      }
      var btn = contact.querySelector('button[type="submit"]');
      var label = btn.innerHTML;
      btn.disabled = true; btn.classList.add('is-busy'); btn.textContent = 'Sending\u2026';
      var d = new FormData(contact);
      fetch('https://formsubmit.co/ajax/' + encodeURIComponent(FORMSUBMIT_ID), {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'Accept': 'application/json' },
        body: JSON.stringify({
          name: d.get('name'),
          email: d.get('email'),
          subject: d.get('subject'),
          message: d.get('message'),
          _replyto: d.get('email'),
          _subject: 'PetRadius contact: ' + d.get('subject'),
          _template: 'table',
          _captcha: 'false'
        })
      })
        .then(function (r) { return r.json().catch(function () { return {}; }).then(function (j) { return { ok: r.ok, body: j }; }); })
        .then(function (res) {
          var success = res.ok && (res.body.success === true || res.body.success === 'true');
          if (success) {
            contact.reset();
            note(out, 'Thanks! Your message has been sent \u2014 we\u2019ll get back to you soon.', true);
          } else {
            note(out, 'Sorry, your message couldn\u2019t be sent right now. Please try again or email us at ' + publicEmail + '.', false);
          }
        })
        .catch(function () {
          note(out, 'Sorry, your message couldn\u2019t be sent. Check your connection, or email us at ' + publicEmail + '.', false);
        })
        .then(function () { btn.disabled = false; btn.classList.remove('is-busy'); btn.innerHTML = label; });
    });
  }
})();

/* ================================================================
   Share buttons, count-up stats, toast
   ================================================================ */
(function () {
  var toastTimer;
  function toast(msg) {
    var el = document.querySelector('.toast');
    if (!el) {
      el = document.createElement('div');
      el.className = 'toast';
      el.setAttribute('role', 'status');
      document.body.appendChild(el);
    }
    el.textContent = msg;
    requestAnimationFrame(function () { el.classList.add('show'); });
    clearTimeout(toastTimer);
    toastTimer = setTimeout(function () { el.classList.remove('show'); }, 2400);
  }
  window.PetRadiusToast = toast;

  // Absolute URL for a path relative to the site root (works on petradius.org and in previews)
  function siteUrl(path) {
    var base = document.body.getAttribute('data-base') || './';
    return new URL(base + (path || ''), location.href).href;
  }

  function copyText(text) {
    if (navigator.clipboard && window.isSecureContext) {
      return navigator.clipboard.writeText(text);
    }
    return new Promise(function (resolve, reject) {
      var ta = document.createElement('textarea');
      ta.value = text;
      ta.setAttribute('readonly', '');
      ta.style.position = 'fixed';
      ta.style.opacity = '0';
      document.body.appendChild(ta);
      ta.select();
      try { document.execCommand('copy') ? resolve() : reject(); } catch (e) { reject(e); }
      document.body.removeChild(ta);
    });
  }

  // Phones and tablets get the native share sheet; computers copy the link
  var isTouch = window.matchMedia && window.matchMedia('(hover: none) and (pointer: coarse)').matches;

  document.addEventListener('click', function (e) {
    var btn = e.target.closest('[data-share]');
    if (!btn) return;
    e.preventDefault();
    e.stopPropagation();
    var url = siteUrl(btn.getAttribute('data-share'));
    var title = btn.getAttribute('data-share-title') || document.title;

    if (isTouch && navigator.share) {
      navigator.share({ title: title, url: url }).catch(function () {});
      return;
    }
    copyText(url).then(function () {
      toast('Link copied');
      btn.classList.add('is-copied');
      var label = btn.querySelector('span');
      var old = label ? label.textContent : '';
      if (label) label.textContent = 'Copied!';
      setTimeout(function () {
        btn.classList.remove('is-copied');
        if (label) label.textContent = old;
      }, 1800);
    }, function () {
      window.prompt('Copy this link:', url);
    });
  });

  // Count-up numbers (homepage stats)
  var counters = Array.prototype.slice.call(document.querySelectorAll('[data-countup]'));
  var reduce = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  if (counters.length && !reduce && 'IntersectionObserver' in window) {
    var run = function (el) {
      var target = parseInt(el.getAttribute('data-countup'), 10) || 0;
      var dur = 1400, start = null;
      var step = function (t) {
        if (start === null) start = t;
        var k = Math.min(1, (t - start) / dur);
        var eased = 1 - Math.pow(1 - k, 3);
        el.textContent = Math.round(target * eased);
        if (k < 1) requestAnimationFrame(step);
      };
      requestAnimationFrame(step);
    };
    counters.forEach(function (el) { el.textContent = '0'; });
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (en.isIntersecting) { io.unobserve(en.target); run(en.target); }
      });
    }, { threshold: 0.4 });
    counters.forEach(function (el) { io.observe(el); });
  }
})();

/* FAQ category tabs (homepage) */
(function () {
  var list = document.querySelector('.faq-tabs');
  if (!list) return;
  var tabs = Array.prototype.slice.call(list.querySelectorAll('[role="tab"]'));
  function select(tab, focus) {
    tabs.forEach(function (t) {
      var on = t === tab;
      t.setAttribute('aria-selected', on ? 'true' : 'false');
      t.tabIndex = on ? 0 : -1;
      var panel = document.getElementById(t.getAttribute('aria-controls'));
      if (panel) panel.hidden = !on;
    });
    if (focus) tab.focus();
    tab.scrollIntoView({ block: 'nearest', inline: 'nearest' });
  }
  tabs.forEach(function (t, i) {
    t.addEventListener('click', function () { select(t); });
    t.addEventListener('keydown', function (e) {
      var n = e.key === 'ArrowRight' ? tabs[(i + 1) % tabs.length] : e.key === 'ArrowLeft' ? tabs[(i - 1 + tabs.length) % tabs.length] : null;
      if (n) { e.preventDefault(); select(n, true); }
    });
  });
})();
