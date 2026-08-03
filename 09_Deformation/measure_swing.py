"""ZIF-8 게이트 오프닝의 반응좌표(리간드 스윙 각도)를 정의하고 두 상에서 측정한다.

정의:
    각 이미다졸레이트는 배위 질소 두 개(N1, N2)를 통해 Zn 두 개를 잇는다.
    N1->N2 축이 링이 회전할 수 있는 유일한 축이며, 이 축 둘레의 회전이 곧 '스윙'이다.

    스윙 각도 phi = (N-N 중점 -> C2 방향) 와 (N-N 중점 -> Zn-Zn 중점 방향) 사이의 각,
    단 둘 다 N-N 축에 수직인 평면에 투영해서 측정한다.

    이 정의는 구조 간 원자 순서 대응이 필요 없어(각 링커에서 자체적으로 계산)
    출처가 다른 두 CIF를 비교할 수 있다.
"""
import sys

import numpy as np
from ase.io import read
from ase.neighborlist import NeighborList, natural_cutoffs


def bond_graph(atoms):
    nl = NeighborList(natural_cutoffs(atoms, mult=1.15), skin=0.0,
                      self_interaction=False, bothways=True)
    nl.update(atoms)
    return nl


def swing_angles(path, metal=('Zn', 'Co')):
    atoms = read(path)
    syms = atoms.get_chemical_symbols()
    nl = bond_graph(atoms)
    pos = atoms.get_positions()
    cell = atoms.get_cell()

    def mic(v):
        """최소 이미지 규약으로 벡터 보정."""
        f = np.linalg.solve(cell.T, v)
        f -= np.round(f)
        return cell.T @ f

    # 각 링커: C,N만으로 5-사이클 추출
    import networkx as nx
    G = nx.Graph()
    G.add_nodes_from(range(len(atoms)))
    for i in range(len(atoms)):
        nb, _ = nl.get_neighbors(i)
        for j in nb:
            G.add_edge(i, int(j))
    heavy = [i for i in G.nodes if syms[i] in ('C', 'N')]
    rings = [c for c in nx.cycle_basis(G.subgraph(heavy)) if len(c) == 5]

    out = []
    for ring in rings:
        ns = [i for i in ring if syms[i] == 'N']
        if len(ns) != 2:
            continue
        n1, n2 = ns
        # C2 = 두 질소 모두와 결합한 고리 탄소
        c2 = next((i for i in ring if syms[i] == 'C'
                   and G.has_edge(i, n1) and G.has_edge(i, n2)), None)
        if c2 is None:
            continue
        # 각 N에 배위한 금속
        m1 = next((j for j in G.neighbors(n1) if syms[j] in metal), None)
        m2 = next((j for j in G.neighbors(n2) if syms[j] in metal), None)
        if m1 is None or m2 is None:
            continue

        p_n1 = pos[n1]
        p_n2 = p_n1 + mic(pos[n2] - p_n1)
        p_c2 = p_n1 + mic(pos[c2] - p_n1)
        p_m1 = p_n1 + mic(pos[m1] - p_n1)
        p_m2 = p_n1 + mic(pos[m2] - p_n1)

        axis = p_n2 - p_n1
        axis /= np.linalg.norm(axis)
        mid_n = 0.5 * (p_n1 + p_n2)
        mid_m = 0.5 * (p_m1 + p_m2)

        # 축에 수직인 성분만 남긴다
        def perp(v):
            v = v - np.dot(v, axis) * axis
            n = np.linalg.norm(v)
            return v / n if n > 1e-8 else None

        r = perp(p_c2 - mid_n)     # 링 방향
        z = perp(mid_m - mid_n)    # 금속 쪽 기준 방향
        if r is None or z is None:
            continue
        ang = np.degrees(np.arccos(np.clip(np.dot(r, z), -1, 1)))
        out.append(ang)
    return np.array(out)


if __name__ == '__main__':
    files = sys.argv[1:] or ['ZIF8_closed.cif', 'ZIF8_open.cif']
    print(f'{"구조":<26} {"링커수":>6} {"평균 phi":>10} {"표준편차":>9} {"최소":>8} {"최대":>8}')
    print('-' * 74)
    res = {}
    for f in files:
        a = swing_angles(f)
        if len(a) == 0:
            print(f'{f:<26} 측정 실패')
            continue
        res[f] = a
        print(f'{f:<26} {len(a):>6} {a.mean():>10.2f} {a.std():>9.2f} '
              f'{a.min():>8.2f} {a.max():>8.2f}')
    if len(res) == 2:
        k = list(res)
        d = res[k[1]].mean() - res[k[0]].mean()
        print(f'\n스윙 각도 차이 (열림 - 닫힘): {d:+.2f} deg')
        print('-> 이 각도 구간을 반응좌표로 스캔한다.')
