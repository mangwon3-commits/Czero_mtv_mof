"""ZIF-69 −SO₃H 계열의 CO₂ 밀도맵 — 왜 Q_st 31.07 이 나오는지 공간으로 본다.

[왜 필요한가]
    숫자는 "얼마나 강한가"만 말하고 "어디서, 왜"를 말하지 않는다. ZIF-69 + SO₃H
    100% 가 Q_st 31.07, 선택도 102 를 냈는데, 그게
      (a) 공동이 좁아져 분산력이 커진 것인지,
      (b) 술폰산기가 정전기로 CO₂ 를 끌어당긴 것인지
    구별이 안 된다. 치환율을 올리면 둘이 **동시에** 일어나기 때문이다.

[전하 ON/OFF 차분이 그걸 가른다 — 10_DensityMap/README.md 1절]
    같은 구조를 전하만 켜고 끄고 두 번 돌린 뒤, 각각 총합 1 로 정규화해 뺀다.

        Δρ(r) = ρ_on(r) − ρ_off(r)

    Lennard-Jones 항은 전하와 무관하므로 차분에서 **완전히 소거**된다. 남는 것은
    "정전기가 CO₂ 를 어디로 옮겼는가" 뿐이다.
      양수 등고면 = 정전기가 새로 끌어들인 자리
      음수 등고면 = 정전기 때문에 빠져나간 자리
    실험으로는 분리할 수 없고 계산에서만 되는 양이다.

    **전하 끈 계산을 중복이라고 지우지 마세요.** 그게 이 계산의 전부입니다.

[ZIF-8 계열과 다른 점]
    07_Bracketed_MTV 는 닫힌상/열린상 쌍이 있었지만(ZIF-8 게이트 오프닝), ZIF-69 는
    gme 강체 골격이라 상이 하나다. 따라서 축은 **조성 × 전하 ON/OFF** 두 개뿐이다.

[전하는 DDEC6 를 쓴다]
    charged/ 의 PACMAN 결과를 읽는다. structures/ 에는 빌더가 써 넣은 EQeq 전하가
    있는데, EQeq 는 공명에 의한 전하 분리를 못 다뤄 폐기한 방법이고 −SO₃H 는
    S=O 공명을 갖는다. "왜 술폰산이 강한가"를 보려는 계산에서 가장 쓰면 안 된다.
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
CHARGED = os.path.join(HERE, 'charged')
OUT = os.path.join(HERE, 'density')

SIMULATE = shutil.which('simulate') or os.path.expanduser(
    '~/miniconda3/envs/czeromof/bin/simulate')

TEMP = 298.0
CUTOFF = 12.0
PRESSURE = 0.15e5
CYCLES, INIT = 5000, 2000
GRID = 90
# RASPA 는 471 MB/프로세스 정도만 쓰지만(측정값), 밀도 격자를 켜면 출력이 커진다.
# 물리 코어가 8개라 그 이상은 문맥 전환만 늘어난다.
MAX_WORKERS = 8

# 조성 축. base(무치환) 는 "작용기 없이 골격만"의 기준선이라 반드시 포함한다.
TARGETS = ['base', 'saIm025', 'saIm050', 'saIm075', 'saIm100']


def unit_cells(atoms, cutoff=CUTOFF):
    cell = atoms.get_cell()
    vol = abs(np.linalg.det(cell))
    reps = []
    for i in range(3):
        j, k = (i + 1) % 3, (i + 2) % 3
        width = vol / np.linalg.norm(np.cross(cell[j], cell[k]))
        reps.append(max(1, int(np.ceil(2.0 * cutoff / width))))
    return reps


def write_input(d, name, na, nb, nc, charges):
    """charges=False 로 도는 쪽이 차분의 기준선이다. 이게 없으면 LJ 를 못 뺀다."""
    with open(os.path.join(d, 'simulation.input'), 'w') as f:
        f.write(f"""SimulationType                MonteCarlo
NumberOfCycles                {CYCLES}
NumberOfInitializationCycles  {INIT}
PrintEvery                    {CYCLES}
RestartFile                   no

Forcefield                    UFF_MOF
CutOff                        {CUTOFF}
UseChargesFromCIFFile         {'yes' if charges else 'no'}
ChargeMethod                  Ewald
EwaldPrecision                1e-6

ComputeDensityProfile3DVTKGrid    yes
WriteDensityProfile3DVTKGridEvery 500
DensityProfile3DVTKGridPoints     {GRID} {GRID} {GRID}

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


def loading_from(path):
    for line in open(path, encoding='utf-8', errors='ignore'):
        if 'Average loading absolute [mol/kg framework]' in line:
            m = re.search(r':?\s*([0-9.eE+-]+)\s*\+/-\s*([0-9.eE+-]+)', line)
            if m:
                return float(m.group(1)), float(m.group(2))
    return None, None


def run_one(job):
    tag, charges = job
    name = tag + '_DDEC6'
    label = 'q_on' if charges else 'q_off'
    d = os.path.join(OUT, f'{tag}__{label}')

    # 이미 끝난 실행은 재사용한다. 밀도 격자가 남아 있어야 하므로 VTK 존재도 본다.
    done = glob.glob(os.path.join(d, 'Output', 'System_0', '*.data'))
    vtk = glob.glob(os.path.join(d, 'VTK', 'System_0', '*DensityProfile*'))
    if done and vtk:
        v, e = loading_from(done[0])
        if v is not None:
            return tag, label, v, e, 'cached'

    os.makedirs(d, exist_ok=True)
    src = os.path.join(CHARGED, name + '.cif')
    if not os.path.exists(src):
        return tag, label, None, None, 'cif 없음'
    shutil.copy(src, os.path.join(d, name + '.cif'))
    na, nb, nc = unit_cells(read(src))
    write_input(d, name, na, nb, nc, charges)
    try:
        subprocess.run([SIMULATE, 'simulation.input'], cwd=d,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                       timeout=28800, check=False)
    except subprocess.TimeoutExpired:
        return tag, label, None, None, 'timeout'
    outs = glob.glob(os.path.join(d, 'Output', 'System_0', '*.data'))
    if not outs:
        return tag, label, None, None, '출력 없음'
    v, e = loading_from(outs[0])
    # VTK 는 **지우지 않는다.** 이 계산의 산출물이다.
    for sub in ('Movies', 'Restart'):
        shutil.rmtree(os.path.join(d, sub), ignore_errors=True)
    n_vtk = len(glob.glob(os.path.join(d, 'VTK', 'System_0', '*DensityProfile*')))
    return tag, label, v, e, f'ok (밀도격자 {n_vtk}개)'


def _star(a):
    return run_one(a)


def main():
    missing = [t for t in TARGETS
               if not os.path.exists(os.path.join(CHARGED, t + '_DDEC6.cif'))]
    if missing:
        print('전하 구조 없음:', missing)
        return 1
    os.makedirs(OUT, exist_ok=True)

    jobs = [(t, c) for t in TARGETS for c in (True, False)]
    print(f'조성 {len(TARGETS)}개 x 전하 ON/OFF = {len(jobs)}작업', flush=True)
    print(f'0.15 bar, 298 K, {CYCLES} 사이클, 격자 {GRID}^3, DDEC6 전하\n', flush=True)

    res = {}
    with ProcessPoolExecutor(max_workers=MAX_WORKERS) as ex:
        for tag, label, v, e, st in ex.map(_star, jobs):
            res.setdefault(tag, {})[label] = (v, e)
            vs = f'{v:.4f}' if v is not None else '-'
            print(f'  [{st:>22}] {label:<5} {tag:<9} 로딩 {vs}', flush=True)

    print('\n' + '=' * 78)
    print(f'{"조성":<10} {"전하 ON":>18} {"전하 OFF":>18} {"정전기 기여":>14}')
    print('-' * 78)
    rows = []
    for t in TARGETS:
        on = res.get(t, {}).get('q_on', (None, None))
        off = res.get(t, {}).get('q_off', (None, None))
        if on[0] is None or off[0] is None:
            print(f'{t:<10} 출력 부족')
            continue
        frac = (on[0] - off[0]) / on[0] * 100 if on[0] else float('nan')
        print(f'{t:<10} {on[0]:>11.4f} ± {on[1]:<4.4f} {off[0]:>11.4f} ± {off[1]:<4.4f} '
              f'{frac:>13.1f}%')
        rows.append({'name': t, 'loading_q_on': on[0], 'loading_q_on_err': on[1],
                     'loading_q_off': off[0], 'loading_q_off_err': off[1],
                     'electrostatic_fraction_pct': frac})
    with open(os.path.join(HERE, 'density_results.json'), 'w', encoding='utf-8') as f:
        json.dump(rows, f, indent=2, ensure_ascii=False)
    print('\n[OK] density_results.json')
    print('\n다음: export_diff_vtk.py 로 ParaView 용 차분맵을 뽑습니다.')
    print('     양수 등고면 = 정전기가 끌어들인 자리, 음수 = 밀려난 자리.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
