#!/usr/bin/env python3
"""IndexNow: tell Bing and other participating search engines which URLs changed.

During a Netlify *production* build, build.py compares the new sitemap with the
one currently live on www.aitotally.com and submits only new or updated URLs.
If the live sitemap can't be read (e.g. the very first deploy), every URL is
submitted. A failed submission is logged and never fails the build.

Submit everything by hand (e.g. after first enabling IndexNow):

    python3 build/indexnow.py --all
"""
import json
import os
import sys
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from common import BASE_URL, SITE  # noqa: E402

ENDPOINT = "https://api.indexnow.org/indexnow"
SITEMAP_NS = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9"}
TIMEOUT_SECONDS = 15
MAX_URLS_PER_REQUEST = 10000
OK_STATUSES = (200, 202)


def key() -> str:
    return SITE["indexNowKey"]


def key_file_name() -> str:
    return "{}.txt".format(key())


def parse_sitemap(xml_text: str) -> dict:
    """Map each <loc> to its <lastmod> ('' when missing)."""
    root = ET.fromstring(xml_text)
    out = {}
    for url in root.findall("s:url", SITEMAP_NS):
        loc = url.find("s:loc", SITEMAP_NS)
        lastmod = url.find("s:lastmod", SITEMAP_NS)
        if loc is not None and loc.text:
            out[loc.text.strip()] = (lastmod.text or "").strip() if lastmod is not None else ""
    return out


def changed_urls(new_entries: list, live: dict | None) -> list:
    """URLs that are new or whose lastmod moved. ``live`` None means submit all."""
    urls = [(BASE_URL + path, lastmod) for path, lastmod in new_entries]
    if live is None:
        return [u for u, _ in urls]
    return [u for u, lastmod in urls if live.get(u) != lastmod]


def payload(urls: list) -> dict:
    return {
        "host": SITE["domain"],
        "key": key(),
        "keyLocation": "{}/{}".format(BASE_URL, key_file_name()),
        "urlList": urls[:MAX_URLS_PER_REQUEST],
    }


def fetch_live_sitemap() -> dict | None:
    try:
        with urllib.request.urlopen(BASE_URL + "/sitemap.xml", timeout=TIMEOUT_SECONDS) as resp:
            return parse_sitemap(resp.read().decode("utf-8"))
    except (urllib.error.URLError, ET.ParseError, TimeoutError, OSError) as err:
        sys.stderr.write("indexnow: could not read live sitemap ({}); submitting all URLs\n".format(err))
        return None


def submit(urls: list) -> bool:
    if not urls:
        sys.stdout.write("indexnow: nothing changed, nothing to submit\n")
        return True
    body = json.dumps(payload(urls)).encode("utf-8")
    req = urllib.request.Request(ENDPOINT, data=body, method="POST",
                                 headers={"Content-Type": "application/json; charset=utf-8"})
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT_SECONDS) as resp:
            ok = resp.status in OK_STATUSES
            sys.stdout.write("indexnow: submitted {} URL(s), HTTP {}\n".format(len(urls), resp.status))
            return ok
    except urllib.error.HTTPError as err:
        sys.stderr.write("indexnow: submission rejected, HTTP {} {}\n".format(err.code, err.reason))
    except (urllib.error.URLError, TimeoutError, OSError) as err:
        sys.stderr.write("indexnow: submission failed ({})\n".format(err))
    return False


def should_ping(env: dict) -> bool:
    """Only Netlify production builds ping; previews, branch deploys and local builds don't."""
    return env.get("CONTEXT") == "production" and env.get("INDEXNOW_DISABLE") != "1"


def ping_changed(new_entries: list, env: dict | None = None) -> None:
    env = os.environ if env is None else env
    if not should_ping(env):
        return
    submit(changed_urls(new_entries, fetch_live_sitemap()))


if __name__ == "__main__":
    if "--all" not in sys.argv:
        sys.stderr.write("usage: python3 build/indexnow.py --all\n")
        sys.exit(2)
    from build import sitemap_entries
    sys.exit(0 if submit(changed_urls(sitemap_entries(), None)) else 1)
