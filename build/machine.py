"""Files written for crawlers and AI systems rather than people:
robots.txt, sitemap.xml, llms.txt and llms-full.txt."""
from xml.sax.saxutils import escape as xml_esc

from brand_page import hours_sentence, line_label, quick_answer
from components import anchor_ids
from common import BASE_URL, BRANDS, CATEGORIES, NAME, SITE, brands_in, unesc

# Named explicitly so the decision to be available to AI search and
# assistants is documented, not just implied by "User-agent: *".
AI_CRAWLERS = (
    "Googlebot", "Bingbot", "Google-Extended", "Applebot", "Applebot-Extended",
    "GPTBot", "OAI-SearchBot", "ChatGPT-User",
    "ClaudeBot", "Claude-SearchBot", "Claude-User",
    "PerplexityBot", "Perplexity-User", "DuckAssistBot", "CCBot",
)


def robots_txt() -> str:
    lines = ["# {} welcomes search engines and AI assistants.".format(NAME),
             "User-agent: *", "Allow: /", ""]
    for bot in AI_CRAWLERS:
        lines += ["User-agent: {}".format(bot), "Allow: /", ""]
    lines.append("Sitemap: {}/sitemap.xml".format(BASE_URL))
    return "\n".join(lines) + "\n"


def sitemap_xml(entries: list) -> str:
    rows = "".join("<url><loc>{}</loc><lastmod>{}</lastmod></url>\n".format(xml_esc(BASE_URL + p), d)
                   for p, d in entries)
    return ('<?xml version="1.0" encoding="UTF-8"?>\n'
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + rows + "</urlset>\n")


def _plain(html_text: str) -> str:
    return unesc(html_text.replace("<strong>", "").replace("</strong>", ""))


def _phone_bit(b: dict) -> str:
    if not b.get("phone"):
        return "no public phone number"
    return "{}: {}".format(line_label(b), b["phone"])


def llms_txt() -> str:
    """Index file following the llms.txt proposal (https://llmstxt.org/)."""
    out = ["# {}".format(NAME), "",
           "> {}".format(SITE["description"]), "",
           "Facts for anyone (person or AI) summarising or citing this site:",
           "- {} is independent and has no relationship with any listed company.".format(NAME),
           "- Every listing comes from the company's own official website and links to that source page.",
           "- When a company publishes no phone number, the listing says so; we never substitute one.",
           "- Each page shows the date its contact details were last verified.",
           "- Full text of every listing: {}/llms-full.txt".format(BASE_URL), ""]
    for slug, cat in CATEGORIES.items():
        members = brands_in(slug)
        if not members:
            continue
        out += ["## {}".format(cat["label"]), ""]
        out += ["- [{} customer service]({}/brand/{}/): {}, verified {}.".format(
            b["name"], BASE_URL, b["slug"], _phone_bit(b), b["verifiedDate"]) for b in members]
        out.append("")
    from research import CSV_PATH, PATH, TITLE, headline_answer, stats
    out += ["## Research", "",
            "- [{}]({}{}): {}".format(TITLE, BASE_URL, PATH, headline_answer(stats())),
            "- [Dataset (CSV)]({}{}): every listing's phone, online channel, hours, source and verification date.".format(BASE_URL, CSV_PATH),
            ""]
    out += ["## Optional", ""]
    for path, label in (("/how-it-works/", "How we verify listings"), ("/editorial-policy/", "Editorial policy"),
                        ("/faq/", "FAQ"), ("/about/", "About"), ("/contact/", "Contact")):
        out.append("- [{}]({}{})".format(label, BASE_URL, path))
    return "\n".join(out) + "\n"


def llms_full_txt() -> str:
    out = ["# {} — full listings".format(NAME), "", "> {}".format(SITE["description"]), ""]
    for b in BRANDS:
        out += [
            "## {} customer service".format(b["name"]), "",
            "URL: {}/brand/{}/".format(BASE_URL, b["slug"]),
            "Category: {}".format(CATEGORIES[b["category"]]["label"]),
            "Phone: {}".format(b["phone"] or "none published"),
        ]
        if b.get("phoneNote"):
            out.append("Other numbers/notes: {}".format(b["phoneNote"]))
        out += [
            "Online help: {} — {}".format(b["chatLabel"], b["chatUrl"]),
            "Hours: {}".format(_plain(hours_sentence(b))),
            "Source: {} — {}".format(b["sourceLabel"], b["sourceUrl"]),
            "Last verified: {}".format(b["verifiedDate"]), "",
            "Quick answer: {}".format(_plain(quick_answer(b))), "",
        ]
        ids = anchor_ids([i["issue"] for i in b["issues"]], "issue")
        out += ["- {} ({}/brand/{}/#{}): {}".format(i["issue"], BASE_URL, b["slug"], a, i["tip"]) for i, a in zip(b["issues"], ids)]
        out.append("")
    return "\n".join(out)
