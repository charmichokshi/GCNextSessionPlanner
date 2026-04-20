#!/usr/bin/env python3
"""
Brand Extractor — uses Firecrawl API to extract comprehensive brand identity
from any website. Outputs structured JSON + markdown report.

Usage:
    python execution/extract_brand.py <url> [--output-dir .tmp/brand_output]

Outputs (written to --output-dir):
    brand_raw.json      — raw API response
    brand_report.md     — human-readable brand guide
    screenshot.png      — screenshot URL (saved in JSON; downloaded if possible)

Credits used: ~6 per run (1 base + 4 branding + 1 screenshot)
"""

import argparse
import json
import os
import sys
import re
import urllib.parse
import urllib.request
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

# ---------------------------------------------------------------------------
# Load env
# ---------------------------------------------------------------------------
load_dotenv(Path(__file__).parent.parent / ".env")

API_KEY = os.getenv("FIRECRAWL_API_KEY", "")


# ---------------------------------------------------------------------------
# Firecrawl API call (no SDK dependency — pure stdlib + requests if available)
# ---------------------------------------------------------------------------

def call_firecrawl(url: str, api_key: str) -> dict:
    """Call Firecrawl /v2/scrape with branding + screenshot + markdown formats."""
    import json as _json

    endpoint = "https://api.firecrawl.dev/v2/scrape"
    payload = {
        "url": url,
        "formats": ["branding", "screenshot", "markdown", "images"],
        "maxAge": 0,          # always fresh
    }
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    # Try requests first, fall back to urllib
    try:
        import requests  # type: ignore
        resp = requests.post(endpoint, json=payload, headers=headers, timeout=120)
        resp.raise_for_status()
        return resp.json()
    except ImportError:
        pass

    # urllib fallback
    data = _json.dumps(payload).encode()
    req = urllib.request.Request(endpoint, data=data, headers=headers, method="POST")
    with urllib.request.urlopen(req, timeout=120) as resp:
        return _json.loads(resp.read())


# ---------------------------------------------------------------------------
# Markdown report generator
# ---------------------------------------------------------------------------

def build_report(url: str, raw: dict) -> str:
    """Turn the raw Firecrawl response into a rich Markdown brand report."""
    data = raw.get("data", {})
    branding = data.get("branding", {})
    metadata = data.get("metadata", {})
    screenshot_url = data.get("screenshot", "")
    images = data.get("images", [])

    domain = urllib.parse.urlparse(url).netloc
    now = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")

    lines = [
        f"# Brand Guidelines — {metadata.get('ogSiteName', domain)}",
        f"",
        f"> **Source URL:** {url}  ",
        f"> **Extracted at:** {now}  ",
        f"> **Color Scheme:** {branding.get('colorScheme', 'unknown')}",
        f"",
        f"---",
        f"",
    ]

    # ---- Logo / Images -------------------------------------------------------
    images_obj = branding.get("images", {})
    logo = branding.get("logo") or images_obj.get("logo", "")
    favicon = images_obj.get("favicon", "")
    og_image = images_obj.get("ogImage", "") or metadata.get("ogImage", "")

    lines += [
        f"## Brand Assets",
        f"",
    ]
    if logo:
        lines.append(f"**Logo:** `{logo}`  ")
        lines.append(f"![Logo]({logo})")
        lines.append("")
    if favicon:
        lines.append(f"**Favicon:** `{favicon}`  ")
        lines.append(f"![Favicon]({favicon})")
        lines.append("")
    if og_image:
        lines.append(f"**OG / Hero Image:** `{og_image}`  ")
        lines.append(f"![OG Image]({og_image})")
        lines.append("")
    if screenshot_url:
        lines.append(f"**Full-Page Screenshot:** `{screenshot_url}`  ")
        lines.append(f"![Screenshot]({screenshot_url})")
        lines.append("")

    # Additional images from page
    if images:
        lines += [
            "**All Images Found on Page:**",
            "",
        ]
        for img in images[:20]:  # cap at 20
            lines.append(f"- `{img}`")
        lines.append("")

    lines += ["---", ""]

    # ---- Colors --------------------------------------------------------------
    colors = branding.get("colors", {})
    if colors:
        lines += [
            "## Color Palette",
            "",
            "| Role | Hex |",
            "|------|-----|",
        ]
        for role, hex_val in colors.items():
            if hex_val:
                lines.append(f"| {role} | `{hex_val}` |")
        lines += ["", "### Hex Values (for CSS/design tools)", ""]
        for role, hex_val in colors.items():
            if hex_val:
                css_var = re.sub(r'(?<!^)(?=[A-Z])', '-', role).lower()
                lines.append(f"- `--color-{css_var}: {hex_val};`")
        lines += ["", "---", ""]

    # ---- Typography ----------------------------------------------------------
    typography = branding.get("typography", {})
    fonts = branding.get("fonts", [])

    if typography or fonts:
        lines += ["## Typography", ""]

        if fonts:
            lines.append("**Fonts Used:**")
            for f in fonts:
                lines.append(f"- {f.get('family', f)}")
            lines.append("")

        font_families = typography.get("fontFamilies", {})
        if font_families:
            lines += [
                "**Font Families:**",
                "",
                "| Role | Font |",
                "|------|------|",
            ]
            for role, family in font_families.items():
                if family:
                    lines.append(f"| {role} | `{family}` |")
            lines.append("")

        font_sizes = typography.get("fontSizes", {})
        if font_sizes:
            lines += [
                "**Font Sizes:**",
                "",
                "| Element | Size |",
                "|---------|------|",
            ]
            for el, size in font_sizes.items():
                if size:
                    lines.append(f"| {el} | `{size}` |")
            lines.append("")

        font_weights = typography.get("fontWeights", {})
        if font_weights:
            lines += [
                "**Font Weights:**",
                "",
                "| Weight Name | Value |",
                "|-------------|-------|",
            ]
            for name, val in font_weights.items():
                if val:
                    lines.append(f"| {name} | `{val}` |")
            lines.append("")

        line_heights = typography.get("lineHeights", {})
        if line_heights:
            lines += [
                "**Line Heights:**",
                "",
                "| Element | Value |",
                "|---------|-------|",
            ]
            for el, val in line_heights.items():
                if val:
                    lines.append(f"| {el} | `{val}` |")
            lines.append("")

        lines += ["---", ""]

    # ---- Spacing / Layout ----------------------------------------------------
    spacing = branding.get("spacing", {})
    layout = branding.get("layout", {})

    if spacing or layout:
        lines += ["## Spacing & Layout", ""]
        if spacing:
            for key, val in spacing.items():
                if val:
                    lines.append(f"- **{key}:** `{val}`")
        if layout:
            for key, val in layout.items():
                if val:
                    lines.append(f"- **{key}:** `{val}`")
        lines += ["", "---", ""]

    # ---- Components ----------------------------------------------------------
    components = branding.get("components", {})
    if components:
        lines += ["## UI Component Styles", ""]
        for comp_name, comp_val in components.items():
            lines.append(f"### {comp_name}")
            lines.append("")
            lines.append("```json")
            lines.append(json.dumps(comp_val, indent=2))
            lines.append("```")
            lines.append("")
        lines += ["---", ""]

    # ---- Icons ---------------------------------------------------------------
    icons = branding.get("icons", {})
    if icons:
        lines += ["## Icons", ""]
        for key, val in icons.items():
            lines.append(f"- **{key}:** `{val}`")
        lines += ["", "---", ""]

    # ---- Animations ----------------------------------------------------------
    animations = branding.get("animations", {})
    if animations:
        lines += ["## Animations & Transitions", ""]
        for key, val in animations.items():
            lines.append(f"- **{key}:** `{val}`")
        lines += ["", "---", ""]

    # ---- Personality ---------------------------------------------------------
    personality = branding.get("personality", {})
    if personality:
        lines += ["## Brand Personality", ""]
        for key, val in personality.items():
            if val:
                if isinstance(val, list):
                    lines.append(f"- **{key}:** {', '.join(val)}")
                else:
                    lines.append(f"- **{key}:** {val}")
        lines += ["", "---", ""]

    # ---- Metadata ------------------------------------------------------------
    if metadata:
        lines += [
            "## Page Metadata",
            "",
            f"- **Title:** {metadata.get('title', '')}",
            f"- **Description:** {metadata.get('description', '')}",
            f"- **OG Title:** {metadata.get('ogTitle', '')}",
            f"- **OG Description:** {metadata.get('ogDescription', '')}",
            f"- **Language:** {metadata.get('language', '')}",
            f"- **Keywords:** {metadata.get('keywords', '')}",
            "",
            "---",
            "",
        ]

    # ---- CSS Design Tokens (quick-start snippet) ----------------------------
    lines += [
        "## CSS Design Token Snippet",
        "",
        "```css",
        "/* Auto-generated brand tokens — paste into your :root {} */",
        ":root {",
    ]
    for role, hex_val in colors.items():
        if hex_val:
            css_var = re.sub(r'(?<!^)(?=[A-Z])', '-', role).lower()
            lines.append(f"  --color-{css_var}: {hex_val};")

    if font_families := typography.get("fontFamilies", {}):
        for role, family in font_families.items():
            if family:
                lines.append(f"  --font-{role}: '{family}', sans-serif;")

    if spacing:
        base = spacing.get("baseUnit")
        radius = spacing.get("borderRadius")
        if base:
            lines.append(f"  --spacing-base: {base}px;")
        if radius:
            lines.append(f"  --border-radius: {radius};")

    lines += ["}", "```", "", "---", ""]
    lines.append(f"*Report generated by `execution/extract_brand.py`*")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Extract brand identity from a website using Firecrawl.")
    parser.add_argument("url", help="Target URL to scrape")
    parser.add_argument("--output-dir", default=None, help="Directory to save outputs (default: .tmp/brand_<domain>)")
    parser.add_argument("--api-key", default=None, help="Firecrawl API key (overrides FIRECRAWL_API_KEY env var)")
    args = parser.parse_args()

    api_key = args.api_key or API_KEY
    if not api_key:
        print("ERROR: No Firecrawl API key found. Set FIRECRAWL_API_KEY in .env or pass --api-key.", file=sys.stderr)
        sys.exit(1)

    # Determine output dir
    domain = urllib.parse.urlparse(args.url).netloc.replace(".", "_").replace("-", "_")
    base_dir = Path(__file__).parent.parent
    out_dir = Path(args.output_dir) if args.output_dir else base_dir / ".tmp" / f"brand_{domain}"
    out_dir.mkdir(parents=True, exist_ok=True)

    print(f"🔥 Extracting brand from: {args.url}")
    print(f"   Output dir: {out_dir}")

    # Call Firecrawl
    print("   Calling Firecrawl API (formats: branding, screenshot, markdown, images)...")
    try:
        raw = call_firecrawl(args.url, api_key)
    except Exception as e:
        print(f"ERROR: Firecrawl API call failed: {e}", file=sys.stderr)
        sys.exit(1)

    if not raw.get("success"):
        print(f"ERROR: Firecrawl returned error: {raw}", file=sys.stderr)
        sys.exit(1)

    # Save raw JSON
    raw_path = out_dir / "brand_raw.json"
    with open(raw_path, "w") as f:
        json.dump(raw, f, indent=2)
    print(f"   ✔ Raw data saved: {raw_path}")

    # Build report
    report = build_report(args.url, raw)
    report_path = out_dir / "brand_report.md"
    with open(report_path, "w") as f:
        f.write(report)
    print(f"   ✔ Brand report saved: {report_path}")

    # Try downloading screenshot
    screenshot_url = raw.get("data", {}).get("screenshot", "")
    if screenshot_url:
        try:
            screenshot_path = out_dir / "screenshot.png"
            urllib.request.urlretrieve(screenshot_url, screenshot_path)
            print(f"   ✔ Screenshot saved: {screenshot_path}")
        except Exception as e:
            print(f"   ⚠ Could not download screenshot: {e}")

    print(f"\n✅ Done! Open {report_path} for the full brand report.")
    print(f"   Screenshot URL (valid 24h): {screenshot_url}")

    # Print summary
    branding = raw.get("data", {}).get("branding", {})
    colors = branding.get("colors", {})
    if colors:
        print("\n🎨 Color Palette:")
        for role, hex_val in colors.items():
            if hex_val:
                print(f"   {role:20s}  {hex_val}")

    fonts = branding.get("fonts", [])
    if fonts:
        print("\n🔤 Fonts:", ", ".join(f.get("family", str(f)) for f in fonts))


if __name__ == "__main__":
    main()
