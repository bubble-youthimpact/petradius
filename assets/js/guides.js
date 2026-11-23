/* PetRadius — interactive guide pages
   Tabs, saved checklists, readiness score, feeding picker, food-switch planner,
   emergency checker and budget calculator. Progress is saved on this device only. */
(function () {
  var $$ = function (sel, root) { return Array.prototype.slice.call((root || document).querySelectorAll(sel)); };
  var page = location.pathname.replace(/index\.html$/, '');

  function load(key) {
    try { return JSON.parse(localStorage.getItem(key) || '{}') || {}; } catch (e) { return {}; }
  }
  function save(key, val) {
    try { localStorage.setItem(key, JSON.stringify(val)); } catch (e) { /* storage unavailable: still works, just not saved */ }
  }

  /* ---------- Tabs ---------- */
  $$('[data-tabs]').forEach(function (wrap) {
    var list = wrap.querySelector('[role="tablist"]');
    var tabs = $$('[role="tab"]', list);
    function select(tab, focus) {
      tabs.forEach(function (t) {
        var on = t === tab;
        t.setAttribute('aria-selected', on ? 'true' : 'false');
        t.tabIndex = on ? 0 : -1;
        var panel = document.getElementById(t.getAttribute('aria-controls'));
        if (panel) panel.hidden = !on;
      });
      if (focus) tab.focus();
    }
    tabs.forEach(function (t, i) {
      t.addEventListener('click', function () { select(t); });
      t.addEventListener('keydown', function (e) {
        var k = e.key, n = null;
        if (k === 'ArrowRight') n = tabs[(i + 1) % tabs.length];
        if (k === 'ArrowLeft') n = tabs[(i - 1 + tabs.length) % tabs.length];
        if (n) { e.preventDefault(); select(n, true); }
      });
    });
  });

  /* ---------- Checklists (readiness, first week) ---------- */
  $$('[data-checklist]').forEach(function (wrap) {
    var key = 'petradius-guide-' + wrap.getAttribute('data-checklist');
    var boxes = $$('input[type="checkbox"][data-id]', wrap);
    var state = load(key);
    boxes.forEach(function (b) { b.checked = !!state[b.getAttribute('data-id')]; });

    var isScore = wrap.hasAttribute('data-score');
    function update() {
      var done = boxes.filter(function (b) { return b.checked; }).length;
      var total = boxes.length;
      if (isScore) {
        var n = wrap.querySelector('[data-score-n]');
        var ring = wrap.querySelector('.g-ring');
        var hint = wrap.querySelector('[data-score-hint]');
        if (n) n.textContent = done;
        if (ring) ring.style.setProperty('--p', Math.round(done / total * 100));
        var level = done >= 10 ? 'great' : done >= 7 ? 'close' : 'wait';
        // Show a result once they've worked through the list (or ticked enough to qualify)
        var answered = done > 0;
        $$('[data-result]', wrap).forEach(function (r) { r.hidden = !answered || r.getAttribute('data-result') !== level; });
        if (hint) hint.hidden = answered;
      } else {
        var d = wrap.querySelector('[data-done]');
        var bar = wrap.querySelector('[data-bar]');
        var msg = wrap.querySelector('[data-complete]');
        if (d) d.textContent = done;
        if (bar) bar.style.width = (done / total * 100) + '%';
        if (msg) msg.hidden = done !== total;
      }
    }
    boxes.forEach(function (b) {
      b.addEventListener('change', function () {
        state[b.getAttribute('data-id')] = b.checked;
        save(key, state);
        update();
      });
    });
    var reset = wrap.querySelector('[data-reset]');
    if (reset) reset.addEventListener('click', function () {
      boxes.forEach(function (b) { b.checked = false; });
      state = {};
      save(key, state);
      update();
    });
    update();
  });

  /* ---------- Feeding schedule picker ---------- */
  var feed = document.querySelector('[data-feed]');
  if (feed) {
    var DATA = {
      dog: {
        young: ['3–4', 'meals daily (puppy formula)'],
        adult: ['2', 'meals daily (morning & evening)'],
        senior: ['2', 'meals daily (senior formula, highly digestible)']
      },
      cat: {
        young: ['3–4', 'meals daily (kitten formula)'],
        adult: ['2', 'meals daily, or measured portion feeding'],
        senior: ['2', 'meals daily (more moisture / wet food)']
      }
    };
    var sp = 'dog', st = 'young';
    var meals = feed.querySelector('[data-feed-meals]');
    var text = feed.querySelector('[data-feed-text]');
    var stageBtns = $$('[data-st]', feed);
    function paint() {
      var d = DATA[sp][st];
      meals.textContent = d[0];
      text.textContent = d[1];
      var young = stageBtns.filter(function (b) { return b.getAttribute('data-st') === 'young'; })[0];
      if (young) young.firstChild.textContent = sp === 'dog' ? 'Puppy' : 'Kitten';
    }
    function radio(attr, set) {
      var btns = $$('[' + attr + ']', feed);
      btns.forEach(function (b) {
        b.addEventListener('click', function () {
          btns.forEach(function (x) { x.setAttribute('aria-checked', x === b ? 'true' : 'false'); });
          set(b.getAttribute(attr));
          paint();
        });
      });
    }
    radio('data-sp', function (v) { sp = v; });
    radio('data-st', function (v) { st = v; });
    paint();
  }

  /* ---------- Food switch planner ---------- */
  var plan = document.querySelector('[data-transition]');
  if (plan) {
    var input = plan.querySelector('[data-start]');
    var list = plan.querySelector('[data-plan]');
    var PHASES = [[2, '25%', 'new food, 75% old'], [3, '50%', 'new food, 50% old'], [2, '75%', 'new food, 25% old'], [0, '100%', 'new food']];
    var fmt = function (d) { return d.toLocaleDateString(undefined, { weekday: 'short', month: 'short', day: 'numeric' }); };
    var toInput = function (d) { return d.getFullYear() + '-' + String(d.getMonth() + 1).padStart(2, '0') + '-' + String(d.getDate()).padStart(2, '0'); };
    input.value = toInput(new Date());
    function render() {
      var parts = (input.value || toInput(new Date())).split('-');
      var day = new Date(+parts[0], +parts[1] - 1, +parts[2]);
      var html = '';
      PHASES.forEach(function (ph) {
        var start = new Date(day);
        var label;
        if (ph[0]) {
          var end = new Date(day); end.setDate(end.getDate() + ph[0] - 1);
          label = fmt(start) + ' – ' + fmt(end);
          day.setDate(day.getDate() + ph[0]);
        } else {
          label = 'From ' + fmt(start);
        }
        html += '<li><b>' + ph[1] + '</b><span>' + ph[2] + '<small>' + label + '</small></span></li>';
      });
      list.innerHTML = html;
    }
    input.addEventListener('change', render);
    render();
  }

  /* ---------- Emergency checker ---------- */
  var emer = document.querySelector('[data-emergency]');
  if (emer) {
    var signs = $$('input[type="checkbox"]', emer);
    var alertBox = emer.querySelector('[data-alert]');
    signs.forEach(function (s) {
      s.addEventListener('change', function () {
        alertBox.hidden = !signs.some(function (x) { return x.checked; });
      });
    });
  }

  /* ---------- Budget calculator ---------- */
  var budget = document.querySelector('[data-budget]');
  if (budget) {
    var bkey = 'petradius-guide-budget';
    var inputs = $$('input[data-cost]', budget);
    var saved = load(bkey);
    var money = function (n) { return '$' + Math.round(n).toLocaleString(); };
    inputs.forEach(function (i) { if (saved[i.getAttribute('data-id')]) i.value = saved[i.getAttribute('data-id')]; });
    function calc() {
      var once = 0, month = 0;
      $$('.g-money-group', budget).forEach(function (g, gi) {
        var sub = 0, isMonth = false;
        $$('input[data-cost]', g).forEach(function (i) {
          var v = parseFloat(i.value) || 0;
          if (v < 0) v = 0;
          sub += v;
          isMonth = i.getAttribute('data-cost') === 'month';
        });
        if (isMonth) month += sub; else once += sub;
        var el = budget.querySelector('[data-subtotal="' + (gi + 1) + '"]');
        if (el) el.textContent = money(sub) + (isMonth ? ' / month' : '');
      });
      budget.querySelector('[data-total="once"]').textContent = money(once);
      budget.querySelector('[data-total="month"]').textContent = money(month);
      budget.querySelector('[data-total="year"]').textContent = money(once + month * 12);
    }
    inputs.forEach(function (i) {
      i.addEventListener('input', function () {
        saved[i.getAttribute('data-id')] = i.value;
        save(bkey, saved);
        calc();
      });
    });
    var breset = budget.querySelector('[data-reset]');
    if (breset) breset.addEventListener('click', function () {
      inputs.forEach(function (i) { i.value = ''; });
      saved = {};
      save(bkey, saved);
      calc();
    });
    calc();
  }
})();

/* ---------- "View original" popup ---------- */
(function () {
  var btn = document.querySelector('[data-original]');
  var modal = document.getElementById('orig-modal');
  if (!btn || !modal || typeof modal.showModal !== 'function') return; // old browsers just open the PDF link
  var frame = modal.querySelector('iframe');
  var images = modal.querySelector('.orig-images');
  // Browsers that show PDFs inline get the PDF; Android (no inline PDF viewer) gets the page images
  var inlinePdf = navigator.pdfViewerEnabled === true ||
    (navigator.pdfViewerEnabled === undefined && !/Android/i.test(navigator.userAgent));

  btn.addEventListener('click', function (e) {
    if (e.metaKey || e.ctrlKey || e.shiftKey || e.button === 1) return; // allow "open in new tab"
    e.preventDefault();
    if (inlinePdf) {
      if (!frame.getAttribute('src')) frame.setAttribute('src', frame.getAttribute('data-src'));
      frame.hidden = false;
    } else {
      images.hidden = false;
    }
    document.documentElement.classList.add('modal-open');
    modal.showModal();
    modal.querySelector('[data-close]').focus();
  });
  modal.querySelector('[data-close]').addEventListener('click', function () { modal.close(); });
  modal.addEventListener('click', function (e) { if (e.target === modal) modal.close(); }); // backdrop
  modal.addEventListener('close', function () { document.documentElement.classList.remove('modal-open'); });
})();

/* ---------- Guides list filter (stage) ---------- */
(function () {
  var box = document.getElementById('guide-filters');
  if (!box) return;
  var btns = Array.prototype.slice.call(box.querySelectorAll('[data-gfilter-stage]'));
  var groups = Array.prototype.slice.call(document.querySelectorAll('.guide-group'));
  btns.forEach(function (b) {
    b.addEventListener('click', function () {
      var stage = b.getAttribute('data-gfilter-stage');
      btns.forEach(function (x) { x.setAttribute('aria-pressed', x === b ? 'true' : 'false'); });
      groups.forEach(function (g) { g.hidden = !!stage && g.getAttribute('data-group') !== stage; });
    });
  });
})();
