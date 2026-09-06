"""RH90 유지율 계산 — 분모를 **코드에 박는다**. 글롭으로 찾지 않는다.

`RH90_DENOMINATORS_20260906.md §5` 가 **결과 전에** 등록한 값이다.
09-06 18:2x 에 laptop2 가 파일과 대조해 7개 전부 일치를 확인했다.

## 왜 글롭을 안 쓰나 — 함정이 실재하고 재현된다

    base      순진한 글롭 -> v2_water 0.6711  (등록 정본 v3 **0.5839**, **+13.0%**)
    saIm100   순진한 글롭 -> v2_water 2.3046  (등록 정본 v3 **1.5410**, **+33.1%**)

`v2_` 가 `v3_` 보다 정렬상 앞서서 **먼저 잡힌다.** 분모가 크면 유지율이 작게
나오고, 80/50 문턱 갈래가 바뀐다. **그래서 찾지 않고 박는다.**

사용:  python calc_retention_v3w.py            # 완주분만 계산
"""
import json, os, glob, math, sys

HERE = "/home/leehk/mof_project/21_ZIF69_MTV"
os.chdir(HERE)

# --- 등록 분모 (RH90_DENOMINATORS §5). 절대 글롭으로 바꾸지 말 것 ---
DENOM = {
    "base":     (0.5839, 0.0093, "v3_water/water_results.json"),
    "saIm0875": (1.3031, 0.0215, "v3_water_grid/water_results_laptop.json"),
    "saIm0917": (1.3249, 0.0258, "v3_water_grid_cliff/water_results.json"),
    "saIm0958": (1.5205, 0.0129, "v3_water_grid_cliff/water_results.json"),
    "saIm100":  (1.5410, 0.0225, "v3_water/water_results.json"),
    "mslm050":  (1.2438, 0.0087, "v3_water_mslm050/water_results.json"),
    "sa50nb50": (1.1257, 0.0110, "v4_water_mix/water_results.json"),
}


def guard():
    """등록 분모가 그 파일에 여전히 있는지 — 착수 전 관문."""
    bad = []
    for n, (v, _, p) in DENOM.items():
        got = None
        if os.path.exists(p):
            for r in json.load(open(p, encoding="utf-8")):
                if r.get("name") == n and float(r.get("RH", -1)) == 0.0:
                    got = r.get("CO2_molkg")
                    break
        if got is None or abs(got - v) > 5e-4:
            bad.append((n, v, got, p))
    if bad:
        print("!! 등록 분모가 파일과 어긋납니다 — 계산 중단")
        for b in bad:
            print(f"     {b}")
        return False
    print(f"  [관문] 등록 분모 {len(DENOM)}개 전부 파일과 일치")
    return True


def main():
    if not guard():
        return 1
    src = "v3w_water/water_results.json"
    if not os.path.exists(src):
        # 최종 요약은 7종이 다 끝나야 쓰인다. 그래도 **조각별 물 점검은 돈다** —
        # 조기 경보가 목적이라 늦게 돌면 뜻이 없다.
        print(f"  최종 요약 아직 없음: {src}  (7종 완주 후 생성)")
        water_outlier_report(os.path.join(HERE, "water_runs_v3w"), list(DENOM))
        return 0
    rows = json.load(open(src, encoding="utf-8"))
    print(f"\n{'조성':<10}{'RH90 CO2':>11}{'분모(RH0)':>12}{'유지율':>10}{'±':>8}")
    print("-" * 53)
    out = []
    for r in rows:
        n = r.get("name")
        if n not in DENOM or float(r.get("RH", -1)) != 0.9:
            continue
        c, ce = r["CO2_molkg"], r.get("CO2_err", 0.0)
        d, de, _ = DENOM[n]
        ret = 100 * c / d
        err = ret * math.hypot(ce / c, de / d)
        out.append((n, c, d, ret, err))
        print(f"{n:<10}{c:>11.4f}{d:>12.4f}{ret:>9.1f}%{err:>7.1f}")
    print("-" * 53)
    print(f"  분모는 **등록값 고정**(RH90_DENOMINATORS §5). 글롭 미사용.")
    print(f"  힘장: 수정본(Hw none/Lw none, md5 8e8ec933). 옛 v3 값과 섞지 말 것.")
    water_outlier_report(os.path.join(HERE, 'water_runs_v3w'), list(DENOM))
    return 0



# ---------------------------------------------------------------------------
# 조각별 **물** 이상치 보고 (WATER_FIX §7, 09-06)
#
# 조각 러너의 "사슬 연속성" 검사는 **CO2 만** 본다. `base` 에서 물 조각4 가
# 앞 넷 대비 **+7.06σ** 로 튀었는데 그 검사는 통과로 찍혔다. 물이 오르면 CO2 가
# 내리므로, 물의 이상치는 **유지율이 과대평가일 수 있다는 신호**다.
#
# **판정이 아니라 보고 항목이다** — 수를 바꾸지 않고 옆에 적는다.
# ---------------------------------------------------------------------------
import re as _re
import glob as _glob


def chunk_loadings(runs_root, name):
    """조각별 (CO2, water) 를 출력에서 직접 읽는다."""
    base = os.path.join(runs_root, "water_runs_chunked", f"rh90_{name}")
    out = []
    for k in range(5):
        f = _glob.glob(os.path.join(base, f"chunk{k}", "Output", "System_0", "*.data"))
        if not f:
            continue
        cur, d = None, {}
        for ln in open(f[0], errors="ignore"):
            m = _re.match(r"\s*Component (\d+) \[(\w+)\]", ln)
            if m:
                cur = m.group(2)
            if "Average loading absolute [mol/kg framework]" in ln and cur:
                mm = _re.search(r":?\s*([0-9.eE+-]+)\s*\+/-", ln)
                if mm:
                    d[cur] = float(mm.group(1))
        if "CO2" in d and "water" in d:
            out.append((k, d["CO2"], d["water"]))
    return out


def water_outlier_report(runs_root, names):
    """조각별 물의 이상치를 보고한다. 문턱은 안 건다 — 수만 적는다."""
    import numpy as np
    print()
    print("=== 조각별 **물** 점검 (보고 항목, 판정 아님) ===")
    print("  러너의 연속성 검사는 CO2 만 본다. 물이 오르면 CO2 가 내리므로")
    print("  물의 이상치는 **유지율 과대평가 신호**다.")
    print()
    print(f"  {'조성':<10}{'물 조각별':<40}{'최대 |z|':>9}{'그 조각':>8}")
    print("  " + "-" * 68)
    for n in names:
        ch = chunk_loadings(runs_root, n)
        if len(ch) < 3:
            print(f"  {n:<10}미완 ({len(ch)}조각)")
            continue
        w = np.array([x[2] for x in ch])
        zs = []
        for i in range(len(w)):
            rest = np.delete(w, i)
            sd = rest.std(ddof=1)
            zs.append(abs(w[i] - rest.mean()) / sd if sd > 0 else 0.0)
        i = int(np.argmax(zs))
        flag = "  **" if zs[i] >= 3 else ""
        print(f"  {n:<10}{' '.join('%.4f' % x for x in w):<40}"
              f"{zs[i]:>9.2f}{ch[i][0]:>8}{flag}")
    print()
    print("  |z| 는 **그 조각을 뺀 나머지** 기준이다(자기 자신이 평균을 끌지 않게).")
    print("  3 이상이면 별표. 문턱이 아니라 눈에 띄게 하는 표시다.")

if __name__ == "__main__":
    sys.exit(main())
