"""check_substituent_clash.py 를 **금속에 무관하게** 만든 판.

[왜 필요한가]
    원본은 금속을 `'Zn'` 문자열로 하드코딩합니다(76·86행).

        n_zn = int((sym == 'Zn').sum())
        if sym[k] != 'Zn' and sym[int(m)] != 'Zn': ...
        expected = n_zn * 3

    ZIF-67 은 금속이 Co 라 n_zn = 0 이 되고, 금속을 그래프에서 빼지 않으니 골격이
    통째로 한 덩어리가 됩니다. 그래서 **성분 1 / 기대 0 / 융합 -1** 로, 멀쩡한
    모체까지 9개 전부 탈락으로 신고합니다. **검사기가 틀린 것입니다.**

    이 프로젝트에서 같은 형태의 실수를 세 번 했습니다 -- 부착 원자를 상수로,
    고리 인덱스를 상수로, 그리고 여기서는 금속 원소를 상수로.
    **구조를 다루는 코드에 원소나 인덱스를 박으면 다른 모체에서 조용히 깨집니다.**

[원본을 고치지 않는 이유]
    같은 작업 디렉터리를 다른 세션이 쓰고 있습니다(SESSION_LOG.md).

[화학 상수는 원본에서 가져온다 -- 진실의 출처를 하나로]
    문턱값(BOND_FLOOR_FRAC / H_CLASH / BOND_SQUASH_FRAC)과 금지 원소쌍 판정
    `forbidden()` 은 **import 해서 그대로 씁니다.** 옮겨 적으면 원본이 바뀔 때
    갈라집니다.

[내가 처음에 틀렸던 것 -- 2026-08-15]
    첫 판은 (B) 를 "금지 원소쌍이면 신고" 로만 짰습니다. 거리 조건
    (공유반지름 합의 0.95배 미만)을 빼먹은 것입니다. 그러자 **니트로기의
    geminal O-O(2.1 A, 정상)** 를 전부 결함으로 신고해, nIm 계열에서
    치환기 하나당 정확히 하나씩 가짜 경보가 났습니다.
    원본 주석이 바로 그것을 경고하고 있었습니다(45~49행).

    **대조군이 잡아 줬습니다** -- 같은 검사기를 ZIF-69 v2(통과가 확인된 구조)에
    걸었더니 saIm100 에서 114건이 나왔습니다. 답을 아는 경우를 항상 함께
    돌려야 하는 이유입니다.
"""
import glob
import os
import sys

import networkx as nx
import numpy as np
from ase.data import atomic_numbers, covalent_radii
from ase.io import read
from ase.neighborlist import NeighborList, natural_cutoffs, neighbor_list

sys.path.insert(0, '/home/mangwon1/mof_project/21_ZIF69_MTV')
import check_substituent_clash as C                                # noqa: E402

METALS = {'Zn', 'Co', 'Cd', 'Fe', 'Mn', 'Ni', 'Cu', 'Mg'}
H_BONDS_TO = ('C', 'N', 'O', 'S')


def rsum(a, b):
    return (covalent_radii[atomic_numbers[a]] + covalent_radii[atomic_numbers[b]])


def check(path):
    a = read(path)
    sym = np.array(a.get_chemical_symbols())
    is_metal = np.isin(sym, list(METALS))
    n_metal = int(is_metal.sum())

    # (A) 성분 수. 금속을 빼면 링커만 남는다.
    #     금속 하나당 링커 2개 + 금속 자신(고립 노드) = 금속 수 x 3.
    nl = NeighborList(natural_cutoffs(a, mult=C.BOND_MULT), skin=0.0,
                      self_interaction=False, bothways=True)
    nl.update(a)
    G = nx.Graph()
    G.add_nodes_from(range(len(a)))
    for k in range(len(a)):
        if is_metal[k]:
            continue
        for m in nl.get_neighbors(k)[0]:
            if not is_metal[int(m)]:
                G.add_edge(k, int(m))
    comps = list(nx.connected_components(G))
    expected = n_metal * 3
    fused = expected - len(comps)

    i, j, d = neighbor_list('ijd', a, C.CUT)

    # (B) 금지 접촉 -- **거리 조건이 핵심이다.** 원소쌍만 보면 정상 geminal 을 잡는다.
    bad = []
    for x, y, dd in zip(i, j, d):
        if x >= y or not C.forbidden(sym[x], sym[y]):
            continue
        if dd < C.BOND_FLOOR_FRAC * rsum(sym[x], sym[y]):
            bad.append((round(float(dd), 3), f'{sym[x]}-{sym[y]}'))

    # (C) 수소 관통
    h_bad = []
    i2, j2, d2 = neighbor_list('ijd', a, 2.2)
    near = {}
    for x, y, dd in zip(i2, j2, d2):
        if sym[x] == 'H' and sym[y] != 'H':
            near.setdefault(int(x), []).append((float(dd), int(y)))
    for h, lst in near.items():
        lst.sort()
        cand = [(dd, y) for dd, y in lst if sym[y] in H_BONDS_TO]
        bonded = cand[0][1] if cand else lst[0][1]
        for dd, y in lst:
            if y != bonded and dd < C.H_CLASH:
                h_bad.append((round(dd, 3), f'H-{sym[y]}'))

    # (D) 짓눌린 결합
    short = []
    for x, y, dd in zip(i, j, d):
        if x >= y or sym[x] == 'H' or sym[y] == 'H':
            continue
        if dd < C.BOND_SQUASH_FRAC * rsum(sym[x], sym[y]):
            short.append((round(float(dd), 3), f'{sym[x]}-{sym[y]}'))

    worst = min(bad + h_bad + short, default=None)
    return {'name': os.path.basename(path), 'n_atoms': len(a), 'n_metal': n_metal,
            'n_components': len(comps), 'expected': expected, 'fused': fused,
            'B': len(bad), 'C': len(h_bad), 'D': len(short), 'worst': worst,
            'pass': fused == 0 and not bad and not h_bad and not short}


def main(patterns):
    files = []
    for p in patterns:
        files += sorted(glob.glob(p))
    if not files:
        print('구조 없음')
        return 1
    print(f'{"구조":<26} {"원자":>5} {"금속":>4} {"성분":>5} {"기대":>5} {"융합":>5} '
          f'{"B금지":>5} {"C관통":>5} {"D짓눌림":>7} {"최악":>14}  판정')
    print('-' * 104)
    bad = 0
    for f in files:
        r = check(f)
        if not r['pass']:
            bad += 1
        w = f'{r["worst"][1]} {r["worst"][0]}' if r['worst'] else '-'
        print(f'{r["name"][:26]:<26} {r["n_atoms"]:>5} {r["n_metal"]:>4} '
              f'{r["n_components"]:>5} {r["expected"]:>5} {r["fused"]:>5} '
              f'{r["B"]:>5} {r["C"]:>5} {r["D"]:>7} {w:>14}  '
              f'{"통과" if r["pass"] else "*** 탈락"}')
    print('-' * 104)
    print(f'{len(files)}개 중 {bad}개 탈락')
    return 0 if bad == 0 else 1


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
