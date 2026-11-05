#!/usr/bin/env python3
"""MAGI-007 Obsidian 금고 생성기 — 봉인 묶음(R1·R3 자리별 · R2·R4 종합자)의 edges.json 을 읽어
질문(A-k) · 합의(S-k) · 자리(허브) · 결정 노트와 INDEX.md · EDGES.md 를 만든다. 봉인 묶음 본문은 고치지 않는다
(예외: R3_laptop2/note.md 의 깨진 상대 링크 넷 — laptop2 00:38 정정표, tar 원본은 불변).
실행: python3 build_graph.py  (어디서든 — 경로는 이 파일 위치 기준)."""
import json, os, re, glob, collections, datetime
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..'))            # MAGI-007_obsidian
MAGI = os.path.abspath(os.path.join(ROOT, '..'))            # MAGI
ZIF = os.path.abspath(os.path.join(MAGI, '..'))             # 21_ZIF69_MTV
REPO = os.path.abspath(os.path.join(ZIF, '..'))
TODAY = '2026-11-05'
SEATS = {'laptop': ('Melchior', 'M', '랩탑', '이론'), 'laptop2': ('Balthasar', 'B', 'laptop2', '실용'),
         'hkhome': ('Caspar', 'C', 'HKHOME', '비평'), 'cloud': ('Synthesizer', 'SYN', '클라우드', '종합')}
PREFIX2SEAT = {'M': 'laptop', 'B': 'laptop2', 'C': 'hkhome'}
R1DOC = {'laptop': 'MAGI-007_R1_laptop.md', 'laptop2': 'MAGI-007_R1_laptop2.md', 'hkhome': 'MAGI-007_R1_hkhome.md'}
R3DOC = {'laptop': 'MAGI-007_R3_laptop.md', 'laptop2': 'MAGI-007_R3_laptop2.md', 'hkhome': 'MAGI-007_R3_hkhome.md'}

def rd(p): return open(p, encoding='utf-8').read()
def wr(p, s):
    os.makedirs(os.path.dirname(p), exist_ok=True); open(p, 'w', encoding='utf-8').write(s)
def rel(frm_file, to_path):
    return os.path.relpath(to_path, os.path.dirname(frm_file)).replace(os.sep, '/')
def L(frm_file, to_path, text):
    text = str(text).replace('[', '［').replace(']', '］')   # 링크 글 안의 대괄호는 마크다운 링크를 깨뜨림
    return f'[{text}]({rel(frm_file, to_path)})'
def clip(s, n): s = ' '.join(s.split()); return s if len(s) <= n else s[:n - 1] + '…'
def esc(s): return str(s).replace('|', '∣')
def nowiki(s): return re.sub(r'\[\[([^\]]+)\]\]', r'`\1`', str(s))

# ---------- edges ----------
def load_edges(bundle):
    p = os.path.join(ROOT, bundle, 'edges.json')
    if not os.path.exists(p): return []
    e = json.load(open(p, encoding='utf-8'))
    if isinstance(e, dict): e = e.get('edges', [])
    out = []
    for x in e:
        out.append({'from': str(x.get('from')), 'to': str(x.get('to')), 'type': str(x.get('type', '')), 'note': str(x.get('note', '') or ''), 'bundle': bundle})
    return out
BUNDLES = ['R1_laptop', 'R1_laptop2', 'R1_hkhome', 'R2_cloud', 'R3_laptop', 'R3_laptop2', 'R3_hkhome', 'R4_cloud']
EDGES = {b: load_edges(b) for b in BUNDLES}
ALL = [e for b in BUNDLES for e in EDGES[b]]
def seat_of_bundle(b): return b.split('_', 1)[1]

# ---------- labels ----------
def bold_labels(path):
    """**ID rest** 꼴의 굵은 머리를 {ID: rest} 로."""
    out = {}
    if not os.path.exists(path): return out
    for line in rd(path).splitlines():
        m = re.search(r'\*\*((?:[MBCD])-[A-Za-z0-9]+)(?:\s*(?:←\s*A-\d+)?)([^*]*?)\*\*(.*)$', line)
        if not m: continue
        nid = m.group(1); rest = m.group(2).strip(' ·.—-:')
        if not rest: rest = m.group(3).strip(' ·.—-:')          # "**M-1** 본문…" 꼴은 굵음 뒤의 글이 라벨
        if rest and not out.get(nid): out[nid] = clip(rest, 110)
    return out
LABEL = {}
for seat in ('laptop', 'laptop2', 'hkhome'):
    pre = SEATS[seat][1]
    lab = bold_labels(os.path.join(ROOT, f'R1_{seat}', 'note.md'))
    if seat == 'laptop':  # 표 "| M-1. 텍스트 |"
        for m in re.finditer(r'\|\s*(M-[A-Za-z0-9]+)\.\s*([^|]+)\|', rd(os.path.join(MAGI, R1DOC[seat]))):
            if not lab.get(m.group(1)): lab[m.group(1)] = clip(m.group(2), 110)
    LABEL[('R1', seat)] = lab
    lab3 = bold_labels(os.path.join(ROOT, f'R3_{seat}', 'note.md'))
    for m in re.finditer(r'^###\s+(D-\d+)\s*←\s*(A-\d+)\s*(.*)$', rd(os.path.join(MAGI, R3DOC[seat])), re.M):
        lab3.setdefault(m.group(1), clip(f'← {m.group(2)} {m.group(3)}', 110))
    LABEL[('R3', seat)] = lab3

# A-k from R2
R2 = rd(os.path.join(MAGI, 'MAGI-007_R2_attack.md')).splitlines()
A = {}
sec = ''
for i, line in enumerate(R2):
    if line.startswith('## '): sec = line[3:].strip()
    m = re.match(r'^###\s+(A-\d+)\s*→\s*(.*)$', line)
    if m:
        j = i + 1
        while j < len(R2) and not R2[j].strip(): j += 1
        body = R2[j].strip() if j < len(R2) else ''
        tags = re.findall(r'`\[[^\]]+\]`', body); stars = body.count('★')
        plain = re.sub(r'`\[[^\]]+\]`', '', body).replace('★', '')
        plain = re.sub(r'^\s*[—-]\s*', '', plain.strip()).replace('**', '').replace('`', '')
        plain = re.sub(r'\[\[([^\]]+)\]\]', r'\1', plain)
        title = clip(plain, 90)
        A[m.group(1)] = {'targets': m.group(2).strip(), 'body': body, 'tags': ' '.join(tags), 'stars': '★' * stars, 'title': clip(title, 90), 'section': sec}
# S-k from R4 §4-1
R4 = rd(os.path.join(MAGI, 'MAGI-007_ligand-modification.md')).splitlines()
S = {}
in41 = False
for line in R4:
    if line.startswith('### 4-1'): in41 = True; continue
    if in41 and line.startswith('### 4-2'): break
    m = re.match(r'^(\d)\.\s+\*\*(.+?)\*\*(.*)$', line)
    if in41 and m: S[f'S-{m.group(1)}'] = {'title': clip(m.group(2), 110), 'body': clip(m.group(3), 420)}
DECS = {'DEC-ZNBDT-C1': '다음 계산 = 열린 자리 4,8-(C≡CH)₂ (R4 §5-1 · 사용자 승인 11-05 00:4x) → ZNBDT-C1 등록 → **관문 (0a)(0b) 탈락 01:39** · 전제 오류 종합자 자백(ASSIGN_ZNBDT_C1 §5) → 닫힘',
        'DEC-′1': '′1 순위표 두 개 재생성 **끝 12:13** — −C₂H₅ 헨리 154.3 → 막음 127.0 ± 4.0(3D 헨리 1위 사라짐 · −Br 과 한 덩어리) · 정정 전 표 보존(ASSIGN_MAGI7_AMEND)',
        'DEC-′2': '′2 관문 ⑤ 서술 열 **등록** — 다음 관문 ⑤ 실행 때 HKHOME 이 추가', 'DEC-′3': '′3 자 이름 소급 표기 **끝** — 5.55 = 씨앗 SEM 자 · 씨앗 SD 자 2.26',
        'DEC-′4': '′4 mslm050 = e0 × 3씨앗 **재확인** — 38.76 ± 0.57 재계산 · 실현 평균 39.71 병기', 'DEC-′5': '′5 점검⓪ **계산 끝** — f_bib 0.277 대 f₀ 0.549(0.51) → 사이 · 서술만 · bib 빌더 미등록',
        'DEC-′6': '′6 후순위 기록 **끝** — CN/Br 혼합(배열 둘) · −NO₂ 열린 자리(관문 통과 → 가능성 표)',
        'DEC-ZNBDT-C2': '무극성 −CN 계산 대조(사용자 02:0x · HKHOME 등록 02:06) → 03:04 완주 → **"보정 방식에 민감 — 판별 불가"**(U 중간 f 0.55 · I 극성) · 종합자 재계산 일치',
        'DEC-ZNBDT-C2-L': '사용자 결정 ②③(11:5x) → 민감도 판 L(리간드 분산) + #2 apolarU 323 K **등록 12:0x**(ASSIGN_C2 §7) → HKHOME 7작업(착수 대기)',
        'DEC-#1': '후속 #1 밀도 격자(laptop2 04:08) → 종합자 서술: N₂ 비움 자리는 막대 둘레(97 %) · 전하는 CO₂ 를 모아 더 밂(0.60→0.50×)',
        'DEC-#3': '후속 #3 −NO₂ 열린 자리 선별 → **관문 (0a)(0b) 통과**(HKHOME 12:07 · 종합자 재현) → 가능성 표 · 다음 걸음 사용자',
        'USER-21:2x-(가)': '사용자 결정 11-04 21:2x — A(격자 이완)를 측정 사실로 닫음 · PACMAN 순전하 |q| ≤ 1e-3',
        'SYN-sealed': '종합자 봉인 예측(11:09 · sha256 bbbc71b7…) — 결정과 불일치(§9-10 ①)', 'SYN-brief-§10-3': '브리핑 v3 §10-3 — C₂H₅ 92.99 전 치환판 혼용(종합자 자백 A-1)'}

# ---------- node resolution ----------
G = os.path.join(ROOT, 'graph')
def qpath(k): return os.path.join(G, 'questions', f'{k}.md')
def spath(k): return os.path.join(G, 'consensus', f'{k}.md')
def hub(seat): return os.path.join(G, 'seats', f'{SEATS[seat][0]}.md')
DECP = os.path.join(G, 'decisions.md')
def resolve(nid, bundle):
    """→ (표시 글, 대상 경로 또는 None)"""
    seat_b = seat_of_bundle(bundle)
    if re.fullmatch(r'A-\d+', nid):
        return f'{nid} {A.get(nid, {}).get("title", "")}'.strip(), qpath(nid)
    if re.fullmatch(r'S-\d+', nid):
        return f'{nid} {S.get(nid, {}).get("title", "")}'.strip(), spath(nid)
    if nid.startswith('DEC-') or nid.startswith('USER-'):
        return f'{nid} {clip(DECS.get(nid, ""), 60)}'.strip(), DECP
    if nid.startswith('SYN-sealed'): return nid, os.path.join(MAGI, 'MAGI-007_sealed_prediction_cloud.md')
    if nid.startswith('SYN-brief'): return nid, os.path.join(MAGI, 'MAGI-007_brief.md')
    if nid.startswith('FINAL_RANKING'): return nid, os.path.join(REPO, '23_SCREENING', 'FINAL_RANKING_20260930.md')
    if nid.startswith('E6-'): return f'{nid} (R4 §6-2 B 등록 읽기)', os.path.join(MAGI, 'MAGI-007_ligand-modification.md')
    if nid.startswith('src:'): return nid, os.path.join(ROOT, bundle, 'sources.md')
    if nid == '§3': return 'R3 §3 (Melchior)', os.path.join(MAGI, R3DOC['laptop'])
    m = re.fullmatch(r'D-(\d+)', nid)
    if m and seat_b in R3DOC:
        lab = LABEL[('R3', seat_b)].get(nid, '')
        return f'{SEATS[seat_b][0]} {nid} {lab}'.strip(), os.path.join(ROOT, f'R3_{seat_b}', 'note.md')
    m = re.fullmatch(r'([MBC])-D-(\d+)', nid)
    if m:
        seat = PREFIX2SEAT[m.group(1)]; d = f'D-{m.group(2)}'
        return f'{SEATS[seat][0]} {d} {LABEL[("R3", seat)].get(d, "")}'.strip(), os.path.join(ROOT, f'R3_{seat}', 'note.md')
    m = re.fullmatch(r'([MBC])-R3-(.*)', nid)
    if m:
        seat = PREFIX2SEAT[m.group(1)]
        return f'{SEATS[seat][0]} R3 {m.group(2)}', os.path.join(MAGI, R3DOC[seat])
    m = re.fullmatch(r'([MBC])-(.*)', nid)
    if m:
        seat = PREFIX2SEAT[m.group(1)]
        lab = LABEL[('R1', seat)].get(nid, '')
        return f'{SEATS[seat][0]} {nid} {lab}'.strip(), os.path.join(ROOT, f'R1_{seat}', 'note.md')
    return nid, None
def node_link(frm, nid, bundle):
    text, path = resolve(nid, bundle)
    return L(frm, path, clip(text, 120)) if path else clip(text, 120)
def seat_of_node(nid, bundle):
    if re.fullmatch(r'D-\d+', nid) or nid == '§3' or nid.startswith('src:'): return seat_of_bundle(bundle)
    m = re.match(r'([MBC])-', nid)
    if m: return PREFIX2SEAT[m.group(1)]
    if nid.startswith(('A-', 'S-', 'SYN', 'DEC', 'USER', 'E6')): return 'cloud'
    return None

def fm(title, tags, aliases=None):
    s = f'---\ntitle: "{title}"\ndate: {TODAY}\ntags: [{", ".join(tags)}]\n'
    if aliases: s += f'aliases: [{", ".join(aliases)}]\n'
    return s + '---\n\n'

# ---------- question pages ----------
for k, a in A.items():
    p = qpath(k); out = fm(f'{k} · {a["title"]}', ['MAGI-007', 'graph', 'question'], [k])
    out += f'# {k} · {a["title"]}\n\n{nowiki(clip(a["body"], 600))}\n\n'
    out += f'원문: {L(p, os.path.join(MAGI, "MAGI-007_R2_attack.md"), "R2 질의문")} §{clip(a["section"], 40)} · 그래프 판 {L(p, os.path.join(ROOT, "R2_cloud", "note.md"), "R2_cloud")} · 겨눈 곳: {nowiki(esc(a["targets"]))}\n\n'
    out += '## 공격 대상 (R2 간선 · 종합자 → 자리)\n\n'
    rows = [e for e in EDGES['R2_cloud'] if e['from'] == k]
    out += ''.join(f'- **{e["type"]}** → {node_link(p, e["to"], "R2_cloud")}' + (f' — {esc(e["note"])}' if e['note'] else '') + '\n' for e in rows) or '- (간선 없음)\n'
    out += '\n## 수비 (R3 간선 · 자리 → 질문)\n\n'
    got = False
    for b in ('R3_laptop', 'R3_laptop2', 'R3_hkhome'):
        for e in EDGES[b]:
            if e['to'] == k:
                got = True
                out += f'- **{e["type"]}** ← {node_link(p, e["from"], b)}' + (f' — {esc(e["note"])}' if e['note'] else '') + f' · {L(p, os.path.join(MAGI, R3DOC[seat_of_bundle(b)]), "본문")}\n'
    if not got: out += '- 답한 자리 없음 → R2 §7 규칙으로 **수용**으로 읽음\n'
    out += '\n## 종합에서 (R4 간선)\n\n'
    rows = [e for e in EDGES['R4_cloud'] if e['to'] == k or e['from'] == k]
    out += ''.join(f'- {node_link(p, e["from"], "R4_cloud")} **{e["type"]}** → {node_link(p, e["to"], "R4_cloud")}' + (f' — {esc(e["note"])}' if e['note'] else '') + '\n' for e in rows) or '- (R4 에서 직접 인용 없음)\n'
    nxt = f'A-{int(k[2:]) + 1}'; prv = f'A-{int(k[2:]) - 1}'
    nav = [L(p, qpath(prv), prv)] if prv in A else []
    nav += [L(p, qpath(nxt), nxt)] if nxt in A else []
    out += f'\nRelated: {L(p, hub("cloud"), "종합자")} · {L(p, os.path.join(MAGI, "MAGI-007_ligand-modification.md"), "R4 종합")} · ' + ' · '.join(nav) + f' · {L(p, os.path.join(ROOT, "INDEX.md"), "INDEX")}\n'
    wr(p, out)

# ---------- consensus pages ----------
for k, s in S.items():
    p = spath(k); out = fm(f'{k} · {s["title"]}', ['MAGI-007', 'graph', 'consensus'], [k])
    out += f'# {k} · {s["title"]}\n\n{s["body"]}\n\n원문: {L(p, os.path.join(MAGI, "MAGI-007_ligand-modification.md"), "R4 종합 §4-1")} · 그래프 판 {L(p, os.path.join(ROOT, "R4_cloud", "note.md"), "R4_cloud")}\n\n'
    out += '## 근거 · 인용 (R4 간선 · 합의 → 자리 · 질문)\n\n'
    rows = [e for e in EDGES['R4_cloud'] if e['from'] == k]
    bys = collections.defaultdict(list)
    for e in rows: bys[seat_of_node(e['to'], 'R4_cloud') or 'etc'].append(e)
    for seat in ('laptop', 'laptop2', 'hkhome', 'cloud', 'etc'):
        if seat not in bys: continue
        name = SEATS[seat][0] if seat in SEATS else '기타'
        out += f'**{name}**\n\n' + ''.join(f'- **{e["type"]}** → {node_link(p, e["to"], "R4_cloud")}' + (f' — {esc(e["note"])}' if e['note'] else '') + '\n' for e in bys[seat]) + '\n'
    rows_in = [e for e in EDGES['R4_cloud'] if e['to'] == k]
    if rows_in: out += '## 이 합의를 가리키는 것\n\n' + ''.join(f'- {node_link(p, e["from"], "R4_cloud")} **{e["type"]}**' + (f' — {esc(e["note"])}' if e['note'] else '') + '\n' for e in rows_in) + '\n'
    out += f'Related: {L(p, hub("cloud"), "종합자")} · ' + ' · '.join(L(p, spath(o), o) for o in S if o != k) + f' · {L(p, os.path.join(ROOT, "INDEX.md"), "INDEX")}\n'
    wr(p, out)

# ---------- decisions ----------
p = DECP; out = fm('MAGI-007 결정 · 사용자 결정 노드', ['MAGI-007', 'graph', 'decision'])
out += '# MAGI-007 결정 노드\n\nR4 §5 의 권고 · 사용자 결정 · 종합자 봉인 예측. 상태는 11-05 02:3x 기준.\n\n| 노드 | 내용 · 상태 |\n|---|---|\n'
for k, v in DECS.items(): out += f'| `{k}` | {esc(v)} |\n'
out += '\n## 간선 (R4)\n\n'
for e in EDGES['R4_cloud']:
    if e['from'].startswith(('DEC', 'USER', 'SYN')) or e['to'].startswith(('DEC', 'USER')):
        out += f'- {node_link(p, e["from"], "R4_cloud")} **{e["type"]}** → {node_link(p, e["to"], "R4_cloud")}' + (f' — {esc(e["note"])}' if e['note'] else '') + '\n'
out += '\n## R4 뒤 (보완 단계)\n\n'
out += f'- ZNBDT-C1 — {L(p, os.path.join(ZIF, "ASSIGN_ZNBDT_C1_20261105.md"), "등록 · §5 판정(관문 탈락)")}\n- ZNBDT-C2 — {L(p, os.path.join(ZIF, "ASSIGN_ZNBDT_C2_20261105.md"), "무극성 −CN 계산 대조 · §5 HKHOME · §6 종합자 대조 · §7 C2-L 등록")} · {L(p, os.path.join(ZIF, "ASSIGN_ZNBDT_C2_FOLLOWUP_20261105.md"), "후속 #1 밀도 서술(§1-1) · #2 · #3 관문 통과(§3-1) · 밤샘 결정표")}\n- 등록 보완 ′1~′6 — {L(p, os.path.join(ZIF, "ASSIGN_MAGI7_AMEND_20261105.md"), "ASSIGN_MAGI7_AMEND_20261105.md")}(순위표 재생성 · 점검⓪ · 자 이름)\n- 규약 {L(p, os.path.join(ZIF, "MAGI_20260905.md"), "§11-5 라운드 중 격리 · 보완 단계")}\n- 아침 결정 ①~⑤(11-05 08:0x 보고 → ① 10:2x · ②~⑤ 11:5x 전부 권고안) — {L(p, os.path.join(ZIF, "COMMS", "cloud.md"), "종합자 우편함")}\n'
out += f'\nRelated: {L(p, hub("cloud"), "종합자")} · {L(p, os.path.join(MAGI, "MAGI-007_ligand-modification.md"), "R4 §5")} · {L(p, os.path.join(ROOT, "INDEX.md"), "INDEX")}\n'
wr(p, out)

# ---------- seat hubs ----------
def assets(bundle):
    return sorted(glob.glob(os.path.join(ROOT, bundle, 'assets', '*')))
for seat in ('laptop', 'laptop2', 'hkhome'):
    name, pre, machine, axis = SEATS[seat]; p = hub(seat)
    out = fm(f'{name} ({machine} · {axis})', ['MAGI-007', 'graph', 'seat', name], [name])
    out += f'# {name} — {machine} · {axis}\n\n'
    out += f'- R1: {L(p, os.path.join(ROOT, f"R1_{seat}", "note.md"), "그래프 판")} · {L(p, os.path.join(ROOT, f"R1_{seat}", "sources.md"), "참고 자료")} · {L(p, os.path.join(MAGI, R1DOC[seat]), "본문")}'
    if seat == 'laptop': out += f' · {L(p, os.path.join(ROOT, "R1_laptop_v1224", "note.md"), "12:24 판(보존)")}'
    out += ''.join(f' · {L(p, a, "자산 " + os.path.basename(a))}' for a in assets(f'R1_{seat}')) + '\n'
    out += f'- R3: {L(p, os.path.join(ROOT, f"R3_{seat}", "note.md"), "그래프 판")} · {L(p, os.path.join(ROOT, f"R3_{seat}", "sources.md"), "참고 자료")} · {L(p, os.path.join(MAGI, R3DOC[seat]), "본문")}'
    out += ''.join(f' · {L(p, a, "자산 " + os.path.basename(a))}' for a in assets(f'R3_{seat}')) + '\n\n'
    out += '## R1 주장 노드\n\n'
    ids = sorted({e['from'] for e in EDGES[f'R1_{seat}']} | {e['to'] for e in EDGES[f'R1_{seat}']} | set(LABEL[('R1', seat)]), key=lambda x: (len(x), x))
    for nid in ids:
        if nid.startswith('src:'): continue
        out += f'- **{nid}** {esc(LABEL[("R1", seat)].get(nid, ""))}\n'
    out += '\n## R1 안의 간선\n\n| from | → | to | 종류 | 메모 |\n|---|---|---|---|---|\n'
    for e in EDGES[f'R1_{seat}']: out += f'| {e["from"]} | → | {esc(e["to"])} | {e["type"]} | {esc(clip(e["note"], 90))} |\n'
    out += '\n## 받은 질의 (R2)\n\n'
    for e in EDGES['R2_cloud']:
        if seat_of_node(e['to'], 'R2_cloud') == seat:
            out += f'- {node_link(p, e["from"], "R2_cloud")} **{e["type"]}** → {esc(e["to"])}' + (f' — {esc(e["note"])}' if e['note'] else '') + '\n'
    out += '\n## 수비 (R3 · D-k → A-k)\n\n'
    for e in EDGES[f'R3_{seat}']:
        tgt = node_link(p, e['to'], f'R3_{seat}') if not e['to'].startswith('A-') else L(p, qpath(e['to']), e['to'] + ' ' + A.get(e['to'], {}).get('title', ''))
        out += f'- **{e["from"]}** {esc(clip(LABEL[("R3", seat)].get(e["from"], ""), 70))} **{e["type"]}** → {tgt}' + (f' — {esc(clip(e["note"], 140))}' if e['note'] else '') + '\n'
    out += '\n## 종합에서 인용 (R4)\n\n'
    for e in EDGES['R4_cloud']:
        if seat_of_node(e['to'], 'R4_cloud') == seat:
            out += f'- {node_link(p, e["from"], "R4_cloud")} **{e["type"]}** → {esc(e["to"])}' + (f' — {esc(e["note"])}' if e['note'] else '') + '\n'
    others = [L(p, hub(s2), SEATS[s2][0]) for s2 in ('laptop', 'laptop2', 'hkhome', 'cloud') if s2 != seat]
    out += f'\nRelated: {" · ".join(others)} · {L(p, os.path.join(G, "EDGES.md"), "간선 전체")} · {L(p, os.path.join(ROOT, "INDEX.md"), "INDEX")}\n'
    wr(p, out)
# synthesizer hub
p = hub('cloud'); out = fm('Synthesizer (클라우드 · 종합 · 공격적 검증 · 질문)', ['MAGI-007', 'graph', 'seat', 'Synthesizer'], ['종합자', 'Synthesizer'])
out += '# 종합자 — 클라우드 · 종합 · 공격적 검증자 · 질문자\n\n'
out += f'- 브리핑 v3 {L(p, os.path.join(MAGI, "MAGI-007_brief.md"), "본문")} · 봉인 예측 {L(p, os.path.join(MAGI, "MAGI-007_sealed_prediction_cloud.md"), "평문")}(sha256 bbbc71b7…)\n'
out += f'- R2 질의: {L(p, os.path.join(ROOT, "R2_cloud", "note.md"), "그래프 판")} · {L(p, os.path.join(ROOT, "R2_cloud", "sources.md"), "참고 자료")} · {L(p, os.path.join(MAGI, "MAGI-007_R2_attack.md"), "본문")}\n'
out += f'- R4 종합: {L(p, os.path.join(ROOT, "R4_cloud", "note.md"), "그래프 판")} · {L(p, os.path.join(ROOT, "R4_cloud", "sources.md"), "참고 자료")} · {L(p, os.path.join(MAGI, "MAGI-007_ligand-modification.md"), "본문")} · {L(p, DECP, "결정 노드")}\n\n'
out += f'- 흐름: {L(p, os.path.join(G, "FLOW.md"), "사고과정 흐름")} · {L(p, os.path.join(G, "TIMELINE.md"), "타임라인")}\n\n'
out += '## 질문 17 (R2)\n\n' + ''.join(f'- {L(p, qpath(k), k)} {a["stars"]} {esc(a["title"])} — 수비 {sum(1 for b in ("R3_laptop", "R3_laptop2", "R3_hkhome") for e in EDGES[b] if e["to"] == k)}건\n' for k, a in A.items())
out += '\n## 합의 7 (R4)\n\n' + ''.join(f'- {L(p, spath(k), k)} {esc(s["title"])}\n' for k, s in S.items())
out += '\n## 종합자 자신에게 건 간선\n\n' + ''.join(f'- {node_link(p, e["from"], e["bundle"])} **{e["type"]}** → {node_link(p, e["to"], e["bundle"])}' + (f' — {esc(e["note"])}' if e['note'] else '') + '\n' for e in ALL if e['to'].startswith('SYN') or e['from'].startswith('SYN'))
out += f'\nRelated: {L(p, hub("laptop"), "Melchior")} · {L(p, hub("laptop2"), "Balthasar")} · {L(p, hub("hkhome"), "Caspar")} · {L(p, os.path.join(G, "EDGES.md"), "간선 전체")} · {L(p, os.path.join(ROOT, "INDEX.md"), "INDEX")}\n'
wr(p, out)

# ---------- EDGES.md ----------
p = os.path.join(G, 'EDGES.md'); out = fm('MAGI-007 간선 전체', ['MAGI-007', 'graph', 'edges'])
out += f'# MAGI-007 간선 전체 ({len(ALL)}개 · 묶음 {len(BUNDLES)})\n\n봉인 묶음의 `edges.json` 을 그대로 옮긴 표. 종류 ∈ 공격 · 수용 · 수정 · 반박 · 인용 · 근거.\n\n'
cnt = collections.Counter()
for e in ALL:
    a, b = seat_of_node(e['from'], e['bundle']), seat_of_node(e['to'], e['bundle'])
    if a and b and a != b: cnt[(a, b, e['type'])] += 1
out += '## 자리 사이 흐름 (자리 안 간선 제외)\n\n```mermaid\ngraph LR\n'
for s2 in ('laptop', 'laptop2', 'hkhome', 'cloud'): out += f'  {SEATS[s2][1]}["{SEATS[s2][0]} · {SEATS[s2][2]}"]\n'
for (a, b, t), n in sorted(cnt.items()): out += f'  {SEATS[a][1]} -->|{t} {n}| {SEATS[b][1]}\n'
out += '```\n\n'
for b in BUNDLES:
    out += f'## {b} ({len(EDGES[b])})\n\n| from | 종류 | to | 메모 |\n|---|---|---|---|\n'
    for e in EDGES[b]: out += f'| {node_link(p, e["from"], b)} | {e["type"]} | {node_link(p, e["to"], b)} | {esc(clip(e["note"], 110))} |\n'
    out += '\n'
out += f'Related: {L(p, hub("cloud"), "종합자")} · {L(p, os.path.join(ROOT, "INDEX.md"), "INDEX")}\n'
wr(p, out)

# ---------- INDEX.md ----------
p = os.path.join(ROOT, 'INDEX.md'); out = fm('MAGI-007 Obsidian 금고', ['MAGI-007', 'index'], ['MAGI-007 금고'])
out += '# MAGI-007 Obsidian 금고 — 리간드 개질 토론(E · A · B 조건)의 자리별 참고 자료와 종합자 질문\n\n'
out += '**여는 법**: 이 폴더의 링크 중 `../../`·`../../../` 로 나가는 것은 저장소 문서를 가리킵니다. Obsidian 에서 그 링크까지 따라가려면 **`21_ZIF69_MTV/` (또는 저장소 뿌리)를 금고로 여십시오**. 이 폴더만 열면 묶음 안 링크와 그래프 층만 보입니다. 봉인 원본은 각 `R*_<기기>.tar.gz`(sha256 은 `COMMS/<기기>.md` 해시 줄과 같음) 이고, 풀린 폴더는 금고용 사본입니다 — 사본 중 손댄 곳은 `R3_laptop2/note.md` 의 Related 링크 넷(laptop2 00:38 정정표)뿐입니다.\n\n'
out += '## 그래프 층 (종합자가 edges.json 에서 생성 · `graph/build_graph.py`)\n\n'
out += f'- {L(p, os.path.join(G, "FLOW.md"), "사고과정 흐름")}: 절차 흐름도 · 논리 흐름도 · 마디 여섯 · 열린 것 — **여기서 시작**\n- {L(p, os.path.join(G, "TIMELINE.md"), "타임라인")}: 11-03 등록 → 11-05 보완 단계, 시각 · 누가 · 어디\n'
out += f'- {L(p, hub("cloud"), "종합자")}: 질문 17 · 합의 7 · 봉인 예측 · 결정\n'
for s2 in ('laptop', 'laptop2', 'hkhome'): out += f'- {L(p, hub(s2), SEATS[s2][0] + " (" + SEATS[s2][2] + " · " + SEATS[s2][3] + ")")}: R1 주장 노드 · 받은 질의 · 수비 · 종합 인용\n'
out += f'- {L(p, DECP, "결정 노드")}: R4 §5 권고 · 사용자 결정 · R4 뒤 ZNBDT-C1 / C2\n- {L(p, os.path.join(G, "EDGES.md"), "간선 전체")}: {len(ALL)} 간선 표와 자리 사이 흐름 그림\n'
out += '\n### 질문 (R2 · 종합자 → 자리)\n\n' + ''.join(f'- {L(p, qpath(k), k + " · " + a["title"])}: {a["stars"] or "—"} · {clip(a["section"], 30)}\n' for k, a in A.items())
out += '\n### 합의 (R4)\n\n' + ''.join(f'- {L(p, spath(k), k + " · " + s["title"])}\n' for k, s in S.items())
out += '\n## 자리별 봉인 묶음 (제출 해시 = 봉인 해시 · 종합자 대조 11-05 01:3x)\n\n'
HASH = {'R1_laptop': '822bfbd2', 'R1_laptop_v1224': 'ee5be14f (12:24 판 · 보존)', 'R1_laptop2': '038401ab', 'R1_hkhome': '8e982397', 'R3_laptop': '0c113d9f', 'R3_laptop2': 'dbb15c1f', 'R3_hkhome': '42a6498c'}
for b in ('R1_laptop', 'R1_laptop_v1224', 'R1_laptop2', 'R1_hkhome', 'R3_laptop', 'R3_laptop2', 'R3_hkhome'):
    seat = seat_of_bundle(b).replace('_v1224', '')
    out += f'- **{b}** ({SEATS[seat][0]} · sha256 {HASH[b]}): {L(p, os.path.join(ROOT, b, "note.md"), "note")} · {L(p, os.path.join(ROOT, b, "sources.md"), "sources")} · `edges.json`' + ''.join(f' · {L(p, a, os.path.basename(a))}' for a in assets(b)) + f' · {L(p, os.path.join(ROOT, b + ".tar.gz"), "tar 원본")}\n'
out += '\n## 종합자 자료\n\n'
for b, t in (('R2_cloud', 'R2 질의 17건의 그래프 판'), ('R4_cloud', 'R4 종합의 그래프 판')):
    out += f'- **{b}**: {L(p, os.path.join(ROOT, b, "note.md"), "note")} · {L(p, os.path.join(ROOT, b, "sources.md"), "sources")} · `edges.json` — {t}\n'
out += '\n## 원문 (저장소 · 이 폴더 밖)\n\n'
for f, t in (('MAGI-007_brief.md', '브리핑 v3 — 질문 · 규율 · 시한 · 운영 제약'), ('MAGI-007_sealed_prediction_cloud.md', '종합자 봉인 예측(평문 · 공개 뒤)'), ('MAGI-007_R1_laptop.md', 'R1 Melchior'), ('MAGI-007_R1_laptop2.md', 'R1 Balthasar'), ('MAGI-007_R1_hkhome.md', 'R1 Caspar'), ('MAGI-007_R2_attack.md', 'R2 종합자 질의 A-1~A-17'), ('MAGI-007_R3_laptop.md', 'R3 Melchior'), ('MAGI-007_R3_laptop2.md', 'R3 Balthasar'), ('MAGI-007_R3_hkhome.md', 'R3 Caspar'), ('MAGI-007_ligand-modification.md', 'R4 종합 · 결정 · §10 연락 사례 · §11 보완 단계')):
    out += f'- {L(p, os.path.join(MAGI, f), f)}: {t}\n'
out += f'- {L(p, os.path.join(ZIF, "ASSIGN_ZNBDT_SUPP_20261103.md"), "ASSIGN_ZNBDT_SUPP_20261103.md")}: E · A · B 등록\n- {L(p, os.path.join(ZIF, "MAGI_20260905.md"), "MAGI_20260905.md")}: 규약(§11-2 봉인 · §11-5 격리/보완)\n'
wr(p, out)

# ---------- laptop2 R3 link fixes (vault copy only) ----------
p = os.path.join(ROOT, 'R3_laptop2', 'note.md'); s = rd(p); n = 0
for old, new in (('../../../21_ZIF69_MTV/MAGI/MAGI-007_R3_laptop2.md', '../../MAGI-007_R3_laptop2.md'), ('../../../21_ZIF69_MTV/MAGI/MAGI-007_R2_attack.md', '../../MAGI-007_R2_attack.md'), ('../../../21_ZIF69_MTV/MAGI/MAGI-007_R1_laptop2.md', '../../MAGI-007_R1_laptop2.md'), ('../R1/note.md', '../R1_laptop2/note.md')):
    if old in s: s = s.replace(old, new); n += 1
wr(p, s)
print(f'questions {len(A)} · consensus {len(S)} · edges {len(ALL)} · laptop2 links fixed {n}')
print('A titles:'); [print(' ', k, a['stars'], a['title']) for k, a in A.items()]
print('S titles:'); [print(' ', k, s['title']) for k, s in S.items()]
print('labels R1:', {s: len(LABEL[("R1", s)]) for s in ("laptop", "laptop2", "hkhome")}, 'R3:', {s: len(LABEL[("R3", s)]) for s in ("laptop", "laptop2", "hkhome")})
