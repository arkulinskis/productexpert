from anvil import *

from ._anvil_designer import PenNoteTemplate

LEVELS = {"major": ("Major", "ui-badge bad"), "minor": ("Minor", "ui-badge warn"), "good": ("Good", "ui-badge good")}


class PenNote(PenNoteTemplate):
    """One red-pen margin note (Red Pen Studio). item = a note from redpen.grade: {level, field_label, title, text,
    source {label, url}, module}."""

    def __init__(self, **properties):
        super().__init__(**properties)
        x = self.item
        n = self.dom_nodes
        label, cls = LEVELS.get(x.get("level"), LEVELS["minor"])
        n["box"].className = "sd-note " + (x.get("level") or "minor")
        n["level"].textContent = label
        n["level"].className = cls
        n["where"].textContent = x.get("field_label") or ""
        n["title"].textContent = x.get("title") or ""
        n["text"].textContent = x.get("text") or ""
        src = x.get("source")
        if src:
            n["src"].textContent = "Source: " + src["label"]
            n["src"].setAttribute("href", src["url"])
        else:
            n["src"].hidden = True
        if x.get("module") and x.get("level") != "good":
            n["mod"].setAttribute("href", "#module/" + x["module"])
        else:
            n["mod"].hidden = True
