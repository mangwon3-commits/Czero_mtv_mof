"""T-B1 — TIP5P-Ew 순수 물 ΔH_vap (298.15 K). 덱은 COMMS/laptop.md 09-04 19:5x 에 등록.

[층위 — 배정문 지시대로 그대로 적습니다]
    골격 없는 순수 물 상자입니다. CLAUDE.md §1 의 고정값을 바꾸는 것이 아니라
    **같은 물 모델을 다른 계에 적용**하는 것입니다.
    Ewald 1e-6 · 컷오프 12 Å · TIP5P-Ew 5사이트 · 전하·LJ 전부 §1 그대로.

[산출식]
    ΔH_vap = -<U_inter>/N + RT        RT(298.15 K) = 2.4790 kJ/mol
    가정 ① 이상기체 기준 U_gas = 0 (강체 단량체)
         ② PV_liq 무시 (1 bar 에서 약 0.0018 kJ/mol)
         ③ 분극 자체에너지 보정 없음 (raw 보고)

[재기동 — NVT (2026-09-05, ASSIGN 데스크탑 권장안 (가)+(다))]
    1차 NPT 판은 상자가 27% 팽창해(밀도 0.729) 액체가 아니었습니다. 원인은 무작위
    초기 배치의 겹침을 NPT 가 팽창으로 해소하고 재응축하지 못한 것입니다.
    이번 판은 **NVT**(부피 이동 없음) 로 ρ=0.997 을 **부과**하고, 초기 배치는
    1차 판의 평형 구조를 목표 밀도로 압축해 씁니다(최소 O–O 2.491 Å, 겹침 0).
    ⚠️ **밀도를 부과했고 예측하지 않았습니다** — 44 와 비교할 때 이 차이가 남습니다.

[사이클 — **§1 원래 규약으로 복귀** (2026-09-05)]
    NVT 는 부피 이동이 없어 사이클당 1.93초(NPT 6.975초의 3.6배 빠름)입니다.
    그래서 **§1 표의 5,000 + 15,000 이 10.73시간**으로 이 기기 실증 최장(17.49 h)
    안에 들어갑니다. **09-04 의 사이클 축소는 NPT 비용 때문이었고, 그 이유가
    사라졌으므로 §1 그대로 돌아갑니다 — 이탈이 없습니다.**

[구판 기록 — 09-04 NPT 이탈 (이번 판에는 적용 안 됨)]
    초기화 **2,000** + 생산 **3,000**.
    사유는 성능이 아니라 **완주 가능성**입니다 — 등록 덱 5,000+15,000 은 실측
    사이클당 6.975초로 **38.76시간**이고 이 기기 실증 최장 연속 17.49 h 의
    2.2배입니다. 체크포인트가 진행도를 복원하지 않아 등록 덱으로는 값을 아예
    못 얻습니다.
    ⚠️ **§1 표(5,000+15,000)는 불변이고 흡착 계산은 전부 그대로입니다.**
    이 계는 골격 없는 순수 액체 NPT 라 층위가 다릅니다. 보고문에 이 이탈을
    명시해 흡착 규약을 따른 것처럼 읽히지 않게 합니다.
    충분성 점검: 완주 시 5블록 ± 가 **0.3 kJ/mol 이하**여야 하고, 넘으면
    연장하고 연장 사실과 최종 사이클 수를 판정문에 적습니다.

[최소 이미지 관문]
    컷오프 12 -> L > 24 Å 필요. N=512 의 <L> ~ 24.86 Å.
    평형 후 실측으로 재확인하고 <L> - 3σ_L <= 24 면 N=1000 으로 재실행.
"""
import os, shutil, subprocess, sys, math

HERE = os.path.dirname(os.path.abspath(__file__))
WATER_DEF = os.path.join(HERE, '..', '19_WaterCompetition', 'water.def')
SIMULATE = shutil.which('simulate') or os.path.expanduser(
    '~/miniconda3/envs/czeromof/bin/simulate')

N_MOL   = int(os.environ.get('TB1_N', '1000'))
CYCLES  = int(os.environ.get('TB1_CYCLES', '15000'))
INIT    = int(os.environ.get('TB1_INIT', '5000'))
TEMP    = 298.15
PRESS   = 100000.0          # 1 bar
CUTOFF  = 12.0
RHO0    = 0.997             # g/cm3, **NVT 에서 부과하는 밀도** (예측 아님)
SEED    = os.path.join(HERE, 'tb1_seed', 'restart_compressed')
TAG     = os.environ.get('TB1_TAG', f'n{N_MOL}')
RUNS    = os.path.join(HERE, f'tb1_runs_{TAG}')

def box_length(n, rho):
    M, NA = 18.01528, 6.02214076e23
    return (n * M / (rho * NA) * 1e24) ** (1.0 / 3.0)

def write_input(d, L):
    with open(os.path.join(d, 'simulation.input'), 'w') as f:
        f.write(f"""SimulationType                MonteCarlo
NumberOfCycles                {CYCLES}
NumberOfInitializationCycles  {INIT}
PrintEvery                    {max(1, CYCLES // 10)}
RestartFile                   yes
ContinueAfterCrash            yes
WriteBinaryRestartFileEvery   500

Forcefield                    UFF_MOF
CutOff                        {CUTOFF}
ChargeMethod                  Ewald
EwaldPrecision                1e-6

Box 0
BoxLengths                    {L:.5f} {L:.5f} {L:.5f}
BoxAngles                     90 90 90
ExternalTemperature           {TEMP}
ExternalPressure              {PRESS}

Component 0 MoleculeName              water
            MoleculeDefinition        TraPPE
            TranslationProbability    0.5
            RotationProbability       0.5
            CreateNumberOfMolecules   0
""")

def main():
    L = box_length(N_MOL, RHO0)
    d = os.path.join(RUNS, 'hvap')
    os.makedirs(d, exist_ok=True)
    shutil.copy(WATER_DEF, os.path.join(d, 'water.def'))
    ri = os.path.join(d, 'RestartInitial', 'System_0')
    os.makedirs(ri, exist_ok=True)
    shutil.copy(SEED, os.path.join(ri, f'restart_Box_1.1.1_{TEMP:.6f}_{PRESS:g}'))
    nsite = sum(1 for ln in open(os.path.join(d, 'water.def'), encoding='utf-8')
                if len(ln.split()) > 4 and ln.split()[1] in ('Ow', 'Hw', 'Lw'))
    print(f'T-B1 ΔH_vap — 순수 물 상자 (골격 없음)', flush=True)
    print(f'  분자 수 {N_MOL}   초기 L {L:.3f} Å   (최소 이미지 하한 {2*CUTOFF:.0f} Å)', flush=True)
    print(f'  **NVT** {TEMP} K, 밀도 {RHO0} g/cm³ **부과**   초기화 {INIT} + 생산 {CYCLES}', flush=True)
    print(f'  물 정의 사이트 {nsite}개 (TIP5P-Ew 는 5)', flush=True)
    if nsite != 5:
        print('  !! 5자리 물이 아닙니다. 중단.', flush=True); return 1
    if L <= 2 * CUTOFF:
        print(f'  !! 초기 상자가 최소 이미지 하한 이하입니다. 중단.', flush=True); return 1
    write_input(d, L)
    print(f'  작업 폴더 {d}', flush=True)
    r = subprocess.run([SIMULATE, 'simulation.input'], cwd=d)
    print(f'  simulate 종료코드 {r.returncode}', flush=True)
    return r.returncode

if __name__ == '__main__':
    sys.exit(main())
