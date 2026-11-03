"""Data loading, validation and shared helpers for the AI Totally build.

All content lives in ``data/``:
- ``site.json``   site settings, category copy and page dates
- ``brands.json`` one record per company: verified contact facts plus the
  "what to try first" tip for each common issue
"""
import html as html_lib
import json
import os
import re
from urllib.parse import urlparse

SITE_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(SITE_ROOT, "data")
DIST = os.path.join(SITE_ROOT, "dist")
PUBLIC = os.path.join(SITE_ROOT, "public")

REQUIRED_BRAND_FIELDS = ("slug", "name", "category", "chatUrl", "chatLabel", "chatType",
                         "hours", "verifiedDate", "sourceUrl", "sourceLabel", "issues")
CHAT_TYPES = ("chat", "form", "none")
HOURS_MODES = ("247", "unspecified", "detailed")
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
SLUG_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


class DataError(ValueError):
    """Raised when a data file is missing something the site needs."""


def _load_json(name: str, data_dir: str) -> dict:
    with open(os.path.join(data_dir, name), "r", encoding="utf-8") as f:
        return json.load(f)


def validate_brand(b: dict, categories: dict) -> None:
    label = "brands.json entry {!r}".format(b.get("slug"))
    missing = [k for k in REQUIRED_BRAND_FIELDS if not b.get(k)]
    if missing:
        raise DataError("{} is missing: {}".format(label, ", ".join(missing)))
    if "phone" not in b:
        raise DataError("{} needs a phone field (use null when none is published)".format(label))
    if not SLUG_RE.match(b["slug"]):
        raise DataError("{} has an invalid slug".format(label))
    if b["category"] not in categories:
        raise DataError("{} uses unknown category {!r}".format(label, b["category"]))
    if b["chatType"] not in CHAT_TYPES:
        raise DataError("{} chatType must be one of {}".format(label, CHAT_TYPES))
    if b["hours"].get("mode") not in HOURS_MODES:
        raise DataError("{} hours.mode must be one of {}".format(label, HOURS_MODES))
    if not DATE_RE.match(b["verifiedDate"]):
        raise DataError("{} verifiedDate must be YYYY-MM-DD".format(label))
    for url_key in ("chatUrl", "sourceUrl"):
        if not b[url_key].startswith("https://"):
            raise DataError("{} {} must be an https URL".format(label, url_key))
    for issue in b["issues"]:
        if not issue.get("issue") or not issue.get("tip"):
            raise DataError("{} has an issue without both 'issue' and 'tip'".format(label))


def load(data_dir: str = DATA_DIR) -> dict:
    copy = _load_json("site.json", data_dir)
    brands = _load_json("brands.json", data_dir)["brands"]
    categories = {slug: {"slug": slug, **c} for slug, c in copy["categories"].items()}
    seen = set()
    for b in brands:
        validate_brand(b, categories)
        if b["slug"] in seen:
            raise DataError("brands.json has a duplicate slug {!r}".format(b["slug"]))
        seen.add(b["slug"])
    site = copy["site"]
    return {
        "site": site,
        "pages_updated": copy["pagesUpdated"],
        "categories": categories,
        "brands": brands,
        "base_url": "https://" + site["domain"],
    }


DATA = load()
SITE = DATA["site"]
CATEGORIES = DATA["categories"]
BRANDS = DATA["brands"]
BASE_URL = DATA["base_url"]
PAGES_UPDATED = DATA["pages_updated"]
NAME = SITE["name"]


def esc(value) -> str:
    return html_lib.escape(str(value), quote=True)


def unesc(value: str) -> str:
    return html_lib.unescape(value)


def brand_by_slug(slug: str):
    return next((b for b in BRANDS if b["slug"] == slug), None)


def brands_in(cat_slug: str) -> list:
    return [b for b in BRANDS if b["category"] == cat_slug]


def initial_mark(name: str) -> str:
    return esc(name.strip()[0].upper())


def official_root(url: str) -> str:
    p = urlparse(url)
    return p.scheme + "://" + p.netloc + "/"


def schema_phone(phone: str) -> str:
    """US numbers in +1 form for structured data; page text keeps the published format."""
    digits = "".join(ch for ch in phone if ch.isdigit())
    if len(digits) == 10:
        digits = "1" + digits
    if len(digits) == 11 and digits.startswith("1"):
        return "+1-{}-{}-{}".format(digits[1:4], digits[4:7], digits[7:])
    return phone


def tel_href(phone: str) -> str:
    return "tel:" + "".join(ch for ch in phone if ch.isdigit() or ch == "+")


def human_date(iso: str) -> str:
    months = ("January", "February", "March", "April", "May", "June", "July",
              "August", "September", "October", "November", "December")
    year, month, day = iso.split("-")
    return "{} {}, {}".format(months[int(month) - 1], int(day), year)


def page_updated(path: str) -> str:
    return PAGES_UPDATED.get(path, SITE["launchDate"])
