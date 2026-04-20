#!/usr/bin/env python3
"""
score_sessions.py — ONE-TIME session scoring for GC Next '26 Planner
=====================================================================
Run ONCE to score all 925 sessions, optionally enrich with Claude,
and rebuild planner.html with the scored data inlined.

Usage:
    python3 execution/score_sessions.py
    python3 execution/score_sessions.py --api-key sk-ant-...
    python3 execution/score_sessions.py --no-enrich        # deterministic only, no Claude
    python3 execution/score_sessions.py --no-rebuild-html  # skip HTML rebuild

Outputs:
    session_library/sessions_scored.json   ← scored + enriched session data
    planner.html                           ← rebuilt with SCORED_DATA inlined
"""

import json
import os
import re
import sys
import argparse
import math
from pathlib import Path
from datetime import datetime

# ── Optional: use requests for Claude API call ────────────────────────────────
try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False

# ── Paths ─────────────────────────────────────────────────────────────────────
ROOT         = Path(__file__).parent.parent
SESSIONS_IN  = ROOT / "session_library" / "sessions_data.json"
SESSIONS_OUT = ROOT / "session_library" / "sessions_scored.json"
PLANNER_HTML = ROOT / "planner.html"
ENV_FILE     = ROOT / ".env"

# ── Load .env ─────────────────────────────────────────────────────────────────
def load_env():
    env = {}
    if ENV_FILE.exists():
        for line in ENV_FILE.read_text().splitlines():
            line = line.strip()
            if line and "=" in line and not line.startswith("#"):
                k, v = line.split("=", 1)
                env[k.strip()] = v.strip()
    return env

# ── USER PROFILE (must mirror what planner.html uses) ────────────────────────
INTEREST_KEYWORDS = [
    "agent", "agentic", "multi-agent", "multiagent",
    "vertex", "gemini", "adk", "agent development kit",
    "mcp", "model context protocol",
    "llm", "large language model", "generative ai", "genai",
    "langchain", "rag", "retrieval", "embedding",
    "foundation model", "fine-tun", "prompt engineering",
    "inference", "production", "deployment",
    "cloud native", "developer productivity",
    "startup", "founder", "venture", "entrepreneur",
    "networking", "community", "a2a", "agent2agent",
    "multimodal", "reasoning model",
]

TYPE_BASE = {
    "Keynotes":          3.5,
    "Workshops":         3.0,
    "Discussion Groups": 2.5,
    "Breakouts":         2.0,
    "Solution Talks":    1.8,
    "Spotlights":        1.5,
    "Developer Meetups": 1.2,
    "Birds of a Feather":1.0,
    "Lounge Sessions":   0.8,
    "Lightning Talks":   0.6,
    "Capture the Flag":  0.2,
}

LEVEL_BONUS = {
    "Advanced Technical": 2.0,
    "Technical":          1.8,
    "General":            1.0,
    "Introductory":      -0.5,
    "":                   0.5,
}

TAG_MAP = {
    "#GenAI":       ["genai", "generative ai", "llm", "large language model", "foundation model"],
    "#Agents":      ["agent", "agentic", "multi-agent", "multiagent", "a2a", "agent2agent"],
    "#VertexAI":    ["vertex"],
    "#Gemini":      ["gemini"],
    "#ADK":         ["adk", "agent development kit"],
    "#MCP":         ["mcp", "model context protocol"],
    "#RAG":         ["rag", "retrieval-augmented", "retrieval augmented"],
    "#MLOps":       ["mlops", "deployment", "production", "inference", "fine-tun"],
    "#Startup":     ["startup", "founder", "entrepreneurship", "venture", "$"],
    "#Networking":  ["networking", "community", "meetup", "connect"],
    "#Workshop":    ["workshop", "hands-on", "lab"],
    "#Keynote":     ["keynote"],
    "#CloudNative": ["kubernetes", "cloud native", "container", "gke", "cloud run"],
    "#Security":    ["security", "vulnerability", "zero trust", "ctf"],
    "#Multimodal":  ["multimodal", "vision", "audio", "video generation", "imagen", "veo"],
}


def score_session(s: dict) -> float:
    """Deterministic relevance score (0–10) for USER_PROFILE."""
    score = 5.0

    # Session type base score
    score += TYPE_BASE.get(s.get("session_type", ""), 0.5)

    # Level bonus
    score += LEVEL_BONUS.get(s.get("level", ""), 0.3)

    # Keyword match in name + description + topics
    name = (s.get("name") or "").lower()
    desc = (s.get("description") or "").lower()
    topics_text = " ".join(s.get("topics") or []).lower()
    full_text = f"{name} {desc} {topics_text}"

    matched_kws = sum(1 for kw in INTEREST_KEYWORDS if kw in full_text)
    score += min(matched_kws * 0.35, 2.0)

    # Topic bonus (explicit topic match)
    for topic in (s.get("topics") or []):
        tl = topic.lower()
        if any(kw in tl for kw in ["agent", "vertex", "gemini", "adk", "mcp", "llm", "genai", "ml"]):
            score += 0.4

    # Registrant count bonus (log scale — social proof)
    try:
        rc = int(s.get("registrantCount") or 0)
        if rc > 0:
            score += min(math.log10(rc) * 0.6, 2.0)
    except (ValueError, TypeError):
        pass

    # Penalise sessions with no capacity (full / restricted)
    rc_cap = s.get("remaining_capacity")
    if rc_cap is not None:
        try:
            if int(rc_cap) == 0:
                score -= 0.3
        except (ValueError, TypeError):
            pass

    return round(min(max(score, 1.0), 10.0), 2)


def compute_tags(s: dict) -> list:
    """Compute relevant hashtag labels for a session."""
    tags = []
    name = (s.get("name") or "").lower()
    desc = (s.get("description") or "").lower()
    topics_text = " ".join(s.get("topics") or []).lower()
    stype = s.get("session_type", "")
    full = f"{name} {desc} {topics_text}"

    for tag, keywords in TAG_MAP.items():
        if any(kw in full for kw in keywords):
            tags.append(tag)

    # Session-type derived tags
    if "Keynote" in stype and "#Keynote" not in tags:
        tags.insert(0, "#Keynote")
    if "Workshop" in stype and "#Workshop" not in tags:
        tags.append("#Workshop")

    return tags[:5]


# ── Topic → benefit phrase map for deterministic _why generation ──────────────
WHY_PHRASES = {
    "agent":            "directly advances your agentic AI expertise",
    "adk":              "covers ADK — your primary build framework",
    "mcp":              "unpacks MCP, the standard you're actively building on",
    "model context protocol": "deep-dives the MCP spec and real-world tooling",
    "vertex":           "expands your Vertex AI production skills",
    "gemini":           "showcases latest Gemini capabilities and APIs",
    "multi-agent":      "tackles multi-agent coordination patterns you can apply immediately",
    "llm":              "covers LLM architecture relevant to your production deployments",
    "rag":              "explores RAG patterns for grounding your AI apps",
    "production":       "addresses real-world deployment challenges you face",
    "inference":        "covers inference optimization critical for cost-efficient LLM apps",
    "startup":          "surfaces startup and side-income angles aligned to your goals",
    "founder":          "connects you with founders building in the AI space",
    "networking":       "prime networking opportunity with peers and Google engineers",
    "community":        "connects you with the broader GDE and developer community",
    "developer productivity": "directly improves your AI-assisted dev workflow",
    "generative ai":    "covers GenAI fundamentals and emerging patterns",
    "genai":            "packed with GenAI product updates and use cases",
    "multimodal":       "explores multimodal AI — a skill gap worth closing",
    "cloud native":     "reinforces cloud-native best practices for AI workloads",
    "fine-tun":         "covers fine-tuning techniques to customise models for your use cases",
    "embedding":        "dives into embeddings and vector search for smarter retrieval",
    "deployment":       "practical deployment patterns for production AI systems",
    "a2a":              "introduces Agent-to-Agent (A2A) protocol — the next interop standard",
}

TYPE_WHY = {
    "Keynotes":          "Major announcements and product direction straight from Google leadership.",
    "Workshops":         "Hands-on session — you'll leave with working code you can use.",
    "Discussion Groups": "Small-group deep dive; rare chance to have a direct conversation with the experts.",
    "Birds of a Feather":"Peer exchange with practitioners solving the same problems you are.",
    "Developer Meetups": "Community networking with builders — great for making GDE connections.",
    "Solution Talks":    "Whiteboard-level architecture walkthrough from practitioners.",
    "Spotlights":        "Curated spotlight on a high-signal partner or customer story.",
}

LEVEL_WHY = {
    "Advanced Technical": "Pitched at experts — no hand-holding, direct to implementation detail.",
    "Technical":          "Technical depth with real code and architecture decisions.",
    "General":            "Strategic overview — good for connecting dots across tracks.",
}


def generate_why(s: dict) -> str:
    """Generate a deterministic 1-2 sentence 'why attend' for each session."""
    name = (s.get("name") or "").lower()
    desc = (s.get("description") or "").lower()
    topics = [t.lower() for t in (s.get("topics") or [])]
    stype  = s.get("session_type", "")
    level  = s.get("level", "")
    full   = f"{name} {desc} {' '.join(topics)}"

    # Find first matching topic phrase
    topic_hit = ""
    for kw, phrase in WHY_PHRASES.items():
        if kw in full:
            topic_hit = phrase
            break

    # Session type sentence
    type_sent  = TYPE_WHY.get(stype, "")
    level_sent = LEVEL_WHY.get(level, "")

    # Lead speakers
    speakers = s.get("speakers") or []
    speaker_str = ""
    notable_orgs = ["Google", "Anthropic", "DeepMind", "OpenAI", "Shopify", "Stripe", "Spotify"]
    for sp in speakers[:2]:
        co = sp.get("company", "")
        if any(org.lower() in co.lower() for org in notable_orgs):
            speaker_str = f" Speaker from {co}."
            break

    # Registrant social-proof
    try:
        rc = int(s.get("registrantCount") or 0)
        popularity = f" ({rc:,} people registered — high demand.)" if rc > 2000 else ""
    except (ValueError, TypeError):
        popularity = ""

    # Compose sentence
    if topic_hit:
        sentence1 = f"This session {topic_hit}."
    elif type_sent:
        sentence1 = type_sent
    else:
        sentence1 = "Relevant to your AI and cloud expertise."

    # Second sentence: type or level hint
    sentence2 = ""
    if type_sent and topic_hit:
        sentence2 = " " + type_sent
    elif level_sent and not type_sent:
        sentence2 = " " + level_sent

    return (sentence1 + sentence2 + speaker_str + popularity).strip()


def enrich_with_claude(api_key: str, top_sessions: list) -> dict:
    """
    Call Claude once with top-N sessions → return why_for_you map + insights.
    Returns: {"why_map": {id: str}, "insights": {...}}
    """
    if not HAS_REQUESTS:
        print("   ⚠️  'requests' package not installed. Run: pip3 install requests")
        return {"why_map": {}, "insights": None}

    trimmed = [
        {
            "id": s["id"],
            "name": s["name"],
            "session_type": s.get("session_type", ""),
            "level": s.get("level", ""),
            "topics": s.get("topics", []),
            "description": (s.get("description") or "")[:200],
            "_score": s["_score"],
        }
        for s in top_sessions
    ]

    prompt = f"""You are helping a Google Developer Expert (GDE) in AI plan Google Cloud Next '26.

USER PROFILE:
- Role: AI Project Manager, GDE in AI & Google Cloud Platform
- Interests: AI Agents, ADK, Vertex AI, Gemini, MCP, LLM production deployment, startup ideas, networking
- Goals: Learn agentic AI, discover side income, network with Google engineers and founders
- Preferred levels: Technical, Advanced Technical, General

For EACH session below, write ONE concise sentence "why_for_you" (max 25 words) explaining why it matches this GDE.

SESSIONS ({len(trimmed)} total):
{json.dumps(trimmed, indent=2)}

Also provide:
- 3 top conference trends (1 sentence each)
- 3 actionable side income ideas this GDE could start post-conference
- 1 concrete post-event project to build within 30 days

RESPOND WITH ONLY VALID JSON — no markdown, no explanation:
{{
  "enrichments": [
    {{"id": "session_id_string", "why_for_you": "One sentence max 25 words."}}
  ],
  "insights": {{
    "top_trends": ["trend 1", "trend 2", "trend 3"],
    "side_income_ideas": ["idea 1", "idea 2", "idea 3"],
    "project_idea": "Concrete 30-day project description."
  }}
}}"""

    try:
        resp = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "Content-Type": "application/json",
                "x-api-key": api_key,
                "anthropic-version": "2023-06-01",
            },
            json={
                "model": "claude-opus-4-5",
                "max_tokens": 8000,
                "system": "You are a conference schedule optimizer. Respond with valid JSON only. No markdown.",
                "messages": [{"role": "user", "content": prompt}],
            },
            timeout=180,
        )
        resp.raise_for_status()
        raw = resp.json()["content"][0]["text"]
        raw = re.sub(r"```json\s*|```", "", raw).strip()
        result = json.loads(raw)
        why_map = {e["id"]: e.get("why_for_you", "") for e in result.get("enrichments", [])}
        print(f"   ✅ Claude enriched {len(why_map)} sessions.")
        return {"why_map": why_map, "insights": result.get("insights")}
    except Exception as e:
        print(f"   ⚠️  Claude enrichment failed: {e}")
        return {"why_map": {}, "insights": None}


def rebuild_planner_html(sessions: list, insights: dict, dry_run: bool = False):
    """
    Replace SCORED_DATA + PREBUILT_INSIGHTS in planner.html.
    The script looks for sentinel comments to do a clean replacement.
    """
    if not PLANNER_HTML.exists():
        print(f"   ⚠️  {PLANNER_HTML} not found, skipping HTML rebuild.")
        return

    # Build lean scored list (only fields the UI needs)
    lean = []
    for s in sessions:
        lean.append({
            "id":                 s.get("id", ""),
            "name":               s.get("name", ""),
            "date":               s.get("date", ""),
            "start_time":         s.get("start_time", ""),
            "end_time":           s.get("end_time", ""),
            "session_type":       s.get("session_type", ""),
            "level":              s.get("level", ""),
            "topics":             s.get("topics") or [],
            "description":        (s.get("description") or "")[:300],
            "registrantCount":    s.get("registrantCount", "0"),
            "location_id":        s.get("location_id", ""),
            "session_code":       s.get("session_code", ""),
            "moreInfoUrl":        s.get("moreInfoUrl", ""),
            "remaining_capacity": s.get("remaining_capacity", 1),
            "speakers": [
                {
                    "fullName": sp.get("fullName", ""),
                    "jobTitle": sp.get("jobTitle", ""),
                    "company":  sp.get("company", ""),
                }
                for sp in (s.get("speakers") or [])
            ],
            "_score": s.get("_score", 5.0),
            "_tags":  s.get("_tags", []),
            "_why":   s.get("_why", ""),
        })

    scored_json   = json.dumps(lean, ensure_ascii=False, separators=(",", ":"))
    insights_json = json.dumps(insights, ensure_ascii=False) if insights else "null"

    html = PLANNER_HTML.read_text(encoding="utf-8")

    # Strategy 1 – replace between sentinel comments (after first rebuild)
    sentinel_re = re.compile(
        r"// ──SCORED_DATA_START──\s*\n\s*const SCORED_DATA = [\s\S]*?// ──SCORED_DATA_END──",
        re.MULTILINE,
    )
    sentinel_insights_re = re.compile(
        r"// ──INSIGHTS_START──\s*\n\s*const PREBUILT_INSIGHTS = [\s\S]*?// ──INSIGHTS_END──",
        re.MULTILINE,
    )

    new_scored_block = (
        f"// ──SCORED_DATA_START──\n"
        f"    const SCORED_DATA = {scored_json};\n"
        f"    // ──SCORED_DATA_END──"
    )
    new_insights_block = (
        f"// ──INSIGHTS_START──\n"
        f"    const PREBUILT_INSIGHTS = {insights_json};\n"
        f"    // ──INSIGHTS_END──"
    )

    if sentinel_re.search(html):
        html = sentinel_re.sub(new_scored_block, html)
        html = sentinel_insights_re.sub(new_insights_block, html)
        print("   ✅ Sentinel replacement done.")
    else:
        # Strategy 2 – replace original SESSION_DATA line (first run)
        old_marker = "// ── SESSION DATA (inline) ──────────────────────────────────────────────────"
        if old_marker in html:
            insert = (
                f"// ── SCORED DATA (pre-computed by execution/score_sessions.py) ───────────────\n"
                f"    {new_scored_block}\n\n"
                f"    {new_insights_block}\n\n"
                f"    {old_marker}"
            )
            html = html.replace(old_marker, insert, 1)
            print("   ✅ Inserted SCORED_DATA before SESSION_DATA marker.")
        else:
            # Strategy 3 – find the SESSION_DATA const and insert before it
            match = re.search(r"(const SESSION_DATA = \[)", html)
            if match:
                pos = match.start()
                html = (
                    html[:pos]
                    + f"{new_scored_block}\n\n    {new_insights_block}\n\n    "
                    + html[pos:]
                )
                print("   ✅ Inserted SCORED_DATA before SESSION_DATA const.")
            else:
                print("   ⚠️  Could not locate SESSION_DATA in planner.html. Skipping HTML rebuild.")
                return

    if dry_run:
        print(f"   [DRY RUN] Would write {len(html):,} chars to {PLANNER_HTML}")
    else:
        PLANNER_HTML.write_text(html, encoding="utf-8")
        print(f"   ✅ planner.html updated ({len(html)//1024} KB).")


def main():
    parser = argparse.ArgumentParser(
        description="One-time scoring for GC Next '26 sessions.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("--api-key",        help="Anthropic API key (or set ANTHROPIC_API_KEY in .env)")
    parser.add_argument("--no-enrich",      action="store_true", help="Skip Claude enrichment")
    parser.add_argument("--no-rebuild-html",action="store_true", help="Skip rebuilding planner.html")
    parser.add_argument("--enrich-top",     type=int, default=60,  help="How many top sessions to enrich (default 60)")
    parser.add_argument("--dry-run",        action="store_true", help="Don't write files, just print")
    args = parser.parse_args()

    env      = load_env()
    api_key  = args.api_key or env.get("ANTHROPIC_API_KEY")

    # ── 1. Load sessions ──────────────────────────────────────────────────────
    print(f"\n📂  Loading {SESSIONS_IN.name}...")
    sessions = json.loads(SESSIONS_IN.read_text(encoding="utf-8"))
    print(f"    {len(sessions)} sessions loaded.")

    # ── 2. Deterministic scoring ──────────────────────────────────────────────
    print("\n⚙️   Computing deterministic scores...")
    for s in sessions:
        s["_score"] = score_session(s)
        s["_tags"]  = compute_tags(s)
        s["_why"]   = generate_why(s)  # deterministic baseline; overridden by Claude if --api-key

    sessions.sort(key=lambda s: s["_score"], reverse=True)
    print(f"    Done. Top 5:")
    for s in sessions[:5]:
        print(f"      [{s['_score']:.1f}] {s['name'][:70]}")

    # ── 3. Claude enrichment (optional) ──────────────────────────────────────
    insights = None
    if args.no_enrich:
        print("\n⏭️   Skipping Claude enrichment (--no-enrich).")
    elif not api_key:
        print("\n⚠️   No ANTHROPIC_API_KEY found in .env or --api-key arg.")
        print("    Skipping Claude enrichment. Scores are deterministic only.")
        print("    Add key to .env as: ANTHROPIC_API_KEY=sk-ant-...")
    else:
        top_n = sessions[:args.enrich_top]
        print(f"\n🤖  Enriching top {len(top_n)} sessions with Claude...")
        enrichment = enrich_with_claude(api_key, top_n)
        why_map = enrichment["why_map"]
        insights = enrichment["insights"]
        for s in sessions:
            if s["id"] in why_map:
                s["_why"] = why_map[s["id"]]

    # ── 4. Save sessions_scored.json ──────────────────────────────────────────
    output = {
        "_meta": {
            "generated_at":   datetime.utcnow().isoformat() + "Z",
            "total_sessions": len(sessions),
            "enriched":       bool(api_key and not args.no_enrich),
            "script":         "execution/score_sessions.py",
        },
        "insights":  insights,
        "sessions":  sessions,
    }
    if args.dry_run:
        print(f"\n[DRY RUN] Would write {len(sessions)} sessions to {SESSIONS_OUT}")
    else:
        SESSIONS_OUT.write_text(json.dumps(output, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"\n✅  Saved {len(sessions)} scored sessions → {SESSIONS_OUT.name}")

    # ── 5. Rebuild planner.html ───────────────────────────────────────────────
    if not args.no_rebuild_html:
        print(f"\n🔧  Rebuilding planner.html with scored data...")
        rebuild_planner_html(sessions, insights, dry_run=args.dry_run)
    else:
        print("\n⏭️   Skipping HTML rebuild (--no-rebuild-html).")

    print("\n🎉  Done! Open planner.html in a browser — no API key needed.")


if __name__ == "__main__":
    main()
