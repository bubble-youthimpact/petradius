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
    var chips = Array.prototype.slice.call(document.querySelectorAll('[data-type-filter]'));
    var type = '';
    var PAGE = 12;
    var limit = PAGE;
    var moreBtn = document.getElementById('show-more');
    var render = function () {
      var q = input.value.trim().toLowerCase();
      var age = ageSel ? ageSel.value : '';
      var shelter = shelterSel ? shelterSel.value : '';
      var matches = 0, visible = 0;
      cards.forEach(function (card) {
        var match = (!q || card.getAttribute('data-search').indexOf(q) !== -1) &&
          (!type || card.getAttribute('data-type') === type) &&
          (!age || card.getAttribute('data-age') === age) &&
          (!shelter || card.getAttribute('data-shelter') === shelter);
        var show = match && matches < limit;
        if (match) matches++;
        if (show) visible++;
        card.hidden = !show;
      });
      if (empty) empty.classList.toggle('show', matches === 0);
      if (count) count.textContent = matches === 0 ? 'No pets found'
        : 'Showing ' + visible + (visible < matches ? ' of ' + matches : '') + (matches === 1 ? ' pet' : ' pets');
      if (moreBtn) moreBtn.hidden = visible >= matches;
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
    [ageSel, shelterSel].forEach(function (el) { if (el) el.addEventListener('change', filter); });
    input.addEventListener('input', filter);
    searchForm.addEventListener('submit', function (e) { e.preventDefault(); filter(); });
    var clear = document.getElementById('clear-filters');
    if (clear) clear.addEventListener('click', function () {
      input.value = ''; type = '';
      if (ageSel) ageSel.value = '';
      if (shelterSel) shelterSel.value = '';
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
