"""Generate docs/assets/readme-banner.png — VisionsCraft-style hero for README."""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

W, H = 1400, 480
RADIUS = 32
BG = (8, 8, 10)
OUT = Path(__file__).with_name("readme-banner.png")


def load_font(size: int, bold: bool = True) -> ImageFont.ImageFont:
    candidates = [
        r"C:\Windows\Fonts\arialbd.ttf" if bold else r"C:\Windows\Fonts\arial.ttf",
        r"C:\Windows\Fonts\seguisb.ttf" if bold else r"C:\Windows\Fonts\segoeui.ttf",
        r"C:\Windows\Fonts\segoeuib.ttf" if bold else r"C:\Windows\Fonts\segoeui.ttf",
    ]
    for path in candidates:
        try:
            return ImageFont.truetype(path, size)
        except OSError:
            continue
    return ImageFont.load_default()


def measure(font: ImageFont.ImageFont, text: str) -> tuple[int, int]:
    bbox = font.getbbox(text)
    return bbox[2] - bbox[0], bbox[3] - bbox[1]


def draw_diamond(draw: ImageDraw.ImageDraw, cx: int, cy: int, size: int, fill: tuple[int, ...]) -> None:
    s = size
    draw.polygon([(cx, cy - s), (cx + s, cy), (cx, cy + s), (cx - s, cy)], fill=fill)


def centered_words_with_diamonds(
    draw: ImageDraw.ImageDraw,
    y: int,
    words: list[str],
    font: ImageFont.ImageFont,
    fill: tuple[int, ...],
    diamond_fill: tuple[int, ...],
    diamond_size: int = 5,
    gap: int = 18,
) -> int:
    """Draw WORDS separated by filled diamonds; return line height."""
    widths = [measure(font, w)[0] for w in words]
    _, line_h = measure(font, words[0])
    total = sum(widths) + gap * (len(words) - 1) + diamond_size * 2 * (len(words) - 1) + gap * (len(words) - 1)
    x = (W - total) // 2
    cy = y + line_h // 2
    for i, word in enumerate(words):
        draw.text((x, y), word, font=font, fill=fill)
        x += widths[i]
        if i < len(words) - 1:
            x += gap
            draw_diamond(draw, x + diamond_size, cy, diamond_size, diamond_fill)
            x += diamond_size * 2 + gap
    return line_h


def gradient_spaced_text(
    img: Image.Image,
    center_x: int,
    y: int,
    text: str,
    font: ImageFont.ImageFont,
    tracking: float = 0.045,
) -> int:
    parts: list[tuple[str, int]] = []
    total_w = 0
    max_h = 0
    for i, ch in enumerate(text):
        cw, ch_h = measure(font, ch)
        gap = int(cw * tracking) if i < len(text) - 1 else 0
        parts.append((ch, cw + gap))
        total_w += cw + gap
        max_h = max(max_h, ch_h)

    pad = 8
    grad = Image.new("RGBA", (total_w + 2, max_h + pad), (0, 0, 0, 0))
    gd = ImageDraw.Draw(grad)
    for x in range(total_w + 2):
        t = x / max(total_w + 1, 1)
        r = int(0 + 255 * t)
        g = int(229 + (77 - 229) * t)
        b = int(255 + (184 - 255) * t)
        gd.line([(x, 0), (x, max_h + pad - 1)], fill=(r, g, b, 255))

    mask = Image.new("L", (total_w + 2, max_h + pad), 0)
    md = ImageDraw.Draw(mask)
    cursor = 0
    for ch, advance in parts:
        md.text((cursor, 0), ch, font=font, fill=255)
        cursor += advance

    colored = Image.new("RGBA", (total_w + 2, max_h + pad), (0, 0, 0, 0))
    colored.paste(grad, (0, 0))
    colored.putalpha(mask)
    img.paste(colored, (center_x - total_w // 2, y), colored)
    return max_h


def main() -> None:
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    base = Image.new("RGBA", (W, H), (*BG, 255))
    mask = Image.new("L", (W, H), 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, W - 1, H - 1), radius=RADIUS, fill=255)
    img = Image.composite(base, img, mask)

    edge = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(edge).rounded_rectangle(
        (1, 1, W - 2, H - 2),
        radius=RADIUS,
        outline=(48, 50, 56, 160),
        width=2,
    )
    img = Image.alpha_composite(img, edge)
    draw = ImageDraw.Draw(img)

    title_font = load_font(66, True)
    sub_font = load_font(24, True)
    stack_font = load_font(20, False)
    brand_font = load_font(15, True)

    y = 100
    h1 = gradient_spaced_text(img, W // 2, y, "ALKHIDMAT RELIEF COPILOT", title_font)
    y = y + h1 + 36

    h2 = centered_words_with_diamonds(
        draw,
        y,
        ["INTAKE", "TRIAGE", "HITL"],
        sub_font,
        fill=(250, 250, 252, 255),
        diamond_fill=(250, 250, 252, 255),
        diamond_size=5,
        gap=16,
    )
    y = y + h2 + 28

    h3 = centered_words_with_diamonds(
        draw,
        y,
        ["DashScope Qwen", "FastAPI", "LangGraph", "Next.js", "Cloud Run"],
        stack_font,
        fill=(168, 170, 178, 255),
        diamond_fill=(168, 170, 178, 255),
        diamond_size=4,
        gap=14,
    )
    y = y + h3 + 26

    brand = "ALIBABA CLOUD AI HACKATHON  ·  PAKISTAN 2026"
    bw, _ = measure(brand_font, brand)
    draw.text(((W - bw) // 2, y), brand, font=brand_font, fill=(255, 106, 0, 255))

    final = img.convert("RGB")
    final.save(OUT, "PNG", optimize=True)
    print(OUT, final.size)


if __name__ == "__main__":
    main()
