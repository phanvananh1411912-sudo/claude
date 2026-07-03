# icons3d/ — bộ icon 3D (PNG) cho thành phần NGHĨA

Thả file PNG (nền trong suốt, khuyến nghị ≥128×128) vào thư mục này theo quy ước tên
**pinyin bỏ dấu** của bộ thủ; trùng tên thì thêm hậu tố số. Bảng tên đầy đủ nằm ở
`RAD_ICON3D` trong `data.mjs`. Ba file hiện có (`shui.png`, `huo.png`, `mu.png`) chỉ là
**placeholder** sinh tự động — thay bằng ảnh clay 3D thật (theo `gen_prompts_84.md`) hoặc
Fluent Emoji 3D.

App probe `shui.png` khi khởi động: tải được → mặc định chế độ **3D**; không có → chế độ **Nét**
(icon SVG). Ảnh nào thiếu sẽ tự rơi về icon SVG/emoji của bộ đó, không vỡ giao diện.

Ví dụ tên file: 水→`shui.png` · 火→`huo.png` · 木→`mu.png` · 目→`mu2.png` · 示→`shi2.png` · 石→`shi3.png` · 玉→`yu3.png`
