"""'둥지 효과(Nest Effect)' 검증 구조 생성 -- 팀 문헌조사 반영.

팀 보고서(김경은 7차, 유서진 7/28)의 핵심 지적:
    비대칭 미세환경은 EWG + EDG 만으로 만들어지는 게 아니다. 극성기(EWG/EDG)가
    1차 포집점을 만들고, **비극성기(-CH3, 방향족)가 '둥지의 벽'** 역할을 하며
    N2/CH4 같은 무극성 기체를 배제하는 2차 접촉점을 형성한다. 두 종류가 인접
    교대 배치될 때 CO2 한 분자가 여러 방향에서 동시에 잡힌다.

    정량 근거로 제시된 사례: 이미다졸(극성)과 메틸(비극성)이 같은 좁은 채널에
    공존하는 카이랄 Zn-MOF에서 CO2 Qst 43.7 kJ/mol, CH4는 16.4 kJ/mol,
    CO2/N2 선택도 최대 867 (Lv et al., Chem. Commun. 2014, 50, 6886).

우리 기존 Strategy B의 문제:
    NO2 12개 + NH2 12개로 **치환율 100%** -- 메틸이 하나도 남아있지 않다.
    문헌대로라면 '둥지의 벽'이 없는 셈이고, 이게 Qst가 23.01에서 멈춘 한 원인일 수
    있다. 여기서는 메틸을 남긴 3원 조성을 만들어 직접 비교한다.

추가 반영:
    같은 보고서가 인용한 고처리량 스크리닝(Li, Chung, Simon, Snurr, JPCL 2017)은
    모구조 기공이 이미 6 A 이하면 관능기 추가가 오히려 CO2 흡착을 '감소'시키는
    과충전(over-functionalization)을 보고했다. ZIF-8 창구는 3.4 A로 그 영역에
    있으므로, 치환율이 낮은 조성도 반드시 함께 시험한다.
"""
import json
import os
import sys

import numpy as np
import networkx as nx
from ase.io import read
from ase.neighborlist import NeighborList, natural_cutoffs

HERE = os.path.dirname(os.path.abspath(__file__))
LIB = os.path.join(HERE, '..', '05_MTV_Ligand_Library')
sys.path.insert(0, LIB)

BASE = os.path.join(LIB, 'ZIF8_mIm_only_P1.cif')
SITEMAP = os.path.join(LIB, 'site_map.json')
OUT = os.path.join(HERE, 'structures')

# 극성/비극성 분류 -- 둥지 배치에 쓴다
POLAR = {'nIm', 'clIm', 'cnIm', 'amIm', 'amrIm', 'saIm', 'tfIm'}
NONPOLAR = {'mIm', 'etIm'}

# 검증 조성. 메틸(둥지 벽) 잔존 비율을 바꿔가며 본다.
COMPOSITIONS = [
    # 대조군
    ({'mIm': 1.00}, '순수 ZIF-8'),
    # 기존 Strategy B 재현 (메틸 0%)
    ({'nIm': 0.50, 'amIm': 0.50}, 'push-pull, 메틸 없음(기존)'),
    # 메틸을 남긴 둥지 -- 문헌이 말하는 진짜 비대칭 미세환경
    ({'mIm': 0.50, 'nIm': 0.25, 'amIm': 0.25}, '둥지: 메틸50 + NO2/NH2'),
    ({'mIm': 0.50, 'clIm': 0.25, 'amIm': 0.25}, '둥지: 메틸50 + Cl/NH2'),
    # 지방족 아민 (문헌 순위 1위) 로 교체
    ({'mIm': 0.50, 'nIm': 0.25, 'amrIm': 0.25}, '둥지: 메틸50 + NO2/지방족아민'),
    ({'mIm': 0.50, 'clIm': 0.25, 'amrIm': 0.25}, '둥지: 메틸50 + Cl/지방족아민'),
    # 술폰산 (문헌 순위 2위)
    ({'mIm': 0.75, 'saIm': 0.25}, '술폰산 25%'),
    # 과충전 경계 확인용 -- 메틸 75% 유지
    ({'mIm': 0.75, 'nIm': 0.125, 'amrIm': 0.125}, '둥지: 메틸75 + NO2/지방족아민'),
]


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


def adjacency(atoms, G, sites):
    """같은 Zn을 공유하는 링커를 인접으로 보는 그래프."""
    syms = atoms.get_chemical_symbols()
    zn_of = []
    for s in sites:
        zns = set()
        for n in [i for i in s['ring'] if syms[i] == 'N']:
            for j in G.neighbors(n):
                if syms[j] == 'Zn':
                    zns.add(j)
        zn_of.append(zns)
    A = nx.Graph()
    A.add_nodes_from(range(len(sites)))
    for i in range(len(sites)):
        for j in range(i + 1, len(sites)):
            if zn_of[i] & zn_of[j]:
                A.add_edge(i, j)
    return A


def nest_assign(sites, A, comp, seed=0):
    """극성기끼리 인접하도록, 비극성기가 그 사이를 채우도록 배치한다.

    무작위 배치는 극성기를 서로 먼 기공에 흩뿌려 둥지가 형성되지 않는다.
    여기서는 (1) 인접 그래프를 2색 채색해 극성 후보 자리를 먼저 잡고,
    (2) 그 안에서 EWG/EDG를 교대 배정하며, (3) 나머지를 비극성기로 채운다.
    """
    rng = np.random.default_rng(seed)
    n = len(sites)
    polar_items = [(k, v) for k, v in comp.items() if k in POLAR]
    nonpolar_items = [(k, v) for k, v in comp.items() if k in NONPOLAR]
    n_polar = int(round(sum(v for _, v in polar_items) * n))

    color = nx.greedy_color(A, strategy='largest_first')
    # 색상 0 그룹을 우선 극성 자리로 채운다 -> 극성기끼리 인접 배치됨
    order = sorted(range(n), key=lambda i: (color[i], rng.random()))
    polar_sites = order[:n_polar]

    assign = [None] * n
    # 극성 자리에 EWG/EDG를 교대 배정
    if polar_items:
        tot = sum(v for _, v in polar_items)
        quota = {k: int(round(v / tot * n_polar)) for k, v in polar_items}
        seq = []
        for k, q in quota.items():
            seq += [k] * q
        while len(seq) < n_polar:
            seq.append(polar_items[0][0])
        # 인접한 극성 자리끼리 서로 다른 종이 되도록 색상으로 재정렬
        polar_sorted = sorted(polar_sites, key=lambda i: color[i])
        keys = [k for k, _ in polar_items]
        for idx, s in enumerate(polar_sorted):
            assign[s] = keys[idx % len(keys)] if len(keys) > 1 else keys[0]
    # 나머지를 비극성기로
    fill = nonpolar_items[0][0] if nonpolar_items else polar_items[0][0]
    for i in range(n):
        if assign[i] is None:
            assign[i] = fill
    return assign


def main():
    import mtv_cif_builder as mcb
    from ase import Atoms
    from ase.io import write

    os.makedirs(OUT, exist_ok=True)
    atoms0 = read(BASE)
    G = graph_of(atoms0)
    sites = json.load(open(SITEMAP))
    A = adjacency(atoms0, G, sites)

    rows = []
    print(f'{"조성":<34} {"극성기":>7} {"메틸":>6} {"원자":>6} {"최소거리":>9}')
    print('-' * 72)
    for comp, label in COMPOSITIONS:
        tag = '_'.join(f'{k}{int(v*100):03d}' for k, v in sorted(comp.items()))
        out_cif = os.path.join(OUT, tag + '.cif')
        assign = nest_assign(sites, A, comp)

        from collections import Counter
        cnt = Counter(assign)
        n_polar = sum(v for k, v in cnt.items() if k in POLAR)
        n_me = cnt.get('mIm', 0)

        frags = {n: mcb.build_fragment(n) for n in set(assign) if n != 'mIm'}
        remove, nsym, npos = set(), [], []
        avoid = atoms0.get_positions().copy()
        for site, lig in zip(sites, assign):
            if lig == 'mIm':
                continue
            subst, newat = mcb.plan_substitution(atoms0, site, frags[lig],
                                                 avoid_positions=avoid)
            remove.update(subst)
            for s_, p_ in newat:
                nsym.append(s_)
                npos.append(p_)
                avoid = np.vstack([avoid, p_])
        mask = np.ones(len(atoms0), dtype=bool)
        mask[sorted(remove)] = False
        out = atoms0[mask]
        if nsym:
            out += Atoms(symbols=nsym, positions=npos)
        write(out_cif, out)
        t = open(out_cif, encoding='utf-8').read()
        for o, nn in (('_space_group_name_H-M_alt', '_symmetry_space_group_name_H-M'),
                      ('_space_group_IT_number', '_symmetry_Int_Tables_number'),
                      ('_space_group_symop_operation_xyz', '_symmetry_equiv_pos_as_xyz')):
            t = t.replace(o, nn)
        open(out_cif, 'w', encoding='utf-8').write(t)

        d = out.get_all_distances(mic=True)
        np.fill_diagonal(d, np.inf)
        print(f'{label:<34} {n_polar:>7} {n_me:>6} {len(out):>6} {d.min():>9.3f}')
        rows.append({'tag': tag, 'label': label, 'composition': comp,
                     'n_polar': n_polar, 'n_methyl': n_me,
                     'n_atoms': len(out), 'min_dist': round(float(d.min()), 3)})

    with open(os.path.join(HERE, 'nest_index.json'), 'w', encoding='utf-8') as f:
        json.dump(rows, f, indent=2, ensure_ascii=False)
    print(f'\n[OK] {len(rows)}개 구조 -> {OUT}')


if __name__ == '__main__':
    main()
