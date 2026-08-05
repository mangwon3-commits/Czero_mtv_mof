"""아릴 치환 계열(−NO₂/−CH₃/−Br) 9종의 Widom CO₂·N₂ + 0.15 bar GCMC.

[이 계산이 답하려는 것]
    −SO₃H 100% 가 Q_st 31.07 ± 0.72 로 목표대(30~40)에 들어갔다. 그런데 −SO₃H 는
    부피가 커서 접근가능부피를 25%→50% 구간에서 810.8 → 243.0 Å³ 로 무너뜨린다.
    작용기를 더 작은 것으로 바꾸면 같은 Q_st 를 덜 잃고 얻을 수 있는가 —
    그게 이 계열의 질문이다. 치환기 셋은 성질이 서로 다르게 갈리도록 골랐다.

        −NO₂ (ZIF-78) : 강한 사중극자, 공명 전하 분리. 정전기 쪽 극단.
        −Br  (ZIF-81) : 큰 분극률, 약한 극성. 분산력 쪽 극단.
        −CH₃ (ZIF-79) : 무극성 부피 채움. 순수 대조군.

    셋 다 같은 자리(벤조 b2)에 같은 방식으로 붙으므로 비교가 성립한다.

[−CH₃ 는 25% 만 있다]
    50/75/100% 는 원자 겹침 6/12/27 개로 감사에서 탈락했다. 대조군이 한 점밖에
    없으므로 −CH₃ 로는 '조성 의존성'을 말할 수 없고, 25% 한 점의 값만 −NO₂/−Br 의
    25% 와 나란히 놓고 읽어야 한다. 결론 문장에 이 제약을 반드시 같이 적을 것.

[사이클은 −SO₃H 계열과 같은 15000]
    조성끼리 순위를 매기려면 오차가 차이보다 작아야 한다. 5000 사이클에서는
    −SO₃H 로딩 상대오차가 8.6~11% 로 순위가 무의미했다(18_PoreNarrowing). 같은
    잣대로 비교하려면 사이클도 같아야 한다 — 여기서 줄이면 zif69_results.json 과
    나란히 놓을 수 없게 된다.
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
RUNS = os.path.join(HERE, 'aryl_runs')

SIMULATE = shutil.which('simulate') or os.path.expanduser(
    '~/miniconda3/envs/czeromof/bin/simulate')

TEMP = 298.0
CUTOFF = 12.0
R_GAS = 8.314462618e-3
PRESSURE = 0.15e5
WIDOM_CYCLES, WIDOM_INIT = 15000, 3000
GCMC_CYCLES, GCMC_INIT = 15000, 5000
# 물리 코어 8개. RASPA 한 프로세스가 코어 하나를 통째로 쓰므로 그 이상은
# 문맥 전환만 늘린다(메모리는 프로세스당 471 MB 로 병목이 아니다 — 측정값).
MAX_WORKERS = 8


def unit_cells(atoms, cutoff=CUTOFF):
    """ZIF-69 는 육방정계(gamma=120°)라 격자상수 나누기로는 최소거리규약이 깨진다.
    수직 폭 기준으로 반복수를 정한다."""
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

    # 끝난 실행은 재사용한다. 8시간짜리 묶음이라 중간에 끊기면 처음부터가 아깝다.
    done = glob.glob(os.path.join(d, 'Output', 'System_0', '*.data'))
    if done:
        r = parse(done[0])
        if any(x is not None for x in r):
            return name, gas, mode, r, 'cached'

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
    ch = json.load(open(os.path.join(HERE, 'aryl_charged.json'), encoding='utf-8'))
    tags = ch['charged']
    idx = {r['tag']: r for r in
           json.load(open(os.path.join(HERE, 'aryl_scan_index.json'), encoding='utf-8'))}

    cifs = []
    for t in tags:
        p = os.path.join(CHARGED, t + '_DDEC6.cif')
        if os.path.exists(p):
            cifs.append(p)
        else:
            print(f'  [전하파일 없음] {t} — charge_aryl.py 를 먼저 도세요')
    if not cifs:
        return 1

    jobs = ([(c, g, 'widom') for c in cifs for g in ('CO2', 'N2')]
            + [(c, 'CO2', 'gcmc') for c in cifs])
    print(f'구조 {len(cifs)}종 x (Widom CO2 + Widom N2 + GCMC) = {len(jobs)}작업',
          flush=True)
    print(f'0.15 bar, 298 K, {GCMC_CYCLES} 사이클, UFF_MOF, DDEC6 전하\n', flush=True)

    os.makedirs(RUNS, exist_ok=True)
    res = {}
    with ProcessPoolExecutor(max_workers=MAX_WORKERS) as ex:
        for name, gas, mode, r, st in ex.map(_star, jobs):
            res.setdefault(name, {})[(mode, gas)] = r
            print(f'  [{st:>9}] {mode:<5} {gas:<3} {name}', flush=True)

    print('\n' + '=' * 122)
    print(f'{"조성":<12} {"작용기":<6} {"LCD":>7} {"PLD":>7} {"AV":>8} '
          f'{"Qst (kJ/mol)":>17} {"CO2/N2":>16} {"0.15bar 로딩":>19}')
    print('-' * 122)
    rows = []
    for name in sorted(res):
        tag = name.replace('_DDEC6', '')
        kc = res[name].get(('widom', 'CO2'))
        kn = res[name].get(('widom', 'N2'))
        gc = res[name].get(('gcmc', 'CO2'))
        if not (kc and kn and gc) or kc[0] is None or kn[0] is None or gc[4] is None:
            print(f'{tag:<12} 출력 부족')
            continue
        qst, eqst = -kc[2] - R_GAS * TEMP, kc[3]
        sel = kc[0] / kn[0]
        esel = sel * np.sqrt((kc[1] / kc[0]) ** 2 + (kn[1] / kn[0]) ** 2)
        g = idx.get(tag, {})
        print(f'{tag:<12} {g.get("group",""):<6} {g.get("LCD", float("nan")):>7.3f} '
              f'{g.get("PLD", float("nan")):>7.3f} {g.get("AV", float("nan")):>8.1f} '
              f'{qst:>10.2f} ± {eqst:<4.2f} {sel:>9.2f} ± {esel:<4.2f} '
              f'{gc[4]:>11.4f} ± {gc[5]:<6.4f}')
        rows.append({'name': tag, 'group': g.get('group'), 'frac': g.get('frac'),
                     'LCD': g.get('LCD'), 'PLD': g.get('PLD'), 'AV': g.get('AV'),
                     'KH_CO2': kc[0], 'KH_CO2_err': kc[1],
                     'KH_N2': kn[0], 'KH_N2_err': kn[1],
                     'selectivity': sel, 'selectivity_err': esel,
                     'Qst_CO2': qst, 'Qst_CO2_err': eqst,
                     'loading_015bar': gc[4], 'loading_015bar_err': gc[5]})
    with open(os.path.join(HERE, 'aryl_results.json'), 'w', encoding='utf-8') as f:
        json.dump(rows, f, indent=2, ensure_ascii=False)
    print('\n[OK] aryl_results.json')
    print('비교 기준: −SO₃H 100% = Qst 31.07 ± 0.72, 선택도 102.22 ± 9.92, '
          '로딩 2.1556 ± 0.0352')
    print('차이가 1.5σ 미만이면 순위를 매기지 마세요.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
