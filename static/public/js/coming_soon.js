/**
 * Coming Soon - Contagem regressiva e efeitos dinâmicos
 */
(function () {
  'use strict';

  const CONFIG = window.COMING_SOON_CONFIG || {};
  const countdownEnd = CONFIG.countdownEnd ? new Date(CONFIG.countdownEnd) : null;
  const showSeconds = CONFIG.showSeconds !== false;

  const $ = id => document.getElementById(id);
  const daysEl = $('cs-days');
  const hoursEl = $('cs-hours');
  const minsEl = $('cs-mins');
  const secsEl = $('cs-secs');
  const countdownEl = $('cs-countdown');
  const finishedEl = $('cs-finished');
  const progressWrap = $('cs-progress-wrap');
  const progressBar = $('cs-progress-bar');
  const titleEl = $('cs-title');
  const particlesEl = $('cs-particles');

  function pad(n) {
    return String(Math.max(0, Math.floor(n))).padStart(2, '0');
  }

  function getTotalSeconds() {
    if (!countdownEnd) return 0;
    const now = new Date();
    const diff = countdownEnd - now;
    return Math.max(0, diff / 1000);
  }

  function updateCountdown() {
    const totalSecs = getTotalSeconds();
    if (totalSecs <= 0) {
      if (countdownEl) countdownEl.style.display = 'none';
      if (progressWrap) progressWrap.style.display = 'none';
      if (finishedEl) {
        finishedEl.style.display = 'block';
        finishedEl.style.animation = 'cs-title-glow 1.5s ease-in-out infinite alternate';
      }
      if (progressBar) progressBar.style.width = '100%';
      return;
    }

    const days = Math.floor(totalSecs / 86400);
    const hours = Math.floor((totalSecs % 86400) / 3600);
    const mins = Math.floor((totalSecs % 3600) / 60);
    const secs = Math.floor(totalSecs % 60);

    if (daysEl) daysEl.textContent = pad(days);
    if (hoursEl) hoursEl.textContent = pad(hours);
    if (minsEl) minsEl.textContent = pad(mins);
    if (secsEl) secsEl.textContent = pad(secs);

    var endMs = countdownEnd ? countdownEnd.getTime() : 0;
    var nowMs = Date.now();
    var totalDurationMs = 30 * 24 * 60 * 60 * 1000;
    var startMs = endMs - totalDurationMs;
    var elapsedMs = nowMs - startMs;
    var pct = totalDurationMs > 0 ? Math.min(100, Math.max(0, (elapsedMs / totalDurationMs) * 100)) : 0;
    if (progressBar) progressBar.style.width = pct + '%';

    requestAnimationFrame(function () {
      if (titleEl) {
        titleEl.style.transform = 'scale(1.02)';
        setTimeout(function () {
          if (titleEl) titleEl.style.transform = 'scale(1)';
        }, 150);
      }
    });
  }

  function createParticles() {
    if (!particlesEl) return;
    var count = 50;
    for (var i = 0; i < count; i++) {
      var span = document.createElement('span');
      span.style.left = Math.random() * 100 + '%';
      span.style.top = Math.random() * 100 + '%';
      span.style.animationDelay = Math.random() * 3 + 's';
      span.style.animationDuration = 2 + Math.random() * 2 + 's';
      particlesEl.appendChild(span);
    }
  }

  function init() {
    createParticles();
    updateCountdown();
    if (showSeconds && countdownEnd) {
      setInterval(updateCountdown, 1000);
    } else if (countdownEnd) {
      setInterval(updateCountdown, 60000);
    }
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
