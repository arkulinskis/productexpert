from anvil import *

from ._anvil_designer import LoopRowTemplate
from ... import px

CLASS = {"Strong hire": "ui-badge good", "Hire": "ui-badge good", "Lean no hire": "ui-badge warn", "No hire yet": "ui-badge bad"}


class LoopRow(LoopRowTemplate):
    """One of the member's loops on #loop. item = {id, title, stage, current, started, verdict, score}."""

    def __init__(self, **properties):
        super().__init__(**properties)
        x = self.item
        n = self.dom_nodes
        n["a"].setAttribute("href", "#loop/" + x["id"])
        n["title"].textContent = x["title"]
        if x["stage"] == "done":
            n["sub"].textContent = "%s · average %d%%" % (px.date(x["started"], "short"), x.get("score") or 0)
            n["badge"].textContent = x.get("verdict") or ""
            n["badge"].className = CLASS.get(x.get("verdict"), "ui-badge")
        elif x["stage"] == "debrief":
            n["sub"].textContent = "%s · all rounds in" % px.date(x["started"], "short")
            n["badge"].textContent = "Debrief waiting"
            n["badge"].className = "ui-badge accent"
        else:
            n["sub"].textContent = "%s · round %d of 4" % (px.date(x["started"], "short"), (x.get("current") or 0) + 1)
            n["badge"].textContent = "In progress"
            n["badge"].className = "ui-badge brand"
