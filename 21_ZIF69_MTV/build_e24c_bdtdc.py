# -*- coding: utf-8 -*-
"""MAGI-005 E-24c — Zn(bib)(bdtdc) 4,8-자리 치환기 확장(−Cl · −OCH₃ · −C₂H₅ · −SCH₃) 100 % 후보 빌드.
등록 `ASSIGN_MAGI5B_20260925.md` §HKHOME 16차. `build_e24_bdtdc.py`(→ laptop `build_e22_bdtdc.py` 6bad71ad)를 **수정 없이 import** —
자리 찾기 · rdkit 조각 · 비틀림 주사 · 충돌 검사 · 점검 함수 그대로. 바꾼 것: SMILES 네 개 · 출력 폴더 · 이름(E24c_…).
⚠ 조각은 rdkit PhX 한 배좌를 **강체로** C–X 축 둘레로만 돌립니다(원판 규약). OCH₃ · C₂H₅ · SCH₃ 의 내부 비틀림은
  rdkit MMFF 배좌 그대로 — GFN-FF 이완이 그 뒤를 정리합니다. 이 한계는 E-22 NO₂ · SO₂Me 때와 같습니다.
"""
import json, math, os, sys
from ase import Atoms
from ase.io import read
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import build_e24_bdtdc as E   # noqa: E402  (import 만 — main 은 안 부름)
B = E.B
B.SMILES.update({'Cl': 'c1ccccc1Cl', 'OCH3': 'c1ccccc1OC', 'C2H5': 'c1ccccc1CC', 'SCH3': 'c1ccccc1SC'})
OUTD = os.path.join(HERE, 'e24c_candidates')
KINDS = ('Cl', 'OCH3', 'C2H5', 'SCH3')


def main():
    os.makedirs(OUTD, exist_ok=True)
    a0 = read(B.SRC); a0 = Atoms(a0.get_chemical_symbols(), positions=a0.positions, cell=a0.cell, pbc=True)
    G = B.graph(a0); S, nring = B.sites(a0, G)
    assert nring == 4 and len(S) == 8, (nring, len(S))
    rec = {'test': 'MAGI-005 E-24c 빌드', 'assign': 'ASSIGN_MAGI5B_20260925.md §HKHOME 16차', 'builder': 'build_e24_bdtdc.py → build_e22_bdtdc.py(6bad71ad) import',
           'template': os.path.relpath(B.SRC, HERE), 'seed': B.SEED, 'torsion_step_deg': B.STEP, 'rows': []}
    for kind in KINDS:
        new, th, hist, loc = B.build(a0, G, S, kind, S)
        name = f'E24c_ZnDia_{kind}_100'; path = os.path.join(OUTD, name + '.cif'); B.write_cif(path, new)
        r = {'name': name, 'kind': kind, 'fraction': 1.0, 'n_substituted': len(S), 'sweeps_changed': hist,
             'torsion_deg': {str(k): round(math.degrees(v), 1) for k, v in th.items()},
             'fragment_local': [[e, [round(x, 4) for x in pp]] for e, pp in loc],
             **E.checks(new, len(S) * len(loc), loc, kind, len(S)), 'clash_check': B.CK.check(path)}
        rec['rows'].append(r)
        print(f"{name:20s} {r['formula']:26s} 비결합 최소 {r['nonbonded_min_A(topo>=3)']} · 치환기 {r['substituent_nonbonded_min_A']} · "
              f"C–X {r['C-X_range']} · 내부 {r['substituent_internal_bond_range']} · 충돌검사 {'통과' if r['clash_check']['pass'] else '탈락'} · 재주사 {hist}", flush=True)
    json.dump(rec, open(os.path.join(OUTD, 'e24c_build.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1, default=float)
    return 0


if __name__ == '__main__':
    sys.exit(main())
