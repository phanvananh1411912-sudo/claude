# -*- coding: utf-8 -*-
"""PP1 — dinh dang doc: cot duoc goi thanh nhieu 'khoi' xep chong khi cau qua dai,
thay vi ep het vao 1 hang roi thu nho chu. Tai dung du lieu 24 cau tu build_passage.py."""
import sys
sys.path.insert(0, "/tmp/claude-0/-home-user-claude/368fd0ad-9a9f-5714-9d62-e83f8aba626e/scratchpad")
from build_passage import SENTENCES, KY_HIEU_1, KY_HIEU_2, BOLD_TOKENS, FONT

from docx import Document
from docx.shared import Pt, Twips
from docx.enum.section import WD_ORIENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

TABLE_PT = 11.0          # font co dinh, du lon de doc thoai mai
DXA_PER_CHAR = 135
MIN_COL = 900
PAGE_W = 16838
MARGIN = 500
USABLE = PAGE_W - 2 * MARGIN


def set_run(run, size, bold=False, italic=False):
    run.font.name = FONT
    run.font.size = Pt(size)
    run.bold = bold
    run.italic = italic
    rPr = run._element.get_or_add_rPr()
    rFonts = rPr.find(qn("w:rFonts"))
    if rFonts is None:
        rFonts = OxmlElement("w:rFonts")
        rPr.append(rFonts)
    for attr in ("w:ascii", "w:hAnsi", "w:cs", "w:eastAsia"):
        rFonts.set(qn(attr), FONT)


def add_code_runs(par, code, size):
    PLACEHOLDER = "§"
    protected = code.replace("=>", PLACEHOLDER)
    runs, token = [], ""
    for ch in protected:
        if ch in "+=":
            if token:
                runs.append(("tok", token)); token = ""
            runs.append(("sep", ch))
        else:
            token += ch
    if token:
        runs.append(("tok", token))
    for kind, text in runs:
        text = text.replace(PLACEHOLDER, "=>")
        bold = kind == "tok" and text in BOLD_TOKENS
        r = par.add_run(text)
        set_run(r, size, bold=bold)


def col_width(c1, c2):
    n = max(len(c1), len(c2))
    return max(MIN_COL, n * DXA_PER_CHAR + 160)


def set_cell_width(cell, w):
    tcPr = cell._tc.get_or_add_tcPr()
    tcW = tcPr.find(qn("w:tcW"))
    if tcW is None:
        tcW = OxmlElement("w:tcW")
        tcPr.append(tcW)
    tcW.set(qn("w:w"), str(w))
    tcW.set(qn("w:type"), "dxa")


def set_table_borders(table):
    tbl = table._tbl
    tblPr = tbl.tblPr
    borders = OxmlElement("w:tblBorders")
    for edge in ("top", "left", "bottom", "right", "insideH", "insideV"):
        el = OxmlElement(f"w:{edge}")
        el.set(qn("w:val"), "single")
        el.set(qn("w:sz"), "4")
        el.set(qn("w:color"), "000000")
        borders.append(el)
    tblPr.append(borders)
    layout = OxmlElement("w:tblLayout")
    layout.set(qn("w:type"), "fixed")
    tblPr.append(layout)


def chunk_columns(cols):
    """Goi cac cot thanh tung 'khoi' — moi khoi vua khit chieu ngang trang."""
    widths = [col_width(c1, c2) for c1, c2 in cols]
    chunks, current, current_w = [], [], 0
    for (c1, c2), w in zip(cols, widths):
        if current and current_w + w > USABLE:
            chunks.append(current)
            current, current_w = [], 0
        current.append((c1, c2, w))
        current_w += w
    if current:
        chunks.append(current)
    return chunks


def add_block_table(doc, chunk):
    table = doc.add_table(rows=2, cols=len(chunk))
    set_table_borders(table)
    table.autofit = False
    for i, (c1, c2, w) in enumerate(chunk):
        cell1 = table.cell(0, i)
        cell2 = table.cell(1, i)
        set_cell_width(cell1, w)
        set_cell_width(cell2, w)
        par1 = cell1.paragraphs[0]
        par1.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = par1.add_run(c1)
        set_run(r, TABLE_PT, bold=True)
        par2 = cell2.paragraphs[0]
        par2.alignment = WD_ALIGN_PARAGRAPH.CENTER
        add_code_runs(par2, c2, TABLE_PT)
    # khoang cach rat nho giua cac khoi cua cung 1 cau (khong dung paragraph rong)
    spacer = doc.add_paragraph()
    spacer.paragraph_format.space_before = Pt(0)
    spacer.paragraph_format.space_after = Pt(2)
    fmt = spacer.paragraph_format
    fmt.line_spacing = Pt(1)
    return table


doc = Document()
sec = doc.sections[0]
sec.orientation = WD_ORIENT.LANDSCAPE
sec.page_width = Twips(PAGE_W)
sec.page_height = Twips(11906)
for m in ("left_margin", "right_margin", "top_margin", "bottom_margin"):
    setattr(sec, m, Twips(MARGIN))

h = doc.add_heading(level=1)
r = h.add_run("PASSAGE ANALYSIS — ZOO CONSERVATION PROGRAMMES (C1T1) — PP1: dinh dang doc")
set_run(r, 15, bold=True)

for block in (KY_HIEU_1, KY_HIEU_2):
    p = doc.add_paragraph()
    r = p.add_run(block)
    set_run(r, 9, italic=True)

max_chunks_seen = 0
for s in SENTENCES:
    p = doc.add_paragraph()
    r = p.add_run(s["num"])
    set_run(r, 12, bold=True)

    p = doc.add_paragraph()
    r = p.add_run(s["vn"])
    set_run(r, 11, italic=True)

    p = doc.add_paragraph()
    r = p.add_run(s["en"])
    set_run(r, 11, bold=True)

    chunks = chunk_columns(s["cols"])
    max_chunks_seen = max(max_chunks_seen, len(chunks))
    for chunk in chunks:
        add_block_table(doc, chunk)

    doc.add_paragraph()  # khoang cach giua cac cau
    print(f"{s['num']}: {len(s['cols'])} cot -> {len(chunks)} khoi, font co dinh {TABLE_PT}pt")

import os
out = os.environ.get("OUT", "Passage-ZooConservation-PP1-20260710.docx")
doc.save(out)
print("Saved:", out)
print("So khoi nhieu nhat cho 1 cau:", max_chunks_seen)
