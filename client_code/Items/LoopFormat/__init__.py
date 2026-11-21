from anvil import *

from ._anvil_designer import LoopFormatTemplate
from ... import state


class LoopFormat(LoopFormatTemplate):
    """An Interview Day loop format on #loop. item = a format from get_loops {id, title, company, blurb, minutes,
    rounds: [{title, minutes, who, role}]}. Start raises x-start(fmt) on the panel."""

    def __init__(self, **properties):
        super().__init__(**properties)
        f = self.item
        n = self.dom_nodes
        n["title"].textContent = f["title"]
        n["company"].textContent = f["company"]
        n["blurb"].textContent = f["blurb"]
        self.rounds_panel.items = ["%s · %d min · %s, %s" % (r["title"], r["minutes"], r["who"], r["role"]) for r in f["rounds"]]
        self.start_button.text = "Start: %d minutes" % f["minutes"]
        state.set_control_attr(self.start_button, "aria-label", "Start the %s (%d minutes)" % (f["title"].lower(), f["minutes"]))

    @handle("start_button", "click")
    def start_button_click(self, **event_args):
        self.parent.raise_event("x-start", fmt=self.item["id"])
