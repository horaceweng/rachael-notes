#!/usr/bin/env python3
"""Add a new PDF. Usage: new_doc.py <pdf_path> <slug> --title ... [--subtitle ...]"""
import argparse
import json
import re
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from render import render  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent

ap = argparse.ArgumentParser()
ap.add_argument("pdf_path")
ap.add_argument("slug")
ap.add_argument("--title", required=True)
ap.add_argument("--subtitle", default="")
ap.add_argument("--publish", action="store_true", help="include in the deployed site (default: local preview only)")
a = ap.parse_args()

if not re.fullmatch(r"[a-z0-9-]+", a.slug):
    sys.exit("slug must match ^[a-z0-9-]+$")
doc_dir = ROOT / "docs" / a.slug
if doc_dir.exists():
    sys.exit(f"docs/{a.slug} already exists")
orders = [json.loads(p.read_text(encoding="utf-8")).get("order", 0)
          for p in (ROOT / "docs").glob("*/meta.json")]
(ROOT / "pdfs").mkdir(exist_ok=True)
shutil.copy2(a.pdf_path, ROOT / "pdfs" / f"{a.slug}.pdf")
(doc_dir / "ocr").mkdir(parents=True)
meta = {"title": a.title, "subtitle": a.subtitle, "pdf": f"pdfs/{a.slug}.pdf",
        "order": max(orders, default=0) + 1, "publish": a.publish}
(doc_dir / "meta.json").write_text(json.dumps(meta, ensure_ascii=False) + "\n", encoding="utf-8")
render(a.slug)
