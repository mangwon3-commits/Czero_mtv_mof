# -*- coding: utf-8 -*-
"""MAGI-005 R3 (Junseok) 보강 산술 — A-2·A-4·A-10/A-20·A-16·A-17·A-18. 저장소에 안 씀."""
import json, sys, zipfile, re, io, statistics as st, warnings
import numpy as np
from scipy.stats import spearmanr
warnings.filterwarnings('ignore')
exec(open(sys.argv[2]).read().split("X = json.load")[0])          # desc() · charges() · D
X = json.load(open(sys.argv[1])); z = zipfile.ZipFile(D + 'core_pop_cifs.zip')
META = json.load(open('/home/mangwon/mof_project/23_SCREENING/data/CR_meta_data_SI_slice.json'))
for x in X:
    d = desc(z.read(x['file']).decode('utf-8', 'ignore')); x['q'] = d['qfree'] or 0.0
    m = re.match(r'(\d{4})\[([^\]]+)\]\[([^\]]+)\](\d)', x['key']); x['dim'] = int(m.group(4)) if m else None
    x['L'] = (x['n015'] / (x['KH_CO2'] * 15000.0)) if (x['n015'] and x['KH_CO2']) else None
COLL = {'2016[Co][pts]3[ASR]5', '2016[Co][pts]3[FSR]8'}             # A-2 수축상

def cif_info(fn):
    t = z.read(fn).decode('utf-8', 'ignore')
    g = lambda k: (re.search(k + r'\s+([-\d.()]+)', t) or [None, None])[1]
    nat = len(read(io.StringIO(t), format='cif'))
    sg = (re.search(r"_space_group_name_H-M_alt\s+'?([^'\n]+)|_symmetry_space_group_name_H-M\s+'?([^'\n]+)", t) or None)
    return {'a': g('_cell_length_a'), 'b': g('_cell_length_b'), 'c': g('_cell_length_c'), 'al': g('_cell_angle_alpha'),
            'be': g('_cell_angle_beta'), 'ga': g('_cell_angle_gamma'), 'nat': nat, 'sg': (sg.group(1) or sg.group(2)).strip() if sg else '?'}
from ase.io import read

def meta_candidates(x):
    info = cif_info(x['file']); ext = {'ASR': 'All Solvent Removed', 'FSR': 'Free Solvent Removed'}
    e = re.search(r'\[(ASR|FSR|ION)\]', x['key']).group(1)
    mets = [m for m in (x['metal'] or '').split(',') if m]
    out = []
    for k, v in META.items():
        si = v.get('structure_info', {})
        if si.get('n_atoms') != info['nat']:
            continue
        if e in ext and si.get('extension') and si['extension'] != ext[e]:
            continue
        mid = (v.get('id') or {}).get('mofid-v1') or ''
        if mets and not all(('[' + m + ']') in mid or (m in mid) for m in mets):
            continue
        out.append((k, (v.get('reference') or {}).get('DOI'), (v.get('id') or {}).get('common_name'), si.get('space_group', {}).get('number')))
    return info, out

print('== ① 정체 대조 (원자 수 · 용매판 · 금속으로 메타 후보) ==')
for key in ('2016[Co][pts]3[ASR]5', '2010[Zn][pts]3[ASR]1', '2012[Co][dia]3[ASR]3', '2024[Zn][crb]3[ASR]1',
            '2024[Zn][srs]3[FSR]2', '2017[Zn][dia]3[FSR]1', '2019[Zn][pcu]3[ASR]6'):
    x = next((y for y in X if y['key'] == key), None)
    if not x:
        print('  %s 없음' % key); continue
    info, c = meta_candidates(x)
    print('  %-22s 원자 %3d · 셀 %s %s %s / %s %s %s · %s' % (key, info['nat'], info['a'], info['b'], info['c'], info['al'], info['be'], info['ga'], info['sg']))
    for k, doi, cn, sgn in c[:4]:
        print('      후보 %-34s DOI %-24s 이름 %-12s SG %s' % (k, doi, cn, sgn))
    if not c:
        print('      후보 0')

print('\n== ② crb 행 셀 대 배포본 ZIF-2 (Pbca 9.679 / 24.114 / 24.45) ==')
for x in sorted([y for y in X if '[crb]' in y['key'] and y['metal'] == 'Zn'], key=lambda y: y['key']):
    i = cif_info(x['file'])
    print('  %-22s %s %s %s / %s %s %s · %s · 원자 %d · S %.1f' % (x['key'], i['a'], i['b'], i['c'], i['al'], i['be'], i['ga'], i['sg'], i['nat'], x['S']))

def med(v):
    v = [a for a in v if a is not None]; return st.median(v) if v else float('nan')
print('\n== ③ 차원(키 숫자)으로 가름 ==')
for lab, g in (('S>75.8', [x for x in X if x['S'] > 75.8]), ('S>75.8 수축상 제외', [x for x in X if x['S'] > 75.8 and x['key'] not in COLL])):
    for dim in (2, 3):
        h = [x for x in g if x['dim'] == dim]
        print('  %-18s %dD  행 %2d · S 중앙 %6.1f · LCD %.2f · PLD %.2f · L %.3f · 적재 %.2f · |q| %.2f' % (
            lab, dim, len(h), med([x['S'] for x in h]), med([x['LCD'] for x in h]), med([x['PLD'] for x in h]),
            med([x['L'] for x in h]), med([x['n015'] for x in h]), med([x['q'] for x in h])))
print('  3D 전체 선택도 띠별 LCD 중앙 (J-7 을 3D 로):')
for lab, lo, hi in (('<20', 0, 20), ('20~40', 20, 40), ('40~75.8', 40, 75.8), ('>75.8', 75.8, 1e9)):
    h = [x for x in X if x['dim'] == 3 and lo <= x['S'] < hi and x['key'] not in COLL]
    print('     S %-8s n %3d · LCD 중앙 %.2f · L 중앙 %.3f' % (lab, len(h), med([x['LCD'] for x in h]), med([x['L'] for x in h])))
print('  3D 배위 부류 (J-3 을 3D 로, 수축상 제외):')
for k in ('N-only', 'N+O', 'O-only'):
    h = [x for x in X if x['dim'] == 3 and x['kind'] == k and x['key'] not in COLL]
    print('     %-7s n %3d · S 중앙 %5.1f · 75.8 초과 %2d' % (k, len(h), med([x['S'] for x in h]), sum(1 for x in h if x['S'] > 75.8)))

print('\n== ④ N만 · LCD<5 상관, 수축상 제외 / 3D 만 ==')
def rho(h, lab):
    if len(h) < 6: print('  %-26s n %d 적음' % (lab, len(h))); return
    r, p = spearmanr([x['q'] for x in h], [x['S'] for x in h]); print('  %-26s n %2d · ρ %+.2f (p %.2g)' % (lab, len(h), r, p))
g = [x for x in X if x['kind'] == 'N-only' and x['LCD'] < 5]
rho(g, '전체(원 결과)'); rho([x for x in g if x['key'] not in COLL], '수축상 제외')
rho([x for x in g if x['key'] not in COLL and x['dim'] == 3], '수축상 제외 · 3D 만')
for lab, lo, hi in (('LCD 5~7', 5, 7), ('LCD>=7', 7, 99)):
    h = [x for x in X if x['kind'] == 'N-only' and lo <= x['LCD'] < hi and x['dim'] == 3]
    rho(h, 'N만 3D ' + lab)

print('\n== ⑤ 금속별 (A-16): Zn 만 ==')
zn = [x for x in X if x['metal'] == 'Zn']
t = [x for x in zn if x['S'] > 75.8]
print('  Zn 이면서 S>75.8: %d행 · |q|자유 최대 %.2f (saIm050 4.19) · 4.19 초과 %d' % (len(t), max(x['q'] for x in t), sum(1 for x in t if x['q'] > 4.19)))
for lab, lo, hi in (('LCD<5', 0, 5), ('LCD 5~7', 5, 7), ('LCD>=7', 7, 99)):
    h = [x for x in zn if lo <= x['LCD'] < hi]
    rho(h, 'Zn 전 부류 ' + lab)
    rho([x for x in h if x['kind'] == 'N-only'], 'Zn N만 ' + lab)

print('\n== ⑥ T-J1′ 대조 교체 후보 L ==')
for key in ('2012[Co][dia]3[ASR]3', '2010[Zn][pts]3[ASR]1'):
    x = next(y for y in X if y['key'] == key)
    print('  %-22s S %.1f · L %.3f · n015 %.2f · LCD %.2f · PLD %.2f' % (key, x['S'], x['L'], x['n015'], x['LCD'], x['PLD']))
