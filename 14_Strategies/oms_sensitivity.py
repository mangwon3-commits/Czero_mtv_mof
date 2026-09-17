"""전략 A(OMS)의 제대로 된 평가: OMS 결합 세기 감도 분석.

문제:
    UFF는 Zn을 단순 LJ 구로 다룬다 (CO2와의 우물 깊이 43 K = 0.36 kJ/mol).
    실제 OMS 결합은 금속 d궤도와 CO2 산소 비공유전자쌍 사이의 배위(dative)
    상호작용이라 20~45 kJ/mol인데, 고전 힘장에는 이 항이 없다.
    따라서 앞선 전략 A의 "효과 없음"(Q_st 14.16 vs 순수 14.02)은
    물리적 결론이 아니라 '측정 불가'였다.

접근:
    3배위 Zn만 별도 원자 타입으로 분리하고, 그 자리의 LJ 우물 깊이를
    스캔하면서 평균 Q_st가 어떻게 움직이는지 본다. 이것은 예측이 아니라
    감도 분석이다 -- "OMS가 X만큼 세게 결합한다면 계 전체 Q_st는 얼마가 되는가"에
    답하고, 나아가 (a) OMS가 얼마나 세야 하는지 (b) 셀당 1개로 충분한지를 가린다.

    DFT로 진짜 값을 구하는 것이 정답이지만, 그 전에 '해볼 가치가 있는가'를
    판정하는 것이 이 계산의 목적이다.
"""
import glob
import os
import re
import shutil
import subprocess
import sys

import numpy as np
from ase.io import read
from ase.neighborlist import NeighborList, natural_cutoffs

HERE = os.path.dirname(os.path.abspath(__file__))
FF_DIR = os.path.expanduser('~/RASPA/simulations/share/raspa/forcefield')
SRC = os.path.join(HERE, 'charged', 'StratA_defect_OMS_DDEC6.cif')
WORK = os.path.join(HERE, 'oms_scan')
R_GAS = 8.314462618e-3
TEMP = 298.0
CYCLES, INIT = 6000, 1500

# UFF Zn 기준값. 이 배수만큼 우물을 깊게 해가며 스캔한다.
UFF_ZN_EPS, UFF_ZN_SIG = 62.3992, 2.46155
SCALES = [1, 5, 15, 30, 60, 120]


def find_oms(cif):
    a = read(cif)
    s = a.get_chemical_symbols()
    nl = NeighborList(natural_cutoffs(a, mult=1.15), skin=0.0,
                      self_interaction=False, bothways=True)
    nl.update(a)
    for i, x in enumerate(s):
        if x == 'Zn':
            nb, _ = nl.get_neighbors(i)
            if sum(1 for j in nb if s[j] in ('N', 'O')) == 3:
                return i
    return None


def relabel(src, dst, oms_idx, newlabel='Zoms'):
    """OMS Zn의 _atom_site_label만 별도 이름으로 바꿔 RASPA가 다른 타입으로 보게 한다."""
    lines = open(src, encoding='utf-8').read().split('\n')
    tags = [i for i, l in enumerate(lines) if l.strip().startswith('_atom_site')]
    names = [lines[i].strip() for i in tags]
    li = names.index('_atom_site_label')
    start = tags[-1] + 1
    k = 0
    for i in range(start, len(lines)):
        p = lines[i].split()
        if len(p) <= li:
            continue
        if k == oms_idx:
            p[li] = newlabel
            lines[i] = ' '.join(p)
            break
        k += 1
    open(dst, 'w', encoding='utf-8').write('\n'.join(lines))


def make_ff(name, eps, sig):
    """UFF_MOF를 복사해 Zoms 항목을 추가한 force field를 만든다."""
    d = os.path.join(FF_DIR, name)
    shutil.rmtree(d, ignore_errors=True)
    shutil.copytree(os.path.join(FF_DIR, 'UFF_MOF'), d)
    p = os.path.join(d, 'force_field_mixing_rules.def')
    lines = open(p).read().split('\n')
    # 정의 개수 +1
    for i, l in enumerate(lines):
        if l.strip().isdigit():
            lines[i] = str(int(l.strip()) + 1)
            break
    # 'Zn_' 항목 앞에 삽입 (더 긴 이름이 나중에 덮어쓰지 않도록 순서 무관하게 별도 이름 사용)
    for i, l in enumerate(lines):
        if l.startswith('Zn_'):
            lines.insert(i, f'{"Zoms":<14} lennard-jones {eps:9.4f}   {sig:.5f}      '
                            f'// OMS 감도분석용 (UFF Zn x{eps/UFF_ZN_EPS:.0f})')
            break
    open(p, 'w').write('\n'.join(lines))
    return name


def run(cif, ff, tag):
    d = os.path.join(WORK, tag)
    os.makedirs(d, exist_ok=True)
    nm = os.path.basename(cif).replace('.cif', '')
    shutil.copy(cif, os.path.join(d, nm + '.cif'))
    a = read(cif)
    cell = a.get_cell()
    vol = abs(np.linalg.det(cell))
    reps = []
    for i in range(3):
        j, k = (i + 1) % 3, (i + 2) % 3
        reps.append(max(1, int(np.ceil(24.0 / (vol / np.linalg.norm(np.cross(cell[j], cell[k])))))))
    open(os.path.join(d, 'simulation.input'), 'w').write(f"""SimulationType                MonteCarlo
NumberOfCycles                {CYCLES}
NumberOfInitializationCycles  {INIT}
PrintEvery                    {CYCLES}
RestartFile                   no

Forcefield                    {ff}
CutOff                        12.0
UseChargesFromCIFFile         yes

Framework 0
FrameworkName                 {nm}
UnitCells                     {reps[0]} {reps[1]} {reps[2]}
ExternalTemperature           {TEMP}
ExternalPressure              1e-5

Component 0 MoleculeName              CO2
            MoleculeDefinition        TraPPE
            WidomProbability          1.0
            CreateNumberOfMolecules   0
""")
    subprocess.run(['simulate', 'simulation.input'], cwd=d,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                   timeout=7200, check=False)
    outs = glob.glob(os.path.join(d, 'Output', 'System_0', '*.data'))
    if not outs:
        return None, None
    kh = u = None
    for line in open(outs[0], encoding='utf-8', errors='ignore'):
        if 'Average Henry coefficient:' in line:
            m = re.search(r':\s*([0-9.eE+-]+)', line)
            if m:
                kh = float(m.group(1))
        if '<U_gh>_1-<U_h>_0:' in line:
            m = re.search(r'\(\s*([0-9.eE+-]+)', line)
            if m:
                u = float(m.group(1))
    for s in ('VTK', 'Movies', 'Restart'):
        shutil.rmtree(os.path.join(d, s), ignore_errors=True)
    return kh, (-u + R_GAS * TEMP) if u is not None else None  # Q_st = −ΔU + RT (RASPA dH 정의; 09-18 부호 정정, 21_ZIF69_MTV/QST_RT_SIGN_20260911.md)


def main():
    os.makedirs(WORK, exist_ok=True)
    oms = find_oms(SRC)
    if oms is None:
        print('OMS를 찾지 못했습니다')
        return 1
    print(f'OMS Zn 원자 인덱스 {oms} (3배위) 를 별도 타입 Zoms 로 분리\n')

    tagged = os.path.join(WORK, 'StratA_OMS_tagged.cif')
    relabel(SRC, tagged, oms)

    print(f'{"OMS 세기":>10} {"eps/kB(K)":>11} {"KH(CO2)":>12} {"평균 Qst":>10} '
          f'{"순수대비":>10}')
    print('-' * 60)
    base_q = 14.02   # 순수 ZIF-8 DDEC6 기준
    rows = []
    for sc in SCALES:
        eps = UFF_ZN_EPS * sc
        ff = make_ff(f'UFF_OMS_x{sc}', eps, UFF_ZN_SIG)
        kh, q = run(tagged, ff, f'x{sc}')
        if q is None:
            print(f'{"x"+str(sc):>10} {eps:>11.1f}   계산 실패')
            continue
        print(f'{"x"+str(sc):>10} {eps:>11.1f} {kh:>12.4e} {q:>10.2f} {q-base_q:>+10.2f}')
        rows.append({'scale': sc, 'eps_K': eps, 'KH': kh, 'Qst': q})

    print(f'\n참고: 목표 Q_st 30~36 kJ/mol (15_Target 분석)')
    print(f'      셀당 Zn 12개 중 OMS 1개 -- 나머지 11개는 UFF 기본값 유지')
    import json
    with open(os.path.join(HERE, 'oms_sensitivity.json'), 'w', encoding='utf-8') as f:
        json.dump(rows, f, indent=2)
    return 0


if __name__ == '__main__':
    sys.exit(main())
