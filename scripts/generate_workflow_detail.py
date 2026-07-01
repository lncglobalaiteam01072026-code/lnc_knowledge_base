#!/usr/bin/env python3
"""
Tao sheet Excel giai thich chi tiet 11 workflows — ngon ngu don gian cho khach hang.
Chay: python scripts/generate_workflow_detail.py
"""
from datetime import date
from openpyxl import Workbook
from openpyxl.styles import PatternFill, Font, Alignment, Border, Side
from openpyxl.utils import get_column_letter

# ── Color palette ─────────────────────────────────────────────────────────────
NAVY     = "0B1E3A"
NAVY_MID = "1A3557"
TEAL     = "00C896"
TEAL_BG  = "E6FAF5"
WHITE    = "FFFFFF"
RULE     = "D2E3F0"
AMBER    = "B45309"
AMBER_BG = "FEF3C7"
BLUE_BG  = "EFF6FF"
GREEN    = "065F46"
GREEN_BG = "D1FAE5"
PURPLE   = "5B21B6"
PURPLE_BG= "EDE9FE"
GRAY     = "6B7280"
ROSE     = "9F1239"
ROSE_BG  = "FFF1F2"
SLATE    = "374151"
SLATE_BG = "F1F5F9"
ORANGE   = "C2410C"
ORANGE_BG= "FFF7ED"

def fill(c): return PatternFill("solid", fgColor=c)
def f(bold=False, color="000000", size=10, italic=False):
    return Font(bold=bold, color=color, size=size, italic=italic, name="Calibri")
def a(h="left", v="center", wrap=False):
    return Alignment(horizontal=h, vertical=v, wrap_text=wrap)
def allborder():
    s = Side(style="thin", color=RULE)
    return Border(left=s, right=s, top=s, bottom=s)
def sides(*names):
    s = Side(style="thin", color=RULE)
    return Border(**{n: s for n in names})

# ── Render one workflow section, returns next row ─────────────────────────────
def render_wf(ws, row, wf, headers):
    # Header bar
    ws.merge_cells(f"A{row}:F{row}")
    hd = ws.cell(row, 1, f"  {wf['name']}")
    hd.fill = fill(wf["bg_head"])
    hd.font = f(bold=True, color=WHITE, size=12)
    hd.alignment = a("left", "center")
    ws.row_dimensions[row].height = 32
    row += 1

    # Info rows
    for txt, fg, bg in [
        (f"  Tan suat: {wf['freq']}", TEAL, wf["bg_light"]),
        (f"  Lich kich hoat: {wf['trigger']}", GRAY, wf["bg_light"]),
        (f"  Pham vi: {wf['scope']}", "374151", wf["bg_light"]),
    ]:
        ws.merge_cells(f"A{row}:F{row}")
        c = ws.cell(row, 1, txt)
        c.fill = fill(bg)
        c.font = f(color=fg, size=9, italic=True)
        c.alignment = a("left", "center", wrap=True)
        c.border = sides("bottom")
        ws.row_dimensions[row].height = 24
        row += 1

    # Column header row
    for col_i, hdr in enumerate(headers, 1):
        c = ws.cell(row, col_i, hdr)
        c.fill = fill(NAVY_MID)
        c.font = f(bold=True, color=WHITE, size=9)
        c.alignment = a("center", "center")
        c.border = allborder()
    ws.row_dimensions[row].height = 22
    row += 1

    # Step rows
    for s_i, (step_no, action, detail, example, output, note) in enumerate(wf["steps"]):
        row_bg = wf["bg_light"] if s_i % 2 == 0 else WHITE
        vals  = [step_no, action, detail, example, output, note]
        fgs   = [WHITE,   NAVY,   "1F2937", "4B5563", GREEN, AMBER]
        bolds = [True,    True,   False,    False,    True,  False]
        for col_i, (val, fg, bd) in enumerate(zip(vals, fgs, bolds), 1):
            c = ws.cell(row, col_i, val)
            c.fill = fill(row_bg)
            c.font = f(bold=bd, color=fg, size=9)
            c.alignment = a("center" if col_i == 1 else "left", "top", wrap=True)
            c.border = allborder()
        ws.cell(row, 1).fill = fill(wf["bg_head"])   # step pill colour
        ws.cell(row, 5).fill = fill(GREEN_BG)
        ws.cell(row, 5).font = f(color=GREEN, size=9, bold=True)
        ws.cell(row, 4).font = f(color="6B7280", size=9, italic=True)
        ws.row_dimensions[row].height = 46
        row += 1

    ws.row_dimensions[row].height = 10
    return row + 1

# ── Workbook setup ────────────────────────────────────────────────────────────
wb = Workbook()
ws = wb.active
ws.title = "Chi Tiet Workflow"
ws.sheet_view.showGridLines = False

widths = [4, 20, 38, 32, 28, 20]
for i, w in enumerate(widths, 1):
    ws.column_dimensions[get_column_letter(i)].width = w

HEADERS = ["Buoc", "Hanh dong", "Dieu gi xay ra (de hieu)", "Vi du / Hinh anh minh hoa", "Ket qua nhan duoc", "Luu y"]

row = 1

# ── Page header ───────────────────────────────────────────────────────────────
ws.merge_cells(f"A{row}:F{row}")
c = ws.cell(row, 1, "HE THONG TU DONG CAP NHAT DU LIEU — 11 QUY TRINH")
c.fill = fill(NAVY); c.font = f(bold=True, color=WHITE, size=15)
c.alignment = a("center", "center"); ws.row_dimensions[row].height = 38
row += 1

ws.merge_cells(f"A{row}:F{row}")
c = ws.cell(row, 1,
    "LNC Global  ·  11 quy trinh tu dong chay tren GitHub "
    "— khong can nhan vien ngoi truc  ·  "
    "Du lieu luon moi, chinh xac, san sang cho AI chatbot 24/7")
c.fill = fill(NAVY_MID); c.font = f(color="8BAABF", size=10, italic=True)
c.alignment = a("center", "center"); ws.row_dimensions[row].height = 22
row += 1

ws.row_dimensions[row].height = 8; row += 1

ws.merge_cells(f"A{row}:F{row}")
c = ws.cell(row, 1,
    "  Moi quy trinh duoi day chay hoan toan tu dong theo lich dinh san "
    "— giong nhu mot nhan vien robot lam viec 24/7 khong nghi, "
    "doc trang web chinh phu, loc thong tin, kiem tra chat luong "
    "roi luu len Drive cho ca team dung.")
c.fill = fill(TEAL_BG); c.font = f(color="047857", size=10)
c.alignment = a("left", "center", wrap=True)
c.border = sides("left", "right", "top", "bottom")
ws.row_dimensions[row].height = 36; row += 1

ws.row_dimensions[row].height = 10; row += 1

# ══════════════════════════════════════════════════════════════════════════════
#  ALL 11 WORKFLOWS
# ══════════════════════════════════════════════════════════════════════════════
workflows = [

  # ── 1: Quarterly program core ───────────────────────────────────────────────
  {
    "name":    "QUY TRINH 1 — Cap nhat chinh sach (3 thang / lan)",
    "freq":    "Quarterly — moi quy: 01/01 · 01/04 · 01/07 · 01/10",
    "trigger": "Tu dong chay luc 10:00 sang gio Viet Nam vao dau moi quy — hoac khi team cap nhat phan mem — hoac bam nut chay thu cong",
    "scope":   "34 trang web chinh sach AAIP (Alberta) va BCPNP (BC): dieu kien du dieu kien, cach nop ho so, giay to can thiet...",
    "bg_light": BLUE_BG, "bg_head": NAVY,
    "steps": [
      ("1","He thong thuc day","Dung ngay gio da hen, he thong tu dong khoi dong — khong can ai ngoi bam nut hay nhac nho.","Giong nhu dat bao thuc: den gio la tu reo, tu lam viec.","Quy trinh bat dau chay","Hoan toan tu dong"),
      ("2","Tai phan mem ve may chu","May chu cua GitHub tu tai bo phan mem crawl moi nhat ve — dam bao luon dung phien ban cap nhat nhat.","Nhu mo laptop va dong bo OneDrive truoc khi bat dau lam viec.","Phan mem san sang tren may chu","Binh thuong ~30 giay"),
      ("3","Lay kho du lieu hien tai","Tai kho du lieu KB dang co ve de so sanh — chi cap nhat phan thay doi, giu nguyen phan cu con dung.","Giong mo file Excel cu len de dien them so lieu moi, khong xoa du lieu cu.","Kho du lieu hien tai san sang de cap nhat","Can mat khau (PAT) — neu het han se bao loi"),
      ("4","Cai cong cu can thiet","Cai dat trinh duyet tu dong (Chromium) va cac cong cu doc web, doc PDF. Buoc nay nhu chuan bi dung cu truoc khi lam viec.","Nhu cai ung dung truoc khi dung — chi mat vai phut, chi lam 1 lan moi lan chay.","Moi truong lam viec san sang","~2 phut"),
      ("5","Doc 34 trang web chinh phu","Phan mem tu mo tung trang web cua Chinh phu Canada, doc noi dung, tu dong loc bo menu — quang cao — footer. Chi giu lai thong tin chinh sach thuc su quan trong.","Nhu thue 1 nhan vien ngoi doc 34 trang web, ghi chep lai phan quan trong — nhung lam trong 15 phut thay vi ca ngay.","34 file van ban sach + lich su draw dang bang so lieu","Buoc chinh — mat ~15-20 phut"),
      ("6","Kiem tra chat luong tu dong","He thong tu kiem tra: file co du thong tin bat buoc khong? Noi dung co qua ngan khong? Bang bieu co bi loi dinh dang khong? Neu phat hien loi → dung ngay, khong luu du lieu sai vao he thong.","Nhu bo phan QC kiem tra san pham truoc khi xuat kho — hang loi bi giu lai, khong den tay khach hang.","Thong qua = tiep tuc / Co loi = dung va bao ngay","Cua kiem soat chat luong quan trong nhat"),
      ("7","Dong bo len Google Drive","Toan bo du lieu moi duoc tu dong copy len Google Drive — ca team co the truy cap ngay lap tuc, khong can gui file qua email.","Nhu luu file vao o dia chung — ai cung mo duoc, luc nao cung co ban moi nhat.","Drive cap nhat — ca team thay ngay","Neu Drive loi → bo qua, van tiep tuc luu GitHub"),
      ("8","Luu lich su thay doi","Ghi lai tat ca thay doi kem ngay gio vao kho luu tru GitHub — nhu so nhat ky, ai thay doi gi, luc may gio deu co the tra lai.","Nhu 'Save' nhung co the xem lai moi phien ban truoc — neu co loi co the quay ve ban cu.","Kho du lieu cap nhat tren GitHub","Chi luu khi co thay doi thuc su"),
    ]
  },

  # ── 2: Monthly draw history ─────────────────────────────────────────────────
  {
    "name":    "QUY TRINH 2 — Cap nhat lich su moi (hang thang)",
    "freq":    "Monthly — ngay 01 hang thang luc 09:00 sang gio VN",
    "trigger": "Tu dong ngay dau thang — hoac bam chay thu cong khi can",
    "scope":   "File PDF ket qua draw cua AAIP va BCPNP — lay so lieu: ngay moi, diem toi thieu, so nguoi duoc moi",
    "bg_light": "F0FDF4", "bg_head": "166534",
    "steps": [
      ("1","He thong thuc day","Dau thang, he thong tu khoi dong luc 09:00 sang — khong can ai nhac.","Nhu lich nhac viec tu dong gui email dau thang.","Quy trinh bat dau","Tu dong"),
      ("2","Chuan bi phan mem","Tai code va kho du lieu ve may chu, cai cong cu can thiet.","Buoc khoi dong tieu chuan truoc moi ca lam viec.","Moi truong san sang","~3 phut"),
      ("3","Tim va tai PDF ket qua draw","Phan mem truy cap trang web Alberta va BC, tim file PDF ket qua draw moi nhat, tu dong tai ve.","Nhu nhan vien vao website moi thang tim file PDF ket qua xo so va download ve.","File PDF draw moi nhat da tai ve","Buoc chinh ~5 phut"),
      ("4","Doc va trich xuat so lieu tu PDF","Phan mem doc noi dung PDF, tu nhan ra cac con so quan trong: ngay draw, ten luong, diem toi thieu, so nguoi duoc moi — roi sap xep thanh bang co cau truc.","Nhu OCR doc hoa don giay va chuyen thanh bang Excel — tu dong, khong can go tay.","Bang so lieu draw co cau truc ro rang","Du lieu quan trong cho chatbot tu van"),
      ("5","Luu len Drive va GitHub","Du lieu draw moi duoc luu len Google Drive va GitHub — ca team thay ngay, AI chatbot cung dung duoc ngay.","So lieu draw tuoi nhat luon san sang.","Draw history cap nhat tren Drive & GitHub","Chi luu khi co draw moi"),
    ]
  },

  # ── 3: Weekly BCPNP PDFs ────────────────────────────────────────────────────
  {
    "name":    "QUY TRINH 3 — Tai PDF thu moi BCPNP (hang tuan)",
    "freq":    "Weekly — Thu Hai hang tuan luc 09:00 sang gio VN",
    "trigger": "Tu dong moi Thu Hai — vi BCPNP thuong cong bo invitation letter vao cuoi tuan",
    "scope":   "PDF invitation letters tu trang welcomebc.ca — thu moi chinh thuc hang tuan cua BC",
    "bg_light": AMBER_BG, "bg_head": "92400E",
    "steps": [
      ("1","He thong thuc day moi Thu Hai","BCPNP thuong phat thu moi vao cuoi tuan — he thong tu kiem tra vao sang Thu Hai de lay file moi nhat.","Nhu nhan vien den van phong sang Thu Hai de lay thu moi ve.","Quy trinh bat dau","Moi tuan"),
      ("2","Chuan bi phan mem","Tai code, kho du lieu, cai cong cu — cac buoc chuan bi tieu chuan.","Buoc khoi dong truoc moi ca lam.","Moi truong san sang","~3 phut"),
      ("3","Vao website BCPNP tim PDF moi","Phan mem mo trang welcomebc.ca, tim danh sach PDF invitation letters moi nhat, xac dinh file nao chua co trong kho.","Nhu nhan vien vao trang web, nhin danh sach file, kiem tra cai nao moi so voi tuan truoc.","Danh sach PDF moi can tai","Buoc chinh ~5 phut"),
      ("4","Tai PDF va doc so lieu","Tai ve tung file PDF moi. Sau do doc noi dung, trich xuat: ngay moi, luong, diem, so nguoi — luu song song ca PDF goc lan bang so lieu.","Luu ca anh chup man hinh goc (PDF) lan bang so lieu da xu ly — co the kiem chung bat ky luc nao.","PDF goc + bang so lieu trong kho","Co the doi chieu voi ban goc"),
      ("5","Luu len Drive va GitHub","File PDF moi va so lieu duoc luu len Drive va GitHub — AI chatbot cap nhat thong tin draw BCPNP moi tuan.","Thong tin draw BCPNP luon tuoi, cham nhat 1 tuan.","PDF + data tuan moi tren Drive","Tu dong"),
    ]
  },

  # ── 4: Monthly CIC News ─────────────────────────────────────────────────────
  {
    "name":    "QUY TRINH 4 — Thu thap tin tuc di tru (hang thang)",
    "freq":    "Monthly — ngay 03 hang thang luc 10:00 sang gio VN",
    "trigger": "Tu dong ngay 3 hang thang — hoac bam thu cong",
    "scope":   "Tin tuc PNP va Express Entry tu CICNews — trang tin tuc di tru uy tin Canada",
    "bg_light": "F0FDF4", "bg_head": "166534",
    "steps": [
      ("1","He thong thuc day","Ngay 3 hang thang, he thong tu thu thap tin tuc moi nhat ve di tru Canada.","Nhu dat mua bao: dung ngay tu giao den cua.","Quy trinh bat dau","Tu dong"),
      ("2","Chuan bi phan mem","Cai cong cu can thiet — lan nay khong can mo trinh duyet vi chi doc RSS feed (nhe hon cac quy trinh khac).","RSS feed nhu mot luong tin tuc duoc dong goi san — khong can mo browser, tai rat nhanh.","Moi truong san sang","~1 phut (nhanh hon)"),
      ("3","Doc luong tin tuc RSS","He thong goi thang vao luong du lieu cua CICNews, lay 20 bai viet moi nhat ve PNP — tieu de, tom tat, ngay dang, duong link goc.","Nhu doc tom tat 20 to bao cung luc trong 30 giay — khong can mo tung trang.","Danh sach 20 bai tin tuc moi nhat","Khong can mo browser → rat nhanh"),
      ("4","Sap xep va luu van ban","Tin tuc duoc dinh dang sach, them thong tin nguon, ngay thang — luu thanh file van ban san sang cho AI doc va tra loi khach hang.","Nhu bien tap vien sap xep tin tuc, ghi ro nguon va ngay de de tra cuu ve sau.","File tin tuc sach, co nguon goc ro rang","San sang cho AI chatbot"),
      ("5","Luu len Drive va GitHub","Tin tuc moi luu len Drive va GitHub — AI chatbot biet duoc cac thay doi chinh sach moi nhat de tu van khach hang chinh xac hon.","Chatbot duoc 'doc bao' hang thang — luon cap nhat.","Tin tuc thang moi tren Drive","Tu dong"),
    ]
  },

  # ── 5: Monthly Job Bank ─────────────────────────────────────────────────────
  {
    "name":    "QUY TRINH 5 — Thong tin thi truong viec lam (hang thang)",
    "freq":    "Monthly — ngay 02 hang thang luc 10:00 sang gio VN",
    "trigger": "Tu dong ngay 2 hang thang — hoac bam thu cong",
    "scope":   "Bao cao thi truong lao dong Alberta va BC tu Job Bank Canada — dung ho tro tu van nghe nghiep",
    "bg_light": "F0FDF4", "bg_head": "166534",
    "steps": [
      ("1","He thong thuc day","Ngay 2 hang thang, tu dong thu thap du lieu thi truong lao dong moi nhat.","Nhu bao cao thi truong lao dong tu cap nhat hang thang.","Quy trinh bat dau","Tu dong"),
      ("2","Chuan bi phan mem","Tai code, cai cong cu — lan nay can mo trinh duyet vi trang Job Bank dung JavaScript hien thi noi dung dong.","Mot so trang web can trinh duyet that moi hien thi dung — he thong dung Chromium an de lam dieu nay.","Moi truong san sang","~2 phut"),
      ("3","Truy cap trang Job Bank Canada","Phan mem mo trang Job Bank, vao muc bao cao thi truong lao dong Alberta va BC — doc bang so lieu ve nganh nghe dang thieu nhan luc, muc luong trung binh.","Nhu chuyen vien nghien cuu mo bao cao chinh phu moi thang va copy so lieu quan trong.","Noi dung bao cao lao dong da doc","~5 phut"),
      ("4","Luu du lieu lao dong","So lieu nganh nghe thieu nhan luc o Alberta va BC duoc luu thanh file van ban co cau truc — consultant dung de tu van nghe nghiep cho khach hang.","Thong tin nay giup tra loi: 'Nganh XYZ cua toi co duoc uu tien o Alberta khong?'","2 file bao cao lao dong Alberta + BC","Du lieu ho tro tu van"),
      ("5","Luu len Drive va GitHub","Du lieu lao dong moi len Drive va GitHub — chatbot va consultant deu co the tra cuu.","Thi truong lao dong cap nhat hang thang.","Bao cao viec lam moi tren Drive","Tu dong"),
    ]
  },

  # ── 6: Biweekly Reddit ──────────────────────────────────────────────────────
  {
    "name":    "QUY TRINH 6 — Y kien cong dong Reddit (2 lan/thang)",
    "freq":    "Biweekly — ngay 01 va 15 hang thang luc 10:00 sang gio VN",
    "trigger": "Tu dong 2 lan/thang — du lieu cong dong thay doi lien tuc nen can cap nhat thuong xuyen hon",
    "scope":   "Cac bai viet va cau hoi diem cao tren Reddit r/ImmigrationCanada — goc nhin thuc te tu nguoi da lam PR",
    "bg_light": TEAL_BG, "bg_head": "047857",
    "steps": [
      ("1","He thong thuc day 2 lan/thang","Ngay 1 va 15, he thong tu thu thap y kien moi tu cong dong di tru tren Reddit.","Nhu co nhan vien 2 tuan vao dien dan 1 lan de doc cau hoi pho bien nhat.","Quy trinh bat dau","2 lan/thang"),
      ("2","Chuan bi phan mem","Cai cong cu — lan nay khong can trinh duyet vi Reddit co API du lieu cong khai, tai rat nhanh.","Reddit cho phep doc du lieu truc tiep nhu doc RSS — khong can mo browser.","Moi truong san sang","~1 phut"),
      ("3","Loc bai viet diem cao","He thong doc 25 bai viet moi nhat, loc chi giu bai co lien quan den Alberta hoac BC, diem upvote > 10 — tuc la bai da duoc cong dong xac nhan huu ich.","Nhu chi doc cac cau hoi duoc nhieu nguoi binh chon 'huu ich' — tranh doc tin rac.","Danh sach bai viet chat luong ve Alberta/BC","Du lieu khong chinh thuc nhung sat thuc te"),
      ("4","Luu cau hoi va kinh nghiem thuc te","Cac cau hoi, kinh nghiem cua nguoi da duoc moi duoc luu lai — giup AI chatbot hieu cac moi lo va cau hoi thuong gap cua khach hang thuc su.","Khach hang hay hoi: 'Nguoi ta bao toi dang lam nghe X thi kho duoc moi?' — chatbot doc Reddit nen biet context nay.","File cau hoi cong dong trong kho","Goc nhin thuc te tu nguoi di truoc"),
      ("5","Luu len Drive va GitHub","Y kien cong dong moi luu len Drive va GitHub.","Chatbot luon biet nguoi that dang lo lang dieu gi.","Reddit data moi tren Drive","Tu dong"),
    ]
  },

  # ── 7: Annual language & ECA ────────────────────────────────────────────────
  {
    "name":    "QUY TRINH 7 — Cap nhat yeu cau ngon ngu & bang cap (hang nam)",
    "freq":    "Annual — ngay 15 thang 1 hang nam luc 11:00 sang gio VN",
    "trigger": "1 lan/nam vi thong tin IELTS, CELPIP, WES rat it thay doi — cap nhat hang nam la du",
    "scope":   "IELTS, CELPIP, TEF Canada (diem ngon ngu) + WES, IQAS (danh gia bang cap nuoc ngoai)",
    "bg_light": PURPLE_BG, "bg_head": PURPLE,
    "steps": [
      ("1","He thong thuc day dau nam","Ngay 15/01 hang nam, he thong tu cap nhat toan bo thong tin ve bai thi ngon ngu va danh gia bang cap.","Thong tin IELTS, CELPIP thay doi rat it — 1 lan/nam la du, khong can ton tai nguyen chay thuong xuyen.","Quy trinh bat dau","1 lan/nam"),
      ("2","Chuan bi phan mem","Tai code, kho du lieu, cai cong cu — can trinh duyet vi mot so trang dung JavaScript.","Buoc chuan bi tieu chuan.","Moi truong san sang","~2 phut"),
      ("3","Doc trang web IELTS, CELPIP, TEF","Phan mem vao tung trang web cua IELTS, CELPIP va TEF Canada — doc bang quy doi diem, yeu cau diem toi thieu cho tung chuong trinh.","Nhu nhan vien ngoi doc 3 trang web thi ngon ngu, ghi chep bang diem quy doi — nhung lam trong 5 phut.","5 file thong tin ngon ngu cap nhat","Thong tin it thay doi → annual du"),
      ("4","Doc huong dan WES va IQAS","Tai va doc huong dan danh gia bang cap cua WES (to chuc toan quoc) va IQAS (Alberta) — quy trinh, giay to can thiet, thoi gian xu ly.","Khach hang hay hoi 'Bang dai hoc Viet Nam co duoc cong nhan khong?' — chatbot can co thong tin WES/IQAS de tra loi dung.","Huong dan ECA day du trong kho","Thong tin on dinh, it thay doi"),
      ("5","Luu len Drive va GitHub","Thong tin ngon ngu va bang cap cap nhat len Drive va GitHub — dung suot ca nam cho den lan cap nhat tiep theo.","Cap nhat 1 lan dung 12 thang — tiet kiem tai nguyen.","Thong tin IELTS/ECA moi tren Drive","Tu dong"),
    ]
  },

  # ── 8: Monthly IRCC ─────────────────────────────────────────────────────────
  {
    "name":    "QUY TRINH 8 — Cap nhat du lieu IRCC (hang thang)",
    "freq":    "Monthly — ngay 05 hang thang luc 09:00 sang gio VN",
    "trigger": "Tu dong ngay 5 hang thang — hoac bam chay thu cong khi can",
    "scope":   "3 nguon IRCC: thoi gian xu ly ho so · thong ke phe duyet PNP · lien ket Express Entry voi PNP",
    "bg_light": AMBER_BG, "bg_head": "B45309",
    "steps": [
      ("1","He thong thuc day","Ngay 5 hang thang, he thong tu thu thap du lieu moi nhat tu IRCC — Bo Di tru Lien bang Canada.","IRCC cap nhat thoi gian xu ly hang thang — ngay 5 la thoi diem du lieu moi nhat da duoc dang.","Quy trinh bat dau","Tu dong"),
      ("2","Chuan bi phan mem","Tai code va kho du lieu ve may chu, cai cong cu can thiet bao gom trinh duyet tu dong.","Buoc khoi dong tieu chuan — giong cac quy trinh khac.","Moi truong san sang","~3 phut"),
      ("3","Lay thoi gian xu ly ho so","Tai file JSON truc tiep tu may chu IRCC — file nay chua thoi gian xu ly cap nhat cho tat ca loai visa va PR. Khong can mo trinh duyet, du lieu duoc giao thang dang co cau truc.","IRCC cung cap file du lieu cong khai — nhu tai bang Excel tu website chinh phu moi thang.","Thoi gian xu ly moi nhat theo tung loai ho so","Nguon chinh thuc nhat — dung cho chatbot"),
      ("4","Lay thong ke phe duyet PNP","Tai du lieu open data cua IRCC ve so luong ho so PNP da duoc phe duyet theo tinh, theo nam — dung de phan tich xu huong va tu van chien luoc cho khach hang.","Nhu doc bao cao thuong nien cua chinh phu ve so nguoi nhap cu theo tung tinh.","Bang thong ke phe duyet PNP theo tinh/nam","Du lieu phan tich chien luoc"),
      ("5","Lay thong tin lien ket Express Entry","Truy cap trang IRCC giai thich cach PNP lien ket voi Express Entry — thong tin nay thay doi theo chinh sach nen can cap nhat dinh ky.","Khach hang hay hoi: 'PNP co giup toi vao Express Entry khong?' — chatbot can co thong tin moi nhat de tra loi dung.","Huong dan EE-PNP link cap nhat","Thong tin chinh sach quan trong"),
      ("6","Kiem tra va luu du lieu","3 nguon du lieu duoc kiem tra co ban roi luu vao kho — moi file co nhan nguon goc ro rang (IRCC, ngay cap nhat) de chatbot biet day la thong tin chinh thuc.","Nhu dong dau 'nguon chinh phu Canada' len moi tai lieu truoc khi luu vao he thong.","3 file du lieu IRCC trong kho KB","Co nhan nguon chinh phu"),
      ("7","Dong bo len Google Drive","Toan bo du lieu IRCC moi duoc copy len Google Drive — consultant co the tra cuu thoi gian xu ly ho so moi nhat truc tiep.","Nhu cap nhat bang gia moi nhat vao file chung cua team.","Drive cap nhat — thong tin xu ly ho so moi nhat","Neu Drive loi → van luu GitHub"),
      ("8","Luu lich su thay doi","Ghi lai toan bo thay doi vao kho GitHub — co the so sanh thoi gian xu ly thang nay voi thang truoc de phat hien xu huong.","Lich su du lieu giup tra loi: 'Thoi gian xu ly dang tang hay giam so voi 3 thang truoc?'","IRCC data thang moi tren GitHub","Chi luu khi co thay doi"),
    ]
  },

  # ── 9: Monthly AstraDB Sync ─────────────────────────────────────────────────
  {
    "name":    "QUY TRINH 9 — Dong bo len Vector Database (sau moi cap nhat lon)",
    "freq":    "Monthly — ngay 10 hang thang luc 11:00 sang gio VN (sau khi cac quy trinh 1-8 da chay xong)",
    "trigger": "Tu dong ngay 10 hang thang — hoac bam thu cong sau khi co nhieu du lieu moi",
    "scope":   "Toan bo kho KB (50+ nguon) — chuyen doi thanh dang vector de AI chatbot co the tim kiem nghi nghia",
    "bg_light": ROSE_BG, "bg_head": ROSE,
    "steps": [
      ("1","He thong thuc day","Ngay 10 hang thang — sau khi cac quy trinh crawl da chay xong, he thong bat dau dong bo du lieu moi len Vector Database.","Nhu sau khi nhan hang moi ve kho, ban phai cap nhat lai danh muc de nhan vien de tim.","Quy trinh bat dau","Sau cac quy trinh crawl"),
      ("2","Ket noi len AstraDB","He thong ket noi den Datastax AstraDB — co so du lieu vector duoc thiet ke rieng de AI co the tim kiem theo nghi nghia (semantic search).","Nhu ket noi den thu vien kho lon — khong tim theo tu khoa, ma tim theo 'y nghia va chu de'.","Ket noi AstraDB thanh cong","Can API key — neu het han se bao loi"),
      ("3","Quet toan bo kho KB","Doc tat ca file Markdown trong kho KB — khoang 100+ file covering chinh sach AAIP, BCPNP, IRCC, tin tuc, draw history, Job Bank...","Nhu nhan vien quan thu vien doc lai toan bo sach moi lan co sach moi nhap kho.","Danh sach tat ca file can cap nhat","Quet ~100 files"),
      ("4","Chia nho noi dung (Chunking)","Moi file lon duoc cat thanh cac doan ngan (500-1000 tu) — phan mem tu dong biet cat o dau sao cho moi doan van con day du y nghia, khong bi cat giua cau.","Nhu chia quyen sach day 300 trang thanh 50 the bai flash card — moi the la mot chu de hoan chinh.","Khong gian cac doan ngan, ro rang","Chien luoc cat thong minh theo tung loai noi dung"),
      ("5","Tao Vector Embeddings","Moi doan van ban duoc bien doi thanh mot 'vector' — mot day so hoc hien thi vi tri cua doan van ban trong khong gian nghi nghia. Doan noi ve 'diem IELTS' se gan voi 'diem ngon ngu', xa voi 'giay to nop ho so'.","Nhu dich ngon ngu cua con nguoi sang ngon ngu cua may — may hieu 'y nghia' thay vi chi quet tu khoa.","Moi doan van ban co vector tuong ung","AI chatbot dua tren cong nghe nay de tra loi"),
      ("6","Nap vao AstraDB","Upload toan bo vector len hai collection: lnc_kb_chunks (van ban Markdown) va lnc_kb_structured (JSON draw history, stats) — chi cap nhat doan nao thay doi, giu nguyen doan cu.","Nhu update danh muc thu vien — sach moi them vao, sach cu khong mat.","Du lieu moi tren AstraDB — chatbot co the su dung ngay","Moi lan cap nhat: ~10 phut"),
      ("7","Kiem tra chatbot hoat dong","Chay mot loat cau hoi thu nghiem tren chatbot sau khi cap nhat — dam bao no tra loi dung voi du lieu moi nhat.","Nhu 'UAT test' sau moi lan cap nhat he thong.","Chatbot pass tat ca test cases","Phat hien loi truoc khi khach hang dung"),
    ]
  },

  # ── 10: Weekly Health Check ─────────────────────────────────────────────────
  {
    "name":    "QUY TRINH 10 — Kiem tra suc khoe he thong (hang tuan)",
    "freq":    "Weekly — Chu Nhat hang tuan luc 08:00 sang gio VN",
    "trigger": "Tu dong moi Chu Nhat sang som — bao cao ket qua qua email/Slack cho team",
    "scope":   "Kiem tra 50 URL nguon du lieu + tinh toan ty le thanh cong + phat hien loi som truoc khi crawl chinh chay",
    "bg_light": SLATE_BG, "bg_head": SLATE,
    "steps": [
      ("1","He thong thuc day","Moi Chu Nhat 08:00 sang, he thong tu dong 'kham suc khoe' toan bo pipeline — kiem tra xem tat ca 50 trang web nguon co con hoat dong khong.","Nhu bac si kham dinh ky: phat hien van de som, xu ly truoc khi thanh benh nang.","Quy trinh kiem tra bat dau","Moi tuan 1 lan"),
      ("2","Kiem tra 50 URL nguon","He thong gui request kiem tra den tung URL trong config — kiem tra: trang web con mo khong? Ma phan hoi la 200 (OK) hay 404 (khong tim thay)?","Nhu goi dien cho 50 doi tac de kiem tra xem ai van dang hoat dong.","Danh sach URL: con song / da loi","Phat hien loi truoc khi crawl that"),
      ("3","Do thoi gian phan hoi","Ghi lai thoi gian phan hoi cua tung trang — trang nao cham bat thuong (>10 giay) co the bao hieu sap bi loi hoac da bi chinh phu cap nhat cau truc.","Nhu kiem tra toc do internet: binh thuong la nhanh, cham bat thuong la dau hieu can xem lai.","Bao cao thoi gian phan hoi 50 URL","Phat hien som xu huong xau"),
      ("4","Phan tich ty le thanh cong 30 ngay qua","Tinh toan: trong 30 ngay qua, moi nguon crawl thanh cong bao nhieu lan? Nguon nao co ty le loi cao nhat? Nguon nao luon on dinh?","Nhu bao cao the luc cuoi thang: nhan vien nao lam viec on dinh, ai thuong xuyen bi om.","Bang ty le thanh cong theo tung nguon","Biet nguon nao can theo doi them"),
      ("5","Tao bao cao suc khoe","Tong hop ket qua thanh bao cao ngan gon: so URL OK, so URL loi, so URL canh bao, ty le on dinh tong the.","Nhu bao cao kham suc khoe: chi so nao binh thuong, chi so nao can chu y.","File bao cao suc khoe he thong","Luu vao kho KB de theo doi lich su"),
      ("6","Gui thong bao","Neu phat hien loi nghiem trong (URL chinh bi down), tu dong gui canh bao cho team qua Slack/email — de xu ly kip thoi truoc khi crawl chinh chay.","Nhu he thong canh bao chay: phat hien moi co van de la bao ngay, khong doi den khi chay that.","Team nhan thong bao kip thoi","Chi gui khi co loi nghiem trong"),
    ]
  },

  # ── 11: Monthly auto report ─────────────────────────────────────────────────
  {
    "name":    "QUY TRINH 11 — Tao bao cao tu dong cuoi thang",
    "freq":    "Monthly — ngay 28 hang thang luc 09:00 sang gio VN",
    "trigger": "Tu dong cuoi thang — tong ket toan bo hoat dong cua he thong trong thang",
    "scope":   "Tong ket: so file moi, so crawl thanh cong, ty le loi, du lieu moi nhat theo tung chuong trinh",
    "bg_light": ORANGE_BG, "bg_head": ORANGE,
    "steps": [
      ("1","He thong thuc day cuoi thang","Ngay 28 hang thang, he thong tu dong tong ket toan bo hoat dong cua thang vua qua — bao nhieu lan crawl, bao nhieu file moi, ty le thanh cong la bao nhieu.","Nhu ke toan cuoi thang lam bao cao so sach.","Quy trinh tao bao cao bat dau","Tu dong"),
      ("2","Dem so file moi da them vao KB","Quet kho KB va so sanh voi ngay dau thang — dem chinh xac bao nhieu file Markdown, bao nhieu JSON da duoc them moi hoac cap nhat.","Nhu kiem ke kho hang cuoi thang: them duoc bao nhieu san pham moi.","So file moi: ~XX files trong thang","Du lieu thong ke chinh xac"),
      ("3","Tong hop ket qua cac workflow","Thu thap log cua tat ca 10 quy trinh da chay trong thang: workflow nao thanh cong, workflow nao gap loi, mat bao lau, da xu ly bao nhieu nguon.","Nhu bao cao hieu suat cua tung to may trong xuong.","Bang tong ket 10 workflows trong thang","Phan tich hieu suat he thong"),
      ("4","Tao file Excel bao cao","Tu dong tao file Excel dep voi bieu do, bang so lieu, ty le thanh cong theo mau sac — giong he thong bao cao chuyen nghiep.","File Excel duoc tao giong nhu nguoi lam thu cong — nhung may lam trong 30 giay.","File Excel bao cao thang.xlsx","San sang gui cho khach hang"),
      ("5","Tao trang HTML tom tat","Tao them mot trang web HTML dep, de xem tren dien thoai — khach hang co the xem bao cao truc tiep khong can mo Excel.","Nhu dashboard online: mo link tren dien thoai la thay ngay ket qua.","Trang HTML bao cao co the xem online","Khach hang khong can cai Excel"),
      ("6","Luu len Drive va GitHub","File Excel va trang HTML duoc luu len Drive (de gui khach hang) va GitHub Pages (de xem online).","Khach hang nhan link bao cao trong hop thu, bam vao la xem ngay.","Bao cao thang tren Drive & GitHub Pages","Tu dong gui link cho khach hang"),
    ]
  },
]

# ── Render all workflows ──────────────────────────────────────────────────────
for wf in workflows:
    row = render_wf(ws, row, wf, HEADERS)

# ── Bottom summary ────────────────────────────────────────────────────────────
ws.merge_cells(f"A{row}:F{row}")
c = ws.cell(row, 1,
    "  KET LUAN: 11 quy trinh tren chay hoan toan tu dong — "
    "LNC Global khong can bo tri nhan vien theo doi, "
    "du lieu luon moi va chinh xac, "
    "AI chatbot luon co thong tin de tu van khach hang 24/7.")
c.fill = fill(NAVY)
c.font = f(bold=True, color=TEAL, size=10)
c.alignment = a("left", "center", wrap=True)
ws.row_dimensions[row].height = 30

today = date.today().strftime("%Y%m%d")
out = f"LNC_Workflow_Detail_{today}_v4.xlsx"
wb.save(out)
print(f"[OK] Da tao: {out}")
