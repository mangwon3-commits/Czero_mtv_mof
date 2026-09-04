"""습윤 작업 용량 v4 — sa25nb75 + ms50nb50 (외부 16코어 몫). grid 래퍼 패턴.

사용 (꾸러미 루트에서):
    cd 21_ZIF69_MTV
    export RASPA_DIR=$HOME/RASPA/simulations
    HWC_V4E_WORKERS=6 python -u run_humid_wc_v4ext.py 2>&1 | tee humid_v4ext.log
완료 파일: v4_humid_wc/humid_working_capacity_v4ext.json (+ 로그) 를 회신.
"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import run_humid_wc_v3 as _v3  # noqa: F401,E402
import run_humid_wc as hw      # noqa: E402
V4 = os.path.join(HERE, "v4_humid_wc"); os.makedirs(V4, exist_ok=True)
hw.RUNS = os.path.join(HERE, "humid_wc_runs_v4ext")
hw.RESULT = os.path.join(V4, "humid_working_capacity_v4ext.json")
hw.TARGETS = ["sa25nb75", "ms50nb50"]
hw.MAX_WORKERS = int(os.environ.get("HWC_V4E_WORKERS", "6"))
if __name__ == "__main__":
    for k in ("CHARGED", "RUNS", "RESULT", "TARGETS"): print(f"  {k:<8} {getattr(hw,k)}", flush=True)
    assert hw.CHARGED.endswith("charged_v3") and hw.RUNS.endswith("v4ext")
    miss = [t for t in hw.TARGETS if not os.path.exists(os.path.join(hw.CHARGED, t + "_DDEC6.cif"))]
    if miss: print(f"  !! 전하 파일 없음: {miss}"); sys.exit(1)
    sys.exit(hw.main())
