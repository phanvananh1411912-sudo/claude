import json, re, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from parse_lessons import parse_file
from draft_pinyin import sent_pinyin

SP = '/tmp/claude-0/-home-user-claude/8d38f015-ed38-5363-ae81-d0cc7e396864/scratchpad'
lessons = parse_file(f'{SP}/HSK3-Full-40bai.md', False)
assert len(lessons) == 40, len(lessons)
issues = []
for L in lessons:
    if len(L['sentences']) < 3: issues.append((L['no'], 'FEW_SENT'))
    if len(L['vocab']) < 3: issues.append((L['no'], 'FEW_VOCAB'))
    if not L['grammar']: issues.append((L['no'], 'NO_GRAMMAR'))
    for s in L['sentences']:
        if not re.search(r'[一-鿿]', s['han']): issues.append((L['no'], 'NONHAN', s['han'][:20]))
        s['draft_pinyin'] = sent_pinyin(s['han'])
print('lessons 40, issues:', issues)
print('sentences:', sum(len(L['sentences']) for L in lessons),
      'vocab rows:', sum(len(L['vocab']) for L in lessons),
      'grammar:', sum(len(L['grammar']) for L in lessons))

json.dump({'hsk3': lessons}, open(f'{SP}/parsed_hsk3.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

# vocab: those not already enriched in previous run
import glob
vocab_dict = {}
for f in sorted(glob.glob(f'{SP}/enriched/vocab_*.out.json')):
    if 'hsk3' in f: continue
    vocab_dict.update(json.load(open(f, encoding='utf-8')))
uniq = {}
for L in lessons:
    for v in L['vocab']:
        uniq.setdefault(v['word'], v['meaning'])
new = {w: m for w, m in uniq.items() if w not in vocab_dict}
print('unique hsk3 words:', len(uniq), '| already have:', len(uniq) - len(new), '| new:', len(new))

words = sorted(new)
NC = 3
per = (len(words) + NC - 1) // NC
for i in range(NC):
    chunk = {w: {'meaning': new[w], 'pinyin': '', 'need_pinyin': True} for w in words[i*per:(i+1)*per]}
    json.dump(chunk, open(f'{SP}/batches/vocab_hsk3_{i+1}.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print(f'vocab_hsk3_{i+1}: {len(chunk)}')

for i in range(5):
    part = lessons[i*8:(i+1)*8]
    out = []
    for L in part:
        out.append({
            'group': 'hsk3', 'no': L['no'], 'titleHan': L['titleHan'], 'titleVi': L['titleVi'],
            'grammar_names': [g['name'] for g in L['grammar']],
            'grammar_details': L['grammar'],
            'sentences': [{'idx': j + 1, 'speaker': '', 'han': s['han'],
                           'pinyin_source': '', 'pinyin_draft': s['draft_pinyin']}
                          for j, s in enumerate(L['sentences'])],
        })
    json.dump(out, open(f'{SP}/batches/sent_hsk3_{i+1}.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print(f'sent_hsk3_{i+1}:', len(part), 'lessons,', sum(len(L["sentences"]) for L in part), 'sentences')
