"""수분 경쟁 v3 격자 — saIm0583 한 종만 (4작업: RH 0/25/50/90).

[왜 축소판인가]
    NEW_MACHINE_20260822.md 4-5절: 물리 코어가 4개 이하면 대상을 승자 조성
    saIm0583 하나로 줄이는 편이 낫다 — 16작업은 네 파도 45~60시간이지만,
    4작업은 한 파도로 끝나고 승자 조성만으로도 사전 등록된 수분 관문
    (RH90 유지율)은 채워진다. 이 기기(클라우드 컨테이너)가 물리 4코어라
    이 축소판을 만들었다.

[엔진·규약]
    run_water_v3grid.py 를 import 해서 모듈 전역(입력·출력 경로, 물 정의,
    워커 수)을 그대로 물려받고, TARGETS 만 saIm0583 으로 거른다.
    엔진·사이클·힘장·물 정의는 한 글자도 다르지 않다.

[출력]
    run_water_v3grid.py 와 같은 v3_water_grid/water_results.json,
    water_runs_v3grid/ 를 쓴다. 그래서 나중에 나머지 3종(0625/0667/0875)을
    run_water_v3grid.py 로 돌리면 여기서 완주한 4작업은 이어받기가
    cached 로 건너뛴다.

사용:
    WATER_V3_WORKERS=<물리코어수> python run_water_v3grid_0583.py
"""
import os
import shutil
import sys

import run_water_v3grid  # noqa: F401 — 전역 설정(경로·워커·격자 대상)을 물려받는다
import run_water as rw

rw.TARGETS = [t for t in rw.TARGETS if t[0] == 'saIm0583']

if __name__ == '__main__':
    print('수분 경쟁 v3 — saIm0583 한 종 (4코어 축소판)', flush=True)
    print(f'  입력   {rw.CHARGED}', flush=True)
    print(f'  작업   {rw.RUNS}', flush=True)
    print(f'  결과   {os.path.join(rw.HERE, "water_results.json")}', flush=True)
    print(f'  워커   {rw.MAX_WORKERS}', flush=True)
    print(f'  대상   {" ".join(n for n, _ in rw.TARGETS)}', flush=True)
    if len(rw.TARGETS) != 1:
        print('  !! saIm0583 이 격자 대상에 없습니다. 중단합니다.', flush=True)
        sys.exit(1)
    for p, label in ((rw.CHARGED, '전하 CIF 폴더'), (rw.WATER_DEF, '물 정의')):
        if not os.path.exists(p):
            print(f'  !! {label} 없음: {p}', flush=True)
            sys.exit(1)
    # 물 정의가 5자리인지 확인합니다. 배포본 TraPPE/water.def 는 3자리라
    # 조용히 다른 물로 계산됩니다 — 실패가 결과처럼 보이는 그 유형입니다.
    nsite = sum(1 for ln in open(rw.WATER_DEF, encoding='utf-8')
                if len(ln.split()) > 4 and ln.split()[1] in ('Ow', 'Hw', 'Lw'))
    print(f'  물 정의 사이트 {nsite}개 (TIP5P-Ew 는 5)', flush=True)
    if nsite != 5:
        print('  !! 5자리 물이 아닙니다. 중단합니다.', flush=True)
        sys.exit(1)
    print(flush=True)
    rc = rw.main()

    # 기기 이름을 붙인 사본. 데스크탑도 같은 16작업을 돌리므로 saIm0583 이
    # 두 벌 생길 수 있고, 같은 water_results.json 경로로는 어느 기기가 낸
    # 값인지 되돌릴 수 없습니다. 두 벌이 생기면 그것이 곧 원래 하려던
    # conda 빌드 대 소스 빌드 교차 검증입니다 — 덮어쓰면 그 검증이 사라집니다.
    src = os.path.join(rw.HERE, 'water_results.json')
    if rc == 0 and os.path.exists(src):
        dst = os.path.join(rw.HERE, 'water_results_cloud4c.json')
        shutil.copy(src, dst)
        print(f'  기기명 사본 저장: {dst}', flush=True)

    sys.exit(rc)
