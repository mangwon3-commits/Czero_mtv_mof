"""T-4 도달 가능성 — 데스크탑이 결과 전에 등록한 두 기준 (11cd13d).

마스크(ACCESSIBLE_MIN=3.0)를 걷는다. 그건 등록 사항이 아니라 T-6 겹침용
구현값이었고, T-4 문턱과 같은 3.0 이라 시험을 봉쇄했다.

치환기 O/N 3 Å 이내 복셀 중
  (가) 밀도가 0 이 아닌 복셀이 존재하는가          <- 표본기가 실제로 방문했는가
  (나) 밀도가 접근가능 복셀 중앙값 이상인 복셀이 존재하는가

  둘 다 예    -> 도달 가능 -> 등록 통계 그대로 T-4 판정
  둘 다 아니오 -> 판정 불가
  갈리면      -> 유보

⚠ 먼저 확인할 것: (나)의 기준선이 **0 이면 문턱이 무의미**해진다.
   그러면 (나)는 (가)와 같은 검사가 되므로 그 사실을 보고한다.
"""
import sys, os, numpy as np
sys.path.insert(0, "/home/leehk/mof_project/21_ZIF69_MTV")
os.chdir("/home/leehk/mof_project/21_ZIF69_MTV")
import overlap_density as od
from ase.io import read
from scipy.spatial import cKDTree

SRC = {
    "base":    ("water_runs_density_v3/rh90_base/VTK/System_0/COMDensityProfile_water.vtk",
                "최종판"),
    "nbIm025": ("density_grids_rescue/rh90_nbIm025/COMDensityProfile_water.vtk",
                "14,500 사이클판"),
    "saIm050": ("density_grids_rescue/saIm050_hardlink/COMDensityProfile_water.vtk",
                "진행 중 스냅 — 잠정"),
}

print("T-4 도달 가능성 검사 (데스크탑 등록 11cd13d, 마스크 걷음)")
print()
for name, (p, note) in SRC.items():
    if not os.path.exists(p):
        print(f"[{name}] 격자 없음"); continue
    a = read(f"charged_v3/{name}_DDEC6.cif")
    sel = od.substituent_ON(a)
    cell = np.array(a.get_cell())
    g, L, dims = od.read_vtk_grid(p)
    v = g.reshape(-1).astype(float)

    idx = np.stack(np.meshgrid(*[np.arange(d) for d in dims], indexing="ij"), -1)
    reps = np.round(L / a.get_cell().lengths())
    cart = (np.mod(idx.reshape(-1, 3) / dims * reps, 1.0)) @ cell
    sh = np.array([[i, j, k] for i in (-1, 0, 1)
                   for j in (-1, 0, 1) for k in (-1, 0, 1)])
    fp = a.get_scaled_positions() % 1.0
    d_fw, _ = cKDTree(((fp[None] + sh[:, None]) @ cell).reshape(-1, 3)).query(cart, k=1)
    fs = a.get_scaled_positions()[sel] % 1.0
    d_sub, _ = cKDTree(((fs[None] + sh[:, None]) @ cell).reshape(-1, 3)).query(cart, k=1)

    acc = d_fw > 3.0                      # 기준선 모집단 (등록 문구 그대로)
    med = float(np.median(v[acc]))
    near = d_sub <= 3.0

    n_near = int(near.sum())
    n_nz = int((near & (v > 0)).sum())
    n_ge = int((near & (v >= med)).sum())
    ga = n_nz > 0
    na = n_ge > 0 and med > 0

    print(f"[{name}]  {note}")
    print(f"   3 Å 이내 복셀 {n_near:,}개   접근가능 중앙값 = **{med:.6f}**"
          f"{'   ⚠ 0 이라 (나)가 (가)와 같아짐' if med <= 0 else ''}")
    print(f"   (가) 밀도 0 아닌 복셀   {n_nz:,}개  ->  **{'예' if ga else '아니오'}**")
    print(f"   (나) 중앙값 이상 복셀   {n_ge:,}개  ->  "
          f"**{'예' if na else ('판정불가(기준선 0)' if med <= 0 else '아니오')}**")
    if n_nz:
        vv = v[near & (v > 0)]
        print(f"        3 Å 이내 밀도: 최대 {vv.max():.4f}, 합 {vv.sum():.1f}, "
              f"전체 대비 {100*vv.sum()/v.sum():.2f}%")
    print()
