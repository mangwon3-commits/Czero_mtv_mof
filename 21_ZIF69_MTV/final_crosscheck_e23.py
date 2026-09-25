#!/usr/bin/env python3
"""E-23 최종 순위 독립 검산 (2026-09-26, 클라우드 세션 — 종합자 HKHOME 보조).

판정문 `MAGI5_E23_FINAL_RANKING_20260926.md` 의 수를 **원자료 JSON 에서만** 다시 낸다.
판정문의 수는 한 개도 읽지 않는다(대조는 맨 끝 표에서 사람이 한다 — 기대값은
판정문 표를 옮겨 적은 REPORTED 사전뿐이고 계산에는 안 쓰인다).

규칙(등록 ee13bd2f, ASSIGN_MAGI5B §HKHOME 12차):
  ① 배치 평균 S_mix — 배치 단위 d/√(SD₁²+SD₂²) 1.5 (단위 ± 병기)
     형판 계열(배치 없음) 대 앙상블은 분모 = 앙상블 SD(RULER_DECISION §7 "앙상블 대 모체")
     형판 계열끼리는 3씨앗 ±̄/√3 합성(단위) — 씨앗 SD 병기
  ② ① 동률이면 물 지수(4씨앗) 단위 1.5
  ③ 그래도 동률이면 공동
관문 조인(CLAUDE.md §2): 순위에 드는 모든 실현이 관문 ⑤ pass 인지 결과 파일에서 확인.

실행: python final_crosscheck_e23.py [--json out.json]
"""
import json, math, statistics as st, sys, os

HERE = os.path.dirname(os.path.abspath(__file__))
def J(p): return json.load(open(os.path.join(HERE, p)))

FF = "8e8ec933f9013c7e932da04dc256efd3"
problems = []

# ---------------------------------------------------------------- 0. 행 모으기 + 표지 관문
def mixrows(p):
    d = J(p)
    out = {}
    for r in d["rows"]:
        tag = f"{p}:{r['name']}"
        if r.get("status") != "ok": problems.append(f"{tag} status={r.get('status')}")
        if r.get("returncode") != 0: problems.append(f"{tag} rc={r.get('returncode')}")
        if not r.get("finished"): problems.append(f"{tag} finished 없음")
        if r.get("ff_md5") != FF: problems.append(f"{tag} ff_md5={r.get('ff_md5')}")
        if r.get("S_mix") is None: problems.append(f"{tag} S_mix 없음")
        out[r["name"]] = r
    return out

M = {}
for p in ["results_tj1_mix_laptop.json", "results_e21b_mix_junseok.json",
          "results_e23_mix_junseok.json", "results_e23_mix_desktop.json",
          "results_e24_mix_desktop.json", "results_e24b_mix_desktop.json"]:
    for k, v in mixrows(p).items():
        M[(p, k)] = v

seeds = [v["seed"] for v in M.values()]
dup = len(seeds) - len(set(seeds))
if dup: problems.append(f"씨앗 겹침 {dup}")

def row(p, n): return M[(p, n)]
TJ, E21B = "results_tj1_mix_laptop.json", "results_e21b_mix_junseok.json"
E23J, E23D = "results_e23_mix_junseok.json", "results_e23_mix_desktop.json"
E24, E24B = "results_e24_mix_desktop.json", "results_e24b_mix_desktop.json"

# ---------------------------------------------------------------- 1. 실현 모으기
# e0 = T-J1' s1 + E-21b s2·s3 평균(sa50nb50 은 s1 만) — 등록 문구 그대로
def e0(comp):
    rs = [row(TJ, comp)]
    if comp != "sa50nb50":
        rs += [row(E21B, f"{comp}_s2"), row(E21B, f"{comp}_s3")]
    S = st.mean(r["S_mix"] for r in rs)
    # e0 의 ± = 씨앗 ±̄/√n_seed(평균의 오차) — 판정문과 같은 규약. 보수 규약(씨앗 ±̄ 그대로)은 err_cons
    err_cons = st.mean(r["S_mix_err"] for r in rs)
    err = err_cons / math.sqrt(len(rs))
    SH = rs[0]["S_Henry"]
    return dict(S=S, err=err, err_cons=err_cons, SH=SH, ratio=S / SH, n_seed=len(rs))

def ens(comp, src):
    out = [dict(name=f"{comp}e0", **e0(comp))]
    for i in range(1, 6):
        r = row(src, f"{comp}e{i}")
        out.append(dict(name=r["name"], S=r["S_mix"], err=r["S_mix_err"],
                        SH=r["S_Henry"], ratio=r["S_mix"] / r["S_Henry"], n_seed=1))
    return out

def seeds3(src, stem):
    return [dict(name=f"{stem}_s{i}", S=row(src, f"{stem}_s{i}")["S_mix"],
                 err=row(src, f"{stem}_s{i}")["S_mix_err"],
                 SH=row(src, f"{stem}_s{i}")["S_Henry"],
                 ratio=row(src, f"{stem}_s{i}")["S_mix"] / row(src, f"{stem}_s{i}")["S_Henry"])
            for i in (1, 2, 3)]

GROUPS = {
    "mslm050":  ("ZIF", ens("mslm050", E23J)),
    "saIm050":  ("ZIF", ens("saIm050", E23J)),
    "sa50nb50": ("ZIF", ens("sa50nb50", E23D)),
    "tpl":      ("TPL", seeds3(E23D, "e22_parent")),
    "tpl_CN":   ("TPL", seeds3(E24, "e24_cn_100")),
    "tpl_CH3":  ("TPL", seeds3(E24B, "e24_ch3_100")),
}

S = {}
for g, (kind, rs) in GROUPS.items():
    v = [r["S"] for r in rs]
    n = len(v)
    S[g] = dict(kind=kind, n=n, vals=v, mean=st.mean(v), sd=st.stdev(v),
                pm=st.mean(r["err"] for r in rs) / math.sqrt(n),
                pm_cons=st.mean(r.get("err_cons", r["err"]) for r in rs) / math.sqrt(n),
                ratio=st.mean(r["ratio"] for r in rs),
                ratio_sd=st.stdev(r["ratio"] for r in rs))

# ---------------------------------------------------------------- 2. 물 지수(4씨앗)
W = {}
e19 = J("results_magi5_e19_water_seeds_junseok.json")["compositions"]
for c in ("mslm050", "saIm050", "sa50nb50"):
    x = e19[c]
    kw = st.mean(x["KH_water_each"])
    if abs(kw - x["KH_water_mean"]) > 1e-12: problems.append(f"E-19 {c} 평균 불일치")
    idx = kw / x["KH_CO2"]
    err = idx * math.hypot(x["KH_water_mean_err"] / kw, x["KH_CO2_err"] / x["KH_CO2"])
    W[c] = dict(idx=idx, err=err, n=len(x["KH_water_each"]), src="E-19")

def tpl_water(water_file, name, widom_file):
    rs = [r for r in J(water_file)["rows"] if r["name"] == name]
    for r in rs:
        if r.get("status") != "ok" or r.get("returncode") != 0 or not r.get("marker_finished") \
           or not r.get("header_gate_ok") or r.get("water_sites_in_rundir") != 5:
            problems.append(f"{water_file}:{name} s{r.get('seed_idx')} 표지 이상")
    kw = st.mean(r["KH_water"] for r in rs)
    kw_err = st.mean(r["KH_water_err"] for r in rs) / math.sqrt(len(rs))
    on = [r for r in J(widom_file)["rows"] if r["charges"] == "on"][0]
    idx = kw / on["KH_CO2"]
    err = idx * math.hypot(kw_err / kw, on["KH_CO2_err"] / on["KH_CO2"])
    return dict(idx=idx, err=err, n=len(rs), seed_sd=st.stdev(r["KH_water"] for r in rs) / on["KH_CO2"])

W["tpl"] = tpl_water("results_e22c_water_hkhome.json", "e22_parent",
                     "results_magi5_e3_e22_parent_widom_desktop-js1ib6u.json")
W["tpl_CN"] = tpl_water("results_e24_cn_water_hkhome.json", "e24_cn_100",
                        "results_magi5_e3_e24_cn_100_widom_hkhome.json")
W["tpl_CH3"] = tpl_water("results_e24b_ch3_water_hkhome.json", "e24_ch3_100",
                         "results_magi5_e3_e24_ch3_100_widom_hkhome.json")

# ---------------------------------------------------------------- 3. 관문 조인
G = {}
def gate(file, key):
    d = J(file)
    rows = d["rows"]
    r = rows.get(key) if isinstance(rows, dict) else next((x for x in rows if x.get("name") == key), None)
    return None if r is None else (r.get("status") == "ok" and r.get("pass") is True)
for i in range(1, 6):
    G[f"mslm050e{i}"] = gate("results_e14d_gate5_hkhome.json", f"mslm050e{i}")
    G[f"saIm050e{i}"] = gate("risk_results_v3ens0500.json", f"saIm050e{i}")
    G[f"sa50nb50e{i}"] = gate("risk_results_v3ens50nb50.json", f"sa50nb50e{i}")
G["mslm050e0"] = gate("risk_results_v3.json", "mslm050")
G["saIm050e0"] = gate("risk_results_v3.json", "saIm050")
G["sa50nb50e0"] = gate("risk_results_v3ens50nb50.json", "sa50nb50")
G["tpl"] = gate("results_e22b_gate5_hkhome.json", "e22_parent")
G["tpl_CN"] = gate("results_e24_gate5_junseok.json", "e24_cn_100")
G["tpl_CH3"] = gate("results_e24_gate5_junseok.json", "e24_ch3_100")
acc = {r["tag"]: r for r in J("results_e24b_access_junseok.json")["rows"]}
ACC = {}
for g, tag in (("tpl", "e22_parent"), ("tpl_CN", "e24_cn_100"), ("tpl_CH3", "e24_ch3_100")):
    r = acc[tag]
    pockets = [r[k]["chan"]["pockets_stdout"] for k in ("r1.65", "r1.82") if k in r]
    ACC[g] = dict(PLD=r["PLD_Df"], pockets=pockets, ok=r["PLD_Df"] >= 3.64 and all(p == 0 for p in pockets))
for k, v in G.items():
    if v is not True: problems.append(f"관문 ⑤ {k} = {v}")
for k, v in ACC.items():
    if not v["ok"]: problems.append(f"E-24b ① {k} = {v}")

# ---------------------------------------------------------------- 4. 규칙 적용
def cmp(a, b):
    """a − b 를 등록 자로. 반환 (배치 단위 또는 None, 단위)."""
    A, B = S[a], S[b]
    d = A["mean"] - B["mean"]
    u = d / math.hypot(A["pm"], B["pm"])
    if A["kind"] == "ZIF" and B["kind"] == "ZIF":
        bu = d / math.hypot(A["sd"], B["sd"])
    elif A["kind"] == "TPL" and B["kind"] == "ZIF":
        bu = d / B["sd"]
    elif A["kind"] == "ZIF" and B["kind"] == "TPL":
        bu = d / A["sd"]
    else:
        bu = None           # 형판 계열끼리는 배치 없음 — 단위(±̄/√3)로
    return bu, u

def wcmp(a, b):
    A, B = W[a], W[b]
    return (A["idx"] - B["idx"]) / math.hypot(A["err"], B["err"])

def tie(a, b):
    bu, u = cmp(a, b)
    key = bu if bu is not None else u
    return abs(key) < 1.5

def rank(names):
    # 등록 규칙: S_mix 평균 내림차순, 인접한 동률 묶음 안은 물 지수(낮을수록 위)로
    order = sorted(names, key=lambda g: -S[g]["mean"])
    blocks, cur = [], [order[0]]
    for g in order[1:]:
        if all(tie(h, g) for h in cur): cur.append(g)
        else: blocks.append(cur); cur = [g]
    blocks.append(cur)
    out = []
    for b in blocks:
        b = sorted(b, key=lambda g: W[g]["idx"])
        out.append(b)
    return out

# ---------------------------------------------------------------- 5. 출력
REPORTED = {  # 판정문 표(대조용 — 계산에 안 씀)
    "mslm050": (39.71, 3.39, 0.38, 0.568, 0.718, 0.050),
    "saIm050": (38.80, 2.66, 0.29, 0.669, 1.340, 0.283),
    "sa50nb50": (38.05, 5.07, 0.31, 0.533, 2.471, 0.582),
    "tpl": (75.43, 0.42, 2.14, 0.859, 0.0147, 0.0003),
    "tpl_CN": (122.56, 1.49, 4.85, 1.112, 0.119, 0.013),
    "tpl_CH3": (128.62, 4.15, 4.63, 0.835, 0.0101, 0.0002),
}
def main():
    res = {"problems": problems, "groups": {}, "pairs": {}, "rank": {}}
    print("# E-23 독립 검산 — 원자료만")
    print(f"행 {len(M)} · 씨앗 겹침 {dup} · 관문 ⑤ {sum(v is True for v in G.values())}/{len(G)} pass · E-24b ① {sum(v['ok'] for v in ACC.values())}/{len(ACC)}")
    print("\n| 물질 | n | S_mix | SD | ±̄/√n | 비 | 비 SD | 물 지수 ± | 판정문과 최대 차 |")
    print("|---|---|---|---|---|---|---|---|---|")
    for g, s in S.items():
        w = W[g]
        mine = (s["mean"], s["sd"], s["pm"], s["ratio"], w["idx"], w["err"])
        rep = REPORTED[g]
        # 판정문 반올림 자리에서의 차
        diffs = [abs(a - b) for a, b in zip(mine, rep)]
        tol = [0.005, 0.005, 0.005, 0.0005, 5e-4 if rep[4] > 0.1 else 5e-5, 5e-4 if rep[5] > 0.01 else 5e-5]
        flag = "일치" if all(d <= t * 1.01 for d, t in zip(diffs, tol)) else "차이: " + ", ".join(
            f"{n}={m:.4g}/{r:.4g}" for n, m, r, d, t in zip(["S", "SD", "pm", "비", "지수", "지수±"], mine, rep, diffs, tol) if d > t * 1.01)
        print(f"| {g} | {s['n']} | {s['mean']:.2f} | {s['sd']:.2f} | {s['pm']:.2f} | {s['ratio']:.3f} | {s['ratio_sd']:.3f} | {w['idx']:.4g} ± {w['err']:.2g} | {flag} |")
        res["groups"][g] = dict(**{k: v for k, v in s.items()}, water=w, match=flag)
    print("\n## 짝 비교 (배치 단위 · 단위)  — 물 지수 단위")
    for a, b in [("mslm050", "saIm050"), ("mslm050", "sa50nb50"), ("saIm050", "sa50nb50"),
                 ("tpl", "mslm050"), ("tpl", "saIm050"), ("tpl", "sa50nb50"),
                 ("tpl_CH3", "tpl_CN"), ("tpl_CH3", "tpl"), ("tpl_CN", "tpl"),
                 ("tpl_CN", "sa50nb50"), ("tpl_CH3", "saIm050")]:
        bu, u = cmp(a, b)
        wu = wcmp(a, b)
        uc = (S[a]["mean"] - S[b]["mean"]) / math.hypot(S[a]["pm_cons"], S[b]["pm_cons"])
        print(f"  {a:9s} − {b:9s}: " + (f"{bu:+.2f} 배치 단위 · " if bu is not None else "(배치 없음) · ") + f"{u:+.2f} 단위 (보수 규약 {uc:+.2f}) | 물 지수 {wu:+.2f} 단위")
        res["pairs"][f"{a}-{b}"] = dict(batch_units=bu, units=u, units_conservative=uc, water_units=wu)
    # 비 (3) — 형판 비 대 ZIF 배치 평균 비, 분모 = ZIF 비의 배치 SD
    print("\n## (3) 비 S_mix/S_Henry — 형판 대 ZIF(분모 ZIF 비 배치 SD)")
    for z in ("mslm050", "saIm050", "sa50nb50"):
        print(f"  tpl {S['tpl']['ratio']:.3f} − {z} {S[z]['ratio']:.3f} = {(S['tpl']['ratio']-S[z]['ratio'])/S[z]['ratio_sd']:+.2f} 배치 단위")
    print("\n## 최종 1위 규칙")
    for lab, names in (("ZIF 목록", ["mslm050", "saIm050", "sa50nb50"]),
                       ("전체 목록", list(S.keys()))):
        r = rank(names)
        def inner(b):
            if len(b) == 1: return b[0]
            s = b[0]
            for x, y in zip(b, b[1:]):
                s += (" > " if abs(wcmp(x, y)) >= 1.5 else " = ") + y
            return "[" + s + "]"
        print(f"  {lab}: " + "  >  ".join(inner(b) for b in r)
              + "   ([ ] = S_mix 동률 묶음 — 안은 물 지수 ② 로, '=' 이면 ③ 공동)")
        res["rank"][lab] = r
    print("\n## 문제", "없음" if not problems else "")
    for p in problems: print("  -", p)
    if "--json" in sys.argv:
        out = sys.argv[sys.argv.index("--json") + 1]
        json.dump(res, open(out, "w"), ensure_ascii=False, indent=1, default=str)

if __name__ == "__main__":
    main()
