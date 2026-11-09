# Product Expert

**Product Expert** is a free, senior-level training and certification site for product managers preparing to become a
**Director of Product**. Every basic (Scrum, Kanban, stories, specs, roadmaps, scoring models, funnels, MVPs) is packed
into one module; the other 31 modules go deep on what directors are judged on: strategy and moats, continuous discovery
and trustworthy experiments, metric trees, retention and growth accounting, pricing, positioning and launches, enterprise
and unit economics, org design, hiring and coaching managers, operating cadence, boards and CEOs, conflict and
transformation, AI products, platforms, regulation and technical trade-offs. It teaches through short sourced briefings,
spaced-repetition drills, "Director's call?" judgement calls, written leadership scenarios, in-browser labs, real case
files and self-assessed final exams with verifiable certificates. Built on [Anvil](https://anvil.works) as native Anvil
Forms (Python + HTML templates, a layout, custom components, RepeatingPanels).

- **App repo:** github.com/arkulinskis/productexpert (branch `master`). Anvil pulls `master`.
- **Live:** not published yet (waiting for the Anvil clone).
- **Sibling:** AI Expert (aiexpert). The learning engine (Learning/Exams/Credentials, Drill/Rubric components, labs
  frame, plans) was ported from it; content, look, hero, labs, cases and Library are new.

## What it does

**For everyone (no account needed):**
- **Landing page** (`#landing`): the hero is a before/after board (drag handle, keyboard too): the same quarter planned as
  a feature roadmap (eleven features with due dates across four teams) and as an outcome tree (one outcome, three customer
  opportunities, three tested bets). Then a "strong senior PM vs director of product" table, how learning works, the 8
  programs, the 5 labs, 3 case files, the sample certificate with a credential lookup, the Honour Roll and an honest FAQ
  (free, not accredited, no promotion promise).
- **Programs** (`#tracks`, `#tracks/<id>`): 8 programs x 4 modules + a capstone each:
  1. *Product Leadership Foundations* (core): the whole PM toolkit in one sitting; judgement and leverage; decision
     quality under uncertainty; writing that drives decisions.
  2. *Product Strategy* (str): good vs bad strategy; moats (7 Powers, network effects); disruption, jobs and aggregation;
     portfolios, horizons and honest roadmaps.
  3. *Discovery & Evidence* (dsc): continuous discovery; assumption testing and evidence strength; experimentation
     without fooling yourself; product-market fit measured honestly.
  4. *Metrics, Growth & Monetization* (grw): north stars and metric trees; retention and growth accounting; growth loops
     and PLG; pricing and packaging.
  5. *Business & Go-to-Market* (biz): positioning; launches and GTM motions; enterprise product leadership; unit economics
     and the P&L.
  6. *Building the Product Org* (org): org design and team topologies; hiring, levels and performance; coaching PMs and
     managing managers; operating cadence (planning, OKRs, reviews).
  7. *Executive Influence* (inf): stakeholders and managing up; the CEO, the exec team and the board; conflict and
     negotiation; leading change and transformation.
  8. *Frontier Product Leadership* (frn): leading AI products (evals, error analysis, human control); platforms, APIs and
     marketplaces; trust, ethics and regulation (GDPR, EU AI Act, dark patterns, accessibility); technical leverage
     (debt, DORA, SLOs).
  Foundations + any four specialist certificates earns the **Director of Product** credential.
- **Module briefings** (`#module/<id>`): the briefing, Do / Avoid, case files, sources, further reading from the
  Library, and a link to the module's lab where there is one.
- **Labs** (`#labs`, `#labs/<id>`), all in the browser (theme/assets/px-labs.js):
  - *Peeking simulator*: 200 A/A tests; daily peeking gives about 23% false winners, a fixed horizon or a sequential
    boundary brings it back near 5%.
  - *Metric tree builder*: weekly active teams from 5,000 toward 8,000 in 12 months with an 8-point effort budget across
    sign-ups (costly), activation, retention, invites and resurrection; a sensitivity table shows which lever compounds.
  - *Cohort and growth accounting lab*: shape the retention curve, acquisition and resurrection; beat the founder's
    buy-growth plan at month 24 with acquisition growth of 2% a month or less and a quick ratio of at least 1.3.
  - *Van Westendorp pricing lab*: 120 simulated answers to the four questions; read the curves, reveal the acceptable
    range (about $7-21), pick a price.
  - *Unit economics lab*: a self-serve segment vs mid-market; LTV, LTV:CAC, payback; reach 3:1 and payback under 12
    months.
- **The Library** (`#library`, `#library/<program>`): about 100 hand-picked resources (books, articles, papers, courses,
  talks, tools, standards and laws), each linking to the original, filterable by program, kind, free only, and searchable.
- **Case files** (`#cases`, `#cases/<id>`): 22 sourced cases (Sonos app relaunch, Unity Runtime Fee, Netflix Qwikster,
  Amazon Fire Phone, Google+, Quibi, Windows 8, Tropicana, New Coke, Slack, Superhuman, Bing's headline test,
  Booking.com, Threads, Adobe Creative Cloud, Shape Up, the "Spotify model", Airbnb and founder mode, Facebook News Feed,
  Klarna, CrowdStrike, Southwest), filterable by kind.
- **Verify a credential** (`#verify/<code>`) and **certificate pages** (`#certificate/<code>`), plus the Honour Roll.

**For members:**
- **Dashboard** (`#home`): rank (Associate PM → VP of Product) and XP, streak, drills due, this week of the study plan,
  exams ready, continue where you left off, every program's progress, credentials, case of the day, Honour Roll.
- **Study plan** (`#plan`): background (PM 3+ years, senior/group PM, design/eng/data leader, founder/GM), goal (become
  a director, lead my org better, prepare for senior interviews) and hours a week (3/5/8/12); every module and final exam
  scheduled week by week with dates; warm-up reading per background.
- **Drills** (`#study/review`, `#study/<module>`): recall cards and "Director's call?" judgements, Leitner boxes 0-6;
  keys Space / 1 / 2.
- **Challenges** (`#challenge/<id>`): a leadership scenario per module with real numbers; write your decision, compare
  with the model answer, tick the rubric (70% to pass).
- **Module completion** = briefing read + every drill learned + challenge ≥ 70%.
- **Final examination** (`#exam/<program>`): honour code, 12 recall items (80%) + the capstone (70%); pass → certificate
  `PXP-<CODE>-<YEAR>-<6 chars>`; Director of Product is issued automatically with Foundations + 4 specialist certificates.
- **Labs** record a member's first completion (+15 XP). **Reading list**: Save any Library resource.
- **Credentials** (`#credentials`), **Profile** (name on certificates, job title, Honour Roll opt-in, theme, password).

**For admins** (`#admin`; arkulinskis@gmail.com becomes admin on first sign-in): overview, credentials (search,
revoke/reinstate), feedback inbox (older messages), users, demo data (six fictional product leaders with progress and
certificates, marked as sample records).

## Setting it up in Anvil (once)

1. Anvil editor: **Create app → Clone from GitHub**, paste `https://github.com/arkulinskis/productexpert`.
2. Check the **Users** service (email + password, Continue with Google, sign-up on).
3. Accept the **Schema Mismatch** alert with **"The schema of the source code is correct"**.
4. Run it, sign up with the admin email first, then **Publish**.

<!-- libraries:start -->
## Libraries and outside services

What this project uses besides its own code. Generated by `APP_MAKER/tools/libraries.py`; to change it, edit `APP_MAKER/libraries/catalog.py` and re-run the script.

| Name | How it gets in | Used here for |
|---|---|---|
| [Google Fonts](https://fonts.google.com) | Loaded from a CDN | JetBrains Mono, Newsreader, Onest |
| [Anvil Uplink](https://anvil.works/docs/uplink) | Python package | Connects a Python program on any computer to an Anvil app, so each can call the other's functions. |

**Built into the browser:** localStorage, Clipboard.

**Anvil platform:** Anvil, Anvil Data Tables, Anvil JS bridge (anvil.js), Anvil Users, Anvil Google service.

**Build and test tools (not shipped):** axe-core, Node.js, Headless Chrome (DevTools Protocol), PyYAML.

<!-- libraries:end -->

## Working on it

See `.claude/skills/productexpert/SKILL.md`. In short:

```
python tools/check.py                    # Anvil's validator, JS syntax, asset hashes, server tests -> ALL CHECKS PASSED
python -I tools/ui_test.py               # the real app in the Anvil App Server (Docker) driven by headless Chrome
python -I tools/ui_test.py --shots DIR   # + screenshots of every page (desktop/phone, light/dark, guest/member)
git push origin master                   # deploy
```

## Project layout

```
client_code/    startup.py, router.py, state.py, auth.py, legal.py, px.py (helpers over the JS engines)
                Layouts/Shell; Pages: Landing, Auth, Home, Tracks, Module, Study, Challenge, Exam, Credentials, Certificate,
                Verify, Cases, Library, Labs, Plan, Profile, Admin; Components: Hero, BetBoard, LabStage, Drill, Rubric,
                Certificate, Seal, Ring, Bar; Items/* (cards and rows); Dialogs/LinkBox
server_code/    content_core.py (Foundations), content_strategy/discovery/growth/business/org/influence/frontier.py
                (the programs), content_cases.py (case files), content_library.py (the Library), Curriculum.py,
                Learning.py, Exams.py, Credentials.py, Labs.py, Plan.py, Accounts.py, Admin.py, DemoData.py, Feedback.py,
                common.py, SchemaCheck.py
theme/assets/   app.css (tokens + pages + role layer), px-kit.js (diagrams, bet board hero, stamp, certificate, ring,
                confetti), px-labs.js (the five labs), app-kit.js, icons.css (generated), theme.css (spinner), icon.svg + PNGs
tools/          check.py, assets.py, build_icons.py, make_icons.py, ui_test.py + ui/ (flow, phone, admin, exam, a11y, design, seed)
```

## Content rules

- Every factual claim is tied to a source listed in the module or case file (checked Nov 2026). Where reports disagree,
  the text says "about" or "reported", or leaves the number out. Where practitioners disagree (founder mode, OKRs,
  the Spotify model), the briefing says so.
- Regulation moves: the EU AI Act dates reflect the 2026 provisional Digital Omnibus agreement and are flagged as such;
  re-check before changing them.
- The Library links only to originals (authors, publishers, journals, official sites). Paid books are marked Paid and
  linked to the publisher or author; nothing is hosted.
- Lab numbers are fictional and labelled as simulations.
