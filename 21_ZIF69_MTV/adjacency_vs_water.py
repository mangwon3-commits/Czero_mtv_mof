"""인접 치환 쌍이 물 흡착을 설명하는가 — **군 A(saIm0583)에서 독립 시험**.

[가설은 랩탑 것이고, 이 시험은 다른 조성·다른 관측량입니다]
    랩탑이 08-28 05:07 에 군 B(sa50nb50)에서 등록했습니다:

        인접 -SO3H 쌍 up  ->  물 up  ->  소요 up

    근거: 군 B 실현별 소요가 인접 쌍 수와 나란히 갔습니다
    (e2 2쌍 622분+ / e1 1쌍 361~397분 / e3 0쌍 진행 중).

    **여기서는 같은 가설을 군 A 에서 봅니다** — 조성이 다르고(saIm0583
    대 sa50nb50), 관측량이 다릅니다(로딩 대 소요). 맞으면 두 자료에서
    독립으로 선 것이고, 어긋나면 조성 의존입니다.

[★ 방향을 **세기 전에** 적습니다]
    군 A 의 CO2 로딩은 **이미 알고 있습니다**(08-28 03:37 완주). 인접 쌍
    수는 **아직 안 셌습니다.** 그래서 이것은 완전한 사전 등록이 아니라
    **"가설과 방향은 고정, 예측 변수는 미지"** 상태의 시험입니다.
    그 한계를 그대로 적습니다.

        예측 1   인접 쌍 vs H2O_molkg   ->  **양(+)**
        예측 2   인접 쌍 vs CO2_molkg   ->  **음(-)**

    군 A 의 CO2 순서는 세 RH 에서 **모두 같습니다**:

        e2 < e5 < e1 < e3 < e4      (낮은 것부터)

    따라서 구체적 예측은 **e2 가 인접 쌍이 가장 많고 e4 가 가장 적다** 입니다.

[n=5 입니다 — 미리 못을 박습니다]
    표본 5로 상관을 내면 p<0.05 에 |r| >= 0.878 이 필요합니다. **맞아도
    "일관" 이지 "확립" 이 아닙니다.** 랩탑이 자기 예측에 붙인 단서와 같습니다.

[인접의 정의 — 자료로 정합니다]
    자리-자리 거리 분포에서 **첫 껍질**을 끊습니다. 임의 문턱을 고르면
    "문턱을 움직여 원하는 상관을 얻는" 형태가 되므로, 껍질 사이 간극이
    가장 큰 곳을 쓰고 **문턱 민감도도 같이 출력**합니다.

    ⚠️ 랩탑이 08-27 에 쓴 정의와 다를 수 있습니다. 쌍 **개수**를 직접
    비교하지 말고 **순위**로만 견주십시오.

사용:
    python3 adjacency_vs_water.py
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
LIGLIB = os.path.join(ROOT, "05_MTV_Ligand_Library")
sys.path.insert(0, LIGLIB)
sys.path.insert(0, HERE)

BASE_CIF = os.path.join(LIGLIB, "ZIF69_base.cif")
SITE_MAP = os.path.join(LIGLIB, "site_map_zif69_bicyclic.json")
ENSA = os.path.join(HERE, "v3_water_lowrh_ensA", "water_results.json")
REALS = [f"saIm0583e{i}" for i in range(1, 6)]


def pearson(x, y):
    n = len(x)
    mx, my = sum(x) / n, sum(y) / n
    sxy = sum((a - mx) * (b - my) for a, b in zip(x, y))
    sxx = sum((a - mx) ** 2 for a in x)
    syy = sum((b - my) ** 2 for b in y)
    return sxy / (sxx * syy) ** 0.5 if sxx and syy else float("nan")


def main():
    import warnings
    warnings.filterwarnings("ignore")
    import numpy as np
    from ase.io import read
    from mtv_cif_builder import (CBIM_ARYL_ATTACHMENT_INDEX, _mic_min_distance,
                                 _unwrap, attachment_index)

    atoms = read(BASE_CIF)
    sites = [{"ring": s["bicyclic_ring"], "substituent": s["aryl_substituent"]}
             for s in json.load(open(SITE_MAP, encoding="utf-8"))]
    cell = np.asarray(atoms.get_cell())
    anchors = np.array([_unwrap(atoms, s["ring"])[
        attachment_index(atoms, s, CBIM_ARYL_ATTACHMENT_INDEX)] for s in sites])
    n = len(sites)

    D = {}
    for i in range(n):
        for j in range(i + 1, n):
            D[(i, j)] = float(_mic_min_distance(anchors[i:i + 1],
                                                anchors[j:j + 1], cell))
    ds = sorted(D.values())
    print(f"  자리 {n}개, 쌍 {len(ds)}개.  거리 {ds[0]:.3f} ~ {ds[-1]:.3f} A")

    # 첫 껍질 = 정렬된 거리에서 간극이 가장 큰 곳 (하위 40% 안에서)
    lim = int(len(ds) * 0.4)
    gaps = [(ds[k + 1] - ds[k], k) for k in range(lim)]
    gap, k = max(gaps)
    cut = (ds[k] + ds[k + 1]) / 2
    print(f"  첫 껍질 경계  {ds[k]:.3f} | {ds[k+1]:.3f}   간극 {gap:.3f} A"
          f"  ->  문턱 **{cut:.3f} A**  (껍질 안 {k+1}쌍)\n")

    ens = json.load(open(ENSA, encoding="utf-8"))
    rows = ens["rows"] if isinstance(ens, dict) and "rows" in ens else ens

    print("  %-12s %6s   %8s %8s %8s   %8s %8s %8s"
          % ("실현", "인접쌍", "CO2_5", "CO2_10", "CO2_15",
             "H2O_5", "H2O_10", "H2O_15"))
    print("  " + "-" * 76)
    pairs, co2, h2o = [], {5: [], 10: [], 15: []}, {5: [], 10: [], 15: []}
    for tag in REALS:
        meta = json.load(open(os.path.join(HERE, "structures_v2",
                                           f"ZIF69_{tag}.meta.json"),
                              encoding="utf-8"))
        ch = set(meta["chosen_sites"])
        npair = sum(1 for (i, j), d in D.items()
                    if d <= cut and i in ch and j in ch)
        pairs.append(npair)
        g = {int(round(r["RH"] * 100)): r for r in rows if r["name"] == tag}
        for rh in (5, 10, 15):
            co2[rh].append(g[rh]["CO2_molkg"])
            h2o[rh].append(g[rh]["H2O_molkg"])
        print("  %-12s %6d   %8.4f %8.4f %8.4f   %8.4f %8.4f %8.4f"
              % (tag, npair, *[g[r]["CO2_molkg"] for r in (5, 10, 15)],
                 *[g[r]["H2O_molkg"] for r in (5, 10, 15)]))

    print(f"\n  인접 쌍 {pairs}   (예측: e2 최다, e4 최소)")
    print(f"\n  %-10s %8s %8s %8s   %s" % ("상관 r", "RH5", "RH10", "RH15", "예측"))
    print("  " + "-" * 52)
    rc = [pearson(pairs, co2[r]) for r in (5, 10, 15)]
    rh_ = [pearson(pairs, h2o[r]) for r in (5, 10, 15)]
    print("  %-10s %8.3f %8.3f %8.3f   %s" % ("vs CO2", *rc, "음(-)"))
    print("  %-10s %8.3f %8.3f %8.3f   %s" % ("vs H2O", *rh_, "양(+)"))

    ok_c = all(v < 0 for v in rc)
    ok_h = all(v > 0 for v in rh_)
    print(f"\n  방향 일치:  CO2 {'O' if ok_c else 'X'}   H2O {'O' if ok_h else 'X'}")
    print(f"  n=5 에서 p<0.05 는 |r| >= 0.878 — 아래 표로 확인하십시오.")

    print("\n  문턱 민감도 (인접 쌍 정의를 흔들어 봅니다)")
    print("  %-10s %8s   %8s %8s" % ("문턱 A", "쌍 합", "r(CO2,RH5)", "r(H2O,RH5)"))
    for c in (cut - 0.5, cut, cut + 0.5, cut + 1.0, cut + 2.0):
        p2 = []
        for tag in REALS:
            meta = json.load(open(os.path.join(HERE, "structures_v2",
                                               f"ZIF69_{tag}.meta.json"),
                                  encoding="utf-8"))
            ch = set(meta["chosen_sites"])
            p2.append(sum(1 for (i, j), d in D.items()
                          if d <= c and i in ch and j in ch))
        print("  %-10.3f %8d   %8.3f %8.3f"
              % (c, sum(p2), pearson(p2, co2[5]), pearson(p2, h2o[5])))
    return 0


if __name__ == "__main__":
    sys.exit(main())
