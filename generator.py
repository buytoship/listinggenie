"""
ListingGenie core generator.

Design: open-weight model first, deterministic fallback second.
- If a local Ollama server is running (http://localhost:11434), we ask an
  open-weight model (default: gemma3:4b, override with LISTINGGENIE_MODEL)
  to draft the listing, then post-process it into platform constraints.
- If Ollama is not available, a rule-based generator produces the same
  structure so the demo always works with zero setup and zero API cost.
"""
import json
import os
import re
import urllib.request

OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://localhost:11434")
MODEL = os.environ.get("LISTINGGENIE_MODEL", "gemma3:4b")

TITLE_LIMIT = {"etsy": 140, "ebay": 140}
TAG_LIMIT_ETS = 13
TAG_CHAR_LIMIT = 20


def _clean_words(text):
    return [w.strip(" ,.;:").lower() for w in re.split(r"\s+", text or "") if w.strip()]


def _title_case(text):
    return " ".join(w.capitalize() for w in text.split())


def build_titles(product):
    name = product["name"].strip()
    kws = [k.strip() for k in product.get("keywords", []) if k.strip()]
    platform = product.get("platform", "etsy")
    limit = TITLE_LIMIT.get(platform, 140)
    audience = product.get("audience", "").strip()
    fmt = product.get("format", "").strip()

    seeds = []
    if kws:
        seeds.append(", ".join([name] + kws[:3]))
    if audience:
        seeds.append(f"{name} for {audience}")
    base = name + (f", {fmt}" if fmt else "") + (f", {kws[0]}" if kws else "")
    seeds.append(base)
    seeds.append(", ".join(dict.fromkeys([name] + kws + ([fmt] if fmt else []))))

    titles, seen = [], set()
    for s in seeds:
        t = s[:limit].rstrip(", ")
        if t and t.lower() not in seen:
            seen.add(t.lower())
            titles.append({"title": t, "chars": len(t)})
    return titles[:3]


def build_tags(product):
    raw = []
    raw += product.get("keywords", [])
    raw.append(product["name"])
    raw.append(product.get("category", ""))
    raw.append(product.get("format", ""))
    raw += ["digital download", "instant download", "printable", "digital product"]
    tags, seen = [], set()

    def _add(cand):
        t = re.sub(r"\s+", " ", re.sub(r"[^a-z0-9 &+-]", " ", cand.strip().lower()))
        t = t[:TAG_CHAR_LIMIT].strip()
        if t and t not in seen and len(t) >= 3:
            seen.add(t)
            tags.append(t)

    for item in raw:  # full phrases first — they carry the search intent
        _add(item)
        if len(tags) >= TAG_LIMIT_ETS:
            return tags
    for item in raw:  # then single words to fill any remaining slots
        for p in re.split(r"\s+", item):
            if len(p) > 3:
                _add(p)
            if len(tags) >= TAG_LIMIT_ETS:
                return tags
    return tags


def build_description(product, ai_text=None):
    if ai_text:
        return ai_text.strip()
    name = product["name"]
    feats = product.get("features", [])
    feat_block = "\n".join(f"• {f}" for f in feats) or "• Instant digital download\n• Easy to use, no software required"
    return (
        f"{name} — Instant Digital Download\n\n"
        f"WHAT'S INCLUDED\n{feat_block}\n\n"
        f"HOW IT WORKS\n"
        f"1. Purchase & download instantly\n"
        f"2. Open, print, or import into your favourite app\n"
        f"3. Start using it in minutes\n\n"
        f"PLEASE NOTE\n"
        f"• Digital download only — no physical item will be shipped\n"
        f"• For personal use unless a commercial licence is stated\n"
    )


def build_pricing_tip(product):
    price = product.get("price")
    if not price:
        return "No price given. For Etsy digital products, comparable listings cluster at $3–$30 single / $15–$75 bundle."
    try:
        p = float(price)
    except (TypeError, ValueError):
        return "Price not numeric — check the price field."
    fee = 0.20 + p * 0.065 + p * 0.03 + 0.25  # listing + transaction + US payment processing
    return f"At ${p:.2f} on Etsy: est. fees ≈ ${fee:.2f} (listing $0.20 + 6.5% + 3% + $0.25), you keep ≈ ${p - fee:.2f} before offsite-ads (optional under $10k/yr sales)."


def try_ollama(product):
    """Return AI draft text, or None if no local model is reachable."""
    prompt = (
        "You are a marketplace listing writer for Etsy/eBay sellers of digital products.\n"
        f"Product: {json.dumps(product, ensure_ascii=False)}\n"
        "Write a polished listing description (max 220 words): a one-line hook, "
        "WHAT'S INCLUDED bullets from the features, HOW IT WORKS in 3 steps, and a short note "
        "that it is a digital download. Plain text only."
    )
    payload = json.dumps({"model": MODEL, "prompt": prompt, "stream": False}).encode()
    req = urllib.request.Request(f"{OLLAMA_URL}/api/generate", data=payload,
                                 headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            data = json.loads(resp.read().decode())
            return data.get("response") or None
    except Exception:
        return None


def generate(product, use_ai=True):
    ai_text = try_ollama(product) if use_ai else None
    return {
        "engine": f"ollama:{MODEL}" if ai_text else "fallback:rules-v1",
        "titles": build_titles(product),
        "tags": build_tags(product),
        "description": build_description(product, ai_text),
        "pricing_tip": build_pricing_tip(product),
    }
