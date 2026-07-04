import json, glob, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from hsk_excel_builder import build_workbook

SP = '/tmp/claude-0/-home-user-claude/8d38f015-ed38-5363-ae81-d0cc7e396864/scratchpad'
data = json.load(open(f'{SP}/parsed_lessons.json', encoding='utf-8'))

# load enriched sentence data: (group, no) -> [ {idx, pinyin, vi, grammar} ]
enr = {}
for f in glob.glob(f'{SP}/enriched/sent_*.out.json'):
    for L in json.load(open(f, encoding='utf-8')):
        enr[(L['group'], L['no'])] = L['sentences']

vocab_dict = {}
for f in sorted(glob.glob(f'{SP}/enriched/vocab_*.out.json')):
    vocab_dict.update(json.load(open(f, encoding='utf-8')))

GROUPS = [('hsk1', 'Bài {}'), ('hsk2doc', 'HSK2-Bài {}'), ('hsk2ht', 'HSK2-Hội thoại {}')]
errors, warns = [], []
cau, tv, np_ = [], [], []

for grp, fmt in GROUPS:
    for L in data[grp]:
        key = (grp, L['no'])
        bai = fmt.format(L['no'])
        es = enr.get(key)
        if es is None:
            errors.append(f'MISSING enrichment {key}'); continue
        if len(es) != len(L['sentences']):
            errors.append(f'COUNT mismatch {key}: {len(es)} vs {len(L["sentences"])}'); continue
        gnames = [g['name'] for g in L['grammar']]
        used = set()
        for src, e in zip(L['sentences'], es):
            han = (src['speaker'] + '：' if src.get('speaker') else '') + src['han']
            py = e.get('pinyin', '').strip()
            vi = e.get('vi', '').strip()
            if src.get('speaker'):
                vi = f"{src['speaker']}: {vi}"
            tags = e.get('grammar', [])
            bad = [t for t in tags if t not in gnames]
            if bad:
                warns.append(f'{key} idx{e["idx"]}: tag not in list {bad}')
                tags = [t for t in tags if t in gnames]
            used.update(tags)
            if not py: errors.append(f'{key} idx{e["idx"]}: empty pinyin')
            if not vi: errors.append(f'{key} idx{e["idx"]}: empty vi')
            cau.append((bai, e['idx'], han, py, vi, '; '.join(tags)))
        for g in gnames:
            if g not in used: warns.append(f'{key}: grammar "{g}" chưa gán câu nào')
        seen_words = set()
        for v in L['vocab']:
            w = v['word']
            if w in seen_words: continue
            seen_words.add(w)
            d = vocab_dict.get(w, {})
            py = v['pinyin'] or d.get('pinyin', '')
            hv, pos = d.get('hanviet', ''), d.get('pos', '')
            if not py: errors.append(f'{key} vocab {w}: no pinyin')
            if not hv: errors.append(f'{key} vocab {w}: no hanviet')
            if not pos: errors.append(f'{key} vocab {w}: no pos')
            tv.append((bai, w, py, hv, pos, v['meaning']))
        for g in L['grammar']:
            np_.append((bai, g['name'], g['meaning']))

print(f'Câu: {len(cau)} | Từ vựng: {len(tv)} | Ngữ pháp: {len(np_)}')
print(f'ERRORS: {len(errors)}')
for e in errors[:40]: print(' E:', e)
print(f'WARNINGS: {len(warns)}')
for w in warns[:40]: print(' W:', w)

if errors:
    sys.exit(1)
out = f'{SP}/HSK4NEXUS-TronGoi-120bai.xlsx'
build_workbook(out, cau, tv, np_)
print('built', out)
