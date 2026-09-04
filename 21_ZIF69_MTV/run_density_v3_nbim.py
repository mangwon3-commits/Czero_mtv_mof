"""−NO₂ 사다리 전하 ON/OFF — §1-5 (2026-09-05 04:3x 등록, 결과 전).

[왜]
    §1(`MECHANISM_VERDICT_20260905.md`)이 −SO₃H 사다리에서 **정전기 지배**
    (f = 0.71~0.85)를 확정했습니다. 그때 T-4 대상으로 끼워 넣은 `nbIm025`
    한 점이 **f = 0.429(혼합)** 이고 정전기 몫이 base 와 **동일한 42.8%** 였습니다.
    같은 "극성 치환기" 인데 이득의 성격이 다르다는 뜻인데, **한 점이라 판정으로
    쓸 수 없었습니다.** 사다리로 만들면 판정이 됩니다.

[판정 — 새로 만들지 않습니다]
    `ASSIGN_20260905.md` §1-3 의 f 문턱을 **그대로** 씁니다:
        f = Δ_정전기 / Δ_total,  Δ 는 전부 base 대비
        f ≥ 0.7 정전기 지배 / f ≤ 0.3 설명 안 됨 / 사이 혼합
        사다리 4점(025·050·075·100) 전부 같은 구간일 때만 판정.
        갈리면 "치환율 의존". ± 전파해 경계 걸치면 유보. 생산 실현 1개라
        조성 간 f 의 소수점 비교 금지 — 구간 판정만
    **문턱도 자도 새로 만들지 않았습니다.** 대상 집합만 −NO₂ 로 옮긴 것입니다.

[대상] nbIm050 · nbIm075 · nbIm100 (3종 × ON/OFF = 6작업)
    `nbIm025` 와 `base` 는 §1 에서 이미 돌았으므로 `density_v3/` 값을 씁니다.

[출력을 분리하는 이유]
    `run_density_map.main()` 이 결과를 `rd.HERE/density_results.json` 에 씁니다.
    `HERE` 를 `density_v3` 로 두면 **§1 의 결과 파일을 덮어씁니다** — 08-27 에
    조성 필터된 러너가 공용 결과를 덮은 사고와 같은 자리입니다. 별도 디렉터리로
    보냅니다.

[등록 덱 값은 파일 기본값에 둡니다] 환경변수로만 주면 다음 기동에서 조용히
    달라집니다(09-04 랩탑 N=512 사고). 기동 시 덱을 찍는 것도 같은 이유입니다.
"""
import os
import sys

import run_density_map as rd

REAL = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(REAL, "density_v3_nbim")
os.makedirs(OUT, exist_ok=True)

rd.HERE = OUT
rd.OUT = OUT
rd.CHARGED = os.path.join(REAL, "charged_v3")
rd.MAX_WORKERS = int(os.environ.get("DENSITY_NBIM_WORKERS", "6"))
rd.TARGETS = ["nbIm050", "nbIm075", "nbIm100"]      # 등록 대상 — 파일 기본값

if __name__ == "__main__":
    print("−NO₂ 사다리 전하 ON/OFF (§1-5, 2026-09-05 등록)", flush=True)
    print(f"  입력   {rd.CHARGED}", flush=True)
    print(f"  출력   {rd.OUT}   (§1 의 density_v3/ 를 덮지 않습니다)", flush=True)
    print(f"  대상   {len(rd.TARGETS)}종 {rd.TARGETS}  x ON/OFF = {len(rd.TARGETS)*2}작업",
          flush=True)
    print(f"  사이클 초기화 {rd.INIT} + 생산 {rd.CYCLES}, 격자 {rd.GRID}^3 "
          f"(밀도맵 규약 — CLAUDE.md §1 흡착 표와 다름, v1·v2 비교선)", flush=True)
    print(f"  워커   {rd.MAX_WORKERS}", flush=True)
    print("  판정   ASSIGN_20260905 §1-3 의 f 문턱 그대로. 새 문턱 없음", flush=True)
    missing = [t for t in rd.TARGETS
               if not os.path.exists(os.path.join(rd.CHARGED, t + "_DDEC6.cif"))]
    if missing:
        print(f"  !! charged_v3 에 없음: {missing}", flush=True)
        sys.exit(1)
    sys.exit(rd.main())
