#!/usr/bin/env python3
"""ListingGenie — zero-dependency web demo + CLI.

Run the web demo:  python3 app.py            -> http://localhost:8000
Run the CLI:       python3 app.py --cli examples/calendar.json
"""
import json
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer
from generator import generate

PAGE = """<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<title>ListingGenie — Listing Generator for Digital-Product Sellers</title>
<style>body{font-family:system-ui;max-width:760px;margin:2rem auto;padding:0 1rem}
label{display:block;margin:.7rem 0 .2rem;font-weight:600}input,select,textarea{width:100%;padding:.5rem}
button{margin-top:1rem;padding:.6rem 1.2rem}pre{background:#f4f4f4;padding:1rem;white-space:pre-wrap}</style>
</head><body>
<h1>ListingGenie</h1>
<p>Turn rough notes into an Etsy/eBay-ready listing: titles, 13 tags, description, pricing tip.
Runs on a local open-weight model via Ollama when available — no API key, no per-token cost.</p>
<form method="post" action="/generate">
<label>Product name</label><input name="name" required value="2027 Minimalist Calendar Printable">
<label>Platform</label><select name="platform"><option>etsy</option><option>ebay</option></select>
<label>Category</label><input name="category" value="printable planner">
<label>Format</label><input name="format" value="PDF, A4 + US Letter, GoodNotes ready">
<label>Keywords (comma separated)</label><input name="keywords" value="2027 calendar, monthly planner, wall calendar 2027">
<label>Features (one per line)</label><textarea name="features" rows="4">12 monthly pages + year-at-a-glance
Sunday-start and Monday-start versions
Print PDF + hyperlinked GoodNotes version</textarea>
<label>Target buyer</label><input name="audience" value="planner lovers">
<label>Price (USD, optional)</label><input name="price" value="6.99">
<button type="submit">Generate listing</button></form>
<div id="out">{OUTPUT}</div>
</body></html>"""


def render(result):
    titles = "\n".join(f"- ({t['chars']} chars) {t['title']}" for t in result["titles"])
    return (f"<h2>Generated listing</h2><p><em>Engine: {result['engine']}</em></p>"
            f"<h3>Titles</h3><pre>{titles}</pre>"
            f"<h3>Tags ({len(result['tags'])})</h3><pre>{', '.join(result['tags'])}</pre>"
            f"<h3>Description</h3><pre>{result['description']}</pre>"
            f"<h3>Pricing tip</h3><pre>{result['pricing_tip']}</pre>")


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        body = PAGE.replace("{OUTPUT}", "").encode()
        self.send_response(200); self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body))); self.end_headers(); self.wfile.write(body)

    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        from urllib.parse import parse_qs
        form = {k: v[0] for k, v in parse_qs(self.rfile.read(length).decode()).items()}
        product = {
            "name": form.get("name", ""), "platform": form.get("platform", "etsy"),
            "category": form.get("category", ""), "format": form.get("format", ""),
            "keywords": [k.strip() for k in form.get("keywords", "").split(",") if k.strip()],
            "features": [f.strip() for f in form.get("features", "").splitlines() if f.strip()],
            "audience": form.get("audience", ""), "price": form.get("price", ""),
        }
        body = PAGE.replace("{OUTPUT}", render(generate(product))).encode()
        self.send_response(200); self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body))); self.end_headers(); self.wfile.write(body)

    def log_message(self, *a):
        pass


if __name__ == "__main__":
    if len(sys.argv) > 2 and sys.argv[1] == "--cli":
        with open(sys.argv[2]) as f:
            print(json.dumps(generate(json.load(f)), indent=2, ensure_ascii=False))
    else:
        print("ListingGenie running at http://localhost:8000")
        HTTPServer(("0.0.0.0", 8000), Handler).serve_forever()
