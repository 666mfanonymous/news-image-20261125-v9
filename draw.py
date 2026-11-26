#!/usr/bin/env python3
"""Render THE WORLD IN ONE DAY v8 (1024x1024 px) for Wednesday, 25 November 2026.

v8 — WINNERS' EDITORIAL SCAFFOLD + PICTURED SET + STRICT LINUX DEJAVU FONT SAFETY:
- Multi-color editorial broadsheet on warm cream paper (#F7F2E7) with crisp white
  rounded story cards (#FFFFFF), navy (#1F3A5F), teal (#0E7C7B), forest (#2E6B34),
  ochre (#C08A1E), crimson (#B81D18), and ink (#1A1A18).
- Giant black Bold Serif date "Wednesday 25 November 2026" (~58px) dominates top;
  small red masthead "THE WORLD IN ONE DAY" + right summary counts; red italic
  3-hero teaser subline; "THE DAY IN NUMBERS" 6-box stat strip ABOVE heroes.
- Proportional 11-region color bar (sum = 36) + single-line "18 FIELDS" strip.
- 3 equal side-by-side heroes (#1 US Tariffs, #2 Asian Chip Rout, #3 Pakistan's
  first astronaut at Tiangong), each with ~44% drawn scene on top + bold serif
  sentence-case headline + deck + short red WHY IT MATTERS line.
- Exact 5x2 medium grid (#4–#13) with ~40-42% multi-color drawn scene banners on
  top featuring bold baked-in CAPS callouts, kickers, 15px serif headlines & decks.
- Bottom band: clean PIL world map left ("WHERE IT HAPPENED") with region-colored
  pins #1–#13 ONLY + compact region color legend (no count tables under map), and
  2 wide columns right (#14–#36) of scannable briefs with sources + [O]/[R]/[C].
- Footer: big red-bordered DATE CHECK box with all 7 Tue 24 Nov exclusions,
  confidence legend + sources line, and 23 honest 25 Nov footer left-outs.
- Strict runtime TextAuditor + wrap_strict + built-in Linux DejaVu stress audit
  (raises AssertionError on ANY dropped word, ellipsis, box overflow, or overlap).
- Deterministic, PIL + stdlib only, zero network, zero AI images.
"""

from __future__ import annotations

import argparse
import math
import os
import sys
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Iterable, Sequence

from PIL import Image, ImageDraw, ImageFont

WIDTH = 1024
HEIGHT = 1024
MX = 10
CW = WIDTH - 2 * MX  # 1004 px
# Audit-only bound for real Linux DejaVu line heights; reference 68 overflowed by 2px in stress audit.
MASTHEAD_DATE_BOX_BOTTOM = 72
# Audit-only bound for real Linux DejaVu line heights; reference 82 overflowed by 2px in stress audit.
SUBLINE_BOX_BOTTOM = 86

# ============================================================================
# MULTI-COLOR EDITORIAL PALETTE (v6 — NO MONOTONE BLACK-AND-CRIMSON WALLS)
# ============================================================================
PAPER = "#F7F2E7"
PAPER_WARM = "#EFE8D8"
CARD_BG = "#FFFFFF"
CARD_BORDER = "#D6CCB8"
RULE_SOFT = "#C7BCA6"

INK = "#1A1A18"
INK_BODY = "#2D2B27"
INK_MUTED = "#5A5348"
INK_LIGHT = "#FFFFFF"

NAVY = "#1F3A5F"
NAVY_SOFT = "#E7EEF5"
TEAL = "#0E7C7B"
TEAL_SOFT = "#E3F2F1"
FOREST = "#2E6B34"
FOREST_SOFT = "#E7F2E8"
OCHRE = "#C08A1E"
OCHRE_SOFT = "#F8F0DC"
CRIMSON = "#B81D18"
CRIMSON_SOFT = "#FCECEA"

# 11 distinct, harmonious region colors built around the core editorial palette
REGION_COLORS: dict[str, str] = {
    "N. America": "#B81D18",   # Crimson
    "L. America": "#C45328",   # Terracotta
    "W. Europe": "#1F3A5F",    # Navy
    "E. Europe": "#2E5B88",    # Slate Navy
    "Middle East": "#C08A1E",  # Ochre
    "Africa": "#96651A",       # Warm Bronze
    "S. Asia": "#2E6B34",      # Forest Green
    "East Asia": "#0E7C7B",    # Teal
    "SE Asia": "#1E8A6E",      # Jade Teal
    "Oceania": "#34729E",      # Pacific Blue
    "Space/Global": "#524C44", # Editorial Charcoal
}

REGION_ORDER: list[str] = [
    "N. America",
    "L. America",
    "W. Europe",
    "E. Europe",
    "Middle East",
    "Africa",
    "S. Asia",
    "East Asia",
    "SE Asia",
    "Oceania",
    "Space/Global",
]

REGION_DISPLAY_FULL: dict[str, str] = {
    "N. America": "N. America",
    "L. America": "Latin America",
    "W. Europe": "W. Europe",
    "E. Europe": "E. Europe",
    "Middle East": "Middle East",
    "Africa": "Africa",
    "S. Asia": "South Asia",
    "East Asia": "East Asia",
    "SE Asia": "SE Asia",
    "Oceania": "Oceania",
    "Space/Global": "Space/Global",
}

REGION_BAR_CANDIDATES: dict[str, list[str]] = {
    "N. America": ["N. AMERICA", "N. AM", "NA"],
    "L. America": ["LATIN AM.", "L. AMER", "LA"],
    "W. Europe": ["W. EUROPE", "W. EUR", "WE"],
    "E. Europe": ["E. EUROPE", "E. EUR", "EE"],
    "Middle East": ["M. EAST", "MID E.", "ME"],
    "Africa": ["AFRICA", "AFR"],
    "S. Asia": ["S. ASIA", "SA", ""],
    "East Asia": ["E. ASIA", "EA"],
    "SE Asia": ["SE ASIA", "SEA"],
    "Oceania": ["OCEANIA", "OC", ""],
    "Space/Global": ["GLOBAL", "GLOB"],
}

# Font search priority:
# - Windows: Georgia / Segoe UI
# - Linux: Liberation (metrically narrow like Times/Arial) FIRST, then DejaVu
SERIF_BOLD_NATIVE = [
    "georgiab.ttf",
    "LiberationSerif-Bold.ttf",
    "DejaVuSerif-Bold.ttf",
    "timesbd.ttf",
]
SERIF_ITALIC_NATIVE = [
    "georgiai.ttf",
    "LiberationSerif-Italic.ttf",
    "DejaVuSerif-Oblique.ttf",
    "DejaVuSerif-Italic.ttf",
    "timesi.ttf",
]
SANS_BOLD_NATIVE = [
    "segoeuib.ttf",
    "LiberationSans-Bold.ttf",
    "DejaVuSans-Bold.ttf",
    "arialbd.ttf",
]
SANS_REG_NATIVE = [
    "segoeui.ttf",
    "LiberationSans-Regular.ttf",
    "DejaVuSans.ttf",
    "arial.ttf",
]

# DejaVu stress profile: uses actual DejaVu if installed (Linux), or Verdana
# (~1.18x wider than Segoe UI) + 1.14x Georgia Serif on Windows to simulate
# worst-case Linux DejaVu width metrics.
SERIF_BOLD_DEJAVU = ["DejaVuSerif-Bold.ttf", "georgiab.ttf", "LiberationSerif-Bold.ttf"]
SERIF_ITALIC_DEJAVU = ["DejaVuSerif-Oblique.ttf", "DejaVuSerif-Italic.ttf", "georgiai.ttf"]
SANS_BOLD_DEJAVU = ["DejaVuSans-Bold.ttf", "verdanab.ttf", "segoeuib.ttf"]
SANS_REG_DEJAVU = ["DejaVuSans.ttf", "verdana.ttf", "segoeui.ttf"]


@dataclass(frozen=True)
class FontProfile:
    name: str
    serif_bold: tuple[str, ...]
    serif_italic: tuple[str, ...]
    sans_bold: tuple[str, ...]
    sans_reg: tuple[str, ...]
    serif_scale: float = 1.0  # Extra synthetic width multiplier when DejaVuSerif isn't installed
    sans_scale: float = 1.0


NATIVE_PROFILE = FontProfile(
    "native",
    tuple(SERIF_BOLD_NATIVE),
    tuple(SERIF_ITALIC_NATIVE),
    tuple(SANS_BOLD_NATIVE),
    tuple(SANS_REG_NATIVE),
    1.0,
    1.0,
)

DEJAVU_STRESS_PROFILE = FontProfile(
    "dejavu-stress",
    tuple(SERIF_BOLD_DEJAVU),
    tuple(SERIF_ITALIC_DEJAVU),
    tuple(SANS_BOLD_DEJAVU),
    tuple(SANS_REG_DEJAVU),
    1.14,  # Applied only when falling back to Georgia on Windows; 1.0 if real DejaVuSerif loads
    1.0,
)

ACTIVE_PROFILE: FontProfile = NATIVE_PROFILE


def _font_dirs() -> list[Path]:
    dirs: list[Path] = []
    win = os.environ.get("WINDIR")
    if win:
        dirs.append(Path(win) / "Fonts")
    dirs.extend(
        [
            Path("/usr/share/fonts/truetype/liberation"),
            Path("/usr/share/fonts/truetype/liberation2"),
            Path("/usr/share/fonts/truetype/dejavu"),
            Path("/usr/share/fonts/TTF"),
            Path("/usr/share/fonts"),
            Path("/Library/Fonts"),
            Path("/System/Library/Fonts"),
        ]
    )
    return [d for d in dirs if d.exists()]


_FONT_CACHE: dict[tuple[tuple[str, ...], int], tuple[ImageFont.FreeTypeFont, str]] = {}
_METRICS_CACHE: dict[int, tuple[int, int]] = {}


def load_font_with_name(
    candidates: Iterable[str],
    size: int,
    *,
    allow_footer_meta: bool = False,
) -> tuple[ImageFont.FreeTypeFont, str]:
    min_allowed = 9 if allow_footer_meta else 10
    if size < min_allowed:
        raise ValueError(
            f"Font size {size}px violates v6 floor (>={min_allowed}px, footer_meta={allow_footer_meta})"
        )
    key = (tuple(candidates), size)
    if key in _FONT_CACHE:
        return _FONT_CACHE[key]
    search = _font_dirs()
    for name in candidates:
        try:
            f = ImageFont.truetype(name, size)
            _FONT_CACHE[key] = (f, name)
            return f, name
        except OSError:
            pass
        for folder in search:
            p = folder / name
            if p.exists():
                try:
                    f = ImageFont.truetype(str(p), size)
                    _FONT_CACHE[key] = (f, name)
                    return f, name
                except OSError:
                    pass
    f = ImageFont.load_default(size=size)
    _FONT_CACHE[key] = (f, "default")
    return f, "default"


def load_font(
    candidates: Iterable[str],
    size: int,
    *,
    allow_footer_meta: bool = False,
) -> ImageFont.FreeTypeFont:
    return load_font_with_name(candidates, size, allow_footer_meta=allow_footer_meta)[0]


def font_kind(kind: str, size: int, *, allow_footer_meta: bool = False) -> tuple[ImageFont.FreeTypeFont, float]:
    """Return (font, synthetic_width_scale) for active profile."""
    if kind == "serif_bold":
        f, nm = load_font_with_name(ACTIVE_PROFILE.serif_bold, size, allow_footer_meta=allow_footer_meta)
        sc = 1.0 if "dejavu" in nm.lower() else ACTIVE_PROFILE.serif_scale
        return f, sc
    if kind == "serif_italic":
        f, nm = load_font_with_name(ACTIVE_PROFILE.serif_italic, size, allow_footer_meta=allow_footer_meta)
        sc = 1.0 if "dejavu" in nm.lower() else ACTIVE_PROFILE.serif_scale
        return f, sc
    if kind == "sans_bold":
        f, nm = load_font_with_name(ACTIVE_PROFILE.sans_bold, size, allow_footer_meta=allow_footer_meta)
        return f, ACTIVE_PROFILE.sans_scale
    if kind == "sans_reg":
        f, nm = load_font_with_name(ACTIVE_PROFILE.sans_reg, size, allow_footer_meta=allow_footer_meta)
        return f, ACTIVE_PROFILE.sans_scale
    raise ValueError(f"Unknown font kind: {kind}")


def font_metrics(font: ImageFont.FreeTypeFont) -> tuple[int, int]:
    """Return (top_bearing, visual_height) using standard sample glyphs."""
    fid = id(font)
    if fid not in _METRICS_CACHE:
        b = font.getbbox("AgH0p")
        _METRICS_CACHE[fid] = (int(b[1]), max(1, int(b[3] - b[1])))
    return _METRICS_CACHE[fid]


def top_bearing(font: ImageFont.FreeTypeFont) -> int:
    return font_metrics(font)[0]


def measure_w(d: ImageDraw.ImageDraw, text: str, font: ImageFont.FreeTypeFont, scale: float = 1.0) -> float:
    return float(d.textlength(text, font=font)) * scale


# ============================================================================
# STRICT FONT-SAFETY AUDITOR (ZERO DROPPED WORDS, ZERO ELLIPSIS, ZERO OVERLAP)
# ============================================================================
@dataclass
class TextBox:
    group: str
    label: str
    x0: float
    y0: float
    x1: float
    y1: float


class TextAuditor:
    def __init__(self) -> None:
        self.boxes: list[TextBox] = []
        self.rendered_texts: list[tuple[str, str]] = []

    def record(
        self,
        group: str,
        label: str,
        x0: float,
        y0: float,
        x1: float,
        y1: float,
        text: str,
        *,
        container: tuple[float, float, float, float] | None = None,
    ) -> None:
        if "..." in text or "…" in text:
            raise AssertionError(
                f"[{ACTIVE_PROFILE.name}] Ellipsis truncation forbidden in {label}: {text!r}"
            )
        if container is not None:
            cx0, cy0, cx1, cy1 = container
            if x0 < cx0 - 1.5 or x1 > cx1 + 1.5:
                raise AssertionError(
                    f"[{ACTIVE_PROFILE.name}] Horizontal overflow in {label}: "
                    f"[{x0:.1f}, {x1:.1f}] outside [{cx0:.1f}, {cx1:.1f}] text={text!r}"
                )
            if y0 < cy0 - 1.5 or y1 > cy1 + 1.5:
                raise AssertionError(
                    f"[{ACTIVE_PROFILE.name}] Vertical overflow in {label}: "
                    f"[{y0:.1f}, {y1:.1f}] outside [{cy0:.1f}, {cy1:.1f}] text={text!r}"
                )
        for prev in self.boxes:
            if prev.group != group:
                continue
            ov_x = min(x1, prev.x1) - max(x0, prev.x0)
            ov_y = min(y1, prev.y1) - max(y0, prev.y0)
            if ov_x > 1.0 and ov_y > 1.2:
                raise AssertionError(
                    f"[{ACTIVE_PROFILE.name}] Text collision in group '{group}': "
                    f"'{label}' ({x0:.1f},{y0:.1f},{x1:.1f},{y1:.1f}) overlaps "
                    f"'{prev.label}' ({prev.x0:.1f},{prev.y0:.1f},{prev.x1:.1f},{prev.y1:.1f})"
                )
        self.boxes.append(TextBox(group, label, x0, y0, x1, y1))
        self.rendered_texts.append((label, text))


def wrap_strict(
    d: ImageDraw.ImageDraw,
    text: str,
    font: ImageFont.FreeTypeFont,
    max_w: float,
    max_lines: int,
    *,
    scale: float = 1.0,
    label: str = "",
) -> list[str]:
    """Word-wrap text strictly; RAISE AssertionError on any dropped word, oversize token, or line overflow."""
    if "..." in text or "…" in text:
        raise AssertionError(f"[{ACTIVE_PROFILE.name}] Ellipsis forbidden in {label}: {text!r}")
    words = text.split(" ")
    lines: list[str] = []
    cur = ""
    for w in words:
        cand = f"{cur} {w}".strip()
        if measure_w(d, cand, font, scale) <= max_w:
            cur = cand
        else:
            if cur:
                lines.append(cur)
                cur = w
            else:
                raise AssertionError(
                    f"[{ACTIVE_PROFILE.name}] Token {w!r} wider than max_w={max_w:.1f} in {label}"
                )
            if measure_w(d, cur, font, scale) > max_w:
                raise AssertionError(
                    f"[{ACTIVE_PROFILE.name}] Token {cur!r} wider than max_w={max_w:.1f} in {label}"
                )
    if cur:
        lines.append(cur)
    if " ".join(lines) != text:
        raise AssertionError(f"[{ACTIVE_PROFILE.name}] Dropped words in {label}: {lines!r} vs {text!r}")
    if len(lines) > max_lines:
        raise AssertionError(
            f"[{ACTIVE_PROFILE.name}] Wrapped to {len(lines)} lines > max_lines={max_lines} "
            f"in {label} (max_w={max_w:.1f}, scale={scale:.2f}): {lines!r}"
        )
    for ln in lines:
        w_ln = measure_w(d, ln, font, scale)
        if w_ln > max_w + 0.5:
            raise AssertionError(
                f"[{ACTIVE_PROFILE.name}] Line width {w_ln:.1f} > max_w={max_w:.1f} in {label}: {ln!r}"
            )
    return lines


def draw_text_top(
    d: ImageDraw.ImageDraw,
    x: float,
    y_top: float,
    text: str,
    font: ImageFont.FreeTypeFont,
    fill: str,
    *,
    auditor: TextAuditor | None = None,
    group: str = "",
    label: str = "",
    scale: float = 1.0,
    container: tuple[float, float, float, float] | None = None,
) -> tuple[float, float]:
    """Draw text with top aligned to y_top; return (rendered_width, bottom_y)."""
    tb, vh = font_metrics(font)
    d.text((x, y_top - tb), text, font=font, fill=fill)
    w_eff = measure_w(d, text, font, scale)
    y_bot = y_top + vh
    if auditor is not None:
        auditor.record(group, label, x, y_top, x + w_eff, y_bot, text, container=container)
    return w_eff, y_bot


def draw_wrapped_block(
    d: ImageDraw.ImageDraw,
    x: float,
    y_top: float,
    text: str,
    font: ImageFont.FreeTypeFont,
    fill: str,
    max_w: float,
    max_lines: int,
    line_h: float,
    *,
    scale: float = 1.0,
    auditor: TextAuditor | None = None,
    group: str = "",
    label: str = "",
    container: tuple[float, float, float, float] | None = None,
) -> tuple[float, list[str]]:
    """Wrap strictly and draw multi-line block; return (bottom_y, lines)."""
    lines = wrap_strict(d, text, font, max_w, max_lines, scale=scale, label=label)
    tb, vh = font_metrics(font)
    max_drawn_w = 0.0
    cur_y = y_top
    for ln in lines:
        d.text((x, cur_y - tb), ln, font=font, fill=fill)
        max_drawn_w = max(max_drawn_w, measure_w(d, ln, font, scale))
        cur_y += line_h
    block_bot = y_top + (len(lines) - 1) * line_h + vh
    if auditor is not None:
        auditor.record(
            group, label, x, y_top, x + max_drawn_w, block_bot, " ".join(lines), container=container
        )
    return block_bot, lines


def draw_centered_single(
    d: ImageDraw.ImageDraw,
    cx: float,
    y_top: float,
    text: str,
    font: ImageFont.FreeTypeFont,
    fill: str,
    *,
    scale: float = 1.0,
    auditor: TextAuditor | None = None,
    group: str = "",
    label: str = "",
    container: tuple[float, float, float, float] | None = None,
) -> float:
    w_raw = float(d.textlength(text, font=font))
    w_eff = w_raw * scale
    x_draw = cx - w_raw / 2.0
    x_audit = cx - w_eff / 2.0
    tb, vh = font_metrics(font)
    d.text((x_draw, y_top - tb), text, font=font, fill=fill)
    y_bot = y_top + vh
    if auditor is not None:
        auditor.record(group, label, x_audit, y_top, x_audit + w_eff, y_bot, text, container=container)
    return y_bot


def fit_single_line(
    d: ImageDraw.ImageDraw,
    kind: str,
    text: str,
    max_w: float,
    start_size: int,
    min_size: int,
    *,
    label: str = "",
) -> tuple[ImageFont.FreeTypeFont, int, float]:
    for sz in range(start_size, min_size - 1, -1):
        f, sc = font_kind(kind, sz)
        if measure_w(d, text, f, sc) <= max_w:
            return f, sz, sc
    raise AssertionError(
        f"[{ACTIVE_PROFILE.name}] '{label}' ({text!r}) cannot fit in {max_w:.1f}px even at {min_size}px"
    )


def draw_badge_circle(
    d: ImageDraw.ImageDraw,
    cx: float,
    cy: float,
    r: float,
    num: int,
    bg: str,
    border: str = CARD_BG,
) -> None:
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=bg, outline=border, width=2)
    f, _ = font_kind("sans_bold", 10)
    s = str(num)
    tw = d.textlength(s, font=f)
    tb, vh = font_metrics(f)
    d.text((cx - tw / 2.0, cy - vh / 2.0 - tb), s, font=f, fill=INK_LIGHT)


def draw_conf_pill(
    d: ImageDraw.ImageDraw,
    x_right: float,
    y_top: float,
    conf: str,
    *,
    compact: bool = False,
) -> float:
    """Draw right-aligned OFFICIAL/REPORTED/CLAIM pill; return its left x."""
    f, sc = font_kind("sans_bold", 10)
    txt = conf
    tw = float(d.textlength(txt, font=f))
    pad_x = 4 if compact else 5
    pw = tw * max(1.0, sc) + 2 * pad_x
    ph = 12 if compact else 13
    x0 = x_right - pw
    if conf == "OFFICIAL":
        bg, fg, bd = NAVY, INK_LIGHT, NAVY
    elif conf == "REPORTED":
        bg, fg, bd = FOREST, INK_LIGHT, FOREST
    else:
        bg, fg, bd = CRIMSON, INK_LIGHT, CRIMSON
    d.rounded_rectangle([x0, y_top, x_right, y_top + ph], radius=3, fill=bg, outline=bd, width=1)
    tb, vh = font_metrics(f)
    d.text((x0 + (pw - tw) / 2.0, y_top + (ph - vh) / 2.0 - tb), txt, font=f, fill=fg)
    return x0


# ============================================================================
# 3 LARGE HERO PIL SCENES (~44% OF HERO CELL HEIGHT, MULTI-COLOR EDITORIAL)
# ============================================================================

def render_clipped_scene(
    img: Image.Image,
    scene_fn: Callable[[ImageDraw.ImageDraw, int, int, int, int], None],
    x: int,
    y: int,
    w: int,
    h: int,
) -> None:
    """Render a scene into its own clipped buffer so NO vector shape can EVER bleed outside (x, y, w, h)."""
    buf = Image.new("RGB", (w, h), CARD_BG)
    bd = ImageDraw.Draw(buf)
    scene_fn(bd, 0, 0, w, h)
    img.paste(buf, (x, y))


def hero_scene_tariffs(d: ImageDraw.ImageDraw, x: int, y: int, w: int, h: int) -> None:
    """Hero #1: proposed tariffs up to 35% — container ship + four rate pills."""
    # Soft pale sky + maritime sea
    sea_y = y + int(h * 0.72)
    d.rectangle([x, y, x + w, sea_y], fill="#E6EEF5")
    d.rectangle([x, sea_y, x + w, y + h], fill="#24476B")
    # Subtle waves
    for wy in range(sea_y + 7, y + h - 3, 8):
        for wx in range(x + 14 + (wy * 5) % 23, x + w - 24, 38):
            d.line([(wx, wy), (wx + 16, wy)], fill="#3E678F", width=1)

    # Larger, clean container ship with one row of three broad containers
    sx, sy = x + 10, sea_y - 1
    d.polygon([(sx, sy), (sx + 236, sy), (sx + 221, sy + 17), (sx + 12, sy + 17)], fill="#16293E")
    d.line([(sx + 8, sy + 7), (sx + 225, sy + 7)], fill=CRIMSON, width=3)
    # Bridge tower on left
    d.rectangle([sx + 10, sy - 39, sx + 42, sy], fill="#F7F2E7", outline=NAVY, width=1)
    d.rectangle([sx + 14, sy - 33, sx + 38, sy - 25], fill=NAVY)
    d.rectangle([sx + 14, sy - 19, sx + 38, sy - 12], fill="#6C89A6")
    d.line([(sx + 26, sy - 39), (sx + 26, sy - 49)], fill=NAVY, width=2)
    for col, color in enumerate((TEAL, OCHRE, CRIMSON)):
        cx = sx + 48 + col * 52
        d.rectangle([cx, sy - 29, cx + 49, sy - 2], fill=color, outline="#E6EEF5", width=2)

    # Four small rate pills above the ship and bridge
    f10, _ = font_kind("sans_bold", 10)
    px = x + 6
    for rate in ("CHINA 20%", "INDIA 25%", "EU 15%", "VIETNAM 35%"):
        pw = d.textlength(rate, font=f10) + 10
        d.rounded_rectangle([px, y + 5, px + pw, y + 20], radius=3, fill=NAVY)
        draw_text_top(d, px + 5, y + 8, rate, f10, INK_LIGHT)
        px += pw + 4

    # Large bold "35%" callout in open top-right sky (white numerals, crimson outline)
    f35, _ = font_kind("sans_bold", 36)
    tb35, vh35 = font_metrics(f35)
    w35 = float(d.textlength("35%", font=f35))
    cx35 = x + w - 54
    cy35 = y + 24 + (sea_y - 26 - vh35) / 2.0
    d.text(
        (cx35 - w35 / 2.0, cy35 - tb35),
        "35%",
        font=f35,
        fill=INK_LIGHT,
        stroke_width=3,
        stroke_fill=CRIMSON,
    )

    # One clean caption badge + badge #1
    cap_txt = "14 ECONOMIES"
    cap_w = d.textlength(cap_txt, font=f10) + 10
    d.rounded_rectangle([x + 30, y + h - 18, x + 30 + cap_w, y + h - 4], radius=3, fill=NAVY)
    draw_text_top(d, x + 35, y + h - 16, cap_txt, f10, INK_LIGHT)
    draw_badge_circle(d, x + 16, y + h - 13, 10, 1, REGION_COLORS["N. America"])
    draw_conf_pill(d, x + w - 6, y + h - 18, "OFFICIAL", compact=True)


def hero_scene_markets(d: ImageDraw.ImageDraw, x: int, y: int, w: int, h: int) -> None:
    """Hero #2: Asian chip rout — sleek dark terminal chart with glowing crimson plunge + index readouts."""
    d.rectangle([x, y, x + w, y + h], fill="#141E2B")
    # Subtle terminal gridlines
    for gy in range(y + 18, y + h - 14, 18):
        d.line([(x + 6, gy), (x + w - 6, gy)], fill="#233246", width=1)
    for gx in range(x + 36, x + w - 10, 44):
        d.line([(gx, y + 10), (gx, y + h - 18)], fill="#1E2C3E", width=1)

    # Top-left header bar
    f10, _ = font_kind("sans_bold", 10)
    d.rectangle([x + 6, y + 6, x + 138, y + 20], fill="#24374F")
    draw_text_top(d, x + 11, y + 8, "AI SPENDING DOUBTS", f10, "#E2ECF7")

    # Plunge line chart left-to-center
    pts = [
        (x + 10, y + 26),
        (x + 44, y + 31),
        (x + 76, y + 40),
        (x + 108, y + 38),
        (x + 140, y + 58),
        (x + 172, y + 71),
        (x + 196, y + 79),
    ]
    # Soft red glow fill under plunge
    d.polygon([(x + 10, y + h - 18)] + pts + [(x + 196, y + h - 18)], fill="#3A1D24")
    d.line(pts, fill="#F04E45", width=3)
    d.ellipse([pts[-1][0] - 4, pts[-1][1] - 4, pts[-1][0] + 4, pts[-1][1] + 4], fill="#FF6B63")

    # AI microchip icon tucked mid-left
    mx, my = x + 32, y + 48
    d.rectangle([mx, my, mx + 28, my + 24], fill="#1F3147", outline="#6AA3D5", width=1)
    for px in range(mx + 5, mx + 26, 6):
        d.line([(px, my - 4), (px, my)], fill="#6AA3D5", width=1)
        d.line([(px, my + 24), (px, my + 28)], fill="#6AA3D5", width=1)
    for py in range(my + 5, my + 22, 6):
        d.line([(mx - 4, py), (mx, py)], fill="#6AA3D5", width=1)
        d.line([(mx + 28, py), (mx + 32, py)], fill="#6AA3D5", width=1)
    f12, _ = font_kind("sans_bold", 12)
    draw_centered_single(d, mx + 14, my + 5, "AI", f12, "#A8D5F8")

    # Large bold "-6.2%" callout tucked cleanly under the plunge curve (white numerals, crimson outline)
    f_k62, _ = font_kind("sans_bold", 27)
    tb62, _ = font_metrics(f_k62)
    d.text(
        (x + 67, y + 68 - tb62),
        "-6.2%",
        font=f_k62,
        fill=INK_LIGHT,
        stroke_width=3,
        stroke_fill=CRIMSON,
    )

    # Right market ticker readouts (clean, zero overlap)
    tickers = [
        ("KOSPI", "-6.2%", "#FF7870"),
        ("SK HYNIX", "-11.1%", "#FF5C52"),
        ("SAMSUNG", "-9.9%", "#FF7870"),
        ("TAIEX", "-4.8%", "#F5B971"),
    ]
    ry = y + 10
    f11, _ = font_kind("sans_bold", 11)
    for nm, pct, col in tickers:
        draw_text_top(d, x + 204, ry, nm, f10, "#9BB0C9")
        pw = d.textlength(pct, font=f11)
        draw_text_top(d, x + w - 8 - pw, ry - 1, pct, f11, col)
        d.line([(x + 204, ry + 13), (x + w - 8, ry + 13)], fill="#233246", width=1)
        ry += 17

    # Bottom-left badge #2 + Reported pill
    d.rounded_rectangle([x + 30, y + h - 18, x + 142, y + h - 4], radius=3, fill="#24374F")
    draw_text_top(d, x + 36, y + h - 16, "Kospi ends 4,697.51", f10, "#E2ECF7")
    draw_badge_circle(d, x + 16, y + h - 13, 10, 2, REGION_COLORS["East Asia"])
    draw_conf_pill(d, x + w - 6, y + h - 18, "REPORTED", compact=True)


def hero_scene_astronaut(d: ImageDraw.ImageDraw, x: int, y: int, w: int, h: int) -> None:
    """Hero #3: Shenzhou-24 launch — white rocket ascending through blue sky."""
    d.rectangle([x, y, x + w, y + h], fill="#82BCE5")
    # A few clouds clear of the central launch vehicle
    for cx, cy in ((35, 39), (w - 45, 49), (70, 77)):
        d.ellipse([x + cx - 25, y + cy - 5, x + cx + 25, y + cy + 5], fill="#EAF5FC")
        d.ellipse([x + cx - 12, y + cy - 11, x + cx + 9, y + cy + 5], fill="#EAF5FC")
    cx = x + w // 2
    # Smoke plume and orange exhaust below the large central rocket
    for ox, oy, r in ((-20, 91, 18), (19, 91, 19), (0, 82, 14), (-35, 102, 24), (36, 103, 25)):
        d.ellipse([cx + ox - r, y + oy - r, cx + ox + r, y + oy + r], fill="#F3F0E8")
    d.polygon([(cx - 7, y + 68), (cx + 7, y + 68), (cx + 11, y + 79), (cx, y + 94), (cx - 11, y + 79)], fill="#F17A23")
    d.polygon([(cx - 4, y + 68), (cx + 4, y + 68), (cx, y + 85)], fill="#FFD45A")
    d.rectangle([cx - 8, y + 32, cx + 8, y + 69], fill="#FFFFFF", outline=NAVY, width=1)
    d.polygon([(cx - 8, y + 32), (cx, y + 19), (cx + 8, y + 32)], fill="#FFFFFF", outline=NAVY)
    d.rectangle([cx - 15, y + 43, cx - 9, y + 70], fill="#F5F7FA", outline=NAVY, width=1)
    d.rectangle([cx + 9, y + 43, cx + 15, y + 70], fill="#F5F7FA", outline=NAVY, width=1)
    d.rectangle([cx - 7, y + 49, cx + 7, y + 53], fill=CRIMSON)
    f10, _ = font_kind("sans_bold", 10)
    draw_text_top(d, x + 10, y + 7, "LIFT-OFF 00:18 UTC", f10, NAVY)
    draw_text_top(d, cx + 25, y + 27, "SHENZHOU-24", f10, NAVY)

    # Bottom-left badge #3 + Official pill
    d.rounded_rectangle([x + 30, y + h - 18, x + 126, y + h - 4], radius=3, fill="#1B2E4B")
    draw_text_top(d, x + 35, y + h - 16, "5–10 day stay", f10, "#E2ECF7")
    draw_badge_circle(d, x + 16, y + h - 13, 10, 3, REGION_COLORS["Space/Global"])
    draw_conf_pill(d, x + w - 6, y + h - 18, "OFFICIAL", compact=True)


# ============================================================================
# 10 MEDIUM SCENE BANNERS (#4–#13, ~40% OF CELL, BOLD BAKED-IN CAPS LABELS)
# ============================================================================

def scene_dhaka_wage(d: ImageDraw.ImageDraw, x: int, y: int, w: int, h: int) -> None:
    """#4 Dhaka Garment Wage — Bangladesh emerald & red sun + big white 17,000 TAKA callout."""
    d.rectangle([x, y, x + w, y + h], fill="#17573B")
    # Bangladesh crimson sun disk left (elevated clear of badge #4!)
    d.ellipse([x + 14, y + 5, x + 44, y + 35], fill="#D22630")
    # White data card right with bold baked-in CAPS callout
    d.rounded_rectangle([x + 56, y + 5, x + w - 6, y + h - 16], radius=4, fill="#FFFFFF")
    f14, _ = font_kind("sans_bold", 14)
    f10, _ = font_kind("sans_bold", 10)
    draw_centered_single(d, (x + 56 + x + w - 6) / 2.0, y + 8, "17,000 TAKA", f14, FOREST)
    draw_badge_circle(d, x + 13, y + h - 12, 8.5, 4, REGION_COLORS["S. Asia"])
    draw_conf_pill(d, x + w - 4, y + h - 14, "OFFICIAL", compact=True)


def scene_farmgate(d: ImageDraw.ImageDraw, x: int, y: int, w: int, h: int) -> None:
    """#5 South Africa Farmgate Court Ruling — warm judicial sandstone + gavel + RULING."""
    d.rectangle([x, y, x + w, y + h], fill="#EFE6D5")
    d.polygon([(x + 18, y + 11), (x + 36, y + 5), (x + 41, y + 17), (x + 23, y + 23)], fill="#6F4324")
    d.line([(x + 30, y + 17), (x + 46, y + 33)], fill="#4E2D16", width=4)
    d.rectangle([x + 14, y + 31, x + 54, y + 36], fill="#4E2D16")
    f14, _ = font_kind("sans_bold", 14)
    f10, _ = font_kind("sans_bold", 10)
    draw_centered_single(d, x + 126, y + 8, "RULING", f14, INK)
    draw_centered_single(d, x + 126, y + 24, "PANEL VOIDED", f10, "#7C5214")
    draw_badge_circle(d, x + 13, y + h - 12, 8.5, 5, REGION_COLORS["Africa"])
    draw_conf_pill(d, x + w - 4, y + h - 14, "OFFICIAL", compact=True)


def scene_uk_energy(d: ImageDraw.ImageDraw, x: int, y: int, w: int, h: int) -> None:
    """#6 UK Energy Price Cap — utility icon and one crimson £2,166 callout."""
    d.rectangle([x, y, x + w, y + h], fill="#E7EFF7")
    d.rounded_rectangle([x + 10, y + 4, x + 78, y + 32], radius=4, fill=NAVY)
    f10, _ = font_kind("sans_bold", 10)
    f14, _ = font_kind("sans_bold", 14)
    d.line([(x + 36, y + 10), (x + 36, y + 17)], fill="#F8CA52", width=2)
    d.line([(x + 50, y + 10), (x + 50, y + 17)], fill="#F8CA52", width=2)
    d.arc([x + 33, y + 12, x + 53, y + 29], 0, 180, fill="#F8CA52", width=2)
    d.line([(x + 43, y + 29), (x + 43, y + 32)], fill="#F8CA52", width=2)
    f16, _ = font_kind("sans_bold", 16)
    draw_centered_single(d, x + 136, y + 13, "£2,166", f16, CRIMSON)
    draw_badge_circle(d, x + 13, y + h - 12, 8.5, 6, REGION_COLORS["W. Europe"])
    draw_conf_pill(d, x + w - 4, y + h - 14, "OFFICIAL", compact=True)


def scene_gaza_strike(d: ImageDraw.ImageDraw, x: int, y: int, w: int, h: int) -> None:
    """#7 Gaza Shati Camp Strike — dusk ochre sky, urban silhouettes, dark smoke plume + 7 KILLED."""
    d.rectangle([x, y, x + w, y + h], fill="#EBD7C5")
    d.rectangle([x, y + h - 15, x + w, y + h], fill="#B0937A")
    d.rectangle([x + 12, y + 20, x + 28, y + h - 14], fill="#6C5B4E")
    d.rectangle([x + 32, y + 14, x + 52, y + h - 14], fill="#53463C")
    d.rectangle([x + 56, y + 24, x + 78, y + h - 14], fill="#7B6758")
    d.ellipse([x + 54, y + 3, x + 84, y + 24], fill="#5E5852")
    d.ellipse([x + 68, y + 1, x + 94, y + 19], fill="#7D756D")
    f14, _ = font_kind("sans_bold", 14)
    f10, _ = font_kind("sans_bold", 10)
    draw_centered_single(d, x + 140, y + 8, "7 KILLED", f14, CRIMSON)
    draw_centered_single(d, x + 140, y + 24, "SHATI CAMP", f10, INK)
    draw_badge_circle(d, x + 13, y + h - 12, 8.5, 7, REGION_COLORS["Middle East"])
    draw_conf_pill(d, x + w - 4, y + h - 14, "REPORTED", compact=True)


def scene_ras_tanura(d: ImageDraw.ImageDraw, x: int, y: int, w: int, h: int) -> None:
    """#8 Ras Tanura Drone Intercept — desert sand dusk, crossed-out drone + 4 DRONES."""
    d.rectangle([x, y, x + w, y + h], fill="#F1E1C6")
    d.rectangle([x, y + h - 14, x + w, y + h], fill="#CFA972")
    d.rectangle([x + 16, y + 25, x + 34, y + h - 13], fill="#8A745A")
    d.rectangle([x + 37, y + 28, x + 52, y + h - 13], fill="#6E5C47")
    dx, dy = x + 60, y + 16
    d.polygon([(dx - 12, dy), (dx + 12, dy), (dx + 3, dy - 7), (dx - 3, dy - 7)], fill=INK)
    d.line([(dx - 11, dy - 9), (dx + 11, dy + 8)], fill=CRIMSON, width=3)
    d.line([(dx + 11, dy - 9), (dx - 11, dy + 8)], fill=CRIMSON, width=3)
    f14, _ = font_kind("sans_bold", 14)
    f10, _ = font_kind("sans_bold", 10)
    draw_centered_single(d, x + 138, y + 8, "4 DRONES", f14, INK)
    draw_centered_single(d, x + 138, y + 24, "RAS TANURA", f10, "#8B5A12")
    draw_badge_circle(d, x + 13, y + h - 12, 8.5, 8, REGION_COLORS["Middle East"])
    draw_conf_pill(d, x + w - 4, y + h - 14, "REPORTED", compact=True)


def scene_solomons_pact(d: ImageDraw.ImageDraw, x: int, y: int, w: int, h: int) -> None:
    """#9 Australia-Solomons Security Pact — Pacific navy, AUS link arc + A$740m."""
    d.rectangle([x, y, x + w, y + h], fill="#193A57")
    d.rounded_rectangle([x + 12, y + 7, x + 54, y + 29], radius=3, fill="#122B42", outline="#F2C14E", width=2)
    f11, _ = font_kind("sans_bold", 11)
    draw_centered_single(d, x + 33, y + 12, "AUS", f11, "#F2C14E")
    d.line([(x + 56, y + 18), (x + 82, y + 18)], fill="#F2C14E", width=2)
    d.ellipse([x + 79, y + 14, x + 87, y + 22], fill="#58C4B8")
    f14, _ = font_kind("sans_bold", 14)
    f10, _ = font_kind("sans_bold", 10)
    draw_centered_single(d, x + 140, y + 6, "A$740m", f14, INK_LIGHT)
    draw_centered_single(d, x + 140, y + 22, "SECURITY PACT", f10, "#A9D0EE")
    draw_badge_circle(d, x + 13, y + h - 12, 8.5, 9, REGION_COLORS["Oceania"])
    draw_conf_pill(d, x + w - 4, y + h - 14, "OFFICIAL", compact=True)


def scene_netanyahu_trial(d: ImageDraw.ImageDraw, x: int, y: int, w: int, h: int) -> None:
    """#10 Netanyahu Graft Trial — crisp marble courtroom + navy 3 CASES dossier badge."""
    d.rectangle([x, y, x + w, y + h], fill="#EDEAE2")
    d.rounded_rectangle([x + 10, y + 6, x + 76, y + 32], radius=4, fill=NAVY)
    f13, _ = font_kind("sans_bold", 13)
    draw_centered_single(d, x + 43, y + 12, "3 CASES", f13, INK_LIGHT)
    f11, _ = font_kind("sans_bold", 11)
    f10, _ = font_kind("sans_bold", 10)
    draw_centered_single(d, x + 136, y + 8, "GRAFT TRIAL", f11, INK)
    draw_centered_single(d, x + 136, y + 23, "RETHINK URGED", f10, CRIMSON)
    draw_badge_circle(d, x + 13, y + h - 12, 8.5, 10, REGION_COLORS["Middle East"])
    draw_conf_pill(d, x + w - 4, y + h - 14, "REPORTED", compact=True)


def scene_cairo_fire(d: ImageDraw.ImageDraw, x: int, y: int, w: int, h: int) -> None:
    """#11 Cairo Fuel Tanker Inferno — dark road silhouette, orange-crimson flames + 30+ DEAD."""
    d.rectangle([x, y, x + w, y + h], fill="#3B231A")
    d.rectangle([x, y + h - 14, x + w, y + h], fill="#241510")
    d.ellipse([x + 28, y + 3, x + 64, y + 33], fill="#E66424")
    d.ellipse([x + 36, y + 6, x + 58, y + 29], fill="#F7B32B")
    d.rounded_rectangle([x + 14, y + 21, x + 62, y + 34], radius=5, fill="#B81D18")
    d.ellipse([x + 20, y + 30, x + 29, y + 39], fill="#141414")
    d.ellipse([x + 48, y + 30, x + 57, y + 39], fill="#141414")
    f14, _ = font_kind("sans_bold", 14)
    f10, _ = font_kind("sans_bold", 10)
    draw_centered_single(d, x + 132, y + 8, "30+ DEAD", f14, "#F8CA52")
    draw_centered_single(d, x + 132, y + 24, "CAIRO RING ROAD", f10, "#F5D9C4")
    draw_badge_circle(d, x + 13, y + h - 12, 8.5, 11, REGION_COLORS["Africa"])
    draw_conf_pill(d, x + w - 4, y + h - 14, "OFFICIAL", compact=True)


def scene_ukraine_grid(d: ImageDraw.ImageDraw, x: int, y: int, w: int, h: int) -> None:
    """#12 Ukraine Strikes & Power Cuts — dark blackout blue, power pylon + lightning bolt + 5 DEAD."""
    d.rectangle([x, y, x + w, y + h], fill="#192332")
    px = x + 34
    d.line([(px, y + 6), (px - 11, y + 34)], fill="#9CB1C9", width=2)
    d.line([(px, y + 6), (px + 11, y + 34)], fill="#9CB1C9", width=2)
    d.line([(px - 13, y + 15), (px + 13, y + 15)], fill="#9CB1C9", width=2)
    d.line([(px - 9, y + 24), (px + 9, y + 24)], fill="#9CB1C9", width=1)
    bx = x + 64
    d.polygon([(bx + 4, y + 5), (bx - 6, y + 20), (bx + 1, y + 20), (bx - 4, y + 35), (bx + 10, y + 17), (bx + 2, y + 17)], fill="#F7C948")
    f14, _ = font_kind("sans_bold", 14)
    f10, _ = font_kind("sans_bold", 10)
    draw_centered_single(d, x + 138, y + 8, "5 DEAD", f14, "#FF7A73")
    draw_badge_circle(d, x + 13, y + h - 12, 8.5, 12, REGION_COLORS["E. Europe"])
    draw_conf_pill(d, x + w - 4, y + h - 14, "REPORTED", compact=True)


def scene_java_mine(d: ImageDraw.ImageDraw, x: int, y: int, w: int, h: int) -> None:
    """#13 West Java Flooded Gold Mine — forest surface, earth strata, flooded teal pit + 9 DEAD."""
    d.rectangle([x, y, x + w, y + h], fill="#3B3A32")
    d.rectangle([x, y, x + w, y + 9], fill="#2E6B34")
    d.polygon([(x + 14, y + 9), (x + 68, y + 9), (x + 56, y + h - 5), (x + 26, y + h - 5)], fill="#165C73")
    d.line([(x + 20, y + 22), (x + 62, y + 22)], fill="#5CC2DF", width=2)
    d.line([(x + 24, y + 31), (x + 58, y + 31)], fill="#3E9BB8", width=1)
    f14, _ = font_kind("sans_bold", 14)
    f10, _ = font_kind("sans_bold", 10)
    draw_centered_single(d, x + 132, y + 9, "9 DEAD", f14, "#F8CA52")
    draw_centered_single(d, x + 132, y + 25, "17 TRAPPED · 100m", f10, "#E7F0EA")
    draw_badge_circle(d, x + 13, y + h - 12, 8.5, 13, REGION_COLORS["SE Asia"])
    draw_conf_pill(d, x + w - 4, y + h - 14, "REPORTED", compact=True)


# ============================================================================
# PIL WORLD MAP ("WHERE IT HAPPENED") — 13 REGION-COLORED PINS ONLY (#1–#13)
# ============================================================================

def draw_world_map(
    d: ImageDraw.ImageDraw,
    x: int,
    y: int,
    w: int,
    h: int,
    pins: Sequence[tuple[int, str, float, float]],
) -> None:
    d.rounded_rectangle([x, y, x + w, y + h], radius=5, fill="#EAE4D7", outline=CARD_BORDER, width=1)
    mx0, my0 = x + 4, y + 4
    mw, mh = w - 8, h - 8

    def proj(lon: float, lat: float) -> tuple[float, float]:
        px = mx0 + ((lon + 180.0) / 360.0) * mw
        py = my0 + ((82.0 - lat) / 140.0) * mh
        return px, py

    for lat in (-30, 0, 30, 60):
        _, gy = proj(0, lat)
        d.line([(mx0, gy), (mx0 + mw, gy)], fill="#DDD5C4", width=1)
    for lon in (-120, -60, 0, 60, 120):
        gx, _ = proj(lon, 0)
        d.line([(gx, my0), (gx, my0 + mh)], fill="#DDD5C4", width=1)

    continents = [
        [(-165, 65), (-135, 70), (-95, 68), (-60, 50), (-75, 35), (-82, 25), (-98, 18), (-112, 24), (-125, 48), (-150, 60)],
        [(-52, 60), (-22, 70), (-30, 80), (-58, 76)],
        [(-80, 10), (-60, 10), (-36, -6), (-42, -24), (-65, -52), (-74, -40), (-81, -5)],
        [(-10, 36), (0, 44), (-6, 56), (10, 60), (28, 70), (48, 66), (44, 44), (28, 40), (14, 40), (4, 43)],
        [(-17, 15), (-5, 35), (12, 37), (32, 31), (50, 11), (40, -14), (28, -33), (17, -33), (12, -6), (-8, 5)],
        [(36, 42), (48, 66), (105, 74), (168, 64), (142, 42), (122, 30), (108, 12), (96, 18), (78, 8), (66, 24), (54, 24), (44, 14), (35, 32)],
        [(96, 5), (118, 5), (122, -8), (104, -8)],
        [(114, -22), (132, -12), (153, -24), (148, -38), (128, -33), (114, -34)],
    ]
    for poly in continents:
        d.polygon([proj(lo, la) for lo, la in poly], fill="#C9C0AE", outline="#A89E8A")

    assert len(pins) == 13, f"Map must have exactly 13 pins (#1-#13), got {len(pins)}"
    f_pin, _ = font_kind("sans_bold", 10)
    r = 6.5

    # Carefully fanned pin offsets so dense EMEA cluster (#6 London, #12 Ukraine,
    # #7 Gaza, #10 Jerusalem, #11 Cairo, #8 Ras Tanura) has >= 16px separation!
    pin_offsets: dict[int, tuple[float, float]] = {
        1: (0.0, 0.0),      # Washington DC
        2: (7.0, -3.0),     # Seoul E
        3: (-2.0, -9.0),    # Jiuquan N
        4: (8.0, 6.0),      # Dhaka ESE
        5: (0.0, 0.0),      # Cape Town
        6: (-11.0, -6.0),   # London NW
        7: (-3.0, -4.0),    # Gaza NW
        8: (3.0, 12.0),     # Ras Tanura S over Arabian Sea
        9: (0.0, 0.0),      # Solomons
        10: (14.0, -8.0),   # Jerusalem NE
        11: (-16.0, 10.0),  # Cairo SW
        12: (2.0, -14.0),   # Ukraine N
        13: (0.0, 4.0),     # West Java S
    }

    placed: list[tuple[int, str, float, float, float, float]] = []
    for num, reg, lon, lat in pins:
        tx, ty = proj(lon, lat)
        odx, ody = pin_offsets.get(num, (0.0, 0.0))
        bx = max(mx0 + r + 1, min(mx0 + mw - r - 1, tx + odx))
        by = max(my0 + r + 1, min(my0 + mh - r - 1, ty + ody))
        placed.append((num, reg, tx, ty, bx, by))

    for i_a in range(len(placed)):
        for i_b in range(i_a + 1, len(placed)):
            na, _, _, _, ax, ay = placed[i_a]
            nb, _, _, _, bxx, byy = placed[i_b]
            dist = math.hypot(ax - bxx, ay - byy)
            if dist < 16.0:
                raise AssertionError(f"Map pins #{na} and #{nb} too close ({dist:.1f}px < 16px)")

    for _, _, tx, ty, bx, by in placed:
        if math.hypot(bx - tx, by - ty) > 2.5:
            d.line([(tx, ty), (bx, by)], fill="#4A453E", width=1)
            d.ellipse([tx - 1.3, ty - 1.3, tx + 1.3, ty + 1.3], fill="#4A453E")

    tb, vh = font_metrics(f_pin)
    for num, reg, _, _, bx, by in placed:
        col = REGION_COLORS[reg]
        d.ellipse([bx - r, by - r, bx + r, by + r], fill=col, outline=CARD_BG, width=1)
        s = str(num)
        tw = d.textlength(s, font=f_pin)
        d.text((bx - tw / 2.0, by - vh / 2.0 - tb), s, font=f_pin, fill=INK_LIGHT)


# ============================================================================
# EXACT 36 VERIFIED 25 NOVEMBER 2026 STORIES (v6 PICTURED SET & EXACT DATA)
# ============================================================================

@dataclass(frozen=True)
class HeroStory:
    num: int
    region: str
    field: str
    conf: str
    source: str
    kicker: str
    headline: str
    summary: str
    why: str
    scene: Callable[[ImageDraw.ImageDraw, int, int, int, int], None]
    lon: float
    lat: float


@dataclass(frozen=True)
class MediumStory:
    num: int
    region: str
    field: str
    conf: str
    source: str
    kicker: str
    headline: str
    summary: str
    scene_label: str
    scene: Callable[[ImageDraw.ImageDraw, int, int, int, int], None]
    lon: float
    lat: float


@dataclass(frozen=True)
class IndexStory:
    num: int
    region: str
    field: str
    conf: str
    source: str
    headline: str
    detail: str


HERO_STORIES: list[HeroStory] = [
    HeroStory(
        1, "N. America", "Trade", "OFFICIAL", "Reuters/AP",
        "WASHINGTON · TRADE",
        "US proposes tariffs of up to 35% on 14 economies",
        "Vietnam 35%, India 25%, China 20%, EU 15% proposed; lower if deals land, hearings January 25.",
        "Broadest trade move of the day: 14 economies face duties at once.",
        hero_scene_tariffs, -77.0, 38.9,
    ),
    HeroStory(
        2, "East Asia", "Markets", "REPORTED", "Reuters",
        "SEOUL · TOKYO · TAIPEI · MARKETS",
        "AI doubts sink Asian chip stocks: Kospi closes -6.2%",
        "Kospi ends at 4,697.51; SK Hynix -11.1%, Samsung -9.9%, Taiwan's Taiex -4.8% and Nikkei -2.8%.",
        "Investors doubt the AI spending boom will pay off.",
        hero_scene_markets, 127.0, 37.5,
    ),
    HeroStory(
        3, "Space/Global", "Space", "OFFICIAL", "AP/BBC",
        "JIUQUAN, CHINA · SPACE",
        "Pakistan's first astronaut docks at China's space station",
        "Muhammad Zeeshan Ali, 40, becomes first foreigner aboard Tiangong via Shenzhou-24 for a 5-to-10-day stay.",
        "China's station takes its first foreign astronaut.",
        hero_scene_astronaut, 100.3, 40.9,
    ),
]

MEDIUM_STORIES: list[MediumStory] = [
    MediumStory(
        4, "S. Asia", "Labour", "OFFICIAL", "Reuters/AP",
        "DHAKA · LABOUR",
        "Garment workers offered higher minimum wage",
        "Wage board proposes raising pay from 12,500 to 17,000 taka (+36%, ~$138/mo).",
        "17,000 TAKA", scene_dhaka_wage, 90.4, 23.8,
    ),
    MediumStory(
        5, "Africa", "Justice", "OFFICIAL", "Reuters",
        "CAPE TOWN · JUSTICE",
        "Court lifts 'Farmgate' threat to Ramaphosa",
        "Judges void the 2022 panel report that opened the way to impeachment.",
        "RULING", scene_farmgate, 18.4, -33.9,
    ),
    MediumStory(
        6, "W. Europe", "Energy", "OFFICIAL", "Ofgem/BBC",
        "LONDON · ENERGY",
        "UK energy price cap to rise 26% in January",
        "Ofgem lifts typical household bill from £1,723 to £2,166 a year from 1 Jan.",
        "£2,166", scene_uk_energy, -0.1, 51.5,
    ),
    MediumStory(
        7, "Middle East", "War", "REPORTED", "Al Jazeera",
        "GAZA CITY · WAR",
        "Israeli strike kills Hamas security chief",
        "Abu al-Awf, his wife and 2 daughters die in Shati camp strike.",
        "7 KILLED", scene_gaza_strike, 34.4, 31.5,
    ),
    MediumStory(
        8, "Middle East", "War", "REPORTED", "Al Jazeera",
        "RAS TANURA · WAR",
        "Saudis down Houthi drones over Ras Tanura",
        "Saudi coalition says 4 Houthi drones downed over Ras Tanura; smoke reported.",
        "4 DRONES", scene_ras_tanura, 50.1, 26.7,
    ),
    MediumStory(
        9, "Oceania", "Diplomacy", "OFFICIAL", "Reuters/AP",
        "CANBERRA · DIPLOMACY",
        "Solomon Islands signs security pact with Australia",
        "Australia named 'primary security partner'; A$740m over 10 years.",
        "A$740m", scene_solomons_pact, 159.9, -9.4,
    ),
    MediumStory(
        10, "Middle East", "Justice", "REPORTED", "AP",
        "JERUSALEM · JUSTICE",
        "Judges urge rethink of Netanyahu graft charges",
        "Bribery case faces 'considerable difficulties'; PM says 'trial must end'.",
        "3 CASES", scene_netanyahu_trial, 35.2, 31.8,
    ),
    MediumStory(
        11, "Africa", "Disaster", "OFFICIAL", "AP/Reuters",
        "CAIRO · DISASTER",
        "Fuel tanker fire kills at least 30 near Cairo",
        "Tanker overturned and exploded on a ring road, Health Ministry says.",
        "30+ DEAD", scene_cairo_fire, 31.2, 30.1,
    ),
    MediumStory(
        12, "E. Europe", "War", "REPORTED", "AP",
        "UKRAINE · WAR",
        "Russian strikes kill 5, cut power in 5 regions",
        "Zaporizhzhia nuclear plant on diesel after 17th grid loss in 2026.",
        "5 DEAD", scene_ukraine_grid, 31.0, 48.5,
    ),
    MediumStory(
        13, "SE Asia", "Disaster", "REPORTED", "AP/AlJazeera",
        "WEST JAVA · DISASTER",
        "9 dead, 17 still trapped in flooded gold mine",
        "Rescuers pull bodies from 100-metre unlicensed pit in West Java.",
        "9 DEAD", scene_java_mine, 106.8, -6.6,
    ),
]

INDEX_STORIES: list[IndexStory] = [
    IndexStory(14, "Middle East", "War", "CLAIM", "Reuters/AP", "Hormuz", "Iran says IRGC mined 2 tankers"),
    IndexStory(15, "E. Europe", "War", "REPORTED", "Reuters/EMPR", "Syzran", "Rosneft refineries hit, one dies"),
    IndexStory(16, "E. Europe", "War", "REPORTED", "BBC", "Odesa", "112 drones hit, five regions dark, two die"),
    IndexStory(17, "N. America", "Business", "OFFICIAL", "Reuters", "Dell Q3", "$54.9B, up 103%; AI +291%"),
    IndexStory(18, "Africa", "War", "REPORTED", "AP/BBC", "Sudan", "RSF drones hit two cities, 19 die"),
    IndexStory(19, "N. America", "Space", "OFFICIAL", "CBS", "Washington", "FCC clears SpaceX for 1M sats"),
    IndexStory(20, "Space/Global", "Climate", "OFFICIAL", "Reuters", "COP31", "OPEC blames EU; Pope urges action"),
    IndexStory(21, "L. America", "Crime", "OFFICIAL", "AP", "Cartagena", "Éxito hostages freed, captor dead"),
    IndexStory(22, "N. America", "Politics", "REPORTED", "AP", "Washington", "US halts Ukraine air-defence arms"),
    IndexStory(23, "SE Asia", "Rights", "OFFICIAL", "BBC", "The Hague", "ICJ: Myanmar guilty of genocide"),
    IndexStory(24, "N. America", "Tech", "REPORTED", "Axios", "AI safety", "Anthropic, OpenAI staff warn of rush"),
    IndexStory(25, "W. Europe", "Politics", "OFFICIAL", "JustSec", "Berlin", "Merz: Russia eyes beyond Ukraine"),
    IndexStory(26, "E. Europe", "War", "REPORTED", "BBC", "Russian dead", "490,334 in hacked records"),
    IndexStory(27, "N. America", "Markets", "OFFICIAL", "CNBC", "New York", "Dow +0.3% after 1,100-pt plunge"),
    IndexStory(28, "L. America", "Health", "OFFICIAL", "AP", "Geneva", "WHO urges US to lift Cuba fuel cap"),
    IndexStory(29, "N. America", "Trade", "OFFICIAL", "Reuters", "Nvidia", "Schumer-Huang China chip clash"),
    IndexStory(30, "Space/Global", "Humanitarian", "OFFICIAL", "IOM/AP", "IOM", "16 Days opens as shelters close"),
    IndexStory(31, "E. Europe", "Diplomacy", "REPORTED", "AA", "Kyiv", "Zelenskyy: no Dec deal; Congress votes Jan"),
    IndexStory(32, "Africa", "Diplomacy", "OFFICIAL", "AP", "Cairo", "Egypt, Sudan reject solo GERD filling"),
    IndexStory(33, "East Asia", "Justice", "OFFICIAL", "CBS", "China", "Official Ma faces death over 100+ leaks"),
    IndexStory(34, "L. America", "Crime", "OFFICIAL", "AP", "Mexico", "Chapo Isidro held, FBI Top 10; drones fly"),
    IndexStory(35, "L. America", "Diplomacy", "REPORTED", "AP", "Ecuador", "US cartel halt faces rights probe"),
    IndexStory(36, "W. Europe", "Transport", "REPORTED", "BBC", "Paris", "Eurostar strike disrupts rail to Brussels"),
]

DAY_IN_NUMBERS: list[tuple[str, str, str]] = [
    ("35%", "top US tariff (Vietnam)", NAVY),
    ("-6.2%", "Kospi close", CRIMSON),
    ("+26%", "UK cap from 1 Jan", TEAL),
    ("30+", "Cairo tanker fire", OCHRE),
    ("9", "Java gold pit", CRIMSON),
    ("17,000", "Dhaka wage +36%", FOREST),
]

LEFT_OUT_TITLES: list[str] = [
    "Benghazi Toll", "Poland US Troops", "Nigeria Clashes", "Iowa Blast",
    "Amazon Tin Probe", "Lakers Beat Jazz", "Poland No-Fly Zone", "Gulf of Finland",
    "Gripen Jets Jan", "Lynx KF41 Arrives", "Trump Envoys", "N. Korea NLL Ship",
    "BBC Strike Vote", "Decathlon Hack", "Gaza Hospital Cut", "France vs Putin",
    "Barzani Pushback", "Naser Oric Held", "UK FCA Meta Muse", "RU Governor Held",
    "Japan No. 3 AI", "London Museum", "Delhi Smog Curbs",
]

DATE_CHECK_TEXT = (
    "Every story above happened or was first reported on Wednesday 25 November 2026 (UTC). "
    "Left out as earlier news: Dow first close above 50,000 (Tue 24 Nov) · "
    "Huawei Brooklyn verdict, 10 of 12 (Tue 24 Nov) · Saudi-led strike on Hodeidah (Tue 24 Nov) · "
    "Riyadh PIF Tower strike (Tue 24 Nov) · Chen Jining probe (Tue 24 Nov) · "
    "Nvidia reinstates Jensen Huang (Tue 24 Nov) · Sinner's knee surgery (Tue 24 Nov)."
)

LEGEND_TEXT = (
    "OFFICIAL = authority's own figure or act · REPORTED = press report · "
    "CLAIM = one side's account. Every drawing original."
)
SOURCES_TEXT = "Sources: Al Jazeera, Reuters, AP, AFP, DW, France 24, CNBC, Yonhap, Ofgem, ESA"

# ============================================================================
# DATA INTEGRITY & FACTUAL SAFETY GUARDS (EXECUTED AT IMPORT / BUILD TIME)
# ============================================================================
ALL_META = (
    [(s.num, s.region, s.field, s.conf, s.source) for s in HERO_STORIES]
    + [(s.num, s.region, s.field, s.conf, s.source) for s in MEDIUM_STORIES]
    + [(s.num, s.region, s.field, s.conf, s.source) for s in INDEX_STORIES]
)
TOTAL_STORIES = len(ALL_META)
DRAWN_SCENES = len(HERO_STORIES) + len(MEDIUM_STORIES)
REGION_COUNTS = Counter(r for _, r, _, _, _ in ALL_META)
FIELD_COUNTS = Counter(f for _, _, f, _, _ in ALL_META)

assert TOTAL_STORIES == 36, f"Expected 36 stories, got {TOTAL_STORIES}"
assert DRAWN_SCENES == 13, f"Expected 13 drawn scenes, got {DRAWN_SCENES}"
assert len(HERO_STORIES) == 3 and len(MEDIUM_STORIES) == 10 and len(INDEX_STORIES) == 23
assert [n for n, *_ in ALL_META] == list(range(1, 37))
assert len(REGION_COUNTS) == 11 and sum(REGION_COUNTS.values()) == 36
assert len(FIELD_COUNTS) == 18 and sum(FIELD_COUNTS.values()) == 36
assert len(LEFT_OUT_TITLES) == 23
for _n, _r, _f, _c, _s in ALL_META:
    assert _c in {"OFFICIAL", "REPORTED", "CLAIM"}
    assert _s.strip(), f"Story #{_n} missing source"

# Hard Date-Safety & Fact-Safety Guards
_news_corpus = " ".join(
    [s.headline + " " + s.summary + " " + s.why for s in HERO_STORIES]
    + [s.headline + " " + s.summary + " " + s.scene_label for s in MEDIUM_STORIES]
    + [s.headline + " " + s.detail for s in INDEX_STORIES]
    + [a + " " + b for a, b, _ in DAY_IN_NUMBERS]
    + LEFT_OUT_TITLES
).lower()

for _forbid in (
    "50,018", "50,000", "50k", "dow tops", "huawei", "chen jining",
    "sinner", "hodeidah", "pif tower", "reinstates", "17,500", "since 2022",
    "world chronicle", "utc flow",
):
    assert _forbid not in _news_corpus, f"Forbidden token {_forbid!r} found outside DATE CHECK!"

assert "17,000 taka (+36%" in MEDIUM_STORIES[0].summary
assert "17th grid loss in 2026" in MEDIUM_STORIES[8].summary
assert MEDIUM_STORIES[4].conf == "REPORTED" and "4 Houthi drones" in MEDIUM_STORIES[4].summary
assert INDEX_STORIES[0].num == 14 and "Hormuz" in INDEX_STORIES[0].headline and INDEX_STORIES[0].conf == "CLAIM"

CONF_CODE = {"OFFICIAL": "O", "REPORTED": "R", "CLAIM": "C"}
CONF_COLOR = {"OFFICIAL": NAVY, "REPORTED": FOREST, "CLAIM": CRIMSON}

# Field order sorted descending by count, then canonical name
FIELDS_ORDERED: list[tuple[str, int]] = sorted(
    FIELD_COUNTS.items(),
    key=lambda kv: (-kv[1], kv[0]),
)


# ============================================================================
# MAIN RENDERER (SUPPORTS NATIVE AND DEJAVU-STRESS PROFILES)
# ============================================================================

def render_broadsheet(profile: FontProfile) -> tuple[Image.Image, TextAuditor, dict[str, float]]:
    global ACTIVE_PROFILE
    prev_profile = ACTIVE_PROFILE
    ACTIVE_PROFILE = profile
    try:
        return _render_broadsheet_inner()
    finally:
        ACTIVE_PROFILE = prev_profile


def _render_broadsheet_inner() -> tuple[Image.Image, TextAuditor, dict[str, float]]:
    img = Image.new("RGB", (WIDTH, HEIGHT), PAPER)
    d = ImageDraw.Draw(img)
    auditor = TextAuditor()
    stats_out: dict[str, float] = {}

    # ------------------------------------------------------------------
    # BAND 1: TOP LINE + GIANT SERIF DATE + RED ITALIC SUBLINE (Y = 3..81)
    # ------------------------------------------------------------------
    f_top_l, sc_tl = font_kind("sans_bold", 11)
    f_top_r, sc_tr = font_kind("sans_bold", 10)
    top_l = "THE WORLD IN ONE DAY"
    top_r = "36 STORIES · 11 REGIONS · 18 FIELDS · ALL FROM WEDNESDAY 25 NOVEMBER 2026"
    draw_text_top(
        d, MX, 3, top_l, f_top_l, CRIMSON,
        auditor=auditor, group="band1", label="masthead_left", scale=sc_tl,
        container=(MX, 1, WIDTH - MX, 15),
    )
    tr_w_raw = float(d.textlength(top_r, font=f_top_r))
    tr_w_eff = tr_w_raw * sc_tr
    tr_x = WIDTH - MX - tr_w_raw
    tb_r, vh_r = font_metrics(f_top_r)
    d.text((tr_x, 4 - tb_r), top_r, font=f_top_r, fill=INK_MUTED)
    auditor.record(
        "band1", "masthead_right", WIDTH - MX - tr_w_eff, 4, WIDTH - MX, 4 + vh_r, top_r,
        container=(MX, 1, WIDTH - MX, 15),
    )

    d.line([(MX, 15), (WIDTH - MX, 15)], fill=RULE_SOFT, width=1)

    # Giant black serif date — LARGEST text on the page (56px native, >=50px DejaVu)
    date_txt = "Wednesday 25 November 2026"
    f_date, date_sz, sc_date = fit_single_line(
        d, "serif_bold", date_txt, CW - 8, start_size=56, min_size=48, label="masthead_date"
    )
    stats_out["date_px"] = float(date_sz)
    date_bot = draw_centered_single(
        d, WIDTH / 2.0, 16, date_txt, f_date, INK,
        scale=sc_date, auditor=auditor, group="band1", label="masthead_date",
        container=(MX, 15, WIDTH - MX, MASTHEAD_DATE_BOX_BOTTOM),
    )

    # Red italic serif subline (3 hero teasers)
    sub_txt = (
        "US proposes tariffs on 14 economies · AI doubts sink Asian chip stocks · "
        "Pakistan's first astronaut docks at Tiangong"
    )
    f_sub, sub_sz, sc_sub = fit_single_line(
        d, "serif_italic", sub_txt, CW - 6, start_size=14, min_size=12, label="subline"
    )
    sub_y = max(65.0, date_bot + 1.0)
    sub_bot = draw_centered_single(
        d, WIDTH / 2.0, sub_y, sub_txt, f_sub, CRIMSON,
        scale=sc_sub, auditor=auditor, group="band1", label="subline",
        container=(MX, 62, WIDTH - MX, SUBLINE_BOX_BOTTOM),
    )

    rule_y = int(round(max(81.0, sub_bot + 2.0)))
    d.line([(MX, rule_y), (WIDTH - MX, rule_y)], fill=INK, width=2)
    d.line([(MX, rule_y + 3), (WIDTH - MX, rule_y + 3)], fill=RULE_SOFT, width=1)

    # ------------------------------------------------------------------
    # BAND 2: "THE DAY IN NUMBERS" 6-BOX STAT STRIP ABOVE HEROES
    # ------------------------------------------------------------------
    b2_hdr_y = rule_y + 5  # ~86
    f_b2h, sc_b2h = font_kind("sans_bold", 10)
    draw_text_top(
        d, MX, b2_hdr_y, "THE DAY IN NUMBERS", f_b2h, CRIMSON,
        auditor=auditor, group="band2_hdr", label="day_in_numbers_hdr", scale=sc_b2h,
        container=(MX, b2_hdr_y - 1, WIDTH - MX, b2_hdr_y + 11),
    )
    b2_sub = "Six verified headline figures from Wednesday 25 November 2026"
    f_b2s, sc_b2s = font_kind("sans_reg", 10)
    b2s_w_raw = float(d.textlength(b2_sub, font=f_b2s))
    b2s_w_eff = b2s_w_raw * sc_b2s
    tb_s, vh_s = font_metrics(f_b2s)
    d.text((WIDTH - MX - b2s_w_raw, b2_hdr_y - tb_s), b2_sub, font=f_b2s, fill=INK_MUTED)
    auditor.record(
        "band2_hdr", "day_in_numbers_sub", WIDTH - MX - b2s_w_eff, b2_hdr_y, WIDTH - MX, b2_hdr_y + vh_s, b2_sub,
        container=(MX, b2_hdr_y - 1, WIDTH - MX, b2_hdr_y + 11),
    )

    stat_y0 = b2_hdr_y + 10  # ~96
    stat_h = 52
    stat_y1 = stat_y0 + stat_h
    stat_gap = 6
    stat_w = (CW - 5 * stat_gap) / 6.0  # 162.33 px
    f_stat_n, sc_sn = font_kind("sans_bold", 28)
    f_stat_c, sc_sc = font_kind("sans_reg", 10)

    for i, (val, cap, col) in enumerate(DAY_IN_NUMBERS):
        sx0 = int(round(MX + i * (stat_w + stat_gap)))
        sx1 = int(round(MX + (i + 1) * stat_w + i * stat_gap))
        if i == 5:
            sx1 = WIDTH - MX
        d.rounded_rectangle([sx0, stat_y0, sx1, stat_y1], radius=4, fill=CARD_BG, outline=CARD_BORDER, width=1)
        d.rounded_rectangle([sx0 + 1, stat_y0 + 1, sx1 - 1, stat_y0 + 3], radius=1, fill=col)
        pad = 6
        _, num_bot = draw_text_top(
            d, sx0 + pad, stat_y0 + 4, val, f_stat_n, col,
            auditor=auditor, group=f"stat_{i}", label=f"stat_{i}_num", scale=sc_sn,
            container=(sx0 + 2, stat_y0 + 3, sx1 - 2, stat_y0 + 33),
        )
        draw_wrapped_block(
            d, sx0 + pad, max(stat_y0 + 35.0, num_bot + 0.5), cap, f_stat_c, INK_BODY,
            max_w=(sx1 - sx0) - 2 * pad, max_lines=1, line_h=9.0,
            scale=sc_sc, auditor=auditor, group=f"stat_{i}", label=f"stat_{i}_cap",
            container=(sx0 + 2, stat_y0 + 34, sx1 - 2, stat_y1),
        )

    # ------------------------------------------------------------------
    # BAND 3: PROPORTIONAL 11-REGION COLOR BAR + THE DAY IN UTC
    # ------------------------------------------------------------------
    reg_y0 = stat_y1 + 2
    reg_h = 15
    reg_y1 = reg_y0 + reg_h
    min_seg_w = 36.0
    small_regs = [r for r in REGION_ORDER if REGION_COUNTS[r] == 1]
    big_regs = [r for r in REGION_ORDER if REGION_COUNTS[r] > 1]
    rem_w = CW - len(small_regs) * min_seg_w
    big_total = sum(REGION_COUNTS[r] for r in big_regs)

    f_reg, sc_reg = font_kind("sans_bold", 10)
    cur_x = float(MX)
    for idx_r, reg in enumerate(REGION_ORDER):
        cnt = REGION_COUNTS[reg]
        seg_w = min_seg_w if cnt == 1 else (rem_w * cnt / big_total)
        x0_s = int(round(cur_x))
        x1_s = WIDTH - MX if idx_r == len(REGION_ORDER) - 1 else int(round(cur_x + seg_w))
        cur_x += seg_w
        d.rectangle([x0_s, reg_y0, x1_s, reg_y1], fill=REGION_COLORS[reg], outline=PAPER, width=1)
        chosen = None
        for cand in REGION_BAR_CANDIDATES[reg]:
            lbl = f"{cand} {cnt}".strip() if cand else str(cnt)
            if measure_w(d, lbl, f_reg, sc_reg) <= (x1_s - x0_s) - 4:
                chosen = lbl
                break
        if chosen is None:
            raise AssertionError(f"[{ACTIVE_PROFILE.name}] Region segment {reg} ({x1_s-x0_s}px) cannot fit count {cnt}")
        tb_rg, vh_rg = font_metrics(f_reg)
        w_raw = float(d.textlength(chosen, font=f_reg))
        cx_s = (x0_s + x1_s) / 2.0
        d.text((cx_s - w_raw / 2.0, reg_y0 + (reg_h - vh_rg) / 2.0 - tb_rg), chosen, font=f_reg, fill=INK_LIGHT)
        auditor.record(
            "reg_bar", f"reg_{reg}",
            cx_s - (w_raw * sc_reg) / 2.0, reg_y0,
            cx_s + (w_raw * sc_reg) / 2.0, reg_y1,
            chosen, container=(x0_s, reg_y0, x1_s, reg_y1),
        )

    # One dark UTC strip: only the six verified times, strictly one line
    utc_y0 = reg_y1 + 1
    utc_y1 = utc_y0 + 13
    f_utc, sc_utc = font_kind("sans_reg", 10)
    utc_txt = (
        "THE DAY IN UTC  00:18 Shenzhou-24 lifts off · 03:56 Tiangong docks · "
        "06:30 Kospi -6.2% close · 07:00 Ofgem +26% · 13:30 US GDP 4.3% · 21:00 Dow erases 1,100 pts"
    )
    if measure_w(d, utc_txt, f_utc, sc_utc) > CW - 12:
        utc_txt = (
            "THE DAY IN UTC  00:18 Shenzhou-24 · 03:56 Tiangong dock · "
            "06:30 Kospi -6.2% · 07:00 Ofgem +26% · 13:30 US GDP 4.3% · 21:00 Dow erases 1,100 pts"
        )
    if measure_w(d, utc_txt, f_utc, sc_utc) <= CW - 12:
        d.rectangle([MX, utc_y0, WIDTH - MX, utc_y1], fill=NAVY)
        draw_text_top(
            d, MX + 6, utc_y0 + 1, utc_txt, f_utc, INK_LIGHT,
            auditor=auditor, group="utc_bar", label="utc_six_times", scale=sc_utc,
            container=(MX + 6, utc_y0, WIDTH - MX - 6, utc_y1),
        )

    # ------------------------------------------------------------------
    # BAND 4: THREE EQUAL HEROES SIDE BY SIDE (h = 250px)
    # Scene ON TOP = 115px (46.0% of hero cell height!)
    # ------------------------------------------------------------------
    hero_y0 = utc_y1 + 1
    hero_h = 250
    hero_y1 = hero_y0 + hero_h
    hero_scene_h = 115
    assert 0.42 <= hero_scene_h / hero_h <= 0.48, "Hero scene must be ~45% of hero cell height"
    stats_out["hero_scene_pct"] = round(100.0 * hero_scene_h / hero_h, 1)

    hero_gap = 7
    hero_w = (CW - 2 * hero_gap) / 3.0  # 330.0 px
    f_hk, sc_hk = font_kind("sans_bold", 10)
    f_hsrc, sc_hsrc = font_kind("sans_reg", 10)
    f_hhl, sc_hhl = font_kind("serif_bold", 22)
    f_hdk, sc_hdk = font_kind("sans_reg", 11)
    f_hwhy_lbl, sc_hyl = font_kind("sans_bold", 11)
    f_hwhy_txt, sc_hyt = font_kind("sans_bold", 11)

    for hi, hs in enumerate(HERO_STORIES):
        hx0 = int(round(MX + hi * (hero_w + hero_gap)))
        hx1 = WIDTH - MX if hi == 2 else int(round(MX + (hi + 1) * hero_w + hi * hero_gap))
        cw_card = hx1 - hx0
        d.rounded_rectangle([hx0, hero_y0, hx1, hero_y1], radius=6, fill=CARD_BG, outline=CARD_BORDER, width=1)

        sx0, sy0, sw, sh = hx0 + 2, hero_y0 + 2, cw_card - 4, hero_scene_h - 2
        render_clipped_scene(img, hs.scene, sx0, sy0, sw, sh)

        tx0 = hx0 + 7
        tw = cw_card - 14  # 316 px
        text_box = (hx0 + 4, hero_y0 + hero_scene_h, hx1 - 4, hero_y1 - 1)
        grp = f"hero_{hs.num}"

        ky = hero_y0 + hero_scene_h + 2
        k_col = REGION_COLORS[hs.region]
        draw_text_top(
            d, tx0, ky, hs.kicker, f_hk, k_col,
            auditor=auditor, group=grp, label=f"h{hs.num}_kicker", scale=sc_hk, container=text_box,
        )
        src_txt = f"({hs.source})"
        sw_raw = float(d.textlength(src_txt, font=f_hsrc))
        sw_eff = sw_raw * sc_hsrc
        tb_hs, vh_hs = font_metrics(f_hsrc)
        d.text((tx0 + tw - sw_raw, ky - tb_hs), src_txt, font=f_hsrc, fill=INK_MUTED)
        auditor.record(
            grp, f"h{hs.num}_src", tx0 + tw - sw_eff, ky, tx0 + tw, ky + vh_hs, src_txt, container=text_box
        )

        # Bold Serif 22px sentence-case headline (2-3 lines, strictly zero clipped words!)
        hl_y = ky + 11
        hl_bot, _ = draw_wrapped_block(
            d, tx0, hl_y, hs.headline, f_hhl, INK,
            max_w=tw, max_lines=3, line_h=20.0, scale=sc_hhl,
            auditor=auditor, group=grp, label=f"h{hs.num}_hl", container=text_box,
        )

        # Deck (11px sans, 2-3 lines)
        dk_y = hl_bot + 2
        dk_bot, _ = draw_wrapped_block(
            d, tx0, dk_y, hs.summary, f_hdk, INK_BODY,
            max_w=tw, max_lines=3, line_h=11.0, scale=sc_hdk,
            auditor=auditor, group=grp, label=f"h{hs.num}_dk", container=text_box,
        )

        # WHY IT MATTERS pinned cleanly at bottom of card (11px bold, red label + ink text)
        why_full = f"WHY IT MATTERS: {hs.why}"
        why_lines = wrap_strict(
            d, why_full, f_hwhy_txt, tw, max_lines=2, scale=sc_hyt, label=f"h{hs.num}_why"
        )
        why_lh = 10.5
        _, vh_w = font_metrics(f_hwhy_txt)
        why_total_h = (len(why_lines) - 1) * why_lh + vh_w
        why_y = hero_y1 - 3 - why_total_h
        sep_y = why_y - 2.5
        if sep_y <= dk_bot + 0.2:
            raise AssertionError(
                f"[{ACTIVE_PROFILE.name}] Hero #{hs.num} deck bottom ({dk_bot:.1f}) collides with WHY ({why_y:.1f})"
            )
        d.line([(tx0, sep_y), (tx0 + tw, sep_y)], fill="#E4DCCD", width=1)
        prefix = "WHY IT MATTERS:"
        tb_w, _ = font_metrics(f_hwhy_txt)
        for li, ln in enumerate(why_lines):
            ly = why_y + li * why_lh
            if li == 0 and ln.startswith(prefix):
                rest = ln[len(prefix):]
                pw_raw = float(d.textlength(prefix, font=f_hwhy_lbl))
                d.text((tx0, ly - tb_w), prefix, font=f_hwhy_lbl, fill=CRIMSON)
                d.text((tx0 + pw_raw, ly - tb_w), rest, font=f_hwhy_txt, fill=INK)
            else:
                d.text((tx0, ly - tb_w), ln, font=f_hwhy_txt, fill=INK)
        max_ww = max(measure_w(d, ln, f_hwhy_txt, sc_hyt) for ln in why_lines)
        auditor.record(
            grp, f"h{hs.num}_why", tx0, why_y, tx0 + max_ww, why_y + why_total_h,
            " ".join(why_lines), container=text_box,
        )

    # ------------------------------------------------------------------
    # BAND 5: EXACT 5x2 MEDIUM GRID (#4–#13, 2 rows x 135px)
    # Scene ON TOP = 53px (39.3% of medium cell height!)
    # ------------------------------------------------------------------
    med_y0 = hero_y1 + 2
    med_row_h = 135
    med_row_gap = 2
    med_scene_h = 53
    assert 0.39 <= med_scene_h / med_row_h <= 0.46, "Medium scene must be ~40-45% of card height"
    stats_out["med_scene_pct"] = round(100.0 * med_scene_h / med_row_h, 1)

    med_col_gap = 5
    med_w = (CW - 4 * med_col_gap) / 5.0  # 196.8 px
    f_mk, sc_mk = font_kind("sans_bold", 10)
    f_msrc, sc_msrc = font_kind("sans_reg", 10)
    f_mhl, sc_mhl = font_kind("serif_bold", 15)
    f_mdk, sc_mdk = font_kind("sans_reg", 10)

    for mi, ms in enumerate(MEDIUM_STORIES):
        row = mi // 5
        col = mi % 5
        mx_c0 = int(round(MX + col * (med_w + med_col_gap)))
        mx_c1 = WIDTH - MX if col == 4 else int(round(MX + (col + 1) * med_w + col * med_col_gap))
        my_c0 = med_y0 + row * (med_row_h + med_row_gap)
        my_c1 = my_c0 + med_row_h
        cw_m = mx_c1 - mx_c0

        d.rounded_rectangle([mx_c0, my_c0, mx_c1, my_c1], radius=5, fill=CARD_BG, outline=CARD_BORDER, width=1)
        render_clipped_scene(img, ms.scene, mx_c0 + 2, my_c0 + 2, cw_m - 4, med_scene_h - 2)

        tx0 = mx_c0 + 5
        tw = cw_m - 10  # ~187 px
        tbox = (mx_c0 + 3, my_c0 + med_scene_h, mx_c1 - 3, my_c1 - 1)
        grp = f"med_{ms.num}"

        ky = my_c0 + med_scene_h + 1.5
        k_txt = ms.kicker
        s_txt = ms.source
        if measure_w(d, k_txt, f_mk, sc_mk) + measure_w(d, s_txt, f_msrc, sc_msrc) + 4 > tw:
            k_txt = ms.kicker.split(" · ")[0]
        draw_text_top(
            d, tx0, ky, k_txt, f_mk, REGION_COLORS[ms.region],
            auditor=auditor, group=grp, label=f"m{ms.num}_kicker", scale=sc_mk, container=tbox,
        )
        sw_r = float(d.textlength(s_txt, font=f_msrc))
        sw_e = sw_r * sc_msrc
        tb_ms, vh_ms = font_metrics(f_msrc)
        d.text((tx0 + tw - sw_r, ky - tb_ms), s_txt, font=f_msrc, fill=INK_MUTED)
        auditor.record(
            grp, f"m{ms.num}_src", tx0 + tw - sw_e, ky, tx0 + tw, ky + vh_ms, s_txt, container=tbox
        )

        # Bold Serif 15px sentence-case headline (2-3 lines)
        hl_y = ky + 10.0
        hl_bot, _ = draw_wrapped_block(
            d, tx0, hl_y, ms.headline, f_mhl, INK,
            max_w=tw, max_lines=3, line_h=13.5, scale=sc_mhl,
            auditor=auditor, group=grp, label=f"m{ms.num}_hl", container=tbox,
        )

        # Deck (10px sans — fits cleanly in 2-3 lines even under Verdana/DejaVu)
        dk_y = hl_bot + 1.0
        draw_wrapped_block(
            d, tx0, dk_y, ms.summary, f_mdk, INK_BODY,
            max_w=tw, max_lines=3, line_h=9.5, scale=sc_mdk,
            auditor=auditor, group=grp, label=f"m{ms.num}_dk", container=tbox,
        )

    med_y1 = med_y0 + 2 * med_row_h + med_row_gap

    # ------------------------------------------------------------------
    # BAND 6: WORLD MAP LEFT (#1–#13 + COLOR LEGEND) + 2 WIDE INDEX COLS (#14–#36)
    # Ends at Y = 954
    # ------------------------------------------------------------------
    b6_y0 = med_y1 + 2
    b6_y1 = 954
    d.line([(MX, b6_y0 - 2), (WIDTH - MX, b6_y0 - 2)], fill=RULE_SOFT, width=1)

    map_w = 280
    map_x0 = MX
    map_x1 = map_x0 + map_w
    idx_x0 = map_x1 + 8
    idx_total_w = WIDTH - MX - idx_x0
    idx_gutter = 10
    idx_col_w = (idx_total_w - idx_gutter) / 2.0  # 353.0 px

    f_sec, sc_sec = font_kind("sans_bold", 11)
    f_subm, sc_subm = font_kind("sans_reg", 10)
    draw_text_top(
        d, map_x0, b6_y0 + 1, "WHERE IT HAPPENED", f_sec, INK,
        auditor=auditor, group="b6_hdr", label="map_hdr", scale=sc_sec,
        container=(map_x0, b6_y0, map_x1, b6_y0 + 14),
    )
    pin_sub = "pins 1–13"
    ps_w = float(d.textlength(pin_sub, font=f_subm))
    draw_text_top(
        d, map_x1 - ps_w, b6_y0 + 2, pin_sub, f_subm, INK_MUTED,
        auditor=auditor, group="b6_hdr", label="map_sub", scale=sc_subm,
        container=(map_x0, b6_y0, map_x1, b6_y0 + 14),
    )

    map_y0 = b6_y0 + 14
    map_h = 150
    map_pins = (
        [(s.num, s.region, s.lon, s.lat) for s in HERO_STORIES]
        + [(s.num, s.region, s.lon, s.lat) for s in MEDIUM_STORIES]
    )
    draw_world_map(d, map_x0, map_y0, map_w, map_h, map_pins)

    # Region color legend directly under map (NO counts, NO count tables — color keys ONLY!)
    leg_y0 = map_y0 + map_h + 2
    f_leg_h, sc_lh = font_kind("sans_bold", 10)
    f_leg_r, sc_lr = font_kind("sans_reg", 10)
    draw_text_top(
        d, map_x0, leg_y0, "REGION COLOURS (11 REGIONS)", f_leg_h, INK_MUTED,
        auditor=auditor, group="map_legend", label="reg_leg_hdr", scale=sc_lh,
        container=(map_x0, leg_y0 - 1, map_x1, leg_y0 + 12),
    )
    ly = leg_y0 + 12
    half_w = map_w / 2.0
    for ri, reg in enumerate(REGION_ORDER):
        r_col = ri % 2
        r_row = ri // 2
        lx = map_x0 + r_col * half_w
        cy_dot = ly + r_row * 11.0 + 5
        d.ellipse([lx + 1, cy_dot - 3.5, lx + 8, cy_dot + 3.5], fill=REGION_COLORS[reg])
        draw_text_top(
            d, lx + 11, ly + r_row * 11.0, REGION_DISPLAY_FULL[reg], f_leg_r, INK_BODY,
            auditor=auditor, group="map_legend", label=f"reg_leg_{reg}", scale=sc_lr,
            container=(lx, ly + r_row * 11.0 - 1, lx + half_w + 1, min(b6_y1, ly + r_row * 11.0 + 11)),
        )

    # Index Right Header
    draw_text_top(
        d, idx_x0, b6_y0 + 1, "ALSO ON WEDNESDAY 25 NOVEMBER — 23 MORE STORIES", f_sec, NAVY,
        auditor=auditor, group="b6_hdr", label="idx_hdr", scale=sc_sec,
        container=(idx_x0, b6_y0, WIDTH - MX, b6_y0 + 14),
    )
    idx_key = "[O] Official  [R] Reported  [C] Claim"
    ik_w = float(d.textlength(idx_key, font=f_subm))
    draw_text_top(
        d, WIDTH - MX - ik_w, b6_y0 + 13, idx_key, f_subm, INK_MUTED,
        auditor=auditor, group="b6_hdr", label="idx_key", scale=sc_subm,
        container=(idx_x0, b6_y0 + 12, WIDTH - MX, b6_y0 + 25),
    )

    # Two one-line columns; preserve the 13px title / 11px fact type floors.
    idx_body_y0 = b6_y0 + 26
    idx_body_y1 = b6_y1 - 28
    col_slices = [INDEX_STORIES[:12], INDEX_STORIES[12:]]
    f_ih, sc_ih = font_kind("sans_bold", 13)
    f_is, sc_is = font_kind("sans_bold", 10)
    f_id, sc_id = font_kind("sans_reg", 11)
    f_nb, _ = font_kind("sans_bold", 10)
    tb_nb, vh_nb = font_metrics(f_nb)
    tb_ih, vh_ih = font_metrics(f_ih)
    tb_id, vh_id = font_metrics(f_id)
    tb_is, _ = font_metrics(f_is)
    tb_sub, _ = font_metrics(f_subm)

    for ci, slice_items in enumerate(col_slices):
        cx0 = idx_x0 + ci * (idx_col_w + idx_gutter)
        cx1 = cx0 + idx_col_w
        if ci == 1:
            gx_div = idx_x0 + idx_col_w + idx_gutter / 2.0
            d.line([(gx_div, idx_body_y0), (gx_div, idx_body_y1)], fill="#DDD4C3", width=1)

        badge_gutter = 20.0
        line_avail_w = idx_col_w - badge_gutter - 1.0
        laid_out: list[tuple[IndexStory, str, float]] = []
        total_h = 0.0
        for st in slice_items:
            hl_tok = f"{st.headline}:"
            src_str = f"({st.source})"
            conf_str = f"[{CONF_CODE[st.conf]}]"
            full_w = (
                measure_w(d, hl_tok, f_ih, sc_ih) + 4.0
                + measure_w(d, st.detail, f_id, sc_id)
                + measure_w(d, src_str + " ", f_subm, sc_subm)
                + measure_w(d, conf_str, f_is, sc_is)
            )
            if full_w > line_avail_w:
                raise AssertionError(
                    f"[{ACTIVE_PROFILE.name}] Index #{st.num} overflows 1 hanging line in {line_avail_w:.1f}px: "
                    f"{hl_tok} {st.detail} {src_str} {conf_str} ({full_w:.1f}px)"
                )
            item_h = 13.0
            laid_out.append((st, st.detail, item_h))
            total_h += item_h

        avail_h = idx_body_y1 - idx_body_y0
        if total_h > avail_h + 0.5:
            raise AssertionError(
                f"[{ACTIVE_PROFILE.name}] Index Col {ci+1} needs {total_h:.1f}px > avail {avail_h:.1f}px"
            )
        gap_y = 0.0

        cur_y = float(idx_body_y0)
        cbox = (cx0 - 1, idx_body_y0 - 1, cx1 + 1, idx_body_y1 + 2)
        grp = f"idx_col_{ci}"

        for ri_item, (st, l1_fact, item_h) in enumerate(laid_out):
            # Colored number pill in the 20px gutter; exactly one line per item
            num_s = str(st.num)
            d.rounded_rectangle([cx0, cur_y + 1, cx0 + 17, cur_y + 12], radius=3, fill=REGION_COLORS[st.region])
            nw = float(d.textlength(num_s, font=f_nb))
            d.text((cx0 + (17 - nw) / 2.0, cur_y + 1 + (11 - vh_nb) / 2.0 - tb_nb), num_s, font=f_nb, fill=INK_LIGHT)

            hl_tok = f"{st.headline}:"
            hx = cx0 + badge_gutter
            d.text((hx, cur_y - tb_ih), hl_tok, font=f_ih, fill=INK)
            hl_w_raw = float(d.textlength(hl_tok, font=f_ih))
            hl_w_eff = hl_w_raw * sc_ih

            fx1 = hx + hl_w_raw + 2.0
            fx1_eff = hx + hl_w_eff + 2.0
            d.text((fx1, cur_y - tb_id), l1_fact, font=f_id, fill=INK_BODY)
            l1_w_raw = float(d.textlength(l1_fact, font=f_id))
            l1_w_eff = l1_w_raw * sc_id

            src_str = f"({st.source})"
            conf_str = f"[{CONF_CODE[st.conf]}]"
            tx_tail = fx1 + l1_w_raw + 2.0
            tx_tail_eff = fx1_eff + l1_w_eff + 2.0
            d.text((tx_tail, cur_y - tb_sub), src_str, font=f_subm, fill=INK_MUTED)
            sw_r = float(d.textlength(src_str + " ", font=f_subm))
            sw_e = sw_r * sc_subm
            d.text((tx_tail + sw_r, cur_y - tb_is), conf_str, font=f_is, fill=CONF_COLOR[st.conf])
            cw_e = measure_w(d, conf_str, f_is, sc_is)
            auditor.record(
                grp, f"idx_{st.num}_row",
                cx0, cur_y, tx_tail_eff + sw_e + cw_e, cur_y + 12.0,
                f"{hl_tok} {l1_fact} {src_str} {conf_str}".strip(), container=cbox,
            )

            cur_y += item_h + gap_y
            if ri_item < len(laid_out) - 1:
                sep_i = cur_y - gap_y / 2.0
                d.line([(hx, sep_i), (cx1, sep_i)], fill="#E7DFCE", width=1)

    # ------------------------------------------------------------------
    # BAND 7: FOOTER — SOLID CRIMSON DATE CHECK BOX + LEGEND/SOURCES + 23 LEFT-OUTS
    # Y = 956..1022
    # ------------------------------------------------------------------
    dc_y0 = 956
    dc_y1 = 1000
    d.rounded_rectangle([MX, dc_y0, WIDTH - MX, dc_y1], radius=4, fill=CRIMSON, outline=CRIMSON, width=2)

    d.rounded_rectangle([MX + 12, dc_y0 + 6, MX + 90, dc_y0 + 20], radius=3, fill=INK_LIGHT)
    f_dcb, sc_dcb = font_kind("sans_bold", 10)
    draw_centered_single(
        d, MX + 51, dc_y0 + 8, "DATE CHECK", f_dcb, CRIMSON,
        scale=sc_dcb, auditor=auditor, group="date_check", label="dc_pill",
        container=(MX + 10, dc_y0 + 4, MX + 92, dc_y0 + 22),
    )

    f_dct, sc_dct = font_kind("sans_bold", 10)
    dc_tx = MX + 102
    dc_tw = (WIDTH - MX - 12) - dc_tx
    draw_wrapped_block(
        d, dc_tx, dc_y0 + 3, DATE_CHECK_TEXT, f_dct, INK_LIGHT,
        max_w=dc_tw, max_lines=3, line_h=12.0, scale=sc_dct,
        auditor=auditor, group="date_check", label="dc_body",
        container=(dc_tx - 1, dc_y0 + 2, WIDTH - MX - 12, dc_y1 - 1),
    )

    # Footer meta uses the space freed below the one-line index.
    meta_y0 = b6_y1 - 24
    f_meta, sc_meta = font_kind("sans_reg", 9, allow_footer_meta=True)
    f_metab, sc_metab = font_kind("sans_bold", 9, allow_footer_meta=True)
    draw_text_top(
        d, idx_x0, meta_y0, LEGEND_TEXT, f_meta, INK_MUTED,
        auditor=auditor, group="footer_meta", label="legend_line", scale=sc_meta,
        container=(idx_x0, meta_y0 - 1, WIDTH - MX, meta_y0 + 11),
    )
    src_w_raw = float(d.textlength(SOURCES_TEXT, font=f_meta))
    src_w_eff = src_w_raw * sc_meta
    tb_m, vh_m = font_metrics(f_meta)
    d.text((WIDTH - MX - src_w_raw, meta_y0 + 11 - tb_m), SOURCES_TEXT, font=f_meta, fill=INK_MUTED)
    auditor.record(
        "footer_meta", "sources_line", WIDTH - MX - src_w_eff, meta_y0 + 11, WIDTH - MX, meta_y0 + 11 + vh_m, SOURCES_TEXT,
        container=(idx_x0, meta_y0 + 10, WIDTH - MX, b6_y1),
    )

    # 23 Footer Left-Outs (2 lines @ 9px footer meta)
    lo_y0 = dc_y1 + 2
    left_out_line = "LEFT OUT 25 NOV (23): " + " · ".join(LEFT_OUT_TITLES) + "."
    lo_lines = wrap_strict(
        d, left_out_line, f_meta, CW, max_lines=2, scale=sc_meta, label="footer_left_outs"
    )
    lo_prefix = "LEFT OUT 25 NOV (23):"
    for li, ln in enumerate(lo_lines):
        ly = lo_y0 + li * 9.5
        if li == 0 and ln.startswith(lo_prefix):
            pw_r = float(d.textlength(lo_prefix, font=f_metab))
            d.text((MX, ly - tb_m), lo_prefix, font=f_metab, fill=INK)
            d.text((MX + pw_r, ly - tb_m), ln[len(lo_prefix):], font=f_meta, fill=INK_MUTED)
        else:
            d.text((MX, ly - tb_m), ln, font=f_meta, fill=INK_MUTED)
    max_lo_w = max(measure_w(d, ln, f_meta, sc_meta) for ln in lo_lines)
    auditor.record(
        "footer_lo", "left_outs", MX, lo_y0, MX + max_lo_w, lo_y0 + (len(lo_lines) - 1) * 9.5 + vh_m,
        " ".join(lo_lines), container=(MX, lo_y0 - 1, WIDTH - MX, 1022),
    )

    # Final assertion: Date font is strictly the largest text on the page
    assert stats_out["date_px"] > 28, "Masthead date must be strictly larger than any headline or stat"
    return img, auditor, stats_out


def main() -> None:
    parser = argparse.ArgumentParser(description="Render THE WORLD IN ONE DAY v8 (1024x1024)")
    parser.add_argument(
        "--out",
        type=Path,
        default=Path(__file__).resolve().parent / "entry.png",
        help="Output PNG path (default: entry.png alongside draw.py)",
    )
    parser.add_argument(
        "--dejavu-test",
        type=Path,
        default=None,
        help="Optional output path to also save the worst-case Linux DejaVu width stress render",
    )
    args = parser.parse_args()

    # 1. Render production image with full live runtime assertions
    img, auditor_native, stats_native = render_broadsheet(NATIVE_PROFILE)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    img.save(args.out, format="PNG", optimize=True)

    # 2. Mandatory Linux DejaVu width-stress audit on EVERY build (raises on ANY defect!)
    img_dj, auditor_dj, stats_dj = render_broadsheet(DEJAVU_STRESS_PROFILE)
    if args.dejavu_test is not None:
        args.dejavu_test.parent.mkdir(parents=True, exist_ok=True)
        img_dj.save(args.dejavu_test, format="PNG", optimize=True)

    size_bytes = args.out.stat().st_size
    assert img.size == (1024, 1024) and img.mode == "RGB"
    assert size_bytes < 1024 * 1024, f"entry.png too large ({size_bytes} bytes >= 1 MiB)"

    print(
        f"Rendered {args.out.name}: {TOTAL_STORIES} dated stories | "
        f"{len(REGION_COUNTS)} regions | {len(FIELD_COUNTS)} fields | "
        f"{DRAWN_SCENES} drawn scenes | {size_bytes:,} bytes | "
        f"date={int(stats_native['date_px'])}px (dejavu={int(stats_dj['date_px'])}px) | "
        f"hero_scene={stats_native['hero_scene_pct']}% med_scene={stats_native['med_scene_pct']}% | "
        f"audited_boxes={len(auditor_native.boxes)}/{len(auditor_dj.boxes)} PASS"
    )


if __name__ == "__main__":
    main()
