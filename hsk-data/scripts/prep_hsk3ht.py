import json, sys, os, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from parse_lessons import parse_file
from draft_pinyin import sent_pinyin

SP = '/tmp/claude-0/-home-user-claude/8d38f015-ed38-5363-ae81-d0cc7e396864/scratchpad'
lessons = parse_file(f'{SP}/HSK3-HoiThoai-DiaLy-16bai.md', True)  # dialogue=True
print('dialogues:', len(lessons))
issues = []
for L in lessons:
    if len(L['sentences']) < 3: issues.append((L['no'], 'FEW_SENT'))
    if len(L['vocab']) < 3: issues.append((L['no'], 'FEW_VOCAB'))
    if not L['grammar']: issues.append((L['no'], 'NO_GRAMMAR'))
    for s in L['sentences']:
        src = (s.get('speaker', '') + '：' if s.get('speaker') else '') + s['han']
        s['draft_pinyin'] = sent_pinyin(src)
        if not re.search(r'[一-鿿]', s['han']): issues.append((L['no'], 'NONHAN', s['han'][:20]))
print('issues:', issues)
print('sentences:', sum(len(L['sentences']) for L in lessons),
      'vocab rows:', sum(len(L['vocab']) for L in lessons),
      'grammar:', sum(len(L['grammar']) for L in lessons))

json.dump({'hsk3ht': lessons}, open(f'{SP}/parsed_hsk3ht.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

# vocab: unique words not already in prior enriched dicts
import glob
vocab_dict = {}
for f in sorted(glob.glob(f'{SP}/enriched/vocab_*.out.json')):
    vocab_dict.update(json.load(open(f, encoding='utf-8')))
uniq = {}
for L in lessons:
    for v in L['vocab']:
        uniq.setdefault(v['word'], v['meaning'])
new = {w: m for w, m in uniq.items() if w not in vocab_dict}
print('unique words:', len(uniq), '| already have:', len(uniq) - len(new), '| new:', len(new))
json.dump({w: {'meaning': new[w], 'pinyin': '', 'need_pinyin': True} for w in sorted(new)},
          open(f'{SP}/batches/vocab_hsk3ht_1.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

# sentence batches: 2 batches of 3 dialogues
for i in range(2):
    part = lessons[i*3:(i+1)*3]
    out = []
    for L in part:
        out.append({
            'group': 'hsk3ht', 'no': L['no'], 'titleHan': L['titleHan'], 'titleVi': L['titleVi'],
            'grammar_names': [g['name'] for g in L['grammar']],
            'grammar_details': L['grammar'],
            'sentences': [{'idx': j+1, 'speaker': s.get('speaker', ''), 'han': s['han'],
                           'pinyin_source': '', 'pinyin_draft': s['draft_pinyin']}
                          for j, s in enumerate(L['sentences'])],
        })
    json.dump(out, open(f'{SP}/batches/sent_hsk3ht_{i+1}.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print(f'sent_hsk3ht_{i+1}:', len(part), 'dialogues,', sum(len(L["sentences"]) for L in part), 'turns')
