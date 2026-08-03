"""스윙 각도를 반응좌표로 고정한 구속 스캔으로 골격 변형에너지 U(phi)를 얻는다.

왜 필요한가:
    자유 최소화는 열린 구조(phi=24.6도)를 닫힌 쪽(phi=0.7도)으로 되돌려버려
    두 상의 에너지 차를 '두 최소점의 차'로 구할 수 없다. 반응좌표를 고정하면
    이 붕괴를 막고 U(phi) 곡선 전체를 얻을 수 있다.

방법:
    1. 힘장 최소화된 닫힌 구조에서 출발한다.
       (실험 좌표에서 출발하면 힘장이 실험을 재현 못 하는 오차 ~8000 kcal/mol이
        신호 ~1200 kcal/mol을 압도한다. 자체 최소점에서 출발하면 이 오차가 상쇄된다.)
    2. 각 이미다졸레이트를 자기 N-N 축 둘레로 delta_phi 만큼 강체 회전시킨다.
       (N과 Zn은 고정 -- 배위 골격은 그대로 두고 링만 돌린다)
    3. 각 phi에서 LAMMPS 단일점 에너지를 계산한다.

    강체 회전이라 링 내부 결합길이/각도는 보존되고, 변하는 것은 링 배향과
    그에 따른 비결합 상호작용 및 Zn-N-C 각도뿐이다 -- 즉 게이트 오프닝의 물리.
"""
import os
import re
import subprocess
import sys

import numpy as np
import networkx as nx
from ase.io import read
from ase.neighborlist import NeighborList, natural_cutoffs

HERE = os.path.dirname(os.path.abspath(__file__))
METALS = ('Zn', 'Co')


def build_graph(atoms):
    nl = NeighborList(natural_cutoffs(atoms, mult=1.15), skin=0.0,
                      self_interaction=False, bothways=True)
    nl.update(atoms)
    G = nx.Graph()
    G.add_nodes_from(range(len(atoms)))
    for i in range(len(atoms)):
        nb, _ = nl.get_neighbors(i)
        for j in nb:
            G.add_edge(i, int(j))
    return G


def find_linkers(atoms, G):
    """각 링커에 대해 (N1, N2, C2, 회전대상 원자목록)을 반환.

    C2를 함께 돌려주는 이유: 회전 방향(부호)을 링커마다 결정해야 하기 때문이다.
    N1->N2 축의 방향은 cycle_basis가 고리 원자를 반환하는 순서에 따라 임의로
    정해지므로, 모든 링커를 '+phi'로 돌리면 절반이 반대 방향으로 회전해
    이웃 링커와 충돌하고 에너지가 발산한다(실측: 30도에서 2e9 kcal/mol).
    각 링커에서 실제 스윙 각도를 재고 목표에 가까워지는 부호를 골라야 한다.
    """
    syms = atoms.get_chemical_symbols()
    heavy = [i for i in G.nodes if syms[i] in ('C', 'N')]
    rings = [c for c in nx.cycle_basis(G.subgraph(heavy)) if len(c) == 5]
    linkers = []
    for ring in rings:
        ns = [i for i in ring if syms[i] == 'N']
        if len(ns) != 2:
            continue
        n1, n2 = ns
        c2 = next((i for i in ring if syms[i] == 'C'
                   and G.has_edge(i, n1) and G.has_edge(i, n2)), None)
        if c2 is None:
            continue
        # 두 질소를 제외한 링커 전체(고리탄소 + 치환기 + 수소)가 회전 대상
        rot = set()
        frontier = [i for i in ring if i not in (n1, n2)]
        while frontier:
            cur = frontier.pop()
            if cur in rot or cur in (n1, n2):
                continue
            if syms[cur] in METALS:
                continue
            rot.add(cur)
            frontier.extend(j for j in G.neighbors(cur)
                            if j not in rot and j not in (n1, n2)
                            and syms[j] not in METALS)
        m1 = next((j for j in G.neighbors(n1) if syms[j] in METALS), None)
        m2 = next((j for j in G.neighbors(n2) if syms[j] in METALS), None)
        if m1 is None or m2 is None:
            continue
        linkers.append({'n1': n1, 'n2': n2, 'c2': c2, 'm1': m1, 'm2': m2,
                        'rot': sorted(rot)})
    return linkers


def swing_of(pos, cell, lk):
    """measure_swing.py와 동일한 정의로 이 링커의 스윙 각도를 계산."""
    def mic(v):
        f = np.linalg.solve(cell.T, v)
        f -= np.round(f)
        return cell.T @ f

    p1 = pos[lk['n1']]
    p2 = p1 + mic(pos[lk['n2']] - p1)
    pc = p1 + mic(pos[lk['c2']] - p1)
    pm1 = p1 + mic(pos[lk['m1']] - p1)
    pm2 = p1 + mic(pos[lk['m2']] - p1)
    axis = (p2 - p1) / np.linalg.norm(p2 - p1)
    mid_n, mid_m = 0.5 * (p1 + p2), 0.5 * (pm1 + pm2)

    def perp(v):
        v = v - np.dot(v, axis) * axis
        n = np.linalg.norm(v)
        return v / n if n > 1e-8 else None

    r, z = perp(pc - mid_n), perp(mid_m - mid_n)
    if r is None or z is None:
        return None
    return np.degrees(np.arccos(np.clip(np.dot(r, z), -1, 1)))


def rotate_about(points, origin, axis, theta):
    axis = axis / np.linalg.norm(axis)
    K = np.array([[0, -axis[2], axis[1]],
                  [axis[2], 0, -axis[0]],
                  [-axis[1], axis[0], 0]])
    Rm = np.eye(3) + np.sin(theta) * K + (1 - np.cos(theta)) * (K @ K)
    return (Rm @ (points - origin).T).T + origin


def make_rotated(atoms, linkers, target_phi):
    """각 링커를 스윙 각도가 target_phi가 되도록 회전시킨다.

    회전 부호는 링커마다 +/- 를 모두 시험해 목표에 가까워지는 쪽을 택한다
    (N1->N2 축 방향이 임의로 정해지므로 전역 부호를 쓸 수 없다).
    """
    a = atoms.copy()
    pos = a.get_positions()
    cell = np.array(a.get_cell())

    def mic(v):
        f = np.linalg.solve(cell.T, v)
        f -= np.round(f)
        return cell.T @ f

    newpos = pos.copy()
    for lk in linkers:
        cur = swing_of(pos, cell, lk)
        if cur is None:
            continue
        delta = target_phi - cur
        n1, n2, rot = lk['n1'], lk['n2'], lk['rot']
        p1 = pos[n1]
        p2 = p1 + mic(pos[n2] - p1)
        axis = p2 - p1
        origin = 0.5 * (p1 + p2)
        pts = np.array([p1 + mic(pos[i] - p1) for i in rot])

        best = None
        for sign in (+1.0, -1.0):
            trial = rotate_about(pts, origin, axis, np.radians(sign * delta))
            tmp = newpos.copy()
            for idx, i in enumerate(rot):
                tmp[i] = trial[idx]
            got = swing_of(tmp, cell, lk)
            if got is None:
                continue
            err = abs(got - target_phi)
            if best is None or err < best[0]:
                best = (err, trial)
        if best is None:
            continue
        for idx, i in enumerate(rot):
            newpos[i] = best[1][idx]
    a.set_positions(newpos)
    return a


def write_data_with_coords(template, atoms, out):
    """LAMMPS data 파일의 Atoms 좌표만 교체 (토폴로지/전하 보존)."""
    lines = open(template).read().split('\n')
    i0 = next(i for i, l in enumerate(lines) if l.strip().startswith('Atoms'))
    pos = atoms.get_positions()
    k = 0
    i = i0 + 1
    while i < len(lines) and k < len(pos):
        s = lines[i].split()
        if len(s) >= 7:
            # id mol type q x y z ...
            s[4], s[5], s[6] = (f'{pos[k][0]:.6f}', f'{pos[k][1]:.6f}',
                                f'{pos[k][2]:.6f}')
            lines[i] = ' '.join(s)
            k += 1
        elif s and not s[0].isdigit() and k > 0:
            break
        i += 1
    open(out, 'w').write('\n'.join(lines))
    return k


SINGLE_POINT = """units           real
atom_style      full
boundary        p p p
pair_style      lj/cut/coul/long 12.500
bond_style      harmonic
angle_style     hybrid cosine/periodic fourier
dihedral_style  harmonic
improper_style  fourier
kspace_style    ewald 0.000001
special_bonds   lj/coul 0.0 0.0 1.0
pair_modify     tail yes mix arithmetic
read_data       {data}
include         {coeffs}
run             0
print           "SCAN_ENERGY $(pe)"
"""


def main():
    base_cif = os.path.join(HERE, 'min_closed.cif')
    # [주의] min_closed.data는 nocoeff로 저장돼 Pair/Bond/Angle Coeffs가 없다.
    # 계수를 가진 원본 data.ZIF8_closed를 템플릿으로 쓰고 좌표만 갈아끼운다.
    template = os.path.join(HERE, 'data.ZIF8_closed')
    if not (os.path.exists(base_cif) and os.path.exists(template)):
        print('min_closed.cif / data.ZIF8_closed 가 필요합니다.')
        return 1

    atoms = read(base_cif)
    G = build_graph(atoms)
    linkers = find_linkers(atoms, G)
    print(f'인식된 링커: {len(linkers)}개 (2x2x2 슈퍼셀 기준 192개 기대)')
    syms = atoms.get_chemical_symbols()
    # 스윙 각도는 (고리 원자 ↔ 금속) 상대 배치로 정의되므로 그 둘을 고정해야
    # 반응좌표가 보존된다. 나머지(치환기, 수소)만 이완시켜 충돌을 푼다.
    frozen = {lk[k] for lk in linkers for k in ('n1', 'n2', 'c2', 'm1', 'm2')}
    for lk in linkers:
        for i in lk['rot']:
            if syms[i] == 'C' and any(G.has_edge(i, lk[k]) for k in ('n1', 'n2')):
                frozen.add(i)
    print(f'고정 원자: {len(frozen)}개 / 전체 {len(atoms)}개 '
          f'(나머지 {len(atoms) - len(frozen)}개 이완)\n')

    # 계수(coeff) 부분은 원본 data 파일에 있으므로 별도 include 불필요 ->
    # lammps-interface가 만든 in.* 의 스타일 정의를 그대로 재사용한다.
    scan_dir = os.path.join(HERE, 'scan')
    os.makedirs(scan_dir, exist_ok=True)

    angles = list(range(0, 31, 3))
    results = []
    for phi in angles:
        rot_atoms = make_rotated(atoms, linkers, phi)
        d = os.path.join(scan_dir, f'phi{phi:02d}.data')
        n = write_data_with_coords(template, rot_atoms, d)
        inp = os.path.join(scan_dir, f'in.phi{phi:02d}')
        # [주의] 이 골격(RASPA 예제 ZIF-8)은 CIF에 부분전하가 0으로 기록돼 있어
        # Ewald가 'uncharged system'으로 실패한다. 순수 mIm ZIF-8은 중성 골격이고
        # 스윙 장벽은 메틸기와 이웃 링커 사이의 입체/반데르발스가 지배하므로
        # 정전기 항 없이 lj/cut으로 계산한다. (치환체로 확장할 때는 EQeq 전하를
        # 넣고 coul/long + kspace로 되돌려야 한다 -- 그때는 정전기가 유의미하다)
        # 반응좌표를 고정한 채 나머지를 이완시킨다.
        # 스윙 각도는 고리 원자와 금속의 상대 배치로 정의되므로 그 둘을 얼리고
        # (fix setforce 0), 충돌이 가장 심한 치환기/수소만 이완시킨다.
        # 이렇게 하면 각도가 보존되면서도 강체 회전보다 훨씬 조인 상한을 준다.
        frozen_ids = ' '.join(str(i + 1) for i in sorted(frozen))
        open(inp, 'w').write(f"""units           real
atom_style      full
boundary        p p p
pair_style      lj/cut 12.500
bond_style      harmonic
angle_style     hybrid cosine/periodic fourier
dihedral_style  harmonic
improper_style  fourier
special_bonds   lj/coul 0.0 0.0 1.0
pair_modify     tail yes mix arithmetic
read_data       {os.path.basename(d)}
run             0
print           "RIGID_ENERGY $(pe)"
group           frozen id {frozen_ids}
fix             hold frozen setforce 0.0 0.0 0.0
min_style       cg
minimize        1.0e-10 1.0e-10 5000 50000
print           "RELAXED_ENERGY $(pe)"
write_data      relaxed_phi{phi:02d}.data nocoeff
""")
        r = subprocess.run(['lmp_serial', '-in', os.path.basename(inp)],
                           cwd=scan_dir, capture_output=True, text=True, timeout=1800)
        mr = re.search(r'RIGID_ENERGY\s+(-?[0-9.eE+]+)', r.stdout)
        mx = re.search(r'RELAXED_ENERGY\s+(-?[0-9.eE+]+)', r.stdout)
        e_rigid = float(mr.group(1)) if mr else None
        e = float(mx.group(1)) if mx else e_rigid
        # 회전이 실제로 목표 각도를 만들었는지, 충돌은 없는지 진단
        cellm = np.array(rot_atoms.get_cell())
        got = np.array([x for x in (swing_of(rot_atoms.get_positions(), cellm, lk)
                                    for lk in linkers) if x is not None])
        dm = rot_atoms.get_all_distances(mic=True)
        np.fill_diagonal(dm, np.inf)
        results.append((phi, e, e_rigid))
        print(f'  phi={phi:>2}도 실제{got.mean():5.2f}도 | 최소거리 {dm.min():.3f} Å | '
              f'강체 U={e_rigid if e_rigid else float("nan"):>10.1f} -> '
              f'이완 U={e if e else float("nan"):>10.1f} kcal/mol')

    ok = [(p, e, er) for p, e, er in results if e is not None]
    if not ok:
        print('\n에너지 추출 실패')
        return 1
    e0, er0 = ok[0][1], ok[0][2]
    ncell = 8      # 2x2x2 슈퍼셀
    nlink = 24     # 단위셀당 링커 수
    print(f'\n{"phi(도)":>8} {"강체 dU":>14} {"구속이완 dU":>14} {"링커당":>12}')
    print(f'{"":8} {"(kJ/mol/셀)":>14} {"(kJ/mol/셀)":>14} {"(kJ/mol)":>12}')
    print('-' * 54)
    for p, e, er in ok:
        du = (e - e0) * 4.184 / ncell
        dur = (er - er0) * 4.184 / ncell if er is not None else float('nan')
        print(f'{p:>8} {dur:>14.1f} {du:>14.1f} {du / nlink:>12.2f}')

    import json
    with open(os.path.join(HERE, 'swing_scan.json'), 'w', encoding='utf-8') as f:
        json.dump([{'phi_deg': p, 'U_relaxed_kcal': e, 'U_rigid_kcal': er,
                    'dU_relaxed_kJ_per_cell': (e - e0) * 4.184 / ncell,
                    'dU_rigid_kJ_per_cell': ((er - er0) * 4.184 / ncell
                                             if er is not None else None)}
                   for p, e, er in ok], f, indent=2)
    print(f'\n[OK] 저장: swing_scan.json')
    return 0


if __name__ == '__main__':
    sys.exit(main())
