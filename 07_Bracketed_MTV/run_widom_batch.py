"""괄호치기(closed/open) 구조 14개에 RASPA Widom 삽입을 병렬 실행한다.

설정:
    Forcefield  UFF_MOF          -- UFF LJ 파라미터 (Rappe et al. JACS 1992)
    UseChargesFromCIFFile yes    -- EQeq 부분전하 사용
    298 K, Widom insertion       -- CO2와 N2 각각

[중요] Widom 삽입은 본질적으로 '무한희석' 방법이다. 여기서 얻는 것은
    - K_H : 헨리 상수 (무한희석)
    - Q_st: 무한희석 등량흡착열 = -(<U_gh> - <U_h>) - RT
  특정 압력(예: 0.15 bar)에서의 Q_st는 유한 로딩 상태이므로 GCMC가 따로 필요하다.
  다만 flue gas의 CO2 분압 0.15 bar는 로딩이 낮아 무한희석 값이 좋은 근사가 된다.
"""
import glob
import os
import re
import shutil
import subprocess
import sys
from concurrent.futures import ProcessPoolExecutor

import numpy as np
from ase.io import read

HERE = os.path.dirname(os.path.abspath(__file__))
RUNS = os.path.join(HERE, 'widom_runs')
CYCLES = 2000
INIT = 500
TEMP = 298.0
CUTOFF = 12.0
FORCEFIELD = 'UFF_MOF'
R_GAS = 8.314462618e-3  # kJ/mol/K


def unit_cells(atoms, cutoff=CUTOFF):
    """비직교 셀에서도 안전하도록 '수직 폭' 기준으로 반복수를 정한다.

    단순히 격자상수를 컷오프로 나누면 육방정계(gamma=120도) 같은 셀에서 최소거리규약이
    깨진다 (실측: ZIF-69에서 1x1x2로도 RASPA가 INAPPROPRIATE UNIT CELLS 경고).
    각 축의 수직 폭 = 부피 / (다른 두 축이 만드는 평행사변형 넓이).
    """
    cell = atoms.get_cell()
    vol = abs(np.linalg.det(cell))
    reps = []
    for i in range(3):
        j, k = (i + 1) % 3, (i + 2) % 3
        area = np.linalg.norm(np.cross(cell[j], cell[k]))
        width = vol / area
        reps.append(max(1, int(np.ceil(2.0 * cutoff / width))))
    return reps


def parse_output(path):
    """Output/System_0/*.data 에서 K_H와 무한희석 흡착에너지를 뽑는다."""
    kh = kh_err = None
    u = u_err = None
    with open(path, encoding='utf-8', errors='ignore') as f:
        for line in f:
            if 'Average Henry coefficient:' in line:
                m = re.search(r':\s*([0-9.eE+-]+)\s*\+/-\s*([0-9.eE+-]+)', line)
                if m:
                    kh, kh_err = float(m.group(1)), float(m.group(2))
            if '<U_gh>_1-<U_h>_0:' in line:
                m = re.search(r'\(\s*([0-9.eE+-]+)\s*\+/-\s*([0-9.eE+-]+)\s*kJ/mol', line)
                if m:
                    u, u_err = float(m.group(1)), float(m.group(2))
    return kh, kh_err, u, u_err


def run_one(job):
    cif, gas = job
    name = os.path.basename(cif).replace('.cif', '')
    d = os.path.join(RUNS, f'{gas}_{name}')
    os.makedirs(d, exist_ok=True)
    shutil.copy(cif, os.path.join(d, f'{name}.cif'))
    na, nb, nc = unit_cells(read(cif))

    with open(os.path.join(d, 'simulation.input'), 'w') as f:
        f.write(f"""SimulationType                MonteCarlo
NumberOfCycles                {CYCLES}
NumberOfInitializationCycles  {INIT}
PrintEvery                    {CYCLES}
RestartFile                   no

Forcefield                    {FORCEFIELD}
CutOff                        {CUTOFF}
UseChargesFromCIFFile         yes

Framework 0
FrameworkName                 {name}
UnitCells                     {na} {nb} {nc}
ExternalTemperature           {TEMP}

Component 0 MoleculeName              {gas}
            MoleculeDefinition        TraPPE
            WidomProbability          1.0
            CreateNumberOfMolecules   0
""")
    try:
        subprocess.run(['simulate', 'simulation.input'], cwd=d,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                       timeout=3600, check=False)
    except subprocess.TimeoutExpired:
        return (name, gas, None, None, None, None, 'timeout')

    outs = glob.glob(os.path.join(d, 'Output', 'System_0', '*.data'))
    if not outs:
        return (name, gas, None, None, None, None, 'no-output')
    kh, kh_err, u, u_err = parse_output(outs[0])
    # 용량 절약: 대용량 보조 출력 제거
    for sub in ('VTK', 'Movies', 'Restart'):
        shutil.rmtree(os.path.join(d, sub), ignore_errors=True)
    return (name, gas, kh, kh_err, u, u_err, 'ok')


def main():
    os.makedirs(RUNS, exist_ok=True)
    cifs = sorted(glob.glob(os.path.join(HERE, '*.cif')))
    jobs = [(c, g) for c in cifs for g in ('CO2', 'N2')]
    print(f'구조 {len(cifs)}개 x 가스 2종 = {len(jobs)}개 작업, '
          f'{CYCLES} cycles, {FORCEFIELD}, EQeq 전하 사용\n', flush=True)

    results = {}
    with ProcessPoolExecutor(max_workers=7) as ex:
        for name, gas, kh, kh_err, u, u_err, status in ex.map(run_one, jobs):
            results.setdefault(name, {})[gas] = (kh, kh_err, u, u_err, status)
            print(f'  [{status:>9}] {gas:<3} {name}', flush=True)

    print('\n' + '=' * 104)
    print(f'{"구조":<30} {"KH(CO2)":>11} {"KH(N2)":>11} {"CO2/N2":>8} '
          f'{"Qst(CO2)":>10} {"Qst(N2)":>9}')
    print('-' * 104)
    rows = []
    for name in sorted(results):
        co2 = results[name].get('CO2', (None,) * 5)
        n2 = results[name].get('N2', (None,) * 5)
        kh_c, _, u_c, _, _ = co2
        kh_n, _, u_n, _, _ = n2
        sel = (kh_c / kh_n) if (kh_c and kh_n) else float('nan')
        # Qst = -(U_gh - U_h) - RT   [kJ/mol]
        qst_c = (-u_c - R_GAS * TEMP) if u_c is not None else float('nan')
        qst_n = (-u_n - R_GAS * TEMP) if u_n is not None else float('nan')
        print(f'{name:<30} {kh_c if kh_c else float("nan"):>11.4e} '
              f'{kh_n if kh_n else float("nan"):>11.4e} {sel:>8.2f} '
              f'{qst_c:>10.2f} {qst_n:>9.2f}')
        rows.append({'name': name, 'KH_CO2': kh_c, 'KH_N2': kh_n,
                     'selectivity': sel, 'Qst_CO2': qst_c, 'Qst_N2': qst_n})

    import json
    with open(os.path.join(HERE, 'widom_results.json'), 'w', encoding='utf-8') as f:
        json.dump(rows, f, indent=2)
    print(f'\n[OK] 저장: {os.path.join(HERE, "widom_results.json")}')
    print('Qst는 무한희석 값 (Widom). 0.15 bar 유한로딩 Qst는 GCMC 별도 필요.')


if __name__ == '__main__':
    sys.exit(main())
