"""문헌 앵커 — ZIF-93 (rho, almeIm) 를 우리 잠긴 프로토콜로 계산한다.

[왜 이것을 도는가]
    우리 v3 Q_st 사다리 전체가 **실측 앵커 없이** 떠 있다. GME 계열
    원논문(Banerjee JACS 2009)에는 Q_st 가 없다(전문 확인). 그래서
    "우리 30.36 이 문헌의 30 과 같은 자인가" 를 말할 수 없다.

    ZIF-93 은 Morris JPCC 2012 가 **Q_st0 = 29.3 kJ/mol** 을 실측으로
    보고한 물질이고, CIF 가 이미 저장소에 있다. 같은 프로토콜로 돌려
    그 값을 재현하면 우리 절대값에 자가 붙는다.

[사전 등록 판정 — 계산 전에 적는다]
    |우리 Q_st0 - 29.3| <= 3 kJ/mol  -> 우리 절대값 신뢰. 다른 물질과의
                                        비교를 정량으로 말할 수 있다.
    3 초과                            -> 그 편차를 계통 보정 후보로 공표한다.
                                        결과를 숨기지 않는다.
    어느 쪽이든 탈락 조건은 없다. 이것은 후보가 아니라 자(尺)다.

[한계 — 미리 적어 둔다]
    (1) Morris 의 29.3 은 가변온도 등온선 피팅값이고 우리는 Widom 삽입의
        무한희석 Q_st 다. 정의가 완전히 같지 않다.
    (2) UFF_MOF 는 -CHO 를 위해 만들어진 힘장이 아니다. 편차가 크면
        그것이 "우리 계산이 틀렸다" 가 아니라 "이 작용기에서 힘장이
        약하다" 일 수 있다.
    (3) 전하는 PACMAN 으로 새로 뽑는다(원 CIF 에 전하 없음).
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import run_aryl_gcmc as rg  # noqa: E402

WORK = os.path.join(HERE, "anchor_zif93")
CIF = os.path.join(WORK, "ZIF93_DDEC6.cif")

if __name__ == "__main__":
    if not os.path.exists(CIF):
        print(f"  !! 전하 CIF 없음: {CIF}")
        print("     charge_anchor_zif93.py 를 먼저 도세요.")
        sys.exit(1)
    print("문헌 앵커 — ZIF-93 (rho, almeIm)", flush=True)
    print(f"  문헌: Morris JPCC 2012, Q_st0 = 29.3 kJ/mol (ZIF-94 는 30.5)")
    print(f"  판정: |ours - 29.3| <= 3 이면 절대값 신뢰", flush=True)
    print(f"  규약: 0.15 bar / 298 K / 15000 사이클 / UFF_MOF / Ewald 1e-6\n",
          flush=True)
    os.makedirs(os.path.join(WORK, "runs"), exist_ok=True)
    res = {}
    for gas in ("CO2", "N2"):
        r = rg.run_one((CIF, gas, "widom"))
        res[gas] = r
        print(f"  Widom {gas}: {r}", flush=True)
    r = rg.run_one((CIF, "CO2", "gcmc"))
    print(f"  GCMC 0.15 bar: {r}", flush=True)
    import json
    json.dump({"structure": "ZIF-93", "topology": "rho",
               "literature_Qst0": 29.3, "literature_source":
               "Morris et al. J. Phys. Chem. C 2012, 116, 24084",
               "widom": {k: str(v) for k, v in res.items()},
               "gcmc_015bar": str(r)},
              open(os.path.join(HERE, "anchor_zif93.json"), "w",
                   encoding="utf-8"), indent=2, ensure_ascii=False)
    print("\n[OK] anchor_zif93.json")
