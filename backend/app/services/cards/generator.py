"""Server-side PNG card generation using Pillow."""

import io
import logging
from datetime import date

from PIL import Image, ImageDraw, ImageFont

logger = logging.getLogger(__name__)

# Card dimensions
W, H = 600, 340
PADDING = 32

# Colors
BG_DARK = (17, 24, 39)       # gray-900
BG_CARD = (31, 41, 55)       # gray-800
BLUE = (59, 130, 246)
GREEN = (34, 197, 94)
ORANGE = (251, 146, 60)
YELLOW = (250, 204, 21)
PURPLE = (168, 85, 247)
WHITE = (255, 255, 255)
GRAY = (156, 163, 175)
GRAY_DIM = (107, 114, 128)

# Branding
BRAND = "PlanQuest"
LINK = "t.me/planAIbot"


def _get_font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    """Get a font — fallback to default if system fonts unavailable."""
    paths = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
    ]
    for path in paths:
        try:
            return ImageFont.truetype(path, size)
        except (OSError, IOError):
            continue
    return ImageFont.load_default()


def _draw_rounded_rect(draw: ImageDraw.Draw, xy: tuple, radius: int, fill: tuple) -> None:
    """Draw a rounded rectangle."""
    x0, y0, x1, y1 = xy
    draw.rectangle([x0 + radius, y0, x1 - radius, y1], fill=fill)
    draw.rectangle([x0, y0 + radius, x1, y1 - radius], fill=fill)
    draw.pieslice([x0, y0, x0 + 2 * radius, y0 + 2 * radius], 180, 270, fill=fill)
    draw.pieslice([x1 - 2 * radius, y0, x1, y0 + 2 * radius], 270, 360, fill=fill)
    draw.pieslice([x0, y1 - 2 * radius, x0 + 2 * radius, y1], 90, 180, fill=fill)
    draw.pieslice([x1 - 2 * radius, y1 - 2 * radius, x1, y1], 0, 90, fill=fill)


def _add_branding(draw: ImageDraw.Draw) -> None:
    """Add PlanQuest branding at bottom."""
    font_sm = _get_font(13)
    draw.text((PADDING, H - 28), f"{BRAND} · {LINK}", fill=GRAY_DIM, font=font_sm)


def generate_streak_card(name: str, streak: int, best_streak: int) -> bytes:
    """Generate streak achievement card."""
    img = Image.new("RGB", (W, H), BG_DARK)
    draw = ImageDraw.Draw(img)

    # Background accent
    _draw_rounded_rect(draw, (16, 16, W - 16, H - 16), 20, BG_CARD)

    # Streak flame area
    font_huge = _get_font(72, bold=True)
    font_lg = _get_font(28, bold=True)
    font_md = _get_font(18)
    font_sm = _get_font(14)

    # Fire emoji area (just number)
    draw.text((PADDING + 20, 40), str(streak), fill=ORANGE, font=font_huge)
    draw.text((PADDING + 20, 120), "kunlik streak", fill=WHITE, font=font_lg)

    # Name
    draw.text((PADDING + 20, 165), name, fill=GRAY, font=font_md)

    # Best streak
    draw.text((PADDING + 20, 210), f"Eng yaxshi: {best_streak} kun", fill=GRAY_DIM, font=font_sm)

    # Right side — flame visualization (bars)
    bar_x = W - 160
    for i in range(min(streak, 7)):
        bar_h = 30 + i * 15
        y = H - 60 - bar_h
        color = ORANGE if i < streak else GRAY_DIM
        _draw_rounded_rect(draw, (bar_x + i * 18, y, bar_x + i * 18 + 12, H - 60), 4, color)

    _add_branding(draw)

    buf = io.BytesIO()
    img.save(buf, format="PNG", optimize=True)
    return buf.getvalue()


def generate_level_card(name: str, level: int, title: str, total_xp: int) -> bytes:
    """Generate level-up card."""
    img = Image.new("RGB", (W, H), BG_DARK)
    draw = ImageDraw.Draw(img)

    # Gradient-like background
    _draw_rounded_rect(draw, (16, 16, W - 16, H - 16), 20, (25, 25, 60))

    font_huge = _get_font(64, bold=True)
    font_lg = _get_font(24, bold=True)
    font_md = _get_font(18)
    font_sm = _get_font(14)

    # Level number
    draw.text((PADDING + 20, 35), f"Level {level}", fill=YELLOW, font=font_huge)

    # Title
    draw.text((PADDING + 20, 110), title, fill=PURPLE, font=font_lg)

    # Name
    draw.text((PADDING + 20, 150), name, fill=GRAY, font=font_md)

    # XP
    draw.text((PADDING + 20, 190), f"Jami: {total_xp:,} XP", fill=GRAY_DIM, font=font_sm)

    # Stars decoration
    star_y = 60
    for i in range(min(level, 10)):
        x = W - 60 - (i % 5) * 30
        y = star_y + (i // 5) * 30
        draw.text((x, y), "★", fill=YELLOW, font=_get_font(22))

    _add_branding(draw)

    buf = io.BytesIO()
    img.save(buf, format="PNG", optimize=True)
    return buf.getvalue()


def generate_weekly_card(
    name: str,
    tasks_done: int,
    habits_done: int,
    focus_minutes: int,
    xp_earned: int,
    streak: int,
) -> bytes:
    """Generate weekly win card."""
    img = Image.new("RGB", (W, H), BG_DARK)
    draw = ImageDraw.Draw(img)

    _draw_rounded_rect(draw, (16, 16, W - 16, H - 16), 20, BG_CARD)

    font_lg = _get_font(22, bold=True)
    font_md = _get_font(16)
    font_stat = _get_font(32, bold=True)
    font_sm = _get_font(12)

    # Title
    draw.text((PADDING + 10, 30), f"Haftalik natija — {name}", fill=WHITE, font=font_lg)

    today = date.today()
    draw.text((PADDING + 10, 60), f"Hafta: {today.isocalendar()[1]}, {today.year}", fill=GRAY_DIM, font=font_sm)

    # Stats grid — 2 rows × 3 columns
    stats = [
        (str(tasks_done), "task", GREEN),
        (str(habits_done), "habit", BLUE),
        (f"{focus_minutes}m", "fokus", PURPLE),
        (f"+{xp_earned}", "XP", YELLOW),
        (f"{streak}d", "streak", ORANGE),
    ]

    col_w = (W - 2 * PADDING - 20) // 3
    for i, (val, label, color) in enumerate(stats):
        col = i % 3
        row = i // 3
        x = PADDING + 10 + col * col_w
        y = 95 + row * 100

        draw.text((x, y), val, fill=color, font=font_stat)
        draw.text((x, y + 38), label, fill=GRAY, font=font_md)

    _add_branding(draw)

    buf = io.BytesIO()
    img.save(buf, format="PNG", optimize=True)
    return buf.getvalue()
