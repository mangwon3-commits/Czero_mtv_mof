"""CoRE MOF 스크리닝 — `MOF_Screening.ipynb`(83셀) 정리본.

[무엇]
    CoRE MOF 메타데이터(`CR_meta_data_SI.json`)에서 기하·안정성·수분·Widom 값을 꺼내
    관문을 통과시키고, 우리 ZIF-69 조성(`21_ZIF69_MTV/results_v3.json`)을 같은 축에 얹습니다.

[왜 다시 썼나 — 원본 노트북의 결함 다섯]
    D1 위치 인덱스   `df.iloc[:, 9]`(GEMC 열) · `widom[0]/widom[1]`(CO2/N2). 열 순서가 바뀌면 조용히 틀린 값이 나옵니다.
                     이 저장소는 같은 유형(부착 원자 고정 인덱스 4)으로 08-14 에 v1 치환 결과를 전량 폐기했습니다.
                     → 여기서는 **이름으로 찾고, 못 찾으면 예외를 냅니다.**
    D2 맨 except     `except: return NaN` 이 스무 곳 넘게 있어 **실패가 결측으로 보입니다**(CLAUDE.md §0 의 핵심 결함 유형).
                     → 여기서는 실패를 세어 `report()` 에 남기고, 조용히 0/NaN 으로 만들지 않습니다.
    D3 사후 문턱     3중 관문(stable & PLD≥3.3 & weak) → 0개 → 그 뒤에 PLD 창 3.3~3.6 / 3.7~4.2 를 만들고
                     다시 PLD≥3.4 · VF≥0.2 를 더했습니다. **자료를 본 뒤 문턱이 움직였습니다**(§2 위반).
                     → 여기서는 문턱을 `GATES` 한 곳에 모아 **출처(등록 문서/자료를 본 시점)를 같이 적습니다.**
    D4 오차 없음     Widom K_H 점값으로 순위를 매깁니다. 우리 `results_v3.json` 은 같은 양에 `*_err` 가 있습니다.
                     → `rank()` 는 오차 열이 있으면 **1.5배 규칙**(CLAUDE.md §2)을 적용하고, 없으면 "순위 없음" 으로 돌려줍니다.
    D5 임의 가중치   점수 0.6×선택도 + 0.4×용량, 상위 5 % 클리핑. 근거가 "정상 물질 점수가 바닥에 깔리는 것 방지" 였습니다.
                     → 점수화는 **선택 사항**으로 빼고 기본은 원자료 축(K_H, 선택도)을 그대로 씁니다.

사용:
    python3 screen_core.py --meta data/CR_meta_data_SI.json
    python3 screen_core.py --meta data/CR_meta_data_SI.json --ours ../21_ZIF69_MTV/results_v3.json
"""
import argparse
import collections
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))

# ---------------------------------------------------------------------------
# 문턱 — 한 곳에 모으고, 각각 어디서 왔는지 적습니다 (D3)
# ---------------------------------------------------------------------------
GATES = {
    "node_stable": dict(
        value="stable", field="CrystalNets.all_nodes",
        source="원본 노트북 1순위. CoRE 제공 판정을 그대로 씀."),
    "PLD_min": dict(
        value=3.3, field="Zeopp.PLD",
        source="원본 노트북 2순위. CO2 운동 지름 3.3 Å.",
        caveat="우리 자료로 반증됨 — MUF-16 은 PLD 3.143 · CO2 탐침 AV 0 인데 "
               "건조 CO2 1.117 mol/kg(모체 0.5839 의 1.9배). "
               "21_ZIF69_MTV/TNF_RESULTS_20260910.md ㉣. 이 관문은 **위상 안에서만** 유효."),
    "water_weak": dict(
        value="weak", field="water.water_classification",
        source="원본 노트북 3순위. CoRE 제공 분류."),
}
# 아래 둘은 **자료를 본 뒤** 만들어진 창입니다. 기술(description)이지 설계 목표가 아닙니다.
WINDOWS_POST_HOC = {
    "N2_sieving": dict(PLD=(3.3, 3.6),
                       note="원본 '매직 윈도우'. 3중 관문이 0개를 낸 뒤 만들어짐."),
    "high_flux": dict(PLD=(3.7, 4.2), LCD_min=5.5,
                      note="원본 '호리병'. 같은 시점에 만들어짐."),
}


class Missing(Exception):
    """필드를 이름으로 못 찾았을 때 — 조용히 넘기지 않습니다 (D1·D2)."""


def dig(rec, path, *, required=True, default=None):
    """`'Zeopp.PLD'` 처럼 **이름으로** 판다. 위치 인덱스를 쓰지 않습니다."""
    cur = rec
    for part in path.split("."):
        if not isinstance(cur, dict) or part not in cur:
            if required:
                raise Missing(path)
            return default
        cur = cur[part]
    return cur


def widom_pair(rec, *, co2_key="CO2", n2_key="N2"):
    """Widom 값을 **이름으로** 꺼냅니다.

    원본은 `widom[0]/widom[1]` 로 위치를 믿었습니다. CoRE 스키마가 리스트라면
    순서를 가정하는 대신 **가정했다는 사실을 돌려주어** 호출한 쪽이 검증하게 합니다.
    """
    w = dig(rec, "GEMC.Widom", required=False)
    if w is None:
        w = dig(rec, "Widom", required=False)
    if isinstance(w, dict):
        return w.get(co2_key), w.get(n2_key), "by-name"
    if isinstance(w, (list, tuple)) and len(w) >= 2:
        return w[0], w[1], "by-position(UNVERIFIED)"
    raise Missing("Widom")


def load_core(path):
    with open(path, encoding="utf-8") as fh:
        raw = json.load(fh)
    return raw if isinstance(raw, dict) else {str(i): r for i, r in enumerate(raw)}


def extract(core, *, gates=GATES):
    """관문 판정에 필요한 값만 뽑고, **못 뽑은 이유를 센다**(D2)."""
    rows, fails = [], collections.Counter()
    for key, rec in core.items():
        row = {"key": key}
        try:
            row["PLD"] = float(dig(rec, "Zeopp.PLD"))
            row["LCD"] = float(dig(rec, "Zeopp.LCD", required=False, default=0.0) or 0.0)
            row["VF"] = float(dig(rec, "Zeopp.VF", required=False, default=0.0) or 0.0)
            row["dimension"] = dig(rec, "Zeopp.dimension", required=False, default=None)
        except (Missing, TypeError, ValueError) as exc:
            fails[f"Zeopp:{exc}"] += 1
            continue
        row["node"] = dig(rec, "CrystalNets.all_nodes", required=False, default=None)
        if row["node"] is None:
            fails["CrystalNets.all_nodes 없음"] += 1
        row["water"] = dig(rec, "water.water_classification", required=False, default=None)
        if row["water"] is None:
            fails["water_classification 없음"] += 1
        try:
            kh_co2, kh_n2, how = widom_pair(rec)
            row["KH_CO2"], row["KH_N2"], row["widom_how"] = kh_co2, kh_n2, how
            row["selectivity"] = (kh_co2 / kh_n2) if (kh_co2 and kh_n2) else None
        except Missing:
            fails["Widom 없음"] += 1
            row["KH_CO2"] = row["KH_N2"] = row["selectivity"] = None
            row["widom_how"] = None
        rows.append(row)
    return rows, fails


def apply_gates(rows, gates=GATES):
    """관문을 **하나씩 따로** 세고, 교집합도 셉니다(원본 '병목 진단'의 정리판)."""
    per = {
        "node_stable": [r for r in rows if r["node"] == gates["node_stable"]["value"]],
        "PLD_min": [r for r in rows if r["PLD"] >= gates["PLD_min"]["value"]],
        "water_weak": [r for r in rows if r["water"] == gates["water_weak"]["value"]],
    }
    passed = [r for r in rows
              if r["node"] == gates["node_stable"]["value"]
              and r["PLD"] >= gates["PLD_min"]["value"]
              and r["water"] == gates["water_weak"]["value"]]
    return per, passed


def rank(rows, key, err_key=None, *, threshold=1.5):
    """오차 열이 있으면 **1.5배 규칙**으로 순위를 매기고, 없으면 순위를 거부합니다(D4).

    CLAUDE.md §2: "차이가 그 1.5배 미만이면 순위를 매기지 않습니다."
    """
    vals = [r for r in rows if r.get(key) is not None]
    vals.sort(key=lambda r: -r[key])
    if not err_key or any(r.get(err_key) is None for r in vals):
        return vals, ("순위 없음 — 오차 열이 없습니다. "
                      "점값 정렬만 돌려줍니다(CLAUDE.md §2: 오차 없이 순위 금지).")
    groups, cur = [], [vals[0]]
    for a, b in zip(vals, vals[1:]):
        d = a[key] - b[key]
        unit = (a[err_key] ** 2 + b[err_key] ** 2) ** 0.5
        if unit > 0 and d >= threshold * unit:
            groups.append(cur); cur = [b]
        else:
            cur.append(b)
    groups.append(cur)
    return groups, f"{len(groups)}덩어리 (문턱 {threshold}×합성 오차)"


def load_ours(path):
    with open(path, encoding="utf-8") as fh:
        d = json.load(fh)
    return d["rows"] if isinstance(d, dict) and "rows" in d else d


def place_ours(ours):
    """우리 조성을 **같은 관문·같은 창**에 넣어 어디 앉는지만 봅니다.

    ⚠ 순위는 안 매깁니다 — CoRE 값과 우리 값은 힘장·전하·프로토콜이 다른
    **다른 계열**입니다(CLAUDE.md §2 "버전을 넘나들며 인용하지 마세요" 의 확장).
    """
    out = {"n": len(ours)}
    out["PLD>=3.3"] = sum(1 for r in ours if (r.get("PLD") or 0) >= 3.3)
    out["PLD>=3.4"] = sum(1 for r in ours if (r.get("PLD") or 0) >= 3.4)
    lo, hi = WINDOWS_POST_HOC["N2_sieving"]["PLD"]
    out["N2_sieving_window"] = [r["name"] for r in ours if lo <= (r.get("PLD") or 0) <= hi]
    lo, hi = WINDOWS_POST_HOC["high_flux"]["PLD"]
    out["high_flux_window"] = [
        r["name"] for r in ours
        if lo <= (r.get("PLD") or 0) <= hi
        and (r.get("LCD") or 0) >= WINDOWS_POST_HOC["high_flux"]["LCD_min"]]
    plds = sorted((r.get("PLD") or 0) for r in ours)
    out["PLD_min_med_max"] = [plds[0], plds[len(plds) // 2], plds[-1]]
    return out


def main():
    ap = argparse.ArgumentParser(description="CoRE MOF 스크리닝 정리본")
    ap.add_argument("--meta", default=os.path.join(HERE, "data", "CR_meta_data_SI.json"))
    ap.add_argument("--ours", default=os.path.join(
        HERE, os.pardir, "21_ZIF69_MTV", "results_v3.json"))
    a = ap.parse_args()

    if os.path.exists(a.ours):
        ours = load_ours(a.ours)
        p = place_ours(ours)
        print(f"\n[우리 조성 {p['n']}개 — CoRE 관문에 얹어 보기]")
        print(f"  PLD >= 3.3  {p['PLD>=3.3']}/{p['n']}   ·   PLD >= 3.4  {p['PLD>=3.4']}/{p['n']}")
        print(f"  PLD 최소/중앙/최대  {p['PLD_min_med_max'][0]:.3f} / "
              f"{p['PLD_min_med_max'][1]:.3f} / {p['PLD_min_med_max'][2]:.3f}")
        print(f"  사후 창 'N2 sieving'(3.3~3.6)  {len(p['N2_sieving_window'])}개 {p['N2_sieving_window']}")
        print(f"  사후 창 'high flux'(3.7~4.2 & LCD>=5.5)  "
              f"{len(p['high_flux_window'])}개 {p['high_flux_window']}")
        groups, note = rank(ours, "selectivity", "selectivity_err")
        print(f"  선택도 순위: {note}")
        if isinstance(groups[0], list):
            for i, g in enumerate(groups[:4], 1):
                print(f"    {i}군: " + ", ".join(
                    f"{r['name']} {r['selectivity']:.1f}±{r['selectivity_err']:.1f}" for r in g))
    else:
        print(f"  (우리 자료 없음: {a.ours})")

    if not os.path.exists(a.meta):
        print(f"\n[CoRE 자료 없음] {a.meta}\n  data/MANIFEST.md 를 보고 내려받으십시오.")
        return 0
    core = load_core(a.meta)
    rows, fails = extract(core)
    per, passed = apply_gates(rows)
    print(f"\n[CoRE {len(core)}개]")
    for k, v in per.items():
        print(f"  {k:12s} {len(v)}개")
    print(f"  3중 관문 교집합  {len(passed)}개")
    if fails:
        print("  못 뽑은 것(조용히 넘기지 않습니다):")
        for k, v in fails.most_common(8):
            print(f"    {v:6d}  {k}")
    hows = collections.Counter(r["widom_how"] for r in rows if r["widom_how"])
    if hows.get("by-position(UNVERIFIED)"):
        print(f"  ⚠ Widom 을 **위치로** 읽은 행 {hows['by-position(UNVERIFIED)']}개 — "
              f"CO2 가 [0] 인지 스키마로 확인하기 전에는 선택도를 인용하지 마십시오(D1).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
