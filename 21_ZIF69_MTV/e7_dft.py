# -*- coding: utf-8 -*-
"""E-7 DFT 단일점(균형보정) — dft 환경(pyscf). 입력 e7_poses.json(e7_build.py 산출). 등록 E7_DFT_WATER_REGISTRATION_20260925.md.
ωB97X-V(VV10) · 밀도 맞춤(def2-universal-jkfit) · 자세 거르기 def2-SVP → 최종 def2-TZVP(§2 고정)."""
import json, os, sys, time
from pyscf import gto, dft, lib, qmmm
HA2KJ = 2625.4996
lib.num_threads(int(os.environ.get('E7_THREADS', '8')))


def energy(sym, xyz, ghost, basis, charge=0, pc=None):
    energy.cycles = getattr(energy, 'cycles', [])
    atoms = [(('ghost-' + s) if i in ghost else s, x) for i, (s, x) in enumerate(zip(sym, xyz))]
    real_e = sum(gto.charge(s) for i, s in enumerate(sym) if i not in ghost) - charge
    spin = real_e % 2
    if spin and os.environ.get('E7_ALLOW_OPEN_SHELL') != '1':
        # 09-25: 홀수 전자를 조용히 UKS 라디칼로 돌린 결함(전 조각) — 이제 거부한다. 총전하를 고쳐서 부를 것.
        raise ValueError(f'홀수 전자 {real_e} (charge {charge}) — 라디칼 조각 거부')
    m = gto.M(atom=atoms, basis=basis, charge=charge if not ghost else charge, spin=spin, verbose=0)
    mf = (dft.UKS(m) if spin else dft.RKS(m)).density_fit(auxbasis='def2-universal-jkfit')
    mf.xc = 'wb97x-v'; mf.nlc = 'vv10'; mf.conv_tol = 1e-8
    if pc and len(pc[0]):
        mf = qmmm.mm_charge(mf, pc[0], pc[1])    # Zn 자리 점전하 매립(세 계산 모두 같은 장)
    mf.grids.level = int(os.environ.get('E7_GRID', '2')); mf.nlcgrids.level = int(os.environ.get('E7_NLCGRID', '0'))   # 물 이합체에서 기본(3/1)과 결합에너지 차 < 0.01 kJ/mol, 9배 빠름(09-25 실측)
    cyc = []
    mf.callback = lambda env: cyc.append(env.get('cycle'))
    mf.max_cycle = 100
    e = mf.kernel()
    if not mf.converged:                      # 09-25 MAF-66 조각(S5)이 50회 안에 못 수렴 → 2차 수렴법으로 이어 풂(같은 범함수·격자)
        dm = mf.make_rdm1()
        mf = mf.newton(); e = mf.kernel(dm0=dm)
        cyc.append('newton')
    energy.cycles.append(len(cyc))
    return e, mf.converged


def cp_bind(frag_sym, frag_xyz, wat_xyz, basis, charge=0, pc=None):
    sym = list(frag_sym) + ['O', 'H', 'H']; xyz = list(frag_xyz) + list(wat_xyz)
    nf = len(frag_sym); wi = set(range(nf, nf + 3)); fi = set(range(nf))
    eab, c1 = energy(sym, xyz, set(), basis, charge, pc)
    ea, c2 = energy(sym, xyz, wi, basis, charge, pc)       # 조각 + 물 유령
    eb, c3 = energy(sym, xyz, fi, basis, 0, pc)            # 물 + 조각 유령
    return (eab - ea - eb) * HA2KJ, (c1 and c2 and c3)


if __name__ == '__main__':
    P = json.load(open('e7_poses.json', encoding='utf-8'))
    site = sys.argv[1]; pose = sys.argv[2]; basis = sys.argv[3] if len(sys.argv) > 3 else 'def2-svp'
    d = P[site]; r = [x for x in d['poses'] if x['pose'] == pose][0]
    t = time.time()
    e, conv = cp_bind(d['frag_symbols'], d['frag_xyz'], r['water'], basis, d.get('dft_charge', 0))
    print(json.dumps({'site': site, 'pose': pose, 'basis': basis, 'E_dft': round(e, 3), 'E_ff': r['E_ff'], 'converged': conv,
                      'seconds': round(time.time() - t, 1), 'scf_cycles': energy.cycles}, ensure_ascii=False), flush=True)
