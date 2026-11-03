#!/usr/bin/env node
/*
 * Render AI Totally's social-share images and logo with headless Chromium.
 * One-off asset script, not part of the Netlify build. Re-run after adding a
 * brand so it gets its own 1200x630 share image:
 *
 *   node scripts/make-images.js
 *
 * Needs Playwright (Node) with Chromium. Writes to public/.
 */
"use strict";
const fs = require("fs");
const path = require("path");
const { chromium } = require("playwright");

const SITE_ROOT = path.resolve(__dirname, "..");
const BRANDS = path.join(SITE_ROOT, "data", "brands.json");
const PUBLIC = path.join(SITE_ROOT, "public");

const esc = (s) => String(s).replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));

const CSS = `
*{box-sizing:border-box;margin:0}
body{width:1200px;height:630px;background:#F6F8FC;color:#0E1726;font-family:'Segoe UI',Helvetica,Arial,sans-serif;
  display:flex;flex-direction:column;justify-content:space-between;padding:72px 80px;position:relative;overflow:hidden}
body::before{content:"";position:absolute;inset:0;background:radial-gradient(520px 300px at 12% 8%,rgba(53,80,240,.18),transparent 70%),radial-gradient(520px 300px at 92% 92%,rgba(15,166,120,.20),transparent 70%)}
body>*{position:relative}
.brand{display:flex;align-items:center;gap:16px;font-size:40px;font-weight:800;letter-spacing:-1.5px}
.brand::before{content:"at";display:grid;place-items:center;width:58px;height:58px;border-radius:16px;background:linear-gradient(135deg,#3550F0,#0FA678);color:#fff;font-size:26px;letter-spacing:-1px}
.brand span{color:#0B7F5C}
.eyebrow{display:inline-block;padding:10px 20px;border-radius:999px;background:#fff;border:1px solid #E2E7F0;font-size:24px;font-weight:700;color:#3550F0;margin-bottom:26px}
h1{font-size:84px;line-height:1.04;font-weight:800;letter-spacing:-3px;max-width:1040px}
.foot{font-size:26px;color:#3F4B5E;display:flex;justify-content:space-between}
.tick{color:#0B7F5C;font-weight:800}`;

const card = (eyebrow, headline, foot) => `<!doctype html><html><head><meta charset="utf-8"><style>${CSS}</style></head><body>
<div class="brand">aitotally<span>.</span></div>
<div><div class="eyebrow">${esc(eyebrow)}</div><h1>${esc(headline)}</h1></div>
<div class="foot"><span>${esc(foot)}</span><span><span class="tick">&#10003;</span> Checked against official sites</span></div>
</body></html>`;

const LOGO = `<!doctype html><html><head><meta charset="utf-8"><style>
*{margin:0}body{width:512px;height:512px;display:grid;place-items:center;background:transparent}
.m{width:512px;height:512px;border-radius:112px;background:linear-gradient(135deg,#3550F0,#0FA678);display:grid;place-items:center;
font-family:'Segoe UI',Helvetica,Arial,sans-serif;font-weight:800;font-size:230px;color:#fff;letter-spacing:-12px}
</style></head><body><div class="m">at</div></body></html>`;

(async () => {
  const brands = JSON.parse(fs.readFileSync(BRANDS, "utf8")).brands;
  fs.mkdirSync(path.join(PUBLIC, "og"), { recursive: true });
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1200, height: 630 }, deviceScaleFactor: 1 });
  await page.setContent(card("Customer service finder", "Find the real way to reach customer service.", "www.aitotally.com"));
  await page.screenshot({ path: path.join(PUBLIC, "og-image.png") });
  for (const b of brands) {
    await page.setContent(card("Customer service", `How to contact ${b.name}`, "Independent guide · www.aitotally.com"));
    await page.screenshot({ path: path.join(PUBLIC, "og", `${b.slug}.png`) });
  }
  const logo = await browser.newPage({ viewport: { width: 512, height: 512 } });
  await logo.setContent(LOGO);
  await logo.screenshot({ path: path.join(PUBLIC, "logo.png"), omitBackground: true });
  await browser.close();
  process.stdout.write(`Wrote og-image.png, logo.png and ${brands.length} brand images\n`);
})().catch((err) => {
  process.stderr.write(String(err && err.stack ? err.stack : err) + "\n");
  process.exit(1);
});
