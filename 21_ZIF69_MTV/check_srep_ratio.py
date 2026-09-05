"""등재 단일 실현값이 내 5실현 안에서 어디에 있는가 — 배율에 미치는 영향."""
import numpy as np, math

base = np.array([19.88, 19.82, 19.95, 19.50, 20.05])
sa = np.array([142.35, 138.88, 147.99, 139.58, 141.24])
REF = {"base": (20.10, 0.45), "saIm100": (150.91, 13.72)}

print("=== 등재값이 5실현 안 어디인가 ===")
for nm, arr in (("base", base), ("saIm100", sa)):
    ref, refpm = REF[nm]
    m, s = arr.mean(), arr.std(ddof=1)
    z = (ref - m) / s
    above = (arr < ref).sum()
    print(f"  {nm:<9} 5실현 {arr.min():.2f}~{arr.max():.2f}  평균 {m:.2f}  s_rep {s:.2f}")
    print(f"            등재 **{ref:.2f}**  ->  평균에서 **+{z:.2f}σ**,"
          f"  5실현 중 **{above}개보다 큼**"
          + ("  ← **전부보다 큼**" if above == len(arr) else ""))

print()
print("=== 배율 ===")
rb, rs = REF["base"][0], REF["saIm100"][0]
mb, ms = base.mean(), sa.mean()
sb, ss = base.std(ddof=1), sa.std(ddof=1)
cb = math.hypot(REF["base"][1], sb)
cs = math.hypot(REF["saIm100"][1], ss)

print(f"  등재 단일 실현      {rs:.2f} / {rb:.2f} = **{rs/rb:.2f}배**")
print(f"  내 5실현 평균       {ms:.2f} / {mb:.2f} = **{ms/mb:.2f}배**")
print(f"  차                  {rs/rb - ms/mb:+.2f}배")
print()
# 배율의 오차 (상대오차 전파)
r = ms / mb
er = r * math.hypot(cs / ms, cb / mb)
print(f"  실측 배율의 결합 오차  {r:.2f} ± **{er:.2f}**")
print(f"  등재 배율 {rs/rb:.2f} 는 그 안에서 **{abs(rs/rb - r)/er:.2f}σ**")
print()
print("  -> 두 값은 통계적으로 구별되지 않는다. 다만 **등재 점추정이 높은 쪽**이고,")
print("     saIm100 등재값은 내 5실현 **전부보다 큽니다.**")
