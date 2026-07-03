# Hán Tự Emoji · Tra chữ Hán theo lục thư bằng emoji

Web app học chữ Hán theo pipeline **chữ → loại chữ (lục thư) → phân rã thành phần → công thức emoji**, chạy trên dữ liệu **makemeahanzi** + bảng emoji bộ thủ + **Thuyết Văn Giải Tự (說文解字)**. Một file `index.html` mở là chạy, không cài đặt, không internet.

## Nguyên tắc hiển thị

- **Thành phần NGHĨA** (semantic) → chuỗi ưu tiên **icon 3D (PNG) → icon SVG inline → emoji → chữ**. Icon SVG (lucide/tabler/phosphor/game-icons) nhuộm xanh dương qua `currentColor`; icon 3D hiển thị trong **khung tròn nền xanh nhạt + viền xanh** (ảnh không nhuộm màu được); `seal` tạm là chữ Hán trong khung tròn xanh (chờ SVG tiểu triện GlyphWiki). Kèm nghĩa đen + vai trò khi ghép (Thuyết Văn) và nút mở rộng 說文解字.
- **Toggle "Icon: 3D / Nét"** trên header: mặc định 3D nếu thư mục `icons3d/` có ảnh (probe `icons3d/shui.png`), ngược lại dùng icon SVG. Ảnh thiếu tự rơi về tầng SVG.
- **Thành phần ÂM** (phonetic) → giữ **chữ Hán + pinyin**, viền/nền **đỏ**; nếu thành phần âm có emoji riêng (vd 青→🌿) thì hiện mờ phía sau.
- **Chữ tượng hình / chỉ sự** → **một emoji lớn** + badge loại chữ (🖼 Tượng hình / 💡 Chỉ sự·Hội ý / 🧩 Hình thanh).
- **Công thức**: `[emoji NGHĨA 🔵] + [chữ ÂM 🔴 + pinyin] = chữ`.

## Kiến trúc 4 + 2 màn hình (hash router)

```
#/                    Ngữ Nghĩa Chính  — hero 吃 + cây ngữ nghĩa 3 tầng + mẹo nhớ (dữ liệu kb.mjs)
#/analysis/<chữ>      Phân Tích Chữ    — 3 card thông số + Sơ đồ cấu tạo (BIỂU Ý clay / BIỂU ÂM violet)
                                         + Thuyết văn collapsible + Cây ngữ nghĩa + Họ âm học động
#/graph?mode=&focus=  Đồ Thị Quan Hệ   — SVG tự vẽ: semantic (cùng bộ) / phonetic (cùng âm) / structure (IDS)
#/compound/<id>       Tra Cứu Từ Ghép  — hero 2 glyph + Semantic Bridge 01→02→03 + collocations + lưu ý
#/radicals            Bộ Thủ           — bảo toàn nguyên vẹn màn cũ (84 bộ · Cilin · 4 tầng nghĩa · HSK1)
#/practice            Luyện Tập        — bảo toàn nguyên vẹn 4 game cũ (chỉ đổi tông màu clay/violet)
```

Điều hướng bằng hash — nút back/forward của trình duyệt hoạt động, link chia sẻ được. Sidebar trái dùng chung (tìm chữ/pinyin, nạp dictionary.txt, 84 bộ lối tắt, lọc Cilin, HSK1); cột phải là DetailPanel theo ngữ cảnh.

## Hệ thiết kế

Token trong `:root` (port từ Semantic KB Viewer): nền `#FBF8F1`, thẻ trắng bo `--radius:14px`, **teal** `#0E7C6B` (chủ đạo), **clay** `#C97A3B` (= BIỂU Ý), **violet** `#7C6BD8` (= BIỂU ÂM). Font: Plus Jakarta Sans (heading) · Inter (body) · Noto Serif SC (glyph lớn) qua Google Fonts, offline tự fallback hệ thống.

## 6 chế độ (2 màn kế thừa)

| Chế độ | Mô tả |
|--------|-------|
| **Tra chữ** | Ô tìm kiếm (chữ Hán hoặc pinyin) → thẻ kết quả: công thức emoji, khung 田字格, thẻ thành phần NGHĨA/ÂM kèm Thuyết Văn + badge Cilin, badge lục thư. |
| **Bộ thủ** | Lưới 84 bộ, nhóm/lọc theo 9 đại loại **同义词词林 Cilin** (A Người … I Trạng thái, mỗi loại một màu pastel). Bấm một bộ → Thuyết Văn + danh sách chữ chứa bộ đó, có toggle **Chỉ HSK1**. |
| **Học chữ** | Cho nghĩa → chọn đúng tất cả thành phần → xem công thức + giải thích. |
| **Ghép chữ** | Kéo-thả mảnh vào ô đúng để dựng chữ. Âm thanh & rung phản hồi. |
| **Sáng tạo** | Chọn ≥ 2 mảnh (biến thể tự quy về gốc) → tìm chữ chứa đủ. |
| **Đố bộ thủ** | Trắc nghiệm **5 dạng** (chọn thể loại hoặc trộn): ① chữ → bộ thủ tạo nghĩa · ② chữ → loại lục thư · ③ loại lục thư → tìm chữ (đố ngược) · ④ bộ thủ → ý nghĩa · ⑤ ý nghĩa → bộ thủ (đố ngược). Có tính điểm + giải thích sau mỗi câu. |

## Dữ liệu & resolver

- `index.html` **nhúng sẵn** 3 nguồn: bảng emoji 84 bộ thủ (`radical_emoji_map.json`), Thuyết Văn 84 bộ (`shuowen_radicals_vi.json`), và **26 chữ demo** định dạng makemeahanzi (`sample_dictionary.txt`).
- **Resolver** (logic phân giải thành phần):
  - Biến thể → gốc: `氵→水`, `忄→心`, `灬→火`, `讠→言`…
  - Nhập nhằng theo vị trí/ngữ cảnh: `阝` trái=阜🏔️ / phải=邑🏘️ · `月` nhóm cơ thể=肉🥩 / thường=🌙 · `王` trái=玉💎.
  - Fallback: thành phần không có emoji (`彳`, `冖`…) → hiển thị nguyên chữ trong khung xám, không bỏ trống.
- **Cilin (同义词词林)**: mỗi bộ thủ mang đại loại chính/phụ (`dai_loai`, `dai_loai_phu`, `mien_nghia`) hiển thị thành badge màu pastel, ví dụ 水 → `[B · Sự vật | F · Động tác]`. Script tuỳ chọn `enrich_cilin.py` nhận `cilin.txt` (bản mở rộng HIT) để điền mã trung/tiểu loại đầy đủ vào `ma_chi_tiet` — app chạy bình thường khi chưa có.
- Module test độc lập: **`resolver.mjs`** (logic thuần) + **`resolver_test.mjs`** — chạy `node resolver_test.mjs` (**32/32 pass**). App cũng tự chạy 11 test resolver khi tải (xem góc footer).

## Quy trình build (nguồn sự thật duy nhất)

`index.html` là **file sinh ra** — đừng sửa trực tiếp. Nguồn chuẩn:

| File | Nội dung |
|---|---|
| `template.html` | UI (CSS + markup + code giao diện), chứa placeholder `/*__DATA__*/`, `/*__RESOLVER__*/` |
| `data.mjs` | RAD_RADICALS/VARIANTS/AMBIG, RAD_ICON, RAD_ICON3D, PINYIN_FB, SAMPLE_DICT, CILIN, HSK1 |
| `resolver.mjs` | toàn bộ logic phân giải (resolveComponent, analyzeCharacter, topOperands, pickIconLayer) |
| `kb.mjs` | dữ liệu **biên soạn tay** (CURATED 吃/吃醋, KB_ENTRIES, KB_PINYIN) |
| `screens.mjs` | router + AppShell + 6 màn hình (game giữ nguyên từ bản cũ) |
| `embed/shuowen.mjs`, `embed/icons.mjs` | khối Thuyết Văn 84 bộ và 69 SVG icon |
| `radical_emoji_map.json` | file map gốc (đã đồng bộ 刀→game-icons:bowie-knife, 齒→game-icons:tooth kèm icon_note) |

Sửa xong chạy:

```bash
node build.mjs          # tái sinh index.html
node resolver_test.mjs  # 32/32 pass
```

## Icon 3D (`icons3d/`)

Thả PNG (nền trong suốt, ≥128×128) vào thư mục `icons3d/` theo tên **pinyin bỏ dấu** (bảng đầy đủ: `RAD_ICON3D` trong `data.mjs`; trùng âm thì hậu tố số: 目→`mu2.png`, 石→`shi3.png`…). Ba file có sẵn (`shui/huo/mu.png`) là placeholder sinh tự động — thay bằng bộ clay 3D thật (tự sinh theo `gen_prompts_84.md`) hoặc Fluent Emoji 3D. Xem `icons3d/README.md`.

## Nạp từ điển đầy đủ

App mặc định dùng 26 chữ demo. Để tra **mọi chữ**, tải bản đầy đủ (~10MB) rồi bấm **📄 Nạp dictionary.txt đầy đủ** trong tab *Tra chữ* (đọc tại chỗ bằng trình duyệt, không cần server):

```bash
curl -L -o dictionary.txt https://raw.githubusercontent.com/skishore/makemeahanzi/master/dictionary.txt
```

## Ghi chú

Phần nguyên văn Thuyết Văn ở vài bộ (đánh dấu `*`) được soạn từ tri thức, **cần đối chiếu** với `swjz.xml` (cjkvi-dict) hoặc ctext.org trước khi phát hành chính thức.

Muốn nhúng resolver/data vào app React/TypeScript khác (Semantic KB Viewer…): xem **`INTEGRATION.md`**.
