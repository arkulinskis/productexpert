"""Interview Day (#loop): a timed, four-round mock director loop built from the module challenges.

Three loop formats (scale-up, startup, enterprise), each with the same four rounds: strategy case (20 min), metrics
and evidence (12), people leadership (12) and the CEO conversation (8). Each round draws one challenge from that
format's pool and is asked by a fictional interviewer. The timer is soft: the page shows it, the answer is accepted
late, and the minutes used are recorded. After the last round the debrief shows each round's model answer and rubric
(loop_debrief); the member ticks what they covered and finish_loop scores every round, records each written answer
as an attempt at its challenge (Learning._record_attempt, so it appears under that challenge and counts toward the
module) and gives a verdict from Strong hire to No hire yet, with the weakest round's module.

Table loops: user, fmt, rounds (obj: [{kind, title, minutes, challenge, persona, answer, seconds, submitted, points,
score}]), started, finished, verdict, score, is_demo. Only the owner can open, answer or finish a loop.
"""
import random

import anvil.server
import anvil.tables as tables
from anvil.tables import app_tables

from . import common as C
from . import Curriculum as K

ROUNDS = [("strategy", "Strategy case", 20), ("metrics", "Metrics and evidence", 12), ("people", "People leadership", 12),
          ("ceo", "The CEO conversation", 8)]
LOOPS = {
    "scaleup": {
        "title": "Scale-up loop", "company": "Series C B2B software company, 400 people, growth slowing",
        "blurb": "The classic director loop: a defended strategy case, a metrics deep dive, a people round and 8 minutes with the CEO.",
        "rounds": {
            "strategy": (("Maya Lindqvist", "VP of Product, your future manager",
                          "Here's a real situation from a company like ours. Think out loud, then commit to a call."),
                         ["ch-str-kernel", "ch-str-moats", "ch-str-portfolio", "ch-biz-positioning"]),
            "metrics": (("Arjun Patel", "Head of Data Science",
                         "I care less about the formula than whether you'd trust the number. Walk me through it."),
                        ["ch-grw-northstar", "ch-grw-retention", "ch-dsc-experiments"]),
            "people": (("Sofia Reyes", "VP of Engineering",
                        "You'd run a group of PMs who work closely with my teams. How do you handle this?"),
                       ["ch-org-design", "ch-org-coaching", "ch-org-cadence"]),
            "ceo": (("Daniel Okafor", "CEO and co-founder",
                     "I've got eight minutes. Give me your recommendation first, then the why."),
                    ["ch-inf-exec", "ch-inf-conflict", "ch-core-writing"]),
        },
    },
    "startup": {
        "title": "Startup loop", "company": "Series A product, 45 people, first product leader hire",
        "blurb": "Fewer people, less data, more ambiguity: fit, focus, pricing and a founder who still owns the vision.",
        "rounds": {
            "strategy": (("Lena Fischer", "Co-founder and CEO",
                          "We can't do everything. Tell me where you'd focus us and what you'd say no to."),
                         ["ch-str-dynamics", "ch-dsc-pmf", "ch-dsc-assumptions", "ch-biz-economics"]),
            "metrics": (("Tom Achterberg", "Head of Growth (team of two)",
                         "Our numbers are small and noisy. How would you read this and what would you do?"),
                        ["ch-grw-loops", "ch-grw-retention", "ch-grw-pricing"]),
            "people": (("Priyanka Shah", "CTO and co-founder",
                        "You'd be hiring the product team from scratch alongside me. How do you handle this one?"),
                       ["ch-org-talent", "ch-core-decisions", "ch-org-coaching"]),
            "ceo": (("Lena Fischer", "Co-founder and CEO, again",
                     "Last one. I have strong opinions about the product. Change my mind, or don't."),
                    ["ch-inf-exec", "ch-biz-launch", "ch-core-judgement"]),
        },
    },
    "enterprise": {
        "title": "Enterprise loop", "company": "Public software company, 6,000 people, a portfolio of products",
        "blurb": "Portfolio choices, big deals, platform debt, change across many teams and a sceptical executive committee.",
        "rounds": {
            "strategy": (("Catherine Moreau", "SVP of Product, your future manager",
                          "You'd own a portfolio here. Show me how you'd make the hard allocation call."),
                         ["ch-str-portfolio", "ch-biz-enterprise", "ch-frn-tech", "ch-str-moats"]),
            "metrics": (("Rahul Mehta", "Director of Analytics",
                         "Finance will check every number you put in front of them. Talk me through yours."),
                        ["ch-grw-pricing", "ch-core-toolkit", "ch-grw-northstar"]),
            "people": (("Grace Adeyemi", "Chief People Officer",
                        "Most of your org was here before you. How do you lead through this?"),
                       ["ch-org-design", "ch-inf-change", "ch-org-cadence"]),
            "ceo": (("Henrik Sandberg", "Chief Operating Officer",
                     "The executive committee meets in ten minutes. What do I tell them, and why?"),
                    ["ch-inf-stakeholders", "ch-frn-ai", "ch-frn-trust"]),
        },
    },
}
ORDER = ["scaleup", "startup", "enterprise"]
VERDICTS = ["Strong hire", "Hire", "Lean no hire", "No hire yet"]
MIN_ANSWER = 40


def verdict_for(scores):
    """Round scores (0-100) -> (verdict, average)."""
    avg = int(round(sum(scores) / float(len(scores)))) if scores else 0
    low = min(scores) if scores else 0
    if avg >= 85 and low >= 70:
        return VERDICTS[0], avg
    if avg >= 70 and low >= 50:
        return VERDICTS[1], avg
    if avg >= 50:
        return VERDICTS[2], avg
    return VERDICTS[3], avg


def formats_public():
    out = []
    for fid in ORDER:
        f = LOOPS[fid]
        out.append({"id": fid, "title": f["title"], "company": f["company"], "blurb": f["blurb"],
                    "minutes": sum(r[2] for r in ROUNDS),
                    "rounds": [{"kind": kind, "title": title, "minutes": mins, "who": f["rounds"][kind][0][0],
                                "role": f["rounds"][kind][0][1]} for kind, title, mins in ROUNDS]})
    return out


def _stage(rounds, finished):
    if finished:
        return "done", len(rounds)
    for i, r in enumerate(rounds):
        if not r.get("submitted"):
            return "round", i
    return "debrief", len(rounds)


def _ch_brief(cid, with_model=False):
    ch = K.CHALLENGES[cid]
    m = K.MODULES[ch["module"]]
    out = {"id": cid, "title": ch["title"], "situation": ch["situation"], "ask": ch["ask"], "fig": ch.get("fig") or "director",
           "module": m["id"], "module_title": m["title"]}
    if with_model:
        out["model"] = ch["model"]
        out["rubric"] = list(ch["rubric"])
    return out


def loop_public(row, with_models=False):
    rounds = list(row["rounds"] or [])
    stage, current = _stage(rounds, row["finished"])
    f = LOOPS.get(row["fmt"]) or LOOPS["scaleup"]
    show_models = with_models or stage == "done"
    out_rounds = []
    for i, r in enumerate(rounds):
        x = {"i": i, "kind": r["kind"], "title": r["title"], "minutes": r["minutes"], "persona": r["persona"],
             "submitted": bool(r.get("submitted")), "seconds": int(r.get("seconds") or 0)}
        # the challenge itself shows only from the round it's asked in (no peeking at later rounds)
        if i <= current or stage != "round":
            x["challenge"] = _ch_brief(r["challenge"], with_model=show_models and stage != "round")
            x["answer"] = r.get("answer") or ""
        if stage == "done":
            x["score"] = int(r.get("score") or 0)
            x["points"] = list(r.get("points") or [])
        out_rounds.append(x)
    out = {"id": row.get_id(), "fmt": row["fmt"], "title": f["title"], "company": f["company"], "stage": stage, "current": current,
           "started": C.iso(row["started"]), "finished": C.iso(row["finished"]), "rounds": out_rounds,
           "verdict": row["verdict"], "score": int(row["score"] or 0) if row["finished"] else None}
    if stage == "done" and rounds:
        weakest = min(range(len(rounds)), key=lambda j: int(rounds[j].get("score") or 0))
        ch = K.CHALLENGES[rounds[weakest]["challenge"]]
        m = K.MODULES[ch["module"]]
        out["weakest"] = {"round": rounds[weakest]["title"], "module": m["id"], "module_title": m["title"],
                          "challenge": ch["id"], "score": int(rounds[weakest].get("score") or 0)}
    return out


def _own(loop_id, me):
    row = C.row_by_id(app_tables.loops, loop_id)
    if row is None or row["user"] != me:
        return None
    return row


@anvil.server.callable(require_user=True)
def get_loops():
    """The loop formats and the member's past loops (newest first)."""
    me = C.require_user()
    rows = app_tables.loops.search(tables.order_by("started", ascending=False), user=me)
    mine = []
    for row in rows:
        stage, current = _stage(list(row["rounds"] or []), row["finished"])
        mine.append({"id": row.get_id(), "title": (LOOPS.get(row["fmt"]) or LOOPS["scaleup"])["title"], "stage": stage,
                     "current": current, "started": C.iso(row["started"]), "verdict": row["verdict"],
                     "score": int(row["score"] or 0) if row["finished"] else None})
        if len(mine) >= 12:
            break
    return {"formats": formats_public(), "mine": mine}


@anvil.server.callable(require_user=True)
def start_loop(fmt):
    me = C.require_user()
    f = LOOPS.get(fmt)
    if f is None:
        return C.fail("That loop format doesn't exist.")
    if C.rate_limited("loop_start", 10, 3600):
        return C.fail("That's a lot of loops in one hour. Take a break and come back.")
    recent = set()
    for row in app_tables.loops.search(tables.order_by("started", ascending=False), user=me):
        for r in row["rounds"] or []:
            recent.add(r.get("challenge"))
        if len(recent) > 24:
            break
    rounds = []
    for kind, title, mins in ROUNDS:
        persona, pool = f["rounds"][kind]
        fresh = [cid for cid in pool if cid not in recent and cid in K.CHALLENGES]
        cid = random.choice(fresh or pool)
        rounds.append({"kind": kind, "title": title, "minutes": mins, "challenge": cid,
                       "persona": {"name": persona[0], "role": persona[1], "line": persona[2]},
                       "answer": "", "seconds": 0, "submitted": False, "points": [], "score": 0})
    row = app_tables.loops.add_row(user=me, fmt=fmt, rounds=rounds, started=C.now(), finished=None, verdict=None, score=0,
                                   is_demo=False)
    return C.ok(id=row.get_id())


@anvil.server.callable(require_user=True)
def get_loop(loop_id):
    me = C.require_user()
    row = _own(loop_id, me)
    if row is None:
        return C.fail("That interview loop isn't yours, or it was deleted.")
    return C.ok(loop=loop_public(row))


@anvil.server.callable(require_user=True)
def submit_loop_round(loop_id, index, answer, seconds):
    """Hand in the current round (late is fine: the timer is soft). Short or empty answers are kept but score 0."""
    me = C.require_user()
    row = _own(loop_id, me)
    if row is None:
        return C.fail("That interview loop isn't yours, or it was deleted.")
    rounds = list(row["rounds"] or [])
    stage, current = _stage(rounds, row["finished"])
    if stage != "round" or index != current:
        return C.ok(loop=loop_public(row))  # already handed in (a double click or a second tab): show where it is
    r = dict(rounds[current])
    try:
        secs = int(seconds or 0)
    except Exception:
        secs = 0
    r.update(answer=C.text(answer, 6000, multiline=True), seconds=max(0, min(secs, r["minutes"] * 60 * 3)), submitted=True)
    rounds[current] = r
    row["rounds"] = rounds
    return C.ok(loop=loop_public(row))


@anvil.server.callable(require_user=True)
def loop_debrief(loop_id):
    """After the last round: every round with its model answer and rubric."""
    me = C.require_user()
    row = _own(loop_id, me)
    if row is None:
        return C.fail("That interview loop isn't yours, or it was deleted.")
    stage, _current = _stage(list(row["rounds"] or []), row["finished"])
    if stage == "round":
        return C.fail("Finish every round first.")
    return C.ok(loop=loop_public(row, with_models=True))


@anvil.server.callable(require_user=True)
def finish_loop(loop_id, points, client_day=None):
    """Score each round from the rubric ticks, record the answers as challenge attempts and give the verdict."""
    from .Learning import _record_attempt, score_points, today
    me = C.require_user()
    row = _own(loop_id, me)
    if row is None:
        return C.fail("That interview loop isn't yours, or it was deleted.")
    rounds = list(row["rounds"] or [])
    stage, _current = _stage(rounds, row["finished"])
    if stage == "round":
        return C.fail("Finish every round first.")
    if stage == "done":
        return C.ok(loop=loop_public(row), xp_gained=0)
    if not isinstance(points, (list, tuple)):
        points = []
    row["finished"] = C.now()  # first, so a double click can't record the attempts twice
    day = today(client_day)
    scores, gained = [], 0
    for i, r in enumerate(rounds):
        r = dict(r)
        ch = K.CHALLENGES[r["challenge"]]
        ticks = points[i] if i < len(points) else []
        if len((r.get("answer") or "").strip()) >= MIN_ANSWER:
            res = _record_attempt(me, ch, r["answer"], ticks, day)
            r["score"], r["points"] = res["score"], score_points(ticks, len(ch["rubric"]))[0]
            gained += res["xp_gained"]
        else:
            r["score"], r["points"] = 0, [False] * len(ch["rubric"])
        scores.append(r["score"])
        rounds[i] = r
    verdict, avg = verdict_for(scores)
    row.update(rounds=rounds, verdict=verdict, score=avg)
    return C.ok(loop=loop_public(row), xp_gained=gained)


def latest(user):
    """The member's most recent finished loop (dashboard), or None."""
    for row in app_tables.loops.search(tables.order_by("started", ascending=False), user=user):
        if row["finished"]:
            return {"id": row.get_id(), "title": (LOOPS.get(row["fmt"]) or LOOPS["scaleup"])["title"], "verdict": row["verdict"],
                    "score": int(row["score"] or 0), "finished": C.iso(row["finished"])}
    return None
