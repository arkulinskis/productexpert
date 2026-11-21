from anvil import *
from anvil.js import window

from ._anvil_designer import RadarTemplate
from ... import px


class Radar(RadarTemplate):
    """The Readiness Check radar: one spoke per program (PX.radar), full spokes cobalt, weak ones saffron."""

    def __init__(self, **properties):
        self._data: list = []
        self._ready = False
        super().__init__(**properties)
        self._ready = True
        self._draw()

    def _draw(self):
        if not self._ready:
            return
        box = self.dom_nodes["box"]
        box.innerHTML = window.PX.radar(px.js(self._data or [])) if self._data else ""

    @property
    def data(self):
        return self._data

    @data.setter
    def data(self, value):
        self._data = list(value or [])
        self._draw()
