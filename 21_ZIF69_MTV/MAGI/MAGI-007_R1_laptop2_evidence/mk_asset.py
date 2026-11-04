import json, os
E = os.path.expanduser("~/.mof_magi/MAGI-007_laptop2_evidence/evidence.json")
O = os.path.expanduser("~/.mof_magi/MAGI-007_obsidian/R1")
os.makedirs(os.path.join(O, "assets"), exist_ok=True)
e = json.load(open(E, encoding="utf-8"))
p = e["parent_298"][0]
pc = sum(p[6]) / 3
pn = sum(p[7]) / 3
hdr = ("material,S_mix_298_mean,pm,n,N_CO2,N_N2,CO2_vs_parent_pct,N2_vs_parent_pct,"
       "humid_ads_water_mol_per_kg,humid_CO2_over_dry,relax300_n_channels_1.65,relax300_pockets,relax300_PLD_after")
rows = [hdr, "parent,75.43,2.14,3,%.4f,%.4f,0,0,%.4f,,,," % (pc, pn, e["humid_binary_ads"]["parent"]["water_ads_mean"])]
for k, tag in (("cn", "e24i_cn_open"), ("br", "e24i_br_open"), ("cl", "e24i_cl_open"), ("ch3", "e24i_ch3_open"), ("c2h5", "e24i_c2h5_open")):
    s = e["smix_298_open"][k]
    h = e["humid_binary_ads"][k]
    r = e["relax300"][tag]
    rows.append("%s,%.2f,%.2f,%d,%.4f,%.4f,%.1f,%.1f,%.4f,%.3f,%s,%s,%s" % (
        k, s["S_mix_mean"], s["pm"], s["n"], s["N_CO2_mean"], s["N_N2_mean"],
        100 * (s["N_CO2_mean"] / pc - 1), 100 * (s["N_N2_mean"] / pn - 1),
        h["water_ads_mean"], h["CO2_humid_binary_over_dry_mix"],
        r["chan_after"]["n_channels"], r["chan_after"]["pockets_stdout"], r["PLD_after"]))
open(os.path.join(O, "assets", "b1_b3_evidence_table.csv"), "w", encoding="utf-8").write("\n".join(rows) + "\n")
print("\n".join(rows))
