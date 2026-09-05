"""등재 선택도가 내 실현보다 높은 것이 어디서 오는가 — 분자/분모 분해."""
import numpy as np, math

REF = {"base": dict(co2=5.33337e-05, n2=2.65311e-06, sel=20.1023),
       "saIm100": dict(co2=4.31371e-04, n2=2.85843e-06, sel=150.9119)}
MINE = {"base": dict(co2=np.array([5.29569, 5.26187, 5.29154, 5.20893, 5.30750]) * 1e-5,
                     n2=np.array([2.66352, 2.65503, 2.65245, 2.67091, 2.64755]) * 1e-6),
        "saIm100": dict(co2=np.array([4.08996, 3.94279, 4.24854, 4.01965, 4.04159]) * 1e-4,
                        n2=np.array([2.8390, 2.8798, 2.8571, 2.8621, 2.8864]) * 1e-6)}

print(f"{'구조':<9}{'양':<5}{'등재':>13}{'내 평균':>13}{'내 s_rep':>11}"
      f"{'등재 위치':>11}{'평균비교':>10}")
print("-" * 74)
zs = []
for s in REF:
    for g in ("co2", "n2"):
        v = MINE[s][g]
        m, sd = v.mean(), v.std(ddof=1)
        ref = REF[s][g]
        z1 = (ref - m) / sd                      # 단일 실현 산포 기준
        z2 = (ref - m) / (sd * math.sqrt(1 + 1 / 5))   # 등재도 1실현임을 반영
        if g == "co2":
            zs.append(z2)
        print(f"{s:<9}{g.upper():<5}{ref:>13.5e}{m:>13.5e}{sd:>11.3e}"
              f"{z1:>+10.2f}σ{z2:>+9.2f}σ")

print("-" * 74)
print()
print("  **두 구조 모두 CO₂ 에서 등재가 높고 N₂ 는 0.5σ 안이다.**")
zc = sum(zs) / math.sqrt(len(zs))
print(f"  CO₂ 두 건 결합 z = **+{zc:.2f}σ**  (단측 p ≈ {0.5*math.erfc(zc/math.sqrt(2)):.3f})")
print()
print("  선택도 = CO₂/N₂ 이므로 **분자 쪽 차이가 그대로 선택도 차이**가 된다.")
print("  등재 배율 7.51 대 내 7.16 의 원인이 여기다.")
print()
print("  ⚠ n=2 구조다. 우연일 수 있고, 러너 판본·조건 차이일 수도 있다.")
print("     **관찰로만 적는다.** 판정(8.6 단위, 유지)은 이것과 무관하다.")
