"""ZIF-69 v3 density maps: GFN-FF relaxed structures and fresh DDEC6 charges.

This wrapper exists so that the v2 map directory and its results can never be
read or overwritten accidentally.  The physical protocol is deliberately
unchanged: CO2 at 0.15 bar/298 K, 5,000 production cycles, 90^3 VTK grid, and
charge ON/OFF pairs.  Only the host geometry/charge generation changes.
"""
import os
import sys

import run_density_map as rd

REAL = os.path.dirname(os.path.abspath(__file__))
V3 = os.path.join(REAL, "density_v3")
os.makedirs(V3, exist_ok=True)

# HERE is used inside main() to build the JSON path; overriding CHARGED alone
# caused an old-result overwrite in the water workflow, so all derived paths
# are redirected together.
rd.HERE = V3
rd.OUT = V3
rd.CHARGED = os.path.join(REAL, "charged_v3")
rd.MAX_WORKERS = int(os.environ.get("DENSITY_V3_WORKERS", "8"))

# [2026-09-05] 등록 대상에 nbIm025 를 더한다 — T-4 의 등록 대상이
# `nbIm025 · saIm050 · base` 이기 때문이다(DESIGN_STUDY_20260903.md 5-A T-4,
# ASSIGN_20260905.md §1-2).
#
# **환경변수로 주지 않고 파일 기본값에 둔다.** 09-04 에 랩탑이 N_MOL 을 환경변수로만
# 주다가 재기동에서 조용히 다른 덱(N=512)으로 떴습니다 — 등록된 덱 값이 환경변수에만
# 있으면 다음 기동에서 말없이 달라집니다. 기동 시 덱을 찍는 것도 같은 이유입니다.
rd.TARGETS = list(rd.TARGETS) + ["nbIm025"]

if __name__ == "__main__":
    print("밀도맵 v3 (GFN-FF 셀 고정 이완 + DDEC6)", flush=True)
    print(f"  입력   {rd.CHARGED}", flush=True)
    print(f"  출력   {rd.OUT}", flush=True)
    print(f"  결과   {os.path.join(rd.HERE, 'density_results.json')}", flush=True)
    print(f"  워커   {rd.MAX_WORKERS}", flush=True)
    print(f"  대상   {len(rd.TARGETS)}종 {rd.TARGETS}", flush=True)
    print(f"  사이클 초기화 {rd.INIT} + 생산 {rd.CYCLES} (밀도맵 규약, "
          f"CLAUDE.md §1 흡착 표와 다름 — v1·v2 비교선)", flush=True)
    missing = [t for t in rd.TARGETS
               if not os.path.exists(os.path.join(rd.CHARGED, t + "_DDEC6.cif"))]
    if missing:
        print(f"  !! charged_v3 에 없는 조성: {missing}", flush=True)
        sys.exit(1)
    sys.exit(rd.main())
