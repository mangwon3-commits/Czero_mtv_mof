# -*- coding: utf-8 -*-
"""ZNBDT-C2 — 무극성 −CN 계산 대조: 열린 자리 −CN 구조(e24i_cn_open)의 **니트릴 C · N 전하만 0** 으로 둔 CIF 두 판.
등록 `ASSIGN_ZNBDT_C2_20261105.md` §1(자료 0건). 기하 · 원자 순서 · 다른 열은 원판과 바이트 단위로 같고 전하 열만 바뀝니다.
  U판(주판)  니트릴 C · N 전하 0, 빠진 전하 합을 나머지 원자 전체에 같은 몫으로 나눠 순전하를 원판과 같게
  I판(민감도) 니트릴 C · N 전하 0, 빠진 전하 합을 각 니트릴의 고리 ipso C 에 얹음(Ar–C≡N 단위 전하 보존, C≡N 쌍극자만 제거)
니트릴 원자는 위상으로 찾습니다: N–C < 1.2 Å 이고 N 의 이웃이 그 C 하나뿐인 짝. 셀당 넷이어야 합니다(assert).
실행: czeromof 파이썬 — `python build_znbdt_c2_apolar.py` (21_ZIF69_MTV 에서)
"""
import hashlib, json, os, sys
import numpy as np
from ase.io import read
from ase.neighborlist import neighbor_list

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, 'charged_v3', 'e24i_cn_open_DDEC6.cif')
OUT = {'U': os.path.join(HERE, 'charged_v3', 'znbdt_c2_apolarU_DDEC6mod.cif'),
       'I': os.path.join(HERE, 'charged_v3', 'znbdt_c2_apolarI_DDEC6mod.cif')}
REC = os.path.join(HERE, 'results_znbdt_c2_build_hkhome.json')


def atom_rows(lines):
    """_atom_site_ 루프의 (머리 열 목록, 자료 줄 번호 목록) — run_magi5_widom.zero_charge_copy 와 같은 판별."""
    hdr, idx, inl = [], [], False
    for k, l in enumerate(lines):
        s = l.strip()
        if s.startswith('_atom_site_'):
            inl = True; hdr.append(s); continue
        if inl and s and not s.startswith('_') and not s.startswith('loop_') and len(s.split()) >= len(hdr):
            idx.append(k); continue
        if inl and (s.startswith('loop_') or s == ''):
            inl = False
    return hdr, idx


def main():
    raw = open(SRC, encoding='utf-8').read()
    lines = raw.splitlines()
    hdr, idx = atom_rows(lines)
    qc = hdr.index('_atom_site_charge')
    q0 = np.array([float(lines[k].split()[qc]) for k in idx])
    a = read(SRC); s = a.get_chemical_symbols()
    assert len(a) == len(idx) == 208, (len(a), len(idx))
    i, j, d = neighbor_list('ijd', a, 1.75)
    nb = {k: set() for k in range(len(a))}
    for x, y, dd in zip(i, j, d):
        if dd < (1.2 if 'N' in (s[x], s[y]) and 'C' in (s[x], s[y]) else 1.6):
            nb[x].add(y)
    pairs = []
    for n_ in range(len(a)):
        if s[n_] != 'N': continue
        cs = [c for c in nb[n_] if s[c] == 'C' and a.get_distance(n_, c, mic=True) < 1.2]
        if len(cs) == 1 and len(nb[n_]) == 1:
            c_ = cs[0]; ipso = [y for y in nb[c_] if y != n_ and s[y] == 'C']
            assert len(ipso) == 1, (n_, c_, ipso)
            pairs.append((n_, c_, ipso[0]))
    assert len(pairs) == 4, pairs
    removed = sum(q0[n] + q0[c] for n, c, _ in pairs)
    nit = {x for n, c, _ in pairs for x in (n, c)}
    rec = {'test': 'ZNBDT-C2 무극성 −CN 전하 판 만들기', 'assign': 'ASSIGN_ZNBDT_C2_20261105.md §1',
           'src': os.path.relpath(SRC, HERE), 'src_md5': hashlib.md5(raw.encode()).hexdigest(),
           'net_charge_src': float(q0.sum()), 'removed_sum_e': float(removed),
           'nitrile': [{'N': int(n), 'C': int(c), 'ipso': int(p), 'qN': float(q0[n]), 'qC': float(q0[c]), 'q_ipso': float(q0[p])}
                       for n, c, p in pairs], 'variants': {}}
    for v, path in OUT.items():
        q = q0.copy()
        for x in nit: q[x] = 0.0
        if v == 'U':
            rest = [k for k in range(len(a)) if k not in nit]
            q[rest] += removed / len(rest)
            note = f'나머지 {len(rest)} 원자에 {removed / len(rest):+.6f} e 씩'
        else:
            for n, c, p in pairs: q[p] += q0[n] + q0[c]
            note = 'ipso C 마다 그 니트릴의 (qN+qC)'
        new = list(lines)
        for k, row in enumerate(idx):
            parts = new[row].split(); parts[qc] = f'{q[k]:.6f}'; new[row] = ' '.join(parts)
        body = '\n'.join(new) + '\n'   # 머리 주석은 넣지 않음(RASPA CIF 파서 미확인) — 출처는 결과 JSON 에
        open(path, 'w', encoding='utf-8').write(body)
        b = read(path)
        assert np.allclose(b.get_positions(), a.get_positions(), atol=1e-6) and b.get_chemical_symbols() == s
        qw = np.array([float(body.splitlines()[k].split()[qc]) for k in idx])
        rec['variants'][v] = {'cif': os.path.relpath(path, HERE), 'md5': hashlib.md5(body.encode()).hexdigest(), 'rule': note,
                              'net_charge_written': float(qw.sum()), 'net_ok_1e-3': bool(abs(qw.sum()) <= 1e-3),
                              'max_change_non_nitrile': float(max(abs(qw[k] - q0[k]) for k in range(len(a)) if k not in nit)),
                              'n_changed': int(sum(abs(qw[k] - q0[k]) > 5e-7 for k in range(len(a))))}
        r = rec['variants'][v]
        print(f"{v}판 {r['cif']} · 순전하 {r['net_charge_written']:+.6f} ({'통과' if r['net_ok_1e-3'] else '탈락'}) · 바뀐 원자 {r['n_changed']} · 니트릴 밖 최대 변화 {r['max_change_non_nitrile']:.4f} e")
    print(f"원판 순전하 {rec['net_charge_src']:+.6f} · 빠진 니트릴 전하 합 {removed:+.4f} e (셀당 {len(pairs)} 짝)")
    json.dump(rec, open(REC, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    return 0 if all(v['net_ok_1e-3'] for v in rec['variants'].values()) else 1


if __name__ == '__main__':
    sys.exit(main())
