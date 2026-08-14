"""수분 경쟁 재계산 (structures_v2 / charged_v2 기준).

[왜 다시 하는가]
    STRUCTURE_DEFECT.md — 빌더가 벤조 고리 부착 원자를 고정 상수로 골라 24개 자리
    중 18개에서 엉뚱한 탄소에 치환기를 달았습니다. 기존 water_results.json 은
    깨진 구조로 계산한 값입니다.

[왜 원본을 고치지 않고 감싸는가]
    같은 작업 디렉터리를 다른 세션이 함께 쓰고 있습니다(SESSION_LOG.md).
    원본을 편집하면 상대 세션과 부딪힙니다.

[첫 시도가 왜 실패했는가 — 2026-08-14]
    CHARGED 와 RUNS 만 바꿔치기했더니 **v1 결과가 그대로 나왔습니다.**
    run_water.py 의 main() 은 결과 파일 경로를 모듈 상수가 아니라
    `os.path.join(HERE, 'water_results.json')` 로 **함수 안에서 직접** 만들고,
    그 파일을 이어받기 소스로도 읽습니다(286행). 그래서 RUNS 를 비운 새 폴더로
    돌려도 옛 결과 파일을 보고 전부 건너뛰었습니다.

    HERE 자체를 v2 전용 폴더로 옮겨야 합니다. 그러면 286·339행이 가리키는 곳이
    함께 옮겨갑니다. 대신 HERE 로부터 상대경로로 잡히는 WATER_DEF 가 깨지므로
    절대경로로 다시 지정합니다(5사이트 물 정의 — MIGRATION.md 3-4).
"""
import os
import sys

import run_water as rw

REAL = os.path.dirname(os.path.abspath(__file__))
V2 = os.path.join(REAL, 'v2_water')
os.makedirs(V2, exist_ok=True)

# 순서가 중요합니다. HERE 를 먼저 옮기고, HERE 파생 경로를 전부 다시 지정합니다.
rw.HERE = V2
rw.CHARGED = os.path.join(REAL, 'charged_v2')
rw.RUNS = os.path.join(REAL, 'water_runs_v2')
rw.WATER_DEF = os.path.join(REAL, '..', '19_WaterCompetition', 'water.def')
rw.MAX_WORKERS = int(os.environ.get('WATER_V2_WORKERS', '4'))

if __name__ == '__main__':
    print('수분 경쟁 v2', flush=True)
    print(f'  입력   {rw.CHARGED}', flush=True)
    print(f'  작업   {rw.RUNS}', flush=True)
    print(f'  결과   {os.path.join(rw.HERE, "water_results.json")}', flush=True)
    print(f'  물정의 {rw.WATER_DEF}', flush=True)
    print(f'  워커   {rw.MAX_WORKERS}', flush=True)
    for p, label in ((rw.CHARGED, '전하 CIF 폴더'), (rw.WATER_DEF, '물 정의')):
        if not os.path.exists(p):
            print(f'  !! {label} 없음: {p}', flush=True)
            sys.exit(1)
    old = os.path.join(rw.HERE, 'water_results.json')
    if os.path.exists(old):
        print(f'  (이어받기: 기존 v2 결과 있음)', flush=True)
    else:
        print('  (처음부터 — 이어받을 v2 결과 없음)', flush=True)
    print(flush=True)
    sys.exit(rw.main())
