"""Static asset handling for fast page loads.

- CSS is minified and inlined into every page, so the first render never
  waits on a separate stylesheet request.
- JavaScript files get a content hash in their name (e.g. search.3f2a9c1b.js)
  so they can be cached for a year; a changed file gets a new name.
"""
import hashlib
import os
import re

from common import PUBLIC

CSS_PATH = os.path.join(PUBLIC, "css", "main.css")
JS_DIR = os.path.join(PUBLIC, "js")
HASH_LENGTH = 8


def minify_css(css: str) -> str:
    """Conservative minifier: drops comments and redundant whitespace only."""
    css = re.sub(r"/\*.*?\*/", "", css, flags=re.S)
    css = re.sub(r"\s+", " ", css)
    css = re.sub(r"\s*([{};,>])\s*", r"\1", css)
    css = re.sub(r";}", "}", css)
    return css.strip()


def inline_css() -> str:
    with open(CSS_PATH, encoding="utf-8") as f:
        return minify_css(f.read()).replace("</", "<\\/")


def _digest(path: str) -> str:
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()[:HASH_LENGTH]


def js_manifest() -> dict:
    """Map each source name (search.js) to its fingerprinted name (search.<hash>.js)."""
    out = {}
    for name in sorted(os.listdir(JS_DIR)):
        if name.endswith(".js"):
            stem = name[:-3]
            out[name] = "{}.{}.js".format(stem, _digest(os.path.join(JS_DIR, name)))
    return out


JS = js_manifest()
CSS_INLINE = inline_css()


def js_src(name: str) -> str:
    return "/js/" + JS[name]
