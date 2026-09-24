# -*- coding: utf-8 -*-
"""자유 극성 원자 밀도(금속에 안 붙은 N·O, nm^-3)와 그 |q| 합 밀도 — CoRE 524 + 우리 v3 조성. 저장소에 안 씀."""
import json, io, zipfile, glob, os, sys, statistics as st, warnings
import numpy as np
from scipy.stats import spearmanr
warnings.filterwarnings('ignore')
from ase.io import read
from ase.neighborlist import neighbor_list, natural_cutoffs
D = '/home/mangwon/mof_project/21_ZIF69_MTV/'
X = {x['file']: x for x in json.load(open(sys.argv[1]))}
METALS = set('Li Na K Mg Ca Sr Ba Sc Ti V Cr Mn Fe Co Ni Cu Zn Y Zr Nb Mo Ru Rh Pd Ag Cd In Sn La Ce Pr Nd Sm Eu Gd Tb Dy Ho Er Tm Yb Lu Hf W Re Os Ir Pt Au Hg Pb Bi Al Ga U Th'.split())

def charges_from_cif(txt, n):
    # _atom_site_charge 열 읽기 (P1 가정)
    lines = txt.splitlines(); q = []
    for i, l in enumerate(lines):
        if l.strip() == 'loop_':
            hdr = []; j = i + 1
            while j < len(lines) and lines[j].strip().startswith('_'):
                hdr.append(lines[j].strip()); j += 1
            if '_atom_site_charge' in hdr:
                k = hdr.index('_atom_site_charge')
                while j < len(lines) and lines[j].strip() and not lines[j].strip().startswith(('loop_', '_')):
                    p = lines[j].split()
                    if len(p) == len(hdr):
                        q.append(float(p[k]))
                    j += 1
                break
    return q if len(q) == n else None

def desc(txt):
    a = read(io.StringIO(txt), format='cif')
    sym = a.get_chemical_symbols(); V = a.get_volume() / 1000.0   # nm^3
    q = charges_from_cif(txt, len(sym))
    i, j = neighbor_list('ij', a, natural_cutoffs(a, mult=1.15))
    bonded_metal = set(ii for ii, jj in zip(i, j) if sym[jj] in METALS)
    free = [k for k, s in enumerate(sym) if s in ('N', 'O') and k not in bonded_metal]
    fN = sum(1 for k in free if sym[k] == 'N'); fO = sum(1 for k in free if sym[k] == 'O')
    qd = (sum(abs(q[k]) for k in free) / V) if q else None
    return {'fN': fN / V, 'fO': fO / V, 'fNO': (fN + fO) / V, 'qfree': qd}

z = zipfile.ZipFile(D + 'core_pop_cifs.zip')
rows = []
for fn, x in X.items():
    try:
        d = desc(z.read(fn).decode('utf-8', 'ignore'))
    except Exception:
        continue
    rows.append(dict(x, **d))
# 헨리 곡률: n(0.15)/n(0.01) — 선형이면 15
wc = {}
for f in glob.glob(D + 'core_wc_results_*.json'):
    for r in json.load(open(f))['rows']:
        if r.get('n_0.01bar') and r.get('n_0.15bar'):
            wc.setdefault(r['file'], r['n_0.15bar'] / r['n_0.01bar'])
for r in rows:
    r['curv'] = wc.get(r['file'])

def sp(g, key):
    g = [r for r in g if r.get(key) is not None]
    if len(g) < 8:
        return '-'
    rho, p = spearmanr([r[key] for r in g], [r['S'] for r in g]); return '%+.2f (n %d, p %.1e)' % (rho, len(g), p)
print('== 선택도와의 순위상관 (Spearman) ==')
for lab, g in (('전체', rows), ('PLD<4.5', [r for r in rows if r['PLD'] < 4.5]), ('PLD>=4.5', [r for r in rows if r['PLD'] >= 4.5]),
               ('N-only', [r for r in rows if r['kind'] == 'N-only']), ('N+O', [r for r in rows if r['kind'] == 'N+O'])):
    print('  %-9s 자유N·O 밀도 %s · |q|자유 밀도 %s · PLD %s' % (lab, sp(g, 'fNO'), sp(g, 'qfree'), sp(g, 'PLD')))
print('\n== PLD<4.5 에서 |q|자유 밀도 삼분위별 선택도 ==')
g = sorted([r for r in rows if r['PLD'] < 4.5 and r['qfree'] is not None], key=lambda r: r['qfree'])
for k in range(3):
    h = g[k * len(g) // 3:(k + 1) * len(g) // 3]
    print('  %d분위 |q|자유 %.1f~%.1f e/nm3 · S 중앙 %.1f · S>75.8 %d/%d · 적재 중앙 %.2f' % (
        k + 1, h[0]['qfree'], h[-1]['qfree'], st.median([r['S'] for r in h]), sum(1 for r in h if r['S'] > 75.8), len(h),
        st.median([r['n015'] for r in h if r['n015'] is not None])))
print('\n== 헨리 곡률 n(0.15)/n(0.01) (선형 15) ==')
for lab, gg in (('S>75.8', [r for r in rows if r['S'] > 75.8]), ('S 20~40', [r for r in rows if 20 <= r['S'] <= 40]), ('S<13', [r for r in rows if r['S'] < 13])):
    c = [r['curv'] for r in gg if r['curv']]
    print('  %-8s n %3d · 중앙 %.1f · 사분위 %.1f/%.1f' % (lab, len(c), st.median(c), np.percentile(c, 25), np.percentile(c, 75)))
# 우리 v3 조성을 같은 척도로
res = {r['name']: r for r in json.load(open(D + 'results_v3.json'))} if os.path.exists(D + 'results_v3.json') else {}
mix = {r['name']: r for r in json.load(open(D + 'results_v4mix.json'))} if os.path.exists(D + 'results_v4mix.json') else {}
print('\n== 우리 조성, 같은 척도 ==')
for nm in ('base', 'nbIm100', 'saIm050', 'saIm0583', 'mslm050', 'sa50nb50', 'saIm100'):
    f = D + 'charged_v3/%s_DDEC6.cif' % nm
    if not os.path.exists(f):
        print('  %-9s CIF 없음' % nm); continue
    d = desc(open(f).read())
    r = res.get(nm) or mix.get(nm) or {}
    s = r.get('selectivity') or r.get('selectivity_CO2_N2') or r.get('S')
    print('  %-9s 자유N·O %.2f/nm3 (N %.2f · O %.2f) · |q|자유 %s e/nm3 · S %s' % (
        nm, d['fNO'], d['fN'], d['fO'], ('%.1f' % d['qfree']) if d['qfree'] else '-', s))
print('\n  CoRE PLD<4.5 |q|자유 중앙 %.1f · S>75.8 행들의 |q|자유 중앙 %.1f' % (
    st.median([r['qfree'] for r in rows if r['PLD'] < 4.5 and r['qfree']]), st.median([r['qfree'] for r in rows if r['S'] > 75.8 and r['qfree']])))
if res:
    print('  results_v3 키 예:', list(next(iter(res.values())).keys())[:14])
