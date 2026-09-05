"""T-4 판정 — 물 밀도 최대 피크가 치환기 O/N 3 Å 이내인가.

등록 사항 (전부 결과 전에 고정됨):
  · 문턱      3 Å  (ASSIGN_20260905 §2)
  · 후보 집합 치환기 O/N = **모든 O + Zn 에 배위하지 않은 N**  (커밋 09241a9)
              원소로 ('O','N') 을 고르면 Zn 배위 N 96개가 섞여 판정이 자동 통과한다
  · 격자      **질량중심(COM)**. 전원자는 TIP5P-Ew 의 질량 없는 L 자리 2개가 섞임
  · 접근가능  골격 원자에서 3.0 Å 초과 (ACCESSIBLE_MIN)

병기 (판정문 필수):
  (가) 세 격자 전부 **실현 1개**, 씨앗이 서로 다름 -> **실행 간 산포 미측정**
  (나) nbIm025 는 **14,500/15,000 사이클** 판 (삭제 사고로 최종 기록 유실)
  (다) base 도 니트로 24개를 가진 구조 -> nbIm025 와의 대비는 '유무' 가 아니라 **+25%**
  (라) 상위 1%·0.1% 분위의 **자리 안정성**을 함께 낸다 (데스크탑 요청)
       — 최강 복셀 하나에 설명을 요구하는 것이 오늘 우리가 밟은 함정이다
"""
import sys, os, glob, numpy as np
sys.path.insert(0, "/home/leehk/mof_project/21_ZIF69_MTV")
os.chdir("/home/leehk/mof_project/21_ZIF69_MTV")
import overlap_density as od
from ase.io import read

THRESH = 3.0
SRC = {
    "base":     "water_runs_density_v3/rh90_base/VTK/System_0/COMDensityProfile_%s.vtk",
    "nbIm025":  "density_grids_rescue/rh90_nbIm025/COMDensityProfile_%s.vtk",
    "saIm050":  "density_grids_rescue/saIm050_hardlink/COMDensityProfile_%s.vtk",
}
NOTE = {
    "base":    "재실행분(최종판), 씨앗 1788559403",
    "nbIm025": "**14,500/15,000 사이클**, 씨앗 1788537975",
    "saIm050": "하드링크 확보(최종판), 씨앗 1788537979",
}


def percentile_sites(g, acc, cart, cell, sel_pos, q):
    """상위 q 분위 복셀 집합의 치환기까지 거리 분포 — 자리 안정성."""
    v = g.reshape(-1).astype(float).copy()
    v[~acc] = -1.0
    thr = np.percentile(v[acc], 100 - q)
    idx = np.where(v >= thr)[0]
    sh = np.array([[i, j, k] for i in (-1, 0, 1)
                   for j in (-1, 0, 1) for k in (-1, 0, 1)])
    pad = ((sel_pos[None] + sh[:, None]) @ cell).reshape(-1, 3)
    from scipy.spatial import cKDTree
    dmin, _ = cKDTree(pad).query(cart[idx], k=1)
    w = v[idx]
    return dmin, w, len(idx)


print("=" * 74)
print("T-4 판정 — 물 밀도 최대 피크에서 치환기 O/N 까지 최단거리 (문턱 3 Å)")
print("=" * 74)

rows = []
for name, note in NOTE.items():
    pw = SRC[name] % "water"
    if not os.path.exists(pw):
        print(f"\n[{name}] 격자 없음: {pw}")
        continue
    a = read(f"charged_v3/{name}_DDEC6.cif")
    sel = od.substituent_ON(a)
    g, L, dims = od.read_vtk_grid(pw)
    acc, cart, _ = od.accessible_mask(a, dims, L)
    cell = np.array(a.get_cell())
    sel_pos = a.get_scaled_positions()[sel] % 1.0

    d, pk, k = od.peak_distance(a, g, acc, cart, sel)
    v = g.reshape(-1)
    ties = int((v[acc] == v[acc].max()).sum())
    nz = v[v > 0]
    raw = round(1 / nz.min()) if len(nz) else 0

    verdict = "**결함형 자리**" if d <= THRESH else "결함형 자리 아님"
    print(f"\n[{name}]  {note}")
    print(f"   치환기 O/N {int(sel.sum())}개   접근가능 복셀 {int(acc.sum()):,}"
          f" ({100*acc.sum()/acc.size:.1f}%)   원계수 ~{raw:,}")
    print(f"   **최대 피크 -> 치환기 최단거리 = {d:.3f} Å**   (피크값 {pk:.4f},"
          f" 최대값 동률 {ties}개)")
    print(f"   판정: 문턱 {THRESH} Å 대비 -> **{verdict}**")

    for q in (1.0, 0.1):
        dm, w, n = percentile_sites(g, acc, cart, cell, sel_pos, q)
        within = 100 * (dm <= THRESH).mean()
        print(f"   상위 {q:>4.1f}% ({n:,}복셀): 거리 중앙값 {np.median(dm):.3f} Å,"
              f" 최소 {dm.min():.3f}, 3 Å 이내 비율 **{within:.1f}%**")
    rows.append((name, d, verdict))

print()
print("=" * 74)
print("요약")
for n, d, v in rows:
    print(f"  {n:<9} {d:6.3f} Å   {v}")
print()
print("병기 (판정문 필수)")
print("  (가) 세 격자 전부 실현 1개, 씨앗 상이 -> **실행 간 산포 미측정**")
print("  (나) nbIm025 는 14,500/15,000 사이클 판")
print("  (다) base 도 니트로 24개 -> nbIm025 대비는 '유무' 아닌 **+25%**")
print("  (라) 최강 복셀 하나가 아니라 상위 분위와 함께 읽을 것")
