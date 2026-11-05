# -*- coding: utf-8 -*-
"""MAGI-007 보완 명령 #3 (랩탑) — 열린 링커(고리 2 · 3)의 4,8-자리 넷에 −NO₂. 등록 `ASSIGN_ZNBDT_C2_FOLLOWUP_20261105.md` §3(자료 0건).
`build_znbdt_c1_bdtdc.py`(HKHOME 61b4ee4a) 사본 — 바꾼 것 넷: KINDS = ('NO2',) · SMILES 'NO2' = 'c1ccccc1[N+](=O)[O-]'(E-22 NO₂ 와 같은 조각) ·
출력 폴더 `znbdt_no2_screen/` · 기록 파일 `znbdt_no2_build.json`. 고른 자리 OPEN_RINGS = (2, 3) · one() · main() 은 원판 그대로.
⚠ 조각은 rdkit PhX 한 배좌를 강체로 C–X 축 둘레로만 돌림(원판 규약) — NO₂ 평면 비틀림은 이 회전으로만 찾음.
⚠ 이 기기(랩탑)에는 xtb 가 없습니다(MACHINE_CAPABILITIES.md). 이완 · 관문 (0a)(0b)는 xtb 가 있는 기기가 relax_tnf.py 로 잇습니다.
실행: czeromof 파이썬(rdkit · ase) — `python build_znbdt_no2_bdtdc.py` (21_ZIF69_MTV 에서)
"""
import json, math, os, random, sys
from ase import Atoms
from ase.io import read
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import build_e24_bdtdc as E   # noqa: E402  (import 만 — main 은 안 부름)
B = E.B
B.SMILES.update({'NO2': 'c1ccccc1[N+](=O)[O-]'})
OUTD = os.path.join(HERE, 'znbdt_no2_screen')
KINDS = ('NO2',)
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
    rec = {'test': '보완 #3 빌드 — 열린 링커 4,8-(NO₂)₂ 선별', 'assign': 'ASSIGN_ZNBDT_C2_FOLLOWUP_20261105.md §3',
           'builder': 'build_znbdt_c1_bdtdc.py 사본 → build_e24i_bdtdc.py 사본 → build_e24_bdtdc.py → build_e22_bdtdc.py(6bad71ad) import', 'template': os.path.relpath(B.SRC, HERE),
           'seed': B.SEED, 'torsion_step_deg': B.STEP, 'open_rings': list(OPEN_RINGS), 'rows': []}
    chosen = [s_ for s_ in S if s_['ring'] in OPEN_RINGS]
    assert len(chosen) == 4, len(chosen)
    for kind in KINDS:
        one(a0, G, S, kind, chosen, f'E24i_ZnDia_{kind}_open', 0.5, rec)
    json.dump(rec, open(os.path.join(OUTD, 'znbdt_no2_build.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1, default=float)
    return 0


if __name__ == '__main__':
    sys.exit(main())
