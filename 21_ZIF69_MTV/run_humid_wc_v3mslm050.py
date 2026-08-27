"""습윤 작업 용량 v3 — mslm050 한 종. **관문 통과 상대의 승자 지표.**

[사전 등록] 21_ZIF69_MTV/MSLM050_CHALLENGE_20260827.md

[왜 이 조성인가 — 관문을 통과하는 상대를 승자 지표로 재 본 적이 없다]
    관문(LCD 감소 20%)을 통과하는 치환 조성은 여섯뿐이고 그중 mslm 은
    mslm025 와 **mslm050** 둘입니다. mslm050 은 **LCD 감소 6.68% 로 치환
    조성 중 관문 여유가 가장 큽니다.**

    08-27 에 잰 mslm075 는 **관문 탈락**(21.67%)이라 "상대에게 최선을 준"
    형태로만 쓸 수 있고, **관문 통과 상대를 이겼다는 뜻이 아닙니다.**

[왜 위협인가]
    우리 승자의 치환기(-SO3H)가 하필 물을 가장 많이 끕니다(모체 대비 2.93배).
    습윤에서 그것은 부채입니다. mslm050 은 -OH 가 없어 물을 덜 끌고
    **건조 로딩이 이미 saIm0583 6실현 평균보다 높습니다**(1.2431 대 1.1623).

    mslm075 성질을 얹은 추정이 WC 0.77~0.82 인데 saIm0583 6실현 평균은
    0.7306 입니다. **넘으면 1등이 바뀝니다.** 추정이지 측정이 아닙니다.

[배선] run_humid_wc_v3mslm075.py 와 같습니다. 규약(물 분압 2852.1 Pa 고정,
ads/tsa/vsa, 사이클 15,000)은 그대로 — 같은 표에 놓아야 하므로.
"""

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import run_humid_wc_v3 as _v3          # noqa: F401,E402  (v3 배선)
import run_humid_wc as hw              # noqa: E402

V3 = os.path.join(HERE, "v3_humid_wc")
os.makedirs(V3, exist_ok=True)

hw.RUNS = os.path.join(HERE, "humid_wc_runs_v3mslm050")
hw.RESULT = os.path.join(V3, "humid_working_capacity_mslm050.json")
hw.TARGETS = ["mslm050"]
hw.MAX_WORKERS = int(os.environ.get("HWC_MSLM050_WORKERS", "3"))

if __name__ == "__main__":
    print("습윤 작업 용량 v3 — mslm050 (건조 스크린 비-saIm 최고)", flush=True)
    for k in ("CHARGED", "RUNS", "RESULT", "TARGETS", "MAX_WORKERS"):
        print(f"  {k:<8} {getattr(hw, k)}", flush=True)
    assert hw.CHARGED.endswith("charged_v3")
    assert hw.RUNS.endswith("mslm050") and hw.RESULT.endswith("mslm050.json")
    if not os.path.exists(os.path.join(hw.CHARGED, "mslm050_DDEC6.cif")):
        print("  !! 전하 파일 없음", flush=True); sys.exit(1)
    print(flush=True)
    sys.exit(hw.main())
