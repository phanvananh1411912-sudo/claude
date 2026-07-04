import json, sys, os, re, glob
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from prep_hsk3ht2 import parse_file
from draft_pinyin import sent_pinyin

SP = '/tmp/claude-0/-home-user-claude/8d38f015-ed38-5363-ae81-d0cc7e396864/scratchpad'
all_lessons = parse_file(f'{SP}/HSK3-HoiThoai-KinhDoanh-2122.md')
all_lessons.sort(key=lambda L: L['no'])
issues = []
for L in all_lessons:
    if not L['grammar']: issues.append((L['no'], 'NO_GRAMMAR'))
    for s in L['sentences']:
        src = (s['speaker'] + '：' if s['speaker'] else '') + s['han']
        s['draft_pinyin'] = sent_pinyin(src)
        if not re.search(r'[一-鿿]', s['han']): issues.append((L['no'], 'NONHAN', s['han'][:20]))
print('dialogues:', len(all_lessons), '| nos:', [L['no'] for L in all_lessons], '| issues:', issues)
for L in all_lessons:
    print(f"  đối thoại {L['no']}: {len(L['sentences'])} dòng, speakers={sorted({s['speaker'] for s in L['sentences']})}, vocab={len(L['vocab'])}, grammar={len(L['grammar'])}")

json.dump({'hsk3ht4': all_lessons}, open(f'{SP}/parsed_hsk3ht4.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

vocab_dict = {}
for f in sorted(glob.glob(f'{SP}/enriched/vocab_*.out.json')):
    vocab_dict.update(json.load(open(f, encoding='utf-8')))
uniq = {}
for L in all_lessons:
    for v in L['vocab']:
        uniq.setdefault(v['word'], v['meaning'])
new = {w: m for w, m in uniq.items() if w not in vocab_dict}
print('unique words:', len(uniq), '| already have:', len(uniq)-len(new), '| new:', len(new))
json.dump({w: {'meaning': new[w], 'pinyin': '', 'need_pinyin': True} for w in sorted(new)},
          open(f'{SP}/batches/vocab_hsk3ht4_1.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

out = []
for L in all_lessons:
    out.append({
        'group': 'hsk3ht4', 'no': L['no'], 'titleHan': L['titleHan'], 'titleVi': L['titleVi'],
        'grammar_names': [g['name'] for g in L['grammar']],
        'grammar_details': L['grammar'],
        'sentences': [{'idx': j+1, 'speaker': s['speaker'], 'han': s['han'],
                       'pinyin_source': '', 'pinyin_draft': s['draft_pinyin']}
                      for j, s in enumerate(L['sentences'])],
    })
json.dump(out, open(f'{SP}/batches/sent_hsk3ht4_1.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('sent_hsk3ht4_1:', sum(len(L["sentences"]) for L in all_lessons), 'dòng')
