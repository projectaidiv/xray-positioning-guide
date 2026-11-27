"""
رسومات توضيحية مبسطة (SVG) لوضعية المريض واتجاه الأشعة — بتتولّد من الكود نفسه،
فمفيش مشاكل حقوق ولا ملفات صور ثقيلة.

Schematic SVG diagrams generated in code: no copyright issues, no heavy image files.
Labels are English only (standard radiography terms) so no Arabic font is needed.

أنواع الرسم / diagram types (من data/exams.py):
  erect          واقف / أشعة أفقية   {"view": "front"|"side", "level": 0..1, "arms": "hips"|"up"|"down"|"out"}
  supine         مستلقي / أشعة رأسية {"cr_x": 0..1}
  lateral_recum  راقد على الجنب       {"note": "..."}
  limb           طرف على الطاولة     {"part": "Hand", "tilt": 0, "note": "..."}
"""
import base64
import math

TEAL = "#475569"
LIGHT = "#e2e8f0"
DARK = "#1e293b"
RED = "#dc2626"
W, H = 640, 340


def _wrap(body: str, sid: int | None, note: str | None) -> str:
    extra = ""
    if sid:
        extra += f'<text x="{W - 14}" y="26" text-anchor="end" font-size="15" font-weight="700" fill="{DARK}">SID {sid} cm</text>'
    if note:
        extra += f'<text x="14" y="{H - 12}" font-size="14" font-weight="700" fill="{RED}">{note}</text>'
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" font-family="Arial, Helvetica, sans-serif">'
        f'<defs><marker id="ah" markerWidth="10" markerHeight="8" refX="9" refY="4" orient="auto">'
        f'<path d="M0,0 L10,4 L0,8 z" fill="{RED}"/></marker></defs>'
        f'<rect width="{W}" height="{H}" rx="14" fill="#f8fafc" stroke="#cbd5e1"/>'
        f"{body}{extra}</svg>"
    )


def _tube(x, y, w=74, h=44):
    return (
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="8" fill="#b45309"/>'
        f'<text x="{x + w / 2}" y="{y + h / 2 + 5}" text-anchor="middle" font-size="13" font-weight="700" fill="#fff">Tube</text>'
    )


def _detector_v(x, y1, y2):
    return (
        f'<rect x="{x}" y="{y1}" width="14" height="{y2 - y1}" rx="3" fill="{DARK}"/>'
        f'<text x="{x + 7}" y="{y1 - 8}" text-anchor="middle" font-size="13" font-weight="700" fill="{DARK}">Detector</text>'
    )


def _cr_label(x, y):
    return f'<text x="{x}" y="{y}" text-anchor="middle" font-size="13" font-weight="700" fill="{RED}">CR</text>'


def _dot(x, y):
    return f'<circle cx="{x}" cy="{y}" r="6" fill="{RED}" stroke="#fff" stroke-width="2"/>'


def _erect(d, sid):
    view, level, arms = d.get("view", "front"), d.get("level", 0.3), d.get("arms", "down")
    floor, head_top = 300, 58
    ly = head_top + level * (floor - head_top)
    cx = 395
    half = 27 if view == "front" else 18
    parts = [f'<line x1="20" y1="{floor}" x2="{W - 20}" y2="{floor}" stroke="#94a3b8" stroke-width="3"/>']
    fill = f'fill="{LIGHT}" stroke="{TEAL}" stroke-width="3"'
    # legs, torso, head
    parts.append(f'<rect x="{cx - half}" y="205" width="{half - 2}" height="{floor - 205}" rx="6" {fill}/>')
    parts.append(f'<rect x="{cx + 2}" y="205" width="{half - 2}" height="{floor - 205}" rx="6" {fill}/>')
    parts.append(f'<rect x="{cx - half}" y="104" width="{2 * half}" height="110" rx="14" {fill}/>')
    parts.append(f'<circle cx="{cx}" cy="80" r="22" {fill}/>')
    if view == "side":  # nose toward the detector
        parts.append(f'<path d="M{cx + 20},76 l12,6 l-12,4 z" {fill}/>')
    sh_l, sh_r, sy = cx - half, cx + half, 114
    arm = f'stroke="{TEAL}" stroke-width="9" stroke-linecap="round" fill="none"'
    if arms == "hips":
        parts.append(f'<polyline points="{sh_l},{sy} {sh_l - 26},{sy + 40} {sh_l + 4},{sy + 82}" {arm}/>')
        parts.append(f'<polyline points="{sh_r},{sy} {sh_r + 26},{sy + 40} {sh_r - 4},{sy + 82}" {arm}/>')
    elif arms == "up":
        parts.append(f'<polyline points="{cx},{sy} {cx - 8},{40} {cx + 6},{14}" {arm}/>')
    elif arms == "out":
        parts.append(f'<polyline points="{sh_l},{sy} {sh_l - 36},{sy + 36} {sh_l - 44},{sy + 74}" {arm}/>')
        parts.append(f'<polyline points="{sh_r},{sy} {sh_r + 22},{sy + 36} {sh_r + 22},{sy + 70}" {arm}/>')
    else:
        parts.append(f'<line x1="{sh_l - 6}" y1="{sy}" x2="{sh_l - 6}" y2="{sy + 90}" {arm}/>')
    det_x = cx + half + 22 if view == "front" else cx + 58
    det_x = 470
    parts.append(_detector_v(det_x, 60, 270))
    parts.append(_tube(36, int(ly - 22)))
    parts.append(f'<line x1="112" y1="{ly}" x2="{det_x - 2}" y2="{ly}" stroke="{RED}" stroke-width="3" stroke-dasharray="8 5" marker-end="url(#ah)"/>')
    parts.append(_dot(cx, ly))
    parts.append(_cr_label(210, ly - 10))
    return "".join(parts)


def _supine(d, sid):
    cr_x = d.get("cr_x", 0.5)
    x0, x1 = 92, 545
    cx = x0 + cr_x * (x1 - x0)
    fill = f'fill="{LIGHT}" stroke="{TEAL}" stroke-width="3"'
    parts = [
        f'<rect x="50" y="236" width="540" height="20" rx="4" fill="#94a3b8"/>',
        f'<circle cx="112" cy="214" r="20" {fill}/>',
        f'<rect x="136" y="200" width="228" height="34" rx="14" {fill}/>',
        f'<rect x="364" y="206" width="180" height="28" rx="12" {fill}/>',
        f'<rect x="{cx - 70}" y="262" width="140" height="8" rx="3" fill="{DARK}"/>',
        f'<text x="{cx}" y="290" text-anchor="middle" font-size="13" font-weight="700" fill="{DARK}">Detector (under table)</text>',
        _tube(cx - 37, 40),
        f'<line x1="{cx}" y1="86" x2="{cx}" y2="196" stroke="{RED}" stroke-width="3" stroke-dasharray="8 5" marker-end="url(#ah)"/>',
        _dot(cx, 217),
        _cr_label(cx + 24, 140),
        f'<text x="60" y="190" font-size="12" fill="{DARK}">Head</text>',
    ]
    return "".join(parts)


def _lateral_recum(d, sid):
    fill = f'fill="{LIGHT}" stroke="{TEAL}" stroke-width="3"'
    y = 205
    parts = [
        '<rect x="110" y="250" width="420" height="20" rx="4" fill="#94a3b8"/>',
        f'<ellipse cx="320" cy="{y + 2}" rx="78" ry="42" {fill}/>',
        f'<circle cx="252" cy="{y - 4}" r="18" {fill}/>',
        f'<text x="320" y="{y - 54}" text-anchor="middle" font-size="12" fill="{DARK}">Patient (side-lying)</text>',
        _tube(36, y - 22),
        _detector_v(470, 150, 270),
        f'<line x1="112" y1="{y}" x2="468" y2="{y}" stroke="{RED}" stroke-width="3" stroke-dasharray="8 5" marker-end="url(#ah)"/>',
        _dot(320, y),
        _cr_label(190, y - 10),
    ]
    return "".join(parts)


def _limb(d, sid):
    part = d.get("part", "Limb")
    tilt = d.get("tilt", 0)
    cx = 330
    dy = 130
    shift = math.tan(math.radians(tilt)) * dy
    tx, ty = cx - shift, 215 - dy  # start point of the arrow
    fill = f'fill="{LIGHT}" stroke="{TEAL}" stroke-width="3"'
    parts = [
        '<rect x="90" y="262" width="460" height="20" rx="4" fill="#94a3b8"/>',
        f'<rect x="200" y="244" width="260" height="14" rx="3" fill="{DARK}"/>',
        f'<text x="{cx}" y="300" text-anchor="middle" font-size="13" font-weight="700" fill="{DARK}">Detector</text>',
        f'<rect x="250" y="206" width="160" height="38" rx="16" {fill}/>',
        f'<text x="{cx}" y="231" text-anchor="middle" font-size="15" font-weight="700" fill="{DARK}">{part}</text>',
        _tube(tx - 37 - shift * 0.0, 40),
        f'<line x1="{tx}" y1="88" x2="{cx}" y2="204" stroke="{RED}" stroke-width="3" stroke-dasharray="8 5" marker-end="url(#ah)"/>',
        _cr_label(cx + 26, 150),
    ]
    return "".join(parts)


_BUILDERS = {"erect": _erect, "supine": _supine, "lateral_recum": _lateral_recum, "limb": _limb}


def build_svg(diagram: dict, sid: int | None = None) -> str:
    builder = _BUILDERS[diagram["t"]]
    return _wrap(builder(diagram, sid), sid, diagram.get("note"))


def svg_data_uri(diagram: dict, sid: int | None = None) -> str:
    b64 = base64.b64encode(build_svg(diagram, sid).encode("utf-8")).decode("ascii")
    return f"data:image/svg+xml;base64,{b64}"
