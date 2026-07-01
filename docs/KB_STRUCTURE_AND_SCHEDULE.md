# Cấu trúc Knowledge Base và Lịch Crawl

Tài liệu này mô tả cây thư mục KB output, nội dung từng thư mục, và lịch crawl tự động theo tần suất.

---

## Cây thư mục đầu ra

```
lnc-knowledge-base/
│
├── 01_program_core/                    # Nội dung chính của từng chương trình
│   ├── aaip/                           # Alberta Advantage Immigration Program
│   │   ├── eligibility.md
│   │   ├── how_to_apply.md
│   │   ├── points_grid.md
│   │   ├── ineligible_businesses.md
│   │   ├── nominee_obligations.md
│   │   ├── pr_application_guide.md
│   │   ├── worker_streams_how_to_apply.md
│   │   ├── resources.md
│   │   ├── express_entry/
│   │   │   ├── overview.md
│   │   │   ├── eligibility.md
│   │   │   └── after_nominated.md
│   │   ├── opportunity_stream/
│   │   │   ├── overview.md
│   │   │   ├── eligibility.md
│   │   │   └── after_nominated.md
│   │   ├── rural_renewal/
│   │   │   ├── overview.md
│   │   │   ├── eligibility.md
│   │   │   └── after_nominated.md
│   │   ├── farm_stream/
│   │   │   ├── overview.md
│   │   │   ├── eligibility.md
│   │   │   ├── how_to_apply.md
│   │   │   └── after_nominated.md
│   │   ├── graduate_entrepreneur/
│   │   │   ├── overview.md
│   │   │   └── eligibility.md
│   │   └── foreign_graduate_entrepreneur/
│   │       ├── overview.md
│   │       └── eligibility.md
│   │
│   └── bcpnp/                          # BC Provincial Nominee Program
│       ├── eligibility.md
│       ├── base_stream.md
│       ├── regional_stream.md
│       ├── strategic_projects.md
│       ├── ineligible_businesses.md
│       ├── performance_agreement.md
│       └── fees.md
│
├── 02_documents_compliance/            # Giấy tờ & yêu cầu tuân thủ
│   ├── language_tests.md
│   ├── eca_guide.md
│   └── checklists/
│       └── bcpnp_document_checklist.md
│
├── 03_province_community/              # Danh sách cộng đồng / vùng địa lý
│   ├── alberta/
│   │   ├── communities/
│   │   │   └── _index.md
│   │   └── rural_renewal_communities.md
│   └── bc/
│       └── economic_regions/
│           └── _index.md
│
├── 04_forms_guides/                    # Form và hướng dẫn PDF
│   ├── aaip/
│   │   ├── eoi_points_grid.pdf
│   │   ├── worker_document_checklist.pdf
│   │   ├── helpful_hints_portal.pdf
│   │   ├── representative_form.pdf
│   │   └── dependants_authorization_form.pdf
│   └── bcpnp/
│       ├── ei_program_guide_base.pdf
│       ├── ei_program_guide_regional.pdf
│       ├── ei_application_guide.pdf
│       ├── ei_post_arrival_guide.pdf
│       ├── ei_post_nomination_guide.pdf
│       ├── ei_interpreter_form.pdf
│       ├── representative_form_applicant.pdf
│       ├── si_program_guide.pdf
│       ├── si_application_guide.pdf
│       ├── si_post_nomination_guide.pdf
│       ├── si_employer_declaration_form.pdf
│       └── si_representative_form_employer.pdf
│
├── 05_policies_rules/                  # FAQ và chính sách
│   └── aaip/
│       └── faq.md
│
└── 06_statistics/                      # Thống kê, lịch sử draw, thời gian xử lý
    ├── aaip/
    │   ├── draw_history_{year}.json
    │   └── entrepreneur_pipeline.md
    ├── bcpnp/
    │   ├── ei_draw_history_{year}.json
    │   ├── ei_invitations_2025.pdf
    │   ├── si_invitations_{year}.md
    │   └── si_pool_snapshot.md
    └── ircc/
        ├── pnp_processing_times.md
        └── pnp_approvals.csv
```

---

## Giải thích từng thư mục

### `01_program_core/` — Nội dung cốt lõi chương trình

Chứa thông tin chính thức từ trang web chính phủ về quy trình và điều kiện của từng chương trình.

#### `aaip/` — Alberta Advantage Immigration Program

| File | Nội dung |
|------|----------|
| `eligibility.md` | Điều kiện đủ điều kiện cho Rural Entrepreneur Stream; bảng điểm EOI tổng quan |
| `points_grid.md` | Bảng điểm EOI chi tiết (Points Grid) |
| `ineligible_businesses.md` | Danh sách ngành nghề không được chấp nhận |
| `how_to_apply.md` | Quy trình nộp đơn Rural Entrepreneur Stream |
| `nominee_obligations.md` | Nghĩa vụ sau khi được đề cử (nominee obligations) |
| `pr_application_guide.md` | Hướng dẫn nộp đơn PR sau khi được đề cử |
| `worker_streams_how_to_apply.md` | Quy trình nộp đơn cho các Worker Streams |
| `resources.md` | Tổng hợp tài nguyên và liên kết hữu ích |
| `express_entry/` | Alberta Express Entry Stream (overview, eligibility, sau đề cử) |
| `opportunity_stream/` | Alberta Opportunity Stream (overview, eligibility, sau đề cử) |
| `rural_renewal/` | Rural Renewal Stream (overview, eligibility, sau đề cử) |
| `farm_stream/` | Farm Stream (overview, eligibility, cách nộp, sau đề cử) |
| `graduate_entrepreneur/` | Graduate Entrepreneur Stream |
| `foreign_graduate_entrepreneur/` | Foreign Graduate Entrepreneur Stream |

#### `bcpnp/` — BC Provincial Nominee Program

| File | Nội dung |
|------|----------|
| `eligibility.md` | Điều kiện chung cho Entrepreneur Immigration |
| `base_stream.md` | Base Stream — yêu cầu, điểm, quy trình |
| `regional_stream.md` | Regional Stream — yêu cầu vùng địa lý |
| `strategic_projects.md` | Strategic Projects stream |
| `ineligible_businesses.md` | Ngành nghề không được chấp nhận |
| `performance_agreement.md` | Điều khoản Performance Agreement |
| `fees.md` | Bảng phí nộp đơn |

---

### `02_documents_compliance/` — Giấy tờ & tuân thủ

Thông tin về yêu cầu giấy tờ áp dụng chung cho cả AAIP lẫn BCPNP.

| File | Nội dung |
|------|----------|
| `language_tests.md` | Danh sách bài thi ngôn ngữ được IRCC chấp nhận, điểm tối thiểu theo chương trình |
| `eca_guide.md` | Hướng dẫn đánh giá bằng cấp nước ngoài (ECA) |
| `checklists/bcpnp_document_checklist.md` | Checklist giấy tờ cần thiết cho BCPNP |

---

### `03_province_community/` — Cộng đồng & vùng địa lý

Danh sách các cộng đồng và vùng kinh tế tham gia chương trình định cư.

| File | Nội dung |
|------|----------|
| `alberta/communities/_index.md` | Danh sách các cộng đồng tham gia AAIP Rural Entrepreneur Stream |
| `alberta/rural_renewal_communities.md` | Các cộng đồng được chỉ định cho Rural Renewal Stream |
| `bc/economic_regions/_index.md` | Các vùng kinh tế BC tham gia Regional Stream của BCPNP |

---

### `04_forms_guides/` — Form và hướng dẫn PDF

File PDF tải trực tiếp từ trang chính phủ. Không xử lý nội dung, lưu nguyên bản.

**AAIP:** EOI Points Grid, Document Checklist, Helpful Hints, Representative Form, Dependants Authorization Form

**BCPNP:** Program guides (EI Base, Regional, SI), Application guides, Post-arrival/nomination guides, Representative & interpreter forms, Employer declaration form

---

### `05_policies_rules/` — Chính sách và FAQ

| File | Nội dung |
|------|----------|
| `aaip/faq.md` | Câu hỏi thường gặp chính thức từ trang AAIP |

---

### `06_statistics/` — Thống kê và lịch sử draw

Dữ liệu số: lịch sử draw, thời gian xử lý, tỉ lệ chấp thuận.

| File | Nội dung |
|------|----------|
| `aaip/draw_history_{year}.json` | Lịch sử các đợt draw AAIP theo năm (tổng hợp từ web + PDF) |
| `aaip/entrepreneur_pipeline.md` | Thống kê pipeline đơn doanh nhân AAIP |
| `bcpnp/ei_draw_history_{year}.json` | Lịch sử draw Entrepreneur Immigration BCPNP |
| `bcpnp/si_invitations_{year}.md` | Thống kê lời mời Skills Immigration BCPNP |
| `bcpnp/si_pool_snapshot.md` | Snapshot pool đăng ký Skills Immigration hiện tại |
| `bcpnp/ei_invitations_2025.pdf` | File PDF tổng hợp lời mời EI năm 2025 |
| `ircc/pnp_processing_times.md` | Thời gian xử lý PNP (Base và Express Entry stream) từ IRCC |
| `ircc/pnp_approvals.csv` | Dữ liệu thô số PR được chấp thuận theo tỉnh (open data IRCC) |

---

## Lịch crawl tự động

### Weekly — Mỗi thứ Hai, 02:00 UTC

> **Lý do weekly:** BCPNP công bố invitation rounds thường xuyên (mỗi 1–2 tuần), cần cập nhật nhanh.

| Source ID | URL nguồn | File đầu ra |
|-----------|-----------|-------------|
| `bcpnp_invitations` | welcomebc.ca/…/invitations-to-apply | `06_statistics/bcpnp/ei_draw_history_{year}.json` |
| | | `06_statistics/bcpnp/si_invitations_{year}.md` |
| | | `06_statistics/bcpnp/si_pool_snapshot.md` |

---

### Monthly — Ngày 1 hàng tháng, 02:00 UTC

> **Lý do monthly:** Lịch sử draw AAIP và thời gian xử lý IRCC cập nhật 1–2 lần/tháng.

| Source ID | URL nguồn | File đầu ra |
|-----------|-----------|-------------|
| `aaip_processing_info` | alberta.ca/aaip-processing-information | `06_statistics/aaip/entrepreneur_pipeline.md` |
| | | `06_statistics/aaip/draw_history_{year}.json` |
| `aaip_draw_summary_pdf` | alberta.ca/…/im-aaip-draw-history-summary.pdf | Merge vào `draw_history_{year}.json` |
| `ircc_processing_times` | canada.ca/…/flpt-en.json (API) | `06_statistics/ircc/pnp_processing_times.md` |
| `ircc_pnp_approvals` | ircc.canada.ca/…/ODP-PR-PT_IMMCAT.csv | `06_statistics/ircc/pnp_approvals.csv` |

---

### Quarterly — Ngày 1 tháng 1, 4, 7, 10 — 03:00 UTC

> **Lý do quarterly:** Nội dung chương trình (eligibility, streams, communities) thay đổi chậm, thường theo quý hoặc khi có chính sách mới.

#### AAIP — Alberta

| Source ID | Nội dung crawl | File đầu ra |
|-----------|----------------|-------------|
| `aaip_eligibility` | Điều kiện + points grid + ineligible businesses | `eligibility.md`, `points_grid.md`, `ineligible_businesses.md` |
| `aaip_how_to_apply` | Quy trình nộp đơn Rural Entrepreneur | `how_to_apply.md` |
| `aaip_after_nominated` | Sau khi được đề cử + hướng dẫn PR | `nominee_obligations.md`, `pr_application_guide.md` |
| `aaip_communities` | Danh sách cộng đồng tham gia | `03_province_community/alberta/communities/_index.md` |
| `aaip_express_entry` | Alberta Express Entry Stream | `express_entry/overview.md`, `eligibility.md`, `after_nominated.md` |
| `aaip_opportunity_stream` | Alberta Opportunity Stream | `opportunity_stream/overview.md`, `eligibility.md`, `after_nominated.md` |
| `aaip_rural_renewal` | Rural Renewal Stream | `rural_renewal/overview.md`, `eligibility.md`, `after_nominated.md` |
| `aaip_rural_renewal_communities` | Cộng đồng Rural Renewal | `03_province_community/alberta/rural_renewal_communities.md` |
| `aaip_farm_stream` | Farm Stream | `farm_stream/overview.md`, `eligibility.md`, `how_to_apply.md`, `after_nominated.md` |
| `aaip_graduate_entrepreneur` | Graduate Entrepreneur Stream | `graduate_entrepreneur/overview.md`, `eligibility.md` |
| `aaip_foreign_graduate_entrepreneur` | Foreign Graduate Entrepreneur | `foreign_graduate_entrepreneur/overview.md`, `eligibility.md` |
| `aaip_worker_how_to_apply` | Hướng dẫn Worker Streams | `worker_streams_how_to_apply.md` |
| `aaip_resources` | Tổng hợp tài nguyên | `resources.md` |
| `aaip_eoi_points_grid` | PDF: Bảng điểm EOI | `04_forms_guides/aaip/eoi_points_grid.pdf` |
| `aaip_worker_doc_checklist` | PDF: Checklist giấy tờ Worker | `04_forms_guides/aaip/worker_document_checklist.pdf` |
| `aaip_helpful_hints` | PDF: Helpful Hints portal | `04_forms_guides/aaip/helpful_hints_portal.pdf` |
| `aaip_faq` | FAQ chính thức AAIP | `05_policies_rules/aaip/faq.md` |

#### BCPNP — British Columbia

| Source ID | Nội dung crawl | File đầu ra |
|-----------|----------------|-------------|
| `bcpnp_entrepreneur` | Base/Regional/Strategic streams, fees, performance agreement | `base_stream.md`, `regional_stream.md`, `strategic_projects.md`, `ineligible_businesses.md`, `performance_agreement.md`, `fees.md` |
| `bcpnp_eligibility` | Điều kiện Entrepreneur Immigration | `eligibility.md` |
| `bcpnp_documents` | Checklist giấy tờ | `02_documents_compliance/checklists/bcpnp_document_checklist.md` |
| `bcpnp_guides_pdf` | 12 PDF guides (EI + SI programs, application, post-nomination, forms) | `04_forms_guides/bcpnp/*.pdf` |
| `bcpnp_regional_communities` | Các vùng kinh tế BC | `03_province_community/bc/economic_regions/_index.md` |

---

### Annual — 15 tháng 1, 04:00 UTC

> **Lý do annual:** Các form mẫu và hướng dẫn bằng cấp/ngôn ngữ gần như không đổi theo năm. PDF lịch sử draw năm trước lấy toàn bộ 1 lần vào đầu năm mới.

| Source ID | Nội dung crawl | File đầu ra |
|-----------|----------------|-------------|
| `ircc_language_tests` | Danh sách bài thi ngôn ngữ + điểm tối thiểu (IRCC) | `02_documents_compliance/language_tests.md` |
| `ircc_eca` | Hướng dẫn đánh giá bằng cấp nước ngoài ECA | `02_documents_compliance/eca_guide.md` |
| `aaip_representative_form` | PDF: Mẫu ủy quyền người đại diện AAIP | `04_forms_guides/aaip/representative_form.pdf` |
| `aaip_dependants_auth_form` | PDF: Mẫu ủy quyền thông tin vợ/chồng, người phụ thuộc | `04_forms_guides/aaip/dependants_authorization_form.pdf` |
| `bcpnp_ei_invitations_2025` | PDF tổng hợp lời mời EI cả năm trước | `06_statistics/bcpnp/ei_invitations_2025.pdf` |

---

## Tóm tắt theo tần suất

| Tần suất | Lịch chạy | Số sources | Chương trình |
|----------|-----------|-----------|--------------|
| **Weekly** | Thứ 2 — 02:00 UTC | 1 | BCPNP |
| **Monthly** | Ngày 1 — 02:00 UTC | 4 | AAIP, IRCC |
| **Quarterly** | Ngày 1 tháng 1/4/7/10 — 03:00 UTC | 22 | AAIP, BCPNP |
| **Annual** | 15 tháng 1 — 04:00 UTC | 5 | IRCC, AAIP, BCPNP |
