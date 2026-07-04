import json, glob, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from hsk_excel_builder import build_workbook

SP = '/tmp/claude-0/-home-user-claude/8d38f015-ed38-5363-ae81-d0cc7e396864/scratchpad'
lessons = json.load(open(f'{SP}/parsed_hsk3ht2.json', encoding='utf-8'))['hsk3ht2']

enr = {}
for f in glob.glob(f'{SP}/enriched/sent_hsk3ht2_*.out.json'):
    for L in json.load(open(f, encoding='utf-8')):
        enr[L['no']] = L['sentences']

vocab_dict = {}
for f in sorted(glob.glob(f'{SP}/enriched/vocab_*.out.json')):
    vocab_dict.update(json.load(open(f, encoding='utf-8')))

errors, warns = [], []
cau, tv, np_ = [], [], []
for L in lessons:
    bai = f'HSK3-Hội thoại {L["no"]}'
    es = enr.get(L['no'])
    if es is None: errors.append(f'MISSING {L["no"]}'); continue
    if len(es) != len(L['sentences']): errors.append(f'COUNT {L["no"]}: {len(es)} vs {len(L["sentences"])}'); continue
    gnames = [g['name'] for g in L['grammar']]
    used = set()
    for src, e in zip(L['sentences'], es):
        han = (src['speaker'] + '：' if src.get('speaker') else '') + src['han']
        py, vi = e.get('pinyin', '').strip(), e.get('vi', '').strip()
        if src.get('speaker'):
            vi = f"{src['speaker']}: {vi}"
        tags = [t for t in e.get('grammar', []) if t in gnames]
        if len(tags) != len(e.get('grammar', [])):
            warns.append(f'{L["no"]} idx{e["idx"]}: tag lạ bị loại')
        used.update(tags)
        if not py: errors.append(f'{L["no"]} idx{e["idx"]}: empty pinyin')
        if not vi: errors.append(f'{L["no"]} idx{e["idx"]}: empty vi')
        cau.append((bai, e['idx'], han, py, vi, '; '.join(tags)))
    for g in gnames:
        if g not in used: warns.append(f'{L["no"]}: "{g}" chưa gán câu nào')
    seen = set()
    for v in L['vocab']:
        w = v['word']
        if w in seen: continue
        seen.add(w)
        d = vocab_dict.get(w, {})
        py = v['pinyin'] or d.get('pinyin', '')
        hv, pos = d.get('hanviet', ''), d.get('pos', '')
        if not py: errors.append(f'{L["no"]} vocab {w}: no pinyin')
        if not hv: errors.append(f'{L["no"]} vocab {w}: no hanviet')
        if not pos: errors.append(f'{L["no"]} vocab {w}: no pos')
        tv.append((bai, w, py, hv, pos, v['meaning']))
    for g in L['grammar']:
        np_.append((bai, g['name'], g['meaning']))

print(f'Câu: {len(cau)} | Từ vựng: {len(tv)} | Ngữ pháp: {len(np_)}')
print(f'ERRORS: {len(errors)}');  [print(' E:', e) for e in errors[:40]]
print(f'WARNINGS: {len(warns)}'); [print(' W:', w) for w in warns[:40]]
if errors: sys.exit(1)
out = f'{SP}/HSK4NEXUS-HSK3-HoiThoai-Bai7-13.xlsx'
build_workbook(out, cau, tv, np_)
print('built', out)
