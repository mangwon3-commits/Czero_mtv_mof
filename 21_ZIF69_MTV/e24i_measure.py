"""E-24i 들어가는가 관문(0a)(등록 §HKHOME 22차) — `e24g_measure.py` 사본(대상 · 경로 · 출력만) + 관문(0b) `clash_gate.check` 를 같은 행에 붙임. 그 원문: E-24g · E-24h 들어가는가 관문(등록 §HKHOME 21차 (0)) — `e24c_measure.py` 사본(대상 · 경로 · 출력 · Br···H 만 바꿈). 그 원문: E-24c 들어가는가 관문(등록 §HKHOME 16차 (0)) — `e24_measure.py` 사본(그 파일은 import 하면 E-24 결과를 다시 써서 복사함), 대상 · 경로 · 출력만 바꿈.
E-24 원문: — E-22a 와 같은 양: ① 비결합 최소 접촉(위상거리 ≥ 3, 이종 원자–H 포함) ② 치환기 아닌 골격 원자 최대 변위(같은 원소 최근접 짝, 순서 무관).
Zeo++ 는 RASPA(E-23)가 도는 동안 안 씀(CLAUDE.md §5) — PLD/LCD 는 뒤에."""
import json, collections, numpy as np
from ase.io import read
from ase.neighborlist import neighbor_list
from ase.data import covalent_radii
from ase.geometry import find_mic
import clash_gate
TAGS = {'e24i_ch3_open': 'E24i_ZnDia_CH3_open', 'e24i_cl_open': 'E24i_ZnDia_Cl_open', 'e24i_br_open': 'E24i_ZnDia_Br_open', 'e24i_c2h5_open': 'E24i_ZnDia_C2H5_open', 'e24i_cn_open': 'E24i_ZnDia_CN_open'}
HEAVY_H_EXTRA = ('Cl···H', 'H···S', 'Br···H')
HEAVY_H = ('H···O', 'H···N', 'F···H')


def contacts(a):
    cuts = [covalent_radii[z] * 1.15 if a[k].symbol != 'Zn' else 1.45 for k, z in enumerate(a.numbers)]
    i, j = neighbor_list('ij', a, cuts); G = collections.defaultdict(set)
    for x, y in zip(i, j): G[x].add(y)
    ii, jj, dd = neighbor_list('ijd', a, 3.2); s = a.get_chemical_symbols(); best = {}
    for x, y, d in zip(ii, jj, dd):
        if x >= y or 'Zn' in (s[x], s[y]): continue
        near = {x} | G[x] | {w for v in G[x] for w in G[v]}
        if y in near: continue
        pair = '···'.join(sorted((s[x], s[y])))
        if pair not in best or d < best[pair][0]: best[pair] = (round(float(d), 3), s[x] + str(x), s[y] + str(y))
    return best


res = {}
par = read('e22_candidates/E22_ZnDia_parent.cif'); P = par.get_positions()
for tag, cif in TAGS.items():
    a0 = read(f'e24i_candidates/{cif}.cif'); a1 = read(f'relax_tnf/{tag}_relaxed.cif'); assert len(a0) == len(a1)
    X0 = a0.get_positions(); fw = []
    for k in range(len(a0)):
        _, dl = find_mic(P - X0[k], a0.cell, pbc=True); j = int(np.argmin(dl))
        if dl[j] < 0.3 and par[j].symbol == a0[k].symbol: fw.append(k)
    P1 = a1.get_positions(); dists = []
    for k in fw:
        _, dl = find_mic(P1 - X0[k], a0.cell, pbc=True)
        dists.append(min(dl[j] for j in range(len(a1)) if a1[j].symbol == a0[k].symbol))
    c0, c1 = contacts(a0), contacts(a1)
    het_h = min([c1[p][0] for p in c1 if p in HEAVY_H + HEAVY_H_EXTRA] or [9.9])
    heavy = min([c1[p][0] for p in c1 if 'H' not in p.split('···')] or [9.9])
    res[tag] = {'n_atoms': len(a1), 'n_framework_matched': len(fw), 'max_framework_disp_A': round(float(max(dists)), 3),
                'min_heteroatom_H_A': het_h, 'min_heavy_heavy_A': heavy, 'contacts_before': c0, 'contacts_after': c1,
                'gate0_pass': het_h >= 1.8 and float(max(dists)) <= 1.0}
    res[tag]['gate0b'] = clash_gate.check(f'relax_tnf/{tag}_relaxed.cif')
    res[tag]['gate_all_pass'] = res[tag]['gate0_pass'] and res[tag]['gate0b']['pass_0b']
    print(f"{tag:12s} 골격 최대 변위 {max(dists):.2f} Å (짝 {len(fw)}) | 이종–H 최소 {het_h} · 무거운 원자 최소 {heavy} | (0a) {'통과' if res[tag]['gate0_pass'] else '탈락'} | (0b) 여유 {res[tag]['gate0b']['min_margin_A']:+.3f} {res[tag]['gate0b']['worst_pair']} {'통과' if res[tag]['gate0b']['pass_0b'] else '탈락'}", flush=True)
json.dump(res, open('results_e24i_fit_hkhome.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
