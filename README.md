# ListingGenie

Turn rough product notes into a marketplace-ready listing — titles, tags,
description and a pricing sanity check — for Etsy / eBay sellers of
**digital products** (templates, planners, calendars, printables).

Built for the **DEV Hacktoberfest Open-Source AI Challenge — Week 2: Side Hustle**.

## Why this exists

Digital-product sellers don't lose sales because their product is bad.
They lose them at the listing page: a title over the character limit,
3 tags used out of 13, a description that never says it's a digital
download. ListingGenie takes 30 seconds of rough notes and returns a
listing that respects the platform's actual constraints.

## Open-source AI at the core

- Runs on a **local open-weight model via [Ollama](https://ollama.com)**
  (default `gemma3:4b`; set `LISTINGGENIE_MODEL` to use Llama 3.2, Qwen, etc.).
- **No API key, no per-token bill.** A seller generating 200 listings a
  month pays $0 in inference — that is what makes a $5–9/mo tool viable.
- **Private by default.** Unpublished product ideas never leave the
  seller's machine.
- No local model? A deterministic fallback generator produces the same
  structure, so the demo always runs. The app tells you which engine ran.

## Quick start

```bash
# zero dependencies — Python 3.10+ standard library only
python3 app.py                 # web demo at http://localhost:8000

# optional: real open-weight drafting
ollama pull gemma3:4b
ollama serve                   # then reload the web demo

# CLI
python3 app.py --cli examples/calendar.json
```

## What it generates

| Output | Constraint handled |
|---|---|
| 3 title variants | ≤140 chars, keywords first |
| 13 tags | Etsy's exact tag count, ≤20 chars each |
| Description | hook + what's included + how it works + digital-download note |
| Pricing tip | Etsy fee math ($0.20 + 6.5% + 3% + $0.25) and take-home estimate |

## Who would pay

Etsy/Etsy-adjacent digital sellers listing 10+ products a month:
$5–9/mo for batch generation + niche keyword packs (planners, invitations,
resumes, worksheets). The unit economics only work because inference is
local and open-weight — a closed API would eat the whole subscription.

## Roadmap

- Batch mode (CSV in → listings out)
- Keyword packs per niche, tuned from real marketplace data
- One-click export: Etsy CSV / eBay file-exchange format

## License

MIT
