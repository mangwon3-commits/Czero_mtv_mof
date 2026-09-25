"""E-22a 측정 — 등록 ASSIGN_MAGI5B §HKHOME 6차: ① 비결합 최소 접촉(위상거리 ≥ 3) ② 치환기 아닌 골격 원자 최대 변위 ③ PLD/LCD(Zeo++)."""
import json, subprocess, os, numpy as np, collections
from ase.io import read
from ase.neighborlist import neighbor_list
from ase.data import covalent_radii
TAGS = {'e22_parent': 'E22_ZnDia_parent', 'e22_no2_050': 'E22_ZnDia_NO2_050', 'e22_no2_100': 'E22_ZnDia_NO2_100',
        'e22_so2me_050': 'E22_ZnDia_SO2Me_050', 'e22_so2me_100': 'E22_ZnDia_SO2Me_100'}
NET = '/home/mangwon1/miniconda3/envs/czeromof/bin/network'

def contacts(a):
    cuts = [covalent_radii[z] * 1.15 if a[k].symbol != 'Zn' else 1.45 for k, z in enumerate(a.numbers)]
    i, j = neighbor_list('ij', a, cuts)
    G = collections.defaultdict(set)
    for x, y in zip(i, j): G[x].add(y)
    ii, jj, dd = neighbor_list('ijd', a, 3.2)
    s = a.get_chemical_symbols(); best = {}
    for x, y, d in zip(ii, jj, dd):
        if x >= y: continue
        pair = '···'.join(sorted((s[x], s[y])))
        if pair not in ('O···O', 'H···O', 'H···H', 'N···O'): continue
        # 위상거리 < 3 이면 제외(BFS 2단계)
        near = {x} | G[x] | {w for v in G[x] for w in G[v]}
        if y in near: continue
        if pair not in best or d < best[pair][0]: best[pair] = (round(float(d), 3), s[x] + str(x), s[y] + str(y))
    return best

res = {}
par_in = read('e22_candidates/E22_ZnDia_parent.cif')
for tag, cif in TAGS.items():
    a0 = read(f'e22_candidates/{cif}.cif'); a1 = read(f'relax_tnf/{tag}_relaxed.cif')
    assert len(a0) == len(a1)
    # 골격 원자 = 모체 입력과 0.3 Å 안에서 짝이 되는 원자(치환기·치환된 H 제외)
    fw = []
    for k in range(len(a0)):
        d = a0.get_distances(k, list(range(len(a0))), mic=True)  # dummy to keep API
    P = par_in.get_positions(); X0 = a0.get_positions()
    from ase.geometry import find_mic
    for k in range(len(a0)):
        dv, dl = find_mic(P - X0[k], a0.cell, pbc=True)
        j = int(np.argmin(dl))
        if dl[j] < 0.3 and par_in[j].symbol == a0[k].symbol: fw.append(k)
    # relax_tnf 는 원자 순서를 바꿔 쓴다(09-25 확인: 같은 번호 비교 시 모체 변위 13 Å — 결함) → 같은 원소 최근접 짝으로(순서 무관)
    P1 = a1.get_positions(); dists = []
    for k in fw:
        dv, dl = find_mic(P1 - X0[k], a0.cell, pbc=True)
        dists.append(min(dl[j] for j in range(len(a1)) if a1[j].symbol == a0[k].symbol))
    maxd = float(max(dists))
    r = subprocess.run([NET, '-ha', '-res', f'/tmp/claude-1000/-home-mangwon1-mof-project/f528ae7e-a636-42e3-a50f-8a6c2523c6c0/scratchpad/{tag}.res', f'relax_tnf/{tag}_relaxed.cif'], capture_output=True, text=True, timeout=1200)
    lcd, pld = [float(x) for x in open(f'/tmp/claude-1000/-home-mangwon1-mof-project/f528ae7e-a636-42e3-a50f-8a6c2523c6c0/scratchpad/{tag}.res').read().split()[1:3]]
    c0, c1 = contacts(a0), contacts(a1)
    res[tag] = {'n_atoms': len(a1), 'n_framework_matched': len(fw), 'max_framework_disp_A': round(maxd, 3), 'LCD': lcd, 'PLD': pld,
                'contacts_before': c0, 'contacts_after': c1}
    print(f"{tag:14s} PLD {pld:.3f} LCD {lcd:.3f} | 골격 최대 변위 {maxd:.2f} Å (짝 {len(fw)}) | 후 O···O {c1.get('O···O',('-',))[0]} H···O {c1.get('H···O',('-',))[0]} | 전 O···O {c0.get('O···O',('-',))[0]} H···O {c0.get('H···O',('-',))[0]}", flush=True)
json.dump(res, open('results_e22a_hkhome.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
