#!/usr/bin/env python3
"""Regenerate the Professor Davis Coakley Award 2026 site (and, once later
phases land, the QR codes and print PDFs) from content/pieces.yaml.

Usage:
    python build.py            # regenerate docs/ (site) locally
    python build.py --deploy   # regenerate, then git add/commit/push

See README.md for the non-developer walkthrough.
"""
import argparse
import html
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

import yaml
from jinja2 import Environment, FileSystemLoader, select_autoescape

ROOT = Path(__file__).resolve().parent
CONTENT_FILE = ROOT / "content" / "pieces.yaml"
TEMPLATES_DIR = ROOT / "templates"
DOCS_DIR = ROOT / "docs"
ASSETS_DIR = DOCS_DIR / "assets"

BASE_URL = "https://davis-coakley-medal-2026.web.app/"
FIREBASE_PROJECT = "davis-coakley-medal-2026"
FIREBASE_KEY = ROOT / ".secrets" / "firebase-service-account.json"

NO_DESCRIPTION_STATUSES = {"missing_description", "missing_fields"}

_ITALIC_RE = re.compile(r"\*(.+?)\*")


def md_to_html(text: str) -> str:
    """Escape a plain paragraph then apply the one supported markdown rule:
    *word* -> <em>word</em>. Escaping first means the asterisks themselves
    are never HTML, only the italic markup we add is."""
    escaped = html.escape(text, quote=False)
    return _ITALIC_RE.sub(r"<em>\1</em>", escaped)


def video_embed_url(url: str) -> str:
    """Turn a normal YouTube/Vimeo URL into its privacy-enhanced embed form."""
    if not url:
        return ""
    yt = re.search(r"(?:youtu\.be/|youtube\.com/(?:watch\?v=|embed/))([\w-]{6,})", url)
    if yt:
        return f"https://www.youtube-nocookie.com/embed/{yt.group(1)}"
    vimeo = re.search(r"vimeo\.com/(\d+)", url)
    if vimeo:
        return f"https://player.vimeo.com/video/{vimeo.group(1)}?dnt=1"
    return url


def load_pieces():
    with open(CONTENT_FILE, encoding="utf-8") as f:
        raw = yaml.safe_load(f)

    pieces = []
    for p in raw:
        piece = dict(p)
        piece["byline_display"] = piece.get("artist") or piece.get("role") or ""
        piece["has_content"] = piece["status"] not in NO_DESCRIPTION_STATUSES and bool(
            piece.get("description") or piece.get("sections") or piece.get("closing")
        )
        piece["description_html"] = [md_to_html(p_) for p_ in piece.get("description", [])]
        piece["closing_html"] = [md_to_html(p_) for p_ in piece.get("closing", [])]
        sections_html = []
        for s in piece.get("sections", []):
            sections_html.append({
                "heading": html.escape(s["heading"], quote=False),
                "lang": s.get("lang") or "",
                "body": [md_to_html(p_) for p_ in s.get("body", [])],
            })
        piece["sections_html"] = sections_html
        piece["video_embed_url"] = video_embed_url(piece.get("video_url", ""))
        piece["title_lang"] = piece.get("title_lang", "")
        pieces.append(piece)

    ids = [p["id"] for p in pieces]
    assert len(ids) == len(set(ids)), f"duplicate piece ids: {ids}"
    return pieces


def og_description_for(piece) -> str:
    if piece["description_html"]:
        first = re.sub(r"<[^>]+>", "", piece["description_html"][0])
        first = html.unescape(first)
        return (first[:157] + "…") if len(first) > 160 else first
    bits = [b for b in (piece.get("form"), piece.get("byline_display")) if b]
    tail = " — ".join(bits) if bits else "Professor Davis Coakley Award 2026"
    return f"{tail}. Professor Davis Coakley Award 2026, 73rd IGS Annual & Scientific Meeting, Cork."


def build_site(pieces):
    if DOCS_DIR.exists():
        for item in DOCS_DIR.iterdir():
            if item.name == "assets":
                continue  # assets (fonts, logo, favicons, css) are source-controlled, not generated
            if item.is_dir():
                shutil.rmtree(item)
            else:
                item.unlink()

    env = Environment(
        loader=FileSystemLoader(str(TEMPLATES_DIR)),
        autoescape=select_autoescape(["html"]),
    )

    index_tpl = env.get_template("index.html")
    piece_tpl = env.get_template("piece.html")

    index_html = index_tpl.render(
        pieces=pieces,
        page_title="Professor Davis Coakley Award 2026 — 73rd IGS Annual & Scientific Meeting",
        og_title="Professor Davis Coakley Award 2026",
        og_description="Ageing with Innovation: Are We Ready? — 13 works from the Professor Davis Coakley Award 2026, 73rd IGS Annual & Scientific Meeting, Cork.",
        canonical_url=BASE_URL,
        base_url=BASE_URL,
        asset_prefix="",
    )
    (DOCS_DIR / "index.html").write_text(index_html, encoding="utf-8")

    for piece in pieces:
        out_dir = DOCS_DIR / piece["id"]
        out_dir.mkdir(parents=True, exist_ok=True)
        canonical = f"{BASE_URL}{piece['id']}/"
        page_title = f"{piece['title']} — Professor Davis Coakley Award 2026"
        html_out = piece_tpl.render(
            piece=piece,
            page_title=page_title,
            og_title=piece["title"],
            og_description=og_description_for(piece),
            canonical_url=canonical,
            base_url=BASE_URL,
            asset_prefix="../",
        )
        (out_dir / "index.html").write_text(html_out, encoding="utf-8")

    print(f"Built index.html + {len(pieces)} piece pages into {DOCS_DIR}")


def git_deploy():
    subprocess.run(["git", "add", "content/pieces.yaml", "docs", "qr", "cards"], cwd=ROOT, check=True)
    status = subprocess.run(["git", "status", "--porcelain"], cwd=ROOT, capture_output=True, text=True, check=True)
    if not status.stdout.strip():
        print("Nothing to commit — working tree already matches pieces.yaml.")
        return
    subprocess.run(
        ["git", "commit", "-m", "Rebuild site/QR/cards from pieces.yaml via build.py"],
        cwd=ROOT,
        check=True,
    )
    branch = subprocess.run(
        ["git", "rev-parse", "--abbrev-ref", "HEAD"], cwd=ROOT, capture_output=True, text=True, check=True
    ).stdout.strip()
    subprocess.run(["git", "push", "-u", "origin", branch], cwd=ROOT, check=True)
    print(f"Pushed to origin/{branch}")


def firebase_deploy():
    if not FIREBASE_KEY.exists():
        print(
            f"Skipping Firebase deploy: no key at {FIREBASE_KEY}\n"
            "Ask whoever set this up for the Firebase service account JSON and "
            "save it there (it's git-ignored, never commit it) — see README.md.",
            file=sys.stderr,
        )
        return
    env = {**os.environ, "GOOGLE_APPLICATION_CREDENTIALS": str(FIREBASE_KEY)}
    subprocess.run(
        ["npx", "--yes", "firebase-tools@latest", "deploy", "--only", "hosting",
         "--project", FIREBASE_PROJECT, "--non-interactive"],
        cwd=ROOT, check=True, env=env,
    )
    print(f"Deployed to {BASE_URL}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--deploy", action="store_true", help="commit+push to git, then deploy to Firebase Hosting")
    args = parser.parse_args()

    pieces = load_pieces()
    build_site(pieces)
    # QR code generation (Phase 3) and print PDF generation (Phase 4) hook in here.

    if args.deploy:
        git_deploy()
        firebase_deploy()


if __name__ == "__main__":
    main()
