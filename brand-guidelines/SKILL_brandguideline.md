---
name: brand-guidelines
description: Applies brand colors, typography, and design system tokens to any artifact that may benefit from a specific brand's look-and-feel. Use it when brand colors or style guidelines, visual formatting, company design standards apply, or when building a site "inspired by" another brand. Use the brand extractor directive (directives/brand_extractor.md) to add new brands. Currently includes: Anthropic, Firecrawl, Google Cloud Next 2026.
license: Complete terms in LICENSE.txt
---

# Brand Guidelines Library

## Overview

This library contains extracted brand identity reference data for multiple brands. Each section provides colors, typography, design tokens, hero images, and component styles — ready to use in designs, prototypes, or CSS stylesheets.

**To extract a new brand:** Run `python3 execution/extract_brand.py <URL>` — raw data goes to `.tmp/brand_<domain>/`. Then append a new section here following the template below.

**Keywords**: branding, corporate identity, visual identity, styling, brand colors, typography, design tokens, UI components, hero images, logos


## Google Cloud Next 2026 Brand

> **Event:** Google Cloud Next '26 — Las Vegas Conference  
> **Source URL:** https://www.googlecloudevents.com/next-vegas/  
> **Extracted:** 2026-04-10 via `execution/extract_brand.py`  
> **Color Scheme:** **Dark** (near-black background, light text on dark)  
> **Raw data:** `.tmp/brand_www_googlecloudevents_com/brand_raw.json`  
> **Screenshot:** `.tmp/brand_www_googlecloudevents_com/screenshot.png`

### Event Facts

| Field | Value |
|-------|-------|
| Event Name | Google Cloud Next 2026 |
| Dates | **April 22–24, 2026** |
| Venue | Mandalay Bay Convention Center, Las Vegas |
| Tagline | *"Where big ideas become a reality"* |
| Registration URL | https://www.googlecloudevents.com/next-vegas/fb-register |

### Brand Assets & Imagery

**All assets downloaded locally to:** `.tmp/brand_www_googlecloudevents_com/assets/`

| Asset | Local File | Source URL |
|-------|-----------|------------|
| Logo (SVG) | `assets/logo.svg` | `https://assets.swoogo.com/uploads/5760008-68c07a1922aca.svg` |
| Favicon | `assets/favicon.png` | `https://assets.swoogo.com/uploads/tiny/1727412-625da9ee7af9a.png` |
| OG / Hero Image (1920×1080) | `assets/hero_og.png` | `https://assets.swoogo.com/uploads/full/5991375-68f6a5a6729e8.png` |
| Hero backdrop (stage/crowd) | `assets/hero_stage.png` | `https://assets.swoogo.com/uploads/full/6552250-699ba23d147cf.png` |
| Hero animated GIF | `assets/hero_animated.gif` | `https://assets.swoogo.com/uploads/full/6143970-692dd7a15b322.gif` |
| Speaker section bg | `assets/speakers_bg.png` | `https://assets.swoogo.com/uploads/full/5954830-68ec4f8f1463c.png` |
| Community/connect section | `assets/community.png` | `https://assets.swoogo.com/uploads/full/5760640-68c08db931fbe.png` |
| Keynotes badge icon (SVG) | `assets/keynotes_icon.svg` | `https://assets.swoogo.com/uploads/5429372-684280803a503.svg` |
| Next at Night concert | `assets/next_at_night.png` | `https://assets.swoogo.com/uploads/full/6778133-69cd51d6c9d0d.png` |
| Networking/community | `assets/networking.png` | `https://assets.swoogo.com/uploads/full/5944492-68e7ea067e960.png` |
| Expo demo (animated GIF) | `assets/expo_demo.gif` | `https://assets.swoogo.com/uploads/full/6535656-6996508fde121.gif` |

**Luminary Sponsor logos (white SVGs):**
- Accenture, Capgemini, Cognizant, Deloitte, NVIDIA, Palo Alto Networks


### Color Palette

| Role | Hex | Usage |
|------|-----|-------|
| Primary | `#AECBFA` | Light blue — primary text highlights, headings on dark bg |
| Secondary | `#0D6EFD` | Bright blue — strong CTA, button fills |
| Accent | `#4285F4` | Google Blue — links, interactive elements |
| Background | `#010101` | Near-black — full-page dark mode canvas |
| Text Primary | `#FFFFFF` / `#AECBFA` | White/light-blue on dark backgrounds |
| Link | `#4285F4` | Google Blue hyperlinks |

**Expanded palette (inferred from Google Cloud design system + page):**

| Role | Hex | Notes |
|------|-----|-------|
| Surface dark | `#0D0D0D` | Card backgrounds |
| Surface medium | `#1A1A2E` | Section dividers, elevated surfaces |
| Google Blue | `#4285F4` | Core Google brand blue |
| Google Blue light | `#AECBFA` | Used for large headings in dark mode |
| Google Blue vivid | `#0D6EFD` | High-contrast CTA buttons |
| White | `#FFFFFF` | Body copy on dark bg |
| Muted text | `#9AA0A6` | Captions, metadata |

**Key insight:** This is a **Google Blue** brand with a theatrical dark-mode treatment. The pale blue `#AECBFA` on near-black `#010101` creates an electric, cosmic feel suited for a major tech event.

**CSS Custom Properties:**
```css
:root {
  --color-primary: #AECBFA;
  --color-secondary: #0D6EFD;
  --color-accent: #4285F4;
  --color-background: #010101;
  --color-surface: #0D0D0D;
  --color-surface-elevated: #1A1A2E;
  --color-text-primary: #FFFFFF;
  --color-text-secondary: #9AA0A6;
  --color-link: #4285F4;
  --color-google-blue: #4285F4;
  --color-google-blue-light: #AECBFA;
}
```

### Typography

**Primary Font:** `Google Sans` — Google's proprietary humanist sans-serif  
**Heading Font:** `Google Sans Display` — Display weight for large headings  
**Fallback:** `Arial`, `Helvetica`, `sans-serif`

| Role | Font | Fallback |
|------|------|---------|
| Body / UI | `Google Sans` | `Arial, Helvetica, sans-serif` |
| Large Headings | `Google Sans Display` | `sans-serif` |

**Font Sizes (very large — epic event scale):**

| Element | Size | Notes |
|---------|------|-------|
| H1 | `96px` | Massive hero headline |
| H2 | `72px` | Section headings |
| Body | `20px` | Generous, readable body text |

**Design note:** Headings are extremely large (96px) for maximum visual impact — befitting a major 3-day conference event. This creates a "stadium-scale" typographic presence.

**Open-source substitute for Google Sans:**
```css
@import url('https://fonts.googleapis.com/css2?family=Google+Sans:wght@400;500;700&display=swap');
/* Or if unavailable, use: */
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;700&display=swap');

:root {
  --font-primary: 'Google Sans', 'DM Sans', Arial, sans-serif;
  --font-heading: 'Google Sans Display', 'Google Sans', 'DM Sans', sans-serif;
}
```

> **Note:** Google Sans is available via Google Fonts for some weights. `DM Sans` is a close open-source alternative.

### Spacing & Layout

| Property | Value |
|----------|-------|
| Base unit | `4px` |
| Border radius | `16px` (rounded cards — much rounder than Firecrawl) |

**Spacing scale:**
```css
:root {
  --spacing-1: 4px;
  --spacing-2: 8px;
  --spacing-4: 16px;
  --spacing-6: 24px;
  --spacing-8: 32px;
  --spacing-12: 48px;
  --spacing-16: 64px;
  --spacing-24: 96px;
  --border-radius-sm: 8px;
  --border-radius: 16px;
  --border-radius-lg: 24px;
}
```

### UI Component Styles

Inferred from Google's Material Design 3 + event page visual patterns:

#### Primary CTA Button ("Register now")
```css
.btn-primary {
  background: #4285F4;       /* Google Blue */
  color: #FFFFFF;
  border: none;
  border-radius: 24px;        /* Pill-shaped — Google's event style */
  font-family: 'Google Sans', sans-serif;
  font-weight: 500;
  font-size: 16px;
  padding: 12px 28px;
  letter-spacing: 0.01em;
  cursor: pointer;
  transition: background 0.2s ease, box-shadow 0.2s ease;
}
.btn-primary:hover {
  background: #1A73E8;
  box-shadow: 0 4px 16px rgba(66, 133, 244, 0.4);
}
```

#### Secondary / Outline Button ("View pricing")
```css
.btn-secondary {
  background: transparent;
  color: #AECBFA;
  border: 1.5px solid #AECBFA;
  border-radius: 24px;
  font-family: 'Google Sans', sans-serif;
  font-weight: 500;
  font-size: 16px;
  padding: 12px 28px;
  cursor: pointer;
  transition: all 0.2s ease;
}
.btn-secondary:hover {
  background: rgba(174, 203, 250, 0.1);
}
```

#### Card / Panel
```css
.card {
  background: #0D0D0D;
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 16px;
  padding: 32px;
}
```

### Brand Personality & Tone

| Attribute | Value |
|-----------|-------|
| Tone | Professional, aspirational, inclusive |
| Energy | High — major annual conference, concert events |
| Target Audience | Cloud engineers, enterprise architects, AI/ML developers, CTOs, startup founders |
| Voice | Bold, inspiring, technically credible |

**Key messages observed:**
- *"Where big ideas become a reality"* — aspirational
- *"Stay ahead of the curve"* — urgency, innovation
- *"Connect with innovators"* — community
- *"Dive into your favorite topics"* — breadth

### Event Page Structure (for building similar event sites)

Extracted from page content analysis:

1. **Top Nav** — event logo left, nav links (Plan Your Trip, Agentic AI, Session Library, Speakers, etc.), Sign In + Register CTA right
2. **Hero** — Full-bleed animated GIF/video backdrop, event dates + venue in `<h5>`, huge `<h1>` tagline, dual CTAs (Register Now + View Pricing)
3. **Three value props** — Grid: "Stay ahead / Connect / Dive in" with short descriptions + links
4. **Entertainment section** — "Next at Night" concert promo (Benson Boone + Weezer), Allegiant Stadium callout
5. **Featured Speakers** — Grid of speaker cards
6. **Agenda** — Tabbed by day (Tue–Fri), time-slot blocks
7. **Session Guide** — Category grid: Keynotes, Spotlights, Breakouts, Lightning Talks, Workshops, etc. with icons + capacity info
8. **Pricing / Ticket tiers** — Tiered early-bird pricing ($999 → $1,599 → $2,299)
9. **Luminary Sponsors** — Horizontal logo bar: Accenture, Capgemini, Cognizant, Deloitte, NVIDIA, Palo Alto Networks
10. **CTA Footer** — "Plan your trip" link + Google Cloud logo

### Session Types Reference

| Type | Duration | Format | Notes |
|------|----------|--------|-------|
| Keynotes | 60–90 min | Main Stage | Google execs + industry luminaries |
| Spotlights | 45 min | Spotlight stages | Partner + customer stories |
| Breakouts | 45 min | Breakout rooms | Deep-dive, Q&A included |
| Lightning Talks | 20 min | Expo/Dev Theater | Single use case, quick takeaways |
| Solution Talks | 45 min | Interactive | Architecture-focused, medium capacity |
| Skills Zone Workshops | 45 min | Hands-on | Dev-focused, with Google instructors |
| Showcase Demos | Open | Expo floor | Self-paced experiential demos |
| Discussion Groups | 30 min | Small group | Led by experts |
| Developer Meetup | Varies | Small capacity | Developer community networking |
| Birds of a Feather | 30 min | Lunch Café | Role/industry informal hangout |
| Lounge Sessions | 30 min | Community Lounge | Casual expert chats |

### Full CSS Design Token Snippet

```css
/* Google Cloud Next 2026 Brand Tokens — auto-extracted 2026-04-10 */
:root {
  /* Colors — Dark Mode */
  --color-background: #010101;
  --color-surface: #0D0D0D;
  --color-surface-elevated: #1A1A2E;
  --color-primary: #AECBFA;            /* Light blue — headings */
  --color-secondary: #0D6EFD;          /* Bright blue — CTAs */
  --color-accent: #4285F4;             /* Google Blue — links/interactive */
  --color-text-primary: #FFFFFF;
  --color-text-secondary: #9AA0A6;
  --color-link: #4285F4;
  --color-border: rgba(255, 255, 255, 0.08);

  /* Typography */
  --font-primary: 'Google Sans', 'DM Sans', Arial, sans-serif;
  --font-heading: 'Google Sans Display', 'Google Sans', sans-serif;

  /* Font Sizes */
  --text-hero: 96px;
  --text-h1: 96px;
  --text-h2: 72px;
  --text-h3: 40px;
  --text-h4: 28px;
  --text-body: 20px;
  --text-small: 16px;
  --text-caption: 14px;

  /* Spacing (4px base unit) */
  --spacing-1: 4px;
  --spacing-2: 8px;
  --spacing-4: 16px;
  --spacing-6: 24px;
  --spacing-8: 32px;
  --spacing-12: 48px;
  --spacing-16: 64px;
  --spacing-24: 96px;

  /* Borders */
  --border-radius-sm: 8px;
  --border-radius: 16px;
  --border-radius-pill: 24px;
  --border-radius-lg: 32px;
}
```

### Brand Inspiration Summary — Building a GC Next–Inspired Site

- **Dark mode is mandatory** — near-black `#010101` base, never pure black
- **Google Blue** (`#4285F4`) is the hero color — use for interaction, not decoration
- **Pale blue** (`#AECBFA`) for stunning large headings on dark — the "wow" color
- **Font: Google Sans** — rounded, warm, humanist. Use `DM Sans` if Google Sans unavailable
- **Go huge with typography** — H1 at 96px signals scale and importance
- **Pill buttons** (border-radius: 24px) — soft, approachable CTAs
- **Rounded cards** (16px radius) — warmer than sharp Material 2 corners
- **Animated/video hero** — GIFs and video backgrounds are central to the event vibe
- **Section-by-section content depth** — each section has a purpose: inspire → connect → learn → register
- **Sponsor logos** in white on dark — always a horizontal bar
- Keep content **aspirational but data-grounded**: agenda slots, pricing tiers, session counts