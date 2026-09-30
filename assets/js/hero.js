// The three reels share the same source frames, edit points, fps and duration.
(() => {
  const hero = document.getElementById('home');
  const videos = [...hero.querySelectorAll('[data-hero-view]')];
  const buttons = [...hero.querySelectorAll('[data-view]')];
  const playback = document.getElementById('heroPlayback');
  const controls = hero.querySelector('.hero-media-controls');
  const status = document.getElementById('heroMediaStatus');
  const reducedMotion = matchMedia('(prefers-reduced-motion: reduce)');
  let active = videos.find(video => video.classList.contains('is-active')) || videos[0];
  let userPaused = reducedMotion.matches;
  let visible = true;
  let switching = false;
  let revision = 0;

  function updatePlayback() {
    const paused = switching ? userPaused : active.paused;
    playback.classList.toggle('is-paused', paused);
    playback.setAttribute('aria-label', paused ? 'Play background video' : 'Pause background video');
    playback.title = playback.getAttribute('aria-label');
  }

  function resume() {
    if (!userPaused && visible && !document.hidden && !switching) {
      loadVideo(active);
      active.play().catch(() => updatePlayback());
    } else {
      active.pause();
    }
    updatePlayback();
  }

  // Resolve only when the target has decoded the requested frame. Keep the
  // previous video visible while loading/seeking, so switching never flashes.
  function waitFor(video, event, ready) {
    if (video.error) return Promise.reject(new Error('Video unavailable'));
    if (ready()) return Promise.resolve();
    return new Promise((resolve, reject) => {
      const cleanup = () => {
        clearTimeout(timer);
        video.removeEventListener(event, done);
        video.removeEventListener('error', fail);
      };
      const done = () => { if (ready()) { cleanup(); resolve(); } };
      const fail = () => { cleanup(); reject(new Error('Video unavailable')); };
      const timer = setTimeout(fail, 15000);
      video.addEventListener(event, done);
      video.addEventListener('error', fail);
    });
  }

  async function selectView(view) {
    const target = videos.find(video => video.dataset.heroView === view);
    const request = ++revision;
    switching = true;
    controls.setAttribute('aria-busy', 'true');
    status.textContent = '';
    // Freeze the common timeline before seeking. Repeated clicks retain this
    // same position, and only the latest request may reveal or resume a video.
    videos.forEach(video => video.pause());
    const time = active.currentTime;
    try {
      loadVideo(target);
      await waitFor(target, 'loadeddata', () => target.readyState >= 2);
      if (request !== revision) return;
      if (Math.abs(target.currentTime - time) > 0.001) target.currentTime = time;
      await waitFor(target, 'seeked', () => !target.seeking && target.readyState >= 2);
      if (request !== revision) return;
      if (Math.abs(target.currentTime - time) > 0.01) throw new Error('Video seek failed');
      active = target;
      videos.forEach(video => video.classList.toggle('is-active', video === active));
      buttons.forEach(button => button.setAttribute('aria-pressed', String(button.dataset.view === view)));
    } catch {
      if (request === revision) status.textContent = 'Video unavailable. Please try again.';
    } finally {
      if (request === revision) {
        switching = false;
        controls.removeAttribute('aria-busy');
        resume();
      }
    }
  }

  buttons.forEach(button => button.addEventListener('click', () => selectView(button.dataset.view)));
  playback.addEventListener('click', () => {
    userPaused = switching ? !userPaused : !active.paused;
    resume();
  });
  videos.forEach(video => {
    video.muted = true;
    ['play', 'pause'].forEach(event => video.addEventListener(event, () => {
      if (video === active) updatePlayback();
    }));
  });
  new IntersectionObserver(entries => {
    visible = entries[0].isIntersecting;
    resume();
  }, { threshold: 0 }).observe(hero);
  document.addEventListener('visibilitychange', resume);
  reducedMotion.addEventListener('change', event => {
    userPaused = event.matches;
    resume();
  });
  resume();
})();
