from anvil import *

from ._anvil_designer import StudioDocRowTemplate
from ... import px, state


class StudioDocRow(StudioDocRowTemplate):
    """A saved Red Pen practice doc on #studio. item = {id, kind, title, grade, score, updated}. Delete raises
    x-delete(doc_id) on the panel; the page confirms and deletes."""

    def __init__(self, **properties):
        super().__init__(**properties)
        d = self.item
        n = self.dom_nodes
        n["a"].setAttribute("href", "#studio/doc/" + d["id"])
        n["title"].textContent = d.get("title") or "Untitled"
        n["sub"].textContent = "%s · %d/100 · %s" % ("Strategy one-pager" if d["kind"] == "strategy" else "Outcome roadmap",
                                                     d.get("score") or 0, px.date(d.get("updated"), "short"))
        n["grade"].textContent = d.get("grade") or "-"
        n["grade"].className = "sd-mini g-" + (d.get("grade") or "D")
        state.set_control_attr(self.delete_button, "aria-label", "Delete " + (d.get("title") or "this document"))

    @handle("delete_button", "click")
    def delete_button_click(self, **event_args):
        self.parent.raise_event("x-delete", doc_id=self.item["id"])
