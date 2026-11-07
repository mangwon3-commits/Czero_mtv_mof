# -*- coding: utf-8 -*-
"""MAGI-007 보완 명령 #5 (랩탑) — 겹침 쪽 링커(고리 0 · 1)의 4,8-자리 넷에 −Cl · −Br. 등록 `ASSIGN_ZNBDT_NO2_PLACEMENT_20261107.md` §2-1(자료 0건).
`build_e24i_bdtdc.py` 사본 — 바꾼 것 다섯: OPEN_RINGS = (0, 1)(모체 4,8-H···O 2.695 Å 쪽) · KINDS = ('Cl', 'Br') ·
출력 폴더 `e24j_candidates/` · 이름 `e24j_cl_ovl` · `e24j_br_ovl` · 기록 파일 `e24j_build.json`. SMILES · one() · 고른 자리 수(4) 검사는 원판 그대로.
⚠ 이름 앞머리 e24j 는 09-26 의 E-24j(HKHOME 24차, 모체 UFF4MOF 상한 300 · `run_e24j_relax.py`)와 겹칩니다. 파일 이름은 겹치지 않으며, 등록문 이름을 그대로 씁니다.
⚠ 조각은 rdkit PhX 한 배좌를 강체로 C–X 축 둘레로만 돌림(원판 규약). 이 기기(랩탑)에는 xtb 가 없어 이완 · 관문 (0a)(0b)는 laptop2 가 잇습니다.
실행: czeromof 파이썬(rdkit · ase) — `python build_e24j_bdtdc.py` (21_ZIF69_MTV 에서)
"""
import json, math, os, random, sys
from ase import Atoms
from ase.io import read
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import build_e24_bdtdc as E   # noqa: E402  (import 만 — main 은 안 부름)
B = E.B
B.SMILES.update({'Br': 'c1ccccc1Br', 'Cl': 'c1ccccc1Cl'})
OUTD = os.path.join(HERE, 'e24j_candidates')
KINDS = ('Cl', 'Br')
OPEN_RINGS = (0, 1)   # 모체 X선 4,8-H···O 2.695 Å(겹침 쪽) — 고리 2 · 3 은 4.101 Å(열린 쪽, e24i)
NAMES = {'Cl': 'e24j_cl_ovl', 'Br': 'e24j_br_ovl'}


def one(a0, G, S, kind, chosen, name, frac, rec):
    new, th, hist, loc = B.build(a0, G, S, kind, chosen)
    path = os.path.join(OUTD, name + '.cif'); B.write_cif(path, new)
    r = {'name': name, 'kind': kind, 'fraction': frac, 'n_substituted': len(chosen),
         'rings': sorted({s['ring'] for s in chosen}), 'sweeps_changed': hist,
         'torsion_deg': {str(k): round(math.degrees(v), 1) for k, v in th.items()},
         'fragment_local': [[e, [round(x, 4) for x in pp]] for e, pp in loc],
         **E.checks(new, len(chosen) * len(loc), loc, kind, len(chosen)), 'clash_check': B.CK.check(path)}
    rec['rows'].append(r)
    print(f"{name:22s} {r['formula']:28s} 비결합 최소 {r['nonbonded_min_A(topo>=3)']} · 치환기 {r['substituent_nonbonded_min_A']} · "
          f"C–X {r['C-X_range']} · 내부 {r['substituent_internal_bond_range']} · 충돌검사 {'통과' if r['clash_check']['pass'] else '탈락'} · 재주사 {hist}", flush=True)


def main():
    os.makedirs(OUTD, exist_ok=True)
    a0 = read(B.SRC); a0 = Atoms(a0.get_chemical_symbols(), positions=a0.positions, cell=a0.cell, pbc=True)
    G = B.graph(a0); S, nring = B.sites(a0, G)
    assert nring == 4 and len(S) == 8, (nring, len(S))
    rec = {'test': '보완 #5 빌드 — 겹침 쪽 링커(고리 0 · 1) 4,8-치환 · 배치 민감도', 'assign': 'ASSIGN_ZNBDT_NO2_PLACEMENT_20261107.md §2-1',
           'builder': 'build_e24i_bdtdc.py 사본 → build_e24_bdtdc.py → build_e22_bdtdc.py(6bad71ad) import', 'template': os.path.relpath(B.SRC, HERE),
           'seed': B.SEED, 'torsion_step_deg': B.STEP, 'open_rings': list(OPEN_RINGS), 'rows': []}
    chosen = [s_ for s_ in S if s_['ring'] in OPEN_RINGS]
    assert len(chosen) == 4, len(chosen)
    for kind in KINDS:
        one(a0, G, S, kind, chosen, NAMES[kind], 0.5, rec)
    json.dump(rec, open(os.path.join(OUTD, 'e24j_build.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1, default=float)
    return 0


if __name__ == '__main__':
    sys.exit(main())
