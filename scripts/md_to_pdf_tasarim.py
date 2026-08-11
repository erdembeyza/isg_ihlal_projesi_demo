"""
tasarim_mimari.md → PDF
Orijinal tasarım dokümanı şablonuna yakın düzen: başlık + SORUMLU ile başlar,
bölümler (GENEL AÇIKLAMALAR, VERİ TABANI, DTO, COMPONENT, MODÜL) ve tablolar.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

from fpdf import FPDF

ROOT = Path(__file__).resolve().parents[1]
MD_PATH = ROOT / "tasarim_mimari.md"
OUT_PATH = ROOT / "ISG_Kural_Ihlal_Tespiti_Tasarim_Dokumani_v2.pdf"
OUT_DOWNLOADS = Path.home() / "Downloads" / "ISG_Kural_Ihlal_Tespiti_Tasarim_Dokumani_v2.pdf"

FONT_REG = "C:/Windows/Fonts/arial.ttf"
FONT_BOLD = "C:/Windows/Fonts/arialbd.ttf"

RED = (180, 40, 40)
DARK = (30, 30, 30)
GRAY = (80, 80, 80)
LIGHT = (245, 245, 245)
HEADER_BG = (204, 51, 51)


class TasarimPDF(FPDF):
    def header(self) -> None:
        if self.page_no() <= 1:
            return
        self.set_font("ArialTR", "", 8)
        self.set_text_color(120, 120, 120)
        self.set_x(self.l_margin)
        self.cell(
            self.epw,
            5,
            "İSG Kural İhlal Tespit ve Uyarı Sistemi – Tasarım Süreci Dokümanı v2.0",
            align="L",
        )
        self.ln(2)
        self.set_draw_color(*RED)
        self.set_line_width(0.35)
        self.line(self.l_margin, self.get_y(), self.w - self.r_margin, self.get_y())
        self.ln(5)

    def footer(self) -> None:
        self.set_y(-12)
        self.set_font("ArialTR", "", 8)
        self.set_text_color(120, 120, 120)
        self.cell(0, 8, f"{self.page_no()}", align="C")


def strip_md_inline(text: str) -> str:
    text = re.sub(r"\*\*(.+?)\*\*", r"\1", text)
    text = re.sub(r"`([^`]+)`", r"\1", text)
    text = re.sub(r"\\<", "<", text)
    text = re.sub(r"\\>", ">", text)
    text = text.replace("\\`", "`")
    for k, v in {
        "✅": "[OK]",
        "❌": "[X]",
        "—": "-",
        "–": "-",
        "→": "->",
        "←": "<-",
        "•": "-",
        "⚠": "!",
        "️": "",
        "’": "'",
        "‘": "'",
        "“": '"',
        "”": '"',
    }.items():
        text = text.replace(k, v)
    return text


def parse_table_row(line: str) -> list[str] | None:
    line = line.strip()
    if not line.startswith("|"):
        return None
    parts = [p.strip() for p in line.strip("|").split("|")]
    if all(re.fullmatch(r":?-{3,}:?", p) for p in parts):
        return None
    return [strip_md_inline(p) for p in parts]


def ensure_space(pdf: TasarimPDF, need: float = 18) -> None:
    if pdf.get_y() > pdf.h - pdf.b_margin - need:
        pdf.add_page()
        pdf.set_x(pdf.l_margin)


def write_text(
    pdf: TasarimPDF,
    text: str,
    *,
    size: int = 10,
    bold: bool = False,
    color=DARK,
    leading: float = 5.0,
    indent: float = 0,
) -> None:
    pdf.set_x(pdf.l_margin + indent)
    pdf.set_font("ArialTR", "B" if bold else "", size)
    pdf.set_text_color(*color)
    pdf.multi_cell(pdf.epw - indent, leading, text)
    pdf.set_x(pdf.l_margin)


def write_section(pdf: TasarimPDF, title: str) -> None:
    ensure_space(pdf, 28)
    pdf.ln(3)
    pdf.set_fill_color(*HEADER_BG)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("ArialTR", "B", 11)
    pdf.set_x(pdf.l_margin)
    pdf.cell(pdf.epw, 8, f"  {title}", fill=True)
    pdf.ln(10)
    pdf.set_text_color(*DARK)


def write_subsection(pdf: TasarimPDF, title: str) -> None:
    ensure_space(pdf, 20)
    pdf.ln(2)
    write_text(pdf, title, size=11, bold=True, color=RED, leading=6)
    pdf.set_draw_color(220, 220, 220)
    y = pdf.get_y()
    pdf.line(pdf.l_margin, y, pdf.w - pdf.r_margin, y)
    pdf.ln(3)


def write_label_block(pdf: TasarimPDF, label: str, body: str) -> None:
    ensure_space(pdf, 16)
    write_text(pdf, label, size=9, bold=True, color=RED, leading=4.8)
    write_text(pdf, body, size=9.5, color=DARK, leading=4.8)
    pdf.ln(1)


def write_bullet(pdf: TasarimPDF, text: str) -> None:
    ensure_space(pdf, 12)
    pdf.set_x(pdf.l_margin)
    pdf.set_font("ArialTR", "", 9.5)
    pdf.set_text_color(*DARK)
    bullet = "-  "
    pdf.set_font("ArialTR", "B", 9.5)
    pdf.cell(5, 4.8, bullet)
    pdf.set_font("ArialTR", "", 9.5)
    pdf.multi_cell(pdf.epw - 5, 4.8, text)
    pdf.set_x(pdf.l_margin)


def write_table(pdf: TasarimPDF, rows: list[list[str]]) -> None:
    if not rows:
        return
    cols = max(len(r) for r in rows)
    for r in rows:
        while len(r) < cols:
            r.append("")

    usable = pdf.epw
    if cols == 2:
        widths = [usable * 0.36, usable * 0.64]
    elif cols == 3:
        widths = [usable * 0.28, usable * 0.28, usable * 0.44]
    elif cols == 4:
        widths = [usable * 0.26, usable * 0.20, usable * 0.16, usable * 0.38]
    elif cols == 5:
        # Sütun Adı | Veri Tipi | Not Null | PK/FK | Açıklama  (orijinal şablon)
        widths = [usable * 0.20, usable * 0.16, usable * 0.12, usable * 0.10, usable * 0.42]
    else:
        widths = [usable / cols] * cols

    line_h = 4.0
    for i, row in enumerate(rows):
        pdf.set_font("ArialTR", "B" if i == 0 else "", 7.5)
        max_lines = 1
        for j, cell in enumerate(row):
            w = max(widths[j] - 1.4, 4)
            lines = pdf.multi_cell(w, line_h, cell or " ", dry_run=True, output="LINES")
            max_lines = max(max_lines, max(1, len(lines)))
        row_h = max_lines * line_h + 1.2

        if pdf.get_y() + row_h > pdf.h - pdf.b_margin - 8:
            pdf.add_page()
            pdf.set_x(pdf.l_margin)

        y0 = pdf.get_y()
        x0 = pdf.l_margin
        if i == 0:
            pdf.set_fill_color(*HEADER_BG)
            pdf.set_text_color(255, 255, 255)
        elif i % 2 == 0:
            pdf.set_fill_color(*LIGHT)
            pdf.set_text_color(*DARK)
        else:
            pdf.set_fill_color(255, 255, 255)
            pdf.set_text_color(*DARK)

        for j, cell in enumerate(row):
            x = x0 + sum(widths[:j])
            pdf.rect(x, y0, widths[j], row_h, style="F")
            pdf.set_xy(x + 0.6, y0 + 0.5)
            pdf.set_font("ArialTR", "B" if i == 0 else "", 7.5)
            pdf.multi_cell(max(widths[j] - 1.2, 4), line_h, cell or " ")
        pdf.set_y(y0 + row_h)
        pdf.set_x(pdf.l_margin)
        pdf.set_draw_color(220, 220, 220)
        pdf.line(x0, pdf.get_y(), x0 + usable, pdf.get_y())
    pdf.ln(3)
    pdf.set_text_color(*DARK)


def build_pdf(md_text: str, out: Path) -> None:
    pdf = TasarimPDF(orientation="P", unit="mm", format="A4")
    pdf.set_margins(14, 14, 14)
    pdf.set_auto_page_break(auto=True, margin=14)
    pdf.add_font("ArialTR", "", FONT_REG)
    pdf.add_font("ArialTR", "B", FONT_BOLD)
    pdf.add_page()

    # Orijinal şablon gibi: başlık + SORUMLU (ayrı kapak yok)
    write_text(
        pdf,
        "İSG KURAL İHLAL TESPİT VE UYARI SİSTEMİ – TASARIM SÜRECİ DOKÜMANI",
        size=13,
        bold=True,
        color=RED,
        leading=6.5,
    )
    pdf.ln(1)
    write_text(pdf, "SORUMLU", size=10, bold=True, color=RED, leading=5)
    write_text(pdf, "Beyza Erdem", size=10, color=DARK, leading=5)
    write_text(pdf, "Doküman sürümü: 2.0 (revize — güncel uygulama)", size=9, color=GRAY, leading=4.5)
    write_text(pdf, "Önceki sürüm: 1.0 (ilk tasarım PDF'i)  |  Tarih: 10 Ağustos 2026", size=9, color=GRAY, leading=4.5)
    pdf.ln(2)
    pdf.set_draw_color(*RED)
    pdf.set_line_width(0.5)
    pdf.line(pdf.l_margin, pdf.get_y(), pdf.w - pdf.r_margin, pdf.get_y())
    pdf.ln(5)

    lines = md_text.splitlines()
    # Skip H1 + meta block already rendered
    start = 0
    if lines and lines[0].startswith("# "):
        start = 1
    while start < len(lines):
        s = lines[start].strip()
        if s.startswith("**SORUMLU") or s.startswith("**Doküman") or s.startswith("**Önceki") or s.startswith("**Tarih"):
            start += 1
            continue
        if s == "Beyza Erdem":
            start += 1
            continue
        if s == "" or s == "---":
            start += 1
            continue
        break

    i = start
    table_rows: list[list[str]] = []
    in_code = False
    code_buf: list[str] = []

    def flush_table() -> None:
        nonlocal table_rows
        if table_rows:
            write_table(pdf, table_rows)
            table_rows = []

    while i < len(lines):
        line = lines[i]

        if line.strip().startswith("```"):
            flush_table()
            if not in_code:
                in_code = True
                code_buf = []
            else:
                in_code = False
                ensure_space(pdf, 20)
                pdf.set_x(pdf.l_margin)
                pdf.set_font("ArialTR", "", 8)
                pdf.set_fill_color(*LIGHT)
                pdf.set_text_color(*DARK)
                pdf.multi_cell(pdf.epw, 4.0, "\n".join(code_buf) if code_buf else " ", fill=True)
                pdf.set_x(pdf.l_margin)
                pdf.ln(2)
                code_buf = []
            i += 1
            continue

        if in_code:
            code_buf.append(line)
            i += 1
            continue

        if line.strip().startswith("|"):
            row = parse_table_row(line)
            if row is not None:
                table_rows.append(row)
            i += 1
            continue
        else:
            flush_table()

        if line.strip() == "---":
            pdf.ln(1)
            pdf.set_draw_color(220, 220, 220)
            pdf.line(pdf.l_margin, pdf.get_y(), pdf.w - pdf.r_margin, pdf.get_y())
            pdf.ln(4)
            i += 1
            continue

        if line.startswith("## "):
            flush_table()
            write_section(pdf, strip_md_inline(line[3:]))
            i += 1
            continue

        if line.startswith("### "):
            flush_table()
            write_subsection(pdf, strip_md_inline(line[4:]))
            i += 1
            continue

        if line.startswith("> "):
            write_text(pdf, strip_md_inline(line[2:]), size=8.5, color=GRAY, leading=4.5)
            pdf.ln(0.5)
            i += 1
            continue

        # "Tablo Tanımı:", "Model Tanımı:", "Bileşen Tanımı:", ...
        m = re.match(
            r"^\*\*(Tablo Tanımı|Model Tanımı|Bileşen Tanımı|Modül Tanımı|Aksiyon Listesi|Alt Bileşenler):\*\*\s*(.*)$",
            line,
        )
        if m:
            label = m.group(1)
            rest = strip_md_inline(m.group(2))
            if rest:
                write_label_block(pdf, label + ":", rest)
            else:
                write_text(pdf, label + ":", size=9, bold=True, color=RED, leading=4.8)
            i += 1
            continue

        if re.match(r"^[-*] ", line):
            write_bullet(pdf, strip_md_inline(line[2:]))
            i += 1
            continue

        if re.match(r"^\d+\.\s", line):
            write_text(pdf, strip_md_inline(line), size=9.5, leading=4.8)
            i += 1
            continue

        if line.strip() == "":
            pdf.ln(1.2)
            i += 1
            continue

        if line.startswith("# "):
            i += 1
            continue

        write_text(pdf, strip_md_inline(line), size=9.5, leading=4.8)
        i += 1

    flush_table()
    pdf.output(str(out))


def main() -> int:
    if not MD_PATH.exists():
        print("Bulunamadi:", MD_PATH, file=sys.stderr)
        return 1
    text = MD_PATH.read_text(encoding="utf-8")
    build_pdf(text, OUT_PATH)
    try:
        OUT_DOWNLOADS.write_bytes(OUT_PATH.read_bytes())
    except OSError:
        pass
    print("PDF olusturuldu:", OUT_PATH)
    print("Kopya:", OUT_DOWNLOADS)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
