# -*- coding: utf-8 -*-
"""HKHOME ⑤ — #5′ 셀 이완의 Br–O(Cl–O) 결합 인식 확인. 등록 `ASSIGN_ZNBDT_NO2_PLACEMENT_20261107.md` §7 추가(22:0x · 순찰 2) ⑤ ·
종합자 cloud.md 11-08 11:4x ④.

묻는 것: lammps-interface(UFF4MOF) 가 만든 위상에 할로젠–O 결합이 들어 있는가(기대: 할로젠 원자당 결합 1 = C–X).
읽는 것: `lmp_e24j_cr/<tag>/data.<tag>`(이완 입력 위상) 와 `min_<tag>.data`(이완 뒤 write_data) — 둘 다 Masses 주석에서 원소 · UFF 형을 읽고
Bonds 절에서 할로젠 원자마다 결합 수 · 상대 형을 셉니다. Bond Coeffs 주석에서 할로젠이 든 결합 형과 r0 도 적습니다.
이완 뒤 구조에서 각 할로젠–O 결합의 실제 거리(최소상 · 삼사정계 박스)도 적습니다(값은 기록 · 판정은 종합자).
산출 results_e24j_bondcheck_hkhome.json. RASPA · Zeo++ 안 씀(파일 읽기만).
"""
import collections
import hashlib
import json
import os
import socket

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
W = os.path.join(HERE, 'lmp_e24j_cr')
TAGS = {'e24j_br_ovl': 'Br', 'e24j_cl_ovl': 'Cl'}
OUT = os.path.join(HERE, f'results_e24j_bondcheck_{socket.gethostname().lower()}.json')


def md5(p):
    return hashlib.md5(open(p, 'rb').read()).hexdigest()


def sections(p):
    L = open(p).read().splitlines()
    head, sec, cur = [], {}, None
    names = {'Masses', 'Atoms', 'Bonds', 'Bond Coeffs', 'Velocities', 'Angles', 'Dihedrals', 'Impropers',
             'Pair Coeffs', 'Angle Coeffs', 'Dihedral Coeffs', 'Improper Coeffs', 'PairIJ Coeffs'}
    for ln in L:
        s = ln.split('#')[0].strip()
        key = ln.strip().split('#')[0].strip()
        if key in names:
            cur = key; sec[cur] = []; continue
        if cur is None:
            head.append(ln); continue
        if ln.strip():
            sec[cur].append(ln)
    return head, sec


def box(head):
    v = {}
    for ln in head:
        t = ln.split()
        if 'xlo' in ln: v['xlo'], v['xhi'] = float(t[0]), float(t[1])
        elif 'ylo' in ln: v['ylo'], v['yhi'] = float(t[0]), float(t[1])
        elif 'zlo' in ln: v['zlo'], v['zhi'] = float(t[0]), float(t[1])
        elif 'xy' in ln: v['xy'], v['xz'], v['yz'] = float(t[0]), float(t[1]), float(t[2])
    H = np.array([[v['xhi'] - v['xlo'], 0, 0], [v.get('xy', 0), v['yhi'] - v['ylo'], 0], [v.get('xz', 0), v.get('yz', 0), v['zhi'] - v['zlo']]])
    return H   # 행 = a, b, c


def check(p, X, ref=None):
    """ref = 입력 위상의 (형 → UFF 형 · 질량 · 결합 형 표). write_data 판은 Masses 주석 · Bond Coeffs 가 없어 같은 형 번호로 빌림(질량 대조)."""
    head, sec = sections(p)
    tlab, mass = {}, {}
    for ln in sec['Masses']:
        t = ln.split('#'); n = t[0].split()
        k = int(n[0]); mass[k] = float(n[1])
        tlab[k] = t[1].strip() if len(t) > 1 else '?'
    if ref is not None:
        assert all(abs(mass[k] - ref['mass'][k]) < 1e-3 for k in mass), '형 번호의 질량이 입력 위상과 다름'
        tlab = {k: (v if v != '?' else ref['tlab'][k]) for k, v in tlab.items()}
    elem = {k: ('Br' if v.startswith('Br') else 'Cl' if v.startswith('Cl') else v.split('_')[0].rstrip('0123456789')) for k, v in tlab.items()}
    atype, pos = {}, {}
    for ln in sec['Atoms']:
        t = ln.split('#')[0].split()
        i, ty = int(t[0]), int(t[2]); atype[i] = ty; pos[i] = np.array([float(t[4]), float(t[5]), float(t[6])])
    bcoef = {}
    for ln in sec.get('Bond Coeffs', []):
        t = ln.split('#'); n = t[0].split()
        bcoef[int(n[0])] = {'label': t[1].strip() if len(t) > 1 else '?', 'r0': float(n[-1])}
    if ref is not None and not bcoef:
        bcoef = dict(ref['bcoef'])
    H = box(head); Hi = np.linalg.inv(H)
    nb = collections.defaultdict(list); btype_of = {}
    for ln in sec['Bonds']:
        t = ln.split('#')[0].split()
        bt, a, b = int(t[1]), int(t[2]), int(t[3])
        nb[a].append((b, bt)); nb[b].append((a, bt))
    xs = [i for i in atype if elem[atype[i]] == X]
    per_atom = collections.Counter(); partners = collections.Counter(); xo = []
    for i in xs:
        per_atom[len(nb[i])] += 1
        for j, bt in nb[i]:
            pj = tlab[atype[j]]; partners[pj] += 1
            if elem[atype[j]] == 'O':
                d = pos[j] - pos[i]; f = d @ Hi; f -= np.round(f); r = float(np.linalg.norm(f @ H))
                xo.append({'X': i, 'O': j, 'O_type': pj, 'bond_type': bt, 'r0': bcoef.get(bt, {}).get('r0'), 'r_A': round(r, 4)})
    x_types = {k: v for k, v in bcoef.items() if X in v['label'].split()}
    return {'_ref': {'tlab': tlab, 'mass': mass, 'bcoef': bcoef}, 'labels_from_input_topology': ref is not None,
            'file': os.path.relpath(p, HERE), 'md5': md5(p), 'n_atoms': len(atype), 'n_bonds': len(sec['Bonds']),
            'n_X': len(xs), 'bonds_per_X_hist': dict(sorted(per_atom.items())), 'partner_types': dict(partners),
            'bond_types_with_X': {str(k): v for k, v in x_types.items()},
            'n_X_O_bonds': len(xo), 'X_O_bonds': xo[:64],
            'X_O_r_A_minmax': [min(b['r_A'] for b in xo), max(b['r_A'] for b in xo)] if xo else None}


def main():
    res = {'test': '#5′ 셀 이완 위상의 할로젠–O 결합 인식 확인(⑤)', 'assign': 'ASSIGN_ZNBDT_NO2_PLACEMENT_20261107.md §7 추가(22:0x) ⑤ · cloud.md 11-08 11:4x ④',
           'expect': '할로젠 원자당 결합 1(C–X) · 상대 형 C_R 만', 'machine': socket.gethostname().lower(), 'tags': {}}
    for tag, X in TAGS.items():
        d = os.path.join(W, tag)
        ci = check(os.path.join(d, f'data.{tag}'), X)
        ca = check(os.path.join(d, f'min_{tag}.data'), X, ref=ci['_ref'])
        ci.pop('_ref'); ca.pop('_ref')
        res['tags'][tag] = {'X': X, 'input_topology': ci, 'after_relax': ca}
    # 같은 계열(ZNBDT 할로젠) 다른 lammps-interface 위상 — CLAUDE §0 "한 곳에서 찾은 무늬는 같은 계열 전부에서". 입력 위상만 · 서술.
    # ZIF(lmp_aryl · lmp_v3* 등)는 넣지 않음: 이 검사기를 그 파일들에서 검증하지 않았음(Cl 결합 0 개 같은 읽기 이상이 보임).
    sib = {'lmp_e24g/e24g_br_100/data.e24g_br_100': 'Br', 'lmp_e24g/e24h_cl_050a/data.e24h_cl_050a': 'Cl',
           'lmp_e24g/e24h_cl_050b/data.e24h_cl_050b': 'Cl', 'lmp_e29b/e24c_cl_100/data.e24c_cl_100': 'Cl'}
    res['siblings_input_topology'] = {}
    for rp, X in sib.items():
        fp = os.path.join(HERE, rp)
        if os.path.exists(fp):
            c = check(fp, X); c.pop('_ref'); c['X_O_bonds'] = c['X_O_bonds'][:4]
            res['siblings_input_topology'][rp] = c
            print(f"[같은 계열] {rp} X {c['n_X']} · X 당 결합 수 {c['bonds_per_X_hist']} · X–O 결합 {c['n_X_O_bonds']} · md5 {c['md5'][:8]}")
    ok = all(os.path.exists(os.path.join(W, t, f'min_{t}.data')) for t in TAGS)
    res['status'] = 'ok' if ok else 'fail'; res['finished'] = True
    json.dump(res, open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    for tag, v in res['tags'].items():
        for k in ('input_topology', 'after_relax'):
            c = v[k]
            print(f"{tag} {k:15s} X {c['n_X']} · X 당 결합 수 {c['bonds_per_X_hist']} · 상대 형 {c['partner_types']} · X–O 결합 {c['n_X_O_bonds']} · md5 {c['md5'][:8]}")
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
