"""ZNBDT-C1 관문 탈락 근거 — 이완본에서 말단 C≡C–H 의 O 접촉을 **위상으로** 찾아 자리(고리)별로 적음. 읽기만(쓰는 것은 출력 JSON 하나).
이완본 CIF 는 원소순으로 다시 정렬돼 원자 번호가 빌드본과 다르므로 번호를 쓰지 않음:
  알카인 C = C 이웃과 1.25 Å 안 · 말단 H = 알카인 C 에 붙은 H · 부착 C = 알카인 C 에 붙은 방향족 C → 모체 X선(`build_e22_bdtdc.SRC`)의 4,8-자리 C 와
  최소상 거리 0.8 Å 안에서 짝지어 고리 번호를 얻음(B.sites 의 'ring').
대상: C1 열린 자리(relax_tnf/e24i_cch_open_relaxed.cif) · E-24g 전 치환(relax_tnf/e24g_cch_100_relaxed.cif, 비교).
물음: E-24g 전 치환판의 탈락 접촉(H···O 1.734)은 겹친 고리(0 · 1)의 자리에서 났나, 열린 고리(2 · 3)에서 났나.
실행: czeromof 파이썬 · 21_ZIF69_MTV 에서 → results_znbdt_c1_contacts_hkhome.json"""
import collections, json, os, sys
import numpy as np
from ase import Atoms
from ase.io import read
from ase.data import covalent_radii
from ase.geometry import find_mic
from ase.neighborlist import neighbor_list
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE); os.chdir(HERE)
import build_e24_bdtdc as E   # noqa: E402
import clash_gate             # noqa: E402
B = E.B
p0 = read(B.SRC); p0 = Atoms(p0.get_chemical_symbols(), positions=p0.positions, cell=p0.cell, pbc=True)
S, _ = B.sites(p0, B.graph(p0))
SITE_C = [(s['ring'], p0.positions[s['C']], s['H']) for s in S]


def graph(a):
    cuts = [covalent_radii[z] * 1.15 if a[k].symbol != 'Zn' else 1.45 for k, z in enumerate(a.numbers)]
    i, j = neighbor_list('ij', a, cuts); G = collections.defaultdict(set)
    for x, y in zip(i, j): G[int(x)].add(int(y))
    return G


def site_ring(a, c):
    best = min(((float(np.linalg.norm(find_mic(a.positions[c] - pos, a.cell, pbc=True)[0])), ring) for ring, pos, _ in SITE_C))
    return best[1] if best[0] < 0.8 else None, round(best[0], 3)


def run(path):
    a = read(path); s = a.get_chemical_symbols(); G = graph(a)
    O = [k for k in range(len(a)) if s[k] == 'O']
    alk = {k for k in range(len(a)) if s[k] == 'C' and any(s[j] == 'C' and a.get_distance(k, j, mic=True) < 1.25 for j in G[k])}
    rows = []
    for h in (k for k in range(len(a)) if s[k] == 'H'):
        ct = [j for j in G[h] if j in alk]
        if not ct: continue
        ct = ct[0]; ci = [j for j in G[ct] if j in alk and j != ct][0]
        ar = [j for j in G[ci] if s[j] == 'C' and j not in alk][0]
        ring, dmatch = site_ring(a, ar)
        dHO = sorted((a.get_distance(h, o, mic=True), o) for o in O)
        dCO = sorted((a.get_distance(ct, o, mic=True), o) for o in O)
        ang = a.get_angle(ar, ci, ct, mic=True), a.get_angle(ci, ct, h, mic=True)
        rows.append({'ring': ring, 'match_A': dmatch, 'H_O_min_A': round(dHO[0][0], 3), 'H_O_2nd_A': round(dHO[1][0], 3),
                     'Cterm_O_min_A': round(dCO[0][0], 3), 'angle_Car_C_C_deg': round(ang[0], 1), 'angle_C_C_H_deg': round(ang[1], 1),
                     'same_O_for_H_and_Cterm': dHO[0][1] == dCO[0][1]})
    rows.sort(key=lambda r: (r['ring'] if r['ring'] is not None else 9, r['H_O_min_A']))
    return {'path': path, 'n_terminal_H': len(rows), 'rows': rows, 'gate0b': clash_gate.check(path)}


out = {'note': 'ZNBDT-C1 관문(0a)(0b) 탈락 근거 — 위상 기반 접촉 · 자리별', 'parent_site_H_O': {}}
O0 = [k for k in range(len(p0)) if p0[k].symbol == 'O']
for ring, pos, h in SITE_C:
    out['parent_site_H_O'].setdefault(str(ring), []).append(round(min(p0.get_distance(h, o, mic=True) for o in O0), 3))
for tag, p in (('c1_open', 'relax_tnf/e24i_cch_open_relaxed.cif'), ('e24g_full', 'relax_tnf/e24g_cch_100_relaxed.cif'),
               ('c1_open_asbuilt', 'znbdt_c1_candidates/E24i_ZnDia_CCH_open.cif'), ('e24g_full_asbuilt', 'e24g_candidates/E24g_ZnDia_CCH_100.cif')):
    out[tag] = run(p)
    print(f"== {tag} {p} · 말단 H {out[tag]['n_terminal_H']} · (0b) 여유 {out[tag]['gate0b']['min_margin_A']:+.3f} {out[tag]['gate0b']['worst_pair']} {'통과' if out[tag]['gate0b']['pass_0b'] else '탈락'}")
    for r in out[tag]['rows']:
        print(f"   고리 {r['ring']} (짝 {r['match_A']}) · H···O {r['H_O_min_A']} (다음 {r['H_O_2nd_A']}) · C말단···O {r['Cterm_O_min_A']} · 각 Car–C≡C {r['angle_Car_C_C_deg']} · C≡C–H {r['angle_C_C_H_deg']} · 같은 O {r['same_O_for_H_and_Cterm']}")
print('모체 4,8-H···O (고리별)', out['parent_site_H_O'])
json.dump(out, open('results_znbdt_c1_contacts_hkhome.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1, default=str)
