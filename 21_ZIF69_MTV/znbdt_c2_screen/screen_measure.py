import sys, os, json, collections, numpy as np
sys.path.insert(0, os.getcwd())
from ase.io import read
from ase.neighborlist import neighbor_list
from ase.data import covalent_radii
from ase.geometry import find_mic
import clash_gate
clash_gate.BONDI.setdefault('I', 1.98)  # Bondi 1964 — 원본 표에 없음(선별 한정)
S = sys.argv[1]
JOBS = {'I (screen)': (f'{S}/E24i_ZnDia_I_open.cif', f'{S}/relax/i_open_relaxed.cif'),
        'F (screen)': (f'{S}/E24i_ZnDia_F_open.cif', f'{S}/relax/f_open_relaxed.cif'),
        'CN (E-24i)': ('e24i_candidates/E24i_ZnDia_CN_open.cif', 'relax_tnf/e24i_cn_open_relaxed.cif'),
        'Br (E-24i)': ('e24i_candidates/E24i_ZnDia_Br_open.cif', 'relax_tnf/e24i_br_open_relaxed.cif'),
        'Cl (E-24i)': ('e24i_candidates/E24i_ZnDia_Cl_open.cif', 'relax_tnf/e24i_cl_open_relaxed.cif'),
        'CCH (C1)': ('znbdt_c1_candidates/E24i_ZnDia_CCH_open.cif', 'relax_tnf/e24i_cch_open_relaxed.cif')}
HET_H = ('H···O', 'H···N', 'F···H', 'Cl···H', 'H···S', 'Br···H', 'H···I')
def contacts(a):
    cuts = [covalent_radii[z] * 1.15 if a[k].symbol != 'Zn' else 1.45 for k, z in enumerate(a.numbers)]
    i, j = neighbor_list('ij', a, cuts); G = collections.defaultdict(set)
    for x, y in zip(i, j): G[x].add(y)
    ii, jj, dd = neighbor_list('ijd', a, 3.6); s = a.get_chemical_symbols(); best = {}
    for x, y, d in zip(ii, jj, dd):
        if x >= y or 'Zn' in (s[x], s[y]): continue
        if y in ({x} | G[x] | {w for v in G[x] for w in G[v]}): continue
        p = '···'.join(sorted((s[x], s[y])))
        if p not in best or d < best[p]: best[p] = round(float(d), 3)
    return best
par = read('e22_candidates/E22_ZnDia_parent.cif'); P = par.get_positions(); out = {}
for tag, (c0, c1) in JOBS.items():
    a0, a1 = read(c0), read(c1); X0 = a0.get_positions(); P1 = a1.get_positions(); dmax = 0
    for k in range(len(a0)):
        _, dl = find_mic(P - X0[k], a0.cell, pbc=True); j = int(np.argmin(dl))
        if dl[j] < 0.3 and par[j].symbol == a0[k].symbol:
            _, d1 = find_mic(P1 - X0[k], a0.cell, pbc=True)
            dmax = max(dmax, min(d1[m] for m in range(len(a1)) if a1[m].symbol == a0[k].symbol))
    c = contacts(a1); hh = min([v for p, v in c.items() if p in HET_H] or [9.9])
    g = clash_gate.check(c1)
    out[tag] = dict(het_H=hh, disp=round(float(dmax), 3), gate0a=hh >= 1.8 and dmax <= 1.0, margin=g['min_margin_A'], worst=g['worst_pair'], gate0b=g['pass_0b'],
                    subst=[f'{p} {v}' for p, v in c.items() if any(e in p for e in ('I', 'F', 'Br', 'Cl', 'N'))][:6])
    o = out[tag]
    print(f"{tag:11s} 이종–H {o['het_H']:.3f}  변위 {o['disp']:.2f} | (0a) {'통과' if o['gate0a'] else '탈락'} | (0b) 겹침 {o['margin']:+.3f} {o['worst']} {'통과' if o['gate0b'] else '탈락'}")
json.dump(out, open(f'{S}/screen_gates.json', 'w'), ensure_ascii=False, indent=1, default=str)
