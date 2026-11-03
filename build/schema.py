"""JSON-LD builders. Every page emits one connected @graph so search engines
and AI systems can resolve the site, the page, and the company it describes
as linked entities rather than isolated blobs."""
import json

from common import BASE_URL, NAME, SITE, esc

ORG_ID = BASE_URL + "/#organization"
WEBSITE_ID = BASE_URL + "/#website"


def org_node() -> dict:
    addr = SITE["address"]
    return {
        "@type": "Organization",
        "@id": ORG_ID,
        "name": NAME,
        "alternateName": SITE["domain"],
        "url": BASE_URL + "/",
        "logo": {"@type": "ImageObject", "url": BASE_URL + "/logo.png", "width": 512, "height": 512},
        "description": SITE["description"],
        "email": SITE["contactEmail"],
        "address": {
            "@type": "PostalAddress",
            "streetAddress": addr["streetAddress"],
            "addressLocality": addr["addressLocality"],
            "postalCode": addr["postalCode"],
            "addressCountry": addr["addressCountry"],
        },
        "publishingPrinciples": BASE_URL + "/editorial-policy/",
    }


def website_node() -> dict:
    return {
        "@type": "WebSite",
        "@id": WEBSITE_ID,
        "name": NAME,
        "url": BASE_URL + "/",
        "description": SITE["description"],
        "inLanguage": "en-US",
        "publisher": {"@id": ORG_ID},
    }


def webpage_node(path: str, name: str, description: str, updated: str, *,
                 page_type: str = "WebPage", speakable: bool = False, extra: dict | None = None) -> dict:
    node = {
        "@type": page_type,
        "@id": BASE_URL + path + "#webpage",
        "url": BASE_URL + path,
        "name": name,
        "description": description,
        "inLanguage": "en-US",
        "dateModified": updated,
        "isPartOf": {"@id": WEBSITE_ID},
        "publisher": {"@id": ORG_ID},
    }
    if path != "/":
        node["breadcrumb"] = {"@id": BASE_URL + path + "#breadcrumb"}
    if speakable:
        node["speakable"] = {"@type": "SpeakableSpecification",
                             "cssSelector": ["h1", ".quick-answer p"]}
    if extra:
        node.update(extra)
    return node


def breadcrumb_node(path: str, crumbs: list) -> dict:
    """crumbs: list of (label, path) pairs, starting with Home."""
    return {
        "@type": "BreadcrumbList",
        "@id": BASE_URL + path + "#breadcrumb",
        "itemListElement": [
            {"@type": "ListItem", "position": i + 1, "name": label, "item": BASE_URL + href}
            for i, (label, href) in enumerate(crumbs)
        ],
    }


def faq_node(path: str, items: list, prefix: str = "faq", ids: list | None = None) -> dict:
    """items: (question, answer) pairs; answers may contain HTML entities and tags.
    Each Question's url is the on-page anchor rendered by components.qa_details."""
    import re

    from common import unesc
    from components import anchor_ids
    ids = ids or anchor_ids([q for q, _ in items], prefix)
    return {
        "@type": "FAQPage",
        "@id": BASE_URL + path + "#faq",
        "mainEntity": [
            {"@type": "Question", "name": unesc(q), "url": BASE_URL + path + "#" + i,
             "acceptedAnswer": {"@type": "Answer", "text": unesc(re.sub(r"<[^>]+>", "", a))}}
            for i, (q, a) in zip(ids, items)
        ],
    }


def item_list_node(path: str, name: str, entries: list) -> dict:
    """entries: (name, path) pairs."""
    return {
        "@type": "ItemList",
        "@id": BASE_URL + path + "#list",
        "name": name,
        "numberOfItems": len(entries),
        "itemListElement": [
            {"@type": "ListItem", "position": i + 1, "name": label, "url": BASE_URL + href}
            for i, (label, href) in enumerate(entries)
        ],
    }


def script(nodes: list) -> str:
    graph = [org_node(), website_node()] + nodes
    payload = json.dumps({"@context": "https://schema.org", "@graph": graph},
                         ensure_ascii=False, separators=(",", ":"))
    return '<script type="application/ld+json">{}</script>'.format(payload.replace("</", "<\\/"))


def crumbs_html(crumbs: list) -> str:
    parts = []
    for i, (label, href) in enumerate(crumbs):
        if i == len(crumbs) - 1:
            parts.append('<span aria-current="page">{}</span>'.format(esc(label)))
        else:
            parts.append('<a href="{}">{}</a>'.format(href, esc(label)))
    return '<nav aria-label="Breadcrumb"><p class="breadcrumb">{}</p></nav>'.format(" &rsaquo; ".join(parts))
