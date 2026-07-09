# Hệ thống tự động thu thập thông tin di trú

## Luồng xử lý

**1. Danh sách nguồn**
Hệ thống có sẵn 104 website cần theo dõi — web chính phủ Canada, New Zealand, văn phòng luật, báo di trú...

**2. Tự động vào web đọc**
Robot tự mở từng trang web, đọc nội dung như người dùng bình thường.

**3. Cắt lấy phần cần thiết**
Chỉ lấy đúng phần thông tin quan trọng, bỏ menu / quảng cáo / footer.

**4. Lưu thành file**
Nội dung được lưu thành file văn bản có nhãn rõ ràng — nguồn từ đâu, ngày cập nhật, thuộc chương trình nào.

**5. Kiểm tra chất lượng**
Tự động kiểm tra file có đủ thông tin không. Nếu thiếu thì đánh dấu lỗi.

**6. Đẩy lên Google Drive**
Toàn bộ file được đồng bộ lên Drive để team có thể truy cập.

**7. Lưu lịch sử**
Mọi thay đổi được lưu lại trên GitHub để biết thông tin nào thay đổi vào ngày nào.

---

> Toàn bộ quy trình chạy **tự động theo lịch** — hàng ngày, hàng tháng, hoặc hàng quý — không cần ai thao tác thủ công.
