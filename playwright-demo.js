/* ══════════════════════════════════════════════════
   PLAYWRIGHT INTERACTIVE DEMO
   Tích hợp: thêm vào cuối file app.js hoặc import riêng
══════════════════════════════════════════════════ */

(function () {
  'use strict';

  // ── HTML Modal ──────────────────────────────────
  const MODAL_HTML = `
<div id="pw-overlay">
  <div class="pw-modal">

    <div class="pw-modal-header">
      <div class="pw-dots">
        <span class="d1"></span><span class="d2"></span><span class="d3"></span>
      </div>
      <span class="pw-modal-title">PLAYWRIGHT TEST RUNNER — login.spec.ts</span>
      <span class="pw-version-badge">v1.40</span>
      <button class="pw-close-btn" onclick="PW.close()">✕</button>
    </div>

    <div class="pw-tabs">
      <div class="pw-tab active" onclick="PW.tab('code')">CODE</div>
      <div class="pw-tab" onclick="PW.tab('run')">▶ RUN</div>
      <div class="pw-tab" onclick="PW.tab('explain')">EXPLAIN</div>
    </div>

    <div class="pw-modal-body">

      <!-- CODE TAB -->
      <div id="pw-tab-code" class="pw-code-wrap">
        <button class="pw-copy-btn" onclick="PW.copy()">COPY</button>
        <div class="pw-code-block"><pre><span class="pw-cm">// login.spec.ts — E2E test: Login flow</span>
<span class="pw-kw">import</span> { <span class="pw-var">test</span>, <span class="pw-var">expect</span> } <span class="pw-kw">from</span> <span class="pw-str">'@playwright/test'</span>;

<span class="pw-var">test</span>.<span class="pw-fn">describe</span>(<span class="pw-str">'Login flow'</span>, () => {

  <span class="pw-var">test</span>(<span class="pw-str">'should login with valid credentials'</span>, <span class="pw-kw">async</span> ({ <span class="pw-var">page</span> }) => {

    <span class="pw-cm">// Step 1 — Navigate to login page</span>
    <span class="pw-kw">await</span> <span class="pw-var">page</span>.<span class="pw-fn">goto</span>(<span class="pw-str">'http://localhost:3000/login'</span>);

    <span class="pw-cm">// Step 2 — Fill email field</span>
    <span class="pw-kw">await</span> <span class="pw-var">page</span>.<span class="pw-fn">fill</span>(<span class="pw-str">'[data-testid="email"]'</span>, <span class="pw-str">'user@example.com'</span>);

    <span class="pw-cm">// Step 3 — Fill password field</span>
    <span class="pw-kw">await</span> <span class="pw-var">page</span>.<span class="pw-fn">fill</span>(<span class="pw-str">'[data-testid="password"]'</span>, <span class="pw-str">'SecurePass123'</span>);

    <span class="pw-cm">// Step 4 — Click login button</span>
    <span class="pw-kw">await</span> <span class="pw-var">page</span>.<span class="pw-fn">click</span>(<span class="pw-str">'[data-testid="login-btn"]'</span>);

    <span class="pw-cm">// Step 5 — Assert success message visible</span>
    <span class="pw-kw">await</span> <span class="pw-fn">expect</span>(<span class="pw-var">page</span>.<span class="pw-fn">locator</span>(<span class="pw-str">'[data-testid="success"]'</span>))
      .<span class="pw-fn">toBeVisible</span>();

  });

});</pre></div>
      </div>

      <!-- RUN TAB -->
      <div id="pw-tab-run" class="pw-run-wrap" style="display:none">
        <div class="pw-run-controls">
          <button class="pw-run-btn" id="pw-run-btn" onclick="PW.run()">▶ RUN TEST</button>
          <button class="pw-reset-btn" onclick="PW.reset()">↺ RESET</button>
          <span class="pw-status idle" id="pw-status">IDLE</span>
        </div>

        <div class="pw-browser">
          <div class="pw-browser-bar">
            <div class="pw-b-dots">
              <span class="bd1"></span><span class="bd2"></span><span class="bd3"></span>
            </div>
            <div class="pw-b-url" id="pw-url">about:blank</div>
          </div>
          <div class="pw-screen" id="pw-screen">
            <div class="pw-fake-form" id="pw-form">
              <input class="pw-fake-input" id="pw-email" placeholder="Email" readonly>
              <input class="pw-fake-input" id="pw-pass" placeholder="Password" type="password" readonly>
              <div class="pw-fake-btn" id="pw-btn">Login</div>
              <div class="pw-success-msg" id="pw-success">✓ Login successful!</div>
            </div>
            <div class="pw-highlight" id="pw-hl"></div>
          </div>
        </div>

        <div class="pw-log">
          <div class="pw-log-header">
            <span>TEST LOG</span>
            <span class="pw-log-sum" id="pw-log-sum"></span>
          </div>
          <div class="pw-log-entries" id="pw-log-entries"></div>
        </div>
      </div>

      <!-- EXPLAIN TAB -->
      <div id="pw-tab-explain" class="pw-explain-wrap" style="display:none">
        <div class="pw-explain-card">
          <h4>PLAYWRIGHT LÀ GÌ?</h4>
          <p>Framework E2E testing của Microsoft — tự động hóa Chrome, Firefox, Safari để kiểm tra toàn bộ user journey từ click đến API response.</p>
        </div>
        <div class="pw-explain-card">
          <h4>page.goto(url)</h4>
          <p>Điều hướng trình duyệt đến URL. Playwright chờ trang load hoàn toàn trước khi thực hiện bước tiếp theo.</p>
        </div>
        <div class="pw-explain-card">
          <h4>page.fill(selector, value)</h4>
          <p>Tìm element bằng <code>data-testid</code> và điền text. Ổn định hơn CSS class vì không bị ảnh hưởng khi redesign UI.</p>
        </div>
        <div class="pw-explain-card">
          <h4>page.click(selector)</h4>
          <p>Simulate click chuột. Playwright tự chờ element <code>visible</code> và <code>enabled</code> trước khi click — không cần <code>waitFor</code> thủ công.</p>
        </div>
        <div class="pw-explain-card">
          <h4>expect(...).toBeVisible()</h4>
          <p>Assert element phải xuất hiện trên màn hình. Nếu không xuất hiện trong timeout mặc định (5s) → test <code>FAIL</code> ngay lập tức.</p>
        </div>
        <div class="pw-explain-card">
          <h4>TẠI SAO DÙNG data-testid?</h4>
          <p>Selector theo <code>data-testid</code> không thay đổi khi redesign CSS hoặc đổi class. Test ổn định hơn và tách biệt hoàn toàn với implementation.</p>
        </div>
      </div>

    </div>
  </div>
</div>
`;

  // ── Steps config ────────────────────────────────
  const STEPS = [
    { name: 'Navigate to login page',      code: "page.goto('http://localhost:3000/login')",            time: '120ms', action: 'nav'    },
    { name: 'Fill email field',            code: 'page.fill(\'[data-testid="email"]\', "user@...")',    time: '45ms',  action: 'email'  },
    { name: 'Fill password field',         code: 'page.fill(\'[data-testid="password"]\', "••••")',     time: '38ms',  action: 'pass'   },
    { name: 'Click login button',          code: 'page.click(\'[data-testid="login-btn"]\')',           time: '62ms',  action: 'click'  },
    { name: 'Assert success message',      code: 'expect(locator(\'[data-testid="success"]\')).toBeVisible()', time: '89ms', action: 'assert' },
  ];

  const CODE_TEXT = `import { test, expect } from '@playwright/test';

test.describe('Login flow', () => {
  test('should login with valid credentials', async ({ page }) => {
    await page.goto('http://localhost:3000/login');
    await page.fill('[data-testid="email"]', 'user@example.com');
    await page.fill('[data-testid="password"]', 'SecurePass123');
    await page.click('[data-testid="login-btn"]');
    await expect(page.locator('[data-testid="success"]')).toBeVisible();
  });
});`;

  let _running = false;

  // ── Public API ──────────────────────────────────
  window.PW = {

    open() {
      document.getElementById('pw-overlay').classList.add('open');
      document.body.style.overflow = 'hidden';
    },

    close() {
      document.getElementById('pw-overlay').classList.remove('open');
      document.body.style.overflow = '';
    },

    tab(name) {
      ['code', 'run', 'explain'].forEach(t => {
        document.getElementById('pw-tab-' + t).style.display = t === name ? '' : 'none';
      });
      document.querySelectorAll('.pw-tab').forEach((el, i) => {
        el.classList.toggle('active', ['code', 'run', 'explain'][i] === name);
      });
    },

    copy() {
      navigator.clipboard.writeText(CODE_TEXT).catch(() => {});
      const btn = document.querySelector('.pw-copy-btn');
      btn.textContent = 'COPIED!';
      btn.classList.add('copied');
      setTimeout(() => { btn.textContent = 'COPY'; btn.classList.remove('copied'); }, 2000);
    },

    reset() {
      document.getElementById('pw-log-entries').innerHTML = '';
      document.getElementById('pw-log-sum').textContent = '';
      document.getElementById('pw-log-sum').className = 'pw-log-sum';
      document.getElementById('pw-hl').style.display = 'none';
      document.getElementById('pw-form').style.display = 'none';
      document.getElementById('pw-email').value = '';
      document.getElementById('pw-email').classList.remove('typing');
      document.getElementById('pw-pass').value = '';
      document.getElementById('pw-pass').classList.remove('typing');
      document.getElementById('pw-btn').classList.remove('clicked');
      document.getElementById('pw-success').classList.remove('show');
      document.getElementById('pw-url').textContent = 'about:blank';
      _setStatus('idle');
      _running = false;
      document.getElementById('pw-run-btn').disabled = false;
    },

    async run() {
      if (_running) return;
      _running = true;
      PW.reset();
      _running = true;
      document.getElementById('pw-run-btn').disabled = true;
      _setStatus('running');

      const sleep = ms => new Promise(r => setTimeout(r, ms));

      // Step 1 — Navigate
      _addLog(0, 'running');
      await sleep(400);
      document.getElementById('pw-url').textContent = 'localhost:3000/login';
      document.getElementById('pw-form').style.display = 'flex';
      _updateLog(0, 'pass');
      await sleep(280);

      // Step 2 — Email
      _addLog(1, 'running');
      const email = document.getElementById('pw-email');
      _highlight(email, 'data-testid="email"');
      email.classList.add('typing');
      let etxt = '';
      for (const c of 'user@example.com') { etxt += c; email.value = etxt; await sleep(38); }
      _updateLog(1, 'pass');
      await sleep(200);

      // Step 3 — Password
      _addLog(2, 'running');
      const pass = document.getElementById('pw-pass');
      _highlight(pass, 'data-testid="password"');
      pass.classList.add('typing');
      let ptxt = '';
      for (let i = 0; i < 13; i++) { ptxt += '•'; pass.value = ptxt; await sleep(32); }
      _updateLog(2, 'pass');
      await sleep(200);

      // Step 4 — Click
      _addLog(3, 'running');
      const btn = document.getElementById('pw-btn');
      _highlight(btn, 'data-testid="login-btn"');
      await sleep(320);
      btn.classList.add('clicked');
      _updateLog(3, 'pass');
      await sleep(380);

      // Step 5 — Assert
      _addLog(4, 'running');
      const suc = document.getElementById('pw-success');
      suc.classList.add('show');
      _highlight(suc, 'data-testid="success"');
      await sleep(480);
      _updateLog(4, 'pass');
      await sleep(200);

      document.getElementById('pw-hl').style.display = 'none';
      _setStatus('pass');
      const sum = document.getElementById('pw-log-sum');
      sum.className = 'pw-log-sum pass';
      sum.textContent = '5/5 PASSED · 354ms';
      _running = false;
      document.getElementById('pw-run-btn').disabled = false;
    },
  };

  // ── Helpers ─────────────────────────────────────
  function _setStatus(s) {
    const el = document.getElementById('pw-status');
    el.className = 'pw-status ' + s;
    el.textContent = s === 'idle' ? 'IDLE' : s === 'running' ? 'RUNNING...' : s === 'pass' ? '✓ PASSED' : '✗ FAILED';
  }

  function _addLog(idx, state) {
    const icons = { running: '●', pass: '✓', fail: '✗' };
    const div = document.createElement('div');
    div.className = 'pw-log-entry';
    div.id = 'pw-step-' + idx;
    div.innerHTML = `
      <div class="pw-log-icon ${state}">${icons[state] || ''}</div>
      <div class="pw-log-text">
        <span class="pw-log-name">${STEPS[idx].name}</span>
        <span class="pw-log-code">${STEPS[idx].code}</span>
      </div>
      <div class="pw-log-time"></div>
    `;
    document.getElementById('pw-log-entries').appendChild(div);
    requestAnimationFrame(() => div.classList.add('show'));
  }

  function _updateLog(idx, state) {
    const div = document.getElementById('pw-step-' + idx);
    if (!div) return;
    const icon = div.querySelector('.pw-log-icon');
    icon.className = 'pw-log-icon ' + state;
    icon.textContent = state === 'pass' ? '✓' : state === 'fail' ? '✗' : '●';
    if (state === 'pass') div.querySelector('.pw-log-time').textContent = STEPS[idx].time;
  }

  function _highlight(el, label) {
    const hl = document.getElementById('pw-hl');
    if (!el) { hl.style.display = 'none'; return; }
    const rect = el.getBoundingClientRect();
    const parent = document.getElementById('pw-screen').getBoundingClientRect();
    hl.style.display = 'block';
    hl.style.left   = (rect.left - parent.left - 2) + 'px';
    hl.style.top    = (rect.top  - parent.top  - 2) + 'px';
    hl.style.width  = (rect.width  + 4) + 'px';
    hl.style.height = (rect.height + 4) + 'px';
    hl.setAttribute('data-label', label);
  }

  // ── Init ────────────────────────────────────────
  function init() {
    // Inject modal HTML
    document.body.insertAdjacentHTML('beforeend', MODAL_HTML);

    // Close on overlay click
    document.getElementById('pw-overlay').addEventListener('click', function (e) {
      if (e.target === this) PW.close();
    });

    // ESC to close
    document.addEventListener('keydown', e => {
      if (e.key === 'Escape') PW.close();
    });

    // Playwright card attachment is handled by stage4-features.js
    // after the expandable tool DOM is built — no MutationObserver needed here.
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

})();
