"""Tests for the AI Totally generator. Standard library only:

    cd aitotally && python3 -m unittest discover -s tests -v

(pytest also runs these unchanged.)
"""
import json
import os
import re
import sys
import unittest
import xml.etree.ElementTree as ET

SITE_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(SITE_ROOT, "build"))

import build  # noqa: E402
import brand_page  # noqa: E402
import common  # noqa: E402

LD_RE = re.compile(r'<script type="application/ld\+json">(.*?)</script>', re.S)


def read_dist(rel: str) -> str:
    with open(os.path.join(common.DIST, rel), encoding="utf-8") as f:
        return f.read()


def json_ld(html: str) -> dict:
    blocks = LD_RE.findall(html)
    assert len(blocks) == 1, "expected exactly one JSON-LD block"
    return json.loads(blocks[0])


def graph_types(ld: dict) -> list:
    return [n["@type"] for n in ld["@graph"]]


class DataTests(unittest.TestCase):
    def _brand(self, **overrides):
        b = {"slug": "acme", "name": "Acme", "category": "retail", "phone": None,
             "chatUrl": "https://acme.example/help", "chatLabel": "Acme Help", "chatType": "chat",
             "hours": {"mode": "247"}, "verifiedDate": "2026-11-03",
             "sourceUrl": "https://acme.example/contact", "sourceLabel": "Acme Contact",
             "issues": [{"issue": "Refunds", "tip": "Check your order page first."}]}
        b.update(overrides)
        return b

    def test_valid_brand_passes(self):
        common.validate_brand(self._brand(), common.CATEGORIES)

    def test_missing_phone_field_is_rejected(self):
        b = self._brand()
        del b["phone"]
        with self.assertRaises(common.DataError):
            common.validate_brand(b, common.CATEGORIES)

    def test_unknown_category_is_rejected(self):
        with self.assertRaises(common.DataError):
            common.validate_brand(self._brand(category="nope"), common.CATEGORIES)

    def test_non_https_source_is_rejected(self):
        with self.assertRaises(common.DataError):
            common.validate_brand(self._brand(sourceUrl="http://acme.example"), common.CATEGORIES)

    def test_bad_date_is_rejected(self):
        with self.assertRaises(common.DataError):
            common.validate_brand(self._brand(verifiedDate="3 Nov 2026"), common.CATEGORIES)

    def test_issue_without_tip_is_rejected(self):
        with self.assertRaises(common.DataError):
            common.validate_brand(self._brand(issues=[{"issue": "Refunds"}]), common.CATEGORIES)

    def test_every_brand_has_issues_with_tips(self):
        for b in common.BRANDS:
            self.assertGreaterEqual(len(b["issues"]), 5, b["slug"])

    def test_every_category_has_its_own_copy(self):
        for slug, cat in common.CATEGORIES.items():
            self.assertGreater(len(cat["intro"].split()), 80, slug)

    def test_schema_phone_formats_us_numbers(self):
        self.assertEqual(common.schema_phone("(800) 207-7847"), "+1-800-207-7847")
        self.assertEqual(common.schema_phone("1-800-937-8997"), "+1-800-937-8997")


class BrandCopyTests(unittest.TestCase):
    def test_quick_answer_with_phone_names_the_number(self):
        b = common.brand_by_slug("t-mobile")
        self.assertIn(b["phone"], brand_page.quick_answer(b))

    def test_quick_answer_without_phone_says_none_published(self):
        b = common.brand_by_slug("instagram")
        self.assertIn("doesn&rsquo;t publish a customer service phone number", brand_page.quick_answer(b))

    def test_detailed_hours_render_in_company_time_zone(self):
        b = common.brand_by_slug("t-mobile")
        self.assertEqual(brand_page.hours_sentence(b), "Support runs 4:00 AM&ndash;9:00 PM Pacific time, every day.")


class CategorySummaryTests(unittest.TestCase):
    def test_all_with_phone(self):
        import pages
        self.assertEqual(pages.category_summary(4, 4, "Airlines"),
                         "Every company in our Airlines section (4) publishes a customer service phone number.")

    def test_none_with_phone(self):
        import pages
        self.assertTrue(pages.category_summary(0, 3, "Streaming").startswith("None of the 3 companies"))

    def test_mixed(self):
        import pages
        self.assertIn("the other 6 rely on", pages.category_summary(2, 8, "Shopping"))


class BuiltSiteTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.page_count = build.build()

    def test_every_brand_and_category_page_exists(self):
        for b in common.BRANDS:
            self.assertTrue(os.path.exists(os.path.join(common.DIST, "brand", b["slug"], "index.html")), b["slug"])
        for slug in common.CATEGORIES:
            self.assertTrue(os.path.exists(os.path.join(common.DIST, "category", slug, "index.html")), slug)

    def test_brand_page_has_canonical_quick_answer_and_linked_schema(self):
        html = read_dist("brand/delta/index.html")
        self.assertIn('<link rel="canonical" href="https://www.aitotally.com/brand/delta/">', html)
        self.assertIn('class="quick-answer"', html)
        self.assertIn("800-221-1212", html)
        ld = json_ld(html)
        types = graph_types(ld)
        for t in ("Organization", "WebSite", "WebPage", "BreadcrumbList", "FAQPage"):
            self.assertIn(t, types)
        page = next(n for n in ld["@graph"] if n["@type"] == "WebPage")
        self.assertIn("speakable", page)
        self.assertEqual(page["about"]["contactPoint"][0]["telephone"], "+1-800-221-1212")

    def test_faq_schema_matches_visible_questions(self):
        html = read_dist("brand/uber/index.html")
        faq = next(n for n in json_ld(html)["@graph"] if n["@type"] == "FAQPage")
        for q in faq["mainEntity"]:
            self.assertIn(q["name"].replace("'", "&rsquo;"), html)

    def test_only_one_faqpage_per_page(self):
        for rel in ("faq/index.html", "index.html", "brand/amazon/index.html"):
            self.assertLessEqual(graph_types(json_ld(read_dist(rel))).count("FAQPage"), 1, rel)

    def test_sitemap_is_valid_and_lists_every_page(self):
        tree = ET.fromstring(read_dist("sitemap.xml"))
        ns = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9"}
        locs = [u.find("s:loc", ns).text for u in tree.findall("s:url", ns)]
        self.assertEqual(len(locs), self.page_count)
        self.assertIn("https://www.aitotally.com/brand/delta/", locs)
        self.assertTrue(all(loc.startswith("https://www.aitotally.com/") for loc in locs))

    def test_sitemap_lastmod_never_precedes_verification(self):
        tree = ET.fromstring(read_dist("sitemap.xml"))
        ns = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9"}
        dates = {u.find("s:loc", ns).text: u.find("s:lastmod", ns).text for u in tree.findall("s:url", ns)}
        for b in common.BRANDS:
            self.assertGreaterEqual(dates["https://www.aitotally.com/brand/{}/".format(b["slug"])], b["verifiedDate"])

    def test_robots_allows_ai_crawlers_and_points_to_sitemap(self):
        robots = read_dist("robots.txt")
        for bot in ("GPTBot", "ClaudeBot", "PerplexityBot", "Google-Extended"):
            self.assertIn("User-agent: {}\nAllow: /".format(bot), robots)
        self.assertIn("Sitemap: https://www.aitotally.com/sitemap.xml", robots)
        self.assertNotIn("Disallow", robots)

    def test_llms_files_cover_every_brand(self):
        index, full = read_dist("llms.txt"), read_dist("llms-full.txt")
        self.assertTrue(index.startswith("# AI Totally\n\n> "))
        for b in common.BRANDS:
            self.assertIn("/brand/{}/".format(b["slug"]), index)
            self.assertIn("## {} customer service".format(b["name"]), full)

    def test_internal_links_resolve(self):
        href_re = re.compile(r'href="(/[^"#]*)"')
        broken = set()
        for root, _, files in os.walk(common.DIST):
            for name in files:
                if not name.endswith(".html"):
                    continue
                with open(os.path.join(root, name), encoding="utf-8") as f:
                    for href in href_re.findall(f.read()):
                        target = os.path.join(common.DIST, href.lstrip("/"))
                        if href.endswith("/"):
                            target = os.path.join(target, "index.html")
                        if not os.path.exists(target):
                            broken.add(href)
        self.assertEqual(broken, set())

    def test_titles_and_descriptions_are_unique(self):
        titles, descs = {}, {}
        for root, _, files in os.walk(common.DIST):
            for name in files:
                if name == "index.html":
                    html = read_dist(os.path.relpath(os.path.join(root, name), common.DIST))
                    t = re.search(r"<title>(.*?)</title>", html).group(1)
                    d = re.search(r'<meta name="description" content="(.*?)">', html).group(1)
                    titles.setdefault(t, []).append(root)
                    descs.setdefault(d, []).append(root)
        self.assertEqual([t for t, v in titles.items() if len(v) > 1], [])
        self.assertEqual([d for d, v in descs.items() if len(v) > 1], [])


if __name__ == "__main__":
    unittest.main()
