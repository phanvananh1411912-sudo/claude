import json, re, sys

SP = '/tmp/claude-0/-home-user-claude/8d38f015-ed38-5363-ae81-d0cc7e396864/scratchpad'

def split_lessons(text):
    parts = re.split(r'(?m)^## (课文|对话)(\d+)\s*·\s*(.+)$', text)
    lessons = []
    for i in range(1, len(parts), 4):
        kind, no, title, body = parts[i], int(parts[i+1]), parts[i+2].strip(), parts[i+3]
        lessons.append((kind, no, title, body))
    return lessons

def section(body, name):
    m = re.search(r'(?m)^### %s\s*$(.*?)(?=^### |^## |^# |\Z)' % name, body, re.S)
    return m.group(1) if m else ''

def parse_title(title):
    m = re.match(r'《(.+?)》\s*[\(（](.+?)[\)）]', title)
    if m: return m.group(1).strip(), m.group(2).strip()
    m = re.match(r'《(.+?)\s*[\(（](.+?)[\)）]\s*》', title)
    if m: return m.group(1).strip(), m.group(2).strip()
    return title, ''

def parse_sentences(sec, dialogue):
    lines = [l.strip() for l in sec.splitlines() if l.strip() and not l.strip().startswith('>')]
    out = []
    for l in lines:
        if dialogue:
            m = re.match(r'\*\*(.+?)\*\*\s*[：:]\s*(.*)', l)
            if m:
                out.append({'speaker': m.group(1), 'han': m.group(2), 'pinyin': ''})
            elif out and not l.startswith('*'):
                out[-1]['han'] += l
        else:
            if re.match(r'^\*[^*].*\*$', l):
                if out: out[-1]['pinyin'] = l.strip('*').strip()
            else:
                out.append({'han': l, 'pinyin': ''})
    return out

def parse_vocab(sec):
    out = []
    for l in sec.splitlines():
        l = l.strip()
        if not l.startswith('|'): continue
        cells = [c.strip() for c in l.strip('|').split('|')]
        if not cells or cells[0] in ('词语', '') or set(cells[0]) <= set('-— :'): continue
        if len(cells) == 3:
            py = re.sub(r'[\(（]\s*HSK\d\s*[\)）]', '', cells[1]).strip()
            out.append({'word': cells[0], 'pinyin': py, 'meaning': cells[2]})
        elif len(cells) == 2:
            out.append({'word': cells[0], 'pinyin': '', 'meaning': cells[1]})
    return out

def parse_grammar(sec):
    out = []
    for l in sec.splitlines():
        l = l.strip()
        m = re.match(r'-\s*\*\*(.+?)\*\*\s*[：:]\s*(.*)', l)
        if not m: continue
        name, rest = m.group(1).strip(), m.group(2).strip()
        if '→' in rest:
            ex, expl = rest.split('→', 1)
            out.append({'name': name, 'example': ex.strip(), 'meaning': expl.strip()})
        else:
            out.append({'name': name, 'example': '', 'meaning': rest})
    return out

def parse_file(path, dialogue_kind):
    text = open(path, encoding='utf-8').read()
    result = []
    for kind, no, title, body in split_lessons(text):
        dlg = kind == '对话'
        han, vi = parse_title(title)
        sec_name = '对话' if dlg else '课文'
        result.append({
            'kind': 'dialogue' if dlg else 'reading',
            'no': no, 'titleHan': han, 'titleVi': vi,
            'sentences': parse_sentences(section(body, sec_name), dlg),
            'vocab': parse_vocab(section(body, '生词')),
            'grammar': parse_grammar(section(body, '语法点')),
        })
    return result

hsk1 = parse_file(f'{SP}/HSK1-Full-40bai.md', False)
hsk2 = parse_file(f'{SP}/HSK2-Full-80bai.md', True)
data = {'hsk1': hsk1,
        'hsk2doc': [l for l in hsk2 if l['kind'] == 'reading'],
        'hsk2ht': [l for l in hsk2 if l['kind'] == 'dialogue']}
json.dump(data, open(f'{SP}/parsed_lessons.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

for grp, lessons in data.items():
    print(grp, len(lessons))
    for L in lessons:
        ns, nv, ng = len(L['sentences']), len(L['vocab']), len(L['grammar'])
        npy = sum(1 for s in L['sentences'] if s['pinyin'])
        flags = []
        if ns < 3: flags.append('FEW_SENT')
        if nv < 3: flags.append('FEW_VOCAB')
        if ng == 0: flags.append('NO_GRAMMAR')
        if grp == 'hsk1' and L['no'] <= 20 and npy != ns: flags.append(f'PINYIN {npy}/{ns}')
        for s in L['sentences']:
            if not re.search(r'[一-鿿]', s['han']): flags.append('NONHAN:' + s['han'][:20])
        if flags: print(' ', L['no'], L['titleHan'], ns, nv, ng, flags)
print('totals:', {g: (sum(len(l['sentences']) for l in ls), sum(len(l['vocab']) for l in ls), sum(len(l['grammar']) for l in ls)) for g, ls in data.items()})
