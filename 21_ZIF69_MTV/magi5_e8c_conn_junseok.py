# -*- coding: utf-8 -*-
"""E-8c 손 검토 — CIF 결합(ase natural_cutoffs × 1.15, 주기 경계)으로 산소·탄소 환경을 센다.
COO⁻ = O 둘과 이웃한 C(그 O 에 H 없음) · COOH = 그 O 중 H 가진 것 · 물 = H 둘·C 없는 O · OH⁻ = H 하나·C 없는 O · 에터 O = C 둘.
형식 전하 추정 = 금속 산화수 합 − (COO⁻ 수) − (OH⁻ 수) − (O²⁻ 수) + (N⁺ 없음 가정)."""
import sys
from collections import Counter

import numpy as np
from ase.io import read
from ase.neighborlist import natural_cutoffs, neighbor_list

D = '/home/mangwon/mof_project/21_ZIF69_MTV/core_pop_cifs/'
METAL_OX = {'Zn': 2, 'Cd': 2, 'Co': 2, 'Cu': 2, 'Ni': 2}


def env(name):
    import os
    import zipfile
    if not os.path.exists(D + name + '.cif'):      # core_pop_cifs/ 는 gitignore — zip 에서 꺼냄
        open(D + name + '.cif', 'wb').write(zipfile.ZipFile(D + '../core_pop_cifs.zip').read(name + '.cif'))
    a = read(D + name + '.cif')
    cut = [c * 1.15 for c in natural_cutoffs(a)]
    i, j = neighbor_list('ij', a, cut)
    sym = a.get_chemical_symbols()
    nb = [[] for _ in sym]
    for x, y in zip(i, j):
        nb[x].append(sym[y])
    cnt = Counter()
    for k, s in enumerate(sym):
        c = Counter(nb[k])
        if s == 'C':
            if c['O'] == 2:
                os_ = [y for x, y in zip(i, j) if x == k and sym[y] == 'O']
                protonated = sum(1 for o in os_ if 'H' in [sym[y] for x, y in zip(i, j) if x == o])
                cnt['COOH' if protonated else 'COO-'] += 1
            elif c['H'] == 2 and c['C'] + c['N'] + c['O'] == 2:
                cnt['CH2'] += 1
            elif c['H'] == 1 and c['C'] + c['N'] + c['O'] == 3 and c['O'] == 0:
                cnt['CH(sp3?)'] += 1
            elif c['H'] == 3:
                cnt['CH3'] += 1
        elif s == 'O':
            nC, nH, nM = c['C'], c['H'], sum(v for e, v in c.items() if e in METAL_OX)
            if nC == 0 and nH == 2:
                cnt['H2O'] += 1
            elif nC == 0 and nH == 1:
                cnt['OH(no C)'] += 1
            elif nC == 0 and nH == 0:
                cnt['O(no C, no H)'] += 1
            elif nC == 2:
                cnt['ether O'] += 1
            elif nC == 1 and nH == 1:
                cnt['C-OH'] += 1
        elif s == 'N':
            cnt[f'N(H{c["H"]},C{c["C"]},M{sum(v for e, v in c.items() if e in METAL_OX)})'] += 1
    metals = Counter(s for s in sym if s in METAL_OX)
    ox = sum(METAL_OX[m] * n for m, n in metals.items())
    q = ox - cnt['COO-'] - cnt['OH(no C)'] - 2 * cnt['O(no C, no H)']
    return Counter(sym), metals, cnt, ox, q


for name in sys.argv[1:]:
    tot, metals, cnt, ox, q = env(name)
    print(f"\n{name}: {dict(sorted(tot.items()))}")
    print(f"   환경 {dict(sorted(cnt.items()))}")
    print(f"   금속 {dict(metals)} → +{ox} · COO⁻ {cnt['COO-']} · OH⁻ {cnt['OH(no C)']} · O²⁻ {cnt['O(no C, no H)']} → 형식 전하 추정 {q:+d}"
          f"  (N 은 중성 주개로 가정; N 환경 위 목록)")
