"""겹침 O 의 표본 잡음 — base 재실행 13 스냅샷으로 잰다.

같은 실행의 서로 다른 표본량이므로 **씨앗 잡음이 아니라 표본 잡음**이다.
따라서 실제 실행 간 산포의 **하한**이다. 그래도 "예측 차 0.0518 이 잡음보다
큰가" 의 최소한의 대답은 된다.

데스크탑이 T-B2 X 축에서 한 것과 같은 수법 — 반복이 없을 때 천장을 재기.
"""
import sys, os, glob, re, numpy as np
sys.path.insert(0, "/home/leehk/mof_project/21_ZIF69_MTV")
os.chdir("/home/leehk/mof_project/21_ZIF69_MTV")
import overlap_density as od
from ase.io import read

a = read("charged_v3/base_DDEC6.cif")
gc, Lc, dc = od.read_vtk_grid("density_v3/base__q_on/VTK/System_0/COMDensityProfile_CO2.vtk.gz")

snaps = sorted(glob.glob("density_grids_rescue/base_snapshots/water_*.vtk"))
rows = []
acc = cart = None
for p in snaps:
    t = re.search(r"water_(\d+)\.vtk", p).group(1)
    try:
        gw, Lw, dw = od.read_vtk_grid(p)
    except ValueError as e:
        # 쓰기 도중에 복사되어 잘린 판. 스냅 방식의 실제 위험이고 버린다.
        print("  [잘림 제외] " + t + "  " + str(e).split(": ")[-1])
        continue
    if acc is None:
        acc, cart, _ = od.accessible_mask(a, dw, Lw)
        p_c = od.normalise(gc, acc)
    v = gw.reshape(-1)
    nz = v[v > 0]
    Nmax = 1 / nz.min() if len(nz) else 0
    O, _ = od.overlap(p_c, od.normalise(gw, acc))
    rows.append((t, Nmax, O))

# 최종판도
gwf, Lf, df = od.read_vtk_grid("density_grids_final/COMDensityProfile_water__base.vtk.gz")
Of, _ = od.overlap(p_c, od.normalise(gwf, acc))
vf = gwf.reshape(-1); rows.append(("최종", 1 / vf[vf > 0].min(), Of))

print(f"{'스냅':>6}{'N_max':>9}{'O(base)':>10}{'최종과 차':>11}")
print("-" * 38)
for t, n, O in rows:
    print(f"{t:>6}{n:>9,.0f}{O:>10.4f}{O-Of:>11.4f}")
print("-" * 38)

late = [O for t, n, O in rows if n >= 0.7 * rows[-1][1]]
arr = np.array(late)
print(f"  후반부({len(late)}개, N_max >= 최종의 70%) O 산포:")
print(f"    범위 {arr.min():.4f} ~ {arr.max():.4f}   폭 **{arr.max()-arr.min():.4f}**")
print(f"    표준편차 **{arr.std(ddof=1):.4f}**")
print()
print(f"  예측 대조 차이  O(saIm050) - O(base) = 0.3205 - 0.2688 = **0.0518**")
print(f"  -> 표본 잡음 SD 의 **{0.0518/arr.std(ddof=1):.1f}배**"
      if arr.std(ddof=1) > 0 else "")
print()
print("  ⚠ 이것은 **표본 잡음**이지 씨앗 잡음이 아니다(같은 실행).")
print("     실제 실행 간 산포는 이보다 크며 측정된 바 없다. **하한**으로만 읽을 것.")
