# Hướng dẫn setup: GitHub Actions Crawl → Google Drive

Pipeline tự động crawl dữ liệu immigration Canada (AAIP, BCPNP, IRCC), ghi vào KB repo, và đồng bộ lên Google Drive sau mỗi lần chạy.

---

## Mục lục

1. [Yêu cầu trước khi bắt đầu](#1-yêu-cầu-trước-khi-bắt-đầu)
2. [Tạo Google Drive refresh token](#2-tạo-google-drive-refresh-token)
3. [Cấu hình GitHub Secrets](#3-cấu-hình-github-secrets)
4. [Cấu trúc repo](#4-cấu-trúc-repo)
5. [Script build_rclone_conf.py](#5-script-build_rclone_confpy)
6. [Workflows và lịch chạy](#6-workflows-và-lịch-chạy)
7. [Kiểm tra kết quả](#7-kiểm-tra-kết-quả)
8. [Xử lý sự cố](#8-xử-lý-sự-cố)

---

## 1. Yêu cầu trước khi bắt đầu

- Repo crawl trên GitHub (repo này)
- Repo KB riêng để lưu output (ví dụ: `your-org/lnc-knowledge-base`)
- Tài khoản Google có quyền vào thư mục Drive đích
- `rclone` cài trên máy local (để lấy refresh token)
- `gh` CLI cài trên máy local

---

## 2. Tạo Google Drive refresh token

Bước này chạy **một lần duy nhất** trên máy local để lấy refresh token.

### 2.1 Cài rclone

```bash
# macOS
brew install rclone

# Linux
sudo apt install rclone

# Windows
winget install Rclone.Rclone
```

### 2.2 Lấy refresh token

```bash
rclone authorize "drive"
```

Lệnh này sẽ mở browser. Đăng nhập bằng tài khoản Google có quyền vào Drive, sau đó **approve**. Terminal sẽ in ra JSON dạng:

```json
{
  "access_token": "ya29.xxx",
  "token_type": "Bearer",
  "refresh_token": "1//0gXxx...",
  "expiry": "2026-06-28T..."
}
```

Copy phần `refresh_token` (chuỗi bắt đầu bằng `1//`).

> **Lưu ý quan trọng:** Không cần khai báo `client_id` / `client_secret`. rclone tự dùng credentials built-in khớp với token này.

### 2.3 Tạo thư mục đích trên Drive

Tạo một thư mục trên Google Drive (ví dụ: `lnc-knowledge-base`), mở thư mục đó và lấy folder ID từ URL:

```
https://drive.google.com/drive/folders/1abMW4Bek-eeJlahUOsvZKJCGG9OAsSdQ
                                        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
                                        Đây là folder ID
```

---

## 3. Cấu hình GitHub Secrets

Vào **repo crawl → Settings → Secrets and variables → Actions → New repository secret**.

| Secret name | Giá trị | Bắt buộc |
|---|---|---|
| `GDRIVE_REFRESH_TOKEN` | Refresh token lấy ở bước 2.2 | ✓ |
| `KB_REPO` | Tên repo KB, ví dụ `your-org/lnc-knowledge-base` | ✓ |
| `KB_REPO_TOKEN` | PAT có scope `repo` để push vào KB repo | ✓ |

### Tạo KB_REPO_TOKEN

1. GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
2. Generate new token → chọn scope **`repo`**
3. Copy token, lưu vào secret `KB_REPO_TOKEN`

### Lưu GDRIVE_REFRESH_TOKEN qua CLI

```bash
gh secret set GDRIVE_REFRESH_TOKEN --body "1//0gXxx..."
```

> **Lưu ý:** Dùng `--body` thay vì pipe (`echo ... | gh secret set`) để tránh lỗi BOM trên Windows.

---

## 4. Cấu trúc repo

```
crawl_LNC_team/
├── crawl.py                    # Entry point, đọc sources.json
├── config/
│   └── sources.json            # Khai báo tất cả sources (URL, selector, frequency)
├── crawlers/
│   ├── base_crawler.py
│   ├── aaip_crawler.py
│   ├── bcpnp_crawler.py
│   └── ircc_crawler.py
├── scripts/
│   ├── build_rclone_conf.py    # Tạo config rclone + chạy Drive sync
│   └── validate_quarterly.py
├── .github/workflows/
│   ├── crawl_quarterly.yml
│   ├── crawl_monthly.yml
│   ├── crawl_annual.yml
│   └── crawl_weekly.yml
└── output/
    └── lnc-knowledge-base/     # KB repo checkout vào đây (gitignored)
```

---

## 5. Script build_rclone_conf.py

Script này làm hai việc trong mỗi workflow run:

1. **Ghi `/tmp/rclone.conf`** với refresh token từ secret
2. **Chạy `rclone sync`** luôn trong Python (không phụ thuộc vào shell pipeline)

### Tại sao cần dummy access_token?

rclone v1.74+ có pre-check: nếu `access_token == ""`, nó báo lỗi _"no refresh token"_ trước khi thử refresh. Fix: đặt `access_token = "dummy_expired_token"` để rclone đi vào đúng luồng OAuth2 refresh.

```python
token = json.dumps({
    "access_token": "dummy_expired_token",  # phải khác ""
    "token_type":   "Bearer",
    "refresh_token": rt,                    # từ GDRIVE_REFRESH_TOKEN
    "expiry":        "2020-01-01T00:00:00Z" # đã hết hạn → ép refresh
})
```

### Tại sao sync trong Python thay vì shell?

Một số workflow có debug flags (`--log-level DEBUG | head -30`) cắt output sau 30 dòng, khiến rclone bị SIGPIPE và dừng upload giữa chừng. Chạy sync trong Python script đảm bảo upload hoàn tất trước khi bất kỳ shell command nào can thiệp.

---

## 6. Workflows và lịch chạy

| Workflow | Lịch (UTC) | Dữ liệu crawl |
|---|---|---|
| `crawl_quarterly.yml` | Ngày 1 tháng 1, 4, 7, 10 — 03:00 | AAIP + BCPNP program core, communities, IRCC processing times |
| `crawl_monthly.yml` | Ngày 1 hàng tháng — 02:00 | Draw history (AAIP, BCPNP) |
| `crawl_weekly.yml` | Thứ 2 hàng tuần — 02:00 | BCPNP invitations |
| `crawl_annual.yml` | 15 tháng 1 — 04:00 | Language tests, ECA, legal references |

### Luồng xử lý trong mỗi workflow

```
1. Checkout crawler repo
2. Checkout KB repo → output/lnc-knowledge-base/
3. pip install -r requirements.txt
4. playwright install chromium
5. python crawl.py --frequency <quarterly|monthly|weekly|annual>
6. [quarterly only] python scripts/validate_quarterly.py
7. python scripts/build_rclone_conf.py   ← ghi config + sync Drive
8. git commit + push về KB repo
```

Bước 7 có `continue-on-error: true` — nếu Drive sync lỗi, bước 8 vẫn chạy.

### Chạy thủ công

Vào **GitHub → Actions → chọn workflow → Run workflow** (nút bên phải).

---

## 7. Kiểm tra kết quả

### Actions log

```
GitHub → thtv231/crawl_LNC_team → Actions → chọn run
```

- Step **"Run ... crawl"**: xem từng source pass/fail
- Step **"Upload to Google Drive"**: tìm dòng `Drive sync complete`

### KB repo commits

Mỗi lần crawl tạo commit:

```
chore: quarterly crawl Q2-2026 — program core update
chore: monthly crawl 2026-06 — draw history update
chore: annual crawl 2026 — language tests, ECA update
```

### Drive folder

Mở thư mục Drive đích, kiểm tra `Date modified` của các file. File được cập nhật = crawl và sync thành công.

Cấu trúc thư mục Drive sau khi sync:

```
lnc-knowledge-base/
├── 01_program_core/
│   ├── aaip/         (eligibility.md, how_to_apply.md, points_grid.md, ...)
│   └── bcpnp/
├── 02_documents_compliance/
├── 03_province_community/
├── 04_forms_guides/
├── 05_policies_rules/
└── 06_statistics/
    ├── aaip/         (draw_history_2026.json)
    ├── bcpnp/
    └── ircc/
```

---

## 8. Xử lý sự cố

### "token expired and there's no refresh token"

**Nguyên nhân:** `access_token` trong rclone config là chuỗi rỗng.

**Fix:** Kiểm tra `scripts/build_rclone_conf.py` — phải có `"access_token": "dummy_expired_token"`.

---

### Drive upload step fail, KB vẫn commit

Đúng thiết kế (`continue-on-error: true`). Xem log step "Upload to Google Drive" để tìm nguyên nhân, thường là:
- Refresh token hết hạn → chạy lại `rclone authorize "drive"` và cập nhật secret
- Drive folder ID sai → kiểm tra tên remote trong rclone config (`gdrive:lnc-knowledge-base`)

---

### Lỗi khi push .github/workflows/ files

```
refusing to allow an OAuth App to create or update workflow without `workflow` scope
```

**Fix:** Chạy lệnh sau trong terminal, hoàn tất xác thực qua browser:

```bash
gh auth refresh --scopes workflow
```

> Lệnh này cần chạy trong **terminal thông thường**, không phải trong Claude Code.

---

### Duplicate folder trong Drive

rclone báo `NOTICE: Duplicate directory found — ignoring`.

**Fix:** Vào Drive, xóa thủ công thư mục cũ (thư mục owned by service account cũ).

---

### git push timeout khi chạy local

Vấn đề network. Giải pháp thay thế: dùng GitHub Contents API để push file đơn lẻ (non-workflow), hoặc để workflow trên GitHub Actions tự commit.
