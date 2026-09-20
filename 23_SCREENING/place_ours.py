"""우리 31조성을 CoRE 분포 위에 **얹어 보는** 계산 — 순위는 매기지 않습니다.

[왜 별도 파일인가]
    `screen_core.py` 의 `place_ours()` 는 관문·창 통과 여부만 셉니다(기하 축).
    여기서는 K_H(CO2)·선택도 같은 **성능 축**에 얹는데, 그건 계열이 달라 훨씬 조심해야 합니다.

[규율 — 이 파일이 지키는 것]
    ① **하나의 합친 순위를 만들지 않습니다.** CoRE 는 UFF + TraPPE, 우리는 UFF_MOF + Garcia-Sanchez 2009 로
       힘장·전하·프로토콜이 다릅니다. CLAUDE.md §2 "버전을 넘나들며 인용하지 마세요" 의 확장입니다.
    ② 백분위는 **세 모집단에서 따로** 냅니다(전체 / 관문 통과 / 우리와 같은 PLD 대역).
       셋이 크게 다르면 그 자체가 답입니다 — "어느 집단과 비교하느냐에 달렸다".
    ③ 발산한 Widom 행(>1 mmol/g/Pa)은 **빼고** 셉니다. 넣으면 백분위가 무의미해집니다.
    ④ 우리 쪽 순위는 **우리끼리만**, 1.5 규칙으로(`screen_core.rank`).
    ⑤ 힘장 차이의 크기를 **숫자로** 병기합니다(중앙값 비). 이것은 교정이 아니라 눈금 차이의 표시입니다.

사용:
    python3 place_ours.py --meta data/CR_meta_data_SI_slice.json --ours ../21_ZIF69_MTV/results_v3.json
"""
import argparse
import os
import statistics as st
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from screen_core import (GATES, NODE_BAD, NODE_UNKNOWN, WIDOM_SANITY_MAX,
                         apply_gates, extract, load_core, load_ours, rank)


def sane(rows, key=None):
    """발산 문턱은 **K_H 에만** 겁니다 — 선택도는 비(比)라서 같은 문턱을 걸면 안 됩니다.

    (2026-09-20 21:1x: 처음 판이 `selectivity < 1` 만 남겨 백분위가 전부 100 % 로 나왔습니다.
     두 K_H 가 모두 물리적 범위일 때 그 행 전체를 채택하고, 선택도는 그 행에서 읽습니다.)
    """
    out = []
    for r in rows:
        a, b = r.get("KH_CO2"), r.get("KH_N2")
        if not (a and b):
            continue
        if 0 < a < WIDOM_SANITY_MAX and 0 < b < WIDOM_SANITY_MAX:
            out.append(r)
    return out


def pct(sorted_vals, x):
    """x 보다 작은 값의 비율(%). 정렬된 목록 위에서 선형 탐색이면 충분합니다(n<2e4)."""
    n = len(sorted_vals)
    lo, hi = 0, n
    while lo < hi:
        mid = (lo + hi) // 2
        if sorted_vals[mid] < x:
            lo = mid + 1
        else:
            hi = mid
    return 100.0 * lo / n


def populations(rows, ours):
    """비교 모집단 셋. 같은 답이 셋에서 다 나오면 강하고, 갈리면 그 사실이 결론입니다."""
    per, passed = apply_gates(rows)
    plds = [r["PLD"] for r in ours if r.get("PLD")]
    lo, hi = min(plds), max(plds)
    band = [r for r in rows if lo <= r["PLD"] <= hi]
    return [
        ("CoRE 전체", rows),
        ("관문 통과", passed),
        (f"우리 PLD 대역 {lo:.2f}~{hi:.2f}", band),
    ]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--meta", required=True)
    ap.add_argument("--ours", required=True)
    a = ap.parse_args()

    core = load_core(a.meta)
    rows, _ = extract(core)
    ours = load_ours(a.ours)

    print("=" * 78)
    print("우리 31조성을 CoRE 위에 얹기 — **순위 아님**, 위치만")
    print("=" * 78)

    # ── 눈금 차이부터 ────────────────────────────────────────────────────────
    ock = sorted(r["KH_CO2"] for r in sane(ours))
    osl = sorted(r["selectivity"] for r in ours if r.get("selectivity"))
    print("\n[0] 눈금이 다릅니다 — 먼저 그 크기를 적습니다")
    print("    CoRE   UFF + TraPPE            ·  우리  UFF_MOF + Garcia-Sanchez 2009 + PACMAN DDEC6")
    for name, pop in populations(rows, ours):
        ck = sorted(r["KH_CO2"] for r in sane(pop))
        cs = sorted(r["selectivity"] for r in sane(pop) if r.get("selectivity"))
        if not ck:
            continue
        print(f"    {name:22s} K_H(CO2) 중앙 {st.median(ck):.3e}  →  우리/CoRE = "
              f"{st.median(ock)/st.median(ck):5.2f} 배   |   선택도 중앙 {st.median(cs):6.2f} "
              f"→ {st.median(osl)/st.median(cs):5.2f} 배")
    print("    ⚠ 이 배율은 **교정이 아닙니다.** 눈금이 이만큼 어긋나 있다는 표시입니다.")

    # ── 백분위 ──────────────────────────────────────────────────────────────
    for axis, okey, label in (("KH_CO2", "KH_CO2", "CO2 친화도 K_H"),
                              ("selectivity", "selectivity", "CO2/N2 선택도")):
        print(f"\n[{'1' if axis == 'KH_CO2' else '2'}] {label} — 우리 조성의 백분위 (모집단 셋)")
        pops = []
        for name, pop in populations(rows, ours):
            vals = sorted(r[axis] for r in sane(pop) if r.get(axis))
            if len(vals) >= 30:
                pops.append((name, vals))
        head = "    조성            우리 값      " + "".join(f"{n[:16]:>18s}" for n, _ in pops)
        print(head)
        sel = sorted(ours, key=lambda r: -(r.get(okey) or 0))
        for r in sel[:6] + [None] + sel[-3:]:
            if r is None:
                print("    " + "…" * 6)
                continue
            v = r.get(okey)
            if not v:
                continue
            cells = "".join(f"{pct(vals, v):15.1f} %" for _, vals in pops)
            print(f"    {r['name']:14s} {v:10.4g}   {cells}")
        med = st.median([r[okey] for r in ours if r.get(okey)])
        cells = "".join(f"{pct(vals, med):15.1f} %" for _, vals in pops)
        print(f"    {'(우리 중앙값)':14s} {med:10.4g}   {cells}")
        for name, vals in pops:
            print(f"      · {name}: n={len(vals)}")

    # ── 눈금에 안 먹히는 비교: 산포 ─────────────────────────────────────────
    print("\n[2b] 눈금 차이에 **안 먹히는** 비교 — 각 계열 안에서의 산포(배수)")
    print("     수준(level) 비교는 힘장 오프셋이 통째로 먹어 버립니다. 비(比)는 안 먹힙니다.")
    for axis, label in (("KH_CO2", "K_H(CO2)"), ("selectivity", "선택도")):
        ov = sorted(r[axis] for r in ours if r.get(axis))
        print(f"\n     {label}")
        print(f"       우리 31조성          최소 {ov[0]:.4g} → 최대 {ov[-1]:.4g}   "
              f"= **{ov[-1]/ov[0]:.1f} 배**   (사분위 {ov[len(ov)//4]:.4g}~{ov[3*len(ov)//4]:.4g} = {ov[3*len(ov)//4]/ov[len(ov)//4]:.1f} 배)")
        for name, pop in populations(rows, ours):
            cv = sorted(r[axis] for r in sane(pop) if r.get(axis))
            if len(cv) < 30:
                continue
            n = len(cv)
            print(f"       {name:20s} 5~95 % {cv[n//20]:.4g} → {cv[19*n//20]:.4g}   "
                  f"= **{cv[19*n//20]/cv[n//20]:.1f} 배**   (사분위 {cv[n//4]/cv[3*n//4] and cv[3*n//4]/cv[n//4]:.1f} 배)")
    print("\n     읽기: 링커 치환으로 우리가 움직인 폭과, CoRE 전체가 **구조 다양성**으로 벌린 폭의 비교입니다.")
    print("           (우리 쪽은 전 범위, CoRE 쪽은 5~95 % — 발산·꼬리를 뺀 보수적 대역입니다.)")

    # ── 우리끼리의 순위 (여기서만 유효) ──────────────────────────────────────
    print("\n[3] 우리끼리의 순위 — 1.5 규칙 (여기서만 순위가 성립합니다)")
    for key, err in (("selectivity", "selectivity_err"), ("KH_CO2", "KH_CO2_err")):
        groups, note = rank(ours, key, err)
        print(f"    {key}: {note}")
        if isinstance(groups, list) and groups and isinstance(groups[0], list):
            for i, g in enumerate(groups[:5], 1):
                txt = ", ".join(f"{r['name']} {r[key]:.4g}±{r[err]:.3g}" for r in g)
                print(f"      {i}군: {txt}")

    print("\n[4] 우리가 **좌표를 갖고 있지 않은** 축")
    print("    CoRE 관문 3개 중 우리가 가진 것은 PLD 하나뿐입니다.")
    print("    · water_classification  — CoRE 는 GEMC 물 등온선으로 분류. 우리는 그 계산을 안 했습니다.")
    print("    · CrystalNets 위상/안정성 — 우리 v3 구조에 CrystalNets 를 돌린 적이 없습니다.")
    print("    두 축에서 우리 위치는 **모름**이지, 통과가 아닙니다. 이것이 갈래 (C) 가 할 일입니다.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
