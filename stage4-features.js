/* ══════════════════════════════════════════════════
   STAGE 4 FEATURES
   - Progress checklist với localStorage
   - Copy code button
   - Expandable tool detail
══════════════════════════════════════════════════ */

(function () {
  'use strict';

  const LS_KEY = 'stage4-checklist';

  // ── Tool data: description, features, link, pricing ──
  const TOOL_DATA = {
    'Playwright': {
      desc: 'Framework E2E testing mạnh nhất hiện tại của Microsoft — hỗ trợ Chromium, Firefox, WebKit. Chạy test song song, headless hoặc có UI.',
      features: [
        'Auto-wait: tự chờ element ready, không cần sleep()',
        'Multi-browser: Chrome, Firefox, Safari cùng 1 test',
        'Codegen: record actions → tự sinh code test',
        'Trace Viewer: replay lại toàn bộ test dưới dạng video',
        'API testing: test REST API không cần browser',
      ],
      link: 'https://playwright.dev',
      linkLabel: 'playwright.dev → Docs',
      pricing: 'Open source · MIT License · Free',
    },
    'Checkly': {
      desc: 'Monitoring-as-code platform — định nghĩa API health checks và browser checks bằng code, deploy cùng CI/CD pipeline.',
      features: [
        'Playwright-based browser checks trên 20+ locations',
        'API monitors với assertions chi tiết',
        'Alert qua Slack, PagerDuty, email khi fail',
        'Checkly CLI: quản lý monitors bằng code (GitOps)',
        'Dashboard realtime uptime & response time',
      ],
      link: 'https://www.checklyhq.com/docs',
      linkLabel: 'checklyhq.com → Docs',
      pricing: 'Free tier · Paid từ $20/tháng',
    },
    'Axe / a11y': {
      desc: 'Axe-core là engine accessibility testing mạnh nhất — tích hợp vào Playwright, Jest, Cypress để tự động scan WCAG violations.',
      features: [
        'Detect 50+ loại accessibility issues tự động',
        'WCAG 2.0/2.1/2.2 AA/AAA compliance checks',
        'Tích hợp: axe-playwright, jest-axe, @axe-core/react',
        'Zero false positives — chỉ báo lỗi chắc chắn',
        'Deque axe DevTools Chrome extension',
      ],
      link: 'https://www.deque.com/axe/core-documentation',
      linkLabel: 'deque.com → axe Docs',
      pricing: 'axe-core: Open source · axe DevTools: Free tier',
    },
    'Claude Code': {
      desc: 'AI coding agent chạy trong terminal — đọc toàn bộ codebase, sinh unit test, integration test, fix bug tự động theo context thực tế.',
      features: [
        'Sinh test cases từ function signature + implementation',
        'Tự detect edge cases và error scenarios',
        'Fix failing tests với context đầy đủ của codebase',
        'Suggest mock strategies cho external dependencies',
        'Review test coverage và đề xuất bổ sung',
      ],
      link: 'https://docs.anthropic.com/en/docs/claude-code',
      linkLabel: 'docs.anthropic.com → Claude Code',
      pricing: 'Yêu cầu Anthropic API credits',
    },
  };

  // ── Checklist steps ──
  const CHECKLIST_STEPS = [
    { id: 'write-tests',    label: 'Viết unit tests song song với code',          step: 'STEP 1' },
    { id: 'e2e-tests',      label: 'Tạo Playwright E2E tests cho happy paths',    step: 'STEP 1' },
    { id: 'unit-folder',    label: 'Cấu trúc tests/unit/ — test từng function',   step: 'STEP 2' },
    { id: 'integration',    label: 'Cấu trúc tests/integration/ — API + DB',      step: 'STEP 2' },
    { id: 'e2e-folder',     label: 'Cấu trúc tests/e2e/ — full user journeys',    step: 'STEP 2' },
    { id: 'checkly-setup',  label: 'Config Checkly health checks trên API',       step: 'STEP 3' },
    { id: 'slack-alert',    label: 'Setup Slack alerts cho failures',             step: 'STEP 3' },
    { id: 'coverage-80',    label: 'Đạt test coverage > 80%',                     step: 'OUTPUT' },
  ];

  // ── Load / Save localStorage ──
  function loadState() {
    try { return JSON.parse(localStorage.getItem(LS_KEY) || '{}'); }
    catch { return {}; }
  }
  function saveState(state) {
    try { localStorage.setItem(LS_KEY, JSON.stringify(state)); }
    catch {}
  }

  // ── Render checklist HTML ──
  function buildChecklistHTML() {
    const state = loadState();
    const done  = CHECKLIST_STEPS.filter(s => state[s.id]).length;
    const total = CHECKLIST_STEPS.length;
    const pct   = Math.round((done / total) * 100);

    const items = CHECKLIST_STEPS.map(s => {
      const isDone = !!state[s.id];
      return `
        <div class="s4-check-item${isDone ? ' done' : ''}"
             onclick="S4.toggleCheck('${s.id}')"
             data-id="${s.id}">
          <div class="s4-checkbox">${isDone ? '✓' : ''}</div>
          <span class="s4-check-label">${s.label}</span>
          <span class="s4-check-step">${s.step}</span>
        </div>`;
    }).join('');

    return `
      <div class="s4-checklist-bar" id="s4-checklist">
        <div class="s4-checklist-header">
          <div class="s4-checklist-title">My Progress Checklist</div>
          <div class="s4-progress-wrap">
            <div class="s4-progress-track">
              <div class="s4-progress-fill" id="s4-progress-fill" style="width:${pct}%"></div>
            </div>
            <span class="s4-progress-text" id="s4-progress-text">${done}/${total}</span>
          </div>
          <button class="s4-clear-btn" onclick="S4.clearAll(event)">RESET</button>
        </div>
        <div class="s4-checklist-items" id="s4-checklist-items">${items}</div>
        <div class="s4-completed-badge${done === total ? ' show' : ''}" id="s4-completed-badge">
          🎉 Stage 4 hoàn thành! Sẵn sàng launch →
        </div>
      </div>`;
  }

  // ── Render tools grid với expandable ──
  function buildToolsHTML(tools, accent) {
    return `
      <div class="tools-grid">
        ${tools.map(t => {
          const info = TOOL_DATA[t.name] || {};
          return `
            <div class="s4-tool-card" onclick="S4.toggleTool(this)" data-tool="${t.name}">
              <div class="s4-tool-top">
                <div class="s4-tool-row">
                  <span class="tool-badge ${t.color}">${t.name}</span>
                  <span class="s4-expand-icon">▼ INFO</span>
                </div>
                <span class="s4-tool-use">${t.use}</span>
              </div>
              ${info.desc ? `
              <div class="s4-tool-detail">
                <div class="s4-tool-detail-inner">
                  <p class="s4-tool-desc">${info.desc}</p>
                  <div class="s4-tool-features">
                    ${(info.features || []).map(f => `<div class="s4-tool-feature">${f}</div>`).join('')}
                  </div>
                  <div style="display:flex;align-items:center;gap:12px;flex-wrap:wrap">
                    ${info.link ? `<a class="s4-tool-link" href="${info.link}" target="_blank" rel="noopener" onclick="event.stopPropagation()"><span class="s4-tool-link-icon">↗</span>${info.linkLabel}</a>` : ''}
                    ${info.pricing ? `<span class="s4-tool-pricing">${info.pricing}</span>` : ''}
                  </div>
                </div>
              </div>` : ''}
            </div>`;
        }).join('')}
      </div>`;
  }

  // ── Add copy button to code blocks ──
  function addCopyButtons() {
    document.querySelectorAll('.step-desc.code-style').forEach((el, idx) => {
      if (el.querySelector('.s4-copy-btn')) return; // already added
      const wrap = document.createElement('div');
      wrap.className = 's4-code-wrap';
      el.parentNode.insertBefore(wrap, el);
      wrap.appendChild(el);

      const btn = document.createElement('button');
      btn.className = 's4-copy-btn';
      btn.innerHTML = '<span class="s4-copy-icon">⎘</span> COPY';
      btn.onclick = (e) => {
        e.stopPropagation();
        const text = el.innerText.replace(/^COPY$/m, '').trim();
        navigator.clipboard.writeText(text).catch(() => {});
        btn.innerHTML = '<span class="s4-copy-icon">✓</span> COPIED';
        btn.classList.add('copied');
        setTimeout(() => {
          btn.innerHTML = '<span class="s4-copy-icon">⎘</span> COPY';
          btn.classList.remove('copied');
        }, 2000);
      };
      wrap.appendChild(btn);
    });
  }

  // ── Public API ──
  window.S4 = {

    toggleCheck(id) {
      const state = loadState();
      state[id] = !state[id];
      saveState(state);

      // Update UI without full re-render
      const item = document.querySelector(`[data-id="${id}"]`);
      if (!item) return;
      const isDone = state[id];
      item.classList.toggle('done', isDone);
      item.querySelector('.s4-checkbox').textContent = isDone ? '✓' : '';

      // Update progress
      const done  = CHECKLIST_STEPS.filter(s => state[s.id]).length;
      const total = CHECKLIST_STEPS.length;
      const pct   = Math.round((done / total) * 100);
      const fill  = document.getElementById('s4-progress-fill');
      const txt   = document.getElementById('s4-progress-text');
      const badge = document.getElementById('s4-completed-badge');
      if (fill) fill.style.width = pct + '%';
      if (txt)  txt.textContent  = done + '/' + total;
      if (badge) badge.classList.toggle('show', done === total);
    },

    clearAll(e) {
      e.stopPropagation();
      saveState({});
      // Re-render checklist section only
      const el = document.getElementById('s4-checklist');
      if (el) el.outerHTML = buildChecklistHTML();
      // Re-attach since outerHTML replaces element
      setTimeout(() => {
        const fresh = document.getElementById('s4-checklist');
        if (fresh) fresh.outerHTML = buildChecklistHTML();
      }, 0);
      location.reload(); // simplest way to re-render
    },

    toggleTool(card) {
      // Close others
      document.querySelectorAll('.s4-tool-card.expanded').forEach(c => {
        if (c !== card) c.classList.remove('expanded');
      });
      card.classList.toggle('expanded');
    },
  };

  // ── Hook into renderStage ──
  function patchStage4(data) {
    if (data.id !== 'stage-4') return;

    requestAnimationFrame(() => {
      const content = document.getElementById('stage-content');
      if (!content) return;

      // 1. Inject checklist before detail-body
      const detailBody = content.querySelector('.detail-body');
      if (detailBody && !content.querySelector('#s4-checklist')) {
        detailBody.insertAdjacentHTML('afterbegin', buildChecklistHTML());
      }

      // 2. Replace tools-grid with expandable version
      const toolsSection = content.querySelector('.tools-grid');
      if (toolsSection && data.tools) {
        toolsSection.outerHTML = buildToolsHTML(data.tools, data.color);
      }

      // 3. Add copy buttons to code blocks
      addCopyButtons();

      // 4. Re-attach demo modals after DOM rebuild
      if (window.CKDash_attachCard) CKDash_attachCard();
      requestAnimationFrame(() => {
        document.querySelectorAll('.s4-tool-card').forEach(card => {
          // Playwright demo
          if (card.textContent.includes('Playwright') && !card.dataset.pwAttached) {
            card.dataset.pwAttached = '1';
            card.addEventListener('click', function(e) {
              if (!e.target.closest('.s4-tool-detail') && window.PW) {
                window.PW.open();
              }
            });
          }
          // Checkly demo + Dashboard
          if (card.textContent.includes('Checkly') && !card.dataset.ckAttached) {
            card.dataset.ckAttached = '1';
            card.addEventListener('click', function(e) {
              if (!e.target.closest('.s4-tool-detail') && window.CKDemo) {
                window.CKDemo.open();
              }
            });
          }
          // Axe / a11y demo
          if (card.textContent.includes('Axe') && !card.dataset.axeAttached) {
            card.dataset.axeAttached = '1';
            card.addEventListener('click', function(e) {
              if (!e.target.closest('.s4-tool-detail') && window.AXEDemo) {
                window.AXEDemo.open();
              }
            });
          }
          // Claude Code demo
          if (card.textContent.includes('Claude Code') && !card.dataset.ccAttached) {
            card.dataset.ccAttached = '1';
            card.addEventListener('click', function(e) {
              if (!e.target.closest('.s4-tool-detail') && window.CCDemo) {
                window.CCDemo.open();
              }
            });
          }
        });
      });
    });
  }

  // ── Override renderStage ──
  const _originalRender = window.renderStage;
  window.renderStage = function (d) {
    _originalRender(d);
    patchStage4(d);
  };

  // ── Handle if stage-4 is already active (URL hash) ──
  document.addEventListener('DOMContentLoaded', () => {
    const hash = window.location.hash.replace('#', '');
    if (hash === 'stage-4') {
      const d = window.STAGES && window.STAGES['stage-4'];
      if (d) patchStage4(d);
    }
  });

})();
