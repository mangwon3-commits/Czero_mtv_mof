"""습윤 작업 용량 — saIm050 앙상블 e1~e5 (15작업). 조성 축을 닫는 마지막 조각.

[사전 등록] 21_ZIF69_MTV/ENSEMBLE_0500_PROTOCOL.md — 계산 전에 작성됐습니다.

[무엇을 재는가]
    08-25 에 saIm0583 의 6실현 앙상블이 끝나면서, 배치 SD 0.0580 을 치환 조성
    전체에 얹으면 **인접 쌍이 하나도 구별되지 않는다**는 것이 나왔습니다
    (0.31~0.82 단위, 전부 1.5 미만). 그중 saIm050 만 특별합니다:

        saIm050   0.7680   <- 실현 1개
        saIm0583  0.7306   <- 6실현 평균

    **점추정에서 saIm050 이 위입니다.** 다만 saIm050 도 실현 하나뿐이라 그
    값 역시 위쪽 draw 일 수 있어 뒤집혔다고 말할 수 없습니다. 지금은 어느
    쪽도 주장할 수 없는 상태이고, saIm050 이 이 문제가 걸린 **유일한
    조성**입니다 — 다른 조성들은 점추정이 아래에 있고 배치 오차를 얹어도
    위로 올라오지 않습니다.

[왜 물 RH0/RH90 이 아니라 습윤 WC 인가 — 08-26 정정]
    이 규약의 첫 판은 Junseok 에게 **물 RH0/RH90 10작업**을 배정하면서
    판정은 습윤 WC 로 하도록 적었습니다. **그 둘은 다른 양입니다.**
    물 10작업이 내는 것은 298 K, CO2 0.15 bar 단일 조건의 로딩 두 점이고,
    작업 용량은 흡착/탈착 두 조건의 차이라 TSA 는 두 번째 온도가 필요합니다.
    10작업으로는 M050 을 만들 수 없습니다.

    Junseok 이 이것을 잡았습니다. 그대로 돌렸으면 유지율은 나오는데 조성
    축은 안 닫히고, 더 나쁘게는 RH90 로딩을 M050 이라 부르며 0.7306 과
    비교했을 것입니다 — 로딩과 작업 용량을 같은 칸에 넣는 것이라 표는
    채워져 보이는데 비교가 성립하지 않습니다.

[왜 15작업 전부인가]
    습윤 WC 는 ads/tsa/vsa 세 조건의 조합이라 하나만 빼도 WC 가 안 나옵니다.
    5실현 x 3조건 = 15 가 최소입니다.

[판정 — 수를 보기 전에 고정 (PROTOCOL 3절)]
    M050  = saIm050  6실현 평균 (시드 0 = 기존 생산 구조 0.7680 포함)
    M0583 = 0.7306   (saIm0583 6실현 평균)
    s0583 = 0.0580   (배치 SD)
    s_comb = sqrt(s050^2 + s0583^2)

        |M050 - M0583| / s_comb >= 1.5  -> **순위 확정**
                                           큰 쪽이 승자. saIm050 이 크면
                                           승자 교체, saIm0583 이 크면 유지
        < 1.5                           -> **조성 축 종료**
                                           "치환 조성끼리는 배치 오차 안에서
                                           구별되지 않는다" 를 확정으로 적고
                                           조성 최적화를 더 하지 않는다

    어느 쪽이 나오든 결론입니다. 1.5 는 이미 쓰는 문턱이라 새 수가 아닙니다.

    **평균과 SD 는 전부 n=6 입니다.** 08-25 에 s_wc 문턱이 어느 n 을
    상정했는지 적혀 있지 않아 모호했던 것을 반복하지 않습니다.
    **leave-one-out 을 쓰지 않습니다** — 같은 날 데스크탑과 랩탑이 각자
    대상을 분모에서 빼고 z 를 계산해 +2.08 / +3.75 를 적었다가 정정했습니다.

    부수 관찰(관문 아님): s050 을 s0583=0.0580 과 비교합니다. 크게 다르면
    "배치 SD 를 전 조성에 동일하게 얹는다" 는 08-25 의 가정이 흔들리므로
    그때 별도로 판단합니다. 미리 문턱을 걸지 않습니다.

[엔진·규약]
    run_humid_wc_v3ens0583.py 와 같은 방식입니다 — run_humid_wc 의 모듈
    전역만 갈아끼우고 그 main() 을 그대로 부릅니다. 물 분압 2852.1 Pa 고정,
    사이클·힘장·전하·물 정의를 한 글자도 바꾸지 않습니다. 그래야 saIm0583
    앙상블과 **같은 자** 위에 놓입니다.

[출력을 왜 분리하나]
    v3_humid_wc/ 는 **조성 축**의 답이 모이는 곳입니다. 앙상블은 같은 조성의
    다른 실현이라 **배치 축**입니다. 같은 파일에 넣으면 표가 e1~e5 를 조성
    5종으로 읽어, 조성 비교표에 배치 반복이 섞입니다.

사용:
    HWC_ENS_WORKERS=<물리코어수> python run_humid_wc_v3ens0500.py
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import run_humid_wc_v3 as _v3          # noqa: F401,E402  (v3 배선)
import run_humid_wc as hw              # noqa: E402

ENS = os.path.join(HERE, "v3_humid_wc_ens")
os.makedirs(ENS, exist_ok=True)

hw.RUNS = os.path.join(HERE, "humid_wc_runs_v3ens0500")
hw.RESULT = os.path.join(ENS, "humid_working_capacity_ens0500.json")
hw.TARGETS = ["saIm050e1", "saIm050e2", "saIm050e3",
              "saIm050e4", "saIm050e5"]
hw.MAX_WORKERS = int(os.environ.get("HWC_ENS_WORKERS", "8"))

if __name__ == "__main__":
    print("습윤 작업 용량 — saIm050 앙상블 e1~e5 (15작업)", flush=True)
    for k in ("CHARGED", "RUNS", "RESULT", "TARGETS", "MAX_WORKERS"):
        print(f"  {k:<8} {getattr(hw, k)}", flush=True)

    assert hw.CHARGED.endswith("charged_v3")
    assert hw.RUNS.endswith("v3ens0500") and hw.RESULT.endswith("ens0500.json")
    if len(hw.TARGETS) != 5:
        print("  !! 앙상블 5실현이 아닙니다. 중단합니다.", flush=True)
        sys.exit(1)
    missing = [t for t in hw.TARGETS
               if not os.path.exists(os.path.join(hw.CHARGED, t + "_DDEC6.cif"))]
    if missing:
        print(f"  !! 전하 CIF 없음: {' '.join(missing)}", flush=True)
        sys.exit(1)
    # 물 정의가 5자리인지 확인합니다. 배포본 TraPPE/water.def 는 3자리라
    # 조용히 다른 물로 계산됩니다 — 실패가 결과처럼 보이는 그 유형입니다.
    wd = getattr(hw, "WATER_DEF", None)
    if wd and os.path.exists(wd):
        nsite = sum(1 for ln in open(wd, encoding="utf-8")
                    if len(ln.split()) > 4 and ln.split()[1] in ("Ow", "Hw", "Lw"))
        print(f"  물 정의 사이트 {nsite}개 (TIP5P-Ew 는 5)", flush=True)
        if nsite != 5:
            print("  !! 5자리 물이 아닙니다. 중단합니다.", flush=True)
            sys.exit(1)
    print(flush=True)
    sys.exit(hw.main())
