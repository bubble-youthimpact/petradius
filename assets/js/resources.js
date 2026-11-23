/* PetRadius — Websites & Videos page: shared links (?r=<id>) scroll to and highlight that resource.
   Older shared links to guides are sent to the guide's own page. */
(function () {
  var id = new URLSearchParams(location.search).get('r');
  if (!id) return;
  var me = document.currentScript || document.querySelector('script[data-guides]');
  var guides = ((me && me.getAttribute('data-guides')) || '').split(',');
  if (guides.indexOf(id) !== -1) {
    location.replace('../guides/' + encodeURIComponent(id) + '/');
    return;
  }
  var item = document.getElementById('r-' + id);
  if (!item) return;
  item.scrollIntoView({ block: 'center' });
  item.classList.add('is-highlight');
  setTimeout(function () { item.classList.remove('is-highlight'); }, 2600);
})();
