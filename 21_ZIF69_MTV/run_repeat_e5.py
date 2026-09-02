"""`saIm0583e5` 건조 GCMC 를 **같은 기기·같은 러너로 3회 반복** — (다)의 직접 시험.

[왜 — REPEAT_E5_20260828.md 에 사전 등록]
    Junseok 물러너 RH0 과 데스크탑 건조 GCMC 가 같은 다섯 구조에서
    χ² = 36 (dof 5, p < 1e-4) 으로 갈립니다. 구조는 한 판뿐임이 git 으로
    확정됐고(전부 b700140 바이트), 템플릿 차이는 상수 오프셋을 만들 텐데
    관측된 차이는 부호가 뒤섞여(3 음 / 2 양) 상수 설명이 죽습니다.

    남은 가설이 (다) — **RASPA ± 가 실행 간 재현 산포를 과소평가한다** —
    이고, 이것은 반복 실행으로 직접 재집니다. e5 를 고른 이유: 갈림이
    가장 큰 실현(+4.53σ)입니다.

[설계]
    run_aryl_gcmc.run_one 을 **그대로** 씁니다(모드 'gcmc', CO2, 0.15e5 Pa,
    298 K, 15000/5000). 템플릿을 복사하지 않고 import 해서 실행 디렉터리만
    바꿉니다 — 복사하면 원본과 드리프트가 생깁니다.

    반복마다 새 디렉터리(repeat_e5/r1..r3)라 이어받기에 안 걸립니다.
    원본 runs_v3 는 건드리지 않습니다.

[fork 전역 주의 — run_gcmc_v3.py 독스트링 그대로]
    import 순서: run_aryl_gcmc 를 import 한 **뒤** CHARGED/RUNS 를 덮어씁니다.
    리눅스 fork 라 자식이 덮어쓴 전역을 그대로 받습니다.

사용:
    setsid nohup nice -n 19 python run_repeat_e5.py > repeat_e5.log 2>&1 &
"""
import json
import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import run_aryl_gcmc as rg   # noqa: E402

TAG = 'saIm0583e5'
N_REPEAT = 3
OUT = os.path.join(HERE, 'repeat_e5_results.json')


def main():
    src = os.path.join(HERE, 'charged_v3', f'{TAG}_DDEC6.cif')
    assert os.path.exists(src), src
    print(f'  {TAG} 건조 GCMC x {N_REPEAT}회 반복 (모드 gcmc, {rg.PRESSURE:.0f} Pa, '
          f'{rg.TEMP} K, {rg.GCMC_CYCLES}/{rg.GCMC_INIT})', flush=True)

    rows = []
    for i in range(1, N_REPEAT + 1):
        runs = os.path.join(HERE, 'repeat_e5', f'r{i}')
        charged = os.path.join(runs, '_charged')
        os.makedirs(charged, exist_ok=True)
        shutil.copyfile(src, os.path.join(charged, f'{TAG}_DDEC6.cif'))
        rg.CHARGED = charged
        rg.RUNS = runs
        # run_one 은 **태그가 아니라 CIF 경로**를 받습니다
        # (run_aryl_gcmc.py:118  cif, gas, mode = job).
        cif = os.path.join(charged, f'{TAG}_DDEC6.cif')
        name, gas, mode, res, status = rg.run_one((cif, 'CO2', 'gcmc'))
        print(f'  [r{i}] {status}  {res}', flush=True)
        rows.append({'repeat': i, 'status': status, 'res': res})
        json.dump(rows, open(OUT, 'w'), indent=1)

    print(f'  [OK] {OUT}', flush=True)
    return 0


if __name__ == '__main__':
    sys.exit(main())
