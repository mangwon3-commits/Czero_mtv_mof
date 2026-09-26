#!/usr/bin/env python3
"""관문(0b) 독립 구현 — 클라우드 검증석(cloud 3차 ①). 등록 `ASSIGN_MAGI5B_20260925.md` §HKHOME 22차 문구만 보고 짬
(종합자 `clash_gate.py` 는 안 봄). 표준 파이썬만.

등록 문구:
  치환기 무거운 원자 X 와 골격 무거운 원자 Y 의 거리 d 에 대해 겹침 = r_vdW(X) + r_vdW(Y) − d ≥ 0.4 Å 이면 충돌.
  Bondi 반지름 C 1.70 · N 1.55 · O 1.52 · F 1.47 · S 1.80 · Cl 1.75 · Br 1.85 · Zn 1.39.
  결합 판정은 이완 뒤 구조가 아니라 모체 X선 위상(+ 치환기 내부 · 부착 C–X)에서 — 부착 C 에서 2 결합 안의 골격 원자만 뺌.
구현:
  · 모체 X선 = `e22_candidates/E22_ZnDia_parent.cif`(CoRE 2017_Zn__dia_3_ASR_1 과 좌표 같음). 위상 = 공유반지름 합 + 0.45 Å(Zn–O/N 포함).
  · 빌드 CIF 의 골격 원자는 X선 원자와 좌표가 같음(0.3 Å 안 같은 원소) → X선 번호. 나머지가 치환기 원자.
  · 이완본은 빌드와 원자 수가 같음 → 같은 원소끼리 가까운 짝부터 일대일 대응(이완본에서 결합 그래프를 만들지 않음).
  · 치환기 묶음 = 빌드 기하에서 치환기 원자끼리 · 부착 C 와의 공유 결합으로 이은 성분. 부착 C = 치환기 원자와 결합한
    빌더 4,8-자리 탄소(`e22_candidates/e22_build.json` sites — n-C₃H₇ 빌드는 사슬 C 가 다른 골격 C 에 1.09 Å 라 자리로 한정).
  · Y 는 치환기 원자가 아닌 무거운 원자 전부(다른 자리 치환기는 Y 가 아님 — 치환기끼리는 서술로 따로).
  · 제외: 그 치환기의 부착 C 에서 모체 위상 2 결합 안(0 · 1 · 2)의 골격 원자.
  · 거리: 최소 영상(셀 최단 9.3 Å — 4.6 Å 안 짝은 정확).

  python gate0b_check.py                      # relax_tnf 형판 계열 전부 + 빌드
  python gate0b_check.py --only e24i          # 이름에 e24i 가 든 것만
"""
import glob, json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from geom_e24h_symmetry_cf3 import read_cif, mat, dist  # noqa: E402

BONDI = {"C": 1.70, "N": 1.55, "O": 1.52, "F": 1.47, "S": 1.80, "Cl": 1.75, "Br": 1.85, "Zn": 1.39}
COV = {"H": 0.31, "C": 0.76, "N": 0.71, "O": 0.66, "F": 0.57, "S": 1.05, "Cl": 1.02, "Br": 1.20, "Zn": 1.22}
TH = 0.4

# 이완본 이름 → 빌드 CIF (E-24i 는 아래 find_build 가 찾음)
BUILD = {
    "e22_no2_050": "e22_candidates/E22_ZnDia_NO2_050.cif", "e22_no2_100": "e22_candidates/E22_ZnDia_NO2_100.cif",
    "e22_so2me_050": "e22_candidates/E22_ZnDia_SO2Me_050.cif", "e22_so2me_100": "e22_candidates/E22_ZnDia_SO2Me_100.cif",
    "e22_parent": "e22_candidates/E22_ZnDia_parent.cif",
    "e24_ch3_100": "e24_candidates/E24_ZnDia_CH3_100.cif", "e24_cn_100": "e24_candidates/E24_ZnDia_CN_100.cif",
    "e24_f_100": "e24_candidates/E24_ZnDia_F_100.cif",
    "e24c_c2h5_100": "e24c_candidates/E24c_ZnDia_C2H5_100.cif", "e24c_cl_100": "e24c_candidates/E24c_ZnDia_Cl_100.cif",
    "e24c_och3_100": "e24c_candidates/E24c_ZnDia_OCH3_100.cif", "e24c_sch3_100": "e24c_candidates/E24c_ZnDia_SCH3_100.cif",
    "e24g_br_100": "e24g_candidates/E24g_ZnDia_Br_100.cif", "e24g_cch_100": "e24g_candidates/E24g_ZnDia_CCH_100.cif",
    "e24g_cf3_100": "e24g_candidates/E24g_ZnDia_CF3_100.cif", "e24g_nc3h7_100": "e24g_candidates/E24g_ZnDia_nC3H7_100.cif",
    "e24h_cl_050a": "e24g_candidates/E24h_ZnDia_Cl_050a.cif", "e24h_cl_050b": "e24g_candidates/E24h_ZnDia_Cl_050b.cif",
    "e24h_c2h5_050a": "e24g_candidates/E24h_ZnDia_C2H5_050a.cif", "e24h_c2h5_050b": "e24g_candidates/E24h_ZnDia_C2H5_050b.cif",
}


def find_build(tag):
    if tag in BUILD:
        return os.path.join(HERE, BUILD[tag])
    # E-24i: e24i_<x>_open → e24i_candidates/*<x>*open*.cif (대소문자 무시)
    m = re.match(r"e24i_(.+)_open$", tag)
    if m:
        x = m.group(1).lower()
        for p in glob.glob(os.path.join(HERE, "e24i_candidates", "*.cif")):
            b = os.path.basename(p).lower()
            if "open" in b and re.search(rf"_{re.escape(x)}(_|\.)", b):
                return p
    return None


def topo(M, A):
    n = len(A)
    adj = [set() for _ in range(n)]
    for i in range(n):
        for j in range(i + 1, n):
            si, sj = A[i][0], A[j][0]
            if si == "H" and sj == "H":
                continue
            if dist(M, A[i][1], A[j][1]) <= COV[si] + COV[sj] + 0.45:
                adj[i].add(j); adj[j].add(i)
    return adj


def within2(adj, c):
    s = {c} | adj[c]
    for k in list(adj[c]):
        s |= adj[k]
    return s


def nearest_same(M, A, f, el, cut):
    best = (cut, None)
    for j, a in enumerate(A):
        if a[0] == el:
            d = dist(M, f, a[1])
            if d < best[0]:
                best = (d, j)
    return best[1]


def assign(M, A, B):
    pairs = sorted((dist(M, a[1], b[1]), i, j) for i, a in enumerate(A) for j, b in enumerate(B) if a[0] == b[0] and dist(M, a[1], b[1]) < 3.0)
    ai, bj, out = set(), set(), {}
    for d, i, j in pairs:
        if i not in ai and j not in bj:
            ai.add(i); bj.add(j); out[i] = j
    return out


SITES = {s["C"] for s in json.load(open(os.path.join(HERE, "e22_candidates", "e22_build.json"), encoding="utf-8"))["sites"]}


def gate(relaxed, build, X0, M0, ADJ0):
    cb, B = read_cif(build)
    MB = mat(cb)
    # 빌드 → X선(골격)
    b2x = {}
    for j, b in enumerate(B):
        k = nearest_same(M0, X0, b[1], b[0], 0.3)
        if k is not None:
            b2x[j] = k
    subB = [j for j in range(len(B)) if j not in b2x]
    # 치환기 묶음(빌드 기하) — 치환기 원자끼리 + 부착 골격 C
    grp, att = {}, {}
    for j in subB:
        grp[j] = j
    def f(j):
        while grp[j] != j:
            grp[j] = grp[grp[j]]; j = grp[j]
        return j
    for i in subB:
        for j in subB:
            if i < j and not (B[i][0] == "H" and B[j][0] == "H") and dist(MB, B[i][1], B[j][1]) <= COV[B[i][0]] + COV[B[j][0]] + 0.45:
                grp[f(i)] = f(j)
    for j in subB:
        if B[j][0] == "H":
            continue
        for k, x in b2x.items():
            if x in SITES and dist(MB, B[j][1], B[k][1]) <= COV[B[j][0]] + COV["C"] + 0.45:
                att.setdefault(f(j), set()).add(x)
    groups = {}
    for j in subB:
        groups.setdefault(f(j), []).append(j)
    # 이완본 좌표로
    if relaxed == build:
        M, A, r2b = MB, B, {j: j for j in range(len(B))}
    else:
        cr, A = read_cif(relaxed)
        M = mat(cr)
        if len(A) != len(B):
            return dict(error=f"원자 수 다름 {len(A)} 대 {len(B)}")
        a2b = assign(M, A, B)
        if len(a2b) != len(A):
            return dict(error=f"대응 {len(a2b)}/{len(A)}")
        r2b = {b: a for a, b in a2b.items()}
    subset = set(subB)
    worst, clashes, pairs_ss = None, [], None
    for g, members in groups.items():
        if g not in att or len(att[g]) != 1:
            if any(B[j][0] != "H" for j in members):
                return dict(error=f"부착 C 판별 실패 {sorted(att.get(g, []))}")
            continue
        c_att = next(iter(att[g]))
        excl = within2(ADJ0, c_att)
        for j in members:
            if B[j][0] == "H":
                continue
            xa = A[r2b[j]]
            for k in range(len(B)):
                if k in subset or B[k][0] == "H":
                    continue
                if b2x[k] in excl:
                    continue
                ya = A[r2b[k]]
                d = dist(M, xa[1], ya[1])
                ov = BONDI[xa[0]] + BONDI[ya[0]] - d
                if worst is None or ov > worst[0]:
                    worst = (round(ov, 3), xa[0], ya[0], round(d, 3))
                if ov >= TH:
                    clashes.append((round(ov, 3), xa[0], ya[0], round(d, 3)))
    # 서술: 서로 다른 치환기끼리
    gl = [(g, [j for j in m if B[j][0] != "H"]) for g, m in groups.items()]
    for a in range(len(gl)):
        for b in range(a + 1, len(gl)):
            for i in gl[a][1]:
                for j in gl[b][1]:
                    d = dist(M, A[r2b[i]][1], A[r2b[j]][1])
                    ov = BONDI[B[i][0]] + BONDI[B[j][0]] - d
                    if pairs_ss is None or ov > pairs_ss[0]:
                        pairs_ss = (round(ov, 3), B[i][0], B[j][0], round(d, 3))
    return dict(n_sub=len(subB), n_groups=len([g for g in groups if g in att]), worst=worst,
                n_clash=len(clashes), passed=(len(clashes) == 0), sub_sub_worst=pairs_ss)


def main():
    c0, X0 = read_cif(os.path.join(HERE, "e22_candidates", "E22_ZnDia_parent.cif"))
    M0 = mat(c0)
    ADJ0 = topo(M0, X0)
    only = sys.argv[sys.argv.index("--only") + 1] if "--only" in sys.argv else None
    tags = sorted(os.path.basename(p)[:-len("_relaxed.cif")] for p in glob.glob(os.path.join(HERE, "relax_tnf", "*_relaxed.cif"))
                  if re.match(r"e2(2|4|4c|4g|4h|4i)_", os.path.basename(p)))
    if only:
        tags = [t for t in tags if only in t]
    print(f"# 관문(0b) 독립 구현 — 겹침 = r(X) + r(Y) − d ≥ {TH} Å 충돌 · Bondi · 위상 = 모체 X선 · 부착 C 2결합 안 제외")
    print("| 구조 | 빌드: 최악 겹침(X···Y d) · 충돌 짝 | **이완본: 최악 겹침(X···Y d)** · 충돌 짝 | (0b) | 치환기끼리 최악(서술) |")
    print("|---|---|---|---|---|")
    res = {}
    for t in tags:
        bp = find_build(t)
        rp = os.path.join(HERE, "relax_tnf", t + "_relaxed.cif")
        if bp is None or not os.path.exists(bp):
            print(f"| {t} | 빌드 CIF 못 찾음 | | | |"); continue
        gb = gate(bp, bp, X0, M0, ADJ0)
        gr = gate(rp, bp, X0, M0, ADJ0)
        res[t] = dict(build=gb, relaxed=gr)
        def fm(g):
            if "error" in g:
                return g["error"]
            if g["worst"] is None:
                return "치환기 없음"
            w = g["worst"]
            return f"{w[0]:+.3f}({w[1]}···{w[2]} {w[3]:.3f}) · {g['n_clash']}"
        verdict = "—" if "error" in gr else ("통과(치환기 없음)" if gr["worst"] is None else ("**통과**" if gr["passed"] else "**충돌**"))
        ss = gr.get("sub_sub_worst")
        print(f"| {t} | {fm(gb)} | {fm(gr)} | {verdict} | {'—' if not ss else f'{ss[0]:+.3f}({ss[1]}···{ss[2]} {ss[3]:.3f})'} |")
    if "--json" in sys.argv:
        json.dump(res, open(sys.argv[sys.argv.index("--json") + 1], "w"), ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()
