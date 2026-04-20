# Brand Extractor — Directive

## Goal
Extract comprehensive brand identity from any website using the Firecrawl API, then update `brand-guidelines/SKILL_brandguideline.md` with the results so the brand stays current.

## When to Use
- User wants to build a site "inspired by" or "similar to" another site
- User says "extract brand from X", "get colors / fonts / styles from X"
- User wants to update the brand guidelines with a new reference site
- User provides a URL and wants design tokens, typography, button styles, logo, hero images

## Inputs
| Variable | Description |
|----------|-------------|
| `TARGET_URL` | The website to scrape (e.g. `https://firecrawl.dev`) |
| `FIRECRAWL_API_KEY` | API key, stored in `.env` as `FIRECRAWL_API_KEY` |

## Tools / Scripts
- **Script:** `execution/extract_brand.py`
- **Output dir:** `.tmp/brand_<domain>/`
- **Key outputs:** `brand_raw.json`, `brand_report.md`, `screenshot.png`

## Credits Cost
~6 Firecrawl credits per run (1 base + 4 branding + 1 screenshot format).

---

## Step-by-Step SOP

### Step 1 — Verify API key
Check `.env` for `FIRECRAWL_API_KEY`. If missing, prompt the user or set it before running.

```bash
# Check key is set
grep FIRECRAWL_API_KEY .env
```

### Step 2 — Run the extractor
```bash
python execution/extract_brand.py <TARGET_URL>
```

This calls Firecrawl with formats: `branding`, `screenshot`, `markdown`, `images`.

Expected output in `.tmp/brand_<domain>/`:
- `brand_raw.json` — full API response
- `brand_report.md` — human-readable brand guide
- `screenshot.png` — full-page screenshot (if download succeeds; URL valid 24h)

### Step 3 — Review and extract key tokens
Read `brand_report.md` and identify:
- Primary, secondary, accent colors
- Typography: primary + heading fonts, sizes, weights
- Button styles (from `components.buttonPrimary` / `buttonSecondary`)
- Logo / hero image URLs
- Brand personality / tone

### Step 4 — Update brand-guidelines/SKILL_brandguideline.md
Append or replace the relevant section with the extracted brand data.
Structure:

```markdown
## [Brand Name] — Extracted Brand

> Source: <URL> | Extracted: <date>

### Colors
| Role | Hex |
...

### Typography
...

### Button Styles
...

### Logo & Hero Images
...

### CSS Design Tokens
...
```

If the brand guideline already has content for this URL, replace/update it rather than duplicating.

### Step 5 — Save hero images / screenshots to brand-guidelines/assets/
If there are hero images or logo URLs, note them in the guidelines. Download locally only if the user explicitly requests it (screenshot URLs expire in 24h).

---

## Error Handling

| Error | Fix |
|-------|-----|
| `401 Unauthorized` | Check `FIRECRAWL_API_KEY` in `.env` |
| `timeout` | Increase timeout or retry; some JS-heavy sites take 30-60s |
| `branding` key missing in response | Site may block headless browsers; try with `enhancedProxy: true` (add to payload in script) |
| `screenshot` empty | Normal — some sites block screenshots; proceed without it |
| Script errors on `requests` import | `pip install requests python-dotenv` |

---

## Known Behaviors & Learnings

- The `branding` format costs 4 extra credits (total ~5 per call) — worth it for comprehensive output
- `maxAge: 0` forces fresh scrape — remove if speed matters more than freshness
- Screenshot URLs expire after **24 hours** — save to disk immediately if you need them long-term
- Some sites return empty `colors` but full `typography` — still useful
- `images` format returns all `<img>` src URLs on the page — first few are usually hero/above-fold images

---

## Output Example (abbreviated)

```json
{
  "branding": {
    "colorScheme": "dark",
    "logo": "https://example.com/logo.svg",
    "colors": {
      "primary": "#E25822",
      "background": "#0F0F0F",
      "textPrimary": "#FFFFFF"
    },
    "fonts": [{"family": "Inter"}],
    "typography": {
      "fontFamilies": {"primary": "Inter", "heading": "Inter"},
      "fontSizes": {"h1": "56px", "body": "16px"}
    },
    "components": {
      "buttonPrimary": {"background": "#E25822", "textColor": "#FFF", "borderRadius": "8px"}
    }
  }
}
```
