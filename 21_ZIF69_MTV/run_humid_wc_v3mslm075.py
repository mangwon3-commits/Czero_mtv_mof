"""습윤 작업 용량 v3 — mslm075 한 종 (건조 스크린 비-saIm 최고).

[왜 이 조성인가 — 물 축이 saIm 계열에만 걸려 있었다]
    건조 스크린은 9계열 31구조를 봤고 saIm 이 4.9배(배치 SD 대비)로 이겼다.
    그런데 **물 축은 saIm 계열에만 걸렸다.** 물이 실제 관문이었고, v4 혼합
    결과는 물 축이 건조 순위와 다르게(거의 역순으로) 정렬됨을 보여 준다.

        건조 Qst 순위        물 축
        1  saIm100  34.01     있음
        2  saIm075  31.42     있음
        3  saIm050  29.51     있음
        4  mslm075  29.01     **없음**  <- 비-saIm 최고
        5  nbIm100  28.87     **없음**

    mslm075 는 건조 WC 가 이미 있다(v3_wc/working_capacity.json). 습윤
    3작업이면 비-saIm 계열 최상위가 처음으로 물 축에 오르고, ms50nb50
    (mslm+nbIm 반반)의 유지율 1위(91.91%)가 **화학 때문인지 혼합 때문인지**
    를 가르는 첫 단서가 된다.

[왜 배치 대조군 판정과 무관한가]
    mtv_cif_builder.py:800-825 에서 모체 clIm_aryl 는 subs 에 안 들어간다.
    mslm075 = {clIm_aryl: 0.25, mslm_aryl: 0.75} 이므로 len(subs)==1 이고
    **이미 충돌 회피 배치**다. 판정이 어느 쪽이든 버릴 일이 없다.

[배선]
    run_humid_wc_v3grid.py / run_humid_wc_v3g0583.py 와 같은 패턴이다.
    다른 것은 대상·폴더·결과 파일뿐이고 규약(물 분압 2852.1 Pa 고정,
    ads/tsa/vsa)은 그대로 — 같은 표에 놓아야 하므로.

[사전 등록] 21_ZIF69_MTV/ASSIGN_36H_20260826.md 3-2 절
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import run_humid_wc_v3 as _v3          # noqa: F401,E402  (v3 배선)
import run_humid_wc as hw              # noqa: E402

V3 = os.path.join(HERE, "v3_humid_wc")
os.makedirs(V3, exist_ok=True)

hw.RUNS = os.path.join(HERE, "humid_wc_runs_v3mslm075")
hw.RESULT = os.path.join(V3, "humid_working_capacity_mslm075.json")
hw.TARGETS = ["mslm075"]
hw.MAX_WORKERS = int(os.environ.get("HWC_MSLM075_WORKERS", "3"))

if __name__ == "__main__":
    print("습윤 작업 용량 v3 — mslm075 (건조 스크린 비-saIm 최고)", flush=True)
    for k in ("CHARGED", "RUNS", "RESULT", "TARGETS", "MAX_WORKERS"):
        print(f"  {k:<8} {getattr(hw, k)}", flush=True)
    assert hw.CHARGED.endswith("charged_v3")
    assert hw.RUNS.endswith("mslm075") and hw.RESULT.endswith("mslm075.json")
    if not os.path.exists(os.path.join(hw.CHARGED, "mslm075_DDEC6.cif")):
        print("  !! 전하 파일 없음", flush=True); sys.exit(1)
    print(flush=True)
    sys.exit(hw.main())
