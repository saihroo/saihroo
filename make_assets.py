"""Generate the animated GIF assets for the saihroo GitHub profile."""

import math
import os

from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont

ROOT = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.join(ROOT, "assets")
os.makedirs(ASSETS, exist_ok=True)

FONT_BOLD = r"C:\Windows\Fonts\consolab.ttf"
FONT_REG = r"C:\Windows\Fonts\consola.ttf"

CYAN = (34, 211, 238)
CYAN_LIGHT = (165, 243, 252)
CYAN_MID = (14, 165, 233)
BLUE = (99, 102, 241)
SLATE = (100, 116, 139)
SLATE_DARK = (71, 85, 105)
TEXT = (226, 232, 240)
BG_TOP = (3, 7, 17)
BG_BOTTOM = (5, 19, 29)
PANEL = (4, 10, 18)


def lerp(a, b, t):
    return tuple(int(round(a[i] + (b[i] - a[i]) * t)) for i in range(3))


def font(path, size):
    return ImageFont.truetype(path, size)


def vertical_gradient(size, top, bottom):
    w, h = size
    img = Image.new("RGB", size)
    draw = ImageDraw.Draw(img)
    for y in range(h):
        t = y / max(1, h - 1)
        draw.line([(0, y), (w, y)], fill=lerp(top, bottom, t))
    return img


def rounded_mask(size, radius):
    mask = Image.new("L", size, 0)
    ImageDraw.Draw(mask).rounded_rectangle(
        [0, 0, size[0] - 1, size[1] - 1], radius=radius, fill=255
    )
    return mask


def fade_edges(size, fade=64):
    w, h = size
    mask = Image.new("L", size, 255)
    draw = ImageDraw.Draw(mask)
    for x in range(fade):
        value = int(255 * (x / fade) ** 1.4)
        draw.line([(x, 0), (x, h)], fill=value)
        draw.line([(w - 1 - x, 0), (w - 1 - x, h)], fill=value)
    return mask


def text_mask(size, xy, text, font, anchor=None):
    mask = Image.new("L", size, 0)
    ImageDraw.Draw(mask).text(xy, text, font=font, fill=255, anchor=anchor)
    return mask


def gradient_fill(size, stops):
    """Horizontal multi-stop gradient image."""
    w, h = size
    img = Image.new("RGB", size)
    draw = ImageDraw.Draw(img)
    for x in range(w):
        t = x / max(1, w - 1)
        scaled = t * (len(stops) - 1)
        index = min(int(scaled), len(stops) - 2)
        local = scaled - index
        draw.line([(x, 0), (x, h)], fill=lerp(stops[index], stops[index + 1], local))
    return img


def palette(frame, colors=128):
    return frame.convert("RGB").convert(
        "P", palette=Image.ADAPTIVE, colors=colors, dither=Image.NONE
    )


# ---------------------------------------------------------------------------
# Hero banner
# ---------------------------------------------------------------------------

HERO_W, HERO_H = 1000, 300
HERO_FRAMES = 24
HERO_MS = 100


def build_hero():
    name_font = font(FONT_BOLD, 74)
    prompt_font = font(FONT_BOLD, 13)
    meta_font = font(FONT_REG, 12)
    role_font = font(FONT_BOLD, 15)
    desc_font = font(FONT_REG, 13)
    status_font = font(FONT_REG, 12)
    glyph_font = font(FONT_BOLD, 118)

    base = vertical_gradient((HERO_W, HERO_H), BG_TOP, BG_BOTTOM).convert("RGBA")
    draw = ImageDraw.Draw(base)

    # grid
    for x in range(0, HERO_W, 28):
        draw.line([(x, 0), (x, HERO_H)], fill=(34, 211, 238, 11))
    for y in range(0, HERO_H, 28):
        draw.line([(0, y), (HERO_W, y)], fill=(34, 211, 238, 11))

    # outer frame + terminal panel
    draw.rounded_rectangle(
        [0, 0, HERO_W - 1, HERO_H - 1], radius=22, outline=(34, 211, 238, 120), width=2
    )
    draw.rounded_rectangle(
        [16, 16, HERO_W - 17, HERO_H - 17],
        radius=16,
        fill=(4, 9, 16, 242),
        outline=(21, 94, 117, 190),
        width=1,
    )
    draw.line([(17, 56), (HERO_W - 18, 56)], fill=(22, 78, 99, 190))

    # window chrome
    for cx, color in ((38, (255, 95, 87)), (56, (254, 188, 46)), (74, (40, 200, 64))):
        draw.ellipse([cx - 4, 30, cx + 4, 38], fill=color)
    draw.text(
        (HERO_W / 2, 34),
        "saihroo@github: ~/profile",
        font=meta_font,
        fill=(100, 116, 139),
        anchor="ma",
    )
    draw.text((HERO_W - 34, 34), "zsh", font=meta_font, fill=(71, 85, 105), anchor="ra")

    # prompt
    prompt_y = 69
    draw.text((34, prompt_y), "saihroo@github", font=prompt_font, fill=CYAN)
    prompt_w = draw.textlength("saihroo@github", font=prompt_font)
    draw.text((34 + prompt_w, prompt_y), ":~$", font=prompt_font, fill=SLATE)
    cmd_x = 34 + prompt_w + draw.textlength(":~$", font=prompt_font) + 8

    # name with gradient + glow
    name_xy = (32, 88)
    name_mask = text_mask((HERO_W, HERO_H), name_xy, "saihroo", name_font)
    name_bbox = name_mask.getbbox()
    name_grad = gradient_fill((HERO_W, HERO_H), [CYAN_LIGHT, CYAN, CYAN_MID])
    base.paste(name_grad, (0, 0), name_mask)
    name_glow_mask = name_mask.filter(ImageFilter.GaussianBlur(13))

    # right side glyph
    glyph_xy = (792, 58)
    glyph_mask = text_mask((HERO_W, HERO_H), glyph_xy, "</>", glyph_font, anchor="ma")
    glyph_grad = gradient_fill((HERO_W, HERO_H), [CYAN_LIGHT, CYAN, BLUE])
    glyph_glow_mask = glyph_mask.filter(ImageFilter.GaussianBlur(16))

    # static copy
    draw.text((36, 188), "SOFTWARE ENGINEER", font=role_font, fill=CYAN_LIGHT)
    draw.text(
        (37, 214),
        "Full-Stack  ·  AI  ·  Mobile  ·  Game Dev",
        font=desc_font,
        fill=(148, 163, 184),
    )
    draw.text((38, 252), ">", font=status_font, fill=CYAN)
    draw.text((52, 252), "stack", font=status_font, fill=SLATE_DARK)
    draw.text(
        (96, 252),
        "TypeScript · Kotlin · Python · C# · Luau",
        font=status_font,
        fill=(203, 213, 225),
    )

    # decorative bits
    draw.text((712, 74), "{ }", font=font(FONT_BOLD, 16), fill=(103, 232, 249, 100))
    draw.text((930, 232), "0x1F", font=font(FONT_REG, 11), fill=(100, 116, 139, 130))
    draw.text((706, 236), "=>", font=font(FONT_BOLD, 14), fill=(129, 140, 248, 90))

    # scanline strip
    scan_h = 22
    scan = Image.new("RGBA", (HERO_W - 40, scan_h), (0, 0, 0, 0))
    scan_draw = ImageDraw.Draw(scan)
    for y in range(scan_h):
        t = y / (scan_h - 1)
        alpha = int(22 * math.sin(math.pi * t) ** 2)
        scan_draw.line([(0, y), (HERO_W - 40, y)], fill=CYAN + (alpha,))
    scan_draw.line([(0, scan_h // 2), (HERO_W - 40, scan_h // 2)], fill=CYAN_LIGHT + (95,))
    scan_draw.line([(0, scan_h // 2 + 1), (HERO_W - 40, scan_h // 2 + 1)], fill=CYAN + (45,))

    # bottom travelling bar
    bar_w = 170
    bar = Image.new("RGBA", (bar_w, 3), (0, 0, 0, 0))
    bar_draw = ImageDraw.Draw(bar)
    for x in range(bar_w):
        t = x / (bar_w - 1)
        alpha = int(240 * math.sin(math.pi * t) ** 1.5)
        bar_draw.line([(x, 0), (x, 2)], fill=CYAN_LIGHT + (alpha,))

    fade = fade_edges((HERO_W, HERO_H), fade=90)
    frames = []
    for f in range(HERO_FRAMES):
        phase = f / HERO_FRAMES
        img = base.copy()

        # name glow pulse
        glow_alpha = 0.42 + 0.20 * math.sin(2 * math.pi * phase)
        glow = Image.new("RGBA", img.size, CYAN + (255,))
        glow.putalpha(name_glow_mask.point(lambda v, a=glow_alpha: int(v * a)))
        img.alpha_composite(glow)

        # glyph glow pulse (opposite phase)
        glyph_alpha = 0.30 + 0.16 * math.sin(2 * math.pi * phase + math.pi)
        glyph_glow = Image.new("RGBA", img.size, CYAN + (255,))
        glyph_glow.putalpha(glyph_glow_mask.point(lambda v, a=glyph_alpha: int(v * a)))
        img.alpha_composite(glyph_glow)

        frame_draw = ImageDraw.Draw(img)

        # typed command
        typed = "whoami"[: min(6, 1 + f // 2)]
        frame_draw.text((cmd_x, prompt_y), typed, font=prompt_font, fill=TEXT)

        # cursor after command
        if f < 12 or (f // 6) % 2 == 0:
            cursor_x = cmd_x + frame_draw.textlength(typed, font=prompt_font) + 3
            frame_draw.rectangle(
                [cursor_x, prompt_y + 1, cursor_x + 8, prompt_y + 15], fill=CYAN
            )

        # rotating dashed ring behind the glyph
        ring_layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
        ring_draw = ImageDraw.Draw(ring_layer)
        offset = f * (360 / HERO_FRAMES)
        for i in range(7):
            start = offset + i * (360 / 7)
            ring_draw.arc(
                [672, 46, 910, 284],
                start=start,
                end=start + 9,
                fill=(34, 211, 238, 52),
                width=1,
            )
        img.alpha_composite(ring_layer)

        # glyph above the ring
        img.alpha_composite(glyph_glow)
        img.paste(glyph_grad, (0, 0), glyph_mask)

        # scanline
        scan_y = int(56 - scan_h + (227 + scan_h) * (f + 1) / HERO_FRAMES)
        img.alpha_composite(scan, (20, scan_y))

        # bottom accent
        bar_x = int(-bar_w + (HERO_W + bar_w) * (f + 1) / HERO_FRAMES)
        img.alpha_composite(bar, (bar_x, HERO_H - 9))

        img.putalpha(fade)
        frames.append(palette(img, 96))

    out = os.path.join(ASSETS, "hero.gif")
    frames[0].save(
        out,
        save_all=True,
        append_images=frames[1:],
        duration=HERO_MS,
        loop=0,
        optimize=True,
        disposal=2,
    )
    print("hero.gif", os.path.getsize(out), "bytes")


# ---------------------------------------------------------------------------
# Typing line
# ---------------------------------------------------------------------------

TYPE_W, TYPE_H = 760, 66
TYPE_MS = 70
ROLES = [
    "software engineer",
    "full-stack developer",
    "ai + automation",
    "android developer",
    "game developer",
]


def build_typing():
    body_font = font(FONT_BOLD, 20)
    prompt_font = font(FONT_REG, 13)

    base = Image.new("RGBA", (TYPE_W, TYPE_H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(base)
    draw.rounded_rectangle(
        [0, 0, TYPE_W - 1, TYPE_H - 1],
        radius=12,
        fill=(4, 10, 18, 255),
        outline=(34, 211, 238, 110),
        width=1,
    )
    draw.rounded_rectangle(
        [6, 6, TYPE_W - 7, TYPE_H - 7], radius=8, outline=(21, 94, 117, 90), width=1
    )
    draw.text((18, TYPE_H / 2 - 1), "saihroo@github:~$", font=prompt_font, fill=SLATE, anchor="lm")
    prompt_right = 18 + draw.textlength("saihroo@github:~$", font=prompt_font)
    text_x = prompt_right + 14

    def typed(role):
        return [(role[:i], True) for i in range(len(role) + 1)]

    def hold(role):
        return [(role, (i // 5) % 2 == 0) for i in range(10)]

    def erased(role):
        states = [(role[:i], True) for i in range(len(role) - 2, -1, -2)]
        states.append(("", True))
        return states

    states = hold(ROLES[0])
    for i in range(1, len(ROLES)):
        states += erased(ROLES[i - 1])
        states += typed(ROLES[i])
        states += hold(ROLES[i])
    states += erased(ROLES[-1])
    states += typed(ROLES[0])

    frames = []
    for text, cursor_on in states:
        img = base.copy()
        d = ImageDraw.Draw(img)
        d.text((text_x, TYPE_H / 2 - 1), text, font=body_font, fill=CYAN_LIGHT, anchor="lm")
        if cursor_on:
            cx = text_x + d.textlength(text, font=body_font) + 3
            d.rectangle([cx, TYPE_H / 2 - 12, cx + 10, TYPE_H / 2 + 12], fill=CYAN)
        frames.append(palette(img, 48))

    out = os.path.join(ASSETS, "typing.gif")
    frames[0].save(
        out,
        save_all=True,
        append_images=frames[1:],
        duration=TYPE_MS,
        loop=0,
        optimize=True,
        disposal=2,
    )
    print("typing.gif", os.path.getsize(out), "bytes", len(frames), "frames")


# ---------------------------------------------------------------------------
# Stack ticker
# ---------------------------------------------------------------------------

STACK_W, STACK_H = 880, 104
STACK_MS = 80
ROW1 = "TYPESCRIPT · JAVASCRIPT · REACT · KOTLIN · ANDROID · PYTHON · AI"
ROW2 = "C# · .NET · SQL · ROBLOX · LUAU · GIT · GITHUB · LINUX"


def build_ticker():
    mono = font(FONT_BOLD, 18)
    label_font = font(FONT_REG, 11)

    base = vertical_gradient((STACK_W, STACK_H), BG_TOP, BG_BOTTOM).convert("RGBA")
    draw = ImageDraw.Draw(base)
    for x in range(0, STACK_W, 28):
        draw.line([(x, 0), (x, STACK_H)], fill=(34, 211, 238, 8))
    for y in range(0, STACK_H, 28):
        draw.line([(0, y), (STACK_W, y)], fill=(34, 211, 238, 8))
    draw.rounded_rectangle(
        [0, 0, STACK_W - 1, STACK_H - 1],
        radius=14,
        fill=(4, 10, 18, 235),
        outline=(34, 211, 238, 105),
        width=1,
    )
    draw.line([(14, 28), (STACK_W - 15, 28)], fill=(22, 78, 99, 130))
    draw.text((18, 9), "stack --list", font=label_font, fill=SLATE)
    draw.text((STACK_W - 18, 9), "live", font=label_font, fill=(34, 211, 238, 160), anchor="ra")

    row1 = Image.new("RGBA", (3000, 40), (0, 0, 0, 0))
    rd = ImageDraw.Draw(row1)
    rd.text((0, 20), ROW1, font=mono, fill=CYAN_LIGHT, anchor="lm")
    w1 = int(rd.textlength(ROW1, font=mono)) + 42
    row1 = row1.crop((0, 0, w1, 40))

    row2 = Image.new("RGBA", (3000, 40), (0, 0, 0, 0))
    rd = ImageDraw.Draw(row2)
    rd.text((0, 20), ROW2, font=mono, fill=(103, 232, 249), anchor="lm")
    w2 = int(rd.textlength(ROW2, font=mono)) + 42
    row2 = row2.crop((0, 0, w2, 40))

    # period images with a trailing separator dot for a clean wrap
    def period(strip, text):
        img = Image.new("RGBA", (strip.width + 30, 40), (0, 0, 0, 0))
        img.alpha_composite(strip, (0, 0))
        d = ImageDraw.Draw(img)
        d.ellipse([strip.width + 10, 17, strip.width + 17, 24], fill=(34, 211, 238, 120))
        return img

    p1 = period(row1, ROW1)
    p2 = period(row2, ROW2)

    n = max(56, int(max(p1.width, p2.width) / 10))
    step1 = p1.width / n
    step2 = p2.width / n

    fade = fade_edges((STACK_W, 40), fade=100)

    frames = []
    for f in range(n):
        img = base.copy()
        off1 = (f * step1) % p1.width
        off2 = (f * step2) % p2.width

        layer1 = Image.new("RGBA", (STACK_W, 40), (0, 0, 0, 0))
        x = -off1
        while x < STACK_W:
            layer1.alpha_composite(p1, (int(x), 0))
            x += p1.width
        layer1.putalpha(ImageChops.multiply(layer1.getchannel("A"), fade))
        img.alpha_composite(layer1, (0, 38))

        layer2 = Image.new("RGBA", (STACK_W, 40), (0, 0, 0, 0))
        x = -((p2.width - off2) % p2.width)
        while x < STACK_W:
            layer2.alpha_composite(p2, (int(x), 0))
            x += p2.width
        layer2.putalpha(ImageChops.multiply(layer2.getchannel("A"), fade))
        img.alpha_composite(layer2, (0, 60))

        frames.append(palette(img, 64))

    out = os.path.join(ASSETS, "stack.gif")
    frames[0].save(
        out,
        save_all=True,
        append_images=frames[1:],
        duration=STACK_MS,
        loop=0,
        optimize=True,
        disposal=2,
    )
    print("stack.gif", os.path.getsize(out), "bytes", n, "frames")


# ---------------------------------------------------------------------------
# Chainsaw Man loop
# ---------------------------------------------------------------------------


def build_chainsaw():
    src = Image.open(os.path.join(ASSETS, "chainsaw-source.gif"))
    size = 220
    frames = []
    for i in range(src.n_frames):
        src.seek(i)
        frame = src.convert("RGBA")
        frame = frame.resize((size, size), Image.LANCZOS)
        frames.append(palette(frame, 128))
    out = os.path.join(ASSETS, "chainsaw.gif")
    frames[0].save(
        out,
        save_all=True,
        append_images=frames[1:],
        duration=70,
        loop=0,
        optimize=True,
        disposal=2,
    )
    print("chainsaw.gif", os.path.getsize(out), "bytes", len(frames), "frames")


if __name__ == "__main__":
    build_hero()
    build_typing()
    build_ticker()
    build_chainsaw()
