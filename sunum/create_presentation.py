"""
Erdemir staj sunumu — İSG Kural İhlal Tespit ve Uyarı Sistemi
Şablon: beyaz zemin, kırmızı vurgu, Arial, ERDEMİR / OYAK MADEN METALÜRJİ
"""

from __future__ import annotations

from io import BytesIO
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.oxml.ns import qn
from pptx.util import Emu, Inches, Pt

# ── Marka renkleri (ErdemirOnline / şablon) ──────────────────────────
RED = RGBColor(0xCC, 0x33, 0x33)
DARK = RGBColor(0x22, 0x22, 0x22)
GRAY = RGBColor(0x66, 0x66, 0x66)
LIGHT_GRAY = RGBColor(0x99, 0x99, 0x99)
LINE_GRAY = RGBColor(0xDD, 0xDD, 0xDD)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
SOFT_BG = RGBColor(0xF7, 0xF7, 0xF7)
GREEN = RGBColor(0x2E, 0x7D, 0x32)
ORANGE = RGBColor(0xE6, 0x51, 0x00)

SLIDE_W = Inches(13.333)
SLIDE_H = Inches(7.5)
MARGIN_L = Inches(0.7)
MARGIN_R = Inches(0.7)
DATE_STR = "05.08.2026"
OUT_DIR = Path(__file__).resolve().parent
OUT_FILE = OUT_DIR / "Beyza_Erdem_ISG_Ihlal_Tespit_Sistemi.pptx"


def _font(size: int, bold: bool = False):
    candidates = [
        "C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf",
        "C:/Windows/Fonts/ARIALBD.TTF" if bold else "C:/Windows/Fonts/ARIAL.TTF",
    ]
    for path in candidates:
        try:
            return ImageFont.truetype(path, size)
        except OSError:
            continue
    return ImageFont.load_default()


def make_erdemir_logo(width: int = 420, height: int = 160) -> BytesIO:
    """Şablondaki kırmızı oval ERDEMİR logosu."""
    img = Image.new("RGBA", (width, height), (255, 255, 255, 0))
    draw = ImageDraw.Draw(img)
    pad = 4
    draw.ellipse([pad, pad, width - pad, height - pad], fill=(204, 51, 51, 255))
    # İç iki daire (marka motifine yakın sade yorum)
    cx, cy = width // 2, height // 2
    r1, r2 = int(height * 0.28), int(height * 0.16)
    draw.ellipse([cx - r1 - 40, cy - r1, cx - 40 + r1, cy + r1], outline=(255, 255, 255, 220), width=3)
    draw.ellipse([cx + 40 - r2, cy - r2, cx + 40 + r2, cy + r2], outline=(255, 255, 255, 220), width=3)
    font = _font(max(28, height // 3), bold=True)
    text = "ERDEMİR"
    bbox = draw.textbbox((0, 0), text, font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    draw.text(((width - tw) / 2, (height - th) / 2 - 2), text, fill=(255, 255, 255, 255), font=font)
    buf = BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return buf


def make_oyak_logo(width: int = 360, height: int = 70) -> BytesIO:
    """Altbilgi OYAK MADEN METALÜRJİ logosu."""
    img = Image.new("RGBA", (width, height), (255, 255, 255, 0))
    draw = ImageDraw.Draw(img)
    oval_w, oval_h = 58, 50
    ox, oy = 4, (height - oval_h) // 2
    draw.ellipse([ox, oy, ox + oval_w, oy + oval_h], fill=(204, 51, 51, 255))
    font_oyak = _font(16, bold=True)
    bbox = draw.textbbox((0, 0), "OYAK", font=font_oyak)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    draw.text((ox + (oval_w - tw) / 2, oy + (oval_h - th) / 2 - 1), "OYAK", fill=(255, 255, 255, 255), font=font_oyak)
    # Ayırıcı
    lx = ox + oval_w + 12
    draw.line([(lx, 12), (lx, height - 12)], fill=(180, 180, 180, 255), width=2)
    font_txt = _font(13, bold=True)
    draw.text((lx + 12, 16), "MADEN", fill=(102, 102, 102, 255), font=font_txt)
    draw.text((lx + 12, 36), "METALÜRJİ", fill=(102, 102, 102, 255), font=font_txt)
    buf = BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return buf


def set_run(run, text: str, size: int, bold: bool = False, color=DARK, italic: bool = False):
    run.text = text
    run.font.name = "Arial"
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.italic = italic
    run.font.color.rgb = color
    # East Asian / complex script fallback
    rPr = run._r.get_or_add_rPr()
    latin = rPr.find(qn("a:latin"))
    if latin is None:
        latin = rPr.makeelement(qn("a:latin"), {})
        rPr.insert(0, latin)
    latin.set("typeface", "Arial")


def add_text_box(slide, left, top, width, height, text, size=18, bold=False, color=DARK,
                 align=PP_ALIGN.LEFT, italic=False, anchor=MSO_ANCHOR.TOP):
    box = slide.shapes.add_textbox(left, top, width, height)
    tf = box.text_frame
    tf.word_wrap = True
    tf.auto_size = None
    try:
        tf._txBody.bodyPr.set("anchor", {MSO_ANCHOR.TOP: "t", MSO_ANCHOR.MIDDLE: "ctr", MSO_ANCHOR.BOTTOM: "b"}[anchor])
    except Exception:
        pass
    p = tf.paragraphs[0]
    p.alignment = align
    set_run(p.add_run(), text, size, bold, color, italic)
    return box


def add_paragraphs(slide, left, top, width, height, lines, size=16, color=DARK, bold=False, spacing=6):
    """lines: list[str] or list[tuple(str, dict)]"""
    box = slide.shapes.add_textbox(left, top, width, height)
    tf = box.text_frame
    tf.word_wrap = True
    for i, line in enumerate(lines):
        if isinstance(line, tuple):
            text, opts = line
        else:
            text, opts = line, {}
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = opts.get("align", PP_ALIGN.LEFT)
        p.space_after = Pt(opts.get("spacing", spacing))
        set_run(
            p.add_run(),
            text,
            opts.get("size", size),
            opts.get("bold", bold),
            opts.get("color", color),
            opts.get("italic", False),
        )
    return box


def add_bullet_block(slide, left, top, width, height, items, size=16, color=DARK):
    box = slide.shapes.add_textbox(left, top, width, height)
    tf = box.text_frame
    tf.word_wrap = True
    for i, item in enumerate(items):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = PP_ALIGN.LEFT
        p.space_after = Pt(8)
        p.level = 0
        # Bullet via text prefix for reliable cross-PPT rendering
        set_run(p.add_run(), f"•  {item}", size, False, color)
    return box


def draw_rect(slide, left, top, width, height, fill=None, line=None, line_w=Pt(1)):
    shape = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, left, top, width, height)
    shape.shadow.inherit = False
    if fill is None:
        shape.fill.background()
    else:
        shape.fill.solid()
        shape.fill.fore_color.rgb = fill
    if line is None:
        shape.line.fill.background()
    else:
        shape.line.color.rgb = line
        shape.line.width = line_w
    return shape


def draw_round_rect(slide, left, top, width, height, fill=SOFT_BG, line=None):
    shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
    shape.shadow.inherit = False
    shape.fill.solid()
    shape.fill.fore_color.rgb = fill
    if line is None:
        shape.line.fill.background()
    else:
        shape.line.color.rgb = line
        shape.line.width = Pt(1)
    # milder corner
    try:
        shape.adjustments[0] = 0.08
    except Exception:
        pass
    return shape


def add_content_chrome(slide, page: int, total: int, erdemir_logo: BytesIO, oyak_logo: BytesIO):
    """Üst gri çizgi + sağ üst logo; alt sayfa/tarih + OYAK logosu."""
    # Üst ince çizgi
    line = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.5), Inches(0.55), Inches(12.333), Pt(1.25))
    line.fill.solid()
    line.fill.fore_color.rgb = LINE_GRAY
    line.line.fill.background()
    line.shadow.inherit = False

    # Sağ üst Erdemir logosu
    erdemir_logo.seek(0)
    slide.shapes.add_picture(erdemir_logo, Inches(11.55), Inches(0.12), height=Inches(0.38))

    # Alt sol: sayfa / tarih
    add_text_box(
        slide, Inches(0.55), Inches(7.05), Inches(2.2), Inches(0.3),
        f"{page}/{total}", size=11, color=GRAY,
    )
    # kırmızı dikey kısa çizgi
    v = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(1.15), Inches(7.1), Pt(1.5), Inches(0.18))
    v.fill.solid()
    v.fill.fore_color.rgb = RED
    v.line.fill.background()
    v.shadow.inherit = False
    add_text_box(
        slide, Inches(1.3), Inches(7.05), Inches(1.5), Inches(0.3),
        DATE_STR, size=11, color=GRAY,
    )

    # Alt orta OYAK
    oyak_logo.seek(0)
    slide.shapes.add_picture(oyak_logo, Inches(5.55), Inches(6.95), height=Inches(0.38))


def add_slide_title(slide, title: str):
    add_text_box(
        slide, MARGIN_L, Inches(0.72), Inches(11.5), Inches(0.55),
        title, size=28, bold=True, color=DARK,
    )


def build():
    prs = Presentation()
    prs.slide_width = SLIDE_W
    prs.slide_height = SLIDE_H
    blank = prs.slide_layouts[6]

    erdemir_large = make_erdemir_logo(480, 170)
    erdemir_small = make_erdemir_logo(280, 100)
    oyak = make_oyak_logo(340, 68)

    TOTAL = 11

    # ══════════════════════════════════════════════════════════════════
    # 1) KAPAK
    # ══════════════════════════════════════════════════════════════════
    s = prs.slides.add_slide(blank)
    erdemir_large.seek(0)
    s.shapes.add_picture(erdemir_large, Inches(0.9), Inches(2.35), width=Inches(4.6))

    oyak.seek(0)
    s.shapes.add_picture(oyak, Inches(1.15), Inches(6.55), height=Inches(0.42))

    # Dikey kırmızı ayırıcı
    vline = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(6.35), Inches(1.6), Pt(2.25), Inches(4.4))
    vline.fill.solid()
    vline.fill.fore_color.rgb = RED
    vline.line.fill.background()
    vline.shadow.inherit = False

    add_text_box(
        s, Inches(6.8), Inches(2.2), Inches(5.8), Inches(1.4),
        "İSG Kural İhlal Tespit\nve Uyarı Sistemi",
        size=30, bold=True, color=DARK,
    )
    add_text_box(
        s, Inches(6.8), Inches(3.85), Inches(5.5), Inches(0.4),
        "Beyza Erdem", size=18, bold=True, color=DARK,
    )
    add_text_box(
        s, Inches(6.8), Inches(4.25), Inches(5.5), Inches(0.35),
        "Stajyer — Bilgi Teknolojileri / İSG Dijitalleşme", size=14, color=GRAY,
    )
    add_text_box(
        s, Inches(6.8), Inches(4.7), Inches(5.5), Inches(0.35),
        DATE_STR, size=13, italic=True, color=LIGHT_GRAY,
    )
    add_text_box(
        s, Inches(6.8), Inches(5.3), Inches(5.5), Inches(0.5),
        "Mevcut sahalar kameralarıyla gerçek zamanlı KKD denetimi",
        size=12, color=GRAY,
    )

    # ══════════════════════════════════════════════════════════════════
    # 2) GÜNDEM
    # ══════════════════════════════════════════════════════════════════
    s = prs.slides.add_slide(blank)
    add_content_chrome(s, 2, TOTAL, erdemir_small, oyak)
    add_slide_title(s, "Gündem")

    agenda = [
        ("01", "Problem", "Demir-çelik sahasında KKD ihlali riski"),
        ("02", "Çözüm", "Kamera + YOLOv8 + web paneli"),
        ("03", "Mimari & Akış", "Üç katmanlı uçtan uca sistem"),
        ("04", "İSG Farkındalığı", "Baret, yelek, gözlük ve güvenli çalışma"),
        ("05", "Fabrika Bağlantısı", "Haddehane / formen / uygulanabilirlik"),
        ("06", "Sonuç & Yol Haritası", "Kazanımlar, sınırlar, sonraki adımlar"),
    ]
    y0 = Inches(1.45)
    for i, (num, title, desc) in enumerate(agenda):
        y = y0 + Inches(i * 0.78)
        # num box
        draw_round_rect(s, MARGIN_L, y, Inches(0.7), Inches(0.58), fill=RED)
        add_text_box(s, MARGIN_L, y + Inches(0.1), Inches(0.7), Inches(0.4), num, size=16, bold=True, color=WHITE, align=PP_ALIGN.CENTER)
        add_text_box(s, Inches(1.65), y + Inches(0.02), Inches(10), Inches(0.32), title, size=18, bold=True, color=DARK)
        add_text_box(s, Inches(1.65), y + Inches(0.32), Inches(10), Inches(0.28), desc, size=13, color=GRAY)

    # ══════════════════════════════════════════════════════════════════
    # 3) PROBLEM
    # ══════════════════════════════════════════════════════════════════
    s = prs.slides.add_slide(blank)
    add_content_chrome(s, 3, TOTAL, erdemir_small, oyak)
    add_slide_title(s, "Problem: Saha Kameraları Neden Yetmiyor?")

    cards = [
        ("Yüksek riskli ortam", "Sıcak/soğuk haddehane ve üretim\nsahalarında KKD eksikliği\nciddi iş kazasına yol açabilir."),
        ("Manuel denetim sınırı", "7/24 CCTV izlemek formenin\nzamanını alır; geç fark edilen\nihlal müdahaleyi geciktirir."),
        ("Kanıt ve izlenebilirlik", "İhlalin zamanı, bölgesi ve\nfotoğrafı sistematik\nkayıt altına alınmalıdır."),
    ]
    for i, (t, d) in enumerate(cards):
        x = Inches(0.7 + i * 4.1)
        draw_round_rect(s, x, Inches(1.55), Inches(3.85), Inches(3.5), fill=SOFT_BG)
        bar = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, x, Inches(1.55), Inches(3.85), Pt(5))
        bar.fill.solid()
        bar.fill.fore_color.rgb = RED
        bar.line.fill.background()
        bar.shadow.inherit = False
        add_text_box(s, x + Inches(0.25), Inches(1.9), Inches(3.35), Inches(0.7), t, size=18, bold=True, color=DARK)
        add_text_box(s, x + Inches(0.25), Inches(2.7), Inches(3.35), Inches(2.0), d, size=14, color=GRAY)

    add_text_box(
        s, MARGIN_L, Inches(5.35), Inches(12), Inches(0.8),
        "Hedef: Mevcut güvenlik kameralarını kullanarak, ek donanım maliyeti olmadan, "
        "KKD ihlallerini proaktif ve otomatik olarak tespit etmek.",
        size=15, bold=True, color=DARK,
    )

    # ══════════════════════════════════════════════════════════════════
    # 4) ÇÖZÜM
    # ══════════════════════════════════════════════════════════════════
    s = prs.slides.add_slide(blank)
    add_content_chrome(s, 4, TOTAL, erdemir_small, oyak)
    add_slide_title(s, "Çözüm: Uçtan Uca İSG İhlal Sistemi")

    add_text_box(
        s, MARGIN_L, Inches(1.4), Inches(12), Inches(0.6),
        "Erdemir üretim sahalarında baret / yelek / gözlük takmayan personeli kamera görüntüsünden "
        "tespit eder, kanıt fotoğrafı kaydeder ve yetkili personele web panelinden raporlar.",
        size=15, color=DARK,
    )

    steps = [
        ("1", "Görüntü", "RTSP / webcam\nmevcut kameralar"),
        ("2", "Yapay Zeka", "YOLOv8 Nano\nKKD sınıf tespiti"),
        ("3", "Backend", "Spring Boot + JWT\nPostgreSQL kayıt"),
        ("4", "Panel", "Admin / Formen\nizleme & aksiyon"),
    ]
    for i, (n, t, d) in enumerate(steps):
        x = Inches(0.7 + i * 3.15)
        draw_round_rect(s, x, Inches(2.35), Inches(2.9), Inches(2.55), fill=WHITE, line=LINE_GRAY)
        circ = s.shapes.add_shape(MSO_SHAPE.OVAL, x + Inches(1.05), Inches(2.55), Inches(0.8), Inches(0.8))
        circ.fill.solid()
        circ.fill.fore_color.rgb = RED
        circ.line.fill.background()
        circ.shadow.inherit = False
        add_text_box(s, x + Inches(1.05), Inches(2.7), Inches(0.8), Inches(0.5), n, size=20, bold=True, color=WHITE, align=PP_ALIGN.CENTER)
        add_text_box(s, x + Inches(0.15), Inches(3.5), Inches(2.6), Inches(0.4), t, size=16, bold=True, color=DARK, align=PP_ALIGN.CENTER)
        add_text_box(s, x + Inches(0.15), Inches(3.95), Inches(2.6), Inches(0.7), d, size=12, color=GRAY, align=PP_ALIGN.CENTER)
        if i < 3:
            add_text_box(s, x + Inches(2.75), Inches(3.3), Inches(0.4), Inches(0.4), "→", size=22, bold=True, color=RED, align=PP_ALIGN.CENTER)

    add_text_box(
        s, MARGIN_L, Inches(5.3), Inches(12), Inches(0.55),
        "Sıfır yeni kamera yatırımı  ·  Bölge bazlı formen erişimi  ·  Haftalık PDF rapor + isteğe bağlı Telegram uyarısı",
        size=13, bold=True, color=GRAY,
    )

    # ══════════════════════════════════════════════════════════════════
    # 5) MİMARİ
    # ══════════════════════════════════════════════════════════════════
    s = prs.slides.add_slide(blank)
    add_content_chrome(s, 5, TOTAL, erdemir_small, oyak)
    add_slide_title(s, "Sistem Mimarisi — 3 Katman")

    layers = [
        ("AI Core", "Python 3.12 · Ultralytics YOLOv8n · OpenCV",
         ["Kamera akışını okur (RTSP/HTTP/webcam)", "KKD sınıflarını tespit eder", "IoU tracker ile ~8 sn süre eşiği", "Kanıt JPEG + heartbeat gönderir"]),
        ("Backend", "Java 21 · Spring Boot · JWT · Flyway · PostgreSQL",
         ["Kimlik doğrulama ve yetkilendirme", "İhlal kaydı, filtreleme, çözümleme", "Kamera durumu & denetim günlüğü", "Haftalık özet / PDF rapor API"]),
        ("Frontend", "Angular 22 · Chart.js · ErdemirOnline UI",
         ["ISG Yönetici paneli (tüm fabrika)", "Formen paneli (bölge bazlı)", "Görüntüleyici (salt okunur)", "İstatistik, kalite, kullanıcı yönetimi"]),
    ]
    for i, (title, stack, bullets) in enumerate(layers):
        x = Inches(0.55 + i * 4.2)
        draw_round_rect(s, x, Inches(1.4), Inches(4.0), Inches(5.1), fill=SOFT_BG)
        topbar = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, x, Inches(1.4), Inches(4.0), Inches(0.85))
        topbar.fill.solid()
        topbar.fill.fore_color.rgb = RED
        topbar.line.fill.background()
        topbar.shadow.inherit = False
        add_text_box(s, x + Inches(0.2), Inches(1.5), Inches(3.6), Inches(0.35), title, size=18, bold=True, color=WHITE)
        add_text_box(s, x + Inches(0.2), Inches(1.85), Inches(3.6), Inches(0.3), stack, size=10, color=RGBColor(0xFF, 0xE0, 0xE0))
        add_bullet_block(s, x + Inches(0.25), Inches(2.5), Inches(3.5), Inches(3.6), bullets, size=13, color=DARK)

    # ══════════════════════════════════════════════════════════════════
    # 6) TEKNİK AKIŞ
    # ══════════════════════════════════════════════════════════════════
    s = prs.slides.add_slide(blank)
    add_content_chrome(s, 6, TOTAL, erdemir_small, oyak)
    add_slide_title(s, "Tespit Akışı — Kameradan Panele")

    flow = [
        ("Kamera karesi", "RTSP / IP Webcam / video"),
        ("YOLOv8 analizi", "Her N karede PPE sınıfları"),
        ("Kişi eşleme", "NO-Hardhat / NO-Vest → kişi kutusu"),
        ("Süre eşiği", "IoU tracker ~8 sn (yanlış alarm ↓)"),
        ("Bildirim", "POST /api/ihlaller + fotoğraf"),
        ("Panel aksiyonu", "Aktif → Çözüldü / Hatalı tespit"),
    ]
    for i, (t, d) in enumerate(flow):
        row, col = divmod(i, 3)
        x = Inches(0.7 + col * 4.15)
        y = Inches(1.5 + row * 2.15)
        draw_round_rect(s, x, y, Inches(3.9), Inches(1.85), fill=WHITE, line=LINE_GRAY)
        badge = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x + Inches(0.2), y + Inches(0.25), Inches(0.55), Inches(0.45))
        badge.fill.solid()
        badge.fill.fore_color.rgb = RED
        badge.line.fill.background()
        badge.shadow.inherit = False
        add_text_box(s, x + Inches(0.2), y + Inches(0.3), Inches(0.55), Inches(0.35), str(i + 1), size=14, bold=True, color=WHITE, align=PP_ALIGN.CENTER)
        add_text_box(s, x + Inches(0.9), y + Inches(0.3), Inches(2.8), Inches(0.4), t, size=15, bold=True, color=DARK)
        add_text_box(s, x + Inches(0.25), y + Inches(0.95), Inches(3.4), Inches(0.6), d, size=13, color=GRAY)

    # ══════════════════════════════════════════════════════════════════
    # 7) İSG / KKD  (Değerlendirme Bölüm B — kritik)
    # ══════════════════════════════════════════════════════════════════
    s = prs.slides.add_slide(blank)
    add_content_chrome(s, 7, TOTAL, erdemir_small, oyak)
    add_slide_title(s, "İSG & KKD Farkındalığı")

    add_text_box(
        s, MARGIN_L, Inches(1.35), Inches(12), Inches(0.45),
        "Sistem, demir-çelik sahasında zorunlu kişisel koruyucu donanım kurallarını dijital olarak destekler.",
        size=14, color=GRAY,
    )

    kkd = [
        ("BARET", "Kafa travması / düşen cisim riskine karşı zorunlu. Model: NO-Hardhat tespiti."),
        ("YELEK", "Görünürlük ve saha ayrımı. Model: NO-Safety Vest tespiti."),
        ("GÖZLÜK", "Sıçrama / toz / kıvılcım riski. Sınıf haritası hazır; saha verisiyle fine-tune gerekir."),
    ]
    for i, (name, desc) in enumerate(kkd):
        y = Inches(1.95 + i * 1.05)
        draw_round_rect(s, MARGIN_L, y, Inches(12.0), Inches(0.9), fill=SOFT_BG)
        tag = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.9), y + Inches(0.2), Inches(1.6), Inches(0.5))
        tag.fill.solid()
        tag.fill.fore_color.rgb = RED
        tag.line.fill.background()
        tag.shadow.inherit = False
        add_text_box(s, Inches(0.9), y + Inches(0.28), Inches(1.6), Inches(0.35), name, size=13, bold=True, color=WHITE, align=PP_ALIGN.CENTER)
        add_text_box(s, Inches(2.8), y + Inches(0.28), Inches(9.5), Inches(0.45), desc, size=14, color=DARK)

    add_paragraphs(
        s, MARGIN_L, Inches(5.25), Inches(12), Inches(1.2),
        [
            ("Güvenli çalışma yaklaşımı", {"size": 14, "bold": True, "color": DARK}),
            ("•  Yanlış pozitifler «Hatalı tespit» ile ayıklanır → model iyileştirme havuzuna düşer (sürekli kalite).", {"size": 13, "color": GRAY}),
            ("•  Formen sahada müdahale eder; İSG yöneticisi fabrika genelini izler ve raporlar.", {"size": 13, "color": GRAY}),
        ],
        spacing=4,
    )

    # ══════════════════════════════════════════════════════════════════
    # 8) FABRİKA BAĞLANTISI (Bölüm C)
    # ══════════════════════════════════════════════════════════════════
    s = prs.slides.add_slide(blank)
    add_content_chrome(s, 8, TOTAL, erdemir_small, oyak)
    add_slide_title(s, "Fabrika / Proses Bağlantısı")

    add_text_box(
        s, MARGIN_L, Inches(1.35), Inches(12), Inches(0.4),
        "Sistem; Erdemir saha organizasyonuna (bölge + formen) göre tasarlandı.",
        size=14, color=GRAY,
    )

    # Sol: bölgeler
    draw_round_rect(s, MARGIN_L, Inches(1.9), Inches(5.9), Inches(4.4), fill=SOFT_BG)
    add_text_box(s, Inches(0.95), Inches(2.1), Inches(5.3), Inches(0.4), "Demo / saha bölgeleri", size=16, bold=True, color=DARK)
    regions = [
        "1. Sıcak Haddehane — hadde hattı çevresi",
        "1. Soğuk Haddehane — soğuk hadde sahası",
        "Veri Merkezi — kamera / entegrasyon demosu",
        "Çoklu kamera: PC + telefon + tablet akışı",
    ]
    add_bullet_block(s, Inches(0.95), Inches(2.65), Inches(5.3), Inches(3.2), regions, size=14)

    # Sağ: roller + uygulanabilirlik
    draw_round_rect(s, Inches(6.9), Inches(1.9), Inches(5.8), Inches(4.4), fill=SOFT_BG)
    add_text_box(s, Inches(7.15), Inches(2.1), Inches(5.3), Inches(0.4), "Rol → iş süreci", size=16, bold=True, color=DARK)
    roles = [
        "ISG_YONETICI: tüm fabrika, red/rapor/kullanıcı",
        "FORMEN: kendi bölgesi, çözümleme & takip",
        "GÖRÜNTÜLEYİCİ: üst yönetim salt okuma",
        "AI_CORE_SERVIS: yalnızca tespit servisi",
    ]
    add_bullet_block(s, Inches(7.15), Inches(2.65), Inches(5.3), Inches(3.2), roles, size=14)

    # ══════════════════════════════════════════════════════════════════
    # 9) PANEL & ÇIKTILAR
    # ══════════════════════════════════════════════════════════════════
    s = prs.slides.add_slide(blank)
    add_content_chrome(s, 9, TOTAL, erdemir_small, oyak)
    add_slide_title(s, "Panel Çıktıları ve Operasyonel Değer")

    outputs = [
        ("Canlı ihlal listesi", "Bölge, tip, süre, kanıt fotoğrafı, durum (Aktif / Çözüldü / Hatalı)"),
        ("KPI & trend", "Pasta grafik, haftalık değişim yüzdesi, model kalite grafiği"),
        ("Kamera sağlığı", "Heartbeat ile FPS / çevrimdışı kamera takibi"),
        ("Raporlama", "Haftalık PDF özet; isteğe bağlı Telegram anlık uyarı"),
        ("Denetim günlüğü", "Kim, ne zaman, hangi aksiyonu aldı — izlenebilirlik"),
        ("Fine-tune döngüsü", "Hatalı tespitler eğitim havuzuna → model iyileştirme"),
    ]
    for i, (t, d) in enumerate(outputs):
        col, row = divmod(i, 3)
        # wait - I want 2 rows of 3
        row, col = divmod(i, 3)
        x = Inches(0.7 + col * 4.15)
        y = Inches(1.45 + row * 2.35)
        draw_round_rect(s, x, y, Inches(3.95), Inches(2.1), fill=WHITE, line=LINE_GRAY)
        accent = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, x, y, Pt(6), Inches(2.1))
        accent.fill.solid()
        accent.fill.fore_color.rgb = RED
        accent.line.fill.background()
        accent.shadow.inherit = False
        add_text_box(s, x + Inches(0.3), y + Inches(0.35), Inches(3.4), Inches(0.45), t, size=15, bold=True, color=DARK)
        add_text_box(s, x + Inches(0.3), y + Inches(0.95), Inches(3.4), Inches(0.9), d, size=13, color=GRAY)

    # ══════════════════════════════════════════════════════════════════
    # 10) KAZANIMLAR / SINIRLAR / SONRAKI ADIMLAR
    # ══════════════════════════════════════════════════════════════════
    s = prs.slides.add_slide(blank)
    add_content_chrome(s, 10, TOTAL, erdemir_small, oyak)
    add_slide_title(s, "Kazanımlar, Sınırlar ve İyileştirme Alanları")

    cols = [
        ("Kazanımlar", GREEN, [
            "Faz 0–8 tamamlandı (uçtan uca)",
            "Mevcut kamera altyapısı kullanımı",
            "Rol bazlı erişim (JWT / RBAC)",
            "Çoklu kamera + rapor + denetim",
            "Formen sahada hızlı müdahale",
        ]),
        ("Mevcut sınırlar", ORANGE, [
            "Gözlük sınıfı için saha etiketi gerekir",
            "Genel PPE modeli → Erdemir fine-tune",
            "Yüz tanıma / sicil eşleme yok (bilinçli)",
            "Demo ortamı; üretim sertleştirmesi ayrı",
        ]),
        ("Sonraki adımlar", RED, [
            "Saha görüntüsüyle model fine-tune",
            "Gözlük veri setinin genişletilmesi",
            "Üretim RTSP & ağ sertleştirmesi",
            "İSG prosedürlerine resmi entegrasyon",
        ]),
    ]
    for i, (title, color, items) in enumerate(cols):
        x = Inches(0.55 + i * 4.2)
        draw_round_rect(s, x, Inches(1.4), Inches(4.0), Inches(5.0), fill=SOFT_BG)
        bar = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, x, Inches(1.4), Inches(4.0), Pt(6))
        bar.fill.solid()
        bar.fill.fore_color.rgb = color
        bar.line.fill.background()
        bar.shadow.inherit = False
        add_text_box(s, x + Inches(0.25), Inches(1.7), Inches(3.5), Inches(0.4), title, size=17, bold=True, color=DARK)
        add_bullet_block(s, x + Inches(0.25), Inches(2.3), Inches(3.5), Inches(3.8), items, size=13)

    # ══════════════════════════════════════════════════════════════════
    # 11) KAPANIŞ + KARİYER MOTİVASYONU
    # ══════════════════════════════════════════════════════════════════
    s = prs.slides.add_slide(blank)
    add_content_chrome(s, 11, TOTAL, erdemir_small, oyak)
    add_slide_title(s, "Özet & Teşekkürler")

    draw_round_rect(s, MARGIN_L, Inches(1.45), Inches(12.0), Inches(2.0), fill=SOFT_BG)
    add_text_box(
        s, Inches(0.95), Inches(1.7), Inches(11.3), Inches(1.5),
        "Erdemir sahalarında mevcut kameralarla, YOLOv8 ile baret ve yelek ihlallerini "
        "gerçek zamanlı yakalayan; formene ve İSG yöneticisine web panelinden raporlayan "
        "uçtan uca bir İSG dijitalleşme çözümüdür.",
        size=16, color=DARK,
    )

    add_text_box(
        s, MARGIN_L, Inches(3.7), Inches(12), Inches(0.4),
        "Kariyer motivasyonu", size=16, bold=True, color=RED,
    )
    add_text_box(
        s, MARGIN_L, Inches(4.15), Inches(12), Inches(1.2),
        "Demir-çelik sektörü; yüksek proses karmaşıklığı ve İSG disiplininin bir arada olduğu "
        "nadir alanlardan biridir. Bu stajda edindiğim saha bağlamını, yazılım ve yapay zekâ "
        "becerilerimle birleştirerek Erdemir’de güvenli, veriye dayalı üretim kültürüne katkı "
        "sunmak istiyorum.",
        size=14, color=DARK,
    )
    add_text_box(
        s, MARGIN_L, Inches(5.55), Inches(12), Inches(0.5),
        "Sorularınız için teşekkürler.",
        size=18, bold=True, color=DARK, align=PP_ALIGN.CENTER,
    )

    prs.save(OUT_FILE)
    print(f"OK: {OUT_FILE}")


if __name__ == "__main__":
    build()
