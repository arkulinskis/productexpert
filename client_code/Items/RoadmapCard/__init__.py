from anvil import *

from ._anvil_designer import RoadmapCardTemplate
from ... import state

FIELDS = ["problem", "bet", "evidence", "measure"]


class RoadmapCard(RoadmapCardTemplate):
    """One bet in a Red Pen roadmap column. item = {problem, bet, evidence, measure, col, col_label, i, n}.
    value() -> the four fields; Remove raises x-remove(col, i) on the panel (the page redraws the column)."""

    def __init__(self, **properties):
        super().__init__(**properties)
        c = self.item
        for key in FIELDS:
            box = getattr(self, key + "_box")
            box.text = c.get(key) or ""
            state.set_control_attr(box, "maxlength", "300")
        self.dom_nodes["label"].textContent = "%s · bet %d" % (c.get("col_label") or "", (c.get("i") or 0) + 1)
        state.set_control_attr(self.remove_button, "aria-label", "Remove %s bet %d" % (c.get("col_label") or "", (c.get("i") or 0) + 1))

    def value(self):
        out = {}
        for key in FIELDS:
            out[key] = getattr(self, key + "_box").text or ""
        return out

    @handle("remove_button", "click")
    def remove_button_click(self, **event_args):
        self.parent.raise_event("x-remove", col=self.item["col"], i=self.item["i"])
