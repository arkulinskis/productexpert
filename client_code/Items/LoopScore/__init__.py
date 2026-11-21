from anvil import *

from ._anvil_designer import LoopScoreTemplate


class LoopScore(LoopScoreTemplate):
    """One round's score bar on the Interview Day verdict. item = a finished round {i, title, minutes, seconds, score,
    challenge {title}}."""

    def __init__(self, **properties):
        super().__init__(**properties)
        r = self.item
        n = self.dom_nodes
        score = int(r.get("score") or 0)
        n["title"].textContent = "%d. %s" % (r["i"] + 1, r["title"])
        n["score"].textContent = "%d%%" % score
        n["score"].className = "num " + ("good" if score >= 70 else "warn" if score >= 50 else "bad")
        self.bar.pct = score
        secs = int(r.get("seconds") or 0)
        mins = secs // 60 + (1 if secs % 60 else 0)
        n["sub"].textContent = "%s · %d of %d min%s" % ((r.get("challenge") or {}).get("title") or "", mins, r["minutes"],
                                                        " (over time)" if secs > r["minutes"] * 60 else "")
