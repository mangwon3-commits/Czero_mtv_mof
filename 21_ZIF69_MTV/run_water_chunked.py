"""분할 실행 시제품 — 생산 15,000 을 3,000 × 5 조각으로 나눠 돌리고 수합한다.

[사전 등록] 21_ZIF69_MTV/CHUNKED_PROTOCOL_20260826.md

[제안자] 사용자 (2026-08-26). CLAUDE.md §1 이 "사이클을 바꾸고 싶으면 바꾸지
말고 물어보라" 고 하므로 laptop2 가 물었고, 승인 후 이 파일을 씁니다.

[총 사이클은 바뀌지 않습니다]
    초기화 5,000 + 생산 15,000, 힘장·물 정의·압력·컷오프·전하 전부 불변입니다.
    바뀌는 것은 **실행 구조** 하나입니다.

[왜 통계가 보존되는가 — 이것이 이 제안의 핵심입니다]
    RASPA 의 현행 `±` 는 생산 15,000 을 **3,000씩 5블록**으로 나눈 블록평균의
    SEM 에 t(0.975,4)=2.776 을 곱한 값입니다. 출력의 Block[0]~Block[4] 가
    그것이고, 계수 2.776 의 자유도 4 가 곧 5블록입니다.

    이 러너는 그 **블록 경계를 작업 경계로 승격**시킵니다.

        현행   한 실행 안에서  3,000 × 5 블록  -> 블록평균 SEM x 2.776
        분할   5개 작업으로   3,000 × 5 조각  -> 조각평균 SEM x 2.776

    **같은 추정량입니다.** 상관 구조도 같습니다 — 조각 k+1 이 조각 k 의 배치를
    이어받으므로 블록 k+1 이 블록 k 에 이어지는 것과 **같은 하나의 마르코프
    사슬**입니다. 새 자를 만들지 않습니다(COMMS.md 규약 ⑥).

    **조건**: 조각 2~5 는 `NumberOfInitializationCycles 0` 이어야 합니다.
    재초기화하면 사슬이 끊기고 그때는 같은 시험이 아닙니다.

[왜 필요한가]
    이어받기의 시간 이득이 **0** 임이 08-26 에 확정됐습니다(COMMS/desktop.md).
    `ContinueAfterCrash` 는 배치만 복원하고 사이클은 0 부터 다시 돕니다.
    그래서 **작업 내부에는 그물이 없습니다**(COMMS.md:245).

    이것 때문에 난 사고가 셋입니다 — 08-17 정전 19작업, 08-22 컨테이너 55분
    쳇바퀴, 08-26 laptop2 의 RH25 생산 10,000 사이클. 분할은 그 그물을 만듭니다.

        laptop2 실측    통짜 최장 노출   조각 최장 노출
        RH90              22.37 h          8.95 h
        크래시 1회 손실   22.37 h          3.36 h 이하

[기존 러너를 건드리지 않습니다]
    `run_water.py` 로 랩탑이 계산 중입니다. 이 파일은 별도이고, 파싱·완주
    판정·전하 검사는 **그 모듈에서 import 해 씁니다** — 자를 두 벌 두지
    않기 위해서입니다(규약 ⑥).

    다만 입력 템플릿은 `run_one` 안 f-문자열이라 뽑아 쓸 수 없어 **복사**
    했습니다. 복사본이 원본과 갈라지는 것을 막으려고 기동 시
    `_assert_template_matches()` 가 원본 소스에서 불변 줄들을 확인하고,
    하나라도 없으면 **중단**합니다.

사용:
    python run_water_chunked.py --name saIm0875 --rh 0
    python run_water_chunked.py --name saIm0875 --rh 0 --dry-run
"""
import argparse
import glob
import math
import os
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import run_water_v3grid          # noqa: F401,E402  (v3 격자 배선: 경로·물 정의)
import run_water as rw           # noqa: E402
from ase.io import read          # noqa: E402

CHUNKS = 5
CHUNK_CYCLES = rw.CYCLES // CHUNKS          # 3000

# 템플릿 복사본이 원본과 갈라지지 않았는지 확인할 불변 줄들.
# 물리·규약을 정하는 줄만 고릅니다 — 숫자가 바뀌면 결과가 바뀌는 것들입니다.
_INVARIANTS = (
    'SimulationType                MonteCarlo',
    'Forcefield                    UFF_MOF',
    'UseChargesFromCIFFile         yes',
    'ChargeMethod                  Ewald',
    'EwaldPrecision                1e-6',
    'MoleculeName              CO2',
    'MoleculeName              water',
    'TranslationProbability    0.5',
    'RotationProbability       0.3',
    'ReinsertionProbability    0.1',
    'SwapProbability           1.0',
    'CreateNumberOfMolecules   0',
)


def _assert_template_matches():
    """원본 run_water.py 에 이 파일이 복사한 불변 줄들이 그대로 있는지 본다.

    원본이 바뀌었는데 이 복사본이 안 바뀌면 **두 규약이 조용히 갈립니다.**
    그것이 §3 이 경고하는 유형이라 기동 시 막습니다.
    """
    src = open(os.path.join(HERE, 'run_water.py'), encoding='utf-8').read()
    missing = [s for s in _INVARIANTS if s not in src]
    if missing:
        print('  !! run_water.py 에서 다음 줄을 못 찾았습니다 — 템플릿이 갈렸습니다:',
              flush=True)
        for m in missing:
            print(f'       {m}', flush=True)
        print('     이 러너의 복사본을 원본에 맞춰 고치기 전에는 돌리지 마세요.',
              flush=True)
        sys.exit(2)
    if (rw.CYCLES, rw.INIT) != (15000, 5000):
        print(f'  !! run_water 의 사이클이 {rw.CYCLES}/{rw.INIT} 입니다 '
              f'(기대 15000/5000). §1 값이 바뀌었습니다. 중단합니다.', flush=True)
        sys.exit(2)
    if CHUNK_CYCLES * CHUNKS != rw.CYCLES:
        print(f'  !! 생산 {rw.CYCLES} 가 {CHUNKS} 로 나누어떨어지지 않습니다.',
              flush=True)
        sys.exit(2)


def write_input(d, name, rh, k):
    """조각 k(0부터)의 simulation.input 을 쓴다.

    조각 0 만 초기화를 돌고, 1~4 는 앞 조각의 배치를 이어받는다.
    """
    fw = name + '_DDEC6'
    cif = os.path.join(rw.CHARGED, name + '_DDEC6.cif')
    na, nb, nc = rw.unit_cells(read(cif))
    p_h2o = rw.P_SAT_298 * rh
    p_tot = rw.P_CO2 + p_h2o
    x_co2, x_h2o = rw.P_CO2 / p_tot, p_h2o / p_tot

    moves = ('            TranslationProbability    0.5\n'
             '            RotationProbability       0.3\n'
             '            ReinsertionProbability    0.1\n'
             '            SwapProbability           1.0\n'
             '            CreateNumberOfMolecules   0\n')
    comp = f"""Component 0 MoleculeName              CO2
            MoleculeDefinition        TraPPE
            MolFraction               {x_co2:.6f}
{moves}"""
    if rh > 0:
        comp += f"""
Component 1 MoleculeName              water
            MoleculeDefinition        TraPPE
            MolFraction               {x_h2o:.6f}
{moves}"""

    init = rw.INIT if k == 0 else 0
    restart = 'no' if k == 0 else 'yes'
    with open(os.path.join(d, 'simulation.input'), 'w') as f:
        f.write(f"""SimulationType                MonteCarlo
NumberOfCycles                {CHUNK_CYCLES}
NumberOfInitializationCycles  {init}
PrintEvery                    {CHUNK_CYCLES}
RestartFile                   {restart}
ContinueAfterCrash            yes
WriteBinaryRestartFileEvery   {rw.CRASH_EVERY}

Forcefield                    UFF_MOF
CutOff                        {rw.CUTOFF}
UseChargesFromCIFFile         yes
ChargeMethod                  Ewald
EwaldPrecision                1e-6

Framework 0
FrameworkName                 {fw}
UnitCells                     {na} {nb} {nc}
ExternalTemperature           {rw.TEMP}
ExternalPressure              {p_tot:.4f}

{comp}""")


def carry_restart(prev_d, next_d):
    """앞 조각의 Restart/ 를 다음 조각의 RestartInitial/ 로 옮긴다.

    RASPA 는 실행 끝에 `Restart/System_0/restart_...` 를 쓰고,
    `RestartFile yes` 면 `RestartInitial/System_0/` 에서 읽는다.
    (run_water.py:267 이 완주 뒤 Restart/ 를 지우는 것이 그 산출물이다 —
     이 러너는 지우지 않고 이어 넘긴다.)
    """
    src = os.path.join(prev_d, 'Restart', 'System_0')
    dst = os.path.join(next_d, 'RestartInitial', 'System_0')
    if not os.path.isdir(src):
        return False, f'앞 조각에 Restart/System_0 이 없습니다: {src}'
    files = [f for f in os.listdir(src) if f.startswith('restart')]
    if not files:
        return False, f'restart 파일이 없습니다: {src}'
    os.makedirs(dst, exist_ok=True)
    for f in files:
        shutil.copy(os.path.join(src, f), os.path.join(dst, f))
    return True, f'{len(files)}개 이어 넘김'


def main():
    ap = argparse.ArgumentParser(description='분할 실행 시제품')
    ap.add_argument('--name', required=True, help='조성 태그 (예: saIm0875)')
    ap.add_argument('--rh', type=float, required=True, help='0 / 0.25 / 0.5 / 0.9')
    ap.add_argument('--dry-run', action='store_true')
    a = ap.parse_args()

    _assert_template_matches()

    base = os.path.join(HERE, 'water_runs_chunked',
                        f'rh{int(a.rh*100):02d}_{a.name}')
    cif = os.path.join(rw.CHARGED, a.name + '_DDEC6.cif')

    print(f'분할 실행 — {a.name} RH{int(a.rh*100)}%', flush=True)
    print(f'  조각 {CHUNKS}개 x 생산 {CHUNK_CYCLES} = {rw.CYCLES} (총 사이클 불변)',
          flush=True)
    print(f'  조각 0 만 초기화 {rw.INIT}, 조각 1~{CHUNKS-1} 은 0 + RestartFile yes',
          flush=True)
    print(f'  입력 {cif}', flush=True)
    print(f'  작업 {base}', flush=True)
    if not os.path.exists(cif):
        print(f'  !! 전하 CIF 없음: {cif}', flush=True)
        return 1
    nsite = sum(1 for ln in open(rw.WATER_DEF, encoding='utf-8')
                if len(ln.split()) > 4 and ln.split()[1] in ('Ow', 'Hw', 'Lw'))
    print(f'  물 정의 사이트 {nsite}개 (TIP5P-Ew 는 5)', flush=True)
    if nsite != 5:
        print('  !! 5자리 물이 아닙니다. 중단합니다.', flush=True)
        return 1
    if a.dry_run:
        print('  --dry-run 이므로 아무것도 돌리지 않았습니다.', flush=True)
        return 0

    vals, prev_d = [], None
    for k in range(CHUNKS):
        d = os.path.join(base, f'chunk{k}')
        os.makedirs(d, exist_ok=True)
        shutil.copy(cif, os.path.join(d, a.name + '_DDEC6.cif'))
        shutil.copy(rw.WATER_DEF, os.path.join(d, 'water.def'))
        if k > 0:
            ok, msg = carry_restart(prev_d, d)
            print(f'  [조각 {k}] 이어 넘기기 — {msg}', flush=True)
            if not ok:
                print('  !! 사슬이 끊겼습니다. 중단합니다.', flush=True)
                return 1
        write_input(d, a.name, a.rh, k)
        print(f'  [조각 {k}] 실행 중...', flush=True)
        subprocess.run([rw.SIMULATE, 'simulation.input'], cwd=d,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                       timeout=259200, check=False)
        outs = glob.glob(os.path.join(d, 'Output', 'System_0', '*.data'))
        if not outs:
            print(f'  !! 조각 {k} 출력 없음. 중단합니다.', flush=True)
            return 1
        if not rw.finished(outs[0]):
            print(f'  !! 조각 {k} 미완주. 중단합니다.', flush=True)
            return 1
        if not rw.net_charge_ok(outs[0]):
            print(f'  !! 조각 {k} 물 알짜전하 != 0. 중단합니다.', flush=True)
            return 1
        res = rw.parse_components(outs[0])          # 규약 ⑥ — 원본 파서를 쓴다
        co2 = res.get('CO2', (float('nan'), 0.0))[0]
        vals.append(co2)
        print(f'  [조각 {k}] CO2 {co2:.4f} mol/kg', flush=True)
        prev_d = d

    # 수합 — 현행과 **같은 형태**의 추정량. 새 자를 만들지 않는다.
    #   현행: 3,000사이클 블록 5개의 평균, SEM x t(0.975,4)
    #   분할: 3,000사이클 조각 5개의 평균, SEM x t(0.975,4)
    n = len(vals)
    mean = sum(vals) / n
    sd = math.sqrt(sum((v - mean) ** 2 for v in vals) / (n - 1))
    sem = sd / math.sqrt(n)
    ci95 = 2.776 * sem                              # t(0.975,4)

    print(flush=True)
    print(f'  조각별 CO2: {["%.4f" % v for v in vals]}', flush=True)
    print(f'  평균 {mean:.4f}  표본SD {sd:.4f}  SEM {sem:.4f}', flush=True)
    print(f'  **CO2 = {mean:.4f} ± {ci95:.4f} mol/kg** (95% CI, t(0.975,4)x SEM)',
          flush=True)

    # 사슬 연속성 — 조각별 값이 단조 추세면 평형이 안 이어진 것이다.
    inc = all(vals[i] < vals[i + 1] for i in range(n - 1))
    dec = all(vals[i] > vals[i + 1] for i in range(n - 1))
    print(f'  사슬 연속성: {"❌ 단조 추세 — 평형 미도달 의심" if (inc or dec) else "✅ 단조 추세 없음"}',
          flush=True)
    print('  (판정은 CHUNKED_PROTOCOL_20260826.md 3절. 통짜 값과 대면 사람이 한다)',
          flush=True)
    return 0


if __name__ == '__main__':
    sys.exit(main())
