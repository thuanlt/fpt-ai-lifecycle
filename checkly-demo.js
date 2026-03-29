/* ══════════════════════════════════════════════════
   CHECKLY INTERACTIVE DEMO
   Click card Checkly → mở modal API health monitor
══════════════════════════════════════════════════ */

(function () {
  'use strict';

  // ── Scenarios ──────────────────────────────────
  const SCENARIOS = {
    ok:      { status: 200, latency: 142,   body: '{"status":"ok","uptime":99.98,"version":"2.1.0","timestamp":"2026-03-28T10:00:00Z"}' },
    slow:    { status: 200, latency: 3840,  body: '{"status":"ok","uptime":99.94,"version":"2.1.0"}' },
    '500':   { status: 500, latency: 210,   body: '{"error":"Internal Server Error","code":500,"message":"Database connection failed"}' },
    '404':   { status: 404, latency: 88,    body: '{"error":"Not Found","code":404,"message":"Endpoint does not exist"}' },
    timeout: { status: null, latency: 30000, body: '' },
  };

  const PRESET_URLS = {
    ok:      'https://api.example.com/health',
    slow:    'https://api.example.com/health',
    '500':   'https://api.example.com/users',
    '404':   'https://api.example.com/unknown',
    timeout: 'https://api.example.com/heavy-query',
  };

  // ── Modal HTML ─────────────────────────────────
  const MODAL_HTML = `
<div id="ck-overlay">
  <div class="ck-modal">

    <div class="ck-modal-header">
      <div class="ck-dots">
        <span class="d1"></span><span class="d2"></span><span class="d3"></span>
      </div>
      <span class="ck-modal-title">CHECKLY — API HEALTH MONITOR SIMULATOR</span>
      <span class="ck-version-badge">LIVE</span>
      <button class="ck-close-btn" onclick="CKDemo.close()">✕</button>
    </div>

    <div class="ck-tabs">
      <div class="ck-tab active" onclick="CKDemo.tab('monitor')">MONITOR</div>
      <div class="ck-tab" onclick="CKDemo.tab('explain')">EXPLAIN</div>
    </div>

    <div class="ck-modal-body">

      <!-- MONITOR TAB -->
      <div id="ck-tab-monitor" class="ck-monitor-wrap">

        <div>
          <div class="ck-section-label">ENDPOINT</div>
          <div class="ck-input-row">
            <select class="ck-method-select" id="ck-method">
              <option>GET</option><option>POST</option><option>PUT</option><option>DELETE</option>
            </select>
            <input class="ck-url-input" id="ck-url" value="https://api.example.com/health" placeholder="Enter API URL...">
            <button class="ck-run-btn" id="ck-run-btn" onclick="CKDemo.run()">▶ RUN CHECK</button>
          </div>
        </div>

        <div>
          <div class="ck-section-label">QUICK PRESETS</div>
          <div class="ck-presets">
            <span class="ck-preset active" data-preset="ok"    onclick="CKDemo.preset('ok',this)">✓ 200 OK (fast)</span>
            <span class="ck-preset"        data-preset="slow"  onclick="CKDemo.preset('slow',this)">⚠ 200 OK (slow)</span>
            <span class="ck-preset"        data-preset="500"   onclick="CKDemo.preset('500',this)">✗ 500 Server Error</span>
            <span class="ck-preset"        data-preset="404"   onclick="CKDemo.preset('404',this)">✗ 404 Not Found</span>
            <span class="ck-preset"        data-preset="timeout" onclick="CKDemo.preset('timeout',this)">✗ Timeout</span>
          </div>
        </div>

        <div>
          <div class="ck-section-label">ASSERTIONS</div>
          <div class="ck-assertions">
            <div class="ck-assert-row">
              <span class="ck-assert-label">Status code</span>
              <select class="ck-assert-select" id="a-status-op">
                <option>equals</option><option>not equals</option><option>less than</option>
              </select>
              <input class="ck-assert-input" id="a-status-val" value="200">
            </div>
            <div class="ck-assert-row">
              <span class="ck-assert-label">Response time</span>
              <select class="ck-assert-select" id="a-time-op">
                <option>less than</option><option>greater than</option>
              </select>
              <input class="ck-assert-input" id="a-time-val" value="2000">
              <span class="ck-assert-unit">ms</span>
            </div>
            <div class="ck-assert-row">
              <span class="ck-assert-label">Body contains</span>
              <select class="ck-assert-select" id="a-body-op">
                <option>contains</option><option>not contains</option><option>(skip)</option>
              </select>
              <input class="ck-assert-input" id="a-body-val" value="ok">
            </div>
          </div>
        </div>

        <div class="ck-result" id="ck-result">
          <div class="ck-result-header">
            <div class="ck-status-dot running" id="ck-dot"></div>
            <span class="ck-status-label running" id="ck-status-label">Running check...</span>
            <span class="ck-latency-tag" id="ck-latency-tag"></span>
          </div>
          <div class="ck-result-body">
            <div class="ck-metrics">
              <div class="ck-metric">
                <div class="ck-metric-val green" id="m-status">—</div>
                <div class="ck-metric-label">STATUS</div>
              </div>
              <div class="ck-metric">
                <div class="ck-metric-val blue" id="m-time">—</div>
                <div class="ck-metric-label">LATENCY</div>
              </div>
              <div class="ck-metric">
                <div class="ck-metric-val blue" id="m-size">—</div>
                <div class="ck-metric-label">SIZE</div>
              </div>
            </div>
            <div>
              <div class="ck-section-label">ASSERTION RESULTS</div>
              <div class="ck-checks" id="ck-checks"></div>
            </div>
            <div class="ck-resp-block">
              <div class="ck-resp-label">RESPONSE BODY</div>
              <div class="ck-resp-body" id="ck-resp-body">—</div>
            </div>
          </div>
        </div>

      </div>

      <!-- EXPLAIN TAB -->
      <div id="ck-tab-explain" class="ck-explain-wrap" style="display:none">
        <div class="ck-explain-card">
          <h4>CHECKLY LÀ GÌ?</h4>
          <p>Monitoring-as-code platform — định nghĩa API health checks và browser tests bằng code, deploy cùng CI/CD. Chạy monitors từ 20+ locations toàn cầu.</p>
        </div>
        <div class="ck-explain-card">
          <h4>API MONITOR HOẠT ĐỘNG NHƯ THẾ NÀO?</h4>
          <p>Checkly gửi HTTP request đến endpoint của bạn theo lịch (mỗi 1–10 phút), kiểm tra response theo <code>assertions</code> đã định nghĩa, và alert ngay khi có failure.</p>
        </div>
        <div class="ck-explain-card">
          <h4>ASSERTIONS</h4>
          <p>Mỗi check có thể có nhiều assertions: <code>statusCode equals 200</code>, <code>responseTime lessThan 2000</code>, <code>jsonBody.status equals "ok"</code>. Tất cả phải pass thì check mới PASS.</p>
        </div>
        <div class="ck-explain-card">
          <h4>ALERTING</h4>
          <p>Khi check fail, Checkly gửi alert qua <code>Slack</code>, <code>PagerDuty</code>, <code>email</code>, hoặc webhook. Có thể config re-try trước khi alert để tránh false positive.</p>
        </div>
        <div class="ck-explain-card">
          <h4>CHECKLY CLI (MONITORING-AS-CODE)</h4>
          <p>Define monitors bằng TypeScript/JavaScript, commit vào Git, deploy qua <code>npx checkly deploy</code>. Monitors sống cùng codebase — không cần UI để quản lý.</p>
        </div>
      </div>

    </div>
  </div>
</div>
`;

  // ── State ──────────────────────────────────────
  let _scenario = 'ok';
  let _running  = false;

  // ── Public API ─────────────────────────────────
  window.CKDemo = {

    open() {
      document.getElementById('ck-overlay').classList.add('open');
      document.body.style.overflow = 'hidden';
    },

    close() {
      document.getElementById('ck-overlay').classList.remove('open');
      document.body.style.overflow = '';
    },

    tab(name) {
      ['monitor', 'explain'].forEach(t => {
        document.getElementById('ck-tab-' + t).style.display = t === name ? '' : 'none';
      });
      document.querySelectorAll('.ck-tab').forEach((el, i) => {
        el.classList.toggle('active', ['monitor', 'explain'][i] === name);
      });
    },

    preset(s, el) {
      _scenario = s;
      document.getElementById('ck-url').value = PRESET_URLS[s] || 'https://api.example.com/health';
      document.querySelectorAll('.ck-preset').forEach(p => p.classList.remove('active'));
      el.classList.add('active');
    },

    async run() {
      if (_running) return;
      _running = true;
      document.getElementById('ck-run-btn').disabled = true;

      const sc        = SCENARIOS[_scenario] || SCENARIOS.ok;
      const statusVal = parseInt(document.getElementById('a-status-val').value) || 200;
      const timeVal   = parseInt(document.getElementById('a-time-val').value)   || 2000;
      const bodyVal   = document.getElementById('a-body-val').value || 'ok';
      const statusOp  = document.getElementById('a-status-op').value;
      const timeOp    = document.getElementById('a-time-op').value;
      const bodyOp    = document.getElementById('a-body-op').value;

      // Show result panel in loading state
      const resultEl = document.getElementById('ck-result');
      resultEl.classList.add('show');
      _setRunning();

      // Simulate network (cap visual delay at 1.8s)
      const visualDelay = Math.min(sc.latency, 1800);
      await new Promise(r => setTimeout(r, visualDelay));

      // ── Timeout ──
      if (_scenario === 'timeout') {
        _setResult(false, 'CHECK FAILED — Request timed out (>30s)', '>30,000ms');
        document.getElementById('m-status').textContent = 'TIMEOUT';
        document.getElementById('m-status').className   = 'ck-metric-val red';
        document.getElementById('m-time').textContent   = '>30s';
        document.getElementById('m-time').className     = 'ck-metric-val red';
        document.getElementById('m-size').textContent   = '0 B';
        document.getElementById('m-size').className     = 'ck-metric-val blue';
        document.getElementById('ck-resp-body').textContent = '(no response — connection timed out)';
        _renderChecks([
          { name: 'Status code ' + statusOp + ' ' + statusVal, pass: false, got: 'TIMEOUT' },
          { name: 'Response time ' + timeOp + ' ' + timeVal + 'ms', pass: false, got: '>30000ms' },
          { name: bodyOp === '(skip)' ? 'Body (skipped)' : 'Body ' + bodyOp + ' "' + bodyVal + '"', pass: false, got: '(no body)' },
        ]);
        _done();
        return;
      }

      // ── Evaluate assertions ──
      let statusPass;
      if      (statusOp === 'equals')     statusPass = sc.status === statusVal;
      else if (statusOp === 'not equals') statusPass = sc.status !== statusVal;
      else                                statusPass = sc.status < statusVal;

      const timePass = timeOp === 'less than' ? sc.latency < timeVal : sc.latency > timeVal;
      const bodyPass = bodyOp === '(skip)'      ? true
                     : bodyOp === 'contains'    ? sc.body.includes(bodyVal)
                     : !sc.body.includes(bodyVal);

      const allPass = statusPass && timePass && bodyPass;
      const isOk    = sc.status >= 200 && sc.status < 300;

      // Failed assertions list
      const failed = [
        !statusPass && 'status code',
        !timePass   && 'response time',
        !bodyPass   && 'body',
      ].filter(Boolean);

      _setResult(
        allPass,
        allPass
          ? 'CHECK PASSED — All assertions met'
          : 'CHECK FAILED — ' + failed.join(', ') + ' assertion failed',
        sc.latency + 'ms'
      );

      // Metrics
      const mStatus = document.getElementById('m-status');
      mStatus.textContent = sc.status;
      mStatus.className   = 'ck-metric-val ' + (isOk ? 'green' : 'red');

      const mTime = document.getElementById('m-time');
      mTime.textContent = sc.latency + 'ms';
      mTime.className   = 'ck-metric-val ' + (sc.latency < 500 ? 'green' : sc.latency < 2000 ? 'orange' : 'red');

      const mSize = document.getElementById('m-size');
      mSize.textContent = sc.body.length + ' B';
      mSize.className   = 'ck-metric-val blue';

      // Response body
      try {
        document.getElementById('ck-resp-body').textContent =
          JSON.stringify(JSON.parse(sc.body), null, 2);
      } catch {
        document.getElementById('ck-resp-body').textContent = sc.body || '(empty)';
      }

      // Assertions
      _renderChecks([
        { name: 'Status code ' + statusOp + ' ' + statusVal,     pass: statusPass, got: sc.status },
        { name: 'Response time ' + timeOp + ' ' + timeVal + 'ms', pass: timePass,  got: sc.latency + 'ms' },
        {
          name: bodyOp === '(skip)' ? 'Body check (skipped)' : 'Body ' + bodyOp + ' "' + bodyVal + '"',
          pass: bodyPass,
          got: bodyOp === '(skip)' ? 'skipped' : bodyPass ? 'matched' : 'no match',
        },
      ]);

      _done();
    },
  };

  // ── Helpers ────────────────────────────────────
  function _setRunning() {
    document.getElementById('ck-dot').className         = 'ck-status-dot running';
    document.getElementById('ck-status-label').className = 'ck-status-label running';
    document.getElementById('ck-status-label').textContent = 'Running check...';
    document.getElementById('ck-latency-tag').textContent  = '';
    document.getElementById('m-status').textContent = '—';
    document.getElementById('m-time').textContent   = '—';
    document.getElementById('m-size').textContent   = '—';
    document.getElementById('ck-resp-body').textContent = '—';
    document.getElementById('ck-checks').innerHTML  = '';
  }

  function _setResult(pass, label, latency) {
    const state = pass ? 'pass' : 'fail';
    document.getElementById('ck-dot').className          = 'ck-status-dot ' + state;
    document.getElementById('ck-status-label').className  = 'ck-status-label ' + state;
    document.getElementById('ck-status-label').textContent = label;
    document.getElementById('ck-latency-tag').textContent  = latency;
  }

  function _renderChecks(checks) {
    document.getElementById('ck-checks').innerHTML = checks.map(c => `
      <div class="ck-check-row">
        <div class="ck-check-icon ${c.pass ? 'pass' : 'fail'}">${c.pass ? '✓' : '✗'}</div>
        <span class="ck-check-name">${c.name}</span>
        <span class="ck-check-got ${c.pass ? 'pass' : 'fail'}">${c.got}</span>
      </div>`).join('');
  }

  function _done() {
    _running = false;
    document.getElementById('ck-run-btn').disabled = false;
  }

  // ── Init ───────────────────────────────────────
  function init() {
    document.body.insertAdjacentHTML('beforeend', MODAL_HTML);

    // Close on overlay backdrop click
    document.getElementById('ck-overlay').addEventListener('click', function (e) {
      if (e.target === this) CKDemo.close();
    });

    // ESC to close
    document.addEventListener('keydown', e => {
      if (e.key === 'Escape') CKDemo.close();
    });
  }

  // ── Attach to Checkly card (called by stage4-features.js) ──
  window.CKDemo_attach = function () {
    document.querySelectorAll('.s4-tool-card').forEach(card => {
      if (card.textContent.includes('Checkly') && !card.dataset.ckAttached) {
        card.dataset.ckAttached = '1';
        card.addEventListener('click', function (e) {
          if (!e.target.closest('.s4-tool-detail') && window.CKDemo) {
            CKDemo.open();
          }
        });
      }
    });
  };

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

})();
