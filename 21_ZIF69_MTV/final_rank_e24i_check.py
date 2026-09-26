#!/usr/bin/env python3
"""E-23 규칙 확장 3(E-24i 열린 자리) 독립 검산 — 클라우드 검증석 cloud 3차 ③. 표준 파이썬 · 원자료만.

`final_crosscheck_e23.py` 의 S · W(ZIF 셋 · 모체)에 E-24i 다섯을 원자료에서 더하고(전 치환 행은 §25 로 보류 — 넣지 않음),
`final_rank_e24g_check.py` 의 해석 셋 × 자 둘 함수로 순위를 냄.
  S_mix: 적재에서 다시 냄 · ± = ±̄/√3 · 씨앗 SD. C₂H₅ 는 막음(성분마다 막음 수 등식 확인).
  물 지수: 4씨앗 평균 ÷ K_H(CO₂ ON). C₂H₅ 는 막음 1.30 물 ÷ 막음 K_H(CO₂ ON @1.65)(등록 보완 27f32f80).
"""
import json, math, os, statistics as st, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import final_crosscheck_e23 as F      # noqa: E402
import final_rank_e24g_check as R     # noqa: E402  (해석 함수 — 모듈 전역 S · W 를 바꿔 씀)


def J(p):
    return json.load(open(os.path.join(HERE, p), encoding="utf-8"))


def smix(p, blocked=False):
    rows = [r for r in J(p)["rows"] if r.get("status") == "ok"]
    if blocked:
        rows = [r for r in rows if all(r["block"][g]["n_blocked"] == r["n_expected"][g] and r["block"][g]["blocked_line"] for g in ("CO2", "N2"))]
    assert len(rows) == 3 and len({r["seed"] for r in rows}) == 3, p
    s = [r["N_CO2"] / r["N_N2"] * (0.85 / 0.15) for r in rows]
    e = [x * math.hypot(r["N_CO2_err"] / r["N_CO2"], r["N_N2_err"] / r["N_N2"]) for x, r in zip(s, rows)]
    return dict(kind="TPL", n=3, mean=st.mean(s), sd=st.stdev(s), pm=st.mean(e) / math.sqrt(3),
                N_CO2=st.mean(r["N_CO2"] for r in rows), seeds=[r["seed"] for r in rows])


def widom_on(p):
    r = [r for r in J(p)["rows"] if r["charges"] == "on"][0]
    return r["KH_CO2"], r["KH_CO2_err"], r["selectivity"]


def water(rows, den):
    assert len(rows) == 4 and len({r["seed"] for r in rows}) == 4
    k = [r["KH_water"] for r in rows]; e = [r["KH_water_err"] for r in rows]
    m, me = st.mean(k), st.mean(e) / 2
    i = m / den[0]
    return dict(idx=i, err=i * math.hypot(me / m, den[1] / den[0]))


WH = J("results_e24i_water_hkhome.json")["rows"]
NEW, SH = {}, {}
for x, mixf in (("cn", "results_e24i_e24i_cn_open_mix_hkhome.json"), ("br", "results_e24i_e24i_br_open_mix_laptop2.json"),
                ("cl", "results_e24i_e24i_cl_open_mix_junseok.json"), ("ch3", "results_e24i_e24i_ch3_open_mix_laptop2.json")):
    t = f"e24i_{x}_open"
    wf = [f for f in os.listdir(HERE) if f.startswith(f"results_magi5_e3_{t}_widom_")][0]
    k, ke, s_on = widom_on(wf)
    NEW[t] = (smix(mixf), water([r for r in WH if r["name"] == t and r["status"] == "ok"], (k, ke)))
    SH[t] = s_on
bp = J("results_e24i_blockpockets_hkhome.json")["per_structure"]["e24i_c2h5_open"]
NEW["e24i_c2h5_open"] = (smix("results_e24i_e24i_c2h5_open_mix_junseok.json", blocked=True),
                        water([r for r in J("results_e24i_c2h5_open_water_blk_junseok.json")["rows"]
                               if r["status"] == "ok" and r["marker_finished"] and r["block"]["n_blocked"] == r["n_expected"]],
                              (bp["rows"]["on_CO2@1.65"]["KH"], bp["rows"]["on_CO2@1.65"]["KH_err"])))
SH["e24i_c2h5_open"] = bp["S_ON_blocked"]

S = {k: v for k, v in F.S.items() if k in ("mslm050", "saIm050", "sa50nb50", "tpl")}
W = {k: v for k, v in F.W.items() if k in S}
for k, (s, w) in NEW.items():
    S[k], W[k] = s, w
R.S, R.W = S, W   # 해석 함수가 이 표를 보게


def main():
    names = list(S)
    seeds = [x for k in NEW for x in NEW[k][0]["seeds"]]
    print(f"# E-23 확장 3 검산 — E-24i 다섯 + 모체 + ZIF 셋 · S_mix 씨앗 {len(seeds)}개 겹침 {len(seeds) - len(set(seeds))}")
    print("\n| 물질 | S_mix ± (±̄/√n) · SD | 비 S_mix/S_Henry | 작동점 N_CO₂ | 물 지수 ± | 모체 대비 S_mix · 물(단위) | ZIF 최선 배수 |")
    print("|---|---|---|---|---|---|---|")
    for g in sorted(names, key=lambda g: -S[g]["mean"]):
        s, w = S[g], W[g]
        rat = f"{s['mean'] / SH[g]:.3f}" if g in SH else "—"
        nco2 = f"{s['N_CO2']:.2f}" if "N_CO2" in s else "—"
        vs = "—" if g == "tpl" else (f"{R.su(g, 'tpl', 'pm'):+.2f} · {R.wu(g, 'tpl'):+.2f}" if s["kind"] == "TPL" else "(ZIF)")
        print(f"| {g} | {s['mean']:.2f} ± {s['pm']:.2f} · {s['sd']:.2f} | {rat} | {nco2} | {w['idx']:.5f} ± {w['err']:.5f} | {vs} | {s['mean'] / S['mslm050']['mean']:.2f} |")
    top = [g for g in names if g.startswith("e24i")]
    print("\n## 짝(S_mix 단위 · 씨앗 SD 자 | 물 지수 단위)")
    for i, a in enumerate(sorted(top, key=lambda g: -S[g]["mean"])):
        for b in sorted(top, key=lambda g: -S[g]["mean"])[i + 1:]:
            print(f"  {a:15s} − {b:15s}: {R.su(a, b, 'pm'):+.2f} · {R.su(a, b, 'sd'):+.2f} | 물 {R.wu(a, b):+.2f}")
    for ruler, lab in (("pm", "±̄/√3 단위(등록)"), ("sd", "씨앗 SD 자")):
        ga = [b for b, _ in R.interp_ga(names, ruler)]
        na, wins, cyc = R.interp_na(names, ruler)
        da = [g for blk in R.interp_da(names, ruler) for g in blk]
        print(f"\n## {lab}")
        print("  (가) 비지배 → 물:", " > ".join(ga))
        print("      1위 후보군:", R.interp_ga(names, ruler)[0][1])
        print("  (나) 쌍별 승수  :", " > ".join(f"{g}({wins[g]})" for g in na), "· 순환", len(cyc))
        print("  (다) 인접 묶음  :", " | ".join("[" + " ".join(b) + "]" for b in R.interp_da(names, ruler)))


if __name__ == "__main__":
    main()
