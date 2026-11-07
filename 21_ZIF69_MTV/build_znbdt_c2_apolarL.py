# -*- coding: utf-8 -*-
"""ZNBDT-C2-L — 무극성 −CN 민감도 판 L: `build_znbdt_c2_apolar.py` 사본(원판 무수정 · 그 atom_rows 를 import).
등록 `ASSIGN_ZNBDT_C2_20261105.md` §7(종합자 · 자료 0건). 기하 · 원자 순서 · 다른 열은 원판과 바이트 단위로 같고 전하 열만 바뀝니다.
  L판  니트릴 C · N 전하 0(U·I 와 같음) → 빠진 짝 합(qN+qC)을 그 니트릴이 붙은 리간드의 비수소 원자(니트릴 C·N 제외) 전부에 균등 분배.
       리간드 = 결합 그래프에서 Zn 을 뗀 뒤 ipso C 가 속한 연결 성분 — **등록 문구대로 원판 `nb` 그래프**(N–C 는 < 1.2 Å, 그 밖은 < 1.6 Å).
       한 리간드에 니트릴 둘이면 두 짝 합을 그 리간드에 더함.
  주의(기록만): 이 `nb` 그래프는 C–S(1.735~1.753 Å)를 1.6 Å 밖으로 보아 티오펜 S 가 리간드 성분에 들지 않습니다 — 분배 원자에 S 없음.
       "bdtdc 비수소 전부"(S 포함) 와 다른 점은 결과 JSON `variants.L.note_S` 에 원자 수와 함께 적습니다.
니트릴 짝 · 원판 md5 는 기존 기록(results_znbdt_c2_build_hkhome.json, U·I)과 같아야 진행(assert). U·I 판 파일은 건드리지 않고 md5 만 다시 봅니다.
실행: czeromof 파이썬 — `python build_znbdt_c2_apolarL.py` (21_ZIF69_MTV 에서)
"""
import collections, hashlib, json, os, sys
import numpy as np
from ase.io import read
from ase.neighborlist import neighbor_list

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from build_znbdt_c2_apolar import atom_rows, SRC, REC   # noqa: E402
OUT_L = os.path.join(HERE, 'charged_v3', 'znbdt_c2_apolarL_DDEC6mod.cif')
md5 = lambda p: hashlib.md5(open(p, 'rb').read()).hexdigest()


def main():
    raw = open(SRC, encoding='utf-8').read()
    lines = raw.splitlines()
    hdr, idx = atom_rows(lines)
    qc = hdr.index('_atom_site_charge')
    q0 = np.array([float(lines[k].split()[qc]) for k in idx])
    a = read(SRC); s = a.get_chemical_symbols()
    assert len(a) == len(idx) == 208, (len(a), len(idx))
    # ── 원판과 같은 nb 그래프 · 같은 니트릴 짝 찾기 ──
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
    rec = json.load(open(REC, encoding='utf-8'))
    assert rec['src_md5'] == hashlib.md5(raw.encode()).hexdigest(), '원판 md5 가 기록과 다름'
    assert [(p['N'], p['C'], p['ipso']) for p in rec['nitrile']] == [tuple(map(int, p)) for p in pairs], '니트릴 짝이 기록과 다름'
    for v in ('U', 'I'):
        assert md5(os.path.join(HERE, rec['variants'][v]['cif'])) == rec['variants'][v]['md5'], f'{v}판 파일이 기록과 다름'
    nit = {x for n, c, _ in pairs for x in (n, c)}
    # ── 리간드 = Zn 을 뗀 nb 그래프에서 ipso C 의 연결 성분 ──
    def comp(start):
        seen, st = {start}, [start]
        while st:
            u = st.pop()
            for w in nb[u]:
                if w not in seen and s[w] != 'Zn':
                    seen.add(w); st.append(w)
        return frozenset(seen)
    lig = collections.OrderedDict()
    for n, c, p in pairs:
        L = comp(p)
        lig.setdefault(L, []).append((n, c, p))
    q = q0.copy()
    for x in nit: q[x] = 0.0
    ligrec = []
    for L, prs in lig.items():
        tgt = sorted(k for k in L if s[k] != 'H' and k not in nit)
        add = sum(q0[n] + q0[c] for n, c, _ in prs)
        q[tgt] += add / len(tgt)
        # 같은 리간드의 S (nb 그래프 밖) — 기록용: 성분 원자와 1.8 Å 안의 S
        s_near = sorted({int(y) for x, y, dd in zip(i, j, d) if x in L and s[y] == 'S' and dd < 1.8})
        ligrec.append({'component_n': len(L), 'component_formula': dict(collections.Counter(s[k] for k in L)),
                       'nitrile_N': [int(n) for n, _, _ in prs], 'n_target': len(tgt),
                       'target_formula': dict(collections.Counter(s[k] for k in tgt)), 'added_sum_e': float(add),
                       'per_atom_e': float(add / len(tgt)), 'S_bonded_but_outside_component': s_near})
    new = list(lines)
    for k, row in enumerate(idx):
        parts = new[row].split(); parts[qc] = f'{q[k]:.6f}'; new[row] = ' '.join(parts)
    body = '\n'.join(new) + '\n'   # 머리 주석 없음(U·I 와 같음)
    open(OUT_L, 'w', encoding='utf-8').write(body)
    b = read(OUT_L)
    assert np.allclose(b.get_positions(), a.get_positions(), atol=1e-6) and b.get_chemical_symbols() == s
    qw = np.array([float(body.splitlines()[k].split()[qc]) for k in idx])
    nS = sum(len(r['S_bonded_but_outside_component']) for r in ligrec)
    rec['variants']['L'] = {
        'cif': os.path.relpath(OUT_L, HERE), 'md5': hashlib.md5(body.encode()).hexdigest(),
        'assign': 'ASSIGN_ZNBDT_C2_20261105.md §7 (C2-L)', 'builder': 'build_znbdt_c2_apolarL.py',
        'rule': '니트릴 C·N 0 · 짝 합을 그 리간드(Zn 뗀 원판 nb 그래프의 ipso C 연결 성분)의 비수소 원자(니트릴 C·N 제외)에 균등',
        'ligands': ligrec,
        'note_S': (f'원판 nb 그래프(C–S 1.735~1.753 Å > 1.6 Å 문턱)에서 티오펜 S 는 리간드 성분 밖 — 분배 원자에 S 없음'
                   f'(리간드마다 S {nS // max(len(ligrec), 1)}개 · 등록 문구 "원판 nb 그래프" 대로 함 · "bdtdc 비수소 전부" 로 읽으면 분배 원자 +S)'),
        'net_charge_written': float(qw.sum()), 'net_ok_1e-3': bool(abs(qw.sum()) <= 1e-3),
        'max_change_non_nitrile': float(max(abs(qw[k] - q0[k]) for k in range(len(a)) if k not in nit)),
        'n_changed': int(sum(abs(qw[k] - q0[k]) > 5e-7 for k in range(len(a))))}
    r = rec['variants']['L']
    for g in ligrec:
        print(f"리간드 성분 {g['component_n']} 원자 {g['component_formula']} · 니트릴 {len(g['nitrile_N'])} · 분배 {g['n_target']} 원자 {g['target_formula']}"
              f" · 원자당 {g['per_atom_e']:+.6f} e · 성분 밖 S {g['S_bonded_but_outside_component']}")
    print(f"L판 {r['cif']} · md5 {r['md5'][:8]} · 순전하 {r['net_charge_written']:+.6f} ({'통과' if r['net_ok_1e-3'] else '탈락'})"
          f" · 바뀐 원자 {r['n_changed']} · 니트릴 밖 최대 변화 {r['max_change_non_nitrile']:.4f} e")
    json.dump(rec, open(REC, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    return 0 if r['net_ok_1e-3'] else 1


if __name__ == '__main__':
    sys.exit(main())
