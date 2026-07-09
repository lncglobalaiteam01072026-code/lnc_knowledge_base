---
access_level: chatbot
chunk_strategy: standard
file_role: wp_package_guide
lang: en
last_updated: '2026-07-09'
priority_weight: 1.0
program: IRCC
retrieval_strategy: direct
source_id: lnc_wp_package_guide
source_url: https://www.canada.ca/en/immigration-refugees-citizenship/services/application/application-forms-guides/apply-work-permit-outside-canada.html
topic: wp_application_package
version: '1.0'
---

# Work Permit Document Package — Team Docs Reference

## Mục tiêu
Giúp team Docs kiểm tra và tạo bộ hồ sơ Work Permit (nộp ngoài Canada) chuẩn theo quy định IRCC — không sai, không thiếu, không thừa.

---

## Bộ 3 Form Templates (trong KB)

| # | File | Form ID | Mục đích | Ai điền |
|---|------|---------|----------|---------|
| 1 | `10_form_docs/canada/1. Application form for work permit (IMM1295) - DONE.pdf` | IMM1295 | Application for Work Permit (Outside Canada) — form chính | Applicant chính |
| 2 | `10_form_docs/canada/2. Family information for work permit (IMM5645).pdf` | IMM5645 | Family Information — khai báo toàn bộ thành viên gia đình | Applicant chính |
| 3 | `10_form_docs/canada/3. Schedule 1 - Application for Temporary Residence visa (IMM5257_1e) - DONE.pdf` | IMM5257_1e | Schedule 1 — dành cho một số visa office cụ thể (ví dụ Bangkok) | Applicant chính |

> **Lưu ý kỹ thuật**: IMM1295 và IMM5257 là XFA dynamic PDF — phải dùng Adobe Acrobat Reader DC, không dùng browser PDF viewer. IMM5645 là static PDF, có thể điền tay hoặc type và print.

---

## Tài liệu hướng dẫn liên quan trong KB

| Tài liệu | File | Nội dung |
|----------|------|----------|
| Guide 5487 | `09_regulations/canada/guides/guide_5487_wp_outside.md` | Hướng dẫn chi tiết từng field IMM1295 |
| WP Application Package | `09_regulations/canada/packages/wp_outside_canada.md` | Toàn bộ package + document checklist |
| WP Completeness Check | `09_regulations/canada/ee_process/ircc_completeness_check.md` | Spec IRCC: thư xác nhận kinh nghiệm phải có gì |
| WP Need Permit | `09_regulations/canada/work_permit/need_permit.md` | Xác định applicant có cần WP không |
| PDI Genuineness | `09_regulations/canada/bulletins/pdi_genuineness.md` | Officer tiêu chí đánh giá tính xác thực job offer |
| PDI Steps Assess | `09_regulations/canada/bulletins/pdi_steps_assess.md` | Quy trình officer đánh giá WP application |

---

## Quy trình kiểm tra bộ hồ sơ (5 bước)

### Bước 1 — Xác định loại WP
- Employer-specific (có LMIA hoặc LMIA-exempt)? → IMM1295 + LMIA letter / offer number
- Open Work Permit? → IMM1295 + tài liệu chứng minh eligibility (PGWP, SOWP...)
- Nộp ngoài Canada? → Dùng bộ này (IMM1295)
- Nộp trong Canada (extend)? → Dùng IMM5710 (chưa có trong bộ — cần thêm)

### Bước 2 — Form chính (IMM1295)
Các mục hay bị lỗi:
- [ ] **Section A** — Tên đúng với passport, date of birth YYYY-MM-DD
- [ ] **Section B** — Contact info: địa chỉ đầy đủ, email, phone
- [ ] **Section C** — Travel document: passport number, issue/expiry date, country of issue
- [ ] **Section D** — Current immigration status đúng
- [ ] **Section E** — Work permit details: job title khớp NOC, employer name, intended work location
- [ ] **Section F** — Declaration + chữ ký tay (bắt buộc, không để trống)
- [ ] **Photo** — 1 ảnh 35mm × 45mm nếu nộp giấy

### Bước 3 — IMM5645 (Family Information)
Trường hay bị bỏ sót:
- [ ] **Section A**: Cha + mẹ + vợ/chồng (dù không đi cùng Canada)
- [ ] **Section B**: Tất cả con — kể cả con đã lớn, con nuôi, con riêng
- [ ] **Section C**: Tất cả anh/chị/em ruột — kể cả đã mất
- [ ] Nếu không có vợ/chồng: ký vào NOTE 1 (chứng nhận độc thân)
- [ ] Tên: điền cả tiếng Anh (không dấu) + tiếng Việt (có dấu) trên cùng dòng

### Bước 4 — Schedule 1 (IMM5257_1e)
Chỉ cần khi:
- Visa office Bangkok xử lý hồ sơ Việt Nam yêu cầu
- Applicant xin TRV (Temporary Resident Visa) đồng thời với WP
- Kiểm tra: chữ ký + date ở trang cuối, không để trống

### Bước 5 — Supporting Documents
Theo `09_regulations/canada/packages/wp_outside_canada.md`:
- [ ] Passport: photo-biographic page (certified copy)
- [ ] Job offer letter / LMIA approval (nếu employer-specific)
- [ ] Employment reference letters — đủ yếu tố theo `ircc_completeness_check.md`
- [ ] Educational transcripts / credentials (nếu NOC yêu cầu)
- [ ] Language test results (IELTS/TEF nếu relevant)
- [ ] Financial proof (nếu relevant)
- [ ] Biometrics instruction letter (nếu đã book)

---

## Lỗi phổ biến và cách tránh

| Lỗi | Hậu quả | Cách tránh |
|-----|---------|-----------|
| IMM1295 điền bằng browser PDF viewer | Form bị lỗi, IRCC không đọc được | Bắt buộc Adobe Acrobat Reader DC |
| Tên tiếng Việt thiếu dấu trên IMM5645 | File bị trả về | Điền đủ cả 2 ngôn ngữ |
| Bỏ trống Section C (anh chị em) IMM5645 | Completeness failure | Khai đủ, nếu không có ghi "N/A" |
| Job title không khớp NOC trong reference letter | Officer nghi ngờ, có thể từ chối | Đối chiếu `noc/profiles/noc_{code}.md` trước khi viết |
| Self-employment khai như employed | IRCC nghi ngờ gian lận | Xem `ircc_completeness_check.md` mục self-employed |
| Thiếu chữ ký Declaration IMM1295 | Form bị reject ngay | Không để trống — AI không ký thay |

---

## Human Checkpoint — BẮT BUỘC

- [ ] Attorney / RCIC review trước khi nộp — AI không tự nộp form
- [ ] Không điền ngày nộp cho đến khi Attorney confirm
- [ ] Mọi thay đổi thông tin khách hàng phải được client ký xác nhận
