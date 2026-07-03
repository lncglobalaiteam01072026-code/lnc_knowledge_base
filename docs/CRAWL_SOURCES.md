# Nguồn dữ liệu crawl — Cây thư mục KB

Tổng hợp toàn bộ nguồn được crawl tự động, tổ chức theo chương trình và tần suất.
File này được cập nhật thủ công khi có thay đổi `config/sources.json`.

---

## Lịch chạy

| Tần suất | Cron | Nguồn |
|----------|------|-------|
| Daily | Hàng ngày 01:00 UTC | immigration.ca (AAIP, BCPNP) |
| Weekly | Thứ Hai 02:00 UTC | BCPNP invitations |
| Biweekly | Thứ Hai tuần chẵn 03:00 UTC | Reddit communities (Alberta, BC, NZ) |
| Monthly | Ngày 1 hàng tháng 02:00 UTC | AAIP statistics, IRCC processing, NZAEWV stats, JobBank, CIC News |
| Quarterly | Ngày 1 tháng 1/4/7/10 03:00 UTC | Toàn bộ program core (AAIP, BCPNP, NZAEWV, IRCC) |
| Annual | 15/01 04:00 UTC | Language tests, ECA, biểu mẫu |

---

## AAIP — Alberta Advantage Immigration Program

### 📅 Daily

```
01_program_core/aaip/
└── immigration_ca_overview.md
    └── https://immigration.ca/alberta-immigration/
```

### 📅 Monthly

```
06_statistics/aaip/
├── draw_history_{year}.json
│   └── https://www.alberta.ca/aaip-processing-information
│   └── https://www.alberta.ca/system/files/im-aaip-draw-history-summary.pdf (PDF fallback)
└── entrepreneur_pipeline.md
    └── https://www.alberta.ca/aaip-processing-information
```

### 📅 Quarterly

```
01_program_core/aaip/
│
│   [Rural Entrepreneur Stream]
├── eligibility.md
│   └── https://www.alberta.ca/aaip-rural-entrepreneur-stream-eligibility
├── points_grid.md
│   └── https://www.alberta.ca/aaip-rural-entrepreneur-stream-eligibility
├── ineligible_businesses.md
│   └── https://www.alberta.ca/aaip-rural-entrepreneur-stream-eligibility
├── how_to_apply.md
│   └── https://www.alberta.ca/aaip-rural-entrepreneur-stream-how-to-apply
├── nominee_obligations.md
│   └── https://www.alberta.ca/aaip-rural-entrepreneur-stream-after-you-are-nominated
├── pr_application_guide.md
│   └── https://www.alberta.ca/aaip-rural-entrepreneur-stream-after-you-are-nominated
│
│   [Express Entry Stream]
├── express_entry/
│   ├── overview.md
│   │   └── https://www.alberta.ca/aaip-alberta-express-entry-stream
│   ├── eligibility.md
│   │   └── https://www.alberta.ca/aaip-alberta-express-entry-stream-eligibility
│   └── after_nominated.md
│       └── https://www.alberta.ca/aaip-alberta-express-entry-stream-after-you-are-nominated
│
│   [Opportunity Stream]
├── opportunity_stream/
│   ├── overview.md
│   │   └── https://www.alberta.ca/aaip-alberta-opportunity-stream
│   ├── eligibility.md
│   │   └── https://www.alberta.ca/aaip-alberta-opportunity-stream-eligibility
│   └── after_nominated.md
│       └── https://www.alberta.ca/aaip-alberta-opportunity-stream-after-you-are-nominated
│
│   [Rural Renewal Stream]
├── rural_renewal/
│   ├── overview.md
│   │   └── https://www.alberta.ca/aaip-rural-renewal-stream
│   ├── eligibility.md
│   │   └── https://www.alberta.ca/aaip-rural-renewal-stream-eligibility
│   └── after_nominated.md
│       └── https://www.alberta.ca/aaip-rural-renewal-stream-after-you-are-nominated
│
│   [Farm Stream]
├── farm_stream/
│   ├── overview.md
│   │   └── https://www.alberta.ca/aaip-farm-stream
│   ├── eligibility.md
│   │   └── https://www.alberta.ca/aaip-farm-stream-eligibility
│   ├── how_to_apply.md
│   │   └── https://www.alberta.ca/aaip-farm-stream-how-to-apply
│   └── after_nominated.md
│       └── https://www.alberta.ca/aaip-farm-stream-after-you-are-nominated
│
│   [Graduate Entrepreneur Stream]
├── graduate_entrepreneur/
│   ├── overview.md
│   │   └── https://www.alberta.ca/aaip-graduate-entrepreneur-stream
│   └── eligibility.md
│       └── https://www.alberta.ca/aaip-graduate-entrepreneur-stream-eligibility
│
│   [Foreign Graduate Entrepreneur Stream]
├── foreign_graduate_entrepreneur/
│   ├── overview.md
│   │   └── https://www.alberta.ca/aaip-foreign-graduate-entrepreneur-stream
│   └── eligibility.md
│       └── https://www.alberta.ca/aaip-foreign-graduate-entrepreneur-stream-eligibility
│
│   [Worker Streams]
├── worker_streams_how_to_apply.md
│   └── https://www.alberta.ca/how-to-apply-to-aaip-worker-streams
└── resources.md
    └── https://www.alberta.ca/aaip-resources

03_province_community/alberta/
├── communities/_index.md
│   └── https://www.alberta.ca/aaip-rural-entrepreneur-stream-participating-communities
└── rural_renewal_communities.md
    └── https://www.alberta.ca/aaip-rural-renewal-stream-community-designation

04_forms_guides/aaip/
├── eoi_points_grid.pdf
│   └── https://www.alberta.ca/system/files/im-worker-stream-expression-of-interest-points-grid.pdf
├── worker_document_checklist.pdf
│   └── https://www.alberta.ca/system/files/jeti-aaip-worker-streams-document-checklist.pdf
└── helpful_hints_portal.pdf
    └── https://www.alberta.ca/system/files/jeti-aaip-helpful-hints.pdf

05_policies_rules/aaip/
└── faq.md
    └── https://www.alberta.ca/aaip-answers-for-common-questions
```

### 📅 Annual

```
04_forms_guides/aaip/
├── representative_form.pdf
│   └── https://www.alberta.ca/system/files/custom_downloaded_images/lbr-aaip-candidate-representative-form.pdf
└── dependants_authorization_form.pdf
    └── https://www.alberta.ca/system/files/custom_downloaded_images/lbr-aaip-authorization-spouse-dependants-information-form.pdf
```

---

## BCPNP — BC Provincial Nominee Program

### 📅 Daily

```
01_program_core/bcpnp/
└── immigration_ca_overview.md
    └── https://immigration.ca/british-columbia-immigration/
```

### 📅 Weekly

```
06_statistics/bcpnp/
├── ei_draw_history_{year}.json
│   └── https://www.welcomebc.ca/immigrate-to-b-c/about-the-bc-provincial-nominee-program/invitations-to-apply
├── si_invitations_{year}.md
│   └── https://www.welcomebc.ca/immigrate-to-b-c/about-the-bc-provincial-nominee-program/invitations-to-apply
└── si_pool_snapshot.md
    └── https://www.welcomebc.ca/immigrate-to-b-c/about-the-bc-provincial-nominee-program/invitations-to-apply
```

### 📅 Quarterly

```
01_program_core/bcpnp/
├── base_stream.md
│   └── https://www.welcomebc.ca/immigrate-to-b-c/for-entrepreneurs-and-businesses
├── regional_stream.md
│   └── https://www.welcomebc.ca/immigrate-to-b-c/for-entrepreneurs-and-businesses
├── strategic_projects.md
│   └── https://www.welcomebc.ca/immigrate-to-b-c/for-entrepreneurs-and-businesses
├── ineligible_businesses.md
│   └── https://www.welcomebc.ca/immigrate-to-b-c/for-entrepreneurs-and-businesses
├── performance_agreement.md
│   └── https://www.welcomebc.ca/immigrate-to-b-c/for-entrepreneurs-and-businesses
├── fees.md
│   └── https://www.welcomebc.ca/immigrate-to-b-c/for-entrepreneurs-and-businesses
└── eligibility.md
    └── https://www.welcomebc.ca/immigrate-to-b-c/entrepreneur-immigration

02_documents_compliance/checklists/
└── bcpnp_document_checklist.md
    └── https://www.welcomebc.ca/immigrate-to-b-c/about-the-bc-provincial-nominee-program/documents

03_province_community/bc/
└── economic_regions/_index.md
    └── https://www.welcomebc.ca/immigrate-to-b-c/about-the-bc-provincial-nominee-program/regional-immigration

04_forms_guides/bcpnp/
│   [Entrepreneur Immigration — EI]
├── ei_program_guide_base.pdf
├── ei_program_guide_regional.pdf
├── ei_application_guide.pdf
├── ei_post_arrival_guide.pdf
├── ei_post_nomination_guide.pdf
├── representative_form_applicant.pdf
├── ei_interpreter_form.pdf
│   [Skills Immigration — SI]
├── si_program_guide.pdf
├── si_application_guide.pdf
├── si_post_nomination_guide.pdf
├── si_employer_declaration_form.pdf
└── si_representative_form_employer.pdf
    (tất cả PDF tải trực tiếp qua slug: https://www.welcomebc.ca/immigrate-to-b-c/{slug}-pdf
     danh sách đầy đủ nằm trên trang Documents: .../about-the-bc-provincial-nominee-program/documents)
```

### 📅 Annual

```
06_statistics/bcpnp/
└── ei_invitations_2025.pdf
    └── https://www.welcomebc.ca/immigrate-to-b-c/bc-pnp-invitations-to-apply-ei-2025-pdf
```

---

## NZAEWV — New Zealand Accredited Employer Work Visa

> **Lưu ý kỹ thuật**: Tất cả nguồn INZ dùng `use_httpx: true` (HTTP/1.1 + markdownify).
> immigration.govt.nz block headless Chrome (Playwright) với 403.

### 📅 Monthly

```
06_statistics/nzaewv/
└── processing_times.md
    └── https://www.immigration.govt.nz/about-us/news-centre/accredited-employer-work-visa-aewv-key-information-and-statistics/

08_news_updates/nzaewv/
└── inz_media_centre.md
    └── https://www.immigration.govt.nz/about-us/news-centre/
```

### 📅 Quarterly

```
01_program_core/nzaewv/
│   [source: nzaewv_overview — 3 output files từ 1 URL]
├── overview.md       (section_selector: full_page)
├── eligibility.md    (section_selector: h2:contains('Who can apply'))
│   └── cùng URL: https://www.immigration.govt.nz/visas/accredited-employer-work-visa/
├── how_to_apply.md   (section_selector: h2:contains('How to apply'))
│   └── cùng URL: https://www.immigration.govt.nz/visas/accredited-employer-work-visa/
│   (INZ gộp eligibility + how-to-apply vào 1 trang dài dùng anchor sections)
│
├── employer_accreditation.md
│   └── https://www.immigration.govt.nz/work/for-employers/getting-accreditation-or-approval-to-hire/employer-accreditation-for-the-aewv/aewv-employer-accreditation-and-job-check-process/
└── job_check.md
    └── https://www.immigration.govt.nz/work/for-employers/getting-accreditation-or-approval-to-hire/employer-accreditation-for-the-aewv/applying-for-a-job-check-process-steps/

06_statistics/nzaewv/
└── visa_decision_stats.md
    └── https://www.immigration.govt.nz/about-us/research-and-statistics/statistics/
```

---

## IRCC — Immigration, Refugees and Citizenship Canada

### 📅 Monthly

```
06_statistics/ircc/
├── pnp_processing_times.md
│   └── https://www.canada.ca/content/dam/ircc/documents/json/flpt-en.json
└── pnp_approvals.csv
    └── https://ircc.canada.ca/opendata-donneesouvertes/data/ODP-PR-PT_IMMCAT.csv
```

### 📅 Quarterly

```
06_statistics/ircc/
└── express_entry_pnp_link.md
    └── https://www.canada.ca/en/immigration-refugees-citizenship/services/immigrate-canada/provincial-nominees.html
```

### 📅 Annual

```
02_documents_compliance/
├── language_tests.md
│   └── https://www.canada.ca/en/immigration-refugees-citizenship/services/immigrate-canada/express-entry/documents/language-test.html
└── eca_guide.md
    └── https://www.canada.ca/en/immigration-refugees-citizenship/services/immigrate-canada/express-entry/documents/education-assessment.html
```

---

## JobBank — Canada Job Market Reports

Nguồn bổ sung, `access_level: internal` (không đưa lên chatbot).

### 📅 Monthly

```
07_unofficial/jobbank/
├── alberta_job_market.md
│   └── https://www.jobbank.gc.ca/trend-analysis/job-market-reports/alberta
└── bc_job_market.md
    └── https://www.jobbank.gc.ca/trend-analysis/job-market-reports/british-columbia
```

---

## CIC News — RSS feeds

Nguồn bổ sung, `access_level: internal`.

### 📅 Monthly

```
08_news_updates/cicnews/
├── pnp_news.md
│   └── https://www.cicnews.com/category/provincial-nominees/feed/ (RSS, 20 bài)
└── express_entry_news.md
    └── https://www.cicnews.com/category/express-entry/feed/ (RSS, 20 bài)
```

---

## Reddit — Community posts

Nguồn bổ sung, `access_level: internal`, `trust_level: LOW`.
Mỗi post đủ điều kiện (score ≥ 5, có keyword di trú) được ghi thành file riêng.
File được xoá và tạo lại mỗi lần chạy nếu nội dung thay đổi.

### 📅 Biweekly

```
03_province_community/alberta/
└── r_{subreddit}_{post_id}.md          ← dynamic, per post
    Subreddits: r/alberta, r/ImmigrationCanada, r/expressentry, r/PersonalFinanceCanada

03_province_community/bc/
└── r_{subreddit}_{post_id}.md          ← dynamic, per post
    Subreddits: r/britishcolumbia, r/ImmigrationCanada, r/expressentry, r/PersonalFinanceCanada

03_province_community/nz/
└── r_{subreddit}_{post_id}.md          ← dynamic, per post
    Subreddits: r/newzealand, r/IWantOut, r/NewZealandVisas
```

---

## Tổng hợp theo thư mục KB

```
lnc-knowledge-base/
├── 01_program_core/
│   ├── aaip/                         ~35 files — quarterly + daily (immigration.ca)
│   ├── bcpnp/                         ~9 files — quarterly + daily (immigration.ca)
│   └── nzaewv/                         5 files — quarterly
├── 02_documents_compliance/
│   ├── checklists/                     1 file  — quarterly
│   ├── language_tests.md               1 file  — annual
│   └── eca_guide.md                    1 file  — annual
├── 03_province_community/
│   ├── alberta/                        2 files static + dynamic Reddit — quarterly / biweekly
│   ├── bc/                             1 file  static + dynamic Reddit — quarterly / biweekly
│   └── nz/                             dynamic Reddit — biweekly
├── 04_forms_guides/
│   ├── aaip/                           5 files — quarterly/annual
│   └── bcpnp/                         12 files — quarterly
├── 05_policies_rules/
│   └── aaip/                           1 file  — quarterly
├── 06_statistics/
│   ├── aaip/                           2 files — monthly
│   ├── bcpnp/                          4 files — weekly/annual
│   ├── ircc/                           3 files — monthly/quarterly
│   └── nzaewv/                         2 files — monthly/quarterly
├── 07_unofficial/
│   └── jobbank/                        2 files — monthly
├── 08_news_updates/
│   ├── cicnews/                        2 files — monthly
│   └── nzaewv/                         1 file  — monthly
└── CRAWL_SUMMARY.md                    ← cập nhật sau mỗi lần crawl
```
