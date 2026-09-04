"""물 밀도 격자 러너 — T-4·T-6 선행 계산 (ASSIGN_20260905 §2, 덱 등록 82afe50).

[왜 새 코드인가]
    run_density_map.py 는 **CO2 격자만** 낸다(단성분 0.15 bar). T-4 는 물 밀도
    격자를, T-6 은 CO2/H2O 겹침을 요구하는데 물 쪽 격자를 내는 러너가 없었다.

[왜 템플릿을 복사하지 않는가 — run_water_chunked.py 와 다른 선택]
    chunked 러너는 입력 템플릿을 **복사**하고 `_assert_template_matches()` 로
    갈림을 막았다. 여기서는 복사가 필요 없다 — run_water.py:252 가
    `subprocess.run([SIMULATE,'simulation.input'], cwd=d, ...)` 로 부르므로,
    **그 호출 직전에 이미 쓰인 simulation.input 에 격자 지시자 3줄만 덧붙이면**
    된다. 템플릿은 원본이 그대로 쓰므로 **갈릴 수가 없다.**
    (복사본이 없으니 _assert_template_matches 도 필요 없다.)

[경로를 전부 함께 옮기는 이유 — 08-27 사고]
    조성 필터된 러너가 공용 water_results.json 을 덮은 전력이 있다(d0b6f50).
    run_density_v2.py 독스트링이 설명한 대로 HERE·RUNS·CHARGED·WATER_DEF 를
    **전부** 옮긴다. 하나만 옮기면 남의 결과를 덮는다.

[등록 조건 — 덱 82afe50, 데스크탑 승인]
    RH 90% · 격자 90^3 · 초기화 5,000 + 생산 15,000 · base/nbIm025/saIm050
    사이클이 밀도맵 규약(2,000+5,000)과 다른 이유: 이 격자가 설명할 대상이
    **15,000 사이클 실행의 유지율**이다. 사이클이 다르면 다른 평형의 그림이다.
"""
import os
import sys

import run_water as rw

REAL = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(REAL, 'density_water_v3')
os.makedirs(OUT, exist_ok=True)

# 순서 주의 — HERE 에서 파생되는 것을 전부 다시 지정한다(run_density_v2.py 방식).
rw.HERE = OUT                                              # water_results.json 이 여기로
rw.RUNS = os.path.join(REAL, 'water_runs_density_v3')      # 작업 폴더
rw.CHARGED = os.path.join(REAL, 'charged_v3')              # 입력 CIF
rw.WATER_DEF = os.path.join(REAL, '..', '19_WaterCompetition', 'water.def')

GRID = 90
TARGETS = ['base', 'nbIm025', 'saIm050']
RH = 0.90

_GRID_BLOCK = (
    "\n"
    "ComputeDensityProfile3DVTKGrid    yes\n"
    "WriteDensityProfile3DVTKGridEvery 500\n"
    f"DensityProfile3DVTKGridPoints     {GRID} {GRID} {GRID}\n"
)

_real_run = rw.subprocess.run


def _run_with_grid(cmd, **kw):
    """simulate 를 부르기 직전에 격자 지시자를 덧붙인다.

    원본이 쓴 simulation.input 을 읽어 뒤에 3줄만 더한다. 이미 있으면 안 더한다
    (이어받기로 같은 폴더를 다시 지날 수 있다).
    """
    d = kw.get('cwd')
    if d and cmd and str(cmd[-1]) == 'simulation.input':
        p = os.path.join(d, 'simulation.input')
        if os.path.exists(p):
            body = open(p, encoding='utf-8').read()
            if 'ComputeDensityProfile3DVTKGrid' not in body:
                with open(p, 'a', encoding='utf-8') as f:
                    f.write(_GRID_BLOCK)
                print(f'    [격자] {GRID}^3 지시자 추가 — {os.path.basename(d)}',
                      flush=True)
    return _real_run(cmd, **kw)


rw.subprocess.run = _run_with_grid


def main():
    print('물 밀도 격자 — T-4·T-6 선행 (ASSIGN_20260905 §2)', flush=True)
    print(f'  RH {int(RH*100)}%  격자 {GRID}^3  '
          f'초기화 {rw.INIT} + 생산 {rw.CYCLES}', flush=True)
    print(f'  대상 {", ".join(TARGETS)}', flush=True)
    print(f'  결과 {os.path.join(rw.HERE, "water_results.json")}', flush=True)
    print(f'  작업 {rw.RUNS}', flush=True)
    for i, name in enumerate(TARGETS, 1):
        cif = os.path.join(rw.CHARGED, name + '_DDEC6.cif')
        if not os.path.exists(cif):
            print(f'  !! 전하 CIF 없음: {cif}', flush=True)
            return 1
    for i, name in enumerate(TARGETS, 1):
        print(f'\n[{i}/{len(TARGETS)}] {name} RH{int(RH*100)}', flush=True)
        r = rw.run_one((name, RH))
        print(f'    -> {r[-1]}', flush=True)
    print('\n끝. VTK 는 각 작업의 VTK/System_0/ 아래.', flush=True)
    return 0


if __name__ == '__main__':
    sys.exit(main())
