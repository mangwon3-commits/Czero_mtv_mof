"""ZIF-67 치환 계열 검증 -- 개수와 기하를 둘 다 센다.

[왜 개수를 세는가]
    AUDIT_20260814.md 3절: v1 ZIF-69 계열에서 이름이 050 인 구조가 실제로는
    14/24(58.3%), 075 는 17/24(70.8%) 였습니다. 충돌 회피 자리 선택 코드가
    **개수까지 말없이 조정**한 것이고, 그래도 계산은 끝까지 완주했습니다.
    그 코드 경로는 지금도 무장돼 있으므로 새 계열마다 세야 합니다.

[무엇으로 세는가 -- 원소 수지]
    mIm 의 C2 치환기는 -CH3 입니다. 이것을 갈아 끼우면 원소 수가 정해진 만큼
    움직입니다. 자리 지도나 메타데이터를 믿지 않고 **CIF 의 원자를 직접** 셉니다.

        cnIm  -CH3 -> -C#N   :  C 그대로, H -3n, N +n
        nIm   -CH3 -> -NO2   :  C -n,     H -3n, N +n, O +2n

    (기준: 모체 Co 12 / C 96 / H 120 / N 48)
"""
import collections
import glob
import os
import re
import sys

from ase.io import read
from ase.neighborlist import neighbor_list

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = {'Co': 12, 'C': 96, 'H': 120, 'N': 48, 'O': 0}
# 치환 하나당 원소 증감
DELTA = {
    'cnIm': {'C': 0, 'H': -3, 'N': +1, 'O': 0},
    'nIm':  {'C': -1, 'H': -3, 'N': +1, 'O': +2},
}
COV = {'H': 0.31, 'C': 0.76, 'N': 0.71, 'O': 0.66, 'Co': 1.26}


def main():
    files = sorted(glob.glob(os.path.join(HERE, 'structures', 'ZIF67_*.cif')))
    if not files:
        print('구조가 없습니다')
        return 1
    print(f'  {"구조":<16} {"이름상":>6} {"실제":>5} {"판정":>6}  '
          f'{"최소거리":>8}  원소 수지')
    bad = 0
    for f in files:
        name = os.path.basename(f).replace('.cif', '')
        m = re.match(r'ZIF67_([A-Za-z0-9]+?)(\d{3})$', name)
        if not m:
            continue
        fam, pct = m.group(1), int(m.group(2))
        n_want = round(24 * pct / 100)
        atoms = read(f)
        c = collections.Counter(atoms.get_chemical_symbols())

        # n 을 원소별로 각각 풀어 본다. 전부 같은 값이 나와야 한다.
        d = DELTA[fam]
        got = {}
        for el, per in d.items():
            if per == 0:
                continue
            got[el] = (c.get(el, 0) - BASE[el]) / per
        vals = sorted(set(got.values()))
        n_real = int(vals[0]) if len(vals) == 1 and vals[0] == int(vals[0]) else None

        dmin = float(neighbor_list('d', atoms, 1.3).min())
        ok = (n_real == n_want)
        if not ok:
            bad += 1
        detail = ' '.join(f'{el}={c.get(el,0)}' for el in ('C', 'H', 'N', 'O')
                          if c.get(el, 0) or el in d)
        nr = n_real if n_real is not None else f'불일치{got}'
        print(f'  {name:<16} {n_want:>6} {str(nr):>5} '
              f'{"OK" if ok else "<<<불일치":>6}  {dmin:>8.3f}  {detail}')
    print(f'\n  개수 불일치 {bad} / {len(files)}')
    return 0 if bad == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
