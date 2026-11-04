"""The page shell used by every AI Totally page: header, independence ribbon,
footer, metadata and the Google Fonts loader."""
from common import BASE_URL, CATEGORIES, NAME, SITE, esc

NAV_ITEMS = [("/category/{}/".format(s), c.get("navLabel", c["label"])) for s, c in CATEGORIES.items()] + [
    ("/how-it-works/", "How It Works"),
]

FOOTER_NAV = [("/", "Home")] + [("/category/{}/".format(s), c["label"]) for s, c in CATEGORIES.items()] + [
    ("/research/companies-without-phone-support/", "Research: who has no phone line?"),
    ("/how-it-works/", "How It Works"),
    ("/faq/", "FAQ"),
    ("/about/", "About"),
    ("/contact/", "Contact"),
]

LEGAL_LINKS = [
    ("/privacy/", "Privacy Policy"),
    ("/terms/", "Terms of Service"),
    ("/trademark-notice/", "Trademark Notice"),
    ("/editorial-policy/", "Editorial Policy"),
    ("/accessibility/", "Accessibility"),
]

FONTS_LOADER = """<script>
(function(){
  try { if (localStorage.getItem('aitotally-fonts-optout') === '1') return; } catch(e) {}
  var head = document.head;
  ['https://fonts.googleapis.com', 'https://fonts.gstatic.com'].forEach(function(href, i){
    var l = document.createElement('link'); l.rel = 'preconnect'; l.href = href;
    if (i === 1) l.crossOrigin = '';
    head.appendChild(l);
  });
  var s = document.createElement('link'); s.rel = 'stylesheet';
  s.href = 'https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@600;700;800&family=Inter:wght@400;500;600;700&display=swap';
  head.appendChild(s);
})();
</script>"""


def _links(items: list, current: str = "") -> str:
    out = []
    for href, label in items:
        here = ' aria-current="page"' if current and href == current else ""
        out.append('<li><a href="{}"{}>{}</a></li>'.format(href, here, esc(label)))
    return "".join(out)


def logo_html() -> str:
    return '<a class="logo" href="/" aria-label="{} home">{}<span>.</span></a>'.format(
        esc(NAME), esc(SITE["logoText"]))


def verification_meta() -> str:
    token = SITE.get("googleSiteVerification")
    return '<meta name="google-site-verification" content="{}">\n'.format(esc(token)) if token else ""


def layout(*, title: str, description: str, path: str, body: str, json_ld: str = "",
           robots: str = "index, follow, max-snippet:-1, max-image-preview:large, max-video-preview:-1",
           og_image: str = "/og-image.png", og_type: str = "website", extra_head: str = "") -> str:
    canonical = BASE_URL + path
    return """<!doctype html>
<html lang="en-US">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{description}">
<meta name="robots" content="{robots}">
{verification}<link rel="canonical" href="{canonical}">
<link rel="alternate" hreflang="en-us" href="{canonical}">
<link rel="alternate" hreflang="x-default" href="{canonical}">
<meta property="og:type" content="{og_type}">
<meta property="og:site_name" content="{name}">
<meta property="og:locale" content="en_US">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{description}">
<meta property="og:url" content="{canonical}">
<meta property="og:image" content="{base}{og_image}">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{title}">
<meta name="twitter:description" content="{description}">
<meta name="twitter:image" content="{base}{og_image}">
<meta name="theme-color" content="#F6F8FC" media="(prefers-color-scheme: light)">
<meta name="theme-color" content="#0A101C" media="(prefers-color-scheme: dark)">
<meta name="color-scheme" content="light dark">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="/logo.png">
{fonts}
<link rel="stylesheet" href="/css/main.css">
{extra_head}{json_ld}
</head>
<body>
<a class="skip-link" href="#main">Skip to content</a>
<header class="site-header">
  <div class="site-header__bar">
    {logo}
    <button type="button" class="nav-toggle" id="nav-toggle" aria-expanded="false" aria-controls="site-nav">Menu</button>
    <nav aria-label="Primary">
      <ul class="site-nav" id="site-nav">{nav}</ul>
    </nav>
  </div>
</header>
<div class="indie-ribbon">
  <strong>We&rsquo;re independent</strong> &mdash; {name} isn&rsquo;t part of, paid by, or endorsed by any company you&rsquo;ll find here.
</div>
<main id="main">
{body}
</main>
<footer class="site-footer">
  <div class="container">
    <div class="footer-grid">
      {logo}
      <nav aria-label="Footer">
        <ul class="footer-nav">{footer_nav}</ul>
      </nav>
    </div>
    <div class="footer-legal">
      <p>{name} is an independent customer service finder. We have no business relationship with the companies listed here and don&rsquo;t speak for any of them. Company and product names belong to their owners and are used only to say whose contact details a page describes.</p>
      <p>&copy; 2026 {domain}. Every listing shows where its details came from and the date we checked them against the company&rsquo;s own website.</p>
      <ul class="footer-legal-links">{legal}<li><button type="button" id="fonts-optout-toggle" class="footer-legal-toggle">Turn off Google Fonts</button></li></ul>
    </div>
  </div>
</footer>
<script src="/js/search.js" defer></script>
<script src="/js/hours.js" defer></script>
<script src="/js/fonts-optout.js" defer></script>
<script src="/js/nav-toggle.js" defer></script>
<script src="/js/anchors.js" defer></script>
</body>
</html>
""".format(
        title=esc(title), description=esc(description), robots=robots, canonical=canonical,
        og_type=og_type, name=esc(NAME), base=BASE_URL, og_image=og_image, fonts=FONTS_LOADER, verification=verification_meta(),
        extra_head=extra_head, json_ld=json_ld, logo=logo_html(), nav=_links(NAV_ITEMS, path),
        footer_nav=_links(FOOTER_NAV), domain=esc(SITE["domain"]), legal=_links(LEGAL_LINKS), body=body,
    )
