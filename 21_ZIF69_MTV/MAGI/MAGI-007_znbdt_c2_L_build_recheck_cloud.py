"""종합자 독립 재현 — ZNBDT-C2-L 전하 분배(ASSIGN_ZNBDT_C2 §7). HKHOME build_znbdt_c2_apolarL.py 를 쓰지 않고 numpy 로만.
묻는 것: (1) §7 문구 "원판 nb 그래프(N–C < 1.2 Å · 그 밖 < 1.6 Å)" 의 연결 성분에 티오펜 S 가 드는가 (2) 그 규칙으로 낸 전하가 L CIF 와 같은가
(3) "bdtdc 비수소 전부(S 포함)" 로 읽으면 몇 원자 · 원자당 얼마인가. 실행: 21_ZIF69_MTV 에서."""
import sys, math, collections, numpy as np
def read_cif(path):
    L = open(path, encoding='utf-8').read().splitlines()
    cell = {}
    for l in L:
        t = l.split()
        if len(t) >= 2 and t[0].startswith('_cell_'): cell[t[0]] = float(t[1])
    i = next(k for k, l in enumerate(L) if l.strip().startswith('_atom_site_'))
    hdr = []
    while L[i].strip().startswith('_atom_site_'): hdr.append(L[i].strip()); i += 1
    rows = []
    while i < len(L) and L[i].strip() and not L[i].startswith('loop_') and not L[i].startswith('_'):
        rows.append(L[i].split()); i += 1
    a, b, c = (cell['_cell_length_a'], cell['_cell_length_b'], cell['_cell_length_c'])
    al, be, ga = (math.radians(cell[k]) for k in ('_cell_angle_alpha', '_cell_angle_beta', '_cell_angle_gamma'))
    v = math.sqrt(1 - math.cos(al)**2 - math.cos(be)**2 - math.cos(ga)**2 + 2 * math.cos(al) * math.cos(be) * math.cos(ga))
    M = np.array([[a, b * math.cos(ga), c * math.cos(be)], [0, b * math.sin(ga), c * (math.cos(al) - math.cos(be) * math.cos(ga)) / math.sin(ga)], [0, 0, c * v / math.sin(ga)]])
    ix = {h: n for n, h in enumerate(hdr)}
    sym_col = ix.get('_atom_site_type_symbol', ix['_atom_site_label'])
    def symbol(tok):
        letters = ''.join(ch for ch in tok if ch.isalpha())
        return letters[:2] if len(letters) >= 2 and letters[1].islower() else letters[:1]
    sym = [symbol(r[sym_col]) for r in rows]
    frac = np.array([[float(r[ix['_atom_site_fract_x']]), float(r[ix['_atom_site_fract_y']]), float(r[ix['_atom_site_fract_z']])] for r in rows])
    q = np.array([float(r[ix['_atom_site_charge']]) for r in rows])
    return sym, frac, q, M
sym, frac, q0, M = read_cif('charged_v3/e24i_cn_open_DDEC6.cif')
symL, fracL, qL, _ = read_cif('charged_v3/znbdt_c2_apolarL_DDEC6mod.cif')
assert sym == symL and np.allclose(frac, fracL), '기하·원자 순서 다름'
n = len(sym); print('원자', n, dict(collections.Counter(sym)))
df = frac[:, None, :] - frac[None, :, :]; df -= np.round(df)
D = np.linalg.norm(np.einsum('ij,abj->abi', M, df), axis=-1); np.fill_diagonal(D, 99)
nb = {k: set() for k in range(n)}
for x in range(n):
    for y in np.where(D[x] < 1.75)[0]:
        thr = 1.2 if {sym[x], sym[y]} == {'N', 'C'} else 1.6
        if D[x, y] < thr: nb[x].add(int(y))
cs = [D[x, y] for x in range(n) if sym[x] == 'C' for y in range(n) if sym[y] == 'S' and D[x, y] < 2.0]
print(f'C–S 거리 {min(cs):.3f}~{max(cs):.3f} Å ({len(cs)}쌍) → 1.6 Å 문턱 {"안" if max(cs) < 1.6 else "밖"} → S 는 nb 그래프에서 {"연결" if max(cs) < 1.6 else "고립"}')
nit = []
for x in range(n):
    if sym[x] == 'N' and len(nb[x]) == 1:
        c = next(iter(nb[x]))
        if sym[c] == 'C' and D[x, c] < 1.2:
            ipso = [y for y in nb[c] if y != x and sym[y] == 'C']; assert len(ipso) == 1
            nit.append((x, c, ipso[0]))
print('니트릴 짝', [(a, b, c) for a, b, c in nit], '전하 qN qC', q0[nit[0][0]], q0[nit[0][1]], '짝 합', q0[nit[0][0]] + q0[nit[0][1]])
def comp(st):
    seen, stack = {st}, [st]
    while stack:
        u = stack.pop()
        for w in nb[u]:
            if w not in seen and sym[w] != 'Zn': seen.add(w); stack.append(w)
    return frozenset(seen)
nitset = {a for a, b, _ in nit} | {b for a, b, _ in nit}
lig = collections.OrderedDict()
for a, b, p in nit: lig.setdefault(comp(p), []).append((a, b, p))
q = q0.copy(); q[list(nitset)] = 0.0
q_withS = q.copy()
for C, prs in lig.items():
    tgt = sorted(k for k in C if sym[k] != 'H' and k not in nitset)
    add = sum(q0[a] + q0[b] for a, b, _ in prs)
    q[tgt] += add / len(tgt)
    S_near = sorted({int(y) for x in C for y in np.where(D[x] < 1.8)[0] if sym[y] == 'S'})
    tgtS = sorted(set(tgt) | set(S_near))
    q_withS[tgtS] += add / len(tgtS)
    print(f'성분 {len(C)} 원자 {dict(collections.Counter(sym[k] for k in C))} · 니트릴 {len(prs)} · 분배 {len(tgt)} {dict(collections.Counter(sym[k] for k in tgt))} · 원자당 {add/len(tgt):+.6f} e'
          f' · 성분 밖 S(1.8 Å 안) {S_near} → S 포함이면 {len(tgtS)} 원자 · 원자당 {add/len(tgtS):+.6f} e')
print(f'L CIF 대조(문구대로 · S 제외): 최대 |Δq| {np.abs(q - qL).max():.2e} e · 바뀐 원자 {(np.abs(qL - q0) > 5e-7).sum()} · 순전하 {qL.sum():+.6f}')
print(f'S 포함 판(가정)과 L CIF 의 차: 최대 |Δq| {np.abs(q_withS - qL).max():.2e} e (S 원자 전하 L CIF 에서 바뀌었나: {bool((np.abs(qL - q0)[[k for k in range(n) if sym[k]=="S"]] > 5e-7).any())})')
