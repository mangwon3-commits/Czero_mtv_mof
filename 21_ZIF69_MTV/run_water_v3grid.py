"""수분 경쟁 v3 — 조성 격자 4종 (58.3 / 62.5 / 66.7 / 87.5%).

[왜 이것이 비어 있었나]
    08-20 외부 16코어가 돌린 수분 경쟁 v3 는 base / 025 / 050 / 075 / 100
    다섯 종이었습니다. 그 뒤 격자 4종이 만들어졌고 건조 GCMC·안정성·습윤
    작업 용량까지 다 났는데, **RH 스캔만 안 났습니다.**

    그래서 지금 승자인 saIm0583 에 대해 사전 등록된 수분 관문
    (RH90 유지율 >=80 유효 / 50~80 조건부 / <50 종료)을 **한 번도 적용한 적이
    없습니다.** RH90 한 점은 습윤 WC 의 흡착 조건에서 간접적으로 있지만,
    RH 25/50 이 없어 물이 어느 습도에서 끼어드는지(온셋)를 말할 수 없습니다.
    Part 7 12-3 절이 "온셋 위치가 우리 데이터의 독자적 기여" 라고 적은 바로
    그 축입니다.

[왜 새 러너를 쓰지 않는가]
    run_water_v3.py 와 **완전히 같은 방식**입니다 — run_water 의 모듈 전역만
    갈아끼우고 그 main() 을 그대로 부릅니다. 엔진·규약·사이클·물 정의를
    한 글자도 바꾸지 않습니다. 그래야 격자 4종과 기존 5종을 같은 표에
    놓을 수 있습니다.

[출력을 왜 분리하나]
    기존 v3_water/water_results.json 에 직접 쓰면 이어받기가 두 배치를
    섞습니다. 규약이 같으므로 섞여도 값은 맞지만, **교차 검증 전에 합치면
    어느 기기가 낸 값인지 되돌릴 수 없습니다.** 따로 받고, base 대조가
    맞는지 확인한 뒤 사람이 합칩니다.

사용:
    WATER_V3_WORKERS=<물리코어수> python run_water_v3grid.py
"""
import os
import sys

import run_water as rw

REAL = os.path.dirname(os.path.abspath(__file__))
V3G = os.path.join(REAL, 'v3_water_grid')
os.makedirs(V3G, exist_ok=True)

rw.HERE = V3G
rw.CHARGED = os.path.join(REAL, 'charged_v3')
rw.RUNS = os.path.join(REAL, 'water_runs_v3grid')
rw.WATER_DEF = os.path.join(REAL, '..', '19_WaterCompetition', 'water.def')
rw.MAX_WORKERS = int(os.environ.get('WATER_V3_WORKERS', '4'))

# 격자 4종. 기존 다섯 종(base/025/050/075/100)은 08-20 에 이미 났습니다.
rw.TARGETS = [
    ('saIm0583', 'SO3H 58.3% (14/24) — 현 승자 조성'),
    ('saIm0625', 'SO3H 62.5% (15/24)'),
    ('saIm0667', 'SO3H 66.7% (16/24)'),
    ('saIm0875', 'SO3H 87.5% (21/24)'),
]

if __name__ == '__main__':
    print('수분 경쟁 v3 — 조성 격자 4종', flush=True)
    print(f'  입력   {rw.CHARGED}', flush=True)
    print(f'  작업   {rw.RUNS}', flush=True)
    print(f'  결과   {os.path.join(rw.HERE, "water_results.json")}', flush=True)
    print(f'  워커   {rw.MAX_WORKERS}', flush=True)
    print(f'  대상   {" ".join(n for n, _ in rw.TARGETS)}', flush=True)
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
    sys.exit(rw.main())
