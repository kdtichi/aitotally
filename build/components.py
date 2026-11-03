"""Reusable HTML pieces, chiefly linkable question-and-answer blocks.

Every tip and FAQ answer gets a stable fragment id (e.g. ``#faq-what-are-delta-s-hours``)
so search engines, AI assistants and people can link straight to one answer.
The same ids are used as each Question's ``url`` in the FAQPage schema.
"""
import re

from common import unesc

_NON_ALNUM = re.compile(r"[^a-z0-9]+")
MAX_ID_WORDS = 8


def anchor_slug(text: str) -> str:
    """Readable, URL-safe slug from visible text (HTML entities and tags ignored)."""
    plain = re.sub(r"<[^>]+>", "", unesc(text)).lower().replace("’", "'").replace("'", "")
    words = [w for w in _NON_ALNUM.split(plain) if w]
    return "-".join(words[:MAX_ID_WORDS]) or "item"


def anchor_ids(questions: list, prefix: str) -> list:
    """One unique id per question, stable across builds, e.g. ``faq-how-do-i-...``."""
    seen: dict = {}
    ids = []
    for q in questions:
        base = "{}-{}".format(prefix, anchor_slug(q))
        seen[base] = seen.get(base, 0) + 1
        ids.append(base if seen[base] == 1 else "{}-{}".format(base, seen[base]))
    return ids


def qa_details(items: list, prefix: str, ids: list | None = None) -> str:
    """Render (question_html, answer_html) pairs as linkable accordions.
    Pass ``ids`` for fixed anchors; otherwise they are derived from the questions."""
    ids = ids or anchor_ids([q for q, _ in items], prefix)
    return "".join(
        '<details class="faq-item" id="{id}"><summary>{q}</summary>'
        '<div class="faq-body"><p>{a}</p>'
        '<a class="answer-link" href="#{id}">Link to this answer</a></div></details>'.format(id=i, q=q, a=a)
        for i, (q, a) in zip(ids, items))
