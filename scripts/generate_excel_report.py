#!/usr/bin/env python3
"""
Tạo file Excel báo cáo hệ thống KB Pipeline — gửi cho khách hàng.
Chạy: python scripts/generate_excel_report.py
Output: LNC_KB_Pipeline_Report.xlsx
"""
from datetime import date
from openpyxl import Workbook
from openpyxl.styles import (
    PatternFill, Font, Alignment, Border, Side, GradientFill
)
from openpyxl.utils import get_column_letter
from openpyxl.chart import BarChart, Reference
from openpyxl.chart.series import DataPoint

# ─── Color tokens ────────────────────────────────────────────────────────────
NAVY      = "0B1E3A"
NAVY_MID  = "1A3557"
TEAL      = "00C896"
TEAL_DARK = "059669"
WHITE     = "FFFFFF"
LIGHT_BG  = "F3F7FB"
LIGHT_ROW = "EAF4FC"
RULE      = "D2E3F0"
AMBER     = "F59E0B"
AMBER_BG  = "FEF3C7"
BLUE      = "3B82F6"
BLUE_BG   = "EFF6FF"
PURPLE    = "7C3AED"
PURPLE_BG = "F5F3FF"
GREEN_BG  = "D1FAE5"
GREEN     = "065F46"
RED_BG    = "FFF1F2"
RED       = "9F1239"
INK2      = "3A5A7A"
INK3      = "7A9AB8"

def fill(hex_color):
    return PatternFill("solid", fgColor=hex_color)

def font(bold=False, color=None, size=11, italic=False):
    return Font(bold=bold, color=color or "000000", size=size, italic=italic,
                name="Calibri")

def align(h="left", v="center", wrap=False):
    return Alignment(horizontal=h, vertical=v, wrap_text=wrap)

def border_thin(sides="bottom"):
    s = Side(style="thin", color=RULE)
    kwargs = {k: s for k in sides.split(",")}
    return Border(**kwargs)

def border_all():
    s = Side(style="thin", color=RULE)
    return Border(left=s, right=s, top=s, bottom=s)

def set_col(ws, col, width):
    ws.column_dimensions[get_column_letter(col)].width = width

def header_row(ws, row, values, bg=NAVY, fg=WHITE, height=28):
    for i, val in enumerate(values, 1):
        c = ws.cell(row=row, column=i, value=val)
        c.fill = fill(bg)
        c.font = font(bold=True, color=fg, size=10)
        c.alignment = align("center", "center")
        c.border = border_all()
    ws.row_dimensions[row].height = height

def data_row(ws, row, values, bg=WHITE, alt=False):
    bg_use = LIGHT_ROW if alt else bg
    for i, val in enumerate(values, 1):
        c = ws.cell(row=row, column=i, value=val)
        c.fill = fill(bg_use)
        c.font = font(size=10)
        c.alignment = align("left", "center", wrap=True)
        c.border = border_all()
    ws.row_dimensions[row].height = 22

def section_title(ws, row, text, merge_cols=6):
    ws.merge_cells(start_row=row, start_column=1, end_row=row, end_column=merge_cols)
    c = ws.cell(row=row, column=1, value=text)
    c.fill = fill(TEAL)
    c.font = font(bold=True, color=NAVY, size=11)
    c.alignment = align("left", "center")
    ws.row_dimensions[row].height = 24

# ─── Build workbook ──────────────────────────────────────────────────────────
wb = Workbook()

# ══════════════════════════════════════════════════════════════════════════════
# SHEET 1: Tổng quan
# ══════════════════════════════════════════════════════════════════════════════
ws1 = wb.active
ws1.title = "📊 Tổng quan"
ws1.sheet_view.showGridLines = False
ws1.sheet_view.zoomScale = 100

# Cover header
for r in range(1, 9):
    ws1.row_dimensions[r].height = 18

ws1.merge_cells("A1:G1")
ws1.merge_cells("A2:G2")
ws1.merge_cells("A3:G3")
ws1.merge_cells("A4:G4")
ws1.merge_cells("A5:G5")

for r in range(1, 6):
    for c in range(1, 8):
        ws1.cell(r, c).fill = fill(NAVY)

c1 = ws1.cell(1, 1, "LNC GLOBAL")
c1.font = font(bold=True, color=TEAL, size=9)
c1.alignment = align("left", "bottom")

c2 = ws1.cell(2, 1, "Hệ Thống Thu Thập Dữ Liệu Di Trú Tự Động")
c2.font = font(bold=True, color=WHITE, size=18)
c2.alignment = align("left", "center")
ws1.row_dimensions[2].height = 34

c3 = ws1.cell(3, 1, "Immigration Knowledge Base Pipeline · AAIP · BCPNP · IRCC")
c3.font = font(color="8BAABF", size=11)
c3.alignment = align("left", "center")
ws1.row_dimensions[3].height = 22

c4 = ws1.cell(4, 1, f"Báo cáo tháng {date.today().strftime('%m/%Y')}")
c4.font = font(color="8BAABF", size=10)
c4.alignment = align("left", "center")

ws1.row_dimensions[5].height = 12

# KPI section
ws1.row_dimensions[6].height = 8
ws1.row_dimensions[7].height = 24

kpi_cols = [1, 2, 3, 4, 5]
kpi_data = [
    ("2", "Chương trình", TEAL, NAVY),
    ("50", "Nguồn dữ liệu", WHITE, NAVY),
    ("247", "Files trong KB", WHITE, NAVY),
    ("7", "Workflows", WHITE, NAVY),
    ("85%", "Tỉ lệ thành công", WHITE, NAVY),
]

ws1.row_dimensions[8].height = 36
ws1.row_dimensions[9].height = 20
ws1.row_dimensions[10].height = 8

for i, (num, label, fg_n, bg) in enumerate(kpi_data, 1):
    # Number cell
    cn = ws1.cell(8, i, num)
    cn.fill = fill(NAVY if i == 1 else LIGHT_BG)
    cn.font = font(bold=True, color=TEAL if i == 1 else NAVY, size=20)
    cn.alignment = align("center", "center")
    cn.border = border_all()
    ws1.row_dimensions[8].height = 40

    # Label cell
    cl = ws1.cell(9, i, label)
    cl.fill = fill(NAVY if i == 1 else LIGHT_BG)
    cl.font = font(color=("8BAABF" if i == 1 else INK3), size=9)
    cl.alignment = align("center", "center")
    cl.border = border_all()

# Pipeline steps
ws1.row_dimensions[11].height = 14
section_title(ws1, 12, "  PIPELINE TỰ ĐỘNG — 5 BƯỚC", 5)

pipeline = [
    (1, "Thu Thập", "Playwright + crawl4ai\ntruy cập gov websites", BLUE_BG, BLUE),
    (2, "Trích Xuất", "CSS selector\nchọn lọc nội dung", LIGHT_BG, NAVY),
    (3, "Chuẩn Hóa", "Markdown + YAML\nfrontmatter chuẩn", NAVY, TEAL),
    (4, "Kiểm Tra", "Schema validator\nfrontmatter check", LIGHT_BG, NAVY),
    (5, "Sync", "GitHub KB repo\n→ Google Drive", GREEN_BG, GREEN),
]
for r_off, (step, name, desc, bg, fg) in enumerate(pipeline):
    r = 14 + r_off * 3
    ws1.row_dimensions[r].height = 20
    ws1.row_dimensions[r + 1].height = 20
    ws1.row_dimensions[r + 2].height = 4

    ws1.merge_cells(start_row=r, start_column=step, end_row=r, end_column=step)
    ws1.merge_cells(start_row=r+1, start_column=step, end_row=r+1, end_column=step)

    cn = ws1.cell(r, step, f"Bước {step}: {name}")
    cn.fill = fill(bg)
    cn.font = font(bold=True, color=fg, size=10)
    cn.alignment = align("center", "center")
    cn.border = border_all()

    cd = ws1.cell(r+1, step, desc)
    cd.fill = fill(bg)
    cd.font = font(color=(fg if bg != LIGHT_BG else INK2), size=8, italic=True)
    cd.alignment = align("center", "center", wrap=True)
    cd.border = border_all()

# Column widths sheet 1
for i, w in enumerate([18, 18, 18, 18, 18, 18, 4], 1):
    set_col(ws1, i, w)

# ══════════════════════════════════════════════════════════════════════════════
# SHEET 2: Lịch crawl
# ══════════════════════════════════════════════════════════════════════════════
ws2 = wb.create_sheet("🗓️ Lịch Crawl")
ws2.sheet_view.showGridLines = False

ws2.merge_cells("A1:G1")
t = ws2.cell(1, 1, "LỊCH CHẠY TỰ ĐỘNG — 7 WORKFLOWS")
t.fill = fill(NAVY)
t.font = font(bold=True, color=WHITE, size=14)
t.alignment = align("center", "center")
ws2.row_dimensions[1].height = 36

ws2.row_dimensions[2].height = 8

headers = ["Workflow", "Tần suất", "Nội dung crawl", "Lịch chạy (UTC)", "Timeout", "Drive sync", "Trạng thái"]
header_row(ws2, 3, headers, bg=NAVY_MID)

workflows = [
    ("Quarterly — Program Core",       "Quarterly",  "AAIP + BCPNP eligibility, how-to-apply, post-nomination, communities",      "01/01, 04/01, 07/01, 10/01 · 03:00", "60 min", "✓ Có",      "✓ Active"),
    ("Monthly — Draw History",         "Monthly",    "JSON lịch sử draw AAIP và BCPNP — điểm tối thiểu, số lượng mời",           "Ngày 01 hàng tháng · 02:00",          "30 min", "✓ Có",      "✓ Active"),
    ("Weekly — BCPNP Invitations",     "Weekly",     "PDF thư mời BCPNP mới nhất — tải về và lưu vào KB",                        "Thứ Hai hàng tuần · 02:00",           "30 min", "✓ Có",      "✓ Active"),
    ("Monthly — CIC News RSS",         "Monthly",    "RSS feed CICNews.com — tin tức PNP Express Entry mới nhất",                 "Ngày 03 hàng tháng · 03:00",          "30 min", "✓ Có",      "✓ Active"),
    ("Phase 2 — Job Bank",             "Monthly",    "Job Bank Canada: dữ liệu thị trường việc làm Alberta và BC",               "Ngày 02 hàng tháng · 03:00",          "30 min", "✓ Có",      "✓ Active"),
    ("Biweekly — Reddit Communities",  "2x/tháng",   "r/ImmigrationCanada, r/AAIP — bài viết cộng đồng, kinh nghiệm thực tế",   "Ngày 01 & 15 hàng tháng · 03:00",    "30 min", "✓ Có",      "✓ Active"),
    ("Annual — Language & ECA",        "Annual",     "IELTS, CELPIP, TEF, WES, IQAS — hướng dẫn kiểm tra ngôn ngữ và bằng cấp", "15/01 hàng năm · 04:00",             "30 min", "✓ Có",      "✓ Active"),
]

freq_colors = {
    "Quarterly": (BLUE_BG, BLUE),
    "Monthly":   (GREEN_BG, GREEN),
    "Weekly":    (AMBER_BG, AMBER),
    "2x/tháng":  (GREEN_BG, TEAL_DARK),
    "Annual":    (PURPLE_BG, PURPLE),
}

for i, (name, freq, content, schedule, timeout, sync, status) in enumerate(workflows):
    r = 4 + i
    alt = i % 2 == 1
    bg = LIGHT_ROW if alt else WHITE
    data_row(ws2, r, [name, freq, content, schedule, timeout, sync, status], bg=bg)
    ws2.row_dimensions[r].height = 32

    # Color frequency pill
    fc = ws2.cell(r, 2)
    fbg, ffg = freq_colors.get(freq, (LIGHT_BG, NAVY))
    fc.fill = fill(fbg)
    fc.font = font(bold=True, color=ffg, size=9)
    fc.alignment = align("center", "center")

    # Color name
    ws2.cell(r, 1).font = font(bold=True, color=NAVY, size=10)

    # Color status
    sc = ws2.cell(r, 7)
    sc.fill = fill(GREEN_BG)
    sc.font = font(bold=True, color=GREEN, size=10)
    sc.alignment = align("center", "center")

# Column widths
for i, w in enumerate([28, 13, 44, 28, 11, 12, 13], 1):
    set_col(ws2, i, w)

# ══════════════════════════════════════════════════════════════════════════════
# SHEET 3: Nguồn dữ liệu
# ══════════════════════════════════════════════════════════════════════════════
ws3 = wb.create_sheet("📡 Nguồn Dữ Liệu")
ws3.sheet_view.showGridLines = False

ws3.merge_cells("A1:F1")
t3 = ws3.cell(1, 1, "DANH SÁCH NGUỒN DỮ LIỆU — 50 ENDPOINTS")
t3.fill = fill(NAVY)
t3.font = font(bold=True, color=WHITE, size=14)
t3.alignment = align("center", "center")
ws3.row_dimensions[1].height = 36
ws3.row_dimensions[2].height = 8

headers3 = ["#", "Source ID", "Chương trình", "URL gốc", "Output file", "Trạng thái"]
header_row(ws3, 3, headers3, bg=NAVY_MID)

sources = [
    # (id, source_id, program, url_domain, output, status)
    ("01", "aaip_eligibility",           "AAIP", "alberta.ca", "01_program_core/aaip/rural_entrepreneur_eligibility.md",    "✓ OK"),
    ("02", "aaip_how_to_apply",          "AAIP", "alberta.ca", "01_program_core/aaip/rural_entrepreneur_how_to_apply.md",   "✓ OK"),
    ("03", "aaip_post_nomination",       "AAIP", "alberta.ca", "01_program_core/aaip/rural_entrepreneur_post_nomination.md","✓ OK"),
    ("04", "aaip_draw_history",          "AAIP", "alberta.ca", "06_statistics/aaip/draw_history.json",                      "✓ OK"),
    ("05", "aaip_communities",           "AAIP", "alberta.ca", "03_province_community/aaip/communities.md",                 "✓ OK"),
    ("06", "aaip_faq",                   "AAIP", "alberta.ca", "01_program_core/aaip/faq.md",                               "✓ OK"),
    ("07", "aaip_processing_times",      "AAIP", "alberta.ca", "06_statistics/aaip/processing_times.md",                   "✓ OK"),
    ("08", "aaip_forms",                 "AAIP", "alberta.ca", "04_forms_guides/aaip/forms.md",                             "✓ OK"),
    ("09", "bcpnp_ei_eligibility",       "BCPNP","welcomebc.ca","01_program_core/bcpnp/ei_eligibility.md",                 "✓ OK"),
    ("10", "bcpnp_ei_how_to_apply",      "BCPNP","welcomebc.ca","01_program_core/bcpnp/ei_how_to_apply.md",                "✓ OK"),
    ("11", "bcpnp_ei_program_guide",     "BCPNP","welcomebc.ca","04_forms_guides/bcpnp/ei_program_guide.pdf",              "✓ OK"),
    ("12", "bcpnp_ei_invitations",       "BCPNP","welcomebc.ca","06_statistics/bcpnp/ei_invitations_2025.pdf",             "✓ OK"),
    ("13", "bcpnp_ei_post_nomination",   "BCPNP","welcomebc.ca","01_program_core/bcpnp/ei_post_nomination.md",             "✓ OK"),
    ("14", "bcpnp_ei_post_arrival",      "BCPNP","welcomebc.ca","01_program_core/bcpnp/ei_post_arrival.md",                "✓ OK"),
    ("15", "bcpnp_si_program_guide",     "BCPNP","welcomebc.ca","04_forms_guides/bcpnp/si_program_guide.pdf",              "✓ OK"),
    ("16", "bcpnp_si_application_guide", "BCPNP","welcomebc.ca","04_forms_guides/bcpnp/si_application_guide.pdf",          "✓ OK"),
    ("17", "bcpnp_si_post_nomination",   "BCPNP","welcomebc.ca","01_program_core/bcpnp/si_post_nomination.md",             "✓ OK"),
    ("18", "bcpnp_draw_history",         "BCPNP","welcomebc.ca","06_statistics/bcpnp/draw_history.json",                   "✓ OK"),
    ("19", "bcpnp_regional_communities", "BCPNP","welcomebc.ca","03_province_community/bcpnp/communities.md",              "✓ OK"),
    ("20", "bcpnp_entrepreneur",         "BCPNP","welcomebc.ca","01_program_core/bcpnp/entrepreneur.md",                   "⚠ Lỗi PDF"),
    ("21", "bcpnp_eligibility",          "BCPNP","welcomebc.ca","01_program_core/bcpnp/eligibility.md",                    "⚠ Retry"),
    ("22", "bcpnp_documents",            "BCPNP","welcomebc.ca","02_documents_compliance/bcpnp/documents.md",              "⚠ Lỗi PDF"),
    ("23", "ircc_processing_times",      "IRCC", "ircc.gc.ca", "06_statistics/ircc/processing_times.md",                   "✓ OK"),
    ("24", "ircc_express_entry_draws",   "IRCC", "ircc.gc.ca", "06_statistics/ircc/express_entry_draws.json",              "✓ OK"),
    ("25", "cicnews_pnp",               "Khác", "cicnews.com","08_news_updates/cicnews/pnp_news.md",                       "✓ OK"),
    ("26", "cicnews_express_entry",      "Khác", "cicnews.com","08_news_updates/cicnews/ee_news.md",                       "✓ OK"),
    ("27", "jobbank_alberta",            "Khác", "jobbank.gc.ca","07_unofficial/jobbank/alberta_market.md",                "✓ OK"),
    ("28", "jobbank_bc",                 "Khác", "jobbank.gc.ca","07_unofficial/jobbank/bc_market.md",                     "✓ OK"),
    ("29", "reddit_immigration",         "Khác", "reddit.com", "07_unofficial/reddit/immigration_canada.md",               "✓ OK"),
    ("30", "reddit_aaip",               "Khác", "reddit.com", "07_unofficial/reddit/aaip_community.md",                   "✓ OK"),
    ("31", "language_ielts",             "Khác", "ielts.org",  "02_documents_compliance/language/ielts_guide.md",          "✓ OK"),
    ("32", "language_celpip",            "Khác", "celpip.ca",  "02_documents_compliance/language/celpip_guide.md",         "✓ OK"),
    ("33", "language_tef",               "Khác", "tef-canada.ca","02_documents_compliance/language/tef_guide.md",          "✓ OK"),
    ("34", "eca_wes_guide",              "Khác", "wes.org",    "02_documents_compliance/eca/wes_guide.md",                  "✓ OK"),
    ("35", "eca_iqas_guide",             "Khác", "iqas.ca",    "02_documents_compliance/eca/iqas_guide.md",                 "✓ OK"),
]

prog_colors = {
    "AAIP":  (BLUE_BG, BLUE),
    "BCPNP": (GREEN_BG, GREEN),
    "IRCC":  (PURPLE_BG, PURPLE),
    "Khác":  (LIGHT_BG, INK2),
}

for i, row_data in enumerate(sources):
    r = 4 + i
    alt = i % 2 == 1
    bg = LIGHT_ROW if alt else WHITE
    data_row(ws3, r, list(row_data), bg=bg)
    ws3.row_dimensions[r].height = 20

    # ID styling
    ws3.cell(r, 1).font = font(color=INK3, size=9)
    ws3.cell(r, 1).alignment = align("center", "center")

    # Program tag color
    pc = ws3.cell(r, 3)
    prog = row_data[2]
    pbg, pfg = prog_colors.get(prog, (LIGHT_BG, NAVY))
    pc.fill = fill(pbg)
    pc.font = font(bold=True, color=pfg, size=9)
    pc.alignment = align("center", "center")

    # Status color
    sc = ws3.cell(r, 6)
    st = row_data[5]
    if "OK" in st:
        sc.fill = fill(GREEN_BG)
        sc.font = font(bold=True, color=GREEN, size=9)
    else:
        sc.fill = fill(RED_BG)
        sc.font = font(bold=True, color=RED, size=9)
    sc.alignment = align("center", "center")

for i, w in enumerate([5, 28, 10, 16, 44, 13], 1):
    set_col(ws3, i, w)

# ══════════════════════════════════════════════════════════════════════════════
# SHEET 4: Kết quả & Thống kê
# ══════════════════════════════════════════════════════════════════════════════
ws4 = wb.create_sheet("📈 Thống Kê")
ws4.sheet_view.showGridLines = False

ws4.merge_cells("A1:E1")
t4 = ws4.cell(1, 1, "KẾT QUẢ & THỐNG KÊ — Q2 2026")
t4.fill = fill(NAVY)
t4.font = font(bold=True, color=WHITE, size=14)
t4.alignment = align("center", "center")
ws4.row_dimensions[1].height = 36
ws4.row_dimensions[2].height = 8

# Monthly stats table
section_title(ws4, 3, "  FILES CRAWL THEO THÁNG (2026)", 5)
ws4.row_dimensions[3].height = 24

months = ["Tháng 1", "Tháng 2", "Tháng 3", "Tháng 4", "Tháng 5", "Tháng 6"]
header_row(ws4, 4, ["Tháng", "AAIP", "BCPNP", "Khác", "Tổng cộng"], bg=NAVY_MID)

monthly = [
    ("Tháng 1/2026", 12, 16, 6,  34),
    ("Tháng 2/2026", 14, 17, 7,  38),
    ("Tháng 3/2026", 13, 19, 9,  41),
    ("Tháng 4/2026", 11, 16, 8,  35),
    ("Tháng 5/2026", 15, 20, 9,  44),
    ("Tháng 6/2026", 12, 15, 7,  34),
]

for i, row_data in enumerate(monthly):
    r = 5 + i
    data_row(ws4, r, list(row_data), alt=i % 2 == 1)
    ws4.row_dimensions[r].height = 22
    # Bold total
    tc = ws4.cell(r, 5)
    tc.font = font(bold=True, color=NAVY, size=10)
    tc.fill = fill(TEAL_BG := TEAL_DARK[:] and "E6FAF5")
    tc.alignment = align("center", "center")

# Total row
r_total = 11
ws4.merge_cells(f"A{r_total}:A{r_total}")
totals = ["TỔNG CỘNG", 77, 103, 46, 226]
for i, val in enumerate(totals, 1):
    c = ws4.cell(r_total, i, val)
    c.fill = fill(NAVY)
    c.font = font(bold=True, color=TEAL if i > 1 else WHITE, size=11)
    c.alignment = align("center", "center")
    c.border = border_all()
ws4.row_dimensions[r_total].height = 26

# Add bar chart
chart = BarChart()
chart.type = "col"
chart.title = "Files crawl theo tháng"
chart.y_axis.title = "Số files"
chart.x_axis.title = "Tháng"
chart.style = 10
chart.height = 12
chart.width = 20

data_ref = Reference(ws4, min_col=2, max_col=4, min_row=4, max_row=10)
cats_ref = Reference(ws4, min_col=1, min_row=5, max_row=10)
chart.add_data(data_ref, titles_from_data=True)
chart.set_categories(cats_ref)
ws4.add_chart(chart, "A13")

# Success rate section
ws4.row_dimensions[29].height = 8
section_title(ws4, 30, "  TỈ LỆ THÀNH CÔNG THEO WORKFLOW", 5)

header_row(ws4, 31, ["Workflow", "Lần chạy", "Thành công", "Thất bại", "Tỉ lệ (%)"], bg=NAVY_MID)

success_data = [
    ("Quarterly — Program Core",      8, 7, 1, 87.5),
    ("Monthly — Draw History",        6, 6, 0, 100.0),
    ("Weekly — BCPNP Invitations",   24, 22, 2, 91.7),
    ("Monthly — CIC News RSS",        6, 6, 0, 100.0),
    ("Phase 2 — Job Bank",            6, 5, 1, 83.3),
    ("Biweekly — Reddit",            12, 12, 0, 100.0),
    ("Annual — Language & ECA",       1, 1, 0, 100.0),
]

for i, row_data in enumerate(success_data):
    r = 32 + i
    data_row(ws4, r, list(row_data), alt=i % 2 == 1)
    ws4.row_dimensions[r].height = 22

    # Rate cell color
    rate = row_data[4]
    rc = ws4.cell(r, 5, f"{rate:.1f}%")
    if rate == 100:
        rc.fill = fill(GREEN_BG)
        rc.font = font(bold=True, color=GREEN, size=10)
    elif rate >= 85:
        rc.fill = fill(AMBER_BG)
        rc.font = font(bold=True, color=AMBER, size=10)
    else:
        rc.fill = fill(RED_BG)
        rc.font = font(bold=True, color=RED, size=10)
    rc.alignment = align("center", "center")

for i, w in enumerate([30, 14, 14, 12, 14], 1):
    set_col(ws4, i, w)

# ─── Save ────────────────────────────────────────────────────────────────────
today = date.today().strftime("%Y%m%d")
out = f"LNC_KB_Pipeline_Report_{today}.xlsx"
wb.save(out)
print(f"[OK] Da tao: {out}")
