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
import json
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


# ---------------------------------------------------------------------------
# [2026-09-05 07:0x] **격자를 지키는 덮어쓰기.**
#
# run_water.py:267 이 완주 직후 VTK/Movies/Restart/CrashRestart 를 지운다.
# 그 판단은 원래 목적(로딩 수치만 필요)에서는 옳다 — 런당 80 MB 가 넘는다.
#
# 그런데 **이 래퍼의 산출물이 바로 그 VTK 다.** 나는 격자 지시문을 주입해
# 놓고, 그것을 지우는 함수를 그대로 재사용했다. rh90_base 가 06:57 에
# 완주하면서 **격자가 통째로 삭제됐다** (로딩 수치는 무사, .data 는 남는다).
#
# 교훈: 남의 함수를 감싸 새 산출물을 만들 때는 **그 함수가 끝에서 무엇을
# 지우는지** 본다. 시작(무엇을 쓰는가)만 보고 끝(무엇을 지우는가)을 안 봤다.
# ---------------------------------------------------------------------------
_real_rmtree = rw.shutil.rmtree


def _keep_vtk(path, *a, **kw):
    """VTK 만 남기고 나머지 정리는 원본 그대로 둔다."""
    if os.path.basename(str(path).rstrip('/')) == 'VTK':
        print(f'  [격자 보존] {path} — 삭제하지 않습니다', flush=True)
        return
    return _real_rmtree(path, *a, **kw)


rw.shutil.rmtree = _keep_vtk


def main():
    # [2026-09-05 01:0x] 대상을 인자로 받는다. 세 구조는 서로 독립이므로
    # 프로세스를 나눠 **동시 3** 으로 돌린다(데스크탑 지시). 사이클·격자·RH·
    # 힘장은 그대로이고 **스케줄링만** 바뀐다. 동시 워커 수는 보고문에 병기한다.
    # 한 프로세스가 셋을 순차로 돌면 다른 프로세스와 **같은 작업 폴더**를 잡아
    # 충돌하므로, 프로세스마다 대상을 하나씩 준다.
    targets = sys.argv[1:] or TARGETS
    bad = [t for t in targets if t not in TARGETS]
    if bad:
        print(f'  !! 등록 대상이 아닙니다: {bad}  (등록: {TARGETS})', flush=True)
        return 1
    print('물 밀도 격자 — T-4·T-6 선행 (ASSIGN_20260905 §2)', flush=True)
    print(f'  RH {int(RH*100)}%  격자 {GRID}^3  '
          f'초기화 {rw.INIT} + 생산 {rw.CYCLES}', flush=True)
    print(f'  대상 {", ".join(targets)}', flush=True)
    print(f'  결과 {os.path.join(rw.HERE, "water_results.json")}', flush=True)
    print(f'  작업 {rw.RUNS}', flush=True)
    for name in targets:
        cif = os.path.join(rw.CHARGED, name + '_DDEC6.cif')
        if not os.path.exists(cif):
            print(f'  !! 전하 CIF 없음: {cif}', flush=True)
            return 1
    # 2026-09-24 — **적재 값을 버리고 있었습니다** (Caspar 질문에서 드러남).
    #   `rw.run_one` 은 `(name, rh, res, status)` 를 주는데 여기서 `r[-1]`(상태)만 찍고
    #   값이 든 `r[2]` 를 버렸습니다. `water_results.json` 은 `rw.main()` 에서 쓰이는데
    #   이 러너는 `run_one` 을 **직접** 부르므로 **아무도 안 썼습니다** — 그런데 위 118행이
    #   그 경로를 찍어 **있는 것처럼 보였습니다**(CLAUDE.md §0). 이제 여기서 씁니다.
    rows, bad = {}, 0
    for i, name in enumerate(targets, 1):
        print(f'\n[{i}/{len(targets)}] {name} RH{int(RH*100)}', flush=True)
        r = rw.run_one((name, RH))
        print(f'    -> {r[-1]}', flush=True)
        if r[-1] in ('ok', 'cached') and r[2]:
            rows[name] = {k: list(v) for k, v in r[2].items()}
            rows[name]['status'] = r[-1]
        else:
            bad += 1
            rows[name] = {'status': r[-1]}          # 실패도 **적습니다** — 빈칸은 안 됩니다
        with open(os.path.join(rw.HERE, 'water_results.json'), 'w',
                  encoding='utf-8') as fh:          # 한 건 끝날 때마다 씁니다(중간 저장)
            json.dump({'RH': RH, 'grid': GRID, 'init': rw.INIT, 'cycles': rw.CYCLES,
                       'rows': rows}, fh, indent=2, ensure_ascii=False)
    print(f'\n끝. 적재 {len(rows) - bad}/{len(targets)} '
          f'-> {os.path.join(rw.HERE, "water_results.json")}', flush=True)
    print('VTK 는 각 작업의 VTK/System_0/ 아래.', flush=True)
    return 1 if bad else 0


if __name__ == '__main__':
    sys.exit(main())
