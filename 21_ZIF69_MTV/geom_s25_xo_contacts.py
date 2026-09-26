#!/usr/bin/env python3
"""결함 §25 독립 재현(클라우드 검증석, 종합자 부탁 ① · ②) — 표준 파이썬만.

형판 Zn(bib)(bdtdc) 4,8-자리 8곳(E-22 빌드 기록 `e22_candidates/e22_build.json` 의 sites — 템플릿 원자 번호)을
X선 골격(CoRE `2017_Zn__dia_3_ASR_1.cif`, `core_pop_cifs.zip` 안 — CCDC 1498478 골격 그대로)에서 찾고,
치환체 빌드 CIF · GFN-FF 고정셀 이완본(`relax_tnf/<tag>_relaxed.cif` = Widom 입력 좌표)에서 **같은 자리**의
치환기(무거운 원자 전부)와 골격 O 사이 최소 거리를 잰다.

검사기 결함(§25)을 되풀이하지 않도록 **대상 구조에서 결합 그래프를 만들지 않음**:
  · 치환기 원자 = 빌드: X선 모체에 같은 원소가 0.3 Å 안에 없는 원자 · 이완본: 빌드의 치환기 원자에 일대일 대응(같은 원소, 가까운 짝부터)된 원자
  · 자리 = 모체의 4,8-탄소 좌표에 가장 가까운 C(고정셀이라 분율 좌표 대응) · 자리 묶음 = 그 자리 C 가 가장 가까운 치환기 원자(4.5 Å 안)
  · 골격 O = 치환기 원자가 아닌 O 전부(아무것도 빼지 않음 — 배위(Zn ≤ 2.4 Å) · 비배위만 표시)
  · 망(상호침투) 구분은 **X선 모체**의 결합 그래프에서만(공유반지름 합 + 0.45 Å, 격자 이동 추적 — 성분 × 자기 병진 격자)

  python geom_s25_xo_contacts.py [--json out.json]
"""
import json, os, sys, tempfile, zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from geom_e24h_symmetry_cf3 import read_cif, mat, dist  # noqa: E402

COV = {"H": 0.31, "C": 0.76, "N": 0.71, "O": 0.66, "F": 0.57, "S": 1.05, "Cl": 1.02, "Br": 1.20, "Zn": 1.22}
VDW = {"H": 1.20, "C": 1.70, "N": 1.55, "O": 1.52, "F": 1.47, "S": 1.80, "Cl": 1.75, "Br": 1.85}
TAGS = [("CN", "e24_candidates/E24_ZnDia_CN_100.cif", "e24_cn_100"),
        ("Br", "e24g_candidates/E24g_ZnDia_Br_100.cif", "e24g_br_100"),
        ("C2H5", "e24c_candidates/E24c_ZnDia_C2H5_100.cif", "e24c_c2h5_100"),
        ("CH3", "e24_candidates/E24_ZnDia_CH3_100.cif", "e24_ch3_100"),
        ("F", "e24_candidates/E24_ZnDia_F_100.cif", "e24_f_100"),
        ("Cl", "e24c_candidates/E24c_ZnDia_Cl_100.cif", "e24c_cl_100"),
        ("CF3", "e24g_candidates/E24g_ZnDia_CF3_100.cif", "e24g_cf3_100"),
        ("OCH3", "e24c_candidates/E24c_ZnDia_OCH3_100.cif", "e24c_och3_100"),
        ("SCH3", "e24c_candidates/E24c_ZnDia_SCH3_100.cif", "e24c_sch3_100"),
        ("CCH", "e24g_candidates/E24g_ZnDia_CCH_100.cif", "e24g_cch_100"),
        ("nC3H7", "e24g_candidates/E24g_ZnDia_nC3H7_100.cif", "e24g_nc3h7_100"),
        ("NO2 100", "e22_candidates/E22_ZnDia_NO2_100.cif", "e22_no2_100"),
        ("SO2Me 100", "e22_candidates/E22_ZnDia_SO2Me_100.cif", "e22_so2me_100"),
        ("NO2 50", "e22_candidates/E22_ZnDia_NO2_050.cif", "e22_no2_050"),
        ("SO2Me 50", "e22_candidates/E22_ZnDia_SO2Me_050.cif", "e22_so2me_050"),
        ("Cl 50a", "e24g_candidates/E24h_ZnDia_Cl_050a.cif", "e24h_cl_050a"),
        ("Cl 50b", "e24g_candidates/E24h_ZnDia_Cl_050b.cif", "e24h_cl_050b"),
        ("C2H5 50a", "e24g_candidates/E24h_ZnDia_C2H5_050a.cif", "e24h_c2h5_050a"),
        ("C2H5 50b", "e24g_candidates/E24h_ZnDia_C2H5_050b.cif", "e24h_c2h5_050b")]


def read_xray():
    z = zipfile.ZipFile(os.path.join(HERE, "core_pop_cifs.zip"))
    with tempfile.NamedTemporaryFile("wb", suffix=".cif", delete=False) as t:
        t.write(z.read("2017_Zn__dia_3_ASR_1.cif"))
    out = read_cif(t.name)
    os.unlink(t.name)
    return out


def nearest(M, atoms, f, pred=lambda a: True, skip=()):
    best = (1e9, None)
    for j, a in enumerate(atoms):
        if j in skip or not pred(a):
            continue
        d = dist(M, f, a[1])
        if d < best[0]:
            best = (d, j)
    return best


# ---------------------------------------------------------------- 망(상호침투) — X선 모체에서만
def hnf(vs):
    """정수 3-벡터들이 만드는 격자의 위삼각 기저 [(피벗 열, 벡터)]."""
    rows = [list(v) for v in vs if any(v)]
    basis = []
    for c in range(3):
        while True:
            nz = [r for r in rows if r[c] != 0]
            if len(nz) <= 1:
                break
            nz.sort(key=lambda r: abs(r[c]))
            p = nz[0]
            new = [p]
            for r in rows:
                if r is p:
                    continue
                if r[c] != 0:
                    q = r[c] // p[c]
                    r = [r[k] - q * p[k] for k in range(3)]
                if any(r):
                    new.append(r)
            rows = new
        nz = [r for r in rows if r[c] != 0]
        if nz:
            b = nz[0] if nz[0][c] > 0 else [-x for x in nz[0]]
            basis.append((c, b))
            rows = [r for r in rows if r is not nz[0]]
    return basis


def member(v, basis):
    v = list(v)
    for c, b in basis:
        if v[c] % b[c]:
            return False
        q = v[c] // b[c]
        v = [v[k] - q * b[k] for k in range(3)]
    return not any(v)


def nets(M, atoms):
    n = len(atoms)
    adj = [[] for _ in range(n)]
    for i in range(n):
        for j in range(n):
            si, sj = atoms[i][0], atoms[j][0]
            if i == j or (si == "H" and sj == "H"):
                continue
            fi, fj = atoms[i][1], atoms[j][1]
            if dist(M, fi, fj) <= COV[si] + COV[sj] + 0.45:
                adj[i].append((j, [round(fi[k] - fj[k]) for k in range(3)]))   # j 의 상 f_j + m 이 i 옆
    comp, u, gens = [None] * n, [None] * n, []
    for r in range(n):
        if comp[r] is not None:
            continue
        k = len(gens); gens.append([])
        comp[r], u[r] = k, (0, 0, 0)
        stack = [r]
        while stack:
            i = stack.pop()
            for j, m in adj[i]:
                w = tuple(u[i][t] + m[t] for t in range(3))
                if comp[j] is None:
                    comp[j], u[j] = k, w; stack.append(j)
                else:
                    d = tuple(w[t] - u[j][t] for t in range(3))
                    if any(d):
                        gens[k].append(d)
    return comp, u, [hnf(g) for g in gens]


def index(basis):
    if len(basis) < 3:
        return None
    return abs(basis[0][1][basis[0][0]] * basis[1][1][basis[1][0]] * basis[2][1][basis[2][0]])


def same_net(atoms, NET, i, j):
    """원자 i(원래 자리)와, i 에 가장 가까운 j 의 상이 같은 망인가."""
    comp, u, lat = NET
    if comp[i] != comp[j]:
        return False
    fi, fj = atoms[i][1], atoms[j][1]
    m = [round(fi[k] - fj[k]) for k in range(3)]
    return member([u[j][t] + m[t] - u[i][t] for t in range(3)], lat[comp[i]])


# ---------------------------------------------------------------- 측정
def coordinated(M, atoms, j):
    return any(a[0] == "Zn" and dist(M, atoms[j][1], a[1]) <= 2.4 for a in atoms)


def assign(M, A, Bm, B):
    """이완본 A 의 원자를 빌드 B 의 같은 원소 원자에 일대일로(가까운 짝부터) 대응 — 이완본에서 결합 그래프를 안 만듦."""
    pairs = []
    for i, a in enumerate(A):
        for j, b in enumerate(B):
            if a[0] == b[0]:
                d = dist(M, a[1], b[1])
                if d < 3.0:
                    pairs.append((d, i, j))
    pairs.sort()
    ai, bj, amap = set(), set(), {}
    for d, i, j in pairs:
        if i not in ai and j not in bj:
            ai.add(i); bj.add(j); amap[i] = (j, d)
    return amap


def measure(path, sites, X0, build=None):
    """build=None 이면 path 가 빌드 — 치환기 = X선 모체에 같은 원소가 0.3 Å 안에 없는 원자.
    build=(cell, atoms, subset) 이면 path 는 이완본 — 치환기 = 빌드 치환기 원자에 대응된 원자."""
    cell, A = read_cif(path)
    M = mat(cell)
    maxfw = None
    if build is None:
        sub = [j for j, a in enumerate(A) if nearest(MX, XA, a[1], lambda b, e=a[0]: b[0] == e)[0] > 0.3]
    else:
        bc, BA, bsub = build
        amap = assign(M, A, mat(bc), BA)
        assert len(amap) == len(A) == len(BA), (path, len(amap), len(A), len(BA))
        sub = [i for i, (j, d) in amap.items() if j in bsub]
        maxfw = max(d for i, (j, d) in amap.items() if j not in bsub)
    subset = set(sub)
    site_c = [nearest(M, A, XA[s["C"]][1], lambda a: a[0] == "C", skip=subset)[1] for s in sites]
    groups = [[] for _ in sites]
    for j in sub:
        if A[j][0] == "H":
            continue
        d, k = min((dist(M, A[j][1], A[c][1]), k) for k, c in enumerate(site_c))
        if d <= 4.5:
            groups[k].append(j)
    out = []
    for k, g in enumerate(groups):
        if not g:
            out.append(None); continue
        best = (1e9, None, None)
        for j in g:
            d, o = nearest(M, A, A[j][1], lambda a: a[0] == "O", skip=subset)
            if d < best[0]:
                best = (d, j, o)
        d, j, o = best
        out.append(dict(el=A[j][0], d=round(d, 3), O="비배위" if not coordinated(M, A, o) else "배위"))
    return out, len(sub), (cell, A, subset), maxfw


def main():
    B = json.load(open(os.path.join(HERE, "e22_candidates", "e22_build.json"), encoding="utf-8"))
    sites = B["sites"]
    global MX, XA
    X = read_xray()
    M0, X0 = mat(X[0]), X[1]
    MX, XA = M0, X0
    NET = nets(M0, X0)
    comps = sorted(set(NET[0]))
    fw = [c for c in comps if sum(1 for x in NET[0] if x == c) > 20]
    print(f"# §25 독립 재현 — X선 모체 {len(X0)}원자 · 결합 성분 {len(comps)}(골격 {len(fw)}) · "
          f"골격 성분의 자기 병진 격자 지수 {[index(NET[2][c]) for c in fw]}(= 셀 안 서로 다른 망 수)")
    print("\n## ② X선 모체: 4,8-H 와 가장 가까운 O")
    short = []
    for s in sites:
        c, h = s["C"], s["H"]
        assert X0[c][0] == "C" and X0[h][0] == "H", s
        d, o = nearest(M0, X0, X0[h][1], lambda a: a[0] == "O")
        sn = same_net(X0, NET, h, o)
        if d < 3.0:
            short.append(s)
        print(f"  고리 {s['ring']} C{c}–H{h} {dist(M0, X0[c][1], X0[h][1]):.3f} · H···O {d:.3f} Å · O{o} "
              f"{'비배위' if not coordinated(M0, X0, o) else '배위'} · {'같은 망' if sn else '다른 망'}")
    rings = sorted({s['ring'] for s in short})
    print(f"  → H···O < 3 Å 자리 {len(short)}곳 = 고리 {rings}(고리당 4,8 두 자리) · 나머지 {len(sites) - len(short)}곳")
    print("\n## ① 자리별 치환기(무거운 원자 전부) ↔ 골격 O 최소 거리 — 빌드 → 이완본(relax_tnf, = Widom 입력)")
    print("   자리: " + " · ".join(f"r{s['ring']}{'*' if s in short else ''}" for s in sites) + "   (* = X선 H···O 2.70 자리)")
    res = {}
    for lab, bpath, tag in TAGS:
        row = {}
        bout = measure(os.path.join(HERE, bpath), sites, X0)
        row["build"] = bout
        rp = os.path.join(HERE, "relax_tnf", tag + "_relaxed.cif")
        row["relaxed"] = measure(rp, sites, X0, build=bout[2]) if os.path.exists(rp) else None
        res[lab] = row
        for kind in ("build", "relaxed"):
            v = row[kind]
            txt = "—" if v is None else " ".join("·" if x is None else f"{x['el']}{x['d']:.2f}" for x in v[0])
            extra = "" if v is None else f"   (치환기 원자 {v[1]}" + (f" · 골격 최대 변위 {v[3]:.2f} Å)" if v[3] is not None else ")")
            print(f"  {lab if kind == 'build' else '':9s} {'빌드' if kind == 'build' else '이완'} {txt}{extra}")
    print("\n## 요약 — 이완본: 2.70 자리 · 4.1 자리 치환기–O 최소(원소) · vdW 합 대비")
    idx_short = [i for i, s in enumerate(sites) if s in short]
    for lab, row in res.items():
        v = row["relaxed"]
        if not v:
            continue
        a = [x for i, x in enumerate(v[0]) if x and i in idx_short]
        b = [x for i, x in enumerate(v[0]) if x and i not in idx_short]
        fa = f"{min(x['d'] for x in a):.2f}({a[0]['el']}, O {a[0]['O']}, vdW {VDW[a[0]['el']] + VDW['O']:.2f})" if a else "—"
        fb = f"{min(x['d'] for x in b):.2f}({b[0]['el']})" if b else "—"
        print(f"  {lab:9s} 2.70 자리 {len(a)}곳 {fa} · 4.1 자리 {len(b)}곳 {fb}")
    if "--json" in sys.argv:
        res = {k: {kk: (None if vv is None else dict(sites=vv[0], n_sub=vv[1], max_fw_disp=vv[3])) for kk, vv in r.items()} for k, r in res.items()}
        json.dump(res, open(sys.argv[sys.argv.index("--json") + 1], "w"), ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()
