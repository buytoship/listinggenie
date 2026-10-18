---
title: ListingGenie — a local open-weight listing writer for Etsy sellers
published: false
tags: devchallenge, hf26challenge
---

*This is a submission for the [Hacktoberfest Open-Source AI Challenge Week 2: Side Hustle](https://dev.to/challenges/hacktoberfest-week2-2026-10-12)*

## What I Built

**ListingGenie** turns 30 seconds of rough product notes into a marketplace-ready listing for **Etsy and eBay sellers of digital products** — templates, planners, calendars, and printables.

Digital-product sellers rarely lose sales because their product is bad. They lose them at the listing page: a title that blows past the character limit, 3 tags used out of 13, a description that never says "instant digital download." ListingGenie takes a name, a few keywords, features, and an optional price, and returns:

- **3 title variants** — ≤140 chars each, keywords first (Etsy/eBay constraint)
- **13 tags** — Etsy's exact tag count, ≤20 chars each
- **A structured description** — hook, what's included, how it works in 3 steps, digital-download note
- **An Etsy fee/pricing tip** — listing fee + 6.5% transaction + 3% + $0.25 processing, with your estimated take-home (tested on a real sample: a $6.99 calendar listing nets ≈$5.88)

**Who would pay for it:** sellers listing 10+ digital products a month. The business model is simple: $5–9/month for batch generation plus niche keyword packs (planners, invitations, resumes, worksheets). That math only works because inference is local and open-weight — $0 per listing in API costs, on a product where the listing itself sells for $3–$30.

## Demo

[DEMO_URL]

Share a deployed link or a video demo.

## Code

[REPO_URL]

The repo contains `app.py` (zero-dependency Python web demo + CLI), `generator.py` (the generator core), `README.md`, `LICENSE` (MIT), and `examples/` with a real tested run against a 2027 calendar listing.

## How I Built It

The project is built around a **local open-weight model via [Ollama](https://ollama.com)**:

1. **Open-weight core** — If a local Ollama server is running, the generator sends the product data to an open-weight model (default `gemma3:4b`, overridable via `LISTINGGENIE_MODEL` — Llama 3.2, Qwen, etc. all work) to draft the description, then post-processes the result into the platform constraints (title/tag limits).
2. **Deterministic fallback** — If no local model is reachable, a rule-based generator produces the same output structure, so the demo runs with zero setup and the post is honest about which engine ran. In the tested sample output included in the repo (`examples/sample-output.json`), the engine is `fallback:rules-v1` because no Ollama server was running — the demo degrades gracefully instead of failing.
3. **Zero dependencies** — the whole app is Python 3 standard library only (`http.server`, `urllib`). No `pip install`, no API keys, no build step. It runs with `python3 app.py`.

The open piece isn't decoration: it *is* the cost structure of the business.

## Why Does Open Innovation Matter?

Three reasons a closed API would kill this product:

1. **Cost** — A seller generating 200 listings a month through a closed API pays real per-token money every month, forever. ListingGenie's local open-weight inference costs **$0 per listing**. A closed API would eat the entire $5–9 subscription; open models make the subscription pure margin.
2. **Privacy** — Sellers' unpublished product ideas, niche keywords, and pricing strategy are their competitive edge. With local inference, that data **never leaves their machine**. A closed API means handing your product roadmap to someone else's server.
3. **Portability** — Sellers work from kitchens, coffee shops, and airplanes. Open-weight models run offline; a closed API fails the moment Wi-Fi does. And if one model underperforms, the user swaps it (`LISTINGGENIE_MODEL=llama3.2`) instead of begging a vendor for a pricing tier.

Open innovation is what makes a $5/month listing tool both possible and trustworthy.

## Prize Categories

No partner category is claimed in this draft — the project uses no partner technology yet, so it competes for the overall prize and featured categories only. (I may add a deployed demo on Render before the deadline, which would make it eligible for Best Use of Render.)
