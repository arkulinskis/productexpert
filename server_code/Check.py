"""The Director Readiness Check (#check): 16 "would a director do this?" statements, two per program, open to anyone.

How it stays honest: get_check() deals the statements WITHOUT their verdicts. Each answer goes to reveal_check(),
which records the FIRST answer for that statement in the server session and only then returns the verdict and the
why. save_check() rescores from those recorded answers (the answers the browser sends are only cross-checked), so a
tampered request can't fake 16/16. The result gets a short public code: #check/<code> shows it to anyone, without
any user fields. Signed-in people keep their results (my_checks, latest() on the dashboard); a guest's code can be
claimed after signing up (claim_check).

Table checks: code, user (None for guests), score (0-16), by_track {track: 0-2}, missed [item ids], created, is_demo.
"""
import random

import anvil.server
import anvil.tables as tables
from anvil.tables import app_tables

from . import common as C
from . import Curriculum as K

# The 16 statements, in the order they are dealt (one "would" and one "wouldn't" per program, mixed).
ITEM_IDS = ["str-kernel:a1", "core-decisions:a3", "dsc-experiments:a1", "org-talent:a1", "grw-loops:a3",
            "biz-positioning:a3", "inf-exec:a2", "frn-tech:a1", "core-judgement:a2", "str-moats:a2", "grw-retention:a2",
            "dsc-pmf:a1", "org-cadence:a2", "biz-launch:a2", "frn-ai:a3", "inf-stakeholders:a1"]
BANDS = [(15, "Ready for the director chair", "You call these the way experienced directors do. Prove it under pressure: "
                                              "a mock Interview Day, then the final examinations."),
         (12, "Close: a few blind spots", "Strong judgement with a couple of gaps. Close them with the modules below "
                                          "before your next director loop."),
         (8, "Strong senior PM, not yet director", "You know the craft, but several calls still follow senior-PM "
                                                   "instincts. The modules below are where directors think differently."),
         (0, "Early: build the director habits", "Most of these calls trip people up before they have led a product "
                                                 "org. Start with Foundations and the modules below.")]
CODE_CHARS = "ABCDEFGHJKMNPQRSTUVWXYZ23456789"
SESSION_KEY = "check_run"


def band_for(score):
    for floor, title, text in BANDS:
        if score >= floor:
            return {"title": title, "text": text, "floor": floor}
    return {"title": BANDS[-1][1], "text": BANDS[-1][2], "floor": 0}


def _new_code():
    for _i in range(20):
        code = "".join(random.choice(CODE_CHARS) for _j in range(8))
        if app_tables.checks.get(code=code) is None:
            return code
    raise RuntimeError("Couldn't make a result code.")


def _run():
    return anvil.server.session.get(SESSION_KEY) or {}


def score_answers(answers):
    """{item id: would (bool)} -> (score, by_track {track: 0-2}, missed [item ids]). Only the 16 check items count."""
    by_track = {t["id"]: 0 for t in K.TRACKS}
    missed = []
    for iid in ITEM_IDS:
        it = K.ITEMS[iid]
        if iid in answers and bool(answers[iid]) == bool(it["sound"]):
            by_track[it["track"]] += 1
        else:
            missed.append(iid)
    return sum(by_track.values()), by_track, missed


def result_public(row):
    """A saved result for anyone with its code: no user fields."""
    score, by_track, missed = int(row["score"] or 0), dict(row["by_track"] or {}), list(row["missed"] or [])
    tracks = []
    for t in K.TRACKS:
        tracks.append({"id": t["id"], "code": t["code"], "title": t["title"], "score": int(by_track.get(t["id"], 0)), "of": 2})
    gaps, seen = [], set()
    for iid in missed:
        it = K.ITEMS.get(iid)
        if it is None or it["module"] in seen:
            continue
        seen.add(it["module"])
        m = K.MODULES[it["module"]]
        gaps.append({"id": m["id"], "title": m["title"], "track": K.TRACK_BY_ID[m["track"]]["title"], "minutes": m["minutes"]})
    return {"code": row["code"], "score": score, "of": len(ITEM_IDS), "band": band_for(score), "tracks": tracks,
            "gaps": gaps, "created": C.iso(row["created"]), "demo": bool(row["is_demo"])}


@anvil.server.callable
def get_check():
    """Public: the 16 statements, without verdicts, and a fresh run (answers are recorded per run)."""
    run_id = "".join(random.choice(CODE_CHARS) for _j in range(10))
    getattr(anvil.server, "session")[SESSION_KEY] = {"id": run_id, "answers": {}}
    items = []
    for iid in ITEM_IDS:
        it = K.ITEMS[iid]
        t = K.TRACK_BY_ID[it["track"]]
        items.append({"id": iid, "q": it["q"], "track": t["id"], "track_code": t["code"], "track_title": t["title"],
                      "module": it["module"], "module_title": K.MODULES[it["module"]]["title"]})
    return {"run": run_id, "items": items, "bands": [{"floor": b[0], "title": b[1]} for b in BANDS]}


@anvil.server.callable
def reveal_check(run_id, item_id, would):
    """Public: record the first answer to one statement in this run, then return its verdict and the why."""
    run = _run()
    if not run or run.get("id") != run_id:
        return C.fail("This check has expired. Start it again (it takes about three minutes).")
    if item_id not in ITEM_IDS:
        return C.fail("Unknown statement.")
    if C.rate_limited("check_reveal", 200, 3600):
        return C.fail("That's a lot of answers in one hour. Take a break and come back.")
    answers = dict(run.get("answers") or {})
    if item_id not in answers:
        answers[item_id] = bool(would)
        getattr(anvil.server, "session")[SESSION_KEY] = {"id": run_id, "answers": answers}
    it = K.ITEMS[item_id]
    return C.ok(sound=bool(it["sound"]), correct=answers[item_id] == bool(it["sound"]), why=it["a"],
                first=answers[item_id])


@anvil.server.callable
def save_check(run_id, answers=None):
    """Public, rate-limited: score the run from the answers recorded by reveal_check and return the result code."""
    run = _run()
    if not run or run.get("id") != run_id:
        return C.fail("This check has expired. Start it again (it takes about three minutes).")
    recorded = dict(run.get("answers") or {})
    if any(iid not in recorded for iid in ITEM_IDS):
        return C.fail("Answer all 16 statements first.")
    if isinstance(answers, dict):  # the browser's copy must agree with what the server recorded
        for iid, would in answers.items():
            if iid in recorded and bool(would) != recorded[iid]:
                return C.fail("Your answers don't match this check. Start it again.")
    if C.rate_limited("check_save", 12, 3600):
        return C.fail("That's a lot of checks in one hour. Take a break and come back.")
    score, by_track, missed = score_answers(recorded)
    row = app_tables.checks.add_row(code=_new_code(), user=C.me(), score=score, by_track=by_track, missed=missed,
                                    created=C.now(), is_demo=False)
    getattr(anvil.server, "session")[SESSION_KEY] = {}
    return C.ok(code=row["code"], result=result_public(row))


@anvil.server.callable
def get_check_result(code):
    """Public: a saved result by its code (no user fields). mine = the signed-in person owns it."""
    code = C.text(code, 20).upper()
    row = app_tables.checks.get(code=code) if code else None
    if row is None:
        return C.fail("No readiness check has that code.")
    me = C.me()
    owner = row["user"]
    return C.ok(result=result_public(row), mine=bool(me is not None and owner is not None and owner == me),
                claimable=bool(me is not None and owner is None and not row["is_demo"]))


@anvil.server.callable(require_user=True)
def claim_check(code):
    """Attach a guest's result (made in the last two days) to the signed-in account."""
    me = C.require_user()
    row = app_tables.checks.get(code=C.text(code, 20).upper())
    if row is None or row["is_demo"]:
        return C.fail("No readiness check has that code.")
    if row["user"] is not None:
        return C.ok(claimed=row["user"] == me)
    if (C.now() - row["created"]).total_seconds() > 2 * 86400:
        return C.fail("That result is too old to add to your account. Take the check again.")
    row["user"] = me
    return C.ok(claimed=True)


def latest(user):
    """The member's most recent result (for the dashboard), or None."""
    rows = app_tables.checks.search(tables.order_by("created", ascending=False), user=user)
    for row in rows:
        r = result_public(row)
        return {"code": r["code"], "score": r["score"], "of": r["of"], "band": r["band"]["title"], "created": r["created"],
                "weak": [x["code"] for x in r["tracks"] if x["score"] < 2]}
    return None


@anvil.server.callable(require_user=True)
def my_checks():
    me = C.require_user()
    rows = app_tables.checks.search(tables.order_by("created", ascending=False), user=me)
    out = []
    for row in rows:
        out.append({"code": row["code"], "score": int(row["score"] or 0), "of": len(ITEM_IDS),
                    "band": band_for(int(row["score"] or 0))["title"], "created": C.iso(row["created"])})
        if len(out) >= 10:
            break
    return {"items": out}
