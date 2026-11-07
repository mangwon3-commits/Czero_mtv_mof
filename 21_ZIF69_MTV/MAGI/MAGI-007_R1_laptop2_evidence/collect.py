# -*- coding: utf-8 -*-
"""MAGI-007 R1 (Balthasar, laptop2) 근거 수집 — 저장소 HEAD f589c08b 의 원자료 JSON 만 git show 로 읽어 다시 계산. 저장소 무수정 · 계산(RASPA 등) 0.
출력: evidence.json (같은 폴더). E · A · B 결과는 읽지 않음(규율 1)."""
import json, math, os, statistics as st, subprocess, glob
REPO = os.path.expanduser("~/mof_project"); H = "f589c08b"; D = "21_ZIF69_MTV/"
def show(p):
    return json.loads(subprocess.run(["git", "show", f"{H}:{p}"], cwd=REPO, capture_output=True, text=True, check=True).stdout)
def ls(prefix):
    return subprocess.run(["git", "ls-tree", "--name-only", H, prefix], cwd=REPO, capture_output=True, text=True).stdout.split()
def md5(p):
    import hashlib
    return hashlib.md5(subprocess.run(["git", "show", f"{H}:{p}"], cwd=REPO, capture_output=True, check=True).stdout).hexdigest()
out = {"head": H, "sources": {}, "smix_298_open": {}, "humid_binary_ads": {}, "relax300": {}, "mix323_parent": {}, "parent_298": {}}
MIX = {"cn": ["results_e24i_e24i_cn_open_mix_hkhome.json", "results_e24i_e24i_cn_open_mix_s456_hkhome.json"],
       "br": ["results_e24i_e24i_br_open_mix_laptop2.json", "results_e24i_e24i_br_open_mix_s456_hkhome.json"],
       "cl": ["results_e24i_e24i_cl_open_mix_junseok.json"], "ch3": ["results_e24i_e24i_ch3_open_mix_laptop2.json"],
       "c2h5": ["results_e24i_e24i_c2h5_open_mix_junseok.json"]}
for k, fs in MIX.items():
    rows, mach = [], []
    for f in fs:
        d = show(D + f); out["sources"][D + f] = md5(D + f)
        for r in d["rows"]:
            if r.get("status") == "ok" and r.get("returncode") == 0:
                rows.append(r); mach.append((d.get("machine") or r.get("machine"), r.get("minutes")))
    v = [r["S_mix"] for r in rows]; e = [r["S_mix_err"] for r in rows]
    n2rel = [r["N_N2_err"] / r["N_N2"] for r in rows]
    out["smix_298_open"][k] = {"n": len(v), "S_mix_mean": st.mean(v), "pm": st.mean(e) / math.sqrt(len(e)), "SD": st.stdev(v),
        "N_CO2_mean": st.mean(r["N_CO2"] for r in rows), "N_N2_mean": st.mean(r["N_N2"] for r in rows),
        "N2_rel_pm_each": n2rel, "S_rel_pm_each": [a / b for a, b in zip(e, v)], "minutes_by_machine": mach,
        "seeds_unique": len({r["seed"] for r in rows}) == len(rows)}
HUM = {"cn": "humid_working_capacity_w2_e24i_cn_open_junseok.json", "br": "humid_working_capacity_w2_e24i_br_open_hkhome.json",
       "cl": "humid_working_capacity_w2_e24i_cl_open_laptop2.json", "ch3": "humid_working_capacity_w2_e24i_ch3_open_laptop.json",
       "c2h5": "humid_working_capacity_w2_e24i_c2h5_open_junseok.json", "parent": "humid_working_capacity_w2_e22parent_laptop.json"}
for k, f in HUM.items():
    p = D + "v3w_humid_wc/" + f; d = show(p); out["sources"][p] = md5(p)
    a = [r["loadings"]["ads"] for r in d["rows"] if r.get("loadings", {}).get("ads")]
    co2 = [x["CO2"]["mol_per_kg"] for x in a]; w = [x["water"]["mol_per_kg"] for x in a if x.get("water")]
    m = {"n": len(co2), "CO2_ads_mean": st.mean(co2), "water_ads_mean": st.mean(w) if w else None,
         "water_over_CO2": (st.mean(w) / st.mean(co2)) if w else None}
    if k in out["smix_298_open"]:
        m["CO2_humid_binary_over_dry_mix"] = st.mean(co2) / out["smix_298_open"][k]["N_CO2_mean"]
    out["humid_binary_ads"][k] = m
p = D + "results_e24i_relax300_laptop.json"; d = show(p); out["sources"][p] = md5(p)
for nm, r in (d["rows"].items() if isinstance(d["rows"], dict) else [(x.get("name") or x.get("tag"), x) for x in d["rows"]]):
    b, a = r.get("before") or {}, r.get("after") or {}
    out["relax300"][str(nm)] = {"status": r.get("status"), "PLD_before": b.get("PLD"), "PLD_after": a.get("PLD"), "LCD_before": b.get("LCD"), "LCD_after": a.get("LCD"),
        "outer_loops": r.get("outer_loops"), "final_EDiff": r.get("final_EDiff"), "minutes": r.get("minutes"),
        "chan_after": {kk: (r.get("chan_after") or {}).get(kk) for kk in ("n_channels", "pockets_stdout")} if r.get("chan_after") else None}
out["relax300_elapsed_min"] = d.get("elapsed_min")
p = D + "results_e27_mix323_laptop.json"; d = show(p); out["sources"][p] = md5(p)
pr = [r for r in d["rows"] if str(r.get("name", "")).startswith("e22_parent") and r.get("status") == "ok"]
out["mix323_parent"] = {"T_K": d.get("protocol", {}).get("T_K"), "S_mix_each": [r["S_mix"] for r in pr], "S_mix_err_each": [r["S_mix_err"] for r in pr],
    "mean": st.mean(r["S_mix"] for r in pr), "pm": st.mean(r["S_mix_err"] for r in pr) / math.sqrt(len(pr)), "minutes": [r.get("minutes") for r in pr],
    "N2_rel_pm_each": [r["N_N2_err"] / r["N_N2"] for r in pr]}
# 모체 298 K S_mix 원자료 찾기 — results_*mix*.json 중 e22_parent 행, 298 K
cand = []
for f in ls(D):
    b = os.path.basename(f)
    if b.startswith("results_") and "mix" in b and b.endswith(".json") and "323" not in b:
        try:
            d = show(f)
        except Exception:
            continue
        if not isinstance(d, dict) or not isinstance(d.get("rows"), list):
            continue
        pt = d.get("protocol"); T = pt.get("T_K") if isinstance(pt, dict) else None
        pr = [r for r in d["rows"] if isinstance(r, dict) and str(r.get("name", "")).startswith("e22_parent") and r.get("status") == "ok" and "S_mix" in r]
        if pr and (T in (None, 298, 298.0)):
            cand.append((f, T, [round(r["S_mix"], 2) for r in pr], [round(r["S_mix_err"], 2) for r in pr], [r.get("minutes") for r in pr], md5(f), [r.get("N_CO2") for r in pr], [r.get("N_N2") for r in pr], [r.get("N_N2_err") for r in pr], [r.get("seed") for r in pr], [r.get("returncode") for r in pr]))
out["parent_298"] = cand
json.dump(out, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "evidence.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1, default=str)
for k, v in out["smix_298_open"].items():
    print(f"S_mix {k:5s} n {v['n']} {v['S_mix_mean']:.2f} ± {v['pm']:.2f} SD {v['SD']:.2f} · N_CO2 {v['N_CO2_mean']:.3f} · N_N2 {v['N_N2_mean']:.4f} · N2 rel± {min(v['N2_rel_pm_each']):.3f}~{max(v['N2_rel_pm_each']):.3f} · S rel± {max(v['S_rel_pm_each']):.3f} · min {v['minutes_by_machine']}")
for k, v in out["humid_binary_ads"].items():
    print(f"humid ads {k:6s} CO2 {v['CO2_ads_mean']:.3f} · water {v['water_ads_mean']} · w/CO2 {v['water_over_CO2']} · humid/dry CO2 {v.get('CO2_humid_binary_over_dry_mix')}")
for k, v in out["relax300"].items():
    print("relax300", k, v)
print("relax300 elapsed", out["relax300_elapsed_min"])
print("323 parent", out["mix323_parent"])
for c in out["parent_298"]:
    print("parent298", c)
