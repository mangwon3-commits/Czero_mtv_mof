"""E-24c 들어가는가 관문(등록 §HKHOME 16차 (0)) — `e24_measure.py` 사본(그 파일은 import 하면 E-24 결과를 다시 써서 복사함), 대상 · 경로 · 출력만 바꿈.
E-24 원문: — E-22a 와 같은 양: ① 비결합 최소 접촉(위상거리 ≥ 3, 이종 원자–H 포함) ② 치환기 아닌 골격 원자 최대 변위(같은 원소 최근접 짝, 순서 무관).
Zeo++ 는 RASPA(E-23)가 도는 동안 안 씀(CLAUDE.md §5) — PLD/LCD 는 뒤에."""
import json, collections, numpy as np
from ase.io import read
from ase.neighborlist import neighbor_list
from ase.data import covalent_radii
from ase.geometry import find_mic
TAGS = {'e24c_cl_100': 'E24c_ZnDia_Cl_100', 'e24c_och3_100': 'E24c_ZnDia_OCH3_100', 'e24c_c2h5_100': 'E24c_ZnDia_C2H5_100', 'e24c_sch3_100': 'E24c_ZnDia_SCH3_100'}
HEAVY_H_EXTRA = ('Cl···H', 'H···S')
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
    a0 = read(f'e24c_candidates/{cif}.cif'); a1 = read(f'relax_tnf/{tag}_relaxed.cif'); assert len(a0) == len(a1)
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
    print(f"{tag:12s} 골격 최대 변위 {max(dists):.2f} Å (짝 {len(fw)}) | 이종–H 최소 {het_h} · 무거운 원자 최소 {heavy} | 관문(0) {'통과' if res[tag]['gate0_pass'] else '탈락'}", flush=True)
json.dump(res, open('results_e24c_fit_hkhome.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
