"""Original-data page: which companies publish no customer service phone number.

Every figure is computed from data/brands.json at build time, so the page,
its CSV download, its schema and llms.txt can never disagree with the listings.
"""
import csv
import io

from common import BASE_URL, BRANDS, CATEGORIES, NAME, esc, human_date, page_updated
from components import qa_details
from layout import layout
from schema import breadcrumb_node, crumbs_html, faq_node, script, webpage_node

PATH = "/research/companies-without-phone-support/"
CSV_PATH = "/research/customer-service-contacts.csv"
TITLE = "Which big companies have no customer service phone number?"
CHANNEL_WORDS = {"chat": "Chat or virtual assistant", "form": "Contact form", "none": "Help articles only"}
CSV_FIELDS = ("company", "category", "publishes_phone_number", "phone_number", "online_channel",
              "online_help_url", "support_hours", "source_url", "verified_date", "aitotally_url")


def stats() -> dict:
    no_phone = [b for b in BRANDS if not b.get("phone")]
    by_cat = []
    for slug, cat in CATEGORIES.items():
        members = [b for b in BRANDS if b["category"] == slug]
        if members:
            with_phone = sum(1 for b in members if b.get("phone"))
            by_cat.append({"slug": slug, "label": cat["label"], "total": len(members),
                           "with_phone": with_phone, "without": len(members) - with_phone})
    channels = {k: sum(1 for b in no_phone if b["chatType"] == k) for k in CHANNEL_WORDS}
    dates = sorted(b["verifiedDate"] for b in BRANDS)
    total = len(BRANDS)
    return {
        "total": total,
        "with_phone": total - len(no_phone),
        "without": len(no_phone),
        "pct_without": round(100 * len(no_phone) / total) if total else 0,
        "no_phone": no_phone,
        "by_cat": by_cat,
        "channels": channels,
        "always_open": sum(1 for b in BRANDS if b["hours"].get("mode") == "247"),
        "first_check": dates[0],
        "last_check": dates[-1],
        "all_without": [c["label"] for c in by_cat if c["with_phone"] == 0],
        "all_with": [c["label"] for c in by_cat if c["without"] == 0],
    }


def _join(labels: list, word: str = "and") -> str:
    if len(labels) <= 1:
        return "".join(labels)
    return ", ".join(labels[:-1]) + " {} ".format(word) + labels[-1]


def headline_answer(s: dict) -> str:
    text = ("Of the {total} well-known companies {name} tracks, {without} ({pct}%) publish no customer "
            "service phone number on their own website; they offer chat, contact forms or help articles instead.").format(
        total=s["total"], name=NAME, without=s["without"], pct=s["pct_without"])
    if s["all_without"]:
        text += " No company we list in {} publishes one.".format(_join(s["all_without"], "or"))
    if s["all_with"]:
        text += " Every company we list in {} does.".format(_join(s["all_with"]))
    return text


def hours_text(b: dict) -> str:
    mode = b["hours"].get("mode")
    if mode == "247":
        return "24/7"
    if mode == "detailed":
        h = b["hours"]
        return "{}-{} {} {}".format(h["start"], h["end"], h["tz"], h["days"])
    return b["hours"].get("text", "")


def csv_text() -> str:
    out = io.StringIO()
    w = csv.writer(out, lineterminator="\n")
    w.writerow(CSV_FIELDS)
    for b in BRANDS:
        w.writerow([b["name"], CATEGORIES[b["category"]]["label"], "yes" if b.get("phone") else "no",
                    b.get("phone") or "", CHANNEL_WORDS[b["chatType"]], b["chatUrl"], hours_text(b),
                    b["sourceUrl"], b["verifiedDate"], "{}/brand/{}/".format(BASE_URL, b["slug"])])
    return out.getvalue()


def page_faqs(s: dict) -> list:
    return [
        ("Why don&rsquo;t some companies offer phone support?",
         "Companies don&rsquo;t usually say why. In our data the gap is concentrated in free, account-based "
         "services &mdash; social networks, email and streaming &mdash; which steer people to help centers, "
         "in-app tools and chat instead of a phone line."),
        ("Is a phone number I found online for one of these companies real?",
         "Treat it with suspicion. For the {} companies listed here, we found no customer service number on "
         "the company&rsquo;s own website. Numbers for them that appear in ads, social posts or unfamiliar "
         "websites may be scams.".format(s["without"])),
        ("How was this data collected?",
         "Each company&rsquo;s own help or contact pages were checked between {} and {}. A company counts as "
         "publishing a number if a customer service phone number appears on those pages.".format(
             human_date(s["first_check"]), human_date(s["last_check"]))),
    ]


def _category_table(s: dict) -> str:
    rows = "".join(
        "<tr><th scope='row'><a href='/category/{slug}/'>{label}</a></th><td>{total}</td><td>{w}</td><td>{wo}</td></tr>".format(
            slug=c["slug"], label=esc(c["label"]), total=c["total"], w=c["with_phone"], wo=c["without"])
        for c in s["by_cat"])
    return """<div class="key-facts data-table"><table>
<caption class="label-heading" style="caption-side:top;text-align:left;padding-bottom:10px;">Phone support by category</caption>
<thead><tr><th scope="col">Category</th><th scope="col">Companies</th><th scope="col">Publish a number</th><th scope="col">No number</th></tr></thead>
<tbody>{rows}</tbody>
<tfoot><tr><th scope="row">All companies</th><td>{t}</td><td>{w}</td><td>{wo}</td></tr></tfoot>
</table></div>""".format(rows=rows, t=s["total"], w=s["with_phone"], wo=s["without"])


def _no_phone_table(s: dict) -> str:
    rows = "".join(
        "<tr><th scope='row'><a href='/brand/{slug}/'>{name}</a></th><td>{cat}</td><td><a href='{url}' rel='nofollow noopener' target='_blank'>{channel}</a></td><td><time datetime='{d}'>{dh}</time></td></tr>".format(
            slug=b["slug"], name=esc(b["name"]), cat=esc(CATEGORIES[b["category"]]["label"]), url=esc(b["chatUrl"]),
            channel=CHANNEL_WORDS[b["chatType"]], d=b["verifiedDate"], dh=human_date(b["verifiedDate"]))
        for b in sorted(s["no_phone"], key=lambda x: x["name"].lower()))
    return """<div class="key-facts data-table"><table>
<caption class="label-heading" style="caption-side:top;text-align:left;padding-bottom:10px;">The {n} companies with no customer service phone number</caption>
<thead><tr><th scope="col">Company</th><th scope="col">Category</th><th scope="col">How to get help instead</th><th scope="col">Checked</th></tr></thead>
<tbody>{rows}</tbody></table></div>""".format(n=s["without"], rows=rows)


def _stat_tiles(s: dict) -> str:
    tiles = [
        ("{}%".format(s["pct_without"]), "publish no customer service phone number ({} of {})".format(s["without"], s["total"])),
        (str(s["channels"]["form"]), "of the {} with no phone line use a contact form instead".format(s["without"])),
        (str(s["channels"]["chat"]), "of the {} offer chat or a virtual assistant instead".format(s["without"])),
        (str(s["always_open"]), "companies we list say they offer support 24/7"),
    ]
    return '<div class="stat-tiles">{}</div>'.format("".join(
        '<div class="stat-tile"><span class="stat-tile__num">{}</span><span class="stat-tile__label">{}</span></div>'.format(n, esc(l))
        for n, l in tiles))


def dataset_node(s: dict) -> dict:
    return {
        "@type": "Dataset",
        "@id": BASE_URL + PATH + "#dataset",
        "name": "Customer service contact channels of {} well-known US companies".format(s["total"]),
        "description": headline_answer(s),
        "url": BASE_URL + PATH,
        "creator": {"@id": BASE_URL + "/#organization"},
        "publisher": {"@id": BASE_URL + "/#organization"},
        "isAccessibleForFree": True,
        "temporalCoverage": "{}/{}".format(s["first_check"], s["last_check"]),
        "spatialCoverage": "United States",
        "keywords": ["customer service", "phone support", "contact center", "customer support channels"],
        "variableMeasured": ["Publishes a customer service phone number", "Online support channel",
                             "Support hours", "Verification date"],
        "distribution": [{"@type": "DataDownload", "encodingFormat": "text/csv", "contentUrl": BASE_URL + CSV_PATH}],
    }


def render_research() -> str:
    s = stats()
    faqs = page_faqs(s)
    crumbs = [("Home", "/"), ("Research", PATH)]
    updated = page_updated(PATH)
    description = "{}% of {} big companies publish no customer service phone number. See which ones, by category, and what they offer instead — with downloadable data.".format(
        s["pct_without"], s["total"])
    body = """
<article class="page-hero container">
  {crumbs}
  <p class="eyebrow">Research &middot; {name} data</p>
  <h1>{title}</h1>
  <p class="updated-line">Published {upd_h} &middot; Contact details checked {first_h} &ndash; {last_h}</p>
  <div class="quick-answer"><span class="quick-answer__label">Key finding</span><p>{answer}</p></div>
  {tiles}
  <div class="prose">
    <h2>What do companies offer instead of a phone line?</h2>
    <p>Of the {without} companies with no phone number, {form} send you to a contact form, {chat} offer chat or a virtual assistant, and {none} offer help articles only. Most of these channels work best when you&rsquo;re signed in, because the company can see your account.</p>
  </div>
  {cat_table}
  {list_table}
  <div class="prose">
    <h2>Why this matters</h2>
    <p>When a company publishes no phone number, people searching for one are more likely to find fake &ldquo;support lines&rdquo; in ads or on look-alike websites. If a company on this list is answering your call, check that you dialled a number from its own website or app.</p>
    <h2>How we collected the data</h2>
    <p>For each company, we checked its own help center or contact pages and recorded the phone number, online channel and hours it publishes &mdash; never forums, other directories or ads. A company counts as publishing a number when a customer service phone number appears on those pages; a department line, such as a technical support line, also counts. Each company&rsquo;s page on {name} links to the exact source and shows the date it was checked. The figures here update automatically whenever a listing is rechecked.</p>
    <h2>Download and cite this data</h2>
    <p>Download the full dataset as a spreadsheet-friendly file: <a href="{csv}" download>customer-service-contacts.csv</a> ({total} companies). If you use it, please cite and link to this page:</p>
    <p class="cite-box">{name}. &ldquo;{title}&rdquo; {upd_h}. {url}</p>
  </div>
  <div class="faq-list" style="margin-top:40px;"><h2 class="label-heading">Questions about this data</h2>{faq_html}</div>
</article>
""".format(crumbs=crumbs_html(crumbs), name=esc(NAME), title=esc(TITLE), upd_h=human_date(updated),
           first_h=human_date(s["first_check"]), last_h=human_date(s["last_check"]), answer=esc(headline_answer(s)),
           tiles=_stat_tiles(s), without=s["without"], form=s["channels"]["form"], chat=s["channels"]["chat"],
           none=s["channels"]["none"], cat_table=_category_table(s), list_table=_no_phone_table(s), csv=CSV_PATH,
           total=s["total"], url=BASE_URL + PATH, faq_html=qa_details(faqs, "faq"))
    page = webpage_node(PATH, TITLE, description, updated, speakable=True, extra={
        "datePublished": updated, "mainEntity": {"@id": BASE_URL + PATH + "#dataset"}})
    json_ld = script([page, breadcrumb_node(PATH, crumbs), dataset_node(s), faq_node(PATH, faqs)])
    return layout(title="{} ({} Data) | {}".format(TITLE.rstrip("?") + "?", updated[:4], NAME), description=description,
                  path=PATH, body=body, json_ld=json_ld, og_type="article")
