"""랩탑 R 측정 — 실행 간 재현 산포용 RH0 반복 (LAPTOP_R_20260829.md).

[배정문과 다른 점 — 바꾼 것이 아니라 맞춘 것입니다]
    배정문 2절은 구조를 `saIm0583` 으로 적었습니다. 그런데 **랩탑은 그 구조의
    RH0 을 잰 적이 없습니다.**

        saIm0583@RH0  ->  v3_water_grid/water_results_desktop4.json  (데스크탑)
        랩탑 자료      ->  water_results_laptop.json = 0625 / 0667 / 0875

    배정문 4절이 "랩탑 원본이 없는 구조로는 '반복' 이 성립하지 않습니다" 라고
    금지하고 있으므로 0583 으로는 돌릴 수 없습니다. 같은 문서 1절이 지적한
    17-b 라벨 오류("랩탑 열은 데스크탑 자료였다")가 이 배정문에도 남은 것으로
    보입니다.

    2절이 이 경우를 대비해 두었습니다 — "랩탑이 이미 RH0 을 잰 구조 중 하나를
    고르되", "원본 선택이 위와 다르면 바꾸지 말고 실제 원본 조건을 적고 그에
    맞추십시오." 그대로 따릅니다.

[원본 실행의 실제 조건 — 보고에 그대로 적습니다]
    구조     saIm0625 (charged_v3/saIm0625_DDEC6.cif)
    러너     run_water_v3grid_rest3.py  (커밋 31b0f1c, sha256 63d5c274858b45f7)
             -> run_water_v3grid.py 전역 상속 -> run_water.py
    동시성   **8 워커** (배정문의 "동시성 1" 과 다름 — 규약 7-2 대로 병기)
    시각     08-22 14:41 기동, 12작업, RH0 은 08-22 18:2x 완주
    결과     v3_water_grid/water_results_laptop.json

    run_water.py 는 그 뒤 08-25 에 d0b6f50 으로 바뀌었지만 변경은 **결과 파일
    병합 로직뿐**입니다. 사이클·힘장·압력·온도·물 정의·이동 확률은 한 줄도
    바뀌지 않았습니다(diff 확인). 물리적으로 같은 러너입니다.

[이번 실행]
    RH0 만, saIm0625 만, 반복마다 **새 디렉터리**(이어받기 회피), 동시성 1.
    3회 -> 원본 포함 n=4.

    동시성이 원본(8)과 다른 것은 배정문 2절 지시입니다. 경합이 없으므로
    한 작업이 더 빨리 끝나지만, 재는 것은 **결과값의 실행 간 산포**이지
    소요 시간이 아닙니다.

사용:
    RREP_INDEX=1 python run_water_Rrep.py
"""
import os
import sys

import run_water_v3grid  # noqa: F401 — 경로·물 정의·격자 전역을 그대로 상속
import run_water as rw

IDX = os.environ.get('RREP_INDEX', '1')
STRUCT = 'saIm0625'
HERE = os.path.dirname(os.path.abspath(__file__))

# 반복마다 새 디렉터리 — 이어받기가 걸리면 "반복" 이 아니라 캐시 회수가 된다.
OUT = os.path.join(HERE, 'v3_water_Rrep', f'rep{IDX}')
os.makedirs(OUT, exist_ok=True)

rw.HERE = OUT
rw.RUNS = os.path.join(HERE, f'water_runs_Rrep{IDX}')
rw.RH_LIST = [0.0]
rw.TARGETS = [t for t in rw.TARGETS if t[0] == STRUCT]
rw.MAX_WORKERS = 1

if __name__ == '__main__':
    print(f'랩탑 R 측정 — RH0 반복 {IDX}/3', flush=True)
    print(f'  구조   {STRUCT}  (원본: run_water_v3grid_rest3.py, 8워커)', flush=True)
    print(f'  입력   {rw.CHARGED}', flush=True)
    print(f'  작업   {rw.RUNS}   (새 디렉터리)', flush=True)
    print(f'  결과   {os.path.join(rw.HERE, "water_results.json")}', flush=True)
    print(f'  워커   {rw.MAX_WORKERS}   RH {rw.RH_LIST}', flush=True)

    if len(rw.TARGETS) != 1:
        print(f'  !! 대상이 1종이 아닙니다({len(rw.TARGETS)}). 중단.', flush=True)
        sys.exit(1)
    for p, label in ((rw.CHARGED, '전하 CIF 폴더'), (rw.WATER_DEF, '물 정의')):
        if not os.path.exists(p):
            print(f'  !! {label} 없음: {p}', flush=True)
            sys.exit(1)
    cif = os.path.join(rw.CHARGED, STRUCT + '_DDEC6.cif')
    if not os.path.exists(cif):
        print(f'  !! 전하 CIF 없음: {cif}', flush=True)
        sys.exit(1)
    # 5자리 물 확인 — 배포본 3자리로 바뀌면 조용히 다른 물로 계산된다.
    nsite = sum(1 for ln in open(rw.WATER_DEF, encoding='utf-8')
                if len(ln.split()) > 4 and ln.split()[1] in ('Ow', 'Hw', 'Lw'))
    print(f'  물 정의 사이트 {nsite}개 (TIP5P-Ew 는 5)', flush=True)
    if nsite != 5:
        print('  !! 5자리 물이 아닙니다. 중단.', flush=True)
        sys.exit(1)
    print(flush=True)
    sys.exit(rw.main())
