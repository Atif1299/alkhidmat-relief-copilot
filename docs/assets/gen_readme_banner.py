"""Generate docs/assets/readme-banner.png for GitHub README hero."""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

W, H = 1280, 420
RADIUS = 28
BG = (10, 10, 12)
OUT = Path(__file__).with_name("readme-banner.png")


def load_font(size: int, bold: bool = True) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidates = [
        r"C:\Windows\Fonts\arialbd.ttf" if bold else r"C:\Windows\Fonts\arial.ttf",
        r"C:\Windows\Fonts\segoeuib.ttf" if bold else r"C:\Windows\Fonts\segoeui.ttf",
        r"C:\Windows\Fonts\calibrib.ttf" if bold else r"C:\Windows\Fonts\calibri.ttf",
    ]
    for path in candidates:
        try:
            return ImageFont.truetype(path, size)
        except OSError:
            continue
    return ImageFont.load_default()


def text_size(font: ImageFont.ImageFont, text: str) -> tuple[int, int]:
    bbox = font.getbbox(text)
    return bbox[2] - bbox[0], bbox[3] - bbox[1]


def main() -> None:
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    base = Image.new("RGBA", (W, H), (*BG, 255))
    mask = Image.new("L", (W, H), 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, W - 1, H - 1), radius=RADIUS, fill=255)
    img = Image.composite(base, img, mask)

    vignette = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    vd = ImageDraw.Draw(vignette)
    for i in range(80):
        a = int(18 * (i / 80))
        vd.rounded_rectangle(
            (i, i, W - 1 - i, H - 1 - i),
            radius=RADIUS,
            outline=(0, 0, 0, a),
        )
    img = Image.alpha_composite(img, vignette)
    draw = ImageDraw.Draw(img)

    title = "ALKHIDMAT RELIEF COPILOT"
    subtitle = "INTAKE  ◆  TRIAGE  ◆  HITL"
    stack = "Next.js 14  ◆  FastAPI  ◆  LangGraph  ◆  Postgres  ◆  Cloud Run"

    title_font = load_font(54, True)
    tw, th = text_size(title_font, title)
    if tw > W - 80:
        title_font = load_font(44, True)
        tw, th = text_size(title_font, title)

    sub_font = load_font(22, True)
    stack_font = load_font(18, False)

    tx = (W - tw) // 2
    ty = 118

    # cyan (#00E5FF) → pink (#FF40B4)
    grad = Image.new("RGBA", (tw, th + 8), (0, 0, 0, 0))
    gd = ImageDraw.Draw(grad)
    for x in range(tw):
        t = x / max(tw - 1, 1)
        r = int(0 + (255 - 0) * t)
        g = int(229 + (64 - 229) * t)
        b = int(255 + (180 - 255) * t)
        gd.line([(x, 0), (x, th + 7)], fill=(r, g, b, 255))

    text_mask = Image.new("L", (tw, th + 8), 0)
    ImageDraw.Draw(text_mask).text((0, 0), title, font=title_font, fill=255)
    colored = Image.new("RGBA", (tw, th + 8), (0, 0, 0, 0))
    colored.paste(grad, (0, 0))
    colored.putalpha(text_mask)
    img.paste(colored, (tx, ty), colored)

    sw, sh = text_size(sub_font, subtitle)
    sx = (W - sw) // 2
    sy = ty + th + 36
    draw.text((sx, sy), subtitle, font=sub_font, fill=(245, 245, 247, 255))

    kw, kh = text_size(stack_font, stack)
    kx = (W - kw) // 2
    ky = sy + sh + 28
    draw.text((kx, ky), stack, font=stack_font, fill=(168, 170, 178, 255))

    border = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(border).rounded_rectangle(
        (1, 1, W - 2, H - 2),
        radius=RADIUS,
        outline=(40, 42, 48, 180),
        width=2,
    )
    img = Image.alpha_composite(img, border)

    final = img.convert("RGB")
    final.save(OUT, "PNG", optimize=True)
    print(OUT, final.size)


if __name__ == "__main__":
    main()
