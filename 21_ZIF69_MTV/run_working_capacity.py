"""작업 용량(working capacity) — 흡착과 탈착의 차이를 잰다.

[이 계산이 답하려는 것]
    지금까지 잰 것은 전부 **흡착 쪽 한 점**(0.15 bar, 298 K)이다. Part 6 이
    "목표대 진입"이라고 쓴 것은 Q_st 가 30~40 에 들어갔다는 뜻이지 성능 주장이
    아니다. 실제로 쓸 수 있는 양은

        작업 용량 = 흡착 조건 로딩 − 탈착(재생) 조건 로딩

    이고, 이것을 재기 전까지는 절반만 본 것이다.

[왜 높은 Q_st 가 불리할 수 있는가 — Atkins §25.3, p. 917]
    흡착되면 흡착질의 병진 자유도가 줄어 ΔS < 0 이다. 따라서 ΔG = ΔH − TΔS 가
    음수이려면 ΔH < 0 여야 한다. **흡착을 일으키는 바로 그 부등식이 탈착을 막는다.**
    ΔH 가 더 음수일수록(= Q_st 가 클수록) 붙잡는 힘은 세지지만 떼어내는 비용도 커진다.

    재생은 그 부등식을 뒤집는 일이다.
        VSA : 압력을 낮춰 기상 화학퍼텐셜 μ 를 내린다
        TSA : 온도를 올려 −TΔS 항이 ΔH 를 이기게 한다
    그래서 목표대의 **상한 40** 은 "놓을 수 있어야 한다"에서 온다.

[조건]
    흡착   0.15 bar / 298 K   (배가스. 기존 값과 교차 검증도 겸한다)
    VSA-1  0.10 bar / 298 K
    VSA-2  0.05 bar / 298 K
    TSA    0.15 bar / 373 K

[대상 4종 — saIm100 은 제외한다]
    saIm100 은 수분 경쟁에서 RH90 유지율 38.1 ± 1.2% 로 **사전 등록한 종료 기준
    (50% 미만)에 걸려 종료 판정**을 받았다.
    [2026-08-20 정정] 위 38.1% 는 v1(깨진 구조)의 값으로 철회됐다. v3 정본은
    60.6 ± 2.0% 이고 3단계 기준상 **조건부**다. 이 파일의 배제는 그 당시
    판정에 따른 역사적 기록으로 남긴다 -- v3 실행(run_wc_v3)은 saIm100 을
    포함했다. 종료된 조성의 작업 용량을 재서
    표에 올리면, 나중에 그 숫자만 떼어 인용될 위험이 있다. 기준을 세워 놓고
    결과가 좋아 보인다고 되살리는 것이 바로 자기합리화다.

[읽는 법]
    1σ 를 병기하고, 차이가 1.5σ 미만이면 순위를 매기지 않는다. 작업 용량은 두
    로딩의 차이이므로 오차가 **더해진다**: σ_wc = sqrt(σ_ads² + σ_des²).
    개별 로딩보다 오차가 크다는 뜻이고, 그래서 순위가 사라질 가능성이 높다.
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

HERE = os.path.dirname(os.path.abspath(__file__))
CHARGED = os.path.join(HERE, 'charged')
RUNS = os.path.join(HERE, 'wc_runs')
RESULT = os.path.join(HERE, 'working_capacity.json')

CYCLES, INIT = 15000, 5000
# RASPA 는 코어당 프로세스 하나이고 한 건에 471 MB 다(실측). 메모리가 아니라
# 물리 코어 8개가 병목이므로 8이 상한이다.
# 참고: risk_screen.py 는 4다 — 거기는 Zeo++ 가 한 건에 3.2 GB 라 성격이 다르다.
MAX_WORKERS = int(os.environ.get('WC_WORKERS', '8'))

TARGETS = ['base', 'saIm025', 'saIm050', 'saIm075']

# (라벨, 압력 Pa, 온도 K)
CONDITIONS = [
    ('ads',   0.15e5, 298.0),
    ('vsa10', 0.10e5, 298.0),
    ('vsa05', 0.05e5, 298.0),
    ('tsa',   0.15e5, 373.0),
]


def find_cif(tag):
    """전하 부여된 CIF 를 찾는다. 이름 규약이 계열마다 조금씩 다르다."""
    pats = [f'{tag}_DDEC6.cif', f'ZIF69_{tag}_DDEC6.cif', f'{tag}.cif']
    for sub in (CHARGED, os.path.join(HERE, 'structures')):
        for p in pats:
            f = os.path.join(sub, p)
            if os.path.exists(f):
                return f
    hits = glob.glob(os.path.join(CHARGED, f'*{tag}*.cif'))
    return hits[0] if hits else None


def run_one(job):
    tag, label, press, temp = job
    cif = find_cif(tag)
    if not cif:
        return tag, label, None, 'CIF 없음'
    name = os.path.basename(cif).replace('.cif', '')
    d = os.path.join(RUNS, f'{label}_{tag}')

    # 작업 단위 이어받기. 죽어도 끝난 것은 다시 돌리지 않는다(MIGRATION 3-8).
    done = glob.glob(os.path.join(d, 'Output', 'System_0', '*.data'))
    if done:
        r = rg.parse(done[0])
        if r[4] is not None:
            return tag, label, r, 'cached'

    if rg.occupied_by_other(d):
        return tag, label, None, '다른세션실행중'

    os.makedirs(d, exist_ok=True)
    shutil.copy(cif, os.path.join(d, name + '.cif'))
    na, nb, nc = rg.unit_cells(read(cif))

    with open(os.path.join(d, 'simulation.input'), 'w') as f:
        f.write(f"""SimulationType                MonteCarlo
NumberOfCycles                {CYCLES}
NumberOfInitializationCycles  {INIT}
PrintEvery                    {CYCLES}
RestartFile                   no

Forcefield                    UFF_MOF
CutOff                        {rg.CUTOFF}
UseChargesFromCIFFile         yes
ChargeMethod                  Ewald
EwaldPrecision                1e-6

Framework 0
FrameworkName                 {name}
UnitCells                     {na} {nb} {nc}
ExternalTemperature           {temp}
ExternalPressure              {press}

Component 0 MoleculeName              CO2
            MoleculeDefinition        TraPPE
            TranslationProbability    0.5
            RotationProbability       0.3
            ReinsertionProbability    0.1
            SwapProbability           1.0
            CreateNumberOfMolecules   0
""")
    try:
        # 72시간. 8시간으로 뒀다가 물 계산 결과 5개를 조용히 날린 적이 있다
        # (MIGRATION 3-8). 단일 성분이라 실제로는 훨씬 짧게 끝난다.
        subprocess.run([rg.SIMULATE, 'simulation.input'], cwd=d,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                       timeout=259200, check=False)
    except subprocess.TimeoutExpired:
        print(f'  [시간초과] {label} {tag}', flush=True)
        return tag, label, None, 'timeout'
    outs = glob.glob(os.path.join(d, 'Output', 'System_0', '*.data'))
    if not outs:
        return tag, label, None, 'no-output'
    res = rg.parse(outs[0])
    for sub in ('VTK', 'Movies', 'Restart'):
        shutil.rmtree(os.path.join(d, sub), ignore_errors=True)
    return tag, label, res, 'ok'


def main():
    jobs = [(t, lab, p, T) for t in TARGETS for lab, p, T in CONDITIONS]
    os.makedirs(RUNS, exist_ok=True)
    print(f'작업 {len(jobs)}개 (구조 {len(TARGETS)} x 조건 {len(CONDITIONS)}), '
          f'워커 {MAX_WORKERS}', flush=True)
    for lab, p, T in CONDITIONS:
        print(f'  {lab:<6} {p/1e5:>5.2f} bar  {T:>5.1f} K', flush=True)
    print(flush=True)

    res = {}
    with ProcessPoolExecutor(max_workers=MAX_WORKERS) as ex:
        for tag, label, r, st in ex.map(run_one, jobs):
            res[(tag, label)] = r
            load = f'{r[4]:.4f}' if (r and r[4] is not None) else '-'
            print(f'  [{st:>16}] {label:<6} {tag:<8} 로딩 {load}', flush=True)

    print('\n' + '=' * 96)
    print(f'{"조성":<10} {"흡착 0.15bar":>16} {"VSA 0.10":>16} {"VSA 0.05":>16} '
          f'{"TSA 373K":>16}')
    print('-' * 96)
    rows = []
    for t in TARGETS:
        cells = []
        vals = {}
        for lab, _, _ in CONDITIONS:
            r = res.get((t, lab))
            if r and r[4] is not None:
                vals[lab] = (r[4], r[5])
                cells.append(f'{r[4]:.4f}±{r[5]:.4f}')
            else:
                cells.append('실패')
        print(f'{t:<10} ' + ' '.join(f'{c:>16}' for c in cells))
        row = {'name': t, 'loadings': {k: {'mol_per_kg': v[0], 'err': v[1]}
                                       for k, v in vals.items()}}
        # 작업 용량과 그 오차. 차이의 오차는 더해진다(독립 가정).
        if 'ads' in vals:
            a, ea = vals['ads']
            row['working_capacity'] = {}
            for lab in ('vsa10', 'vsa05', 'tsa'):
                if lab in vals:
                    d_, ed = vals[lab]
                    row['working_capacity'][lab] = {
                        'value': round(a - d_, 4),
                        'err': round((ea ** 2 + ed ** 2) ** 0.5, 4)}
        rows.append(row)

    print('\n' + '=' * 96)
    print(f'{"조성":<10} {"WC(VSA 0.10)":>20} {"WC(VSA 0.05)":>20} {"WC(TSA)":>20}')
    print('-' * 96)
    for row in rows:
        wc = row.get('working_capacity', {})
        cells = []
        for lab in ('vsa10', 'vsa05', 'tsa'):
            if lab in wc:
                cells.append(f'{wc[lab]["value"]:.4f}±{wc[lab]["err"]:.4f}')
            else:
                cells.append('-')
        print(f'{row["name"]:<10} ' + ' '.join(f'{c:>20}' for c in cells))

    with open(RESULT, 'w', encoding='utf-8') as f:
        json.dump({'conditions': [{'label': l, 'pressure_Pa': p,
                                   'temperature_K': T}
                                  for l, p, T in CONDITIONS],
                   'cycles': CYCLES, 'note': 'saIm100 은 수분 종료 판정으로 제외',
                   'rows': rows}, f, indent=2, ensure_ascii=False)
    print(f'\n[OK] {os.path.basename(RESULT)}')
    print('\n주: 작업 용량의 오차는 두 로딩 오차의 제곱합근입니다. 개별 로딩보다'
          ' 큽니다.\n    1.5σ 미만 차이는 순위를 매기지 마세요.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
