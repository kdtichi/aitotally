"""Policy pages: privacy, terms, trademark notice, editorial policy, accessibility."""
from common import NAME, SITE, esc
from pages import info_page

EMAIL = esc(SITE["contactEmail"])
N = esc(NAME)


def _mail() -> str:
    return '<a href="mailto:{0}">{0}</a>'.format(EMAIL)


def render_privacy() -> str:
    prose = """
<p><strong>Effective November 3, 2026</strong></p>
<p>{n} is an independent directory of customer service contact details that companies publish themselves. We collect very little, and this page explains exactly what and why.</p>
<h2>What we collect</h2>
<p><strong>Emails you send us.</strong> If you write to {mail} &mdash; to flag a wrong listing, suggest a company or ask something &mdash; we get your email address and whatever you put in the message. We use it only to reply and to check or fix the listing you mentioned.</p>
<p><strong>Standard server logs.</strong> Our hosting provider automatically records basic technical details for each visit, such as IP address, browser type, the page requested and the time. We use these to keep the site secure and to understand overall traffic. We don&rsquo;t use them to profile you or follow you around the web.</p>
<p><strong>No tracking cookies.</strong> {n} sets no cookies at all &mdash; no ad cookies, no tracking cookies, no third-party analytics &mdash; which is why there&rsquo;s no cookie banner. A few pages use your browser&rsquo;s local storage for small preferences, like the font setting below; that stays on your device.</p>
<p><strong>Fonts.</strong> We load our typefaces from Google Fonts, which means your browser contacts Google&rsquo;s servers and Google can see your IP address under <a href="https://policies.google.com/privacy" rel="nofollow noopener" target="_blank">its own privacy policy</a>. If you&rsquo;d rather it didn&rsquo;t, use &ldquo;Turn off Google Fonts&rdquo; in the footer. That stops the request entirely on your device, and the site switches to your system fonts.</p>
<h2>Links to other sites</h2>
<p>Company pages link to each company&rsquo;s own website, phone line or chat. Once you leave {n}, that company&rsquo;s privacy policy applies, not ours.</p>
<h2>How we use information</h2>
<ul><li>To answer your emails and correct listings</li><li>To keep the site secure and working</li><li>To understand overall, non-identifying traffic</li></ul>
<p>We don&rsquo;t sell personal information or share it with anyone for marketing. We would only disclose it if the law required us to, or to protect people&rsquo;s safety or our legal rights.</p>
<h2>How long we keep it</h2>
<p>We keep emails only as long as we need to deal with them, then delete them routinely. Server logs are kept for a limited time in line with normal hosting practice.</p>
<h2>Children</h2>
<p>{n} isn&rsquo;t aimed at children under 13, and we don&rsquo;t knowingly collect their information.</p>
<h2>Your rights</h2>
<p>Depending on where you live, laws such as the CCPA or the EU/UK GDPR may give you the right to see, correct or delete information we hold about you. Email {mail} to ask.</p>
<h2>Who runs this site</h2>
<p>{n} is an independent, online-only project. Send any privacy request, including formal requests under the laws above, to {mail}.</p>
<h2>Changes</h2>
<p>If this policy changes, we&rsquo;ll update this page and its effective date.</p>
""".format(n=N, mail=_mail())
    return info_page(path="/privacy/", eyebrow="Legal", h1="Privacy Policy", prose=prose,
                     title="Privacy Policy | {}".format(NAME),
                     description="What {} collects (very little), how it's used, and what we never collect.".format(NAME))


def render_terms() -> str:
    prose = """
<p><strong>Effective November 3, 2026</strong></p>
<p>These terms cover your use of {domain} (&ldquo;the site&rdquo;). By using the site you agree to them; if you don&rsquo;t, please don&rsquo;t use it.</p>
<h2>What {n} is</h2>
<p>An independent, informational directory of customer service contact details &mdash; phone numbers, chat links and support hours &mdash; taken from each company&rsquo;s own website. <strong>{n} is not affiliated with, endorsed by or sponsored by any company on the site</strong>, or their subsidiaries or affiliates.</p>
<h2>For information only</h2>
<p>The site is general information. It doesn&rsquo;t replace contacting a company through its own channels, and it isn&rsquo;t legal, financial or other professional advice.</p>
<h2>Accuracy</h2>
<p>We work hard to check every listing against the company&rsquo;s own website and show the date and source on each page. Even so:</p>
<ul>
<li>Companies change numbers, hours and channels without notice, so a listing can go out of date between checks.</li>
<li>We can&rsquo;t guarantee that any listing is accurate, complete or current.</li>
<li>Before relying on a listing for anything important &mdash; especially involving your account, money or personal data &mdash; confirm it on the company&rsquo;s own website.</li>
</ul>
<p>Found an error? <a href="/contact/">Let us know</a>.</p>
<h2>Other companies&rsquo; services</h2>
<p>We link to phone lines, chat tools and websites run by other companies. We don&rsquo;t control them and aren&rsquo;t responsible for their content, security, availability or what happens when you use them.</p>
<h2>Trademarks</h2>
<p>Company and brand names on the site belong to their owners and are used only to identify whose contact details a page describes. See our <a href="/trademark-notice/">Trademark Notice</a>.</p>
<h2>Fair use of the site</h2>
<p>Please don&rsquo;t:</p>
<ul>
<li>Pretend to be {n} or any company listed here</li>
<li>Use contact details from the site to harass, defraud or spam anyone</li>
<li>Copy or republish the site&rsquo;s content in bulk without permission</li>
<li>Try to disrupt the site or access it without authorization</li>
</ul>
<h2>No warranties</h2>
<p>The site is provided &ldquo;as is&rdquo; and &ldquo;as available&rdquo;, without warranties of any kind, including accuracy, fitness for a particular purpose or non-infringement.</p>
<h2>Limitation of liability</h2>
<p>To the extent the law allows, {n} isn&rsquo;t liable for indirect, incidental, special or consequential damages, or for loss of money, data or goodwill, arising from using the site or relying on a listing &mdash; including losses from a scam you came across elsewhere.</p>
<h2>Changes</h2>
<p>We may update these terms. If you keep using the site after a change, you accept the new terms. We&rsquo;ll update the effective date whenever we do.</p>
<h2>Questions</h2>
<p>Email {mail}.</p>
""".format(n=N, domain=esc(SITE["domain"]), mail=_mail())
    return info_page(path="/terms/", eyebrow="Legal", h1="Terms of Service", prose=prose,
                     title="Terms of Service | {}".format(NAME),
                     description="The terms for using {}'s independent customer service finder.".format(NAME))


def render_trademark() -> str:
    prose = """
<p><strong>Effective November 3, 2026</strong></p>
<p>{n} is independent. We are <strong>not affiliated with, endorsed by, sponsored by or otherwise connected with</strong> any company named on this site, or with their subsidiaries or affiliates.</p>
<h2>Who owns the names</h2>
<p>Every company, product and brand name on {n} is a trademark or registered trademark of its owner. Nothing here claims any ownership of, or rights to, those marks.</p>
<h2>Why we mention them</h2>
<p>We use a company&rsquo;s name only to say whose contact details a page describes &mdash; the same way a phone book or a news story names a business. It&rsquo;s factual, and it doesn&rsquo;t suggest any sponsorship or partnership.</p>
<p>We don&rsquo;t use company logos or branding. Every listing appears in {n}&rsquo;s own design, so nothing here could be mistaken for a company&rsquo;s own website.</p>
<h2>For rights holders</h2>
<p>If you represent a listed company and have concerns about how your name is used, email {mail}. We&rsquo;ll respond promptly and are happy to correct, change or remove a listing at your request.</p>
""".format(n=N, mail=_mail())
    return info_page(path="/trademark-notice/", eyebrow="Legal", h1="Trademark Notice", prose=prose,
                     title="Trademark Notice | {}".format(NAME),
                     description="{} is independent of every company it lists. How and why we mention company names.".format(NAME))


def render_editorial_policy() -> str:
    prose = """
<p><strong>Effective November 3, 2026</strong></p>
<p>This is the standard every listing on {n} has to meet, written down in one place.</p>
<h2>Where facts come from</h2>
<p>Every phone number, chat link and set of support hours is checked on the company&rsquo;s own website &mdash; its help center, contact page or a support article. We don&rsquo;t use forums, review sites, other directories or ads as a source, even when they&rsquo;d be quicker.</p>
<h2>When we can&rsquo;t confirm something</h2>
<p>Sometimes an official page is blocked, unavailable or contradicts itself. When that happens, we either say so on the listing or leave the company out until we can confirm it. We never fill a gap with a guess.</p>
<h2>Companies with no phone line</h2>
<p>Plenty of companies don&rsquo;t publish a phone number. We say that outright, rather than borrowing a number from somewhere else &mdash; that kind of substitution is exactly how many support scams start.</p>
<h2>Dates</h2>
<p>Each company page shows the date its details were last checked. That date only moves when we actually recheck the source &mdash; never just to make a page look fresh, on the page or in our sitemap.</p>
<h2>Tips and guidance</h2>
<p>The &ldquo;what to try first&rdquo; tips on each company page are practical general advice written by {n}. They are not the company&rsquo;s official policy, and we label them that way.</p>
<h2>No look-alikes</h2>
<p>We don&rsquo;t use company logos, icons or branding, so no page here can be mistaken for the real company&rsquo;s site. The <a href="/trademark-notice/">Trademark Notice</a> has the detail.</p>
<h2>Corrections</h2>
<p>Report an error on the <a href="/contact/">Contact page</a>. We recheck every report against the official source before changing anything.</p>
<h2>Independence</h2>
<p>No company on {n} owns us, pays us or reviews our pages. That&rsquo;s stated on every page, not just this one.</p>
""".format(n=N)
    return info_page(path="/editorial-policy/", eyebrow="Legal", h1="Editorial Policy", prose=prose,
                     title="Editorial Policy | {}".format(NAME),
                     description="How {} sources, verifies, dates and corrects every customer service listing.".format(NAME))


def render_accessibility() -> str:
    prose = """
<p><strong>Last reviewed November 3, 2026</strong></p>
<p>People usually land on {n} in the middle of a problem, sometimes stressed and sometimes using assistive technology. The site has to work for all of them.</p>
<h2>Our target</h2>
<p>We aim to meet <strong>WCAG 2.1 Level AA</strong>.</p>
<h2>What&rsquo;s built in</h2>
<ul>
<li>Semantic HTML with a logical heading order on every page</li>
<li>Text contrast of at least 4.5:1</li>
<li>Clear keyboard focus everywhere &mdash; nothing needs a mouse</li>
<li>A keyboard-friendly search with proper ARIA roles</li>
<li>Big tap-to-call numbers, sized for one-handed phone use</li>
<li>A layout that works from small phones to wide screens</li>
</ul>
<h2>Still improving</h2>
<p>We test new pages as we add them. If you hit a barrier &mdash; a missing label, a focus trap, hard-to-read text &mdash; please tell us. It&rsquo;s a bug we want to fix.</p>
<h2>Report a problem</h2>
<p>Email {mail} with the page address and what happened. We aim to reply within a few business days.</p>
""".format(n=N, mail=_mail())
    return info_page(path="/accessibility/", eyebrow="Legal", h1="Accessibility Statement", prose=prose,
                     title="Accessibility Statement | {}".format(NAME),
                     description="{}'s WCAG 2.1 AA accessibility commitment, what's built in, and how to report a barrier.".format(NAME))
