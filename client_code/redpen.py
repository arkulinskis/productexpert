"""Red Pen: rule-based margin notes on a strategy one-pager or an outcome roadmap (Red Pen Studio, #studio).

Pure Python with no imports, so the SAME rules run in the browser (instant notes; "My own" mode never calls the
server) and on the server (Studio.save_studio_doc rescores what it stores). No AI: every note is a rule with a
source. Keep it Skulpt-safe: no re, no comprehension variables named like module-level names.

    blank(kind)                 an empty doc: "strategy" = {field: text}, "roadmap" = {"now"|"next"|"later": [card]}
    clean(kind, doc)            the doc trimmed to the known fields and lengths (server and client both use it)
    grade(kind, doc)            {"score": 0-100, "grade": "A".."D", "notes": [note], "majors", "minors"}
                                note = {"id", "level": "major"|"minor"|"good", "field", "field_label", "title", "text",
                                        "source": {"label", "url"}, "module": module id or None}
    to_markdown(kind, title, doc, result, brief=None)   the doc + its notes as Markdown (download, print)
"""

STRATEGY_FIELDS = [
    ("diagnosis", "Diagnosis", "What is the critical challenge, and what evidence shows it?"),
    ("policy", "Guiding policy", "Your overall approach to that challenge. It should rule options out."),
    ("actions", "Coherent actions", "One per line: the coordinated steps that carry out the policy."),
    ("will_not", "We will not", "One per line: what you are choosing not to do."),
    ("measures", "Measures", "One per line: how you will know it is working."),
    ("risk", "Risks and signals to revisit", "What could prove you wrong, and what would make you change course?"),
]
ROADMAP_COLS = [("now", "Now"), ("next", "Next"), ("later", "Later")]
CARD_FIELDS = [("problem", "Problem"), ("bet", "Bet"), ("evidence", "Evidence"), ("measure", "Measure")]
MAX_CARDS = 4
FIELD_MAX = 1500
CARD_MAX = 300

SRC = {
    "rumelt": {"label": "Richard Rumelt: The perils of bad strategy (McKinsey Quarterly)",
               "url": "https://www.mckinsey.com/capabilities/strategy-and-corporate-finance/our-insights/the-perils-of-bad-strategy"},
    "porter": {"label": "Michael Porter: What is strategy? (Harvard Business Review, 1996)",
               "url": "https://hbr.org/1996/11/what-is-strategy"},
    "martin": {"label": "Roger Martin: strategy as choices with real opposites", "url": "https://rogerlmartin.com/"},
    "outcomes": {"label": "Userpilot: outcome-based roadmaps", "url": "https://userpilot.com/blog/outcome-based-roadmap/"},
    "timelines": {"label": "Product Talk: roadmaps with timelines", "url": "https://www.producttalk.org/roadmaps-with-timelines/"},
    "nnl": {"label": "ProdPad: Now-Next-Later roadmaps (Janna Bastow)", "url": "https://www.prodpad.com/"},
}

BUZZWORDS = ["synergy", "synergies", "world class", "best in class", "customer centric", "leverage", "holistic",
             "seamless", "seamlessly", "empower", "empowering", "next generation", "cutting edge", "innovative",
             "disrupt", "disruptive", "game changing", "game changer", "revolutionize", "revolutionise", "paradigm",
             "all in one", "robust", "end to end", "frictionless", "ai powered", "one stop shop", "best of breed",
             "future of work", "unlock value", "move the needle", "north star of excellence"]
GOAL_PHRASES = ["become the leading", "become the number one", "become the 1", "be the number one", "be the leading",
                "market leader", "category leader", "all in one", "become the go to", "become the premier",
                "become the most", "be the most", "dominate"]
GROWTH_VERBS = ["grow", "increase", "reach", "hit", "achieve", "double", "triple", "exceed", "deliver"]
TARGET_WORDS = ["arr", "mrr", "revenue", "bookings", "valuation", "market share"]
EXCLUDE_WORDS = ["not", "rather", "instead", "only", "over", "without", "exclude", "excluding", "never", "focus",
                 "focused", "concentrate", "except", "unlike", "no"]
EVIDENCE_WORDS = ["because", "since", "data", "win", "churn", "retention", "segment", "customers", "interviews",
                  "survey", "rate", "rates", "cohort", "losing", "lose", "slowed", "dropped", "fell", "grew", "while"]
OUTPUT_WORDS = ["ship", "ships", "shipped", "shipping", "launch", "launched", "launches", "release", "released",
                "deliver", "delivered", "build", "built", "complete", "completed", "done", "finish", "finished",
                "features", "feature", "deploy", "deployed", "live", "v2", "v3", "milestone", "milestones"]
OUTCOME_WORDS = ["retention", "retain", "churn", "renewal", "renewals", "conversion", "convert", "activation",
                 "activated", "adoption", "adopt", "active", "actives", "usage", "use", "win", "nrr", "revenue",
                 "margin", "satisfaction", "nps", "csat", "minutes", "hours", "saved", "cost", "tickets", "rate",
                 "engagement", "repeat", "payback", "ltv", "time", "share", "accounts", "customers", "users", "teams"]
MONTHS = ["january", "february", "march", "april", "june", "july", "august", "september", "october", "november",
          "december", "jan", "feb", "apr", "jun", "jul", "aug", "sep", "sept", "oct", "nov", "dec"]
DATE_WORDS = ["q1", "q2", "q3", "q4", "eoy", "eom", "eoq", "deadline"]
LEVEL_COST = {"major": 16, "minor": 7, "good": 0}


# ------------------------------------------------------------------------------------------- text helpers
def _s(v, limit):
    s = "" if v is None else str(v)
    s = s.replace("\r\n", "\n").strip()
    return s[:limit]


def _norm(text):
    """Lower case, punctuation (incl. hyphens) to spaces, padded: ' all in one people platform '."""
    out = []
    for ch in (text or "").lower():
        if ch.isalnum() or ch in "%$#":
            out.append(ch)
        else:
            out.append(" ")
    return " " + " ".join("".join(out).split()) + " "


def _words(text):
    return _norm(text).split()


def _has_phrase(norm, phrases):
    found = []
    for ph in phrases:
        if (" " + ph + " ") in norm and ph not in found:
            found.append(ph)
    return found


def _has_word(words, vocab):
    for w in words:
        if w in vocab:
            return True
    return False


def _has_digit(text):
    for ch in text or "":
        if ch.isdigit():
            return True
    return False


def _lines(text):
    out = []
    for line in (text or "").split("\n"):
        line = line.strip().lstrip("-*•0123456789.) ").strip()
        if line:
            out.append(line)
    return out


def _has_date(text):
    """Calendar commitments: months, quarters, years, 15/03-style dates, 'sprint 14', 'week 12', 'may 3'."""
    words = _words(text)
    for i, w in enumerate(words):
        if w in MONTHS or w in DATE_WORDS:
            return True
        if len(w) == 4 and w.isdigit() and "2020" <= w <= "2039":
            return True
        nxt = words[i + 1] if i + 1 < len(words) else ""
        if w in ("may", "sprint", "week", "by") and nxt.isdigit():
            return True
    raw = text or ""
    for i in range(1, len(raw) - 1):
        if raw[i] == "/" and raw[i - 1].isdigit() and raw[i + 1].isdigit():
            return True
    return False


def _is_output(text):
    words = _words(text)
    if not words:
        return False
    if "%" in (text or ""):
        return False
    return _has_word(words, OUTPUT_WORDS) and not _has_word(words, OUTCOME_WORDS)


def _is_goal(text):
    norm = _norm(text)
    if _has_phrase(norm, GOAL_PHRASES):
        return True
    words = norm.split()
    has_num = _has_digit(text)
    if has_num and ("%" in text or "$" in text or _has_word(words, TARGET_WORDS)):
        return True
    if has_num and _has_word(words, GROWTH_VERBS):
        return True
    return False


# ------------------------------------------------------------------------------------------- docs
def blank(kind):
    if kind == "roadmap":
        return {"now": [blank_card()], "next": [blank_card()], "later": [blank_card()]}
    out = {}
    for key, _label, _hint in STRATEGY_FIELDS:
        out[key] = ""
    return out


def blank_card():
    return {"problem": "", "bet": "", "evidence": "", "measure": ""}


def _card_empty(card):
    for key, _label in CARD_FIELDS:
        if card.get(key):
            return False
    return True


def clean(kind, doc):
    doc = doc if isinstance(doc, dict) else {}
    if kind == "roadmap":
        out = {}
        for col, _label in ROADMAP_COLS:
            cards = doc.get(col) if isinstance(doc.get(col), (list, tuple)) else []
            kept = []
            for card in cards[:MAX_CARDS]:
                card = card if isinstance(card, dict) else {}
                c = {}
                for key, _l in CARD_FIELDS:
                    c[key] = _s(card.get(key), CARD_MAX)
                kept.append(c)
            out[col] = kept
        return out
    out = {}
    for key, _label, _hint in STRATEGY_FIELDS:
        out[key] = _s(doc.get(key), FIELD_MAX)
    return out


def _label(kind, field):
    if kind == "roadmap":
        for col, label in ROADMAP_COLS:
            if col == field:
                return label
        return "Whole roadmap"
    for key, label, _hint in STRATEGY_FIELDS:
        if key == field:
            return label
    return "Whole document"


def _note(kind, nid, level, field, title, text, src, module=None):
    return {"id": nid, "level": level, "field": field, "field_label": _label(kind, field), "title": title,
            "text": text, "source": dict(SRC[src]) if src else None, "module": module}


def _join(items):
    items = list(items)
    if len(items) <= 1:
        return "".join(items)
    return ", ".join(items[:-1]) + " and " + items[-1]


# ------------------------------------------------------------------------------------------- rules: strategy
def _strategy_notes(doc):
    k = "strategy"
    notes = []
    diag = doc.get("diagnosis") or ""
    dw = _words(diag)
    if not dw:
        notes.append(_note(k, "diag-missing", "major", "diagnosis", "No diagnosis",
                           "Start with the critical challenge. Without a diagnosis, the rest is a wish list: Rumelt calls "
                           "this failing to face the challenge.", "rumelt", "str-kernel"))
    elif len(dw) < 20:
        notes.append(_note(k, "diag-thin", "major", "diagnosis", "Thin diagnosis",
                           "%d words is a slogan, not a diagnosis. Name what is actually hard, for whom, and why now." % len(dw),
                           "rumelt", "str-kernel"))
    if dw and not _has_digit(diag) and not _has_word(dw, EVIDENCE_WORDS):
        notes.append(_note(k, "diag-evidence", "minor", "diagnosis", "Diagnosis without evidence",
                           "Back the challenge with something checkable: win rates by segment, churn, a cohort, what "
                           "customers said.", "rumelt", "str-kernel"))
    if len(dw) >= 20 and (_has_digit(diag) or _has_word(dw, EVIDENCE_WORDS)):
        notes.append(_note(k, "diag-ok", "good", "diagnosis", "The diagnosis faces the challenge",
                           "It names a specific problem and gives evidence for it.", "rumelt"))

    pol = doc.get("policy") or ""
    pw = _words(pol)
    wont = _lines(doc.get("will_not"))
    excludes = _has_word(pw, EXCLUDE_WORDS)
    if not pw:
        notes.append(_note(k, "pol-missing", "major", "policy", "No guiding policy",
                           "Say how you will deal with the challenge: the approach that makes some options obviously "
                           "out of bounds.", "rumelt", "str-kernel"))
    elif _is_goal(pol):
        notes.append(_note(k, "pol-goal", "major", "policy", "A goal posing as a policy",
                           "A target or an ambition ('grow ARR 50%', 'become the leading platform') says where you want "
                           "to be, not how you will get there. Mistaking goals for strategy is a classic hallmark of bad "
                           "strategy.", "rumelt", "str-kernel"))
    if pw and not excludes and not wont:
        notes.append(_note(k, "pol-choice", "minor", "policy", "A policy that rules nothing out",
                           "A real choice has an opposite a sensible competitor could pick. Name the segment, the way to "
                           "win, or the option you are rejecting.", "martin", "str-kernel"))
    elif pw and not _is_goal(pol) and (excludes or wont):
        notes.append(_note(k, "pol-ok", "good", "policy", "A policy with a real choice in it",
                           "It points somewhere specific and leaves options out.", "martin"))

    acts = _lines(doc.get("actions"))
    if len(acts) < 2:
        notes.append(_note(k, "act-few", "major", "actions", "Too few actions",
                           "%s. A policy needs at least two coordinated steps that carry it out and reinforce each other."
                           % ("No actions yet" if not acts else "One action"), "rumelt", "str-kernel"))
    elif len(acts) > 5:
        notes.append(_note(k, "act-list", "major", "actions", "A list, not a strategy",
                           "%d actions of equal weight is a to-do list. Keep the two to five that reinforce each other; "
                           "move the rest to 'We will not' or to the teams." % len(acts), "rumelt", "str-portfolio"))
    else:
        notes.append(_note(k, "act-ok", "good", "actions", "A focused set of actions",
                           "%d actions: few enough to coordinate." % len(acts), "rumelt"))

    if not wont:
        notes.append(_note(k, "wont-missing", "major", "will_not", "Nothing you will not do",
                           "The essence of strategy is choosing what not to do. Write the two or three things a "
                           "reasonable team might expect you to do, which you won't.", "porter", "str-portfolio"))
    else:
        notes.append(_note(k, "wont-ok", "good", "will_not", "Explicit trade-offs",
                           "%d thing%s you will not do." % (len(wont), "" if len(wont) == 1 else "s"), "porter"))

    meas = _lines(doc.get("measures"))
    outs = []
    for line in meas:
        if _is_output(line):
            outs.append(line)
    if not meas:
        notes.append(_note(k, "meas-missing", "major", "measures", "No measures",
                           "How will you know the strategy is working? Name the customer or business outcomes you expect "
                           "to move.", "outcomes", "grw-northstar"))
    elif outs:
        notes.append(_note(k, "meas-output", "major", "measures", "Measures that are outputs",
                           "%s count%s what you ship, not what changes for customers or the business. Measure the "
                           "outcome the work is for (retention, win rate, time to value)." %
                           (_join(["'" + o + "'" for o in outs[:3]]), "s" if len(outs) == 1 else ""), "outcomes", "grw-northstar"))
    else:
        notes.append(_note(k, "meas-ok", "good", "measures", "Outcome measures",
                           "They describe a change in behaviour or results, not a delivery.", "outcomes"))

    risk = doc.get("risk") or ""
    if len(_words(risk)) < 4:
        notes.append(_note(k, "risk-missing", "minor", "risk", "No risks or signals to revisit",
                           "A falsifiable strategy says what evidence would make you change it. Name one or two "
                           "signals and when you will look.", "rumelt", "str-kernel"))
    else:
        notes.append(_note(k, "risk-ok", "good", "risk", "You know what would change your mind",
                           "Signals to revisit make the strategy falsifiable.", "rumelt"))

    allnorm = ""
    for key, _label, _hint in STRATEGY_FIELDS:
        allnorm += _norm(doc.get(key) or "")
    buzz = _has_phrase(allnorm, BUZZWORDS)
    if buzz:
        notes.append(_note(k, "fluff", "major" if len(buzz) >= 3 else "minor", "", "Fluff",
                           "Impressive words with no content: %s. Replace each with the specific thing you mean." %
                           _join(["'" + b + "'" for b in buzz[:6]]), "rumelt", "str-kernel"))
    return notes


# ------------------------------------------------------------------------------------------- rules: roadmap
def _roadmap_notes(doc):
    k = "roadmap"
    notes = []
    cols = {}
    for col, _label in ROADMAP_COLS:
        kept = []
        for card in doc.get(col) or []:
            if not _card_empty(card):
                kept.append(card)
        cols[col] = kept
    total = len(cols["now"]) + len(cols["next"]) + len(cols["later"])
    if total == 0:
        notes.append(_note(k, "rm-empty", "major", "", "An empty roadmap",
                           "Add at least one bet to Now: the problem, your bet, the evidence and the measure.", "nnl"))
        return notes
    if not cols["now"]:
        notes.append(_note(k, "now-empty", "major", "now", "Nothing in Now",
                           "Now is what teams are working on this quarter. Without it, the roadmap can't guide anyone.",
                           "nnl", "core-toolkit"))
    dated = []
    for col in ("next", "later"):
        for card in cols[col]:
            text = " ".join([card.get(key) or "" for key, _l in CARD_FIELDS])
            if _has_date(text):
                if col not in dated:
                    dated.append(col)
    if dated:
        notes.append(_note(k, "rm-dates", "major", dated[0], "Dates beyond Now",
                           "%s carr%s calendar dates. Promising dates for work you haven't discovered yet turns guesses "
                           "into commitments; keep dates for Now, or for the few commitments you've earned with "
                           "discovery." % (_join([c.capitalize() for c in dated]), "ies" if len(dated) == 1 else "y"),
                           "timelines", "core-toolkit"))
    elif cols["next"] or cols["later"]:
        notes.append(_note(k, "rm-nodates", "good", "next", "No false dates",
                           "Next and Later describe intent, not deadlines.", "timelines"))

    no_evidence, no_problem, no_measure, outputs, bets = 0, 0, 0, 0, 0
    for col, _label in ROADMAP_COLS:
        for card in cols[col]:
            has_bet = len(_words(card.get("bet"))) > 0
            if not has_bet:
                continue
            bets += 1
            if len(_words(card.get("evidence"))) < 3:
                no_evidence += 1
            if len(_words(card.get("problem"))) < 3:
                no_problem += 1
            m = card.get("measure") or ""
            if not _words(m):
                no_measure += 1
            elif _is_output(m) or _has_date(m) and not _has_word(_words(m), OUTCOME_WORDS):
                outputs += 1
    if bets == 0:
        notes.append(_note(k, "rm-nobets", "minor", "now", "Problems with no bets yet",
                           "Fine for Later; Now and Next need a bet the team is making.", "nnl"))
    if no_evidence:
        notes.append(_note(k, "rm-evidence", "major" if no_evidence >= 2 else "minor", "", "Bets with no evidence",
                           "%d of %d bet%s give%s no evidence. Say what you've seen (interviews, data, a test) that makes "
                           "this bet worth the team's time." % (no_evidence, bets, "" if bets == 1 else "s",
                                                                "s" if no_evidence == 1 else ""), "outcomes", "dsc-assumptions"))
    elif bets:
        notes.append(_note(k, "rm-evidence-ok", "good", "", "Every bet shows its evidence",
                           "Each bet says why it's worth making.", "outcomes"))
    if no_problem:
        notes.append(_note(k, "rm-problem", "minor", "", "Solutions without a problem",
                           "%d bet%s name%s a feature but not the customer problem it solves. Lead with the problem, so "
                           "the team can find a better solution." % (no_problem, "" if no_problem == 1 else "s",
                                                                      "s" if no_problem == 1 else ""), "nnl", "dsc-continuous"))
    if outputs:
        notes.append(_note(k, "rm-output", "major", "", "Measures that are outputs",
                           "%d measure%s count%s delivery ('ship it', 'launched', a date). Measure the change you expect "
                           "in customer behaviour or the business." % (outputs, "" if outputs == 1 else "s",
                                                                      "s" if outputs == 1 else ""), "outcomes", "grw-northstar"))
    if no_measure:
        notes.append(_note(k, "rm-nomeasure", "minor", "", "Bets with no measure",
                           "%d bet%s ha%s no measure. How will you know it worked?" % (no_measure, "" if no_measure == 1 else "s",
                                                                                     "s" if no_measure == 1 else "ve"),
                           "outcomes", "grw-northstar"))
    if bets and not outputs and not no_measure:
        notes.append(_note(k, "rm-measure-ok", "good", "", "Outcome measures",
                           "Every bet is judged by what changes, not by what ships.", "outcomes"))

    allnorm = ""
    for col, _label in ROADMAP_COLS:
        for card in cols[col]:
            for key, _l in CARD_FIELDS:
                allnorm += _norm(card.get(key) or "")
    buzz = _has_phrase(allnorm, BUZZWORDS)
    if buzz:
        notes.append(_note(k, "rm-fluff", "minor", "", "Fluff",
                           "Impressive words with no content: %s." % _join(["'" + b + "'" for b in buzz[:6]]), "rumelt"))
    return notes


# ------------------------------------------------------------------------------------------- grade
def grade(kind, doc):
    doc = clean(kind, doc)
    notes = _roadmap_notes(doc) if kind == "roadmap" else _strategy_notes(doc)
    score = 100
    majors, minors = 0, 0
    for n in notes:
        score -= LEVEL_COST[n["level"]]
        if n["level"] == "major":
            majors += 1
        elif n["level"] == "minor":
            minors += 1
    score = max(0, min(100, score))
    letter = "A" if score >= 85 else "B" if score >= 70 else "C" if score >= 50 else "D"
    order = {"major": 0, "minor": 1, "good": 2}
    notes = sorted(notes, key=lambda n: order[n["level"]])
    return {"score": score, "grade": letter, "notes": notes, "majors": majors, "minors": minors}


def passing(result):
    return result.get("grade") in ("A", "B")


# ------------------------------------------------------------------------------------------- markdown
def to_markdown(kind, title, doc, result, brief=None):
    doc = clean(kind, doc)
    out = ["# " + (title or ("Strategy one-pager" if kind == "strategy" else "Outcome roadmap")), ""]
    if brief:
        out += ["> " + brief, ""]
    if kind == "roadmap":
        for col, label in ROADMAP_COLS:
            out += ["## " + label, ""]
            cards = []
            for card in doc.get(col) or []:
                if not _card_empty(card):
                    cards.append(card)
            if not cards:
                out += ["(nothing yet)", ""]
            for card in cards:
                out.append("- **" + (card.get("bet") or card.get("problem") or "Untitled") + "**")
                for key, label2 in CARD_FIELDS:
                    if card.get(key):
                        out.append("  - " + label2 + ": " + card[key].replace("\n", " "))
            out.append("")
    else:
        for key, label, _hint in STRATEGY_FIELDS:
            out += ["## " + label, "", doc.get(key) or "(empty)", ""]
    if result:
        out += ["---", "", "## Red pen: %s (%d/100)" % (result["grade"], result["score"]), ""]
        for n in result["notes"]:
            tag = {"major": "MAJOR", "minor": "minor", "good": "good"}[n["level"]]
            line = "- [%s] **%s** (%s): %s" % (tag, n["title"], n["field_label"], n["text"])
            if n.get("source"):
                line += " Source: [%s](%s)" % (n["source"]["label"], n["source"]["url"])
            out.append(line)
        out += ["", "Marked by Product Expert's Red Pen Studio (rule-based, no AI): https://productexpert.anvil.app/#studio"]
    return "\n".join(out) + "\n"
