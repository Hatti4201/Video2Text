import os
import subprocess

# Same design tokens as extension/theme.css. "default" matches YouTube's own
# red/white/black branding so the extension panel blends into the page. To
# add another theme, add a new key here with the same "light"/"dark" shape.
THEMES = {
    "default": {
        "light": {
            "background": "#ffffff",
            "foreground": "#0f0f0f",
            "card": "#f9f9f9",
            "card_foreground": "#0f0f0f",
            "popover": "#ffffff",
            "popover_foreground": "#0f0f0f",
            "primary": "#cc0000",
            "primary_foreground": "#ffffff",
            "secondary": "#272727",
            "secondary_foreground": "#ffffff",
            "muted": "#f2f2f2",
            "muted_foreground": "#606060",
            "accent": "#e5e5e5",
            "accent_foreground": "#0f0f0f",
            "destructive": "#d93025",
            "destructive_foreground": "#ffffff",
            "border": "#e5e5e5",
            "input": "#e5e5e5",
            "ring": "#cc0000",
        },
        "dark": {
            "background": "#0f0f0f",
            "foreground": "#f1f1f1",
            "card": "#212121",
            "card_foreground": "#f1f1f1",
            "popover": "#212121",
            "popover_foreground": "#f1f1f1",
            "primary": "#cc0000",
            "primary_foreground": "#ffffff",
            "secondary": "#3f3f3f",
            "secondary_foreground": "#f1f1f1",
            "muted": "#272727",
            "muted_foreground": "#aaaaaa",
            "accent": "#3f3f3f",
            "accent_foreground": "#f1f1f1",
            "destructive": "#ff5252",
            "destructive_foreground": "#0f0f0f",
            "border": "#3f3f3f",
            "input": "#3f3f3f",
            "ring": "#cc0000",
        },
    },
}

DEFAULT_THEME = "default"


def _system_mode() -> str:
    """Best-effort OS dark-mode detection. macOS only for now; everything
    else (and any failure) falls back to light."""
    try:
        result = subprocess.run(
            ["defaults", "read", "-g", "AppleInterfaceStyle"],
            capture_output=True,
            text=True,
            timeout=1,
        )
        return "dark" if result.stdout.strip() == "Dark" else "light"
    except Exception:
        return "light"


def get_palette(theme: str | None = None, mode: str | None = None) -> dict:
    theme = theme or os.environ.get("VIDEO2TEXT_THEME", DEFAULT_THEME)
    mode = mode or os.environ.get("VIDEO2TEXT_MODE") or _system_mode()

    palette = THEMES.get(theme, THEMES[DEFAULT_THEME])
    return palette.get(mode, palette["light"])
