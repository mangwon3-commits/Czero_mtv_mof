# -*- coding: utf-8 -*-
"""MAGI-005 R1 (Junseok) — CoRE 524 우리 자 모집단 역설계. 저장소에 아무것도 쓰지 않음(메모리 + 스크래치 출력만)."""
import json, glob, os, io, zipfile, statistics as st, warnings, sys
import numpy as np
warnings.filterwarnings('ignore')
D = '/home/mangwon/mof_project/21_ZIF69_MTV/'
OUTJ = sys.argv[1] if len(sys.argv) > 1 else '/tmp/magi5_core.json'

pick = {p['file']: p for p in json.load(open(D + 'core_pop_pick.json'))}
rows = {}
for f in sorted(glob.glob(D + 'core_pop_results_*.json')) + [D + 'bridge_core_results.json']:
    d = json.load(open(f))
    for r in d['rows']:
        if r.get('status') != 'ok':
            continue
        fn = r.get('file') or (r.get('key', '') + '.cif')
        if fn in pick and fn not in rows:
            rows[fn] = dict(r)
# 0.15 bar 적재 (§AW)
wc = {}
for f in sorted(glob.glob(D + 'core_wc_results_*.json')):
    for r in json.load(open(f))['rows']:
        if (r.get('run_status') or {}).get('0.15bar') == 'ok' and r.get('n_0.15bar') is not None:
            wc.setdefault(r['file'], r)
S = sorted(r['selectivity'] for r in rows.values())
N = len(S)
def pct(v):  # 백분위 = v 이하 비율
    return 100.0 * sum(1 for s in S if s <= v) / N
print('모집단 %d · 선택도 중앙 %.1f · 사분위 %.1f/%.1f/%.1f · 적재 있는 것 %d' % (
    N, st.median(S), np.percentile(S, 25), np.percentile(S, 50), np.percentile(S, 75), sum(1 for f in rows if f in wc)))
for v, lab in ((65.2, 'saIm050'), (75.8, 'sa50nb50')):
    print('  %s %.1f -> 백분위 %.1f %% · 그 위 %d종' % (lab, v, pct(v), sum(1 for s in S if s > v)))

# 금속 배위 분류 (CIF, P1 가정 — ASE 로 읽고 공유결합 반경 × 1.15)
from ase.io import read
from ase.neighborlist import neighbor_list, natural_cutoffs
METALS = set('Li Na K Mg Ca Sr Ba Sc Ti V Cr Mn Fe Co Ni Cu Zn Y Zr Nb Mo Ru Rh Pd Ag Cd In Sn La Ce Pr Nd Sm Eu Gd Tb Dy Ho Er Tm Yb Lu Hf W Re Os Ir Pt Au Hg Pb Bi Al Ga U Th'.split())
z = zipfile.ZipFile(D + 'core_pop_cifs.zip')
names = set(z.namelist())
def classify(fn):
    if fn not in names:
        return None
    try:
        a = read(io.StringIO(z.read(fn).decode('utf-8', 'ignore')), format='cif')
    except Exception as e:
        return {'err': str(e)[:60]}
    sym = a.get_chemical_symbols()
    els = sorted(set(sym))
    cut = natural_cutoffs(a, mult=1.15)
    i, j = neighbor_list('ij', a, cut)
    mets = [k for k, s in enumerate(sym) if s in METALS]
    donors = {}
    for k in mets:
        nb = [sym[jj] for ii, jj in zip(i, j) if ii == k and sym[jj] not in METALS and sym[jj] != 'H']
        for e in set(nb):
            donors[e] = donors.get(e, 0) + nb.count(e)
    dset = set(donors)
    if dset <= {'N'} and dset:
        kind = 'N-only'
    elif 'N' in dset and ('O' in dset):
        kind = 'N+O'
    elif dset <= {'O'} and dset:
        kind = 'O-only'
    else:
        kind = '+'.join(sorted(dset)) or '?'
    return {'els': els, 'donors': donors, 'kind': kind, 'nat': len(sym), 'hasF': 'F' in els}

out = []
for fn, r in rows.items():
    c = classify(fn) or {}
    w = wc.get(fn, {})
    out.append({'file': fn, 'key': r['key'], 'topo': r.get('topo'), 'metal': r.get('metal'), 'PLD': r.get('PLD'), 'LCD': r.get('LCD'),
                'S': r['selectivity'], 'KH_CO2': r['KH_CO2'], 'dU': r.get('dU_CO2'), 'n015': w.get('n_0.15bar'), 'n015e': w.get('n_0.15bar_err'),
                'kind': c.get('kind'), 'els': c.get('els'), 'donors': c.get('donors'), 'hasF': c.get('hasF')})
json.dump(out, open(OUTJ, 'w'), ensure_ascii=False)

def summ(g, lab):
    if not g:
        print('  %-28s 0' % lab); return
    ss = [x['S'] for x in g]; ls = [x['n015'] for x in g if x['n015'] is not None]
    pl = [x['PLD'] for x in g if x['PLD']]
    print('  %-28s n %3d · S 중앙 %6.1f · S>65.2 %3d · S>75.8 %3d · 적재 중앙 %s · PLD 중앙 %.2f' % (
        lab, len(g), st.median(ss), sum(1 for s in ss if s > 65.2), sum(1 for s in ss if s > 75.8),
        ('%.2f' % st.median(ls)) if ls else '-', st.median(pl) if pl else float('nan')))
print('\n== 금속 배위로 가름 ==')
for k in ('N-only', 'N+O', 'O-only'):
    summ([x for x in out if x['kind'] == k], k)
summ([x for x in out if x['kind'] not in ('N-only', 'N+O', 'O-only')], '기타/미분류')
summ([x for x in out if x['hasF']], 'F 포함')
print('\n== PLD 로 가름 (초미세공 편향 확인) ==')
for lo, hi in ((0, 3.8), (3.8, 4.5), (4.5, 6.0), (6.0, 99)):
    summ([x for x in out if x['PLD'] and lo <= x['PLD'] < hi], 'PLD [%.1f, %.1f)' % (lo, hi))
print('\n== S > 75.8 전부 (선택도 순) ==')
top = sorted([x for x in out if x['S'] > 75.8], key=lambda x: -x['S'])
for x in top:
    print('  %-26s %-6s %-6s PLD %5.2f LCD %5.2f  S %7.1f  n015 %s  %-7s %s' % (
        x['key'][:26], (x['metal'] or '')[:6], (x['topo'] or '')[:6], x['PLD'] or 0, x['LCD'] or 0, x['S'],
        ('%.2f' % x['n015']) if x['n015'] is not None else '  -  ', x['kind'], ''.join(e for e in (x['els'] or []))))
print('\n== N-only (아졸레이트류) 전부 (선택도 순) ==')
for x in sorted([x for x in out if x['kind'] == 'N-only'], key=lambda x: -x['S']):
    print('  %-26s %-6s %-6s PLD %5.2f LCD %5.2f  S %7.1f  n015 %s  %s' % (
        x['key'][:26], (x['metal'] or '')[:6], (x['topo'] or '')[:6], x['PLD'] or 0, x['LCD'] or 0, x['S'],
        ('%.2f' % x['n015']) if x['n015'] is not None else '  -  ', ''.join(x['els'] or [])))
