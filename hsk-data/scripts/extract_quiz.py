import json, re, glob, sys, os
sys.path.insert(0, '/tmp/claude-0/-home-user-claude/8d38f015-ed38-5363-ae81-d0cc7e396864/scratchpad')
from parse_lessons import split_lessons

SD = '/home/user/claude/hsk-data/sources'
OUT = '/tmp/claude-0/-home-user-claude/8d38f015-ed38-5363-ae81-d0cc7e396864/scratchpad'

Q_RE = re.compile(
    r'\*\*(\d+)\.\s*(.+?)\*\*\s*\n+'
    r'((?:[A-D]\..*\n*)+)'
    r'\s*✅\s*答案[：:]\s*([A-D])',
    re.M)
OPT_RE = re.compile(r'^([A-D])\.\s*(.+)$', re.M)
INLINE_RE = re.compile(r'^(.*?)\s*[\(（]([^()（）]+)[\)）]\s*[—–-]\s*(.+)$')

def parse_quiz_block(block, bai, lesson_no):
    out = []
    for m in Q_RE.finditer(block):
        qno, qtext, optblock, ans = m.groups()
        opts = dict(OPT_RE.findall(optblock))
        if len(opts) != 4:
            print(f'  WARN {bai} q{qno}: chỉ {len(opts)} đáp án'); continue
        parsed_opts = {}
        for k, v in opts.items():
            v = v.strip()
            im = INLINE_RE.match(v)
            if im:
                parsed_opts[k] = {'han': im.group(1).strip(), 'pinyin': im.group(2).strip(), 'vi': im.group(3).strip()}
            else:
                parsed_opts[k] = {'han': v, 'pinyin': '', 'vi': ''}
        out.append({'bai': bai, 'so': int(qno), 'cau_hoi': qtext.strip(), 'options': parsed_opts, 'dap_an': ans})
    return out

all_quiz = []

# HSK1
text = open(f'{SD}/HSK1-Full-40bai.md', encoding='utf-8').read()
for kind, no, title, body in split_lessons(text):
    m = re.search(r'### 理解测试\s*\n(.*)', body, re.S)
    if m:
        all_quiz += parse_quiz_block(m.group(1), f'Bài {no}', no)

# HSK2 (bài đọc + hội thoại, split at "PHẦN 2")
text = open(f'{SD}/HSK2-Full-80bai.md', encoding='utf-8').read()
part2_idx = text.index('# PHẦN 2')
doc_text, ht_text = text[:part2_idx], text[part2_idx:]
for kind, no, title, body in split_lessons(doc_text):
    m = re.search(r'### 理解测试\s*\n(.*)', body, re.S)
    if m: all_quiz += parse_quiz_block(m.group(1), f'HSK2-Bài {no}', no)
for kind, no, title, body in split_lessons(ht_text):
    m = re.search(r'### 理解测试\s*\n(.*)', body, re.S)
    if m: all_quiz += parse_quiz_block(m.group(1), f'HSK2-Hội thoại {no}', no)

# HSK3 bài đọc
text = open(f'{SD}/HSK3-Full-40bai.md', encoding='utf-8').read()
for kind, no, title, body in split_lessons(text):
    m = re.search(r'### 理解测试\s*\n(.*)', body, re.S)
    if m: all_quiz += parse_quiz_block(m.group(1), f'HSK3-Bài {no}', no)

# HSK3 hội thoại (18 files)
for fn in sorted(glob.glob(f'{SD}/HSK3-HoiThoai-*.md')):
    text = open(fn, encoding='utf-8').read()
    for kind, no, title, body in split_lessons(text):
        m = re.search(r'### 理解测试\s*\n(.*)', body, re.S)
        if m: all_quiz += parse_quiz_block(m.group(1), f'HSK3-Hội thoại {no}', no)

bais = sorted({q['bai'] for q in all_quiz}, key=lambda b: (b.split(' ')[0] if not b[0].isdigit() else '', b))
print('Tổng số bài có quiz:', len(bais))
print('Tổng số câu hỏi:', len(all_quiz))
import collections
per_bai = collections.Counter(q['bai'] for q in all_quiz)
print('phân bố số câu/bài (min/max):', min(per_bai.values()), max(per_bai.values()))
print('bài có != 5 câu (trừ HSK1 vốn 3 câu):', {b: c for b, c in per_bai.items() if c not in (3, 5)})
groups = collections.Counter()
for b in bais:
    if b.startswith('HSK3-Hội thoại'): groups['HSK3-Hội thoại'] += 1
    elif b.startswith('HSK3-Bài'): groups['HSK3-Bài'] += 1
    elif b.startswith('HSK2-Hội thoại'): groups['HSK2-Hội thoại'] += 1
    elif b.startswith('HSK2-Bài'): groups['HSK2-Bài'] += 1
    else: groups['Bài(HSK1)'] += 1
print(groups)
has_inline = sum(1 for q in all_quiz for o in q['options'].values() if o['pinyin'])
print('options có pinyin/nghia sẵn (inline, HSK1):', has_inline, '/', len(all_quiz)*4)

json.dump(all_quiz, open(f'{OUT}/raw_quiz.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
