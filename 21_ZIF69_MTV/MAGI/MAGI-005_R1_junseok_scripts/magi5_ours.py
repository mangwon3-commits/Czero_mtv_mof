# -*- coding: utf-8 -*-
"""헨리 선형 지수 L = n(0.15 bar)/(K_H·15 kPa) — CoRE 와 우리 조성 같은 발판. + 우리 조성의 자유 극성 원자 밀도. 저장소에 안 씀."""
import json, io, os, sys, zipfile, statistics as st, warnings
import numpy as np
warnings.filterwarnings('ignore')
from ase.io import read
from ase.neighborlist import neighbor_list, natural_cutoffs
D = '/home/mangwon/mof_project/21_ZIF69_MTV/'
METALS = set('Li Na K Mg Ca Sr Ba Sc Ti V Cr Mn Fe Co Ni Cu Zn Y Zr Nb Mo Ru Rh Pd Ag Cd In Sn La Ce Pr Nd Sm Eu Gd Tb Dy Ho Er Tm Yb Lu Hf W Re Os Ir Pt Au Hg Pb Bi Al Ga U Th'.split())

def charges(txt, n):
    L = txt.splitlines()
    for i, l in enumerate(L):
        if l.strip() == 'loop_':
            h = []; j = i + 1
            while j < len(L) and L[j].strip().startswith('_'):
                h.append(L[j].strip()); j += 1
            if '_atom_site_charge' in h:
                k = h.index('_atom_site_charge'); q = []
                while j < len(L) and L[j].strip() and not L[j].strip().startswith(('loop_', '_')):
                    p = L[j].split()
                    if len(p) == len(h):
                        q.append(float(p[k]))
                    j += 1
                return q if len(q) == n else None
    return None

def desc(txt):
    a = read(io.StringIO(txt), format='cif'); s = a.get_chemical_symbols(); V = a.get_volume() / 1000.0
    q = charges(txt, len(s))
    i, j = neighbor_list('ij', a, natural_cutoffs(a, mult=1.15))
    bm = set(ii for ii, jj in zip(i, j) if s[jj] in METALS)
    fr = [k for k, e in enumerate(s) if e in ('N', 'O') and k not in bm]
    return {'fNO': len(fr) / V, 'qfree': (sum(abs(q[k]) for k in fr) / V) if q else None}

X = json.load(open(sys.argv[1]))
for x in X:
    x['L'] = (x['n015'] / (x['KH_CO2'] * 15000.0)) if (x['n015'] and x['KH_CO2']) else None
def band(g, lab):
    L = [x['L'] for x in g if x['L']]
    print('  %-12s n %3d · L 중앙 %.3f · 사분위 %.3f/%.3f' % (lab, len(L), st.median(L), np.percentile(L, 25), np.percentile(L, 75)))
print('== CoRE 헨리 선형 지수 L (1 = 선형) ==')
band([x for x in X if x['S'] > 75.8], 'S>75.8')
band([x for x in X if 40 <= x['S'] <= 75.8], 'S 40~75.8')
band([x for x in X if 20 <= x['S'] < 40], 'S 20~40')
band([x for x in X if x['S'] < 20], 'S<20')

rows = json.load(open(D + 'results_v3.json'))['rows'] + json.load(open(D + 'results_v4mix.json'))['rows']
R = {r['name']: r for r in rows}
print('\n== 우리 조성 (같은 척도) ==')
for nm in ('base', 'nbIm100', 'saIm050', 'saIm0583', 'mslm050', 'sa50nb50', 'saIm075', 'saIm100'):
    r = R.get(nm)
    if not r:
        print('  %-9s 결과 없음' % nm); continue
    f = D + 'charged_v3/%s_DDEC6.cif' % nm
    d = desc(open(f).read()) if os.path.exists(f) else None
    L = r['loading_015bar'] / (r['KH_CO2'] * 15000.0)
    print('  %-9s S %6.1f ± %4.1f · n015 %.3f · L %.3f · PLD %.2f · LCD %.2f · 자유N·O %s/nm3 · |q|자유 %s e/nm3 · Qst보정 %.1f' % (
        nm, r['selectivity'], r.get('selectivity_err') or 0, r['loading_015bar'], L, r['PLD'], r['LCD'],
        ('%.2f' % d['fNO']) if d else '-', ('%.2f' % d['qfree']) if (d and d['qfree']) else '-', r.get('Qst_CO2_rt_corrected') or float('nan')))
# CoRE 기준점 — PLD<4.5 삼분위 경계(앞 계산) 2.4 e/nm3 와 비교용으로 S>75.8 대표 몇
z = zipfile.ZipFile(D + 'core_pop_cifs.zip')
print('\n== CoRE 상위 대표 (같은 척도) ==')
seen = set()
for x in sorted([x for x in X if x['S'] > 75.8], key=lambda x: -x['S']):
    fam = x['key'].split(']')[0] + ']' + x['key'].split(']')[1] + ']' + x['key'].split(']')[2] + ']'
    if fam in seen:
        continue
    seen.add(fam)
    d = desc(z.read(x['file']).decode('utf-8', 'ignore'))
    print('  %-24s S %6.1f · n015 %.2f · L %.3f · PLD %.2f · %-6s · 자유N·O %.2f · |q|자유 %s' % (
        x['key'][:24], x['S'], x['n015'], x['L'], x['PLD'], x['kind'], d['fNO'], ('%.2f' % d['qfree']) if d['qfree'] else '-'))
