"""T-B1-C — 물 힘장 대조. `Hw none` / `Lw none` 두 줄만 다릅니다.

[무엇을 가르는 시험인가]
    `WATER_FF_DEFECT_20260905.md` 의 진단이 맞는지 봅니다. 진단은
    **`Hw` 가 UFF `H_` 의 LJ 를 물려받아 수소결합 자리를 반발벽으로 덮는다** 입니다.

    본 실행(T-B1)과 **씨앗·상자·온도·사이클·전하·Ewald·컷오프가 전부 같고**,
    다른 것은 **지역 `force_field_mixing_rules.def` 에 두 줄을 더한 것뿐**입니다.

        Lw             none
        Hw             lennard-jones    0.0       0.0

[공용 힘장은 건드리지 않습니다]
    CLAUDE.md §1 이 물 모델을 고정값으로 걸어 두었습니다. 공용
    `forcefield/UFF_MOF/` 는 **한 바이트도 바꾸지 않습니다.** RASPA 가 실행
    폴더의 사본을 먼저 읽는 것을 이용합니다. 사본은 이 실행 폴더 안에만 있습니다.

    ⚠️ **지역 사본이 실제로 채택됐는지 반드시 확인하십시오.** 출력 머리말의
    `NO VDW INTERACTION` 목록에 **`Ow-Hw`, `Hw-Hw` 가 들어가야** 합니다.
    안 들어가면 지역 사본이 무시된 것이고, 이 실행은 본 실행의 복제입니다.
    러너가 기동 직후 그 줄을 찍습니다.

    ⚠️ 첫 시도는 두 줄을 **파일 끝**에 붙였다가 실패했습니다. 항 목록 뒤의
    `Lorentz-Berthelot` 꼬리를 RASPA 가 항으로 읽어, `Hw-Hw` 가 UFF 값
    22.14170 / 2.57113 그대로 남았습니다. **등록해 둔 확인 조건이 잡았습니다.**

[등록한 예측 — 실행 전, COMMS/laptop.md 2026-09-05 13:4x]
    구조(주)  O–O 첫 봉우리 2.75~2.90 Å / g(2.82) ≥ 2.0 / 3.5 Å 배위수 4.0~5.2
    열역학(부) ΔH_vap = −<U_inter>/N + RT 가 40~48 kJ/mol
    현재 값   3.32 Å / 0.18 / 6.19 / 32.4  — **셋 다 예측 창 밖**이라 갈립니다

사용:
    python run_tb1_ffctl.py
"""
import os, shutil, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import run_tb1_hvap as base                      # 덱·씨앗·상자식을 그대로 상속

FF_SRC = os.path.expanduser(
    '~/RASPA/simulations/share/raspa/forcefield/UFF_MOF')
RUNS   = os.path.join(HERE, 'tb1_runs_ffctl')

def local_forcefield(d):
    """공용 파일을 읽기만 하고, 두 줄을 더한 사본을 실행 폴더에 둡니다."""
    shutil.copy(os.path.join(FF_SRC, 'pseudo_atoms.def'),
                os.path.join(d, 'pseudo_atoms.def'))
    src = os.path.join(FF_SRC, 'force_field_mixing_rules.def')
    lines = open(src, encoding='utf-8').read().rstrip('\n').split('\n')
    # 항 개수 줄을 찾아 2 늘리고, 마지막 실제 항 다음에 두 줄을 넣는다.
    # (파일 주석: "define shortest matches first, so that more specific ones
    #  overwrites these" -> 뒤에 놓아야 H_ 를 덮습니다.)
    n_idx = next(i for i, ln in enumerate(lines)
                 if ln.strip().isdigit())
    n_old = int(lines[n_idx].strip())
    lines[n_idx] = str(n_old + 2)
    # ⚠️ 파일 **끝에 붙이면 안 됩니다.** 항 목록 뒤에
    #    `# general mixing rule for Lennard-Jones` / `Lorentz-Berthelot`
    #    꼬리가 있어서, 뒤에 붙이면 RASPA 가 그 두 줄을 항으로 읽습니다.
    #    (첫 시도에서 실제로 그렇게 됐고 `Hw-Hw` 가 UFF 값 그대로 남았습니다.)
    #    **꼬리 바로 앞**, 즉 마지막 실제 항 다음에 넣습니다.
    tail = next(i for i, ln in enumerate(lines)
                if ln.strip().startswith('# general mixing rule'))
    ins = ['Lw             none', 'Hw             lennard-jones    0.0       0.0']
    lines[tail:tail] = ins
    with open(os.path.join(d, 'force_field_mixing_rules.def'), 'w') as f:
        f.write('\n'.join(lines) + '\n')
    return n_old, n_old + 2

def main():
    base.RUNS = RUNS
    L = base.box_length(base.N_MOL, base.RHO0)
    d = os.path.join(RUNS, 'hvap')
    os.makedirs(d, exist_ok=True)
    shutil.copy(base.WATER_DEF, os.path.join(d, 'water.def'))
    ri = os.path.join(d, 'RestartInitial', 'System_0')
    os.makedirs(ri, exist_ok=True)
    shutil.copy(base.SEED,
                os.path.join(ri, f'restart_Box_1.1.1_{base.TEMP:.6f}_{base.PRESS:g}'))
    n_old, n_new = local_forcefield(d)

    print('T-B1-C 물 힘장 대조 — Hw/Lw 에 none 두 줄만 추가', flush=True)
    print(f'  분자 {base.N_MOL}   L {L:.3f} Å   NVT {base.TEMP} K   밀도 {base.RHO0} g/cm³ 부과',
          flush=True)
    print(f'  초기화 {base.INIT} + 생산 {base.CYCLES}   (본 실행과 동일)', flush=True)
    print(f'  지역 힘장 항 {n_old} -> {n_new}   (공용 파일 불변)', flush=True)
    print(f'  씨앗 {base.SEED}', flush=True)
    print(f'  작업 폴더 {d}', flush=True)
    base.write_input(d, L)
    r = subprocess.run([base.SIMULATE, 'simulation.input'], cwd=d)
    print(f'  simulate 종료코드 {r.returncode}', flush=True)
    return r.returncode

if __name__ == '__main__':
    sys.exit(main())
