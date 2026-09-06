"""옛 결함-힘장 실행과 새 수정-힘장 실행의 **물 표류**를 같은 창에서 잰다.

왜 블록당 기울기를 그대로 못 대는가
-----------------------------------
둘 다 생산 15,000 사이클로 같다. 그런데 **블록 길이가 다르다.**

    옛 whole   : 15,000 을 5블록   ->  3,000 사이클/블록
    새 chunked : 3,000 x 5조각을 25블록 ->  600 사이클/블록

블록당 % 로 비교하면 옛것이 5배 긴 창을 한 점으로 쓰므로 표류가 있어도
블록당 값은 5배로 부풀고, 없어도 그렇다. **잣대가 다르다.**

그래서 블록 index 가 아니라 **사이클 위치**로 자른다. 생산 창의 앞 40% 와
뒤 40% 평균을 견준다. 창이 같으므로 이건 양쪽에서 같은 양이다.

(PREREG_CHECKLIST 5-2: 같은 이름 다른 양. 자를 먼저 쓰고 수를 쓴다.)

무엇이 섞여 있는가 — 유보
-------------------------
옛 chunked 로 남은 것은 nbIm025/nbIm075(나이트로)뿐이고 새것은 전부
설폰산 계열이라 **힘장과 조성이 엉킨다.** 그래서 옛 whole 에서 살아남은
raw 출력 중 **새것과 같은 조성**(base, saIm0875)을 따로 뽑아 나란히 놓는다.
그 짝만이 힘장 하나만 다른 비교다.
"""
import glob
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))

# (표시이름, 출력 glob, 생산 사이클, 블록수, 힘장, 조성)
CASES = [
    # --- 옛 결함 힘장 (Hw/Lw 누락) ---
    ("옛 base",     "water_runs_density_v3/rh90_base/Output/System_0/*.data",
     15000, 5, "결함", "base"),
    ("옛 saIm050",  "water_runs_density_v3/rh90_saIm050/Output/System_0/*.data",
     15000, 5, "결함", "saIm050"),
    ("옛 saIm0875", "water_runs_v3grid/rh90_saIm0875/Output/System_0/*.data",
     15000, 5, "결함", "saIm0875"),
    ("옛 nbIm025*", "water_runs_chunked/rh90_nbIm025/chunk*/Output/System_0/*.data",
     15000, 25, "결함", "nbIm025"),
    ("옛 nbIm075*", "water_runs_chunked/rh90_nbIm075/chunk*/Output/System_0/*.data",
     15000, 25, "결함", "nbIm075"),
    # --- 새 수정 힘장 ---
    ("새 base",     "water_runs_v3w/water_runs_chunked/rh90_base/chunk*/Output/System_0/*.data",
     15000, 25, "수정", "base"),
    ("새 mslm050",  "water_runs_v3w/water_runs_chunked/rh90_mslm050/chunk*/Output/System_0/*.data",
     None, None, "수정", "mslm050"),
    ("새 sa50nb50", "water_runs_v3w/water_runs_chunked/rh90_sa50nb50/chunk*/Output/System_0/*.data",
     None, None, "수정", "sa50nb50"),
    ("새 saIm0875", "water_runs_v3w/water_runs_chunked/rh90_saIm0875/chunk*/Output/System_0/*.data",
     None, None, "수정", "saIm0875"),
    ("새 saIm0917", "water_runs_v3w/water_runs_chunked/rh90_saIm0917/chunk*/Output/System_0/*.data",
     None, None, "수정", "saIm0917"),
]


def blocks(path):
    lines = open(path, errors="ignore").read().splitlines()
    cur, out = None, {}
    for i, ln in enumerate(lines):
        m = re.match(r"\s*Component (\d+) \[(\w+)\]", ln)
        if m:
            cur = m.group(2)
        if "Average loading absolute [mol/kg framework]" in ln and cur:
            b = []
            for j in range(i, min(i + 14, len(lines))):
                mm = re.match(r"\s*Block\[\s*(\d+)\]\s+([0-9.eE+-]+)", lines[j])
                if mm:
                    b.append(float(mm.group(2)))
                if len(b) == 5:
                    break
            if len(b) == 5:
                out[cur] = b
    return out


def series(pattern):
    """조각을 chunk 번호 순으로 이어 붙인 (물, CO2) 블록열."""
    files = sorted(glob.glob(os.path.join(HERE, pattern)),
                   key=lambda p: int(re.search(r"chunk(\d+)", p).group(1))
                   if "chunk" in p else 0)
    w, c = [], []
    for f in files:
        d = blocks(f)
        if "water" in d:
            w += d["water"]
        if "CO2" in d:
            c += d["CO2"]
    return w, c


def edges(v, frac=0.4):
    """앞 frac 과 뒤 frac 의 평균. 블록수가 달라도 **창의 같은 비율**을 쓴다."""
    k = max(1, int(round(len(v) * frac)))
    a = sum(v[:k]) / k
    b = sum(v[-k:]) / k
    return a, b, k


def main():
    print("=== 옛 결함판 vs 새 수정판 — 물이 아직 오르는가 ===")
    print("  생산 창의 **앞 40% 대 뒤 40%**. 블록 길이가 달라서 블록당 기울기는")
    print("  그대로 못 댄다(옛 3,000 사이클/블록, 새 600). 창 비율로 자른다.")
    print()
    print(f"  {'실행':<12}{'힘장':<6}{'블록':>5}{'물 앞40%':>10}{'뒤40%':>10}"
          f"{'변화':>9}{'CO2 변화':>10}")
    print("  " + "-" * 64)
    rows = []
    for label, pat, _cyc, _nb, ff, comp in CASES:
        w, c = series(pat)
        if len(w) < 4:
            print(f"  {label:<12}{ff:<6}{len(w):>5}  (블록 부족)")
            continue
        aw, bw, k = edges(w)
        ac, bc, _ = edges(c)
        dw = 100 * (bw - aw) / aw
        dc = 100 * (bc - ac) / ac
        rows.append((label, ff, comp, dw, dc, len(w)))
        print(f"  {label:<12}{ff:<6}{len(w):>5}{aw:>10.2f}{bw:>10.2f}"
              f"{dw:>+8.1f}%{dc:>+9.1f}%")

    print()
    print("  === 힘장 하나만 다른 짝 (조성 같음) ===")
    by = {}
    for label, ff, comp, dw, dc, n in rows:
        by.setdefault(comp, {})[ff] = (dw, dc, n, label)
    any_pair = False
    for comp, d in by.items():
        if "결함" in d and "수정" in d:
            any_pair = True
            o, nw = d["결함"], d["수정"]
            print(f"    {comp:<10} 결함 {o[0]:+6.1f}%  ->  수정 {nw[0]:+6.1f}%"
                  f"   (블록 {o[2]} vs {nw[2]})")
    if not any_pair:
        print("    없음 — 힘장과 조성이 엉켜 있다. 이 표로는 갈라낼 수 없다.")
    print()
    print("  나머지 조성은 짝이 없다. 옛 chunked 는 나이트로뿐이고 새것은")
    print("  전부 설폰산이라, 짝이 없는 줄에서는 **힘장과 조성이 엉켜 있다.**")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
