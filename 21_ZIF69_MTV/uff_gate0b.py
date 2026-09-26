# -*- coding: utf-8 -*-
"""관문(0b)을 UFF4MOF 이완본(초격자 · 셀 변형 · 평행이동 · 링커 회전)에 대기 — E-24i 등록 서술 (3)("UFF4MOF 상한 300 수렴 뒤 통로 · (0b) 충돌 유무").
`clash_gate.check` 무수정 호출 — 모체 기준(parent 인자)만 이 파일이 만듦.
  1. 모체 X선 분율 좌표를 대상 초격자 격자에 놓고 rep 만큼 복제(셀 변형을 따라감).
  2. 평행이동: 대상 Zn 마다 가장 가까운 모체 Zn 까지의 변위(최소상)를 모아 **중앙값**만큼 모체를 옮김(LAMMPS 상자 원점 이동 — 실측 CN a 축 ≈ −1.3 Å).
  3. 짝짓기: 같은 원소 · 거리 오름차순 1:1 · 문턱 1.3 Å(링커 회전 16° 에서 고리 가장자리 이동 ≈ 0.7 Å 를 품음). 짝 없는 대상 원자 = 치환기.
  4. 기준 구조 = 짝지은 모체 원자를 대상 위치로 옮긴 것(clash_gate 의 0.8 Å 짝짓기가 정확히 맞도록). **위상 검사**: 이 기준의 결합 그래프가
     옮기기 전 모체(X선 위상) 그래프와 원자 번호로 같아야 함 — 다르면 대상 기하에서 새 결합이 생긴 것(§25 결함의 재발)이므로 판정량을 안 냄.
  5. 치환 원자 수 = 입력 이완본 치환 원자 수 × rep 이어야 함 — 다르면 '짝짓기 실패'.
v1(a855ac9e)은 2 · 3 이 없어 실제 이완본(평행이동)에서 짝짓기 실패를 냈음(판정량 None — 거짓 판정은 없음).
사용: python uff_gate0b.py <tag> <after.cif> [rep_a rep_b rep_c]
"""
import sys
import numpy as np
from ase import Atoms
from ase.io import read
from ase.geometry import find_mic
import clash_gate as G

TOL = 1.3


def scaled_parent(target, rep):
    par = read(G.PARENT)
    f0 = par.get_scaled_positions(); fr, sy = [], []
    for i in range(rep[0]):
        for j in range(rep[1]):
            for k in range(rep[2]):
                fr.append((f0 + [i, j, k]) / rep); sy += par.get_chemical_symbols()
    return Atoms(sy, scaled_positions=np.vstack(fr), cell=target.cell, pbc=True)


def aligned_reference(tgt, rep):
    P0 = scaled_parent(tgt, rep); cell = np.array(tgt.cell)
    st, sp = np.array(tgt.get_chemical_symbols()), np.array(P0.get_chemical_symbols())
    X, P = tgt.get_positions(), P0.get_positions()
    zt, zp = np.where(st == 'Zn')[0], np.where(sp == 'Zn')[0]
    disp = []
    for k in zt:
        D, dl = find_mic(X[k] - P[zp], cell, pbc=True); disp.append(D[dl.argmin()])
    shift = np.median(np.array(disp), axis=0)
    P = P + shift
    pairs = []
    for el in set(sp):
        it, ip = np.where(st == el)[0], np.where(sp == el)[0]
        for k in it:
            _, dl = find_mic(P[ip] - X[k], cell, pbc=True)
            for q in np.argsort(dl)[:4]:
                if dl[q] < TOL: pairs.append((dl[q], k, ip[q]))
    pairs.sort(); used_t, used_p, match = set(), set(), {}
    for d, k, q in pairs:
        if k in used_t or q in used_p: continue
        used_t.add(k); used_p.add(q); match[q] = k
    ref = P0.copy(); ref.set_positions(P)
    before_graph = G.graph(ref)
    newpos = ref.get_positions()
    for q, k in match.items(): newpos[q] = X[k]
    ref.set_positions(newpos)
    after_graph = G.graph(ref)
    heavy = [q for q in range(len(ref)) if sp[q] != 'H']
    diff = sum(1 for q in heavy if {w for w in after_graph[q] if sp[w] != 'H'} != {w for w in before_graph[q] if sp[w] != 'H'})
    return ref, dict(shift_A=np.round(shift, 3).tolist(), n_matched=len(match), n_target=len(tgt), topology_diff_heavy=int(diff))


def run(tag, path, rep=(2, 2, 3)):
    tgt = read(path)
    base = G.check(f'relax_tnf/{tag}_relaxed.cif')
    ref, info = aligned_reference(tgt, rep)
    r = G.check(path, ref)
    r.update(info)
    r['n_sub_expected'] = base['n_sub_atoms'] * int(np.prod(rep))
    r['mapping_ok'] = r['n_sub_atoms'] == r['n_sub_expected'] and info['topology_diff_heavy'] == 0
    if not r['mapping_ok']:
        r['pass_0b'] = None
    return base, r


if __name__ == '__main__':
    tag, path = sys.argv[1], sys.argv[2]
    rep = tuple(int(x) for x in sys.argv[3:6]) if len(sys.argv) >= 6 else (2, 2, 3)
    base, r = run(tag, path, rep)
    print(f"{tag}: 입력 이완본 최소 여유 {base['min_margin_A']:+.3f} ({base['worst_pair']}) · UFF4MOF 뒤 {r['min_margin_A']:+.3f} ({r['worst_pair']}) · "
          f"충돌 짝 {r['n_clash_pairs']} · 치환 원자 {r['n_sub_atoms']}/{r['n_sub_expected']} · 평행이동 {r['shift_A']} · 위상 차 {r['topology_diff_heavy']} · (0b) {r['pass_0b']}", flush=True)
