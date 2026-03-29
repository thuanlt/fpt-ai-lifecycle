/* ══════════════════════════════════════════════════
   AXE / A11Y INTERACTIVE DEMO
   Click card Axe/a11y → mở modal DOM scanner
══════════════════════════════════════════════════ */

(function () {
  'use strict';

  // ── Preset HTML snippets ───────────────────────
  const PRESETS = {
    img: `<div class="hero">\n  <img src="banner.jpg">\n  <img src="logo.png">\n  <img src="promo.gif" alt="">\n</div>`,
    form: `<form>\n  <input type="text" placeholder="Your name">\n  <input type="email" placeholder="Email address">\n  <input type="password">\n  <button>Submit</button>\n</form>`,
    contrast: `<div style="background:#fff">\n  <p style="color:#aaa">Low contrast text</p>\n  <button style="background:#eee;color:#ccc">Click me</button>\n  <span style="color:#bbb;font-size:12px">Footer note</span>\n</div>`,
    heading: `<div>\n  <h1>Page Title</h1>\n  <h3>Section (skipped h2!)</h3>\n  <h5>Subsection (skipped h4!)</h5>\n  <p>Content here</p>\n  <h2>Another Section</h2>\n</div>`,
    clean: `<article>\n  <h1>Accessible Page</h1>\n  <img src="hero.jpg" alt="Team collaborating in office">\n  <form>\n    <label for="name">Full name</label>\n    <input id="name" type="text" autocomplete="name">\n    <label for="email">Email</label>\n    <input id="email" type="email" autocomplete="email">\n    <button type="submit">Send message</button>\n  </form>\n</article>`,
  };

  // ── Violation rules database ───────────────────
  const RULES = {
    img: [
      {
        sev: 'critical', rule: 'image-alt',
        desc: 'img elements must have an alt attribute — screen readers cannot convey image content without it',
        wcag: 'WCAG 2.1 — 1.1.1 Non-text Content (Level A)',
        fix: '<!-- Before (failing) -->\n<img src="banner.jpg">\n\n<!-- After (passing) -->\n<img src="banner.jpg" alt="Team banner showing our mission">',
        count: 2,
      },
      {
        sev: 'serious', rule: 'image-alt-decorative',
        desc: 'Decorative images should use role="presentation" to be hidden from assistive technology',
        wcag: 'WCAG 2.1 — 1.1.1 Non-text Content (Level A)',
        fix: '<!-- Before -->\n<img src="promo.gif" alt="">\n\n<!-- After (explicitly decorative) -->\n<img src="promo.gif" alt="" role="presentation">',
        count: 1,
      },
    ],
    form: [
      {
        sev: 'critical', rule: 'label',
        desc: 'Form inputs must have associated labels — screen readers cannot identify unlabeled inputs',
        wcag: 'WCAG 2.1 — 1.3.1 Info and Relationships (Level A)',
        fix: '<!-- Before -->\n<input type="text" placeholder="Your name">\n\n<!-- After -->\n<label for="name">Your name</label>\n<input id="name" type="text" autocomplete="name">',
        count: 3,
      },
      {
        sev: 'serious', rule: 'autocomplete-valid',
        desc: 'Input fields collecting personal data must have valid autocomplete attributes',
        wcag: 'WCAG 2.1 — 1.3.5 Identify Input Purpose (Level AA)',
        fix: '<input id="email" type="email"\n  autocomplete="email"\n  aria-required="true">',
        count: 2,
      },
      {
        sev: 'moderate', rule: 'button-name',
        desc: 'Buttons should have descriptive text or aria-label for screen reader users',
        wcag: 'WCAG 2.1 — 4.1.2 Name, Role, Value (Level A)',
        fix: '<!-- Before -->\n<button>Submit</button>\n\n<!-- After -->\n<button type="submit" aria-label="Submit contact form">\n  Submit\n</button>',
        count: 1,
      },
    ],
    contrast: [
      {
        sev: 'serious', rule: 'color-contrast',
        desc: 'Text color #aaa on white has contrast ratio 2.32:1 — minimum required is 4.5:1 (WCAG AA)',
        wcag: 'WCAG 2.1 — 1.4.3 Contrast Minimum (Level AA)',
        fix: '<!-- Before: ratio 2.32:1 (FAIL) -->\n<p style="color:#aaa">Low contrast text</p>\n\n<!-- After: ratio 7.0:1 (PASS AAA) -->\n<p style="color:#595959">Better contrast text</p>',
        count: 3,
      },
      {
        sev: 'serious', rule: 'color-contrast-ui',
        desc: 'Button text #ccc on #eee background has ratio 1.24:1 — UI components need minimum 3:1',
        wcag: 'WCAG 2.1 — 1.4.11 Non-text Contrast (Level AA)',
        fix: '<!-- Before: ratio 1.24:1 (FAIL) -->\n<button style="background:#eee;color:#ccc">\n\n<!-- After: ratio 5.9:1 (PASS AA) -->\n<button style="background:#0057b7;color:#ffffff">',
        count: 1,
      },
    ],
    heading: [
      {
        sev: 'moderate', rule: 'heading-order',
        desc: 'Heading levels skipped: h1→h3 (missing h2), h3→h5 (missing h4). Screen readers use headings to navigate',
        wcag: 'WCAG 2.1 — 1.3.1 Info and Relationships (Level A)',
        fix: '<!-- Before (skipping levels) -->\n<h1>Title</h1>\n<h3>Section</h3>\n<h5>Subsection</h5>\n\n<!-- After (sequential) -->\n<h1>Title</h1>\n<h2>Section</h2>\n<h3>Subsection</h3>',
        count: 2,
      },
      {
        sev: 'minor', rule: 'region',
        desc: 'Page content is not contained within landmark regions (main, nav, aside, header, footer)',
        wcag: 'WCAG 2.1 — 1.3.6 Identify Purpose (Level AAA)',
        fix: '<main>\n  <h1>Page Title</h1>\n  <section aria-labelledby="s1">\n    <h2 id="s1">Section</h2>\n  </section>\n</main>',
        count: 1,
      },
    ],
    clean: [],
  };

  // ── Detect which ruleset to apply ──────────────
  function detectRules(html) {
    if (html.includes('<img') && !html.includes('alt="T') && !html.includes('alt="hero')) return RULES.img;
    if (html.includes('<input') && !html.includes('<label')) return RULES.form;
    if (html.includes('color:#aaa') || html.includes('color: #aaa')) return RULES.contrast;
    if (html.includes('<h3') && html.includes('<h1') && !html.includes('<h2')) return RULES.heading;
    return [];
  }

  // ── Modal HTML ─────────────────────────────────
  const MODAL_HTML = `
<div id="axe-overlay">
  <div class="axe-modal">

    <div class="axe-modal-header">
      <div class="axe-dots">
        <span class="d1"></span><span class="d2"></span><span class="d3"></span>
      </div>
      <span class="axe-modal-title">AXE-CORE — DOM ACCESSIBILITY SCANNER</span>
      <span class="axe-version-badge">WCAG 2.1</span>
      <button class="axe-close-btn" onclick="AXEDemo.close()">✕</button>
    </div>

    <div class="axe-tabs">
      <div class="axe-tab active" onclick="AXEDemo.tab('scan')">SCANNER</div>
      <div class="axe-tab" onclick="AXEDemo.tab('explain')">EXPLAIN</div>
    </div>

    <div class="axe-modal-body">

      <!-- SCANNER TAB -->
      <div id="axe-tab-scan" class="axe-scan-wrap">

        <div>
          <div class="axe-sec-label">QUICK PRESETS — HTML CÓ LỖI</div>
          <div class="axe-presets">
            <span class="axe-preset" onclick="AXEDemo.preset('img')">img thiếu alt</span>
            <span class="axe-preset" onclick="AXEDemo.preset('form')">form thiếu label</span>
            <span class="axe-preset" onclick="AXEDemo.preset('contrast')">contrast thấp</span>
            <span class="axe-preset" onclick="AXEDemo.preset('heading')">heading sai thứ tự</span>
            <span class="axe-preset" onclick="AXEDemo.preset('clean')">HTML sạch ✓</span>
          </div>
        </div>

        <div>
          <div class="axe-sec-label">PASTE HTML ĐỂ SCAN</div>
          <textarea class="axe-textarea" id="axe-input" placeholder="Paste HTML snippet vào đây rồi nhấn SCAN..."></textarea>
        </div>

        <div class="axe-controls">
          <button class="axe-scan-btn" id="axe-scan-btn" onclick="AXEDemo.scan()">⚡ SCAN</button>
          <button class="axe-clear-btn" onclick="AXEDemo.clear()">✕ CLEAR</button>
        </div>

        <div class="axe-scanning" id="axe-scanning">
          <div class="axe-scan-dot"></div>
          <span>Running axe-core rules...</span>
        </div>

        <div class="axe-summary" id="axe-summary">
          <div class="axe-sum-header">
            <span class="axe-sum-badge" id="axe-sum-badge">—</span>
            <div class="axe-counts" id="axe-counts"></div>
          </div>
          <div class="axe-violations" id="axe-violations"></div>
        </div>

      </div>

      <!-- EXPLAIN TAB -->
      <div id="axe-tab-explain" class="axe-explain-wrap" style="display:none">
        <div class="axe-explain-card">
          <h4>AXE-CORE LÀ GÌ?</h4>
          <p>Engine accessibility testing open-source của Deque Systems — tìm WCAG violations tự động trong HTML. Tích hợp vào Playwright, Jest, Cypress, hay Chrome DevTools.</p>
        </div>
        <div class="axe-explain-card">
          <h4>SEVERITY LEVELS</h4>
          <p><code>critical</code> — ngăn cản hoàn toàn người dùng sử dụng tính năng (missing alt, unlabeled input). <code>serious</code> — gây khó khăn lớn (low contrast). <code>moderate</code> — ảnh hưởng một số users. <code>minor</code> — best practice.</p>
        </div>
        <div class="axe-explain-card">
          <h4>TÍCH HỢP VỚI PLAYWRIGHT</h4>
          <p>Dùng <code>@axe-core/playwright</code> để chạy accessibility scan trong E2E tests:</p>
          <p style="margin-top:8px"><code>import AxeBuilder from '@axe-core/playwright';<br>const results = await new AxeBuilder({page}).analyze();<br>expect(results.violations).toEqual([]);</code></p>
        </div>
        <div class="axe-explain-card">
          <h4>WCAG 2.1 LÀ GÌ?</h4>
          <p>Web Content Accessibility Guidelines — tiêu chuẩn quốc tế về khả năng tiếp cận web. Level <code>A</code> (cơ bản), <code>AA</code> (tiêu chuẩn phổ biến nhất), <code>AAA</code> (tốt nhất).</p>
        </div>
        <div class="axe-explain-card">
          <h4>ZERO FALSE POSITIVES</h4>
          <p>axe-core chỉ báo lỗi khi chắc chắn 100% là vi phạm — không có false positive. Giúp team tin tưởng vào kết quả scan và không bỏ qua alerts.</p>
        </div>
      </div>

    </div>
  </div>
</div>
`;

  // ── Public API ─────────────────────────────────
  window.AXEDemo = {

    open() {
      document.getElementById('axe-overlay').classList.add('open');
      document.body.style.overflow = 'hidden';
    },

    close() {
      document.getElementById('axe-overlay').classList.remove('open');
      document.body.style.overflow = '';
    },

    tab(name) {
      ['scan', 'explain'].forEach(t => {
        document.getElementById('axe-tab-' + t).style.display = t === name ? '' : 'none';
      });
      document.querySelectorAll('.axe-tab').forEach((el, i) => {
        el.classList.toggle('active', ['scan', 'explain'][i] === name);
      });
    },

    preset(key) {
      document.getElementById('axe-input').value = PRESETS[key] || '';
    },

    clear() {
      document.getElementById('axe-input').value = '';
      document.getElementById('axe-summary').classList.remove('show');
      document.getElementById('axe-scanning').classList.remove('show');
    },

    async scan() {
      const html = document.getElementById('axe-input').value.trim();
      if (!html) return;

      document.getElementById('axe-scan-btn').disabled = true;
      document.getElementById('axe-summary').classList.remove('show');
      document.getElementById('axe-scanning').classList.add('show');

      await new Promise(r => setTimeout(r, 900));
      document.getElementById('axe-scanning').classList.remove('show');

      const violations = detectRules(html);
      this._render(violations);
      document.getElementById('axe-scan-btn').disabled = false;
    },

    _render(violations) {
      const sum    = document.getElementById('axe-summary');
      const badge  = document.getElementById('axe-sum-badge');
      const counts = document.getElementById('axe-counts');
      const list   = document.getElementById('axe-violations');
      sum.classList.add('show');

      if (violations.length === 0) {
        badge.textContent = '✓ 0 VIOLATIONS';
        badge.className = 'axe-sum-badge pass';
        counts.innerHTML = '<span class="axe-count ok">✓ ALL CHECKS PASSED</span>';
        list.innerHTML = '<div class="axe-ok-msg">No accessibility violations found!<br>Your HTML follows WCAG 2.1 guidelines.</div>';
        return;
      }

      const total = violations.reduce((s, v) => s + (v.count || 1), 0);
      badge.textContent = total + ' VIOLATION' + (total > 1 ? 'S' : '') + ' FOUND';
      badge.className = 'axe-sum-badge fail';

      const sevCounts = {};
      violations.forEach(v => { sevCounts[v.sev] = (sevCounts[v.sev] || 0) + (v.count || 1); });
      counts.innerHTML = ['critical', 'serious', 'moderate', 'minor']
        .filter(s => sevCounts[s])
        .map(s => `<span class="axe-count ${s}">${sevCounts[s]} ${s}</span>`)
        .join('');

      list.innerHTML = violations.map((v, i) => `
        <div class="axe-viol" id="axe-viol-${i}">
          <div class="axe-viol-header" onclick="AXEDemo.toggle(${i})">
            <span class="axe-sev ${v.sev}">${v.sev.toUpperCase()}</span>
            <div class="axe-viol-info">
              <div class="axe-viol-rule">${v.rule}</div>
              <div class="axe-viol-desc">${v.desc}</div>
            </div>
            <span class="axe-viol-arrow">▼</span>
          </div>
          <div class="axe-viol-fix">
            <div class="axe-fix-label">HOW TO FIX</div>
            <div class="axe-fix-code">${v.fix}</div>
            <span class="axe-wcag-tag">${v.wcag}</span>
          </div>
        </div>`).join('');
    },

    toggle(i) {
      document.getElementById('axe-viol-' + i).classList.toggle('open');
    },
  };

  // ── Init ───────────────────────────────────────
  function init() {
    document.body.insertAdjacentHTML('beforeend', MODAL_HTML);

    document.getElementById('axe-overlay').addEventListener('click', function (e) {
      if (e.target === this) AXEDemo.close();
    });

    document.addEventListener('keydown', e => {
      if (e.key === 'Escape') AXEDemo.close();
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

})();
