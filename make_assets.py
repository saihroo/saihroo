"""Generate the animated GIF assets for the saihroo GitHub profile."""

import math
import os

from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont, ImageOps

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
GITHUB_BG = (13, 17, 23)


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


def palette(frame, colors=128, bg=GITHUB_BG):
    if frame.mode == "RGBA":
        merged = Image.new("RGB", frame.size, bg)
        merged.paste(frame, (0, 0), frame)
        frame = merged
    return frame.convert("RGB").convert(
        "P", palette=Image.ADAPTIVE, colors=colors, dither=Image.NONE
    )


# ---------------------------------------------------------------------------
# Avatar
# ---------------------------------------------------------------------------

AVATAR = os.path.join(ASSETS, "avatar.png")

AVATAR_STOPS = [
    (0, (2, 6, 12)),
    (55, (7, 40, 60)),
    (125, (14, 165, 233)),
    (200, (103, 232, 249)),
    (255, (200, 250, 255)),
]


def gradient_map(stops):
    """Build a 768-entry RGB lookup table for a multi-stop gradient map."""
    lut = []
    for channel in range(3):
        for value in range(256):
            low, high = stops[0], stops[-1]
            for i in range(len(stops) - 1):
                if stops[i][0] <= value <= stops[i + 1][0]:
                    low, high = stops[i], stops[i + 1]
                    break
            span = max(1, high[0] - low[0])
            t = (value - low[0]) / span
            lut.append(
                int(low[1][channel] + (high[1][channel] - low[1][channel]) * t)
            )
    return lut


def build_avatar(size=204, pixels=102):
    """Crop the GitHub avatar, pixelate it, and tint it cyan."""
    im = Image.open(AVATAR).convert("RGB")
    im = im.crop((70, 20, 410, 360))
    im = im.resize((pixels, pixels), Image.LANCZOS)
    im = im.resize((size, size), Image.NEAREST)

    gray = ImageOps.autocontrast(im.convert("L"), cutoff=1)
    ghost = gray.convert("RGB").point(gradient_map(AVATAR_STOPS)).convert("RGBA")

    mask = Image.new("L", (size * 4, size * 4), 0)
    ImageDraw.Draw(mask).ellipse([0, 0, size * 4 - 1, size * 4 - 1], fill=255)
    mask = mask.resize((size, size), Image.LANCZOS)
    ghost.putalpha(mask)

    vignette = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    vd = ImageDraw.Draw(vignette)
    for i in range(16):
        alpha = int(80 * ((16 - i) / 16) ** 2)
        vd.ellipse([i, i, size - 1 - i, size - 1 - i], outline=(0, 0, 0, alpha))
    ghost.alpha_composite(vignette)

    rim = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    rd = ImageDraw.Draw(rim)
    rd.ellipse([1, 1, size - 2, size - 2], outline=CYAN + (235,), width=2)
    rd.arc([7, 7, size - 8, size - 8], 200, 335, fill=CYAN_LIGHT + (150,), width=1)
    ghost.alpha_composite(rim)
    return ghost, mask


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
    desc_font = font(FONT_REG, 14)
    status_font = font(FONT_REG, 12)

    card = vertical_gradient((HERO_W, HERO_H), BG_TOP, BG_BOTTOM).convert("RGBA")
    draw = ImageDraw.Draw(card)

    # grid
    for x in range(0, HERO_W, 28):
        draw.line([(x, 0), (x, HERO_H)], fill=(34, 211, 238, 12))
    for y in range(0, HERO_H, 28):
        draw.line([(0, y), (HERO_W, y)], fill=(34, 211, 238, 12))

    # frame
    draw.rounded_rectangle(
        [0, 0, HERO_W - 1, HERO_H - 1],
        radius=22,
        outline=(34, 211, 238, 150),
        width=2,
    )
    draw.rounded_rectangle(
        [15, 15, HERO_W - 16, HERO_H - 16],
        radius=16,
        outline=(21, 94, 117, 150),
        width=1,
    )
    draw.line([(16, 56), (HERO_W - 17, 56)], fill=(22, 78, 99, 190))

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
    draw.text((HERO_W - 32, 34), "zsh", font=meta_font, fill=(71, 85, 105), anchor="ra")

    # prompt
    prompt_y = 68
    draw.text((34, prompt_y), "saihroo@github", font=prompt_font, fill=CYAN)
    prompt_w = draw.textlength("saihroo@github", font=prompt_font)
    draw.text((34 + prompt_w, prompt_y), ":~$", font=prompt_font, fill=SLATE)
    cmd_x = 34 + prompt_w + draw.textlength(":~$", font=prompt_font) + 8

    # name
    name_mask = text_mask((HERO_W, HERO_H), (32, 85), "saihroo", name_font)
    name_grad = gradient_fill((HERO_W, HERO_H), [CYAN_LIGHT, CYAN, CYAN_MID])
    name_glow_mask = name_mask.filter(ImageFilter.GaussianBlur(14))

    # copy
    draw.text((36, 181), "SOFTWARE ENGINEER", font=role_font, fill=CYAN_LIGHT)
    draw.text(
        (37, 207),
        "Full-Stack  ·  AI + Automation  ·  Android  ·  Game Dev",
        font=desc_font,
        fill=(148, 163, 184),
    )
    draw.line([(36, 232), (560, 232)], fill=(34, 211, 238, 35))
    draw.text((38, 248), ">", font=status_font, fill=CYAN)
    draw.text((52, 248), "stack", font=status_font, fill=SLATE_DARK)
    draw.text(
        (92, 248),
        "TypeScript · Kotlin · Python · C# · Luau",
        font=status_font,
        fill=(203, 213, 225),
    )

    # decorative bits
    draw.text((636, 82), "{ }", font=font(FONT_BOLD, 18), fill=(103, 232, 249, 120))
    draw.text((648, 214), "=>", font=font(FONT_BOLD, 15), fill=(129, 140, 248, 110))
    draw.text((660, 250), "0x1F", font=font(FONT_REG, 11), fill=(100, 116, 139, 130))
    draw.text(
        (HERO_W - 32, 270),
        "locale: en / es",
        font=font(FONT_REG, 10),
        fill=(71, 85, 105),
        anchor="ra",
    )

    # avatar
    cx, cy = 842, 168
    avatar, avatar_mask = build_avatar()
    ax, ay = cx - avatar.width // 2, cy - avatar.height // 2

    glow = Image.new("RGBA", (320, 320), (0, 0, 0, 0))
    ImageDraw.Draw(glow).ellipse([48, 48, 272, 272], fill=CYAN + (95,))
    glow = glow.filter(ImageFilter.GaussianBlur(30))

    ring = Image.new("RGBA", (HERO_W, HERO_H), (0, 0, 0, 0))
    rd = ImageDraw.Draw(ring)
    for radius, alpha, width in ((108, 45, 1), (100, 80, 1)):
        rd.ellipse(
            [cx - radius, cy - radius, cx + radius, cy + radius],
            outline=CYAN + (alpha,),
            width=width,
        )
    for i in range(12):
        angle = math.radians(i * 30)
        rd.line(
            [
                (cx + math.cos(angle) * 103, cy + math.sin(angle) * 103),
                (cx + math.cos(angle) * 107, cy + math.sin(angle) * 107),
            ],
            fill=CYAN + (120,),
            width=1,
        )
    rd.text(
        (cx - 120, cy - 108),
        "ID 00",
        font=font(FONT_REG, 10),
        fill=(100, 116, 139, 190),
    )
    rd.text(
        (cx + 120, cy - 108),
        "● ONLINE",
        font=font(FONT_REG, 10),
        fill=CYAN + (170,),
        anchor="ra",
    )

    # scanline clipped to the avatar circle
    scan_h = 20
    scan = Image.new("RGBA", (avatar.width, avatar.height), (0, 0, 0, 0))
    sd = ImageDraw.Draw(scan)
    sd.rectangle([0, 0, avatar.width, scan_h], fill=CYAN + (18,))
    sd.line(
        [(0, scan_h - 3), (avatar.width, scan_h - 3)],
        fill=CYAN_LIGHT + (120,),
    )
    scan.putalpha(ImageChops.multiply(scan.getchannel("A"), avatar_mask))

    # bottom travelling bar
    bar_w = 170
    bar = Image.new("RGBA", (bar_w, 3), (0, 0, 0, 0))
    bd = ImageDraw.Draw(bar)
    for x in range(bar_w):
        t = x / (bar_w - 1)
        alpha = int(240 * math.sin(math.pi * t) ** 1.5)
        bd.line([(x, 0), (x, 2)], fill=CYAN_LIGHT + (alpha,))

    card_mask = rounded_mask((HERO_W, HERO_H), 22)
    frames = []
    for f in range(HERO_FRAMES):
        phase = f / HERO_FRAMES
        img = card.copy()

        # name glow pulse
        name_alpha = 0.36 + 0.18 * math.sin(2 * math.pi * phase)
        name_glow = Image.new("RGBA", img.size, CYAN + (255,))
        name_glow.putalpha(
            name_glow_mask.point(lambda v, a=name_alpha: int(v * a))
        )
        img.alpha_composite(name_glow)

        # avatar glow pulse
        avatar_alpha = 0.50 + 0.16 * math.sin(2 * math.pi * phase + math.pi)
        avatar_glow = glow.copy()
        avatar_glow.putalpha(
            avatar_glow.getchannel("A").point(lambda v, a=avatar_alpha: int(v * a))
        )
        img.alpha_composite(avatar_glow, (cx - 160, cy - 160))

        img.alpha_composite(ring)

        # rotating arcs
        arcs = Image.new("RGBA", img.size, (0, 0, 0, 0))
        ad = ImageDraw.Draw(arcs)
        offset = f * (360 / HERO_FRAMES)
        for i in range(3):
            start = offset + i * 120
            ad.arc(
                [cx - 100, cy - 100, cx + 100, cy + 100],
                start=start,
                end=start + 38,
                fill=CYAN_LIGHT + (185,),
                width=2,
            )
            end_angle = math.radians(start + 38)
            ex = cx + math.cos(end_angle) * 100
            ey = cy + math.sin(end_angle) * 100
            ad.ellipse([ex - 2, ey - 2, ex + 2, ey + 2], fill=CYAN_LIGHT + (220,))
        img.alpha_composite(arcs)

        # avatar and scan
        img.alpha_composite(avatar, (ax, ay))
        scan_y = int(
            -scan_h + (avatar.height + scan_h) * (f + 1) / HERO_FRAMES
        )
        img.alpha_composite(scan, (ax, ay + scan_y))

        # name above the animated layers
        img.paste(name_grad, (0, 0), name_mask)

        fd = ImageDraw.Draw(img)

        # typed command + cursor
        typed = "whoami"[: min(6, 1 + f // 2)]
        fd.text((cmd_x, prompt_y), typed, font=prompt_font, fill=TEXT)
        if f < 12 or (f // 4) % 2 == 0:
            cursor_x = cmd_x + fd.textlength(typed, font=prompt_font) + 3
            fd.rectangle(
                [cursor_x, prompt_y + 1, cursor_x + 8, prompt_y + 15],
                fill=CYAN,
            )

        # bottom accent
        bar_x = int(-bar_w + (HERO_W + bar_w) * (f + 1) / HERO_FRAMES)
        img.alpha_composite(bar, (bar_x, HERO_H - 9))

        img.putalpha(ImageChops.multiply(img.getchannel("A"), card_mask))
        bg = Image.new("RGB", (HERO_W, HERO_H), GITHUB_BG)
        bg.paste(img, (0, 0), img)
        frames.append(palette(bg, 96))

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
# Whoami card
# ---------------------------------------------------------------------------

WHO_W, WHO_H = 1000, 300


def build_whoami():
    prompt_font = font(FONT_BOLD, 12)
    name_font = font(FONT_BOLD, 44)
    role_font = font(FONT_BOLD, 14)
    body_font = font(FONT_REG, 14)
    tag_font = font(FONT_BOLD, 12)
    meta_font = font(FONT_REG, 11)
    focus_font = font(FONT_REG, 12)
    label_font = font(FONT_BOLD, 10)

    img = Image.new("RGBA", (WHO_W, WHO_H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    draw.rounded_rectangle(
        [0, 0, WHO_W - 1, WHO_H - 1],
        radius=18,
        fill=(4, 10, 18, 255),
        outline=(34, 211, 238, 120),
        width=1,
    )
    draw.rounded_rectangle(
        [7, 7, WHO_W - 8, WHO_H - 8],
        radius=13,
        outline=(21, 94, 117, 90),
        width=1,
    )
    draw.line([(8, 45), (WHO_W - 9, 45)], fill=(22, 78, 99, 180))

    for cx, color in ((26, (255, 95, 87)), (44, (254, 188, 46)), (62, (40, 200, 64))):
        draw.ellipse([cx - 4, 18, cx + 4, 26], fill=color)
    draw.text(
        (WHO_W / 2, 22),
        "saihroo@github: ~/whoami",
        font=meta_font,
        fill=(100, 116, 139),
        anchor="ma",
    )
    draw.text((WHO_W - 26, 22), "zsh", font=meta_font, fill=(71, 85, 105), anchor="ra")

    # accent rail
    draw.rounded_rectangle([0, 66, 3, 246], radius=2, fill=CYAN + (200,))

    # prompt
    draw.text((28, 58), "saihroo@github", font=prompt_font, fill=CYAN)
    prompt_w = draw.textlength("saihroo@github", font=prompt_font)
    draw.text((28 + prompt_w, 58), ":~$", font=prompt_font, fill=SLATE)
    cmd_x = 28 + prompt_w + draw.textlength(":~$", font=prompt_font) + 8
    draw.text((cmd_x, 58), "whoami", font=prompt_font, fill=TEXT)

    # name
    name_mask = text_mask((WHO_W, WHO_H), (27, 76), "saihroo", name_font)
    name_grad = gradient_fill((WHO_W, WHO_H), [CYAN_LIGHT, CYAN, CYAN_MID])
    name_glow = name_mask.filter(ImageFilter.GaussianBlur(10))
    glow_color = Image.new("RGBA", img.size, CYAN + (255,))
    glow_color.putalpha(name_glow.point(lambda v: int(v * 0.32)))
    img.alpha_composite(glow_color)
    img.paste(name_grad, (0, 0), name_mask)

    # role
    draw.text((30, 138), "SOFTWARE ENGINEER", font=role_font, fill=CYAN_LIGHT)
    role_w = draw.textlength("SOFTWARE ENGINEER", font=role_font)
    draw.text(
        (30 + role_w + 14, 139),
        "// full-stack · ai · mobile · games",
        font=meta_font,
        fill=SLATE,
    )
    draw.line([(28, 164), (972, 164)], fill=(34, 211, 238, 40))

    # bilingual bio
    draw.text((30, 180), "EN", font=tag_font, fill=CYAN)
    draw.text(
        (62, 176),
        "Software engineer: full-stack products, AI automation,",
        font=body_font,
        fill=(203, 213, 225),
    )
    draw.text(
        (62, 194),
        "Android apps and games.",
        font=body_font,
        fill=(203, 213, 225),
    )
    draw.text((30, 220), "ES", font=tag_font, fill=CYAN)
    draw.text(
        (62, 218),
        "Ingeniero de software: productos full-stack, IA,",
        font=body_font,
        fill=(203, 213, 225),
    )
    draw.text(
        (62, 236),
        "apps Android y videojuegos.",
        font=body_font,
        fill=(203, 213, 225),
    )

    # focus panel
    draw.rounded_rectangle(
        [704, 70, 970, 248],
        radius=10,
        fill=(5, 14, 24, 255),
        outline=(21, 94, 117, 150),
        width=1,
    )
    draw.text((720, 82), "FOCUS", font=label_font, fill=CYAN)
    draw.line([(720, 98), (954, 98)], fill=(21, 94, 117, 150))
    focus = ["full-stack", "ai + automation", "android", "game dev"]
    for i, item in enumerate(focus):
        y = 112 + i * 24
        draw.polygon(
            [(720, y + 5), (725, y), (730, y + 5), (725, y + 10)],
            fill=CYAN + (210,),
        )
        draw.text((740, y), item, font=focus_font, fill=(203, 213, 225))
    draw.line([(720, 202), (954, 202)], fill=(21, 94, 117, 150))
    draw.text((720, 212), "STATUS", font=label_font, fill=SLATE)
    draw.text(
        (954, 212),
        "● ONLINE",
        font=label_font,
        fill=CYAN,
        anchor="ra",
    )
    draw.text((720, 230), "LOCALE", font=label_font, fill=SLATE)
    draw.text((954, 230), "EN · ES", font=label_font, fill=(203, 213, 225), anchor="ra")

    # footer prompt
    draw.line([(24, 260), (976, 260)], fill=(34, 211, 238, 30))
    draw.text((30, 271), "saihroo@github:~$", font=meta_font, fill=SLATE)
    foot_w = draw.textlength("saihroo@github:~$", font=meta_font)
    draw.rectangle([30 + foot_w + 8, 269, 30 + foot_w + 16, 283], fill=CYAN)
    draw.text((970, 272), "0x1F", font=meta_font, fill=(71, 85, 105), anchor="ra")

    out = os.path.join(ASSETS, "whoami.png")
    img.save(out, optimize=True)
    print("whoami.png", os.path.getsize(out), "bytes")


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
    build_whoami()
    build_typing()
    build_chainsaw()
