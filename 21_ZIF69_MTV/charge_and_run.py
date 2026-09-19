"""ZIF-69 아릴 자리에 −SO₃H를 넣어 '좁은 공동 + 작용기' 조합을 시험한다.

[왜 ZIF-69인가]
    Part 4의 결론은 분산력과 정전기가 같은 부피를 놓고 경쟁한다는 것이었다.
    ZIF-7(공동 4.3 Å)은 작용기 없이 Q_st 34가 예측되지만 −SO₃H(2.8 Å)를 붙일
    자리가 없고, ZIF-8(11.4 Å)은 자리는 있지만 sod 위상에서 C2 치환기가 창구를
    향해 치환해도 공동이 안 줄어든다(Part 2, 실측 반증).

    ZIF-69는 그 사이다. 실측으로 아릴 치환이 LCD를 8.76 → 7.13 Å 까지 줄이면서
    PLD는 4.24 Å로 열어 둔다(CO₂ 운동직경 3.3 Å보다 여유). 두 메커니즘을 동시에
    걸 수 있는 유일한 모체이므로 여기서 시험한다.

[주의 — 구조 생성 단계에서 이미 보인 경고]
    접근가능부피가 SO₃H 25%의 810.8 Å³에서 50%의 243.0 Å³으로 70% 무너진다.
    LCD(7.73→7.68)와 PLD(4.38→4.24)는 거의 안 변하는데도 그렇다. 부피 큰
    술폰산기가 공동 자체를 메우고 있다는 뜻이다. 로딩을 반드시 함께 봐야 한다.

[사이클]
    18_PoreNarrowing은 5000 사이클이었는데, 그 결과의 −SO₃H 조성 로딩 상대오차가
    8.6~11.0%로 조성끼리 순위를 매길 수 없었다. 강한 흡착점이 있으면 삽입 수용률이
    떨어져 수렴이 느리기 때문이다. 여기서는 그 교훈을 반영해 3배로 늘린다.
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
BASE_SRC = os.path.join(HERE, '..', '05_MTV_Ligand_Library', 'ZIF69_base.cif')

# PACMAN은 coremof_tools 환경에만, simulate는 czeromof 환경에만 있다(MIGRATION.md 3-1).
SIMULATE = shutil.which('simulate') or os.path.expanduser(
    '~/miniconda3/envs/czeromof/bin/simulate')

TEMP = 298.0
CUTOFF = 12.0
R_GAS = 8.314462618e-3
PRESSURE = 0.15e5
# 18_PoreNarrowing(5000) 대비 3배. 위 [사이클] 주석 참조.
WIDOM_CYCLES, WIDOM_INIT = 15000, 3000
GCMC_CYCLES, GCMC_INIT = 15000, 5000
MAX_WORKERS = 12


def unit_cells(atoms, cutoff=CUTOFF):
    """비직교 셀에서도 안전하도록 '수직 폭' 기준으로 반복수를 정한다.
    ZIF-69는 육방정계(gamma=120°)라 격자상수 나누기로는 최소거리규약이 깨진다."""
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
    """PACMAN(DDEC6). 입력 CIF를 덮어쓰므로 반드시 사본에서 작업한다."""
    os.makedirs(CHARGED, exist_ok=True)
    done = [os.path.join(CHARGED, n + '_DDEC6.cif') for n in names]
    if all(os.path.exists(p) for p in done):
        print(f'  전하 파일 {len(done)}개 이미 존재 -> PACMAN 건너뜀', flush=True)
        return done

    from PACMANCharge import pmcharge
    out = []
    for n in names:
        final = os.path.join(CHARGED, n + '_DDEC6.cif')
        if os.path.exists(final):
            out.append(final)
            continue
        # 구조 파일은 ZIF69_<태그>.cif 로 저장돼 있고 인덱스에는 태그만 들어 있다.
        src = BASE_SRC if n == 'base' else os.path.join(STRUCT, f'ZIF69_{n}.cif')
        if not os.path.exists(src):
            print(f'  [구조없음] {src}', flush=True)
            continue
        work = os.path.join(CHARGED, n + '.cif')
        shutil.copy(src, work)
        try:
            pmcharge.predict(cif_file=work, charge_type='DDEC6', digits=6,
                             atom_type=True, neutral=True, keep_connect=False)
        except Exception as e:
            print(f'  [전하실패] {n}: {type(e).__name__}: {e}', flush=True)
            continue
        pac = work.replace('.cif', '_pacman.cif')
        if not os.path.exists(pac):
            print(f'  [전하없음] {n}', flush=True)
            continue
        shutil.move(pac, final)
        t = open(final, encoding='utf-8').read()
        t = re.sub(r'^data_\S+', f'data_{n}_DDEC6', t, count=1, flags=re.M)
        open(final, 'w', encoding='utf-8').write(t)
        fix_tags(final)
        os.path.exists(work) and os.remove(work)
        out.append(final)
        print(f'  [ok] {n}', flush=True)
    return out


def parse(path):
    kh = u = load = None
    ekh = eu = eload = None
    for line in open(path, encoding='utf-8', errors='ignore'):
        if 'Average Henry coefficient:' in line:
            m = re.search(r':\s*([0-9.eE+-]+)\s*\+/-\s*([0-9.eE+-]+)', line)
            if m:
                kh, ekh = float(m.group(1)), float(m.group(2))
        if '<U_gh>_1-<U_h>_0:' in line:
            m = re.search(r'\(\s*([0-9.eE+-]+)\s*\+/-\s*([0-9.eE+-]+)', line)
            if m:
                u, eu = float(m.group(1)), float(m.group(2))
        if 'Average loading absolute [mol/kg framework]' in line:
            m = re.search(r':?\s*([0-9.eE+-]+)\s*\+/-\s*([0-9.eE+-]+)', line)
            if m:
                load, eload = float(m.group(1)), float(m.group(2))
    return kh, ekh, u, eu, load, eload


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
ChargeMethod                  Ewald
EwaldPrecision                1e-6

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
                       timeout=28800, check=False)
    except subprocess.TimeoutExpired:
        return name, gas, mode, None, 'timeout'
    outs = glob.glob(os.path.join(d, 'Output', 'System_0', '*.data'))
    if not outs:
        return name, gas, mode, None, 'no-output'
    res = parse(outs[0])
    for sub in ('VTK', 'Movies', 'Restart'):
        shutil.rmtree(os.path.join(d, sub), ignore_errors=True)
    return name, gas, mode, res, 'ok'


def _star(a):
    return run_one(a)


def main():
    idx = json.load(open(os.path.join(HERE, 'build_index.json'), encoding='utf-8'))
    names = [r['tag'] for r in idx]
    geo = {r['tag']: r for r in idx}
    print(f'구조 {len(names)}개 -> DDEC6 전하\n', flush=True)
    cifs = make_charges(names)
    if not cifs:
        print('전하 계산 실패')
        return 1

    jobs = ([(c, g, 'widom') for c in cifs for g in ('CO2', 'N2')]
            + [(c, 'CO2', 'gcmc') for c in cifs])
    print(f'\n작업 {len(jobs)}개 (Widom CO2/N2 + 0.15bar GCMC, {GCMC_CYCLES} 사이클)\n',
          flush=True)
    os.makedirs(RUNS, exist_ok=True)
    res = {}
    with ProcessPoolExecutor(max_workers=MAX_WORKERS) as ex:
        for name, gas, mode, r, st in ex.map(_star, jobs):
            res.setdefault(name, {})[(mode, gas)] = r
            print(f'  [{st:>9}] {mode:<5} {gas:<3} {name}', flush=True)

    print('\n' + '=' * 118)
    print(f'{"조성":<22} {"LCD":>7} {"PLD":>7} {"AV":>8} '
          f'{"Qst":>16} {"CO2/N2":>16} {"0.15bar 로딩":>18}')
    print('-' * 118)
    rows = []
    for name in sorted(res):
        base = name.replace('_DDEC6', '')
        kc = res[name].get(('widom', 'CO2'))
        kn = res[name].get(('widom', 'N2'))
        gc = res[name].get(('gcmc', 'CO2'))
        if not (kc and kn and gc):
            print(f'{base:<22} 출력 부족')
            continue
        qst = -kc[2] + R_GAS * TEMP  # Q_st = −ΔU + RT (RASPA dH 정의; 09-18 부호 정정, 21_ZIF69_MTV/QST_RT_SIGN_20260911.md)
        eqst = kc[3]
        sel = kc[0] / kn[0]
        esel = sel * np.sqrt((kc[1] / kc[0]) ** 2 + (kn[1] / kn[0]) ** 2)
        load, eload = gc[4], gc[5]
        g = geo.get(base, {})
        print(f'{base:<22} {g.get("lcd", float("nan")):>7.3f} '
              f'{g.get("pld", float("nan")):>7.3f} {g.get("av", float("nan")):>8.1f} '
              f'{qst:>9.2f} ± {eqst:<4.2f} {sel:>9.2f} ± {esel:<4.2f} '
              f'{load:>10.4f} ± {eload:<6.4f}')
        rows.append({'name': base, 'LCD': g.get('lcd'), 'PLD': g.get('pld'),
                     'AV': g.get('av'), 'frac_saIm': g.get('frac'),
                     'KH_CO2': kc[0], 'KH_CO2_err': kc[1],
                     'KH_N2': kn[0], 'KH_N2_err': kn[1],
                     'selectivity': sel, 'selectivity_err': esel,
                     'Qst_CO2': qst, 'Qst_CO2_err': eqst,
                     'loading_015bar': load, 'loading_015bar_err': eload})
    with open(os.path.join(HERE, 'zif69_results.json'), 'w', encoding='utf-8') as f:
        json.dump(rows, f, indent=2, ensure_ascii=False)
    print('\n[OK] zif69_results.json')
    return 0


if __name__ == '__main__':
    sys.exit(main())
