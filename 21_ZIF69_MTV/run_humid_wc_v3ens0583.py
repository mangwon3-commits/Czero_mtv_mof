"""습윤 작업 용량 — saIm0583 앙상블 e1~e5 (15작업). 헤드라인 수치의 오차막대.

[무엇을 재는가 — 지금 우리 결론의 가장 약한 자리]
    제약 하 1위 saIm0583 의 습윤 TSA 작업 용량 **0.8328 ± 0.0252 mol/kg**
    (모체 대비 +77%)가 최종 보고의 헤드라인입니다. 그런데 그 값은 **배치
    하나에서 나온 것**입니다.

    "배치(realization)" 란 같은 조성이라도 24 개 치환 가능 자리 중 **어느
    14 자리를 골랐는가**가 다른 구조입니다. 08-23 에 측정된 바로는:

        같은 조성 6 실현의 건조 로딩 산포  s_ens  = 0.0963 mol/kg (8.1%)
        조성 4 종의 건조 로딩 산포         s_comp = 0.0375 mol/kg (2.8%)
        -> 배치가 조성보다 2.57 배 크게 움직인다

    **즉 헤드라인의 ± 0.0252 는 몬테카를로 통계 오차일 뿐, 배치를 바꿨을 때
    얼마나 움직이는지는 아무도 재지 않았습니다.** 8% 산포가 습윤 WC 에도
    그대로 실린다면 실제 불확실도는 지금 적힌 것의 몇 배입니다.

    이 15 작업이 그것을 직접 냅니다. e1~e5 각각의 습윤 TSA WC 를 구해
    표본 표준편차 s_wc 를 보면 됩니다.

[사전 등록 — 수를 보기 전에 고정합니다]
    비교 대상은 조성 간 습윤 WC 산포입니다. 현재 확정값으로

        saIm0583 0.8328 · saIm050 0.7680 · sa50nb50 0.6930
        ms50nb50 0.6257 · sa25nb75 0.5999
        표본 SD  s_comp_wc = 0.0949 mol/kg  (n-1, n=5)

    판정:

        s_wc <  s_comp_wc / 1.5 = 0.0633   -> 배치 영향이 조성 차이보다 작다.
                                              조성 간 습윤 WC 순위 유지
        s_wc >= s_comp_wc                  -> 배치가 조성만큼 움직인다.
                                              **헤드라인에 배치 오차 병기 필수**
        그 사이                            -> 병기하되 순위는 유지

    어느 쪽이 나오든 결론입니다. 순위가 죽어도 그것이 답입니다 — 08-23 에
    유지율 순위가 같은 이유로 보류된 전례가 있습니다.

[왜 15 작업 전부인가]
    습윤 WC 는 ads/tsa/vsa 세 조건의 조합이라 하나만 빼도 WC 가 안 나옵니다.
    5 실현 x 3 조건 = 15 가 최소입니다.

[엔진·규약]
    run_humid_wc_v3grid.py 계열과 같은 방식입니다 — run_humid_wc 의 모듈
    전역만 갈아끼우고 그 main() 을 그대로 부릅니다. 물 분압 2852.1 Pa 고정,
    사이클·힘장·전하·물 정의를 한 글자도 바꾸지 않습니다. 그래야 위 표의
    다섯 조성과 같은 자 위에 놓입니다.

[출력을 왜 분리하나]
    v3_humid_wc/ 는 **조성 축**의 답이 모이는 곳입니다. 앙상블은 같은 조성의
    다른 실현이라 **배치 축**입니다. 같은 파일에 넣으면 나중에 표가
    saIm0583e1~e5 를 조성 5 종으로 읽어, 조성 비교표에 배치 반복이 섞입니다 —
    정확히 지금 걸러내려는 혼동을 표가 만들어 냅니다.

사용:
    HWC_ENS_WORKERS=8 python run_humid_wc_v3ens0583.py
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import run_humid_wc_v3 as _v3          # noqa: F401,E402  (v3 배선)
import run_humid_wc as hw              # noqa: E402

ENS = os.path.join(HERE, "v3_humid_wc_ens")
os.makedirs(ENS, exist_ok=True)

hw.RUNS = os.path.join(HERE, "humid_wc_runs_v3ens0583")
hw.RESULT = os.path.join(ENS, "humid_working_capacity_ens0583.json")
hw.TARGETS = ["saIm0583e1", "saIm0583e2", "saIm0583e3",
              "saIm0583e4", "saIm0583e5"]
hw.MAX_WORKERS = int(os.environ.get("HWC_ENS_WORKERS", "8"))

if __name__ == "__main__":
    print("습윤 작업 용량 — saIm0583 앙상블 e1~e5 (15작업)", flush=True)
    for k in ("CHARGED", "RUNS", "RESULT", "TARGETS", "MAX_WORKERS"):
        print(f"  {k:<8} {getattr(hw, k)}", flush=True)

    assert hw.CHARGED.endswith("charged_v3")
    assert hw.RUNS.endswith("v3ens0583") and hw.RESULT.endswith("ens0583.json")
    if len(hw.TARGETS) != 5:
        print("  !! 앙상블 5실현이 아닙니다. 중단합니다.", flush=True)
        sys.exit(1)
    missing = [t for t in hw.TARGETS
               if not os.path.exists(os.path.join(hw.CHARGED, t + "_DDEC6.cif"))]
    if missing:
        print(f"  !! 전하 CIF 없음: {' '.join(missing)}", flush=True)
        sys.exit(1)
    # 물 정의가 5자리인지 확인합니다. 배포본 TraPPE/water.def 는 3자리라
    # 조용히 다른 물로 계산됩니다 — 실패가 결과처럼 보이는 그 유형입니다.
    wd = getattr(hw, "WATER_DEF", None)
    if wd and os.path.exists(wd):
        nsite = sum(1 for ln in open(wd, encoding="utf-8")
                    if len(ln.split()) > 4 and ln.split()[1] in ("Ow", "Hw", "Lw"))
        print(f"  물 정의 사이트 {nsite}개 (TIP5P-Ew 는 5)", flush=True)
        if nsite != 5:
            print("  !! 5자리 물이 아닙니다. 중단합니다.", flush=True)
            sys.exit(1)
    print(flush=True)
    sys.exit(hw.main())
