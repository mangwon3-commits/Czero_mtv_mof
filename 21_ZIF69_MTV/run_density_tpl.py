"""밀도맵 — 형판 Zn(bib)(bdtdc) 모체 · 4,8-치환체 **건조**(CO₂ 단성분, 전하 ON/OFF) — E-28 (2026-09-26).

[왜]
  사용자 09-26 01:1x: "형판 모체-치환별 건조-습윤 밀도맵 VTK 가 없다 — 포스터 figure 에 필요".
  E-23 전체 목록 1·2위(4,8-(CH₃)₂ · 4,8-(CN)₂)와 그 모체에 **격자가 하나도 없었습니다.**
  F · NO₂ 는 대조(E-24 "4,8-자리 S_ON 보존은 법칙이 아님" — F ↓ · NO₂ = · CN ↑ · CH₃ ↑↑)입니다.

[규약 — 하나도 안 바꿉니다]
  `run_density_v3_gap.py` 와 같은 방식 — `run_density_map` 을 **수정 없이** import 하고 경로 · 덱만 옮깁니다.
  0.15 bar · 298 K · 초기화 2,000 + 생산 5,000(**밀도맵 규약**, CLAUDE.md §1 표와 다른 것은 의도) ·
  90³ 격자 · DDEC6 전하(`charged_v3/`, E-22b · E-24 Widom 과 같은 CIF) · 전하 ON/OFF 짝.
  셀 복제는 최소상 규약이 정합니다 — 이 형판은 **1×2×3**(단사 β 99.61°). 격자는 그 슈퍼셀 위에 있으므로
  단위셀로 접을 때 **셀 행렬**을 쓰십시오(`density_v3/README.md` 주의 절).

[출력을 가르는 이유]
  `density_v3/` · `density_v3_nbim/` · `density_v3_gap/` 전례 — 등록 덱이 섞이지 않게 폴더를 가릅니다.

[덱을 환경변수로 안 주는 이유] `run_density_v3_gap.py` 와 같음 — 덱은 파일에 박고 기동 때 찍습니다.
"""
import os
import sys

import run_density_map as rd

REAL = os.path.dirname(os.path.abspath(__file__))
TPL = os.path.join(REAL, "density_v3_tpl")
os.makedirs(TPL, exist_ok=True)

rd.HERE = TPL
rd.OUT = TPL
rd.CHARGED = os.path.join(REAL, "charged_v3")
rd.MAX_WORKERS = int(os.environ.get("DENSITY_TPL_WORKERS", "5"))
# 결승 셋 먼저, 대조 둘 뒤 — ex.map 이 이 순서로 워커에 넣습니다.
rd.TARGETS = ["e22_parent", "e24_ch3_100", "e24_cn_100", "e24_f_100", "e22_no2_100"]

if __name__ == "__main__":
    print("밀도맵 E-28 건조 — 형판 Zn(bib)(bdtdc) 모체 · 4,8-치환체", flush=True)
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
