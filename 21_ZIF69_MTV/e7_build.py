# -*- coding: utf-8 -*-
"""E-7 조각·물 자세·힘장 결합에너지 — 등록 `E7_DFT_WATER_REGISTRATION_20260925.md` (자료 0건).

czeromof 환경(ase·scipy). DFT 는 e7_dft.py(dft 환경)가 이 파일의 산출(e7_poses.json)을 읽어 돈다.

[조각]  링커 자리(S1~S5): 전하 CIF 에서 목표 원자가 속한 비금속 연결 성분(= 링커 하나)을 주기 경계를 풀어 꺼내고,
        Zn 에 배위한 N 을 Zn 방향 1.01 Å 의 H 로 막는다(중성 링커).
        열린 Zn(S6): Zn + 배위 원자. 카복실레이트는 O₂C 까지 두고 C 의 바깥 이웃을 H(1.09 Å)로,
        이미다졸은 5원 고리까지 두고 고리 밖 무거운 이웃을 H(N–H 1.01 · C–H 1.09)로 막는다.
[전하]  조각 원자 = CIF DDEC6 전하 그대로. 막은 H 는 (목표 총전하 − 조각 전하 합)/막은 H 수 를 똑같이 나눠 가진다.
        목표 총전하: 링커 0, 열린 Zn 클러스터 = 2 − (카복실레이트 수).
[힘장]  UFF_MOF 원소 LJ(혼합 규칙 파일 값) × Ow(89.633 K, 3.097 Å), Lorentz–Berthelot, 12 Å shifted(파일 머리말 "shifted"),
        Hw·Lw LJ 없음. 쿨롱: 조각 전하 × TIP5P-Ew(Hw +0.241, Lw −0.241, Ow 0), 절단 없음(클러스터).
[자세]  ① 힘장 최소(강체 물 6 자유도, 무작위 시작 40, scipy) ② 정형 수소결합 4 — 받개 자리: 물 H 가 자리 원자를 향함(O…X 2.90,
        N 2.95, Cl 3.25 Å) 평면 두 방향 × 방향 두 개 / 주개 자리(O–H, N–H): 물 O 를 D–H 연장선 2.90 Å / 열린 Zn: 물 O 를 Zn 빈 방향 2.10 Å.
        물–조각 최소 거리 < 1.5 Å 인 자세는 버린다.
"""
import json, math, os, sys
import numpy as np
from ase.io import read
from ase.neighborlist import neighbor_list
from scipy.optimize import minimize
from scipy.spatial.transform import Rotation as Rot

HERE = os.path.dirname(os.path.abspath(__file__))
K2KJ = 0.0083144626          # K → kJ/mol
COUL = 1389.35456            # kJ/mol·Å/e²
CUT = 12.0
UFF = {'Cu': (2.5161, 3.11369), 'O': (30.1932, 3.11815), 'N': (34.7221, 3.26069), 'C': (52.8380, 3.43085), 'S': (137.8821, 3.59478),
       'Cl': (114.2308, 3.51638), 'H': (22.1417, 2.57113), 'Zn': (62.3992, 2.46155), 'F': (25.1610, 2.99698)}
OW = (89.633, 3.097)
# TIP5P-Ew 강체 기하(19_WaterCompetition/water.def) — O · H · H · L · L
WAT = np.array([[0, 0, 0], [0.75695, 0, 0.58588], [-0.75695, 0, 0.58588], [0, 0.57154, -0.40415], [0, -0.57154, -0.40415]])
WQ = np.array([0.0, 0.241, 0.241, -0.241, -0.241])

SITES = {
    'S1_SO3H':  dict(cif='charged_v3/saIm050_DDEC6.cif', find='so3h'),
    'S2_SO2CH3': dict(cif='charged_v3/mslm050_DDEC6.cif', find='so2ch3'),
    'S3_NO2':   dict(cif='charged_v3/nbIm100_DDEC6.cif', find='no2'),
    'S4_Cl':    dict(cif='charged_v3/base_DDEC6.cif', find='cl'),
    'S5a_NH2':  dict(cif='charged_v3/maf66_DDEC6.cif', find='nh2'),
    'S5b_Nfree': dict(cif='charged_v3/maf66_DDEC6.cif', find='nfree'),
    # S6(열린 금속) 철회 — 09-25 기하 확인: Zn(bib)(bdtdc) 사면체 N2O2 · Cu dia 4+2(축 O 2.51 Å) · Zn srs 사면체. 빈자리 없음.
}


def load(cif):
    from pymatgen.io.cif import CifParser
    a = read(os.path.join(HERE, cif))
    blk = list(CifParser(os.path.join(HERE, cif)).as_dict().values())[0]
    q = np.array([float(x) for x in blk['_atom_site_charge']])
    assert len(q) == len(a), (cif, len(q), len(a))
    return a, q


def nbrs(a, cut=None):
    i, j, D = neighbor_list('ijD', a, {('H', 'H'): 0.0, **{}} if False else 1.0) if False else (None, None, None)
    # 원소쌍 결합 거리: 공유반지름 합 × 1.2 (Zn–X 는 2.4 Å 까지)
    from ase.data import covalent_radii
    cuts = [covalent_radii[z] * 1.15 for z in a.numbers]
    for k, s in enumerate(a.get_chemical_symbols()):
        if s in ('Zn', 'Cu'):
            cuts[k] = 1.45      # Zn–O 2.065 Å 가 1.30 에서 빠졌음(09-25 검사기 의심으로 발견)
    i, j, D = neighbor_list('ijD', a, cuts)
    out = {k: [] for k in range(len(a))}
    for x, y, d in zip(i, j, D):
        out[x].append((y, d))
    return out


def component(a, nb, start, stop_metal=True):
    """start 에서 비금속 결합으로 이어진 원자(주기 경계를 푼 좌표 벡터 포함)."""
    sym = a.get_chemical_symbols()
    pos = {start: a.positions[start].copy()}
    stack = [start]
    while stack:
        k = stack.pop()
        for y, d in nb[k]:
            if stop_metal and sym[y] in ('Zn', 'Cu'):
                continue
            if y not in pos:
                pos[y] = pos[k] + d
                stack.append(y)
    return pos


def cap(p_from, p_to, L):
    v = p_to - p_from
    return p_from + v / np.linalg.norm(v) * L


def find_target(a, nb, kind):
    sym = a.get_chemical_symbols()
    el = lambda k: sym[k]
    for k in range(len(a)):
        ns = [el(y) for y, _ in nb[k]]
        if kind == 'so3h' and el(k) == 'S' and ns.count('O') == 3:
            ohs = [y for y, _ in nb[k] if el(y) == 'O' and any(el(z) == 'H' for z, _ in nb[y])]
            if ohs:
                return k, 'S'
        if kind == 'so2ch3' and el(k) == 'S' and ns.count('O') == 2 and ns.count('C') == 2:
            return k, 'S'
        if kind == 'no2' and el(k) == 'N' and ns.count('O') == 2:
            return k, 'N'
        if kind == 'cl' and el(k) == 'Cl':
            return k, 'Cl'
        if kind == 'nh2' and el(k) == 'N' and ns.count('H') == 2:
            return k, 'N'
        if kind == 'nfree' and el(k) == 'N' and ns.count('H') == 0 and 'Zn' not in ns and ns.count('N') >= 1:
            return k, 'N'
        if kind in ('openzn', 'opencu') and el(k) == ('Zn' if kind == 'openzn' else 'Cu'):
            return k, el(k)
    raise RuntimeError(f'자리 {kind} 못 찾음')


def build_linker(a, q, nb, t):
    sym = a.get_chemical_symbols()
    pos = component(a, nb, t)
    idx = list(pos)
    X = [pos[k] for k in idx]; S = [sym[k] for k in idx]; Q = [q[k] for k in idx]
    caps = []
    for k in idx:
        for y, d in nb[k]:
            if sym[y] in ('Zn', 'Cu'):
                caps.append(cap(pos[k], pos[k] + d, 1.01))
    tgt = 0.0
    qc = (tgt - sum(Q)) / max(1, len(caps))
    for c in caps:
        X.append(c); S.append('H'); Q.append(qc)
    return np.array(X), S, np.array(Q), idx.index(t), len(caps), qc


def build_openzn(a, q, nb, z):
    sym = a.get_chemical_symbols()
    X, S, Q = [a.positions[z].copy()], [sym[z]], [q[z]]
    caps = []; n_carb = 0; lig_dirs = []
    for y, d in nb[z]:
        py = a.positions[z] + d
        lig_dirs.append(d / np.linalg.norm(d))
        if sym[y] == 'O':            # 카복실레이트: O–C(–O)
            c = [(w, dd) for w, dd in nb[y] if sym[w] == 'C'][0]
            pc = py + c[1]
            o2 = [(w, dd) for w, dd in nb[c[0]] if sym[w] == 'O' and w != y][0]
            po2 = pc + o2[1]
            ext = [(w, dd) for w, dd in nb[c[0]] if sym[w] == 'C'][0]
            for p, s in ((py, 'O'), (pc, 'C'), (po2, 'O')):
                X.append(p); S.append(s)
            Q += [q[y], q[c[0]], q[o2[0]]]
            caps.append(cap(pc, pc + ext[1], 1.09)); n_carb += 1
        elif sym[y] == 'N':          # 이미다졸 고리
            ring = component_ring(a, nb, y)
            for w, p in ring.items():
                X.append(py + p); S.append(sym[w]); Q.append(q[w])
                for v, dd in nb[w]:
                    if v in ring or sym[v] in ('Zn', 'Cu'):
                        continue
                    if sym[v] == 'H':
                        X.append(py + p + dd); S.append('H'); Q.append(q[v])
                    else:
                        caps.append(cap(py + p, py + p + dd, 1.01 if sym[w] == 'N' else 1.09))
    tgt = 2.0 - n_carb
    qc = (tgt - sum(Q)) / max(1, len(caps))
    for c in caps:
        X.append(c); S.append('H'); Q.append(qc)
    sv = np.sum(lig_dirs, axis=0)
    if np.linalg.norm(sv) < 0.2:      # 평면 사각형(Cu(II)): 축 방향 = 리간드 평면 법선
        open_dir = np.linalg.svd(np.array(lig_dirs))[2][-1]
    else:                             # 사면체: 리간드 평균의 반대(가장 넓은 면)
        open_dir = -sv / np.linalg.norm(sv)
    return np.array(X), S, np.array(Q), 0, len(caps), qc, open_dir, int(round(tgt))


def component_ring(a, nb, n0):
    """n0 이 속한 5원 고리 원자 → n0 기준 상대 좌표."""
    sym = a.get_chemical_symbols()
    heavy = lambda k: [(y, d) for y, d in nb[k] if sym[y] in ('C', 'N')]
    for y1, d1 in heavy(n0):
        for y2, d2 in heavy(y1):
            if y2 == n0: continue
            for y3, d3 in heavy(y2):
                if y3 in (n0, y1): continue
                for y4, d4 in heavy(y3):
                    if y4 in (n0, y1, y2): continue
                    for y5, d5 in heavy(y4):
                        if y5 == n0:
                            r = {n0: np.zeros(3)}; r[y1] = d1; r[y2] = d1 + d2; r[y3] = d1 + d2 + d3; r[y4] = d1 + d2 + d3 + d4
                            return r
    raise RuntimeError('5원 고리 못 찾음')


def align(u, v):
    """v 를 u 로 돌리는 회전 — 정반대 벡터에서 scipy 가 영 사원수를 내는 경우를 피한다."""
    u = u / np.linalg.norm(u); v = v / np.linalg.norm(v)
    c = float(np.dot(u, v))
    if c < -0.999999:
        perp = np.cross(v, [1, 0, 0] if abs(v[0]) < 0.9 else [0, 1, 0]); perp /= np.linalg.norm(perp)
        return Rot.from_rotvec(perp * math.pi)
    return Rot.align_vectors([u], [v])[0]


def water_xyz(p):
    """p = [x,y,z, rotvec(3)] → 5자리 좌표."""
    return Rot.from_rotvec(p[3:]).apply(WAT) + p[:3]


def e_ff(X, S, Q, W):
    e_lj = 0.0
    for x, s in zip(X, S):
        eps, sig = UFF[s]
        e = math.sqrt(eps * OW[0]); sg = 0.5 * (sig + OW[1])
        r = np.linalg.norm(W[0] - x)
        if r < CUT:
            lj = lambda rr: 4 * e * ((sg / rr) ** 12 - (sg / rr) ** 6)
            e_lj += lj(r) - lj(CUT)
    e_lj *= K2KJ
    d = np.linalg.norm(X[:, None, :] - W[None, :, :], axis=2)
    e_c = COUL * np.sum(Q[:, None] * WQ[None, :] / d)
    return e_lj + e_c, e_lj, e_c


def ok_geom(X, W, lim=1.5):
    return np.min(np.linalg.norm(X[:, None, :] - W[None, :3, :], axis=2)) >= lim


def poses(X, S, Q, ti, kind, open_dir=None, rng=np.random.default_rng(7), n_caps=0):
    tx = X[ti]
    caps_idx = list(range(len(X) - n_caps, len(X)))
    out = []
    # ① 힘장 최소
    best = None
    for _ in range(40):
        dirv = rng.normal(size=3); dirv /= np.linalg.norm(dirv)
        p0 = np.r_[tx + dirv * rng.uniform(2.8, 3.6), rng.normal(size=3)]
        def f(p):
            W = water_xyz(p)
            if not ok_geom(X, W, 1.2):
                return 1e3
            # 막은 H(인공 — 실제 골격에선 Zn 자리) 옆 자세 금지: 물 O 가 자리 원자에 막은 H 보다 0.5 Å 이상 가까워야 함(09-25 S3 ff_min 결함)
            if caps_idx and min(np.linalg.norm(X[c] - W[0]) for c in caps_idx) < np.linalg.norm(tx - W[0]) + 0.5:
                return 1e3
            return e_ff(X, S, Q, W)[0]
        r = minimize(f, p0, method='Powell', options={'maxiter': 4000, 'xtol': 1e-3, 'ftol': 1e-4})
        if best is None or r.fun < best.fun:
            best = r
    out.append(('ff_min', water_xyz(best.x)))
    # ② 정형 자세
    sym = S
    nbrs_t = [k for k in range(len(X)) if k != ti and np.linalg.norm(X[k] - tx) < 1.9]
    away = tx - np.mean([X[k] for k in nbrs_t], axis=0) if nbrs_t else np.array([0, 0, 1.0])
    away /= np.linalg.norm(away)

    def place_O(o_pos, h_point_to=None, spin=0.0):
        # 물 O 를 o_pos 에; h_point_to 가 있으면 H1 이 그쪽을 향하게, 없으면 두 H 가 away 방향
        if h_point_to is not None:
            u = h_point_to - o_pos; u /= np.linalg.norm(u)
            r = align(u, WAT[1])
        else:
            bis = (WAT[1] + WAT[2]) / 2; bis /= np.linalg.norm(bis)
            r = align(away, bis)
            u = away
        r = Rot.from_rotvec(u * spin) * r
        return r.apply(WAT) + o_pos

    targets = []
    if kind in ('so3h', 'so2ch3', 'no2', 'nfree', 'cl'):
        acc = [k for k in range(len(X)) if sym[k] in ('O', 'N', 'Cl') and np.linalg.norm(X[k] - tx) < 1.9 and k != ti] if kind in ('so3h', 'so2ch3', 'no2') else [ti]
        acc = [k for k in acc if not any(sym[h] == 'H' and np.linalg.norm(X[h] - X[k]) < 1.1 for h in range(len(X)))] or acc
        L = {'O': 2.90, 'N': 2.95, 'Cl': 3.25}
        for k in acc[:2]:
            ax = X[k] - tx
            ax = away.copy() if np.linalg.norm(ax) < 1e-6 else ax / np.linalg.norm(ax)   # 자리 원자 자신이 받개(Cl·비배위 N)면 고립전자쌍 방향 = away
            for spin in (0.0, math.pi / 2):
                o = X[k] + ax * L[sym[k]]
                targets.append((f'acc_{sym[k]}{k}_s{int(spin*100)}', place_O(o, X[k], spin)))
    if kind in ('so3h', 'nh2'):
        dh = [(k, h) for k in range(len(X)) for h in range(len(X)) if sym[h] == 'H' and sym[k] in ('O', 'N')
              and np.linalg.norm(X[h] - X[k]) < 1.1 and np.linalg.norm(X[k] - tx) < 1.9 + (0 if kind == 'so3h' else 0.1)]
        for k, h in dh[:2]:
            u = X[h] - X[k]; u /= np.linalg.norm(u)
            for spin in (0.0, math.pi / 2):
                away[:] = u                   # 주개 자세: 물 H 는 N–H/O–H 연장 방향(바깥)으로 — 09-25 +164 kJ/mol 결함 수정
                targets.append((f'don_{sym[k]}{k}_s{int(spin*100)}', place_O(X[k] + u * 2.90, None, spin)))
    if kind in ('openzn', 'opencu'):
        dirs = [open_dir] if kind == 'openzn' else [open_dir, -open_dir]
        for dv in dirs:
            for spin in ((0.0, math.pi / 2) if kind == 'opencu' else (0.0, math.pi / 2, math.pi, 3 * math.pi / 2)):
                away[:] = dv
                L = 2.10 if kind == 'openzn' else 2.35     # Cu(II) 축 물 2.3~2.4 Å
                targets.append((f'{sym[ti]}_{"p" if dv is open_dir else "m"}_s{int(spin*100)}', place_O(tx + dv * L, None, spin)))
    acc_t = [t for t in targets if t[0].startswith('acc')]; don_t = [t for t in targets if t[0].startswith('don')]
    rest = [t for t in targets if not t[0].startswith(('acc', 'don'))]
    pick = (acc_t[:2] + don_t[:2]) if (acc_t and don_t) else (acc_t + don_t + rest)[:4]
    for name, W in pick:
        out.append((name, W))
    return [(n, W) for n, W in out if ok_geom(X, W)]


if __name__ == '__main__':
    res = {}
    for site, cfg in SITES.items():
        a, q = load(cfg['cif']); nb = nbrs(a)
        t, _ = find_target(a, nb, cfg['find'])
        if cfg['find'] in ('openzn', 'opencu'):
            X, S, Q, ti, ncap, qc, od, charge = build_openzn(a, q, nb, t)
        else:
            X, S, Q, ti, ncap, qc = build_linker(a, q, nb, t); od = None; charge = 0
        ps = poses(X, S, Q, ti, cfg['find'], od, n_caps=ncap)
        rows = []
        for name, W in ps:
            e, lj, c = e_ff(X, S, Q, W)
            rows.append({'pose': name, 'E_ff': round(e, 3), 'E_lj': round(lj, 3), 'E_coul': round(c, 3),
                         'water': [[float(v) for v in w] for w in W[:3]]})
        res[site] = {'cif': cfg['cif'], 'target_index_in_cif': int(t), 'n_frag': len(X), 'n_caps': ncap, 'cap_charge': round(qc, 4),
                     'frag_charge_total': round(float(Q.sum()), 6), 'dft_charge': charge,
                     'frag_symbols': S, 'frag_xyz': [[float(v) for v in x] for x in X], 'poses': rows}
        print(f"{site:10s} 조각 {len(X):3d}원자 (막은 H {ncap}, 각 {qc:+.3f} e) 전하합 {Q.sum():+.4f} → 자세 {len(rows)}: "
              + ' · '.join(f"{r['pose']} {r['E_ff']:.1f}" for r in rows), flush=True)
    json.dump(res, open(os.path.join(HERE, 'e7_poses.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
