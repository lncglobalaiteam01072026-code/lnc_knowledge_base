# Nguồn dữ liệu crawl — Cây thư mục KB

Tổng hợp toàn bộ nguồn được crawl tự động, tổ chức theo chương trình và tần suất.
File này được generate từ `config/sources.json`.

---

## Lịch chạy

| Tần suất | Cron | Nguồn |
|----------|------|-------|
| Weekly | Thứ Hai 02:00 UTC | BCPNP invitations |
| Monthly | Ngày 1 hàng tháng 02:00 UTC | AAIP statistics, IRCC processing |
| Quarterly | Ngày 1 tháng 1/4/7/10 03:00 UTC | Toàn bộ program core |
| Annual | 15/01 04:00 UTC | Language tests, ECA, biểu mẫu |

---

## AAIP — Alberta Advantage Immigration Program

### 📅 Monthly

```
06_statistics/aaip/
├── draw_history_{year}.json
│   └── https://www.alberta.ca/aaip-processing-information
│   └── https://www.alberta.ca/system/files/im-aaip-draw-history-summary.pdf
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
    (tất cả PDF tải từ https://www.welcomebc.ca/immigrate-to-b-c/for-entrepreneurs-and-businesses)
```

### 📅 Annual

```
06_statistics/bcpnp/
└── ei_invitations_2025.pdf
    └── https://www.welcomebc.ca/immigrate-to-b-c/bc-pnp-invitations-to-apply-ei-2025-pdf
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

### 📅 Annual

```
02_documents_compliance/
├── language_tests.md
│   └── https://www.canada.ca/en/immigration-refugees-citizenship/services/immigrate-canada/express-entry/documents/language-test.html
└── eca_guide.md
    └── https://www.canada.ca/en/immigration-refugees-citizenship/services/immigrate-canada/express-entry/documents/education-assessed/how.html
```

---

## Tổng hợp theo thư mục KB

```
lnc-knowledge-base/
├── 01_program_core/
│   ├── aaip/                         33 files — quarterly
│   └── bcpnp/                         7 files — quarterly
├── 02_documents_compliance/
│   ├── checklists/                    1 file  — quarterly
│   ├── language_tests.md              1 file  — annual
│   └── eca_guide.md                   1 file  — annual
├── 03_province_community/
│   ├── alberta/                       2 files — quarterly
│   └── bc/                            1 file  — quarterly
├── 04_forms_guides/
│   ├── aaip/                          5 files — quarterly/annual
│   └── bcpnp/                        12 files — quarterly
├── 05_policies_rules/
│   └── aaip/                          1 file  — quarterly
├── 06_statistics/
│   ├── aaip/                          2 files — monthly
│   ├── bcpnp/                         4 files — weekly/annual
│   └── ircc/                          2 files — monthly
└── CRAWL_SUMMARY.md                   ← cập nhật sau mỗi lần crawl
```
