from anvil import *

from ._anvil_designer import LoopDebriefTemplate


class LoopDebrief(LoopDebriefTemplate):
    """One Interview Day round in the debrief (mode "debrief": rubric to tick) or the review after the verdict
    (mode "review"). item = a round from loop_debrief / get_loop {i, title, minutes, seconds, persona, challenge
    {id, title, situation, ask, model, rubric}, answer, score}. value() -> the rubric ticks."""

    def __init__(self, **properties):
        super().__init__(**properties)
        r = self.item
        ch = r.get("challenge") or {}
        n = self.dom_nodes
        n["round"].textContent = "Round %d · %s" % (r["i"] + 1, r["title"])
        n["who"].textContent = "%s · %d of %d min" % (r["persona"]["name"], (r.get("seconds") or 0) // 60 + (1 if (r.get("seconds") or 0) % 60 else 0), r["minutes"])
        n["title"].textContent = ch.get("title") or ""
        n["situation"].textContent = ch.get("situation") or ""
        n["ask"].textContent = ch.get("ask") or ""
        ans = (r.get("answer") or "").strip()
        n["mine"].textContent = ans or "(No answer handed in.)"
        n["model"].textContent = ch.get("model") or ""
        review = r.get("mode") == "review"
        self.rubric_part.visible = not review and bool(ans)
        self.review_part.visible = review and len(ans) >= 40
        if not review and ans:
            self.rubric.items = ch.get("rubric") or []
        n["ch_link"].setAttribute("href", "#challenge/" + (ch.get("id") or ""))

    def value(self):
        return self.rubric.value() if self.rubric_part.visible else []
