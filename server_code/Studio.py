"""Red Pen Studio (#studio): rule-based margin notes on a strategy one-pager or an outcome roadmap.

The rules live in client_code/redpen.py (pure Python, shared): the browser marks a draft instantly and "My own" mode
never calls the server. Practice briefs reuse module challenge situations; members save a practice doc
(save_studio_doc rescores it with the same rules, so a tampered score is ignored) and then see the model answer.
+10 XP the first time a doc earns a B or better.

Table studio_docs: user, kind ("strategy" | "roadmap"), brief, title, doc (obj), score, grade, created, updated,
xp_awarded, is_demo. Only the owner can list, open or delete their docs.
"""
import anvil.server
import anvil.tables as tables
from anvil.tables import app_tables

from . import common as C
from . import Curriculum as K
from . import redpen

MAX_DOCS = 60
XP_FIRST_B = 10

# Practice briefs: a challenge situation, the company's current (weak) draft to red-pen, and the model answer
# (shown only after a member saves their version). Model answers follow the challenge's model answer.
BRIEFS = [
    {
        "id": "slogan", "kind": "strategy", "challenge": "ch-str-kernel",
        "ask": "Rewrite the HR software company's strategy as a one-pager: diagnosis, guiding policy, coherent actions, "
               "what you will not do, measures and risks.",
        "start": {
            "diagnosis": "Vision: empower every employee.",
            "policy": "Become the all-in-one people platform.",
            "actions": "AI\nEnterprise\nInternational\nMobile\nIntegrations\nPayroll",
            "will_not": "", "measures": "", "risk": "",
        },
        "model": {
            "diagnosis": "Growth slowed from 45% to 18% because we spread effort across six priorities while our advantage "
                         "(fast setup and ease of use for companies without big HR teams) only wins with 50-500 employee "
                         "companies. Above 2,000 employees we compete on payroll and compliance depth, where we are weak, "
                         "and two suites are starting to bundle basic HR as a free feature.",
            "policy": "Be the best system for mid-sized companies without large HR teams, competing on time to value and "
                      "the breadth of everyday workflows, and partner rather than build for deep payroll.",
            "actions": "Concentrate the roadmap on the mid-market's most painful workflows: onboarding, performance, time off\n"
                       "Integrate with the leading payroll providers instead of building payroll\n"
                       "Use AI only where it cuts setup and admin time\n"
                       "Align sales compensation to the 50-500 employee segment",
            "will_not": "Enterprise compliance depth\nOur own payroll\nBroad international expansion this year",
            "measures": "Win rate in the 50-500 employee segment\nNet revenue retention\nTime to first value for new customers",
            "risk": "Suites bundling basic HR into our segment. We revisit the strategy if mid-market win rate or net "
                    "retention falls for two quarters running.",
        },
    },
    {
        "id": "allcore", "kind": "roadmap", "challenge": "ch-str-portfolio",
        "ask": "Turn the group's feature roadmap into an outcome roadmap: Now, Next and Later, each bet with its problem, "
               "evidence and measure.",
        "start": {
            "now": [{"problem": "", "bet": "Salesforce integration v2", "evidence": "", "measure": "Ship by end of Q1"},
                    {"problem": "", "bet": "Tech debt sprint", "evidence": "", "measure": "Done"}],
            "next": [{"problem": "", "bet": "Analytics dashboard (March 15)", "evidence": "", "measure": "Launch"},
                     {"problem": "Sales asked for it", "bet": "Custom fields", "evidence": "", "measure": "Released in April"}],
            "later": [{"problem": "", "bet": "AI assistant, Q4", "evidence": "", "measure": "Number of AI features shipped"},
                      {"problem": "", "bet": "Mobile app v2", "evidence": "", "measure": "Launch on iOS and Android"}],
        },
        "model": {
            "now": [{"problem": "Renewal-critical customers lose hours fixing data that fails to sync with Salesforce",
                     "bet": "Fix the three sync failures behind most renewal-risk tickets",
                     "evidence": "14 of the 20 at-risk renewals cite sync errors in success calls",
                     "measure": "Sync-related tickets down 50%; renewal rate in at-risk accounts"},
                    {"problem": "Existing customers can't see which teams use the product, so its value is hard to prove",
                     "bet": "Analytics for existing customers, staffed with two full teams",
                     "evidence": "30 customers asked for it; 9 of 12 interviewees said they would pay",
                     "measure": "Paid adoption by 15% of accounts within two quarters"}],
            "next": [{"problem": "The mobile app has 2% adoption and no owner",
                      "bet": "Decide: give it a clear job and owner, shrink it to maintenance, or sunset it with notice",
                      "evidence": "Usage data plus ten interviews with field users",
                      "measure": "Weekly active field users, or support cost saved"}],
            "later": [{"problem": "Managers spend hours preparing reports for leadership",
                       "bet": "Explore AI-written report summaries as a small time-boxed bet",
                       "evidence": "Six of ten interviewees build leadership reports by hand every week",
                       "measure": "Minutes saved per report in a pilot with five accounts"}],
        },
    },
]
BRIEF_BY_ID = {b["id"]: b for b in BRIEFS}


def brief_public(b, with_model=False):
    ch = K.CHALLENGES[b["challenge"]]
    out = {"id": b["id"], "kind": b["kind"], "title": ch["title"], "situation": ch["situation"], "ask": b["ask"],
           "start": b["start"], "challenge": ch["id"], "module": ch.get("module")}
    if with_model:
        out["model"] = b["model"]
        out["model_result"] = redpen.grade(b["kind"], b["model"])
    return out


def _doc_public(row, full=False):
    out = {"id": row.get_id(), "kind": row["kind"], "brief": row["brief"], "title": row["title"], "score": int(row["score"] or 0),
           "grade": row["grade"], "updated": C.iso(row["updated"]), "created": C.iso(row["created"])}
    if full:
        out["doc"] = row["doc"]
        b = BRIEF_BY_ID.get(row["brief"])
        out["brief_data"] = brief_public(b, with_model=True) if b else None
    return out


def _own(doc_id, me):
    row = C.row_by_id(app_tables.studio_docs, doc_id)
    if row is None or row["user"] != me:
        return None
    return row


@anvil.server.callable
def get_studio_briefs():
    """Public: the practice briefs (situation, ask, the draft to red-pen), without their model answers."""
    return {"briefs": [brief_public(b) for b in BRIEFS]}


@anvil.server.callable(require_user=True)
def save_studio_doc(doc_id, brief_id, doc, title=None, client_day=None):
    """Save (or update) the member's practice doc for a brief. Rescored here; returns the model answer too."""
    me = C.require_user()
    b = BRIEF_BY_ID.get(brief_id)
    if b is None:
        return C.fail("That practice brief doesn't exist.")
    kind = b["kind"]
    clean = redpen.clean(kind, doc)
    if clean == redpen.clean(kind, b["start"]):
        return C.fail("That's still the company's draft. Rewrite it first, then save.")
    if C.rate_limited("studio_save", 40, 3600):
        return C.fail("That's a lot of saves in one hour. Take a break and come back.")
    result = redpen.grade(kind, clean)
    title = C.text(title, 120) or K.CHALLENGES[b["challenge"]]["title"]
    row = _own(doc_id, me) if doc_id else None
    if doc_id and row is None:
        return C.fail("That document isn't yours, or it was deleted.")
    if row is None:
        if len(app_tables.studio_docs.search(user=me)) >= MAX_DOCS:
            return C.fail("You have %d saved documents. Delete a few first." % MAX_DOCS)
        row = app_tables.studio_docs.add_row(user=me, kind=kind, brief=brief_id, title=title, doc=clean, score=result["score"],
                                             grade=result["grade"], created=C.now(), updated=C.now(), xp_awarded=False,
                                             is_demo=False)
    else:
        row.update(title=title, doc=clean, score=result["score"], grade=result["grade"], updated=C.now())
    gained = 0
    if redpen.passing(result) and not row["xp_awarded"]:
        from .Learning import add_xp, today
        row["xp_awarded"] = True
        add_xp(me, XP_FIRST_B, today(client_day))
        gained = XP_FIRST_B
    return C.ok(doc=_doc_public(row, full=True), result=result, xp_gained=gained)


@anvil.server.callable(require_user=True)
def list_studio_docs():
    me = C.require_user()
    rows = app_tables.studio_docs.search(tables.order_by("updated", ascending=False), user=me)
    return {"items": [_doc_public(r) for r in rows]}


@anvil.server.callable(require_user=True)
def get_studio_doc(doc_id):
    me = C.require_user()
    row = _own(doc_id, me)
    if row is None:
        return C.fail("That document isn't yours, or it was deleted.")
    return C.ok(doc=_doc_public(row, full=True))


@anvil.server.callable(require_user=True)
def delete_studio_doc(doc_id):
    me = C.require_user()
    row = _own(doc_id, me)
    if row is None:
        return C.fail("That document isn't yours, or it was deleted.")
    row.delete()
    return C.ok()
