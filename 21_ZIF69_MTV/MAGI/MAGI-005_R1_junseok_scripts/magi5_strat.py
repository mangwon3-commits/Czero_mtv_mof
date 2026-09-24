# -*- coding: utf-8 -*-
import json, io, zipfile, statistics as st, re, sys
import numpy as np
X = json.load(open(sys.argv[1]))
D = '/home/mangwon/mof_project/21_ZIF69_MTV/'
z = zipfile.ZipFile(D + 'core_pop_cifs.zip')

# 1) 계열 중복 제거: ASR/FSR 짝(같은 번호)은 같은 구조의 두 판 -> 하나로. 키에서 [ASR]/[FSR] 떼고 번호 유지
def fam(k):   # 연도+금속+위상+차원 = 느슨한 계열
    m = re.match(r'(\d{4})\[([^\]]+)\]\[([^\]]+)\](\d)', k); return m.groups() if m else (k,)
def uniq(k):  # 같은 구조의 ASR/FSR 판을 묶는 느슨한 열쇠 = 계열 + 번호 (번호가 판마다 달라 완전하진 않음)
    return re.sub(r'\[(ASR|FSR|ION)\]', '[*]', k)
print('== 층화: PLD 띠 × 배위 (선택도 중앙 · 75.8 초과 수 / n) ==')
for lo, hi in ((0, 3.8), (3.8, 4.5), (4.5, 6.0), (6.0, 99)):
    line = '  PLD [%.1f,%4.1f)' % (lo, hi)
    for k in ('N-only', 'N+O', 'O-only'):
        g = [x['S'] for x in X if x['kind'] == k and x['PLD'] and lo <= x['PLD'] < hi]
        line += '   %-6s %s' % (k, ('%5.1f · %2d/%3d' % (st.median(g), sum(1 for s in g if s > 75.8), len(g))) if g else '   -          ')
    print(line)
# 2) 계열 단위 집계 — 계열 하나를 한 표로
print('\n== 75.8 초과를 계열로 묶으면 ==')
top = [x for x in X if x['S'] > 75.8]
fams = {}
for x in top:
    fams.setdefault(fam(x['key']), []).append(x)
for f, g in sorted(fams.items(), key=lambda kv: -max(x['S'] for x in kv[1])):
    kinds = sorted(set(x['kind'] for x in g))
    print('  %-26s 행 %2d · S %.0f~%.0f · n015 %.2f~%.2f · PLD %.2f~%.2f · %s' % (
        '%s[%s][%s]%s' % f, len(g), min(x['S'] for x in g), max(x['S'] for x in g),
        min(x['n015'] for x in g), max(x['n015'] for x in g), min(x['PLD'] for x in g), max(x['PLD'] for x in g), '/'.join(kinds)))
print('  계열 수 %d (행 %d)' % (len(fams), len(top)))
# 3) 상위 계열 대표 CIF 머리말 — 무슨 물질인가
print('\n== 대표 CIF 머리말 ==')
seen = set()
for x in sorted(top, key=lambda x: -x['S']):
    f = fam(x['key'])
    if f in seen:
        continue
    seen.add(f)
    t = z.read(x['file']).decode('utf-8', 'ignore').splitlines()
    heads = [l.strip() for l in t[:60] if l.strip().startswith(('data_', '_chemical_name', '_chemical_formula_sum', '_database_code', '_journal', '_publ', '_citation', '_refcode'))]
    print('  %-24s %s' % (x['key'][:24], ' | '.join(heads)[:260]))
# 4) N-only 중 PLD<4.5 (ZIF 류 초미세공)의 선택도 분포
g = sorted([x for x in X if x['kind'] == 'N-only' and x['PLD'] and x['PLD'] < 4.5], key=lambda x: -x['S'])
print('\n== N-only · PLD<4.5 : n %d · S 중앙 %.1f ==' % (len(g), st.median([x['S'] for x in g])))
