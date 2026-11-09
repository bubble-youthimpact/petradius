/* PetRadius quiz engine — drives every quiz from assets/js/quizzes.js */
(function () {
  'use strict';

  var root = document.getElementById('petradius-quiz-widget');
  if (!root || !window.PETRADIUS_QUIZZES) return;

  var quiz = window.PETRADIUS_QUIZZES[root.getAttribute('data-quiz')];
  if (!quiz) return;
  var base = root.getAttribute('data-base') || '../../';
  var isPersonality = quiz.type === 'personality';
  var questions = quiz.questions;

  var $ = function (id) { return document.getElementById(id); };
  var counterEl = $('questionCounter');
  var titleEl = $('questionTitle');
  var optionsEl = $('optionsList');
  var nextBtn = $('nextBtn');
  var progressEl = $('progressBar');
  var cardEl = $('quizCard');
  var resultsEl = $('resultsContainer');
  var scoreEl = $('resultsScore');
  var messageEl = $('resultsMessage');
  var extraEl = $('resultsExtra');

  var index = 0;
  var score = 0;
  var tally = [];
  var choice = null;
  var locked = false;

  function esc(s) {
    return String(s).replace(/[&<>"]/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c];
    });
  }

  function load() {
    var q = questions[index];
    choice = null;
    locked = false;
    nextBtn.style.display = 'none';
    counterEl.textContent = 'Question ' + (index + 1) + ' of ' + questions.length;
    titleEl.textContent = q.question;
    progressEl.style.width = (index / questions.length * 100) + '%';

    optionsEl.innerHTML = '';
    q.options.forEach(function (text, i) {
      var btn = document.createElement('button');
      btn.type = 'button';
      btn.className = 'option-btn';
      btn.textContent = text;
      btn.addEventListener('click', function () { select(i, btn); });
      optionsEl.appendChild(btn);
    });
    nextBtn.textContent = index === questions.length - 1 ? 'View Results' : 'Next Question';
  }

  function select(i, btn) {
    var buttons = optionsEl.querySelectorAll('.option-btn');

    if (isPersonality) {
      // Personality quiz: no right answer, choice can change until "Next"
      choice = i;
      buttons.forEach(function (b) {
        b.classList.toggle('selected', b === btn);
        b.setAttribute('aria-pressed', b === btn ? 'true' : 'false');
      });
      nextBtn.style.display = 'block';
      return;
    }

    if (locked) return;
    locked = true;
    var answer = questions[index].answer;
    if (i === answer) {
      btn.classList.add('correct');
      score++;
    } else {
      btn.classList.add('incorrect');
      buttons[answer].classList.add('correct');
    }
    buttons.forEach(function (b) { b.disabled = true; });
    nextBtn.style.display = 'block';
  }

  function next() {
    if (isPersonality) {
      if (choice === null) return;
      tally[choice] = (tally[choice] || 0) + 1;
    }
    index++;
    if (index < questions.length) {
      load();
      titleEl.focus({ preventScroll: true });
    } else {
      showResults();
    }
  }

  function showResults() {
    progressEl.style.width = '100%';
    cardEl.style.display = 'none';
    resultsEl.style.display = 'block';

    if (!isPersonality) {
      scoreEl.style.display = '';
      scoreEl.textContent = score + ' / ' + questions.length;
      var tier = quiz.results.filter(function (r) { return score >= r.min; })[0];
      messageEl.textContent = tier ? tier.text : '';
      extraEl.innerHTML = '';
      report(score + '/' + questions.length + ' \u00b7 ' + (tier ? tier.label : ''));
    } else {
      scoreEl.style.display = 'none';
      var max = Math.max.apply(null, quiz.results.map(function (_, i) { return tally[i] || 0; }));
      var winners = quiz.results.filter(function (_, i) { return (tally[i] || 0) === max; });
      messageEl.textContent = winners.length > 1
        ? 'It’s a tie! Your personality matches more than one breed:'
        : 'Your personality match is…';
      extraEl.innerHTML = winners.map(function (r) {
        return '<div class="breed-result">' +
          '<h3>' + esc(r.breed) + '</h3>' +
          '<p class="breed-headline">' + esc(r.headline) + '</p>' +
          '<p>' + esc(r.text) + '</p>' +
          '<p class="breed-enjoy"><strong>You might enjoy:</strong> ' + esc(r.enjoy) + '</p>' +
          '</div>';
      }).join('') +
        '<p class="breed-note">This quiz is just for fun — every dog is an individual, and mixed breeds can be a perfect match too. ' +
        '<a href="' + base + 'pets/">Meet adoptable dogs</a> to find your real-life companion.</p>';
      report(winners.map(function (r) { return r.breed; }).join(' & '));
    }
    resultsEl.focus({ preventScroll: true });
    resultsEl.scrollIntoView({ behavior: 'smooth', block: 'start' });
  }

  // Tell the account layer (account.js) so it can save the result
  function report(resultText) {
    var saved = $('resultsSaved');
    if (saved) saved.textContent = '';
    document.dispatchEvent(new CustomEvent('quiz:complete', { detail: {
      quizId: root.getAttribute('data-quiz'),
      quizSlug: root.getAttribute('data-slug') || '',
      quizTitle: root.getAttribute('data-title') || '',
      type: quiz.type,
      score: isPersonality ? 0 : score,
      total: questions.length,
      result: resultText
    } }));
  }

  function restart() {
    index = 0; score = 0; tally = [];
    resultsEl.style.display = 'none';
    cardEl.style.display = 'block';
    load();
  }

  nextBtn.addEventListener('click', next);
  $('restartBtn').addEventListener('click', restart);
  load();
})();
