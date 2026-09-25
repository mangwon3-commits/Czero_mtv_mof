#!/usr/bin/env python3
"""막음 구가 닿지 않는 주머니를 전부 덮는가 — 순수 파이썬 격자 검사(클라우드 검증석 4회차, 2026-09-26).

왜: E-24c ① 에서 C₂H₅ 는 CO₂ 탐침(1.65 Å)으로 `-chan` 주머니 4 인데 `-block 1.65` 막음 구는 2
(OCH₃ 는 4 · 4). 막음 S_ON 188.6(E-24c (3) 기각 → E-24e)이 막히지 않은 주머니를 품었는지 가르려는 것.
Zeo++ 없이(계산 금지 · 환경 변경 금지 — numpy 도 없음) 탐침 중심 접근 격자를 만들고, 주기 경계를
넘는 연결을 '전압(격자 이동) 추적' 합집합-찾기로 나눠 **통로(자기 상과 이어짐) · 주머니(안 이어짐)** 를 셉니다.
그 다음 주머니 격자점이 `.block` 구(분수 좌표 중심 · 반지름 Å) 안에 드는지 최소상 거리로 봅니다.

한계: Zeo++ 의 보로노이 망이 아니라 격자(간격 ≈ h Å)라 경계 근처 좁은 목은 다르게 끊기거나 이어질 수 있음.
그래서 **대조(OCH₃ 4 · 모체 0)가 Zeo++ 개수를 재현할 때만** C₂H₅ 결과를 읽습니다.
반지름: Zeo++ 기본(CCDC) — 이 저장소의 호출은 `-r` 없이 `network -ha`.

  python pocket_block_cover_check.py relax_tnf/e24c_c2h5_100_relaxed.cif --probe 1.65 --block <file.block> [--h 0.3]
"""
import math, sys, subprocess, re

RAD = {"H": 1.09, "C": 1.70, "N": 1.55, "O": 1.52, "F": 1.47, "S": 1.80, "Cl": 1.75, "Zn": 1.39}


def read_cif(path):
    txt = open(path).read()
    g = lambda k: float(re.search(rf"_cell_{k}\s+([\d.]+)", txt).group(1))
    a, b, c = g("length_a"), g("length_b"), g("length_c")
    al, be, ga = (math.radians(g(f"angle_{x}")) for x in ("alpha", "beta", "gamma"))
    # 셀 행렬(행 = 격자 벡터)
    ax = (a, 0.0, 0.0)
    bx = (b * math.cos(ga), b * math.sin(ga), 0.0)
    cx_ = c * math.cos(be)
    cy_ = c * (math.cos(al) - math.cos(be) * math.cos(ga)) / math.sin(ga)
    cz_ = math.sqrt(max(c * c - cx_ * cx_ - cy_ * cy_, 0.0))
    M = (ax, bx, (cx_, cy_, cz_))
    atoms = []
    for line in txt.splitlines():
        p = line.split()
        if len(p) >= 6 and p[0] in RAD:
            try:
                atoms.append((p[0], float(p[3]) % 1.0, float(p[4]) % 1.0, float(p[5]) % 1.0))
            except ValueError:
                pass
    return M, atoms


def cart(M, f):
    return tuple(f[0] * M[0][k] + f[1] * M[1][k] + f[2] * M[2][k] for k in range(3))


def analyse(cif, probe, h):
    M, atoms = read_cif(cif)
    L = [math.sqrt(sum(v * v for v in M[i])) for i in range(3)]
    n = [max(8, int(round(L[i] / h))) for i in range(3)]
    rmax = max(RAD[e] for e, *_ in atoms) + probe
    # 원자 칸 묶기(분수 좌표 칸, 칸 크기 ≥ rmax 가 되게)
    nb = [max(1, int(L[i] // rmax)) for i in range(3)]
    bins = {}
    for e, x, y, z in atoms:
        key = (int(x * nb[0]) % nb[0], int(y * nb[1]) % nb[1], int(z * nb[2]) % nb[2])
        bins.setdefault(key, []).append((e, x, y, z))
    # 단사/비직교라 칸 이웃 폭을 넉넉히(각 축 ±2) 잡고, 칸마다 후보 원자 목록을 미리 만듦
    span = [2 if nb[i] > 4 else nb[i] for i in range(3)]
    cand = {}
    for bi in range(nb[0]):
        for bj in range(nb[1]):
            for bk in range(nb[2]):
                keys = {((bi + di) % nb[0], (bj + dj) % nb[1], (bk + dk) % nb[2])
                        for di in range(-span[0], span[0] + 1)
                        for dj in range(-span[1], span[1] + 1)
                        for dk in range(-span[2], span[2] + 1)}
                cand[(bi, bj, bk)] = [(x, y, z, (RAD[e] + probe) ** 2) for key in keys for e, x, y, z in bins.get(key, ())]
    m00, m01, m02 = M[0]; m10, m11, m12 = M[1]; m20, m21, m22 = M[2]
    acc = bytearray(n[0] * n[1] * n[2])
    idx = lambda i, j, k: (i * n[1] + j) * n[2] + k
    for i in range(n[0]):
        fx = (i + 0.5) / n[0]
        for j in range(n[1]):
            fy = (j + 0.5) / n[1]
            for k in range(n[2]):
                fz = (k + 0.5) / n[2]
                ok = True
                for x, y, z, lim2 in cand[(int(fx * nb[0]), int(fy * nb[1]), int(fz * nb[2]))]:
                    dx = fx - x; dx -= round(dx)
                    dy = fy - y; dy -= round(dy)
                    dz = fz - z; dz -= round(dz)
                    cx = dx * m00 + dy * m10 + dz * m20
                    cy = dx * m01 + dy * m11 + dz * m21
                    cz = dx * m02 + dy * m12 + dz * m22
                    if cx * cx + cy * cy + cz * cz < lim2:
                        ok = False
                        break
                if ok:
                    acc[idx(i, j, k)] = 1
    # 전압 추적 합집합-찾기: parent[p], off[p] = p 에서 부모로 가는 격자 이동
    N = len(acc)
    parent = list(range(N)); off = [(0, 0, 0)] * N
    perc = {}

    def find(p):
        path = []
        while parent[p] != p:
            path.append(p); p = parent[p]
        root = p
        # 경로 압축(이동 누적)
        acc_off = (0, 0, 0)
        for q in reversed(path):
            o = off[q]; acc_off = (acc_off[0] + o[0], acc_off[1] + o[1], acc_off[2] + o[2])
        # 다시 돌며 각 q 의 루트까지 이동을 계산
        tot = acc_off
        for q in path:
            o = off[q]
            parent[q] = root; off[q] = tot
            tot = (tot[0] - o[0], tot[1] - o[1], tot[2] - o[2])
        return root

    def pot(p):
        r = find(p)
        return r, off[p] if p != r else (0, 0, 0)

    for i in range(n[0]):
        for j in range(n[1]):
            for k in range(n[2]):
                p = idx(i, j, k)
                if not acc[p]:
                    continue
                for ax_, (di, dj, dk) in enumerate(((1, 0, 0), (0, 1, 0), (0, 0, 1))):
                    ii, jj, kk = i + di, j + dj, k + dk
                    w = [0, 0, 0]
                    if ii == n[0]: ii = 0; w[0] = 1
                    if jj == n[1]: jj = 0; w[1] = 1
                    if kk == n[2]: kk = 0; w[2] = 1
                    q = idx(ii, jj, kk)
                    if not acc[q]:
                        continue
                    rp, op = pot(p); rq, oq = pot(q)
                    # 이동: p 의 셀 기준 q 는 w 만큼 옆 셀. 루트 좌표: pos(p)=op, pos(q)=oq, 요구 op + w == oq (같은 루트면)
                    if rp == rq:
                        d = (op[0] + w[0] - oq[0], op[1] + w[1] - oq[1], op[2] + w[2] - oq[2])
                        if d != (0, 0, 0):
                            perc[rp] = True
                    else:
                        # rq 를 rp 밑에: off[rq] = op + w - oq
                        parent[rq] = rp
                        off[rq] = (op[0] + w[0] - oq[0], op[1] + w[1] - oq[1], op[2] + w[2] - oq[2])
                        if perc.pop(rq, False):
                            perc[rp] = True
    comps = {}
    for p in range(N):
        if acc[p]:
            comps.setdefault(find(p), []).append(p)
    chans = [r for r in comps if perc.get(r)]
    pockets = [r for r in comps if not perc.get(r)]
    return dict(M=M, n=n, comps=comps, chans=chans, pockets=pockets, n_acc=sum(acc))


def main():
    a = sys.argv
    cif = a[1]
    probe = float(a[a.index("--probe") + 1]) if "--probe" in a else 1.65
    h = float(a[a.index("--h") + 1]) if "--h" in a else 0.3
    blk = a[a.index("--block") + 1] if "--block" in a else None
    R = analyse(cif, probe, h)
    n, M = R["n"], R["M"]
    vox = abs(M[0][0] * (M[1][1] * M[2][2] - M[1][2] * M[2][1])) / (n[0] * n[1] * n[2])  # 근사(b·c 대각 성분)
    print(f"{cif} probe {probe} h {h} grid {n} 접근점 {R['n_acc']}")
    print(f"  통로 {len(R['chans'])} (크기 {[len(R['comps'][r]) for r in R['chans']]}) · 주머니 {len(R['pockets'])} (크기 {sorted((len(R['comps'][r]) for r in R['pockets']), reverse=True)})")
    if blk:
        if blk.startswith("git:"):
            txt = subprocess.run(["git", "show", blk[4:]], capture_output=True, text=True).stdout
        else:
            txt = open(blk).read()
        rows = [list(map(float, l.split())) for l in txt.strip().splitlines()[1:]]
        print(f"  막음 구 {len(rows)}: {rows}")

        def inside_any(p):
            i, rem = divmod(p, n[1] * n[2]); j, k = divmod(rem, n[2])
            f = ((i + 0.5) / n[0], (j + 0.5) / n[1], (k + 0.5) / n[2])
            for sx, sy, sz, sr in rows:
                d = [f[0] - sx, f[1] - sy, f[2] - sz]
                d = [x - round(x) for x in d]
                c = cart(M, d)
                if c[0] ** 2 + c[1] ** 2 + c[2] ** 2 <= sr * sr:
                    return True
            return False
        # 과막음: 통로(열린 부분) 격자점이 구 안에 드는 비율 — 0 이어야 통로 흡착을 안 지움
        ch_pts = [p for r in R["chans"] for p in R["comps"][r]]
        ch_in = sum(inside_any(p) for p in ch_pts)
        print(f"  통로 점 {len(ch_pts)} 중 막음 구 안 {ch_in} ({100*ch_in/max(1,len(ch_pts)):.2f} %) — 과막음 지표")
        for r in sorted(R["pockets"], key=lambda r: -len(R["comps"][r])):
            pts = R["comps"][r]
            inside = 0
            for p in pts:
                i, rem = divmod(p, n[1] * n[2]); j, k = divmod(rem, n[2])
                f = ((i + 0.5) / n[0], (j + 0.5) / n[1], (k + 0.5) / n[2])
                hit = False
                for sx, sy, sz, sr in rows:
                    d = [f[0] - sx, f[1] - sy, f[2] - sz]
                    d = [x - round(x) for x in d]
                    c = cart(M, d)
                    if c[0] ** 2 + c[1] ** 2 + c[2] ** 2 <= sr * sr:
                        hit = True; break
                inside += hit
            # 주머니 중심(첫 점 기준 최소상 평균)
            i, rem = divmod(pts[0], n[1] * n[2]); j, k = divmod(rem, n[2])
            f0 = ((i + 0.5) / n[0], (j + 0.5) / n[1], (k + 0.5) / n[2])
            print(f"    주머니 점 {len(pts):5d} · 막음 구 안 {inside:5d} ({100*inside/len(pts):5.1f} %) · 한 점 {tuple(round(x,3) for x in f0)}")


if __name__ == "__main__":
    main()
