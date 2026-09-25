# -*- coding: utf-8 -*-
"""MAGI-005 E-22 준비 — Zn(bib)(bdtdc) 형판의 benzodithiophene 4,8-자리 치환 후보 CIF. laptop(Melchior). 계산 0(빌드·점검만).

배정: `ASSIGN_MAGI5B_20260925.md` §laptop 6차(14:32) "E-22 준비". 예측 등록은 후보 목록을 받은 종합자가 함(자료 0건).
형판: `core_pop_cifs/2017_Zn__dia_3_ASR_1.cif`(zip 판과 md5 526ff364 일치 확인) — P1, Zn4 C88 H72 N16 O16 S8
      = Zn(bib)(bdtdc) × 4 (bib = 1,4-비스(이미다졸-1-일)**부탄** C10H14N4 — 조성으로 확인, bdtdc C12H4O4S2).

[자리]  무 Zn·무 H 결합 그래프(공유반지름 × 1.15)의 최소 고리 기저에서 **탄소만의 6원 고리**(= BDT 가운데 벤젠, 셀당 4)의
        C–H 탄소. 셀당 8(링커당 2 = 4,8-자리). 3,7-자리(티오펜 C–H)는 5원 고리라 자동으로 빠짐.
[치환기 기하]  rdkit: 페닐-X(PhNO₂ · PhSO₂CH₃) 를 ETKDG(seed 0xE22) + MMFF94 최적화 → ipso 틀(x = C→X, 법선 = 고리면)에서
        치환기 원자의 내부 좌표를 떼어 형판의 같은 틀(x = 원래 C→H 방향, 법선 = 고리면)에 옮김. 결합 길이·각은 MMFF 값.
[비틀림]  Car–X 축 둘레 5° 격자 주사 — 치환기 원자에서 **자기 치환기·ipso C 밖** 모든 원자(주기 영상)까지 최소거리를 최대로.
        X 자신은 ipso 의 고리 이웃 둘(1,3 쌍, 비틀림 무관)을 뺌. 100 % 는 자리 순서 의존을 없애려 전 자리를 3회 돌려 재주사(수렴 기록).
[50 %]  **링커 단위**: bdtdc 4개 중 2개를 4,8-이치환(나머지 2개 무치환) — 합성 가능한 쪽이 4,8-대칭 이치환 링커와 모체 링커의 MTV 혼합이라서.
        (자리 단위 무작위 4/8 은 일치환 링커를 만듦 — 이 판에서는 안 만듦. 필요하면 같은 스크립트에 모드 추가.)
        어느 두 링커인지는 `random.Random(SEED).sample` 로 고르고 seed 를 기록(동결이 아니라 기록 — 다른 배치는 seed 만 바꿈).
[점검]  조성 · 전원자 최소거리(모체 C–H 0.929 < 1.0 이라 참고값) · **비결합 최소거리(위상거리 ≥ 3) ≥ 1.0 Å** · 치환기–골격 최소거리 ·
        check_substituent_clash.check(성분 수 = Zn×3 · 금지 접촉 · H 관통 · 짓눌린 결합) · 치환기 결합 길이·각 · 고리면 대 치환기면 비틀림.
출력:  e22_candidates/E22_ZnDia_{parent,NO2_100,NO2_050,SO2Me_100,SO2Me_050}.cif(P1, 전하 없음 — PACMAN 은 이완 뒤) + e22_candidates/e22_build.json
"""
import json, math, os, random, sys
import numpy as np
import networkx as nx
from ase import Atoms
from ase.io import read, write
from ase.neighborlist import natural_cutoffs, neighbor_list
from rdkit import Chem
from rdkit.Chem import AllChem

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import check_substituent_clash as CK   # noqa: E402

SRC = os.path.join(HERE, 'core_pop_cifs', '2017_Zn__dia_3_ASR_1.cif')
OUTD = os.path.join(HERE, 'e22_candidates')
SEED = 0xE22            # rdkit 배치·50 % 링커 고르기 공용. 기록용.
STEP = 5                # 비틀림 격자(°)
SMILES = {'NO2': 'c1ccccc1[N+](=O)[O-]', 'SO2Me': 'c1ccccc1S(=O)(=O)C'}


def write_cif(path, atoms):
    """ASE 쓰기 + 옛 대칭 태그(build_candidate_aryl.fix_tags 와 같은 치환 — RASPA·Zeo++·PACMAN 이 읽는 판)."""
    write(path, atoms)
    t = open(path, encoding='utf-8').read()
    for o, n in (('_space_group_name_H-M_alt', '_symmetry_space_group_name_H-M'),
                 ('_space_group_IT_number', '_symmetry_Int_Tables_number'),
                 ('_space_group_symop_operation_xyz', '_symmetry_equiv_pos_as_xyz')):
        t = t.replace(o, n)
    open(path, 'w', encoding='utf-8').write(t)


def graph(a):
    i, j, d = neighbor_list('ijd', a, natural_cutoffs(a, mult=CK.BOND_MULT))
    G = nx.Graph(); G.add_nodes_from(range(len(a)))
    for x, y, dd in zip(i, j, d):
        if x < y:
            G.add_edge(int(x), int(y))
    return G


def sites(a, G):
    sym = a.get_chemical_symbols()
    H = G.subgraph([k for k in range(len(a)) if sym[k] not in ('H', 'Zn')])
    rings = [c for c in nx.minimum_cycle_basis(H) if len(c) == 6 and all(sym[k] == 'C' for k in c)]
    out = []
    for ri, c in enumerate(sorted(rings, key=min)):
        for k in sorted(c):
            hs = [m for m in G[k] if sym[m] == 'H']
            if hs:
                nb = sorted(m for m in G[k] if sym[m] == 'C' and m in c)
                out.append({'ring': ri, 'C': k, 'H': hs[0], 'nbr': nb})
    return out, len(rings)


def fragment(kind):
    """rdkit PhX → ipso 틀 좌표: 치환기 원자(원소, [x, y, z]) · x = C→X, z = 고리 법선."""
    m = Chem.AddHs(Chem.MolFromSmiles(SMILES[kind]))
    AllChem.EmbedMolecule(m, randomSeed=SEED); AllChem.MMFFOptimizeMolecule(m, maxIters=2000)
    P = m.GetConformer().GetPositions(); at = [x.GetSymbol() for x in m.GetAtoms()]
    ipso = 5                                   # SMILES 의 여섯째 방향족 C 에 X 가 붙음
    X = [n.GetIdx() for n in m.GetAtomWithIdx(ipso).GetNeighbors() if not n.GetIsAromatic()][0]
    ring_nb = [n.GetIdx() for n in m.GetAtomWithIdx(ipso).GetNeighbors() if n.GetIsAromatic()]
    ex = P[X] - P[ipso]; ex /= np.linalg.norm(ex)
    nz = np.cross(P[ring_nb[0]] - P[ipso], P[ring_nb[1]] - P[ipso]); nz -= nz.dot(ex) * ex; nz /= np.linalg.norm(nz)
    ey = np.cross(nz, ex)
    # 치환기 = ipso 에서 X 쪽으로 도달하는 비방향족 부분(X 와 그 뒤)
    sub, stack = {X}, [X]
    while stack:
        u = stack.pop()
        for n in m.GetAtomWithIdx(u).GetNeighbors():
            if n.GetIdx() != ipso and n.GetIdx() not in sub:
                sub.add(n.GetIdx()); stack.append(n.GetIdx())
    order = [X] + sorted(sub - {X})
    loc = [(at[k], [float((P[k] - P[ipso]).dot(e)) for e in (ex, ey, nz)]) for k in order]
    return loc


def frame(a, s):
    c = a.positions[s['C']]
    v = [a.get_distance(s['C'], k, mic=True, vector=True) for k in (s['H'], *s['nbr'])]
    nz = np.cross(v[1], v[2]); nz /= np.linalg.norm(nz)
    ex = v[0] - v[0].dot(nz) * nz; ex /= np.linalg.norm(ex)
    return c, ex, np.cross(nz, ex), nz


def place(c, ex, ey, nz, loc, th):
    ct, st = math.cos(th), math.sin(th)
    return np.array([c + p[0] * ex + (p[1] * ct - p[2] * st) * ey + (p[1] * st + p[2] * ct) * nz for _, p in loc])


def mind(a, pts, excl_rows):
    """pts 각 점에서 a 의 원자까지 최소 영상 거리. excl_rows[i] = 그 점에서 뺄 원자 인덱스 집합."""
    from ase.geometry import get_distances
    _, D = get_distances(pts, a.positions, cell=a.cell, pbc=True)
    for i, ex in enumerate(excl_rows):
        D[i, list(ex)] = np.inf
    return float(D.min())


def build(a0, G, S, kind, chosen):
    """chosen 자리의 H 를 치환기로 바꿈. 반환: 새 Atoms, 자리별 기록."""
    loc = fragment(kind)
    keep = [k for k in range(len(a0)) if k not in {s['H'] for s in chosen}]
    base = a0[keep]; remap = {k: i for i, k in enumerate(keep)}
    th = {s['C']: 0.0 for s in chosen}
    fr = {s['C']: frame(a0, s) for s in chosen}
    grid = np.radians(np.arange(0, 360, STEP))
    hist = []
    for sweep in range(3):
        changed = 0
        for s in chosen:
            others = [place(*fr[t['C']], loc, th[t['C']]) for t in chosen if t['C'] != s['C']]
            env = base + Atoms([e for t in chosen if t['C'] != s['C'] for e, _ in loc],
                               positions=np.vstack(others) if others else np.zeros((0, 3)), cell=base.cell, pbc=True)
            ipso = remap[s['C']]; nb = {remap[k] for k in s['nbr']}
            excl = [{ipso} | nb] + [{ipso}] * (len(loc) - 1)
            best = max(grid, key=lambda t: mind(env, place(*fr[s['C']], loc, t), excl))
            if abs(best - th[s['C']]) > 1e-9:
                changed += 1
            th[s['C']] = float(best)
        hist.append(changed)
        if changed == 0:
            break
    new = base + Atoms([e for s in chosen for e, _ in loc],
                       positions=np.vstack([place(*fr[s['C']], loc, th[s['C']]) for s in chosen]), cell=base.cell, pbc=True)
    new.wrap()
    return new, th, hist, loc


def checks(new, n_sub_atoms, loc, kind, chosen_n):
    sym = np.array(new.get_chemical_symbols()); G = graph(new)
    i, j, d = neighbor_list('ijd', new, 3.2)
    allmin = float(d.min())
    sp = dict(nx.all_pairs_shortest_path_length(G, cutoff=2))
    nonb = [(float(dd), sym[x] + '-' + sym[y]) for x, y, dd in zip(i, j, d) if x < y and y not in sp.get(int(x), {})]
    nonb.sort()
    first_sub = len(new) - n_sub_atoms
    subn = [(float(dd), sym[x] + '-' + sym[y]) for x, y, dd in zip(i, j, d)
            if x < y and (x >= first_sub or y >= first_sub) and y not in sp.get(int(x), {})]
    subn.sort()
    # 치환기가 누구와 부딪히나 — 상대 원자의 무 Zn 성분(링커)으로 이름표(bib = N 있고 S 없음 · bdtdc = S 있음)
    Hz = G.subgraph([k for k in G if sym[k] != 'Zn'])
    def who(k):
        if sym[k] == 'Zn':
            return 'Zn'
        c = nx.node_connected_component(Hz, k); el = set(sym[list(c)])
        tag = 'bdtdc' if 'S' in el else ('bib' if 'N' in el else '?')
        nb = sorted(sym[m] for m in G[k] if sym[m] != 'H')
        return f"{sym[k]}({tag}; 결합 {''.join(nb) or '-'})"
    contacts = []
    for x, y, dd in zip(i, j, d):
        if x < y and (x >= first_sub) != (y >= first_sub) and y not in sp.get(int(x), {}):
            s_, o_ = (x, y) if x >= first_sub else (y, x)
            contacts.append((round(float(dd), 3), sym[s_] + '(치환기)', who(int(o_))))
    contacts = sorted(set(contacts))[:4]
    # 치환기 내부 기하(첫 치환기 대표 + 전 자리 범위)
    per = len(loc); geo = {'C-X': [], 'X-O': [], 'O-X-O': [], 'twist_deg': []}
    for s in range(chosen_n):
        o = first_sub + s * per; X = o
        ipso = min((k for k in G[X] if sym[k] == 'C' and k < first_sub), key=lambda k: new.get_distance(X, k, mic=True))
        geo['C-X'].append(new.get_distance(ipso, X, mic=True))
        Os = [k for k in range(o, o + per) if sym[k] == 'O']
        geo['X-O'] += [new.get_distance(X, k, mic=True) for k in Os]
        geo['O-X-O'].append(new.get_angle(Os[0], X, Os[1], mic=True))
        rn = [k for k in G[ipso] if k != X and sym[k] == 'C']
        v1, v2 = (new.get_distance(ipso, k, mic=True, vector=True) for k in rn)
        nr = np.cross(v1, v2); nr /= np.linalg.norm(nr)
        if kind == 'NO2':
            w = np.cross(new.get_distance(X, Os[0], mic=True, vector=True), new.get_distance(X, Os[1], mic=True, vector=True))
            w /= np.linalg.norm(w); geo['twist_deg'].append(math.degrees(math.acos(min(1.0, abs(float(nr.dot(w)))))))
        else:   # 고리면과 C_ar–S–C_me 면의 각
            cm = [k for k in range(o, o + per) if sym[k] == 'C'][0]
            w = np.cross(new.get_distance(X, ipso, mic=True, vector=True), new.get_distance(X, cm, mic=True, vector=True))
            w /= np.linalg.norm(w); geo['twist_deg'].append(math.degrees(math.acos(min(1.0, abs(float(nr.dot(w)))))))
    rng = {k: [round(min(v), 3), round(max(v), 3)] for k, v in geo.items() if v}
    return {'formula': new.get_chemical_formula(), 'n_atoms': len(new), 'all_pair_min_A': round(allmin, 3),
            'nonbonded_min_A(topo>=3)': [round(nonb[0][0], 3), nonb[0][1]],
            'substituent_nonbonded_min_A': [round(subn[0][0], 3), subn[0][1]] if subn else None,
            'nonbonded_ge_1.0': nonb[0][0] >= 1.0, 'substituent_to_framework_contacts_top': contacts, 'substituent_geometry_range': rng}


def main():
    os.makedirs(OUTD, exist_ok=True)
    a0 = read(SRC)
    a0 = Atoms(a0.get_chemical_symbols(), positions=a0.positions, cell=a0.cell, pbc=True)   # 전하 떼기
    G = graph(a0); S, nring = sites(a0, G)
    assert nring == 4 and len(S) == 8, (nring, len(S))
    rings = sorted({s['ring'] for s in S})
    pick = sorted(random.Random(SEED).sample(rings, 2))
    rec = {'test': 'MAGI-005 E-22 준비 — Zn(bib)(bdtdc) 4,8-치환 후보 빌드', 'assign': 'ASSIGN_MAGI5B_20260925.md §laptop 6차',
           'template': os.path.relpath(SRC, HERE), 'template_formula': a0.get_chemical_formula(), 'seed': SEED, 'torsion_step_deg': STEP,
           'sites_per_cell': len(S), 'bdtdc_per_cell': nring, 'sites': S, 'half_rule': '링커 단위 — bdtdc 4 중 2 를 4,8-이치환',
           'half_rings_chosen': pick, 'note': '판정 없음. 전하 없음(PACMAN 은 이완 뒤). Zeo++ 안 씀(E-21 RASPA 동시, CLAUDE.md §5) — PLD 는 데스크탑.',
           'rows': []}
    p = os.path.join(OUTD, 'E22_ZnDia_parent.cif'); write_cif(p, a0)
    c0 = CK.check(p)
    rec['rows'].append({'name': 'E22_ZnDia_parent', 'kind': None, 'fraction': 0.0, 'n_substituted': 0,
                        **checks(a0, 0, [], None, 0),
                        'clash_check': c0})
    for kind in ('NO2', 'SO2Me'):
        for frac, chosen in ((1.0, S), (0.5, [s for s in S if s['ring'] in pick])):
            new, th, hist, loc = build(a0, G, S, kind, chosen)
            n_sub = len(chosen) * len(loc)
            name = f'E22_ZnDia_{kind}_{int(round(frac * 100)):03d}'
            path = os.path.join(OUTD, name + '.cif'); write_cif(path, new)
            r = {'name': name, 'kind': kind, 'fraction': frac, 'n_substituted': len(chosen),
                 'torsion_deg': {str(k): round(math.degrees(v), 1) for k, v in th.items()}, 'sweeps_changed': hist,
                 'fragment_local': [[e, [round(x, 4) for x in pp]] for e, pp in loc],
                 **checks(new, n_sub, loc, kind, len(chosen)), 'clash_check': CK.check(path)}
            rec['rows'].append(r)
            print(f"{name:22s} {r['formula']:28s} 비결합 최소 {r['nonbonded_min_A(topo>=3)']} · 치환기 {r['substituent_nonbonded_min_A']} · "
                  f"충돌검사 {'통과' if r['clash_check']['pass'] else '탈락'}(성분 {r['clash_check']['n_components']}/{r['clash_check']['expected']}) · "
                  f"기하 {r['substituent_geometry_range']} · 재주사 {hist}", flush=True)
    print('parent', rec['rows'][0]['formula'], '충돌검사', rec['rows'][0]['clash_check'])
    json.dump(rec, open(os.path.join(OUTD, 'e22_build.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1, default=float)
    return 0


if __name__ == '__main__':
    sys.exit(main())
