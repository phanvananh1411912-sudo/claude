import json, re
from pypinyin import pinyin, Style, load_phrases_dict

SP = '/tmp/claude-0/-home-user-claude/8d38f015-ed38-5363-ae81-d0cc7e396864/scratchpad'
data = json.load(open(f'{SP}/parsed_lessons.json', encoding='utf-8'))

load_phrases_dict({
    '起晚了': [['qǐ'], ['wǎn'], ['le']], '来不及': [['lái'], ['bu'], ['jí']],
    '说得': [['shuō'], ['de']], '觉得': [['jué'], ['de']], '睡觉': [['shuì'], ['jiào']],
    '地基': [['dì'], ['jī']], '哪怕': [['nǎ'], ['pà']],
})

PUNCT = {'，': ',', '。': '.', '？': '?', '！': '!', '：': ':', '；': ';',
         '“': '"', '”': '"', '‘': "'", '’': "'", '、': ',', '（': '(', '）': ')',
         '《': '"', '》': '"', '……': '...', '…': '...', '—': '-'}

def sent_pinyin(han):
    parts = pinyin(han, style=Style.TONE, errors=lambda x: [PUNCT.get(c, c) for c in x])
    toks = [p[0] for p in parts]
    out = ''
    for t in toks:
        if re.match(r'^[a-zA-Zǖǘǚǜüāáǎàēéěèīíǐìōóǒòūúǔùǹń̀]+$', t):
            out += (' ' if out and out[-1] not in '("\'- ' else '') + t
        else:
            out += t + (' ' if t in ',.?!:;)' else '')
    out = re.sub(r'\s+', ' ', out).strip()
    return out[0].upper() + out[1:] if out else out

n = 0
for grp in data.values():
    for L in grp:
        for s in L['sentences']:
            if not s['pinyin']:
                src = (s.get('speaker', '') + '：' if 'speaker' in s else '') + s['han']
                s['draft_pinyin'] = sent_pinyin(src)
                n += 1

json.dump(data, open(f'{SP}/parsed_lessons.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('drafted', n)

# vocab pinyin lookup: HSK1 tables + tong hop file
lookup = {}
for grp in data.values():
    for L in grp:
        for v in L['vocab']:
            if v['pinyin']: lookup.setdefault(v['word'], v['pinyin'])
for line in open(f'{SP}/TuVung-TongHop.md', encoding='utf-8'):
    cells = [c.strip() for c in line.strip().strip('|').split('|')]
    if len(cells) == 4 and cells[0].isdigit():
        lookup.setdefault(cells[1], cells[2])

uniq = {}
for grp in data.values():
    for L in grp:
        for v in L['vocab']:
            uniq.setdefault(v['word'], v['meaning'])
missing = [w for w in uniq if w not in lookup]
print('unique vocab words:', len(uniq), '| have pinyin:', len(uniq) - len(missing), '| missing pinyin:', len(missing))
json.dump({'lookup': lookup, 'unique': uniq, 'missing_pinyin': missing},
          open(f'{SP}/vocab_state.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(missing[:60])
