"""수분 경쟁 v3 — 이완된 구조(charged_v3) 위에서.

run_water_v2.py 와 같은 방식입니다. run_water.py 의 main() 이 결과 파일 경로를
모듈 상수가 아니라 함수 안에서 `os.path.join(HERE, ...)` 로 만들고 그 파일을
이어받기 소스로도 읽으므로, **HERE 자체를 옮겨야** 합니다. CHARGED/RUNS 만
바꾸면 옛 결과를 보고 전부 건너뜁니다(2026-08-14 에 실제로 그랬습니다).

HERE 를 옮기면 HERE 기준 상대경로인 WATER_DEF 가 깨지므로 절대경로로 다시
지정합니다 — TIP5P-Ew 5자리 물 정의입니다. RASPA 배포본의 TraPPE/water.def 는
3자리라 다릅니다(MIGRATION.md 3-4).
"""
import os
import sys

import run_water as rw

REAL = os.path.dirname(os.path.abspath(__file__))
V3 = os.path.join(REAL, 'v3_water')
os.makedirs(V3, exist_ok=True)

rw.HERE = V3
rw.CHARGED = os.path.join(REAL, 'charged_v3')
rw.RUNS = os.path.join(REAL, 'water_runs_v3')
rw.WATER_DEF = os.path.join(REAL, '..', '19_WaterCompetition', 'water.def')
rw.MAX_WORKERS = int(os.environ.get('WATER_V3_WORKERS', '4'))

if __name__ == '__main__':
    print('수분 경쟁 v3 (이완된 구조)', flush=True)
    print(f'  입력   {rw.CHARGED}', flush=True)
    print(f'  작업   {rw.RUNS}', flush=True)
    print(f'  결과   {os.path.join(rw.HERE, "water_results.json")}', flush=True)
    print(f'  워커   {rw.MAX_WORKERS}', flush=True)
    for p, label in ((rw.CHARGED, '전하 CIF 폴더'), (rw.WATER_DEF, '물 정의')):
        if not os.path.exists(p):
            print(f'  !! {label} 없음: {p}', flush=True)
            sys.exit(1)
    # 작업 단위 이어받기가 있으므로 중단 뒤 그냥 다시 띄우면 됩니다.
    print(flush=True)
    sys.exit(rw.main())
