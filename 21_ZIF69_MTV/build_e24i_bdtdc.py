# -*- coding: utf-8 -*-
"""MAGI-005 E-24i — 겹치지 않는 링커(고리 2 · 3)에만 4,8-치환(−CH₃ · −Cl · −Br · −C₂H₅ · −CN). 등록 `ASSIGN_MAGI5B_20260925.md` §HKHOME 22차.
`build_e24g_bdtdc.py` 사본 — 바꾼 것: 치환기 · 고른 자리(고리 2 · 3 = 모체 4,8-H···O 4.10 Å 쪽) · 출력. 원판 머리말:
MAGI-005 E-24g · E-24h — Zn(bib)(bdtdc) 4,8-자리 치환기 2차 확장(−Br · −C≡CH · −CF₃ · −n-C₃H₇, 100 %)과
희석(−C₂H₅ · −Cl 50 %, 실현 A · B) 빌드. 등록 `ASSIGN_MAGI5B_20260925.md` §HKHOME 21차.
`build_e24_bdtdc.py`(→ laptop `build_e22_bdtdc.py` 6bad71ad)를 **수정 없이 import** — 자리 찾기 · rdkit 조각 · 비틀림 주사 ·
충돌 검사 · 점검 함수 그대로. 바꾼 것: SMILES · 출력 폴더 · 이름 · 50 % 고리 선택(E-22 main 과 같은 식).
50 % = 네 bdtdc 고리 중 두 고리의 4,8-자리 모두. 실현 A = random.Random(B.SEED).sample(rings, 2)(E-22 NO₂ 50 % 와 같은 짝) ·
실현 B = A 의 여집합. ⚠ 조각은 rdkit PhX 한 배좌를 강체로 C–X 축 둘레로만 돌림(원판 규약) — n-C₃H₇ · CF₃ 내부 비틀림은
MMFF 배좌 그대로, GFN-FF 이완이 정리(E-24c 와 같은 한계).
"""
import json, math, os, random, sys
from ase import Atoms
from ase.io import read
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import build_e24_bdtdc as E   # noqa: E402  (import 만 — main 은 안 부름)
B = E.B
B.SMILES.update({'Br': 'c1ccccc1Br', 'C2H5': 'c1ccccc1CC', 'Cl': 'c1ccccc1Cl', 'CH3': 'c1ccccc1C', 'CN': 'c1ccccc1C#N'})
OUTD = os.path.join(HERE, 'e24i_candidates')
KINDS = ('CH3', 'Cl', 'Br', 'C2H5', 'CN')
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
    rings = sorted({s['ring'] for s in S})
    rec = {'test': 'MAGI-005 E-24i 빌드 — 열린 링커만 치환', 'assign': 'ASSIGN_MAGI5B_20260925.md §HKHOME 22차',
           'builder': 'build_e24_bdtdc.py → build_e22_bdtdc.py(6bad71ad) import', 'template': os.path.relpath(B.SRC, HERE),
           'seed': B.SEED, 'torsion_step_deg': B.STEP, 'open_rings': list(OPEN_RINGS), 'rows': []}
    chosen = [s_ for s_ in S if s_['ring'] in OPEN_RINGS]
    assert len(chosen) == 4, len(chosen)
    for kind in KINDS:
        one(a0, G, S, kind, chosen, f'E24i_ZnDia_{kind}_open', 0.5, rec)
    json.dump(rec, open(os.path.join(OUTD, 'e24i_build.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1, default=float)
    return 0


if __name__ == '__main__':
    sys.exit(main())
