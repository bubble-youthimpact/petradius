/* PetRadius — account UI: header menu, login/sign-up, favourites, quiz history, profile */
import { getBackend, friendlyError, DEMO_EMAIL, DEMO_PASSWORD } from './backend.js';
import { PETS, QUIZ_META } from './site-data.js';

const ROOT = document.body.getAttribute('data-base') || './';
// Matches main.js: add index.html when the host needs explicit file names
const NEEDS_FILE = /\.html?$/i.test(location.pathname) || location.protocol === 'file:';
const u = path => ROOT + path + (NEEDS_FILE && (path === '' || path.endsWith('/')) ? 'index.html' : '');
const NEXT_KEY = 'petradius-next';
const HINT_KEY = 'petradius-user-hint';
const $ = (s, el = document) => el.querySelector(s);
const $$ = (s, el = document) => Array.from(el.querySelectorAll(s));
const esc = s => String(s == null ? '' : s).replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
const ss = {
  get(k) { try { return sessionStorage.getItem(k); } catch (e) { return null; } },
  set(k, v) { try { v == null ? sessionStorage.removeItem(k) : sessionStorage.setItem(k, v); } catch (e) {} }
};
const ls = {
  set(k, v) { try { v == null ? localStorage.removeItem(k) : localStorage.setItem(k, JSON.stringify(v)); } catch (e) {} }
};

const USER_ICON = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="12" cy="8" r="4"/><path d="M4 21a8 8 0 0 1 16 0"/></svg>';
function avatarHTML(user, size) {
  if (user && user.photoURL) {
    return `<img src="${esc(user.photoURL)}" alt="" referrerpolicy="no-referrer" width="${size}" height="${size}">`;
  }
  return USER_ICON;
}
function firstName(user) {
  const n = (user && user.displayName || '').trim();
  return n ? n.split(/\s+/)[0] : 'Account';
}
function fmtDate(d) {
  if (!d) return '';
  try { return d.toLocaleDateString(undefined, { year: 'numeric', month: 'short', day: 'numeric' }); } catch (e) { return ''; }
}

/* ---------- Toast ---------- */
let toastTimer;
function toast(html, ms = 4200) {
  let el = $('.toast');
  if (!el) {
    el = document.createElement('div');
    el.className = 'toast';
    el.setAttribute('role', 'status');
    document.body.appendChild(el);
  }
  el.innerHTML = html;
  requestAnimationFrame(() => el.classList.add('show'));
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => el.classList.remove('show'), ms);
}
function rememberHere() { ss.set(NEXT_KEY, location.href); }
let navigating = false;
function goNext() {
  if (navigating) return;
  navigating = true;
  const next = ss.get(NEXT_KEY);
  ss.set(NEXT_KEY, null);
  location.href = next || u('profile/');
}
function note(el, msg, ok) {
  if (!el) return;
  el.textContent = msg;
  el.className = 'form-note show ' + (ok ? 'ok' : 'err');
}
function busy(btn, on, label) {
  if (!btn) return;
  if (on) { btn.dataset.label = btn.innerHTML; btn.disabled = true; btn.classList.add('is-busy'); if (label) btn.textContent = label; }
  else { btn.disabled = false; btn.classList.remove('is-busy'); if (btn.dataset.label) btn.innerHTML = btn.dataset.label; }
}

/* ================================================================
   Header account menu
   ================================================================ */
function renderHeader(user) {
  ls.set(HINT_KEY, user ? { n: user.displayName, e: user.email, p: user.photoURL } : null);
  $$('[data-auth="out"]').forEach(el => { el.hidden = !!user; });
  $$('[data-auth="in"]').forEach(el => { el.hidden = !user; });
  if (!user) return;
  $$('[data-user-avatar]').forEach(el => { el.innerHTML = avatarHTML(user, 36); });
  $$('[data-user-name]').forEach(el => { el.textContent = user.displayName || 'My account'; });
  $$('[data-user-first]').forEach(el => { el.textContent = firstName(user); });
  $$('[data-user-email]').forEach(el => { el.textContent = user.email; });
}

function wireHeader(backend) {
  const btn = $('.avatar-btn');
  const menu = $('.account-dropdown');
  if (btn && menu) {
    const set = open => {
      btn.setAttribute('aria-expanded', open ? 'true' : 'false');
      menu.hidden = !open;
    };
    btn.addEventListener('click', e => { e.stopPropagation(); set(menu.hidden); });
    document.addEventListener('click', e => { if (!menu.hidden && !menu.contains(e.target)) set(false); });
    document.addEventListener('keydown', e => { if (e.key === 'Escape' && !menu.hidden) { set(false); btn.focus(); } });
  }
  $$('[data-signout]').forEach(b => b.addEventListener('click', async () => {
    await backend.signOut();
    toast('You’ve been logged out.');
    if (document.body.classList.contains('requires-auth')) location.href = u('');
  }));
}

/* ================================================================
   Favourites (pet detail heart + card hearts)
   ================================================================ */
let favSet = new Set();
function paintFavs() {
  $$('[data-fav]').forEach(b => {
    const on = favSet.has(b.getAttribute('data-fav'));
    b.setAttribute('aria-pressed', on ? 'true' : 'false');
    b.setAttribute('aria-label', (on ? 'Remove ' : 'Save ') + (b.getAttribute('data-name') || 'pet') + (on ? ' from favorites' : ' to favorites'));
  });
}
async function loadFavs(backend, user) {
  favSet = new Set(user ? await backend.getFavorites().catch(() => []) : []);
  paintFavs();
}
function wireFavs(backend) {
  document.addEventListener('click', async e => {
    const b = e.target.closest('[data-fav]');
    if (!b) return;
    e.preventDefault();
    e.stopPropagation();
    if (!backend.current()) {
      rememberHere();
      toast(`<span>Log in to save favorites.</span> <a href="${u('login/')}">Log in</a>`);
      return;
    }
    const slug = b.getAttribute('data-fav');
    const on = !favSet.has(slug);
    on ? favSet.add(slug) : favSet.delete(slug);
    paintFavs();
    b.classList.remove('pop'); void b.offsetWidth; b.classList.add('pop');
    try {
      await backend.setFavorite(slug, on);
      toast(on ? `Saved to <a href="${u('profile/')}#favorites">your favorites</a>.` : 'Removed from favorites.', 2600);
      document.dispatchEvent(new CustomEvent('favs:changed'));
    } catch (err) {
      on ? favSet.delete(slug) : favSet.add(slug);
      paintFavs();
      toast(esc(friendlyError(err)));
    }
  });
}

/* ================================================================
   Quiz results
   ================================================================ */
function wireQuiz(backend) {
  document.addEventListener('quiz:complete', async e => {
    const box = $('#resultsSaved');
    const user = backend.current();
    if (!user) {
      rememberHere();
      if (box) box.innerHTML = `<a href="${u('login/')}">Log in</a> or <a href="${u('signup/')}">create an account</a> to save your quiz results.`;
      return;
    }
    try {
      await backend.addQuizResult(e.detail);
      if (box) box.innerHTML = `✓ Saved to <a href="${u('profile/')}#quizzes">your quiz history</a>.`;
    } catch (err) {
      if (box) box.textContent = 'We couldn’t save this result: ' + friendlyError(err);
    }
  });
}

/* ================================================================
   Login / sign-up pages
   ================================================================ */
function wireAuthPages(backend) {
  const page = document.body.getAttribute('data-page');
  if (page !== 'login' && page !== 'signup') return;

  if (backend.current()) { goNext(); return; }

  const form = $('#auth-form');
  const out = $('#auth-note');

  $$('.pw-toggle').forEach(t => t.addEventListener('click', () => {
    const input = t.parentElement.querySelector('input');
    const show = input.type === 'password';
    input.type = show ? 'text' : 'password';
    t.setAttribute('aria-pressed', show ? 'true' : 'false');
    t.setAttribute('aria-label', show ? 'Hide password' : 'Show password');
  }));

  const google = $('#google-btn');
  if (google) google.addEventListener('click', async () => {
    busy(google, true);
    try {
      const u = await backend.signInGoogle();
      if (u) goNext();
    } catch (err) {
      note(out, friendlyError(err), false);
    } finally { busy(google, false); }
  });

  const demo = $('#demo-btn');
  if (demo && backend.mode === 'preview') demo.addEventListener('click', () => {
    form.email.value = DEMO_EMAIL;
    form.password.value = DEMO_PASSWORD;
    form.requestSubmit ? form.requestSubmit() : form.dispatchEvent(new Event('submit', { cancelable: true }));
  });

  const reset = $('#forgot-btn');
  if (reset) reset.addEventListener('click', async () => {
    const email = form.email.value.trim();
    if (!email) { note(out, 'Enter your email above, then click “Forgot password?” again.', false); form.email.focus(); return; }
    try {
      await backend.resetPassword(email);
      note(out, backend.mode === 'firebase' ? `If an account exists for ${email}, a reset link is on its way.` : 'Preview mode: password reset emails are sent once Firebase is connected.', true);
    } catch (err) { note(out, friendlyError(err), false); }
  });

  form.addEventListener('submit', async e => {
    e.preventDefault();
    let ok = true;
    $$('[required]', form).forEach(f => {
      const bad = !f.value.trim() || (f.type === 'email' && !/^\S+@\S+\.\S+$/.test(f.value.trim())) || (f.name === 'password' && page === 'signup' && f.value.length < 6);
      f.setAttribute('aria-invalid', bad ? 'true' : 'false');
      if (bad) ok = false;
    });
    if (!ok) { note(out, page === 'signup' ? 'Please fill in every field. Passwords need at least 6 characters.' : 'Please enter your email and password.', false); return; }
    const btn = $('button[type="submit"]', form);
    busy(btn, true, page === 'signup' ? 'Creating account…' : 'Logging in…');
    try {
      if (page === 'signup') await backend.signUp(form.name.value.trim(), form.email.value.trim(), form.password.value);
      else await backend.signIn(form.email.value.trim(), form.password.value);
      goNext();
    } catch (err) {
      note(out, friendlyError(err), false);
      busy(btn, false);
    }
  });
}

/* ================================================================
   Profile page
   ================================================================ */
function petCardHTML(p) {
  return `<div class="pet-card-wrap">
    <a class="pet-card" href="${u('pets/' + p.slug + '/')}">
      <div class="thumb"><img src="${ROOT}${p.img}" alt="${esc(p.name)}, ${esc(p.breed)}" loading="lazy" width="577" height="577"></div>
      <div class="body"><div class="row"><h3>${esc(p.name)}</h3><span class="tag">${esc(p.type)}</span></div><p class="breed">${esc(p.breed)}</p><p class="pet-meta">${esc(p.meta || '')}</p></div>
    </a>
    <button class="card-fav" type="button" data-fav="${p.slug}" data-name="${esc(p.name)}" aria-pressed="true">${HEART}</button>
  </div>`;
}
const HEART = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M19 14c1.49-1.46 3-3.21 3-5.5A5.5 5.5 0 0 0 16.5 3c-1.76 0-3 .5-4.5 2-1.5-1.5-2.74-2-4.5-2A5.5 5.5 0 0 0 2 8.5c0 2.3 1.5 4.05 3 5.5l7 7Z"/></svg>';

function wireProfile(backend) {
  if (document.body.getAttribute('data-page') !== 'profile') return;
  const gate = $('#profile-gate');
  const app = $('#profile-app');
  const tabs = $$('[data-tab]');
  const TAB_IDS = ['info', 'favorites', 'quizzes'];

  function showTab(id, focus) {
    if (!TAB_IDS.includes(id)) id = 'info';
    tabs.forEach(t => {
      const on = t.getAttribute('data-tab') === id;
      t.setAttribute('aria-selected', on ? 'true' : 'false');
      t.tabIndex = on ? 0 : -1;
      if (on && focus) t.focus();
    });
    TAB_IDS.forEach(t => { $('#tab-' + t).hidden = t !== id; });
  }
  tabs.forEach((t, i) => {
    t.addEventListener('click', () => {
      const id = t.getAttribute('data-tab');
      showTab(id);
      try { history.replaceState(null, '', '#' + id); } catch (e) { location.hash = id; }
    });
    t.addEventListener('keydown', e => {
      if (e.key !== 'ArrowRight' && e.key !== 'ArrowLeft') return;
      const n = tabs[(i + (e.key === 'ArrowRight' ? 1 : tabs.length - 1)) % tabs.length];
      n.click(); n.focus();
    });
  });
  window.addEventListener('hashchange', () => showTab(location.hash.slice(1)));
  showTab(location.hash.slice(1));

  const form = $('#profile-form');
  const out = $('#profile-note');

  async function renderInfo(user) {
    const p = await backend.getProfile();
    $('#pf-avatar').innerHTML = avatarHTML({ ...user, photoURL: p.photoURL }, 88);
    $('#pf-name').textContent = p.displayName || 'Welcome!';
    $('#pf-email').textContent = p.email;
    $('#pf-since').textContent = p.createdAt ? 'Member since ' + fmtDate(p.createdAt) : '';
    $('#pf-provider').textContent = user.provider === 'google.com' ? 'Google account' : 'Email account';
    ['displayName', 'location', 'phone', 'bio'].forEach(k => { form[k].value = p[k] || ''; });
    form.email.value = p.email;
    $('#bio-count').textContent = (p.bio || '').length;
    $('#pw-row').hidden = user.provider === 'google.com';
  }

  async function renderFavs() {
    const slugs = await backend.getFavorites();
    favSet = new Set(slugs);
    const pets = slugs.map(s => PETS.find(p => p.slug === s)).filter(Boolean);
    $('#fav-grid').innerHTML = pets.map(petCardHTML).join('');
    $('#fav-empty').hidden = pets.length > 0;
    $$('[data-count="favorites"]').forEach(el => { el.textContent = pets.length; });
    paintFavs();
  }

  async function renderQuizzes() {
    const results = await backend.getQuizResults();
    $$('[data-count="quizzes"]').forEach(el => { el.textContent = results.length; });
    $('#quiz-empty').hidden = results.length > 0;

    $('#quiz-summary').innerHTML = QUIZ_META.map(q => {
      const mine = results.filter(r => r.quizId === q.key);
      let big = '—', small = 'Not taken yet';
      if (mine.length) {
        if (q.type === 'scored') {
          const best = Math.max.apply(null, mine.map(r => r.score));
          big = `${best}<small>/${q.total}</small>`;
          small = `Best score · ${mine.length} attempt${mine.length > 1 ? 's' : ''}`;
        } else {
          big = `<span class="summary-text">${esc(mine[0].result)}</span>`;
          small = 'Latest match';
        }
      }
      return `<a class="summary-card" href="${u('quiz/' + q.slug + '/')}">
        <span class="summary-title">${esc(q.short)}</span>
        <strong>${big}</strong>
        <span class="summary-sub">${small}</span>
      </a>`;
    }).join('');

    $('#quiz-list').innerHTML = results.map(r => {
      const meta = QUIZ_META.find(q => q.key === r.quizId) || {};
      const scoreHTML = r.type === 'scored'
        ? `<span class="score-pill">${r.score}/${r.total}</span>`
        : `<span class="score-pill is-match">Match</span>`;
      return `<li class="history-item">
        ${scoreHTML}
        <div class="history-body">
          <strong>${esc(r.quizTitle || meta.title || 'Quiz')}</strong>
          <span>${esc(r.result || '')}</span>
        </div>
        <div class="history-meta">
          <time>${fmtDate(r.takenAt)}</time>
          ${meta.slug ? `<a href="${u('quiz/' + meta.slug + '/')}">Retake</a>` : ''}
        </div>
      </li>`;
    }).join('');
  }

  if (form) {
    form.bio.addEventListener('input', () => { $('#bio-count').textContent = form.bio.value.length; });
    form.addEventListener('submit', async e => {
      e.preventDefault();
      if (!form.displayName.value.trim()) { form.displayName.setAttribute('aria-invalid', 'true'); note(out, 'Please add your name.', false); return; }
      form.displayName.setAttribute('aria-invalid', 'false');
      const btn = $('button[type="submit"]', form);
      busy(btn, true, 'Saving…');
      try {
        await backend.saveProfile(Object.fromEntries(new FormData(form)));
        note(out, 'Your profile has been updated.', true);
        await renderInfo(backend.current());
      } catch (err) { note(out, friendlyError(err), false); }
      busy(btn, false);
    });
    $('#pf-reset').addEventListener('click', async () => {
      try {
        await backend.resetPassword(backend.current().email);
        note(out, backend.mode === 'firebase' ? 'We’ve emailed you a link to change your password.' : 'Preview mode: password emails are sent once Firebase is connected.', true);
      } catch (err) { note(out, friendlyError(err), false); }
    });
  }

  document.addEventListener('favs:changed', () => { if (backend.current()) renderFavs(); });

  let shownFor = null;
  async function render(user) {
    gate.hidden = !!user;
    app.hidden = !user;
    if (!user) { shownFor = null; return; }
    if (shownFor === user.uid) { $('#pf-name').textContent = user.displayName || 'Welcome!'; return; }
    shownFor = user.uid;
    try {
      await Promise.all([renderInfo(user), renderFavs(), renderQuizzes()]);
    } catch (err) {
      note(out, friendlyError(err), false);
    }
  }
  $('#gate-login') && $('#gate-login').addEventListener('click', rememberHere);
  return render;
}

/* ================================================================
   Boot
   ================================================================ */
(async function boot() {
  const backend = await getBackend();
  if (backend.mode === 'preview') $$('[data-preview-note]').forEach(el => { el.hidden = false; });
  wireHeader(backend);
  wireFavs(backend);
  wireQuiz(backend);
  const renderProfile = wireProfile(backend);

  await backend.ready();
  const apply = user => {
    renderHeader(user);
    loadFavs(backend, user);
    if (renderProfile) renderProfile(user);
  };
  apply(backend.current());
  wireAuthPages(backend);
  backend.onChange(user => {
    apply(user);
    const page = document.body.getAttribute('data-page');
    if (user && (page === 'login' || page === 'signup')) goNext();
  });
  document.documentElement.classList.add('auth-ready');
})();
