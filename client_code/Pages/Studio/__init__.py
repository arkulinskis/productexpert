import json

import anvil.media
import anvil.server
import anvil.js
from anvil import *
from anvil.js import window

from ._anvil_designer import StudioTemplate
from ... import px, redpen, router, state

FIELDS = [f[0] for f in redpen.STRATEGY_FIELDS]
KIND_TITLE = {"strategy": "Strategy one-pager", "roadmap": "Outcome roadmap"}


class Studio(StudioTemplate):
    """#studio: Red Pen Studio. Rule-based margin notes (client_code/redpen.py, the same rules the server uses) on a
    strategy one-pager or an outcome roadmap.
      #studio                    practice briefs (get_studio_briefs), "My own" document types, the member's saved docs
      #studio/own/<kind>         My own: drafts live in this browser (UI.store) and NOTHING is sent to the server
      #studio/practice/<brief>   a practice brief: write, red-pen (in the browser), Save (members) -> the model answer
      #studio/doc/<id>           a saved practice doc (owner only, get_studio_doc)
    Red pen it -> grade + notes; .md download and Print include the notes."""

    def __init__(self, args=(), **properties):
        super().__init__(**properties)
        self._mode, self._kind, self._brief, self._doc_id = "", "strategy", None, None
        self._result = None
        self._cols: dict = {"now": [], "next": [], "later": []}
        for name in ("now", "next", "later"):
            getattr(self, name + "_panel").add_event_handler("x-remove", self._remove_card)
        self.docs_panel.add_event_handler("x-delete", self._delete_doc)
        for key, _label, hint in redpen.STRATEGY_FIELDS:
            px.set_text(self.dom_nodes["h_" + key], hint)
            state.set_control_attr(getattr(self, "f_" + key), "maxlength", str(redpen.FIELD_MAX))
        state.set_control_attr(self.title_box, "maxlength", "120")
        state.set_control_attr(self.title_box, "aria-label", "Title")
        self.dom_nodes["signin_link"].addEventListener("click", anvil.js.report_exceptions(self._signin_click))
        args = list(args or [])
        if not args:
            self._index()
        elif args[0] == "own" and len(args) > 1 and args[1] in KIND_TITLE:
            self._open_own(args[1])
        elif args[0] == "practice" and len(args) > 1:
            self._open_practice(args[1])
        elif args[0] == "doc" and len(args) > 1:
            self._open_doc(args[1])
        else:
            self._index()

    # ---- views
    def _show(self, view):
        self.index_part.visible = view == "index"
        self.edit_part.visible = view == "edit"
        self.missing_part.visible = view == "missing"

    def _index(self):
        self.hero.set(fig="strategy", title="Red Pen Studio",
                      lead="Write a strategy one-pager or an outcome roadmap and get sourced margin notes in a second: "
                           "Rumelt's hallmarks of bad strategy, outputs posing as outcomes, dates nobody can keep. "
                           "Rule-based, so it's instant and nothing goes to an AI.",
                      meta=[["pen", "Two document types"], ["lock", "My own mode stays in your browser"],
                            ["star", "+10 XP for your first B"]])
        briefs = anvil.server.call_s("get_studio_briefs")["briefs"]
        self.briefs_panel.items = briefs
        self.briefs_error.visible = not briefs
        me = state.me()
        self.mine_part.visible = bool(me)
        if me:
            docs = anvil.server.call_s("list_studio_docs")["items"]
            self.docs_panel.items = docs
            self.no_docs.visible = not docs
            self.docs_panel.visible = bool(docs)
        self._show("index")

    def _setup_editor(self, kind, mode):
        self._kind, self._mode = kind, mode
        self.strategy_part.visible = kind == "strategy"
        self.roadmap_part.visible = kind == "roadmap"
        self.local_note.visible = mode == "own"
        me = state.me()
        practice = mode in ("practice", "doc")
        self.brief_box.visible = practice
        self.save_button.visible = practice and bool(me)
        self.dom_nodes["signin_link"].hidden = not (practice and not me)
        self.clear_button.visible = mode == "own"
        self.model_box.visible = False
        self._result = None
        self._draw_result()
        self._show("edit")

    def _open_own(self, kind):
        self.hero.set(fig="strategy" if kind == "strategy" else "portfolio", title="Your %s" % KIND_TITLE[kind].lower(),
                      crumbs=[["#studio", "Red Pen Studio"], [None, "My own"]],
                      lead="Paste or write your real document. It's saved in this browser only, and marked in the browser too.")
        self._setup_editor(kind, "own")
        saved = self._local_get("own_" + kind)
        self._fill(saved.get("doc") if saved else redpen.blank(kind), (saved or {}).get("title") or "")
        if saved and saved.get("doc"):
            self._pen()

    def _open_practice(self, brief_id):
        briefs = anvil.server.call_s("get_studio_briefs")["briefs"]
        b = None
        for x in briefs:
            if x["id"] == brief_id:
                b = x
        if b is None:
            self._missing("That practice brief doesn't exist")
            return
        self._brief = b
        self.hero.set(fig="strategy" if b["kind"] == "strategy" else "portfolio", title=b["title"],
                      crumbs=[["#studio", "Red Pen Studio"], [None, "Practice brief"]],
                      lead="Red-pen the company's draft, rewrite it, then save it to compare with the model answer.",
                      meta=[["pen", KIND_TITLE[b["kind"]]], ["star", "+10 XP for your first B"]])
        self._setup_editor(b["kind"], "practice")
        self._draw_brief(b)
        saved = self._local_get("practice_" + brief_id)
        if saved and saved.get("doc"):
            self._fill(saved["doc"], saved.get("title") or b["title"])
        else:
            self._fill(b["start"], b["title"])
        self._pen()

    def _open_doc(self, doc_id):
        if not state.me():
            router.remember_after(window.location.hash)
            router.go("auth")
            return
        r = anvil.server.call("get_studio_doc", doc_id)
        if not r.get("ok"):
            self._missing("That document isn't here")
            return
        d = r["doc"]
        b = d.get("brief_data")
        self._doc_id = d["id"]
        self._brief = b
        self.hero.set(fig="strategy" if d["kind"] == "strategy" else "portfolio", title=d["title"],
                      crumbs=[["#studio", "Red Pen Studio"], [None, "Saved document"]],
                      meta=[["pen", KIND_TITLE[d["kind"]]], ["calendar", "Saved %s" % px.date(d["updated"], "long")]])
        self._setup_editor(d["kind"], "doc")
        if b:
            self._draw_brief(b)
        self._fill(d["doc"], d["title"])
        self._pen()
        if b and b.get("model"):
            self._draw_model(b)

    def _missing(self, head):
        self.hero.set(fig="strategy", title="Not found", crumbs=[["#studio", "Red Pen Studio"], [None, "Not found"]])
        px.set_text(self.dom_nodes["missing_head"], head)
        self._show("missing")

    def _draw_brief(self, b):
        n = self.dom_nodes
        px.set_text(n["brief_title"], "The situation")
        px.set_text(n["brief_situation"], b["situation"])
        px.set_text(n["brief_ask"], b["ask"])

    def _draw_model(self, b):
        self.model_box.visible = True
        self.model_text.content = redpen.to_markdown(b["kind"], "Model answer", b["model"], None).split("\n", 2)[2]
        mr = b.get("model_result") or redpen.grade(b["kind"], b["model"])
        px.set_text(self.dom_nodes["model_grade"], "Red pen: %s · %d/100" % (mr["grade"], mr["score"]))
        self.dom_nodes["model_ch"].setAttribute("href", "#challenge/" + b["challenge"])

    # ---- the document
    def _fill(self, doc, title):
        doc = redpen.clean(self._kind, doc or {})
        self.title_box.text = title or ""
        if self._kind == "strategy":
            for key in FIELDS:
                getattr(self, "f_" + key).text = doc.get(key) or ""
        else:
            for col, _label in redpen.ROADMAP_COLS:
                cards = list(doc.get(col) or [])
                self._cols[col] = cards if cards else [redpen.blank_card()]
            self._draw_cols()

    def _draw_cols(self):
        for col, label in redpen.ROADMAP_COLS:
            cards = self._cols[col]
            getattr(self, col + "_panel").items = [dict(c, col=col, col_label=label, i=i, n=len(cards)) for i, c in enumerate(cards)]
            getattr(self, "add_" + col).visible = len(cards) < redpen.MAX_CARDS

    def _read_cols(self):
        for col, _label in redpen.ROADMAP_COLS:
            self._cols[col] = [form.value() for form in getattr(self, col + "_panel").get_components()]

    def _collect(self):
        if self._kind == "strategy":
            doc = {}
            for key in FIELDS:
                doc[key] = getattr(self, "f_" + key).text or ""
            return redpen.clean("strategy", doc)
        self._read_cols()
        return redpen.clean("roadmap", self._cols)

    def _add(self, col):
        self._read_cols()
        if len(self._cols[col]) < redpen.MAX_CARDS:
            self._cols[col].append(redpen.blank_card())
        self._draw_cols()

    def _remove_card(self, col, i, **event_args):
        self._read_cols()
        cards = self._cols[col]
        if 0 <= i < len(cards):
            cards.pop(i)
        if not cards:
            cards.append(redpen.blank_card())
        self._draw_cols()

    @handle("add_now", "click")
    def add_now_click(self, **event_args):
        self._add("now")

    @handle("add_next", "click")
    def add_next_click(self, **event_args):
        self._add("next")

    @handle("add_later", "click")
    def add_later_click(self, **event_args):
        self._add("later")

    # ---- red pen (in the browser: no server call)
    def _pen(self):
        doc = self._collect()
        self._result = redpen.grade(self._kind, doc)
        self._draw_result()
        self._remember(doc)
        return doc

    def _draw_result(self):
        r = self._result
        n = self.dom_nodes
        self.mark_box.visible = bool(r)
        self.no_notes.visible = not r
        self.notes_panel.visible = bool(r)
        if not r:
            self.notes_panel.items = []
            return
        n["stamp"].className = "sd-stamp g-" + r["grade"]
        px.set_text(n["grade"], r["grade"])
        px.set_text(n["score"], "%d/100" % r["score"])
        heads = {"A": "Board-ready", "B": "Solid, with a few fixes", "C": "Needs another pass", "D": "Back to the drawing board"}
        px.set_text(n["mark_head"], heads[r["grade"]])
        bits = []
        if r["majors"]:
            bits.append(state.plural(r["majors"], "major note"))
        if r["minors"]:
            bits.append(state.plural(r["minors"], "minor note"))
        px.set_text(n["mark_sub"], (", ".join(bits) if bits else "No problems found") + ". Fix the majors first.")
        self.notes_panel.items = r["notes"]
        self.print_text.content = redpen.to_markdown(self._kind, self.title_box.text or KIND_TITLE[self._kind],
                                                     self._collect(), r, self._brief["ask"] if self._brief else None)

    @handle("pen_button", "click")
    def pen_button_click(self, **event_args):
        self._pen()
        if self._result:
            anvil.js.get_dom_node(self.mark_box).scrollIntoView({"behavior": "smooth", "block": "nearest"})

    # ---- local drafts (My own, and practice drafts before saving)
    def _store_key(self):
        if self._mode == "own":
            return "own_" + self._kind
        if self._mode == "practice" and self._brief:
            return "practice_" + self._brief["id"]
        return None

    def _local_get(self, key):
        raw = state.store_get("studio_" + key)
        if not raw:
            return None
        try:
            v = json.loads(str(raw))
            return v if isinstance(v, dict) else None
        except Exception:
            return None

    def _remember(self, doc=None):
        key = self._store_key()
        if key is None:
            return
        state.store_set("studio_" + key, json.dumps({"doc": doc if doc is not None else self._collect(),
                                                      "title": self.title_box.text or ""}))

    @handle("clear_button", "click")
    def clear_button_click(self, **event_args):
        if not confirm("Clear this document? It can't be brought back.", title="Start over",
                       buttons=[("Cancel", False), ("Clear it", True)]):
            return
        state.store_set("studio_" + self._store_key(), "")
        self._fill(redpen.blank(self._kind), "")
        self._result = None
        self._draw_result()

    @handle("draft_button", "click")
    def draft_button_click(self, **event_args):
        if self._brief:
            self._fill(self._brief["start"], self.title_box.text or self._brief["title"])
            self._pen()

    @handle("blank_button", "click")
    def blank_button_click(self, **event_args):
        self._fill(redpen.blank(self._kind), self.title_box.text)
        self._result = None
        self._draw_result()

    # ---- save (members, practice briefs only)
    def _signin_click(self, event):
        self._remember()
        router.remember_after(window.location.hash)

    @handle("save_button", "click")
    def save_button_click(self, **event_args):
        if not self._brief:
            return
        doc = self._pen()
        self.save_button.enabled = False
        try:
            r = state.call("save_studio_doc", self._doc_id, self._brief["id"], doc, self.title_box.text, px.today())
        finally:
            self.save_button.enabled = True
        if not r:
            return
        d = r["doc"]
        self._doc_id = d["id"]
        if self._mode == "practice":
            state.store_set("studio_practice_" + self._brief["id"], "")
            self._mode = "doc"
            router.replace("studio", "doc", d["id"])
        self._result = r["result"]
        self._draw_result()
        if d.get("brief_data"):
            self._draw_model(d["brief_data"])
        msg = "Saved: %s (%d/100)." % (r["result"]["grade"], r["result"]["score"])
        if r.get("xp_gained"):
            msg += " +%d XP for your first B." % r["xp_gained"]
            px.confetti()
        state.toast(msg, "ok")
        anvil.js.get_dom_node(self.model_box).scrollIntoView({"behavior": "smooth", "block": "start"})

    # ---- download / print
    @handle("download_button", "click")
    def download_button_click(self, **event_args):
        doc = self._pen()
        title = self.title_box.text or KIND_TITLE[self._kind]
        md = redpen.to_markdown(self._kind, title, doc, self._result, self._brief["ask"] if self._brief else None)
        slug = "".join(ch if ch.isalnum() else "-" for ch in title.lower()).strip("-")[:50] or "red-pen"
        anvil.media.download(anvil.BlobMedia("text/markdown", md.encode("utf-8"), name=slug + ".md"))

    @handle("print_button", "click")
    def print_button_click(self, **event_args):
        self._pen()
        window.print()

    # ---- saved docs list
    def _delete_doc(self, doc_id, **event_args):
        if not confirm("Delete this document? It can't be brought back.", title="Delete",
                       buttons=[("Cancel", False), ("Delete", True)]):
            return
        if state.call("delete_studio_doc", doc_id):
            state.toast("Deleted.", "ok")
            docs = anvil.server.call_s("list_studio_docs")["items"]
            self.docs_panel.items = docs
            self.no_docs.visible = not docs
            self.docs_panel.visible = bool(docs)

    @handle("", "hide")
    def form_hide(self, **event_args):
        if self.edit_part.visible and self._mode in ("own", "practice"):
            self._remember()
