"""습윤 작업 용량 v3w — **수정 물 힘장(Hw none / Lw none, 09-06)** 위에서 다시 잰다.

[왜] DECISION_RULE_20260820 이 1위 판정의 유일한 자로 고정한 '습윤 TSA 작업 용량' 의 산출물이
    전부 결함판 물 힘장(09-05 이전) 위의 수라 09-06 부터 인용 불가였고(WATER_FIX §11-F),
    재계산이 어느 배정에도 없었다(MAGI-004 Balthasar R1 논제 1). 새 힘장으로, 새 폴더에서, 처음부터.
[무엇] 조건·사이클·힘장·전하 전부 §1 고정값. 대상은 env HWC_V3W_TARGETS(쉼표), 기본 base,saIm025,saIm050,saIm0583.
      결과 파일은 env HWC_V3W_RESULT(파일명, v3w_humid_wc/ 아래; 기본 humid_working_capacity.json). RESULT 는 끝에 통째로 쓰므로
      **동시에 도는 인스턴스는 반드시 다른 파일명**을 준다(ASSIGN_20260907 §AC). 실행 폴더는 {label}_{tag} 라 공유해도 된다.
[관문] 착수 전 ff_gate.md5_gate() — 파일 관문 불일치면 시작하지 않는다.
"""
import os
import sys

import ff_gate
import run_humid_wc as hw

REAL = os.path.dirname(os.path.abspath(__file__))
V3W = os.path.join(REAL, "v3w_humid_wc")
os.makedirs(V3W, exist_ok=True)

hw.HERE = V3W
hw.CHARGED = os.path.join(REAL, "charged_v3")
hw.RUNS = os.path.join(REAL, "humid_wc_runs_v3w")
hw.RESULT = os.path.join(V3W, os.environ.get("HWC_V3W_RESULT", "humid_working_capacity.json"))  # 2차(앙상블) 파도는 인스턴스별 파일(덮어쓰기 방지, 09-10 §AC)
hw.TARGETS = [t for t in os.environ.get("HWC_V3W_TARGETS", "base,saIm025,saIm050,saIm0583").split(",") if t]
hw.MAX_WORKERS = int(os.environ.get("HWC_V3W_WORKERS", "8"))

if __name__ == "__main__":
    ok, md5 = ff_gate.md5_gate()
    print(f"  파일 관문 md5 {md5} {'일치' if ok else '불일치 — 중단'}", flush=True)
    if not ok:
        sys.exit(3)
    print("습윤 작업 용량 v3w (수정 물 힘장)", flush=True)
    for k in ("CHARGED", "RUNS", "RESULT", "TARGETS", "MAX_WORKERS"):
        print(f"  {k:12s} {getattr(hw, k)}", flush=True)
    missing = [t for t in hw.TARGETS if not os.path.exists(os.path.join(hw.CHARGED, t + "_DDEC6.cif"))]
    if missing:
        print(f"  !! charged_v3 에 없음: {missing}", flush=True)
        sys.exit(1)
    print(flush=True)
    sys.exit(hw.main())
