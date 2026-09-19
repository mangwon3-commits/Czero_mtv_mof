"""DDEC6 전하 구조로 Widom(K_H, Q_st)과 0.15 bar GCMC(로딩)를 재계산한다.

EQeq 결과와 직접 비교하기 위해 힘장/사이클/온도는 동일하게 유지한다:
    UFF_MOF, 298 K, CutOff 12.0, Widom 2000 cycles / GCMC 5000 cycles
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
STRUCT = os.path.join(HERE, 'charged')
RUNS = os.path.join(HERE, 'runs')
TEMP = 298.0
CUTOFF = 12.0
R_GAS = 8.314462618e-3
WIDOM_CYCLES, WIDOM_INIT = 5000, 1500
GCMC_CYCLES, GCMC_INIT = 5000, 2000
PRESSURE = 0.15e5


def unit_cells(atoms, cutoff=CUTOFF):
    cell = atoms.get_cell()
    vol = abs(np.linalg.det(cell))
    reps = []
    for i in range(3):
        j, k = (i + 1) % 3, (i + 2) % 3
        width = vol / np.linalg.norm(np.cross(cell[j], cell[k]))
        reps.append(max(1, int(np.ceil(2.0 * cutoff / width))))
    return reps


def parse(path):
    kh = u = load = None
    for line in open(path, encoding='utf-8', errors='ignore'):
        if 'Average Henry coefficient:' in line:
            m = re.search(r':\s*([0-9.eE+-]+)\s*\+/-', line)
            if m:
                kh = float(m.group(1))
        if '<U_gh>_1-<U_h>_0:' in line:
            m = re.search(r'\(\s*([0-9.eE+-]+)\s*\+/-', line)
            if m:
                u = float(m.group(1))
        if 'Average loading absolute [mol/kg framework]' in line:
            m = re.search(r':?\s*([0-9.eE+-]+)\s*\+/-', line)
            if m:
                load = float(m.group(1))
    return kh, u, load


def run_one(job):
    cif, gas, mode = job
    name = os.path.basename(cif).replace('.cif', '')
    d = os.path.join(RUNS, f'{mode}_{gas}_{name}')
    os.makedirs(d, exist_ok=True)
    shutil.copy(cif, os.path.join(d, name + '.cif'))
    na, nb, nc = unit_cells(read(cif))

    if mode == 'widom':
        moves = ('            WidomProbability          1.0\n'
                 '            CreateNumberOfMolecules   0\n')
        cyc, init, press = WIDOM_CYCLES, WIDOM_INIT, 1e-5
    else:
        moves = ('            TranslationProbability    0.5\n'
                 '            RotationProbability       0.3\n'
                 '            ReinsertionProbability    0.1\n'
                 '            SwapProbability           1.0\n'
                 '            CreateNumberOfMolecules   0\n')
        cyc, init, press = GCMC_CYCLES, GCMC_INIT, PRESSURE

    with open(os.path.join(d, 'simulation.input'), 'w') as f:
        f.write(f"""SimulationType                MonteCarlo
NumberOfCycles                {cyc}
NumberOfInitializationCycles  {init}
PrintEvery                    {cyc}
RestartFile                   no

Forcefield                    UFF_MOF
CutOff                        {CUTOFF}
UseChargesFromCIFFile         yes

Framework 0
FrameworkName                 {name}
UnitCells                     {na} {nb} {nc}
ExternalTemperature           {TEMP}
ExternalPressure              {press}

Component 0 MoleculeName              {gas}
            MoleculeDefinition        TraPPE
{moves}""")
    try:
        subprocess.run(['simulate', 'simulation.input'], cwd=d,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                       timeout=7200, check=False)
    except subprocess.TimeoutExpired:
        return name, gas, mode, None, None, None, 'timeout'
    outs = glob.glob(os.path.join(d, 'Output', 'System_0', '*.data'))
    if not outs:
        return name, gas, mode, None, None, None, 'no-output'
    kh, u, load = parse(outs[0])
    for sub in ('VTK', 'Movies', 'Restart'):
        shutil.rmtree(os.path.join(d, sub), ignore_errors=True)
    return name, gas, mode, kh, u, load, 'ok'


def _star(a):
    return run_one(a)


def main():
    os.makedirs(RUNS, exist_ok=True)
    cifs = sorted(glob.glob(os.path.join(STRUCT, '*_DDEC6.cif')))
    jobs = ([(c, g, 'widom') for c in cifs for g in ('CO2', 'N2')]
            + [(c, 'CO2', 'gcmc') for c in cifs])
    print(f'구조 {len(cifs)}개 -> 작업 {len(jobs)}개 (Widom CO2/N2 + 0.15bar GCMC)\n', flush=True)

    res = {}
    with ProcessPoolExecutor(max_workers=7) as ex:
        for name, gas, mode, kh, u, load, st in ex.map(_star, jobs):
            res.setdefault(name, {})[(mode, gas)] = (kh, u, load)
            print(f'  [{st:>9}] {mode:<5} {gas:<3} {name}', flush=True)

    print('\n' + '=' * 104)
    print(f'{"구조":<26} {"KH(CO2)":>11} {"KH(N2)":>11} {"CO2/N2":>8} '
          f'{"Qst":>8} {"0.15bar 로딩":>13}')
    print('-' * 104)
    rows = []
    for name in sorted(res):
        kc = res[name].get(('widom', 'CO2'), (None,) * 3)
        kn = res[name].get(('widom', 'N2'), (None,) * 3)
        gc = res[name].get(('gcmc', 'CO2'), (None,) * 3)
        sel = (kc[0] / kn[0]) if (kc[0] and kn[0]) else float('nan')
        qst = (-kc[1] + R_GAS * TEMP) if kc[1] is not None else float('nan')
        load = gc[2] if gc[2] is not None else float('nan')
        print(f'{name.replace("_DDEC6",""):<26} {kc[0] or float("nan"):>11.4e} '
              f'{kn[0] or float("nan"):>11.4e} {sel:>8.2f} {qst:>8.2f} {load:>13.4f}')
        rows.append({'name': name.replace('_DDEC6', ''), 'KH_CO2': kc[0],
                     'KH_N2': kn[0], 'selectivity': sel, 'Qst_CO2': qst,
                     'loading_015bar': load})
    with open(os.path.join(HERE, 'ddec6_results.json'), 'w', encoding='utf-8') as f:
        json.dump(rows, f, indent=2)
    print(f'\n[OK] 저장: ddec6_results.json')
    return 0


if __name__ == '__main__':
    sys.exit(main())
