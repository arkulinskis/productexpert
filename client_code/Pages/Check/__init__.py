import anvil.server
import anvil.js
from anvil import *
from anvil.js import window

from ._anvil_designer import CheckTemplate
from ... import px, router, state
from ...Dialogs.LinkBox import LinkBox

STORE_KEY = "check_code"


class Check(CheckTemplate):
    """#check: the Director Readiness Check, open to anyone. 16 "would a director do this?" statements (two per
    program, get_check); each answer is recorded on the server first and then reveals the verdict and the why
    (reveal_check); save_check scores the recorded answers and returns a code. #check/<code> shows a result to anyone
    (get_check_result, no names): score, band, radar (Components/Radar), gap modules, Build my plan and Share.
    Keys: 1 would, 2 wouldn't, Enter / Space / right arrow for the next statement."""

    def __init__(self, args=(), **properties):
        super().__init__(**properties)
        self._items: list = []
        self._answers: dict = {}
        self._i, self._run, self._revealed, self._busy, self._listening = 0, None, False, False, False
        self._right = 0
        self._code = ""
        self._key_fn = anvil.js.report_exceptions(self._key)
        self.dom_nodes["plan_link"].addEventListener("click", anvil.js.report_exceptions(self._plan_click))
        self.dom_nodes["signup_link"].addEventListener("click", anvil.js.report_exceptions(self._plan_click))
        code = (args[0] if args else "").strip().upper()
        if code:
            self._load_result(code)
        else:
            self._intro()

    # ---- views
    def _show(self, view):
        self.intro_part.visible = view == "intro"
        self.run_part.visible = view == "run"
        self.result_part.visible = view == "result"
        self.missing_part.visible = view == "missing"

    def _intro(self):
        self.hero.set(fig="judgement", title="Director Readiness Check",
                      lead="Sixteen calls product directors make every week. Decide what a strong director would do, see "
                           "why straight away, and find out where your judgement is already director-level.",
                      meta=[["clock", "About 3 minutes"], ["target", "16 statements, 2 per program"],
                            ["lock", "No account needed"]])
        last = state.store_get(STORE_KEY)
        self.last_card.visible = bool(last)
        if last:
            self.dom_nodes["last_link"].setAttribute("href", "#check/" + str(last))
            px.set_text(self.dom_nodes["last_text"], "Open result " + str(last))
        self._show("intro")

    @handle("start_button", "click")
    def start_button_click(self, **event_args):
        r = state.call("get_check")
        if not r:
            return
        self._run, self._items = r["run"], list(r["items"])
        self._i, self._answers, self._right, self._revealed = 0, {}, 0, False
        px.title("Readiness check in progress")
        self.hero.set(lead="Make each call before you reveal the why. Be honest with yourself: the result is only useful if it's yours.",
                      meta=[["clock", "About 3 minutes"], ["target", "16 statements"]])
        self._show("run")
        self._listen(True)
        self._draw_item()
        state.focus(self.would_button)

    def _draw_item(self):
        it = self._items[self._i]
        n = self.dom_nodes
        total = len(self._items)
        self.bar.pct = 100.0 * self._i / max(1, total)
        px.set_text(n["count"], "%d / %d" % (self._i + 1, total))
        px.set_text(n["b_track"], "%s · %s" % (it["track_code"], it["track_title"]))
        px.set_text(n["q"], it["q"])
        r = self._revealed
        self.back.visible = r
        self.would_button.visible = self.wouldnt_button.visible = not r
        self.next_button.visible = r
        self.next_button.text = "See my result" if self._i + 1 >= total else "Next statement"
        px.set_text(n["keys"], "Enter for the next statement" if r else "1 a director would · 2 a director wouldn't")

    def _answer(self, would):
        if self._revealed or self._busy or not self._items:
            return
        it = self._items[self._i]
        self._busy = True
        try:
            r = anvil.server.call_s("reveal_check", self._run, it["id"], bool(would))
        finally:
            self._busy = False
        if not r or not r.get("ok"):
            state.toast((r or {}).get("error") or "That didn't work. Start the check again.", "error")
            self._listen(False)
            self._intro()
            return
        self._answers[it["id"]] = bool(r["first"])
        if r["correct"]:
            self._right += 1
        n = self.dom_nodes
        sound = bool(r["sound"])
        self.verdict.classes["sound"], self.verdict.classes["trap"] = sound, not sound
        n["verdict_ic"].className = "ic ic-check" if sound else "ic ic-alert"
        px.set_text(n["verdict_t"], "Director's call" if sound else "Not a director's call")
        said = "would" if r["first"] else "wouldn't"
        px.set_text(n["you"], ("You said a director %s. You called it." if r["correct"] else
                               "You said a director %s. Not this time.") % said)
        n["you"].className = "ck-you " + ("good" if r["correct"] else "bad")
        px.set_text(n["why"], r["why"])
        px.set_text(n["from"], "Taught in: %s" % it["module_title"])
        self._revealed = True
        self._draw_item()
        state.focus(self.next_button)

    def _next(self):
        if not self._revealed or self._busy:
            return
        if self._i + 1 < len(self._items):
            self._i += 1
            self._revealed = False
            self._draw_item()
            state.focus(self.would_button)
            return
        self._busy = True
        try:
            r = state.call("save_check", self._run, self._answers)
        finally:
            self._busy = False
        if not r:
            self._listen(False)
            self._intro()
            return
        self._listen(False)
        state.store_set(STORE_KEY, r["code"])
        router.replace("check", r["code"])
        self._draw_result(r["result"], mine=bool(state.me()), claimable=False)
        if r["result"]["score"] >= 15:
            px.confetti()

    @handle("would_button", "click")
    def would_button_click(self, **event_args):
        self._answer(True)

    @handle("wouldnt_button", "click")
    def wouldnt_button_click(self, **event_args):
        self._answer(False)

    @handle("next_button", "click")
    def next_button_click(self, **event_args):
        self._next()

    # ---- result
    def _load_result(self, code):
        r = anvil.server.call("get_check_result", code)
        if not r.get("ok"):
            self.hero.set(fig="judgement", title="Result not found", crumbs=[["#check", "Readiness Check"], [None, "Not found"]])
            self._show("missing")
            return
        self._draw_result(r["result"], mine=r["mine"], claimable=r["claimable"])

    def _draw_result(self, res, mine, claimable):
        self._code = res["code"]
        n = self.dom_nodes
        b = res["band"]
        px.title("Readiness check: %d of %d" % (res["score"], res["of"]))
        self.hero.set(fig="judgement", title="Readiness check result", lead=b["title"],
                      crumbs=[["#check", "Readiness Check"], [None, res["code"]]],
                      meta=[["target", "%d of %d calls" % (res["score"], res["of"])], ["calendar", px.date(res["created"], "long")]])
        px.set_text(n["score"], str(res["score"]))
        px.set_text(n["of"], "/ %d" % res["of"])
        px.set_text(n["band"], b["title"])
        px.set_text(n["band_text"], b["text"])
        px.set_text(n["when"], "Taken %s" % px.date(res["created"], "long"))
        n["sample"].hidden = not res.get("demo")
        me = state.me()
        n["plan_link"].setAttribute("href", "#plan" if me else "#auth/signup")
        self.claim_box.visible = bool(me and claimable)
        self.guest_box.visible = not me
        self.radar.data = res["tracks"]
        self.tracks_panel.items = res["tracks"]
        gaps = res["gaps"]
        self.gaps_panel.items = gaps
        self.gaps_panel.visible = bool(gaps)
        if gaps:
            px.set_text(n["gaps_head"], "Where to close the gap")
            px.set_text(n["gaps_lead"], "%s missed. These modules teach the director's view of each one:" %
                        state.plural(res["of"] - res["score"], "call"))
        else:
            px.set_text(n["gaps_head"], "No gaps on this check")
            px.set_text(n["gaps_lead"], "Every call matched a director's. Now prove it under pressure and in writing.")
        self._show("result")

    def _plan_click(self, event):
        if not state.me():
            router.remember_after("#plan")

    @handle("share_button", "click")
    def share_button_click(self, **event_args):
        url = window.location.origin + window.location.pathname + "#check/" + self._code
        try:
            window.navigator.clipboard.writeText(url)
            state.toast("Link copied. It shows the score, never your name.", "ok")
        except Exception:
            alert(LinkBox(link=url), buttons=[], role="app-dialog")

    @handle("claim_button", "click")
    def claim_button_click(self, **event_args):
        r = state.call("claim_check", self._code)
        if r:
            self.claim_box.visible = False
            state.toast("Saved to your account.", "ok")

    # ---- keyboard
    def _listen(self, on):
        if on and not self._listening:
            window.document.addEventListener("keydown", self._key_fn)
            self._listening = True
        elif not on and self._listening:
            window.document.removeEventListener("keydown", self._key_fn)
            self._listening = False

    def _key(self, event):
        tag = str(getattr(event.target, "tagName", "") or "")
        if tag in ("INPUT", "TEXTAREA", "SELECT"):
            return
        k = getattr(event, "key", None)
        if not self._revealed and k == "1":
            self._answer(True)
        elif not self._revealed and k == "2":
            self._answer(False)
        elif self._revealed and k in ("Enter", " ", "ArrowRight"):
            event.preventDefault()
            self._next()

    @handle("", "hide")
    def form_hide(self, **event_args):
        self._listen(False)

    @handle("", "show")
    def form_show(self, **event_args):
        if self.run_part.visible:
            self._listen(True)
