# -*- coding: utf-8 -*-
"""#5 빌드 곁기록(랩탑) — 빌더 기록(e24j_build.json)이 놓친 X···O 접촉을 CIF 에서 직접 재고, 이완 전 (0b) clash_gate 값을 참고로 남긴다.
판정 아님: 등록 관문 (0a)(0b) 는 laptop2 의 GFN-FF 이완 뒤에 적용된다(ASSIGN_ZNBDT_NO2_PLACEMENT_20261107.md §2-1).
실행: 21_ZIF69_MTV 에서 czeromof 파이썬."""
import hashlib, json, os, sys
import numpy as np
sys.path.insert(0, os.getcwd())
from ase.io import read
from ase.neighborlist import natural_cutoffs, neighbor_list
import check_substituent_clash as CK
import clash_gate as G

ROWS = [('e24j_cl_ovl', 'e24j_candidates/e24j_cl_ovl.cif', '겹침(고리 0·1)'),
        ('e24j_br_ovl', 'e24j_candidates/e24j_br_ovl.cif', '겹침(고리 0·1)'),
        ('E24i_ZnDia_Cl_open', 'e24i_candidates/E24i_ZnDia_Cl_open.cif', '열린(고리 2·3) 대조'),
        ('E24i_ZnDia_Br_open', 'e24i_candidates/E24i_ZnDia_Br_open.cif', '열린(고리 2·3) 대조')]
out = {'what': '#5 빌드 곁기록 — 빌더 그래프(공유 반지름 × BOND_MULT)가 X···O 를 결합으로 잡는지 · 직접 잰 X···O · 이완 전 clash_gate',
       'assign': 'ASSIGN_ZNBDT_NO2_PLACEMENT_20261107.md §2-1', 'machine': 'laptop', 'bond_mult': CK.BOND_MULT,
       'note': '판정 아님 — 등록 관문은 laptop2 이완 뒤. clash_gate 는 Bondi 반지름 · 겹침 0.4 Å(결합 판정을 쓰지 않음)', 'rows': []}
for name, path, where in ROWS:
    a = read(path); s = a.get_chemical_symbols(); D = a.get_all_distances(mic=True)
    i, j, _ = neighbor_list('ijd', a, natural_cutoffs(a, mult=CK.BOND_MULT))
    X = [k for k, e in enumerate(s) if e in ('Cl', 'Br')]
    per = []
    for k in X:
        d = D[k].copy(); d[k] = 9e9
        o = int(np.argmin(np.where(np.array(s) == 'O', d, 9e9)))
        nb = sorted(s[jj] + str(jj) for ii, jj in zip(i, j) if ii == k)
        per.append({'atom': s[k] + str(k), 'X_O_min_A': round(float(d[o]), 3), 'O': 'O' + str(o),
                    'graph_neighbors': nb, 'X_O_counted_as_bond': any(n.startswith('O') for n in nb)})
    g = G.check(path)
    out['rows'].append({'name': name, 'cif': path, 'site': where, 'md5': hashlib.md5(open(path, 'rb').read()).hexdigest(),
                        'X_O_min_A': min(p['X_O_min_A'] for p in per), 'X_O_counted_as_bond_any': any(p['X_O_counted_as_bond'] for p in per),
                        'per_X': per, 'clash_gate_unrelaxed': {k: g[k] for k in ('min_margin_A', 'worst_pair', 'n_clash_pairs', 'pass_0b')}})
    r = out['rows'][-1]
    print(f"{name:20s} X···O 최소 {r['X_O_min_A']:.3f} · 결합으로 잡힘 {r['X_O_counted_as_bond_any']} · 이완 전 (0b) 여유 {g['min_margin_A']} · 통과 {g['pass_0b']}")
json.dump(out, open('e24j_candidates/e24j_contacts_laptop.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
