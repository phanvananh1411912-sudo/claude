import json, sys, os, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from draft_pinyin import sent_pinyin

SP = '/tmp/claude-0/-home-user-claude/8d38f015-ed38-5363-ae81-d0cc7e396864/scratchpad'
data = json.load(open(f'{SP}/raw_quiz.json', encoding='utf-8'))

def bai_no(b):
    return int(re.search(r'\d+', b).group())

hsk1_lo = [q for q in data if q['bai'].startswith('Bài') and not q['bai'].startswith('HSK') and bai_no(q['bai']) <= 20]
hsk1_hi = [q for q in data if q['bai'].startswith('Bài') and not q['bai'].startswith('HSK') and bai_no(q['bai']) > 20]
hsk2_doc = [q for q in data if q['bai'].startswith('HSK2-Bài')]
hsk2_ht = [q for q in data if q['bai'].startswith('HSK2-Hội thoại')]
hsk3_doc = [q for q in data if q['bai'].startswith('HSK3-Bài')]
hsk3_ht = [q for q in data if q['bai'].startswith('HSK3-Hội thoại')]

print('hsk1_lo (chỉ cần question):', len(hsk1_lo))
print('hsk1_hi (cần full):', len(hsk1_hi))
print('hsk2_doc:', len(hsk2_doc))
print('hsk2_ht:', len(hsk2_ht))
print('hsk3_doc:', len(hsk3_doc))
print('hsk3_ht:', len(hsk3_ht))
print('tổng:', len(hsk1_lo)+len(hsk1_hi)+len(hsk2_doc)+len(hsk2_ht)+len(hsk3_doc)+len(hsk3_ht), 'vs', len(data))

os.makedirs(f'{SP}/quiz_batches', exist_ok=True)

def draft(q):
    q = dict(q)
    q['cau_hoi_pinyin_draft'] = sent_pinyin(q['cau_hoi'])
    for k, o in q['options'].items():
        if not o.get('pinyin'):
            o['pinyin_draft'] = sent_pinyin(o['han'])
    return q

def dump_batches(name, items, per, mode):
    items = [draft(q) for q in items]
    n = (len(items) + per - 1) // per
    for i in range(n):
        chunk = items[i*per:(i+1)*per]
        json.dump({'mode': mode, 'questions': chunk}, open(f'{SP}/quiz_batches/{name}_{i+1}.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print(f'{name}: {n} batch(es), {len(items)} câu, ~{per}/batch')

dump_batches('hsk1_lo', hsk1_lo, 60, 'question_only')
dump_batches('hsk1_hi', hsk1_hi, 30, 'full')
dump_batches('hsk2_doc', hsk2_doc, 34, 'full')
dump_batches('hsk2_ht', hsk2_ht, 34, 'full')
dump_batches('hsk3_doc', hsk3_doc, 34, 'full')
dump_batches('hsk3_ht', hsk3_ht, 35, 'full')
