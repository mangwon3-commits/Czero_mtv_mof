"""수분 경쟁 — saIm0583 앙상블 e1~e5, RH0/RH90 만 (10작업).

[무엇을 재는가 — 이것은 조성 비교가 아닙니다]
    07437de 가 조성 간 순위를 보류했습니다. 이유는 배치 산포가 조성 간
    산포보다 큽니다:

        건조 로딩  s_ens = 0.0963 (8.1%)   같은 조성 6실현
                   s_comp = 0.0375 (2.8%)  조성 4종
                   -> 배치가 조성보다 2.57배 크게 움직인다

    그런데 **유지율은 같은 구조 안의 비율이라 배치 분산이 부분 상쇄**됩니다.
    RH0 이 높게 나온 실현은 RH90 도 높게 나올 것이므로 비율에서 상쇄됩니다.
    상쇄가 얼마나 되는지가 미측정이라 관문 판정(유효/조건부/종료)만 쓰고
    조성 간 순위는 보류한 상태입니다.

    이 10작업이 그 상쇄 비율을 **직접** 냅니다. e1~e5 각각의 유지율을 구해
    그 표준편차 s_ret 을 보면 됩니다:

        s_ret 이 작다  -> 상쇄가 크다 -> 조성 간 유지율 비교가 살아난다
        s_ret 이 크다  -> 상쇄가 작다 -> 유지율 순위도 보류가 맞았다

    어느 쪽이 나오든 결론입니다. **판정 기준을 결과를 보고 정하지 않도록,
    무엇을 하겠다는 것을 먼저 적습니다** (COMMS/desktop.md 08-23 20:xx 항목):

        조성 4종 유지율 (RH90/RH0 에서 직접 계산, 반올림값 아님)
            saIm0583 75.900 · saIm0625 71.733
            saIm0667 75.055 · saIm0875 74.538
            평균 74.307 · 표본SD s_comp_ret = 1.805 pp (n-1, n=4)

        s_ret < s_comp_ret / 1.5 = 1.204 pp -> 조성 간 유지율 비교 재개 근거
        그 외                                -> 보류 유지

    문턱 1.204 pp 는 계산 전에 고정됐습니다. 0625·0667 로딩은 랩탑 우편함
    산문에서 왔지만 산문에 빠진 것은 err·H2O 이고 로딩은 확정값이라 랩탑
    JSON 이 와도 이 네 유지율은 바뀌지 않습니다.

[왜 RH0/RH90 만인가]
    상쇄 비율에 필요한 것은 유지율뿐이고 유지율은 RH90/RH0 입니다. RH25/50 은
    계단 모양을 보는 데 쓰이지 이 질문에는 안 쓰입니다. 5실현 x 4단계 =
    20작업이면 RH25/50 이 10작업을 더 먹는데, 그 10작업은 이 질문에 답하지
    않습니다.

[왜 결과를 격자와 다른 폴더에 쓰는가]
    v3_water_grid/ 는 **조성 격자**의 답이 모이는 곳입니다. 앙상블은 같은
    조성의 다른 실현이라 조성 축이 아니라 배치 축입니다. 같은 파일에 넣으면
    merge_water_batches.py 가 saIm0583e1..e5 를 조성 5종으로 읽고 유지율
    표에 나란히 찍습니다 — 조성 비교표에 배치 반복이 섞여 들어가는 것이라
    정확히 지금 걸러내려는 혼동을 표가 만들어 냅니다.

    v3_water_ens/ 로 분리하면 merge 도구의 세대 검사('v3_water' 로 잡힘)가
    격자와의 병합을 **거부**합니다. 그것이 맞는 동작입니다.

[엔진·규약]
    run_water_v3grid.py 를 import 해 경로·물 정의·워커 수를 물려받고
    TARGETS 와 RH_LIST 만 바꿉니다. 사이클·힘장·CO2 모델·물 정의·압력이
    한 글자도 다르지 않습니다 (CLAUDE.md 1 절).

[작업 길이 — LPT 를 절반만 얻습니다]
    RH90 이 RH0 보다 5.4배 깁니다(Junseok 실측: 2.11h vs 11.48h). RH_LIST 를
    [0.90, 0.0] 으로 놓아 각 구조 안에서 비싼 것을 먼저 넣습니다
    (CLAUDE.md 5 절).

    다만 run_water.py:295 의 작업 생성이 **구조 우선**이라
    [e1/90, e1/0, e2/90, e2/0, ...] 순이 됩니다. RH90 5개를 앞에 모으는
    완전한 LPT 는 RH_LIST 만으로는 안 됩니다. 6워커 실제 진행:

        t=0     e1/90 e1/0 e2/90 e2/0 e3/90 e3/0  (RH90 3개 + RH0 3개)
        t=2.1   RH0 셋 끝 -> e4/90, e4/0, e5/90 착수
        t=4.2   e4/0 끝 -> e5/0 착수
        t=13.6  e4/90, e5/90 끝  <- makespan

    **약 13.6시간**입니다. 완전 LPT 면 11.5시간이라 2.1시간 차이인데, 그것을
    얻으려면 run_water.py 의 작업 생성 순서를 건드려야 합니다. 그 파일은
    다른 러너 넷이 공유하므로 2시간 때문에 바꾸지 않습니다. 기기에 6일
    여유가 있어 꼬리가 문제되지 않습니다.

사용:
    WATER_BATCH_TAG=junseok WATER_V3_WORKERS=6 python run_water_v3ens0583.py
"""
import os
import shutil
import sys

import run_water_v3grid  # noqa: F401 — 경로·워커·물 정의 전역을 물려받는다
import run_water as rw

ENS = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'v3_water_ens')
os.makedirs(ENS, exist_ok=True)
rw.HERE = ENS
rw.RUNS = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'water_runs_v3ens')

# 비싼 것 먼저 (LPT). run_water.py:295 가 이 순서대로 큐를 만든다.
rw.RH_LIST = [0.90, 0.0]

rw.TARGETS = [
    ('saIm0583e1', 'SO3H 58.3% 실현 1'),
    ('saIm0583e2', 'SO3H 58.3% 실현 2'),
    ('saIm0583e3', 'SO3H 58.3% 실현 3'),
    ('saIm0583e4', 'SO3H 58.3% 실현 4'),
    ('saIm0583e5', 'SO3H 58.3% 실현 5'),
]

if __name__ == '__main__':
    print('수분 경쟁 — saIm0583 앙상블 e1~e5, RH0/RH90 (10작업)', flush=True)
    print(f'  입력   {rw.CHARGED}', flush=True)
    print(f'  작업   {rw.RUNS}', flush=True)
    print(f'  결과   {os.path.join(rw.HERE, "water_results.json")}', flush=True)
    print(f'  워커   {rw.MAX_WORKERS}', flush=True)
    print(f'  대상   {" ".join(n for n, _ in rw.TARGETS)}', flush=True)
    print(f'  RH     {rw.RH_LIST}  (비싼 RH90 먼저 — LPT)', flush=True)

    if len(rw.TARGETS) != 5:
        print('  !! 앙상블 5실현이 아닙니다. 중단합니다.', flush=True)
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
    # 없으면 거부됩니다 — 2026-08-23 에 태그 없는 파일이 자기 자신과 교차
    # 검증 쌍을 이루는 것을 막으려 넣은 규약입니다.
    src = os.path.join(rw.HERE, 'water_results.json')
    if rc == 0 and os.path.exists(src):
        tag = os.environ.get('WATER_BATCH_TAG') or os.uname().nodename.lower()
        dst = os.path.join(rw.HERE, f'water_results_{tag}.json')
        shutil.copy(src, dst)
        print(f'  기기명 사본 저장: {dst}', flush=True)

    sys.exit(rc)
