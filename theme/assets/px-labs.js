/* px-labs.js: the five hands-on labs (they run entirely in the browser; nothing is sent anywhere).
   PX.lab(el, id, onDone)  mounts lab `id` ('peek' | 'tree' | 'cohort' | 'price' | 'unit') into el and returns a destroy
                            function. onDone(score, detailJson) is called when the learner reaches the lab's goal (once per mount).
   PX.labTest              pure functions for tests (experiment simulator, metric tree, cohort model, price curves, unit economics).
   Python wraps it in Components/LabStage. */
(function () {
  'use strict';
  var PX = window.PX = window.PX || {};
  function esc(s) {
    return String(s == null ? '' : s).replace(/[&<>"']/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c];
    });
  }
  function money(n) { return '$' + Math.round(n).toLocaleString('en-US'); }
  function num(n) { return Math.round(n).toLocaleString('en-US'); }
  function pct(x, d) { return (Math.round(x * 100 * Math.pow(10, d || 0)) / Math.pow(10, d || 0)) + '%'; }
  var uid = 0;
  function id(p) { uid += 1; return 'lab-' + p + '-' + uid; }
  function rng(seed) {                 // mulberry32: a small seeded random generator, so results repeat
    var a = seed >>> 0;
    return function () {
      a = (a + 0x6D2B79F5) >>> 0;
      var t = a;
      t = Math.imul(t ^ (t >>> 15), t | 1);
      t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
      return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
    };
  }
  function gauss(r) { var u = 1 - r(), v = r(); return Math.sqrt(-2 * Math.log(u)) * Math.cos(2 * Math.PI * v); }
  function slider(key, label, hint, min, max, step, value) {
    var i = id(key);
    return '<div class="lab-sl"><label for="' + i + '"><b>' + label + '</b>' + (hint ? '<small>' + hint + '</small>' : '') + '</label>' +
      '<div class="row"><input type="range" id="' + i + '" min="' + min + '" max="' + max + '" step="' + step + '" value="' + value + '" data-k="' + key + '"><output data-o="' + key + '"></output></div></div>';
  }
  /* A small line chart. series: [{pts: [y...], cls, label, dash}], opts: {ymax, ymin, xlabel(i), target, w, h, aria} */
  function chart(series, opts) {
    var W = opts.w || 520, H = opts.h || 220, L = 52, R = 12, T = 12, B = 28;
    var n = series[0].pts.length, ymin = opts.ymin || 0;
    var ymax = opts.ymax || Math.max.apply(null, series.map(function (s) { return Math.max.apply(null, s.pts); }).concat([opts.target || 0])) * 1.08 || 1;
    function X(i) { return L + (W - L - R) * (n <= 1 ? 0 : i / (n - 1)); }
    function Y(v) { return T + (H - T - B) * (1 - (v - ymin) / (ymax - ymin)); }
    var out = '';
    for (var g = 0; g <= 4; g++) {
      var v = ymin + (ymax - ymin) * g / 4;
      out += '<line class="ch-grid" x1="' + L + '" y1="' + Y(v) + '" x2="' + (W - R) + '" y2="' + Y(v) + '"/>' +
        '<text class="ch-ax" x="' + (L - 6) + '" y="' + (Y(v) + 4) + '" text-anchor="end">' + (opts.yfmt ? opts.yfmt(v) : num(v)) + '</text>';
    }
    var every = Math.max(1, Math.round(n / 6));
    for (var i = 0; i < n; i += every) {
      out += '<text class="ch-ax" x="' + X(i) + '" y="' + (H - 8) + '" text-anchor="middle">' + esc(opts.xlabel ? opts.xlabel(i) : i) + '</text>';
    }
    if (opts.target) out += '<line class="ch-target" x1="' + L + '" y1="' + Y(opts.target) + '" x2="' + (W - R) + '" y2="' + Y(opts.target) + '"/>';
    if (opts.vline != null) out += '<line class="ch-v" x1="' + opts.vline + '" y1="' + T + '" x2="' + opts.vline + '" y2="' + (H - B) + '"/>';
    series.forEach(function (s) {
      var d = s.pts.map(function (v, j) { return (j ? 'L' : 'M') + X(j).toFixed(1) + ' ' + Y(Math.max(ymin, Math.min(ymax, v))).toFixed(1); }).join('');
      out += '<path class="ch-line ' + (s.cls || '') + '" d="' + d + '"' + (s.dash ? ' stroke-dasharray="5 4"' : '') + '/>';
    });
    var legend = '<div class="ch-legend">' + series.map(function (s) { return '<span><i class="' + (s.cls || '') + '"></i>' + esc(s.label) + '</span>'; }).join('') +
      (opts.target ? '<span><i class="ch-tgt"></i>' + esc(opts.targetLabel || 'Target') + '</span>' : '') + '</div>';
    return '<svg class="lab-chart" viewBox="0 0 ' + W + ' ' + H + '" role="img" aria-label="' + esc(opts.aria || 'Chart') + '">' + out + '</svg>' + legend;
  }
  function wire(el, onInput) {
    function h(e) { if (e.target.getAttribute && e.target.getAttribute('data-k')) onInput(e); }
    el.addEventListener('input', h);
    el.addEventListener('change', h);
    return function () { el.removeEventListener('input', h); el.removeEventListener('change', h); };
  }

  /* ================================================================ peek: false positives from peeking */
  var PEEK = { n: 200, days: 14, perDay: 500, rate: 0.1 };
  function zTest(c1, c2, n) {
    var p = (c1 + c2) / (2 * n), se = Math.sqrt(p * (1 - p) * 2 / n);
    return se > 0 ? (c1 / n - c2 / n) / se : 0;
  }
  /* method: 'fixed' (look once at the end, |z| > 1.96), 'peek' (stop at the first daily |z| > 1.96),
     'seq' (daily looks with a stricter Pocock-style boundary |z| > 2.6). Returns the share of A/A tests declared a winner. */
  function simulate(method, seed) {
    var r = rng(seed), sd = Math.sqrt(PEEK.perDay * PEEK.rate * (1 - PEEK.rate)), mean = PEEK.perDay * PEEK.rate;
    var hits = 0, byDay = [];
    for (var d = 0; d < PEEK.days; d++) byDay.push(0);
    for (var e = 0; e < PEEK.n; e++) {
      var a = 0, b = 0, found = -1;
      for (var day = 0; day < PEEK.days; day++) {
        a += Math.max(0, Math.round(mean + sd * gauss(r)));
        b += Math.max(0, Math.round(mean + sd * gauss(r)));
        var z = Math.abs(zTest(a, b, PEEK.perDay * (day + 1)));
        if (found < 0) {
          if (method === 'peek' && z > 1.96) found = day;
          else if (method === 'seq' && z > 2.6) found = day;
          else if (method === 'fixed' && day === PEEK.days - 1 && z > 1.96) found = day;
        }
      }
      if (found >= 0) { hits++; for (var k = found; k < PEEK.days; k++) byDay[k]++; }
    }
    return { rate: hits / PEEK.n, hits: hits, byDay: byDay.map(function (x) { return x / PEEK.n; }) };
  }
  function labPeek(el, done) {
    var method = 'peek', seed = 7, ranPeek = false, fired = false;
    var h = '<div class="lab lab-peek"><div class="lab-brief"><b>The setup:</b> ' + PEEK.n + ' A/A tests: both arms get the <b>same</b> experience, ' +
      'so every “winner” is a false positive. ' + num(PEEK.perDay) + ' users per arm per day, a ' + pct(PEEK.rate) + ' conversion rate, ' + PEEK.days + ' days each. ' +
      'At p &lt; 0.05 you expect about 5% false winners. Choose how the team reads the results.</div><div class="lab-cols"><div class="lab-ctl">' +
      '<fieldset class="lab-seg"><legend>How the team reads results</legend>' +
      '<label><input type="radio" name="' + id('m') + '" value="peek" checked> Check daily, stop at the first p &lt; 0.05</label>' +
      '<label><input type="radio" name="' + id('m') + '" value="fixed"> Look once, on day ' + PEEK.days + '</label>' +
      '<label><input type="radio" name="' + id('m') + '" value="seq"> Check daily with a sequential boundary</label></fieldset>' +
      '<button type="button" class="ui-btn sm" data-act="rerun">Run 200 new tests</button>' +
      '<p class="small muted">The sequential option uses a stricter threshold at every look (|z| &gt; 2.6, close to a Pocock boundary for 14 looks), so you can monitor without inflating errors.</p></div>' +
      '<div class="lab-out"><div class="lab-big"><span>False “winners”</span><b data-r="rate"></b><small data-r="sub"></small></div>' +
      '<div data-r="chart"></div><p class="lab-verdict" data-r="verdict" role="status"></p></div></div></div>';
    el.innerHTML = h;
    function q(s) { return el.querySelector(s); }
    function draw() {
      var res = simulate(method, seed);
      if (method === 'peek') ranPeek = true;
      q('[data-r=rate]').textContent = pct(res.rate, 1);
      q('[data-r=sub]').textContent = res.hits + ' of ' + PEEK.n + ' identical tests declared a winner';
      var fixed = simulate('fixed', seed);
      q('[data-r=chart]').innerHTML = chart([{ pts: res.byDay, cls: 's1', label: 'Share declared a winner by this day' },
        { pts: fixed.byDay.map(function () { return 0.05; }), cls: 's2', label: 'The 5% you signed up for', dash: true }],
        { ymax: Math.max(0.3, res.rate * 1.15), yfmt: function (v) { return Math.round(v * 100) + '%'; }, xlabel: function (i) { return 'day ' + (i + 1); },
          aria: 'Cumulative share of A/A tests declared a winner by day' });
      var v = q('[data-r=verdict]'), ok = res.rate <= 0.07;
      v.className = 'lab-verdict ' + (ok ? 'ok' : '');
      if (method === 'peek') v.textContent = 'Peeking turned a 5% error rate into about ' + pct(res.rate) + '. Every daily look is another chance for noise to cross the line. Now fix it.';
      else if (ok) v.textContent = (ranPeek ? 'Back near 5%. ' : '') + (method === 'fixed' ? 'Looking once at a planned sample keeps the promise of p < 0.05.' : 'A stricter boundary at each look lets you monitor daily without paying for it in false wins.');
      else v.textContent = 'Still above 7% this time. Run new tests: random variation moves the number a little.';
      if (ok && ranPeek && !fired && done) { fired = true; done(100, JSON.stringify({ method: method, rate: Math.round(res.rate * 1000) / 10, seq: method === 'seq' })); }
    }
    function onChange(e) { if (e.target.type === 'radio') { method = e.target.value; draw(); } }
    function onClick(e) { var b = e.target.closest && e.target.closest('[data-act=rerun]'); if (b) { seed += 1; draw(); } }
    el.addEventListener('change', onChange);
    el.addEventListener('click', onClick);
    draw();
    return function () { el.removeEventListener('change', onChange); el.removeEventListener('click', onClick); };
  }

  /* ================================================================ tree: north star metric tree */
  var TREE0 = { signups: 1500, act: 0.30, ret: 0.88, invite: 0.05, res: 0.01, start: 5000, target: 8000, budget: 8 };
  var LEVERS = [
    ['signups', 'Paid sign-ups per month', 'More ads and sales. 2 effort points per step.', 250, 2, function (v) { return num(v); }],
    ['act', 'Activation rate', 'Share of sign-ups that reach first value. 1 point per step.', 0.03, 1, function (v) { return pct(v); }],
    ['ret', 'Monthly retention of active teams', 'Share of active teams still active next month. 1 point per step.', 0.01, 1, function (v) { return pct(v); }],
    ['invite', 'Invites per active team per month', 'Teams bringing in other teams (a loop). 1 point per step.', 0.02, 1, function (v) { return (Math.round(v * 100) / 100).toFixed(2); }],
    ['res', 'Resurrection', 'Share of churned teams that come back each month. 1 point per step.', 0.005, 1, function (v) { return pct(v, 1); }],
  ];
  function treeModel(s) {
    var A = s.start, pool = 0, out = [A];
    for (var m = 0; m < 12; m++) {
      var nw = (s.signups + s.invite * A) * s.act, ret = A * s.ret, ch = A - ret, rs = s.res * pool;
      pool = pool + ch - rs;
      A = ret + nw + rs;
      out.push(A);
    }
    return out;
  }
  function labTree(el, done) {
    var steps = { signups: 0, act: 0, ret: 0, invite: 0, res: 0 }, fired = false;
    function state() {
      var s = JSON.parse(JSON.stringify(TREE0));
      LEVERS.forEach(function (l) { s[l[0]] = TREE0[l[0]] + l[3] * steps[l[0]]; });
      return s;
    }
    function used() { return LEVERS.reduce(function (a, l) { return a + steps[l[0]] * l[4]; }, 0); }
    var h = '<div class="lab lab-tree"><div class="lab-brief"><b>North star:</b> weekly active teams. You start at ' + num(TREE0.start) +
      ' and the 12-month goal is <b>' + num(TREE0.target) + '</b>. Each step on a lever costs effort points; you have <b>' + TREE0.budget + '</b>. ' +
      'Active teams next month = retained teams + (sign-ups + invites) × activation + resurrected teams.</div><div class="lab-cols"><div class="lab-ctl">';
    LEVERS.forEach(function (l) { h += slider(l[0], l[1], l[2], 0, 4 / l[4], 1, 0); });
    h += '<p class="lab-points" data-r="points" role="status"></p></div><div class="lab-out"><div class="lab-big"><span>Active teams at month 12</span><b data-r="end"></b><small data-r="sub"></small></div>' +
      '<div data-r="chart"></div><table class="lab-table"><thead><tr><th>Lever</th><th>Now</th><th>Month 12 gain from one more point</th></tr></thead><tbody data-r="sens"></tbody></table>' +
      '<p class="lab-verdict" data-r="verdict" role="status"></p></div></div></div>';
    el.innerHTML = h;
    function q(s) { return el.querySelector(s); }
    function draw() {
      var s = state(), series = treeModel(s), base = treeModel(TREE0), end = series[12], u = used();
      q('[data-r=end]').textContent = num(end);
      q('[data-r=sub]').textContent = 'Without changes: ' + num(base[12]);
      q('[data-r=points]').textContent = 'Effort used: ' + u + ' of ' + TREE0.budget + ' points' + (u > TREE0.budget ? ' (over budget)' : '');
      q('[data-r=points]').className = 'lab-points ' + (u > TREE0.budget ? 'over' : '');
      LEVERS.forEach(function (l) { var o = q('[data-o=' + l[0] + ']'); if (o) o.textContent = l[5](s[l[0]]); });
      q('[data-r=chart]').innerHTML = chart([{ pts: series, cls: 's1', label: 'Your plan' }, { pts: base, cls: 's3', label: 'No change', dash: true }],
        { target: TREE0.target, targetLabel: 'Goal', xlabel: function (i) { return 'M' + i; }, aria: 'Active teams by month for your plan, no change, and the goal' });
      q('[data-r=sens]').innerHTML = LEVERS.map(function (l) {
        var t = JSON.parse(JSON.stringify(s)); t[l[0]] += l[3] / l[4];
        return '<tr><td>' + esc(l[1]) + '</td><td class="pos">' + l[5](s[l[0]]) + '</td><td class="pos">+' + num(treeModel(t)[12] - end) + '</td></tr>';
      }).join('');
      var ok = end >= TREE0.target && u <= TREE0.budget, v = q('[data-r=verdict]');
      v.className = 'lab-verdict ' + (ok ? 'ok' : '');
      v.textContent = ok ? 'Goal reached within budget. Notice how activation multiplies every sign-up and invite, and retention keeps what you win: levers that multiply each other compound.'
        : u > TREE0.budget ? 'Over the effort budget. Real teams can\'t move every lever at once: choose.'
          : 'Short of the goal by ' + num(TREE0.target - end) + '. Look at the table: which lever adds the most per point right now?';
      if (ok && !fired && done) { fired = true; done(100, JSON.stringify({ end: Math.round(end), used: u, act: steps.act, ret: steps.ret, signups: steps.signups })); }
    }
    var stop = wire(el, function (e) { steps[e.target.getAttribute('data-k')] = parseInt(e.target.value, 10) || 0; draw(); });
    draw();
    return stop;
  }

  /* ================================================================ cohort: retention curves and growth accounting */
  var COH0 = { newUsers: 8000, m1: 0.40, plateau: 0.12, res: 0.01, paid: 0.06, months: 24 };
  function retention(s, age) { return age <= 0 ? 1 : s.plateau + (s.m1 - s.plateau) * Math.pow(0.6, age - 1); }
  function cohortModel(s) {
    var N = [], active = [], acct = [], pool = 0, prev = 0;
    for (var t = 0; t < s.months; t++) {
      N.push(s.newUsers * Math.pow(1 + s.paid, t));
      var kept = 0;
      for (var i = 0; i < t; i++) kept += N[i] * retention(s, t - i);
      var rs = s.res * pool, a = N[t] + kept + rs, ch = t ? prev - kept : 0;
      pool = pool - rs + ch;
      active.push(a);
      acct.push({ nw: N[t], retained: kept, res: rs, churned: ch, qr: ch > 0 ? (N[t] + rs) / ch : Infinity });
      prev = a;
    }
    return { active: active, acct: acct };
  }
  function labCohort(el, done) {
    var s = JSON.parse(JSON.stringify(COH0)), fired = false;
    var h = '<div class="lab lab-cohort"><div class="lab-brief"><b>The product:</b> a consumer subscription app. Each month a new cohort arrives and decays along the retention curve. ' +
      'The founder\'s plan grows acquisition 6% a month. <b>Goal:</b> beat that plan\'s month-24 active users with acquisition growing no more than 2% a month, and a quick ratio of at least 1.3 at month 24.</div>' +
      '<div class="lab-cols"><div class="lab-ctl">' +
      slider('newUsers', 'New users in month 1', '', 2000, 20000, 500, s.newUsers) +
      slider('paid', 'Monthly growth of acquisition', 'Buying more users every month', 0, 0.1, 0.005, s.paid) +
      slider('m1', 'Month-1 retention', 'Onboarding and activation', 0.2, 0.7, 0.01, s.m1) +
      slider('plateau', 'Long-run retention (where the curve flattens)', 'Product-market fit for a core group', 0, 0.4, 0.01, s.plateau) +
      slider('res', 'Monthly resurrection of churned users', 'Win-back, reminders, new reasons to return', 0, 0.05, 0.0025, s.res) +
      '</div><div class="lab-out"><div class="lab-big"><span>Active users, month 24</span><b data-r="end"></b><small data-r="sub"></small></div>' +
      '<div data-r="chart"></div><dl class="lab-dl" data-r="acct"></dl><p class="lab-verdict" data-r="verdict" role="status"></p></div></div></div>';
    el.innerHTML = h;
    function q(x) { return el.querySelector(x); }
    function draw() {
      var m = cohortModel(s), last = m.acct[s.months - 1];
      var curve = []; for (var a = 0; a < s.months; a++) curve.push(retention(s, a));
      q('[data-r=end]').textContent = num(m.active[s.months - 1]);
      q('[data-r=sub]').textContent = 'Founder\'s plan: ' + num(cohortModel(COH0).active[s.months - 1]) + ' · retention curve flattens at ' + pct(s.plateau);
      [['newUsers', function (v) { return num(v); }], ['paid', function (v) { return pct(v, 1); }], ['m1', pct], ['plateau', pct], ['res', function (v) { return pct(v, 2); }]]
        .forEach(function (f) { q('[data-o=' + f[0] + ']').textContent = f[1](s[f[0]]); });
      q('[data-r=chart]').innerHTML = chart([{ pts: m.active, cls: 's1', label: 'Active users' }],
        { xlabel: function (i) { return 'M' + (i + 1); }, aria: 'Active users by month' }) +
        chart([{ pts: curve, cls: 's2', label: 'Share of a cohort still active' }],
          { h: 140, ymax: 1, yfmt: function (v) { return Math.round(v * 100) + '%'; }, xlabel: function (i) { return i; }, aria: 'Retention curve by months since sign-up' });
      q('[data-r=acct]').innerHTML = '<div><dt>New (month 24)</dt><dd>' + num(last.nw) + '</dd></div><div><dt>Retained</dt><dd>' + num(last.retained) + '</dd></div>' +
        '<div><dt>Resurrected</dt><dd>' + num(last.res) + '</dd></div><div><dt>Churned</dt><dd>' + num(last.churned) + '</dd></div>' +
        '<div><dt>Quick ratio</dt><dd>' + (isFinite(last.qr) ? (Math.round(last.qr * 100) / 100).toFixed(2) : '∞') + '</dd></div>';
      var founder = cohortModel(COH0).active[s.months - 1], beat = m.active[s.months - 1] >= founder;
      var ok = beat && last.qr >= 1.3 && s.paid <= 0.02 + 1e-9, v = q('[data-r=verdict]');
      v.className = 'lab-verdict ' + (ok ? 'ok' : '');
      v.textContent = ok ? 'Compounding growth without buying it: a flatter curve and resurrected users do the work. That flattening is what product-market fit looks like.'
        : s.paid > 0.02 + 1e-9 ? 'Growth is being bought: acquisition grows ' + pct(s.paid, 1) + ' a month. Bring it to 2% or less and fix retention instead.'
          : !beat ? 'Behind the founder\'s plan (' + num(founder) + ' at month 24). Raise where the retention curve flattens: kept users compound.'
            : 'Ahead of the plan, but the quick ratio is ' + (Math.round(last.qr * 100) / 100).toFixed(2) + ': churn nearly cancels new users. Aim for 1.3 or more.';
      if (ok && !fired && done) { fired = true; done(100, JSON.stringify({ qr: Math.round(last.qr * 100) / 100, plateau: s.plateau, m1: s.m1, res: s.res })); }
    }
    var stop = wire(el, function (e) { s[e.target.getAttribute('data-k')] = parseFloat(e.target.value) || 0; draw(); });
    draw();
    return stop;
  }

  /* ================================================================ price: Van Westendorp */
  function survey(seed, n) {
    var r = rng(seed), out = [];
    for (var i = 0; i < n; i++) {
      var v = 14 * Math.exp(0.32 * gauss(r));                         // each respondent's sense of value, around $14
      var j = function () { return Math.exp(0.12 * gauss(r)); };
      var tc = v * 0.38 * j(), ch = v * 0.68 * j(), ex = v * 1.3 * j(), te = v * 1.85 * j();
      ch = Math.max(ch, tc + 0.5); ex = Math.max(ex, ch + 0.5); te = Math.max(te, ex + 0.5);
      out.push([tc, ch, ex, te]);
    }
    return out;
  }
  /* shares at price p: too cheap / cheap (answer >= p), expensive / too expensive (answer <= p) */
  function shares(data, p) {
    var n = data.length, s = [0, 0, 0, 0];
    data.forEach(function (d) { if (d[0] >= p) s[0]++; if (d[1] >= p) s[1]++; if (d[2] <= p) s[2]++; if (d[3] <= p) s[3]++; });
    return s.map(function (x) { return x / n; });
  }
  /* PMC: too cheap meets "not cheap" (1 - cheap); PME: too expensive meets "not expensive" (1 - expensive);
     OPP: too cheap meets too expensive. Definitions vary slightly between sources. */
  function crossings(data) {
    var pmc = null, pme = null, opp = null, prev = null;
    for (var p = 1; p <= 45; p += 0.05) {
      var s = shares(data, p), f1 = s[0] - (1 - s[1]), f2 = s[3] - (1 - s[2]), f3 = s[0] - s[3];
      if (prev) {
        if (pmc == null && prev[0] > 0 && f1 <= 0) pmc = p;
        if (pme == null && prev[1] < 0 && f2 >= 0) pme = p;
        if (opp == null && prev[2] > 0 && f3 <= 0) opp = p;
      }
      prev = [f1, f2, f3];
    }
    return { pmc: pmc, pme: pme, opp: opp };
  }
  function labPrice(el, done) {
    var data = survey(42, 120), price = 30, revealed = false, fired = false, cx = crossings(data);
    var P = []; for (var p = 2; p <= 40; p += 1) P.push(p);
    var h = '<div class="lab lab-price"><div class="lab-brief"><b>The product:</b> a team analytics add-on, priced per user per month. 120 target buyers answered Van Westendorp\'s four questions: ' +
      'at what price would it be <i>so cheap you\'d doubt the quality</i>, <i>a bargain</i>, <i>getting expensive</i>, and <i>too expensive to consider</i>? ' +
      'Sales wants $30. Read the curves, find the acceptable range, and choose a price inside it.</div><div class="lab-cols"><div class="lab-ctl">' +
      slider('price', 'Your price (per user per month)', 'Move the line across the curves', 2, 40, 1, price) +
      '<dl class="lab-dl" data-r="at"></dl><button type="button" class="ui-btn sm" data-act="reveal">Show the acceptable range</button>' +
      '<p class="small muted">The range runs from the point of marginal cheapness (too cheap meets not cheap) to the point of marginal expensiveness (too expensive meets not expensive). Sources define the crossings slightly differently.</p></div>' +
      '<div class="lab-out"><div data-r="chart"></div><p class="lab-range" data-r="range"></p><p class="lab-verdict" data-r="verdict" role="status"></p></div></div></div>';
    el.innerHTML = h;
    function q(x) { return el.querySelector(x); }
    function draw() {
      var curves = [[], [], [], []];
      P.forEach(function (p) { var s = shares(data, p); for (var k = 0; k < 4; k++) curves[k].push(s[k]); });
      var x = 52 + (520 - 52 - 12) * (price - 2) / 38;
      q('[data-r=chart]').innerHTML = chart([{ pts: curves[0], cls: 's4', label: 'Too cheap' }, { pts: curves[1], cls: 's2', label: 'A bargain' },
        { pts: curves[2], cls: 's1', label: 'Getting expensive' }, { pts: curves[3], cls: 's3', label: 'Too expensive' }],
        { ymax: 1, yfmt: function (v) { return Math.round(v * 100) + '%'; }, xlabel: function (i) { return '$' + P[i]; }, vline: x, aria: 'Van Westendorp price sensitivity curves' });
      var s = shares(data, price);
      q('[data-o=price]').textContent = '$' + price;
      q('[data-r=at]').innerHTML = '<div><dt>Think it\'s too expensive</dt><dd>' + pct(s[3]) + '</dd></div><div><dt>Think it\'s getting expensive</dt><dd>' + pct(s[2]) + '</dd></div>' +
        '<div><dt>Think it\'s a bargain</dt><dd>' + pct(s[1]) + '</dd></div><div><dt>Doubt the quality</dt><dd>' + pct(s[0]) + '</dd></div>';
      q('[data-r=range]').textContent = revealed ? 'Acceptable range ≈ $' + cx.pmc.toFixed(0) + ' to $' + cx.pme.toFixed(0) + ' · optimal price point ≈ $' + cx.opp.toFixed(0) : '';
      var inside = price >= cx.pmc && price <= cx.pme, v = q('[data-r=verdict]');
      v.className = 'lab-verdict ' + (revealed && inside ? 'ok' : '');
      v.textContent = !revealed ? 'Move the price, then reveal the range when you think you see it.'
        : inside ? 'Inside the range. ' + pct(s[3]) + ' would still find it too expensive: the next question is which segment you price for, and what goes in each package.'
          : price > cx.pme ? 'Above the range: ' + pct(s[3]) + ' of target buyers rule it out. Sales\' $30 is a negotiation anchor, not research.'
            : 'Below the range: ' + pct(s[0]) + ' would doubt the quality, and you leave money on the table.';
      if (revealed && inside && !fired && done) { fired = true; done(100, JSON.stringify({ price: price, low: Math.round(cx.pmc), high: Math.round(cx.pme) })); }
    }
    var stop = wire(el, function (e) { price = parseInt(e.target.value, 10) || price; draw(); });
    function onClick(e) { var b = e.target.closest && e.target.closest('[data-act=reveal]'); if (b) { revealed = true; draw(); } }
    el.addEventListener('click', onClick);
    draw();
    return function () { stop(); el.removeEventListener('click', onClick); };
  }

  /* ================================================================ unit: LTV, CAC, payback */
  var MID = { arpa: 12000, gm: 0.85, churn: 0.08, cac: 18000 };
  var SMB0 = { arpa: 1200, gm: 0.75, churn: 0.35, cac: 900, annual: 0 };
  function unitEcon(s) {
    var arpa = s.arpa * (s.annual ? 0.85 : 1), churn = s.churn * (s.annual ? 0.7 : 1);
    var gp = arpa * s.gm, ltv = gp / churn;
    return { arpa: arpa, churn: churn, gp: gp, ltv: ltv, ratio: ltv / s.cac, payback: s.cac / (gp / 12) };
  }
  function labUnit(el, done) {
    var s = JSON.parse(JSON.stringify(SMB0)), fired = false, mid = unitEcon(MID);
    var h = '<div class="lab lab-unit"><div class="lab-brief"><b>The decision:</b> fund a self-serve plan for small businesses next to your mid-market product? ' +
      'Finance\'s bar: <b>LTV:CAC of at least 3</b> and <b>CAC payback under 12 months</b>. LTV here = yearly gross profit per account ÷ yearly churn.</div>' +
      '<div class="lab-cols"><div class="lab-ctl">' +
      slider('arpa', 'Price (revenue per account per year)', 'Higher prices can raise churn in practice', 600, 3000, 60, s.arpa) +
      slider('gm', 'Gross margin', 'Support and hosting per dollar of revenue', 0.6, 0.85, 0.01, s.gm) +
      slider('churn', 'Yearly churn', 'Onboarding and product fit for small teams', 0.15, 0.5, 0.01, s.churn) +
      slider('cac', 'Acquisition cost per customer', 'Paid search, content, referrals', 300, 2000, 25, s.cac) +
      '<label class="lab-tog"><input type="checkbox" data-k="annual"> <span><b>Push annual plans</b><small>15% discount, about 30% less churn</small></span></label>' +
      '</div><div class="lab-out"><table class="lab-table"><thead><tr><th></th><th>Mid-market (today)</th><th>Self-serve (yours)</th></tr></thead><tbody data-r="t"></tbody></table>' +
      '<div class="lab-kpis"><div><span>LTV : CAC</span><b data-r="ratio"></b></div><div><span>CAC payback</span><b data-r="pay"></b></div></div>' +
      '<p class="small muted" data-r="sens"></p><p class="lab-verdict" data-r="verdict" role="status"></p></div></div></div>';
    el.innerHTML = h;
    function q(x) { return el.querySelector(x); }
    function draw() {
      var u = unitEcon(s);
      q('[data-o=arpa]').textContent = money(s.arpa);
      q('[data-o=gm]').textContent = pct(s.gm);
      q('[data-o=churn]').textContent = pct(s.churn);
      q('[data-o=cac]').textContent = money(s.cac);
      function row(label, a, b) { return '<tr><td>' + label + '</td><td class="pos">' + a + '</td><td class="pos">' + b + '</td></tr>'; }
      q('[data-r=t]').innerHTML = row('Revenue / account / year', money(MID.arpa), money(u.arpa)) + row('Gross profit / year', money(mid.gp), money(u.gp)) +
        row('Yearly churn', pct(MID.churn), pct(u.churn, 1)) + row('LTV', money(mid.ltv), money(u.ltv)) + row('CAC', money(MID.cac), money(s.cac)) +
        row('LTV : CAC', mid.ratio.toFixed(1), u.ratio.toFixed(1)) + row('Payback (months)', mid.payback.toFixed(1), u.payback.toFixed(1));
      q('[data-r=ratio]').textContent = u.ratio.toFixed(2);
      q('[data-r=pay]').textContent = u.payback.toFixed(1) + ' mo';
      var hi = unitEcon(Object.assign({}, s, { churn: s.churn + 0.1 })), lo = unitEcon(Object.assign({}, s, { churn: Math.max(0.05, s.churn - 0.1) }));
      q('[data-r=sens]').textContent = 'Sensitivity: churn 10 points higher gives LTV ' + money(hi.ltv) + '; 10 points lower gives ' + money(lo.ltv) + '. Churn is the assumption to test first.';
      var ok = u.ratio >= 3 && u.payback < 12, v = q('[data-r=verdict]');
      v.className = 'lab-verdict ' + (ok ? 'ok' : '');
      v.textContent = ok ? 'Clears finance\'s bar on these assumptions. Next: a cheap test to measure real churn and CAC before funding a full team.'
        : u.ratio < 3 ? 'LTV:CAC is ' + u.ratio.toFixed(2) + '. Small changes in churn move LTV the most.' : 'Payback is ' + u.payback.toFixed(1) + ' months: cash comes back too slowly.';
      if (ok && !fired && done) { fired = true; done(100, JSON.stringify({ ratio: Math.round(u.ratio * 100) / 100, payback: Math.round(u.payback * 10) / 10, annual: !!s.annual })); }
    }
    var stop = wire(el, function (e) {
      var k = e.target.getAttribute('data-k');
      s[k] = e.target.type === 'checkbox' ? (e.target.checked ? 1 : 0) : parseFloat(e.target.value) || 0;
      draw();
    });
    draw();
    return stop;
  }

  var LABS = { peek: labPeek, tree: labTree, cohort: labCohort, price: labPrice, unit: labUnit };
  PX.lab = function (el, name, onDone) {
    var f = LABS[name];
    if (!el || !f) return function () {};
    return f(el, function (score, detail) { if (onDone) { try { onDone(score, detail); } catch (e) { console.error(e); } } }) || function () {};
  };
  PX.labTest = { simulate: simulate, zTest: zTest, treeModel: treeModel, TREE0: TREE0, cohortModel: cohortModel, COH0: COH0,
                 survey: survey, shares: shares, crossings: crossings, unitEcon: unitEcon, SMB0: SMB0, MID: MID };
})();
