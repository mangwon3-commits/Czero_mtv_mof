"""⚠ T-6 예측 검정의 교란 — O 가 표본량에 따라 아직 오른다.

base 13 스냅에서 O 가 N_max 1,728 -> 3,041 동안 0.2547 -> 0.2688 로 **단조 증가**.
수렴하지 않았다. 그런데 비교 대상의 표본량이 크게 다르다:

    base     N_max  3,041      saIm050  N_max **19,150**   (6.3배)
    nbIm025  N_max  5,118

**O 가 표본량과 함께 오르는데 표본량이 6.3배 다르면, 관측된 차이가 구조 때문인지
표본량 때문인지 갈리지 않는다.** 예측이 "맞았다" 고 말하기 전에 이걸 봐야 한다.

여기서는 base 의 O(N_max) 추세를 외삽해 **saIm050 수준의 표본량이면 base 의 O 가
얼마가 되는지**를 본다. 외삽이므로 확정이 아니라 **교란의 크기 추정**이다.
"""
import sys, os, glob, re, numpy as np
sys.path.insert(0, "/home/leehk/mof_project/21_ZIF69_MTV")
os.chdir("/home/leehk/mof_project/21_ZIF69_MTV")
import overlap_density as od
from ase.io import read

a = read("charged_v3/base_DDEC6.cif")
gc, _, _ = od.read_vtk_grid("density_v3/base__q_on/VTK/System_0/COMDensityProfile_CO2.vtk.gz")

xs, ys = [], []
acc = None
for p in sorted(glob.glob("density_grids_rescue/base_snapshots/water_*.vtk")):
    try:
        gw, Lw, dw = od.read_vtk_grid(p)
    except ValueError:
        continue
    if acc is None:
        acc, _, _ = od.accessible_mask(a, dw, Lw)
        p_c = od.normalise(gc, acc)
    v = gw.reshape(-1); nz = v[v > 0]
    xs.append(1 / nz.min())
    ys.append(od.overlap(p_c, od.normalise(gw, acc))[0])

gwf, _, _ = od.read_vtk_grid("density_grids_final/COMDensityProfile_water__base.vtk.gz")
vf = gwf.reshape(-1)
xs.append(1 / vf[vf > 0].min())
ys.append(od.overlap(p_c, od.normalise(gwf, acc))[0])

x = np.log(np.array(xs)); y = np.array(ys)
b, c = np.polyfit(x, y, 1)
r = np.corrcoef(x, y)[0, 1]

print("base 의 O 대 log(N_max) 회귀")
print(f"  기울기 **{b:+.5f} / e배**   절편 {c:.4f}   r = {r:+.4f}  (n={len(x)})")
print(f"  N_max 3,041 에서 O = {b*np.log(3041)+c:.4f}  (실측 {ys[-1]:.4f})")
print()
for tgt, nm in ((5118, "nbIm025 수준"), (19150, "saIm050 수준")):
    pred = b * np.log(tgt) + c
    print(f"  **base 를 N_max {tgt:,} ({nm})까지 외삽하면 O = {pred:.4f}**")
print()
print("  실측:  base 0.2688   nbIm025 0.3356   saIm050 0.3205")
print()
b50 = b * np.log(19150) + c
print(f"  saIm050 수준으로 맞춘 base = {b50:.4f}  대  saIm050 실측 0.3205")
print(f"  -> 차이가 {0.3205-0.2688:+.4f} 에서 **{0.3205-b50:+.4f}** 로 줄어든다")
if b50 >= 0.3205:
    print("  -> **표본량 보정만으로 부호가 뒤집힌다. 예측 검정이 성립하지 않는다.**")
else:
    print(f"  -> 부호는 남으나 크기가 {(0.3205-0.2688)/(0.3205-b50):.1f}배 줄어든다")
print()
print("  ⚠ 외삽이다. base 는 N_max 3,041 까지만 관측됐고 그 위는 자료가 없다.")
print("     O 가 어디선가 평평해지면 이 추정은 과대평가다. **확정이 아니라 경보다.**")
