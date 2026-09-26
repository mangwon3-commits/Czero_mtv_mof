# -*- coding: utf-8 -*-
"""통로 병목 분석(서술 도구) — 통로 축 c 를 따라 곧은 선을 긋고, 선에서 각 원자까지 거리 − vdW 반지름의 최소 = 그 선의 여유 반지름.
여유 반지름이 극대인 선 = 통로 중심선, 2 × 극대값 = 곧은 통로 가정의 PLD 추정(Zeo++ PLD 의 하한 쪽 근사), 그 최소를 만든 원자 = 병목 원자.
반지름: Zeo++ 기본(CCDC) H 1.09 · C 1.70 · N 1.55 · O 1.52 · S 1.80 · Zn 1.39 · Cl 1.75 · Br 1.85.
사용: python channel_pinch.py <cif> [격자 간격 Å, 기본 0.15]
"""
import sys
import numpy as np
from ase.io import read

R = {'H': 1.09, 'C': 1.70, 'N': 1.55, 'O': 1.52, 'S': 1.80, 'Zn': 1.39, 'Cl': 1.75, 'Br': 1.85, 'F': 1.47}


def analyse(path, step=0.15, sub_idx=None):
    a = read(path)
    cell = np.array(a.cell); X = a.get_positions(); sym = a.get_chemical_symbols(); rad = np.array([R[s] for s in sym])
    c_hat = cell[2] / np.linalg.norm(cell[2])
    # c 에 수직인 평면으로 투영(원자 + a · b 방향 이웃 상 ±1)
    P = lambda v: v - np.outer(v @ c_hat, c_hat) if v.ndim == 2 else v - (v @ c_hat) * c_hat
    imgs, rr, idx = [], [], []
    for i in (-1, 0, 1):
        for j in (-1, 0, 1):
            imgs.append(P(X + i * cell[0] + j * cell[1])); rr.append(rad); idx.append(np.arange(len(a)))
    Y = np.vstack(imgs); rr = np.concatenate(rr); idx = np.concatenate(idx)
    A, B = P(cell[0]), P(cell[1])                        # 투영 평면의 두 격자 벡터
    na, nb = int(np.linalg.norm(A) / step), int(np.linalg.norm(B) / step)
    u, v = np.meshgrid(np.arange(na) / na, np.arange(nb) / nb, indexing='ij')
    G = u.reshape(-1, 1) * A + v.reshape(-1, 1) * B
    best = np.full(len(G), 9.9); who = np.zeros(len(G), int)
    for s in range(0, len(Y), 400):
        d = np.linalg.norm(G[:, None, :] - Y[None, s:s + 400, :], axis=2) - rr[s:s + 400]
        k = d.argmin(1); m = d[np.arange(len(G)), k]
        upd = m < best; best[upd] = m[upd]; who[upd] = idx[s:s + 400][k[upd]]
    F = best.reshape(na, nb); W = who.reshape(na, nb)
    # 극대(주변 5×5 안 최대) · 여유 > 1.0 Å 만 통로 후보
    out = []
    for i in range(na):
        for j in range(nb):
            f = F[i, j]
            if f < 1.0: continue
            nb_ = F[np.ix_([(i + di) % na for di in range(-3, 4)], [(j + dj) % nb for dj in range(-3, 4)])]
            if f >= nb_.max() - 1e-9:
                out.append((round(i / na, 3), round(j / nb, 3), round(2 * f, 3), int(W[i, j]), sym[W[i, j]]))
    # 같은 봉우리 중복 제거
    ded = []
    for o in sorted(out, key=lambda t: -t[2]):
        if all(min(abs(o[0] - p[0]), 1 - abs(o[0] - p[0])) > 0.05 or min(abs(o[1] - p[1]), 1 - abs(o[1] - p[1])) > 0.05 for p in ded):
            ded.append(o)
    return ded, a


if __name__ == '__main__':
    step = float(sys.argv[2]) if len(sys.argv) > 2 else 0.15
    ded, a = analyse(sys.argv[1], step)
    for o in ded:
        print(f"  통로 중심 (a {o[0]:.3f}, b {o[1]:.3f}) · 곧은 선 PLD 추정 {o[2]:.3f} Å · 병목 원자 {o[4]}{o[3]}")


def label(a, k):
    """원자 k 의 소속: Zn 을 끊은 결합 조각 기준 — S 가 있으면 bdtdc, N 이 있으면 bib. 이웃 원소도 적음."""
    from ase.neighborlist import neighbor_list
    from ase.data import covalent_radii
    import collections
    cuts = [covalent_radii[z] * 1.15 for z in a.numbers]
    i, j = neighbor_list('ij', a, cuts); Gr = collections.defaultdict(set)
    s = a.get_chemical_symbols()
    for x, y in zip(i, j):
        if s[x] != 'Zn' and s[y] != 'Zn': Gr[x].add(y)
    seen, st = set(), [k]
    while st:
        u = st.pop()
        if u in seen: continue
        seen.add(u); st += list(Gr[u] - seen)
    els = {s[u] for u in seen}
    frag = 'bdtdc' if 'S' in els else ('bib' if 'N' in els else '?')
    nbrs = ''.join(sorted(s[u] for u in Gr[k]))
    return f"{frag}(이웃 {nbrs})"
