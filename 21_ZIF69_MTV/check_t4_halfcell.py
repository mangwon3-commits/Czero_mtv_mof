"""동률 8개가 병진으로 이어지는가 — 데스크탑 주장을 내 격자에서 독립 확인.

주장: 동률 복셀의 분율좌표가 각 축에서 정확히 두 값이고 간격이 0.500.
      -> 2x2x2 반셀 병진, 2^3 = 8. 경쟁 자리가 아니라는 것이 개수가 아니라
         **구조**로 나온다. 거리 범위 0 은 그 따름정리다.

간격이 세 축 모두 정확히 0.500 이면 분율좌표 환원도 옳다(정방정계 가정이
남아 있었으면 깨진다). 판정과 무관한 축에서 나온 확인이다.
"""
import sys, os, numpy as np
sys.path.insert(0, "/home/leehk/mof_project/21_ZIF69_MTV")
os.chdir("/home/leehk/mof_project/21_ZIF69_MTV")
import overlap_density as od

G = {
    "base":    "density_grids_final/COMDensityProfile_water__base.vtk.gz",
    "nbIm025": "density_grids_final/COMDensityProfile_water__nbIm025.vtk.gz",
    "saIm050": "density_grids_final/COMDensityProfile_water__saIm050.vtk.gz",
}

for name, p in G.items():
    g, L, dims = od.read_vtk_grid(p)
    v = g.reshape(-1)
    nz = v[v > 0]
    Nmax = 1 / nz.min()
    tie = np.where(v * Nmax >= Nmax - np.sqrt(Nmax))[0]

    idx = np.stack(np.meshgrid(*[np.arange(d) for d in dims], indexing="ij"), -1)
    frac = (idx.reshape(-1, 3) / dims)[tie]          # 슈퍼셀 분율좌표

    print(f"[{name}]  N_max {Nmax:,.0f}   동률 **{len(tie)}개**")
    ok = True
    for ax in range(3):
        u = np.unique(np.round(frac[:, ax], 6))
        gap = np.diff(u)
        good = len(u) == 2 and abs(gap[0] - 0.5) < 1e-6
        ok &= good
        print(f"   축{ax}  값 {{{', '.join('%.3f' % x for x in u)}}}"
              f"   간격 {gap[0] if len(gap) else float('nan'):.6f}"
              f"   {'OK' if good else '**어긋남**'}")
    print(f"   -> 2×2×2 반셀 병진 {'**확인** (2³ = 8)' if ok else '**아님**'}")
    print()
print("간격이 세 축 모두 정확히 0.500 이면 분율좌표 환원이 옳다.")
print("정방정계 가정이 남아 있었으면 육방 셀에서 이 값이 깨진다.")
