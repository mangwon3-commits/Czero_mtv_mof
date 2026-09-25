# -*- coding: utf-8 -*-
"""E-22d — 전하 비교(A 대 B, 같은 기하) + D 꼭짓점 CIF 만들기(이완 기하 + CoRE 전하).
등록 ASSIGN_MAGI5B §HKHOME 9차. 짝은 같은 원소 최근접(주기 경계, 순서 무관 — relax_tnf 가 순서를 바꿈, E-22a)."""
import json, math, os, re, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
A = os.path.join(HERE, 'core_pop_cifs/2017_Zn__dia_3_ASR_1.cif')        # CoRE 기하 + CoRE 전하
B = os.path.join(HERE, 'charged_v3/e22d_coregeom_DDEC6.cif')            # CoRE 기하 + 우리 PACMAN
C = os.path.join(HERE, 'charged_v3/e22_parent_DDEC6.cif')               # 이완 기하 + 우리 PACMAN
D = os.path.join(HERE, 'charged_v3/e22d_relaxgeom_coreq_DDEC6.cif')     # 이완 기하 + CoRE 전하(만듦)
OUT = os.path.join(HERE, 'results_e22d_charges_hkhome.json')


def read(path):
    cell = {}; atoms = []; cols = []; inloop = False
    for ln in open(path, encoding='utf-8'):
        s = ln.strip()
        m = re.match(r'_cell_(length_[abc]|angle_(alpha|beta|gamma))\s+([\d.]+)', s)
        if m: cell[m.group(1)] = float(m.group(3)); continue
        if s == 'loop_': cols = []; inloop = True; continue
        if inloop and s.startswith('_atom_site'): cols.append(s); continue
        if cols and '_atom_site_fract_x' in cols and s and not s.startswith('_') and not s.startswith('#'):
            p = s.split()
            if len(p) < len(cols): continue
            g = dict(zip(cols, p))
            atoms.append((g['_atom_site_type_symbol'], [float(g['_atom_site_fract_' + k]) for k in 'xyz'],
                          float(g['_atom_site_charge'])))
        elif s.startswith('_') or not s: inloop = inloop and s.startswith('_')
    a, b, c = (cell['length_' + k] for k in 'abc')
    al, be, ga = (math.radians(cell['angle_' + k]) for k in ('alpha', 'beta', 'gamma'))
    cx = math.cos(be); cy = (math.cos(al) - math.cos(be) * math.cos(ga)) / math.sin(ga)
    M = np.array([[a, 0, 0], [b * math.cos(ga), b * math.sin(ga), 0], [c * cx, c * cy, c * math.sqrt(1 - cx * cx - cy * cy)]])
    return atoms, M


def pair(src, dst, M):
    """dst 각 원자에 src 의 같은 원소 최근접(주기). 반환: [(i_src, 거리)], 일대일 여부."""
    out = []
    for el, f, _ in dst:
        best = (None, 1e9)
        for i, (e2, f2, _) in enumerate(src):
            if e2 != el: continue
            d = np.array(f) - np.array(f2); d -= np.round(d)
            r = float(np.linalg.norm(d @ M))
            if r < best[1]: best = (i, r)
        out.append(best)
    idx = [i for i, _ in out]
    return out, len(set(idx)) == len(idx) == len(src)


def main():
    at_a, M = read(A); at_b, Mb = read(B); at_c, Mc = read(C)
    res = {'test': 'E-22d', 'registration': 'ASSIGN_MAGI5B_20260925.md §HKHOME 9차',
           'pacman_A_header': open(A).readline().strip(), 'pacman_B': 'pip PACMAN-charge 1.4.2 (charge_tnf.py)'}
    # (1) A 대 B — 같은 기하
    pr, one = pair(at_a, at_b, M)
    dq = [(at_b[j][0], at_b[j][2] - at_a[i][2], r) for j, (i, r) in enumerate(pr)]
    by = {}
    for el, d, _ in dq: by.setdefault(el, []).append(d)
    res['AB'] = {'n': len(dq), 'one_to_one': one, 'max_pair_dist': max(r for *_, r in dq),
                 'max_abs_dq': max(abs(d) for _, d, _ in dq),
                 'by_element': {el: {'n': len(v), 'mean_abs_dq': float(np.mean(np.abs(v))), 'mean_dq': float(np.mean(v)),
                                     'max_abs_dq': float(np.max(np.abs(v))),
                                     'q_A_mean': float(np.mean([at_a[i][2] for (i, _), (e, *_ ) in zip(pr, at_b) if e == el])),
                                     'q_B_mean': float(np.mean([at_b[j][2] for j, (e, *_ ) in enumerate(at_b) if e == el]))}
                                for el, v in sorted(by.items())}}
    res['AB']['pred1_max_ok'] = res['AB']['max_abs_dq'] <= 0.05
    res['AB']['pred1_elem_ok'] = all(v['mean_abs_dq'] <= 0.02 for v in res['AB']['by_element'].values())
    # D — 이완 기하(C 의 좌표) 에 CoRE 전하(A) 를 옮김
    pc, one_c = pair(at_a, at_c, Mc)
    maxd = max(r for _, r in pc)
    qD = [at_a[i][2] for i, _ in pc]
    netA = sum(q for *_, q in at_a); netD = sum(qD)
    gate = {'one_to_one': one_c, 'max_pair_dist': maxd, 'net_A': netA, 'net_D': netD,
            'ok': one_c and maxd <= 0.5 and abs(netD - netA) < 1e-6}
    res['D_gate'] = gate
    if gate['ok']:
        lines = open(C, encoding='utf-8').read().splitlines(); k = 0; out = []
        for ln in lines:
            p = ln.split()
            if k < len(at_c) and len(p) == 8 and p[0] == at_c[k][0] and re.match(r'^-?\d', p[-1]):
                p[-1] = f'{qD[k]:.9f}'; ln = '  '.join(p); k += 1
            out.append(ln)
        assert k == len(at_c), (k, len(at_c))
        out[0] = '# E-22d D: geometry relax_tnf/e22_parent (GFN-FF) + charges from core_pop_cifs/2017_Zn__dia_3_ASR_1.cif (CoRE PACMAN v1.1), nearest same-element map'
        out = [re.sub(r'^data_\S+', 'data_e22d_relaxgeom_coreq_DDEC6', l) for l in out]
        open(D, 'w', encoding='utf-8').write('\n'.join(out) + '\n')
        chk, _ = read(D)
        gate['written'] = D; gate['net_written'] = sum(q for *_, q in chk)
    json.dump(res, open(OUT, 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
    print(json.dumps(res, indent=1, ensure_ascii=False))


if __name__ == '__main__':
    main()
