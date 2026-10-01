#!/usr/bin/env python3
"""Render a doc's PDF to enhanced page images. Usage: render.py <slug> [--force]"""
import json
import sys
from pathlib import Path

import pymupdf
from PIL import Image

sys.path.insert(0, str(Path(__file__).parent))
from enhance import enhance  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent


def render(slug: str, force: bool = False) -> None:
    meta = json.loads((ROOT / "docs" / slug / "meta.json").read_text(encoding="utf-8"))
    pdf = pymupdf.open(ROOT / meta["pdf"])
    pages_dir = ROOT / "site" / "docs" / slug / "pages"
    ocr_dir = ROOT / "work" / slug / "ocr_img"
    pages_dir.mkdir(parents=True, exist_ok=True)
    ocr_dir.mkdir(parents=True, exist_ok=True)
    cover = ROOT / "site" / "docs" / slug / "cover.jpg"
    done = 0
    for i, page in enumerate(pdf, start=1):
        jpg = pages_dir / f"page_{i:03d}.jpg"
        png = ocr_dir / f"page_{i:03d}.png"
        need_jpg = force or not jpg.exists()
        need_png = force or not png.exists()
        need_cover = i == 1 and (force or not cover.exists())
        if not (need_jpg or need_png or need_cover):
            continue
        if need_jpg or need_cover:
            pix = page.get_pixmap(dpi=150)
            img = enhance(Image.frombytes("RGB", (pix.width, pix.height), pix.samples))
            if need_jpg:
                img.save(jpg, quality=82)
            if need_cover:
                h = round(img.height * 360 / img.width)
                img.resize((360, h), Image.LANCZOS).save(cover, quality=80)
        if need_png:
            pix = page.get_pixmap(dpi=170)
            enhance(Image.frombytes("RGB", (pix.width, pix.height), pix.samples)).save(png)
        done += 1
    print(f"{slug}: rendered {done}/{len(pdf)} pages")


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if len(args) != 1:
        sys.exit("usage: render.py <slug> [--force]")
    render(args[0], "--force" in sys.argv)
