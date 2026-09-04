"""T-6 (가) 호환성 검사 — 데스크탑 CO2 격자와 이쪽 물 격자가 같은 자인가.

read_vtk_grid 는 헤더의 **길이 3개만** 읽고 **각도는 버린다**. 각도는 CIF 에서
온다. 둘이 어긋나면 조용히 틀린 값이 나오므로 여기서 직접 대조한다.
"""
import sys, os, gzip, numpy as np
sys.path.insert(0, "/home/leehk/mof_project/21_ZIF69_MTV")
os.chdir("/home/leehk/mof_project/21_ZIF69_MTV")
import overlap_density as od
from ase.io import read


def vtk_header(path):
    op = gzip.open if path.endswith(".gz") else open
    with op(path, "rt") as f:
        h = [f.readline() for _ in range(6)]
    cp = [float(x) for x in h[1].split()[1:7]]
    dims = [int(x) for x in h[4].split()[1:4]]
    return np.array(cp), np.array(dims)


print("=== T-6 (가) 호환성 — 데스크탑 CO2 대 laptop2 물 ===")
ok = True
for name in ("base", "nbIm025", "saIm050"):
    print(f"\n[{name}]")
    pc = f"density_v3/{name}__q_on/VTK/System_0/COMDensityProfile_CO2.vtk.gz"
    pw = f"water_runs_density_v3/rh90_{name}/VTK/System_0/COMDensityProfile_water.vtk"
    a = read(f"charged_v3/{name}_DDEC6.cif")
    cif = np.array(a.cell.cellpar())
    print(f"   CIF (단위셀)        {cif[0]:.4f} {cif[1]:.4f} {cif[2]:.4f}"
          f"  {cif[3]:.1f} {cif[4]:.1f} {cif[5]:.1f}")
    if not os.path.exists(pc):
        print("   CO2 격자 없음"); ok = False; continue
    cc, dc = vtk_header(pc)
    print(f"   데스크탑 CO2 (2x2x2) {cc[0]:.4f} {cc[1]:.4f} {cc[2]:.4f}"
          f"  {cc[3]:.1f} {cc[4]:.1f} {cc[5]:.1f}   격자 {dc}")
    if not os.path.exists(pw):
        print("   ** 이쪽 물 격자 아직 없음 (평형화 중) — 완주 후 재검사 **"); continue
    cw, dw = vtk_header(pw)
    print(f"   laptop2 물  (2x2x2) {cw[0]:.4f} {cw[1]:.4f} {cw[2]:.4f}"
          f"  {cw[3]:.1f} {cw[4]:.1f} {cw[5]:.1f}   격자 {dw}")
    same_cell = np.allclose(cc, cw, atol=1e-4)
    same_dims = (dc == dw).all()
    reps = cc[:3] / cif[:3]
    same_ang = np.allclose(cc[3:], cif[3:], atol=1e-3)
    print(f"   셀 일치 {same_cell}   격자 일치 {same_dims}   "
          f"각도가 CIF 와 일치 {same_ang}   복제수 {np.round(reps, 4)}")
    if not (same_cell and same_dims and same_ang
            and np.allclose(reps, np.round(reps), atol=1e-4)):
        print("   ** 불일치 — T-6 에 그대로 쓰면 안 된다 **"); ok = False
    else:
        print("   -> 같은 자. T-6 (가) 에 그대로 쓸 수 있다.")
print("\n전체:", "통과" if ok else "**확인 필요**")
