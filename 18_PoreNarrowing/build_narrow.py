"""전략: 고밀도 치환으로 기공을 좁혀 반대편 벽의 LJ 퍼텐셜을 겹치게 한다.

배경 (10_DensityMap/analyze_density.py 결과):
    CO2의 밀도가중 평균 벽거리가 조성과 무관하게 3.32~3.48 A로 고정이다.
    ZIF-8 공동이 11.4 A이므로 CO2가 한쪽 벽에서 3.4 A에 있으면 반대편 벽까지는
    ~8 A다. 분산력은 r^-6이므로 반대편 기여는 (3.4/8)^6 ~ 0.6%, 사실상 0이다.
    즉 CO2는 벽 '한쪽만' 느끼고 있고, 이게 Qst ~23 kJ/mol 천장의 기하학적 원인이다.
    작용기 화학을 아무리 바꿔도 이 항은 안 바뀐다. 벽 사이 거리를 줄여야 한다.

작용기 선택 근거 (같은 분석의 enrichment E):
    -Cl    E = 1.66~1.98   원자 6~14개로 부피 9~24%만 쓰고 최고 농축
    -SO3H  (17_NestEffect) 치환율 25%만으로 로딩 0.5820 -- 전체 최고, 극성기당 효율 1위
    -NO2   E = 0.82~1.04   원자 42개로 부피 38~46% 점유, 사실상 무효 (과충전)
    -CN    E = 0.44~0.60   CO2가 회피, 창구를 막기만 함
    따라서 부피당 정전기 이득이 가장 큰 -Cl, -SO3H 만으로 고밀도 치환한다.

닫힌상/열린상 병행:
    정적 ZIF-8의 PLD는 3.25 A로 CO2 운동직경 3.3 A보다 이미 작다. 그런데 실제
    ZIF-8은 CO2를 잘 흡착한다 -- 유한온도에서 링커가 회전(swing)하기 때문이다.
    그래서 정적 구조 하나만 보면 순수 ZIF-8조차 '기공 막힘'으로 오판된다.
    닫힌상(상압 구조)과 열린상(1.47 GPa 게이트-오픈 구조) 양쪽에 같은 조성을
    올려 실제 거동을 괄호로 묶는다.
"""
import json
import os
import sys
from collections import Counter

import numpy as np
import networkx as nx
from ase import Atoms
from ase.io import read, write
from ase.neighborlist import NeighborList, natural_cutoffs

HERE = os.path.dirname(os.path.abspath(__file__))
LIB = os.path.join(HERE, '..', '05_MTV_Ligand_Library')
sys.path.insert(0, LIB)
OUT = os.path.join(HERE, 'structures')

PHASES = {
    'closed': (os.path.join(LIB, 'ZIF8_mIm_only_P1.cif'),
               os.path.join(LIB, 'site_map.json')),
    'open':   (os.path.join(LIB, 'ZIF8_open_mIm_only_P1.cif'),
               os.path.join(LIB, 'site_map_zif8_open.json')),
}

# 치환율을 올려가며 공동이 좁아지는 궤적을 본다. 100%는 문헌상 합성이 실패한
# 사례가 있으므로(NO2-BDC 단독 등) 계산 상한 참고용으로만 포함한다.
COMPOSITIONS = [
    ({'mIm': 1.00},                  '대조군 순수 ZIF-8'),
    ({'mIm': 0.50, 'clIm': 0.50},    'Cl 50%'),
    ({'mIm': 0.25, 'clIm': 0.75},    'Cl 75%'),
    ({'clIm': 1.00},                 'Cl 100% (상한 참고)'),
    ({'mIm': 0.50, 'saIm': 0.50},    'SO3H 50%'),
    ({'mIm': 0.25, 'saIm': 0.75},    'SO3H 75%'),
    ({'clIm': 0.50, 'saIm': 0.50},   'Cl 50% + SO3H 50%'),
    ({'mIm': 0.25, 'clIm': 0.50, 'saIm': 0.25}, 'Cl 50% + SO3H 25%'),
]


def fix_symmetry_tags(path):
    """RASPA/Zeo++가 읽는 구식 태그로 되돌린다 (ASE는 신식 태그로 쓴다)."""
    t = open(path, encoding='utf-8').read()
    for o, n in (('_space_group_name_H-M_alt', '_symmetry_space_group_name_H-M'),
                 ('_space_group_IT_number', '_symmetry_Int_Tables_number'),
                 ('_space_group_symop_operation_xyz', '_symmetry_equiv_pos_as_xyz')):
        t = t.replace(o, n)
    open(path, 'w', encoding='utf-8').write(t)


def linker_adjacency(atoms, sites):
    """같은 Zn을 공유하는 링커를 인접으로 보는 그래프."""
    nl = NeighborList(natural_cutoffs(atoms, mult=1.15), skin=0.0,
                      self_interaction=False, bothways=True)
    nl.update(atoms)
    syms = atoms.get_chemical_symbols()
    zn_of = []
    for s in sites:
        zns = set()
        for n_ in [i for i in s['ring'] if syms[i] == 'N']:
            for j in nl.get_neighbors(n_)[0]:
                if syms[int(j)] == 'Zn':
                    zns.add(int(j))
        zn_of.append(zns)
    A = nx.Graph()
    A.add_nodes_from(range(len(sites)))
    for i in range(len(sites)):
        for j in range(i + 1, len(sites)):
            if zn_of[i] & zn_of[j]:
                A.add_edge(i, j)
    return A


# 부피가 큰 치환기부터 먼저, 서로 최대한 떨어뜨려 배치한다.
BULK_ORDER = {'saIm': 0, 'clIm': 1, 'mIm': 2}


def assign(sites, comp, A, seed=0):
    """부피 큰 치환기를 인접 자리끼리 피해서 배치한다.

    무작위 배치를 쓰면 -SO3H 두 개가 같은 Zn을 공유하는 이웃 자리에 떨어져
    술폰산 산소끼리 0.57~0.73 A까지 겹친다(회전각을 12->72개로 늘려도 해소되지
    않았다 -- 방향 문제가 아니라 밀도 문제다). 인접 그래프에서 이미 배정된
    부피 큰 치환기와의 접촉 수가 최소인 자리를 그리디로 고른다. 극성기를 고르게
    퍼뜨리는 편이 공동을 균일하게 좁힌다는 점에서 물리적으로도 이쪽이 맞다.
    """
    rng = np.random.default_rng(seed)
    n = len(sites)
    counts = {}
    for k, v in comp.items():
        counts[k] = int(round(v * n))
    while sum(counts.values()) < n:
        counts[max(comp, key=comp.get)] += 1
    while sum(counts.values()) > n:
        counts[max(counts, key=counts.get)] -= 1

    out = [None] * n
    placed = []
    for lig in sorted(counts, key=lambda k: BULK_ORDER.get(k, 9)):
        if lig == 'mIm':
            continue
        for _ in range(counts[lig]):
            free = [i for i in range(n) if out[i] is None]
            # 이미 배정된 치환기와의 인접 수가 최소인 자리 (동점이면 무작위)
            best = min(free, key=lambda i: (sum(1 for p in placed if A.has_edge(i, p)),
                                            rng.random()))
            out[best] = lig
            placed.append(best)
    for i in range(n):
        if out[i] is None:
            out[i] = 'mIm'
    return out


def main():
    import mtv_cif_builder as mcb
    os.makedirs(OUT, exist_ok=True)
    rows = []
    print(f'{"구조":<34} {"상":<7} {"치환기":>6} {"원자":>6} {"최소거리":>9}  비고')
    print('-' * 88)

    for phase, (base, sitemap) in PHASES.items():
        atoms0 = read(base)
        sites = json.load(open(sitemap))
        A = linker_adjacency(atoms0, sites)
        for comp, label in COMPOSITIONS:
            tag = '_'.join(f'{k}{int(round(v*100)):03d}' for k, v in sorted(comp.items()))
            name = f'{tag}__{phase}'
            out_cif = os.path.join(OUT, name + '.cif')
            lig = assign(sites, comp, A)
            cnt = Counter(lig)
            n_sub = sum(v for k, v in cnt.items() if k != 'mIm')

            frags = {n: mcb.build_fragment(n) for n in set(lig) if n != 'mIm'}
            remove, nsym, npos = set(), [], []
            avoid = atoms0.get_positions().copy()
            for site, l in zip(sites, lig):
                if l == 'mIm':
                    continue
                subst, newat = mcb.plan_substitution(atoms0, site, frags[l],
                                                     avoid_positions=avoid, n_trial_angles=72)
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
            out.wrap()
            write(out_cif, out)
            fix_symmetry_tags(out_cif)

            d = out.get_all_distances(mic=True)
            np.fill_diagonal(d, np.inf)
            dmin = float(d.min())
            note = '겹침 위험' if dmin < 0.7 else ''
            print(f'{label:<34} {phase:<7} {n_sub:>6} {len(out):>6} {dmin:>9.3f}  {note}')
            rows.append({'name': name, 'tag': tag, 'label': label, 'phase': phase,
                         'composition': comp, 'n_substituted': n_sub,
                         'n_atoms': len(out), 'min_dist': round(dmin, 3)})

    with open(os.path.join(HERE, 'narrow_index.json'), 'w', encoding='utf-8') as f:
        json.dump(rows, f, indent=2, ensure_ascii=False)
    print(f'\n[OK] {len(rows)}개 구조 -> {OUT}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
