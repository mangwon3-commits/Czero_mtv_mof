"""습윤 작업 용량 v3 — 빠진 조성(saIm025) 하나를 채운다.

[왜 saIm025 인가]
    08-19 06:47 에 끝난 습윤 WC v3 는 base / saIm050 / saIm075 / saIm100
    네 점입니다. 흡착 시 물/CO₂ 비가

        base 0.85 → saIm050 1.01 → saIm075 1.24 → saIm100 2.31

    로 가는데, **마지막 계단만 유독 큽니다**(1.24 → 2.31). 이것이 치환율에
    대한 매끄러운 증가의 끝부분인지, 아니면 100% 에서만 일어나는 문턱
    현상인지가 결론의 성격을 바꿉니다. 25% 점이 있으면 앞쪽 기울기를
    잴 수 있어 그 구분이 가능해집니다.

    saIm025 는 안정성 관문을 통과했고 v3 GCMC 도 있습니다(Q_st 27.97).
    습윤 축에만 구멍이 나 있습니다.

[왜 데스크탑인가]
    auto68.sh 가 08-19 06:58 에 완주하고 이 기기가 비었습니다. 격자 4종은
    랩탑에 배정돼 있으므로 겹치지 않습니다. 작업 3개, 워커 3.

[결과 파일을 왜 또 나누는가]
    같은 이름을 쓰면 이어받기가 상대 작업을 "이미 됐다" 로 읽습니다.
    데스크탑 본run(`humid_working_capacity.json`)과 랩탑 격자
    (`humid_working_capacity_grid.json`)에 이어 셋째 파일을 씁니다.

        결과  v3_humid_wc/humid_working_capacity_ext.json
        작업  humid_wc_runs_v3ext/

    조건과 규약은 한 글자도 바꾸지 않습니다 — 같은 표에 놓아야 하므로.

사용:
    HWC_V3E_WORKERS=3 python -u run_humid_wc_v3ext.py
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

# import 만으로 hw.HERE / CHARGED / RUNS / RESULT 가 v3 로 맞춰집니다.
# run_humid_wc_v3 의 실행부는 전부 `if __name__ == "__main__"` 아래라
# import 는 아무것도 실행하지 않습니다.
import run_humid_wc_v3 as _v3          # noqa: F401,E402
import run_humid_wc as hw              # noqa: E402

V3 = os.path.join(HERE, "v3_humid_wc")
os.makedirs(V3, exist_ok=True)

# ---- import 이후에 덮어씁니다. 순서가 뒤집히면 본run 결과를 덮습니다. ----
hw.RUNS = os.path.join(HERE, "humid_wc_runs_v3ext")
hw.RESULT = os.path.join(V3, "humid_working_capacity_ext.json")
hw.TARGETS = ["saIm025"]
hw.MAX_WORKERS = int(os.environ.get("HWC_V3E_WORKERS", "3"))

if __name__ == "__main__":
    print("습윤 작업 용량 v3 — 빠진 조성 채우기", flush=True)
    print(f"  입력   {hw.CHARGED}", flush=True)
    print(f"  작업   {hw.RUNS}", flush=True)
    print(f"  결과   {hw.RESULT}", flush=True)
    print(f"  대상   {hw.TARGETS}", flush=True)
    print(f"  워커   {hw.MAX_WORKERS}", flush=True)

    assert hw.CHARGED.endswith("charged_v3"), "전하 폴더가 v3 가 아닙니다"
    assert hw.RUNS.endswith("humid_wc_runs_v3ext"), "작업 폴더가 겹칩니다"
    assert hw.RESULT.endswith("_ext.json"), "결과 파일이 본run 것과 같습니다"

    missing = [t for t in hw.TARGETS
               if not os.path.exists(os.path.join(hw.CHARGED, t + "_DDEC6.cif"))]
    if missing:
        print(f"  !! charged_v3 에 없음: {missing}", flush=True)
        sys.exit(1)
    print(flush=True)
    sys.exit(hw.main())
