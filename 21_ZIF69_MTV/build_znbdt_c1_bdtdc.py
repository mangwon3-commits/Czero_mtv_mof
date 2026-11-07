# -*- coding: utf-8 -*-
"""ZNBDT-C1 — 열린 링커(고리 2 · 3)의 4,8-자리 넷에 −C≡CH. 등록 `ASSIGN_ZNBDT_C1_20261105.md` §1(종합자 가지 70cee7bc · 자료 0건).
`build_e24i_bdtdc.py` 사본 — 바꾼 것 셋: KINDS = ('CCH',) · SMILES 'CCH' = 'c1ccccc1C#C'(E-24g `build_e24g_bdtdc.py:16` 과 같은 조각) ·
출력 폴더 `znbdt_c1_candidates/`(원판 폴더의 e24i_build.json 을 덮지 않으려고). 고른 자리 OPEN_RINGS = (2, 3) · one() · main() 은 원판 그대로.
네 자리가 같은 종류라 배열은 하나(MAGI-007 R3 hkhome D-12). 원판 머리말: MAGI-005 E-24i — 겹치지 않는 링커(고리 2 · 3)에만 4,8-치환.
⚠ 조각은 rdkit PhX 한 배좌를 강체로 C–X 축 둘레로만 돌림(원판 규약) — C≡C–H 는 직선이라 내부 비틀림 없음.
실행: czeromof 파이썬(rdkit · ase) — `python build_znbdt_c1_bdtdc.py` (21_ZIF69_MTV 에서)
"""
import json, math, os, random, sys
from ase import Atoms
from ase.io import read
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import build_e24_bdtdc as E   # noqa: E402  (import 만 — main 은 안 부름)
B = E.B
B.SMILES.update({'CCH': 'c1ccccc1C#C'})
OUTD = os.path.join(HERE, 'znbdt_c1_candidates')
KINDS = ('CCH',)
OPEN_RINGS = (2, 3)   # 모체 X선 4,8-H···O 4.101 Å(열린 쪽) — 고리 0 · 1 은 2.695 Å(겹침)


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
    rec = {'test': 'ZNBDT-C1 빌드 — 열린 링커 4,8-(C≡CH)₂', 'assign': 'ASSIGN_ZNBDT_C1_20261105.md §1',
           'builder': 'build_e24i_bdtdc.py 사본 → build_e24_bdtdc.py → build_e22_bdtdc.py(6bad71ad) import', 'template': os.path.relpath(B.SRC, HERE),
           'seed': B.SEED, 'torsion_step_deg': B.STEP, 'open_rings': list(OPEN_RINGS), 'rows': []}
    chosen = [s_ for s_ in S if s_['ring'] in OPEN_RINGS]
    assert len(chosen) == 4, len(chosen)
    for kind in KINDS:
        one(a0, G, S, kind, chosen, f'E24i_ZnDia_{kind}_open', 0.5, rec)
    json.dump(rec, open(os.path.join(OUTD, 'znbdt_c1_build.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1, default=float)
    return 0


if __name__ == '__main__':
    sys.exit(main())
