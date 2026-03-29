// ── Routing ───────────────────────────────────────────────────────────────────
function goTo(target) {
  const homeEl  = document.getElementById('page-home');
  const stageEl = document.getElementById('page-stage');

  if (target === 'home') {
    stageEl.classList.remove('active');
    stageEl.classList.add('exit');
    setTimeout(() => {
      stageEl.classList.remove('exit');
      homeEl.classList.add('active');
    }, 320);
    window.scrollTo({ top: 0, behavior: 'smooth' });
    history.pushState({}, '', '#');
    return;
  }

  const data = STAGES[target];
  if (!data) return;

  renderStage(data);
  homeEl.classList.remove('active');
  stageEl.classList.add('active');
  window.scrollTo({ top: 0, behavior: 'instant' });
  history.pushState({}, '', '#' + target);
}

// Handle browser back/forward
window.addEventListener('popstate', () => {
  const hash = window.location.hash.replace('#', '');
  if (hash && STAGES[hash]) goTo(hash);
  else goTo('home');
});

// Handle initial URL hash
window.addEventListener('DOMContentLoaded', () => {
  const hash = window.location.hash.replace('#', '');
  if (hash && STAGES[hash]) goTo(hash);
});

// ── Render stage detail ───────────────────────────────────────────────────────
function renderStage(d) {
  const prevId = getPrev(d.id);
  const nextId = getNext(d.id);

  const html = `
    <div class="detail-header" style="--accent:${d.color}">
      <div class="detail-header-bg"></div>
      <div class="detail-num" style="color:${d.color}">${d.number}</div>
      <div class="detail-icons">${d.icons}</div>
      <div class="detail-phase-label" style="color:${d.color}">${d.label}</div>
      <h2 class="detail-title">${d.title}</h2>
      <div class="detail-weeks">${d.weeks}</div>
      <div class="detail-goal">
        <span class="goal-icon">🎯</span>
        <strong>Goal:</strong> ${d.goal}
      </div>
    </div>

    <div class="detail-body">

      <!-- Tools -->
      <section class="detail-section">
        <h3 class="section-heading" style="--accent:${d.color}">
          <span class="sh-icon">🛠️</span> Tools for This Stage
        </h3>
        <div class="tools-grid">
          ${d.tools.map(t => `
            <div class="tool-card">
              <span class="tool-badge ${t.color}">${t.name}</span>
              <span class="tool-use">${t.use}</span>
            </div>
          `).join('')}
        </div>
      </section>

      <!-- Steps -->
      <section class="detail-section">
        <h3 class="section-heading" style="--accent:${d.color}">
          <span class="sh-icon">📋</span> Step-by-Step Playbook
        </h3>
        <div class="steps-list">
          ${d.steps.map(s => `
            <div class="step-card">
              <div class="step-num" style="background:${d.color}">${s.step}</div>
              <div class="step-body">
                <div class="step-icon-title">
                  <span class="step-icon">${s.icon}</span>
                  <strong class="step-title">${s.title}</strong>
                </div>
                <div class="step-desc ${s.code ? 'code-style' : ''}">${s.desc.replace(/\n/g, '<br>')}</div>
                ${s.example ? `<div class="step-example">${s.example}</div>` : ''}
              </div>
            </div>
          `).join('')}
        </div>
      </section>

      <!-- Two-column: Mistakes + Output -->
      <div class="detail-two-col">
        <section class="detail-section">
          <h3 class="section-heading" style="--accent:${d.color}">
            <span class="sh-icon">⚠️</span> Common Mistakes to Avoid
          </h3>
          <ul class="mistake-list">
            ${d.mistakes.map(m => `<li>${m}</li>`).join('')}
          </ul>
        </section>

        <section class="detail-section output-section" style="border-color:${d.color}30">
          <h3 class="section-heading" style="--accent:${d.color}">
            <span class="sh-icon">📦</span> ${d.output.label}
          </h3>
          <ul class="output-list">
            ${d.output.items.map(i => `<li style="--accent:${d.color}"><span class="check" style="color:${d.color}">✓</span> ${i}</li>`).join('')}
          </ul>
        </section>
      </div>

      <!-- Stage nav -->
      <div class="stage-nav">
        ${prevId ? `
          <button class="snav-btn snav-prev" onclick="goTo('${prevId}')">
            ← ${STAGES[prevId].label}
          </button>
        ` : '<div></div>'}
        <button class="snav-btn snav-home" onclick="goTo('home')">⊞ Overview</button>
        ${nextId ? `
          <button class="snav-btn snav-next" onclick="goTo('${nextId}')">
            ${STAGES[nextId].label} →
          </button>
        ` : '<div></div>'}
      </div>

    </div>
  `;

  document.getElementById('stage-content').innerHTML = html;
}

function getPrev(id) {
  const ids = Object.keys(STAGES);
  const idx = ids.indexOf(id);
  return idx > 0 ? ids[idx - 1] : null;
}
function getNext(id) {
  const ids = Object.keys(STAGES);
  const idx = ids.indexOf(id);
  return idx < ids.length - 1 ? ids[idx + 1] : null;
}
