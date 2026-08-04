"""생성된 모든 MTV 구조에서 '골격에 붙지 않은 원자'를 찾아낸다.

발견 경위:
    clIm 50% 구조에서 Cl 14개 중 6개가 어떤 탄소로부터도 4.4~4.7 A 떨어진
    채 기공 한가운데(분율좌표 ~0.5,0.5,0.5)에 떠 있었다. 서로는 1.36~1.40 A로
    뭉쳐 있다. 즉 치환기가 링커에 결합되지 못하고 공동 중심에 버려진 것이다.

왜 지금까지 안 걸렸나:
    빌더가 '최소 원자간 거리'만 검사했는데, 구조에는 항상 메틸 C-H 결합
    (0.929 A)이 있어서 그게 최솟값을 차지한다. 1.37 A짜리 Cl-Cl 충돌도,
    4.7 A짜리 고아 원자도 전역 최솟값에는 나타나지 않는다. 결합 거리가
    비결합 이상을 가려버린 것이다.

검사 항목:
    (1) 고아 원자  -- 공유결합 반지름 합의 1.3배 안에 이웃이 없는 중원자
    (2) 비결합 충돌 -- 결합이 아닌데 vdW 접촉보다 훨씬 가까운 쌍
    (3) 연결 성분  -- 골격이 하나로 이어져 있는가
"""
import glob
import os
import sys

import numpy as np
import networkx as nx
from ase.data import atomic_numbers, covalent_radii
from ase.io import read
from ase.neighborlist import NeighborList, natural_cutoffs

# 결합 판정 여유. natural_cutoffs 기본(1.0)보다 넉넉히 잡아도 고아는 고아다.
BOND_MULT = 1.30
# 비결합인데 이 거리보다 가까우면 충돌로 본다 (H 포함 최소 접촉의 하한)
CLASH = 1.60


def audit(path):
    a = read(path)
    s = a.get_chemical_symbols()
    n = len(a)
    nl = NeighborList(natural_cutoffs(a, mult=BOND_MULT), skin=0.0,
                      self_interaction=False, bothways=True)
    nl.update(a)
    G = nx.Graph()
    G.add_nodes_from(range(n))
    for i in range(n):
        for j in nl.get_neighbors(i)[0]:
            G.add_edge(i, int(j))

    orphans = [i for i in range(n) if s[i] != 'H' and G.degree(i) == 0]
    h_orphans = [i for i in range(n) if s[i] == 'H' and G.degree(i) == 0]

    d = a.get_all_distances(mic=True)
    np.fill_diagonal(d, np.inf)
    # 1,3 쌍(공통 이웃을 가진 원자쌍)은 결합이 아니어도 가까운 게 정상이다.
    # 메틸의 geminal H-H가 대표적 -- C-H가 0.929 A인 이 구조에서는
    # 0.929 x 2 x sin(109.47/2) = 1.52 A 로, 순수 ZIF-8에도 24x3=72쌍 존재한다.
    # 이걸 충돌로 세면 대조군조차 '결함'이 되므로 반드시 제외해야 한다.
    clashes = []
    for i in range(n):
        for j in range(i + 1, n):
            if d[i, j] >= CLASH or G.has_edge(i, j):
                continue
            if set(G.neighbors(i)) & set(G.neighbors(j)):
                continue                      # 1,3 쌍
            clashes.append((i, j, round(float(d[i, j]), 3), s[i], s[j]))

    comps = list(nx.connected_components(G))
    big = max((len(c) for c in comps), default=0)
    return {'n': n, 'orphans': orphans, 'h_orphans': h_orphans,
            'clashes': clashes, 'n_components': len(comps),
            'largest_component': big, 'detached_atoms': n - big}


def main():
    roots = ['03_Generated_MTV_ZIFs', '05_MTV_Ligand_Library', '07_Bracketed_MTV',
             '14_Strategies/structures', '16_DefectStability/structures',
             '17_NestEffect/structures', '18_PoreNarrowing/structures']
    base = os.path.dirname(os.path.abspath(__file__))
    files = []
    for r in roots:
        files += sorted(glob.glob(os.path.join(base, r, '*.cif')))

    print(f'{"파일":<52} {"원자":>5} {"고아":>5} {"충돌":>5} {"분리":>5}  판정')
    print('-' * 92)
    bad = []
    for f in files:
        try:
            r = audit(f)
        except Exception as e:
            print(f'{os.path.relpath(f, base):<52} 읽기실패 {type(e).__name__}')
            continue
        no = len(r['orphans']) + len(r['h_orphans'])
        nc = len(r['clashes'])
        det = r['detached_atoms']
        flag = 'OK' if (no == 0 and nc == 0 and det == 0) else '결함'
        if flag == '결함':
            bad.append((os.path.relpath(f, base), r))
        print(f'{os.path.relpath(f, base):<52} {r["n"]:>5} {no:>5} {nc:>5} '
              f'{det:>5}  {flag}')

    print(f'\n결함 구조 {len(bad)}/{len(files)}')
    for name, r in bad:
        det = [f'{s}' for s in set()]
        print(f'\n  {name}')
        if r['orphans']:
            a = read(os.path.join(base, name))
            syms = a.get_chemical_symbols()
            from collections import Counter
            print(f'    고아 중원자 {len(r["orphans"])}개: '
                  f'{dict(Counter(syms[i] for i in r["orphans"]))}')
        if r['h_orphans']:
            print(f'    고아 수소 {len(r["h_orphans"])}개')
        if r['clashes']:
            worst = sorted(r['clashes'], key=lambda x: x[2])[:3]
            print(f'    비결합 충돌 {len(r["clashes"])}개, 최악: '
                  + ', '.join(f'{c[3]}-{c[4]} {c[2]}A' for c in worst))
        if r['detached_atoms']:
            print(f'    골격에서 분리된 원자 {r["detached_atoms"]}개 '
                  f'(연결성분 {r["n_components"]}개)')
    return 0


if __name__ == '__main__':
    sys.exit(main())
