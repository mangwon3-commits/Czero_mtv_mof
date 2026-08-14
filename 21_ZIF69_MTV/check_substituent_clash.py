"""치환기끼리 관통한 구조를 찾아낸다 — audit_orphans.py 가 놓치는 결함.

[발견 경위]
    2026-08-14, 수분 MD 용 계를 조립하다가 황 하나에 결합이 5개씩 붙는 것을 봤다.
    원 구조를 뒤졌더니 ZIF69_saIm100 에서 인접한 두 술폰산기가 서로 **관통**해
    있었다 — S-S 2.642 A, O-O 0.924 A. 산소 하나가 황 두 개에 동시에 결합한
    것으로 인식될 만큼 겹쳐 있다.

[왜 audit_orphans.py 가 못 잡았나 — 이게 핵심이다]
    그쪽은 비결합 충돌을 세면서 **1,3 쌍(공통 이웃을 가진 쌍)을 제외**한다.
    메틸의 geminal H-H 를 충돌로 세지 않으려는 정당한 처리다. 그런데 겹침이
    심하면 두 치환기 사이에 결합이 하나 인식되고, 그러면 겹친 원자쌍이 **공통
    이웃을 갖게 되어** 1,3 쌍으로 분류되어 빠진다.

        결함이 충분히 심하면 결함 탐지기에서 스스로 사라진다.

    이 스크립트는 그래서 거리를 세지 않고 **연결 성분 개수**를 센다. 링커가
    서로 붙으면 성분 수가 줄고, 그건 어떤 예외 규칙으로도 가려지지 않는다.

[검사 두 가지]
    (A) 성분 수  — ZIF-69 단위셀은 Zn 24 + nIm 24 + 벤즈이미다졸레이트 24 = 72.
                   이보다 적으면 링커가 융합된 것이다. 결정적 검사.
    (B) 금지 접촉 — 이 라이브러리에서 결합을 만들 수 없는 원소쌍(할로겐-할로겐,
                   할로겐-O/N/S, O-O)이 vdW 접촉보다 훨씬 가까운 경우. 보조 검사.

    사용:  python check_substituent_clash.py [구조_glob ...]
"""
import glob
import os
import sys

import numpy as np
import networkx as nx
from ase.data import atomic_numbers, covalent_radii
from ase.io import read
from ase.neighborlist import NeighborList, natural_cutoffs, neighbor_list

BOND_MULT = 1.15          # 결합 인식 여유. audit_orphans 의 1.30 보다 보수적으로 잡는다
HALO = {'F', 'Cl', 'Br', 'I'}
# 금지 원소쌍이 **어떤 결합보다도 짧은** 거리에 있으면 관통이다.
#
# 단순히 "2.5 A 보다 가까우면 충돌"로 하면 안 된다. 니트로기의 두 산소는 같은 N 에
# 붙은 geminal 쌍이라 2.1 A 이고, CF3 의 F-F 는 2.16 A 다. 둘 다 정상이다.
# 그래서 공유결합 반지름 합에 대한 비율로 자른다 — 이 값보다 짧은 결합은 없다.
#
# audit_orphans.py 처럼 "공통 이웃이 있으면 제외"로 처리하면 **안 된다.** 겹침이
# 심하면 두 치환기 사이에 가짜 결합이 생겨 공통 이웃이 만들어지고, 바로 그 예외로
# 진짜 결함이 숨는다(saIm100 의 O-O 0.924 가 그렇게 숨었다).
BOND_FLOOR_FRAC = 0.95
CUT = 2.60                # 후보를 모으는 상한. 실제 판정은 BOND_FLOOR_FRAC 로 한다


def forbidden(s1, s2):
    if s1 in HALO and s2 in HALO:
        return True
    if (s1 in HALO and s2 in ('O', 'N', 'S')) or (s2 in HALO and s1 in ('O', 'N', 'S')):
        return True
    if s1 == 'O' and s2 == 'O':
        return True
    return False


def check(path):
    a = read(path)
    sym = np.array(a.get_chemical_symbols())
    n_zn = int((sym == 'Zn').sum())

    # (A) 성분 수. Zn 을 빼고 세면 링커만 남는다.
    nl = NeighborList(natural_cutoffs(a, mult=BOND_MULT), skin=0.0,
                      self_interaction=False, bothways=True)
    nl.update(a)
    G = nx.Graph()
    G.add_nodes_from(range(len(a)))
    for k in range(len(a)):
        for m in nl.get_neighbors(k)[0]:
            if sym[k] != 'Zn' and sym[int(m)] != 'Zn':
                G.add_edge(k, int(m))
    comps = [len(c) for c in nx.connected_components(G)]
    # Zn 하나당 링커 2개(링커가 Zn 둘을 잇고 Zn 은 링커 넷을 갖는다) + Zn 자신
    expected = n_zn * 3
    fused = expected - len(comps)

    # (B) 금지 접촉
    i, j, d = neighbor_list('ijd', a, CUT)
    bad = []
    for x, y, dd in zip(i, j, d):
        if x >= y or not forbidden(sym[x], sym[y]):
            continue
        floor = BOND_FLOOR_FRAC * (covalent_radii[atomic_numbers[sym[x]]]
                                   + covalent_radii[atomic_numbers[sym[y]]])
        if dd < floor:
            bad.append((round(float(dd), 3), f'{sym[x]}-{sym[y]}'))
    bad.sort()

    return {'name': os.path.basename(path), 'n_atoms': len(a), 'n_zn': n_zn,
            'n_components': len(comps), 'expected': expected, 'fused': fused,
            'forbidden_contacts': len(bad), 'worst': bad[0] if bad else None,
            'pass': fused == 0 and not bad}


def main():
    pats = sys.argv[1:] or [os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                         'structures', 'ZIF69_*.cif')]
    files = sorted(f for p in pats for f in glob.glob(p))
    if not files:
        print('대상 없음')
        return 1
    print(f'{"구조":<24} {"원자":>6} {"성분":>6} {"기대":>6} {"융합":>6} '
          f'{"금지접촉":>9} {"최악":>16}  판정')
    print('-' * 92)
    n_bad = 0
    for f in files:
        r = check(f)
        n_bad += 0 if r['pass'] else 1
        w = f"{r['worst'][1]} {r['worst'][0]}" if r['worst'] else '-'
        print(f'{r["name"][:24]:<24} {r["n_atoms"]:>6} {r["n_components"]:>6} '
              f'{r["expected"]:>6} {r["fused"]:>6} {r["forbidden_contacts"]:>9} '
              f'{w:>16}  {"통과" if r["pass"] else "*** 탈락"}')
    print('-' * 92)
    print(f'{len(files)}개 중 {n_bad}개 탈락')
    print('\n주: 성분 수가 기대보다 적으면 링커끼리 붙은 것입니다. 거리 검사로는 '
          '안 잡힙니다 —\n    겹침이 심할수록 두 치환기가 "결합"으로 인식되어 '
          '충돌 검사의 1,3 예외에 숨습니다.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
