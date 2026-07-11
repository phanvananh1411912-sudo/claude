#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ETL: tuloaigoptoanbo5.xlsx -> vocab.db (SQLite)

Đọc 13 sheet (nhận diện các bảng con trong cùng sheet), chuẩn hóa về schema
words/entries/examples/relations/collocations + bảng thuộc tính theo từ loại,
tách triệt để các ô đa trị (ví dụ, đồng nghĩa/dễ nhầm, collocation),
và sinh báo cáo chất lượng dữ liệu data_quality_report.md.

Chạy:  python3 build_db.py [đường-dẫn-xlsx] [đường-dẫn-db]
"""
import json
import os
import re
import sqlite3
import sys
from collections import Counter, defaultdict

import openpyxl

XLSX = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(__file__), "tuloaigoptoanbo5.xlsx")
DB = sys.argv[2] if len(sys.argv) > 2 else os.path.join(os.path.dirname(__file__), "vocab.db")
REPORT = os.path.join(os.path.dirname(DB), "data_quality_report.md")

CEFR_LEVELS = {"A1", "A2", "B1", "B2", "C1", "C2"}
# Các giá trị coi như ô trống
EMPTY_VALUES = {"", "—", "-", "–", "n/a", "N/A", "không có", "không cần", "không áp dụng"}
EMPTY_PREFIXES = ("không có", "không áp dụng", "không cần", "chưa có")

REL_COL = "Quan hệ với từ khác (Synonyms/Near Synonyms/Antonyms/Confusable)"

report = defaultdict(list)   # section -> list of lines
stats = Counter()


def is_empty(v):
    if v is None:
        return True
    s = str(v).strip()
    if s.lower() in EMPTY_VALUES:
        return True
    return s.lower().startswith(EMPTY_PREFIXES)


def clean(v):
    """Chuỗi đã strip, hoặc None nếu coi như trống."""
    if is_empty(v):
        return None
    return str(v).strip()


def split_outside_parens(text, seps=";,\n"):
    """Tách chuỗi theo dấu phân cách, bỏ qua dấu nằm trong ngoặc ()/[]/“”/\"\"."""
    items, buf, depth = [], [], 0
    in_quote = False
    for ch in text:
        if ch in "([{":
            depth += 1
        elif ch in ")]}":
            depth = max(0, depth - 1)
        elif ch in "\"“”":
            in_quote = not in_quote
        if ch in seps and depth == 0 and not in_quote:
            items.append("".join(buf))
            buf = []
        else:
            buf.append(ch)
    items.append("".join(buf))
    return [i.strip() for i in items if i.strip()]


def split_term_note(item):
    """'plus (thân mật)' -> ('plus', 'thân mật'); không có ngoặc -> (item, None)."""
    m = re.match(r"^(.*?)\s*\(([^()]*)\)\s*$", item)
    if m and m.group(1).strip():
        return m.group(1).strip(), m.group(2).strip()
    return item.strip(), None


REL_LABELS = {
    "đồng nghĩa": "synonym",
    "gần nghĩa": "near_synonym",
    "trái nghĩa": "antonym",
    "dễ nhầm": "confusable",
    "synonyms": "synonym",
    "near synonyms": "near_synonym",
    "antonyms": "antonym",
}


def parse_relation_cell(text):
    """
    Tách ô 'Quan hệ với từ khác': 'Đồng nghĩa: X; Y | Gần nghĩa: Z | Dễ nhầm: ...'
    -> list (rel_type, target_text, note). Đoạn giải thích dài không tách được
    thì giữ nguyên cả đoạn làm note.
    """
    out = []
    for part in split_outside_parens(text, "|"):
        m = re.match(r"^\s*([^:]{1,25})\s*:\s*(.*)$", part, re.S)
        if m and m.group(1).strip().lower() in REL_LABELS:
            rel = REL_LABELS[m.group(1).strip().lower()]
            body = m.group(2).strip()
            if is_empty(body):
                continue
            # Đoạn giải thích so sánh dài -> giữ nguyên một dòng
            if len(body) > 120 or " vs " in body.lower():
                out.append((rel, None, body))
                continue
            for item in split_outside_parens(body, ";,"):
                term, note = split_term_note(item)
                if not is_empty(term):
                    out.append((rel, term, note))
        else:
            out.append(("related", None, part.strip()))
    return out


def parse_examples_cell(text, seps="\n"):
    """Tách ô ví dụ nhiều dòng; nhận diện nhãn ĐÚNG:/SAI:."""
    out = []
    parts = split_outside_parens(text, seps)
    if len(parts) <= 1 and " / " in text and "\n" not in text:
        parts = [p.strip() for p in text.split(" / ") if p.strip()]
    for p in parts:
        note = None
        m = re.match(r"^\s*(ĐÚNG|SAI|Đúng|Sai)\s*:\s*(.*)$", p, re.S)
        if m:
            note = "ví dụ đúng" if m.group(1).upper() == "ĐÚNG" else "lỗi thường gặp (SAI)"
            p = m.group(2).strip()
        if p:
            out.append((p, note))
    return out


def parse_cefr(v, sheet):
    s = clean(v)
    if s is None:
        return None
    s = s.upper().strip()
    if s in CEFR_LEVELS:
        return s
    stats[f"cefr_invalid:{sheet}"] += 1
    report["CEFR không hợp lệ"].append(f"- `{sheet}`: giá trị `{v}` → để trống")
    return None


def parse_int(v):
    if v is None:
        return None
    try:
        return int(float(str(v).replace(",", "")))
    except ValueError:
        return None


# ---------------------------------------------------------------- schema
SCHEMA = """
PRAGMA journal_mode=WAL;
CREATE TABLE words (
  id        INTEGER PRIMARY KEY,
  headword  TEXT NOT NULL UNIQUE COLLATE NOCASE,
  ipa       TEXT,
  frequency INTEGER
);
CREATE TABLE pos (
  id      INTEGER PRIMARY KEY,
  code    TEXT NOT NULL UNIQUE,
  name_vi TEXT NOT NULL
);
CREATE TABLE entries (
  id             INTEGER PRIMARY KEY,
  word_id        INTEGER NOT NULL REFERENCES words(id),
  pos_id         INTEGER NOT NULL REFERENCES pos(id),
  meaning_vi     TEXT,
  meaning_en     TEXT,
  cefr           TEXT CHECK (cefr IN ('A1','A2','B1','B2','C1','C2') OR cefr IS NULL),
  semantic_group TEXT,
  register       TEXT,
  usage_notes    TEXT,
  source         TEXT,
  attrs          TEXT,
  raw_json       TEXT,
  created_at     TEXT DEFAULT (datetime('now')),
  updated_at     TEXT DEFAULT (datetime('now')),
  UNIQUE (word_id, pos_id)
);
CREATE TABLE examples (
  id       INTEGER PRIMARY KEY,
  entry_id INTEGER NOT NULL REFERENCES entries(id) ON DELETE CASCADE,
  text_en  TEXT NOT NULL,
  text_vi  TEXT,
  note     TEXT
);
CREATE TABLE relations (
  id           INTEGER PRIMARY KEY,
  entry_id     INTEGER NOT NULL REFERENCES entries(id) ON DELETE CASCADE,
  rel_type     TEXT NOT NULL,
  target_entry INTEGER REFERENCES entries(id),
  target_text  TEXT,
  note         TEXT
);
CREATE TABLE collocations (
  id         INTEGER PRIMARY KEY,
  entry_id   INTEGER REFERENCES entries(id) ON DELETE CASCADE,
  pattern    TEXT,
  phrase     TEXT NOT NULL,
  meaning_vi TEXT,
  meaning_en TEXT,
  example    TEXT,
  source     TEXT
);
CREATE TABLE noun_attrs (
  entry_id     INTEGER PRIMARY KEY REFERENCES entries(id) ON DELETE CASCADE,
  countability TEXT,
  plural_form  TEXT,
  noun_type    TEXT,
  grammar_note TEXT
);
CREATE TABLE verb_attrs (
  entry_id        INTEGER PRIMARY KEY REFERENCES entries(id) ON DELETE CASCADE,
  verb_type       TEXT,
  past_simple     TEXT,
  past_participle TEXT,
  third_person    TEXT
);
CREATE TABLE adjective_attrs (
  entry_id          INTEGER PRIMARY KEY REFERENCES entries(id) ON DELETE CASCADE,
  comparative       TEXT,
  superlative       TEXT,
  comparison_note   TEXT,
  gradable          TEXT,
  degree_adverbs    TEXT,
  attributive       INTEGER,
  predicative       INTEGER,
  object_complement INTEGER,
  position_meaning_changes INTEGER,
  position_note     TEXT
);
CREATE TABLE phrasal_verbs (
  entry_id     INTEGER PRIMARY KEY REFERENCES entries(id) ON DELETE CASCADE,
  base_verb_id INTEGER REFERENCES entries(id),
  base_verb    TEXT NOT NULL,
  particle     TEXT NOT NULL,
  separable    TEXT
);
CREATE TABLE sentences (
  id            INTEGER PRIMARY KEY,
  text_en       TEXT NOT NULL,
  sentence_type TEXT,
  meaning_vi    TEXT,
  source        TEXT
);
CREATE TABLE grammar_notes (
  id      INTEGER PRIMARY KEY,
  topic   TEXT NOT NULL,
  title   TEXT,
  content TEXT NOT NULL,
  example TEXT,
  source  TEXT
);
CREATE VIRTUAL TABLE search_index USING fts5(
  headword, meaning_vi, meaning_en, example_text, entry_id UNINDEXED
);
CREATE INDEX idx_entries_word ON entries(word_id);
CREATE INDEX idx_entries_pos ON entries(pos_id);
CREATE INDEX idx_entries_cefr ON entries(cefr);
CREATE INDEX idx_examples_entry ON examples(entry_id);
CREATE INDEX idx_relations_entry ON relations(entry_id);
CREATE INDEX idx_collocations_entry ON collocations(entry_id);
"""

POS_SEED = [
    ("noun", "Danh từ"), ("verb", "Động từ"), ("adjective", "Tính từ"),
    ("adverb", "Trạng từ"), ("conjunction", "Liên từ"), ("preposition", "Giới từ"),
    ("determiner", "Từ hạn định"), ("auxiliary", "Trợ động từ"),
    ("particle", "Tiểu từ"), ("interjection", "Thán từ"),
    ("phrasal_verb", "Cụm động từ"), ("idiom", "Thành ngữ"),
]


class Loader:
    def __init__(self, con):
        self.con = con
        self.cur = con.cursor()
        self.pos_ids = {}
        for code, name in POS_SEED:
            self.cur.execute("INSERT INTO pos(code, name_vi) VALUES (?,?)", (code, name))
            self.pos_ids[code] = self.cur.lastrowid

    def word_id(self, headword, ipa=None, frequency=None):
        self.cur.execute("SELECT id, ipa, frequency FROM words WHERE headword = ? COLLATE NOCASE", (headword,))
        row = self.cur.fetchone()
        if row:
            wid, old_ipa, old_freq = row
            if ipa and not old_ipa:
                self.cur.execute("UPDATE words SET ipa=? WHERE id=?", (ipa, wid))
            if frequency and not old_freq:
                self.cur.execute("UPDATE words SET frequency=? WHERE id=?", (frequency, wid))
            return wid
        self.cur.execute("INSERT INTO words(headword, ipa, frequency) VALUES (?,?,?)",
                         (headword, ipa, frequency))
        return self.cur.lastrowid

    def add_entry(self, headword, pos, sheet, *, ipa=None, frequency=None, meaning_vi=None,
                  meaning_en=None, cefr=None, semantic_group=None, register=None,
                  usage_notes=None, source=None, attrs=None, raw=None):
        headword = clean(headword)
        if not headword:
            return None
        wid = self.word_id(headword, ipa, frequency)
        pid = self.pos_ids[pos]
        self.cur.execute("SELECT id FROM entries WHERE word_id=? AND pos_id=?", (wid, pid))
        dup = self.cur.fetchone()
        if dup:
            stats["dup_skipped"] += 1
            report["Mục trùng (từ + từ loại) — giữ bản đầu, bỏ bản sau"].append(
                f"- `{headword}` ({pos}) trong sheet `{sheet}`")
            return None
        self.cur.execute(
            """INSERT INTO entries(word_id, pos_id, meaning_vi, meaning_en, cefr,
               semantic_group, register, usage_notes, source, attrs, raw_json)
               VALUES (?,?,?,?,?,?,?,?,?,?,?)""",
            (wid, pid, clean(meaning_vi), clean(meaning_en), cefr, clean(semantic_group),
             clean(register), usage_notes, clean(source),
             json.dumps(attrs, ensure_ascii=False) if attrs else None,
             json.dumps(raw, ensure_ascii=False, default=str) if raw else None))
        stats[f"entries:{pos}"] += 1
        return self.cur.lastrowid

    def add_examples(self, entry_id, cell, seps="\n"):
        if entry_id is None or is_empty(cell):
            return
        for text, note in parse_examples_cell(str(cell), seps):
            self.cur.execute("INSERT INTO examples(entry_id, text_en, note) VALUES (?,?,?)",
                             (entry_id, text, note))
            stats["examples"] += 1

    def add_relations(self, entry_id, cell):
        if entry_id is None or is_empty(cell):
            return
        for rel, target, note in parse_relation_cell(str(cell)):
            self.cur.execute(
                "INSERT INTO relations(entry_id, rel_type, target_text, note) VALUES (?,?,?,?)",
                (entry_id, rel, target, note))
            stats["relations"] += 1

    def add_relation_list(self, entry_id, cell, rel_type, note_prefix=None):
        """Ô chỉ chứa danh sách từ cùng một loại quan hệ (vd cột 'Danh từ tương ứng')."""
        if entry_id is None or is_empty(cell):
            return
        text = str(cell)
        if len(text) > 120 or " vs " in text.lower():
            self.cur.execute(
                "INSERT INTO relations(entry_id, rel_type, note) VALUES (?,?,?)",
                (entry_id, rel_type, (f"{note_prefix}: " if note_prefix else "") + text.strip()))
            stats["relations"] += 1
            return
        for item in split_outside_parens(text, ";,\n"):
            term, note = split_term_note(item)
            if is_empty(term):
                continue
            if note_prefix:
                note = f"{note_prefix}" + (f" — {note}" if note else "")
            self.cur.execute(
                "INSERT INTO relations(entry_id, rel_type, target_text, note) VALUES (?,?,?,?)",
                (entry_id, rel_type, term, note))
            stats["relations"] += 1

    def add_collocations(self, entry_id, cell, pattern, source=None):
        if is_empty(cell):
            return
        for item in split_outside_parens(str(cell), ";,\n"):
            phrase, note = split_term_note(item)
            if is_empty(phrase):
                continue
            self.cur.execute(
                """INSERT INTO collocations(entry_id, pattern, phrase, meaning_vi, source)
                   VALUES (?,?,?,?,?)""",
                (entry_id, pattern, phrase, note, source))
            stats["collocations"] += 1


# ---------------------------------------------------------------- sheet parsers

def rows_of(ws):
    return list(ws.iter_rows(values_only=True))


def header_map(row):
    return {str(v).strip(): i for i, v in enumerate(row) if v is not None and str(v).strip()}


def parse_adjectives(ld, ws):
    rows = rows_of(ws)
    h = header_map(rows[1])
    for r in rows[2:]:
        word = clean(r[h["Tính từ"]])
        if not word:
            continue
        yn = lambda col: 1 if clean(r[h[col]]) == "Yes" else (0 if clean(r[h[col]]) == "No" else None)
        eid = ld.add_entry(
            word, "adjective", ws.title,
            frequency=parse_int(r[h["Tần suất"]]),
            meaning_vi=r[h["Nghĩa tiếng Việt"]],
            cefr=parse_cefr(r[h["CEFR"]], ws.title),
            semantic_group=r[h["Nhóm ngữ nghĩa"]],
            usage_notes=clean(r[h["Ghi chú trạng từ"]]),
            raw={k: r[i] for k, i in h.items() if r[i] is not None})
        if eid is None:
            continue
        ld.cur.execute(
            """INSERT INTO adjective_attrs(entry_id, comparative, superlative, comparison_note,
               gradable, degree_adverbs, attributive, predicative, object_complement,
               position_meaning_changes, position_note) VALUES (?,?,?,?,?,?,?,?,?,?,?)""",
            (eid, clean(r[h["Comparative"]]), clean(r[h["Superlative"]]),
             clean(r[h["Ghi chú so sánh"]]), clean(r[h["Gradable/Non-gradable"]]),
             clean(r[h["Nhóm Degree Adverb đi kèm"]]), yn("Attributive"), yn("Predicative"),
             yn("Object Complement"),
             1 if clean(r[h["Meaning Changes by Position"]]) == "Yes" else 0,
             clean(r[h["Ghi chú vị trí"]])))
        ld.add_relation_list(eid, r[h["Trạng từ tương ứng"]], "derived", "trạng từ tương ứng")
        ld.add_relation_list(eid, r[h["Danh từ tương ứng"]], "derived", "danh từ tương ứng")
        ld.add_relation_list(eid, r[h["Động từ tương ứng"]], "derived", "động từ tương ứng")
        coll_col = next(k for k in h if k.startswith("Collocation phổ biến"))
        ld.add_collocations(eid, r[h[coll_col]], "adj+noun")
        only_col = next(k for k in h if k.startswith("Danh từ CHỈ kết hợp riêng"))
        ld.add_collocations(eid, r[h[only_col]], "adj+noun (cụm cố định)")
        ld.add_examples(eid, r[h["Ví dụ thực tế"]])


def parse_nouns(ld, ws):
    rows = rows_of(ws)
    h = header_map(rows[0])
    for r in rows[1:]:
        word = clean(r[h["Word"]])
        if not word:
            continue
        gram = clean(r[h["Đặc điểm ngữ pháp"]]) or ""
        low = gram.lower()
        if "không đếm được" in low and "đếm được;" not in low and not low.startswith("đếm được"):
            countability = "uncountable"
        elif "đếm được" in low:
            countability = "both" if "không đếm được" in low else "countable"
        else:
            countability = None
        eid = ld.add_entry(
            word, "noun", ws.title,
            meaning_vi=r[h["Nghĩa"]],
            cefr=parse_cefr(r[h["CEFR"]], ws.title),
            semantic_group=r[h["Noun Type"]],
            usage_notes="\n".join(x for x in (clean(r[h["Common Mistakes"]]), clean(r[h["Notes"]])) if x) or None,
            raw={k: r[i] for k, i in h.items() if r[i] is not None})
        if eid is None:
            continue
        ld.cur.execute(
            "INSERT INTO noun_attrs(entry_id, countability, plural_form, noun_type, grammar_note) VALUES (?,?,?,?,?)",
            (eid, countability, clean(r[h["Số nhiều bất quy tắc"]]), clean(r[h["Noun Type"]]), gram or None))
        for col, pattern in [("Verb+Noun", "verb+noun"), ("Noun+Verb", "noun+verb"),
                             ("Adjective+Noun", "adj+noun"), ("Noun+Noun", "noun+noun"),
                             ("Noun+Preposition", "noun+prep"), ("Quantifier+Noun", "quantifier+noun"),
                             ("Fixed Expressions", "fixed")]:
            ld.add_collocations(eid, r[h[col]], pattern)
        ld.add_relation_list(eid, r[h["Confusable Groups"]], "confusable")


def parse_verbs(ld, ws):
    rows = rows_of(ws)
    h = header_map(rows[1])
    # --- bảng 1: động từ thường (đến khi gặp header bảng phrasal)
    i = 2
    while i < len(rows) and clean(rows[i][0]) != "Động từ gốc":
        r = rows[i]
        i += 1
        if not isinstance(r[0], (int, float)):
            continue
        word = clean(r[h["Động từ"]])
        if not word:
            continue
        v23 = clean(r[h["V2/V3 bất quy tắc"]])
        past = pp = None
        if v23:
            parts = [p.strip() for p in v23.split(" / ")]
            if len(parts) == 2:
                past, pp = parts
            else:
                past = v23
        eid = ld.add_entry(
            word, "verb", ws.title,
            frequency=parse_int(r[h["Tần suất"]]),
            cefr=parse_cefr(r[h["CEFR"]], ws.title),
            usage_notes=clean(r[h["Phân biệt / Ghi chú"]]),
            source=clean(r[h["Nguồn dữ liệu"]]),
            attrs={k: clean(r[h[k]]) for k in ("Vi/Vt + Giới từ + Tân ngữ", "Phrasal Verb", "Slang")
                   if clean(r[h[k]])} or None,
            raw={k: r[j] for k, j in h.items() if r[j] is not None})
        if eid is None:
            continue
        ld.cur.execute(
            "INSERT INTO verb_attrs(entry_id, verb_type, past_simple, past_participle, third_person) VALUES (?,?,?,?,?)",
            (eid, clean(r[h["Loại động từ"]]), past, pp, clean(r[h["V-s/es bất quy tắc"]])))
        ld.add_examples(eid, r[h["Ví dụ minh hoạ"]])
        ld.add_relation_list(eid, r[h["Đồng nghĩa + sắc thái"]], "synonym")
        ld.add_relation_list(eid, r[h["Từ dễ nhầm"]], "confusable")
        ld.add_collocations(eid, r[h["Collocation/Idiom"]], "verb collocation/idiom")
    # --- bảng 2: phrasal verbs
    if i < len(rows):
        ph = header_map(rows[i])
        for r in rows[i + 1:]:
            base = clean(r[ph["Động từ gốc"]])
            full = clean(r[ph["Phrasal Verb đầy đủ"]])
            if not base or not full:
                continue
            eid = ld.add_entry(
                full, "phrasal_verb", ws.title,
                meaning_vi=r[ph["Nghĩa tiếng Việt"]],
                raw={k: r[j] for k, j in ph.items() if r[j] is not None})
            if eid is None:
                continue
            ld.cur.execute(
                "INSERT INTO phrasal_verbs(entry_id, base_verb, particle, separable) VALUES (?,?,?,?)",
                (eid, base, clean(r[ph["Giới từ/Tiểu từ"]]) or "", clean(r[ph["Tách được / Không tách được"]])))
            ld.add_examples(eid, r[ph["Ví dụ minh hoạ"]])


def parse_adverbs(ld, ws):
    rows = rows_of(ws)
    # bảng 1 (R2-R9): ghi chú vị trí theo loại trạng từ -> grammar_notes
    h1 = header_map(rows[1])
    for r in rows[2:10]:
        cat = clean(r[0])
        if not cat or cat == "TỔNG CỘNG":
            continue
        ld.cur.execute(
            "INSERT INTO grammar_notes(topic, title, content, example, source) VALUES (?,?,?,?,?)",
            ("adverb_position", cat, clean(r[h1["Cấu trúc phổ biến (vị trí trong câu)"]]) or "",
             clean(r[h1["Ví dụ minh hoạ"]]), ws.title))
        stats["grammar_notes"] += 1
    # bảng 2 (R13+): danh sách trạng từ
    h = header_map(rows[12])
    for r in rows[13:]:
        if not isinstance(r[0], (int, float)):
            continue
        word = clean(r[h["Trạng từ"]])
        if not word:
            continue
        root = clean(r[h["Gốc từ (trước suffix)"]])
        attrs = {}
        if root and not root.startswith("—"):
            attrs = {"root_word": root, "root_pos": clean(r[h["Loại từ của gốc"]]),
                     "root_meaning": clean(r[h["Nghĩa của gốc"]])}
        eid = ld.add_entry(
            word, "adverb", ws.title,
            frequency=parse_int(r[h["Tần suất"]]),
            cefr=parse_cefr(r[h["Cấp độ (CEFR)"]], ws.title),
            semantic_group=r[h["Loại trạng từ"]],
            # sheet gốc không có cột nghĩa riêng cho trạng từ; dùng nghĩa của gốc nếu là dạng gốc
            meaning_vi=clean(r[h["Nghĩa của gốc"]]) if not attrs else None,
            attrs=attrs or None,
            raw={k: r[j] for k, j in h.items() if r[j] is not None})
        if eid and attrs:
            ld.cur.execute(
                "INSERT INTO relations(entry_id, rel_type, target_text, note) VALUES (?,?,?,?)",
                (eid, "derived", attrs["root_word"],
                 f"gốc từ ({attrs.get('root_pos') or '?'}): {attrs.get('root_meaning') or ''}".strip()))
            stats["relations"] += 1


def parse_simple_word_sheet(ld, ws, pos, colmap, attrs_cols=(), relation_col=None,
                            example_col=None, example_seps="\n", collocation_cols=(),
                            stop_at=None):
    """
    Parser chung cho các sheet từ loại nhỏ: liên từ, giới từ, từ hạn định,
    trợ động từ, tiểu từ, thán từ. Bỏ qua header lặp lại giữa các section.
    colmap: tên cột chuẩn -> tên header trong sheet.
    """
    rows = rows_of(ws)
    h = None
    word_header = None
    for idx, r in enumerate(rows):
        first = clean(r[0])
        if stop_at and idx + 1 >= stop_at:
            break
        if first in ("Từ/cụm từ", "Từ"):
            h = header_map(r)
            word_header = first
            continue
        if h is None or not first:
            continue
        # dòng tiêu đề section (chỉ có cột A, các cột sau trống)
        if all(v is None or str(v).strip() == "" for v in r[1:4]) and len(first) > 12:
            continue
        get = lambda key: r[h[colmap[key]]] if key in colmap and colmap[key] in h else None
        attrs = {}
        for c in attrs_cols:
            if c in h and clean(r[h[c]]):
                attrs[c] = clean(r[h[c]])
        eid = ld.add_entry(
            first, pos, ws.title,
            ipa=clean(get("ipa")),
            frequency=parse_int(get("frequency")),
            meaning_vi=get("meaning_vi"),
            cefr=parse_cefr(get("cefr"), ws.title),
            semantic_group=clean(get("semantic_group")),
            register=clean(get("register")),
            usage_notes=clean(get("usage_notes")),
            attrs=attrs or None,
            raw={k: r[j] for k, j in h.items() if r[j] is not None})
        if eid is None:
            continue
        if relation_col and relation_col in h:
            ld.add_relations(eid, r[h[relation_col]])
        if "confusable_col" in colmap and colmap["confusable_col"] in h:
            ld.add_relation_list(eid, r[h[colmap["confusable_col"]]], "confusable")
        if example_col and example_col in h:
            ld.add_examples(eid, r[h[example_col]], example_seps)
        for col, pattern in collocation_cols:
            if col in h:
                ld.add_collocations(eid, r[h[col]], pattern)


def parse_determiner_extra_tables(ld, ws):
    """Bảng 'Nguyên tắc' (R71+) -> grammar_notes; bảng lượng từ (R82+) -> collocations."""
    rows = rows_of(ws)
    mode = None
    for r in rows:
        first = clean(r[0])
        if first == "STT" and clean(r[1]) == "Nguyên tắc":
            mode = "rules"
            continue
        if first == "Lượng từ (Quantifier)":
            mode = "quantifiers"
            continue
        if mode == "rules" and isinstance(r[0], (int, float)) and clean(r[1]):
            ld.cur.execute(
                "INSERT INTO grammar_notes(topic, title, content, source) VALUES (?,?,?,?)",
                ("determiner_rules", clean(r[1]), clean(r[2]) or "", ws.title))
            stats["grammar_notes"] += 1
        elif mode == "quantifiers" and first and clean(r[1]):
            ld.cur.execute(
                """INSERT INTO collocations(pattern, phrase, meaning_vi, example, source)
                   VALUES (?,?,?,?,?)""",
                ("quantifier+noun", first,
                 f"{clean(r[1]) or ''} — đi với: {clean(r[2]) or '?'}", clean(r[3]), ws.title))
            stats["collocations"] += 1


def parse_collocation_sheet(ld, ws):
    rows = rows_of(ws)
    h = header_map(rows[0])
    for r in rows[1:]:
        phrase = clean(r[0])
        if not phrase:
            continue
        ld.cur.execute(
            """INSERT INTO collocations(pattern, phrase, meaning_vi, meaning_en, example, source)
               VALUES (?,?,?,?,?,?)""",
            ("collocation", phrase, clean(r[h["Nghĩa tiếng Việt"]]),
             clean(r[h["Nghĩa tiếng Anh (Cambridge)"]]),
             clean(r[h["Ví dụ / Cụm liên quan"]]), clean(r[h["Bài học (nguồn)"]])))
        stats["collocations"] += 1


def parse_idiom_sheet(ld, ws):
    rows = rows_of(ws)
    h = header_map(rows[0])
    for r in rows[1:]:
        phrase = clean(r[0])
        if not phrase:
            continue
        eid = ld.add_entry(
            phrase, "idiom", ws.title,
            meaning_vi=r[h["Nghĩa tiếng Việt"]],
            meaning_en=r[h["Nghĩa tiếng Anh (Cambridge)"]],
            source=clean(r[h["Bài học (nguồn)"]]),
            raw={k: r[j] for k, j in h.items() if r[j] is not None})
        ld.add_examples(eid, r[h["Ví dụ minh hoạ"]])


def parse_sentences(ld, ws):
    rows = rows_of(ws)
    h = header_map(rows[0])
    for r in rows[1:]:
        text = clean(r[0])
        if not text:
            continue
        ld.cur.execute(
            "INSERT INTO sentences(text_en, sentence_type, meaning_vi, source) VALUES (?,?,?,?)",
            (text, clean(r[h["Loại câu"]]), clean(r[h["Nghĩa tiếng Việt"]]), clean(r[h["Bài học"]])))
        stats["sentences"] += 1


# ---------------------------------------------------------------- hậu xử lý

def link_relations(con):
    """Nối relations.target_text -> entries.id khi từ đích có trong DB."""
    cur = con.cursor()
    cur.execute("""
        UPDATE relations SET target_entry = (
          SELECT e.id FROM entries e JOIN words w ON w.id = e.word_id
          WHERE w.headword = relations.target_text COLLATE NOCASE
          ORDER BY e.id LIMIT 1)
        WHERE target_text IS NOT NULL""")
    cur.execute("""
        UPDATE phrasal_verbs SET base_verb_id = (
          SELECT e.id FROM entries e
          JOIN words w ON w.id = e.word_id
          JOIN pos p ON p.id = e.pos_id
          WHERE w.headword = phrasal_verbs.base_verb COLLATE NOCASE AND p.code = 'verb'
          LIMIT 1)""")


def build_fts(con):
    cur = con.cursor()
    cur.execute("""
        INSERT INTO search_index(headword, meaning_vi, meaning_en, example_text, entry_id)
        SELECT w.headword, COALESCE(e.meaning_vi,''), COALESCE(e.meaning_en,''),
               COALESCE((SELECT group_concat(text_en, ' ') FROM examples x WHERE x.entry_id = e.id), ''),
               e.id
        FROM entries e JOIN words w ON w.id = e.word_id""")


def write_report(con):
    cur = con.cursor()
    lines = ["# Báo cáo chất lượng dữ liệu — import tuloaigoptoanbo5.xlsx", ""]
    lines.append("## Số liệu tổng hợp\n")
    cur.execute("""SELECT p.name_vi, p.code, COUNT(*) FROM entries e
                   JOIN pos p ON p.id = e.pos_id GROUP BY p.id ORDER BY COUNT(*) DESC""")
    lines.append("| Từ loại | Số mục từ |")
    lines.append("|---|---|")
    total = 0
    for name, code, n in cur.fetchall():
        lines.append(f"| {name} ({code}) | {n} |")
        total += n
    lines.append(f"| **Tổng** | **{total}** |")
    for label, key in [("Từ (word) duy nhất", "SELECT COUNT(*) FROM words"),
                       ("Ví dụ", "SELECT COUNT(*) FROM examples"),
                       ("Quan hệ từ", "SELECT COUNT(*) FROM relations"),
                       ("— trong đó đã nối được sang mục từ trong DB",
                        "SELECT COUNT(*) FROM relations WHERE target_entry IS NOT NULL"),
                       ("Collocation", "SELECT COUNT(*) FROM collocations"),
                       ("Câu mẫu", "SELECT COUNT(*) FROM sentences"),
                       ("Ghi chú ngữ pháp", "SELECT COUNT(*) FROM grammar_notes")]:
        cur.execute(key)
        lines.append(f"- {label}: **{cur.fetchone()[0]}**")

    lines.append("\n## Trường còn thiếu (cần bổ sung dần qua form nhập liệu)\n")
    for label, sql in [
            ("Mục từ thiếu nghĩa tiếng Việt", "SELECT COUNT(*) FROM entries WHERE meaning_vi IS NULL"),
            ("Mục từ thiếu CEFR", "SELECT COUNT(*) FROM entries WHERE cefr IS NULL"),
            ("Từ thiếu IPA", "SELECT COUNT(*) FROM words WHERE ipa IS NULL"),
            ("Từ thiếu tần suất", "SELECT COUNT(*) FROM words WHERE frequency IS NULL")]:
        cur.execute(sql)
        lines.append(f"- {label}: **{cur.fetchone()[0]}**")
    cur.execute("""SELECT p.code, COUNT(*) FROM entries e JOIN pos p ON p.id=e.pos_id
                   WHERE e.meaning_vi IS NULL GROUP BY p.code ORDER BY COUNT(*) DESC""")
    breakdown = ", ".join(f"{c}: {n}" for c, n in cur.fetchall())
    lines.append(f"  - Thiếu nghĩa tiếng Việt theo từ loại: {breakdown}")
    lines.append("  - Lưu ý: sheet gốc Tính từ/Động từ/Trạng từ không có cột nghĩa"
                 " tiếng Việt riêng (trạng từ chỉ có 'nghĩa của gốc từ').")

    lines.append("\n## Cảnh báo khi import\n")
    for section, items in sorted(report.items()):
        lines.append(f"### {section} ({len(items)})\n")
        lines.extend(items[:50])
        if len(items) > 50:
            lines.append(f"- … và {len(items) - 50} dòng nữa")
        lines.append("")
    with open(REPORT, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")


def main():
    if os.path.exists(DB):
        os.remove(DB)
    for suffix in ("-wal", "-shm"):
        if os.path.exists(DB + suffix):
            os.remove(DB + suffix)
    wb = openpyxl.load_workbook(XLSX, read_only=True, data_only=True)
    con = sqlite3.connect(DB)
    con.executescript(SCHEMA)
    ld = Loader(con)

    parse_adverbs(ld, wb["1. Trang tu (Adverb)"])
    parse_adjectives(ld, wb["2. Tinh tu (Adjective)"])
    parse_simple_word_sheet(
        ld, wb["3. Lien tu (Conjunction)"], "conjunction",
        colmap={"ipa": "IPA", "frequency": "Tần suất", "meaning_vi": "Nghĩa tiếng Việt",
                "cefr": "CEFR", "semantic_group": "Loại liên từ", "register": "Register",
                "usage_notes": "Ghi chú vị trí/đảo ngữ"},
        attrs_cols=("Chức năng ngữ nghĩa", "Cấu trúc & vị trí trong câu",
                    "Nhóm hoán đổi được (đồng chức năng)"),
        relation_col=REL_COL,
        example_col="Ví dụ đúng | Ví dụ sai thường gặp", example_seps="|\n")
    parse_simple_word_sheet(
        ld, wb["4. Gioi tu (Preposition)"], "preposition",
        colmap={"ipa": "IPA", "frequency": "Tần suất", "meaning_vi": "Nghĩa tiếng Việt",
                "cefr": "CEFR", "semantic_group": "Nhóm ngữ nghĩa",
                "confusable_col": "Cặp dễ nhầm lẫn"},
        attrs_cols=("Loại", "Cấu trúc & vị trí"),
        relation_col=REL_COL,
        collocation_cols=[("Verb + Prep", "verb+prep"), ("Adjective + Prep", "adj+prep"),
                          ("Noun + Prep", "noun+prep"), ("Prep + Noun (cụm cố định)", "prep+noun"),
                          ("Fixed Expressions/Idioms", "fixed")])
    parse_simple_word_sheet(
        ld, wb["5. Tu han dinh (Determiner)"], "determiner",
        colmap={"ipa": "IPA", "frequency": "Tần suất", "meaning_vi": "Nghĩa tiếng Việt",
                "cefr": "CEFR", "semantic_group": "Loại (Article/Quantifier)",
                "usage_notes": "Quy tắc & ngoại lệ", "confusable_col": "Cặp dễ nhầm lẫn"},
        attrs_cols=("Loại danh từ đi kèm", "Vị trí trong cụm danh từ"),
        relation_col=REL_COL,
        stop_at=71)
    parse_determiner_extra_tables(ld, wb["5. Tu han dinh (Determiner)"])
    parse_verbs(ld, wb["6. Dong tu (Verb)"])
    parse_simple_word_sheet(
        ld, wb["7. Tro dong tu (Auxiliary)"], "auxiliary",
        colmap={"ipa": "IPA", "frequency": "Tần suất", "meaning_vi": "Nghĩa tiếng Việt",
                "cefr": "CEFR", "semantic_group": "Loại",
                "confusable_col": "Cặp dễ nhầm lẫn"},
        attrs_cols=("Chức năng ngữ nghĩa/ngữ pháp", "Dạng phủ định/rút gọn", "Theo sau bởi"),
        relation_col=REL_COL)
    parse_simple_word_sheet(
        ld, wb["8. Tieu tu (Particle)"], "particle",
        colmap={"ipa": "IPA", "meaning_vi": "Nghĩa tiếng Việt", "cefr": "CEFR",
                "semantic_group": "Loại"},
        attrs_cols=("Nghĩa cốt lõi khi làm particle",
                    "Phân biệt Particle vs Giới từ/Trạng từ (cùng hình thức)"),
        relation_col=REL_COL,
        collocation_cols=[("Ví dụ Phrasal Verb tiêu biểu", "phrasal verb tiêu biểu")])
    parse_simple_word_sheet(
        ld, wb["9. Than tu-Dem xen (Interj)"], "interjection",
        colmap={"ipa": "IPA", "meaning_vi": "Nghĩa tiếng Việt", "cefr": "CEFR",
                "semantic_group": "Loại", "register": "Register (mức độ trang trọng)",
                "usage_notes": "Vị trí & dấu câu"},
        attrs_cols=("Chức năng",),
        relation_col=REL_COL,
        example_col="Ví dụ hội thoại", example_seps="\n")
    parse_nouns(ld, wb["10. Danh tu (Noun)"])
    parse_collocation_sheet(ld, wb["11. Collocation"])
    parse_idiom_sheet(ld, wb["12. Idiom"])
    parse_sentences(ld, wb["13. Cau (Sentences)"])

    link_relations(con)
    build_fts(con)
    con.commit()
    write_report(con)
    con.execute("PRAGMA journal_mode=DELETE")  # gộp WAL vào file .db chính
    con.commit()
    con.close()

    print("== Import xong ==")
    for k in sorted(stats):
        print(f"  {k}: {stats[k]}")
    print(f"DB: {DB}\nBáo cáo: {REPORT}")


if __name__ == "__main__":
    main()
