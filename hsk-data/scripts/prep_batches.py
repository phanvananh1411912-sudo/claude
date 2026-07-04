import json, os

SP = '/tmp/claude-0/-home-user-claude/8d38f015-ed38-5363-ae81-d0cc7e396864/scratchpad'
data = json.load(open(f'{SP}/parsed_lessons.json', encoding='utf-8'))
vs = json.load(open(f'{SP}/vocab_state.json', encoding='utf-8'))
os.makedirs(f'{SP}/batches', exist_ok=True)
os.makedirs(f'{SP}/enriched', exist_ok=True)

# vocab chunks
words = sorted(vs['unique'].keys())
missing = set(vs['missing_pinyin'])
NC = 4
per = (len(words) + NC - 1) // NC
for i in range(NC):
    chunk = {w: {'meaning': vs['unique'][w], 'pinyin': vs['lookup'].get(w, ''),
                 'need_pinyin': w in missing} for w in words[i*per:(i+1)*per]}
    json.dump(chunk, open(f'{SP}/batches/vocab_{i+1}.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print(f'vocab_{i+1}: {len(chunk)} words, {sum(1 for v in chunk.values() if v["need_pinyin"])} need pinyin')

# sentence batches
def dump_batch(name, lessons, grp):
    out = []
    for L in lessons:
        out.append({
            'group': grp, 'no': L['no'], 'titleHan': L['titleHan'], 'titleVi': L['titleVi'],
            'grammar_names': [g['name'] for g in L['grammar']],
            'grammar_details': [{'name': g['name'], 'example': g['example'], 'meaning': g['meaning']} for g in L['grammar']],
            'sentences': [{'idx': i + 1, 'speaker': s.get('speaker', ''), 'han': s['han'],
                           'pinyin_source': s['pinyin'], 'pinyin_draft': s.get('draft_pinyin', '')}
                          for i, s in enumerate(L['sentences'])],
        })
    json.dump(out, open(f'{SP}/batches/{name}.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print(name, len(lessons), 'lessons,', sum(len(L['sentences']) for L in lessons), 'sentences')

for i in range(4):
    dump_batch(f'sent_hsk1_{i+1}', data['hsk1'][i*10:(i+1)*10], 'hsk1')
for i in range(5):
    dump_batch(f'sent_hsk2doc_{i+1}', data['hsk2doc'][i*8:(i+1)*8], 'hsk2doc')
for i in range(10):
    dump_batch(f'sent_hsk2ht_{i+1}', data['hsk2ht'][i*4:(i+1)*4], 'hsk2ht')
