"""수분 저압 확장 — RH 5 / 10 / 15% 6조성 (18작업). 물 친화도 축을 만들기 위한 것.

[무엇을 재는가 — 문헌 공통 축에 우리를 올리는 일]
    Chanut 2017 이 MOF 45 종에서 **물 친화도(헨리 상수)와 습윤 CO2 손실이
    반로그 상관**임을 보였습니다. 그 축에 우리 조성을 올리면 우리가 일반
    법칙을 따르는지, 벗어나는지가 바로 보입니다. 벗어나면 그 자체가 발견입니다.

    문제는 **그 축의 x 좌표가 우리에게 없다는 것**입니다. 우리는 RH 0/25/50/90
    만 재서 저압 구간이 비어 있고, 물 등온선의 초기 기울기를 못 냅니다.

    이 18 작업이 그 구간을 채웁니다. RH 5/10/15 는 **물 클러스터 온셋(≈RH30)
    한참 아래**라, 물이 아직 덩어리를 못 이룬 구간의 기울기 —— 즉 골격 자체의
    물 친화도 —— 를 봅니다.

[왜 새 계산을 안 만들고 RH 만 내리는가]
    run_water.py 를 그대로 씁니다. 엔진·힘장·CO2 모델·물 정의(TIP5P-Ew
    5사이트)·CO2 분압 0.15 bar·사이클 수가 **한 글자도 다르지 않습니다.**
    바뀌는 것은 RH_LIST 뿐입니다.

    Widom 삽입으로 물 헨리 상수를 직접 재는 방법도 있지만, 5사이트 강체
    분자를 좁은 기공에 꽂아 넣는 것은 통계가 나빠 별도 수렴 시험이 필요합니다.
    **이미 검증된 경로를 아래로 연장하는 쪽이 싸고 안전합니다.**

[덤 — W25 와 이어집니다]
    RH25 의 물 로딩(W25)을 온셋 직전 지표로 쓰고 있는데, 5/10/15 가 채워지면
    **온셋 이전 곡선 전체**가 생깁니다. W25 하나가 점이었다면 이제 선이 됩니다.
    소수성 설계(Zhao 2024)의 효과가 "온셋을 뒤로 미루는 것" 이라면 그 미룸이
    이 구간에서 보여야 합니다.

[출력을 왜 분리하나]
    기존 v3_water*/ 는 RH 0/25/50/90 격자의 답이 모이는 곳입니다. 저압 점을
    같은 파일에 넣으면 이어받기가 섞고, 나중에 "이 조성은 4점, 저 조성은 7점"
    이 되어 표가 비대칭해집니다. 따로 받고 사람이 합칩니다.

대상 6 조성 — 지금 비교표에 올라 있는 것 전부:
    base       무치환 대조군 (치환 자리가 없어 배치 자유도 0)
    saIm050    단일 치환 50%
    saIm0583   제약 하 1위 (58.3%)
    sa50nb50   혼합 SO3H 50 + NO2 50
    ms50nb50   혼합 SO2CH3 50 + NO2 50 (유지율 1위)
    sa25nb75   혼합 SO3H 25 + NO2 75

사용:
    WATER_LOWRH_WORKERS=<물리코어수> python run_water_lowrh.py
"""
import os
import shutil
import sys

import run_water as rw

REAL = os.path.dirname(os.path.abspath(__file__))
LOW = os.path.join(REAL, 'v3_water_lowrh')
os.makedirs(LOW, exist_ok=True)

rw.HERE = LOW
rw.CHARGED = os.path.join(REAL, 'charged_v3')
rw.RUNS = os.path.join(REAL, 'water_runs_lowrh')
rw.WATER_DEF = os.path.join(REAL, '..', '19_WaterCompetition', 'water.def')
rw.MAX_WORKERS = int(os.environ.get('WATER_LOWRH_WORKERS', '4'))

# 온셋(≈RH30) 아래 세 점. 비싼 것 먼저 넣어 꼬리를 줄입니다(LPT).
rw.RH_LIST = [0.15, 0.10, 0.05]

rw.TARGETS = [
    ('base',     '무치환 모체 — 대조군'),
    ('saIm050',  'SO3H 50%'),
    ('saIm0583', 'SO3H 58.3% — 제약 하 1위'),
    ('sa50nb50', 'SO3H 50% + NO2 50%'),
    ('ms50nb50', 'SO2CH3 50% + NO2 50% — 유지율 1위'),
    ('sa25nb75', 'SO3H 25% + NO2 75%'),
]

if __name__ == '__main__':
    print('수분 저압 확장 — RH 5/10/15%, 6조성 (18작업)', flush=True)
    print(f'  입력   {rw.CHARGED}', flush=True)
    print(f'  작업   {rw.RUNS}', flush=True)
    print(f'  결과   {os.path.join(rw.HERE, "water_results.json")}', flush=True)
    print(f'  워커   {rw.MAX_WORKERS}', flush=True)
    print(f'  RH     {rw.RH_LIST}  (온셋 ≈0.30 아래)', flush=True)
    print(f'  대상   {" ".join(n for n, _ in rw.TARGETS)}', flush=True)

    if len(rw.TARGETS) != 6 or rw.RH_LIST != [0.15, 0.10, 0.05]:
        print('  !! 대상/RH 가 등록된 18작업이 아닙니다. 중단합니다.', flush=True)
        sys.exit(1)
    for p, label in ((rw.CHARGED, '전하 CIF 폴더'), (rw.WATER_DEF, '물 정의')):
        if not os.path.exists(p):
            print(f'  !! {label} 없음: {p}', flush=True)
            sys.exit(1)
    missing = [n for n, _ in rw.TARGETS
               if not os.path.exists(os.path.join(rw.CHARGED, n + '_DDEC6.cif'))]
    if missing:
        print(f'  !! 전하 CIF 없음: {" ".join(missing)}', flush=True)
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

    # 기기명 사본. 병합 도구가 파일명에서 출처를 읽으므로(machine_of) 태그가
    # 없으면 거부됩니다 — 08-23 에 태그 없는 파일이 자기 자신과 교차 검증
    # 쌍을 이루는 것을 막으려 넣은 규약입니다.
    src = os.path.join(rw.HERE, 'water_results.json')
    if rc == 0 and os.path.exists(src):
        tag = os.environ.get('WATER_BATCH_TAG') or os.uname().nodename.lower()
        shutil.copy(src, os.path.join(rw.HERE, f'water_results_{tag}.json'))
        print(f'  기기명 사본 저장: water_results_{tag}.json', flush=True)

    sys.exit(rc)
