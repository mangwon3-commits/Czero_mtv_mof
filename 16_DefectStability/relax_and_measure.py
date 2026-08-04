"""결손 밀도별 골격 안정성: UFF4MOF 이완 후 붕괴 여부를 정량 측정한다.

측정 지표 (이완 전 -> 후):
    PLD / LCD      공동이 유지되는가 (붕괴하면 급감)
    최소 원자간 거리  구조 파손 여부
    Zn 배위수 분포   OMS가 살아남는가, 아니면 재배위로 메워지는가
    원자 변위 RMSD   골격이 얼마나 크게 재배열되었는가

판정 기준:
    LCD가 초기 대비 20% 이상 감소하면 공동 붕괴로 본다.
    OMS(3배위 Zn) 수가 줄면 이완 중 다른 리간드가 자리를 메운 것이므로
    OMS 전략의 전제가 무너진다.
"""
import glob
import json
import os
import re
import shutil
import subprocess
import sys
from collections import Counter
from concurrent.futures import ProcessPoolExecutor

import numpy as np
import networkx as nx
from ase.io import read, write
from ase.neighborlist import NeighborList, natural_cutoffs

HERE = os.path.dirname(os.path.abspath(__file__))
STRUCT = os.path.join(HERE, 'structures')
WORK = os.path.join(HERE, 'lmp')

# [버그 수정] 이 스크립트는 lammps_mof 환경에서 돌아야 하는데(lammps-interface, lmp_serial),
# Zeo++의 network 바이너리는 czeromof 환경에만 있다. PATH에 없으면 subprocess가 실패하고
# except가 삼켜서 LCD/PLD가 조용히 0으로 남는다(실제로 1차 실행이 전부 0이었다).
# 절대 경로로 직접 지정한다.
NETWORK = shutil.which('network') or os.path.expanduser(
    '~/miniconda3/envs/czeromof/bin/network')


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


def metrics(atoms, tag, tmpdir):
    s = atoms.get_chemical_symbols()
    G = graph_of(atoms)
    cn = [sum(1 for j in G.neighbors(i) if s[j] in ('N', 'O'))
          for i in range(len(atoms)) if s[i] == 'Zn']
    d = atoms.get_all_distances(mic=True)
    np.fill_diagonal(d, np.inf)

    p = os.path.join(tmpdir, tag + '.cif')
    write(p, atoms)
    t = open(p).read()
    for o, n in (('_space_group_name_H-M_alt', '_symmetry_space_group_name_H-M'),
                 ('_space_group_IT_number', '_symmetry_Int_Tables_number'),
                 ('_space_group_symop_operation_xyz', '_symmetry_equiv_pos_as_xyz')):
        t = t.replace(o, n)
    open(p, 'w').write(t)
    lcd = pld = 0.0
    zeo_err = None
    try:
        r = subprocess.run([NETWORK, '-ha', '-res', p + '.res', p],
                           capture_output=True, text=True, timeout=600)
        if r.returncode != 0:
            zeo_err = f'exit {r.returncode}: {r.stderr.strip()[:80]}'
        else:
            q = open(p + '.res').readline().split()
            lcd, pld = float(q[1]), float(q[2])
    except Exception as e:
        zeo_err = f'{type(e).__name__}: {e}'
    # [버그 수정] 실패를 조용히 삼키지 않고 드러낸다
    return {'LCD': lcd, 'PLD': pld, 'min_dist': round(float(d.min()), 3),
            'Zn_CN': dict(Counter(cn)), 'n_OMS': sum(1 for c in cn if c == 3),
            'n_Zn': len(cn), 'zeo_error': zeo_err}


def run_one(name):
    src = os.path.join(STRUCT, name + '.cif')
    d = os.path.join(WORK, name)
    os.makedirs(d, exist_ok=True)
    shutil.copy(src, os.path.join(d, name + '.cif'))

    before = read(src)
    m0 = metrics(before, 'before', d)

    # LAMMPS 입력 생성 -> 이완 -> 최종 구조 저장
    r = subprocess.run(f'yes | lammps-interface -ff UFF4MOF --minimize {name}.cif',
                       shell=True, cwd=d, capture_output=True, text=True, timeout=900)
    inp = os.path.join(d, f'in.{name}')
    if not os.path.exists(inp):
        return name, m0, None, 'lammps-interface 실패'
    with open(inp, 'a') as f:
        f.write(f'\nwrite_data min_{name}.data nocoeff\n')
    try:
        subprocess.run(['lmp_serial', '-in', f'in.{name}'], cwd=d,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=3600)
    except subprocess.TimeoutExpired:
        return name, m0, None, 'LAMMPS 시간초과'

    dat = os.path.join(d, f'min_{name}.data')
    if not os.path.exists(dat):
        return name, m0, None, 'LAMMPS 출력 없음'

    after = read(dat, format='lammps-data', style='full')
    # data 파일에는 원소 정보가 없으므로 슈퍼셀 배수만큼 원본 심볼을 반복 이식
    n0 = len(before)
    rep = len(after) // n0
    after.set_chemical_symbols(list(before.get_chemical_symbols()) * rep)
    m1 = metrics(after, 'after', d)
    m1['supercell_rep'] = rep
    # [버그 수정] lammps-interface가 컷오프를 맞추려고 2x2x2로 확장하므로 '이완 후'는
    # 슈퍼셀이다. 원자 수·OMS 수를 단위셀과 직접 비교하면 정확히 rep배로 부풀어
    # "OMS 1 -> 8"처럼 잘못 읽힌다(1차 실행이 그랬다). 단위셀 기준으로 환산한다.
    m1['n_OMS_per_cell'] = m1['n_OMS'] / rep
    m1['n_Zn_per_cell'] = m1['n_Zn'] / rep
    m0['n_OMS_per_cell'] = float(m0['n_OMS'])
    m0['n_Zn_per_cell'] = float(m0['n_Zn'])
    return name, m0, m1, 'ok'


def main():
    idx = json.load(open(os.path.join(HERE, 'defect_index.json'), encoding='utf-8'))
    names = [r['name'] for r in idx]
    info = {r['name']: r for r in idx}
    os.makedirs(WORK, exist_ok=True)

    print(f'구조 {len(names)}개 이완 중...\n', flush=True)
    res = {}
    with ProcessPoolExecutor(max_workers=6) as ex:
        for name, m0, m1, st in ex.map(run_one, names):
            res[name] = (m0, m1, st)
            print(f'  [{st:>16}] {name}', flush=True)

    print('\n' + '=' * 106)
    print(f'{"구조":<10} {"결손%":>6} {"LCD 전→후":>17} {"PLD 전→후":>17} '
          f'{"최소거리":>9} {"OMS/셀 전→후":>14}  판정')
    print('-' * 106)
    rows = []
    for n in names:
        m0, m1, st = res[n]
        if m1 is None:
            print(f'{n:<10} {"":>6} {st}')
            continue
        vac = info[n]['vacancy_pct']
        if m0.get('zeo_error') or m1.get('zeo_error'):
            print(f'{n:<10} {vac:>5.1f}%  Zeo++ 실패: '
                  f'{m0.get("zeo_error") or m1.get("zeo_error")}')
            continue
        lcd_drop = (m1['LCD'] - m0['LCD']) / m0['LCD'] * 100 if m0['LCD'] else float('nan')
        # 단위셀 환산값으로 비교 (슈퍼셀 배수 제거)
        oms0, oms1 = m0['n_OMS_per_cell'], m1['n_OMS_per_cell']
        verdict = []
        if lcd_drop == lcd_drop and lcd_drop < -20:
            verdict.append('공동붕괴')
        if m1['min_dist'] < 0.7:
            verdict.append('원자겹침')
        if oms0 > 0 and oms1 < oms0 - 0.01:
            verdict.append('OMS소실')
        v = ' / '.join(verdict) if verdict else '유지'
        print(f'{n:<10} {vac:>5.1f}% {m0["LCD"]:>7.2f}→{m1["LCD"]:>7.2f} '
              f'{m0["PLD"]:>7.2f}→{m1["PLD"]:>7.2f} {m1["min_dist"]:>9.3f} '
              f'{oms0:>6.1f}→{oms1:<6.1f}  {v}  ({lcd_drop:+.1f}%)')
        rows.append({'name': n, 'vacancy_pct': vac, 'before': m0, 'after': m1,
                     'LCD_change_pct': round(lcd_drop, 1), 'verdict': v})

    with open(os.path.join(HERE, 'stability_results.json'), 'w', encoding='utf-8') as f:
        json.dump(rows, f, indent=2, ensure_ascii=False)
    print('\n판정 기준: LCD 20% 이상 감소=공동붕괴, 최소거리<0.7Å=원자겹침, '
          'OMS 수 감소=재배위로 자리 메움')
    return 0


if __name__ == '__main__':
    sys.exit(main())
