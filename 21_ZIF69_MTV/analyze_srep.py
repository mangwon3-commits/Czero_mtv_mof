"""s_rep 분석 — 배정 ASSIGN_LAPTOP2_20260905_SREP.md (+ 데스크탑 3141128).

순서 (등록):
  0. **산출물 경로 20개가 서로 다른가**  <- 캐시가 산포를 0으로 만드는 것을 먼저 막는다
  1. **씨앗 20개가 서로 다른가**          <- 겹치면 그 쌍은 독립 실현이 아니므로 제외
  2. 구조별 s_rep(선택도), r = s_rep / ±
  3. 결합 ±' = sqrt(±^2 + s_rep^2) 로 다시 센 base <-> saIm100 **단위**
  4. 판정: >= 1.5 유지 / < 1.5 내림 / r > 3 별건 경보(판정보다 먼저 보고)
     **s_rep 이 정확히 0 이면 판정하지 않고 실패로 적는다** (데스크탑 추가)

선택도는 실현별로 CO2 r_i / N2 r_i 로 짝짓는다. 두 기체는 독립 실행이라 짝짓기는
**관례**이므로, 곁수로 '기체별 s_rep 을 전파한 값' 도 함께 낸다.
"""
import os, sys, json, glob, math, re
import numpy as np

HERE = "/home/leehk/mof_project/21_ZIF69_MTV"
os.chdir(HERE)
RES = os.path.join(HERE, "srep_results")
RUNS = os.path.join(HERE, "aryl_runs")
STRUCTS = ("base", "saIm100")
GASES = ("CO2", "N2")
REPS = (1, 2, 3, 4, 5)

# 저장소 등재 대표 수치 (배정문 §1)
REF = {"base": (20.10, 0.45), "saIm100": (150.91, 13.72)}


def load():
    d = {}
    for s in STRUCTS:
        for g in GASES:
            for r in REPS:
                p = os.path.join(RES, f"{s}_{g}_r{r}.json")
                if os.path.exists(p):
                    d[(s, g, r)] = json.load(open(p, encoding="utf-8"))
    return d


def seed_of(rundir):
    f = glob.glob(os.path.join(rundir, "Output", "System_0", "*.data"))
    if not f:
        return None
    for line in open(f[0], errors="ignore"):
        m = re.search(r"Random number seed:\s*(\d+)", line)
        if m:
            return int(m.group(1))
    return None


d = load()
print(f"결과 {len(d)}/20")
if len(d) < 20:
    print("  아직 미완. 완주 후 다시 도세요.")
    sys.exit(0)

print()
print("=== 0. 산출물 경로가 서로 다른가 (캐시 방지 확인) ===")
dirs = [v["dir"] for v in d.values()]
print(f"  경로 {len(dirs)}개 중 고유 **{len(set(dirs))}개**")
cached = [k for k, v in d.items() if v.get("status") == "cached"]
print(f"  status='cached' 인 건: **{len(cached)}개** {cached if cached else ''}")
if len(set(dirs)) != 20 or cached:
    print("  ** 실패 — 독립 반복이 아니다. 판정하지 않는다. **")
    sys.exit(1)
print("  -> 통과")

print()
print("=== 1. 씨앗 20개가 서로 다른가 ===")
seeds = {}
for k, v in sorted(d.items()):
    seeds[k] = seed_of(v["dir"])
uniq = len(set(seeds.values()))
for s in STRUCTS:
    for g in GASES:
        row = "  ".join(f"r{r}:{seeds[(s,g,r)]}" for r in REPS)
        print(f"  {s:<8} {g:<4} {row}")
print(f"  고유 씨앗 **{uniq}/20**")
dup = [x for x in set(seeds.values()) if list(seeds.values()).count(x) > 1]
if dup:
    print(f"  ** 겹친 씨앗 {dup} — 해당 쌍은 독립 실현이 아니므로 제외해야 한다 **")
else:
    print("  -> 전부 다름, 통과")

print()
print("=== 2. 선택도와 s_rep ===")
out = {}
for s in STRUCTS:
    sel = []
    for r in REPS:
        c, n = d[(s, "CO2", r)]["kh"], d[(s, "N2", r)]["kh"]
        sel.append(c / n)
    sel = np.array(sel)
    srep = sel.std(ddof=1)
    ref, pm = REF[s]
    out[s] = (sel.mean(), srep, pm)
    print(f"  {s:<8} 선택도 " + " ".join(f"{x:8.2f}" for x in sel))
    print(f"           평균 **{sel.mean():.2f}**  s_rep **{srep:.2f}**  "
          f"블록± {pm:.2f}  **r = {srep/pm:.2f}**   (등재 {ref:.2f})")
    if srep == 0:
        print("           ** s_rep = 0 — 판정하지 않고 실패로 적는다 **")

print()
print("=== 3. 결합 오차로 다시 센 base <-> saIm100 단위 ===")
mb, sb, pb = out["base"]; ms, ss, ps = out["saIm100"]
cb = math.hypot(pb, sb); cs = math.hypot(ps, ss)
u_old = (REF["saIm100"][0] - REF["base"][0]) / math.hypot(REF["base"][1], REF["saIm100"][1])
u_new = (ms - mb) / math.hypot(cb, cs)
print(f"  base      {mb:7.2f}  ±' = sqrt({pb:.2f}² + {sb:.2f}²) = **{cb:.2f}**")
print(f"  saIm100   {ms:7.2f}  ±' = sqrt({ps:.2f}² + {ss:.2f}²) = **{cs:.2f}**")
print(f"  등재 기준 단위 {u_old:.1f}  ->  **실측 기준 {u_new:.1f} 단위**")
print()
r_max = max(sb / pb, ss / ps)
print("=== 4. 판정 ===")
if r_max > 3:
    print(f"  ** r = {r_max:.2f} > 3 — 별건 경보. 판정보다 먼저 보고한다. **")
print(f"  단위 {u_new:.1f}  ->  **{'대표 수치 유지' if u_new >= 1.5 else '포스터에서 내림'}**")
