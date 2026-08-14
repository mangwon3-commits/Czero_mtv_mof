"""ZIF-67 결정 구조 정리 -- 기공 손님 제거와 메틸 수소 무질서 해소.

[무엇이 문제였나]
    01_CIF_Cleaned/ZIF_67.cif 를 ASE 로 읽으면 490원자가 나옵니다.
    ZIF-67 = Co(mIm)2 는 ZIF-8 과 등구조이므로 **276원자**여야 합니다.

        ZIF-8   C 96  H 120  N 48   Zn 12   = 276
        읽힌 것 C 96  H 192  N 190  Co 12   = 490

    C 와 금속은 맞고 H 와 N 만 넘칩니다. 원인 둘:

    1. **기공 손님.** CIF 에 N2~N9 여덟 자리가 점유율 0.25~1 로 들어 있습니다.
       골격 질소(N1)는 Co 에 배위하지만 이들은 어디에도 결합하지 않고 기공
       한가운데(0.5,0.5,0 / 0.781,0.219,0.061 등)에 떠 있습니다. 무질서하게
       모형화된 흡착 손님입니다. 서로 0.685~1.575 A 로 겹쳐 있는데, 이는
       **동시에 존재할 수 없는 대체 위치**라는 뜻입니다.

    2. **메틸 수소 무질서.** H3A/B/C 가 점유율 0.5 이고 메틸 탄소 C3 가
       거울면 위(site symmetry order 2)에 있어, 대칭 전개하면 메틸 하나에
       수소가 **6개**(진짜 3개의 두 배향) 생깁니다.

[왜 조용히 지나가나 -- 오늘 세 번째로 만나는 구조]
    **ASE 는 CIF 를 읽을 때 점유율을 무시하고 전부 실재 원자로 만듭니다.**
    경고도 없습니다. 그대로 GCMC 에 넣으면 기공이 막히고 골격 질량이 틀리고
    void fraction 이 틀립니다. 게다가 파일 이름이 01_CIF_**Cleaned** 라
    이미 정리된 것처럼 보입니다 -- 실제로는 01_CIF_Data 원본과 같은 파일입니다.

[어떻게 고르나 -- 라벨이 아니라 결합으로]
    "N2~N9 를 지운다" 로 짜면 다른 구조에서 곧바로 깨집니다. 대신
    **Co 를 포함한 연결 성분만 남깁니다.** 골격은 하나로 이어져 있고 손님은
    떠 있으므로 기하가 스스로 갈라 줍니다.
"""
import collections
import itertools
import sys

import numpy as np
from ase.io import read, write
from ase.neighborlist import neighbor_list

COV = {'H': 0.31, 'C': 0.76, 'N': 0.71, 'O': 0.66, 'Co': 1.26, 'Zn': 1.22,
       'S': 1.05, 'Cl': 1.02, 'F': 0.57, 'Br': 1.20}

# 사면체 H-C-H 각. 이상적 메틸 H...H = 2 * d(C-H) * sin(TETRA/2).
# d(C-H)=1.083 이면 1.769 A 이고, 실측이 정확히 그 값입니다.
#
# **문턱값(">= 1.4 이면 통과") 방식으로 짜면 안 됩니다.** 실제로 그렇게 짰다가
# 틀렸습니다 -- 서로 다른 배향의 수소쌍 중에 2.042 A 인 것이 있어서 문턱을
# 통과해 버리고, 그 뒤로 아무것도 못 고르게 됩니다(메틸당 3개가 아니라 2개).
# 거리의 **하한**이 아니라 **이상값과의 일치**로 골라야 합니다.
TETRA = np.radians(109.4712)


def bond_graph(atoms, scale=1.25):
    syms = sorted(set(atoms.get_chemical_symbols()))
    cut = {(a, b): scale * (COV[a] + COV[b]) for a in syms for b in syms}
    i, j = neighbor_list('ij', atoms, cut)
    g = collections.defaultdict(set)
    for a, b in zip(i, j):
        g[int(a)].add(int(b))
        g[int(b)].add(int(a))
    return g


def main(src, dst):
    atoms = read(src)
    print(f'  읽음        {len(atoms)} 원자  '
          f'{dict(sorted(collections.Counter(atoms.get_chemical_symbols()).items()))}')

    # --- 1. Co 를 포함한 연결 성분만 남긴다 -------------------------------
    g = bond_graph(atoms)
    sym = atoms.get_chemical_symbols()
    metals = [k for k, s in enumerate(sym) if s in ('Co', 'Zn')]
    seen, stack = set(), list(metals)
    while stack:
        k = stack.pop()
        if k in seen:
            continue
        seen.add(k)
        stack.extend(g[k] - seen)
    dropped = len(atoms) - len(seen)
    guest = collections.Counter(sym[k] for k in range(len(atoms)) if k not in seen)
    print(f'  손님 제거   {dropped} 원자  {dict(sorted(guest.items()))}')
    atoms = atoms[sorted(seen)]

    # --- 2. 메틸 수소 무질서 해소 ----------------------------------------
    g = bond_graph(atoms)
    sym = atoms.get_chemical_symbols()
    pos = atoms.get_positions()
    cell = atoms.get_cell()
    def mic(u, v):
        """최소 이미지 거리. 셀 경계를 걸친 메틸에서 이걸 안 쓰면 틀린다."""
        d = pos[u] - pos[v]
        f = np.linalg.solve(cell.T, d)
        return float(np.linalg.norm(cell.T @ (f - np.round(f))))

    drop = set()
    fixed = 0
    worst = 0.0
    for k, s in enumerate(sym):
        if s != 'C':
            continue
        hs = sorted(n for n in g[k] if sym[n] == 'H')
        if len(hs) <= 3:
            continue
        fixed += 1
        # 이 탄소의 실제 C-H 길이에서 이상적 H...H 를 유도한다.
        ch = np.mean([mic(h, k) for h in hs])
        ideal = 2.0 * ch * np.sin(TETRA / 2.0)
        # 세 쌍 모두가 ideal 에 가장 가까운 조합을 고른다.
        best, best_err = None, None
        for combo in itertools.combinations(hs, 3):
            err = max(abs(mic(u, v) - ideal)
                      for u, v in itertools.combinations(combo, 2))
            if best_err is None or err < best_err:
                best, best_err = combo, err
        worst = max(worst, best_err)
        drop |= set(hs) - set(best)
    print(f'  메틸 정리   탄소 {fixed}개에서 수소 {len(drop)}개 제거 '
          f'(이상 H...H 와의 최대 편차 {worst:.3f} A)')
    atoms = atoms[[k for k in range(len(atoms)) if k not in drop]]

    c = collections.Counter(atoms.get_chemical_symbols())
    print(f'  결과        {len(atoms)} 원자  {dict(sorted(c.items()))}')

    # --- 3. 검증 ----------------------------------------------------------
    m = c.get('Co', 0) or c.get('Zn', 0)
    want = {'C': 8 * m, 'H': 10 * m, 'N': 4 * m}      # M(mIm)2 : M C8 H10 N4
    bad = [(e, c.get(e, 0), v) for e, v in want.items() if c.get(e, 0) != v]
    if bad:
        print('  !! 조성 불일치 (M(mIm)2 기준):')
        for e, got, exp in bad:
            print(f'       {e}  실제 {got}  기대 {exp}')
        return 1
    print(f'  검증        M(mIm)2 화학량론 일치 (M={m})')

    d = neighbor_list('d', atoms, 1.3)
    print(f'  최소 원자간 거리 {d.min():.3f} A  (0.7 미만이면 파손)')

    write(dst, atoms)
    print(f'  기록        {dst}')
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1], sys.argv[2]))
