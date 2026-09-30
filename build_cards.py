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
LOGO_PATH = (ROOT / "docs" / "assets" / "logo-seal-navy.png").as_uri()  # cards keep the logo in its real colour
QR_DIR = ROOT / "qr"

MEASURE_FONT = ROOT / "docs" / "assets" / "fonts" / "arimo-variable.woff2"
TITLE_FONT_SIZE_PT = 16.5
TITLE_WEIGHT = 700
TITLE_BOX_WIDTH_MM = 125  # card-left width (133mm) minus a typical number indent, for the overflow check
TITLE_MAX_LINES = 3
MM_PER_PT = 25.4 / 72
NUM_GAP_MM = 1.5  # extra space after the number, bullet-point style


def _title_font(size_pt: float):
    from PIL import ImageFont
    font = ImageFont.truetype(str(MEASURE_FONT), size=int(size_pt * 4))  # oversample for accuracy
    try:
        font.set_variation_by_axes([TITLE_WEIGHT])
    except Exception:
        pass
    return font, 4  # oversample factor


def text_width_mm(text: str, size_pt: float = TITLE_FONT_SIZE_PT) -> float:
    font, oversample = _title_font(size_pt)
    width_pt = font.getlength(text) / oversample
    return width_pt * MM_PER_PT


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
        if p.get("artist"):
            artist = p["artist"]
            role = p.get("role", "")
        else:
            # Group-credited piece (no individual artist): the role field's
            # first line stands in for the artist line, and any further
            # lines (e.g. a "Co-curated by..." credit) still render as the
            # smaller italic role line below it, rather than being swallowed
            # into the bold artist line with no break.
            first, _, rest = p.get("role", "").partition("\n")
            artist = first
            role = rest
        form, medium = p.get("form", ""), p.get("medium", "")
        # Medium explicitly labelled, on its own line, matching the source
        # document's own "Medium: ..." lines rather than a middle-dot join.
        if form and medium:
            form_medium = f"{form}\nMedium: {medium}"
        elif medium:
            form_medium = f"Medium: {medium}"
        else:
            form_medium = form
        num = str(int(p["id"]))  # no leading zero for display, unlike the permanent id/URL
        num_label = f"{num}."
        # Exact measured width of "N." at the title's own size/weight, so
        # the hanging indent (used for both the wrapped title lines and
        # every row below) lines up precisely with where "N. " ends —
        # no CSS-side guessing, which drifted for single-digit numbers.
        indent_mm = round(text_width_mm(num_label) + NUM_GAP_MM, 2)
        card = {
            "id": p["id"],
            "num": num,
            "num_label": num_label,
            "indent_mm": indent_mm,
            "title": p["title"],
            "artist": artist,
            "role": role,
            "affiliation": p.get("affiliation", ""),
            "form_medium": form_medium,
            "qr_path": (QR_DIR / f"{p['id']}.svg").as_uri(),
        }
        cards.append(card)
        # Measure with the number prefixed, since it now sits inline at the
        # same size as the title and eats into line 1's available width.
        n_lines = wrap_line_count(f"{num_label}  {p['title']}")
        if n_lines > TITLE_MAX_LINES:
            overflow.append((p["id"], p["title"], n_lines))
    return cards, overflow


def build_title_card(base_url: str):
    """The exhibition cover card: no piece number, links to the index
    instead of a single piece. Always page/card 1 — printed and slotted
    in ahead of piece 01 in both PDFs."""
    return {
        "is_title": True,
        "title": "Professor Davis Coakley Award 2026",
        "theme": "Ageing with Innovation: Are We Ready?",
        "meta": "73rd IGS Annual Scientific Meeting · Cork · 1–3 October 2026",
        "qr_path": (QR_DIR / "title.svg").as_uri(),
    }


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


def render_number_tags(pieces, tags_css: str):
    """Standalone A4 sheets of plain piece numbers (no title/QR), 8 per
    sheet in a 2x4 grid with dashed cut lines, for physically labelling
    each exhibit next to its artwork."""
    positions = [
        {"left": "0mm", "top": "0mm"},
        {"left": "105mm", "top": "0mm"},
        {"left": "0mm", "top": "74.25mm"},
        {"left": "105mm", "top": "74.25mm"},
        {"left": "0mm", "top": "148.5mm"},
        {"left": "105mm", "top": "148.5mm"},
        {"left": "0mm", "top": "222.75mm"},
        {"left": "105mm", "top": "222.75mm"},
    ]
    tags = [{"num_label": f"{str(int(p['id']))}."} for p in pieces]
    sheets = []
    for i in range(0, len(tags), 8):
        group = tags[i:i + 8]
        sheet = [{**tag, **pos} for tag, pos in zip(group, positions)]
        sheets.append(sheet)

    env = Environment(loader=FileSystemLoader(str(TEMPLATES_DIR)))
    tpl = env.get_template("number_tags.html")
    html = tpl.render(sheets=sheets, tags_css=tags_css)
    out = CARDS_DIR / "number_tags_A4.pdf"
    HTML(string=html, base_url=str(ROOT)).write_pdf(str(out))
    print(f"Wrote {out}")
    return out


def render_title_sign(base_url: str, font_dir: str):
    """Card 1 (the title/cover card) enlarged by sqrt(2) to fill half an
    A4 sheet, for use as a larger standalone sign. Two copies stacked on
    one A4 sheet, split by a dashed cut line down the middle."""
    css_template = Environment(loader=FileSystemLoader(str(TEMPLATES_DIR))).get_template("title_sign.css")
    sign_css = css_template.render(font_dir=font_dir)
    title_card = build_title_card(base_url)

    env = Environment(loader=FileSystemLoader(str(TEMPLATES_DIR)))
    tpl = env.get_template("title_sign.html")
    html = tpl.render(
        sign_css=sign_css,
        title=title_card["title"],
        theme=title_card["theme"],
        meta=title_card["meta"],
        qr_path=title_card["qr_path"],
        logo_path=LOGO_PATH,
        positions=["0mm", "148.5mm"],
    )
    out = CARDS_DIR / "title_sign_A4.pdf"
    HTML(string=html, base_url=str(ROOT)).write_pdf(str(out))
    print(f"Wrote {out}")
    return out


def render_previews(individual_pdf: Path, piece_ids, preview_ids):
    import subprocess
    # 1 card per page; page 1 is the title card, so pieces start at page 2.
    pieces = list(enumerate(piece_ids, start=2))
    page_by_id = {pid: page for page, pid in pieces}
    for old_preview in CARDS_DIR.glob("preview_*.png"):
        old_preview.unlink()
    for pid in preview_ids:
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


def generate(pieces, base_url: str, font_dir: str = FONT_DIR):
    CARDS_DIR.mkdir(exist_ok=True)
    card_css_template = Environment(loader=FileSystemLoader(str(TEMPLATES_DIR))).get_template("card.css")
    card_css = card_css_template.render(font_dir=font_dir)
    tags_css_template = Environment(loader=FileSystemLoader(str(TEMPLATES_DIR))).get_template("number_tags.css")
    tags_css = tags_css_template.render(font_dir=font_dir)

    cards, overflow = build_card_data(pieces)
    if overflow:
        print(f"\nTITLE OVERFLOW at shared card size ({TITLE_FONT_SIZE_PT}pt, {TITLE_MAX_LINES}-line budget) "
              "— reporting, not shrinking:", file=sys.stderr)
        for id_, title, n in overflow:
            print(f"  {id_}: {n} lines needed — {title!r}", file=sys.stderr)

    title_card = build_title_card(base_url)
    all_cards = [title_card] + cards

    individual_pdf = render_individual(all_cards, card_css)
    render_4up(all_cards, card_css)
    render_number_tags(pieces, tags_css)
    render_title_sign(base_url, font_dir)
    longest = max(cards, key=lambda c: len(c["title"]))["id"]
    preview_ids = sorted({cards[0]["id"], cards[-1]["id"], longest})
    render_previews(individual_pdf, [c["id"] for c in cards], preview_ids)
    return overflow


if __name__ == "__main__":
    import yaml
    pieces = yaml.safe_load(open(ROOT / "content" / "pieces.yaml", encoding="utf-8"))
    generate(pieces, base_url="https://davis-coakley-medal-2026.web.app/")
