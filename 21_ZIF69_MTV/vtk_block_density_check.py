#!/usr/bin/env python3
"""막음 구 안 밀도 몫(클라우드 검증석 7 · 8회차) — RASPA COM 밀도 VTK(STRUCTURED_POINTS, 초격자) 와
Zeo++ `.block` 구(단위셀 분수 좌표 · 반지름 Å)를 겹쳐, 구 부피 몫 · 구 안 밀도 몫 · 농축 배수를 셈. 표준 파이썬만.

  python vtk_block_density_check.py <file.vtk.gz> <ref:path/to.block | local.block> [--rep 1,2,3]

격자점 좌표 규약은 f = i/N(점 = 칸 모서리). (i+0.5)/N 규약과는 구 부피 몫이 0.1 %p 안팎 다름.
"""
import gzip, math, subprocess, sys


def load_vtk(p):
    op = gzip.open if p.endswith(".gz") else open
    with op(p, "rt") as f:
        hdr = [next(f) for _ in range(10)]
        cp = [float(x) for x in hdr[1].split()[1:]]
        dims = [int(x) for x in hdr[4].split()[1:]]
        vals = [float(l) for l in f if l.strip()]
    return cp, dims, vals


def mat(a, b, c, al, be, ga):
    al, be, ga = map(math.radians, (al, be, ga))
    cx = c * math.cos(be)
    cy = c * (math.cos(al) - math.cos(be) * math.cos(ga)) / math.sin(ga)
    cz = math.sqrt(c * c - cx * cx - cy * cy)
    return ((a, 0, 0), (b * math.cos(ga), b * math.sin(ga), 0), (cx, cy, cz))


def spheres(src, rep):
    if ":" in src and not src.startswith("/"):
        ref, path = src.split(":", 1)
        txt = subprocess.run(["git", "show", f"{ref}:{path}"], capture_output=True, text=True).stdout
    else:
        txt = open(src).read()
    s = [list(map(float, l.split())) for l in txt.strip().splitlines()[1:] if l.strip()]
    return [((x + i) / rep[0], (y + j) / rep[1], (z + k) / rep[2], r)
            for x, y, z, r in s for i in range(rep[0]) for j in range(rep[1]) for k in range(rep[2])]


def frac(vtk, S):
    cp, n, v = load_vtk(vtk)
    M = mat(*cp)
    tot = sum(v); inside = 0.0; nin = 0
    for idx, val in enumerate(v):
        i = idx % n[0]; j = (idx // n[0]) % n[1]; k = idx // (n[0] * n[1])
        f = (i / n[0], j / n[1], k / n[2])
        for sx, sy, sz, r in S:
            d = [f[0] - sx, f[1] - sy, f[2] - sz]
            d = [t - round(t) for t in d]
            cx = d[0] * M[0][0] + d[1] * M[1][0] + d[2] * M[2][0]
            cy = d[0] * M[0][1] + d[1] * M[1][1] + d[2] * M[2][1]
            cz = d[0] * M[0][2] + d[1] * M[1][2] + d[2] * M[2][2]
            if cx * cx + cy * cy + cz * cz <= r * r:
                nin += 1; inside += val
                break
    return nin / len(v), inside, tot


if __name__ == "__main__":
    a = sys.argv
    rep = tuple(int(x) for x in a[a.index("--rep") + 1].split(",")) if "--rep" in a else (1, 2, 3)
    vf, ins, tot = frac(a[1], spheres(a[2], rep))
    print(f"구 부피 {100*vf:.1f} % · 구 안 밀도 {100*ins/tot if tot else 0:.2f} % ({ins:.4g}/{tot:.4g}) · 농축 {((ins/tot)/vf) if (vf and tot) else 0:.2f}배")
