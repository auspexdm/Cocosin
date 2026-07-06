# Coco's Inn Resort — Website Redesign (V1 Draft)

Premium redesign of [cocosinn.com](https://cocosinn.com) for **Coco's Inn Resort by Spicy Mango**, Kashid Beach, Alibaug.
Built by **Auspex Digital Marketing** · July 2026 · Version 1 (client review draft).

---

## 1. What this is

A single self-contained HTML file — `cocos-inn-v1-draft.html` — containing the entire redesigned website. No build step, no dependencies, no server required. Open it in any browser and it works, including on mobile.

All content (headings, paragraphs, room details, dining menu, attractions, reviews, contact info) has been **migrated verbatim from the current live website**. No resort information was invented.

---

## 2. How to review

1. Open `cocos-inn-v1-draft.html` in Chrome / Safari / any browser.
2. Navigate using the top menu — all 7 pages work via client-side routing (`#/home`, `#/rooms`, etc.).
3. Test mobile by resizing the window or opening on a phone (hamburger menu appears below 760px).
4. Click any real photo to open the lightbox.
5. The floating green button opens WhatsApp chat to +91 91675 62668.

---

## 3. Pages included

| Route | Page | Content |
|---|---|---|
| `#/home` | Home | Hero, Why Choose Coco's Inn, discovery cards, amenities, testimonials (675+ Google reviews), reservation form |
| `#/rooms` | Our Rooms | All 5 room categories with descriptions, amenity chips, pricing placeholders, Book Now CTAs |
| `#/dining` | Dining | Restaurant intro, Kokani Delights menu (Fish Curry, Chicken Sukka, Sol Kadhi, Bombil Fry), local ingredients, 7 real food/restaurant photos |
| `#/events` | Events | Corporate events, corporate activities, weddings |
| `#/things` | Things To Do | Kashid Beach, Murud-Janjira Fort, Korli Fort, Korli Lighthouse, Birla Mandir, Revdanda Fort, Phansad Wildlife Sanctuary |
| `#/about` | About Us | Full about copy, facilities & services, guest reviews, closing CTA |
| `#/contact` | Contact | Address, both phone numbers, socials, WhatsApp, reservation form, Google Maps embed |

---

## 4. Design system

**Palette (derived from the Coco's Inn logo):**

| Token | Hex | Use |
|---|---|---|
| `--lime` | `#8CC63E` | Logo palm green — primary accent, CTAs, swoosh motif |
| `--palm` | `#44691F` | Deep palm green — hover states, links, icons |
| `--ink` | `#20241C` | Logo charcoal — text, dark sections, footer |
| `--ivory` | `#FBFAF5` | Page canvas |
| `--sand` / `--sand-2` | `#EFEADD` / `#E4DCC9` | Tinted sections, placeholders |
| `--gold` | `#C2A25E` | Soft gold accents — taglines, stars |

**Typography:** Marcellus (display/headings) + Mulish (body), loaded from Google Fonts.

**Signature motif:** the green heart-swoosh from the logo, used as an SVG underline beneath key headings, plus a palm silhouette watermark in the hero.

All tokens live in the `:root` block at the top of the file — change a hex once and it updates everywhere.

---

## 5. Features

- Sticky navbar — transparent over the hero, solid with blur on scroll
- Full mobile menu + responsive layouts (desktop / laptop / tablet / mobile)
- Scroll-reveal fade-up animations (respects `prefers-reduced-motion`)
- Hover zoom on photos, card lift effects
- Lightbox for gallery images
- Floating WhatsApp button (wa.me link with pre-filled message)
- Google Maps embed on Contact
- Reservation forms on Home + Contact (demo validation only — see §7)
- Lazy-loaded images, semantic HTML, meta title/description for SEO

---

## 6. Image placeholders — known limitation

The current WordPress site lazy-loads its galleries, so only these assets exposed real URLs and are hotlinked live in the draft:

- Logo (used in navbar, footer, favicon)
- 7 dining/restaurant photos (`/wp-content/uploads/2024/09/…`)

**Every other image slot is a clearly labeled sand-colored placeholder** (e.g. "Room gallery · 11 photos — Sea View Premium AC — insert from current site"). The labels tell you exactly which asset goes where.

**To replace for V2:** download originals from the site's WordPress admin (`wp-admin → Media Library`), then swap each `<div class="ph">…</div>` block for:

```html
<div class="photo"><img loading="lazy" src="images/room-premium-1.jpg" alt="Sea View Premium AC Room"></div>
```

The hero also has a reserved slot — the corner tag reads "Hero video / drone footage drops in here — v2".

---

## 7. Forms — draft note

Both reservation forms (Name, Email, Phone, Check-In Date) currently run demo validation only; nothing is sent anywhere. For the live build, wire them to one of:

- **Web3Forms** (fastest — one hidden access-key input, no backend)
- WPForms if rebuilt inside WordPress
- Any email API / webhook

Each form card carries a visible note: *"form will be wired to WPForms / email on the live build"* — remove that line once connected.

---

## 8. Editing guide

Everything is plain HTML in one file, organized by page:

```
<style>            ← all design tokens + CSS
<header>           ← navbar
#pg-home           ← Home page sections
#pg-rooms          ← Rooms
#pg-dining         ← Dining
#pg-events         ← Events
#pg-things         ← Things To Do
#pg-about          ← About
#pg-contact        ← Contact
<footer>           ← footer
<script>           ← router, nav, reveal, lightbox, form
```

- **Text edits:** search for the sentence and change it in place.
- **Add a room:** copy an existing `.card` block inside `#pg-rooms`.
- **Pricing:** replace `₹ —,———` placeholders once rates are confirmed.
- **New page:** add a `<div class="page" id="pg-xyz">`, add `'xyz'` to the `pages` array in the script, and add a nav link `href="#/xyz"`.

---

## 9. Deployment

For the draft: share the HTML file directly, or drop it on Vercel / Netlify / Hostinger as-is (rename to `index.html`).

For production (post-approval), recommended path: split into a proper multi-page static build or component-based rebuild, self-host the images, wire forms, add per-page meta tags + Open Graph, and point the domain.

---

## 10. V2 roadmap (post client feedback)

- [ ] Replace all placeholders with real resort photography
- [ ] Hero video / drone footage
- [ ] Real room pricing
- [ ] Wire reservation forms (Web3Forms)
- [ ] Full masonry gallery page with all extracted images
- [ ] Per-page SEO meta + schema.org (Resort / LodgingBusiness)
- [ ] Section-by-section refinement per client feedback

---

*Source content © Coco's Inn Resort by Spicy Mango. Design draft by Auspex Digital Marketing.*
