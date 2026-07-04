import json, sys, os, re, glob
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from parse_lessons import split_lessons, section, parse_title, parse_vocab, parse_grammar
from draft_pinyin import sent_pinyin

SP = '/tmp/claude-0/-home-user-claude/8d38f015-ed38-5363-ae81-d0cc7e396864/scratchpad'

def parse_dialogue_with_stage(sec):
    """Speaker turns **name**：text  +  stage directions **（...）** as narration rows."""
    out = []
    for l in sec.splitlines():
        l = l.strip()
        if not l or l.startswith('>'):
            continue
        m = re.match(r'\*\*([^（）]+?)\*\*\s*[：:]\s*(.*)', l)
        if m:
            out.append({'speaker': m.group(1).strip(), 'han': m.group(2).strip()})
            continue
        # stage direction: **（...）** (bold parenthetical, no colon)
        m2 = re.match(r'^\*\*(（.+?）)\*\*$', l)
        if m2:
            out.append({'speaker': '', 'han': m2.group(1).strip()})
            continue
        # continuation of previous spoken line (plain text)
        if out and not l.startswith('*'):
            out[-1]['han'] += l
    return out

def parse_file(path):
    text = open(path, encoding='utf-8').read()
    res = []
    for kind, no, title, body in split_lessons(text):
        han, vi = parse_title(title)
        res.append({
            'kind': 'dialogue', 'no': no, 'titleHan': han, 'titleVi': vi,
            'sentences': parse_dialogue_with_stage(section(body, '对话')),
            'vocab': parse_vocab(section(body, '生词')),
            'grammar': parse_grammar(section(body, '语法点')),
        })
    return res

files = [
    ('HSK3-HoiThoai-CauLong-78.md', 'A'),      # 7,8  云英-德盛
    ('HSK3-HoiThoai-TruotBang-910.md', 'B'),   # 9,10 教练/林宇/苏晴
    ('HSK3-HoiThoai-TruotBang-1113.md', 'C'),  # 11,12,13 苏晴/林宇
]
all_lessons = []
for fn, _ in files:
    all_lessons += parse_file(f'{SP}/{fn}')
all_lessons.sort(key=lambda L: L['no'])

issues = []
for L in all_lessons:
    if len(L['sentences']) < 3: issues.append((L['no'], 'FEW_SENT'))
    if not L['grammar']: issues.append((L['no'], 'NO_GRAMMAR'))
    for s in L['sentences']:
        src = (s['speaker'] + '：' if s['speaker'] else '') + s['han']
        s['draft_pinyin'] = sent_pinyin(src)
        if not re.search(r'[一-鿿]', s['han']): issues.append((L['no'], 'NONHAN', s['han'][:20]))
print('dialogues:', len(all_lessons), '| nos:', [L['no'] for L in all_lessons])
print('issues:', issues)
for L in all_lessons:
    sp = sorted({s['speaker'] for s in L['sentences']})
    narr = sum(1 for s in L['sentences'] if not s['speaker'])
    print(f"  đối thoại {L['no']}: {len(L['sentences'])} dòng ({narr}旁白), speakers={sp}, vocab={len(L['vocab'])}, grammar={len(L['grammar'])}")

json.dump({'hsk3ht2': all_lessons}, open(f'{SP}/parsed_hsk3ht2.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

# vocab
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
          open(f'{SP}/batches/vocab_hsk3ht2_1.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

# sentence batches by theme
batches = {'A': [7, 8], 'B': [9, 10], 'C': [11, 12, 13]}
for key, nos in batches.items():
    part = [L for L in all_lessons if L['no'] in nos]
    out = []
    for L in part:
        out.append({
            'group': 'hsk3ht2', 'no': L['no'], 'titleHan': L['titleHan'], 'titleVi': L['titleVi'],
            'grammar_names': [g['name'] for g in L['grammar']],
            'grammar_details': L['grammar'],
            'sentences': [{'idx': j+1, 'speaker': s['speaker'], 'han': s['han'],
                           'pinyin_source': '', 'pinyin_draft': s['draft_pinyin']}
                          for j, s in enumerate(L['sentences'])],
        })
    json.dump(out, open(f'{SP}/batches/sent_hsk3ht2_{key}.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print(f'sent_hsk3ht2_{key}:', nos, sum(len(L["sentences"]) for L in part), 'dòng')
