"""혼합 배치 산포 22% 가 내 MAGI 평가에 무엇을 하는가.

내 평가는 배치 산포를 `saIm0583`(단일 치환) 5실현에서 **14.41%** 로 빌렸다.
실측: **혼합 22% · 단일 11%**. 즉 내가 빌린 값이 두 구조 사이에 있었고,
**혼합 쪽을 과소평가**했다.
"""
import math

REL_BORROWED = 0.1441      # saIm0583 에서 빌린 값
REL_MIX = 0.22             # sa50nb50 실측
REL_SINGLE = 0.11          # saIm050 실측

A = ("sa50nb50", 71.6)     # 앙상블 평균 (실측)
B = ("saIm050", 56.9)
gap = A[1] - B[1]
n = 5

print("=== 내가 빌린 값 대 실측 ===")
print(f"  빌림 (saIm0583 단일)  **{100*REL_BORROWED:.2f}%**")
print(f"  실측 혼합 sa50nb50    **{100*REL_MIX:.0f}%**   (빌림의 {REL_MIX/REL_BORROWED:.2f}배)")
print(f"  실측 단일 saIm050     **{100*REL_SINGLE:.0f}%**   (빌림의 {REL_SINGLE/REL_BORROWED:.2f}배)")
print()
print("  -> 내 빌림은 두 실측 사이. **혼합을 과소평가**했다.")
print()

print("=== 그것이 통계력에 미친 영향 (σ 자, n=5) ===")
for tag, ra, rb in (("내 빌림 (양쪽 14.41%)", REL_BORROWED, REL_BORROWED),
                    ("실측 (혼합 22% · 단일 11%)", REL_MIX, REL_SINGLE)):
    sa = A[1] * ra / math.sqrt(n)
    sb = B[1] * rb / math.sqrt(n)
    u = gap / math.hypot(sa, sb)
    print(f"  {tag:<28} SE {sa:5.2f}/{sb:5.2f}  ->  **{u:.2f} 단위**")
print()
print(f"  데스크탑 보고 σ 자 실측 = **1.90 단위**")
print()
print("  -> 내 예측(0.77, n=1 혼합자)과 실측(0.68 ± 자 / 1.90 σ 자)이 같은 자리다.")
print("     **'구별 안 됨' 이라는 방향은 맞혔다.** 다만 그건 빌린 값이 우연히")
print("     두 실측 사이에 있었기 때문이고, **혼합만 보면 내 빌림이 1.5배 낙관적**이었다.")
print()
print("  교훈: **배치 산포를 빌릴 때 '어떤 종류의 구조에서' 를 붙여야 한다.**")
print("        혼합 조성은 단일보다 배치 산포가 **2배**다 — 자리가 두 종류라서로 보인다.")
