/* PetRadius — Resources page: guides open in a popup; ?r=<id> links open/highlight a resource */
(function () {
  var modal = document.getElementById('guide-modal');
  if (!modal || typeof modal.showModal !== 'function') return; // very old browsers just follow the link

  var frame = document.getElementById('guide-frame');
  var titleEl = document.getElementById('guide-title');
  var openLink = document.getElementById('guide-open');
  var dlLink = document.getElementById('guide-download');
  var fallback = document.getElementById('guide-fallback');
  var fbOpen = document.getElementById('guide-fallback-open');
  var fbThumb = document.getElementById('guide-thumb');
  var shareBtn = modal.querySelector('.guide-share');
  var closeBtn = document.getElementById('guide-close');

  // Browsers that can show PDFs inline (desktop Chrome/Edge/Safari/Firefox, iPhone/iPad Safari).
  // Android browsers can't, so they get a preview with an "Open PDF" button instead.
  var inlinePdf = navigator.pdfViewerEnabled === true ||
    (navigator.pdfViewerEnabled === undefined && !/Android/i.test(navigator.userAgent));

  function idOf(card) {
    var item = card.closest('.res-item');
    return item ? item.id.replace(/^r-/, '') : '';
  }

  function openGuide(card) {
    var url = card.getAttribute('data-guide');
    var title = card.getAttribute('data-title') || 'Guide';
    var abs = new URL(url, location.href).href;
    titleEl.textContent = title;
    openLink.href = abs;
    dlLink.href = abs;
    fbOpen.href = abs;
    if (shareBtn) {
      shareBtn.setAttribute('data-share', 'resources/?r=' + idOf(card));
      shareBtn.setAttribute('data-share-title', title);
      shareBtn.setAttribute('aria-label', 'Share ' + title);
    }
    if (inlinePdf) {
      fallback.hidden = true;
      frame.hidden = false;
      frame.title = title;
      frame.src = abs + '#view=FitH';
    } else {
      frame.hidden = true;
      frame.src = 'about:blank';
      var img = card.querySelector('.thumb img');
      fbThumb.src = img ? img.currentSrc || img.src : '';
      fallback.hidden = false;
    }
    document.documentElement.classList.add('modal-open');
    modal.showModal();
    closeBtn.focus();
  }

  function closeGuide() { modal.close(); }

  modal.addEventListener('close', function () {
    document.documentElement.classList.remove('modal-open');
    frame.src = 'about:blank';
    // drop ?r= from the address bar so refreshing doesn't reopen it
    if (location.search.indexOf('r=') !== -1 && history.replaceState) {
      history.replaceState(null, '', location.pathname + location.hash);
    }
  });
  closeBtn.addEventListener('click', closeGuide);
  // click on the dark backdrop closes
  modal.addEventListener('click', function (e) { if (e.target === modal) closeGuide(); });

  document.addEventListener('click', function (e) {
    var card = e.target.closest('a[data-guide]');
    if (!card) return;
    if (e.metaKey || e.ctrlKey || e.shiftKey || e.button === 1) return; // let "open in new tab" work
    e.preventDefault();
    openGuide(card);
  });

  // Shared links: resources/?r=<id>
  var id = new URLSearchParams(location.search).get('r');
  if (id) {
    var item = document.getElementById('r-' + id);
    if (item) {
      var guide = item.querySelector('a[data-guide]');
      item.scrollIntoView({ block: 'center' });
      if (guide) {
        openGuide(guide);
      } else {
        item.classList.add('is-highlight');
        setTimeout(function () { item.classList.remove('is-highlight'); }, 2600);
      }
    }
  }
})();
