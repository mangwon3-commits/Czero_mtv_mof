# -*- coding: utf-8 -*-
"""E-15b ① 대조 — 새 실행(ON·OFF) 대 옛 값(E-15 행: S_ON = annotated · S_OFF = E-15 OFF). 1.5 단위 = |Δ| / max(±새, ±옛)."""
import glob
import json
import math
import re

D = '/home/mangwon/mof_project/21_ZIF69_MTV/'
new = {r['charges']: r for r in json.load(open(D + 'results_magi5_e3_e15b_cdhcb_widom_junseok.json', encoding='utf-8'))['rows']}
old = [r for r in json.load(open(D + 'results_magi5_e15_offwidom_junseok.json', encoding='utf-8'))['rows'] if r['name'] == '2017_Cd__hcb_2_ASR_1'][0]
on, off = new['on'], new['off']
S_on, e_on = on['selectivity'], on['selectivity_err']
S_off, e_off = off['selectivity'], off['selectivity_err']
G = S_on / S_off
eG = G * math.hypot(e_on / S_on, e_off / S_off)
G_old = old['S_ON'] / old['S_OFF']
eG_old = G_old * math.hypot(old['S_ON_err'] / old['S_ON'], old['S_OFF_err'] / old['S_OFF'])


def units(a, ea, b, eb):
    return abs(a - b) / max(ea, eb)


print(f"S_ON  새 {S_on:.1f} ± {e_on:.1f} · 옛 {old['S_ON']:.1f} ± {old['S_ON_err']:.1f} → {units(S_on, e_on, old['S_ON'], old['S_ON_err']):.2f} 단위")
print(f"S_OFF 새 {S_off:.2f} ± {e_off:.2f} · 옛(E-15) {old['S_OFF']:.2f} ± {old['S_OFF_err']:.2f} → {units(S_off, e_off, old['S_OFF'], old['S_OFF_err']):.2f} 단위")
print(f"G     새 {G:.2f} ± {eG:.2f} · 옛 {G_old:.2f} ± {eG_old:.2f} → {units(G, eG, G_old, eG_old):.2f} 단위")
ref = old['on_ref']
print(f"K_H(CO2) ON 새 {on['KH_CO2']:.4e} ± {on['KH_CO2_err']:.2e} · 옛 {ref['KH_CO2']:.4e} ± {ref['KH_CO2_err']:.2e} → "
      f"{units(on['KH_CO2'], on['KH_CO2_err'], ref['KH_CO2'], ref['KH_CO2_err']):.2f} 단위 · 상대 ± 새 {on['KH_CO2_err'] / on['KH_CO2'] * 100:.1f} %")
print(f"K_H(N2)  ON 새 {on['KH_N2']:.4e} ± {on['KH_N2_err']:.2e} · 옛 {ref['KH_N2']:.4e} ± {ref['KH_N2_err']:.2e} → "
      f"{units(on['KH_N2'], on['KH_N2_err'], ref['KH_N2'], ref['KH_N2_err']):.2f} 단위")
print(f"dU_CO2 ON 새 {on['dU_CO2']:.2f} · 옛 {ref.get('dU_CO2')} · OFF {off['dU_CO2']:.2f} · Q_st 보정 ON {on.get('Qst_CO2_rt_corrected'):.2f}")
seeds, fin = [], 0
for f in sorted(glob.glob(D + 'magi5_runs_e15b_cdhcb/widom_*/Output/System_0/*.data')):
    t = open(f, encoding='utf-8', errors='ignore').read()
    seeds.append(int(re.search(r'Random number seed:\s*(\d+)', t).group(1)))
    fin += 'Simulation finished' in t
old_seeds = [old.get('seed_CO2'), old.get('seed_N2')]
print(f"표지 {fin}/{len(seeds)} · 새 씨앗 {seeds} · 옛 OFF 씨앗 {old_seeds} · 겹침 {len(set(seeds) & set(s for s in old_seeds if s))}")
