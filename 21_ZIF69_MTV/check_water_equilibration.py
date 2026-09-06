"""RH90 조각 실행이 **물 평형에 닿았는가** 를 블록 시계열로 본다.

왜 조각 평균이 아니라 블록인가
------------------------------
조각 러너의 "사슬 연속성" 검사는 **CO2 만** 본다. 그리고 조각 평균 5점으로는
추세가 안 잡힌다 — `base` 는 조각3 이 내려가서 "조각4 만 튄 이상치" 로 읽혔다.

RASPA 는 생산 구간을 5블록으로 쪼개 각 블록 평균을 찍는다. 조각이 사슬로
이어지므로(chunk0 만 초기화 5,000 + RestartFile no, 나머지는 초기화 0 +
RestartFile yes) 블록을 이어 붙이면 생산 전체의 시계열이 된다. 조각당 5점씩
늘어나므로 5조각이면 25점이고, 거기서는 추세가 보인다.

t 값을 믿지 말 것
-----------------
블록은 한 사슬의 연속 구간이라 서로 상관이 있다. OLS 표준오차는 그걸 무시하므로
**아래 t 는 부풀려져 있다.** 그래서 이 스크립트는 t 를 찍되 판정에 쓰지 않는다.
판정에 쓰는 것은 **독립인 조성들의 기울기 부호가 몇 대 몇인가** 다 — 그건 블록
상관과 무관하다.

판정이 아니라 보고다. 문턱을 걸지 않고 수를 적는다.
"""
import glob
import math
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
RUNS = os.path.join(HERE, "water_runs_v3w", "water_runs_chunked")
NAMES = ["base", "saIm0875", "saIm0917", "saIm0958",
         "saIm100", "mslm050", "sa50nb50"]

# 옛 결함-힘장 실행에도 **같은 코드**를 댈 수 있게 뿌리를 인자로 받는다.
# 새 잣대를 옛 수에 대려면 잣대가 하나여야 한다 — 베껴 쓰면 그게 깨진다.
ROOTS = {
    "v3w":  (os.path.join(HERE, "water_runs_v3w", "water_runs_chunked"), NAMES),
    "old":  (os.path.join(HERE, "water_runs_chunked"),
             ["nbIm025", "nbIm075"]),      # 결함 힘장(Hw/Lw 누락) 시절
}


def blocks(path):
    """성분별 5블록 값을 시간순으로 읽는다. mol/kg 줄 바로 뒤의 Block[0..4]."""
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


def series(name):
    """조각을 이어 붙인 (물, CO2) 블록 시계열."""
    w, c = [], []
    for k in range(5):
        f = glob.glob(os.path.join(RUNS, f"rh90_{name}", f"chunk{k}",
                                   "Output", "System_0", "*.data"))
        if not f:
            continue
        d = blocks(f[0])
        if "water" in d:
            w += d["water"]
        if "CO2" in d:
            c += d["CO2"]
    return w, c


def slope(y):
    """기울기, t, 자유도. t 는 블록 상관 때문에 부풀려져 있다 — 참고용."""
    n = len(y)
    if n < 3:
        return None
    x = list(range(n))
    mx, my = sum(x) / n, sum(y) / n
    sxx = sum((v - mx) ** 2 for v in x)
    sxy = sum((x[i] - mx) * (y[i] - my) for i in range(n))
    b = sxy / sxx
    a = my - b * mx
    s2 = sum((y[i] - a - b * x[i]) ** 2 for i in range(n)) / (n - 2)
    se = math.sqrt(s2 / sxx)
    return b, (b / se if se > 0 else 0.0), n - 2, my


def main(argv=None):
    global RUNS
    argv = list(argv if argv is not None else __import__("sys").argv[1:])
    key = argv[0] if argv else "v3w"
    if key not in ROOTS:
        print(f"뿌리 이름은 {list(ROOTS)} 중 하나여야 한다 — 받은 값 {key!r}")
        return 2
    RUNS, names = ROOTS[key]
    print(f"=== 물 평형 점검 (블록 시계열, 보고 항목) — 뿌리 '{key}' ===")
    print(f"  {RUNS}")
    print("  조각 러너의 연속성 검사는 CO2 만 본다. 물이 오르는 중이면")
    print("  **유지율은 평형값이 아니라 상한**이다.")
    print()
    print(f"  {'조성':<10}{'블록':>5}{'물 기울기/블록':>16}{'t':>7}"
          f"{'CO2 기울기/블록':>17}{'t':>7}")
    print("  " + "-" * 64)
    signs = []
    for n in names:
        w, c = series(n)
        sw, sc = slope(w), slope(c)
        if sw is None:
            print(f"  {n:<10}{len(w):>5}  미완 (블록 3개 미만)")
            continue
        signs.append(1 if sw[0] > 0 else -1)
        print(f"  {n:<10}{len(w):>5}{100*sw[0]/sw[3]:>15.2f}%{sw[1]:>7.2f}"
              f"{100*sc[0]/sc[3]:>16.2f}%{sc[1]:>7.2f}")
    print()
    if signs:
        up = sum(1 for s in signs if s > 0)
        p = 0.5 ** len(signs) * (1 if up in (0, len(signs)) else 0)
        print(f"  물 기울기 **{up}/{len(signs)} 양수**"
              + (f"  — 부호검정 p = {p:.3f} (단측)" if p else ""))
        print("  이 부호 일치가 증거다. 위의 t 가 아니다 — 블록은 독립이 아니라")
        print("  한 사슬의 연속 구간이고, OLS 표준오차는 그걸 무시한다.")
    print()
    print("  조각0 만 있는 조성은 초기화 직후의 가장 이른 창이라 채워지는")
    print("  과도상태가 남아 있다. **무게는 15블록 이상 사슬을 돈 조성에 있다.**")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
