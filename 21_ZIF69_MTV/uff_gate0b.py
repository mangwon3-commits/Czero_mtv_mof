# -*- coding: utf-8 -*-
"""관문(0b)을 UFF4MOF 이완본(초격자 · 셀 변형)에 대기 — E-24i 등록 서술 (3)("UFF4MOF 상한 300 수렴 뒤 통로 · (0b) 충돌 유무").
`clash_gate.check` 무수정 호출. 모체 기준만 바꿈: 모체 X선 분율 좌표를 **대상 초격자의 격자**에 놓고 rep 만큼 복제
(셀 변형을 따라감 — 모체 위상은 그대로, 짝짓기 문턱 0.8 Å 도 그대로).
검사: 치환 원자 수가 (입력 이완본의 치환 원자 수 × rep) 와 같아야 짝짓기가 성립한 것 — 다르면 '짝짓기 실패' 로 판정량을 안 냄.
사용: python uff_gate0b.py <tag> <after.cif> [rep_a rep_b rep_c]   (rep 기본 2 2 3 — run_one 초격자)
"""
import sys
import numpy as np
from ase import Atoms
from ase.io import read
import clash_gate as G


def scaled_parent(target, rep):
    par = read(G.PARENT)
    cell = np.array(target.cell) / np.array(rep)[:, None]
    f0 = par.get_scaled_positions()
    fr, sy = [], []
    for i in range(rep[0]):
        for j in range(rep[1]):
            for k in range(rep[2]):
                fr.append((f0 + [i, j, k]) / rep); sy += par.get_chemical_symbols()
    return Atoms(sy, scaled_positions=np.vstack(fr), cell=target.cell, pbc=True)


def run(tag, path, rep=(2, 2, 3)):
    tgt = read(path)
    base = G.check(f'relax_tnf/{tag}_relaxed.cif')
    r = G.check(path, scaled_parent(tgt, rep))
    want = base['n_sub_atoms'] * int(np.prod(rep))
    r['n_sub_expected'] = want
    r['mapping_ok'] = r['n_sub_atoms'] == want
    if not r['mapping_ok']:
        r['pass_0b'] = None
    return base, r


if __name__ == '__main__':
    tag, path = sys.argv[1], sys.argv[2]
    rep = tuple(int(x) for x in sys.argv[3:6]) if len(sys.argv) >= 6 else (2, 2, 3)
    base, r = run(tag, path, rep)
    print(f"{tag}: 입력 이완본 최소 여유 {base['min_margin_A']:+.3f} ({base['worst_pair']}) · UFF4MOF 뒤 {r['min_margin_A']:+.3f} ({r['worst_pair']}) · "
          f"충돌 짝 {r['n_clash_pairs']} · 치환 원자 {r['n_sub_atoms']}/{r['n_sub_expected']} · (0b) {r['pass_0b']}")
