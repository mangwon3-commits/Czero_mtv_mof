"""습윤 작업 용량 v4 — sa50nb50 (데스크탑 몫). 검증된 grid 래퍼 패턴."""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import run_humid_wc_v3 as _v3  # noqa: F401,E402
import run_humid_wc as hw      # noqa: E402
V4 = os.path.join(HERE, "v4_humid_wc"); os.makedirs(V4, exist_ok=True)
hw.RUNS = os.path.join(HERE, "humid_wc_runs_v4m1")
hw.RESULT = os.path.join(V4, "humid_working_capacity_v4m1.json")
hw.TARGETS = ["sa50nb50"]
hw.MAX_WORKERS = int(os.environ.get("HWC_V4M1_WORKERS", "3"))
if __name__ == "__main__":
    for k in ("CHARGED", "RUNS", "RESULT", "TARGETS"): print(f"  {k:<8} {getattr(hw,k)}", flush=True)
    assert hw.CHARGED.endswith("charged_v3") and hw.RUNS.endswith("v4m1")
    if not os.path.exists(os.path.join(hw.CHARGED, "sa50nb50_DDEC6.cif")):
        print("  !! 전하 파일 없음"); sys.exit(1)
    sys.exit(hw.main())
