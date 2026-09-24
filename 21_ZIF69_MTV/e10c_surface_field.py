# -*- coding: utf-8 -*-
"""MAGI-005 E-10c — 접근면 전기장(“상쇄” 가설의 예측자). 분석 전용(RASPA 0). laptop(Melchior).

배정·등록: `ASSIGN_MAGI5B_20260925.md` §laptop 3차(07:16, 예측자 값 0건). 판정은 종합자.

[양]  전하 CIF(P1, `_atom_site_charge` = PACMAN DDEC6)와 기하만 씁니다.
    접근면 점  골격 원자 i 마다 반지름 R_i = σ_i/2 + 1.65 Å 구면 위 Fibonacci 점 N_SPH 개(원자당 ≥ 50).
               σ_i = UFF_MOF `force_field_mixing_rules.def` 의 `<원소>_` σ. 다른 원자 j(주기 영상 포함)에 대해 |p − r_j| < R_j 이면 버림(겹침).
    φ, E       그 점에서 골격 전하만의 Ewald 정전 퍼텐셜 φ(V)와 장 E = −∇φ(V/Å). 쿨롱 상수 14.399645 V·Å/e.
               k = 0 항 생략(순전하는 중화 배경 — φ 에 상수만 더함; σ_φ·|E| 무영향).
    P6 = 접근면 rms |E|(주) · P7 = 접근면 σ_φ · P8 = P6 × mean(|E| 상위 10 %)/mean(|E|)(국소 집중도).
[수렴] 두 설정 A(α 0.30 Å⁻¹, r_c 12 Å, k 꼬리 1e-8) · B(α 0.36 Å⁻¹, r_c 14 Å, k 꼬리 1e-10) — φ(평균 뺀 것)의 상대 rms 차 · P6·P7 상대차 < 1 % 를 기록.
       보고값은 B(더 엄격한 쪽). 1 % 를 넘는 구조는 `converged: false` 로 표지(값은 그대로 두고 판정에 쓰지 말 것).

사용:  czeromof/python e10c_surface_field.py [--workers 8] [--only name1,name2]
"""
import argparse, json, math, os, re, sys, time
import numpy as np
from scipy.spatial import cKDTree
from scipy.special import erfc

HERE = os.path.dirname(os.path.abspath(__file__))
KE = 14.399645            # e/(4πε0) [V·Å/e]
PROBE = 1.65              # Å — 배정문 σ/2 + 1.65
N_SPH = 60                # 원자당 구면 점(≥ 50) — 등록값(07:20). 표본 수렴은 아래 DENS 로 봄
DENS = [60, 240, 960, 3840, 15360]   # 07:3x 추가(G 대조 전): 초미세공에서 60점/원자는 남는 점 8~10개 → 4배씩 올려 연속 두 밀도의 P6·P7 변화 < 1 % 에서 멈춤(적응 규칙)
SETS = {'A': dict(alpha=0.30, rc=12.0, ktail=1e-8), 'B': dict(alpha=0.36, rc=14.0, ktail=1e-10)}
FF = os.path.join(os.environ.get('RASPA_DIR', os.path.expanduser('~/RASPA/simulations')),
                  'share', 'raspa', 'forcefield', 'UFF_MOF', 'force_field_mixing_rules.def')

CORE = ['2010_Zn__pts_3_ASR_1', '2012_Co__dia_3_ASR_3', '2022_Cd__nuc_3_FSR_1', '2024_Zn__lig_3_ASR_1',
        '2024_Zn__srs_3_ASR_1', '2020_Ag__pts_3_ASR_1', '2014_Cu__bcu_3_ASR_2', '2019_Zn__pcu_3_ASR_6',
        '2017_Zn__dia_3_FSR_1', '2018_Cd__dia_3_ASR_5', '2019_Zn__pcu_3_ASR_1', '2021_Co__dia_3_ASR_1']
OURS = ['saIm050_DDEC6', 'maf66', 'calf20', 'e4zif10', 'e4zif2', 'e4zif3', 'e4zif68', 'e4zif6', 'e4zif77', 'e4zif7', 'e4zif8', 'e4zif90']


def cif_path(name):
    if name in CORE:
        return os.path.join(HERE, 'core_pop_cifs', name + '.cif')
    return os.path.join(HERE, 'charged_v3', name if name.endswith('_DDEC6') else name + '_DDEC6') + '.cif'


def sigmas():
    s = {}
    for ln in open(FF, encoding='utf-8', errors='ignore'):
        m = re.match(r'^([A-Z][a-z]?)_\s+lennard-jones\s+([0-9.]+)\s+([0-9.]+)', ln)
        if m:
            s[m.group(1)] = float(m.group(3))
    return s


def read_p1_cif(path):
    """P1 CIF — 셀·원소·분율좌표·전하. 대칭 연산이 P1 이 아니면 거부."""
    txt = open(path, encoding='utf-8', errors='ignore').read()
    sg = re.search(r"_symmetry_space_group_name_H-M\s+['\"]?([^'\"\n]+)", txt)
    if sg and sg.group(1).replace(' ', '') not in ('P1',):
        raise ValueError(f'P1 아님: {sg.group(1)}')
    cp = {k: float(re.search(r'_cell_' + k + r'\s+([0-9.]+)', txt).group(1))
          for k in ('length_a', 'length_b', 'length_c', 'angle_alpha', 'angle_beta', 'angle_gamma')}
    lines = txt.splitlines(); cols, rows, inloop = [], [], False
    for ln in lines:
        s = ln.strip()
        if s == 'loop_':
            if cols and '_atom_site_fract_x' in cols and rows:
                break
            cols, rows, inloop = [], [], True; continue
        if inloop and s.startswith('_'):
            cols.append(s.split()[0]); continue
        if inloop and cols and '_atom_site_fract_x' in cols:
            if not s or s.startswith('_') or s.startswith('loop_'):
                if rows:
                    break
                continue
            rows.append(s.split())
    ix = {c: cols.index(c) for c in cols}
    el = [r[ix['_atom_site_type_symbol']] for r in rows]
    fr = np.array([[float(r[ix[f'_atom_site_fract_{a}']]) for a in 'xyz'] for r in rows])
    q = np.array([float(r[ix['_atom_site_charge']]) for r in rows])
    a, b, c = cp['length_a'], cp['length_b'], cp['length_c']
    al, be, ga = (math.radians(cp[k]) for k in ('angle_alpha', 'angle_beta', 'angle_gamma'))
    cx = c * math.cos(be); cy = c * (math.cos(al) - math.cos(be) * math.cos(ga)) / math.sin(ga)
    cell = np.array([[a, 0, 0], [b * math.cos(ga), b * math.sin(ga), 0], [cx, cy, math.sqrt(c * c - cx * cx - cy * cy)]])
    return cell, el, fr, q


def images(cell, reach):
    """reach(Å) 안을 덮는 격자 영상 정수 벡터."""
    V = abs(np.linalg.det(cell)); n = []
    for i in range(3):
        j, k = (i + 1) % 3, (i + 2) % 3
        w = V / np.linalg.norm(np.cross(cell[j], cell[k]))
        n.append(int(math.ceil(reach / w)))
    g = np.array([(i, j, k) for i in range(-n[0], n[0] + 1) for j in range(-n[1], n[1] + 1) for k in range(-n[2], n[2] + 1)])
    return g @ cell


def fib_sphere(n):
    i = np.arange(n) + 0.5
    phi = np.arccos(1 - 2 * i / n); th = math.pi * (1 + 5 ** 0.5) * i
    return np.c_[np.cos(th) * np.sin(phi), np.sin(th) * np.sin(phi), np.cos(phi)]


def surface_points(cell, r, R, nsph=N_SPH):
    """원자별 벡터화: 원자 i 의 구 점을 i 의 이웃(주기 영상 포함, 거리 < R_i + R_max) 과만 대조."""
    sph = fib_sphere(nsph)
    sh = images(cell, R.max() * 2 + 1.0)
    rimg = (r[None] + sh[:, None]).reshape(-1, 3); Rimg = np.tile(R, len(sh))
    tree = cKDTree(rimg)
    keepP, owner = [], []
    for i in range(len(r)):
        pts = r[i] + R[i] * sph
        nb = np.asarray(tree.query_ball_point(r[i], R[i] + R.max() + 1e-6))
        nb = nb[np.linalg.norm(rimg[nb] - r[i], axis=1) > 1e-6]            # 자기 자신 제외
        if len(nb):
            d = np.linalg.norm(pts[:, None, :] - rimg[nb][None], axis=2)
            ok = ~(d < Rimg[nb][None] - 1e-6).any(1)
        else:
            ok = np.ones(len(pts), bool)
        keepP.append(pts[ok]); owner.append(np.full(ok.sum(), i))
    return np.vstack(keepP), np.concatenate(owner)


def ewald(cell, r, q, P, alpha, rc, ktail):
    V = abs(np.linalg.det(cell))
    # 역격자
    B = 2 * math.pi * np.linalg.inv(cell).T
    kmax = math.sqrt(-4 * alpha * alpha * math.log(ktail))
    nk = [int(math.ceil(kmax / np.linalg.norm(B[i]))) + 1 for i in range(3)]
    hkl = np.array([(h, k, l) for h in range(0, nk[0] + 1) for k in range(-nk[1], nk[1] + 1) for l in range(-nk[2], nk[2] + 1)
                    if (h > 0) or (h == 0 and k > 0) or (h == 0 and k == 0 and l > 0)])
    kv = hkl @ B; k2 = (kv ** 2).sum(1); m = (k2 > 0) & (k2 <= kmax * kmax); kv, k2 = kv[m], k2[m]
    f = 2.0 * np.exp(-k2 / (4 * alpha * alpha)) / k2 * (4 * math.pi / V)          # 반쪽 k 에 ×2
    S = (q[None, :] * np.exp(1j * (kv @ r.T))).sum(1)                                # 구조 인자
    phi = np.zeros(len(P)); E = np.zeros((len(P), 3))
    for s in range(0, len(P), 512):
        ph = np.exp(-1j * (P[s:s + 512] @ kv.T)) * S[None, :]
        phi[s:s + 512] += (ph.real * f[None]).sum(1)
        E[s:s + 512] += -(ph.imag * f[None]) @ kv
    # 실공간
    sh = images(cell, rc)
    rimg = (r[None] + sh[:, None]).reshape(-1, 3); qimg = np.tile(q, len(sh))
    tree = cKDTree(rimg)
    for s in range(0, len(P), 2048):
        idx = tree.query_ball_point(P[s:s + 2048], rc)
        for t, lst in enumerate(idx):
            lst = np.asarray(lst)
            d = P[s + t] - rimg[lst]; rr = np.linalg.norm(d, axis=1); qq = qimg[lst]
            phi[s + t] += (qq * erfc(alpha * rr) / rr).sum()
            g = qq * (erfc(alpha * rr) / rr ** 2 + 2 * alpha / math.sqrt(math.pi) * np.exp(-(alpha * rr) ** 2) / rr) / rr
            E[s + t] += (g[:, None] * d).sum(0)
    return KE * phi, KE * E, len(kv), len(rimg)


def props(phi, E):
    e = np.linalg.norm(E, axis=1)
    top = np.sort(e)[-max(1, int(round(0.1 * len(e)))):]
    P6 = float(np.sqrt((e ** 2).mean())); P7 = float(phi.std())
    return {'P6_rms_E_V_per_A': P6, 'P7_sigma_phi_V': P7, 'P8': float(P6 * top.mean() / e.mean()),
            'mean_E': float(e.mean()), 'top10_mean_E': float(top.mean())}


def one(name):
    t0 = time.time()
    try:
        cell, el, fr, q = read_p1_cif(cif_path(name))
        sg = sigmas()
        miss = sorted({x for x in el if x not in sg})
        if miss:
            return {'name': name, 'status': f'σ 없음 {miss}'}
        r = fr @ cell; R = np.array([sg[x] / 2 + PROBE for x in el])
        dens, used = {}, []
        for nd in DENS:                                                    # 표본 수렴(적응) — Ewald 는 보고 설정 B
            Pd, _ = surface_points(cell, r, R, nd)
            if len(Pd) == 0:
                dens[nd] = {'n_points': 0}; used.append(nd); continue
            phd, Ed, _, _ = ewald(cell, r, q, Pd, **SETS['B'])
            dens[nd] = {'n_points': int(len(Pd)), **props(phd, Ed)}; used.append(nd)
            if len(used) >= 2 and nd >= 240:
                a_, b_ = dens[used[-2]], dens[used[-1]]
                if a_.get('P6_rms_E_V_per_A') and abs(a_['P6_rms_E_V_per_A'] / b_['P6_rms_E_V_per_A'] - 1) < 0.01 \
                        and abs(a_['P7_sigma_phi_V'] / b_['P7_sigma_phi_V'] - 1) < 0.01:
                    break
        P, own = surface_points(cell, r, R, used[-1])
        out = {'name': name, 'cif': os.path.relpath(cif_path(name), HERE), 'n_atoms': len(el), 'n_points': int(len(P)),
               'points_per_atom_kept': round(len(P) / len(el), 2), 'points_per_atom_generated': used[-1], 'net_charge_e': float(q.sum()), 'sets': {},
               'by_density': {str(k): v for k, v in dens.items()}}
        p6a, p6b = dens[used[-2]].get('P6_rms_E_V_per_A'), dens[used[-1]].get('P6_rms_E_V_per_A')
        p7a, p7b = dens[used[-2]].get('P7_sigma_phi_V'), dens[used[-1]].get('P7_sigma_phi_V')
        out['sampling_rel_dP6'] = (abs(p6a / p6b - 1) if p6a and p6b else None)
        out['sampling_rel_dP7'] = (abs(p7a / p7b - 1) if p7a and p7b else None)
        out['sampling_converged'] = bool(out['sampling_rel_dP6'] is not None and out['sampling_rel_dP6'] < 0.01 and out['sampling_rel_dP7'] < 0.01)
        res = {}
        for k, st in SETS.items():
            phi, E, nk, nimg = ewald(cell, r, q, P, **st)
            res[k] = (phi, E); out['sets'][k] = {**st, 'n_kvec_half': nk, 'n_real_images_atoms': nimg, **props(phi, E)}
        pa, pb = res['A'][0] - res['A'][0].mean(), res['B'][0] - res['B'][0].mean()
        dphi = float(np.sqrt(((pa - pb) ** 2).mean()) / pb.std())
        dP6 = abs(out['sets']['A']['P6_rms_E_V_per_A'] / out['sets']['B']['P6_rms_E_V_per_A'] - 1)
        dP7 = abs(out['sets']['A']['P7_sigma_phi_V'] / out['sets']['B']['P7_sigma_phi_V'] - 1)
        out.update({'conv_rel_rms_dphi': dphi, 'conv_rel_dP6': dP6, 'conv_rel_dP7': dP7,
                    'converged': bool(dphi < 0.01 and dP6 < 0.01 and dP7 < 0.01), **props(*res['B']),
                    'report_set': 'B', 'seconds': round(time.time() - t0, 1), 'status': 'ok'})
        return out
    except Exception as ex:
        return {'name': name, 'status': f'실패: {type(ex).__name__}: {ex}', 'seconds': round(time.time() - t0, 1)}


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--workers', type=int, default=8); ap.add_argument('--only', default='')
    ap.add_argument('--out', default=os.path.join(HERE, 'e10c_surface_field.json'))
    a = ap.parse_args()
    names = [x for x in (a.only.split(',') if a.only else CORE + OURS) if x]
    from concurrent.futures import ProcessPoolExecutor, as_completed
    rows = {}
    if os.path.exists(a.out) and not a.only:
        rows = {r['name']: r for r in json.load(open(a.out, encoding='utf-8')).get('rows', []) if r.get('status') == 'ok'}
    todo = [n for n in names if n not in rows]
    print(f'E-10c 접근면 전기장 — {len(todo)}구조 (워커 {a.workers}) · 탐침 {PROBE} Å · 원자당 {N_SPH}점 · 설정 {SETS}', flush=True)
    with ProcessPoolExecutor(max_workers=a.workers) as ex:
        futs = {ex.submit(one, n): n for n in todo}
        for fu in as_completed(futs):
            r = fu.result(); rows[r['name']] = r
            print(f"  [{r['status'][:40]}] {r['name']:24s} 점 {r.get('n_points')} · P6 {r.get('P6_rms_E_V_per_A')} · 표본 dP6 {r.get('sampling_rel_dP6')} · "
                  f"수렴 dφ {r.get('conv_rel_rms_dphi')} dP6 {r.get('conv_rel_dP6')} · {r.get('seconds')} s", flush=True)
            json.dump({'test': 'MAGI-005 E-10c 접근면 전기장', 'assign': 'ASSIGN_MAGI5B_20260925.md §laptop 3차',
                       'method': {'probe_A': PROBE, 'densities': DENS, 'sampling_rule': '4배씩 올려 연속 두 밀도(≥240)의 P6·P7 변화 < 1 % 에서 멈춤 → sampling_converged; 상한 15360 에서도 넘으면 false', 'sigma_source': FF, 'sets': SETS,
                                  'coulomb_V_A': KE, 'k0': '생략(중화 배경)', 'report_set': 'B',
                                  'converged_rule': 'dφ(평균 뺀 rms/σ_φ)·dP6·dP7 모두 < 1 %'},
                       'note': '판정 없음(종합자). 골격 DDEC6 전하만. 값은 G 와 맞추기 전에 구현 세부를 우편함에 적은 뒤 계산.',
                       'rows': [rows[k] for k in sorted(rows)]}, open(a.out, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('저장', a.out, flush=True)


if __name__ == '__main__':
    sys.exit(main())
