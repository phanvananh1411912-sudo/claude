# Hán Tự Emoji · Tra chữ Hán theo lục thư bằng emoji

Web app học chữ Hán theo pipeline **chữ → loại chữ (lục thư) → phân rã thành phần → công thức emoji**, chạy trên dữ liệu **makemeahanzi** + bảng emoji bộ thủ + **Thuyết Văn Giải Tự (說文解字)**. Một file `index.html` mở là chạy, không cài đặt, không internet.

## Nguyên tắc hiển thị

- **Thành phần NGHĨA** (semantic) → hiện bằng **emoji**, viền/nền **xanh dương**, kèm nghĩa đen + vai trò khi ghép (Thuyết Văn) và nút mở rộng nguyên văn 說文解字.
- **Thành phần ÂM** (phonetic) → giữ **chữ Hán + pinyin**, viền/nền **đỏ**; nếu thành phần âm có emoji riêng (vd 青→🌿) thì hiện mờ phía sau.
- **Chữ tượng hình / chỉ sự** → **một emoji lớn** + badge loại chữ (🖼 Tượng hình / 💡 Chỉ sự·Hội ý / 🧩 Hình thanh).
- **Công thức**: `[emoji NGHĨA 🔵] + [chữ ÂM 🔴 + pinyin] = chữ`.

## 6 chế độ

| Chế độ | Mô tả |
|--------|-------|
| **Tra chữ** | Ô tìm kiếm (chữ Hán hoặc pinyin) → thẻ kết quả: công thức emoji, khung 田字格, thẻ thành phần NGHĨA/ÂM kèm Thuyết Văn + badge Cilin, badge lục thư. |
| **Bộ thủ** | Lưới 84 bộ, nhóm/lọc theo 9 đại loại **同义词词林 Cilin** (A Người … I Trạng thái, mỗi loại một màu pastel). Bấm một bộ → Thuyết Văn + danh sách chữ chứa bộ đó, có toggle **Chỉ HSK1**. |
| **Học chữ** | Cho nghĩa → chọn đúng tất cả thành phần → xem công thức + giải thích. |
| **Ghép chữ** | Kéo-thả mảnh vào ô đúng để dựng chữ. Âm thanh & rung phản hồi. |
| **Sáng tạo** | Chọn ≥ 2 mảnh (biến thể tự quy về gốc) → tìm chữ chứa đủ. |
| **Đố bộ thủ** | Trắc nghiệm: chữ này được tạo nghĩa từ bộ thủ nào? |

## Dữ liệu & resolver

- `index.html` **nhúng sẵn** 3 nguồn: bảng emoji 84 bộ thủ (`radical_emoji_map.json`), Thuyết Văn 84 bộ (`shuowen_radicals_vi.json`), và **26 chữ demo** định dạng makemeahanzi (`sample_dictionary.txt`).
- **Resolver** (logic phân giải thành phần):
  - Biến thể → gốc: `氵→水`, `忄→心`, `灬→火`, `讠→言`…
  - Nhập nhằng theo vị trí/ngữ cảnh: `阝` trái=阜🏔️ / phải=邑🏘️ · `月` nhóm cơ thể=肉🥩 / thường=🌙 · `王` trái=玉💎.
  - Fallback: thành phần không có emoji (`彳`, `冖`…) → hiển thị nguyên chữ trong khung xám, không bỏ trống.
- **Cilin (同义词词林)**: mỗi bộ thủ mang đại loại chính/phụ (`dai_loai`, `dai_loai_phu`, `mien_nghia`) hiển thị thành badge màu pastel, ví dụ 水 → `[B · Sự vật | F · Động tác]`. Script tuỳ chọn `enrich_cilin.py` nhận `cilin.txt` (bản mở rộng HIT) để điền mã trung/tiểu loại đầy đủ vào `ma_chi_tiet` — app chạy bình thường khi chưa có.
- Module test độc lập: **`resolver.mjs`** (logic thuần) + **`resolver.test.mjs`** — chạy `node resolver.test.mjs` (20/20 pass). App cũng tự chạy 11 test resolver khi tải (xem góc footer).

## Nạp từ điển đầy đủ

App mặc định dùng 26 chữ demo. Để tra **mọi chữ**, tải bản đầy đủ (~10MB) rồi bấm **📄 Nạp dictionary.txt đầy đủ** trong tab *Tra chữ* (đọc tại chỗ bằng trình duyệt, không cần server):

```bash
curl -L -o dictionary.txt https://raw.githubusercontent.com/skishore/makemeahanzi/master/dictionary.txt
```

## Ghi chú

Phần nguyên văn Thuyết Văn ở vài bộ (đánh dấu `*`) được soạn từ tri thức, **cần đối chiếu** với `swjz.xml` (cjkvi-dict) hoặc ctext.org trước khi phát hành chính thức.
