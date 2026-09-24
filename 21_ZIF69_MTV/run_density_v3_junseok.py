"""밀도맵 v3 — **mslm 사다리 완성 + cf3Im 사다리 신설** (2026-09-24, Junseok 배정).

[왜 이 다섯인가]
  격자가 사다리 단위로 있어야 "치환율을 올리면 CO₂ 자리가 어떻게 변하는가" 를 그림으로 말합니다.
  09-24 07:3x 현재:

      saIm   025 ✓ 050 ✓ 0583 ✓ 075 ✓ 100 ✓      (완성)
      nbIm   025 ✓ 050 ✓ 075 ✓ 100 ✓             (완성)
      mslm   025 —  050 ✓  075 —                  ← **두 칸만 채우면 완성**
      cf3Im  025 —  050 —  075 —                  ← **통째로 비어 있음**

  `mslm` 은 선택도 58.1 로 saIm(150.9) 다음가는 계열이고, `cf3Im` 은 37.5 로 그다음입니다.
  이 다섯이면 **사다리 넷**(saIm·nbIm·mslm·cf3Im)이 그림으로 섭니다.

[규약 — `run_density_v3.py` 와 한 글자도 다르지 않습니다]
  0.15 bar · 298 K · 초기화 2,000 + 생산 5,000 · 90³ 격자 · DDEC6 전하 · 전하 ON/OFF 짝.
  ⚠ 사이클이 CLAUDE.md §1 표와 다른 것은 **의도**입니다 — 2,000+5,000 은 **밀도맵 규약**이고
  v1·v2·v3 격자가 전부 그것으로 돌았습니다(MECHANISM_VERDICT_20260905 머리말).

[Zeo++ 를 안 돕니다 — Junseok 에게 중요합니다]
  `run_density_map.py` 는 RASPA 만 부릅니다(건당 약 471 MB). Zeo++ `network` 호출이 **없습니다.**
  2026-08-27 에 이 기기가 `ZEO_GB_PER_JOB` 을 9.5→4.0 으로 낮춰 3분 만에 global OOM 을 낸 적이
  있는데, **이 배정에는 그 경로가 아예 없습니다.**

[짧은 작업입니다 — 재시작 창 대비]
  이 기기의 Windows 업데이트 일시중지가 09-17 에 만료돼 **02~08시 자동 재시작 창**이 있습니다.
  밀도맵은 작업 하나가 짧고 **조성×전하 단위로 독립**이라, 재시작이 나도 **도는 한 건만** 잃습니다.
  `run_density_map` 의 이어받기가 완주분을 회수합니다.

[출력을 가르는 이유]
  `density_v3/`(등록 6조성)·`density_v3_nbim/`·`density_v3_gap/` 과 같은 전례.
  섞으면 "등록 덱이 몇이었나" 가 흐려집니다.

[대상을 환경변수로 안 주는 이유]
  09-04 에 랩탑이 덱을 환경변수로만 주다가 재기동에서 **말없이 다른 덱으로** 떴습니다.
  덱은 파일에 박고 기동 때 찍습니다.
"""
import os
import sys

import run_density_map as rd

REAL = os.path.dirname(os.path.abspath(__file__))
OUTDIR = os.path.join(REAL, "density_v3_junseok")
os.makedirs(OUTDIR, exist_ok=True)

rd.HERE = OUTDIR
rd.OUT = OUTDIR
rd.CHARGED = os.path.join(REAL, "charged_v3")
# 물리 6 / 논리 12 · SMT 이득 실측 6→10 워커 +55 %(등록부). 건당 약 471 MB 라 24 GiB 에 여유.
rd.MAX_WORKERS = int(os.environ.get("DENSITY_JUNSEOK_WORKERS", "10"))
rd.TARGETS = ["mslm025", "mslm075", "cf3Im025", "cf3Im050", "cf3Im075"]   # ← 덱은 여기입니다.

if __name__ == "__main__":
    print("밀도맵 v3 — mslm 완성 + cf3Im 신설 (Junseok)", flush=True)
    print(f"  입력   {rd.CHARGED}", flush=True)
    print(f"  출력   {rd.OUT}", flush=True)
    print(f"  결과   {os.path.join(rd.HERE, 'density_results.json')}", flush=True)
    print(f"  워커   {rd.MAX_WORKERS}", flush=True)
    print(f"  대상   {len(rd.TARGETS)}종 {rd.TARGETS}  × 전하 ON/OFF = {2*len(rd.TARGETS)}작업", flush=True)
    print(f"  규약   0.15 bar · 298 K · {rd.INIT}+{rd.CYCLES} 사이클 · {rd.GRID}^3 격자 · DDEC6", flush=True)
    missing = [t for t in rd.TARGETS
               if not os.path.exists(os.path.join(rd.CHARGED, t + "_DDEC6.cif"))]
    if missing:
        print(f"  !! 전하 CIF 없음: {missing}", flush=True)
        sys.exit(2)
    sys.exit(rd.main())
