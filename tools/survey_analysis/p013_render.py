"""
Обложка P-013 — два mock-экрана с одинаковым контентом в разных темах.
Визуальная метафора: «тёмное (наше) vs светлое (их)».
"""
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import math

W, H = 1280, 720
BG = (14, 31, 28)
NEON_GREEN = (43, 255, 136)
WHITE = (255, 255, 255)
MUTED = (154, 181, 174)
SOFT = (110, 140, 132)
STROKE = (46, 69, 64)
DARK_CARD = (24, 42, 38)
SCREEN_BG_DARK = (10, 22, 20)
GRID = (20, 36, 33)

# светлая палитра — продуманная, не «дефолтная Material»
LIGHT_BG = (245, 247, 246)
LIGHT_CARD = (255, 255, 255)
LIGHT_TEXT = (20, 32, 30)
LIGHT_MUTED = (110, 130, 125)
LIGHT_STROKE = (218, 226, 223)
LIGHT_ACCENT = (15, 165, 95)   # приглушённый бренд-зелёный для светлого фона

INTER_PATH = "/home/claude/fonts/Inter-Bold.ttf"
BRAND_LOGO_PATH = "/home/claude/brand_logo.png"


def inter(size, weight="Bold"):
    f = ImageFont.truetype(INTER_PATH, size)
    f.set_variation_by_name(weight)
    return f


def circular_mask(size):
    mask = Image.new("L", (size, size), 0)
    ImageDraw.Draw(mask).ellipse([0, 0, size - 1, size - 1], fill=255)
    return mask


class Cover:
    def __init__(self):
        self.img = Image.new("RGB", (W, H), BG)
        self.draw = ImageDraw.Draw(self.img)

    def add_subtle_grid(self):
        for x in range(0, W, 80):
            self.draw.line([(x, 0), (x, H)], fill=GRID, width=1)
        for y in range(0, H, 80):
            self.draw.line([(0, y), (W, y)], fill=GRID, width=1)

    def add_brand_logo(self, cx, cy, size=80):
        logo = Image.open(BRAND_LOGO_PATH).convert("RGB")
        s = min(logo.size)
        cx0 = (logo.width - s) // 2
        cy0 = (logo.height - s) // 2
        logo = logo.crop((cx0, cy0, cx0 + s, cy0 + s)).resize((size, size), Image.LANCZOS)
        mask = circular_mask(size)
        pos = (cx - size // 2, cy - size // 2)
        self.img.paste(logo, pos, mask)
        self.draw.ellipse(
            [pos[0] - 1, pos[1] - 1, pos[0] + size, pos[1] + size],
            outline=NEON_GREEN, width=1,
        )

    def add_header(self):
        self.add_brand_logo(110, 95, size=80)
        self.draw.text((170, 76), "FINPILOT", font=inter(24, "Bold"), fill=WHITE)
        self.draw.text((170, 110), "UX-РАЗБОР · 02", font=inter(13, "Medium"),
                       fill=MUTED, spacing=4)

    def add_glow_text(self, xy, text, font, fill_color, glow_color, blur=10, alpha=160):
        layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        ld = ImageDraw.Draw(layer)
        ld.text(xy, text, font=font, fill=glow_color + (alpha,))
        for _ in range(2):
            layer = layer.filter(ImageFilter.GaussianBlur(radius=blur))
        self.img.paste(layer, (0, 0), layer)
        self.draw.text(xy, text, font=font, fill=fill_color)

    def add_title_block(self):
        # рубрика
        self.draw.text((110, 215), "КОНФЛИКТ", font=inter(20, "ExtraBold"),
                       fill=NEON_GREEN, spacing=6)
        # вертикальная зелёная полоса
        for i in range(280):
            t = i / 280
            r = int(43 + (212 - 43) * t)
            b = int(136 + (61 - 136) * t)
            self.draw.line([(86, 250 + i), (90, 250 + i)], fill=(r, 255, b), width=1)

        # Заголовок: «Бренд ≠ интерфейс.»
        # ≠ — символ из юникод. Inter поддерживает, проверим
        self.draw.text((110, 252), "Бренд",
                       font=inter(96, "ExtraBold"), fill=WHITE)
        # знак ≠ на отдельной строке с акцентом
        self.add_glow_text(
            (110, 362), "≠ интерфейс.",
            font=inter(76, "ExtraBold"),
            fill_color=NEON_GREEN, glow_color=NEON_GREEN, blur=10,
        )
        self.draw.text((114, 478),
                       "Когда айдентика противоречит пользователю",
                       font=inter(22, "Medium"), fill=MUTED)

    # ===== mock-экраны =====
    def draw_phone_frame(self, x, y, w, h, screen_fill, bezel_color=STROKE):
        self.draw.rounded_rectangle(
            [x - 3, y - 3, x + w + 3, y + h + 3],
            radius=27, fill=None, outline=bezel_color, width=2,
        )
        self.draw.rounded_rectangle(
            [x, y, x + w, y + h],
            radius=24, fill=screen_fill,
        )
        # notch
        nw = 80
        self.draw.rounded_rectangle(
            [x + (w - nw) // 2, y + 8, x + (w + nw) // 2, y + 22],
            radius=8, fill=(0, 0, 0),
        )

    def draw_screen_content(self, x, y, w, h, palette):
        """Один и тот же экран в разных темах. palette — dict с ключами."""
        # заголовок страницы
        self.draw.text((x + 20, y + 50), "Подушка",
                       font=inter(13, "Medium"), fill=palette["muted"])
        self.draw.text((x + 20, y + 68), "безопасности",
                       font=inter(13, "Medium"), fill=palette["muted"])

        # центральная карточка
        card_top = y + 110
        card_h = 130
        self.draw.rounded_rectangle(
            [x + 18, card_top, x + w - 18, card_top + card_h],
            radius=14, fill=palette["card"],
            outline=palette["stroke"], width=1,
        )
        self.draw.text((x + 32, card_top + 18), "BLR",
                       font=inter(13, "Medium"), fill=palette["muted"])
        self.draw.text((x + 32, card_top + 38), "4.2",
                       font=inter(54, "ExtraBold"), fill=palette["text"])
        self.draw.text((x + 32, card_top + 100), "месяца",
                       font=inter(13, "Medium"), fill=palette["muted"])

        # вторая карточка — пример другого числа (для разнообразия в макете)
        card2_top = card_top + card_h + 16
        card2_h = 100
        self.draw.rounded_rectangle(
            [x + 18, card2_top, x + w - 18, card2_top + card2_h],
            radius=14, fill=palette["card"],
            outline=palette["stroke"], width=1,
        )
        self.draw.text((x + 32, card2_top + 16), "Долговая нагрузка",
                       font=inter(11, "Medium"), fill=palette["muted"])
        # прогресс-бар имитация
        bar_y = card2_top + 50
        bar_w = w - 64
        self.draw.rounded_rectangle(
            [x + 32, bar_y, x + 32 + bar_w, bar_y + 8],
            radius=4, fill=palette["stroke"],
        )
        # заполненная часть бара
        fill_w = int(bar_w * 0.28)  # 28% — пример
        self.draw.rounded_rectangle(
            [x + 32, bar_y, x + 32 + fill_w, bar_y + 8],
            radius=4, fill=palette["accent"],
        )
        self.draw.text((x + 32, bar_y + 18), "28%",
                       font=inter(14, "ExtraBold"), fill=palette["text"])
        # норма-метка справа
        tw = self.draw.textlength("норма ≤ 40%", font=inter(11, "Medium"))
        self.draw.text((x + w - 32 - tw, bar_y + 20), "норма ≤ 40%",
                       font=inter(11, "Medium"), fill=palette["muted"])

    def draw_dark_screen(self, x, y, w, h):
        self.draw_phone_frame(x, y, w, h, SCREEN_BG_DARK, bezel_color=STROKE)
        palette = {
            "muted": MUTED, "text": WHITE, "card": DARK_CARD,
            "stroke": STROKE, "accent": NEON_GREEN,
        }
        self.draw_screen_content(x, y, w, h, palette)
        # подпись внизу
        self.draw.text((x, y + h + 16), "DARK · ИСХОДНОЕ",
                       font=inter(11, "ExtraBold"), fill=MUTED, spacing=3)

    def draw_light_screen(self, x, y, w, h):
        self.draw_phone_frame(x, y, w, h, LIGHT_BG, bezel_color=(80, 90, 88))
        palette = {
            "muted": LIGHT_MUTED, "text": LIGHT_TEXT, "card": LIGHT_CARD,
            "stroke": LIGHT_STROKE, "accent": LIGHT_ACCENT,
        }
        self.draw_screen_content(x, y, w, h, palette)
        # подпись внизу
        self.draw.text((x, y + h + 16), "LIGHT · НОВОЕ",
                       font=inter(11, "ExtraBold"), fill=NEON_GREEN, spacing=3)

    def add_mockups(self):
        m_w, m_h = 220, 420
        gap = 50
        x1 = 760
        y1 = 180
        x2 = x1 + m_w + gap

        self.draw_dark_screen(x1, y1, m_w, m_h)
        self.draw_light_screen(x2, y1, m_w, m_h)

    def add_footer(self):
        self.draw.line([(110, 658), (240, 658)], fill=NEON_GREEN, width=2)
        self.draw.text((110, 670), "POST 013  ·  BUILDING IN PUBLIC",
                       font=inter(13, "Medium"), fill=MUTED, spacing=4)

    def render(self, path):
        self.add_subtle_grid()
        self.add_header()
        self.add_title_block()
        self.add_mockups()
        self.add_footer()
        self.img.save(path, "PNG", optimize=True)


if __name__ == "__main__":
    Cover().render("/home/claude/p013_cover.png")
    print("rendered")
