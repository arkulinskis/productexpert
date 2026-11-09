"""Labs: hands-on simulators that run in the browser (theme/assets/px-labs.js). The server lists them and records runs.

A lab run is saved when the learner reaches the lab's goal (the engine decides; score 0-100). The first completed run
of each lab gives LAB_XP. Labs work for visitors too; only members' runs are saved.
"""
import anvil.server
from anvil.tables import app_tables

from . import common as C
from . import Curriculum as K
from . import Learning as L

LAB_XP = 15

LABS = [
    {"id": "peek", "title": "Peeking simulator", "module": "dsc-experiments", "fig": "experiment", "minutes": 10,
     "blurb": "Run 200 simulated A/A tests where nothing changed, then check them daily like an impatient team. Watch false 'wins' pile up, then fix it.",
     "goal": "See how peeking inflates false positives, then get the false-positive rate back near 5%."},
    {"id": "tree", "title": "Metric tree builder", "module": "grw-northstar", "fig": "metrics", "minutes": 8,
     "blurb": "A subscription product's north star decomposed into five inputs. Move each lever within a realistic range and see which ones compound.",
     "goal": "Reach the 12-month north star target with changes a team could plausibly make."},
    {"id": "cohort", "title": "Cohort and growth accounting lab", "module": "grw-retention", "fig": "cohort", "minutes": 10,
     "blurb": "Shape a retention curve, set acquisition and resurrection, and watch active users, churn and the quick ratio over 24 months.",
     "goal": "Beat the founder's buy-more-users plan at month 24 with acquisition growing 2% a month or less, and a quick ratio of at least 1.3."},
    {"id": "price", "title": "Van Westendorp pricing lab", "module": "grw-pricing", "fig": "pricing", "minutes": 10,
     "blurb": "Read 120 simulated survey answers to the four price questions, find the acceptable price range, then pick a price and see the trade-off.",
     "goal": "Find the acceptable price range from the curves and choose a price inside it."},
    {"id": "unit", "title": "Unit economics lab", "module": "biz-economics", "fig": "pnl", "minutes": 8,
     "blurb": "Two segments, one budget. Change price, churn, gross margin and acquisition cost to see LTV, LTV:CAC and payback move.",
     "goal": "Get the new self-serve segment to LTV:CAC of 3 or more with payback under 12 months, using realistic levers."},
]
LAB_BY_ID = {x["id"]: x for x in LABS}


def lab_public(x):
    m = K.MODULES.get(x["module"])
    return dict(x, module_title=m["title"] if m else "", track=m["track"] if m else "",
                track_title=K.TRACK_BY_ID[m["track"]]["title"] if m else "")


@anvil.server.callable
def get_labs():
    me = C.me()
    best = {}
    if me is not None:
        for r in app_tables.lab_runs.search(user=me):
            best[r["lab"]] = max(best.get(r["lab"], 0), int(r["score"] or 0))
    out = []
    for x in LABS:
        d = lab_public(x)
        d["best"] = best.get(x["id"]) if me is not None else None
        out.append(d)
    return {"labs": out, "signed_in": me is not None}


@anvil.server.callable
def get_lab(lab_id):
    x = LAB_BY_ID.get(lab_id)
    if x is None:
        return C.fail("That lab doesn't exist.")
    me = C.me()
    d = lab_public(x)
    d["best"] = None
    if me is not None:
        scores = [int(r["score"] or 0) for r in app_tables.lab_runs.search(user=me, lab=lab_id)]
        d["best"] = max(scores) if scores else None
    others = [lab_public(y) for y in LABS if y["id"] != lab_id]
    return C.ok(lab=d, others=others, signed_in=me is not None)


@anvil.server.callable(require_user=True)
def save_lab_run(lab_id, score, detail=None, client_day=None):
    me = C.require_user()
    if lab_id not in LAB_BY_ID:
        return C.fail("That lab doesn't exist.")
    try:
        score = max(0, min(100, int(score)))
    except (TypeError, ValueError):
        return C.fail("The lab score must be a number.")
    if C.rate_limited("lab", 60, 3600):
        return C.fail("That's a lot of lab runs in one hour. Take a short break.")
    clean: dict = {}
    if isinstance(detail, dict):
        for k, v in list(detail.items())[:12]:
            if isinstance(v, (int, float, bool)):
                clean[str(k)[:40]] = v
            elif isinstance(v, str):
                clean[str(k)[:40]] = v[:200]
    first = len(app_tables.lab_runs.search(user=me, lab=lab_id)) == 0
    app_tables.lab_runs.add_row(user=me, lab=lab_id, score=score, detail=clean, created=C.now(), is_demo=False)
    gained = LAB_XP if first else 2
    L.add_xp(me, gained, L.today(client_day))
    return C.ok(first=first, xp_gained=gained, xp=me["xp"])
