"""MAGI-007 R3 (Caspar · HKHOME) 근거 — A-2 · A-7 에 답하려고 master 원자료만 읽음(쓰기 없음).
작동점 적재를 세 조건(건조 298 K · 건조 323 K · 습윤 298 K)에서 모체 대비로 놓고,
"N₂ 자리 감소(입체)" 와 "CO₂ 경쟁" 이 서로 다르게 예측하는 것을 본다:
  입체 → 모체 대비 N_N₂ 결손이 온도 · 물에 거의 무관(자리 수가 줄었으므로).
  경쟁 → CO₂ 적재가 포화에서 멀어지는 323 K 에서 N_N₂ 결손이 줄어든다.
E · B 결과를 쓴다 — R1 예측을 고치는 데 쓰지 않고 A-2 · A-7 답에만 인용([E · B 결과 인용]).
실행: python3 r3_competition.py  (21_ZIF69_MTV 에서) → r3_competition.json"""
import json, math, os, statistics as st
os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))

def rows(f): return json.load(open(f))["rows"]
def pick(rs, pre): return [r for r in rs if r.get("name", "").startswith(pre)]
def mean(xs): return sum(xs) / len(xs)
def sem(xs): return st.stdev(xs) / math.sqrt(len(xs)) if len(xs) > 1 else float("nan")

DRY298 = {
    "e22_parent": [("results_e23_mix_desktop.json", "e22_parent_s")],
    "cn": [("results_e24i_e24i_cn_open_mix_hkhome.json", "e24i_cn_open_s"), ("results_e24i_e24i_cn_open_mix_s456_hkhome.json", "e24i_cn_open_s")],
    "br": [("results_e24i_e24i_br_open_mix_laptop2.json", "e24i_br_open_s"), ("results_e24i_e24i_br_open_mix_s456_hkhome.json", "e24i_br_open_s")],
    "cl": [("results_e24i_e24i_cl_open_mix_junseok.json", "e24i_cl_open_s")],
    "ch3": [("results_e24i_e24i_ch3_open_mix_laptop2.json", "e24i_ch3_open_s")],
}
DRY323 = {"e22_parent": ("results_e27_mix323_laptop.json", "e22_parent_s"),
          "cn": ("results_znbdt_b_mix323_hkhome.json", "e24i_cn_open_s"),
          "br": ("results_znbdt_b_mix323_hkhome.json", "e24i_br_open_s")}
HUMID = ("results_znbdt_e_humid3_laptop2.json", {"e22_parent": "e22_parent_e3r", "cn": "e24i_cn_open_e3r", "br": "e24i_br_open_e3r",
                                                  "cl": "e24i_cl_open_e3r", "ch3": "e24i_ch3_open_e3r"})
P_N2_DRY, P_N2_HUM = 85.0, 82.1479   # kPa — run_tj1_mix 계열 건조 15/85 대 등록 E 15/82.1479/2.8521

def agg(rs, skey):
    ok = [r for r in rs if r.get("status", "ok") == "ok" and r.get("ok", True)]
    return {"n": len(ok), "S": mean([r[skey] for r in ok]), "S_sem": sem([r[skey] for r in ok]),
            "N_CO2": mean([r["N_CO2"] for r in ok]), "N_N2": mean([r["N_N2"] for r in ok]),
            **({"N_H2O": mean([r["N_H2O"] for r in ok])} if "N_H2O" in ok[0] else {}),
            "seeds_unique": len({r["seed"] for r in ok}) == len(ok)}

out = {"dry298": {}, "dry323": {}, "humid298": {}}
for m, srcs in DRY298.items():
    rs = sum((pick(rows(f), p) for f, p in srcs), [])
    out["dry298"][m] = agg(rs, "S_mix") | {"src": [f for f, _ in srcs]}
for m, (f, p) in DRY323.items():
    out["dry323"][m] = agg(pick(rows(f), p), "S_mix") | {"src": f}
for m, p in HUMID[1].items():
    out["humid298"][m] = agg(pick(rows(HUMID[0]), p), "S_humid") | {"src": HUMID[0]}

def rel(cond, m, k):
    a, b = out[cond][m][k], out[cond]["e22_parent"][k]
    return 100.0 * (a / b - 1.0)

tab = {}
for m in ("cn", "br", "cl", "ch3"):
    t = {"dN2_vs_parent_298_%": rel("dry298", m, "N_N2"), "dCO2_vs_parent_298_%": rel("dry298", m, "N_CO2"),
         "dN2_vs_parent_humid_%": rel("humid298", m, "N_N2"), "dCO2_vs_parent_humid_%": rel("humid298", m, "N_CO2")}
    if m in out["dry323"]:
        t |= {"dN2_vs_parent_323_%": rel("dry323", m, "N_N2"), "dCO2_vs_parent_323_%": rel("dry323", m, "N_CO2"),
              "S323_over_S298": out["dry323"][m]["S"] / out["dry298"][m]["S"],
              "N_N2_323_over_298": out["dry323"][m]["N_N2"] / out["dry298"][m]["N_N2"],
              "N_CO2_323_over_298": out["dry323"][m]["N_CO2"] / out["dry298"][m]["N_CO2"]}
    tab[m] = t
pp = out["dry323"]["e22_parent"], out["dry298"]["e22_parent"]
tab["e22_parent"] = {"S323_over_S298": pp[0]["S"] / pp[1]["S"], "N_N2_323_over_298": pp[0]["N_N2"] / pp[1]["N_N2"],
                     "N_CO2_323_over_298": pp[0]["N_CO2"] / pp[1]["N_CO2"]}
ret = {}
for m in HUMID[1]:
    h, d = out["humid298"][m], out["dry298"][m]
    ret[m] = {"retention": h["S"] / d["S"], "N_CO2_humid_over_dry": h["N_CO2"] / d["N_CO2"],
              "N_N2_humid_over_dry": h["N_N2"] / d["N_N2"], "N_N2_expected_by_pN2": P_N2_HUM / P_N2_DRY,
              "N_H2O": h.get("N_H2O")}
out["relative"], out["retention_E"] = tab, ret

json.dump(out, open("MAGI/MAGI-007_R3_hkhome_evidence/r3_competition.json", "w"), ensure_ascii=False, indent=1)
for c in ("dry298", "dry323", "humid298"):
    print(f"== {c}")
    for m, v in out[c].items():
        print(f"  {m:10s} n={v['n']} S={v['S']:7.2f} ±sem {v['S_sem']:.2f}  N_CO2={v['N_CO2']:.3f}  N_N2={v['N_N2']:.4f}"
              + (f"  N_H2O={v['N_H2O']:.4f}" if "N_H2O" in v else "") + f"  seeds_unique={v['seeds_unique']}")
print("== 모체 대비 %");  [print(" ", m, {k: round(x, 3) for k, x in t.items()}) for m, t in tab.items()]
print("== E 유지비");     [print(" ", m, {k: (round(x, 4) if isinstance(x, float) else x) for k, x in t.items()}) for m, t in ret.items()]
