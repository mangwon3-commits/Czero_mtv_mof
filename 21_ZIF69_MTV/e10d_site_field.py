# -*- coding: utf-8 -*-
"""MAGI-005 E-10d — 흡착 자리 가중 전기장. 분석 전용(RASPA 0). laptop(Melchior).

배정·등록: `ASSIGN_MAGI5B_20260925.md` §laptop 4차(07:30, 예측자 값 0건). ρ 는 계산하지 않음(판정 종합자).

[점]   E-10c 와 **같은 점** — `e10c_surface_field.py` 를 import 해 같은 CIF·같은 σ·같은 접근면 규칙(R_i = σ_i/2 + 1.65 Å)·
       구조별 적응 밀도(`e10c_surface_field.json` 의 points_per_atom_generated)로 다시 만든다(결정적 Fibonacci — 같은 점).
[E]    Ewald 설정 B(α 0.36 · r_c 14 · k 꼬리 1e-10) — E-10c 보고값과 같은 장.
[U_LJ] 탐침 = CO₂ 의 O 자리 하나(`O_co2` ε 85.671 K · σ 3.017 Å). 골격 원자 j 는 `<원소>_` UFF 값(E-10c 와 같은 대응).
       Lorentz-Berthelot(ε_ij = √(ε_O ε_j), σ_ij = (σ_O + σ_j)/2) · 12 Å 절단 · **shifted**(절단에서 0) · 꼬리 보정 없음 — force_field_mixing_rules.def 머리말과 같음.
       주기 영상 포함. 겹침 점: 접근면 규칙이 이미 |p − r_j| ≥ R_j 인 점만 남기므로 따로 버리지 않음(U 가 양수여도 w 가 작게 들어갈 뿐).
[양]   w = exp(−U_LJ / 298 K)(수치 안정을 위해 최소 U 로 이동 — 비는 불변).
       **P9 = √(Σ w|E|² / Σ w)** · P10 = P9 / P6(E-10c 의 P6).
[기록용 표지 — 규칙 아님]  ESS = (Σw)²/Σw²(가중이 몇 점에 몰렸나) · 한 단계 낮은 밀도에서의 P9 와의 상대차(P9 표본 수렴 확인).
"""
import json, math, os, sys, time
import numpy as np
from scipy.spatial import cKDTree

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import e10c_surface_field as C   # noqa: E402

T = 298.0
O_EPS, O_SIG = 85.671, 3.017
RC = 12.0


def lj_params():
    eps, sig = {}, {}
    import re
    for ln in open(C.FF, encoding='utf-8', errors='ignore'):
        m = re.match(r'^([A-Z][a-z]?)_\s+lennard-jones\s+([0-9.]+)\s+([0-9.]+)', ln)
        if m:
            eps[m.group(1)] = float(m.group(2)); sig[m.group(1)] = float(m.group(3))
    return eps, sig


def lj_energy(cell, r, el, P, eps, sig):
    sh = C.images(cell, RC)
    rimg = (r[None] + sh[:, None]).reshape(-1, 3)
    e_j = np.tile(np.array([math.sqrt(O_EPS * eps[x]) for x in el]), len(sh))
    s_j = np.tile(np.array([(O_SIG + sig[x]) / 2 for x in el]), len(sh))
    tree = cKDTree(rimg); U = np.zeros(len(P))
    for s in range(0, len(P), 2048):
        idx = tree.query_ball_point(P[s:s + 2048], RC)
        for t, lst in enumerate(idx):
            lst = np.asarray(lst, dtype=int)
            if lst.size == 0:
                continue                                  # 12 Å 안에 원자 없음 → U = 0
            rr = np.linalg.norm(P[s + t] - rimg[lst], axis=1); ee, ss = e_j[lst], s_j[lst]
            x6 = (ss / rr) ** 6; xc6 = (ss / RC) ** 6
            U[s + t] = (4 * ee * (x6 * x6 - x6) - 4 * ee * (xc6 * xc6 - xc6)).sum()
    return U   # K


def site_props(U, E):
    e2 = (E ** 2).sum(1)
    a = -(U - U.min()) / T; w = np.exp(a)
    P9 = math.sqrt((w * e2).sum() / w.sum())
    ess = w.sum() ** 2 / (w ** 2).sum()
    return P9, ess, w


def one(name, dens_used, dens_prev, P6):
    t0 = time.time()
    try:
        cell, el, fr, q = C.read_p1_cif(C.cif_path(name)); r = fr @ cell
        eps, sig = lj_params(); R = np.array([sig[x] / 2 + C.PROBE for x in el])
        out = {'name': name, 'dens_used': dens_used, 'P6_e10c': P6}
        for tag, nd in (('main', dens_used), ('prev', dens_prev)):
            if nd is None:
                continue
            P, _ = C.surface_points(cell, r, R, nd)
            _, E, _, _ = C.ewald(cell, r, q, P, **C.SETS['B'])
            U = lj_energy(cell, r, el, P, eps, sig)
            P9, ess, w = site_props(U, E)
            e = np.linalg.norm(E, axis=1)
            rec = {'dens': nd, 'n_points': int(len(P)), 'P9_V_per_A': P9, 'ESS': float(ess), 'ESS_frac': float(ess / len(P)),
                   'U_min_K': float(U.min()), 'U_median_K': float(np.median(U)),
                   'P6_check': float(np.sqrt((e ** 2).mean()))}
            out[tag] = rec
        m = out['main']
        out.update({'P9_V_per_A': m['P9_V_per_A'], 'P10': m['P9_V_per_A'] / P6, 'ESS': m['ESS'], 'n_points': m['n_points'],
                    'P6_reproduced_rel': abs(m['P6_check'] / P6 - 1),
                    'P9_sampling_rel_vs_prev': (abs(out['prev']['P9_V_per_A'] / m['P9_V_per_A'] - 1) if 'prev' in out else None),
                    'seconds': round(time.time() - t0, 1), 'status': 'ok'})
        return out
    except Exception as ex:
        return {'name': name, 'status': f'실패: {type(ex).__name__}: {ex}'}


def main():
    src = json.load(open(os.path.join(HERE, 'e10c_surface_field.json'), encoding='utf-8'))
    jobs = []
    for r in src['rows']:
        used = r['points_per_atom_generated']
        dl = [int(k) for k in r['by_density']]; dl.sort()
        prev = dl[dl.index(used) - 1] if dl.index(used) > 0 else None
        jobs.append((r['name'], used, prev, r['P6_rms_E_V_per_A']))
    from concurrent.futures import ProcessPoolExecutor, as_completed
    rows = {}
    print(f'E-10d 흡착 자리 가중 장 — {len(jobs)}구조 · 탐침 O_co2 · LB · 12 Å shifted · T {T} K', flush=True)
    with ProcessPoolExecutor(max_workers=8) as ex:
        futs = {ex.submit(one, *j): j[0] for j in jobs}
        for fu in as_completed(futs):
            r = fu.result(); rows[r['name']] = r
            print(f"  [{r['status'][:30]}] {r['name']:24s} P9 {r.get('P9_V_per_A')} · P10 {r.get('P10')} · ESS {r.get('ESS')} · "
                  f"P6 재현 {r.get('P6_reproduced_rel')} · P9 표본 {r.get('P9_sampling_rel_vs_prev')} · {r.get('seconds')} s", flush=True)
    json.dump({'test': 'MAGI-005 E-10d 흡착 자리 가중 전기장', 'assign': 'ASSIGN_MAGI5B_20260925.md §laptop 4차',
               'method': {'points': 'E-10c 적응판과 같은 점(구조별 dens_used)', 'field': 'Ewald 설정 B', 'probe': {'site': 'O_co2', 'eps_K': O_EPS, 'sigma_A': O_SIG},
                          'mixing': 'Lorentz-Berthelot', 'cutoff_A': RC, 'shifted': True, 'tail': False, 'T_K': T,
                          'P9': 'sqrt(Σw|E|²/Σw), w = exp(-U_LJ/T)', 'P10': 'P9/P6'},
               'note': 'ρ 는 계산하지 않음(판정 종합자). ESS·P9_sampling_rel_vs_prev 는 기록용 표지.',
               'rows': [rows[k] for k in sorted(rows)]}, open(os.path.join(HERE, 'e10d_site_field.json'), 'w', encoding='utf-8'),
              ensure_ascii=False, indent=1)
    print('저장 e10d_site_field.json', flush=True)


if __name__ == '__main__':
    sys.exit(main())
