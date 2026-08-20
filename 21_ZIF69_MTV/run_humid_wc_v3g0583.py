"""습윤 작업 용량 v3 — saIm0583 한 종 (제약 하 1위 판정용 보강, 랩탑용).

run_humid_wc_v3grid.py(검증된 배선, 데스크탑 연기 시험 통과)와 같은
패턴이다. 다른 것은 대상·폴더·결과 파일뿐이다. 규약(물 분압 2852.1 Pa
고정, ads/tsa/vsa)은 그대로 -- 같은 표에 놓아야 하므로.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import run_humid_wc_v3 as _v3          # noqa: F401,E402  (v3 배선)
import run_humid_wc as hw              # noqa: E402

V3 = os.path.join(HERE, "v3_humid_wc")
os.makedirs(V3, exist_ok=True)

hw.RUNS = os.path.join(HERE, "humid_wc_runs_v3g0583")
hw.RESULT = os.path.join(V3, "humid_working_capacity_g0583.json")
hw.TARGETS = ["saIm0583"]
hw.MAX_WORKERS = int(os.environ.get("HWC_G0583_WORKERS", "3"))

if __name__ == "__main__":
    print("습윤 작업 용량 v3 — saIm0583 (경계 생존자 보강)", flush=True)
    for k in ("CHARGED", "RUNS", "RESULT", "TARGETS", "MAX_WORKERS"):
        print(f"  {k:<8} {getattr(hw, k)}", flush=True)
    assert hw.CHARGED.endswith("charged_v3")
    assert hw.RUNS.endswith("g0583") and hw.RESULT.endswith("g0583.json")
    if not os.path.exists(os.path.join(hw.CHARGED, "saIm0583_DDEC6.cif")):
        print("  !! 전하 파일 없음", flush=True); sys.exit(1)
    print(flush=True)
    sys.exit(hw.main())
