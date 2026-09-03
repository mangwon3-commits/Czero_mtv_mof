"""습윤 작업 용량 v3 — `mslm025` · `nbIm075` · `nbIm100` 세 종.

[사전 등록] `MSLM050_CHALLENGE_20260827.md` 6-3 의 **(B) 분기**

    "mslm050 실측 후 관문통과 7점으로 재적합, 잔차 SD 를 배치 바닥으로 하한.
       하한 위험 <10% AND 95% 상한 위험 <30%  ->  (A) 문서 처리
       그 밖                                  ->  (B) mslm025·nbIm075·nbIm100"

[재적합 결과 — 2026-08-28, 세 종 착수 전]

    7점 재적합   r = +0.9729   기울기 0.4049   잔차SD(dof=5) 0.0253
    미측정 24종의 예측 최고 = mslm025 0.6191

    위험 (T = (라) 경계, 미측정 전수 합집합)
      T 0.672 · 바닥 0.0336   **13.0%**      <- 정정 없이도 이미 (B)
      T 0.672 · 바닥 0.0580   **59.7%**
      T 0.646 · 바닥 0.0336   **49.6%**
      T 0.646 · 바닥 0.0580   **86.5%**

    **네 칸 전부 (B)** 입니다.

    ⚠️ 데스크탑 재구성(6.5 / 19.0 / 22.8 / 33.3%)과 크기가 다릅니다 —
    합집합에 넣는 조성 수가 다른 것으로 보입니다(그쪽 상위 1~2, 이쪽 전수).
    **분기는 네 칸 모두 같아 실행에 영향이 없어** 크기 차이는 열어 둡니다.

[`nbIm075` 는 분기와 무관하게 잽니다 — 등록문 6-3 각주]

    "(A)가 발동해도 nbIm075 는 잽니다. nbIm 이 혼합 셋(sa50nb50·ms50nb50·
     sa25nb75) 전부의 공치환기인데 단독 습윤이 없습니다."

[중단 규칙 — 등록 그대로. 수를 보고 안 고칩니다]

    셋이 전부 saIm0583 대비 1.5 단위 아래  ->  남은 넷은 문서 처리
    하나라도 1.5 안으로 들어옴             ->  일곱을 다 잰다

    비교 기준  saIm0583 6실현 평균 **0.7306**
    분모       3절 일관식 (SD **0.0580**, n=6)  — 08-28 `mslm050` 판정과 같은 자

[배선] `run_humid_wc_v3mslm050.py` 와 동일. 규약(물 분압 2852.1 Pa,
ads/tsa/vsa, 사이클 15,000)은 그대로 — 같은 표에 놓아야 하므로.

[laptop2 와 충돌 없음] laptop2 의 `nbIm075` 는 **유지율**(RH0/RH90 물 경쟁)이고
이것은 **습윤 WC**(ads/tsa/vsa, 물 분압 고정) 입니다. 러너·폴더·결과 파일이
전부 다릅니다.
"""

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import run_humid_wc_v3 as _v3          # noqa: F401,E402  (v3 배선)
import run_humid_wc as hw              # noqa: E402

V3 = os.path.join(HERE, "v3_humid_wc")
os.makedirs(V3, exist_ok=True)

TARGETS = ["nbIm075", "mslm025", "nbIm100"]      # nbIm075 가 무조건 항목이라 먼저

hw.RUNS = os.path.join(HERE, "humid_wc_runs_v3nb3")
hw.RESULT = os.path.join(V3, "humid_working_capacity_nb3.json")
hw.TARGETS = TARGETS
hw.MAX_WORKERS = int(os.environ.get("HWC_NB3_WORKERS", "6"))

if __name__ == "__main__":
    print("습윤 작업 용량 v3 — mslm025 · nbIm075 · nbIm100  [6-3 (B) 분기]", flush=True)
    for k in ("CHARGED", "RUNS", "RESULT", "TARGETS", "MAX_WORKERS"):
        print(f"  {k:<12} {getattr(hw, k)}", flush=True)
    assert hw.CHARGED.endswith("charged_v3")
    assert hw.RUNS.endswith("v3nb3") and hw.RESULT.endswith("nb3.json")
    missing = [t for t in TARGETS
               if not os.path.exists(os.path.join(hw.CHARGED, f"{t}_DDEC6.cif"))]
    if missing:
        print(f"  !! 전하 파일 없음: {missing}", flush=True)
        sys.exit(1)
    print(f"  작업 수       {len(TARGETS)} 조성 x 3 조건 = {len(TARGETS)*3}", flush=True)
    print(flush=True)
    sys.exit(hw.main())
