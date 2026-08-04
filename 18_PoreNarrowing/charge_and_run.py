"""위험도 검증을 통과한 구조만 DDEC6 전하를 얹고 RASPA로 넘긴다.

risk_screen.py가 세 기준(PLD > 3.3 A, LCD 감소 < 20%, AV 비소멸)을 통과시킨
구조만 대상으로 한다. 탈락 구조에 계산 자원을 쓰지 않는 게 목적이다.

전하는 PACMAN(DDEC6 재현)을 쓴다. EQeq는 공명에 의한 전하 분리를 다루지
못해 -NO2에서 실패한 전력이 있고, -SO3H도 S=O 공명이 있어 같은 위험이 있다.
PACMAN은 입력 CIF를 덮어쓰므로 반드시 사본에서 작업한다.

힘장/사이클은 기존 계산과 동일하게 유지해야 직접 비교가 된다:
    UFF_MOF, 298 K, CutOff 12.0, Widom 5000 cycles / GCMC 5000 cycles
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
STRUCT = os.path.join(HERE, 'structures')
CHARGED = os.path.join(HERE, 'charged')
RUNS = os.path.join(HERE, 'runs')
# PACMAN은 coremof_tools 환경에만, RASPA의 simulate는 czeromof 환경에만 있다.
# 한 환경에서 두 단계를 다 돌리려면 바이너리를 절대경로로 잡아야 한다
# (Zeo++ network 때와 같은 상황).
SIMULATE = shutil.which('simulate') or os.path.expanduser(
    '~/miniconda3/envs/czeromof/bin/simulate')

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


def fix_tags(path):
    t = open(path, encoding='utf-8').read()
    for o, n in (('_space_group_name_H-M_alt', '_symmetry_space_group_name_H-M'),
                 ('_space_group_IT_number', '_symmetry_Int_Tables_number'),
                 ('_space_group_symop_operation_xyz', '_symmetry_equiv_pos_as_xyz')):
        t = t.replace(o, n)
    open(path, 'w', encoding='utf-8').write(t)


def make_charges(names):
    os.makedirs(CHARGED, exist_ok=True)
    # 이미 전하가 붙은 결과가 있으면 건너뛴다. 전하(PACMAN)는 coremof_tools에서,
    # RASPA는 czeromof에서 돌려야 하므로 두 단계를 나눠 실행할 수 있어야 한다.
    done = [os.path.join(CHARGED, n + '_DDEC6.cif') for n in names]
    if all(os.path.exists(p) for p in done):
        print(f'  전하 파일 {len(done)}개 이미 존재 -> PACMAN 건너뜀', flush=True)
        return done

    from PACMANCharge import pmcharge
    out = []
    for n in names:
        src = os.path.join(STRUCT, n + '.cif')
        work = os.path.join(CHARGED, n + '.cif')
        shutil.copy(src, work)          # PACMAN이 입력을 덮어쓰므로 사본에서
        try:
            pmcharge.predict(cif_file=work, charge_type='DDEC6', digits=6,
                             atom_type=True, neutral=True, keep_connect=False)
        except Exception as e:
            print(f'  [전하실패] {n}: {type(e).__name__}: {e}', flush=True)
            continue
        pac = work.replace('.cif', '_pacman.cif')
        final = os.path.join(CHARGED, n + '_DDEC6.cif')
        if not os.path.exists(pac):
            print(f'  [전하없음] {n}', flush=True)
            continue
        shutil.move(pac, final)
        # data_ 블록 이름이 <파일명>_pacman 으로 바뀌므로 RASPA용으로 되돌린다
        t = open(final, encoding='utf-8').read()
        t = re.sub(r'^data_\S+', f'data_{n}_DDEC6', t, count=1, flags=re.M)
        open(final, 'w', encoding='utf-8').write(t)
        fix_tags(final)
        out.append(final)
        print(f'  [ok] {n}', flush=True)
    return out


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
        subprocess.run([SIMULATE, 'simulation.input'], cwd=d,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                       timeout=10800, check=False)
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
    risk = json.load(open(os.path.join(HERE, 'risk_results.json'), encoding='utf-8'))
    passed = [r['name'] for r in risk['rows'] if r.get('pass')]
    if not passed:
        print('통과 구조가 없습니다. 기준을 재검토하거나 조성을 조정해야 합니다.')
        return 1
    print(f'위험도 통과 {len(passed)}개 -> DDEC6 전하 계산\n', flush=True)
    cifs = make_charges(passed)
    if not cifs:
        print('전하 계산 실패')
        return 1

    jobs = ([(c, g, 'widom') for c in cifs for g in ('CO2', 'N2')]
            + [(c, 'CO2', 'gcmc') for c in cifs])
    print(f'\n작업 {len(jobs)}개 (Widom CO2/N2 + 0.15bar GCMC)\n', flush=True)
    os.makedirs(RUNS, exist_ok=True)
    res = {}
    with ProcessPoolExecutor(max_workers=7) as ex:
        for name, gas, mode, kh, u, load, st in ex.map(_star, jobs):
            res.setdefault(name, {})[(mode, gas)] = (kh, u, load)
            print(f'  [{st:>9}] {mode:<5} {gas:<3} {name}', flush=True)

    # 기공 지표를 붙여서 'Qst가 기공 축소를 따라 오르는가'를 직접 본다
    geo = {r['name']: r for r in risk['rows']}
    print('\n' + '=' * 120)
    print(f'{"구조":<28} {"LCD":>7} {"PLD":>7} {"AV/셀":>8} {"KH(CO2)":>11} '
          f'{"CO2/N2":>8} {"Qst":>8} {"0.15bar":>9}')
    print('-' * 120)
    rows = []
    for name in sorted(res):
        base = name.replace('_DDEC6', '')
        kc = res[name].get(('widom', 'CO2'), (None,) * 3)
        kn = res[name].get(('widom', 'N2'), (None,) * 3)
        gc = res[name].get(('gcmc', 'CO2'), (None,) * 3)
        sel = (kc[0] / kn[0]) if (kc[0] and kn[0]) else float('nan')
        qst = (-kc[1] - R_GAS * TEMP) if kc[1] is not None else float('nan')
        load = gc[2] if gc[2] is not None else float('nan')
        g = geo.get(base, {})
        af = (g.get('after') or {})
        lcd, pld = af.get('LCD') or float('nan'), af.get('PLD') or float('nan')
        av = g.get('AV_per_cell') or float('nan')
        print(f'{base:<28} {lcd:>7.2f} {pld:>7.2f} {av:>8.1f} '
              f'{kc[0] or float("nan"):>11.4e} {sel:>8.2f} {qst:>8.2f} {load:>9.4f}')
        rows.append({'name': base, 'label': g.get('label'), 'phase': g.get('phase'),
                     'LCD': lcd, 'PLD': pld, 'AV_per_cell': av,
                     'KH_CO2': kc[0], 'KH_N2': kn[0], 'selectivity': sel,
                     'Qst_CO2': qst, 'loading_015bar': load})
    with open(os.path.join(HERE, 'narrow_results.json'), 'w', encoding='utf-8') as f:
        json.dump(rows, f, indent=2, ensure_ascii=False)
    print('\n[OK] narrow_results.json')
    return 0


if __name__ == '__main__':
    sys.exit(main())
