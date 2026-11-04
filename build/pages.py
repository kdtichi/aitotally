"""Home, category, and site-information pages for AI Totally."""
import json

from common import (BRANDS, CATEGORIES, NAME, SITE, brand_by_slug, brands_in, esc, initial_mark,
                    page_updated)
from components import qa_details
from research_stats import research_stats
from icons import ABOUT_ICON, CATEGORY_ICONS, HOW_IT_WORKS_ICON
from layout import layout
from schema import (breadcrumb_node, crumbs_html, faq_node, item_list_node, script, webpage_node)

SEARCH_ICON = ('<svg width="18" height="18" viewBox="0 0 24 24" fill="none" aria-hidden="true"><circle cx="11" cy="11" r="7" '
               'stroke="currentColor" stroke-width="2"/><path d="M21 21l-4.35-4.35" stroke="currentColor" stroke-width="2" '
               'stroke-linecap="round"/></svg>')

SITE_FAQ = [
    ("Is AI Totally part of any of the companies listed?",
     "No. AI Totally is completely independent. We aren&rsquo;t owned by, paid by or partnered with any company on this site, and we can&rsquo;t access anyone&rsquo;s account."),
    ("Where do your phone numbers come from?",
     "From each company&rsquo;s own website &mdash; its help center or contact page. We never use forums, other directories or ads as a source. Every company page links to the exact page we checked and shows the date we checked it."),
    ("Why is there no phone number for some companies?",
     "Because the company doesn&rsquo;t publish one. Lots of social networks, email providers and apps only offer chat, forms or help articles. Instead of guessing, we tell you that and send you to the channel that really exists."),
    ("What should I do if a number on your site is wrong?",
     "Tell us through the Contact page with the company name and what changed. We&rsquo;ll recheck it against the company&rsquo;s own site and fix the page."),
    ("Does AI Totally cost anything?",
     "No. There&rsquo;s nothing to pay, no account and no sign-up. Find the company, then contact them directly."),
    ("Do you collect my data?",
     "We don&rsquo;t run ads, tracking cookies or third-party analytics. If you email us, we use your message only to reply and fix the listing. The Privacy Policy has the details."),
    ("I think I contacted a fake support line. What now?",
     "Stop the call or chat and don&rsquo;t share anything else, especially passwords, one-time codes, gift card numbers or card details. Then contact the company using the channel on its AI Totally page. If you already shared payment details, call your bank or card issuer straight away, and you can report the scam to the FTC at reportfraud.ftc.gov."),
    ("Can you add a company I can&rsquo;t find?",
     "Yes, ask us. Email the company name through the Contact page and we&rsquo;ll look at adding a verified listing."),
]


def _faq_details(items: list) -> str:
    return qa_details(items, "faq")


def render_home() -> str:
    index = [{"name": b["name"], "slug": b["slug"], "categoryLabel": CATEGORIES[b["category"]]["label"],
              "aliases": b["aliases"]} for b in BRANDS]
    featured = [b for b in (brand_by_slug(s) for s in SITE["featuredBrands"]) if b]
    cards = "".join("""<a class="brand-card" href="/brand/{slug}/">
  <span class="brand-card__mark" aria-hidden="true">{mark}</span>
  <span class="brand-card__name">{name}</span>
  <span class="brand-card__cat">{cat}</span>
</a>""".format(slug=b["slug"], mark=initial_mark(b["name"]), name=esc(b["name"]),
               cat=esc(CATEGORIES[b["category"]]["label"])) for b in featured)
    groups = ""
    for slug, c in CATEGORIES.items():
        members = brands_in(slug)
        if members:
            items = "".join('<li><a href="/brand/{}/">{}</a></li>'.format(m["slug"], esc(m["name"])) for m in members)
            groups += '<div class="all-brands__group"><h3 class="label-heading"><a href="/category/{}/">{}</a></h3><ul>{}</ul></div>'.format(
                slug, esc(c["label"]), items)
    pills = "".join('<a class="cat-pill" href="/category/{}/">{}</a>'.format(s, esc(c["label"])) for s, c in CATEGORIES.items())
    home_faq = SITE_FAQ[:3]

    body = """
<section class="hero container">
  <p class="eyebrow">Customer Service Finder</p>
  <h1>Skip the hold-music hunt.</h1>
  <form class="search-form" id="search-form" role="search" autocomplete="off">
    <label for="search-input" class="visually-hidden">Find a company</label>
    <input class="search-input" id="search-input" type="text" placeholder="Which company? Try &ldquo;Delta&rdquo;"
      aria-autocomplete="list" aria-controls="search-results" aria-expanded="false">
    <button class="search-submit" type="submit" aria-label="Search">{search_icon}</button>
    <div class="search-results" id="search-results" role="listbox" hidden></div>
  </form>
  <p class="search-hint">Every number comes from the company&rsquo;s own website. Hit Enter to open the best match.</p>
  <script type="application/json" id="brand-index">{index_json}</script>
</section>

<section class="container">
  <div class="quick-answer" style="margin:0 auto;">
    <span class="quick-answer__label">What is AI Totally?</span>
    <p>{name} is a free, independent customer service finder. For {count} well-known companies, it shows the phone number, chat link and support hours each company publishes on its own website &mdash; and says plainly when a company has no phone line at all.</p>
  </div>
</section>

<section class="section container">
  <div class="section-head"><h2>Popular right now</h2></div>
  <div class="brand-grid">{cards}</div>
  <div class="cat-nav-pills" style="margin-top:24px;">{pills}</div>
</section>

<section class="section container">
  <a class="research-teaser" href="/research/companies-without-phone-support/">
    <span class="research-teaser__num">{pct}%</span>
    <span><span class="research-teaser__eyebrow">{name} research</span>
    <span class="research-teaser__title">of the companies we track publish no customer service phone number. See which ones &rarr;</span></span>
  </a>
</section>

<section class="section container" id="all-companies">
  <div class="section-head"><h2>Every company we cover</h2></div>
  <div class="all-brands">{groups}</div>
</section>

<section class="how-strip">
  <div class="container">
    <div class="section-head" style="border:none;margin-bottom:32px;"><h2>Three steps, no runaround</h2></div>
    <div class="how-steps">
      <div class="how-step"><div class="num">01</div><h3>Find the company</h3>
        <p>Search by name or browse by category. We focus on the companies people most often need to reach when something goes wrong.</p></div>
      <div class="how-step"><div class="num">02</div><h3>See where it came from</h3>
        <p>Each listing links to the page on the company&rsquo;s own site where we found it, along with the date we checked.</p></div>
      <div class="how-step"><div class="num">03</div><h3>Contact them yourself</h3>
        <p>Tap to call or open the official chat. You go straight to the company &mdash; we never sit in the middle or ask for your details.</p></div>
    </div>
  </div>
</section>

<section class="section container">
  <div class="faq-list"><h2 class="label-heading" style="margin:0 0 4px;">Good to know</h2>{faq}</div>
  <p style="margin-top:16px;"><a href="/faq/">More questions and answers &rarr;</a></p>
</section>

<section class="section container">
  <div class="disclaimer-block">
    <span class="mark" aria-hidden="true">i</span>
    <p><strong>{name} is independent.</strong> No company on this site owns us, pays us or checks what we publish. We just point you to the support channels they already offer, so you don&rsquo;t end up on a look-alike page. See <a href="/how-it-works/">how we check listings</a>.</p>
  </div>
</section>
""".format(search_icon=SEARCH_ICON, index_json=json.dumps(index).replace("</", "<\\/"), name=esc(NAME),
           count=len(BRANDS), pct=research_stats()["pct_without"], cards=cards, pills=pills, groups=groups, faq=_faq_details(home_faq))

    desc = SITE["description"]
    json_ld = script([
        webpage_node("/", "{} — independent customer service finder".format(NAME), desc, page_updated("/"),
                     speakable=True, extra={"mainEntity": {"@id": "https://" + SITE["domain"] + "/#list"}}),
        item_list_node("/", "Companies on {}".format(NAME), [(b["name"], "/brand/{}/".format(b["slug"])) for b in BRANDS]),
        faq_node("/", home_faq),
    ])
    return layout(title="{} — Find Real Customer Service Numbers & Chat".format(NAME),
                  description=desc, path="/", body=body, json_ld=json_ld)


def category_summary(with_phone: int, total: int, label: str) -> str:
    where = "in our {} section".format(esc(label))
    if with_phone == total:
        return "Every company {} ({}) publishes a customer service phone number.".format(where, total)
    if with_phone == 0:
        return "None of the {} companies {} publishes a customer service phone number &mdash; support runs through chat, forms or help centers.".format(total, where)
    verb = "publishes" if with_phone == 1 else "publish"
    rest = total - with_phone
    tail = "the other one relies" if rest == 1 else "the other {} rely".format(rest)
    return "{} of the {} companies {} {} a customer service phone number; {} on chat, forms or help centers.".format(
        with_phone, total, where, verb, tail)


def render_category(cat_slug: str) -> str:
    cat = CATEGORIES[cat_slug]
    path = "/category/{}/".format(cat_slug)
    members = brands_in(cat_slug)
    pills = "".join('<a class="{}" href="/category/{}/">{}</a>'.format(
        "cat-pill is-active" if s == cat_slug else "cat-pill", s, esc(c["label"])) for s, c in CATEGORIES.items())
    channel = {"chat": "chat", "form": "contact form", "none": "help center"}
    rows = "".join("""<a class="cat-row" href="/brand/{slug}/">
  <span class="cat-row__left"><span class="cat-row__mark" aria-hidden="true">{mark}</span>
    <span><span class="cat-row__name">{name}</span><br><span class="cat-row__meta">{meta}</span></span></span>
  <span class="cat-row__arrow" aria-hidden="true">&rarr;</span>
</a>""".format(slug=b["slug"], mark=initial_mark(b["name"]), name=esc(b["name"]),
               meta=("Phone + " + channel[b.get("chatType") or "form"]) if b.get("phone")
               else "No phone line &mdash; {} only".format(channel[b.get("chatType") or "form"])) for b in members)
    with_phone = sum(1 for b in members if b.get("phone"))
    summary = category_summary(with_phone, len(members), cat["label"])

    crumbs = [("Home", "/"), (cat["label"], path)]
    body = """
<section class="cat-hero container">
  {crumbs}
  <div class="page-icon">{icon}</div>
  <p class="eyebrow">Category</p>
  <h1>{label} customer service</h1>
  <p class="lede" style="margin:0;max-width:60ch;">{desc}</p>
  <div class="cat-nav-pills" style="margin-top:20px;">{pills}</div>
</section>
<section class="section container">
  <div class="quick-answer" style="margin-top:0;"><span class="quick-answer__label">In short</span><p>{summary}</p></div>
  <div class="cat-list">{rows}</div>
</section>
<section class="container">
  <div class="prose" style="max-width:68ch;border-top:1px solid var(--rule);padding-top:32px;">
    <h2 class="label-heading">Getting help from {label_lower} companies</h2>
    <p>{intro}</p>
  </div>
</section>
""".format(crumbs=crumbs_html(crumbs), icon=CATEGORY_ICONS[cat_slug], label=esc(cat["label"]),
           label_lower=esc(cat["label"].lower()), desc=esc(cat["description"]), pills=pills,
           summary=summary, rows=rows, intro=esc(cat["intro"]))

    updated = max([b["verifiedDate"] for b in members] + [SITE["launchDate"]])
    desc = "Verified customer service contacts for {} companies — phone numbers, chat links and hours, each checked against the company's own site.".format(cat["label"].lower())
    json_ld = script([
        webpage_node(path, "{} customer service".format(cat["label"]), desc, updated, page_type="CollectionPage",
                     speakable=True, extra={"mainEntity": {"@id": "https://" + SITE["domain"] + path + "#list"}}),
        breadcrumb_node(path, crumbs),
        item_list_node(path, "{} companies".format(cat["label"]), [(b["name"], "/brand/{}/".format(b["slug"])) for b in members]),
    ])
    return layout(title="{} Customer Service Numbers & Contacts | {}".format(cat["label"], NAME),
                  description=desc, path=path, body=body, json_ld=json_ld)


def info_page(*, path: str, eyebrow: str, h1: str, title: str, description: str, prose: str,
              icon: str = "", page_type: str = "WebPage", extra_nodes: list | None = None) -> str:
    crumbs = [("Home", "/"), (eyebrow if eyebrow != "Legal" else h1, path)]
    body = """
<section class="page-hero container">
  {crumbs}
  {icon}
  <p class="eyebrow">{eyebrow}</p>
  <h1>{h1}</h1>
</section>
<section class="section container"><div class="prose">{prose}</div></section>
""".format(crumbs=crumbs_html(crumbs), icon=icon, eyebrow=esc(eyebrow), h1=h1, prose=prose)
    nodes = [webpage_node(path, h1.replace("&rsquo;", "'"), description, page_updated(path), page_type=page_type),
             breadcrumb_node(path, crumbs)] + (extra_nodes or [])
    return layout(title=title, description=description, path=path, body=body, json_ld=script(nodes))


def render_about() -> str:
    a = SITE["address"]
    prose = """
<p>Search for almost any company&rsquo;s support number and you&rsquo;ll find pages that look official but aren&rsquo;t &mdash; some send you to a paid call line, others to someone pretending to be the company. {name} is the simple alternative: the contact details each company actually publishes, with a link to prove it.</p>
<h2>What you get here</h2>
<p>For every company we list, we look up the phone number, chat or contact link, and support hours on that company&rsquo;s own website, then link you straight to it. If a company doesn&rsquo;t offer a phone line, we say so instead of filling the gap.</p>
<h2>What we&rsquo;re not</h2>
<p>We aren&rsquo;t a call center, and we don&rsquo;t work for any company on the site. We can&rsquo;t see or change your accounts, issue refunds or take payments, and we will never ask for your login or card details.</p>
<h2>Keeping things accurate</h2>
<p>Each company page shows when we last checked it and which official page we used. Companies change numbers and hours without warning, so if something looks off, <a href="/contact/">tell us</a> and we&rsquo;ll check it again. The full standard is in our <a href="/editorial-policy/">editorial policy</a>.</p>
<h2>Who&rsquo;s behind it</h2>
<p>{name} is run from {street}, {city} {postal}, {country}. You can email us at <a href="mailto:{email}">{email}</a>.</p>
""".format(name=esc(NAME), street=esc(a["streetAddress"]), city=esc(a["addressLocality"]), postal=esc(a["postalCode"]),
           country=esc(a["countryName"]), email=esc(SITE["contactEmail"]))
    return info_page(path="/about/", eyebrow="About", h1="Real contact details, nothing in between.",
                     title="About {} | Independent Customer Service Finder".format(NAME),
                     description="Why {} exists, what it does and doesn't do, and how its customer service listings stay accurate.".format(NAME),
                     prose=prose, icon='<div class="page-icon">{}</div>'.format(ABOUT_ICON), page_type="AboutPage")


def render_contact() -> str:
    a, email = SITE["address"], esc(SITE["contactEmail"])
    prose = """
<div class="contact-card"><h2>Spotted a wrong number or link?</h2>
  <p>Tell us the company and what&rsquo;s changed. We&rsquo;ll recheck it on the company&rsquo;s own website and update the page.</p>
  <a href="mailto:{email}">{email}</a></div>
<div class="contact-card"><h2>Missing a company?</h2>
  <p>Send us the name and we&rsquo;ll look at adding a verified listing.</p>
  <a href="mailto:{email}">{email}</a></div>
<p style="margin-top:24px;">Please don&rsquo;t send us account numbers, passwords or card details. We&rsquo;re independent, so we can&rsquo;t look up or change anything with the companies we list &mdash; for that, use the official contact option on the company&rsquo;s page.</p>
<div class="contact-card"><h2>Postal address</h2>
  <p style="margin:0;">{name}<br>{street}<br>{city} {postal}<br>{country}</p></div>
""".format(email=email, name=esc(NAME), street=esc(a["streetAddress"]), city=esc(a["addressLocality"]),
           postal=esc(a["postalCode"]), country=esc(a["countryName"]))
    return info_page(path="/contact/", eyebrow="Contact", h1="Talk to us", page_type="ContactPage",
                     title="Contact {}".format(NAME),
                     description="Report an out-of-date listing, ask us to add a company, or get in touch with {}.".format(NAME),
                     prose=prose)


def render_how_it_works() -> str:
    prose = """
<h2>1. We only use the company&rsquo;s own website</h2>
<p>Every number, chat link and set of hours on {name} comes from the company&rsquo;s official help or contact pages. Never from forums, other directories or ads. Each company page links to the exact source.</p>
<h2>2. We tell you when there&rsquo;s no phone line</h2>
<p>Many companies &mdash; especially social networks and email providers &mdash; don&rsquo;t offer phone support. We say that clearly and point you to the chat, form or help center they do offer.</p>
<h2>3. We date every check</h2>
<p>Each company page shows the date we last verified it. That date only changes when we actually recheck the source.</p>
<h2>4. We stay out of the way</h2>
<p>We don&rsquo;t collect account numbers, passwords or payment details. You contact the company directly.</p>
<h2>How to spot a fake support line</h2>
<p>Customer service is one of the most copied corners of the internet. A few quick checks before you trust a number:</p>
<ul>
  <li><strong>Look at the web address, not the logo.</strong> Anyone can copy a design. The domain tells you who really runs the page.</li>
  <li><strong>Be careful with numbers you only see in ads.</strong> Paid search results are a common way fake support lines get to the top.</li>
  <li><strong>Real support never asks for</strong> your password, one-time codes, gift cards, wire transfers or remote access to your computer.</li>
  <li><strong>If in doubt, type the address yourself.</strong> Go to the company&rsquo;s website directly rather than clicking a link.</li>
</ul>
<p>Still have questions? Try the <a href="/faq/">FAQ</a>, or read the full <a href="/editorial-policy/">editorial policy</a>.</p>
""".format(name=esc(NAME))
    return info_page(path="/how-it-works/", eyebrow="How It Works", h1="How we check every listing.",
                     title="How {} Verifies Customer Service Numbers".format(NAME),
                     description="How {} checks every phone number and chat link against the company's own website — plus how to spot a fake support line.".format(NAME),
                     prose=prose, icon='<div class="page-icon page-icon--wide">{}</div>'.format(HOW_IT_WORKS_ICON))


def render_faq() -> str:
    prose = '<div class="faq-list">{}</div>'.format(_faq_details(SITE_FAQ))
    return info_page(path="/faq/", eyebrow="FAQ", h1="Questions, answered.",
                     title="FAQ | {}".format(NAME),
                     description="Answers about {}: independence, where our numbers come from, missing phone lines, privacy and what to do after a scam call.".format(NAME),
                     prose=prose, extra_nodes=[faq_node("/faq/", SITE_FAQ)])


def render_404() -> str:
    body = """
<section class="page-hero container" style="text-align:center;padding:80px 0 40px;">
  <p class="eyebrow">404</p>
  <h1>Nothing at this address.</h1>
  <p class="lede" style="max-width:46ch;margin:16px auto 32px;">This page may have moved, or the company you&rsquo;re after isn&rsquo;t listed yet.</p>
  <a class="btn btn--accent" href="/">Find a company</a>
</section>
"""
    return layout(title="Page Not Found | {}".format(NAME), description="This page doesn't exist on {}.".format(NAME),
                  path="/404.html", body=body, robots="noindex")
