"""결손 밀도별 ZIF-8 구조를 생성한다 (전략 A 성립 가능성 1차 검증용).

배경:
    OMS 감도 분석 결과, 셀당 OMS 1개로는 목표 Q_st에 원리적으로 도달 불가하고
    (레버리지 ~7%, 필요 국소결합 215 kJ/mol) 현실적 OMS 세기로는 셀당 약 4.8개,
    즉 링커 결손 ~2.4개(10%)가 필요하다. 그런데 UiO-66과 달리 ZIF-8은 그만한
    결손 내성이 알려져 있지 않다. DFT에 자원을 넣기 전에 '골격이 버티는가'를
    먼저 싸게 가린다.

전하 보상:
    이미다졸레이트는 -1 이므로 링커 N개를 빼면 골격에 +N이 남는다.
    OH-(-1) N개를 배위시켜 중성을 맞춘다. 링커 하나가 빠지면 Zn 두 개가
    저배위가 되는데, 그중 하나에 OH를 붙이고 나머지 하나를 OMS로 남긴다.
    -> 결손 N개당 OMS N개.
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
BASE = os.path.join(LIB, 'ZIF8_mIm_only_P1.cif')
SITEMAP = os.path.join(LIB, 'site_map.json')
OUT = os.path.join(HERE, 'structures')


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


def build(n_vac, seed, out_cif):
    atoms = read(BASE)
    syms = atoms.get_chemical_symbols()
    G = graph_of(atoms)
    sites = json.load(open(SITEMAP))
    pos = atoms.get_positions()
    cell = np.array(atoms.get_cell())

    def mic(v):
        f = np.linalg.solve(cell.T, v)
        f -= np.round(f)
        return cell.T @ f

    rng = np.random.default_rng(seed)
    # 한 Zn에서 링커가 2개 이상 빠지면 배위수가 2 이하가 되어 비현실적이므로 피한다
    chosen, used_zn = [], set()
    order = list(rng.permutation(len(sites)))
    for si in order:
        if len(chosen) >= n_vac:
            break
        ring = sites[si]['ring']
        ns = [i for i in ring if syms[i] == 'N']
        zns = {j for n in ns for j in G.neighbors(n) if syms[j] == 'Zn'}
        if zns & used_zn:
            continue
        chosen.append(si)
        used_zn |= zns

    if len(chosen) < n_vac:
        return None, f'결손 {n_vac}개를 Zn 중복 없이 배치할 수 없음 (최대 {len(chosen)})'

    remove, oh_pairs = set(), []
    for si in chosen:
        site = sites[si]
        ring = site['ring']
        linker = set(ring) | set(site['substituent'])
        for i in list(linker):
            for j in G.neighbors(i):
                if syms[j] == 'H':
                    linker.add(j)
        remove |= linker
        n1, n3 = [i for i in ring if syms[i] == 'N']
        z1 = next((j for j in G.neighbors(n1) if syms[j] == 'Zn'), None)
        z2 = next((j for j in G.neighbors(n3) if syms[j] == 'Zn'), None)
        if z1 is None or z2 is None:
            return None, 'Zn 탐색 실패'
        oh_pairs.append((z1, n1, z2))   # z1에 OH, z2는 OMS로 남김

    keep = [i for i in range(len(atoms)) if i not in remove]
    new = atoms[keep]

    for z1, n1, _ in oh_pairs:
        d = mic(pos[n1] - pos[z1])
        d /= np.linalg.norm(d)
        p_o = pos[z1] + d * 1.95
        p_h = p_o + d * 0.97
        new += Atoms('OH', positions=[p_o, p_h])

    write(out_cif, new)
    t = open(out_cif, encoding='utf-8').read()
    for o, nn in (('_space_group_name_H-M_alt', '_symmetry_space_group_name_H-M'),
                  ('_space_group_IT_number', '_symmetry_Int_Tables_number'),
                  ('_space_group_symop_operation_xyz', '_symmetry_equiv_pos_as_xyz')):
        t = t.replace(o, nn)
    open(out_cif, 'w', encoding='utf-8').write(t)

    # OMS(3배위 Zn) 개수 검증
    g2 = graph_of(new)
    s2 = new.get_chemical_symbols()
    cn = [sum(1 for j in g2.neighbors(i) if s2[j] in ('N', 'O'))
          for i in range(len(new)) if s2[i] == 'Zn']
    from collections import Counter
    return {'n_vac': n_vac, 'seed': seed, 'n_atoms': len(new),
            'vacancy_pct': round(n_vac / len(sites) * 100, 1),
            'Zn_CN': dict(Counter(cn)), 'n_OMS': sum(1 for c in cn if c == 3)}, None


def main():
    os.makedirs(OUT, exist_ok=True)
    rows = []
    print(f'{"결손":>5} {"비율":>7} {"seed":>5} {"원자":>6} {"OMS":>5}  Zn 배위수 분포')
    print('-' * 68)
    # 0개(순수)부터 6개(25%)까지
    for n_vac in (0, 1, 2, 3, 4, 6):
        seeds = (0,) if n_vac == 0 else (0, 1)
        for sd in seeds:
            name = f'vac{n_vac}_s{sd}'
            p = os.path.join(OUT, name + '.cif')
            if n_vac == 0:
                a = read(BASE)
                write(p, a)
                t = open(p).read()
                for o, nn in (('_space_group_name_H-M_alt', '_symmetry_space_group_name_H-M'),
                              ('_space_group_IT_number', '_symmetry_Int_Tables_number'),
                              ('_space_group_symop_operation_xyz', '_symmetry_equiv_pos_as_xyz')):
                    t = t.replace(o, nn)
                open(p, 'w').write(t)
                info = {'n_vac': 0, 'seed': sd, 'n_atoms': len(a),
                        'vacancy_pct': 0.0, 'Zn_CN': {4: 12}, 'n_OMS': 0}
                err = None
            else:
                info, err = build(n_vac, sd, p)
            if err:
                print(f'{n_vac:>5} {"":>7} {sd:>5}  실패: {err}')
                continue
            info['name'] = name
            rows.append(info)
            print(f'{n_vac:>5} {info["vacancy_pct"]:>6.1f}% {sd:>5} {info["n_atoms"]:>6} '
                  f'{info["n_OMS"]:>5}  {info["Zn_CN"]}')

    with open(os.path.join(HERE, 'defect_index.json'), 'w', encoding='utf-8') as f:
        json.dump(rows, f, indent=2, ensure_ascii=False)
    print(f'\n[OK] {len(rows)}개 구조 생성 -> {OUT}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
