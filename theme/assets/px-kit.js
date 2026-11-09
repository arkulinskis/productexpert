/* px-kit.js: Product Expert's drawing engines (the parts Python is too slow or clumsy for). window.PX:
     PX.today()                the browser's local date, YYYY-MM-DD (streaks and due dates follow the member's day)
     PX.fmtDate(iso, style)    'short' (6 Nov 2026), 'long' (6 November 2026), 'month', 'time'
     PX.weekday(day)           'M', 'T', ...
     PX.verifyUrl(code)        the public verification address of a credential
     PX.seal(size, label)      the verification stamp (SVG string): a hexagon with the outcome-tree mark
     PX.ring(pct, size, label) a progress ring (SVG string)
     PX.confetti()             a short burst of paper squares (skipped under reduced motion)
     PX.cert(c)                the 1000x707 certificate; c = {holder, credential, code, issued, status, demo, modules, track}
     PX.fitCert(wrap)          scale a certificate to its wrapper; returns a cleanup function
     PX.fig(name, opts)        a line diagram (SVG string) for a module or program (FIGS below). Colours come from CSS
                               variables, so it themes itself.
     PX.betboard(el)           the landing hero: a FEATURE ROADMAP vs an OUTCOME TREE with a drag handle (before/after)
   Python reaches these through client_code/px.py and the Certificate / Seal / Ring / Hero / BetBoard components. */
(function () {
  'use strict';
  var PX = window.PX = window.PX || {};
  function esc(s) {
    return String(s == null ? '' : s).replace(/[&<>"']/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c];
    });
  }
  function reduced() { return !!(window.matchMedia && matchMedia('(prefers-reduced-motion: reduce)').matches); }

  PX.today = function () {
    var d = new Date();
    return d.getFullYear() + '-' + String(d.getMonth() + 1).padStart(2, '0') + '-' + String(d.getDate()).padStart(2, '0');
  };
  PX.fmtDate = function (iso, style) {
    if (!iso) return '';
    var d = iso.length <= 10 ? new Date(iso + 'T12:00:00') : new Date(iso);
    if (isNaN(d.getTime())) return '';
    if (style === 'time') return d.toLocaleString(undefined, { day: 'numeric', month: 'short', hour: '2-digit', minute: '2-digit' });
    var opts = style === 'long' ? { day: 'numeric', month: 'long', year: 'numeric' }
      : style === 'month' ? { month: 'long', year: 'numeric' } : { day: 'numeric', month: 'short', year: 'numeric' };
    return d.toLocaleDateString(undefined, opts);
  };
  PX.weekday = function (day) { return 'SMTWTFS'[new Date(day + 'T12:00:00').getDay()]; };
  PX.verifyUrl = function (code) { return location.origin + location.pathname + '#verify/' + encodeURIComponent(code); };

  /* ---------------------------------------------------------------- the stamp */
  PX.seal = function (size, label) {
    var s = size || 120, id = 'sl' + Math.random().toString(36).slice(2, 7);
    var hex = function (r) {
      var p = [];
      for (var i = 0; i < 6; i++) { var a = Math.PI / 6 + i * Math.PI / 3; p.push((50 + r * Math.cos(a)).toFixed(2) + ',' + (50 + r * Math.sin(a)).toFixed(2)); }
      return p.join(' ');
    };
    return '<svg class="px-seal" width="' + s + '" height="' + s + '" viewBox="0 0 100 100" role="img" aria-label="Product Expert verification stamp">' +
      '<defs><path id="' + id + '" d="M50 50m-33 0a33 33 0 1 1 66 0a33 33 0 1 1-66 0"/></defs>' +
      '<polygon points="' + hex(48) + '" fill="var(--seal-bg, #2340A8)"/>' +
      '<polygon points="' + hex(43.5) + '" fill="none" stroke="var(--seal-ink, #fff)" stroke-width=".9" opacity=".75"/>' +
      '<text font-family="JetBrains Mono, ui-monospace, monospace" font-weight="700" font-size="6.4" letter-spacing="1.2" fill="var(--seal-ink, #fff)"><textPath href="#' + id + '" startOffset="0">' +
      esc(label || 'PRODUCT EXPERT · VERIFIED · DIRECTOR READY ·') + '</textPath></text>' +
      '<g fill="none" stroke="var(--seal-ink, #fff)" stroke-width="3.4" stroke-linecap="round" stroke-linejoin="round">' +
      '<path d="M50 41v7M50 48 39 56M50 48l11 8"/></g>' +
      '<g fill="var(--seal-ink, #fff)"><circle cx="50" cy="38" r="4.2"/><circle cx="38" cy="59" r="3.6"/><circle cx="62" cy="59" r="3.6"/></g>' +
      '<circle cx="50" cy="72" r="1.8" fill="var(--seal-accent, #D9822B)"/></svg>';
  };

  PX.ring = function (pct, size, label) {
    var s = size || 64, r = s / 2 - 5, c = 2 * Math.PI * r, p = Math.max(0, Math.min(100, pct || 0));
    return '<span class="px-ring" style="width:' + s + 'px;height:' + s + 'px" role="img" aria-label="' + p + '% complete"><svg width="' + s + '" height="' + s + '" aria-hidden="true">' +
      '<circle cx="' + s / 2 + '" cy="' + s / 2 + '" r="' + r + '" fill="none" stroke="var(--c-surface-2)" stroke-width="5"/>' +
      '<circle cx="' + s / 2 + '" cy="' + s / 2 + '" r="' + r + '" fill="none" stroke="var(--c-brand)" stroke-width="5" stroke-linecap="round" stroke-dasharray="' + (c * p / 100).toFixed(1) + ' ' + c.toFixed(1) + '" transform="rotate(-90 ' + s / 2 + ' ' + s / 2 + ')"/></svg>' +
      '<b aria-hidden="true">' + esc(label != null && label !== '' ? label : p + '%') + '</b></span>';
  };

  PX.confetti = function () {
    if (reduced()) return;
    var box = document.createElement('div'); box.className = 'px-confetti'; box.setAttribute('aria-hidden', 'true');
    var cols = ['#2340A8', '#D9822B', '#171B24', '#9FB1F5', '#F3C99A'];
    for (var i = 0; i < 64; i++) {
      var p = document.createElement('i');
      p.style.left = Math.random() * 100 + 'vw';
      p.style.background = cols[i % cols.length];
      p.style.animationDuration = (1.6 + Math.random() * 1.6) + 's';
      p.style.animationDelay = (Math.random() * .35) + 's';
      p.style.transform = 'rotate(' + Math.random() * 180 + 'deg)';
      box.appendChild(p);
    }
    document.body.appendChild(box);
    setTimeout(function () { box.remove(); }, 3800);
  };

  /* ---------------------------------------------------------------- diagrams */
  /* A diagram spec: nodes [id, x, y, w, label, kind] on a 400x225 grid, edges [from, to, dashed?].
     kind: '' (plain box), 'b' (brand: the move a director makes), 'a' (accent: the bet, risk or gate), 'g' (ghost: context/data) */
  var FIGS = {
    toolkit: { cap: 'Discovery decides what is worth building; delivery builds it well', n: [
      ['r', 10, 20, 110, 'four risks', 'g'], ['d', 10, 100, 110, 'discovery', 'b'], ['o', 10, 180, 110, 'outcomes', 'a'],
      ['s', 160, 60, 90, 'scrum / kanban', ''], ['p', 160, 140, 90, 'specs + roadmap', ''], ['v', 290, 100, 100, 'delivery', '']],
      e: [['r', 'd'], ['d', 's'], ['d', 'p'], ['s', 'v'], ['p', 'v'], ['v', 'o', 1]] },
    judgement: { cap: 'Spend effort where the return is ten times the cost', n: [
      ['i', 10, 100, 90, '40 requests', 'g'], ['l', 150, 30, 110, 'leverage: do well', 'b'], ['n', 150, 100, 110, 'neutral: good enough', ''],
      ['o', 150, 170, 110, 'overhead: cut', 'g'], ['x', 300, 100, 90, 'outcome', 'a']],
      e: [['i', 'l'], ['i', 'n'], ['i', 'o'], ['l', 'x'], ['n', 'x', 1]] },
    decision: { cap: 'Reversible decisions fast, one-way doors carefully', n: [
      ['q', 10, 100, 90, 'decision', 'g'], ['t', 140, 40, 110, 'two-way door', ''], ['o', 140, 160, 110, 'one-way door', 'a'],
      ['f', 290, 40, 100, 'decide fast', 'b'], ['c', 290, 160, 100, 'decider + input', 'b'], ['l', 290, 100, 100, 'decision log', 'g']],
      e: [['q', 't'], ['q', 'o'], ['t', 'f'], ['o', 'c'], ['c', 'l', 1], ['f', 'l', 1]] },
    writing: { cap: 'Answer first, then the arguments, then the evidence', n: [
      ['a', 140, 20, 120, 'recommendation', 'b'], ['x', 20, 100, 110, 'argument 1', ''], ['y', 145, 100, 110, 'argument 2', ''], ['z', 270, 100, 110, 'argument 3', ''],
      ['e', 20, 180, 360, 'evidence · data · sources', 'g']],
      e: [['a', 'x'], ['a', 'y'], ['a', 'z'], ['x', 'e', 1], ['y', 'e', 1], ['z', 'e', 1]] },
    strategy: { cap: 'Diagnosis, guiding policy, coherent actions', n: [
      ['d', 10, 100, 100, 'diagnosis', 'b'], ['g', 150, 100, 100, 'guiding policy', 'b'], ['a1', 290, 30, 100, 'action', ''],
      ['a2', 290, 100, 100, 'action', ''], ['a3', 290, 170, 100, 'action', ''], ['n', 150, 180, 100, 'not doing', 'a']],
      e: [['d', 'g'], ['g', 'a1'], ['g', 'a2'], ['g', 'a3'], ['g', 'n', 1]] },
    moats: { cap: 'Every power needs a benefit and a barrier', n: [
      ['p', 150, 20, 100, 'power', 'b'], ['b', 30, 100, 110, 'benefit', ''], ['r', 260, 100, 110, 'barrier', 'a'],
      ['s', 10, 180, 120, 'switching costs', 'g'], ['n', 140, 180, 120, 'network effects', 'g'], ['c', 270, 180, 120, 'counter-position', 'g']],
      e: [['p', 'b'], ['p', 'r'], ['s', 'b', 1], ['n', 'p', 1], ['c', 'r', 1]] },
    dynamics: { cap: 'Who aggregates demand, what is commoditising, which job is hired', n: [
      ['u', 150, 15, 100, 'user', 'g'], ['a', 150, 75, 100, 'aggregator', 'a'], ['y', 150, 135, 100, 'your product', 'b'],
      ['j', 10, 75, 110, 'the job', ''], ['c', 290, 135, 100, 'commodity', 'g'], ['d', 290, 195, 100, 'low-end entrant', '']],
      e: [['u', 'a'], ['a', 'y'], ['j', 'u', 1], ['c', 'y'], ['d', 'y', 1]] },
    portfolio: { cap: 'Balance the horizons; kill criteria before funding', n: [
      ['h1', 10, 30, 110, 'H1 core ~70%', ''], ['h2', 10, 100, 110, 'H2 adjacent ~20%', 'b'], ['h3', 10, 170, 110, 'H3 options ~10%', 'a'],
      ['b', 160, 100, 90, 'bet brief', 'g'], ['k', 290, 50, 100, 'continue', 'b'], ['s', 290, 150, 100, 'stop', 'a']],
      e: [['h1', 'b'], ['h2', 'b'], ['h3', 'b'], ['b', 'k'], ['b', 's', 1]] },
    discovery: { cap: 'Outcome, opportunities, solutions, assumption tests', n: [
      ['o', 150, 10, 100, 'outcome', 'a'], ['p1', 40, 75, 120, 'opportunity', 'b'], ['p2', 240, 75, 120, 'opportunity', 'b'],
      ['s1', 10, 140, 90, 'solution', ''], ['s2', 110, 140, 90, 'solution', ''], ['s3', 280, 140, 90, 'solution', ''],
      ['t', 10, 195, 190, 'assumption tests', 'g']],
      e: [['o', 'p1'], ['o', 'p2'], ['p1', 's1'], ['p1', 's2'], ['p2', 's3'], ['s1', 't', 1], ['s2', 't', 1]] },
    evidence: { cap: 'Raise confidence step by step', n: [
      ['o', 10, 190, 90, 'opinion', 'g'], ['e', 85, 145, 90, 'anecdote', 'g'], ['m', 160, 100, 90, 'user data', ''],
      ['t', 235, 55, 90, 'test result', 'b'], ['l', 305, 10, 90, 'launch data', 'a']],
      e: [['o', 'e'], ['e', 'm'], ['m', 't'], ['t', 'l']] },
    experiment: { cap: 'Trust checks before results', n: [
      ['h', 10, 100, 90, 'hypothesis', 'g'], ['r', 130, 40, 90, 'A', ''], ['s', 130, 160, 90, 'B', ''],
      ['m', 250, 40, 140, 'SRM check', 'a'], ['o', 250, 100, 140, 'OEC + guardrails', 'b'], ['p', 250, 160, 140, 'no peeking', 'a']],
      e: [['h', 'r'], ['h', 's'], ['r', 'm'], ['s', 'm'], ['m', 'o'], ['o', 'p', 1]] },
    pmf: { cap: 'Find who would be very disappointed without you', n: [
      ['v', 10, 40, 130, 'very disappointed', 'b'], ['s', 10, 110, 130, 'somewhat', ''], ['n', 10, 180, 130, 'not', 'g'],
      ['l', 200, 40, 190, 'double down on what they love', 'b'], ['f', 200, 110, 190, 'fix what holds them back', 'a']],
      e: [['v', 'l'], ['s', 'f'], ['n', 'f', 1]] },
    metrics: { cap: 'A north star, its inputs, and guardrails', n: [
      ['n', 140, 15, 120, 'north star', 'a'], ['b', 10, 90, 85, 'breadth', 'b'], ['d', 110, 90, 85, 'depth', 'b'], ['f', 210, 90, 85, 'frequency', 'b'],
      ['e', 310, 90, 85, 'efficiency', 'b'], ['g', 10, 180, 385, 'guardrails · counter-metrics', 'g']],
      e: [['b', 'n'], ['d', 'n'], ['f', 'n'], ['e', 'n'], ['g', 'n', 1]] },
    cohort: { cap: 'New + resurrected vs churned', n: [
      ['w', 10, 30, 90, 'new', 'b'], ['r', 10, 110, 90, 'resurrected', 'b'], ['a', 160, 70, 100, 'active users', 'a'],
      ['c', 300, 70, 90, 'churned', 'g'], ['q', 160, 170, 230, 'quick ratio = (new + res) / churned', 'g']],
      e: [['w', 'a'], ['r', 'a'], ['a', 'c'], ['c', 'r', 1]] },
    loops: { cap: 'Loops compound, funnels leak', n: [
      ['u', 20, 30, 100, 'new user', ''], ['a', 280, 30, 100, 'creates value', 'b'], ['s', 280, 170, 100, 'shared / found', 'b'], ['n', 20, 170, 100, 'next user', 'a']],
      e: [['u', 'a'], ['a', 's'], ['s', 'n'], ['n', 'u']] },
    pricing: { cap: 'Value metric, packages, willingness to pay', n: [
      ['w', 10, 100, 100, 'willingness to pay', 'g'], ['v', 150, 30, 100, 'value metric', 'b'], ['g', 150, 100, 100, 'good', ''],
      ['b', 150, 160, 100, 'better', 'b'], ['x', 290, 100, 100, 'best', 'a']],
      e: [['w', 'v'], ['w', 'g'], ['v', 'b', 1], ['g', 'b'], ['b', 'x']] },
    gtm: { cap: 'Alternatives, unique value, best-fit customer, category', n: [
      ['a', 10, 30, 120, 'alternatives', 'g'], ['u', 10, 100, 120, 'unique attributes', ''], ['v', 150, 100, 100, 'value', 'b'],
      ['c', 290, 30, 100, 'best-fit customer', 'b'], ['k', 290, 170, 100, 'category', 'a']],
      e: [['a', 'u'], ['u', 'v'], ['v', 'c'], ['v', 'k']] },
    launch: { cap: 'Deploy, then release in stages', n: [
      ['f', 10, 100, 80, 'flag', 'g'], ['i', 110, 100, 80, 'internal', ''], ['c', 210, 100, 80, '5% canary', 'a'],
      ['g', 310, 100, 80, 'GA', 'b'], ['r', 210, 180, 80, 'rollback', 'g']],
      e: [['f', 'i'], ['i', 'c'], ['c', 'g'], ['c', 'r', 1]] },
    enterprise: { cap: 'A buying group, not a buyer', n: [
      ['d', 150, 100, 100, 'deal', 'a'], ['u', 10, 20, 100, 'users', ''], ['e', 290, 20, 100, 'economic buyer', 'b'],
      ['s', 10, 180, 100, 'security', 'g'], ['p', 150, 180, 100, 'procurement', 'g'], ['i', 290, 180, 100, 'IT', 'g']],
      e: [['u', 'd'], ['e', 'd'], ['s', 'd'], ['p', 'd'], ['i', 'd']] },
    pnl: { cap: 'LTV, CAC, payback and margin', n: [
      ['r', 10, 30, 110, 'revenue / account', ''], ['g', 10, 100, 110, 'gross margin', ''], ['c', 10, 170, 110, 'churn', 'a'],
      ['l', 160, 100, 90, 'LTV', 'b'], ['k', 290, 30, 100, 'CAC', 'g'], ['x', 290, 140, 100, 'LTV : CAC', 'a']],
      e: [['r', 'l'], ['g', 'l'], ['c', 'l'], ['l', 'x'], ['k', 'x']] },
    org: { cap: 'Stream-aligned teams on a platform', n: [
      ['s1', 10, 30, 110, 'stream team', 'b'], ['s2', 145, 30, 110, 'stream team', 'b'], ['s3', 280, 30, 110, 'stream team', 'b'],
      ['e', 10, 110, 110, 'enabling', ''], ['c', 280, 110, 110, 'complex subsystem', ''], ['p', 10, 185, 380, 'platform (as a service)', 'g']],
      e: [['p', 's1', 1], ['p', 's2', 1], ['p', 's3', 1], ['e', 's1'], ['c', 's3']] },
    talent: { cap: 'Structured hiring, clear levels, honest feedback', n: [
      ['r', 10, 100, 90, 'role scorecard', 'g'], ['w', 130, 40, 100, 'work sample', 'b'], ['i', 130, 160, 100, 'structured loop', 'b'],
      ['d', 260, 100, 130, 'evidence debrief', 'a'], ['l', 260, 180, 130, 'ladder + calibration', 'g']],
      e: [['r', 'w'], ['r', 'i'], ['w', 'd'], ['i', 'd'], ['d', 'l', 1]] },
    coaching: { cap: 'Your output is your organisation\'s output', n: [
      ['m', 150, 15, 100, 'director', 'a'], ['g1', 30, 90, 120, 'group PM', 'b'], ['g2', 250, 90, 120, 'group PM', 'b'],
      ['p1', 10, 175, 80, 'PM', ''], ['p2', 110, 175, 80, 'PM', ''], ['p3', 210, 175, 80, 'PM', ''], ['p4', 310, 175, 80, 'PM', '']],
      e: [['m', 'g1'], ['m', 'g2'], ['g1', 'p1'], ['g1', 'p2'], ['g2', 'p3'], ['g2', 'p4'], ['m', 'p2', 1]] },
    cadence: { cap: 'Strategy, objectives, reviews, retros', n: [
      ['s', 10, 100, 90, 'yearly strategy', 'b'], ['o', 120, 30, 90, 'quarterly goals', ''], ['r', 230, 100, 90, 'monthly review', ''],
      ['w', 120, 170, 90, 'weekly rhythm', 'g'], ['t', 320, 30, 70, 'retro', 'a']],
      e: [['s', 'o'], ['o', 'r'], ['r', 'w', 1], ['w', 'o', 1], ['r', 't']] },
    influence: { cap: 'Map, pre-wire, decide, follow through', n: [
      ['m', 10, 100, 90, 'stakeholder map', 'g'], ['p1', 140, 30, 100, '1:1 pre-wire', 'b'], ['p2', 140, 170, 100, '1:1 pre-wire', 'b'],
      ['d', 280, 100, 110, 'decision meeting', 'a']],
      e: [['m', 'p1'], ['m', 'p2'], ['p1', 'd'], ['p2', 'd']] },
    boardroom: { cap: 'Conclusion, metrics, risks, asks', n: [
      ['c', 140, 15, 120, 'CEO + board', 'a'], ['a', 10, 110, 90, 'conclusion', 'b'], ['k', 110, 110, 90, 'metrics', ''],
      ['r', 210, 110, 90, 'risks', ''], ['s', 310, 110, 80, 'asks', 'b'], ['p', 10, 185, 380, 'pre-read, sent ahead', 'g']],
      e: [['a', 'c'], ['k', 'c'], ['r', 'c'], ['s', 'c'], ['p', 'a', 1]] },
    conflict: { cap: 'Interests, not positions', n: [
      ['a', 10, 30, 110, 'position A', 'g'], ['b', 280, 30, 110, 'position B', 'g'], ['i', 10, 110, 110, 'interest A', ''],
      ['j', 280, 110, 110, 'interest B', ''], ['o', 145, 170, 110, 'options', 'b'], ['g', 145, 70, 110, 'shared goal', 'a']],
      e: [['a', 'i'], ['b', 'j'], ['i', 'o'], ['j', 'o'], ['g', 'o', 1]] },
    change: { cap: 'Urgency, coalition, pilot, wins, anchor', n: [
      ['u', 10, 180, 80, 'urgency', 'a'], ['c', 85, 140, 80, 'coalition', ''], ['p', 160, 100, 80, 'pilot', 'b'],
      ['w', 235, 60, 80, 'wins', 'b'], ['a', 310, 20, 80, 'anchor', 'g']],
      e: [['u', 'c'], ['c', 'p'], ['p', 'w'], ['w', 'a']] },
    frontier: { cap: 'Look at outputs, name failures, test, keep humans in control', n: [
      ['t', 10, 30, 100, 'real outputs', 'g'], ['a', 10, 110, 100, 'error analysis', 'b'], ['e', 150, 70, 100, 'evals', 'b'],
      ['h', 290, 30, 100, 'human approval', 'a'], ['c', 290, 110, 100, 'cost per task', ''], ['g', 150, 180, 240, 'staged launch + guardrails', 'g']],
      e: [['t', 'a'], ['a', 'e'], ['e', 'h'], ['e', 'c'], ['e', 'g', 1]] },
    platform: { cap: 'Liquidity, trust and stable rules', n: [
      ['s', 10, 100, 90, 'supply', ''], ['m', 150, 100, 100, 'marketplace', 'b'], ['d', 300, 100, 90, 'demand', ''],
      ['t', 150, 20, 100, 'trust + safety', 'a'], ['r', 150, 180, 100, 'stable rules', 'g']],
      e: [['s', 'm'], ['d', 'm'], ['t', 'm', 1], ['r', 'm', 1]] },
    trust: { cap: 'Privacy, AI risk, accessibility and fair design, by default', n: [
      ['f', 150, 100, 100, 'feature', 'b'], ['p', 10, 30, 110, 'data minimum', 'g'], ['r', 280, 30, 110, 'AI risk tier', 'a'],
      ['a', 10, 170, 110, 'WCAG 2.2', 'g'], ['c', 280, 170, 110, 'easy cancel', 'g']],
      e: [['p', 'f'], ['r', 'f'], ['a', 'f'], ['c', 'f']] },
    tech: { cap: 'SLOs, error budgets, delivery health', n: [
      ['s', 10, 100, 80, 'SLO', 'b'], ['e', 120, 100, 100, 'error budget', 'a'], ['f', 260, 40, 130, 'ship features', ''],
      ['r', 260, 160, 130, 'fix reliability', ''], ['d', 120, 20, 100, 'DORA metrics', 'g']],
      e: [['s', 'e'], ['e', 'f'], ['e', 'r', 1], ['d', 'e', 1]] },
    director: { cap: 'Strategy, evidence, organisation and influence, measured by outcomes', n: [
      ['s', 10, 30, 100, 'strategy', 'b'], ['e', 10, 110, 100, 'evidence', 'b'], ['o', 290, 30, 100, 'organisation', 'b'],
      ['i', 290, 110, 100, 'influence', 'b'], ['d', 150, 70, 100, 'director', 'a'], ['x', 100, 185, 200, 'customer + business outcomes', 'g']],
      e: [['s', 'd'], ['e', 'd'], ['o', 'd'], ['i', 'd'], ['d', 'x']] },
    casefile: { cap: 'What happened, why, and the lesson', n: [
      ['d', 10, 100, 100, 'decision', ''], ['a', 150, 30, 100, 'assumption', 'g'], ['r', 150, 170, 100, 'reaction', 'a'],
      ['l', 290, 100, 100, 'lesson', 'b']],
      e: [['d', 'a', 1], ['d', 'r'], ['a', 'l'], ['r', 'l']] },
    library: { cap: 'Primary sources, linked to the originals', n: [
      ['b', 10, 40, 90, 'books', 'g'], ['p', 10, 110, 90, 'papers', 'g'], ['a', 10, 180, 90, 'articles', 'g'],
      ['l', 160, 110, 90, 'library', 'b'], ['m', 300, 110, 90, 'modules', 'a']],
      e: [['b', 'l'], ['p', 'l'], ['a', 'l'], ['l', 'm']] },
  };
  function renderFig(spec, opts) {
    opts = opts || {};
    var H = 26, byId = {}, out = '';
    spec.n.forEach(function (n) { byId[n[0]] = n; });
    var mid = function (n) { return [n[1] + n[3] / 2, n[2] + H / 2]; };
    var aid = 'ar' + Math.random().toString(36).slice(2, 7);
    out += '<defs><marker id="' + aid + '" viewBox="0 0 8 8" refX="7" refY="4" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 0 8 4 0 8z" fill="var(--fig-line)"/></marker></defs>';
    spec.e.forEach(function (e) {
      var a = byId[e[0]], b = byId[e[1]];
      if (!a || !b) return;
      var p = mid(a), q = mid(b), x1, y1, x2, y2;
      if (Math.abs(q[0] - p[0]) > Math.abs(q[1] - p[1]) * 1.2) {
        x1 = p[0] < q[0] ? a[1] + a[3] : a[1]; y1 = p[1]; x2 = p[0] < q[0] ? b[1] : b[1] + b[3]; y2 = q[1];
      } else {
        x1 = p[0]; y1 = p[1] < q[1] ? a[2] + H : a[2]; x2 = q[0]; y2 = p[1] < q[1] ? b[2] : b[2] + H;
      }
      var cx = (x1 + x2) / 2;
      var d = Math.abs(y2 - y1) < 2 || Math.abs(x2 - x1) < 2 ? 'M' + x1 + ' ' + y1 + 'L' + x2 + ' ' + y2
        : (Math.abs(x2 - x1) > Math.abs(y2 - y1) ? 'M' + x1 + ' ' + y1 + 'C' + cx + ' ' + y1 + ' ' + cx + ' ' + y2 + ' ' + x2 + ' ' + y2
          : 'M' + x1 + ' ' + y1 + 'C' + x1 + ' ' + (y1 + y2) / 2 + ' ' + x2 + ' ' + (y1 + y2) / 2 + ' ' + x2 + ' ' + y2);
      out += '<path class="fe" d="' + d + '" fill="none" stroke="var(--fig-line)" stroke-width="1.3"' + (e[2] ? ' stroke-dasharray="4 3"' : '') + ' marker-end="url(#' + aid + ')"/>';
    });
    spec.n.forEach(function (n) {
      var k = n[5] || '';
      out += '<g class="fn' + (k ? ' k-' + k : '') + '"><rect x="' + n[1] + '" y="' + n[2] + '" width="' + n[3] + '" height="' + H + '" rx="5"/>' +
        '<text x="' + (n[1] + n[3] / 2) + '" y="' + (n[2] + 17) + '" text-anchor="middle">' + esc(n[4]) + '</text></g>';
    });
    var title = opts.title || spec.cap;
    return '<svg class="px-fig" viewBox="0 0 400 225" role="img" aria-label="' + esc(title) + '">' + out + '</svg>';
  }
  PX.fig = function (name, opts) { return renderFig(FIGS[name] || FIGS.director, opts); };
  PX.figCaption = function (name) { return (FIGS[name] || FIGS.director).cap; };

  /* ---------------------------------------------------------------- the landing hero: feature roadmap vs outcome tree */
  var TREE = { n: [
    ['o', 185, 8, 170, 'Outcome: NRR 101% → 110%', 'a'],
    ['p1', 8, 78, 160, 'Admins can’t show value', 'b'], ['p2', 190, 78, 160, 'Teams stall after setup', 'b'], ['p3', 372, 78, 160, 'Security reviews block deals', 'b'],
    ['s1', 8, 148, 160, 'Bet: usage reports', ''], ['s2', 190, 148, 160, 'Bet: guided templates', ''], ['s3', 372, 148, 160, 'Bet: SSO + audit log', ''],
    ['t', 100, 190, 340, 'each bet: riskiest assumption tested first', 'g']],
    e: [['o', 'p1'], ['o', 'p2'], ['o', 'p3'], ['p1', 's1'], ['p2', 's2'], ['p3', 's3']] };
  /* [label, start quarter (0-4), length in quarters, lane, date stamp] */
  var BARS = [
    ['Dark mode', 0, 0.8, 0, 'Feb 14'], ['AI assistant', 0.9, 1.6, 0, 'Jun 30'], ['New dashboard', 2.6, 1.3, 0, 'Oct 1'],
    ['Mobile app v2', 0.2, 2.1, 1, 'Jul 15'], ['Custom fields', 2.4, 1.2, 1, 'Sep 30'],
    ['Slack integration', 0, 1.1, 2, 'Mar 31'], ['Gantt view', 1.2, 1.0, 2, 'Jun 1'], ['Theme editor', 2.3, 1.5, 2, 'Nov 15'],
    ['Big client ask #1', 0.5, 0.9, 3, 'Apr 2'], ['Big client ask #2', 1.5, 1.1, 3, 'Jul 1'], ['Redesign', 2.7, 1.25, 3, 'Dec 20']];
  function roadmapSvg() {
    var x0 = 70, qw = 115, top = 30, lane = 46, out = '';
    for (var q = 0; q < 4; q++) {
      out += '<text class="bb-q" x="' + (x0 + q * qw + qw / 2) + '" y="18" text-anchor="middle">Q' + (q + 1) + '</text>' +
        '<line class="bb-grid" x1="' + (x0 + q * qw) + '" y1="24" x2="' + (x0 + q * qw) + '" y2="214"/>';
    }
    ['Team A', 'Team B', 'Team C', 'Team D'].forEach(function (t, i) {
      out += '<text class="bb-lane" x="6" y="' + (top + i * lane + 22) + '">' + t + '</text>';
    });
    BARS.forEach(function (b) {
      var x = x0 + b[1] * qw + 2, w = b[2] * qw - 4, y = top + b[3] * lane + 6;
      out += '<g class="bb-bar"><rect x="' + x + '" y="' + y + '" width="' + w + '" height="26" rx="4"/>' +
        '<text x="' + (x + 7) + '" y="' + (y + 13) + '">' + esc(b[0]) + '</text>' +
        '<text class="bb-due" x="' + (x + 7) + '" y="' + (y + 23) + '">due ' + esc(b[4]) + '</text></g>';
    });
    return '<svg class="px-fig bb-road" viewBox="0 0 540 220" role="img" aria-label="Feature roadmap: eleven features with due dates across four quarters and four teams">' + out + '</svg>';
  }
  PX.betboard = function (el) {
    if (!el) return function () {};
    var tree = renderFig(TREE, { title: 'Outcome tree: one outcome, three customer opportunities, three bets each tested first' })
      .replace('viewBox="0 0 400 225"', 'viewBox="0 0 540 220"');
    el.innerHTML =
      '<div class="pl-frame">' +
      '<div class="pl-layer pl-demo"><span class="pl-tag">FEATURE ROADMAP</span>' + roadmapSvg() +
      '<p class="pl-note">Eleven promises with dates. Nobody can say which customer problem any of them solves.</p></div>' +
      '<div class="pl-layer pl-prod"><span class="pl-tag">OUTCOME TREE</span>' + tree +
      '<p class="pl-note">One outcome, the customer problems behind it, and bets you test before you build.</p></div>' +
      '<div class="pl-handle" role="slider" tabindex="0" aria-label="Compare the feature roadmap and the outcome tree" aria-valuemin="0" aria-valuemax="100" aria-valuenow="50"><span></span></div>' +
      '</div>';
    var frame = el.querySelector('.pl-frame'), prod = el.querySelector('.pl-prod'), handle = el.querySelector('.pl-handle');
    var pos = 50, dragging = false;
    function set(p, animate) {
      pos = Math.max(0, Math.min(100, p));
      frame.classList.toggle('animate', !!animate);
      prod.style.clipPath = 'inset(0 0 0 ' + pos + '%)';
      handle.style.left = pos + '%';
      handle.setAttribute('aria-valuenow', String(Math.round(pos)));
      handle.setAttribute('aria-valuetext', pos > 60 ? 'Mostly feature roadmap' : pos < 40 ? 'Mostly outcome tree' : 'Half and half');
    }
    function fromEvent(e) {
      var r = frame.getBoundingClientRect();
      return (e.clientX - r.left) / r.width * 100;
    }
    function down(e) { dragging = true; if (frame.setPointerCapture) frame.setPointerCapture(e.pointerId); set(fromEvent(e), false); }
    function move(e) { if (dragging) set(fromEvent(e), false); }
    function up() { dragging = false; }
    function key(e) {
      if (e.key === 'ArrowLeft') { set(pos - 5, true); e.preventDefault(); }
      else if (e.key === 'ArrowRight') { set(pos + 5, true); e.preventDefault(); }
      else if (e.key === 'Home') { set(0, true); e.preventDefault(); }
      else if (e.key === 'End') { set(100, true); e.preventDefault(); }
    }
    frame.addEventListener('pointerdown', down);
    frame.addEventListener('pointermove', move);
    frame.addEventListener('pointerup', up);
    frame.addEventListener('pointercancel', up);
    handle.addEventListener('keydown', key);
    // The authored moment: start on the feature roadmap, then sweep to reveal most of the outcome tree.
    set(96, false);
    var t = setTimeout(function () { set(reduced() ? 50 : 30, !reduced()); frame.classList.add('shown'); }, 450);
    return function () {
      clearTimeout(t);
      frame.removeEventListener('pointerdown', down);
      frame.removeEventListener('pointermove', move);
      frame.removeEventListener('pointerup', up);
      frame.removeEventListener('pointercancel', up);
      handle.removeEventListener('keydown', key);
    };
  };

  /* ---------------------------------------------------------------- the certificate */
  PX.cert = function (c) {
    var arch = c.track === 'fellow';
    var issued = c.issued ? new Date(c.issued).toLocaleDateString('en-GB', { day: 'numeric', month: 'long', year: 'numeric' }) : '';
    var mods = c.modules || [];
    var grid = '';
    for (var y = 40; y < 707; y += 40) grid += '<line x1="0" y1="' + y + '" x2="1000" y2="' + y + '"/>';
    return '<div class="px-cert' + (arch ? ' arch' : '') + '" data-cert>' +
      '<svg class="grid" viewBox="0 0 1000 707" aria-hidden="true"><g>' + grid + '</g></svg>' +
      '<div class="frame"></div>' +
      (c.demo ? '<div class="sample">SAMPLE RECORD</div>' : '') +
      '<div class="inner">' +
      '<div class="top"><div class="mark">' + PX.seal(64) + '</div><div><div class="inst">PRODUCT EXPERT</div><div class="sub">' +
      (arch ? 'DIRECTOR CREDENTIAL' : 'PROGRAM CERTIFICATE') + ' · MEMO OF RECORD</div></div>' +
      '<div class="docno">DOC. ' + esc(c.code) + '</div></div>' +
      '<div class="certify">This certifies that</div>' +
      '<div class="holder">' + esc(c.holder) + '</div>' +
      '<div class="has">' + (arch ? 'holds the Product Leadership Foundations certificate and four specialist certificates, and is recognised as' :
        'completed every module, drill and leadership challenge of the program and passed its final examination for the') + '</div>' +
      '<div class="cred">' + esc(c.credential) + '</div>' +
      (mods.length ? '<div class="mods">' + mods.map(function (m, i) { return '<span><b>' + String(i + 1).padStart(2, '0') + '</b> ' + esc(m) + '</span>'; }).join('') + '</div>' : '') +
      '<div class="bottom"><div class="cell"><span>ISSUED</span><b>' + esc(issued) + '</b></div>' +
      '<div class="cell"><span>CREDENTIAL ID</span><b>' + esc(c.code) + '</b></div>' +
      '<div class="cell"><span>VERIFY</span><b>Product Expert register, #verify</b></div>' +
      '<div class="stampbox">' + PX.seal(110) + '</div></div>' +
      '</div>' + (c.status === 'revoked' ? '<div class="stamp">REVOKED</div>' : '') + '</div>';
  };
  PX.fitCert = function (wrap) {
    function fit() {
      var cert = wrap.querySelector('[data-cert]');
      if (!cert) return;
      var w = wrap.clientWidth || 1000, s = Math.min(1, w / 1000);
      cert.style.transform = 'scale(' + s + ')';
      wrap.style.height = Math.ceil(707 * s) + 'px';
    }
    fit();
    var ro = window.ResizeObserver ? new ResizeObserver(fit) : null;
    if (ro) ro.observe(wrap);
    window.addEventListener('resize', fit);
    setTimeout(fit, 60);
    return function () { window.removeEventListener('resize', fit); if (ro) ro.disconnect(); };
  };
})();
