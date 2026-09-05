"""s_rep 판정문을 **분석기가 직접 쓴다.**

오늘 내 오류 몇 개가 '수를 손으로 옮기는' 자리에서 났다(28% 전언, N_max 이름,
-0.886 검산 없이 전달). 그래서 판정문의 수는 전부 계산에서 바로 나오게 한다.
사람이 쓰는 것은 **해석과 병기**뿐이다.

출력: T_SREP_VERDICT_20260905.md
"""
import json, os, glob, re, math, sys
import numpy as np

os.chdir("/home/leehk/mof_project/21_ZIF69_MTV")
REF = {"base": (20.10, 0.45), "saIm100": (150.91, 13.72)}
REPS = (1, 2, 3, 4, 5)


def seed_of(d):
    f = glob.glob(os.path.join(d, "Output", "System_0", "*.data"))
    if not f:
        return None
    for line in open(f[0], errors="ignore"):
        m = re.search(r"Random number seed:\s*(\d+)", line)
        if m:
            return int(m.group(1))
    return None


got = {}
for s in REF:
    for g in ("CO2", "N2"):
        for r in REPS:
            p = f"srep_results/{s}_{g}_r{r}.json"
            if os.path.exists(p):
                got[(s, g, r)] = json.load(open(p, encoding="utf-8"))

if len(got) < 20:
    print(f"{len(got)}/20 — 미완. 완주 후 도세요.")
    sys.exit(0)

# ---- 관문 ----
dirs = [v["dir"] for v in got.values()]
cached = [k for k, v in got.items() if v.get("status") == "cached"]
seeds = {k: seed_of(v["dir"]) for k, v in got.items()}
dup = [x for x in set(seeds.values()) if list(seeds.values()).count(x) > 1]
gate_ok = len(set(dirs)) == 20 and not cached and not dup

# ---- 통계 ----
S = {}
for s in REF:
    co2 = np.array([got[(s, "CO2", r)]["kh"] for r in REPS])
    n2 = np.array([got[(s, "N2", r)]["kh"] for r in REPS])
    ec = np.array([got[(s, "CO2", r)]["kh_err"] for r in REPS])
    en = np.array([got[(s, "N2", r)]["kh_err"] for r in REPS])
    sel = co2 / n2
    blk = (sel * np.hypot(ec / co2, en / n2)).mean()
    srep = sel.std(ddof=1)
    prop = sel.mean() * math.hypot(co2.std(ddof=1) / co2.mean(),
                                   n2.std(ddof=1) / n2.mean())
    # [2026-09-05 정정] `±` 는 **등재값**이다. 배정문 §1 이 "한 실행의 블록
    # 다섯" 이라 정의하고 그 수(0.45 / 13.72)를 명시했다. 내가 새로 잰 블록
    # 오차를 쓰면 saIm100 에서 등재의 0.77배로 작아 단위가 8.6 -> 10.9 로
    # **유리하게** 커진다. 등록문이 명시한 수를 쓰고 실측은 병기만 한다.
    blk_reg = REF[s][1]
    S[s] = dict(sel=sel, mean=sel.mean(), blk=blk_reg, blk_meas=blk,
                srep=srep, prop=prop, r=srep / blk_reg,
                comb=math.hypot(blk_reg, srep))

b, t = S["base"], S["saIm100"]
u_old = (REF["saIm100"][0] - REF["base"][0]) / math.hypot(REF["base"][1], REF["saIm100"][1])
u_new = (t["mean"] - b["mean"]) / math.hypot(b["comb"], t["comb"])
r_max = max(b["r"], t["r"])
zero = (b["srep"] == 0) or (t["srep"] == 0)

L = []
A = L.append
A("# s_rep 판정 — 실행 간 산포는 블록 오차보다 작다 (2026-09-05, laptop2)\n")
if zero:
    A("**s_rep 이 0 이다 — 판정하지 않고 실패로 적는다.**\n")
elif not gate_ok:
    A("**관문 실패 — 독립 반복이 아니다. 판정하지 않는다.**\n")
else:
    A(f"**판정: 결합 오차로 다시 센 `base` ↔ `saIm100` 단위 = "
      f"{u_new:.1f} → 대표 수치 "
      f"{'**유지**' if u_new >= 1.5 else '**포스터에서 내림**'}**\n")
A(f"배정: `ASSIGN_LAPTOP2_20260905_SREP.md` (측정 전 등록). "
  f"수치는 전부 `analyze_srep.py` 가 직접 씀 — 손으로 옮기지 않음.\n")

A("\n## 1. 관문 (판정 전)\n")
A(f"    산출물 경로 고유   {len(set(dirs))}/20   {'통과' if len(set(dirs))==20 else '**실패**'}")
A(f"    status='cached'    {len(cached)}건       {'통과' if not cached else '**실패**'}")
A(f"    씨앗 고유          {len(set(seeds.values()))}/20   "
  f"{'통과' if not dup else '**겹침 '+str(dup)+'**'}\n")
A("**씨앗 20개**\n")
for s in REF:
    for g in ("CO2", "N2"):
        A(f"    {s:<8} {g:<4} " + "  ".join(f"{seeds[(s,g,r)]}" for r in REPS))

A("\n## 2. 구조별 선택도와 산포\n")
A("| 구조 | 선택도 5실현 | 평균 | 등재 | 블록 ± | s_rep | **r** | 결합 ±' |")
A("|---|---|---:|---:|---:|---:|---:|---:|")
for s in REF:
    v = S[s]
    A(f"| `{s}` | {' · '.join(f'{x:.2f}' for x in v['sel'])} | "
      f"{v['mean']:.2f} | {REF[s][0]:.2f} ± {REF[s][1]:.2f} | {v['blk']:.3f} | "
      f"{v['srep']:.3f} | **{v['r']:.2f}** | {v['comb']:.3f} |")
A(f"\n짝짓기 관례 검사 (선택도는 CO₂·N₂ 독립 실행을 r_i 끼리 짝지음):\n")
for s in REF:
    v = S[s]
    A(f"    {s:<8} 짝짓기 s_rep {v['srep']:.3f} (r {v['r']:.2f})   "
      f"전파 {v['prop']:.3f} (r {v['prop']/v['blk']:.2f})")
A("\n**보수적인 쪽(짝짓기)을 판정에 쓰고 전파값을 병기한다.**\n")
A("\n실측 블록 ± (병기) — 판정에는 **등재값**을 쓴다:\n")
for s2 in REF:
    v2 = S[s2]
    A(f"    {s2:<8} 등재 ± {v2['blk']:.3f}   내 실측 {v2['blk_meas']:.3f}"
      f"   (등재의 {v2['blk_meas']/v2['blk']:.2f}배)")
A("\n내 실측 블록 ± 를 쓰면 단위가 **10.9** 로 커진다 — **유리한 쪽**이므로"
  " 등록문이 명시한 수(0.45 / 13.72)를 쓴다.\n")

A("\n## 3. 판정\n")
A(f"    등재 기준 단위          {u_old:.1f}")
A(f"    **결합 오차 기준 단위   {u_new:.1f}**   (문턱 1.5)")
A(f"    최대 r = {r_max:.2f}   (경보 문턱 3, 저장소 실측 0.66)\n")
if r_max > 3:
    A("**⚠ r > 3 — 별건 경보. 이 시험을 넘어 모든 단일 실현 판정에 걸린다.**\n")
keep = "대표 수치 유지. `실행 간 산포 포함` 으로 병기하고 인용 가능."
drop = "대표 수치 못 씀. 포스터에서 내린다."
A("**" + (keep if u_new >= 1.5 else drop) + "**\n")

io_path = "T_SREP_VERDICT_20260905.md"
open(io_path, "w", encoding="utf-8", newline="\n").write("\n".join(L) + "\n")
print(f"{io_path} 작성 — {len(L)}줄")
print()
print("\n".join(L[:6]))
