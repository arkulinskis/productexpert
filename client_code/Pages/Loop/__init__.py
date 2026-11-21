import anvil.server
import anvil.js
from anvil import *
from anvil.js import window

from ._anvil_designer import LoopTemplate
from ... import px, router, state

VERDICT_TEXT = {
    "Strong hire": "Clear, structured and senior in every round. You'd be a strong candidate for a director loop now.",
    "Hire": "A credible director candidate. Tighten the weakest round below and you're there.",
    "Lean no hire": "Good instincts, but at least one round fell short of what a panel expects from a director.",
    "No hire yet": "Not yet: the answers missed much of what the panel looks for. Study the weakest round's module and try again.",
}
VERDICT_CLASS = {"Strong hire": "good", "Hire": "good", "Lean no hire": "warn", "No hire yet": "bad"}


class Loop(LoopTemplate):
    """#loop: Interview Day. #loop = the three loop formats (get_loops) + the member's loops; start_loop makes one and
    opens #loop/<id>. A loop page shows its stage: a timed round (persona, situation, soft timer on Anvil's Timer, the
    answer box; submit_loop_round), the debrief (loop_debrief: model answers + Rubric per round; finish_loop) or the
    verdict (per-round scores and minutes, the weakest round's module). Drafts and round start times live in this
    browser (UI.store), so a reload or an expired session keeps the clock and the text."""

    def __init__(self, args=(), **properties):
        super().__init__(**properties)
        self._loop = None
        self._started_ms = 0
        self._minutes = 0
        self._warned = False
        self.formats_panel.add_event_handler("x-start", self._start)
        state.set_control_attr(self.answer_box, "maxlength", "6000")
        self._id = args[0] if args else ""
        if self._id:
            self._open(self._id)
        else:
            self._index()

    def _show(self, view):
        for name in ("index", "round", "debrief", "done", "missing"):
            getattr(self, name + "_part").visible = view == name
        if view != "round":
            self.clock.interval = 0

    # ---- index
    def _index(self):
        self.hero.set(fig="influence", title="Interview Day",
                      lead="A timed mock director loop: a defended strategy case, a metrics deep dive, a people round and "
                           "eight minutes with the CEO. Then the model answers, a rubric and the panel's verdict.",
                      meta=[["clock", "4 rounds · 52 minutes"], ["users", "4 interviewers"], ["award", "Strong hire to No hire yet"]])
        d = anvil.server.call("get_loops")
        self.formats_panel.items = d["formats"]
        self.mine_panel.items = d["mine"]
        self.no_mine.visible = not d["mine"]
        self.mine_panel.visible = bool(d["mine"])
        self._show("index")

    def _start(self, fmt, **event_args):
        r = state.call("start_loop", fmt)
        if r:
            router.go("loop", r["id"])

    # ---- one loop
    def _open(self, loop_id):
        r = anvil.server.call("get_loop", loop_id)
        if not r.get("ok"):
            self.hero.set(fig="influence", title="Not found", crumbs=[["#loop", "Interview Day"], [None, "Not found"]])
            self._show("missing")
            return
        self._draw(r["loop"])

    def _draw(self, lp):
        self._loop = lp
        if lp["stage"] == "round":
            self._round(lp)
        elif lp["stage"] == "debrief":
            d = state.call("loop_debrief", lp["id"])
            if d:
                self._debrief(d["loop"])
        else:
            self._done(lp)

    def _key(self, i, what):
        return "loop_%s_%d_%s" % (self._loop["id"], i, what)

    def _round(self, lp):
        i = lp["current"]
        rd = lp["rounds"][i]
        ch, p = rd["challenge"], rd["persona"]
        n = self.dom_nodes
        px.title("Round %d of 4 · Interview Day" % (i + 1))
        self.hero.set(fig=ch["fig"], title="Round %d: %s" % (i + 1, rd["title"]),
                      crumbs=[["#loop", "Interview Day"], [None, lp["title"]]],
                      meta=[["clock", "%d minutes" % rd["minutes"]], ["users", "%s, %s" % (p["name"], p["role"])]])
        for j in range(4):
            r = lp["rounds"][j]
            node = n["st%d" % j]
            node.textContent = "%d. %s" % (j + 1, r["title"])
            node.className = "done" if j < i else ("on" if j == i else "")
            if j == i:
                node.setAttribute("aria-current", "step")
            else:
                node.removeAttribute("aria-current")
        px.set_text(n["p_initials"], state.initials(p["name"]))
        px.set_text(n["p_name"], p["name"])
        px.set_text(n["p_role"], p["role"])
        px.set_text(n["p_line"], p["line"])
        px.set_text(n["ch_title"], ch["title"])
        px.set_text(n["situation"], ch["situation"])
        px.set_text(n["ask"], ch["ask"])
        self.answer_box.text = state.store_get(self._key(i, "draft"), "") or ""
        self.submit_button.text = "Hand in and go to the debrief" if i == 3 else "Hand in this round"
        self.submit_button.enabled = True
        started = state.store_get(self._key(i, "start"))
        if not started:
            started = float(window.Date.now())
            state.store_set(self._key(i, "start"), started)
        self._started_ms, self._minutes, self._warned = float(started), rd["minutes"], False
        self._show("round")
        self._tick()
        self.clock.interval = 1

    def _elapsed(self):
        return max(0.0, (float(window.Date.now()) - self._started_ms) / 1000.0)

    def _tick(self):
        n = self.dom_nodes
        total = self._minutes * 60
        left = total - self._elapsed()
        over = left < 0
        secs = int(abs(left))
        px.set_text(n["time"], "%s%d:%02d" % ("+" if over else "", secs // 60, secs % 60))
        px.set_text(n["timer_label"], "Over time" if over else "Time left")
        frac = max(0.0, min(1.0, left / float(total))) if total else 0
        n["time_fill"].style.transform = "scaleX(%s)" % frac
        near = left <= total * 0.2
        n["timer_box"].className = "ui-card lo-timer" + (" over" if over else (" near" if near else ""))
        if over:
            note = "The interviewer is checking the time. Wrap up and hand in."
        elif near:
            note = "Nearly time: land your recommendation."
        else:
            note = "%d-minute round. The clock is soft." % self._minutes
        px.set_text(n["timer_note"], note)
        if near and not self._warned:
            self._warned = True
            n["time"].setAttribute("aria-live", "polite")  # one announcement when it turns saffron
        if int(self._elapsed()) % 10 == 0 and self._loop:
            state.store_set(self._key(self._loop["current"], "draft"), self.answer_box.text or "")

    @handle("clock", "tick")
    def clock_tick(self, **event_args):
        if not self.round_part.visible:
            self.clock.interval = 0
            return
        self._tick()

    @handle("answer_box", "change")
    def answer_box_change(self, **event_args):
        if self._loop:
            state.store_set(self._key(self._loop["current"], "draft"), self.answer_box.text or "")

    @handle("submit_button", "click")
    def submit_button_click(self, **event_args):
        text = (self.answer_box.text or "").strip()
        if len(text) < 40:
            if not confirm("Your answer is very short, so this round will score 0. Hand it in anyway?",
                           title="Hand in", buttons=[("Keep writing", False), ("Hand it in", True)]):
                return
        lp = self._loop
        i = lp["current"]
        self.submit_button.enabled = False
        r = state.call("submit_loop_round", lp["id"], i, text, int(self._elapsed()))
        if not r:
            self.submit_button.enabled = True
            return
        self.clock.interval = 0
        state.store_set(self._key(i, "draft"), "")
        window.scrollTo(0, 0)
        self._draw(r["loop"])

    # ---- debrief
    def _debrief(self, lp):
        self._loop = lp
        px.title("Debrief · Interview Day")
        self.hero.set(fig="director", title="The debrief", crumbs=[["#loop", "Interview Day"], [None, lp["title"]]],
                      lead="All four rounds are in. Compare each answer with the model answer and tick what you covered.",
                      meta=[["clock", "%d of 52 minutes used" % (sum([r["seconds"] for r in lp["rounds"]]) // 60)]])
        self.debrief_panel.items = [dict(r, mode="debrief") for r in lp["rounds"]]
        self.finish_button.enabled = True
        self._show("debrief")

    @handle("finish_button", "click")
    def finish_button_click(self, **event_args):
        points = [form.value() for form in self.debrief_panel.get_components()]
        self.finish_button.enabled = False
        r = state.call("finish_loop", self._loop["id"], points, px.today())
        if not r:
            self.finish_button.enabled = True
            return
        window.scrollTo(0, 0)
        self._done(r["loop"])
        if r.get("xp_gained"):
            state.toast("+%d XP. Each answer is saved under its challenge." % r["xp_gained"], "ok")
        if r["loop"]["verdict"] in ("Strong hire", "Hire"):
            px.confetti()

    # ---- verdict
    def _done(self, lp):
        self._loop = lp
        n = self.dom_nodes
        v = lp.get("verdict") or "No hire yet"
        px.title("%s · Interview Day" % v)
        self.hero.set(fig="director", title="Verdict: %s" % v, crumbs=[["#loop", "Interview Day"], [None, lp["title"]]],
                      meta=[["calendar", px.date(lp["finished"], "long")], ["target", "Average %d%%" % (lp["score"] or 0)]])
        px.set_text(n["verdict"], v)
        n["verdict_box"].className = "ui-card lo-verdict " + VERDICT_CLASS.get(v, "warn")
        px.set_text(n["verdict_text"], VERDICT_TEXT.get(v, ""))
        px.set_text(n["avg"], "%d%%" % (lp["score"] or 0))
        w = lp.get("weakest")
        n["weak_link"].hidden = not w
        if w:
            n["weak_link"].setAttribute("href", "#module/" + w["module"])
            px.set_text(n["weak_text"], "Weakest round: study %s" % w["module_title"])
        self.scores_panel.items = lp["rounds"]
        self.review_panel.items = [dict(r, mode="review") for r in lp["rounds"]]
        self._show("done")

    @handle("", "hide")
    def form_hide(self, **event_args):
        self.clock.interval = 0
        if self.round_part.visible and self._loop:
            state.store_set(self._key(self._loop["current"], "draft"), self.answer_box.text or "")
