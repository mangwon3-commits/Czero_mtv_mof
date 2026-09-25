# -*- coding: utf-8 -*-
"""E-7b ① — 조각 ESP 적합 전하(Merz–Kollman 형, 총합 = DFT 조각 전하 구속). dft 환경. 등록 E7_DFT_WATER_REGISTRATION §4."""
import json, os, numpy as np
from pyscf import gto, dft, qmmm, lib, df
lib.num_threads(int(os.environ.get('E7_THREADS', '6')))
B2A = 0.52917721092
VDW = {'H': 1.20, 'C': 1.70, 'N': 1.55, 'O': 1.52, 'S': 1.80, 'Cl': 1.75}
P = json.load(open('e7_poses.json', encoding='utf-8'))


def fib(n):
    i = np.arange(n) + 0.5; phi = np.arccos(1 - 2 * i / n); th = np.pi * (1 + 5 ** 0.5) * i
    return np.c_[np.cos(th) * np.sin(phi), np.sin(th) * np.sin(phi), np.cos(phi)]


out = {}
for site, d in P.items():
    S, X = d['frag_symbols'], np.array(d['frag_xyz']); ch = d['dft_charge']
    m = gto.M(atom=list(zip(S, X)), basis='def2-tzvp', charge=ch, spin=0, verbose=0)
    mf = dft.RKS(m).density_fit(auxbasis='def2-universal-jkfit'); mf.xc = 'wb97x-v'; mf.nlc = 'vv10'
    mf.grids.level = 2; mf.nlcgrids.level = 0; mf.conv_tol = 1e-9; mf.max_cycle = 150
    mf = qmmm.mm_charge(mf, d['pc_xyz'], d['pc_q_dft'])
    mf.kernel(); assert mf.converged, site
    dm = mf.make_rdm1()
    pts = []
    for k in (1.4, 1.6, 1.8, 2.0):
        for s, x in zip(S, X):
            for u in fib(120):
                p = x + u * VDW[s] * k
                if all(np.linalg.norm(p - y) >= VDW[t] * k - 1e-6 for t, y in zip(S, X)):
                    pts.append(p)
    pts = np.array(pts)
    fm = gto.fakemol_for_charges(pts / B2A)
    j3 = df.incore.aux_e2(m, fm)                       # (ij|p) = ∫ φi φj / |r − p|
    v_el = -np.einsum('ijp,ij->p', j3, dm)
    Z = m.atom_charges(); R = m.atom_coords()           # bohr
    v_nuc = np.sum(Z[None, :] / np.linalg.norm(pts[:, None, :] / B2A - R[None, :, :], axis=2), axis=1)
    V = v_el + v_nuc                                    # 조각만의 퍼텐셜(점전하 몫은 안 넣음) — hartree/e
    A = 1.0 / np.linalg.norm(pts[:, None, :] / B2A - R[None, :, :], axis=2)
    n = len(S)
    M = np.zeros((n + 1, n + 1)); M[:n, :n] = A.T @ A; M[:n, n] = 1; M[n, :n] = 1
    rhs = np.r_[A.T @ V, ch]
    q = np.linalg.solve(M, rhs)[:n]
    rrms = float(np.sqrt(np.mean((A @ q - V) ** 2)) / np.sqrt(np.mean(V ** 2)))
    out[site] = {'q_esp': [float(x) for x in q], 'sum': float(q.sum()), 'n_points': int(len(pts)), 'rrms_fit': rrms,
                 'q_ddec6_frag': None}
    print(f'{site:10s} 점 {len(pts)} · 적합 상대 rms {rrms:.3f} · 합 {q.sum():+.4f}', flush=True)
json.dump(out, open('results_e7b_esp_charges_hkhome.json', 'w', encoding='utf-8'), indent=1)
