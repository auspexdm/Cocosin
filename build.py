#!/usr/bin/env python3
"""Build the multi-page Coco's Inn site from the single-file source (src/site.html).

- Extracts every inline base64 image into /assets/img/ (deduplicated) so pages are light.
- Writes one real, crawlable page per section (/, /rooms/, /dining/ ...), each with its own
  title, meta description, canonical URL, Open Graph tags and exactly one H1.
- Rewrites the old #/ hash links to real URLs and redirects old #/ links to the new pages.
- Regenerates sitemap.xml.

Run:  python3 build.py
"""
import base64, hashlib, html, json, os, re

ROOT = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(ROOT, "src", "site.html")
BASE = "https://www.cocosinn.com"

PAGES = {
    # key: (path, title, description)
    "home": ("/", "Coco's Inn Resort — Coastal Comfort Near Kashid Beach | Alibaug",
             "Coco's Inn Resort — coastal comfort with a touch of luxury just 2.6 km from Kashid Beach, Alibaug. Sea view rooms, Kokani dining, events & weddings."),
    "rooms": ("/rooms/", "Rooms & Suites near Kashid Beach | Coco's Inn Resort, Alibaug",
              "Sea view rooms and suites at Coco's Inn Resort, 2.6 km from Kashid Beach. Ideal for families, couples and groups. Book direct for the best rates."),
    "dining": ("/dining/", "Restaurant near Kashid Beach — Kokani Dining | Coco's Inn",
               "Multi-cuisine and Kokani dining at Coco's Inn Resort near Kashid Beach, Alibaug — fresh coastal seafood, local flavours and relaxed resort dining."),
    "events": ("/events/", "Weddings, Events & Offsites near Kashid Beach | Coco's Inn",
               "Host weddings, celebrations, conferences and team offsites at Coco's Inn Resort near Kashid Beach, Alibaug. Enquire for dates and packages."),
    "things": ("/things-to-do/", "Things to Do near Kashid Beach & Murud | Coco's Inn Resort",
               "Explore Kashid Beach, Murud-Janjira Fort, Phansad Wildlife Sanctuary and more from Coco's Inn Resort in Barshiv, near Kashid, Alibaug."),
    "reach": ("/how-to-reach/", "How to Reach Coco's Inn Resort, Kashid — Road & Ferry",
              "Directions to Coco's Inn Resort in Barshiv, 2.6 km from Kashid Beach on the Alibaug–Murud coastal road, by road or by ferry from Mumbai."),
    "gallery": ("/gallery/", "Photo Gallery | Coco's Inn Resort, Kashid Beach Alibaug",
                "See Coco's Inn Resort near Kashid Beach — aerial views, pools, rooms, dining and Konkan sunsets."),
    "about": ("/about/", "About Coco's Inn Resort — Coastal Retreat near Kashid, Alibaug",
              "Coco's Inn Resort is a coastal retreat near Kashid Beach, Alibaug, with ocean views, modern amenities and warm Konkan hospitality."),
    "journal": ("/journal/", "Journal — Kashid & Alibaug Travel Guides | Coco's Inn Resort",
                "Travel guides and local tips for Kashid Beach and Alibaug from Coco's Inn Resort: family trips, day trips, food and where to stay."),
    "journal-kashid": ("/journal/kashid-beach-family-trip-guide/", "Kashid Beach Family Trip Guide: Stay, Eat & Things to Do",
                       "Planning a family trip to Kashid Beach? Where to stay 2.6 km from the beach, where to eat, and day trips to Murud-Janjira and Phansad."),
    "contact": ("/contact/", "Contact & Booking | Coco's Inn Resort, Kashid Beach",
                "Call or WhatsApp +91 91675 62668 to book Coco's Inn Resort, Barshive, near Kashid Beach, Tal. Murud, Raigad 402202."),
}

src = open(SRC, encoding="utf-8").read()

# ---------- 1. extract inline images ----------
img_dir = os.path.join(ROOT, "assets", "img")
os.makedirs(img_dir, exist_ok=True)
EXT = {"webp": "webp", "png": "png", "jpeg": "jpg", "jpg": "jpg", "gif": "gif", "svg+xml": "svg"}
seen = {}

def extract(m):
    mime, data = m.group(1), m.group(2)
    raw = base64.b64decode(data)
    h = hashlib.sha1(raw).hexdigest()[:12]
    name = f"{h}.{EXT.get(mime, 'bin')}"
    if name not in seen:
        with open(os.path.join(img_dir, name), "wb") as f:
            f.write(raw)
        seen[name] = len(raw)
    return f"/assets/img/{name}"

src = re.sub(r"data:image/([a-z+]+);base64,([A-Za-z0-9+/=]+)", extract, src)

# ---------- 2. split the document ----------
head_end = src.index("</head>")
head = src[:head_end]
body = src[head_end:]
main_start = body.index("<main>") + len("<main>")
main_end = body.index("</main>")
before_main, main_html, after_main = body[:main_start], body[main_start:main_end], body[main_end:]

# page blocks
starts = [(m.start(), m.group(1)) for m in re.finditer(r'<div class="page" id="pg-([a-z-]+)">', main_html)]
blocks = {}
for i, (pos, key) in enumerate(starts):
    end = starts[i + 1][0] if i + 1 < len(starts) else len(main_html)
    blocks[key] = main_html[pos:end].rstrip()
assert set(blocks) == set(PAGES), blocks.keys()

# ---------- 3. link + script rewrites ----------
def fix_links(s):
    for key, (path, *_ ) in PAGES.items():
        s = s.replace(f'href="#/{key}"', f'href="{path}"')
    return s.replace('href="#/"', 'href="/"')

ROUTER_OLD = re.search(r"// ---------- hash router ----------.*?window\.addEventListener\('hashchange',\(\)=>\{\s*if\(!window\.fbq\) return;.*?\}\);\s*\}\);", after_main, re.S)
assert ROUTER_OLD, "router block not found"
ROUTER_NEW = """// ---------- multi-page nav (replaces old hash router) ----------
const pages=%s;
const PATHS=%s;
const CURRENT=document.body.dataset.page||'home';
// old #/section links still work: send them to the real page
(function(){const h=(location.hash||'').replace('#/','');if(h&&PATHS[h]&&PATHS[h]!==location.pathname)location.replace(PATHS[h]);})();
function route(){
  document.querySelectorAll('[data-nav]').forEach(a=>a.classList.toggle('active',a.dataset.nav===CURRENT.split('-')[0]));
  reveal();
}
if(window.fbq&&['rooms','dining','events'].includes(CURRENT)) fbq('track','ViewContent',{content_name:CURRENT});""" % (
    json.dumps(list(PAGES)), json.dumps({k: v[0] for k, v in PAGES.items()}))
after_main = after_main.replace(ROUTER_OLD.group(0), ROUTER_NEW)
after_main = after_main.replace("page_location:location.hash||'#/home'", "page_location:location.pathname")
after_main = re.sub(r"\n\s*window\.addEventListener\('hashchange',\(\)=>\{l\.classList\.remove\('hide'\);setTimeout\(\(\)=>l\.classList\.add\('hide'\),450\)\}\);", "", after_main)

# ---------- 4. per-page head ----------
def page_head(key):
    path, title, desc = PAGES[key]
    url = BASE + path
    h = head
    h = re.sub(r"<title>.*?</title>", f"<title>{html.escape(title)}</title>", h, flags=re.S)
    h = re.sub(r'<meta name="description" content="[^"]*">', f'<meta name="description" content="{html.escape(desc)}">', h)
    h = re.sub(r'<link rel="canonical" href="[^"]*">', f'<link rel="canonical" href="{url}">', h)
    h = re.sub(r'<meta property="og:title" content="[^"]*">', f'<meta property="og:title" content="{html.escape(title)}">', h)
    h = re.sub(r'<meta property="og:description" content="[^"]*">', f'<meta property="og:description" content="{html.escape(desc)}">', h)
    h = re.sub(r'<meta property="og:url" content="[^"]*">', f'<meta property="og:url" content="{url}">', h)
    if key == "home":
        faqs = json.load(open(os.path.join(ROOT, "src", "faqs-home.json"), encoding="utf-8"))
        faq = {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
            {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in faqs]}
        h = h.replace("</title>", "</title>\n<script type=\"application/ld+json\">" + json.dumps(faq, ensure_ascii=False) + "</script>", 1)
    if key != "home":  # Resort schema lives on the home page; inner pages get breadcrumbs
        h = re.sub(r'<script type="application/ld\+json">.*?</script>\n?', "", h, count=1, flags=re.S)
        crumb = {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Home", "item": BASE + "/"},
            {"@type": "ListItem", "position": 2, "name": title.split("|")[0].split("—")[0].strip(), "item": url}]}
        extra = [crumb]
        if key.startswith("journal-"):
            crumb["itemListElement"].insert(1, {"@type": "ListItem", "position": 2, "name": "Journal", "item": BASE + "/journal/"})
            crumb["itemListElement"][2]["position"] = 3
            extra.append({"@context": "https://schema.org", "@type": "BlogPosting", "headline": title, "description": desc,
                          "image": BASE + "/assets/img/15a1587e6f95.webp", "datePublished": "2026-11-20", "dateModified": "2026-11-20",
                          "inLanguage": "en-IN", "author": {"@type": "Organization", "name": "Coco's Inn Resort"},
                          "publisher": {"@type": "Organization", "name": "Coco's Inn Resort", "url": BASE + "/"},
                          "mainEntityOfPage": url})
        h = h.replace("</title>", "</title>\n" + "".join("<script type=\"application/ld+json\">" + json.dumps(x, ensure_ascii=False) + "</script>\n" for x in extra), 1)
    return h

def page_block(key):
    b = blocks[key].replace(f'<div class="page" id="pg-{key}">', f'<div class="page current" id="pg-{key}">', 1)
    if key != "home":
        # inner pages: the banner heading is this page's single H1
        b = re.sub(r"<h2>(.*?)</h2>", r"<h1>\1</h1>", b, count=1, flags=re.S)
    return b

written = []
for key, (path, *_ ) in PAGES.items():
    out = page_head(key) + before_main.replace("<body>", f'<body data-page="{key}">', 1) + "\n" + page_block(key) + "\n" + after_main
    out = fix_links(out)
    n_h1 = len(re.findall(r"<h1[\s>]", out))
    assert n_h1 == 1, (key, n_h1)
    dest = os.path.join(ROOT, path.strip("/"), "index.html") if path != "/" else os.path.join(ROOT, "index.html")
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    open(dest, "w", encoding="utf-8").write(out)
    written.append((path, len(out.encode())))

# ---------- 5. sitemap ----------
urls = "\n".join(
    f"  <url><loc>{BASE}{p}</loc><lastmod>2026-11-20</lastmod><priority>{'1.0' if p == '/' else '0.8'}</priority></url>"
    for p, *_ in PAGES.values())
open(os.path.join(ROOT, "sitemap.xml"), "w").write(
    '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + urls + "\n</urlset>\n")

print(f"images: {len(seen)} files, {sum(seen.values())//1024} KB")
for p, size in written:
    print(f"{p:16} {size//1024} KB")
