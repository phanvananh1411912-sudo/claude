# Đặc tả yêu cầu — App tra cứu & nhập liệu từ vựng tiếng Anh (local, 1 người dùng)

Tài liệu này là đặc tả đầy đủ để xây dựng phần mềm. Database đã có sẵn tại
`vocab/vocab.db` (SQLite, ~17 MB, dựng từ Excel bằng `vocab/build_db.py`).
**Không cần import lại dữ liệu — chỉ xây app đọc/ghi database này.**

---

## 1. Bối cảnh & mục tiêu

- Người dùng: **một người**, dùng trên máy cá nhân, **không cần đăng nhập, không cần internet**.
- Hai nhóm chức năng chính:
  1. **Tra cứu**: tìm từ theo tiếng Anh hoặc nghĩa tiếng Việt, lọc theo từ loại/CEFR, xem trang chi tiết đầy đủ.
  2. **Nhập liệu**: thêm/sửa mục từ với form động theo từ loại, kèm ví dụ, quan hệ từ, collocation.
- Dữ liệu hiện có: **8.134 mục từ** (2.785 danh từ, 2.043 tính từ, 1.962 động từ, 727 trạng từ, 348 phrasal verb, còn lại là liên từ/giới từ/từ hạn định/trợ động từ/tiểu từ/thán từ/thành ngữ), 22.987 collocation, 11.817 quan hệ từ, 4.557 ví dụ, 41 câu mẫu, 15 ghi chú ngữ pháp.

## 2. Công nghệ bắt buộc/khuyến nghị

- **Backend**: Python 3 + FastAPI (hoặc Flask) + sqlite3 chuẩn (không cần ORM). Server chạy local, một lệnh khởi động duy nhất, ví dụ: `python app.py` rồi mở `http://localhost:8000`.
- **Frontend**: HTML + vanilla JavaScript + CSS, không framework build (không React/webpack). Giao diện tiếng Việt, responsive cơ bản, hỗ trợ UTF-8 (tiếng Việt + ký hiệu IPA).
- **Không được**: yêu cầu internet lúc chạy (mọi font/thư viện phải bundle local hoặc dùng system font), không dùng database khác ngoài file `vocab.db` hiện có.
- Cấu trúc thư mục đề xuất: `vocab/app.py` (server) + `vocab/static/` (html/css/js). Không sửa `build_db.py`.

## 3. Schema database hiện có (KHÔNG được đổi cấu trúc bảng sẵn có)

```sql
words (id, headword UNIQUE COLLATE NOCASE, ipa, frequency)
pos   (id, code UNIQUE, name_vi)
      -- 12 mã: noun, verb, adjective, adverb, conjunction, preposition,
      --        determiner, auxiliary, particle, interjection, phrasal_verb, idiom
entries (id, word_id→words, pos_id→pos, meaning_vi, meaning_en,
         cefr CHECK IN ('A1'..'C2') OR NULL, semantic_group, register,
         usage_notes, source, attrs /*JSON, thuộc tính đặc thù POS*/,
         raw_json /*dòng Excel gốc, chỉ đọc*/, created_at, updated_at,
         UNIQUE(word_id, pos_id))
examples  (id, entry_id→entries CASCADE, text_en, text_vi, note)
          -- note có thể là 'ví dụ đúng' | 'lỗi thường gặp (SAI)' | NULL
relations (id, entry_id→entries CASCADE, rel_type, target_entry→entries NULL,
           target_text, note)
          -- rel_type: synonym | near_synonym | antonym | confusable | derived | related
          -- target_entry NULL nghĩa là từ đích chưa có trong DB (chỉ có target_text)
collocations (id, entry_id→entries NULL /*NULL = collocation độc lập*/, pattern,
              phrase, meaning_vi, meaning_en, example, source)
          -- pattern: verb+noun, adj+noun, noun+prep, quantifier+noun, fixed,
          --          collocation, verb collocation/idiom, phrasal verb tiêu biểu...
noun_attrs      (entry_id PK→entries, countability /*countable|uncountable|both*/,
                 plural_form, noun_type, grammar_note)
verb_attrs      (entry_id PK→entries, verb_type, past_simple, past_participle, third_person)
adjective_attrs (entry_id PK→entries, comparative, superlative, comparison_note,
                 gradable, degree_adverbs, attributive 0/1, predicative 0/1,
                 object_complement 0/1, position_meaning_changes 0/1, position_note)
phrasal_verbs   (entry_id PK→entries, base_verb_id→entries NULL, base_verb, particle, separable)
sentences       (id, text_en, sentence_type, meaning_vi, source)
grammar_notes   (id, topic /*adverb_position|determiner_rules*/, title, content, example, source)
search_index    -- FTS5(headword, meaning_vi, meaning_en, example_text, entry_id UNINDEXED)
```

**Được phép thêm bảng mới** (vd `audit_log`, `settings`) nhưng không xóa/đổi cột bảng cũ.

### Lưu ý quan trọng về `search_index` (FTS5)

`search_index` là bảng FTS5 độc lập, mỗi entry một dòng, cột `entry_id` UNINDEXED.
**Mọi thao tác ghi entry/example phải đồng bộ lại FTS**: xóa dòng cũ theo
`entry_id` rồi insert lại (headword, meaning_vi, meaning_en, example_text =
group_concat các text_en của entry đó). Có thể làm bằng trigger hoặc trong code.

### Lưu ý về `attrs` (JSON)

Các từ loại nhỏ lưu thuộc tính đặc thù trong `entries.attrs` dạng JSON object
`{"tên cột gốc tiếng Việt": "giá trị"}`, ví dụ liên từ có khóa
`"Cấu trúc & vị trí trong câu"`, `"Nhóm hoán đổi được (đồng chức năng)"`.
Trang chi tiết chỉ cần hiển thị các cặp key–value này dạng bảng; form nhập liệu
cho phép sửa value theo key có sẵn và thêm cặp mới.

## 4. Chức năng chi tiết

### 4.1. Trang tra cứu (trang chủ)

- **Ô tìm kiếm** duy nhất, tìm ngay khi gõ (debounce ~250ms):
  - Khớp tiền tố tiếng Anh qua FTS (`abundan*` → abundance, abundant…).
  - Khớp nghĩa tiếng Việt (`khả năng` → able, likely, probable…).
  - Ưu tiên sắp xếp: khớp chính xác headword > khớp tiền tố headword > khớp nghĩa/ví dụ; cùng hạng thì theo `words.frequency` giảm dần (NULL xuống cuối).
- **Bộ lọc** (kết hợp được với tìm kiếm): từ loại (multi-select theo bảng `pos`), CEFR (A1–C2 + "chưa có"), nhóm ngữ nghĩa (`semantic_group`, load động theo từ loại đã chọn).
- **Kết quả** dạng danh sách phân trang (50 dòng/trang): headword, từ loại (badge màu theo POS), CEFR (badge), nghĩa tiếng Việt (cắt ngắn), tần suất. Bấm dòng → trang chi tiết.
- Khi chưa gõ gì: hiện thống kê nhanh (số mục từ theo từ loại, theo CEFR) + nút "Thêm từ mới".

### 4.2. Trang chi tiết mục từ (`/entry/{id}`)

Hiển thị đầy đủ, chia khối:

1. **Đầu trang**: headword + IPA + tần suất + badge từ loại + badge CEFR + register + nhóm ngữ nghĩa. Nếu cùng `word` có entry ở từ loại khác (vd `be` là verb + auxiliary) → hiện tab/link chuyển qua lại.
2. **Nghĩa**: meaning_vi, meaning_en, usage_notes (giữ xuống dòng), source.
3. **Thuộc tính ngữ pháp** theo từ loại:
   - noun: đếm được/không, dạng số nhiều, loại danh từ, ghi chú ngữ pháp.
   - verb: loại động từ, V2, V3, dạng -s/es bất quy tắc.
   - adjective: comparative/superlative, gradable, degree adverbs, vị trí (attributive/predicative/object complement — hiện dạng ✓/✗), ghi chú vị trí.
   - phrasal_verb: động từ gốc (link sang entry gốc nếu `base_verb_id` có), particle, tách được/không.
   - Từ loại khác: bảng key–value từ `attrs` JSON.
4. **Ví dụ**: danh sách `examples`; ví dụ có note `lỗi thường gặp (SAI)` hiển thị nền đỏ nhạt kèm nhãn, `ví dụ đúng` nền xanh nhạt.
5. **Collocation**: nhóm theo `pattern`, mỗi dòng: phrase (+ meaning_vi nếu có, + example nếu có).
6. **Quan hệ từ**: nhóm theo `rel_type` (tên tiếng Việt: Đồng nghĩa, Gần nghĩa, Trái nghĩa, Dễ nhầm, Từ phái sinh, Liên quan). Mục có `target_entry` → render link bấm được sang entry đó; chỉ có `target_text` → chữ thường kèm note; chỉ có `note` (giải thích dài) → hiện nguyên đoạn.
7. **Với động từ**: khối "Phrasal verb của từ này" — query `phrasal_verbs.base_verb_id = entry.id`, mỗi dòng link sang entry phrasal verb.
8. Nút **Sửa** → form nhập liệu (4.3), nút **Xóa** (confirm 2 bước, xóa cascade examples/relations/collocations/attrs + dòng FTS).

### 4.3. Form thêm/sửa mục từ (`/edit/{id}`, `/new`)

- **Bước 1**: nhập headword + chọn từ loại. Ngay khi rời ô (blur), kiểm tra:
  - Trùng `(word, pos)` → cảnh báo đỏ + link mở entry có sẵn, chặn lưu.
  - Cùng word đã có ở POS khác → gợi ý vàng "từ này đã có ở từ loại X" (vẫn cho lưu — đó là mục hợp lệ).
- **Trường chung**: IPA, tần suất, nghĩa VI, nghĩa EN, CEFR (dropdown 6 giá trị + trống), nhóm ngữ nghĩa (autocomplete từ giá trị có sẵn của POS đó), register, usage_notes (textarea), source.
- **Trường theo POS**: chọn từ loại nào thì hiện đúng khối thuộc tính từ loại đó (mirror các bảng `*_attrs` ở mục 4.2.3). Với phrasal_verb: ô base_verb có autocomplete từ danh sách động từ, lưu xong tự nối `base_verb_id`.
- **Ba danh sách con** (thêm/sửa/xóa từng dòng ngay trong form, không cần trang riêng):
  - Ví dụ: text_en, text_vi, note (dropdown: trống / ví dụ đúng / lỗi thường gặp (SAI)).
  - Quan hệ từ: rel_type (dropdown 6 loại), target_text (autocomplete headword có sẵn — chọn từ có sẵn thì lưu luôn `target_entry`), note.
  - Collocation: pattern (autocomplete giá trị có sẵn), phrase, meaning_vi, example.
- **Khi lưu**: transaction duy nhất; cập nhật `entries.updated_at`; đồng bộ `search_index`; ghi `audit_log`.
- **Audit log** (bảng mới): `audit_log(id, ts, action /*create|update|delete*/, entry_id, headword, diff_json)` — diff_json chỉ cần lưu snapshot trước/sau dạng JSON. Có trang `/history` xem 200 thao tác gần nhất.

### 4.4. Trang phụ

- `/collocations`: duyệt + tìm trong 22.987 collocation (lọc theo pattern, tìm theo phrase/nghĩa). Collocation độc lập (entry_id NULL) cũng phải hiện ở đây. Cho thêm/sửa/xóa.
- `/sentences`: bảng 41 câu mẫu (lọc theo loại câu, nguồn), CRUD đơn giản.
- `/grammar`: hiển thị 15 `grammar_notes` nhóm theo topic (vị trí trạng từ, nguyên tắc từ hạn định).
- `/stats`: dashboard — bảng chéo số mục từ theo (từ loại × CEFR), tổng ví dụ/collocation/quan hệ, số mục thiếu nghĩa VI / thiếu CEFR / thiếu IPA (đây là danh sách việc cần bổ sung → mỗi con số bấm vào được, ra danh sách lọc sẵn để sửa dần).
- **Export**: nút xuất CSV cho kết quả tìm kiếm hiện tại (đúng bộ lọc đang áp), UTF-8 BOM để mở được bằng Excel.

### 4.5. An toàn dữ liệu

- Trước mỗi lần server khởi động: tự copy `vocab.db` → `backups/vocab-YYYYMMDD-HHMMSS.db`, giữ tối đa 10 bản gần nhất.
- Mọi thao tác ghi dùng transaction; bật `PRAGMA foreign_keys=ON`.
- Không bao giờ ghi đè cột `raw_json` của dữ liệu import gốc.

## 5. Tiêu chí nghiệm thu (test thủ công sau khi build)

1. Chạy `python app.py`, mở trình duyệt — trang chủ hiện thống kê: tổng 8.134 mục từ.
2. Gõ `khả năng` → kết quả có `able`, `likely`, `probable`. Gõ `abundan` → có `abundance`, `abundant`, `abundantly`.
3. Mở từ `be` → thấy 2 tab: Động từ và Trợ động từ, chuyển qua lại được.
4. Mở `ability` (danh từ) → thấy đếm được, số nhiều `abilities`, đúng 10 collocation nhóm theo pattern.
5. Mở `get up` → link về động từ gốc `get` bấm được; mở `get` → khối phrasal verb liệt kê `get up`, `get on`, `get off`…
6. Mở `but` (liên từ) → ví dụ ĐÚNG nền xanh, ví dụ SAI nền đỏ; quan hệ từ có link sang `and` (trái nghĩa).
7. Thêm từ mới `resilience` (noun, B2, nghĩa "sự kiên cường") với 1 ví dụ + 1 collocation → tìm `kiên cường` ra ngay từ vừa thêm; `/history` ghi nhận thao tác create.
8. Thử thêm lần nữa `resilience` + noun → bị chặn với cảnh báo trùng.
9. Sửa nghĩa một động từ đang thiếu nghĩa VI (vd `be`) → lưu xong tìm được bằng nghĩa mới; `/stats` giảm số "thiếu nghĩa VI" đi 1.
10. Xóa từ test → confirm 2 bước, mất khỏi tìm kiếm, examples/collocations của nó cũng mất (cascade).
11. Tắt mạng internet — toàn bộ app vẫn chạy bình thường.
12. Kiểm tra thư mục `backups/` có file backup sau khi khởi động server.

## 6. Ngoài phạm vi (KHÔNG làm đợt này)

- Đăng nhập/phân quyền, đồng bộ cloud, mobile app.
- Flashcard/SRS, phát âm TTS (để giai đoạn sau).
- Import Excel đợt mới (đã có `build_db.py` riêng).
- Sửa đổi `build_db.py` hoặc chạy lại import (sẽ ghi đè dữ liệu người dùng đã nhập).
