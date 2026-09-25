# -*- coding: utf-8 -*-
"""MAGI-005 E-24 — Zn(bib)(bdtdc) 4,8-자리 작은 치환기(−CH₃ · −F · −C≡N) 100 % 후보 빌드. 등록 `ASSIGN_MAGI5B_20260925.md` §HKHOME 13차(가).
laptop `build_e22_bdtdc.py`(6bad71ad)를 **수정 없이 import** — 자리 찾기 · rdkit 조각 · 비틀림 주사 · 충돌 검사는 그대로.
바꾼 것 둘: SMILES 사전에 세 치환기 추가 · 점검 함수의 치환기 기하 부분(원판은 O 둘을 전제)을 치환기 무관한 판으로(C–X · 치환기 내부 결합).
"""
import json, math, os, sys
import numpy as np
import networkx as nx
from ase.neighborlist import neighbor_list
from ase.io import read
from ase import Atoms

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import build_e22_bdtdc as B   # noqa: E402

B.SMILES.update({'CH3': 'c1ccccc1C', 'F': 'c1ccccc1F', 'CN': 'c1ccccc1C#N'})
OUTD = os.path.join(HERE, 'e24_candidates')
KINDS = ('CH3', 'F', 'CN')


def checks(new, n_sub_atoms, loc, kind, chosen_n):
    sym = np.array(new.get_chemical_symbols()); G = B.graph(new)
    i, j, d = neighbor_list('ijd', new, 3.2)
    sp = dict(nx.all_pairs_shortest_path_length(G, cutoff=2))
    nonb = sorted((float(dd), sym[x] + '-' + sym[y]) for x, y, dd in zip(i, j, d) if x < y and y not in sp.get(int(x), {}))
    first_sub = len(new) - n_sub_atoms
    subn = sorted((float(dd), sym[x] + '-' + sym[y]) for x, y, dd in zip(i, j, d)
                  if x < y and (x >= first_sub or y >= first_sub) and y not in sp.get(int(x), {}))
    per = len(loc); cx = []; internal = []
    for s in range(chosen_n):
        X = first_sub + s * per
        ipso = min((k for k in G[X] if sym[k] == 'C' and k < first_sub), key=lambda k: new.get_distance(X, k, mic=True))
        cx.append(new.get_distance(ipso, X, mic=True))
        for a_ in range(X, X + per):
            for b_ in G[a_]:
                if a_ < b_ < X + per:
                    internal.append(new.get_distance(a_, b_, mic=True))
    return {'formula': new.get_chemical_formula(), 'n_atoms': len(new), 'all_pair_min_A': round(float(d.min()), 3),
            'nonbonded_min_A(topo>=3)': [round(nonb[0][0], 3), nonb[0][1]],
            'substituent_nonbonded_min_A': [round(subn[0][0], 3), subn[0][1]] if subn else None,
            'nonbonded_ge_1.0': nonb[0][0] >= 1.0,
            'C-X_range': [round(min(cx), 3), round(max(cx), 3)],
            'substituent_internal_bond_range': [round(min(internal), 3), round(max(internal), 3)] if internal else None}


def main():
    os.makedirs(OUTD, exist_ok=True)
    a0 = read(B.SRC); a0 = Atoms(a0.get_chemical_symbols(), positions=a0.positions, cell=a0.cell, pbc=True)
    G = B.graph(a0); S, nring = B.sites(a0, G)
    assert nring == 4 and len(S) == 8, (nring, len(S))
    rec = {'test': 'MAGI-005 E-24 빌드', 'assign': 'ASSIGN_MAGI5B_20260925.md §HKHOME 13차(가)', 'builder': 'build_e22_bdtdc.py(laptop 6bad71ad) import',
           'template': os.path.relpath(B.SRC, HERE), 'seed': B.SEED, 'torsion_step_deg': B.STEP, 'rows': []}
    for kind in KINDS:
        new, th, hist, loc = B.build(a0, G, S, kind, S)
        name = f'E24_ZnDia_{kind}_100'; path = os.path.join(OUTD, name + '.cif'); B.write_cif(path, new)
        r = {'name': name, 'kind': kind, 'fraction': 1.0, 'n_substituted': len(S), 'sweeps_changed': hist,
             'torsion_deg': {str(k): round(math.degrees(v), 1) for k, v in th.items()},
             'fragment_local': [[e, [round(x, 4) for x in pp]] for e, pp in loc],
             **checks(new, len(S) * len(loc), loc, kind, len(S)), 'clash_check': B.CK.check(path)}
        rec['rows'].append(r)
        print(f"{name:18s} {r['formula']:26s} 비결합 최소 {r['nonbonded_min_A(topo>=3)']} · 치환기 {r['substituent_nonbonded_min_A']} · "
              f"C–X {r['C-X_range']} · 내부 {r['substituent_internal_bond_range']} · 충돌검사 {'통과' if r['clash_check']['pass'] else '탈락'} · 재주사 {hist}", flush=True)
    json.dump(rec, open(os.path.join(OUTD, 'e24_build.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1, default=float)
    return 0


if __name__ == '__main__':
    sys.exit(main())
