#!/usr/bin/env python3
"""E-23 최종 1위 규칙 확장 2(E-24g · E-24h 뒤) 독립 검산 — 클라우드 검증석 15회차. 표준 파이썬만 · 원자료 JSON 만 읽음.

기존 8물질(`final_crosscheck_e23.py` 의 S · W)에 형판 계열 다섯을 원자료에서 더함:
  Cl 100      S_mix results_e24d_cl_mix_laptop2.json            · 물 results_e24d_cl_water_hkhome.json ÷ E-24c Widom ON
  C₂H₅ 100    S_mix results_e24e_c2h5_mix_junseok.json(막음)    · 물 results_e24e_c2h5_water_junseok.json block1.30(요약의 지수 — 분모 막음 K_H)
  Br 100      S_mix results_e24g_e24g_br_100_mix_laptop2.json   · 물 results_e24g_water_laptop.json ÷ E-24g Widom ON
  Cl 50 a     S_mix results_e24g_e24h_cl_050a_mix_laptop2.json  · 물 같은 laptop 파일 ÷ E-24h Widom ON
  C₂H₅ 50 a   S_mix results_e24g_e24h_c2h5_050a_mix_junseok.json(막음) · 물 …_water_junseok.json 요약(막음 1.30)
비추이 동률 해석 셋 × S_mix 자 둘(±̄/√n 「단위」 · 씨앗 SD — ZIF 는 배치 SD) — 9회차와 같은 틀:
  (가) 비지배 후보군 → 물 지수 → 뽑힌 것 빼고 반복   (나) 쌍별 비교자 승수(S_mix |x| ≥ 1.5 면 S_mix, 아니면 물 지수)   (다) 인접 동률 묶음 → 물
"""
import json, math, os, statistics as st, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import final_crosscheck_e23 as F  # noqa: E402  (S · W 를 원자료에서 만듦)

TH = 1.5


def J(p):
    return json.load(open(os.path.join(HERE, p), encoding="utf-8"))


def smix(p):
    rows = [r for r in J(p)["rows"] if r.get("status") == "ok"]
    assert len(rows) == 3, (p, len(rows))
    s = [r["N_CO2"] / r["N_N2"] * (0.85 / 0.15) for r in rows]
    e = [x * math.hypot(r["N_CO2_err"] / r["N_CO2"], r["N_N2_err"] / r["N_N2"]) for x, r in zip(s, rows)]
    return dict(kind="TPL", n=3, mean=st.mean(s), sd=st.stdev(s), pm=st.mean(e) / math.sqrt(3), seeds=[r["seed"] for r in rows])


def widom_on(p):
    r = [r for r in J(p)["rows"] if r["charges"] == "on"][0]
    return r["KH_CO2"], r["KH_CO2_err"]


def water(p, name, widom):
    rows = [r for r in J(p)["rows"] if name is None or r["name"] == name]
    k = [r["KH_water"] for r in rows]
    e = [r["KH_water_err"] for r in rows]
    m, me = st.mean(k), st.mean(e) / math.sqrt(len(e))
    c, ce = widom_on(widom)
    i = m / c
    return dict(idx=i, err=i * math.hypot(me / m, ce / c), seeds=[r["seed"] for r in rows])


def water_blocked(p):
    s = J(p)["summary"]["block1.30"]
    return dict(idx=s["index"], err=s["index_err"], seeds=s["seeds"])


S, W = dict(F.S), dict(F.W)
NEW = {
    "Cl100": (smix("results_e24d_cl_mix_laptop2.json"),
              water("results_e24d_cl_water_hkhome.json", None, "results_magi5_e3_e24c_cl_100_widom_hkhome.json")),
    "C2H5_100blk": (smix("results_e24e_c2h5_mix_junseok.json"), water_blocked("results_e24e_c2h5_water_junseok.json")),
    "Br100": (smix("results_e24g_e24g_br_100_mix_laptop2.json"),
              water("results_e24g_water_laptop.json", "e24g_br_100", "results_magi5_e3_e24g_br_100_widom_hkhome.json")),
    "Cl050a": (smix("results_e24g_e24h_cl_050a_mix_laptop2.json"),
               water("results_e24g_water_laptop.json", "e24h_cl_050a", "results_magi5_e3_e24h_cl_050a_widom_hkhome.json")),
    "C2H5_050a_blk": (smix("results_e24g_e24h_c2h5_050a_mix_junseok.json"), water_blocked("results_e24g_e24h_c2h5_050a_water_junseok.json")),
}
for k, (s, w) in NEW.items():
    S[k], W[k] = s, w


def su(a, b, ruler):
    """S_mix a − b. ruler 'pm' = ±̄/√n 단위(ZIF 끼리는 배치 SD — 등록 자) · 'sd' = 씨앗(배치) SD."""
    A, B = S[a], S[b]
    d = A["mean"] - B["mean"]
    if A["kind"] == "ZIF" or B["kind"] == "ZIF":
        bu, _ = F.cmp(a, b) if (a in F.S and b in F.S) else (None, None)
        if bu is None:  # 새 형판 대 ZIF: 분모 = ZIF 배치 SD(RULER §7 "앙상블 대 모체")
            z = A if A["kind"] == "ZIF" else B
            bu = d / z["sd"]
        return bu
    if ruler == "pm":
        return d / math.hypot(A["pm"], B["pm"])
    return d / math.hypot(A["sd"], B["sd"])


def wu(a, b):
    A, B = W[a], W[b]
    return (A["idx"] - B["idx"]) / math.hypot(A["err"], B["err"])


def interp_ga(names, ruler):
    """(가) 비지배 후보군(누구에게도 1.5 넘게 지지 않음) → 물 지수 최저가 1위 → 빼고 반복."""
    left, out = list(names), []
    while left:
        cand = [g for g in left if all(su(g, h, ruler) > -TH for h in left if h != g)]
        best = min(cand, key=lambda g: W[g]["idx"])
        out.append((best, sorted(cand, key=lambda g: W[g]["idx"])))
        left.remove(best)
    return out


def beats(a, b, ruler):
    x = su(a, b, ruler)
    if abs(x) >= TH:
        return x > 0
    y = wu(a, b)
    if abs(y) >= TH:
        return y < 0
    return None  # 공동


def interp_na(names, ruler):
    """(나) 쌍별 비교자 승수 + 순환 검사."""
    wins = {g: sum(1 for h in names if h != g and beats(g, h, ruler)) for g in names}
    cyc = [(a, b, c) for a in names for b in names for c in names
           if len({a, b, c}) == 3 and beats(a, b, ruler) and beats(b, c, ruler) and beats(c, a, ruler)]
    return sorted(names, key=lambda g: -wins[g]), wins, cyc


def interp_da(names, ruler):
    """(다) S_mix 내림차순 인접 동률 묶음(묶음 전원과 동률일 때만 합류) → 안은 물 지수."""
    order = sorted(names, key=lambda g: -S[g]["mean"])
    blocks, cur = [], [order[0]]
    for g in order[1:]:
        if all(abs(su(h, g, ruler)) < TH for h in cur):
            cur.append(g)
        else:
            blocks.append(cur); cur = [g]
    blocks.append(cur)
    return [sorted(b, key=lambda g: W[g]["idx"]) for b in blocks]


def main():
    names = list(S.keys())
    seeds = [x for k in NEW for x in NEW[k][0]["seeds"] + NEW[k][1]["seeds"]]
    print(f"# E-23 확장 2 검산 — 원자료만 · 새 형판 {len(NEW)} · 씨앗 {len(seeds)}개 겹침 {len(seeds) - len(set(seeds))}")
    print("\n| 물질 | S_mix | ±̄/√n | SD | 물 지수 ± |")
    print("|---|---|---|---|---|")
    for g in sorted(names, key=lambda g: -S[g]["mean"]):
        print(f"| {g} | {S[g]['mean']:.2f} | {S[g]['pm']:.2f} | {S[g]['sd']:.2f} | {W[g]['idx']:.5g} ± {W[g]['err']:.2g} |")
    top = ["Br100", "C2H5_100blk", "Cl100", "tpl_CH3", "tpl_CN"]
    print("\n## 선두 짝 (S_mix 단위 · 씨앗 SD 자 | 물 지수 단위)")
    for i, a in enumerate(top):
        for b in top[i + 1:]:
            print(f"  {a:12s} − {b:12s}: {su(a, b, 'pm'):+.2f} · {su(a, b, 'sd'):+.2f} | 물 {wu(a, b):+.2f}")
    res = {}
    for ruler in ("pm", "sd"):
        lab = "±̄/√n 단위" if ruler == "pm" else "씨앗 SD 자"
        ga = [b for b, _ in interp_ga(names, ruler)]
        na, wins, cyc = interp_na(names, ruler)
        da = [g for blk in interp_da(names, ruler) for g in blk]
        res[ruler] = (ga, na, da)
        print(f"\n## 자: {lab}")
        print("  (가) 비지배 → 물:", " > ".join(ga[:6]), "…")
        print("      1위 후보군:", interp_ga(names, ruler)[0][1])
        print("  (나) 쌍별 승수  :", " > ".join(f"{g}({wins[g]})" for g in na[:6]), "…", "· 순환", len(cyc))
        print("  (다) 인접 묶음  :", " | ".join("[" + " ".join(b) + "]" for b in interp_da(names, ruler)[:5]), "…")
    firsts = {v[i][0] for v in res.values() for i in range(3)}
    top3 = {tuple(v[i][:3]) for v in res.values() for i in range(3)}
    print(f"\n## 결론: 1위 {firsts} · 상위 셋 {top3}")


if __name__ == "__main__":
    main()
