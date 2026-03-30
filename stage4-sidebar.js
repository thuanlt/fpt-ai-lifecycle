/* ══════════════════════════════════════════════════
   STAGE 4 — SIDEBAR LAYOUT
   Hiện khi đã login, giống Checkly Documentation
══════════════════════════════════════════════════ */
(function () {
  'use strict';

  const LS_KEY = 'stage4-checklist';
  const CHECKLY_PING_URL = 'https://ping.checklyhq.com/9fa10154-3f8f-4c22-a817-ea82344390e9';

  const CHECKLIST_STEPS = [
    { id: 'write-tests',   label: 'Viết unit tests song song với code',         step: 'STEP 1' },
    { id: 'e2e-tests',     label: 'Tạo Playwright E2E tests cho happy paths',   step: 'STEP 1' },
    { id: 'unit-folder',   label: 'Cấu trúc tests/unit/ — test từng function',  step: 'STEP 2' },
    { id: 'integration',   label: 'Cấu trúc tests/integration/ — API + DB',     step: 'STEP 2' },
    { id: 'e2e-folder',    label: 'Cấu trúc tests/e2e/ — full user journeys',   step: 'STEP 2' },
    { id: 'checkly-setup', label: 'Config Checkly health checks trên API',      step: 'STEP 3' },
    { id: 'slack-alert',   label: 'Setup Slack alerts cho failures',            step: 'STEP 3' },
    { id: 'coverage-80',   label: 'Đạt test coverage > 80%',                   step: 'OUTPUT' },
  ];

  const TOOL_DATA = {
    'Playwright': {
      desc: 'Framework E2E testing mạnh nhất của Microsoft — hỗ trợ Chromium, Firefox, WebKit.',
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
      color: 'green',
    },
    'Checkly': {
      desc: 'Monitoring-as-code platform — định nghĩa API health checks bằng code, deploy cùng CI/CD.',
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
      color: 'orange',
    },
    'Axe / a11y': {
      desc: 'Axe-core là engine accessibility testing mạnh nhất — tích hợp vào Playwright để scan WCAG violations.',
      features: [
        'Detect 50+ loại accessibility issues tự động',
        'WCAG 2.0/2.1/2.2 AA/AAA compliance checks',
        'Tích hợp: axe-playwright, jest-axe, @axe-core/react',
        'Zero false positives — chỉ báo lỗi chắc chắn',
        'Chrome extension Deque axe DevTools',
      ],
      link: 'https://www.deque.com/axe/core-documentation',
      linkLabel: 'deque.com → axe Docs',
      pricing: 'axe-core: Open source · axe DevTools: Free tier',
      color: 'purple',
    },
    'Claude Code': {
      desc: 'AI coding agent chạy trong terminal — sinh test, fix bug tự động theo context thực tế.',
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
      color: 'blue',
    },
  };

  // ── Helpers ─────────────────────────────────────
  function loadChecklist() {
    try { return JSON.parse(localStorage.getItem(LS_KEY) || '{}'); } catch { return {}; }
  }
  function saveChecklist(s) {
    try { localStorage.setItem(LS_KEY, JSON.stringify(s)); } catch {}
  }
  function getUser() {
    try { return JSON.parse(sessionStorage.getItem('fpt_user') || 'null'); } catch { return null; }
  }
  function getUserInitials(user) {
    if (!user) return '?';
    const name = user.name || user.email || '';
    return name.split(' ').map(w => w[0]).join('').toUpperCase().slice(0, 2) || name[0]?.toUpperCase() || '?';
  }

  // ── Build Sidebar HTML ──────────────────────────
  function buildSidebar(user) {
    return `
      <aside class="s4-sidebar">
        <div class="s4-sidebar-logo">
          <div class="s4-sidebar-logo-title">QA &amp; Testing</div>
          <div class="s4-sidebar-logo-sub">Stage 4 — FPT AI Lifecycle</div>
        </div>
        <nav class="s4-nav-section">
          <div class="s4-nav-item active" onclick="S4Sidebar.nav('dashboard')" data-panel="dashboard">
            <span class="s4-nav-icon">📊</span> Dashboard
          </div>
          <div class="s4-nav-item" onclick="S4Sidebar.nav('progress')" data-panel="progress">
            <span class="s4-nav-icon">✅</span> My Progress
          </div>
          <div class="s4-nav-item" onclick="S4Sidebar.nav('tools')" data-panel="tools">
            <span class="s4-nav-icon">🛠️</span> My Tool
          </div>
          ${user.email === 'luuthithuan@gmail.com' ? `
          <div class="s4-nav-item s4-nav-item--private" onclick="S4Sidebar.nav('qcagent')" data-panel="qcagent">
            <span class="s4-nav-icon">🤖</span> QC Agent
          </div>` : ''}
          <div class="s4-nav-divider"></div>
          <div class="s4-nav-item" onclick="S4Sidebar.nav('document')" data-panel="document">
            <span class="s4-nav-icon">📄</span> Document
          </div>
        </nav>
        <div class="s4-sidebar-user">
          <div class="s4-sidebar-user-avatar">${getUserInitials(user)}</div>
          <div class="s4-sidebar-user-info">
            <div class="s4-sidebar-user-name">${user?.name || user?.email || 'User'}</div>
            <div class="s4-sidebar-user-role">QA Engineer</div>
          </div>
          <button class="s4-sidebar-logout" title="Logout" onclick="if(window.FPTAuth)FPTAuth.logout()">⏏</button>
        </div>
      </aside>`;
  }

  // ── Build Dashboard Panel ───────────────────────
  function buildDashboardPanel() {
    return `
      <div id="s4-panel-dashboard" class="s4-panel active">
        <div class="s4-page-header">
          <div class="s4-page-breadcrumb">
            <a onclick="goTo('home')">FPT AI Lifecycle</a> › Stage 4 › Dashboard
          </div>
          <div class="s4-page-title">Live Monitoring Dashboard</div>
          <div class="s4-page-desc">Xem trạng thái real-time của API health checks và heartbeat monitors.</div>
        </div>

        <div class="s4-dashboard-grid" id="s4-dash-stats">
          <div class="s4-dash-card">
            <div class="s4-dash-card-label">Heartbeat</div>
            <div class="s4-dash-card-value" id="s4-hb-status" style="font-size:1rem;margin-top:4px">Loading...</div>
          </div>
          <div class="s4-dash-card">
            <div class="s4-dash-card-label">Availability</div>
            <div class="s4-dash-card-value" id="s4-hb-avail">—</div>
          </div>
          <div class="s4-dash-card">
            <div class="s4-dash-card-label">Last Ping</div>
            <div class="s4-dash-card-value" id="s4-hb-last" style="font-size:0.9rem">—</div>
          </div>
        </div>

        <button class="s4-dash-open-btn" onclick="if(window.CKDash)CKDash.open()">
          📊 Open Checkly Live Dashboard
        </button>

        <div class="s4-dash-section-title">RECENT MONITORS</div>
        <div id="s4-monitor-list">
          ${[1,2,3].map(() => `
            <div class="s4-dash-monitor-row">
              <div class="s4-dash-monitor-dot loading"></div>
              <span class="s4-dash-monitor-name" style="color:#d1d5db">Loading...</span>
            </div>`).join('')}
        </div>
      </div>`;
  }

  // ── Build Progress Panel ────────────────────────
  function buildProgressPanel() {
    const state = loadChecklist();
    const done  = CHECKLIST_STEPS.filter(s => state[s.id]).length;
    const total = CHECKLIST_STEPS.length;
    const pct   = Math.round((done / total) * 100);

    const items = CHECKLIST_STEPS.map(s => `
      <div class="s4-check-row${state[s.id] ? ' done' : ''}" onclick="S4Sidebar.toggleCheck('${s.id}')" data-sid="${s.id}">
        <div class="s4-check-box">${state[s.id] ? '✓' : ''}</div>
        <span class="s4-check-label">${s.label}</span>
        <span class="s4-check-step-tag">${s.step}</span>
      </div>`).join('');

    return `
      <div id="s4-panel-progress" class="s4-panel">
        <div class="s4-page-header">
          <div class="s4-page-breadcrumb">
            <a onclick="goTo('home')">FPT AI Lifecycle</a> › Stage 4 › My Progress
          </div>
          <div class="s4-page-title">My Progress Checklist</div>
          <div class="s4-page-desc">Track tiến độ hoàn thành các bước trong Stage 4.</div>
        </div>
        <div class="s4-progress-header">
          <span class="s4-progress-title">Checklist</span>
          <span class="s4-progress-count" id="s4-prog-count">${done}/${total} completed</span>
        </div>
        <div class="s4-progress-bar-wrap">
          <div class="s4-progress-bar-fill" id="s4-prog-fill" style="width:${pct}%"></div>
        </div>
        ${items}
        <div class="s4-done-badge${done === total ? ' show' : ''}" id="s4-done-badge">
          🎉 Stage 4 hoàn thành! Sẵn sàng launch →
        </div>
      </div>`;
  }

  // ── Build Tools Panel ───────────────────────────
  function buildToolsPanel(stageData) {
    const tools = (stageData && stageData.tools) || Object.keys(TOOL_DATA).map(name => ({ name }));
    const items = tools.map(t => {
      const info = TOOL_DATA[t.name] || {};
      return `
        <div class="s4-tool-item" onclick="S4Sidebar.toggleTool(this)">
          <div class="s4-tool-item-header">
            <span class="s4-tool-chip ${info.color || t.color || 'blue'}">${t.name}</span>
            <span class="s4-tool-item-use">${t.use || info.desc?.slice(0, 60) + '...' || ''}</span>
            <span class="s4-tool-expand-icon">▼</span>
          </div>
          ${info.desc ? `
          <div class="s4-tool-item-body">
            <div class="s4-tool-item-desc">${info.desc}</div>
            <div class="s4-tool-feature-list">
              ${(info.features || []).map(f => `<div class="s4-tool-feature">${f}</div>`).join('')}
            </div>
            <div class="s4-tool-footer">
              ${info.link ? `<a class="s4-tool-link" href="${info.link}" target="_blank" rel="noopener" onclick="event.stopPropagation()">↗ ${info.linkLabel}</a>` : ''}
              ${info.pricing ? `<span class="s4-tool-pricing">${info.pricing}</span>` : ''}
            </div>
          </div>` : ''}
        </div>`;
    }).join('');

    return `
      <div id="s4-panel-tools" class="s4-panel">
        <div class="s4-page-header">
          <div class="s4-page-breadcrumb">
            <a onclick="goTo('home')">FPT AI Lifecycle</a> › Stage 4 › My Tool
          </div>
          <div class="s4-page-title">Tools for QA &amp; Testing</div>
          <div class="s4-page-desc">4 công cụ chính cho Stage 4 — click để xem chi tiết.</div>
        </div>
        <div class="s4-tool-list">${items}</div>
      </div>`;
  }

  // ── Build QC Agent Panel (private: luuthithuan@gmail.com only) ─
  function buildQCAgentPanel() {
    return `
      <div id="s4-panel-qcagent" class="s4-panel">
        <div class="s4-page-header">
          <div class="s4-page-breadcrumb">
            <a onclick="goTo('home')">FPT AI Lifecycle</a> › Stage 4 › QC Agent
          </div>
          <div class="s4-page-title">🤖 QC Agent</div>
          <div class="s4-page-desc">AI-powered QA agent — tự động hoá kiểm thử & phân tích lỗi.</div>
        </div>
        <div class="s4-tool-list">
          <div class="s4-tool-item expanded">
            <div class="s4-tool-item-header">
              <span class="s4-tool-chip green">qc-agent</span>
              <span class="s4-tool-item-use">Autonomous QA agent with MCP integrations</span>
            </div>
            <div class="s4-tool-item-body">
              <div class="s4-tool-item-desc">
                QC Agent sử dụng Claude AI + MCP servers (Playwright, Jira, filesystem) để tự động hoá toàn bộ quy trình QA:
                phân tích yêu cầu, sinh test case, chạy E2E test, báo cáo lỗi lên Jira.
              </div>
              <div class="s4-tool-feature-list">
                <div class="s4-tool-feature">✅ Tự động sinh & chạy Playwright test</div>
                <div class="s4-tool-feature">✅ Tích hợp Jira — tạo bug ticket tự động</div>
                <div class="s4-tool-feature">✅ Vector search với Qdrant</div>
                <div class="s4-tool-feature">✅ MCP: Playwright + bash + filesystem</div>
              </div>
              <div class="s4-tool-footer">
                <a class="s4-tool-link" href="https://github.com/thuanlt/fpt-ai-lifecycle/tree/master/qc-agent" target="_blank" rel="noopener" onclick="event.stopPropagation()">↗ View Source on GitHub</a>
                <span class="s4-tool-pricing">Private Access</span>
              </div>
            </div>
          </div>
          <div style="margin-top:1.5rem;padding:1rem;background:#1e1e2e;border-radius:8px;font-family:monospace;font-size:0.85rem;color:#cdd6f4;">
            <div style="color:#a6e3a1;margin-bottom:0.5rem"># Chạy QC Agent</div>
            <div>cd qc-agent</div>
            <div>pip install -r requirements.txt</div>
            <div>python src/main.py</div>
          </div>
        </div>
      </div>`;
  }

  // ── Build Document Panel ────────────────────────
  function buildDocumentPanel(stageData) {
    const d = stageData || {};
    const steps = (d.steps || []).map(s => `
      <div class="s4-step-card">
        <div class="s4-step-num">${s.step || '•'}</div>
        <div class="s4-step-body">
          <div class="s4-step-title">${s.icon || ''} ${s.title || ''}</div>
          <div class="s4-step-desc${s.code ? ' code-style' : ''}">${(s.desc || '').replace(/\n/g,'<br>')}</div>
        </div>
      </div>`).join('');

    const mistakes = (d.mistakes || []).map(m => `<li>${m}</li>`).join('');
    const outputs  = (d.output?.items || []).map(i => `<li>${i}</li>`).join('');

    return `
      <div id="s4-panel-document" class="s4-panel">
        <div class="s4-page-header">
          <div class="s4-page-breadcrumb">
            <a onclick="goTo('home')">FPT AI Lifecycle</a> › Stage 4 › Document
          </div>
          <div class="s4-page-title">Step-by-Step Playbook</div>
          <div class="s4-page-desc">Hướng dẫn từng bước triển khai QA &amp; Testing cho dự án AI.</div>
        </div>

        ${steps ? `
        <div class="s4-doc-section">
          <div class="s4-doc-section-title">📋 Steps</div>
          ${steps}
        </div>` : ''}

        ${mistakes ? `
        <div class="s4-doc-section">
          <div class="s4-doc-section-title">⚠️ Common Mistakes</div>
          <ul class="s4-mistake-list">${mistakes}</ul>
        </div>` : ''}

        ${outputs ? `
        <div class="s4-doc-section">
          <div class="s4-doc-section-title">📦 ${d.output?.label || 'Output'}</div>
          <ul class="s4-output-list">${outputs}</ul>
        </div>` : ''}
      </div>`;
  }

  // ── Load Dashboard Data ─────────────────────────
  async function loadDashboardData() {
    const CHECKLY_API_KEY = 'cu_f136970b18e34ef1bb8d497a2dd70bb1';
    const CHECKLY_ACCOUNT = '6f519222-f81d-43ab-bb93-18a75cf8bef1';

    try {
      const hbRes = await fetch('https://api.checklyhq.com/v1/heartbeats', {
        headers: {
          'Authorization': 'Bearer ' + CHECKLY_API_KEY,
          'X-Checkly-Account': CHECKLY_ACCOUNT,
        }
      });
      if (!hbRes.ok) throw new Error('HTTP ' + hbRes.status);
      const hbData = await hbRes.json();
      const hbs = Array.isArray(hbData) ? hbData : (hbData.results || []);
      const hb = hbs[0];

      if (hb) {
        const statusEl = document.getElementById('s4-hb-status');
        const availEl  = document.getElementById('s4-hb-avail');
        const lastEl   = document.getElementById('s4-hb-last');

        const isUp = !hb.hasFailures && hb.activated !== false;
        if (statusEl) {
          statusEl.textContent = isUp ? '● Healthy' : '● Down';
          statusEl.className = 's4-dash-card-value ' + (isUp ? 'green' : 'red');
          statusEl.style.fontSize = '1rem';
        }
        if (availEl) {
          availEl.textContent = hb.availability ? hb.availability.toFixed(1) + '%' : '—';
          availEl.className = 's4-dash-card-value ' + (parseFloat(hb.availability) >= 95 ? 'green' : 'red');
        }
        if (lastEl) {
          const lastPing = hb.lastPingAt || hb.updatedAt;
          if (lastPing) {
            const diff = Math.round((Date.now() - new Date(lastPing)) / 60000);
            lastEl.textContent = diff < 1 ? 'just now' : diff + 'm ago';
          }
          lastEl.className = 's4-dash-card-value';
          lastEl.style.fontSize = '0.9rem';
        }

        // Monitor list
        const list = document.getElementById('s4-monitor-list');
        if (list) {
          list.innerHTML = hbs.slice(0, 6).map(h => {
            const up = !h.hasFailures;
            return `
              <div class="s4-dash-monitor-row">
                <div class="s4-dash-monitor-dot ${up ? 'pass' : 'fail'}"></div>
                <span class="s4-dash-monitor-name">${h.name || 'Monitor'}</span>
                <span class="s4-dash-monitor-status ${up ? 'pass' : 'fail'}">${up ? 'UP' : 'DOWN'}</span>
              </div>`;
          }).join('');
        }
      }
    } catch (e) {
      console.warn('Checkly API:', e.message);
      const statusEl = document.getElementById('s4-hb-status');
      if (statusEl) { statusEl.textContent = 'API unavailable'; statusEl.style.fontSize = '0.8rem'; }
    }
  }

  // ── Render Sidebar Layout ───────────────────────
  function renderSidebarLayout(stageData) {
    const user = getUser();
    if (!user) return; // Chưa login → dùng layout gốc

    const pageStage = document.getElementById('page-stage');
    if (!pageStage) return;

    // Xóa layout sidebar cũ nếu có
    const old = document.getElementById('s4-docs-layout');
    if (old) old.remove();

    pageStage.classList.add('s4-sidebar-active');

    const layout = document.createElement('div');
    layout.id = 's4-docs-layout';
    layout.className = 's4-docs-layout';
    layout.innerHTML = `
      ${buildSidebar(user)}
      <main class="s4-docs-main">
        ${buildDashboardPanel()}
        ${buildProgressPanel()}
        ${buildToolsPanel(stageData)}
        ${user.email === 'luuthithuan@gmail.com' ? buildQCAgentPanel() : ''}
        ${buildDocumentPanel(stageData)}
      </main>
    `;

    pageStage.appendChild(layout);

    // Load real data
    loadDashboardData();
  }

  // ── Public API ──────────────────────────────────
  window.S4Sidebar = {
    nav(panel) {
      document.querySelectorAll('.s4-nav-item').forEach(el => {
        el.classList.toggle('active', el.dataset.panel === panel);
      });
      document.querySelectorAll('.s4-panel').forEach(el => {
        el.classList.toggle('active', el.id === 's4-panel-' + panel);
      });
    },

    toggleTool(item) {
      document.querySelectorAll('.s4-tool-item.expanded').forEach(el => {
        if (el !== item) el.classList.remove('expanded');
      });
      item.classList.toggle('expanded');
    },

    toggleCheck(id) {
      const state = loadChecklist();
      state[id] = !state[id];
      saveChecklist(state);

      const row = document.querySelector(`[data-sid="${id}"]`);
      if (row) {
        row.classList.toggle('done', !!state[id]);
        row.querySelector('.s4-check-box').textContent = state[id] ? '✓' : '';
      }
      const done  = CHECKLIST_STEPS.filter(s => state[s.id]).length;
      const total = CHECKLIST_STEPS.length;
      const pct   = Math.round((done / total) * 100);
      const fill  = document.getElementById('s4-prog-fill');
      const count = document.getElementById('s4-prog-count');
      const badge = document.getElementById('s4-done-badge');
      if (fill)  fill.style.width = pct + '%';
      if (count) count.textContent = done + '/' + total + ' completed';
      if (badge) badge.classList.toggle('show', done === total);
    },
  };

  // ── Hook vào renderStage ────────────────────────
  const _orig = window.renderStage;
  window.renderStage = function(d) {
    _orig(d);
    if (d.id === 'stage-4') {
      requestAnimationFrame(() => renderSidebarLayout(d));
    }
  };

  // Nếu đang ở stage-4 khi load
  document.addEventListener('DOMContentLoaded', () => {
    const hash = window.location.hash.replace('#', '');
    if (hash === 'stage-4') {
      const d = window.STAGES && window.STAGES['stage-4'];
      if (d) requestAnimationFrame(() => renderSidebarLayout(d));
    }
  });

  // Re-render khi login/logout thay đổi
  window.addEventListener('storage', () => {
    const hash = window.location.hash.replace('#', '');
    if (hash === 'stage-4') {
      const old = document.getElementById('s4-docs-layout');
      const pageStage = document.getElementById('page-stage');
      if (old) { old.remove(); pageStage?.classList.remove('s4-sidebar-active'); }
      const d = window.STAGES && window.STAGES['stage-4'];
      if (d) requestAnimationFrame(() => renderSidebarLayout(d));
    }
  });

})();
