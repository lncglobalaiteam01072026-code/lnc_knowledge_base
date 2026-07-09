# LNC Knowledge Base — Quy trình Crawl Pipeline

> Tài liệu này mô tả toàn bộ quy trình từ cấu hình nguồn → crawl dữ liệu → ghi file → đẩy lên Google Drive và GitHub.

---

## 1. Tổng quan kiến trúc

```
config/sources.json
       │
       ▼
   crawl.py  ─────────────────────────────────────────┐
       │                                              │
       ├─► StandardCrawler   (fetch 1 trang, selector)│
       ├─► DeepCrawler       (BFS đa cấp, depth ≥ 2)  │
       ├─► NewsCrawler       (RSS feed)               │
       └─► PDFCrawler        (download + parse PDF)   │
                                                      │
       ▼                                              │
output/lnc-knowledge-base/                            │
  ├── 00_meta/                                        │
  ├── 01_program_core/          (.md)                 │
  ├── 02_documents_compliance/  (.md)                 │
  ├── 03_province_community/    (.md)                 │
  ├── 04_forms_guides/          (.md / .pdf)          │
  ├── 05_policies_rules/        (.md)                 │
  ├── 06_statistics/            (.json / .md)         │
  ├── 07_unofficial/            (.md)                 │
  └── 08_news_updates/          (.md)                 │
                                                      │
       ▼                                              │
  Validate (schema_validator.py)                      │
       │                                              │
       ├──► Google Drive (rclone sync)  ◄─────────────┘
       └──► GitHub KB repo (git commit + push)
```

---

## 2. Nguồn dữ liệu (`config/sources.json`)

### Thống kê tổng quan

| Chỉ số | Giá trị |
|--------|---------|
| Tổng số nguồn | **104** |
| Chương trình | 8 (AAIP, BCPNP, NZAEWV, IRCC, CICNEWS, NEWS, JOBBANK, REDDIT) |
| Loại crawler | 4 (Standard, DeepCrawler, NewsCrawler, PDF) |

### Phân bổ theo chương trình

| Chương trình | Số nguồn | Mô tả |
|---|---|---|
| AAIP | 45 | Alberta Advantage Immigration Program |
| BCPNP | 21 | BC Provincial Nominee Program |
| NZAEWV | 19 | New Zealand Accredited Employer Work Visa |
| IRCC | 9 | Immigration, Refugees and Citizenship Canada |
| NEWS | 3 | Tin tức di trú Canada (deep crawl) |
| CICNEWS | 2 | CIC News RSS |
| JOBBANK | 2 | Job Bank Alberta & BC |
| REDDIT | 3 | Reddit r/alberta, r/britishcolumbia, r/newzealand |

### Phân bổ theo tần suất

| Frequency | Số nguồn | Workflow kích hoạt |
|---|---|---|
| `quarterly` | 70 | `crawl_quarterly.yml` |
| `monthly` | 15 | `crawl_monthly.yml` / `crawl_news.yml` |
| `annual` | 9 | `crawl_annual.yml` |
| `weekly` | 4 | `crawl_weekly.yml` |
| `biweekly` | 3 | không có workflow riêng (dùng `--all`) |
| `daily` | 3 | `crawl_daily.yml` |

### Cấu trúc một source entry

```json
{
  "id": "nz_employment_law",
  "program": "NZAEWV",
  "frequency": "quarterly",
  "url": "https://www.employment.govt.nz/",
  "link_filter": "employment.govt.nz",
  "crawl_depth": 2,
  "max_articles": 20,
  "crawl_delay": 1.5,
  "verify_links": false,
  "output_dir": "05_policies_rules/nzaewv/employment_law/",
  "output_files": [
    {
      "file": "05_policies_rules/nzaewv/employment_law/www-employment-govt-nz.md",
      "section_selector": "full_page"
    }
  ]
}
``` 

**Các trường quan trọng:**

| Trường | Mô tả |
|---|---|
| `id` | ID định danh duy nhất |
| `program` | Chương trình (AAIP / BCPNP / NZAEWV / …) |
| `frequency` | Tần suất crawl |
| `url` | URL gốc để crawl |
| `crawl_depth` | `> 1` → dùng DeepCrawler (BFS) |
| `link_filter` | Chỉ follow URL chứa chuỗi này |
| `max_articles` | Giới hạn số trang viết (DeepCrawler) |
| `crawl_delay` | Delay giữa các request (giây) |
| `startup_delay` | Delay khởi động (tránh rate limit khi chạy song song) |
| `verify_links` | `true` → HEAD-check URL trước khi enqueue |
| `use_httpx` | `true` → dùng httpx thay Playwright (trang tĩnh) |
| `is_pdf` | `true` → route sang PDFCrawler |
| `output_dir` | Thư mục đích trong KB |
| `section_selector` | CSS selector để extract nội dung |
| `has_tables` | `true` → chuyển bảng sang văn xuôi |

---

## 3. Các loại Crawler

### 3.1 StandardCrawler (87 nguồn)

Fetch một trang duy nhất, extract theo `section_selector`.

```
URL → fetch_markdown() [crawl4ai hoặc httpx]
    → extract_section() [selector-based]
    → tables_to_narrative() [nếu has_tables]
    → write_markdown() / write_json()
    → validate_output()
```

**Subclass theo chương trình:**
- `AAIPCrawler` — parse bảng draw history AAIP → JSON
- `BCPNPCrawler` — parse bảng draw history BCPNP → JSON
- `IRCCCrawler` — parse processing times → JSON/MD
- `NZCrawler` — crawl trang NZAEWV gov

### 3.2 DeepCrawler (14 nguồn)

BFS crawler: crawl nhiều trang liên kết theo độ sâu.

```
[START URL, depth=1]
    │
    ▼
fetch_markdown(url)
    │
    ├─► viết file .md
    │
    └─► extract tất cả https://... trong content
           │
           ├─► lọc theo link_filter
           ├─► bỏ URL trong _SKIP list
           ├─► [nếu verify_links=true] HEAD check → 200 OK?
           └─► enqueue [url, depth+1] nếu depth < crawl_depth
```

**Kích hoạt khi:** `crawl_depth > 1` và `program != "CICNEWS"`

**verify_links mode:** Khi `"verify_links": true`, mỗi URL phát hiện được sẽ bị kiểm tra bằng `httpx.head()` trước khi cho vào queue. URL trả về 4xx/5xx bị loại bỏ ngay → tránh fetch lãng phí.

### 3.3 NewsCrawler (2 nguồn — CICNEWS RSS)

Đọc RSS feed, lấy 10–20 bài mới nhất, viết tóm tắt dạng MD.

### 3.4 PDFCrawler (1 nguồn)

Download file PDF bằng `httpx`, extract text bằng `pypdf`, parse các bản ghi draw.

---

## 4. Output Files

### Định dạng Markdown

Mỗi file `.md` có YAML frontmatter bắt buộc:

```yaml
---
source_id: nz_employment_law
source_url: https://www.employment.govt.nz/
last_updated: "2026-07-08"
program: NZAEWV
topic: employment_law
lang: en
access_level: public
chunk_strategy: by_heading
priority_weight: 0.7
---

# Nội dung trang...
```

### Định dạng JSON (draw history, statistics)

```json
{
  "metadata": {
    "source_id": "aaip_draw_history",
    "last_updated": "2026-07-08",
    "program": "AAIP"
  },
  "data": [
    { "date": "2026-06-15", "stream": "Rural Entrepreneur", "invitations": 45 }
  ]
}
```

### Cấu trúc thư mục KB

```
lnc-knowledge-base/
├── 00_meta/
│   ├── crawl_log.jsonl        ← log từng lần crawl
│   ├── last_updated.json      ← timestamp cập nhật mới nhất mỗi source
│   └── sources.yaml           ← snapshot config
│
├── 01_program_core/
│   ├── aaip/                  ← eligibility, how_to_apply, post_nomination
│   ├── bcpnp/                 ← EI stream, entrepreneur stream
│   └── nzaewv/                ← overview, job_check, green_list, hangluat/
│
├── 02_documents_compliance/   ← language tests, ECA, document checklist
├── 03_province_community/     ← danh sách cộng đồng/địa phương
├── 04_forms_guides/           ← PDF guide đã extract
├── 05_policies_rules/         ← wage threshold, employer obligations, employment law
├── 06_statistics/             ← draw history JSON, processing times
├── 07_unofficial/             ← jobbank, reddit, law firm blogs
├── 08_news_updates/
│   ├── aaip/
│   ├── bcpnp/
│   ├── canada/                ← immigration.ca, canadavisa, CBC
│   ├── cicnews/               ← CIC News RSS
│   └── nzaewv/news/           ← INZ news centre
└── _archive/                  ← bản cũ tự động lưu khi file thay đổi
```

---

## 5. Validation

`validators/schema_validator.validate_output()` kiểm tra sau mỗi lần write:

| Loại file | Kiểm tra |
|---|---|
| `.md` | Đủ frontmatter fields · content ≥ 100 chars · không có bảng `\|---|` raw |
| `.json` | Có key `metadata` và `data` · `data` không rỗng |

Nếu fail → ghi `[FAIL]` vào log, không dừng toàn bộ pipeline.

---

## 6. GitHub Actions Workflows

| Workflow | Schedule | Nguồn chạy | Timeout |
|---|---|---|---|
| `crawl_daily.yml` | Hàng ngày 01:00 UTC (08:00 VN) | `--frequency daily` (immigration.ca) | 30 min |
| `crawl_news.yml` | Ngày 3 hàng tháng 03:00 UTC | `--layer 08_news_updates --frequency monthly` | 30 min |
| `crawl_weekly.yml` | Thứ Hai 02:00 UTC | `--frequency weekly` | 45 min |
| `crawl_monthly.yml` | Ngày 1 hàng tháng | `--frequency monthly` | 45 min |
| `crawl_quarterly.yml` | Ngày 1 tháng 1/4/7/10 | `--frequency quarterly` | 90 min |
| `crawl_annual.yml` | Ngày 1 tháng 1 | `--frequency annual` | 30 min |
| `crawl_all.yml` | Manual trigger | `--all` (104 nguồn) | 90 min |

### Các bước trong mỗi workflow

```
1. Checkout crawler repo (lnc_knowledge_base)
2. Checkout KB content repo → output/lnc-knowledge-base/
3. Setup Python 3.11 + pip cache
4. pip install -r requirements.txt
5. playwright install chromium --with-deps
6. python crawl.py [--frequency X | --all]
7. [Quarterly/All] python scripts/validate_quarterly.py
8. Upload to Google Drive (rclone sync)
9. git add -A → git commit → git push (KB repo)
```

---

## 7. Upload lên Google Drive

Script `scripts/build_rclone_conf.py` tự động:

1. Đọc 3 biến môi trường từ GitHub Secrets:
   - `GDRIVE_REFRESH_TOKEN` — OAuth refresh token
   - `GDRIVE_CLIENT_ID` — Google Cloud OAuth app ID
   - `GDRIVE_CLIENT_SECRET` — OAuth app secret

2. Build `/tmp/rclone.conf`:
```ini
[gdrive]
type = drive
scope = drive
client_id = <GDRIVE_CLIENT_ID>
client_secret = <GDRIVE_CLIENT_SECRET>
token = {"refresh_token": "<GDRIVE_REFRESH_TOKEN>", ...}
```

3. Chạy `rclone sync`:
```bash
rclone sync output/lnc-knowledge-base/ gdrive:lnc-knowledge-base-temp \
  --include "*.md" --include "*.json" \
  --transfers 8 --fast-list
```

**Lưu ý:** `GDRIVE_REFRESH_TOKEN` hết hạn sau ~6 tháng không dùng.
Khi hết hạn → lỗi `invalid_grant` → cần chạy `rclone config reconnect gdrive:` và cập nhật secret.

---

## 8. Commit vào KB GitHub Repo

Sau khi crawl xong, `lnc-crawler-bot` commit vào KB repo:

```bash
git add -A
git commit -m "chore: full crawl 2026-07-08 — all sources"
git pull --rebase -X ours origin HEAD
git push
```

Sử dụng `-X ours` khi rebase để ưu tiên version local (vừa crawl xong) nếu có conflict.

---

## 9. Chạy thủ công (local)

```bash
# Một source
python crawl.py --id nzaewv_green_list

# Nhiều source
python crawl.py --ids nz_business_info nz_employment_law lane_neave_nz

# Theo tần suất
python crawl.py --frequency quarterly
python crawl.py --frequency daily

# Tất cả
python crawl.py --all

# Validate output quarterly
python scripts/validate_quarterly.py
```

---

## 10. Thêm nguồn mới

1. Thêm entry vào `config/sources.json`
2. Chọn `crawler_depth > 1` nếu cần crawl nhiều trang (DeepCrawler)
3. Test: `python crawl.py --id <new_id>`
4. Nếu OK → copy output từ `output/lnc-knowledge-base/` vào thư mục tương ứng ở root
5. `git add` → commit → push
6. Cập nhật `lnc-demo/index.html`: sources array + count

---

*Cập nhật lần cuối: 2026-07-08*
