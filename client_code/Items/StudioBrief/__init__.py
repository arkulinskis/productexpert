from anvil import *

from ._anvil_designer import StudioBriefTemplate


class StudioBrief(StudioBriefTemplate):
    """A Red Pen Studio practice brief on #studio. item = a brief from get_studio_briefs {id, kind, title, situation}."""

    def __init__(self, **properties):
        super().__init__(**properties)
        b = self.item
        n = self.dom_nodes
        n["a"].setAttribute("href", "#studio/practice/" + b["id"])
        n["kind"].textContent = "Strategy one-pager" if b["kind"] == "strategy" else "Outcome roadmap"
        n["from"].textContent = "From the challenge"
        n["title"].textContent = b["title"]
        sit = b.get("situation") or ""
        n["sit"].textContent = sit if len(sit) <= 190 else sit[:187].rsplit(" ", 1)[0] + "..."
