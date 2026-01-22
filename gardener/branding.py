"""Branding settings and icon generation for Scribe."""

from __future__ import annotations

import io
import json
import logging
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Final

from PIL import Image, ImageDraw
from pydantic import BaseModel, Field

import config

logger = logging.getLogger(__name__)

BRANDING_DIR: Final[Path] = config.STATE_DIR / "branding"
SETTINGS_FILE: Final[Path] = BRANDING_DIR / "settings.json"
ICON_SOURCE_FILE: Final[Path] = BRANDING_DIR / "icon-source.png"

DEFAULT_APP_NAME: Final[str] = "Athena Scribe"
DEFAULT_THEME: Final[str] = "default"
DEFAULT_FONT: Final[str] = "system"
DEFAULT_ICON_VERSION: Final[str] = "default"
DEFAULT_BG: Final[str] = "#0f172a"
DEFAULT_ACCENT: Final[str] = "#38bdf8"

APPLE_PADDING_RATIO: Final[float] = 0.12
MIN_ICON_SIZE: Final[int] = 512
MAX_ICON_BYTES: Final[int] = 5 * 1024 * 1024


class BrandingSettings(BaseModel):
    app_name: str = Field(
        default=DEFAULT_APP_NAME,
        min_length=1,
        max_length=40,
    )
    theme: str = Field(default=DEFAULT_THEME, min_length=1, max_length=40)
    font: str = Field(default=DEFAULT_FONT, min_length=1, max_length=40)
    icon_version: str = Field(default=DEFAULT_ICON_VERSION)


@dataclass(frozen=True)
class IconSpec:
    name: str
    size: int
    padding_ratio: float = 0.0


ICON_SPECS: tuple[IconSpec, ...] = (
    IconSpec("favicon-16.png", 16),
    IconSpec("favicon-32.png", 32),
    IconSpec("favicon-48.png", 48),
    IconSpec("apple-touch-icon-120.png", 120, APPLE_PADDING_RATIO),
    IconSpec("apple-touch-icon-152.png", 152, APPLE_PADDING_RATIO),
    IconSpec("apple-touch-icon-167.png", 167, APPLE_PADDING_RATIO),
    IconSpec("apple-touch-icon-180.png", 180, APPLE_PADDING_RATIO),
    IconSpec("pwa-192.png", 192),
    IconSpec("pwa-512.png", 512),
)

ICON_NAMES: Final[set[str]] = {spec.name for spec in ICON_SPECS} | {"favicon.ico"}


def ensure_branding_dir() -> None:
    BRANDING_DIR.mkdir(parents=True, exist_ok=True)


def load_settings() -> BrandingSettings:
    ensure_branding_dir()
    if not SETTINGS_FILE.exists():
        return BrandingSettings()

    try:
        data = json.loads(SETTINGS_FILE.read_text(encoding="utf-8"))
        return BrandingSettings(**data)
    except Exception as exc:
        logger.warning("Failed to read branding settings: %s", exc)
        return BrandingSettings()


def save_settings(settings: BrandingSettings) -> None:
    ensure_branding_dir()
    SETTINGS_FILE.write_text(
        json.dumps(settings.model_dump(), indent=2),
        encoding="utf-8",
    )


def update_settings(
    app_name: str | None = None, theme: str | None = None, font: str | None = None
) -> BrandingSettings:
    settings = load_settings()
    next_app_name = settings.app_name
    next_theme = settings.theme
    next_font = settings.font

    if app_name is not None:
        next_app_name = app_name.strip() or DEFAULT_APP_NAME
    if theme is not None:
        next_theme = theme.strip() or DEFAULT_THEME
    if font is not None:
        next_font = font.strip() or DEFAULT_FONT

    updated = BrandingSettings(
        app_name=next_app_name,
        theme=next_theme,
        font=next_font,
        icon_version=settings.icon_version,
    )
    save_settings(updated)
    return updated


def icon_available() -> bool:
    return ICON_SOURCE_FILE.exists()


def has_custom_icon(settings: BrandingSettings) -> bool:
    return settings.icon_version != DEFAULT_ICON_VERSION


def get_icon_path(name: str) -> Path:
    return BRANDING_DIR / name


def _render_icon(base: Image.Image, size: int, padding_ratio: float) -> Image.Image:
    if padding_ratio <= 0:
        return base.resize((size, size), Image.Resampling.LANCZOS)

    inset = max(1, int(size * padding_ratio))
    inner_size = max(1, size - 2 * inset)
    canvas = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    scaled = base.resize((inner_size, inner_size), Image.Resampling.LANCZOS)
    canvas.paste(scaled, (inset, inset), scaled)
    return canvas


def _ensure_square(image: Image.Image) -> Image.Image:
    width, height = image.size
    if width != height:
        raise ValueError("Icon must be square (equal width and height).")
    return image


def _ensure_min_size(image: Image.Image) -> Image.Image:
    width, _ = image.size
    if width < MIN_ICON_SIZE:
        raise ValueError(f"Icon must be at least {MIN_ICON_SIZE}x{MIN_ICON_SIZE}.")
    return image


def _generate_favicon_ico(base: Image.Image) -> None:
    ico_path = BRANDING_DIR / "favicon.ico"
    sizes = [(16, 16), (32, 32), (48, 48)]
    images = [base.resize(size, Image.Resampling.LANCZOS) for size in sizes]
    images[0].save(ico_path, format="ICO", sizes=sizes)


def _generate_default_base() -> Image.Image:
    size = MIN_ICON_SIZE
    image = Image.new("RGBA", (size, size), DEFAULT_BG)
    draw = ImageDraw.Draw(image)
    margin = int(size * 0.2)
    points = [
        (size / 2, margin),
        (size - margin, size - margin),
        (margin, size - margin),
    ]
    draw.polygon(points, fill=DEFAULT_ACCENT)
    cutout_width = int(size * 0.18)
    cutout_height = int(size * 0.08)
    cutout_x = int(size / 2 - cutout_width / 2)
    cutout_y = int(size * 0.55)
    draw.rectangle(
        [cutout_x, cutout_y, cutout_x + cutout_width, cutout_y + cutout_height],
        fill=DEFAULT_BG,
    )
    return image


def _load_base_image() -> Image.Image:
    if ICON_SOURCE_FILE.exists():
        with Image.open(ICON_SOURCE_FILE) as source:
            return source.convert("RGBA")

    base = _generate_default_base()
    ensure_branding_dir()
    base.save(ICON_SOURCE_FILE, format="PNG")
    return base


def generate_icons() -> None:
    ensure_branding_dir()
    if _icons_uptodate():
        return
    base = _load_base_image()

    for spec in ICON_SPECS:
        icon = _render_icon(base, spec.size, spec.padding_ratio)
        icon.save(BRANDING_DIR / spec.name, format="PNG")

    _generate_favicon_ico(base)


def save_uploaded_icon(content: bytes) -> BrandingSettings:
    try:
        with Image.open(io.BytesIO(content)) as source:
            image = source.convert("RGBA")
    except OSError as exc:
        raise ValueError("Unsupported or corrupted image file.") from exc
    _ensure_square(image)
    _ensure_min_size(image)

    ensure_branding_dir()
    image.save(ICON_SOURCE_FILE, format="PNG")
    generate_icons()

    settings = load_settings()
    settings.icon_version = str(int(time.time()))
    save_settings(settings)
    return settings


def _icons_uptodate() -> bool:
    if not ICON_SOURCE_FILE.exists():
        return False
    source_mtime = ICON_SOURCE_FILE.stat().st_mtime
    required = {spec.name for spec in ICON_SPECS} | {"favicon.ico"}
    for name in required:
        path = BRANDING_DIR / name
        if not path.exists():
            return False
        if path.stat().st_mtime < source_mtime:
            return False
    return True
