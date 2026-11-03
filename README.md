# AI Totally — www.aitotally.com

An independent **customer service finder**. For each company it lists, AI Totally shows the phone number, chat link and support hours that company publishes on its own website, together with the source page and the date it was checked, plus practical "what to try first" tips and quick answers to common questions.

Static site, no framework. The generator uses only the Python 3 standard library and writes plain HTML into `dist/`.

## Project layout

```
build/
  build.py          Entry point — renders everything into dist/
  common.py         Loads + validates data/, shared helpers
  layout.py         Page shell: header, independence ribbon, footer, metadata
  brand_page.py     Company pages: quick answer, contact panel, tips, key facts, FAQ
  pages.py          Home, categories, About, Contact, How It Works, FAQ, 404
  legal.py          Privacy, Terms, Trademark notice, Editorial policy, Accessibility
  schema.py         JSON-LD @graph builders
  machine.py        robots.txt, sitemap.xml, llms.txt, llms-full.txt
  icons.py          Line-art category/page icons
data/
  site.json         Site settings, featured companies, category copy, page dates
  brands.json       One record per company (contact facts + issue tips)
public/             CSS, JS, favicon, logo, share images — copied into dist/
scripts/make-images.js   Regenerates logo + share images (run by hand)
tests/test_build.py      Unit + build tests
netlify.toml        Netlify build, redirects and security headers
```

## Build, test, preview

```bash
python3 build/build.py
python3 -m unittest discover -s tests -v
python3 -m http.server 4174 --directory dist
```

## Deploy on Netlify

1. In Netlify, choose **Add new site → Import an existing project → GitHub** and pick `kdtichi/aitotally`.
2. Leave the base directory empty; `netlify.toml` sets the build command (`python3 build/build.py`) and publish directory (`dist`).
3. Under **Domain management**, add `www.aitotally.com` and `aitotally.com`, then use **Options → Set as primary domain** on `www.aitotally.com`. Netlify redirects the bare domain and plain HTTP to it automatically. Do not add an apex→www rule to `netlify.toml`: if the primary domain is ever the bare domain, the two redirects loop.

Every push to `main` redeploys automatically.

## Adding or editing a company

Add an object to `data/brands.json`:

```json
{
  "slug": "example",
  "name": "Example Inc",
  "category": "retail",
  "aliases": ["example customer service", "example phone number"],
  "phone": "1-800-555-0100",
  "phoneNote": "Optional: other numbers or hours for this line.",
  "chatUrl": "https://www.example.com/help",
  "chatLabel": "Example Help Center",
  "chatType": "chat",
  "hours": { "mode": "247" },
  "verifiedDate": "2026-11-03",
  "sourceUrl": "https://www.example.com/contact",
  "sourceLabel": "Example Contact Us page",
  "issues": [
    { "issue": "Track an order", "tip": "Open the order in your account first ..." }
  ]
}
```

Then run `node scripts/make-images.js` to give it a share image, rebuild, and run the tests. The build refuses to run if a record is incomplete.

Field notes:

- `phone`: `null` when the company publishes no number. Explain why in `phoneAltNote`; the page then says so honestly instead of showing a number.
- `phoneLineLabel` (optional): name the line when the main number is a department line, e.g. `"technical support line (website and account issues)"`.
- `chatType`: `chat`, `form` or `none` (help center only). It controls how the online channel is described.
- `hours.mode`:
  - `{"mode": "247"}` for 24/7 support.
  - `{"mode": "unspecified", "text": "..."}` when hours aren't published or are complicated.
  - `{"mode": "detailed", "tz": "America/Los_Angeles", "start": "04:00", "end": "21:00", "days": "daily"}` for one clean daily window. The page converts it to the visitor's time and shows "Open now" or "Closed now".
- `scamWarningNote` (optional): a company-specific warning, e.g. about a number that circulates but can't be confirmed.
- `issues`: 5–7 entries. Use issue names from the company's own help center. Each `tip` is general, true-for-anyone advice; never a specific policy you haven't verified.

## Editorial rules

- **Never invent a phone number, hours or policy.** Every fact must trace to `sourceUrl` on the company's own domain, never a forum, ad or other directory.
- `verifiedDate` is the day you actually checked the source. Don't bump it to look fresh: it drives the page's "verified" stamp and the sitemap `lastmod`.
- Static pages' dates live in `pagesUpdated` in `data/site.json`. Change one only when that page's content really changes.
- No company logos or branding anywhere: listings are identified by name only.

## Design

Bright and modern: a cool neutral background, indigo accent, mint reserved for "verified" and "open now", and amber for scam warnings. Plus Jakarta Sans (headings) is paired with Inter (body), with rounded cards, a gradient hero with a pill search, and a navy band for "how it works" and the footer. Dark mode is automatic. All design tokens are CSS variables at the top of `public/css/main.css`.

## SEO, AEO and GEO

- **SEO:** unique titles and descriptions, canonical `www` URLs, breadcrumbs, `sitemap.xml` with honest `lastmod`, fast static HTML, mobile-first layout, internal links by category.
- **AEO (answer engines):** every company page opens with a self-contained *Quick answer*, followed by question-style FAQs and a key-facts table. `FAQPage` and `speakable` markup point assistants at the answer text.
- **GEO (generative engines):** each page carries one connected JSON-LD `@graph` (Organization → WebSite → WebPage → the company's `ContactPoint`, with `citation`, `lastReviewed` and `reviewedBy`). `robots.txt` explicitly allows AI crawlers, and `llms.txt` / `llms-full.txt` give AI systems a clean, citable summary of every listing.
