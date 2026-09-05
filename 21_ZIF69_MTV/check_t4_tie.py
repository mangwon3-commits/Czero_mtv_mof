"""③ 분모의 정체 + ② 최대 피크가 결정된 위치인가 (데스크탑 등록, 수 보기 전).

③ 내가 "원계수" 라고 부른 3,041 은 **총 계수가 아니라 최대 복셀의 계수**다.
   격자는 max=1 로 정규화되므로 최소 단위 = 1/N_max 이고, N_max 는
   **가장 많이 방문된 복셀 한 개의 방문 수**다. 이름이 모호했다 — 5번 사례.

② N_max, n_tie(계수 >= N_max - sqrt(N_max), 푸아송 1σ), d_spread.
"""
import sys, os, numpy as np
sys.path.insert(0, "/home/leehk/mof_project/21_ZIF69_MTV")
os.chdir("/home/leehk/mof_project/21_ZIF69_MTV")
import overlap_density as od
from ase.io import read
from scipy.spatial import cKDTree

SRC = {
    "base":    ("water_runs_density_v3/rh90_base/VTK/System_0/COMDensityProfile_water.vtk", "최종판"),
    "nbIm025": ("density_grids_rescue/rh90_nbIm025/COMDensityProfile_water.vtk", "14,500 사이클판"),
    "saIm050": ("density_grids_rescue/saIm050_hardlink/COMDensityProfile_water.vtk", "진행 중 — 잠정"),
}

print("=== ③ 분모의 정체 ===")
for name, (p, _) in SRC.items():
    if not os.path.exists(p):
        continue
    g, L, dims = od.read_vtk_grid(p)
    v = g.reshape(-1)
    nz = v[v > 0]
    Nmax = 1 / nz.min()
    counts = np.rint(v * Nmax)
    print(f"  {name:<9} 최소단위 1/{Nmax:,.0f}  최대값 {v.max():.4f}"
          f"  0아닌복셀 {len(nz):,}  **계수 총합 {counts.sum():,.0f}**")
print("  -> 1/최소단위 = **최대 복셀 하나의 계수**(N_max). 총 계수는 그보다 훨씬 크다.")
print("     내가 '원계수' 라고 쓴 것이 이 N_max 다. 앞으로 **N_max** 로 적는다.")

print()
print("=== ② 최대 피크가 결정된 위치인가 ===")
print(f"{'구조':<9}{'N_max':>8}{'√N_max':>8}{'문턱계수':>9}{'n_tie':>7}"
      f"{'거리 최소~최대':>18}{'3.0 걸침':>9}")
print("-" * 62)
for name, (p, note) in SRC.items():
    if not os.path.exists(p):
        continue
    a = read(f"charged_v3/{name}_DDEC6.cif")
    sel = od.substituent_ON(a)
    cell = np.array(a.get_cell())
    g, L, dims = od.read_vtk_grid(p)
    v = g.reshape(-1)
    nz = v[v > 0]
    Nmax = 1 / nz.min()
    counts = v * Nmax
    cut = Nmax - np.sqrt(Nmax)
    tie = counts >= cut

    idx = np.stack(np.meshgrid(*[np.arange(d) for d in dims], indexing="ij"), -1)
    reps = np.round(L / a.get_cell().lengths())
    cart = (np.mod(idx.reshape(-1, 3) / dims * reps, 1.0)) @ cell
    sh = np.array([[i, j, k] for i in (-1, 0, 1)
                   for j in (-1, 0, 1) for k in (-1, 0, 1)])
    fs = a.get_scaled_positions()[sel] % 1.0
    d_sub, _ = cKDTree(((fs[None] + sh[:, None]) @ cell).reshape(-1, 3)).query(cart, k=1)

    dt = d_sub[tie]
    cross = "**예**" if (dt.min() <= 3.0 <= dt.max()) else ("전부 3Å내" if dt.max() <= 3.0 else "아니오")
    print(f"{name:<9}{Nmax:>8,.0f}{np.sqrt(Nmax):>8.1f}{cut:>9,.0f}{int(tie.sum()):>7}"
          f"{dt.min():>9.3f}~{dt.max():<8.3f}{cross:>9}")
print("-" * 62)
print("  판정 규칙 (등록): n_tie=1 -> 결정됨, 병기 없음")
print("               n_tie>1 이고 3.0 걸침 -> 미결정 병기, d<=3.0 동률 있으면 판정 불가")
print("               n_tie>1 이나 전부 3.0 밖 -> 판정 유지, n_tie 병기")
