# -*- coding: utf-8 -*-
"""MAGI-005 결함 §25 요청(데스크탑 15:3x · master 595c88dc) — Junseok 기기에 있는 UFF4MOF 수렴 기하의 치환기–O 최소 거리. 기계적 사실만 — 판정은 종합자.
대상: C₂H₅ = E-24c ③(lmp_e24c60/e24c_c2h5_100/after.cif, 상한 60 · 44 루프 · EDiff 7.1e-5 · results_e24c_relax60_junseok.json)
      CN   = E-29(lmp_e29/e24_cn_100/after.cif, 상한 60 · 26 루프 · EDiff 9.3e-6 · results_e29_relax60_junseok.json)
      비교: 이완 전 GFN-FF 기하(relax_tnf/<tag>_relaxed.cif = lmp before.cif).
판별: C₂H₅ — CH₂ 탄소(H 2개, 1.25 Å 안) · 그와 1.7 Å 안의 CH₃ 탄소(H 3개). CN — Zn 2.6 Å 밖이고 C 이웃(1.5 Å 안)이 정확히 하나인 N(O 이웃은 허용 —
      O 에 박힌 자리를 빼지 않게; UFF4MOF 기하는 C–N 이 1.36 Å 라 삼중결합 길이 문턱을 쓰지 않음). O 는 골격의 모든 O(형판에서 O 는 카복실만). 거리는 PBC 최소 이미지.
after.cif 는 초격자(2×2×3, 단위셀의 12 배) — 자리 수가 12 배. 값이 같은 자리는 묶어 개수로 적음.
출력 results_s25_contacts_junseok.json.
"""
import json
from collections import Counter

import numpy as np
from ase.io import read
from ase.neighborlist import neighbor_list

H = '/home/mangwon/mof_project/21_ZIF69_MTV'
OUT = f'{H}/results_s25_contacts_junseok.json'
CASES = [('C2H5', 'GFN-FF', 'relax_tnf/e24c_c2h5_100_relaxed.cif'),
         ('C2H5', 'UFF4MOF E-24c ③ (상한 60 · 44 루프 · EDiff 7.1e-5)', 'lmp_e24c60/e24c_c2h5_100/after.cif'),
         ('CN', 'GFN-FF', 'relax_tnf/e24_cn_100_relaxed.cif'),
         ('CN', 'UFF4MOF E-29 (상한 60 · 26 루프 · EDiff 9.3e-6)', 'lmp_e29/e24_cn_100/after.cif')]


def load(p):
    a = read(f'{H}/{p}')
    sym = np.array(a.get_chemical_symbols())
    i, j, d = neighbor_list('ijd', a, 2.7)
    nb = {k: [] for k in range(len(a))}
    for x, y, dd in zip(i, j, d):
        nb[x].append((int(y), float(dd)))
    return a, sym, nb, np.where(sym == 'O')[0]


def near_o(a, nb, sym, O, idx):
    D = a.get_distances(idx, O, mic=True)
    k = int(D.argmin())
    o = int(O[k])
    oc = min((dd for y, dd in nb[o] if sym[y] == 'C' and dd < 1.7), default=None)
    return round(float(D[k]), 3), (round(oc, 3) if oc else None)


def c2h5(a, sym, nb, O):
    nH = {k: sum(1 for y, dd in nb[k] if sym[y] == 'H' and dd < 1.25) for k in range(len(a)) if sym[k] == 'C'}
    ch3 = {k for k, n in nH.items() if n == 3}
    rows = []
    for c2 in (k for k, n in nH.items() if n == 2):
        p = [y for y, dd in nb[c2] if y in ch3 and dd < 1.7]
        if len(p) != 1:
            continue
        hs = [y for y, dd in nb[c2] + nb[p[0]] if sym[y] == 'H' and dd < 1.25]
        d2, oc = near_o(a, nb, sym, O, c2)
        d3, _ = near_o(a, nb, sym, O, p[0])
        rows.append({'CH2_O': d2, 'CH3_O': d3, 'H_O': min(near_o(a, nb, sym, O, h)[0] for h in hs), 'CO_of_nearest_O': oc})
    return rows


def cn(a, sym, nb, O):
    rows = []
    for n in (int(x) for x in np.where(sym == 'N')[0]):
        if any(sym[y] == 'Zn' and dd < 2.6 for y, dd in nb[n]):
            continue
        cs = [(y, dd) for y, dd in nb[n] if sym[y] == 'C' and dd < 1.5]
        if len(cs) != 1:
            continue
        dn, oc = near_o(a, nb, sym, O, n)
        dc, _ = near_o(a, nb, sym, O, cs[0][0])
        rows.append({'N_O': dn, 'C_N': round(cs[0][1], 3), 'Cnitrile_O': dc, 'CO_of_nearest_O': oc})
    return rows


out = {'test': 'MAGI-005 결함 §25 — 치환기–O 최소 거리(Junseok 보유 UFF4MOF 수렴 기하)', 'machine': 'junseok', 'request': '데스크탑 결함 §25 알림(master 595c88dc)',
       'note': '기계적 사실뿐 — 판정은 종합자. 값이 같은 자리는 개수로 묶음. after.cif 는 2×2×3 초격자.', 'cases': []}
for sub, geom, p in CASES:
    a, sym, nb, O = load(p)
    rows = c2h5(a, sym, nb, O) if sub == 'C2H5' else cn(a, sym, nb, O)
    keys = ('CH2_O', 'CH3_O', 'H_O') if sub == 'C2H5' else ('N_O', 'Cnitrile_O', 'C_N')
    c = {'substituent': sub, 'geometry': geom, 'file': p, 'n_atoms': len(a), 'cell': [round(float(x), 3) for x in a.cell.cellpar()], 'n_sites': len(rows),
         'min': {k: min(r[k] for r in rows) for k in keys},
         'distribution': {k: sorted(Counter(r[k] for r in rows).items()) for k in keys[:2]},
         'CO_of_nearest_O': sorted(Counter(r['CO_of_nearest_O'] for r in rows).items())}
    out['cases'].append(c)
    print(f"{sub} {geom}: {len(a)} 원자 · 자리 {len(rows)} · 최소 {c['min']}")
    for k in keys[:2]:
        print(f"   {k}: {c['distribution'][k]}")
json.dump(out, open(OUT, 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
print('저장', OUT)
