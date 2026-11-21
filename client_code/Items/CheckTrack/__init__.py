from anvil import *

from ._anvil_designer import CheckTrackTemplate


class CheckTrack(CheckTrackTemplate):
    """One program on a Readiness Check result: code, title, two pips and the score. item = {code, title, score, of}."""

    def __init__(self, **properties):
        super().__init__(**properties)
        t = self.item
        n = self.dom_nodes
        score, of = int(t.get("score") or 0), int(t.get("of") or 2)
        n["code"].textContent = t.get("code") or ""
        n["title"].textContent = t.get("title") or ""
        n["score"].textContent = "%d/%d" % (score, of)
        n["row"].className = "ck-track" + (" weak" if score < of else "")
        n["p1"].className = "on" if score >= 1 else ""
        n["p2"].className = "on" if score >= 2 else ""
