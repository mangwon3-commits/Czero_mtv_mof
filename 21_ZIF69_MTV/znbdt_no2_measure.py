# -*- coding: utf-8 -*-
"""ZNBDT-C2 후속 #3 (HKHOME 몫) — 열린 자리 4,8-(NO₂)₂ 이완본의 관문 (0a)(0b). 명령 `ASSIGN_ZNBDT_C2_FOLLOWUP_20261105.md` §3(03:0x 기기 변경).
측정은 `znbdt_c2_screen/screen_measure.py` 와 같은 코드(contacts · 골격 변위 · clash_gate.check) + 자리별(니트로 넷 각각: 최근접 접촉 · Bondi 겹침 최댓값을\n관문 범위와 clash_gate 제외 ②범위(부착 C 에서 2결합 안 — 티오펜 S 포함)로 나눠 적음; 제외 범위 값은 관문 밖 서술).
문턱: (0a) 이종–H ≥ 1.8 Å · 골격 최대 변위 ≤ 1.0 Å / (0b) 겹침 < 0.4 Å. 판정 아님 — 가능성 표(명령 §3 뜻).
실행: czeromof 파이썬 — `python znbdt_no2_measure.py` (21_ZIF69_MTV 에서) → results_znbdt_no2_screen_hkhome.json"""
import collections, json, numpy as np
from ase.io import read
from ase.neighborlist import neighbor_list
from ase.data import covalent_radii
from ase.geometry import find_mic
import clash_gate
B0, B1 = 'znbdt_no2_screen/E24i_ZnDia_NO2_open.cif', 'relax_tnf/e24i_no2_open_relaxed.cif'
HET_H = ('H···O', 'H···N', 'F···H', 'Cl···H', 'H···S', 'Br···H')


def graph(a):
    cuts = [covalent_radii[z] * 1.15 if a[k].symbol != 'Zn' else 1.45 for k, z in enumerate(a.numbers)]
    i, j = neighbor_list('ij', a, cuts); G = collections.defaultdict(set)
    for x, y in zip(i, j): G[x].add(y)
    return G


def contacts(a, G):
    ii, jj, dd = neighbor_list('ijd', a, 3.6); s = a.get_chemical_symbols(); best = {}
    for x, y, d in zip(ii, jj, dd):
        if x >= y or 'Zn' in (s[x], s[y]): continue
        if y in ({x} | G[x] | {w for v in G[x] for w in G[v]}): continue
        p = '···'.join(sorted((s[x], s[y])))
        if p not in best or d < best[p][0]: best[p] = (round(float(d), 3), f'{s[x]}{x}', f'{s[y]}{y}')
    return best


a0, a1 = read(B0), read(B1); assert len(a0) == len(a1)
par = read('e22_candidates/E22_ZnDia_parent.cif'); P = par.get_positions(); X0 = a0.get_positions(); P1 = a1.get_positions(); dmax, nfw = 0.0, 0
for k in range(len(a0)):
    _, dl = find_mic(P - X0[k], a0.cell, pbc=True); j = int(np.argmin(dl))
    if dl[j] < 0.3 and par[j].symbol == a0[k].symbol:
        nfw += 1; _, d1 = find_mic(P1 - X0[k], a0.cell, pbc=True)
        dmax = max(dmax, min(d1[m] for m in range(len(a1)) if a1[m].symbol == a0[k].symbol))
G = graph(a1); s = a1.get_chemical_symbols(); c = contacts(a1, G)
het = [(v[0], p, v[1], v[2]) for p, v in c.items() if p in HET_H]; hh = min(het)
g = clash_gate.check(B1)
# 자리별: 니트로 N(O 둘 + C 하나)
sites = []
nitro = [n for n in range(len(a1)) if s[n] == 'N' and sorted(s[x] for x in G[n]) == ['C', 'O', 'O']]
for n in nitro:
    grp = {n} | {x for x in G[n] if s[x] == 'O'}
    near = set(grp) | {y for x in grp for y in G[x]} | {w for x in grp for y in G[x] for w in G[y]}
    ring_c = [x for x in G[n] if s[x] == 'C'][0]
    excl = {ring_c} | G[ring_c] | {w for v in G[ring_c] for w in G[v]}   # clash_gate 제외 ②와 같은 범위(부착 C 에서 2결합 안)
    ii, jj, dd = neighbor_list('ijd', a1, 3.6); best = (9.9, None); w_in = (-9.9, None); w_ex = (-9.9, None)
    for x, y, d in zip(ii, jj, dd):
        if x in grp and y not in near and s[y] != 'Zn':
            if d < best[0]: best = (round(float(d), 3), f'{s[x]}{x}···{s[y]}{y}')
            if s[y] == 'H': continue
            m = clash_gate.BONDI[s[x]] + clash_gate.BONDI[s[y]] - d
            tgt = (round(float(m), 3), f'{s[x]}{x}···{s[y]}{y} {d:.3f}')
            if y in excl:
                if m > w_ex[0]: w_ex = tgt
            elif m > w_in[0]: w_in = tgt
    sites.append({'N': int(n), 'ipso_C': int(ring_c), 'closest_contact_any': best,
                  'max_overlap_gate_scope': w_in, 'max_overlap_excluded_scope(부착 C 2결합 안 · 관문 밖 · 서술)': w_ex})
out = {'test': 'ZNBDT-C2 후속 #3 — 열린 자리 4,8-(NO₂)₂ 관문 (0a)(0b) (HKHOME 이완 · 측정)', 'assign': 'ASSIGN_ZNBDT_C2_FOLLOWUP_20261105.md §3',
       'build': B0, 'relaxed': B1, 'relax_record': 'results_znbdt_no2_relax_hkhome.json', 'n_framework_matched': nfw,
       'max_framework_disp_A': round(float(dmax), 3), 'min_heteroatom_H': hh, 'gate0a_pass': hh[0] >= 1.8 and dmax <= 1.0,
       'gate0b': g, 'gate0b_pass': g['pass_0b'], 'gate_all_pass': hh[0] >= 1.8 and dmax <= 1.0 and g['pass_0b'],
       'sites': sites, 'contacts_after': c, 'note': '판정 아님 — 가능성 표. 전하 · Widom · GCMC 는 하지 않음(명령 §3).'}
print(f"골격 변위 {dmax:.2f} Å (짝 {nfw}) | 이종–H 최소 {hh[0]} {hh[1]} | (0a) {'통과' if out['gate0a_pass'] else '탈락'} | "
      f"(0b) 겹침 {g['min_margin_A']:+.3f} {g['worst_pair']} {'통과' if g['pass_0b'] else '탈락'}")
for t in sites: print(f"  자리 N{t['N']}: 최근접 {t['closest_contact_any']} · 관문 범위 최대 겹침 {t['max_overlap_gate_scope']} · 제외 범위 {t['max_overlap_excluded_scope(부착 C 2결합 안 · 관문 밖 · 서술)']}")
json.dump(out, open('results_znbdt_no2_screen_hkhome.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1, default=str)
