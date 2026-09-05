"""자 섞임의 방향 — "보수적" 이 맞는가.

확정된 것:
  run_aryl_gcmc.py:parse   RASPA `+/-` 를 **그대로** 받는다 (나누지 않음)
  run_water_chunked.py:14  RASPA `±` = **SEM × 2.776** = t(0.975,4) **95% CI**
  -> results_v3.json 의 0.45 / 13.72 는 **95% CI**. 내 s_rep 은 **1σ**. **섞였다.**

LOWRH_18_ANALYSIS.md:26 의 "2.776 으로 나눈" 은 **그 표에만** 해당한다 —
데스크탑 말이 맞고 내 정정이 과했다.

이제 방향을 본다: 섞은 것이 정말 보수적인가?
"""
import math

mb, ms = 19.84, 142.01          # 내 5실현 평균
pb, ps = 0.45, 13.72            # 등재 ± = **95% CI**
sb, ss = 0.207, 3.612           # 내 s_rep = **1σ**
T = 2.776                       # t(0.975, 4)
gap = ms - mb


def units(eb, es):
    return gap / math.hypot(eb, es)


print("셋을 같은 자로 맞춰 본다 (분자는 모두 동일, 차 %.2f)" % gap)
print()
mix_b, mix_s = math.hypot(pb, sb), math.hypot(ps, ss)
print(f"  (섞음, 내가 낸 것)  95%CI + 1σ")
print(f"     ±' {mix_b:.3f} / {mix_s:.3f}   ->  **{units(mix_b, mix_s):.2f} 단위**")

ci_b, ci_s = math.hypot(pb, sb * T), math.hypot(ps, ss * T)
print(f"  (A) 전부 **95% CI** — s_rep 에 2.776 곱")
print(f"     ±' {ci_b:.3f} / {ci_s:.3f}   ->  **{units(ci_b, ci_s):.2f} 단위**")

sg_b, sg_s = math.hypot(pb / T, sb), math.hypot(ps / T, ss)
print(f"  (B) 전부 **1σ** — 블록 ± 를 2.776 으로 나눔")
print(f"     ±' {sg_b:.3f} / {sg_s:.3f}   ->  **{units(sg_b, sg_s):.2f} 단위**")

print()
print("  단위가 작을수록 통과하기 어렵다(= 보수적).")
u_mix, u_ci, u_sg = units(mix_b, mix_s), units(ci_b, ci_s), units(sg_b, sg_s)
order = sorted([("섞음", u_mix), ("전부 95%CI", u_ci), ("전부 1σ", u_sg)],
               key=lambda x: x[1])
print("  보수적인 순: " + "  <  ".join(f"{n} {v:.2f}" for n, v in order))
print()
if u_mix > u_ci:
    print("  -> **섞은 것은 전부 95%CI 보다 덜 보수적이다.**")
    print("     '방향이 보수적' 은 **1σ 기준으로만** 참이고, 95%CI 기준으로는 반대다.")
print()
print("  판정(문턱 1.5)은 셋 다 크게 넘으므로 **안 바뀐다.** 다만 문서에")
print("  '보수적' 이라고만 적으면 **어느 자 기준인지가 빠진다.**")
