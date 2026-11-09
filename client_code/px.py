"""Product Expert helpers on top of state.py: the JavaScript engines in theme/assets/px-kit.js (schematics, stamp,
certificate, progress ring, confetti, the landing bet board), dates in the browser's language and small text helpers.

    px.today()                the member's local date (YYYY-MM-DD): streaks and due dates follow their day
    px.fig(name)              a program's schematic as an SVG string (judgement, strategy, discovery, metrics, gtm, org, influence, frontier, director, ...)
    px.fig_caption(name)      that schematic's one-line caption
    px.date(iso, style)       'short' | 'long' | 'month' | 'time'
    px.confetti()             a short burst for a pass (nothing under reduced motion)
    px.verify_url(code)       the public verification address of a credential
    px.js(value)              a Python dict/list as a real JS object (for the engines)
    px.set_text(node, text)   textContent on an anvil:dom-node
    px.title(text)            the browser tab title: "<text> · Product Expert"
"""
import json

from anvil.js import window

APP_NAME = "Product Expert"
INSTITUTE = "Product Expert"

TRACK_FIG = {"core": "judgement", "str": "strategy", "dsc": "discovery", "grw": "metrics", "biz": "gtm", "org": "org",
             "inf": "influence", "frn": "frontier", "fellow": "director"}


def today():
    return str(window.PX.today())


def fig(name):
    return str(window.PX.fig(name or "director"))


def fig_caption(name):
    return str(window.PX.figCaption(name or "director"))


def date(iso, style="short"):
    return str(window.PX.fmtDate(iso or "", style)) if iso else ""


def ago(iso):
    from . import state
    return state.ago(iso)


def confetti():
    window.PX.confetti()


def verify_url(code):
    return str(window.PX.verifyUrl(code))


def weekday(day):
    return str(window.PX.weekday(day))


def js(value):
    return window.JSON.parse(json.dumps(value))


def set_text(node, text):
    node.textContent = "" if text is None else str(text)


def title(text):
    window.document.title = "%s · %s" % (text, APP_NAME)


def hours(minutes):
    """'~1.5' hours from minutes (one decimal)."""
    return "%g" % (round((minutes or 0) / 6.0) / 10.0)


def tone_badge(tone):
    """(text, badge roles) for a case file's tone."""
    if tone == "exemplary":
        return "Done right", ["badge", "badge-good"]
    if tone == "cautionary":
        return "Cautionary", ["badge", "badge-bad"]
    return "Mixed lessons", ["badge", "badge-warn"]
