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

    def test_possessive_for_names_ending_in_s(self):
        self.assertEqual(brand_page.possessive("Delta Air Lines"), "Delta Air Lines&rsquo;")
        self.assertEqual(brand_page.possessive("Uber"), "Uber&rsquo;s")

    def test_detailed_hours_render_in_company_time_zone(self):
        b = common.brand_by_slug("t-mobile")
        self.assertEqual(brand_page.hours_sentence(b), "Support runs 4:00 AM&ndash;9:00 PM Pacific time, every day.")


class AnchorTests(unittest.TestCase):
    def test_anchor_slug_ignores_entities_and_apostrophes(self):
        import components
        self.assertEqual(components.anchor_slug("What are Delta&rsquo;s hours?"), "what-are-deltas-hours")

    def test_anchor_ids_are_unique(self):
        import components
        self.assertEqual(components.anchor_ids(["Refunds", "Refunds"], "issue"), ["issue-refunds", "issue-refunds-2"])

    def test_qa_details_links_each_answer_to_itself(self):
        import components
        html = components.qa_details([("Q one", "A")], "faq")
        self.assertIn('id="faq-q-one"', html)
        self.assertIn('href="#faq-q-one"', html)


class ResearchTests(unittest.TestCase):
    def test_stats_add_up(self):
        import research
        s = research.stats()
        self.assertEqual(s["with_phone"] + s["without"], s["total"])
        self.assertEqual(sum(s["channels"].values()), s["without"])
        self.assertEqual(sum(c["total"] for c in s["by_cat"]), s["total"])

    def test_headline_matches_data(self):
        import research
        s = research.stats()
        text = research.headline_answer(s)
        self.assertIn("{} ({}%)".format(s["without"], s["pct_without"]), text)
        for label in s["all_without"] + s["all_with"]:
            self.assertIn(label, text)

    def test_csv_has_one_row_per_company(self):
        import csv as csv_mod
        import io
        import research
        rows = list(csv_mod.DictReader(io.StringIO(research.csv_text())))
        self.assertEqual(len(rows), len(common.BRANDS))
        self.assertEqual(sum(r["publishes_phone_number"] == "no" for r in rows), research.stats()["without"])


class IndexNowTests(unittest.TestCase):
    def test_key_is_32_hex_chars(self):
        import indexnow
        self.assertRegex(indexnow.key(), r"^[0-9a-f]{32}$")

    def test_changed_urls_only_new_or_updated(self):
        import indexnow
        live = {common.BASE_URL + "/a/": "2026-01-01", common.BASE_URL + "/b/": "2026-01-01"}
        entries = [("/a/", "2026-01-01"), ("/b/", "2026-02-01"), ("/c/", "2026-01-01")]
        self.assertEqual(indexnow.changed_urls(entries, live), [common.BASE_URL + "/b/", common.BASE_URL + "/c/"])

    def test_changed_urls_submits_all_without_live_sitemap(self):
        import indexnow
        self.assertEqual(len(indexnow.changed_urls([("/a/", "x"), ("/b/", "y")], None)), 2)

    def test_parse_sitemap_round_trips_build_output(self):
        import indexnow
        from machine import sitemap_xml
        entries = [("/a/", "2026-01-01")]
        self.assertEqual(indexnow.parse_sitemap(sitemap_xml(entries)), {common.BASE_URL + "/a/": "2026-01-01"})

    def test_payload_points_to_hosted_key_file(self):
        import indexnow
        p = indexnow.payload([common.BASE_URL + "/"])
        self.assertEqual(p["host"], common.SITE["domain"])
        self.assertEqual(p["keyLocation"], "{}/{}.txt".format(common.BASE_URL, indexnow.key()))

    def test_only_production_builds_ping(self):
        import indexnow
        self.assertTrue(indexnow.should_ping({"CONTEXT": "production"}))
        self.assertFalse(indexnow.should_ping({"CONTEXT": "deploy-preview"}))
        self.assertFalse(indexnow.should_ping({}))
        self.assertFalse(indexnow.should_ping({"CONTEXT": "production", "INDEXNOW_DISABLE": "1"}))

    def test_ping_changed_does_nothing_outside_production(self):
        import indexnow
        from unittest import mock
        with mock.patch.object(indexnow, "submit") as submit:
            indexnow.ping_changed([("/", "2026-01-01")], env={})
        submit.assert_not_called()


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

    def test_google_verification_meta_on_home_page(self):
        token = common.SITE["googleSiteVerification"]
        self.assertIn('<meta name="google-site-verification" content="{}">'.format(token), read_dist("index.html"))

    def test_faq_schema_urls_point_at_on_page_anchors(self):
        html = read_dist("brand/delta/index.html")
        faq = next(n for n in json_ld(html)["@graph"] if n["@type"] == "FAQPage")
        for q in faq["mainEntity"]:
            anchor = q["url"].split("#", 1)[1]
            self.assertIn('id="{}"'.format(anchor), html)

    def test_research_page_dataset_and_csv(self):
        html = read_dist("research/companies-without-phone-support/index.html")
        ld = json_ld(html)
        dataset = next(n for n in ld["@graph"] if n["@type"] == "Dataset")
        self.assertTrue(dataset["distribution"][0]["contentUrl"].endswith("/research/customer-service-contacts.csv"))
        self.assertTrue(os.path.exists(os.path.join(common.DIST, "research", "customer-service-contacts.csv")))
        self.assertIn("/research/companies-without-phone-support/", read_dist("llms.txt"))

    def test_indexnow_key_file_is_served(self):
        import indexnow
        self.assertEqual(read_dist(indexnow.key_file_name()), indexnow.key())

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
