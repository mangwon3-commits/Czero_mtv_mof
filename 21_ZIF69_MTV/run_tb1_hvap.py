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

[최소 이미지 관문]
    컷오프 12 -> L > 24 Å 필요. N=512 의 <L> ~ 24.86 Å.
    평형 후 실측으로 재확인하고 <L> - 3σ_L <= 24 면 N=1000 으로 재실행.
"""
import os, shutil, subprocess, sys, math

HERE = os.path.dirname(os.path.abspath(__file__))
WATER_DEF = os.path.join(HERE, '..', '19_WaterCompetition', 'water.def')
SIMULATE = shutil.which('simulate') or os.path.expanduser(
    '~/miniconda3/envs/czeromof/bin/simulate')

N_MOL   = int(os.environ.get('TB1_N', '512'))
CYCLES  = int(os.environ.get('TB1_CYCLES', '15000'))
INIT    = int(os.environ.get('TB1_INIT', '5000'))
TEMP    = 298.15
PRESS   = 100000.0          # 1 bar
CUTOFF  = 12.0
RHO0    = 0.997             # g/cm3, 초기 상자 씨앗값 (NPT 이므로 출발점일 뿐)
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
RestartFile                   no
ContinueAfterCrash            yes
WriteBinaryRestartFileEvery   5000

Forcefield                    UFF_MOF
CutOff                        {CUTOFF}
ChargeMethod                  Ewald
EwaldPrecision                1e-6

Box 0
BoxLengths                    {L:.5f} {L:.5f} {L:.5f}
BoxAngles                     90 90 90
ExternalTemperature           {TEMP}
ExternalPressure              {PRESS}
VolumeChangeProbability       0.01

Component 0 MoleculeName              water
            MoleculeDefinition        TraPPE
            TranslationProbability    0.5
            RotationProbability       0.5
            CreateNumberOfMolecules   {N_MOL}
""")

def main():
    L = box_length(N_MOL, RHO0)
    d = os.path.join(RUNS, 'hvap')
    os.makedirs(d, exist_ok=True)
    shutil.copy(WATER_DEF, os.path.join(d, 'water.def'))
    nsite = sum(1 for ln in open(os.path.join(d, 'water.def'), encoding='utf-8')
                if len(ln.split()) > 4 and ln.split()[1] in ('Ow', 'Hw', 'Lw'))
    print(f'T-B1 ΔH_vap — 순수 물 상자 (골격 없음)', flush=True)
    print(f'  분자 수 {N_MOL}   초기 L {L:.3f} Å   (최소 이미지 하한 {2*CUTOFF:.0f} Å)', flush=True)
    print(f'  NPT  {TEMP} K  {PRESS/1e5:.1f} bar   초기화 {INIT} + 생산 {CYCLES}', flush=True)
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
