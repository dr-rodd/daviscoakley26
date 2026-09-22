"""Generate the print-ready exhibition cards (A6 individual with bleed, and
A4 4-up with cut guides) from content/pieces.yaml + the QR codes in qr/.

Called from build.py; can also be run standalone: `python build_cards.py`.
"""
import sys
from pathlib import Path

from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML

ROOT = Path(__file__).resolve().parent
TEMPLATES_DIR = ROOT / "templates"
CARDS_DIR = ROOT / "cards"
FONT_DIR = (ROOT / "docs" / "assets" / "fonts").as_uri()
LOGO_PATH = (ROOT / "docs" / "assets" / "logo-seal.png").as_uri()
QR_DIR = ROOT / "qr"

MEASURE_FONT = ROOT / "docs" / "assets" / "fonts" / "eb-garamond-variable.woff2"
TITLE_FONT_SIZE_PT = 17.5
TITLE_WEIGHT = 600
TITLE_BOX_WIDTH_MM = 84
TITLE_MAX_LINES = 3
MM_PER_PT = 25.4 / 72


def _title_font(size_pt: float):
    from PIL import ImageFont
    font = ImageFont.truetype(str(MEASURE_FONT), size=int(size_pt * 4))  # oversample for accuracy
    try:
        font.set_variation_by_axes([TITLE_WEIGHT])
    except Exception:
        pass
    return font, 4  # oversample factor


def wrap_line_count(text: str, box_width_mm: float = TITLE_BOX_WIDTH_MM) -> int:
    """Greedy word-wrap `text` at TITLE_FONT_SIZE_PT/TITLE_WEIGHT into a box
    `box_width_mm` wide, return the number of lines it takes. Used to catch
    titles that would overflow the shared 3-line card budget *before*
    silently clipping them in the PDF."""
    font, oversample = _title_font(TITLE_FONT_SIZE_PT)
    box_width_px = (box_width_mm / MM_PER_PT) * oversample

    words = text.split()
    lines = 1
    line = ""
    for word in words:
        candidate = f"{line} {word}".strip()
        if font.getlength(candidate) <= box_width_px:
            line = candidate
        else:
            lines += 1
            line = word
    return lines


def build_card_data(pieces):
    cards = []
    overflow = []
    for p in pieces:
        card = {
            "id": p["id"],
            "title": p["title"],
            "artist": p.get("artist") or p.get("role") or "",
            "form": p.get("form", ""),
            "qr_path": (QR_DIR / f"{p['id']}.svg").as_uri(),
        }
        cards.append(card)
        n_lines = wrap_line_count(p["title"])
        if n_lines > TITLE_MAX_LINES:
            overflow.append((p["id"], p["title"], n_lines))
    return cards, overflow


def render_individual(cards, card_css: str):
    env = Environment(loader=FileSystemLoader(str(TEMPLATES_DIR)))
    tpl = env.get_template("card_individual.html")
    html = tpl.render(cards=cards, card_css=card_css, logo_path=LOGO_PATH)
    out = CARDS_DIR / "cards_A6_individual.pdf"
    HTML(string=html, base_url=str(ROOT)).write_pdf(str(out))
    print(f"Wrote {out}")
    return out


def render_4up(cards, card_css: str):
    # 2x2 grid, columns at x=0.5mm/148.5mm, rows at y=0mm/105mm (see
    # card_4up.html for why: two A6 widths (296mm) are 1mm narrower than
    # A4 landscape (297mm); two A6 heights (210mm) match A4 landscape
    # height exactly).
    positions = [
        {"left": "0.5mm", "top": "0mm"},
        {"left": "148.5mm", "top": "0mm"},
        {"left": "0.5mm", "top": "105mm"},
        {"left": "148.5mm", "top": "105mm"},
    ]
    sheets = []
    for i in range(0, len(cards), 4):
        group = cards[i:i + 4]
        sheet = [{**card, **pos} for card, pos in zip(group, positions)]
        sheets.append(sheet)

    env = Environment(loader=FileSystemLoader(str(TEMPLATES_DIR)))
    tpl = env.get_template("card_4up.html")
    html = tpl.render(sheets=sheets, card_css=card_css, logo_path=LOGO_PATH)
    out = CARDS_DIR / "cards_A4_4up.pdf"
    HTML(string=html, base_url=str(ROOT)).write_pdf(str(out))
    print(f"Wrote {out}")
    return out


def render_previews(individual_pdf: Path, piece_ids):
    import subprocess
    pieces = list(enumerate(piece_ids, start=1))  # 1 card per page, in doc order
    page_by_id = {pid: page for page, pid in pieces}
    for pid in ("01", "03", "13"):
        page = page_by_id.get(pid)
        if not page:
            continue
        out_prefix = CARDS_DIR / f"preview_{pid}"
        subprocess.run(
            ["pdftoppm", "-png", "-r", "200", "-f", str(page), "-l", str(page),
             str(individual_pdf), str(out_prefix)],
            check=True,
        )
        print(f"Wrote preview for card {pid}")


def generate(pieces, font_dir: str = FONT_DIR):
    CARDS_DIR.mkdir(exist_ok=True)
    card_css_template = Environment(loader=FileSystemLoader(str(TEMPLATES_DIR))).get_template("card.css")
    card_css = card_css_template.render(font_dir=font_dir)

    cards, overflow = build_card_data(pieces)
    if overflow:
        print("\nTITLE OVERFLOW at shared card size (17.5pt, 3-line budget) — reporting, not shrinking:",
              file=sys.stderr)
        for id_, title, n in overflow:
            print(f"  {id_}: {n} lines needed — {title!r}", file=sys.stderr)

    individual_pdf = render_individual(cards, card_css)
    render_4up(cards, card_css)
    render_previews(individual_pdf, [c["id"] for c in cards])
    return overflow


if __name__ == "__main__":
    import yaml
    pieces = yaml.safe_load(open(ROOT / "content" / "pieces.yaml", encoding="utf-8"))
    generate(pieces)
