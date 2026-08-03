"""0.15 bar GCMC로 CO2 밀도맵을 뽑고, 정전기 기여만 분리한 에너지 그리드와 대조한다.

목적:
    "CO2가 정전기 기울기가 큰 영역에 국재하는가"를 검증한다.

방법:
    (1) 0.15 bar, 298 K GCMC + ComputeDensityProfile3DVTKGrid -> 실제 CO2 분포
    (2) 같은 골격에 대해 에너지 그리드를 전하 ON/OFF 두 번 계산
        -> 두 그리드의 차이가 곧 '정전기 기여분'이다.
        (LJ 항은 전하와 무관하므로 차분에서 소거된다)

    Widom 삽입은 분자를 배치하지 않으므로 밀도맵을 만들 수 없어 GCMC가 필요하다.

대상: 순수 ZIF-8(대조군)과 최고 성능 조성을 닫힌/열린 상 모두.
"""
import json
import os
import shutil
import subprocess
import sys

import numpy as np
from ase.io import read

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, '..', '07_Bracketed_MTV')
TEMP = 298.0
PRESSURE = 0.15e5   # 0.15 bar -> Pa (flue gas CO2 분압)
CUTOFF = 12.0
CYCLES = 5000
INIT = 2000

TARGETS = [
    'mIm100__closed', 'mIm100__open',                      # 대조군 (순수 ZIF-8)
    'clIm050_mIm050__closed', 'clIm050_mIm050__open',      # Widom 최고 선택도
    # EWG 종류별 정전기 효율 비교
    'mIm050_nIm050__closed', 'mIm050_nIm050__open',        # NO2 50%
    'mIm075_nIm025__closed', 'mIm075_nIm025__open',        # NO2 25%
    'clIm025_mIm075__closed', 'clIm025_mIm075__open',      # Cl 25%
    'cnIm025_mIm075__closed', 'cnIm025_mIm075__open',      # CN 25%
    'clIm025_mIm050_nIm025__closed', 'clIm025_mIm050_nIm025__open',  # 3원
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


def write_input(d, name, na, nb, nc, charges, density_grid):
    """charges: EQeq 전하 사용 여부. density_grid: 3D 밀도맵 출력 여부."""
    extra = ''
    if density_grid:
        extra = ('ComputeDensityProfile3DVTKGrid yes\n'
                 'WriteDensityProfile3DVTKGridEvery 500\n'
                 'DensityProfile3DVTKGridPoints 90 90 90\n')
    with open(os.path.join(d, 'simulation.input'), 'w') as f:
        f.write(f"""SimulationType                MonteCarlo
NumberOfCycles                {CYCLES}
NumberOfInitializationCycles  {INIT}
PrintEvery                    {CYCLES}
RestartFile                   no

Forcefield                    UFF_MOF
CutOff                        {CUTOFF}
UseChargesFromCIFFile         {'yes' if charges else 'no'}
{extra}
Framework 0
FrameworkName                 {name}
UnitCells                     {na} {nb} {nc}
ExternalTemperature           {TEMP}
ExternalPressure              {PRESSURE}

Component 0 MoleculeName              CO2
            MoleculeDefinition        TraPPE
            TranslationProbability    0.5
            RotationProbability       0.3
            ReinsertionProbability    0.1
            SwapProbability           1.0
            CreateNumberOfMolecules   0
""")


def _loading_from(outfile):
    import re
    load = None
    for line in open(outfile, encoding='utf-8', errors='ignore'):
        if 'Average loading absolute [mol/kg framework]' in line:
            m = re.search(r':?\s*([0-9.eE+-]+)\s*\+/-', line)
            if m:
                load = float(m.group(1))
    return load


def run(name, charges, tag, density_grid):
    import glob as _glob
    src = os.path.join(SRC, name + '.cif')
    d = os.path.join(HERE, f'{name}__{tag}')

    # 이미 끝난 실행은 결과만 재사용 (재실행 비용 회피)
    done = _glob.glob(os.path.join(d, 'Output', 'System_0', '*.data'))
    if done:
        load = _loading_from(done[0])
        if load is not None:
            return name, tag, load, 'cached'

    os.makedirs(d, exist_ok=True)
    shutil.copy(src, os.path.join(d, name + '.cif'))
    na, nb, nc = unit_cells(read(src))
    write_input(d, name, na, nb, nc, charges, density_grid)
    try:
        subprocess.run(['simulate', 'simulation.input'], cwd=d,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                       timeout=7200, check=False)
    except subprocess.TimeoutExpired:
        return name, tag, None, 'timeout'
    import glob
    import re
    outs = glob.glob(os.path.join(d, 'Output', 'System_0', '*.data'))
    if not outs:
        return name, tag, None, 'no-output'
    load = None
    for line in open(outs[0], encoding='utf-8', errors='ignore'):
        if 'Average loading absolute [mol/kg framework]' in line:
            m = re.search(r':?\s*([0-9.eE+-]+)\s*\+/-', line)
            if m:
                load = float(m.group(1))
    return name, tag, load, 'ok'


def _run_star(args):
    """ProcessPoolExecutor는 lambda를 피클할 수 없으므로 모듈 최상위 함수로 둔다."""
    return run(*args)


def main():
    jobs = []
    for t in TARGETS:
        jobs.append((t, True, 'q_on', True))    # 전하 O + 밀도맵
        jobs.append((t, False, 'q_off', True))  # 전하 X + 밀도맵 (차분용)

    from concurrent.futures import ProcessPoolExecutor
    print(f'0.15 bar GCMC, {CYCLES} cycles, 작업 {len(jobs)}개\n', flush=True)
    results = {}
    with ProcessPoolExecutor(max_workers=7) as ex:
        for name, tag, load, status in ex.map(_run_star, jobs):
            results.setdefault(name, {})[tag] = load
            print(f'  [{status:>9}] {name:<32} {tag:<6} '
                  f'loading={load if load is not None else float("nan"):.4f} mol/kg', flush=True)

    # 각 조성을 같은 상(phase)의 순수 ZIF-8과 대비해 입체 비용/정전기 이득/순효과로 분해
    print('\n' + '=' * 96)
    print(f'{"구조":<32} {"전하O":>10} {"전하X":>10} {"정전기":>9} {"입체비용":>10} {"순효과":>9}')
    print('-' * 96)
    rows = []
    for n in TARGETS:
        on = results.get(n, {}).get('q_on')
        off = results.get(n, {}).get('q_off')
        if on is None or off is None:
            continue
        ph = 'open' if n.endswith('__open') else 'closed'
        b_on = results.get(f'mIm100__{ph}', {}).get('q_on')
        b_off = results.get(f'mIm100__{ph}', {}).get('q_off')
        frac = (on - off) / on * 100 if on else float('nan')
        steric = (off / b_off - 1) * 100 if b_off else float('nan')
        net = (on / b_on - 1) * 100 if b_on else float('nan')
        print(f'{n:<32} {on:>10.4f} {off:>10.4f} {frac:>8.1f}% {steric:>9.1f}% {net:>8.1f}%')
        rows.append({'name': n, 'phase': ph, 'q_on': on, 'q_off': off,
                     'electrostatic_pct': round(frac, 1),
                     'steric_pct': round(steric, 1),
                     'net_vs_pristine_pct': round(net, 1)})
    with open(os.path.join(HERE, 'electrostatic_decomposition.json'), 'w',
              encoding='utf-8') as f:
        json.dump(rows, f, indent=2, ensure_ascii=False)
    print('\n전하 ON/OFF 차이가 정전기가 흡착에 기여한 몫이다.')
    print('밀도맵: 각 실행 폴더의 VTK/System_0/DensityProfile*.vtk')


if __name__ == '__main__':
    sys.exit(main())
