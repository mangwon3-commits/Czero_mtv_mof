"""CoRE 의 `water_classification` 규칙을 **되찾은** 것 — 배포본에 규칙이 없어서 자료에서 역산했습니다.

[왜 필요한가]
    CoRE 관문 3개 중 우리가 좌표를 못 가진 축이 둘입니다(`OURS_VS_CORE_20260920.md §5`).
    그중 물 축은 CoRE 가 **GEMC 물 등온선**(TIP4P/UFF4MOF/298 K)에서 붙인 이름표인데,
    **그 이름표를 붙이는 규칙이 zip 어디에도 없습니다**(값만 있습니다).

[어떻게 되찾았나]
    등온선과 이름표가 **13,337 쌍** 있습니다. 지도학습이 아니라 **문턱 한 개**로 맞춰 봤습니다.
    압력별로 이름표가 얼마나 갈리는지 보니 **0.1 Pa**(P/P0 = 0.1/4540 = 2.2e-5, 확실한 Henry 영역)에서 가장 깨끗했습니다.

        저친화(superweak + weak)  n=8,154      고친화(strong 계열)  n=4,534
        최적 문턱  0.1 Pa 적재량 **6.899e-04 mmol/g**
        오분류     552 / 12,688 = **4.35 %**  (저친화인데 초과 227 · 고친화인데 미만 325)
        superweak|weak 경계는 **적재량 0** (오분류 1.67 %)

[한계 — 반드시 같이 읽으십시오]
    · 진짜 규칙은 **한 문턱이 아닙니다**(4.35 % 가 안 맞습니다). 등온선 **모양**(계단 위치)을 쓰는 것으로 보입니다.
      그러니 문턱에서 **2~3배 안**에 있는 물질은 이 규칙으로 판정하지 마십시오.
    · `_high_loading` 접미사는 **못 되찾았습니다**. 최대 적재량으로는 안 갈립니다
      (strong 중앙 2.64 대 strong_high_loading 4.49 — 크게 겹칩니다).
    · `none` 은 압력에 무관하게 평평하고 molecules/supercell 이 4·16·36·48 같은 정수라 **실패 표식**으로 보입니다.
    · **힘장이 다릅니다.** CoRE 는 TIP4P + UFF4MOF, 우리는 TIP5P-Ew(`Hw none`/`Lw none`) + UFF_MOF.
      TIP5P 쪽이 수소결합을 더 세게 잡는 편이므로 우리 K_H 는 그들 눈금 대비 **높게** 나올 것이고,
      그러면 우리 판정은 "strong 쪽으로 치우친" 보수적 추정이 됩니다 — 즉 **weak 판정은 안전한 쪽**입니다.
"""

# 되찾은 문턱 — 2026-09-20, CR.json 13,337쌍에서.
P_PROBE = 0.1                     # Pa. P/P0 = 2.2e-5 로 확실한 Henry 영역입니다.
THRESH_LOADING = 6.899e-4         # mmol/g @ 0.1 Pa.  이 미만이면 weak 쪽.
THRESH_KH = THRESH_LOADING / P_PROBE      # = 6.899e-3 mmol/g/Pa
FIT_ERROR = 0.0435                # 이 문턱 한 개로 맞췄을 때의 오분류율
SAFE_MARGIN = 3.0                 # 문턱까지 이 배수 안이면 "경계" 로 보고 판정하지 않습니다


def classify_from_kh(kh_water, *, unit="mmol/g/Pa"):
    """물 K_H(무한희석, 298 K)로 CoRE 이름표를 추정합니다.

    0.1 Pa 는 Henry 영역이므로 적재량 = K_H x P 로 외삽해도 안전합니다.
    돌려주는 것: (이름표, 문턱까지의 배수, 경계인지)
    """
    if kh_water is None or kh_water <= 0:
        return None, None, True
    loading = kh_water * P_PROBE
    margin = THRESH_LOADING / loading
    borderline = margin < SAFE_MARGIN
    label = "weak" if loading < THRESH_LOADING else "strong(계열)"
    return label, margin, borderline


def classify_from_isotherm(points):
    """{압력(Pa): 적재량(mmol/g)} 에서 직접. 0.1 Pa 가 없으면 가장 낮은 압력에서 Henry 외삽."""
    if not points:
        return None, None, True
    if P_PROBE in points:
        loading = points[P_PROBE]
    else:
        p = min(points)
        loading = points[p] * (P_PROBE / p)      # Henry 외삽
    if loading <= 0:
        return "superweak", float("inf"), False
    margin = THRESH_LOADING / loading
    return ("weak" if loading < THRESH_LOADING else "strong(계열)"), margin, margin < SAFE_MARGIN


if __name__ == "__main__":
    import json
    import sys
    path = sys.argv[1] if len(sys.argv) > 1 else \
        "../21_ZIF69_MTV/v3w_water_kh/water_kh_ALLw_hkhome_seedfixed.json"
    d = json.load(open(path, encoding="utf-8"))
    rows = d["rows"] if isinstance(d, dict) and "rows" in d else d
    got = []
    for r in rows:
        kh = next((r[k] for k in r if k.upper().startswith("KH")), None)
        if kh:
            got.append((r.get("tag") or r.get("name"), kh))
    got.sort(key=lambda t: -t[1])
    print(f"문턱  K_H(물) < {THRESH_KH:.4g} mmol/g/Pa → weak   "
          f"(한 문턱 적합 오분류 {FIT_ERROR*100:.2f} %, 경계 판정 보류 폭 {SAFE_MARGIN:.0f}배)")
    print(f"{'조성':14s} {'K_H':>12s} {'문턱까지':>10s}  판정")
    for name, kh in got:
        lab, margin, border = classify_from_kh(kh)
        flag = "  ← 경계, 판정 보류" if border else ""
        print(f"{name:14s} {kh:12.4g} {margin:9.1f}배  {lab}{flag}")
    n_border = sum(1 for _, kh in got if classify_from_kh(kh)[2])
    print(f"\n{len(got)}개 중 weak {sum(1 for _, kh in got if classify_from_kh(kh)[0]=='weak')}개 · "
          f"경계(판정 보류) {n_border}개")
