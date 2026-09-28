// Independent chapter and diagnostic tabs retain their selection when switching.
(() => {
  const section = document.getElementById('confidence-eval');
  section.querySelectorAll('[role="tablist"]').forEach(list => {
    const tabs = [...list.querySelectorAll(':scope > [role="tab"]')];
    function select(tab) {
      tabs.forEach(item => {
        const selected = item === tab;
        item.classList.toggle('active', selected);
        item.setAttribute('aria-selected', String(selected));
        item.tabIndex = selected ? 0 : -1;
        document.getElementById(item.getAttribute('aria-controls')).hidden = !selected;
      });
    }
    tabs.forEach((tab, index) => {
      tab.addEventListener('click', () => select(tab));
      tab.addEventListener('keydown', event => {
        const vertical = list.getAttribute('aria-orientation') === 'vertical';
        let next;
        if (event.key === 'ArrowRight' || (vertical && event.key === 'ArrowDown')) next = (index + 1) % tabs.length;
        if (event.key === 'ArrowLeft' || (vertical && event.key === 'ArrowUp')) next = (index + tabs.length - 1) % tabs.length;
        if (event.key === 'Home') next = 0;
        if (event.key === 'End') next = tabs.length - 1;
        if (next === undefined) return;
        event.preventDefault();
        select(tabs[next]);
        tabs[next].focus();
      });
    });
  });

  const button = document.getElementById('relSpace');
  const image = document.getElementById('relImage');
  const caption = document.getElementById('relCaption');
  const descriptions = {
    latent: 'These plots compare predicted confidence with how often predictions are actually correct. Looser error cutoffs bring the curves closer to the diagonal, but the probe remains overconfident near the main latent-space operating point.',
    pixel: 'Predicted confidence is compared with observed correctness using pixel errors. The curves approach the diagonal as the error cutoff becomes looser; this apparent improvement depends on the chosen correctness threshold.'
  };
  let space = 'latent';
  button.addEventListener('click', () => {
    space = space === 'latent' ? 'pixel' : 'latent';
    const source = `assets/confidence_eval/reliability_sweep_${space}.webp`;
    image.src = source;
    image.alt = `Reliability across thresholds · ${space}`;
    image.closest('a').href = source;
    caption.querySelector('strong').textContent = image.alt;
    caption.querySelector('span').textContent = descriptions[space];
    button.textContent = space === 'latent' ? 'Latent ⇄ Pixel' : 'Pixel ⇄ Latent';
    button.classList.toggle('active-space', space === 'pixel');
  });
})();
