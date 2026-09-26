#!/usr/bin/env python3
"""cloud 2차 ③ 기하 서술(판정 아님) — 표준 파이썬만(numpy · ase 없음).

(a) E-24h 실현 A(고리 [0,3]) · B([1,2])가 대칭 동치인가:
    단사 격자의 점군 연산 {E, 2_y, -1, m_y}(b 유일축, 분수 좌표) × 병진(A 의 기준 원자를 B 의 같은 원소 원자로 보내는 모든 t)을 훑어,
    A 를 옮긴 좌표가 B 의 같은 원소 원자에 **일대일로** 겹치는 연산 중 최대 원자 차가 가장 작은 것을 찾음. 전하본이면 짝 원자의 |Δq| 최대도.
(b) CF₃ 이완본 F···O 최소 접촉: 그 O 의 정체(이웃 원자) · 모체 이완본 대응 O 대비 C–O · Zn–O 변화 · F–C · F···O 가 결합 거리인지.

  python geom_e24h_symmetry_cf3.py
"""
import math, re, sys, os

HERE = os.path.dirname(os.path.abspath(__file__))
COV = {"H": 0.31, "C": 0.76, "N": 0.71, "O": 0.66, "F": 0.57, "S": 1.05, "Cl": 1.02, "Br": 1.20, "Zn": 1.22}


def read_cif(path):
    txt = open(path).read()
    g = lambda k: float(re.search(rf"_cell_{k}\s+([\d.]+)", txt).group(1))
    cell = [g("length_a"), g("length_b"), g("length_c"), g("angle_alpha"), g("angle_beta"), g("angle_gamma")]
    # atom_site 루프 머리 읽기
    lines = txt.splitlines()
    atoms = []
    for i, l in enumerate(lines):
        if l.strip() == "loop_" and i + 1 < len(lines) and lines[i + 1].strip().startswith("_atom_site"):
            heads = []
            j = i + 1
            while j < len(lines) and lines[j].strip().startswith("_atom_site"):
                heads.append(lines[j].strip()); j += 1
            ix = {h: k for k, h in enumerate(heads)}
            while j < len(lines) and lines[j].strip() and not lines[j].strip().startswith(("loop_", "_")):
                p = lines[j].split()
                sym = p[ix["_atom_site_type_symbol"]]
                f = [float(p[ix[f"_atom_site_fract_{c}"]]) % 1.0 for c in "xyz"]
                q = float(p[ix["_atom_site_charge"]]) if "_atom_site_charge" in ix else None
                atoms.append((sym, f, q))
                j += 1
            break
    return cell, atoms


def mat(cell):
    a, b, c, al, be, ga = cell
    al, be, ga = map(math.radians, (al, be, ga))
    cx = c * math.cos(be); cy = c * (math.cos(al) - math.cos(be) * math.cos(ga)) / math.sin(ga)
    cz = math.sqrt(max(c * c - cx * cx - cy * cy, 0.0))
    return ((a, 0.0, 0.0), (b * math.cos(ga), b * math.sin(ga), 0.0), (cx, cy, cz))


def dist(M, f1, f2):
    d = [f1[k] - f2[k] for k in range(3)]
    d = [x - round(x) for x in d]
    c = [d[0] * M[0][k] + d[1] * M[1][k] + d[2] * M[2][k] for k in range(3)]
    return math.sqrt(c[0] ** 2 + c[1] ** 2 + c[2] ** 2)


ROT = {"E": (1, 1, 1), "2_y": (-1, 1, -1), "-1": (-1, -1, -1), "m_y": (1, -1, 1)}


def match(A, B, M, rot, t, tol=0.5):
    """A 를 (rot, t) 로 옮겨 B 와 일대일 짝. 반환 (최대 차, 짝 목록) 또는 None."""
    used = set(); pairs = []; worst = 0.0
    byel = {}
    for j, (s, f, q) in enumerate(B):
        byel.setdefault(s, []).append(j)
    for i, (s, f, q) in enumerate(A):
        g = [(rot[k] * f[k] + t[k]) % 1.0 for k in range(3)]
        best, bj = 9e9, None
        for j in byel.get(s, []):
            if j in used: continue
            d = dist(M, g, B[j][1])
            if d < best: best, bj = d, j
        if bj is None or best > tol:
            return None
        used.add(bj); pairs.append((i, bj, best)); worst = max(worst, best)
    return worst, pairs


def sym_equiv(pa, pb, label):
    cA, A = read_cif(pa); cB, B = read_cif(pb)
    M = mat(cA)
    celld = max(abs(x - y) for x, y in zip(cA, cB))
    anchor_el = min({s for s, _, _ in A}, key=lambda e: sum(1 for s, _, _ in A if s == e))  # 가장 드문 원소
    i0 = next(i for i, (s, _, _) in enumerate(A) if s == anchor_el)
    best = None
    for name, rot in ROT.items():
        for j, (s, f, q) in enumerate(B):
            if s != anchor_el: continue
            t = [f[k] - rot[k] * A[i0][1][k] for k in range(3)]
            m = match(A, B, M, rot, t)
            if m and (best is None or m[0] < best[0]):
                best = (m[0], name, [round(x % 1.0, 4) for x in t], m[1])
    if best is None:
        print(f"(a) {label}: 셀 차 {celld:.2e} · **겹치는 연산 없음**(허용 0.5 Å) — 대칭 동치 아님")
        return
    worst, name, t, pairs = best
    dq = None
    if A[0][2] is not None and B[0][2] is not None:
        dq = max(abs(A[i][2] - B[j][2]) for i, j, _ in pairs)
    # 항등(E, t≈0)으로 겹치면 "같은 구조" 이지 대칭 동치가 아님 — 따로 표시
    ident = name == "E" and all(min(x, 1 - x) < 1e-3 for x in t)
    print(f"(a) {label}: 셀 차 {celld:.2e} · 원자 {len(A)} · 가장 잘 겹치는 연산 {name} + t {t} · **최대 원자 차 {worst:.4f} Å**"
          + (f" · 짝 원자 |Δq| 최대 {dq:.4f} e" if dq is not None else "") + (" · ⚠ 항등 연산(같은 좌표)" if ident else ""))


def neighbors(M, atoms, i, cut=1.25):
    s0, f0, _ = atoms[i]
    out = []
    for j, (s, f, q) in enumerate(atoms):
        if j == i: continue
        d = dist(M, f0, f)
        lim = (COV.get(s0, 1.0) + COV.get(s, 1.0)) * cut if "Zn" not in (s0, s) else 2.4
        if d < lim:
            out.append((s + str(j), round(d, 3)))
    return sorted(out, key=lambda x: x[1])


def cf3_contact():
    cX, X = read_cif(os.path.join(HERE, "relax_tnf/e24g_cf3_100_relaxed.cif")); M = mat(cX)
    cP, P = read_cif(os.path.join(HERE, "relax_tnf/e22_parent_relaxed.cif")); MP = mat(cP)
    cB, Bld = read_cif(os.path.join(HERE, "e24g_candidates/E24g_ZnDia_CF3_100.cif"))
    Fs = [i for i, (s, _, _) in enumerate(X) if s == "F"]
    Os = [i for i, (s, _, _) in enumerate(X) if s == "O"]
    best = sorted(((dist(M, X[i][1], X[j][1]), i, j) for i in Fs for j in Os))[:4]
    print("(b) CF₃ 이완본 F···O 최소 넷:", [(f"F{i}", f"O{j}", round(d, 3)) for d, i, j in best])
    d, fi, oj = best[0]
    print(f"    최소 F{fi}···O{oj} {d:.3f} Å · F{fi} 이웃 {neighbors(M, X, fi)} · O{oj} 이웃 {neighbors(M, X, oj)}")
    # O 의 탄소 · Zn
    oc = [n for n in neighbors(M, X, oj) if n[0].startswith("C")]
    oz = [n for n in neighbors(M, X, oj) if n[0].startswith("Zn")]
    # 모체 대응 O: 빌드 틀(E22_ZnDia_parent.cif — 빌더 · 측정이 쓴 모체)에서 빌드 좌표와 가장 가까운 O 의 번호 →
    # 모체 이완본(relax_tnf/e22_parent_relaxed.cif)은 그 틀을 이완한 것이라 원자 순서가 같음(원자 수 · 원소 순서로 확인)
    cT, T = read_cif(os.path.join(HERE, "e22_candidates/E22_ZnDia_parent.cif")); MT = mat(cT)
    # 원자 순서는 가정하지 않음(틀 · 이완본 순서가 다름을 확인) — 틀의 대응 O 에서 가장 가까운 O 를 이완본에서 찾음
    fb = Bld[oj][1]
    jt = min((j for j, (s, _, _) in enumerate(T) if s == "O"), key=lambda j: dist(MT, T[j][1], fb))
    jp = min((j for j, (s, _, _) in enumerate(P) if s == "O"), key=lambda j: dist(MP, P[j][1], T[jt][1]))
    pn = neighbors(MP, P, jp)
    print(f"    대응 모체 O: 틀 O{jt}(빌드 좌표와 {dist(MT, T[jt][1], fb):.3f} Å) → 이완본 O{jp}(틀과 {dist(MP, P[jp][1], T[jt][1]):.3f} Å) 이웃 {pn}")
    # 모든 F···O < 2.2 Å
    shortFO = sorted((round(dist(M, X[i][1], X[j][1]), 3), f"F{i}", f"O{j}") for i in Fs for j in Os if dist(M, X[i][1], X[j][1]) < 2.2)
    print(f"    F···O < 2.2 Å: {len(shortFO)}개 · O 별 {sorted({o for _, _, o in shortFO})} · 값 {sorted({d for d, _, _ in shortFO})}")
    # CF3 C–F 길이 분포
    CF = sorted(round(dist(M, X[i][1], X[k][1]), 3) for i in Fs for k, (s, _, _) in enumerate(X) if s == "C" and dist(M, X[i][1], X[k][1]) < 1.7)
    print(f"    C–F 길이 {len(CF)}개: 최소 {CF[0]} · 최대 {CF[-1]} · 1.45 넘는 것 {sum(1 for x in CF if x > 1.45)}개")
    pc = [n for n in pn if n[0].startswith("C")]; pz = [n for n in pn if n[0].startswith("Zn")]
    if oc and pc:
        print(f"    C–O: 모체 {pc[0][1]:.3f} → CF₃ {oc[0][1]:.3f} Å (Δ {oc[0][1]-pc[0][1]:+.3f})")
    print(f"    Zn–O(≤ 2.4 Å): 모체 {[n[1] for n in pz]} → CF₃ {[n[1] for n in oz]}")
    # 같은 카복실 C 의 다른 O
    if oc:
        cidx = int(oc[0][0][1:])
        print(f"    카복실 C{cidx} 이웃 {neighbors(M, X, cidx)}")
    # CF3 탄소
    fcs = [n for n in neighbors(M, X, fi) if n[0].startswith("C")]
    if fcs:
        ci = int(fcs[0][0][1:])
        print(f"    CF₃ 탄소 C{ci} 이웃 {neighbors(M, X, ci)} · C{ci}···O{oj} {dist(M, X[ci][1], X[oj][1]):.3f} Å")
    # 빌드 직후 같은 짝
    print(f"    빌드 직후(이완 전) F{fi}···O{oj} {dist(mat(cB), Bld[fi][1], Bld[oj][1]):.3f} Å")
    # 모체 이완본의 O–H·O–X 최소(비교용): 형판 계열 이전 11구조 F···O 등은 판정 줄 2.39~2.77
    print("    참고: 공유 F–O 결합 ≈ 1.42 Å · F···O 반데르발스 합 ≈ 2.99 Å(1.47 + 1.52)")


if __name__ == "__main__":
    for tag in ("c2h5", "cl"):
        sym_equiv(os.path.join(HERE, f"relax_tnf/e24h_{tag}_050a_relaxed.cif"), os.path.join(HERE, f"relax_tnf/e24h_{tag}_050b_relaxed.cif"), f"{tag} 이완본")
        sym_equiv(os.path.join(HERE, f"charged_v3/e24h_{tag}_050a_DDEC6.cif"), os.path.join(HERE, f"charged_v3/e24h_{tag}_050b_DDEC6.cif"), f"{tag} 전하본")
        sym_equiv(os.path.join(HERE, f"e24g_candidates/E24h_ZnDia_{'C2H5' if tag == 'c2h5' else 'Cl'}_050a.cif"),
                  os.path.join(HERE, f"e24g_candidates/E24h_ZnDia_{'C2H5' if tag == 'c2h5' else 'Cl'}_050b.cif"), f"{tag} 빌드(이완 전)")
    cf3_contact()
