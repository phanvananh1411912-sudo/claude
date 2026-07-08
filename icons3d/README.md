# icons3d/ — bộ icon 3D (PNG) cho thành phần NGHĨA

Thả file PNG (nền trong suốt, khuyến nghị ≥128×128) vào thư mục này. Tên file khớp
với giá trị tương ứng trong `RAD_ICON3D` (`data.mjs`) — mỗi bộ thủ/thành phần trỏ tới
một stem riêng (không có đuôi `.png`). Quy ước hiện dùng cho ảnh tải từ Fluent Emoji 3D
(microsoft/fluentui-emoji): `<mã_unicode_emoji>_<chữ_Hán>.png`, ví dụ 水→`1f4a7_水.png`.
Một số bộ cũ hơn còn dùng tên pinyin bỏ dấu (`ren.png`, `nu.png`...) — các file này hiện
chưa có ảnh thật, sẽ tự rơi về icon SVG/emoji khi thiếu.

App probe `1f4a7_水.png` khi khởi động: tải được → mặc định chế độ **3D**; không có →
chế độ **Nét** (icon SVG). Ảnh nào thiếu sẽ tự rơi về icon SVG/emoji của bộ đó, không vỡ
giao diện.

Ví dụ tên file: 水→`1f4a7_水.png` · 火→`1f525_火.png` · 木→`1f333_木.png`
