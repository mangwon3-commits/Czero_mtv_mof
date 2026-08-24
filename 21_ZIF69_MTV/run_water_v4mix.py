"""수분 경쟁 — v4 혼합 링커 3종 (sa50nb50 / sa25nb75 / ms50nb50), 12작업.

[왜 이것이 비어 있나]
    v4 혼합 조성은 습윤 작업 용량(v4_humid_wc/)까지 났는데 **RH 스캔이
    없습니다.** 그래서 사전 등록된 수분 관문(RH90 유지율 >=80 유효 /
    50~80 조건부 / <50 종료)을 v4 조성에 **한 번도 적용한 적이 없습니다.**

    v3 단일 치환에서 나온 결론은 "58.3~66.7% 구간에서 유지율이 조성 선택
    근거가 못 된다"였습니다(08-23 판정). 그 구간에서 유지율이 평평하다면,
    남은 자유도는 **무엇으로 치환하느냐**입니다 — 그것이 v4 혼합입니다.
    이 러너가 그 축에 같은 자를 댑니다.

[왜 새 엔진을 쓰지 않는가]
    run_water_v3grid.py 와 같은 방식입니다 — run_water 의 모듈 전역만
    갈아끼우고 그 main() 을 그대로 부릅니다. 엔진·규약·사이클·힘장·물
    정의·압력을 한 글자도 바꾸지 않습니다. 그래야 v3 격자 16점과 v4 12점을
    같은 표에 놓을 수 있습니다.

[출력을 왜 분리하나]
    v3_water_grid/ 에 쓰면 이어받기가 v3 격자와 섞습니다. 규약이 같아 값은
    맞지만 어느 캠페인이 낸 값인지 되돌릴 수 없습니다. 기기 태그가 붙은
    사본만 공유하고, 합치는 것은 merge_water_batches.py 가 검산하며 합칩니다.

사용:
    WATER_V4_WORKERS=<물리코어수> python run_water_v4mix.py
"""
import os
import sys

import run_water as rw

REAL = os.path.dirname(os.path.abspath(__file__))
V4W = os.path.join(REAL, 'v4_water_mix')
os.makedirs(V4W, exist_ok=True)

rw.HERE = V4W
rw.CHARGED = os.path.join(REAL, 'charged_v3')
rw.RUNS = os.path.join(REAL, 'water_runs_v4mix')
rw.WATER_DEF = os.path.join(REAL, '..', '19_WaterCompetition', 'water.def')
rw.MAX_WORKERS = int(os.environ.get('WATER_V4_WORKERS', '4'))

# v4 혼합 링커 3종. 전하 CIF 는 08-21 에 이미 났습니다(charged_v3/).
rw.TARGETS = [
    ('sa50nb50', 'SO3H 50% + NO2 50% — 혼합, 술폰산 절반'),
    ('sa25nb75', 'SO3H 25% + NO2 75% — 혼합, 술폰산 소수'),
    ('ms50nb50', 'SO2CH3 50% + NO2 50% — 술폰 대신 메틸술폰'),
]

if __name__ == '__main__':
    print('수분 경쟁 — v4 혼합 링커 3종 (12작업)', flush=True)
    print(f'  입력   {rw.CHARGED}', flush=True)
    print(f'  작업   {rw.RUNS}', flush=True)
    print(f'  결과   {os.path.join(rw.HERE, "water_results.json")}', flush=True)
    print(f'  워커   {rw.MAX_WORKERS}', flush=True)
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
