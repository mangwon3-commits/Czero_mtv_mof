"""습윤 작업 용량 — 물이 있는 상태에서 실제로 얼마나 실어 나르는가.

[왜 이 계산이 필요한가]
    working_capacity.json 은 **건조 조건**의 작업 용량이다. 그런데 saIm075 의
    RH90 유지율은 64.8% 로 "조건부" 구간에 있고, 조건부라는 말은 **전처리 건조
    비용이 결정한다**는 뜻이었다. 그 비용을 따지려면 먼저 두 선택지를 같은
    잣대로 재야 한다.

        A안  젖은 채로 돌린다     -> 습윤 작업 용량 (이 계산)
        B안  말려서 돌린다       -> 건조 작업 용량 (이미 있음) - 건조 에너지

    A안의 값이 없으면 비교 자체가 성립하지 않는다. 지금까지 습윤 조건에서는
    **흡착 다리만** 쟀고 탈착 다리를 안 쟀다.

[핵심 물리 - 물 분압을 고정한다]
    실제 공정에서 기체 흐름의 **물 함량은 변하지 않는다.** 바뀌는 것은 온도와
    CO2 분압뿐이다. 그래서 세 조건 모두 물 분압을 RH90 @ 298 K 값
    (0.90 x 3169 = 2852.1 Pa) 으로 **고정**한다.

    그러면 저절로 따라오는 결과가 하나 있다. 373 K 에서 물의 포화증기압은
    101325 Pa 이므로, 같은 물 분압이 **RH 2.8%** 가 된다.

        ads   298 K, CO2 0.15 bar, H2O 2852 Pa  ->  RH 90%
        tsa   373 K, CO2 0.15 bar, H2O 2852 Pa  ->  RH 2.8%
        vsa   298 K, CO2 0.05 bar, H2O 2852 Pa  ->  RH 90%

    **즉 TSA 재생 단계는 그 자체로 흡착제를 말립니다.** 온도를 올리는 것만으로
    RH 가 90 -> 2.8% 로 떨어지므로, 물을 따로 뺄 필요가 있는지 자체가 이 계산의
    질문이 된다. VSA 는 온도가 그대로라 RH 90% 가 유지되고, 물이 계속 자리를
    차지한 채로 CO2 만 빠져나가야 한다.

[대상 3종]
    base    무치환 기준선 (물을 거의 안 먹는다: RH90 에서 0.516 mol/kg)
    saIm050 조건부 구간, 유지율 76.6%
    saIm075 조건부 구간, 유지율 64.8% -- 건조 작업 용량 1위

    saIm100 은 수분 종료 판정이므로 제외한다. saIm025 는 유지율 92.1% 로 이미
    "유효" 판정이라 건조가 필요 없다 -- 건조 비용 논의의 대상이 아니다.
"""
import glob
import json
import os
import shutil
import subprocess
import sys
from concurrent.futures import ProcessPoolExecutor

from ase.io import read

import run_aryl_gcmc as rg
import run_water as rw

HERE = os.path.dirname(os.path.abspath(__file__))
CHARGED = os.path.join(HERE, 'charged')
RUNS = os.path.join(HERE, 'humid_wc_runs')
RESULT = os.path.join(HERE, 'humid_working_capacity.json')

CYCLES, INIT = 15000, 5000
MAX_WORKERS = int(os.environ.get('HWC_WORKERS', '8'))

P_SAT_298 = 3169.0
P_SAT_373 = 101325.0
P_H2O = 0.90 * P_SAT_298          # 2852.1 Pa -- 세 조건 공통

TARGETS = ['base', 'saIm050', 'saIm075']

# (라벨, CO2 분압 Pa, 온도 K, 그 온도에서의 포화증기압)
CONDITIONS = [
    ('ads', 0.15e5, 298.0, P_SAT_298),
    ('tsa', 0.15e5, 373.0, P_SAT_373),
    ('vsa', 0.05e5, 298.0, P_SAT_298),
]


def run_one(job):
    tag, label, p_co2, temp, p_sat = job
    cif = os.path.join(CHARGED, f'{tag}_DDEC6.cif')
    if not os.path.exists(cif):
        hits = glob.glob(os.path.join(CHARGED, f'*{tag}*.cif'))
        if not hits:
            return tag, label, None, 'CIF 없음'
        cif = hits[0]
    name = os.path.basename(cif).replace('.cif', '')
    d = os.path.join(RUNS, f'{label}_{tag}')

    done = glob.glob(os.path.join(d, 'Output', 'System_0', '*.data'))
    if done and rw.net_charge_ok(done[0]):
        r = rw.parse_components(done[0])
        if 'CO2' in r:
            return tag, label, r, 'cached'
    if rg.occupied_by_other(d):
        return tag, label, None, '다른세션실행중'

    os.makedirs(d, exist_ok=True)
    shutil.copy(cif, os.path.join(d, name + '.cif'))
    # 5사이트 물 정의. 배포본 3사이트를 쓰면 순전하가 +0.482 가 된다(MIGRATION 3-4).
    shutil.copy(rw.WATER_DEF, os.path.join(d, 'water.def'))
    na, nb, nc = rg.unit_cells(read(cif))

    p_tot = p_co2 + P_H2O
    x_co2, x_h2o = p_co2 / p_tot, P_H2O / p_tot
    moves = ('            TranslationProbability    0.5\n'
             '            RotationProbability       0.3\n'
             '            ReinsertionProbability    0.1\n'
             '            SwapProbability           1.0\n'
             '            CreateNumberOfMolecules   0\n')

    with open(os.path.join(d, 'simulation.input'), 'w') as f:
        f.write(f"""SimulationType                MonteCarlo
NumberOfCycles                {CYCLES}
NumberOfInitializationCycles  {INIT}
PrintEvery                    {CYCLES}
RestartFile                   no
ContinueAfterCrash            yes
WriteBinaryRestartFileEvery   500

Forcefield                    UFF_MOF
CutOff                        {rg.CUTOFF}
UseChargesFromCIFFile         yes
ChargeMethod                  Ewald
EwaldPrecision                1e-6

Framework 0
FrameworkName                 {name}
UnitCells                     {na} {nb} {nc}
ExternalTemperature           {temp}
ExternalPressure              {p_tot:.4f}

Component 0 MoleculeName              CO2
            MoleculeDefinition        TraPPE
            MolFraction               {x_co2:.6f}
{moves}
Component 1 MoleculeName              water
            MoleculeDefinition        TraPPE
            MolFraction               {x_h2o:.6f}
{moves}""")
    try:
        subprocess.run([rg.SIMULATE, 'simulation.input'], cwd=d,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                       timeout=259200, check=False)
    except subprocess.TimeoutExpired:
        print(f'  [시간초과] {label} {tag}', flush=True)
        return tag, label, None, 'timeout'
    outs = glob.glob(os.path.join(d, 'Output', 'System_0', '*.data'))
    if not outs:
        return tag, label, None, 'no-output'
    if not rw.net_charge_ok(outs[0]):
        return tag, label, None, '물 순전하 이상'
    res = rw.parse_components(outs[0])
    for sub in ('VTK', 'Movies', 'Restart'):
        shutil.rmtree(os.path.join(d, sub), ignore_errors=True)
    return tag, label, res, 'ok'


def main():
    jobs = [(t, lab, p, T, ps) for t in TARGETS for lab, p, T, ps in CONDITIONS]
    os.makedirs(RUNS, exist_ok=True)
    print(f'습윤 작업 용량 — 물 분압 {P_H2O:.1f} Pa 고정, 작업 {len(jobs)}개, '
          f'워커 {MAX_WORKERS}', flush=True)
    for lab, p, T, ps in CONDITIONS:
        print(f'  {lab:<4} CO2 {p/1e5:>5.2f} bar  {T:>5.1f} K  '
              f'-> RH {P_H2O/ps*100:>5.1f}%', flush=True)
    print(flush=True)

    res = {}
    with ProcessPoolExecutor(max_workers=MAX_WORKERS) as ex:
        for tag, label, r, st in ex.map(run_one, jobs):
            res[(tag, label)] = r
            c = f'{r["CO2"][0]:.4f}' if (r and 'CO2' in r) else '-'
            w = f'{r["water"][0]:.3f}' if (r and 'water' in r) else '-'
            print(f'  [{st:>16}] {label:<4} {tag:<8} CO2 {c}  물 {w}', flush=True)

    print('\n' + '=' * 100)
    print(f'{"조성":<10}{"흡착 CO2":>18}{"TSA 잔류":>18}{"VSA 잔류":>18}'
          f'{"WC(TSA)":>14}{"WC(VSA)":>14}')
    print('-' * 100)
    rows = []
    for t in TARGETS:
        g = {lab: res.get((t, lab)) for lab, _, _, _ in CONDITIONS}
        row = {'name': t, 'p_h2o_Pa': P_H2O, 'loadings': {}}
        for lab, r in g.items():
            if r:
                row['loadings'][lab] = {
                    'CO2': {'mol_per_kg': r['CO2'][0], 'err': r['CO2'][1]},
                    'water': ({'mol_per_kg': r['water'][0], 'err': r['water'][1]}
                              if 'water' in r else None)}
        cells, wc = [], {}
        a = g['ads']['CO2'] if g['ads'] and 'CO2' in g['ads'] else None
        for lab in ('ads', 'tsa', 'vsa'):
            r = g[lab]
            cells.append(f'{r["CO2"][0]:.4f}±{r["CO2"][1]:.4f}'
                         if (r and 'CO2' in r) else '실패')
        for lab in ('tsa', 'vsa'):
            r = g[lab]
            if a and r and 'CO2' in r:
                v = a[0] - r['CO2'][0]
                e = (a[1] ** 2 + r['CO2'][1] ** 2) ** 0.5
                wc[lab] = {'value': round(v, 4), 'err': round(e, 4)}
                cells.append(f'{v:.4f}±{e:.4f}')
            else:
                cells.append('-')
        row['working_capacity'] = wc
        print(f'{t:<10}' + ''.join(f'{c:>18}' if i < 3 else f'{c:>14}'
                                   for i, c in enumerate(cells)))
        rows.append(row)

    with open(RESULT, 'w', encoding='utf-8') as f:
        json.dump({'p_h2o_Pa': P_H2O,
                   'conditions': [{'label': l, 'p_co2_Pa': p, 'T_K': T,
                                   'RH_pct': round(P_H2O / ps * 100, 2)}
                                  for l, p, T, ps in CONDITIONS],
                   'cycles': CYCLES,
                   'note': '물 분압 고정. TSA 는 승온만으로 RH 가 90 -> 2.8% 로 떨어진다.',
                   'rows': rows}, f, indent=2, ensure_ascii=False)
    print(f'\n[OK] {os.path.basename(RESULT)}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
