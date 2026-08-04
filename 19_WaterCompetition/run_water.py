"""CO2/H2O 경쟁 흡착 -- 이 프로젝트에서 가장 오래 미뤄둔 결정적 검증.

[왜 지금 최우선인가]
    18_PoreNarrowing 결과로 최고 성능 조성이 -SO3H 계열로 바뀌었다
    (SO3H 50%: Qst 23.88, 선택도 25.31, 로딩 0.8321 -- 역대 최고).
    그런데 술폰산은 강산이자 강한 흡습성 관능기다. 물은 CO2와 달리
    영구 쌍극자를 갖고 수소결합을 형성하므로, 우리가 만든 정전기 포집점이
    CO2보다 물을 먼저 잡을 가능성이 높다. 실제 배가스는 습윤 상태다.

    즉 수분 경쟁은 더 이상 'OMS 전략의 리스크'가 아니라 **최고 성능 조성
    자체의 존폐 조건**이다.

[설계]
    이원 GCMC (CO2 + H2O). CO2 분압은 배가스 조건 0.15 bar 로 고정하고
    상대습도를 0 -> 90% 로 올리며 CO2 흡착이 얼마나 밀려나는지 본다.
    298 K 에서 P_sat(H2O) = 3169 Pa 이므로 RH 90% = 2852 Pa.

    대조를 위해 소수성 원본(순수 ZIF-8)과 극성기 조성을 함께 돌린다.
    순수 ZIF-8이 물을 거의 안 먹는 것이 확인되어야 계산 자체가 신뢰된다
    (ZIF-8의 소수성은 실험적으로 잘 알려진 사실이므로 이게 내부 검증이 된다).

[물 모델]
    TIP5P-Ew. 배포본 water.def 가 3원자짜리라 알짜전하가 +0.482 가 되는
    문제가 있어 5사이트 정의를 직접 만들어 쓴다(같은 폴더 water.def 참조).
    RASPA는 실행 디렉터리의 <분자>.def 를 먼저 찾으므로 공유 설치본을
    건드리지 않고 덮어쓸 수 있다.

[샘플링]
    소수성 기공 안의 물은 삽입 수용률이 극히 낮아 수렴이 느리다.
    그래서 기존 계산(5000 사이클)보다 늘려 잡는다.
"""
import glob
import json
import os
import re
import shutil
import subprocess
import sys
from concurrent.futures import ProcessPoolExecutor

import numpy as np
from ase.io import read

HERE = os.path.dirname(os.path.abspath(__file__))
CHARGED = os.path.join(HERE, '..', '18_PoreNarrowing', 'charged')
RUNS = os.path.join(HERE, 'runs')
WATER_DEF = os.path.join(HERE, 'water.def')

SIMULATE = shutil.which('simulate') or os.path.expanduser(
    '~/miniconda3/envs/czeromof/bin/simulate')

TEMP = 298.0
CUTOFF = 12.0
P_CO2 = 0.15e5              # Pa, 배가스 CO2 분압
P_SAT_298 = 3169.0          # Pa, 298.15 K 물 포화증기압
RH_LIST = [0.0, 0.25, 0.50, 0.90]
CYCLES, INIT = 15000, 5000

# 닫힌상(상압 구조)만 본다. SO3H 열린상은 위험도 검증에서 창구 폐쇄로 탈락했다.
TARGETS = [
    ('mIm100__closed',                  '순수 ZIF-8 (소수성 대조군)'),
    ('clIm100__closed',                 'Cl 100%'),
    ('mIm050_saIm050__closed',          'SO3H 50% (최고 로딩)'),
    ('clIm050_saIm050__closed',         'Cl 50% + SO3H 50% (최고 Qst)'),
    ('clIm050_mIm025_saIm025__closed',  'Cl 50% + SO3H 25%'),
]


def unit_cells(atoms, cutoff=CUTOFF):
    cell = atoms.get_cell()
    vol = abs(np.linalg.det(cell))
    reps = []
    for i in range(3):
        j, k = (i + 1) % 3, (i + 2) % 3
        width = vol / np.linalg.norm(np.cross(cell[j], cell[k]))
        reps.append(max(1, int(np.ceil(2.0 * cutoff / width))))
    return reps


def parse_components(path):
    """성분별 흡착량 [mol/kg] 을 뽑는다. RASPA 출력은 Component 블록마다
    같은 문구를 반복하므로 어느 성분 블록인지 추적해야 한다."""
    out = {}
    cur = None
    for line in open(path, encoding='utf-8', errors='ignore'):
        m = re.search(r'Component\s+(\d+)\s+\[(\w+)\]', line)
        if m:
            cur = m.group(2)
        if cur and 'Average loading absolute [mol/kg framework]' in line:
            v = re.search(r':?\s*([0-9.eE+-]+)\s*\+/-\s*([0-9.eE+-]+)', line)
            if v and cur not in out:
                out[cur] = (float(v.group(1)), float(v.group(2)))
    return out


def run_one(job):
    name, rh = job
    cif = os.path.join(CHARGED, name + '_DDEC6.cif')
    fw = name + '_DDEC6'
    d = os.path.join(RUNS, f'rh{int(rh*100):02d}_{name}')
    os.makedirs(d, exist_ok=True)
    shutil.copy(cif, os.path.join(d, fw + '.cif'))
    shutil.copy(WATER_DEF, os.path.join(d, 'water.def'))
    na, nb, nc = unit_cells(read(cif))

    p_h2o = P_SAT_298 * rh
    p_tot = P_CO2 + p_h2o
    x_co2 = P_CO2 / p_tot
    x_h2o = p_h2o / p_tot

    moves = ('            TranslationProbability    0.5\n'
             '            RotationProbability       0.3\n'
             '            ReinsertionProbability    0.1\n'
             '            SwapProbability           1.0\n'
             '            CreateNumberOfMolecules   0\n')
    comp = f"""Component 0 MoleculeName              CO2
            MoleculeDefinition        TraPPE
            MolFraction               {x_co2:.6f}
{moves}"""
    if rh > 0:
        comp += f"""
Component 1 MoleculeName              water
            MoleculeDefinition        TraPPE
            MolFraction               {x_h2o:.6f}
{moves}"""

    with open(os.path.join(d, 'simulation.input'), 'w') as f:
        f.write(f"""SimulationType                MonteCarlo
NumberOfCycles                {CYCLES}
NumberOfInitializationCycles  {INIT}
PrintEvery                    {CYCLES}
RestartFile                   no

Forcefield                    UFF_MOF
CutOff                        {CUTOFF}
UseChargesFromCIFFile         yes
ChargeMethod                  Ewald
EwaldPrecision                1e-6

Framework 0
FrameworkName                 {fw}
UnitCells                     {na} {nb} {nc}
ExternalTemperature           {TEMP}
ExternalPressure              {p_tot:.4f}

{comp}""")
    try:
        subprocess.run([SIMULATE, 'simulation.input'], cwd=d,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                       timeout=21600, check=False)
    except subprocess.TimeoutExpired:
        return name, rh, None, 'timeout'
    outs = glob.glob(os.path.join(d, 'Output', 'System_0', '*.data'))
    if not outs:
        return name, rh, None, 'no-output'
    res = parse_components(outs[0])
    for sub in ('VTK', 'Movies', 'Restart'):
        shutil.rmtree(os.path.join(d, sub), ignore_errors=True)
    return name, rh, res, 'ok'


def _star(a):
    return run_one(a)


def main():
    missing = [n for n, _ in TARGETS
               if not os.path.exists(os.path.join(CHARGED, n + '_DDEC6.cif'))]
    if missing:
        print('전하 구조 없음:', missing)
        return 1
    os.makedirs(RUNS, exist_ok=True)

    # 이미 끝난 작업은 건너뛴다. 이 계산은 이원 GCMC 라 한 작업이 길고,
    # 기기를 옮기거나 중단됐다 재개하는 일이 실제로 생긴다.
    # water_results.json 을 먼저 본다. 이건 collect_results.py 가 실행 디렉터리를
    # 직접 훑어 만든 것이라, 드라이버가 중간에 죽어 로그에 안 남은 작업까지 잡힌다
    # (실제로 로그에는 9개, 실행 디렉터리에는 12개가 있었다).
    res = {}
    partial = next((p for p in (os.path.join(HERE, 'water_results.json'),
                                os.path.join(HERE, 'water_partial.json'))
                    if os.path.exists(p)), None)
    if partial:
        for r in json.load(open(partial, encoding='utf-8')):
            d = {'CO2': (r['CO2_molkg'], 0.0)}
            if r['RH'] > 0:
                d['water'] = (r['H2O_molkg'], 0.0)
            res.setdefault(r['name'], {})[r['RH']] = d
        n_done = sum(len(v) for v in res.values())
        print(f'이어받기: 완료된 {n_done}개 작업을 건너뜁니다', flush=True)

    jobs = [(n, rh) for n, _ in TARGETS for rh in RH_LIST
            if rh not in res.get(n, {})]
    print(f'구조 {len(TARGETS)}개 x RH {len(RH_LIST)}단계 중 실행할 작업 {len(jobs)}개', flush=True)
    print(f'CO2 {P_CO2/1e5:.2f} bar 고정, 298 K, TIP5P-Ew, {CYCLES} 사이클\n', flush=True)

    with ProcessPoolExecutor(max_workers=6) as ex:
        for name, rh, r, st in ex.map(_star, jobs):
            res.setdefault(name, {})[rh] = r
            co2 = r.get('CO2', (float('nan'),))[0] if r else float('nan')
            h2o = r.get('water', (0.0,))[0] if r else float('nan')
            print(f'  [{st:>9}] RH{int(rh*100):>3}% {name:<32} '
                  f'CO2 {co2:>7.4f}  H2O {h2o:>8.4f}', flush=True)

    label = dict(TARGETS)
    print('\n' + '=' * 104)
    print(f'{"구조":<30} {"RH":>5} {"CO2 [mol/kg]":>14} {"H2O [mol/kg]":>14} '
          f'{"건조대비 CO2":>13} {"H2O/CO2":>9}')
    print('-' * 104)
    rows = []
    for name, lab in TARGETS:
        dry = (res.get(name, {}).get(0.0) or {}).get('CO2', (float('nan'),))[0]
        for rh in RH_LIST:
            r = res.get(name, {}).get(rh)
            if not r:
                continue
            c = r.get('CO2', (float('nan'), 0))[0]
            w = r.get('water', (0.0, 0))[0]
            ret = c / dry * 100 if dry and dry == dry else float('nan')
            ratio = w / c if c else float('inf')
            print(f'{lab:<30} {int(rh*100):>4}% {c:>14.4f} {w:>14.4f} '
                  f'{ret:>12.1f}% {ratio:>9.2f}')
            rows.append({'name': name, 'label': lab, 'RH': rh,
                         'CO2_molkg': c, 'H2O_molkg': w,
                         'CO2_retention_pct': ret, 'H2O_over_CO2': ratio})
        print()
    with open(os.path.join(HERE, 'water_results.json'), 'w', encoding='utf-8') as f:
        json.dump(rows, f, indent=2, ensure_ascii=False)
    print('[OK] water_results.json')
    print('\n판정: 순수 ZIF-8이 물을 거의 안 먹어야 계산이 신뢰된다(실험적 소수성).')
    print('      극성기 조성의 건조대비 CO2 유지율이 핵심 지표.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
