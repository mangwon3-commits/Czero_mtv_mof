"""Q_st 향상 전략 A(결함 공학)와 B(push-pull MTV) 구조를 생성한다.

전략 A -- 결함 공학 (Open Metal Site 노출)
    닫힌 상 ZIF-8에서 링커 하나를 통째로 제거하면 그 자리에 배위하던 Zn 두 개가
    각각 배위수 4 -> 3이 되어 열린 금속 자리(OMS)가 드러난다. OMS는 CO2 산소의
    비공유전자쌍과 직접 배위할 수 있어 물리흡착 한계(~20 kJ/mol)를 넘는 결합을 준다.

    [전하 균형 주의] 이미다졸레이트는 -1 음이온이다. 중성 링커를 그냥 빼면 골격에
    +1 잔여 전하가 생긴다. 실제 결함 ZIF-8은 빠진 자리를 OH-/HCOO- 등이 채우거나
    양성자화로 보상한다. 여기서는 가장 단순한 보상으로 링커 자리에 OH- 하나를
    한쪽 Zn에 배위시켜 전하를 맞춘다(다른 Zn은 3배위 OMS로 남는다).

전략 B -- push-pull MTV
    같은 기공을 향해 -NO2(강한 전자끌개, 양전하 중심)와 -NH2(루이스 염기/수소결합
    주개, 음전하 중심)를 인접 링커에 배치한다. 두 극성이 만드는 국소 전기장 기울기가
    CO2 사극자와 더 강하게 상호작용하는지(단독 관능화 대비 시너지) 본다.

    핵심은 '인접'이다. 무작위 배치는 두 관능기가 서로 먼 기공에 흩어져 시너지가
    나오지 않는다. 여기서는 각 6원자 창구(6MR)를 이루는 링커들에 NO2/NH2를
    번갈아 배치해 같은 창구를 공유하게 만든다.
"""
import json
import os
import sys

import numpy as np
import networkx as nx
from ase import Atoms
from ase.io import read, write
from ase.neighborlist import NeighborList, natural_cutoffs

HERE = os.path.dirname(os.path.abspath(__file__))
LIB = os.path.join(HERE, '..', '05_MTV_Ligand_Library')
sys.path.insert(0, LIB)

BASE = os.path.join(LIB, 'ZIF8_mIm_only_P1.cif')
SITEMAP = os.path.join(LIB, 'site_map.json')


def graph_of(atoms):
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


# ---------------------------------------------------------------- 전략 A
def build_defect(out_cif):
    atoms = read(BASE)
    syms = atoms.get_chemical_symbols()
    G = graph_of(atoms)
    sites = json.load(open(SITEMAP))

    # 첫 번째 링커를 통째로 제거 대상으로 삼는다
    site = sites[0]
    ring = site['ring']
    linker = set(ring) | set(site['substituent'])
    # 고리에 붙은 수소까지 포함
    for i in list(linker):
        for j in G.neighbors(i):
            if syms[j] == 'H':
                linker.add(j)

    n1, n3 = [i for i in ring if syms[i] == 'N']
    zn1 = next((j for j in G.neighbors(n1) if syms[j] == 'Zn'), None)
    zn2 = next((j for j in G.neighbors(n3) if syms[j] == 'Zn'), None)
    if zn1 is None or zn2 is None:
        raise RuntimeError('링커에 배위한 Zn을 찾지 못함')

    pos = atoms.get_positions()
    cell = np.array(atoms.get_cell())

    def mic(v):
        f = np.linalg.solve(cell.T, v)
        f -= np.round(f)
        return cell.T @ f

    # 전하 보상: zn1 쪽에 OH- 를 붙인다 (빠진 N 방향으로)
    d = mic(pos[n1] - pos[zn1])
    d /= np.linalg.norm(d)
    p_o = pos[zn1] + d * 1.95           # Zn-O 결합길이
    p_h = p_o + d * 0.97                # O-H

    keep = [i for i in range(len(atoms)) if i not in linker]
    new = atoms[keep]
    new += Atoms('OH', positions=[p_o, p_h])

    write(out_cif, new)
    _legacy_tags(out_cif)

    removed = len(linker)
    print(f'[전략 A] 링커 1개({removed}원자) 제거 + OH- 보상')
    print(f'         Zn {zn1}: OH 배위 (4배위 유지) / Zn {zn2}: 3배위 OMS 노출')
    print(f'         원자수 {len(atoms)} -> {len(new)}')
    return out_cif


# ---------------------------------------------------------------- 전략 B
def build_push_pull(out_cif, seed=0):
    """NO2와 NH2를 같은 창구를 공유하도록 번갈아 배치."""
    import mtv_cif_builder as mcb

    atoms = read(BASE)
    G = graph_of(atoms)
    sites = json.load(open(SITEMAP))

    # 링커 간 인접성: 같은 Zn을 공유하면 인접으로 본다
    syms = atoms.get_chemical_symbols()
    zn_of = []
    for s in sites:
        ns = [i for i in s['ring'] if syms[i] == 'N']
        zns = set()
        for n in ns:
            for j in G.neighbors(n):
                if syms[j] == 'Zn':
                    zns.add(j)
        zn_of.append(zns)

    adj = nx.Graph()
    adj.add_nodes_from(range(len(sites)))
    for i in range(len(sites)):
        for j in range(i + 1, len(sites)):
            if zn_of[i] & zn_of[j]:
                adj.add_edge(i, j)

    # 2색 그리디 채색 -> 인접 링커가 서로 다른 관능기를 갖게 한다
    color = nx.greedy_color(adj, strategy='largest_first')
    assign = ['nIm' if color[i] % 2 == 0 else 'amIm' for i in range(len(sites))]
    n_no2 = assign.count('nIm')
    n_nh2 = assign.count('amIm')

    frags = {n: mcb.build_fragment(n) for n in set(assign)}
    remove, new_sym, new_pos = set(), [], []
    avoid = atoms.get_positions().copy()
    for site, lig in zip(sites, assign):
        subst, newat = mcb.plan_substitution(atoms, site, frags[lig],
                                             avoid_positions=avoid)
        remove.update(subst)
        for s_, p_ in newat:
            new_sym.append(s_)
            new_pos.append(p_)
            avoid = np.vstack([avoid, p_])

    mask = np.ones(len(atoms), dtype=bool)
    mask[sorted(remove)] = False
    out = atoms[mask]
    if new_sym:
        out += Atoms(symbols=new_sym, positions=new_pos)

    write(out_cif, out)
    _legacy_tags(out_cif)

    d = out.get_all_distances(mic=True)
    np.fill_diagonal(d, np.inf)
    print(f'[전략 B] push-pull 배치: NO2 {n_no2}개 / NH2 {n_nh2}개 (인접 교대)')
    print(f'         인접 그래프 간선 {adj.number_of_edges()}개, '
          f'최소 원자간 거리 {d.min():.3f} Å')
    return out_cif


def _legacy_tags(path):
    t = open(path, encoding='utf-8').read()
    for o, n in (('_space_group_name_H-M_alt', '_symmetry_space_group_name_H-M'),
                 ('_space_group_IT_number', '_symmetry_Int_Tables_number'),
                 ('_space_group_symop_operation_xyz', '_symmetry_equiv_pos_as_xyz')):
        t = t.replace(o, n)
    open(path, 'w', encoding='utf-8').write(t)


if __name__ == '__main__':
    os.makedirs(os.path.join(HERE, 'structures'), exist_ok=True)
    build_defect(os.path.join(HERE, 'structures', 'StratA_defect_OMS.cif'))
    print()
    build_push_pull(os.path.join(HERE, 'structures', 'StratB_pushpull_NO2_NH2.cif'))
