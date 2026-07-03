# Hán Tự Engine · Ghép Bộ Thủ Chữ Hán

Phần mềm web học chữ Hán theo mô hình **component · variant · structure**: phân tích cấu tạo, ghép bộ thủ thành chữ, và tra chữ từ các mảnh. Một file `index.html` duy nhất — mở bằng trình duyệt là chạy, không cài đặt, không cần internet.

Ứng dụng học chữ Hán qua ghép bộ thủ — thiết kế "Hán Tự Engine", chạy hoàn toàn offline.

## Cách dùng

Mở `index.html` bằng bất kỳ trình duyệt nào (Chrome, Edge, Firefox, Safari…). App có **5 chế độ**:

| Chế độ | Mô tả |
|--------|-------|
| **Học chữ** | Cho nghĩa, chọn đúng tất cả thành phần tạo nên chữ → xem khung 田字格, thẻ giải thích và câu ghi nhớ. |
| **Phân tích** | Chọn một chữ, bóc tách thành phần **tạo NGHĨA** (xanh) / **tạo ÂM** (lam); rê chuột để làm nổi từng bộ. |
| **Ghép chữ** | Kéo-thả (hoặc chạm) các mảnh vào đúng ô trong khung để dựng chữ 情 / 清 / 快. Có âm thanh & rung phản hồi. |
| **Sáng tạo** | Chọn ≥ 2 mảnh (kể cả biến thể như 忄, 氵, 扌) → tìm ra các chữ chứa đủ các mảnh đó. |
| **Đố bộ thủ** | Trắc nghiệm: chữ này được tạo nghĩa từ bộ thủ nào? Có tính điểm. |

## Thiết kế & kỹ thuật

- Port từ thiết kế **"Hán Tự Engine"** (bản export Lovable: TanStack Start + React + Tailwind + shadcn) sang **HTML/CSS/JS thuần trong một file**, giữ nguyên bố cục, bảng màu sand/clay/ink + semantic/phonetic, gradient động, khung 田字格 và các tương tác.
- Tầng dữ liệu theo schema gốc: `COMPONENT` (bộ thủ) → `VARIANT` (biến thể theo vị trí) → `CHARACTER` (chữ, gồm các part có vai trò semantic/phonetic + câu ghi nhớ).
- Phản hồi âm thanh (Web Audio) và rung (Vibration API); giao diện sáng/tối tự động; không tải tài nguyên ngoài → chạy offline.

## Mở rộng dữ liệu

Chỉnh trực tiếp trong `index.html`:

- Thêm bộ thủ: `COMPONENT` + màu trong `COMP_COLOR` + (nếu có) biến thể trong `VARIANT` và ánh xạ `NORMALIZE`.
- Thêm chữ: một phần tử trong mảng `CHARACTER` với `parts` gồm `{comp, variant, role, pos}` và `memory` (câu ghi nhớ, cho phép thẻ `<b>`).
