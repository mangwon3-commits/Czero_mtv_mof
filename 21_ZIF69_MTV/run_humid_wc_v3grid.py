"""습윤 작업 용량 v3 — 조성 격자(saIm0625)만.

[왜 별도 파일인가]
    `run_humid_wc_v3.py` 의 TARGETS 는 모듈 최상단에 박혀 있고
    (base / saIm050 / saIm075 / saIm100), 그 실행이 지금 데스크탑에서
    돌고 있습니다. 돌고 있는 러너를 편집하지 않습니다.

[왜 결과 파일과 작업 폴더를 따로 두는가]
    데스크탑과 랩탑이 **각자의 클론**에서 같은 이름의 결과 JSON 을 쓰면
    푸시할 때 충돌합니다. 그리고 이어받기가 파일 존재로만 판단하므로,
    같은 폴더를 쓰면 한쪽이 다른 쪽 작업을 "이미 됐다" 로 읽습니다 —
    이 프로젝트에서 가장 무서운 종류의 실패입니다.

        결과  v3_humid_wc/humid_working_capacity_grid.json
        작업  humid_wc_runs_v3grid/

[왜 조건은 그대로인가]
    물 분압 2852.1 Pa 고정, ads / tsa / vsa 세 조건. 데스크탑의 네 종과
    **같은 표에 놓고 읽어야** 하므로 규약을 한 글자도 바꾸지 않습니다.

[왜 saIm0625 인가]
    v3 에서 목표대에 든 saIm075·saIm100 이 08-19 안정성 관문에서 둘 다
    탈락했습니다. 통과한 마지막 조성은 saIm050(Q_st 29.51, 문턱 밑)입니다.
    62.5% 는 흡착 문턱과 구조 붕괴가 **동시에 걸려 있는** 조성이고,
    안정성 판정이 어느 쪽으로 나오든 "쓸 수 있는 창이 어디서 닫히는가" 를
    말하려면 이 조성의 습윤 수치가 필요합니다.

사용:
    HWC_V3G_WORKERS=6 python -u run_humid_wc_v3grid.py
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

# import 만으로 hw.HERE / CHARGED / RUNS / RESULT / TARGETS 가 v3 로 맞춰집니다.
# 이 모듈은 전부 `if __name__ == "__main__"` 아래에 있으므로 import 는
# 아무것도 실행하지 않습니다.
import run_humid_wc_v3 as _v3          # noqa: F401,E402
import run_humid_wc as hw              # noqa: E402

V3 = os.path.join(HERE, "v3_humid_wc")
os.makedirs(V3, exist_ok=True)

# ---- import 이후에 덮어씁니다. 순서가 뒤집히면 데스크탑 결과를 덮습니다. ----
hw.RUNS = os.path.join(HERE, "humid_wc_runs_v3grid")
hw.RESULT = os.path.join(V3, "humid_working_capacity_grid.json")
hw.TARGETS = ["saIm0625"]
hw.MAX_WORKERS = int(os.environ.get("HWC_V3G_WORKERS", "6"))

if __name__ == "__main__":
    print("습윤 작업 용량 v3 — 조성 격자", flush=True)
    print(f"  입력   {hw.CHARGED}", flush=True)
    print(f"  작업   {hw.RUNS}", flush=True)
    print(f"  결과   {hw.RESULT}", flush=True)
    print(f"  대상   {hw.TARGETS}", flush=True)
    print(f"  워커   {hw.MAX_WORKERS}", flush=True)

    # 조용한 경로 오염을 막는 확인. run_gcmc_v3.py 가 같은 이유로 assert 를 둡니다.
    assert hw.CHARGED.endswith("charged_v3"), "전하 폴더가 v3 가 아닙니다"
    assert hw.RUNS.endswith("humid_wc_runs_v3grid"), "작업 폴더가 격자용이 아닙니다"
    assert hw.RESULT.endswith("_grid.json"), "결과 파일이 데스크탑 것과 같습니다"

    missing = [t for t in hw.TARGETS
               if not os.path.exists(os.path.join(hw.CHARGED, t + "_DDEC6.cif"))]
    if missing:
        print(f"  !! charged_v3 에 없음: {missing}", flush=True)
        print("     charge_v3.py 를 먼저 도세요(격자 구조의 전하가 필요합니다).",
              flush=True)
        sys.exit(1)
    print(flush=True)
    sys.exit(hw.main())
