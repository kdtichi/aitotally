#!/usr/bin/env python3
"""Static site generator for aitotally.com (AI Totally).

Reads data/site.json and data/brands.json and renders the whole site into
dist/. Python 3 standard library only.

Usage: python3 build/build.py
"""
import os
import shutil
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from brand_page import render_brand  # noqa: E402
from common import BRANDS, CATEGORIES, DIST, PUBLIC, SITE, brands_in, page_updated  # noqa: E402
from legal import (render_accessibility, render_editorial_policy, render_privacy,  # noqa: E402
                   render_terms, render_trademark)
from indexnow import key, key_file_name, ping_changed  # noqa: E402
from machine import llms_full_txt, llms_txt, robots_txt, sitemap_xml  # noqa: E402
from research import CSV_PATH, PATH as RESEARCH_PATH, csv_text, render_research  # noqa: E402
from pages import (render_404, render_about, render_category, render_contact, render_faq,  # noqa: E402
                   render_home, render_how_it_works)

STATIC_PAGES = {
    "/": render_home,
    "/about/": render_about,
    "/contact/": render_contact,
    "/how-it-works/": render_how_it_works,
    "/faq/": render_faq,
    "/privacy/": render_privacy,
    "/terms/": render_terms,
    "/trademark-notice/": render_trademark,
    "/editorial-policy/": render_editorial_policy,
    "/accessibility/": render_accessibility,
    RESEARCH_PATH: render_research,
}

PUBLIC_FILES = ("favicon.svg", "logo.png", "og-image.png")
PUBLIC_DIRS = ("css", "js", "og")


def write(rel_path: str, content: str) -> None:
    full = os.path.join(DIST, rel_path.lstrip("/"))
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w", encoding="utf-8") as f:
        f.write(content)


def page_file(path: str) -> str:
    return path.lstrip("/") + "index.html"


def copy_public() -> None:
    for d in PUBLIC_DIRS:
        src = os.path.join(PUBLIC, d)
        if os.path.isdir(src):
            shutil.copytree(src, os.path.join(DIST, d))
    for f in PUBLIC_FILES:
        src = os.path.join(PUBLIC, f)
        if os.path.exists(src):
            shutil.copy(src, os.path.join(DIST, f))


def sitemap_entries() -> list:
    """(path, lastmod) pairs. lastmod is when that page's content really changed:
    the later of its copy date and its contact details' verification date."""
    launch = SITE["launchDate"]
    entries = [(p, page_updated(p)) for p in STATIC_PAGES]
    for slug in CATEGORIES:
        dates = [b["verifiedDate"] for b in brands_in(slug)] + [launch]
        entries.append(("/category/{}/".format(slug), max(dates)))
    entries += [("/brand/{}/".format(b["slug"]), max(b["verifiedDate"], launch)) for b in BRANDS]
    return entries


def build() -> int:
    if os.path.exists(DIST):
        shutil.rmtree(DIST)
    os.makedirs(DIST)
    copy_public()

    for path, render in STATIC_PAGES.items():
        write(page_file(path), render())
    write("404.html", render_404())
    for slug in CATEGORIES:
        write(page_file("/category/{}/".format(slug)), render_category(slug))
    for b in BRANDS:
        write(page_file("/brand/{}/".format(b["slug"])), render_brand(b, SITE["launchDate"]))

    entries = sitemap_entries()
    write("sitemap.xml", sitemap_xml(entries))
    write("robots.txt", robots_txt())
    write("llms.txt", llms_txt())
    write("llms-full.txt", llms_full_txt())
    write(CSV_PATH, csv_text())
    write(key_file_name(), key())
    return len(entries)


if __name__ == "__main__":
    count = build()
    sys.stdout.write("Built {} pages into {}\n".format(count, DIST))
    ping_changed(sitemap_entries())
