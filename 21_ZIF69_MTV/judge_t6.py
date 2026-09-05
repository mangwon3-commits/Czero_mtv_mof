"""T-6 — CO2/H2O 밀도 격자 겹침 적분.

등록 (ASSIGN_20260905 §2):
  (가) **단성분 CO2 격자 × 물 격자**로 판정  <- 주 판독
  (나) 이원 런 겹침을 병기. (나)가 다른 결론이면 그 사실을 T-6' 근거로 보고

겹침 지표 O = sum min(p_CO2, p_H2O), 두 분포를 각각 합 1 로 정규화.
Bhattacharyya 는 참고로만 낸다.

**데스크탑 예측 (WATER_DISPLACEMENT_20260905.md, 결과 전 등록):**
  O(base) < O(치환체).  대조쌍 base 대 saIm050 (물당 손실 0.0197 대 0.3130, 16배)
  맞으면 "물 K_H 가 아니라 자리 겹침이 유지율을 가른다" 가 자료로 섬
  틀리면 겹침 가설을 버림
  ** 이 예측은 (가)에서만 검정한다 ** — (나)는 경쟁이 끝난 뒤의 잔여 공존도라
  부호 모호성이 있다(강한 경쟁도 낮은 겹침, 무경쟁도 낮은 겹침).
  nbIm025 는 RH0 가 물 러너가 아니라 예측 대조에서 제외(T-6 판정에는 포함).
"""
import sys, os, numpy as np
sys.path.insert(0, "/home/leehk/mof_project/21_ZIF69_MTV")
os.chdir("/home/leehk/mof_project/21_ZIF69_MTV")
import overlap_density as od
from ase.io import read

WATER = {
    "base":    "density_grids_final/COMDensityProfile_water__base.vtk.gz",
    "nbIm025": "density_grids_final/COMDensityProfile_water__nbIm025.vtk.gz",
    "saIm050": "density_grids_final/COMDensityProfile_water__saIm050.vtk.gz",
}
CO2_SINGLE = "density_v3/%s__q_on/VTK/System_0/COMDensityProfile_CO2.vtk.gz"
CO2_BINARY = {
    "base":    "density_grids_final/COMDensityProfile_CO2__base.vtk.gz",
    "nbIm025": "density_grids_final/COMDensityProfile_CO2__nbIm025.vtk.gz",
    "saIm050": "density_grids_final/COMDensityProfile_CO2__saIm050.vtk.gz",
}

print("T-6 겹침 적분  O = sum min(p_CO2, p_H2O)")
print()
print(f"{'구조':<10}{'(가) 단성분 CO2':>16}{'(나) 이원 런':>14}{'차이':>10}"
      f"{'  참고 BC(가)':>12}")
print("-" * 62)
res = {}
for name, pw in WATER.items():
    a = read(f"charged_v3/{name}_DDEC6.cif")
    gw, Lw, dw = od.read_vtk_grid(pw)
    acc, cart, _ = od.accessible_mask(a, dw, Lw)
    p_w = od.normalise(gw, acc)

    out = {}
    for tag, path in (("가", CO2_SINGLE % name), ("나", CO2_BINARY[name])):
        if not os.path.exists(path):
            out[tag] = None; continue
        gc, Lc, dc = od.read_vtk_grid(path)
        assert (dc == dw).all() and np.allclose(Lc, Lw, atol=1e-4), \
            f"{name} {tag}: 격자/셀 불일치 {Lc} vs {Lw}"
        p_c = od.normalise(gc, acc)
        O, BC = od.overlap(p_c, p_w)
        out[tag] = (O, BC)
    res[name] = out
    a_ = out.get("가"); b_ = out.get("나")
    sa = f"{a_[0]:.4f}" if a_ else "없음"
    sb = f"{b_[0]:.4f}" if b_ else "없음"
    diff = f"{a_[0]-b_[0]:+.4f}" if (a_ and b_) else "-"
    bc = f"{a_[1]:.4f}" if a_ else "-"
    print(f"{name:<10}{sa:>16}{sb:>14}{diff:>10}{bc:>12}")

print("-" * 62)
print()
print("=== 데스크탑 예측 검정 — (가)에서만 ===")
ga = {k: v.get("가") for k, v in res.items()}
if ga.get("base") and ga.get("saIm050"):
    ob, os_ = ga["base"][0], ga["saIm050"][0]
    print(f"  대조쌍  O(base) = {ob:.4f}   O(saIm050) = {os_:.4f}")
    ok = ob < os_
    print(f"  예측: O(base) < O(치환체)  ->  **{'맞음' if ok else '틀림'}**"
          f"   (차 {os_-ob:+.4f}, 비 {os_/ob:.2f}배)")
    if ok:
        print("  -> 등록대로 '물 K_H 가 아니라 자리 겹침이 유지율을 가른다' 가 자료로 선다")
    else:
        print("  -> 등록대로 **겹침 가설을 버린다**. base 의 낮은 물당 손실은 다른 원인이다")
    if ga.get("nbIm025"):
        print(f"  (참고) nbIm025 O = {ga['nbIm025'][0]:.4f} — 예측 대조에서는 제외"
              f"(RH0 가 물 러너 아님), T-6 판정에는 포함")
print()
print("=== (나)가 다른 결론을 내는가 ===")
na = {k: v.get("나") for k, v in res.items()}
if na.get("base") and na.get("saIm050"):
    nb, ns = na["base"][0], na["saIm050"][0]
    print(f"  O(base) = {nb:.4f}   O(saIm050) = {ns:.4f}  ->  "
          f"base {'<' if nb < ns else '>'} saIm050")
    same = (nb < ns) == (ga['base'][0] < ga['saIm050'][0])
    print(f"  (가)와 방향 {'같음' if same else '**다름 — T-6′ 근거로 보고**'}")
