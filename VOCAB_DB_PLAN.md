# Đánh giá dữ liệu & Thiết kế Database — Phần mềm từ vựng tiếng Anh

Tài liệu này đánh giá file `tuloaigoptoanbo5.xlsx` và đề xuất thiết kế database + kế hoạch xây dựng phần mềm truy xuất / nhập liệu từ vựng.

---

## 1. Hiện trạng dữ liệu

File gồm **13 sheet**, tổng cộng khoảng **8.300 mục từ**:

| Sheet | Nội dung | Số mục | Số cột | Ghi chú cấu trúc |
|---|---|---|---|---|
| 1. Trạng từ | Adverb | 727 | 8 | 2 bảng con: thống kê theo loại (R2–R10) + danh sách từ (từ R13) |
| 2. Tính từ | Adjective | 2.043 | 23 | 1 bảng, giàu thuộc tính nhất (so sánh hơn/nhất, gradable, vị trí, collocation…) |
| 3. Liên từ | Conjunction | 77 | 13 | 4 bảng con theo loại liên từ, header lặp lại |
| 4. Giới từ | Preposition | 61 | 15 | 3 bảng con, header lặp lại |
| 5. Từ hạn định | Determiner | 146 | 12 | 5 bảng con: 3 bảng từ + bảng nguyên tắc + bảng lượng từ (quantifier + danh từ đi kèm) |
| 6. Động từ | Verb | 1.963 + 348 | 16 / 6 | 2 bảng con **khác hẳn cột**: động từ thường (R3–R1965) + phrasal verb (từ R1966: động từ gốc, tiểu từ, nghĩa, tách được/không) |
| 7. Trợ động từ | Auxiliary | 18 | 11 | 1 bảng |
| 8. Tiểu từ | Particle | 11 | 9 | 1 bảng |
| 9. Thán từ | Interjection | 17 | 10 | 1 bảng |
| 10. Danh từ | Noun | 2.785 | 16 | 1 bảng, giàu collocation (Verb+N, Adj+N, N+Prep…) |
| 11. Collocation | Cụm từ | 77 | 5 | Có cột "Bài học (nguồn)" |
| 12. Idiom | Thành ngữ | 33 | 5 | Có cột "Bài học (nguồn)" |
| 13. Câu | Câu mẫu | 41 | 4 | Có cột "Bài học" |

### 1.1. Điểm mạnh

- **Dữ liệu rất giàu ngữ nghĩa**: mỗi từ loại có bộ thuộc tính chuyên biệt đúng bản chất ngữ pháp (tính từ có comparative/superlative/gradable/vị trí; danh từ có đếm được/số nhiều bất quy tắc/5 loại collocation; động từ có V2-V3/loại nội-ngoại động từ/phrasal verb).
- **Gắn CEFR (A1–C2) và tần suất** gần như đầy đủ → lọc theo trình độ, sắp theo độ phổ biến rất tốt cho app học từ.
- **Nghĩa tiếng Việt + ví dụ minh họa + lỗi thường gặp + từ dễ nhầm** — đúng chất liệu cho người Việt học tiếng Anh.
- **Có truy vết nguồn** (cột "Nguồn dữ liệu", "Bài học Vus-xx") → giữ được khi chuyển sang DB.

### 1.2. Vấn đề cần xử lý khi chuyển sang database

1. **Schema không đồng nhất**: 13 sheet là 13 bộ cột khác nhau (tính từ 23 cột, danh từ 16, liên từ 13…). Không thể ép về một bảng phẳng duy nhất mà không mất thông tin.
2. **Nhiều bảng con trong một sheet**: sheet Trạng từ, Động từ, Từ hạn định, Liên từ, Giới từ chứa 2–5 bảng với header lặp/lệch cột. Script import phải nhận diện điểm ngắt, không đọc kiểu "một sheet = một bảng".
3. **Nhiều giá trị nhồi trong một ô** dạng text tự do: `"Đồng nghĩa: plus | Gần nghĩa: however | Dễ nhầm: ..."`, collocation liệt kê bằng dấu phẩy, ví dụ nhiều dòng trong một ô. Muốn truy vấn được (tìm từ đồng nghĩa, đếm collocation) phải tách ra bảng quan hệ; nếu chưa cần thì giữ nguyên text và tách dần.
4. **Trùng lặp giữa các sheet**: `be`, `have`, `do` vừa ở sheet Động từ vừa ở Trợ động từ; `up`, `down` vừa ở Tiểu từ vừa dính trong phrasal verb. Đây không phải lỗi — một từ có nhiều từ loại — nhưng buộc thiết kế phải tách **từ (word)** khỏi **mục từ theo từ loại (entry/sense)**.
5. **Thiếu không đều**: danh từ/tính từ/động từ không có cột IPA; danh sách trạng từ không có cột nghĩa tiếng Việt riêng (chỉ có "nghĩa của gốc từ"); một số ô CEFR/tần suất trống.
6. **Nghi vấn chất lượng nhỏ**: phân bố CEFR của danh từ có C2 = 556 (bất thường so với B2 = 282, cần rà lại); sheet Động từ có vài dòng đánh số trùng do gộp batch (`go off (2)`).

**Kết luận đánh giá**: dữ liệu đủ tốt và đủ giàu để làm phần mềm tra cứu nghiêm túc, nhưng **bắt buộc phải qua bước ETL chuẩn hóa** (tách bảng con, tách ô đa trị, hợp nhất từ trùng) chứ không import thẳng.

---

## 2. Thiết kế database đề xuất

### 2.1. Nguyên tắc

- **Chuẩn hóa phần lõi, linh hoạt phần đuôi**: các trường chung (từ, IPA, CEFR, tần suất, nghĩa, ví dụ, quan hệ từ) chuẩn hóa thành bảng; các thuộc tính đặc thù theo từ loại để trong **bảng phụ theo POS** (3 loại lớn) hoặc **cột JSON** (các loại nhỏ) — tránh một bảng 40 cột toàn NULL.
- **Word ≠ Entry**: một `word` (chuỗi ký tự) có nhiều `entry` (một entry = từ đó ở một từ loại). Giải quyết triệt để chuyện `be` xuất hiện 2 sheet.
- **Giữ nguyên bản gốc**: mọi ô gốc lưu lại (cột `raw_json` hoặc bảng staging) để đối chiếu, không sợ ETL làm mất dữ liệu.

### 2.2. Sơ đồ bảng (SQLite)

```sql
-- Từ (dạng chữ) — duy nhất theo headword
CREATE TABLE words (
  id        INTEGER PRIMARY KEY,
  headword  TEXT NOT NULL UNIQUE COLLATE NOCASE,  -- "be", "get up", "a double-edged sword"
  ipa       TEXT,
  frequency INTEGER                                -- tần suất (nếu có)
);

-- Từ loại (lookup): noun, verb, adjective, adverb, conjunction, preposition,
-- determiner, auxiliary, particle, interjection, phrasal_verb, collocation, idiom
CREATE TABLE pos (
  id   INTEGER PRIMARY KEY,
  code TEXT NOT NULL UNIQUE,
  name_vi TEXT NOT NULL
);

-- Mục từ = 1 từ ở 1 từ loại (đơn vị tra cứu chính)
CREATE TABLE entries (
  id             INTEGER PRIMARY KEY,
  word_id        INTEGER NOT NULL REFERENCES words(id),
  pos_id         INTEGER NOT NULL REFERENCES pos(id),
  meaning_vi     TEXT,            -- nghĩa tiếng Việt
  meaning_en     TEXT,            -- nghĩa tiếng Anh (Cambridge) nếu có
  cefr           TEXT CHECK (cefr IN ('A1','A2','B1','B2','C1','C2') OR cefr IS NULL),
  semantic_group TEXT,            -- "Nhóm ngữ nghĩa" / "Loại trạng từ" / "Noun Type"...
  register       TEXT,            -- trang trọng / thân mật / trung tính
  usage_notes    TEXT,            -- ghi chú, quy tắc, lỗi thường gặp (gộp text tự do)
  source         TEXT,            -- "Batch goc (750 tu)", "Vus-12"...
  attrs          TEXT,            -- JSON: thuộc tính đặc thù POS chưa tách bảng
  raw_json       TEXT,            -- nguyên trạng dòng Excel gốc (đối chiếu/khôi phục)
  created_at     TEXT DEFAULT (datetime('now')),
  updated_at     TEXT DEFAULT (datetime('now')),
  UNIQUE (word_id, pos_id)
);

-- Ví dụ minh họa (tách khỏi ô đa dòng)
CREATE TABLE examples (
  id        INTEGER PRIMARY KEY,
  entry_id  INTEGER NOT NULL REFERENCES entries(id) ON DELETE CASCADE,
  text_en   TEXT NOT NULL,
  text_vi   TEXT,
  note      TEXT                  -- vd: "sau to be", "ĐÚNG/SAI"
);

-- Quan hệ giữa từ: đồng nghĩa, gần nghĩa, trái nghĩa, dễ nhầm, từ phái sinh
CREATE TABLE relations (
  id            INTEGER PRIMARY KEY,
  entry_id      INTEGER NOT NULL REFERENCES entries(id) ON DELETE CASCADE,
  rel_type      TEXT NOT NULL,    -- synonym | near_synonym | antonym | confusable | derived
  target_entry  INTEGER REFERENCES entries(id),  -- nếu từ đích có trong DB
  target_text   TEXT,             -- nếu chưa có, giữ dạng chữ + ghi chú sắc thái
  note          TEXT
);

-- Collocation / cụm cố định (dùng chung cho sheet 11 và các cột collocation)
CREATE TABLE collocations (
  id         INTEGER PRIMARY KEY,
  entry_id   INTEGER REFERENCES entries(id) ON DELETE CASCADE,
  pattern    TEXT,                -- verb+noun | adj+noun | noun+prep | fixed | idiom...
  phrase     TEXT NOT NULL,
  meaning_vi TEXT,
  meaning_en TEXT,
  example    TEXT,
  source     TEXT                 -- "Vus-03"
);

-- Thuộc tính riêng: 3 từ loại lớn có bảng riêng (truy vấn/nhập liệu có cấu trúc)
CREATE TABLE noun_attrs (
  entry_id         INTEGER PRIMARY KEY REFERENCES entries(id) ON DELETE CASCADE,
  countability     TEXT,          -- countable | uncountable | both
  plural_form      TEXT,          -- số nhiều bất quy tắc
  noun_type        TEXT
);
CREATE TABLE verb_attrs (
  entry_id       INTEGER PRIMARY KEY REFERENCES entries(id) ON DELETE CASCADE,
  verb_type      TEXT,            -- Vt / Vi / linking...
  past_simple    TEXT,            -- V2
  past_participle TEXT,           -- V3
  third_person   TEXT             -- V-s/es bất quy tắc
);
CREATE TABLE adjective_attrs (
  entry_id      INTEGER PRIMARY KEY REFERENCES entries(id) ON DELETE CASCADE,
  comparative   TEXT,
  superlative   TEXT,
  gradable      TEXT,             -- gradable | non-gradable | n/a
  attributive   INTEGER,          -- 0/1
  predicative   INTEGER,
  object_complement INTEGER,
  position_notes TEXT,
  related_adverb TEXT,
  related_noun   TEXT,
  related_verb   TEXT
);

-- Phrasal verb (bảng con thứ 2 của sheet Động từ)
CREATE TABLE phrasal_verbs (
  entry_id     INTEGER PRIMARY KEY REFERENCES entries(id) ON DELETE CASCADE,
  base_verb_id INTEGER REFERENCES entries(id),   -- trỏ về entry "get", "go"...
  particle     TEXT NOT NULL,                    -- "up", "away with"
  separable    TEXT                              -- tách được / không / cả hai
);

-- Câu mẫu theo bài học (sheet 13)
CREATE TABLE sentences (
  id            INTEGER PRIMARY KEY,
  text_en       TEXT NOT NULL,
  sentence_type TEXT,             -- Trần thuật, Nghi vấn...
  meaning_vi    TEXT,
  source        TEXT              -- "Vus-12"
);

-- Tìm kiếm toàn văn (tra theo từ, nghĩa Việt, ví dụ)
CREATE VIRTUAL TABLE search_index USING fts5(
  headword, meaning_vi, meaning_en, examples,
  content=''                      -- external-content, đồng bộ bằng trigger
);
```

Các từ loại nhỏ (liên từ, giới từ, từ hạn định, trợ động từ, tiểu từ, thán từ) **không cần bảng attrs riêng** — thuộc tính đặc thù của chúng (`Cấu trúc & vị trí`, `Dạng phủ định/rút gọn`, `Verb+Prep`…) để trong cột JSON `entries.attrs`. Khi nào cần truy vấn có cấu trúc mới tách bảng — SQLite JSON1 vẫn query được (`json_extract`).

### 2.3. Vì sao chọn SQLite

- Một file `.db` duy nhất — dễ sao lưu, dễ copy giữa máy, không cần cài server.
- FTS5 cho tìm kiếm toàn văn tiếng Anh + tiếng Việt tốt.
- Đủ nhanh cho 10k–100k mục từ, dùng được từ mọi ngôn ngữ (Python, Node, thậm chí chạy trong trình duyệt qua sql.js/wa-sqlite nếu muốn app thuần client như repo hiện tại).
- Nếu sau này cần nhiều người nhập liệu đồng thời qua mạng → nâng lên PostgreSQL, schema giữ nguyên gần như 100%.

---

## 3. Kế hoạch triển khai (5 giai đoạn)

### Giai đoạn 1 — ETL: Excel → staging (ước lượng: 1–2 buổi)
- Script Python (`openpyxl`) đọc 13 sheet, **nhận diện bảng con** theo header đã khảo sát (Adverb từ R13; Verb tách 2 bảng tại R1966; Determiner 5 section; Conjunction/Preposition gộp các section, lấy loại từ header section).
- Đổ nguyên trạng vào bảng staging + sinh **báo cáo chất lượng**: ô trống, CEFR bất thường (nhóm C2 danh từ), trùng lặp, dòng lệch cột.
- Đầu ra: `staging.db` + `data_quality_report.md` để bạn rà và quyết những ca mờ.

### Giai đoạn 2 — Chuẩn hóa & import chính thức (1–2 buổi)
- Tạo schema mục 2.2, hợp nhất từ trùng (be/have/do/up/down) thành 1 word – n entries.
- Tách ví dụ đa dòng thành bảng `examples`; tách phrasal verb, nối `base_verb_id`.
- Quan hệ đồng nghĩa/dễ nhầm: đợt đầu giữ nguyên text trong `relations.target_text`; nối `target_entry` dần bằng script khớp tự động + duyệt tay.
- Kiểm chứng bằng đối chiếu số lượng: tổng entries ≈ 8.300, mỗi sheet khớp số dòng đã đếm.

### Giai đoạn 3 — App tra cứu (MVP) (2–4 buổi)
- **Tra cứu**: ô tìm kiếm (FTS: gõ từ Anh hoặc nghĩa Việt), bộ lọc từ loại + CEFR + nhóm ngữ nghĩa, sắp theo tần suất.
- **Trang chi tiết từ**: nghĩa, IPA, ví dụ, bảng thuộc tính theo từ loại, collocation, từ đồng nghĩa/dễ nhầm (click sang từ liên quan), phrasal verb của động từ gốc.
- Hình thức đề xuất: web app chạy local (Python FastAPI + trang HTML, hoặc thuần client bằng sql.js theo phong cách repo hiện tại). Chọn theo việc bạn muốn nhập liệu nhiều người hay một người.

### Giai đoạn 4 — Nhập liệu (2–3 buổi)
- Form thêm/sửa theo từ loại: chọn POS → hiện đúng bộ trường của POS đó (mirror bảng attrs).
- Validation: trùng từ+POS thì cảnh báo và mở bản ghi cũ; CEFR bắt buộc chọn từ 6 giá trị; ví dụ ≥ 1.
- Nhập nhanh collocation/idiom kèm nguồn bài học; nút export ngược ra Excel/CSV để giữ thói quen làm việc cũ.
- Lịch sử sửa đổi đơn giản (bảng `audit_log`) để không mất dữ liệu khi sửa nhầm.

### Giai đoạn 5 — Mở rộng (tùy chọn, sau khi dùng thật)
- Flashcard/ôn tập ngắt quãng (SRS) lọc theo CEFR + tần suất.
- Thống kê tiến độ kho từ (dashboard theo từ loại/CEFR — như bảng thống kê sheet Adverb, nhưng tự động).
- Import file Excel đợt mới (bạn đang gộp theo batch "Vus-xx" — làm luồng import lặp lại được).
- Âm thanh phát âm (TTS) từ IPA/headword.

---

## 4. Quyết định cần bạn xác nhận trước khi code

1. **Hình thức app**: web local một người dùng (đơn giản nhất) hay có server để nhiều người cùng nhập liệu?
2. **Nhóm CEFR "C2 = 556" ở sheet Danh từ**: rà lại xem có phải mã hóa khác (ví dụ "chưa phân loại") không.
3. Ô đa trị (đồng nghĩa, collocation liệt kê): đợt đầu **giữ nguyên text** hiển thị đẹp, tách dần thành quan hệ có cấu trúc — hay muốn tách triệt để ngay từ đầu (tốn công duyệt tay hơn)?
