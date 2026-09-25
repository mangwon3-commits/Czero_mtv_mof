# -*- coding: utf-8 -*-
"""E-22f — CoRE CIF 의 H 만 이웃 무거운 원자와의 결합 방향으로 중성자 표준 길이까지 옮김(무거운 원자·셀 불변).
등록 ASSIGN_MAGI5B §HKHOME 10차. 길이: Allen & Bruno 2010 (C–H 1.083 · N–H 1.009 · O–H 0.983 Å)."""
import json, os, re, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import e22d_charges as ec                        # read() 재사용
TARGET = {'C': 1.083, 'N': 1.009, 'O': 0.983}


def normalize(src, dst):
    at, M = ec.read(src); Minv = np.linalg.inv(M)
    F = np.array([f for _, f, _ in at]); E = [e for e, _, _ in at]
    newF = F.copy(); log = []
    for i, e in enumerate(E):
        if e != 'H': continue
        d = F - F[i]; d -= np.round(d); v = d @ M; r = np.linalg.norm(v, axis=1); r[i] = 9e9
        r_h = r.copy(); r_h[[k for k, x in enumerate(E) if x == 'H']] = 9e9
        j = int(np.argmin(r_h))
        assert E[j] in TARGET, (i, E[j])
        assert r[j] <= r.min() + 1e-9 or r.min() > 0.6, ('H 최근접이 H', i)
        u = -v[j] / r[j]                             # 무거운 원자 → H 방향
        heavy_cart = F[i] @ M + v[j]                 # 무거운 원자(최근접 상) 데카르트
        newF[i] = (heavy_cart + u * TARGET[E[j]]) @ Minv
        log.append((E[j], float(r[j]), TARGET[E[j]]))
    # 파일: 원자 줄의 좌표만 바꿈(순서·라벨·전하 줄 유지)
    lines = open(src, encoding='utf-8').read().splitlines(); k = 0; out = []
    for ln in lines:
        p = ln.split()
        if k < len(at) and len(p) >= 7 and p[0] == at[k][0] and re.match(r'^-?[\d.]+$', p[3]):
            if at[k][0] == 'H':
                p[3:6] = [f'{x:.6f}' for x in newF[k]]
                ln = '  '.join(p)
            k += 1
        out.append(ln)
    assert k == len(at), (k, len(at))
    open(dst, 'w', encoding='utf-8').write('\n'.join(out) + '\n')
    # 검산: 바뀐 뒤 X–H 길이 · 무거운 원자 불변 · 최소 비결합 H 접촉
    at2, _ = ec.read(dst); F2 = np.array([f for _, f, _ in at2])
    heavy_same = all(np.allclose(F[i], F2[i]) for i, e in enumerate(E) if e != 'H')
    xh = []; hh = []
    for i, e in enumerate(E):
        if e != 'H': continue
        d = F2 - F2[i]; d -= np.round(d); r = np.linalg.norm(d @ M, axis=1); r[i] = 9e9
        s = np.sort(r); xh.append(float(s[0])); hh.append(float(s[1]))
    return dict(n_H=len(log), before_mean=float(np.mean([a for _, a, _ in log])), before_min=float(min(a for _, a, _ in log)),
                after_min=min(xh), after_max=max(xh), heavy_unchanged=heavy_same, min_second_neighbor_of_H=min(hh),
                by_parent={p: sum(1 for x, _, _ in log if x == p) for p in set(x for x, _, _ in log)})


if __name__ == '__main__':
    src = os.path.join(HERE, 'core_pop_cifs/2017_Zn__dia_3_ASR_1.cif')
    dst = os.path.join(HERE, 'e22f/2017_Zn__dia_3_ASR_1_hnorm.cif')
    r = normalize(src, dst); r.update(src=src, dst=dst, target=TARGET)
    json.dump(r, open(os.path.join(HERE, 'e22f/hnorm_check.json'), 'w'), indent=1, ensure_ascii=False)
    print(json.dumps(r, indent=1, ensure_ascii=False))
