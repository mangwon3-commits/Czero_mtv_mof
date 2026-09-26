# -*- coding: utf-8 -*-
"""관문(0b) — 치환기 무거운 원자 충돌(결함 §25 고침). 등록 `ASSIGN_MAGI5B_20260925.md` §HKHOME 22차(E-24i).
정의: 치환기 무거운 원자 X 와 골격(또는 다른 치환기)의 무거운 원자 Y 사이 거리 d 에 대해
      겹침 = r_vdW(X) + r_vdW(Y) − d ≥ 0.4 Å 이면 **충돌**(MolProbity 심한 충돌 정의). Bondi 반지름.
결합 판정은 **검사 대상(이완 뒤) 구조에서 다시 만들지 않음** — §25 의 결함이 바로 그것(X–O 가 결합 길이로 붙으면 "결합" 으로 보고 빠짐).
  · 골격 원자 = 모체 X선(`e22_candidates/E22_ZnDia_parent.cif`)의 같은 원소 원자와 0.8 Å 안에서 짝지어지는 원자. 나머지 = 치환기 원자.
  · 제외 짝: ① 같은 치환기 무리 안 ② 치환기 무리가 붙은 고리 C(부착 C = 치환기 첫 원자에서 2.1 Å 안의 골격 C)와 **모체 위상에서 그 C 로부터 2 결합 안**의 골격 원자.
H 가 낀 짝은 이전 관문(0a)(이종–H ≥ 1.8 Å) 그대로 — 여기서는 안 봄.
사용: python clash_gate.py <cif> [<cif> ...]   → 행마다 최소 여유(= d − (r_X + r_Y)) · 최악 짝 · 충돌 수 · pass
"""
import collections, json, sys
import numpy as np
from ase.io import read
from ase.data import covalent_radii
from ase.geometry import find_mic
from ase.neighborlist import neighbor_list

BONDI = {'C': 1.70, 'N': 1.55, 'O': 1.52, 'F': 1.47, 'S': 1.80, 'Cl': 1.75, 'Br': 1.85, 'Zn': 1.39, 'H': 1.20}
OVERLAP = 0.4
PARENT = 'e22_candidates/E22_ZnDia_parent.cif'


def graph(a):
    cuts = [covalent_radii[z] * 1.15 if a[k].symbol != 'Zn' else 1.45 for k, z in enumerate(a.numbers)]
    i, j = neighbor_list('ij', a, cuts); G = collections.defaultdict(set)
    for x, y in zip(i, j): G[x].add(y)
    return G


def check(path, parent=None):
    par = parent or read(PARENT); Gp = graph(par); P = par.get_positions(); ps = par.get_chemical_symbols()
    a = read(path); s = a.get_chemical_symbols(); X = a.get_positions(); cell = a.cell
    fw = {}                                              # 대상 원자 → 모체 원자
    for k in range(len(a)):
        _, dl = find_mic(P - X[k], cell, pbc=True)
        cand = [q for q in np.argsort(dl)[:6] if dl[q] < 0.8 and ps[q] == s[k] and q not in fw.values()]
        if cand: fw[k] = int(cand[0])
    sub = [k for k in range(len(a)) if k not in fw]
    # 치환기 무리(치환기 원자끼리 1.75 Å 안으로 이어진 덩어리)와 부착 C
    groups, seen = [], set()
    for k in sub:
        if k in seen: continue
        g, stack = set(), [k]
        while stack:
            u = stack.pop()
            if u in g: continue
            g.add(u)
            _, dl = find_mic(X[sub] - X[u], cell, pbc=True)
            stack += [sub[q] for q in range(len(sub)) if dl[q] < 1.75 and sub[q] not in g]
        seen |= g; groups.append(g)
    fw_rev = {v: k for k, v in fw.items()}
    rows, clashes = [], 0
    worst = (9.9, None)
    for g in groups:
        heavy = [u for u in g if s[u] != 'H']
        if not heavy: continue
        att = None
        for u in heavy:
            for k, pk in fw.items():
                if s[k] == 'C':
                    _, d = find_mic(X[k] - X[u], cell, pbc=True)
                    if d < 2.1: att = pk; break
            if att is not None: break
        excl = set()
        if att is not None:
            excl = {att} | Gp[att] | {w for v in Gp[att] for w in Gp[v]}
        excl_idx = {fw_rev[q] for q in excl if q in fw_rev}
        for u in heavy:
            for k in range(len(a)):
                if k in g or k in excl_idx or s[k] == 'H' or s[k] not in BONDI: continue
                _, d = find_mic(X[k] - X[u], cell, pbc=True)
                if d > 4.0: continue
                margin = d - (BONDI[s[u]] + BONDI[s[k]])
                if margin < worst[0]: worst = (round(float(margin), 3), f'{s[u]}{u}···{s[k]}{k} {d:.3f}')
                if -margin >= OVERLAP: clashes += 1
    return {'cif': path, 'n_sub_atoms': len(sub), 'n_groups': len(groups), 'min_margin_A': worst[0], 'worst_pair': worst[1],
            'n_clash_pairs': clashes, 'pass_0b': clashes == 0}


if __name__ == '__main__':
    par = read(PARENT); out = []
    for p in sys.argv[1:]:
        r = check(p, par); out.append(r)
        print(f"{p:48s} 치환 원자 {r['n_sub_atoms']:3d} · 무리 {r['n_groups']} · 최소 여유 {r['min_margin_A']:+.3f} Å ({r['worst_pair']}) · 충돌 짝 {r['n_clash_pairs']} · (0b) {'통과' if r['pass_0b'] else '탈락'}", flush=True)
    if len(sys.argv) > 1 and '--json' in ' '.join(sys.argv): pass
