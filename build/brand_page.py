"""Brand pages: one per company, built answer-first for search and AI engines.

Structure: a quotable quick answer, the verified contact panel, issue tips,
a key-facts table, and an FAQ — each backed by FAQPage/WebPage/Organization
schema that states the same facts as the visible page."""
from common import (BASE_URL, CATEGORIES, NAME, brands_in, esc, human_date, initial_mark,
                    official_root, schema_phone, tel_href)
from components import qa_details
from layout import layout
from schema import breadcrumb_node, crumbs_html, faq_node, script, webpage_node

TZ_LABELS = {
    "America/Los_Angeles": "Pacific time",
    "America/New_York": "Eastern time",
    "America/Chicago": "Central time",
    "America/Denver": "Mountain time",
}
CHANNEL_NOUN = {"chat": "official chat", "form": "official contact form", "none": "official help center"}
CHANNEL_LABEL = {"chat": "Chat and help center", "form": "Contact form", "none": "Help center"}


def possessive(name: str) -> str:
    """'Delta Air Lines' -> 'Delta Air Lines’', 'Uber' -> 'Uber’s' (name already HTML-escaped)."""
    return name + ("&rsquo;" if name.endswith("s") else "&rsquo;s")


def channel_noun(b: dict) -> str:
    return CHANNEL_NOUN[b.get("chatType") or "form"]


def site_domain(url: str) -> str:
    return official_root(url).split("//", 1)[1].rstrip("/")


def line_label(b: dict) -> str:
    return b.get("phoneLineLabel") or "customer service number"


def _fmt_12h(hhmm: str) -> str:
    h, m = map(int, hhmm.split(":"))
    return "{}:{:02d} {}".format(h % 12 or 12, m, "AM" if h < 12 else "PM")


def hours_sentence(b: dict) -> str:
    h = b["hours"]
    mode = h.get("mode", "detailed")
    if mode == "247":
        return "Support is available around the clock, every day."
    if mode == "unspecified":
        return h["text"]
    days = "Monday to Friday" if h.get("days") == "weekdays" else "every day"
    return "Support runs {}&ndash;{} {}, {}.".format(
        _fmt_12h(h["start"]), _fmt_12h(h["end"]), TZ_LABELS.get(h["tz"], h["tz"]), days)


def quick_answer(b: dict) -> str:
    name, domain = esc(b["name"]), esc(site_domain(b["chatUrl"]))
    if b.get("phone"):
        text = "You can reach {name} by calling <strong>{phone}</strong>, its {label}. ".format(
            name=name, phone=esc(b["phone"]), label=esc(line_label(b)))
        text += hours_sentence(b) + " "
        text += "For help online, go to {chat} on {domain}.".format(chat=esc(b["chatLabel"]), domain=domain)
    else:
        text = "{name} doesn&rsquo;t publish a customer service phone number. ".format(name=name)
        text += "The official way to get help is {chat} on {domain}. ".format(chat=esc(b["chatLabel"]), domain=domain)
        if b.get("phoneAltNote"):
            text += esc(b["phoneAltNote"])
    return text.strip()


# Fixed anchors for the five brand-page questions, in faq_items() order, so
# every company page answers at the same links, e.g. /brand/delta/#phone-number.
BRAND_FAQ_IDS = ["phone-number", "hours", "talk-to-a-person", "what-to-contact-about", "spot-a-fake-number"]


def faq_items(b: dict) -> list:
    name = esc(b["name"])
    if b.get("phone"):
        note = " " + esc(b["phoneNote"]) if b.get("phoneNote") else ""
        number_a = "{name} lists {phone} as its {label}.{note}".format(
            name=name, phone=esc(b["phone"]), label=esc(line_label(b)), note=note)
        person_a = ("Call {phone}. If you reach an automated menu, describe your issue in a few words "
                    "or pick the closest option, and have your account or order details ready so the agent "
                    "can help straight away.").format(phone=esc(b["phone"]))
    else:
        alt = " " + esc(b["phoneAltNote"]) if b.get("phoneAltNote") else ""
        number_a = "No. {name} doesn&rsquo;t publish a public customer service number.{alt} Use the {channel} linked on this page instead.".format(
            name=name, alt=alt, channel=channel_noun(b))
        person_a = ("{name} doesn&rsquo;t offer a public phone line, so there&rsquo;s no number to call. "
                    "Your best route to its support team is {chat}, linked above. Signing in first usually "
                    "gets you to the right help faster.").format(name=name, chat=esc(b["chatLabel"]))

    topics = [esc(i["issue"]) for i in b["issues"]]
    topics_a = "People most often get in touch with {name} about: {list}.".format(
        name=name, list="; ".join(topics[:-1]) + "; and " + topics[-1] if len(topics) > 1 else topics[0])

    fake_a = ("Only trust contact details shown on {domain} or inside the official {name} app. "
              "Numbers that appear only in ads, social posts or unfamiliar websites may be scams. "
              "Real support will never ask for your password, a one-time code, gift cards or remote access to your device.").format(
        domain=esc(site_domain(b["sourceUrl"])), name=name)

    return [
        ("What is the {} customer service number?".format(name), number_a),
        ("What are {} customer service hours?".format(possessive(name)), hours_sentence(b)),
        ("How do I talk to a real person at {}?".format(name), person_a),
        ("What can I contact {} about?".format(name), topics_a),
        ("How can I tell if a {} support number is fake?".format(name), fake_a),
    ]


def phone_field(b: dict) -> str:
    name = esc(b["name"])
    if b.get("phone"):
        note = "<p class='stat-sub' style='margin-top:10px;'>{}</p>".format(esc(b["phoneNote"])) if b.get("phoneNote") else ""
        return """<div class="contact-field">
  <label for="phone-link">Phone number {name} publishes</label>
  <a class="phone-number" id="phone-link" href="{tel}">{display}<span class="tap-hint" aria-hidden="true">Tap to call</span></a>
  {note}
</div>""".format(name=name, tel=tel_href(b["phone"]), display=esc(b["phone"]), note=note)
    alt = esc(b["phoneAltNote"]) if b.get("phoneAltNote") else ""
    return """<div class="contact-field">
  <label>Phone number {name} publishes</label>
  <p class="no-phone-verdict">There isn&rsquo;t one &mdash; {name} handles support through its {channel}.</p>
  <p class="stat-sub">{alt} If you&rsquo;ve seen a &ldquo;{name} support number&rdquo; somewhere else, treat it as unconfirmed &mdash; it could be a scam.</p>
  <p class="stat-sub" style="margin-top:8px;"><a href="/research/companies-without-phone-support/">{name} is one of many big companies with no phone line &mdash; see the data &rarr;</a></p>
</div>""".format(name=name, channel=channel_noun(b), alt=alt)


def hours_field(b: dict) -> str:
    h = b["hours"]
    mode = h.get("mode", "detailed")
    if mode == "unspecified":
        return '<div class="contact-field"><label>Support hours</label><p class="no-phone-note">{}</p></div>'.format(esc(h["text"]))
    if mode == "247":
        return """<div class="contact-field" id="hours-widget" data-tz="UTC" data-247="true" data-start="00:00" data-end="00:00" data-days="daily">
  <label>Support hours</label>
  <span class="hours-value" id="hours-value">Open 24 hours, 7 days a week</span>
  <span class="hours-status" id="hours-status" hidden><span class="dot" aria-hidden="true"></span><span></span></span>
</div>"""
    return """<div class="contact-field" id="hours-widget" data-tz="{tz}" data-247="false" data-start="{start}" data-end="{end}" data-days="{days}">
  <label>Support hours <span style="text-transform:none;letter-spacing:0;color:var(--ink-faint);">(shown in your time zone)</span></label>
  <span class="hours-value" id="hours-value">{fallback}</span>
  <span class="hours-status" id="hours-status" hidden><span class="dot" aria-hidden="true"></span><span></span></span>
</div>""".format(tz=esc(h["tz"]), start=esc(h["start"]), end=esc(h["end"]), days=esc(h["days"]), fallback=hours_sentence(b))


def key_facts(b: dict) -> str:
    rows = [("Company", esc(b["name"])),
            ("Category", esc(CATEGORIES[b["category"]]["label"]))]
    if b.get("phone"):
        rows.append(("Main phone line", '<a href="{}">{}</a> ({})'.format(tel_href(b["phone"]), esc(b["phone"]), esc(line_label(b)))))
        if b.get("phoneNote"):
            rows.append(("Other numbers &amp; notes", esc(b["phoneNote"])))
    else:
        rows.append(("Main phone line", "None published"))
    rows += [
        ("Get help online", '<a href="{}" rel="nofollow noopener" target="_blank">{}</a>'.format(esc(b["chatUrl"]), esc(b["chatLabel"]))),
        ("Hours", hours_sentence(b)),
        ("Source", '<a href="{}" rel="nofollow noopener" target="_blank">{}</a>'.format(esc(b["sourceUrl"]), esc(b["sourceLabel"]))),
        ("Last verified", '<time datetime="{0}">{1}</time>'.format(b["verifiedDate"], human_date(b["verifiedDate"]))),
    ]
    body = "".join("<tr><th scope='row'>{}</th><td>{}</td></tr>".format(k, v) for k, v in rows)
    return """<div class="key-facts">
    <h2 class="label-heading">{name} customer service at a glance</h2>
    <table><caption class="visually-hidden">Verified contact details for {name}</caption><tbody>{body}</tbody></table>
  </div>""".format(name=esc(b["name"]), body=body)


def related_html(b: dict) -> str:
    siblings = brands_in(b["category"])
    idx = next(i for i, r in enumerate(siblings) if r["slug"] == b["slug"])
    related = [siblings[(idx + k) % len(siblings)] for k in range(1, min(4, len(siblings) - 1) + 1)]
    if not related:
        return ""
    links = "".join('<a class="related-link" href="/brand/{}/">{}</a>'.format(r["slug"], esc(r["name"])) for r in related)
    return """<div class="related-brands">
      <h2 class="label-heading">More {cat} contacts</h2>
      <div class="related-links">{links}</div>
    </div>""".format(cat=esc(CATEGORIES[b["category"]]["label"]), links=links)


def scam_box(b: dict) -> str:
    name = esc(b["name"])
    has_phone, has_chat = bool(b.get("phone")), b.get("chatType") == "chat"
    heading = {(True, True): "Before you call or chat", (True, False): "Before you call",
               (False, True): "Before you start a chat"}.get((has_phone, has_chat), "Before you reach out")
    note = esc(b["scamWarningNote"]) if b.get("scamWarningNote") else (
        "Real {name} support won&rsquo;t ask you to read out a password or a one-time code, pay with gift cards, "
        "or install remote-access software. If anyone claiming to be {name} asks for any of that, stop there &mdash; "
        "it isn&rsquo;t them.".format(name=name))
    return """<div class="scam-box">
    <span class="scam-box__icon" aria-hidden="true">!</span>
    <div>
      <h2>{heading}</h2>
      <p>{note}</p>
      <ul>
        <li>Have your account email and any order, booking or policy number in front of you.</li>
        <li>The links on this page go to {poss} own website &mdash; you can confirm that in your browser&rsquo;s address bar.</li>
        <li>Seen a different number for {name} in an ad or search result? Assume it&rsquo;s unverified until you find it on {poss} own site.</li>
        <li>{site} never asks for your personal or payment details.</li>
      </ul>
    </div>
  </div>""".format(heading=heading, note=note, name=name, poss=possessive(name), site=esc(NAME))


def title_and_description(b: dict) -> tuple:
    has_phone, has_chat = bool(b.get("phone")), b.get("chatType") == "chat"
    if has_phone and has_chat:
        suffix, chan = "Phone Number, Chat & Hours", "phone number, chat and hours"
    elif has_phone:
        suffix, chan = "Phone Number & Hours", "phone number and hours"
    elif has_chat:
        suffix, chan = "No Phone? How to Reach Them", "official chat (no public phone line)"
    else:
        suffix, chan = "No Phone? How to Get Help", "official help channel (no public phone line)"
    title = "{} Customer Service: {} | {}".format(b["name"], suffix, NAME)
    desc = "How to contact {name}: the {chan}, checked against {name}'s own website on {date}. Independent guide, not run by {name}.".format(
        name=b["name"], chan=chan, date=human_date(b["verifiedDate"]))
    return title, desc


def render_brand(b: dict, copy_date: str) -> str:
    cat = CATEGORIES[b["category"]]
    path = "/brand/{}/".format(b["slug"])
    name = esc(b["name"])
    faqs = faq_items(b)
    issues = qa_details([(esc(i["issue"]), esc(i["tip"])) for i in b["issues"]], "issue")
    faq_html = qa_details(faqs, "faq", BRAND_FAQ_IDS)
    crumbs = [("Home", "/"), (cat["label"], "/category/{}/".format(cat["slug"])), (b["name"], path)]
    updated = max(b["verifiedDate"], copy_date)
    title, description = title_and_description(b)

    contact_point = {
        "@type": "ContactPoint",
        "contactType": "technical support" if "technical support" in line_label(b).lower() else "customer service",
        "areaServed": "US",
        "availableLanguage": ["English"],
        "url": b["chatUrl"],
    }
    if b.get("phone"):
        contact_point["telephone"] = schema_phone(b["phone"])
    if b["hours"].get("mode") == "247":
        contact_point["hoursAvailable"] = {
            "@type": "OpeningHoursSpecification",
            "dayOfWeek": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
            "opens": "00:00", "closes": "23:59"}
    page = webpage_node(path, "{} customer service".format(b["name"]), description, updated, speakable=True, extra={
        "lastReviewed": b["verifiedDate"],
        "reviewedBy": {"@id": BASE_URL + "/#organization"},
        "citation": b["sourceUrl"],
        "about": {"@type": "Organization", "name": b["name"], "url": official_root(b["chatUrl"]),
                  "contactPoint": [contact_point]},
        "mainEntity": {"@id": BASE_URL + path + "#faq"},
    })
    json_ld = script([page, breadcrumb_node(path, crumbs), faq_node(path, faqs, "faq", BRAND_FAQ_IDS)])

    body = """
<div class="container">{crumbs}</div>
<article class="brand-hero container">
  <div class="brand-hero__top">
    <span class="brand-hero__mark" aria-hidden="true">{mark}</span>
    <div>
      <h1>{name} customer service</h1>
      <p class="cat-label">{cat_label} &middot; Contact details checked {verified_h}</p>
    </div>
  </div>
  <div class="quick-answer">
    <span class="quick-answer__label">Quick answer</span>
    <p>{quick}</p>
  </div>

  <div class="contact-panel">
    <div class="contact-panel__grid">
      <div class="contact-panel__main">
        {phone_field}
        <div class="contact-field">
          <label>{channel_label} from {name}</label>
          <a class="chat-link" href="{chat_url}" rel="nofollow noopener" target="_blank">{chat_label} &rarr;</a>
        </div>
        {hours_field}
      </div>
      <div class="contact-panel__aside">
        <div class="stamp"><div class="stamp__inner">
          <div class="stamp__word">Verified</div>
          <div class="stamp__check" aria-hidden="true">&#10003;</div>
          <div class="stamp__date">{verified}</div>
        </div></div>
        <p class="stamp-caption">We checked these details on {poss} own website on {verified_h}. <a href="{source_url}" rel="nofollow noopener" target="_blank">See the source &rarr;</a></p>
      </div>
    </div>
  </div>

  {scam_box}

  <div class="issues-section">
    <h2 class="label-heading">What people contact {name} about &mdash; and what to try first</h2>
    <p class="stat-sub" style="margin-bottom:16px;">Practical tips that work for most companies. They aren&rsquo;t {poss} official policy, so check its help pages for the details.</p>
    <div class="faq-list">{issues}</div>
  </div>

  {key_facts}

  <div class="faq-list" style="margin-top:48px;border-top:1px solid var(--rule);">
    <h2 class="label-heading" style="margin:28px 0 4px;">{name} customer service: common questions</h2>
    {faq_html}
  </div>

  {related}
</article>
""".format(
        crumbs=crumbs_html(crumbs), mark=initial_mark(b["name"]), name=name, poss=possessive(name), cat_label=esc(cat["label"]),
        verified=esc(b["verifiedDate"]), verified_h=human_date(b["verifiedDate"]), quick=quick_answer(b),
        phone_field=phone_field(b), channel_label=CHANNEL_LABEL[b.get("chatType") or "form"],
        chat_url=esc(b["chatUrl"]), chat_label=esc(b["chatLabel"]), hours_field=hours_field(b),
        source_url=esc(b["sourceUrl"]), scam_box=scam_box(b), issues=issues, key_facts=key_facts(b),
        faq_html=faq_html, related=related_html(b),
    )
    og = "/og/{}.png".format(b["slug"])
    return layout(title=title, description=description, path=path, body=body, json_ld=json_ld,
                  og_image=og, og_type="article",
                  extra_head='<meta property="article:modified_time" content="{}">\n'.format(updated))
