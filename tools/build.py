#!/usr/bin/env python3
"""Build site/docs/<slug>/data.js and site/library.js from docs/*/meta.json + OCR md."""
import json
import re
import sys
from pathlib import Path

import pymupdf

ROOT = Path(__file__).resolve().parent.parent
SLUG_RE = re.compile(r"^[a-z0-9-]+$")
MISSING = "〔尚未辨識〕"

library = []
for meta_path in sorted((ROOT / "docs").glob("*/meta.json")):
    slug = meta_path.parent.name
    if not SLUG_RE.match(slug):
        sys.exit(f"invalid slug {slug!r}: must match ^[a-z0-9-]+$")
    meta = json.loads(meta_path.read_text(encoding="utf-8"))
    pdf = pymupdf.open(ROOT / meta["pdf"])
    pages = []
    for i, page in enumerate(pdf, start=1):
        md_path = meta_path.parent / "ocr" / f"page_{i:03d}.md"
        md = md_path.read_text(encoding="utf-8") if md_path.exists() else MISSING
        pages.append({"n": i, "img": f"docs/{slug}/pages/page_{i:03d}.jpg",
                      "w": int(page.rect.width), "h": int(page.rect.height), "md": md})
    doc = {"slug": slug, "title": meta["title"], "subtitle": meta.get("subtitle", ""), "pages": pages}
    out = ROOT / "site" / "docs" / slug
    out.mkdir(parents=True, exist_ok=True)
    (out / "data.js").write_text("window.DOC = " + json.dumps(doc, ensure_ascii=False) + ";\n", encoding="utf-8")
    library.append((meta.get("order", 0), {"slug": slug, "title": meta["title"],
                    "subtitle": meta.get("subtitle", ""), "pages": len(pages),
                    "cover": f"docs/{slug}/cover.jpg"}))
    print(f"{slug}: {len(pages)} pages")

library.sort(key=lambda t: t[0])
(ROOT / "site" / "library.js").write_text(
    "window.LIBRARY = " + json.dumps([d for _, d in library], ensure_ascii=False) + ";\n", encoding="utf-8")
print(f"library.js: {len(library)} docs")
