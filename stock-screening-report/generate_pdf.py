#!/usr/bin/env python3
"""
Stock Screening Report PDF Generator
Usage: python3 generate_pdf.py <markdown_file> <output_pdf_path>
"""
import sys
import os
import re
from fpdf import FPDF

SKILL_DIR = os.path.dirname(os.path.abspath(__file__))
FONT_PATH = os.path.join(SKILL_DIR, "AppleSDGothicNeo-Regular.ttf")
FONT_BOLD_PATH = os.path.join(SKILL_DIR, "AppleSDGothicNeo-Bold.ttf")

TTC_SOURCE = "/System/Library/Fonts/AppleSDGothicNeo.ttc"


def ensure_fonts():
    """Extract Korean fonts from system TTC if local TTFs don't exist."""
    if os.path.exists(FONT_PATH) and os.path.exists(FONT_BOLD_PATH):
        return
    if not os.path.exists(TTC_SOURCE):
        return
    try:
        from fontTools.ttLib import TTCollection
        ttc = TTCollection(TTC_SOURCE)
        if not os.path.exists(FONT_PATH):
            ttc.fonts[0].save(FONT_PATH)  # Regular
        if not os.path.exists(FONT_BOLD_PATH):
            ttc.fonts[6].save(FONT_BOLD_PATH)  # Bold
    except Exception:
        pass


ensure_fonts()

# Colors
NAVY = (15, 32, 65)
DARK_GRAY = (50, 50, 50)
MID_GRAY = (120, 120, 120)
LIGHT_GRAY = (230, 230, 230)
WHITE = (255, 255, 255)
ACCENT_BLUE = (30, 90, 160)
ACCENT_GREEN = (34, 139, 34)
ACCENT_RED = (180, 30, 30)
TABLE_HEADER_BG = (25, 55, 95)
TABLE_ROW_ALT = (240, 245, 250)
BORDER_COLOR = (180, 190, 200)


class StockReportPDF(FPDF):
    def __init__(self):
        super().__init__("P", "mm", "A4")
        self.set_auto_page_break(auto=True, margin=20)
        # Register Korean font
        if os.path.exists(FONT_PATH):
            self.add_font("KR", "", FONT_PATH)
            if os.path.exists(FONT_BOLD_PATH):
                self.add_font("KR", "B", FONT_BOLD_PATH)
            else:
                self.add_font("KR", "B", FONT_PATH)
            self.kr_font = "KR"
        else:
            self.kr_font = "Helvetica"

    def header(self):
        if self.page_no() == 1:
            return
        self.set_fill_color(*NAVY)
        self.rect(0, 0, 210, 12, "F")
        self.set_font(self.kr_font, "", 7)
        self.set_text_color(*WHITE)
        self.set_xy(10, 3)
        self.cell(130, 5, "EQUITY RESEARCH  |  SCREENING REPORT  |  Institutional Use Only", align="L")
        self.set_xy(140, 3)
        self.cell(60, 5, f"Page {self.page_no()}", align="R")
        self.set_text_color(*DARK_GRAY)
        self.ln(15)

    def footer(self):
        self.set_y(-15)
        self.set_draw_color(*BORDER_COLOR)
        self.line(10, self.get_y(), 200, self.get_y())
        self.set_font(self.kr_font, "", 6)
        self.set_text_color(*MID_GRAY)
        self.cell(0, 10, "AI Equity Research Division  |  This report does not constitute investment advice.", align="C")

    def cover_page(self, date_str, count, tickers):
        self.add_page()
        # Navy banner
        self.set_fill_color(*NAVY)
        self.rect(0, 0, 210, 100, "F")
        # Title
        self.set_font(self.kr_font, "B", 28)
        self.set_text_color(*WHITE)
        self.set_xy(15, 25)
        self.cell(180, 14, "EQUITY RESEARCH", align="L")
        self.set_xy(15, 42)
        self.set_font(self.kr_font, "", 20)
        self.cell(180, 10, "SCREENING REPORT", align="L")
        # Divider line
        self.set_draw_color(100, 160, 230)
        self.set_line_width(0.8)
        self.line(15, 58, 100, 58)
        # Subtitle
        self.set_font(self.kr_font, "", 11)
        self.set_text_color(180, 200, 230)
        self.set_xy(15, 65)
        self.cell(180, 7, "Institutional Use Only", align="L")
        self.set_xy(15, 74)
        self.cell(180, 7, f"Coverage: {count} stock(s)  |  Universe: KRX (Korea Exchange)", align="L")
        self.set_xy(15, 83)
        self.cell(180, 7, f"Date: {date_str}", align="L")

        # Tickers block
        self.set_text_color(*DARK_GRAY)
        self.set_xy(15, 115)
        self.set_font(self.kr_font, "B", 13)
        self.cell(180, 10, "Coverage Universe", align="L")
        self.set_draw_color(*ACCENT_BLUE)
        self.set_line_width(0.6)
        self.line(15, 126, 80, 126)

        self.set_font(self.kr_font, "", 12)
        y = 133
        for t in tickers:
            self.set_xy(20, y)
            self.set_text_color(*ACCENT_BLUE)
            self.cell(5, 7, ">", align="L")
            self.set_text_color(*DARK_GRAY)
            self.cell(170, 7, f"  {t}", align="L")
            y += 10

        # Analyst info box
        self.set_fill_color(*TABLE_ROW_ALT)
        self.rect(15, 230, 180, 30, "F")
        self.set_font(self.kr_font, "", 9)
        self.set_text_color(*MID_GRAY)
        self.set_xy(20, 233)
        self.cell(170, 6, "Analyst: AI Equity Research Division")
        self.set_xy(20, 240)
        self.cell(170, 6, f"Report Generated: {date_str}")
        self.set_xy(20, 247)
        self.cell(170, 6, "Data Sources: Public market data (KRX, DART, Financial portals)")

    def section_title(self, number, title):
        self.ln(5)
        self.set_fill_color(*NAVY)
        self.rect(10, self.get_y(), 190, 9, "F")
        self.set_font(self.kr_font, "B", 11)
        self.set_text_color(*WHITE)
        self.set_x(14)
        self.cell(180, 9, f"{number}. {title}", align="L")
        self.ln(12)
        self.set_text_color(*DARK_GRAY)

    def sub_title(self, title):
        self.ln(3)
        self.set_font(self.kr_font, "B", 10)
        self.set_text_color(*ACCENT_BLUE)
        self.set_x(12)
        self.cell(180, 7, title, align="L")
        self.ln(8)
        self.set_text_color(*DARK_GRAY)

    def info_box(self, lines, box_color=ACCENT_BLUE):
        x0 = 14
        y0 = self.get_y()
        w = 182
        line_h = 6.5
        padding = 4
        box_h = len(lines) * line_h + padding * 2

        if y0 + box_h > 270:
            self.add_page()
            y0 = self.get_y()

        # Left accent bar
        self.set_fill_color(*box_color)
        self.rect(x0, y0, 2, box_h, "F")
        # Background
        self.set_fill_color(*TABLE_ROW_ALT)
        self.rect(x0 + 2, y0, w - 2, box_h, "F")

        self.set_font(self.kr_font, "", 9)
        self.set_text_color(*DARK_GRAY)
        cy = y0 + padding
        for line in lines:
            self.set_xy(x0 + 6, cy)
            # Handle star ratings and special chars
            self.cell(w - 8, line_h, line, align="L")
            cy += line_h
        self.set_y(y0 + box_h + 3)

    def kv_line(self, key, value, indent=14):
        self.set_font(self.kr_font, "B", 9)
        self.set_text_color(*MID_GRAY)
        self.set_x(indent)
        self.cell(55, 6, key, align="L")
        self.set_font(self.kr_font, "", 9)
        self.set_text_color(*DARK_GRAY)
        self.cell(125, 6, str(value), align="L")
        self.ln(6.5)

    def risk_line(self, text, indent=18):
        self.set_font(self.kr_font, "", 9)
        self.set_text_color(*ACCENT_RED)
        self.set_x(indent)
        self.cell(5, 6, "!", align="C")
        self.set_text_color(*DARK_GRAY)
        self.cell(165, 6, f" {text}", align="L")
        self.ln(6.5)

    def verdict_line(self, label, ticker, reason, color=ACCENT_BLUE):
        self.set_font(self.kr_font, "B", 10)
        self.set_text_color(*color)
        self.set_x(14)
        self.cell(30, 7, label, align="L")
        self.set_text_color(*DARK_GRAY)
        self.set_font(self.kr_font, "", 10)
        self.cell(155, 7, f"{ticker} -- {reason}", align="L")
        self.ln(9)

    def star_rating(self, category, ratings_dict):
        """ratings_dict: {ticker: int(1-5)}"""
        self.set_font(self.kr_font, "", 9)
        self.set_text_color(*DARK_GRAY)
        self.set_x(14)
        self.cell(35, 6, category, align="L")
        for ticker, stars in ratings_dict.items():
            filled = stars
            empty = 5 - stars
            rating_str = "*" * filled + "." * empty
            self.cell(35, 6, rating_str, align="C")
        self.ln(7)


def parse_markdown_report(md_path):
    """Parse the markdown report into structured sections."""
    with open(md_path, "r", encoding="utf-8") as f:
        content = f.read()
    return content


def extract_sections(content):
    """Extract major sections from the report content."""
    sections = {}
    current_section = "header"
    current_lines = []

    for line in content.split("\n"):
        # Check for section headers (Roman numerals or ━━━ dividers)
        section_match = re.match(r'^(I+V?\.?\s+.+|[IVX]+\.\s+.+)', line.strip())
        if section_match or line.strip().startswith("━"):
            if current_lines:
                sections[current_section] = "\n".join(current_lines)
            current_section = line.strip()[:40]
            current_lines = []
        current_lines.append(line)

    if current_lines:
        sections[current_section] = "\n".join(current_lines)

    return sections


def build_pdf_from_markdown(md_path, output_path):
    """Main function to build PDF from markdown report."""
    content = parse_markdown_report(md_path)
    lines = content.split("\n")

    pdf = StockReportPDF()

    # Extract metadata from content
    date_str = ""
    tickers = []
    for line in lines:
        if "Date:" in line:
            date_str = line.split("Date:")[-1].strip()
        # Find stock names in the screening summary table or individual analysis
        match = re.match(r'^.*[|].*([A-Z가-힣]+.*)\s*[|]', line)
        ticker_match = re.search(r'[■]\s*(.+?)\s*\(', line)
        if ticker_match:
            tickers.append(ticker_match.group(1).strip())

    if not date_str:
        from datetime import date
        date_str = date.today().strftime("%Y-%m-%d")
    if not tickers:
        # Try to find tickers from content
        for line in lines:
            m = re.search(r'[■]\s*(.+?)[\s(]', line)
            if m:
                tickers.append(m.group(1).strip())

    count = max(len(tickers), 1)

    # Cover page
    pdf.cover_page(date_str, count, tickers if tickers else ["(see report)"])

    # Parse and render content
    pdf.add_page()
    in_box = False
    box_lines = []
    current_section_num = ""

    for line in lines:
        stripped = line.strip()

        # Skip pure decoration lines
        if re.match(r'^[━─]+$', stripped):
            continue
        if stripped == "" and not in_box:
            pdf.ln(2)
            continue

        # Section headers (I. II. III. etc)
        section_match = re.match(r'^(I{1,3}V?|IV|V)\.\s+(.+)', stripped)
        if section_match:
            num = section_match.group(1)
            title = section_match.group(2)
            pdf.section_title(num, title)
            continue

        # Sub-headers with box drawing chars
        if stripped.startswith("■"):
            pdf.ln(3)
            pdf.sub_title(stripped)
            continue

        # Box start
        if "┌──" in stripped or "┌─" in stripped:
            in_box = True
            box_title = re.sub(r'[┌─┐]', '', stripped).strip()
            box_lines = []
            if box_title:
                box_lines.append(f"[ {box_title} ]")
            continue

        # Box end
        if "└──" in stripped or "└─" in stripped:
            in_box = False
            if box_lines:
                color = ACCENT_BLUE
                for bl in box_lines:
                    if "Risk" in bl:
                        color = ACCENT_RED
                        break
                    if "Moat" in bl:
                        color = ACCENT_GREEN
                        break
                pdf.info_box(box_lines, color)
            box_lines = []
            continue

        # Inside a box
        if in_box:
            clean = re.sub(r'[│┤├]', '', stripped).strip()
            if clean:
                box_lines.append(clean)
            continue

        # Table rows
        if stripped.startswith("┌") or stripped.startswith("├") or stripped.startswith("└"):
            continue
        if "|" in stripped and "Ticker" not in stripped:
            cells = [c.strip() for c in stripped.split("|") if c.strip()]
            if cells:
                row_text = "  |  ".join(cells)
                pdf.set_font(pdf.kr_font, "", 9)
                pdf.set_x(14)
                pdf.cell(182, 6.5, row_text, align="L")
                pdf.ln(7)
                continue
        if "Ticker" in stripped:
            cells = [c.strip() for c in stripped.split("|") if c.strip()]
            row_text = "  |  ".join(cells)
            pdf.set_fill_color(*TABLE_HEADER_BG)
            pdf.set_text_color(*WHITE)
            pdf.set_font(pdf.kr_font, "B", 9)
            pdf.set_x(14)
            pdf.cell(182, 7, row_text, fill=True, align="L")
            pdf.ln(8)
            pdf.set_text_color(*DARK_GRAY)
            continue

        # Star ratings
        star_match = re.match(r'^(\w[\w\s.()]+?)\s{2,}', stripped)

        # Verdict lines
        if stripped.startswith("Top Pick") or stripped.startswith("Runner") or stripped.startswith("Watch") or stripped.startswith("Avoid"):
            parts = stripped.split("--") if "--" in stripped else stripped.split(":")
            label = parts[0].strip() if parts else stripped
            reason = parts[1].strip() if len(parts) > 1 else ""
            color = ACCENT_GREEN if "Top" in label else ACCENT_RED if "Avoid" in label else ACCENT_BLUE
            pdf.verdict_line(label, "", reason, color)
            continue

        # Risk/warning lines
        if stripped.startswith("!") or stripped.startswith("-") and len(stripped) > 2:
            clean = stripped.lstrip("!- ").strip()
            if clean:
                pdf.set_font(pdf.kr_font, "", 9)
                pdf.set_x(16)
                bullet = "  -  " if stripped.startswith("-") else "  !  "
                pdf.cell(180, 6, f"{bullet}{clean}", align="L")
                pdf.ln(6.5)
            continue

        # Screening criteria
        if stripped.startswith("[") and "]" in stripped:
            pdf.set_font(pdf.kr_font, "", 9)
            pdf.set_x(16)
            pdf.cell(180, 6, stripped, align="L")
            pdf.ln(6.5)
            continue

        # Key-value lines
        kv_match = re.match(r'^([\w\s/()]+?):\s+(.+)', stripped)
        if kv_match and len(kv_match.group(1)) < 30:
            pdf.kv_line(kv_match.group(1), kv_match.group(2))
            continue

        # Investment View / Conviction / Thesis lines
        if any(stripped.startswith(k) for k in ["Investment View", "Conviction Level", "One-Line Thesis", "Fwd P/E"]):
            parts = stripped.split(":", 1)
            if len(parts) == 2:
                pdf.kv_line(parts[0].strip(), parts[1].strip())
            else:
                pdf.set_font(pdf.kr_font, "", 9)
                pdf.set_x(14)
                pdf.cell(182, 6, stripped, align="L")
                pdf.ln(6.5)
            continue

        # Disclaimer / note lines
        if stripped.startswith("※"):
            pdf.set_font(pdf.kr_font, "", 7.5)
            pdf.set_text_color(*MID_GRAY)
            pdf.set_x(14)
            pdf.cell(182, 5.5, stripped, align="L")
            pdf.ln(6)
            pdf.set_text_color(*DARK_GRAY)
            continue

        # Generic text
        if stripped and not re.match(r'^[━─┌┐└┘├┤┬┴┼]+$', stripped):
            pdf.set_font(pdf.kr_font, "", 9)
            pdf.set_x(14)
            # Truncate very long lines
            if len(stripped) > 90:
                pdf.multi_cell(182, 6, stripped, align="L")
            else:
                pdf.cell(182, 6, stripped, align="L")
            pdf.ln(6.5)

    # Ensure output directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    pdf.output(output_path)
    print(f"PDF saved: {output_path}")
    return output_path


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(f"Usage: {sys.argv[0]} <markdown_file> <output_pdf_path>")
        sys.exit(1)

    md_file = sys.argv[1]
    pdf_path = sys.argv[2]

    if not os.path.exists(md_file):
        print(f"Error: {md_file} not found")
        sys.exit(1)

    build_pdf_from_markdown(md_file, pdf_path)
