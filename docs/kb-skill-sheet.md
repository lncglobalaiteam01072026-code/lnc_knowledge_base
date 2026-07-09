# Kho dữ liệu di trú LNC — Tổng hợp kỹ thuật

> Cập nhật: 2026-07-09 · 121 nguồn · 4 chương trình · 9 lớp dữ liệu

---

## 1. Tổng quan hệ thống

| Thông số | Giá trị |
|---|---|
| Tổng nguồn | **121 sources** |
| Chương trình | AAIP (45) · BCPNP (21) · IRCC (26) · NZAEWV (19) · Khác (10) |
| Lớp dữ liệu | 01–09 (9 layers) |
| Deep crawl sources | 15 sources (crawl_depth ≥ 2) |
| PDF sources | 1 source |
| Files ước tính | ~350 files trong KB repo |
| Output repo | `lnc_knowledge_base` (GitHub) |
| Crawler engine | crawl4ai (Playwright) · httpx (canada.ca) · httpx+pypdf (PDF) |
| Codebase | `c:/lnc2chuongtrinhv2` → `lnc_knowledge_base.git` |

### Luồng dữ liệu

```
config/sources.json
        │
        ▼
   crawl.py  ──► get_crawler()
                      │
           ┌──────────┼──────────────────┐
           ▼          ▼                  ▼
    BaseCrawler   DeepCrawler        PDFCrawler
    (1 trang)    (BFS multi-page)   (httpx + pypdf)
           │          │                  │
           └──────────┴──────────────────┘
                      │
              fetch_markdown()
              extract_section()
              tables_to_narrative()
                      │
              write_markdown() / write_json()
                      │
           schema_validator.validate_output()
                      │
              output/lnc-knowledge-base/
                      │
              GitHub commit → Google Drive sync
```

---

## 2. Cấu trúc thư mục KB (9 lớp)

| Layer | Thư mục | Nội dung |
|---|---|---|
| 01 | `01_program_core/` | Điều kiện, quy trình, sau đề cử — nguồn chính thống |
| 02 | `02_documents_compliance/` | Kiểm tra ngôn ngữ (IELTS/TEF), ECA |
| 03 | `03_province_community/` | Danh sách cộng đồng / vùng địa lý |
| 04 | `04_forms_guides/` | PDF biểu mẫu, hướng dẫn nộp hồ sơ |
| 05 | `05_policies_rules/` | Chính sách, FAQ, quy định nội bộ |
| 06 | `06_statistics/` | Draw history (JSON), processing times, thống kê |
| 07 | `07_unofficial/` | Job Bank — thị trường lao động (không chính thống) |
| 08 | `08_news_updates/` | CIC News, Reddit, báo di trú |
| 09 | `09_regulations/` | Luật di trú, NOC 2021, hướng dẫn nộp hồ sơ EE |

---

## 3. Các loại Crawler

### BaseCrawler (chuẩn)
- Dùng cho 1 URL → 1 file output
- `canada.ca` → httpx (HTTP/1.1, Akamai block HTTP/2)
- Các trang khác → crawl4ai (Playwright, JS rendering)
- Hỗ trợ `content_selector`, `section_selector`, `has_tables`

### DeepCrawler (BFS multi-page)
- Kích hoạt khi `crawl_depth > 1` và `program != "CICNEWS"`
- BFS queue, mỗi URL crawl 1 lần
- Skip homepage nếu không phải start URL
- `verify_links: true` → HEAD-check URL trước khi enqueue (httpx, timeout 8s)
- `link_filter` → giới hạn domain
- `max_articles` → giới hạn số trang tối đa

### PDFCrawler
- `is_pdf: true` → download PDF bằng httpx
- Trích text bằng `pypdf`
- Parse draw records bằng regex

### NewsCrawler / RedditCrawler / CSVCrawler / RawFileCrawler
- Các crawler đặc thù cho RSS, Reddit API, CSV, raw file download

---

## 4. Lịch chạy tự động (GitHub Actions)

| Tần suất | Cron | Sources | Mục đích |
|---|---|---|---|
| `daily` | `0 1 * * *` | 3 | immigration.ca (AAIP + BCPNP + news) |
| `weekly` | `0 2 * * 1` | 4 | BCPNP draws, IRCC times, INZ news, canadavisa/CBC |
| `biweekly` | `0 3 1,15 * *` | 3 | Reddit Alberta, BC, NZ |
| `monthly` | `0 9 1 * *` | 15 | Draw history, Green List, processing times |
| `quarterly` | `0 10 1 1,4,7,10 *` | 85 | Program core, regulations, Express Entry |
| `annual` | `0 11 15 1 *` | 11 | Language tests, ECA, immigration levels |

> Workflow quarterly chạy thêm `python scripts/validate_quarterly.py` trước khi commit.

---

## 5. Danh sách nguồn đầy đủ (121 sources)

### AAIP — Alberta Advantage Immigration Program (45 sources)

#### `01_program_core` (35 sources)

| ID | Loại | Tần suất | Output |
|---|---|---|---|
| `aaip_eligibility` | standard | quarterly | `01_program_core/aaip/eligibility.md` |
| `aaip_how_to_apply` | standard | quarterly | `01_program_core/aaip/how_to_apply.md` |
| `aaip_after_nominated` | standard | quarterly | `01_program_core/aaip/nominee_obligations.md` |
| `aaip_express_entry` | standard | quarterly | `01_program_core/aaip/express_entry/overview.md` |
| `aaip_express_entry_eligibility` | standard | quarterly | `01_program_core/aaip/express_entry/eligibility.md` |
| `aaip_express_entry_after_nominated` | standard | quarterly | `01_program_core/aaip/express_entry/after_nominated.md` |
| `aaip_opportunity_stream` | standard | quarterly | `01_program_core/aaip/opportunity_stream/overview.md` |
| `aaip_opportunity_eligibility` | standard | quarterly | `01_program_core/aaip/opportunity_stream/eligibility.md` |
| `aaip_opportunity_after_nominated` | standard | quarterly | `01_program_core/aaip/opportunity_stream/after_nominated.md` |
| `aaip_rural_renewal` | standard | quarterly | `01_program_core/aaip/rural_renewal/overview.md` |
| `aaip_rural_renewal_eligibility` | standard | quarterly | `01_program_core/aaip/rural_renewal/eligibility.md` |
| `aaip_rural_renewal_after_nominated` | standard | quarterly | `01_program_core/aaip/rural_renewal/after_nominated.md` |
| `aaip_farm_stream` | standard | quarterly | `01_program_core/aaip/farm_stream/overview.md` |
| `aaip_farm_eligibility` | standard | quarterly | `01_program_core/aaip/farm_stream/eligibility.md` |
| `aaip_farm_how_to_apply` | standard | quarterly | `01_program_core/aaip/farm_stream/how_to_apply.md` |
| `aaip_farm_after_nominated` | standard | quarterly | `01_program_core/aaip/farm_stream/after_nominated.md` |
| `aaip_graduate_entrepreneur` | standard | quarterly | `01_program_core/aaip/graduate_entrepreneur/overview.md` |
| `aaip_graduate_entrepreneur_eligibility` | standard | quarterly | `01_program_core/aaip/graduate_entrepreneur/eligibility.md` |
| `aaip_foreign_graduate_entrepreneur` | standard | quarterly | `01_program_core/aaip/foreign_graduate_entrepreneur/overview.md` |
| `aaip_foreign_graduate_entrepreneur_eligibility` | standard | quarterly | `01_program_core/aaip/foreign_graduate_entrepreneur/eligibility.md` |
| `aaip_worker_how_to_apply` | standard | quarterly | `01_program_core/aaip/worker_streams_how_to_apply.md` |
| `aaip_resources` | standard | quarterly | `01_program_core/aaip/resources.md` |
| `immigration_ca_aaip` | standard | daily | `01_program_core/aaip/immigration_ca_overview.md` |
| `sobirovs_aaip_rural_entrepreneur` | standard | quarterly | `01_program_core/aaip/hangluat/rural_entrepreneur_stream.md` |
| `sobirovs_aaip_streams_comparison` | standard | quarterly | `01_program_core/aaip/hangluat/aaip_entrepreneur_streams_comparison.md` |
| `sobirovs_aaip_farm_stream` | standard | quarterly | `01_program_core/aaip/hangluat/farm_stream_guide.md` |
| `sobirovs_c11_vs_ict` | standard | quarterly | `01_program_core/aaip/hangluat/c11_vs_ict.md` |
| `sobirovs_ceta_benefits` | standard | quarterly | `01_program_core/aaip/hangluat/ceta_benefits.md` |
| `sobirovs_success_vietnamese` | standard | quarterly | `01_program_core/aaip/hangluat/success_vietnamese_businesswoman.md` |
| `sobirovs_success_aaip_work_permit` | standard | quarterly | `01_program_core/aaip/hangluat/success_aaip_work_permit.md` |
| `sobirovs_foreign_graduate_entrepreneur` | standard | quarterly | `01_program_core/aaip/hangluat/foreign_graduate_entrepreneur.md` |
| `sobirovs_graduate_entrepreneur` | standard | quarterly | `01_program_core/aaip/hangluat/graduate_entrepreneur.md` |
| `sobirovs_pnp_intl_students` | standard | quarterly | `01_program_core/aaip/hangluat/pnp_international_students.md` |
| `sobirovs_brooks_alberta` | standard | quarterly | `01_program_core/aaip/hangluat/brooks_alberta.md` |
| `ackahlaw_aaip_news` | **deep** | monthly | `08_news_updates/aaip/ackahlaw/` |

#### `03_province_community` (2 sources)

| ID | Tần suất | Output |
|---|---|---|
| `aaip_communities` | quarterly | `03_province_community/alberta/communities/_index.md` |
| `aaip_rural_renewal_communities` | quarterly | `03_province_community/alberta/rural_renewal_communities.md` |

#### `04_forms_guides` (5 sources)

| ID | Tần suất | Output |
|---|---|---|
| `aaip_eoi_points_grid` | quarterly | `04_forms_guides/aaip/eoi_points_grid.pdf` |
| `aaip_worker_doc_checklist` | quarterly | `04_forms_guides/aaip/worker_document_checklist.pdf` |
| `aaip_helpful_hints` | quarterly | `04_forms_guides/aaip/helpful_hints_portal.pdf` |
| `aaip_representative_form` | annual | `04_forms_guides/aaip/representative_form.pdf` |
| `aaip_dependants_auth_form` | annual | `04_forms_guides/aaip/dependants_authorization_form.pdf` |

#### `05_policies_rules` (1 source)

| ID | Tần suất | Output |
|---|---|---|
| `aaip_faq` | quarterly | `05_policies_rules/aaip/faq.md` |

#### `06_statistics` (2 sources)

| ID | Loại | Tần suất | Output |
|---|---|---|---|
| `aaip_processing_info` | standard | monthly | `06_statistics/aaip/entrepreneur_pipeline.md` |
| `aaip_draw_summary_pdf` | **PDF** | monthly | `06_statistics/aaip/draw_history_{year}.json` |

---

### BCPNP — BC Provincial Nominee Program (21 sources)

#### `01_program_core` (15 sources)

| ID | Loại | Tần suất | Output |
|---|---|---|---|
| `bcpnp_entrepreneur` | standard | quarterly | `01_program_core/bcpnp/base_stream.md` |
| `bcpnp_eligibility` | standard | quarterly | `01_program_core/bcpnp/eligibility.md` |
| `immigration_ca_bcpnp` | standard | daily | `01_program_core/bcpnp/immigration_ca_overview.md` |
| `sobirovs_bc_pnp_guide` | standard | quarterly | `01_program_core/bcpnp/hangluat/bc_pnp_comprehensive_guide.md` |
| `sobirovs_bc_success_criminal_record` | standard | quarterly | `01_program_core/bcpnp/hangluat/success_bc_pnp_criminal_record.md` |
| `sobirovs_bc_business_plan_success` | standard | quarterly | `01_program_core/bcpnp/hangluat/business_plan_success.md` |
| `sobirovs_bc_summer_approvals` | standard | quarterly | `01_program_core/bcpnp/hangluat/success_summer_approvals.md` |
| `sobirovs_bc_best_cities` | standard | quarterly | `01_program_core/bcpnp/hangluat/best_cities_business.md` |
| `sobirovs_bc_arts_professionals` | standard | quarterly | `01_program_core/bcpnp/hangluat/success_arts_professionals.md` |
| `sobirovs_bc_deep` | **deep** | quarterly | `01_program_core/bcpnp/hangluat/` (multi-page) |
| `sobirovs_bc_pnp_canada_overview` | standard | quarterly | `01_program_core/bcpnp/hangluat/pnp_canada_overview.md` |
| `sobirovs_bc_provincial_work_permit` | standard | quarterly | `01_program_core/bcpnp/hangluat/provincial_business_work_permit.md` |
| `sobirovs_bc_legal_cost_estimator` | standard | quarterly | `01_program_core/bcpnp/hangluat/legal_cost_estimator.md` |
| `sobirovs_vietnam_guide` | standard | quarterly | `01_program_core/bcpnp/hangluat/vietnam_country_guide.md` |
| `heronlaw_bc_pnp` | **deep** | monthly | `01_program_core/bcpnp/hangluat/heronlaw/` |

#### Các lớp khác (6 sources)

| ID | Layer | Tần suất | Output |
|---|---|---|---|
| `bcpnp_documents` | 02 | quarterly | `02_documents_compliance/checklists/bcpnp_document_checklist.md` |
| `bcpnp_regional_communities` | 03 | quarterly | `03_province_community/bc/economic_regions/_index.md` |
| `bcpnp_guides_pdf` | 04 | quarterly | `04_forms_guides/bcpnp/ei_program_guide_base.pdf` |
| `bc_gov_small_business_guide` | 05 | quarterly | `05_policies_rules/bcpnp/bc_gov_small_business_guide.md` |
| `bcpnp_ei_invitations_2025` | 06 | annual | `06_statistics/bcpnp/ei_invitations_2025.pdf` |
| `bcpnp_invitations` | 06 | weekly | `06_statistics/bcpnp/ei_draw_history_{year}.json` |

---

### IRCC — Immigration, Refugees and Citizenship Canada (26 sources)

#### `01_program_core` + `02_documents_compliance` (4 sources)

| ID | Layer | Tần suất | Output |
|---|---|---|---|
| `ircc_pnp_overview` | 01 | annual | `01_program_core/ircc/pnp_overview.md` |
| `ircc_language_tests` | 02 | annual | `02_documents_compliance/language_tests.md` |
| `ircc_eca` | 02 | annual | `02_documents_compliance/eca_guide.md` |
| `ircc_language_requirements` | 02 | annual | `02_documents_compliance/language_requirements.md` |

#### `06_statistics` (5 sources)

| ID | Tần suất | Output |
|---|---|---|
| `ircc_processing_times` | monthly | `06_statistics/ircc/pnp_processing_times.md` |
| `ircc_pnp_approvals` | monthly | `06_statistics/ircc/pnp_approvals.csv` |
| `ircc_ee_pnp_link` | quarterly | `06_statistics/ircc/express_entry_pnp_link.md` |
| `statcan_immigration_stats` | quarterly | `06_statistics/ircc/statcan_immigration_overview.md` |
| `ircc_immigration_levels` | annual | `06_statistics/ircc/immigration_annual_report_page.md` |

#### `09_regulations` — Express Entry (8 sources)

| ID | Tần suất | Output |
|---|---|---|
| `ircc_ee_who_can_apply` | quarterly | `09_regulations/canada/express_entry/who_can_apply.md` |
| `ircc_ee_check_score` | quarterly | `09_regulations/canada/express_entry/check_score.md` |
| `ircc_ee_documents` | quarterly | `09_regulations/canada/express_entry/documents.md` |
| `ircc_ee_create_profile` | quarterly | `09_regulations/canada/express_entry/create_profile.md` |
| `ircc_ee_rounds_invitations` | quarterly | `09_regulations/canada/express_entry/rounds_invitations.md` |
| `ircc_ee_after_apply` | quarterly | `09_regulations/canada/express_entry/after_apply.md` |
| `ircc_ee_application_approved` | quarterly | `09_regulations/canada/express_entry/application_approved.md` |
| `ircc_common_supporting_docs` | quarterly | `09_regulations/canada/express_entry/common_supporting_docs.md` |

#### `09_regulations` — Work Experience & Proof (3 sources)

| ID | Tần suất | Output |
|---|---|---|
| `ircc_proof_work_experience` | quarterly | `09_regulations/canada/proof_work_experience.md` |
| `ircc_work_exp_outside_canada` | quarterly | `09_regulations/canada/express_entry_eligibility.md` |
| `ircc_work_exp_canada` | quarterly | `09_regulations/canada/express_entry_eligibility_canadian.md` |

#### `09_regulations` — NOC 2021 (2 sources)

| ID | Loại | Tần suất | Output |
|---|---|---|---|
| `noc_matrix_overview` | standard | annual | `09_regulations/canada/noc/noc_matrix_overview.md` |
| `noc_it_deep` | **deep** (depth=2) | annual | `09_regulations/canada/noc/` (13 pages) |

#### `09_regulations` — Reference Letter & Financial Proof (4 sources)

| ID | Tần suất | Output |
|---|---|---|
| `ircc_ee_completeness_check` | quarterly | `09_regulations/canada/reference_letter/ircc_completeness_check.md` |
| `ircc_ee_operations_manual` | quarterly | `09_regulations/canada/reference_letter/fsw_eligibility.md` |
| `ircc_financial_proof_guide` | quarterly | `09_regulations/canada/financial_proof/apply_for_pr.md` |
| `ircc_tax_records_guide` | quarterly | `09_regulations/canada/financial_proof/cec_eligibility.md` |

---

### NZAEWV — New Zealand Accredited Employer Work Visa (19 sources)

#### `01_program_core` (11 sources)

| ID | Loại | Tần suất | Output |
|---|---|---|---|
| `nzaewv_overview` | standard | quarterly | `01_program_core/nzaewv/overview.md` + 2 files |
| `nzaewv_employer_accreditation` | standard | quarterly | `01_program_core/nzaewv/employer_accreditation.md` |
| `nzaewv_job_check` | standard | quarterly | `01_program_core/nzaewv/job_check.md` |
| `nzaewv_green_list` | standard | monthly | `01_program_core/nzaewv/green_list.md` |
| `nzaewv_active_investor_plus` | standard | quarterly | `01_program_core/nzaewv/active_investor_plus.md` |
| `nz_business_info` | **deep** | quarterly | `01_program_core/nzaewv/business/` |
| `nz_careers` | **deep** | monthly | `01_program_core/nzaewv/careers/` |
| `pacificlegal_nz` | **deep** | quarterly | `01_program_core/nzaewv/hangluat/pacific_legal/` |
| `malcolm_pacific_nz` | **deep** | quarterly | `01_program_core/nzaewv/hangluat/malcolm_pacific/` |
| `lane_neave_nz` | **deep** | quarterly | `01_program_core/nzaewv/hangluat/lane_neave/` |
| `queen_city_law_nz` | **deep** | quarterly | `01_program_core/nzaewv/hangluat/queen_city_law/` |

#### Các lớp khác (8 sources)

| ID | Layer | Loại | Tần suất | Output |
|---|---|---|---|---|
| `nzaewv_english_requirements` | 02 | standard | annual | `02_documents_compliance/nzaewv/english_requirements.md` |
| `nzaewv_wage_threshold` | 05 | standard | monthly | `05_policies_rules/nzaewv/wage_threshold.md` |
| `nzaewv_employer_obligations` | 05 | standard | quarterly | `05_policies_rules/nzaewv/employer_obligations.md` |
| `nz_employment_law` | 05 | **deep** | quarterly | `05_policies_rules/nzaewv/employment_law/` |
| `nzaewv_processing_times` | 06 | standard | monthly | `06_statistics/nzaewv/processing_times.md` |
| `nzaewv_visa_stats` | 06 | standard | quarterly | `06_statistics/nzaewv/visa_decision_stats.md` |
| `nzaewv_inz_news` | 08 | standard | monthly | `08_news_updates/nzaewv/inz_media_centre.md` |
| `nzaewv_inz_news_deep` | 08 | **deep** | weekly | `08_news_updates/nzaewv/news/` |

---

### Các chương trình khác (10 sources)

| ID | Program | Loại | Tần suất | Output |
|---|---|---|---|---|
| `cicnews_pnp` | CICNEWS | standard | monthly | `08_news_updates/cicnews/pnp_news.md` |
| `cicnews_express_entry` | CICNEWS | standard | monthly | `08_news_updates/cicnews/express_entry_news.md` |
| `immigration_ca_news_canada` | NEWS | **deep** | daily | `08_news_updates/canada/immigration_ca/` |
| `canadavisa_immigration_news` | NEWS | **deep** | weekly | `08_news_updates/canada/canadavisa/` |
| `cbc_immigration_news` | NEWS | **deep** | weekly | `08_news_updates/canada/cbc/` |
| `reddit_alberta` | REDDIT | standard | biweekly | `08_news_updates/reddit/alberta_posts.md` |
| `reddit_bc` | REDDIT | standard | biweekly | `08_news_updates/reddit/bc_posts.md` |
| `reddit_nz` | REDDIT | standard | biweekly | `08_news_updates/reddit/nz_posts.md` |
| `jobbank_alberta` | JOBBANK | standard | monthly | `07_unofficial/jobbank/alberta_job_market.md` |
| `jobbank_bc` | JOBBANK | standard | monthly | `07_unofficial/jobbank/bc_job_market.md` |

---

## 6. Cấu hình source trong sources.json

### Trường bắt buộc

```json
{
  "id": "source_id_unique",
  "program": "AAIP|BCPNP|IRCC|NZAEWV|CICNEWS|NEWS|REDDIT|JOBBANK",
  "layer": "01_program_core",
  "frequency": "daily|weekly|biweekly|monthly|quarterly|annual",
  "url": "https://...",
  "output_files": [
    { "file": "01_program_core/.../output.md", "section_selector": "full_page" }
  ],
  "metadata": {
    "program": "AAIP",
    "topic": "eligibility",
    "lang": "en",
    "access_level": "chatbot"
  }
}
```

### Trường tuỳ chọn quan trọng

| Trường | Giá trị | Tác dụng |
|---|---|---|
| `content_selector` | CSS selector | Lọc nội dung trước khi extract section |
| `section_selector` | `full_page` / `h2:contains('...')` | Cắt section từ markdown |
| `has_tables` | `true` | Chạy `tables_to_narrative()` trước khi lưu |
| `is_pdf` | `true` | Dùng PDFCrawler |
| `is_csv` | `true` | Dùng CSVCrawler |
| `crawl_depth` | `2` / `3` | Kích hoạt DeepCrawler (BFS) |
| `max_articles` | số nguyên | Giới hạn pages trong DeepCrawler |
| `crawl_delay` | float (giây) | Delay giữa requests |
| `link_filter` | domain string | Chỉ enqueue URLs có chứa chuỗi này |
| `verify_links` | `true` | HEAD-check URL trước khi enqueue |
| `output_dir` | path | Thư mục output cho DeepCrawler |
| `use_httpx` | `true` | Force dùng httpx thay vì Playwright |
| `priority_weight` | 0.0–1.0 | Độ ưu tiên trong vector DB |
| `chunk_strategy` | `standard` | Chiến lược chunk cho RAG |

---

## 7. Frontmatter output (Markdown)

Mỗi file `.md` được ghi ra có YAML frontmatter:

```yaml
---
source_id: aaip_eligibility
source_url: https://www.alberta.ca/...
last_updated: 2026-07-09
program: AAIP
topic: eligibility
lang: en
access_level: chatbot
chunk_strategy: standard
priority_weight: 1.0
---
```

Mỗi file `.json` được bọc:

```json
{
  "metadata": { "source_id": "...", "last_updated": "...", ... },
  "data": [ { "draw": 123, "date": "...", ... } ]
}
```

---

## 8. Validation rules

File `validators/schema_validator.py` kiểm tra sau mỗi crawl:

**Markdown:**
- Tất cả frontmatter fields required phải có
- Content ≥ 100 ký tự
- Không có raw `|---|` tables (báo hiệu `table_converter` bị lỗi)

**JSON:**
- Có keys `metadata` và `data`
- `data` không rỗng

---

## 9. Xử lý đặc biệt

### canada.ca (Akamai)
- Akamai CDN chặn HTTP/2 từ CI → dùng httpx HTTP/1.1
- Một số sub-path (`/apply-permanent-residence/submit/`, `/guide-5291*`) trả 404 trên GET dù HEAD trả 200
- Không dùng Chrome User-Agent cho canada.ca (JA3 fingerprint mismatch)

### noc.esdc.gc.ca
- Yêu cầu JavaScript → dùng Playwright (crawl4ai)
- Individual occupation profile URLs (`/Occupations/OccupationProfile?code=XXX`) cần kiểm tra riêng
- Hiện dùng DeepCrawler BFS từ homepage để lấy cấu trúc NOC

### Windows encoding
- `sources.json` chứa ký tự tiếng Việt → đọc bắt buộc `encoding="utf-8"`
- `crawl.py` và `load_config()` đã fix: `CONFIG_PATH.read_text(encoding="utf-8")`

### Google Drive sync
- Script: `scripts/build_rclone_conf.py`
- Dùng rclone với OAuth refresh token → `gdrive:lnc-knowledge-base-temp`
- Token lưu trong GitHub Secret `GDRIVE_REFRESH_TOKEN` (hết hạn ~6 tháng)

---

## 10. Lệnh hay dùng

```bash
# Chạy theo tần suất
python crawl.py --frequency quarterly
python crawl.py --frequency monthly
python crawl.py --frequency annual

# Chạy 1 source
python crawl.py --id aaip_eligibility

# Chạy nhiều source song song
python crawl.py --ids ircc_ee_who_can_apply ircc_ee_check_score noc_matrix_overview

# Chạy tất cả
python crawl.py --all

# Validate quarterly output
python scripts/validate_quarterly.py

# Kiểm tra URL tồn tại (httpx HEAD check)
python -c "
import httpx, asyncio
async def chk(url):
    async with httpx.AsyncClient(timeout=12, follow_redirects=True) as c:
        r = await c.head(url)
        print(r.status_code, url)
asyncio.run(chk('https://...'))
"
```

---

*File này được tạo tự động từ `config/sources.json` — cập nhật mỗi khi thêm source mới.*
