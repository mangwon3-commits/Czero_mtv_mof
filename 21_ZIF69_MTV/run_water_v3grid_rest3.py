"""수분 경쟁 v3 격자 — saIm0583 을 뺀 나머지 3종 (12작업: 3 x RH 0/25/50/90).

[왜 나뉘었나]
    격자 4종 16작업은 원래 한 기기가 다 돌 계획이었습니다. 그런데 배정된
    기기가 물리 4코어여서, NEW_MACHINE_20260822.md 4-5 절 규정대로 승자
    조성 saIm0583 하나(4작업)로 줄였습니다. 남은 12작업이 이 러너입니다.

    saIm0583 4작업: 4코어 클라우드 컨테이너 (run_water_v3grid_0583.py)
    나머지 12작업: 이 파일

[엔진·규약]
    run_water_v3grid.py 를 import 해서 모듈 전역(입력·출력 경로, 물 정의,
    워커 수)을 그대로 물려받고, TARGETS 에서 saIm0583 만 제외합니다.
    엔진·사이클·힘장·물 정의·압력은 한 글자도 다르지 않습니다.

[출력이 겹칩니다 — 읽어 주세요]
    이 러너는 run_water_v3grid.py 와 같은 v3_water_grid/water_results.json
    에 씁니다. 같은 기기에서 두 배치를 돌리면 이어받기가 알아서 합치지만,
    **다른 기기가 낸 파일을 이 경로로 복사해 넣으면 덮어씁니다.**

    4코어 컨테이너가 낸 saIm0583 4행과 이 기기가 낼 12행은 **파일을 합치지
    말고 따로 보관한 뒤 사람이 합칩니다.** 어느 기기가 낸 값인지 되돌릴 수
    있어야 합니다(NEW_MACHINE_20260822.md 5 절).

사용:
    WATER_V3_WORKERS=<물리코어수> python run_water_v3grid_rest3.py
"""
import os
import sys

import run_water_v3grid  # noqa: F401 — 전역 설정(경로·워커·격자 대상)을 물려받는다
import run_water as rw

EXCLUDE = 'saIm0583'
rw.TARGETS = [t for t in rw.TARGETS if t[0] != EXCLUDE]

if __name__ == '__main__':
    print('수분 경쟁 v3 — 격자 나머지 3종 (12작업)', flush=True)
    print(f'  입력   {rw.CHARGED}', flush=True)
    print(f'  작업   {rw.RUNS}', flush=True)
    print(f'  결과   {os.path.join(rw.HERE, "water_results.json")}', flush=True)
    print(f'  워커   {rw.MAX_WORKERS}', flush=True)
    print(f'  제외   {EXCLUDE} (4코어 컨테이너가 별도로 돌림)', flush=True)
    print(f'  대상   {" ".join(n for n, _ in rw.TARGETS)}', flush=True)
    if len(rw.TARGETS) != 3:
        print(f'  !! 대상이 3종이 아닙니다({len(rw.TARGETS)}종). 중단합니다.',
              flush=True)
        sys.exit(1)
    for p, label in ((rw.CHARGED, '전하 CIF 폴더'), (rw.WATER_DEF, '물 정의')):
        if not os.path.exists(p):
            print(f'  !! {label} 없음: {p}', flush=True)
            sys.exit(1)
    missing = [n for n, _ in rw.TARGETS
               if not os.path.exists(os.path.join(rw.CHARGED, n + '_DDEC6.cif'))]
    if missing:
        print(f'  !! 전하 CIF 없음: {missing}', flush=True)
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
    sys.exit(rw.main())
