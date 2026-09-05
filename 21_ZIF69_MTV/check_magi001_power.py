"""MAGI-001 실용 평가 — 10건이 답을 낼 수 있는가.

핵심 질문 둘:
  (가) 배치 산포를 넣으면 §3 의 "+2.92 단위" 가 얼마로 줄어드나
  (나) 5실현씩이면 그것을 다시 몇 단위까지 회복하나
근거: results_v3ens0583.json — 저장소에서 **선택도 배치 산포를 실제로 잰 유일한 자료**
"""
import math
import numpy as np

# saIm0583 5실현 실측 (results_v3ens0583.json)
ens = np.array([71.25, 58.73, 61.91, 78.34, 55.67])
ens_err = np.array([4.14, 4.17, 1.61, 5.84, 1.79])
S_BATCH = ens.std(ddof=1)          # 9.39
STAT = ens_err.mean()              # 3.51

# 비교 대상 (MULTILIGAND §3, 단일 실현)
A = ("sa50nb50", 75.8, 3.0)
B = ("saIm050", 65.2, 2.1)
gap = A[1] - B[1]

print(f"배치 산포 실측 (saIm0583 5실현)  SD = **{S_BATCH:.2f}**  "
      f"통계오차 평균 {STAT:.2f}  ->  **{S_BATCH/STAT:.1f}배**")
print(f"  범위 {ens.min():.2f} ~ {ens.max():.2f}   폭 **{ens.max()-ens.min():.1f}**")
print()

print("=== (가) 지금 인용되는 +2.92 단위는 배치 산포를 안 넣은 값 ===")
u_now = gap / math.hypot(A[2], B[2])
print(f"  {A[0]} {A[1]} ± {A[2]}  대  {B[0]} {B[1]} ± {B[2]}   차 {gap:.1f}")
print(f"  통계오차만       -> **{u_now:.2f} 단위**   (MULTILIGAND §3 의 +2.92)")
ca = math.hypot(A[2], S_BATCH)
cb = math.hypot(B[2], S_BATCH)
u_batch = gap / math.hypot(ca, cb)
print(f"  배치 산포 포함   -> ±' {ca:.2f} / {cb:.2f}  ->  **{u_batch:.2f} 단위**")
print(f"  -> **{u_now/u_batch:.1f}배 줄어든다. 문턱 1.5 아래다.**")
print()

print("=== (나) 5실현씩 재면 얼마까지 회복되나 ===")
for n in (1, 3, 5, 8, 16):
    se = math.hypot(S_BATCH, STAT) / math.sqrt(n)
    u = gap / math.hypot(se, se)
    mark = "  <- 이번 10건" if n == 5 else ""
    print(f"  n={n:>2} 실현/구조   평균의 SE {se:5.2f}   -> **{u:5.2f} 단위**{mark}")
print()
print("  -> **5실현이면 약 1.7 단위. 문턱 1.5 를 겨우 넘는 자리다.**")
print("     3 단위를 원하면 구조당 16실현이 필요하고, 그건 지어 놓은 것이 없다.")
print()

print("=== 비용 (데스크탑 8코어) ===")
print("  필요한 것: 10구조 × {CO2, N2} Widom = **20건**")
print("  ⚠ 데스크탑 비용은 **아무도 안 쟀다**. 내 laptop2 실측은 옮길 수 없다")
print("     (검사 6-2: 기기·동시성·구조·조건 네 축).")
print("  참고만: laptop2 6병렬 Widom base 56.8분 · saIm100 67.3분")
print("          데스크탑 자기 기록 물 Widom 8워커 약 50분/건")
print(f"  파도 수  ⌈20/8⌉ = **3 파도** (⌈⌉ — 오늘 내가 3.17 로 세서 틀렸다)")
for m in (50, 60, 70):
    print(f"    건당 {m}분 가정 -> 3 × {m} = **{3*m}분 = {3*m/60:.1f}시간**")
print("  -> **1건 먼저 재고 나머지를 걸면 그 불확실성이 사라진다.**")
