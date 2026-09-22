"""Generate the exhibition QR codes: one per piece, identical module grid,
dot-style data modules with solid finder-pattern eyes for reliable scanning,
in IGS navy. Verifies every code decodes back to its exact URL before
letting the build succeed.

Called from build.py; can also be run standalone: `python qr_gen.py`.
"""
import io
import sys
from pathlib import Path

import cairosvg
import qrcode
from qrcode.constants import ERROR_CORRECT_M

ROOT = Path(__file__).resolve().parent
QR_DIR = ROOT / "qr"

# Sampled from the real IGS logo you supplied (docs/assets/logo-seal.png) —
# this is their actual navy, not an invented brand colour. High contrast on
# white/off-white, unlike the accent red, which is why it's used here and
# nowhere near body text.
QR_DARK = "#18316F"
BORDER_MODULES = 4
DOT_RADIUS_RATIO = 0.42  # circle radius as a fraction of one module cell


def _finder_exclusion_zones(modules_count: int):
    """Module-index (row, col) sets covered by the 3 finder-pattern 'eyes'
    plus their 1-module separator — 8x8 blocks in the three corners, per the
    QR spec. Skipped by the per-module dot loop; drawn separately as rounded
    eyes by _finder_origins below."""
    zones = set()
    for r0, c0 in [(0, 0), (0, modules_count - 8), (modules_count - 8, 0)]:
        for r in range(r0, r0 + 8):
            for c in range(c0, c0 + 8):
                zones.add((r, c))
    return zones


def _finder_origins(modules_count: int):
    """Top-left (row, col) of each 7x7 finder pattern itself (not the
    separator)."""
    n = modules_count
    return [(0, 0), (0, n - 7), (n - 7, 0)]


def make_qr_matrix(url: str, version: int):
    qr = qrcode.QRCode(version=version, error_correction=ERROR_CORRECT_M, box_size=1, border=0)
    qr.add_data(url)
    qr.make(fit=False)
    return qr.modules  # list[row] of list[bool], size = 17 + 4*version


def required_version(urls) -> int:
    """Smallest QR version (at ECC M) that fits the longest of the given
    URLs, so every piece can share one identical module grid."""
    longest = max(urls, key=len)
    for v in range(1, 41):
        qr = qrcode.QRCode(version=v, error_correction=ERROR_CORRECT_M, box_size=1, border=0)
        qr.add_data(longest)
        try:
            qr.make(fit=False)
            return v
        except Exception:
            continue
    raise ValueError("URL too long for any QR version at ECC M")


def _finder_eye_svg(row0: int, col0: int, dark: str, mask_id: str, light: str = "#ffffff") -> str:
    """A rounded-square eye with a circular pupil — the standard reliable
    'extra-rounded' styled-QR eye: scanners still see the same nested
    square-in-square-in-square silhouette the finder-detection algorithm
    looks for, just with soft corners to match the dotted data field.

    The cutout ring is painted `light` rather than masked to transparent:
    cairosvg's <mask> support proved unreliable (dropped shapes / smeared
    gradients on some eyes), and printed cards always sit on a near-white
    card anyway, so a flat fill is both simpler and more robust."""
    x, y = col0 + BORDER_MODULES, row0 + BORDER_MODULES
    outer = f'<rect x="{x}" y="{y}" width="7" height="7" rx="2" ry="2" fill="{dark}"/>'
    cutout = f'<rect x="{x + 1}" y="{y + 1}" width="5" height="5" rx="1.4" ry="1.4" fill="{light}"/>'
    pupil = f'<circle cx="{x + 3.5}" cy="{y + 3.5}" r="1.5" fill="{dark}"/>'
    return outer + cutout + pupil


def matrix_to_svg(matrix, dark=QR_DARK, light="#ffffff") -> str:
    n = len(matrix)
    size = n + 2 * BORDER_MODULES
    excluded = _finder_exclusion_zones(n)
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {size} {size}" '
        f'width="{size}" height="{size}" shape-rendering="geometricPrecision">'
    ]
    for r in range(n):
        for c in range(n):
            if not matrix[r][c] or (r, c) in excluded:
                continue
            x, y = c + BORDER_MODULES, r + BORDER_MODULES
            cx, cy = x + 0.5, y + 0.5
            parts.append(f'<circle cx="{cx}" cy="{cy}" r="{DOT_RADIUS_RATIO}" fill="{dark}"/>')
    for i, (row0, col0) in enumerate(_finder_origins(n)):
        parts.append(_finder_eye_svg(row0, col0, dark, mask_id=f"eye{i}", light=light))
    parts.append("</svg>")
    return "".join(parts)


def decode_png(png_bytes: bytes) -> str:
    from PIL import Image
    from pyzbar.pyzbar import decode

    img = Image.open(io.BytesIO(png_bytes)).convert("L")
    results = decode(img)
    if not results:
        return ""
    return results[0].data.decode("utf-8")


def generate(pieces, base_url: str):
    QR_DIR.mkdir(exist_ok=True)
    urls = [f"{base_url}{p['id']}/" for p in pieces]
    version = required_version(urls)
    print(f"QR version {version} ({17 + 4 * version}x{17 + 4 * version} modules) fits all {len(urls)} URLs")

    failures = []
    for piece, url in zip(pieces, urls):
        matrix = make_qr_matrix(url, version)
        svg = matrix_to_svg(matrix)
        svg_path = QR_DIR / f"{piece['id']}.svg"
        svg_path.write_text(svg, encoding="utf-8")

        png_bytes = cairosvg.svg2png(bytestring=svg.encode("utf-8"), output_width=1200, output_height=1200,
                                      background_color="white")
        png_path = QR_DIR / f"{piece['id']}.png"
        png_path.write_bytes(png_bytes)

        decoded = decode_png(png_bytes)
        status = "OK" if decoded == url else "MISMATCH"
        print(f"  {piece['id']}  {url}  -> decoded: {decoded or '(none)'}  [{status}]")
        if decoded != url:
            failures.append((piece["id"], url, decoded))

    if failures:
        print("\nQR VERIFICATION FAILED for:", file=sys.stderr)
        for id_, expected, got in failures:
            print(f"  {id_}: expected {expected!r}, got {got!r}", file=sys.stderr)
        raise SystemExit(1)

    print(f"All {len(urls)} QR codes verified OK.")


if __name__ == "__main__":
    import yaml
    pieces = yaml.safe_load(open(ROOT / "content" / "pieces.yaml", encoding="utf-8"))
    generate(pieces, "https://davis-coakley-medal-2026.web.app/")
