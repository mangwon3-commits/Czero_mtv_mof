"""밀도맵 v3 **빈칸 메움** — `saIm0583` · `mslm050` (2026-09-23, 사용자 지시 "넣어").

[왜 이 둘인가]
  `density_v3/`(base·saIm025·saIm050·saIm075·saIm100·nbIm025)와 `density_v3_nbim/`(nbIm050·075·100)로
  **사다리 둘은 덮였는데** 정작 오늘 확정된 두 결론의 주인공이 빠져 있었습니다.

    saIm0583   §AU 의 **정체점 그 자체** — "술폰산 사다리는 58 %에서 멈춘다"(ENS298_SAIM075E_VERDICT).
               지금 격자는 saIm050 과 saIm075 를 건너뛰므로 **왜 거기서 멈추는지**를 그림으로 못 보입니다.
    mslm050    선택도 58.1 · Q_st 33.8 — saIm 다음으로 좋은 계열의 대표인데 격자가 하나도 없습니다.

[규약 — 하나도 안 바꿉니다]
  `run_density_v3.py` 와 **같은 물리**: 0.15 bar · 298 K · 초기화 2,000 + 생산 5,000 ·
  90³ 격자 · DDEC6 전하 · 전하 ON/OFF 짝. 그래야 `density_v3/` 격자와 **같은 자**로 견줍니다.
  ⚠ 사이클이 CLAUDE.md §1 표와 다른 것은 의도입니다 — 2,000+5,000 은 **밀도맵 규약**이고
  v1·v2·v3 격자가 전부 그것으로 돌았습니다(MECHANISM_VERDICT_20260905 머리말).

[출력을 가르는 이유]
  `density_v3/` 는 **등록된 6조성**의 자리입니다(그 README 와 MECHANISM 판정문이 그 6을 가리킴).
  거기에 둘을 더 넣으면 "등록 덱이 8이었다" 로 읽힙니다. `density_v3_nbim/` 이 같은 이유로
  갈라져 있고, 이 래퍼도 그 전례를 따릅니다.

[대상을 환경변수로 안 주는 이유]
  `run_density_v3.py` 주석 그대로 — 09-04 에 랩탑이 덱을 환경변수로만 주다가 재기동에서
  **말없이 다른 덱으로** 떴습니다. 덱은 파일에 박고, 기동 때 찍습니다.
"""
import os
import sys

import run_density_map as rd

REAL = os.path.dirname(os.path.abspath(__file__))
GAP = os.path.join(REAL, "density_v3_gap")
os.makedirs(GAP, exist_ok=True)

rd.HERE = GAP
rd.OUT = GAP
rd.CHARGED = os.path.join(REAL, "charged_v3")
rd.MAX_WORKERS = int(os.environ.get("DENSITY_GAP_WORKERS", "6"))
rd.TARGETS = ["saIm0583", "mslm050"]          # ← 덱은 여기 있습니다. 바꾸려면 이 줄을 고치십시오.

if __name__ == "__main__":
    print("밀도맵 v3 빈칸 메움 (GFN-FF 셀 고정 이완 + DDEC6)", flush=True)
    print(f"  입력   {rd.CHARGED}", flush=True)
    print(f"  출력   {rd.OUT}", flush=True)
    print(f"  결과   {os.path.join(rd.HERE, 'density_results.json')}", flush=True)
    print(f"  워커   {rd.MAX_WORKERS}", flush=True)
    print(f"  대상   {len(rd.TARGETS)}종 {rd.TARGETS}  × 전하 ON/OFF = {2*len(rd.TARGETS)}작업", flush=True)
    for t in rd.TARGETS:
        cif = os.path.join(rd.CHARGED, t + "_DDEC6.cif")
        if not os.path.exists(cif):
            print(f"  !! 전하 CIF 없음: {cif}", flush=True)
            sys.exit(2)
    sys.exit(rd.main())
