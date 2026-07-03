# Ghép Bộ Thủ Chữ Hán · 汉字部首组合器

Phần mềm web giúp **ghép các bộ thủ (部首) thành một chữ Hán**. Chạy trực tiếp trên trình duyệt, không cần cài đặt, không cần internet.

Ứng dụng web giúp ghép bộ thủ tiếng Hán — chỉ một file HTML.

## Cách dùng

Mở file `index.html` bằng bất kỳ trình duyệt nào (Chrome, Edge, Firefox, Safari…).

1. **Chọn bộ thủ** từ bảng 214 bộ thủ Khang Hy bên trái (đã nhóm theo số nét), hoặc **gõ thành phần bất kỳ** vào ô nhập (ví dụ `青`, `每`, `可`).
2. Xem hai kết quả bên phải:
   - **🔎 Chữ có thật** — tra trong cơ sở dữ liệu chữ ghép thông dụng. Ví dụ: `女 + 子 → 好`, `日 + 月 → 明`, `木 + 木 + 木 → 森`. Hiển thị kèm pinyin, âm Hán-Việt và nghĩa tiếng Việt.
   - **🖌️ Ghép hình minh hoạ** — dùng toán tử cấu trúc IDS (⿰ ⿱ ⿲ …) để xếp các bộ thủ thành hình, kể cả khi chữ không tồn tại. Kèm chuỗi mô tả IDS.
3. Đổi **cấu trúc ghép** (trái–phải, trên–dưới, bao quanh…) bằng hàng nút toán tử.
4. Bấm vào chữ lớn để **sao chép**.

## Tính năng

- ✅ Đầy đủ **214 bộ thủ Khang Hy** (chữ, biến thể, pinyin, âm Hán-Việt, nghĩa, số nét).
- ✅ **Tìm kiếm** bộ thủ theo chữ, pinyin, Hán-Việt hoặc nghĩa.
- ✅ Cơ sở dữ liệu **hơn 110 chữ ghép** thông dụng, khớp không phụ thuộc thứ tự và tự nhận diện biến thể (亻→人, 氵→水, 艹→艸…).
- ✅ **Ghép hình bằng CSS** theo 12 toán tử cấu trúc IDS.
- ✅ Giao diện **song ngữ Việt – Trung**, sáng/tối tự động.
- ✅ Một file duy nhất, chạy **ngoại tuyến hoàn toàn**.

## Lưu ý

Phần "Ghép hình minh hoạ" chỉ mô phỏng bố cục để dễ hình dung, **không phải** chữ chính thức trong Unicode. Để có chữ thật, hãy dùng phần "Chữ có thật".

Muốn thêm chữ vào cơ sở dữ liệu? Chỉnh mảng `COMBOS` trong `index.html` theo mẫu:
`["好","女子","hǎo","hảo","tốt / thích","⿰"]` → `[chữ, các thành phần, pinyin, Hán-Việt, nghĩa, toán tử]`.
