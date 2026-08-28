# -*- coding: utf-8 -*-
"""재현성 반복 판정 — 2026-08-29 01:15 등록 (수 보기 전에 작성)
   강하 = 08-24 값 - 오늘 반복 평균.  분모 = R*sqrt(1+1/n).
   합산 = e2/e3/e4 세 구조 강하의 평균, 문턱 1.96*0.005616 = 0.011007 (양측)."""
import glob, json, math, os
import statistics as st

D = os.path.dirname(os.path.abspath(__file__))
R = 0.008424                      # 실행간 SD (saIm0583e1, n=8, dof 7)
SELECTED = {"saIm0583e1", "saIm0583e5"}   # 차가 가장 큰 둘 -> 선택 편향 있음

def Phi(z): return 0.5 * math.erfc(-z / math.sqrt(2))

first = {}
for r in json.load(open(os.path.join(D, "v3_water_ens/water_results.json"))):
    if r.get("RH") == 0.0:
        first[r["name"]] = r["CO2_molkg"]

rep = {}
for p in sorted(glob.glob(os.path.join(D, "v3_water_repro*/water_results.json"))):
    tag = os.path.basename(os.path.dirname(p)).replace("v3_water_repro", "").lstrip("_") or "a"
    try:
        rows = json.load(open(p))
    except Exception:
        continue
    for r in rows:
        if r.get("RH") == 0.0:
            rep.setdefault(r["name"], []).append((tag, r["CO2_molkg"]))

print("=" * 68)
print("재현성 반복 판정   (판정 기준은 2026-08-29 01:15 에 등록, 수 보기 전)")
print("=" * 68)
print("  R = %.6f (n=8, dof 7)" % R)
print()
hdr = "%-12s %9s %9s %3s %9s %8s  %s" % ("구조", "08-24", "오늘평균", "n", "강하", "z", "선택")
print(hdr); print("-" * len(hdr))

drops = {}
for name in sorted(set(first) & set(rep)):
    vs = [v for _, v in rep[name]]
    n = len(vs)
    mu = st.mean(vs)
    drop = first[name] - mu
    s = R * math.sqrt(1 + 1.0 / n)
    drops[name] = (drop, n, s)
    print("%-12s %9.4f %9.4f %3d %+9.5f %+8.2f  %s"
          % (name, first[name], mu, n, drop, drop / s,
             "**선택됨**" if name in SELECTED else "선택 안 됨"))

print()
print("=" * 68)
print("합산 — 선택 안 된 구조만 (편향 없음)")
print("=" * 68)
un = [k for k in sorted(drops) if k not in SELECTED]
if not un:
    print("  아직 없음")
else:
    ds = [drops[k][0] for k in un]
    k = len(ds)
    mean_drop = st.mean(ds)
    # 각 구조 분모가 같다고 보고(모두 n=3) 평균의 분모
    s_each = st.mean([drops[x][2] for x in un])
    s_mean = s_each / math.sqrt(k)
    thr = 1.96 * s_mean
    z = mean_drop / s_mean
    for x in un:
        print("  %-12s 강하 %+.5f  (n=%d)" % (x, drops[x][0], drops[x][1]))
    print()
    print("  구조 %d종   평균 강하 = **%+.5f**" % (k, mean_drop))
    print("  H0 분모 %.6f   문턱 +-%.5f   z = **%+.3f**" % (s_mean, thr, z))
    delta = 0.01229
    pw = Phi(delta / s_mean - 1.96) + Phi(-1.96 - delta / s_mean)
    print("  이 구성의 검정력 (delta=+0.01229 참일 때) = %.1f%%" % (pw * 100))
    print()
    # [01:40 등록 개정 - 아직 수를 안 봤음]  랩탑이 delta_hat 의 95%CI 가 0 을
    # 포함함을 보였습니다(z 1.65, p 0.10). 그러면 검정력이 7%~99.8% 사이에서
    # 안 정해지고, 이분 판정은 거의 뜻이 없습니다. 주 산출을 추정으로 바꿉니다.
    print("  [주 산출] 편향 없는 delta 추정")
    print("    delta_hat(무편향) = **%+.5f**   95%%CI [%+.5f, %+.5f]"
          % (mean_drop, mean_drop - 1.96 * s_mean, mean_drop + 1.96 * s_mean))
    print("    e1/e5 로 잰 편향 있는 추정 +0.01229 [-0.00235, +0.02693] 과 비교하십시오.")
    print()
    print("  [부 산출] 등록 3분기")
    if mean_drop > thr:
        v = "계통 편차 **지지**. 선택 편향 없는 점에서 같은 방향."
    elif mean_drop < -thr:
        v = "**반대 방향**. 계통 편차 기각 쪽."
    else:
        v = ("**미검출**. 그런데 이것을 약한 반증 으로 읽으면 안 됩니다 - "
             "delta 가 점추정(+0.0123) 근처였다면 검정력 59%% 라 약한 반증이지만, "
             "CI 하한 근처였다면 이 시험은 애초에 아무것도 못 잽니다(7%%). "
             "**두 경우를 이 자료로 못 가립니다.**")
    print("    " + v)

print()
print("  * 선택된 e1/e5 의 강하는 29%% 가 평균회귀입니다. 합산에 안 넣었습니다.")
print("  * e2~e4 는 랩탑 쪽이 여전히 1회 추출입니다. 분모의 1 이 그 몫이며")
print("    한 구조 검정력 천장 30.8%% 의 원인입니다.")
print("  * delta 를 **가법**으로 둡니다. 승법이면 e2 87%, e3 101%, e4 104% 라 세 구조")
print("    평균 기대강하가 +0.01229 대신 +0.01196 — 문턱의 3.0% 차이라 무시합니다.")
print("  * delta_hat 자체에도 천장: 오늘 쪽을 무한히 반복해도 SE 는 R/sqrt(2)=%.5f 까지만"
      % (R / math.sqrt(2)))
print("    줄어 z=2.06 (p 0.039). **08-24 쪽이 각 1회 추출인 것이 여기서도 병목입니다.**")

# ===================================================================
# [01:35 등록 추가 — 아직 수를 안 봤음 (완주 0/9)]
#
#   모의 20만 회로 확인: 위 "선택 안 된 셋" 추정량도 **편향돼 있습니다**.
#   뽑힌 둘이 +0.00495 만큼 위로 치우치면, 항등식 2*b_top + 3*b_bot = 0 에
#   의해 안 뽑힌 셋은 **-0.00328 만큼 아래로** 치우칩니다. 문턱 0.011 의 30%.
#
#   해법: **다섯 전부의 단순평균**. 선택은 다섯을 재배치할 뿐 빼지 않으므로
#   E[다섯 평균] = delta 이고 보정이 아예 필요 없습니다. 모의 편차 +0.00001.
#   (참 delta = 0 / 0.01229 / 0.025 모두에서 성립 — delta 무관)
# ===================================================================
print()
print("=" * 68)
print("[주 산출 개정] 다섯 구조 단순평균 — 보정 불필요, 선택 무관")
print("=" * 68)
have = [k for k in ("saIm0583e1", "saIm0583e2", "saIm0583e3",
                    "saIm0583e4", "saIm0583e5") if k in drops]
if len(have) < 5:
    print("  아직 %d/5 — %s 가 없습니다." % (len(have), ", ".join(
        x for x in ("saIm0583e1","saIm0583e2","saIm0583e3","saIm0583e4","saIm0583e5")
        if x not in drops)))
else:
    ds = [drops[k][0] for k in have]
    d5 = sum(ds) / 5.0
    v5 = sum(R * R * (1 + 1.0 / drops[k][1]) for k in have) / 25.0
    s5 = math.sqrt(v5)
    for k in have:
        print("  %-12s 강하 %+.5f  (n=%d)" % (k, drops[k][0], drops[k][1]))
    print()
    print("  **delta_hat(다섯) = %+.5f**   SE %.6f   95%%CI [%+.5f, %+.5f]"
          % (d5, s5, d5 - 1.96 * s5, d5 + 1.96 * s5))
    print("  z = %+.2f   물리적 하한 R/sqrt(5)=%.6f 의 %.0f%% 도달"
          % (d5 / s5, R / math.sqrt(5), R / math.sqrt(5) / s5 * 100))
    print()
    if abs(d5) > 1.96 * s5:
        print("  판정: 0 과 **구별됨** — 08-24 배치에 공통 편차가 있었습니다.")
    else:
        print("  판정: 0 과 **구별 안 됨**.")
        print("        이 추정량은 편향이 없고 SE 가 물리적 하한의 %.0f%% 이므로,"
              % (R / math.sqrt(5) / s5 * 100))
        print("        **이 질문에서 얻을 수 있는 것에 가깝습니다** — 더 돌려도 안 좁아집니다.")
    print()
    print("  [참고] 편향된 두 부분집합 (합산에 쓰지 마십시오)")
    sel = [k for k in have if k in SELECTED]
    uns = [k for k in have if k not in SELECTED]
    ms = sum(drops[k][0] for k in sel) / len(sel)
    mu2 = sum(drops[k][0] for k in uns) / len(uns)
    print("    뽑힌 둘   %+.5f  보정 -0.00495  ->  %+.5f" % (ms, ms - 0.00495))
    print("    안 뽑힌 셋 %+.5f  보정 +0.00328  ->  %+.5f" % (mu2, mu2 + 0.00328))
    print("    다섯 평균  %+.5f  보정 없음     ->  %+.5f" % (d5, d5))
print()
print("  [가중 주의] 반드시 **동일가중**. 정밀도가중은 반복 많은 구조(=선택된 구조)에")
print("    더 실려 편향 +0.00027 을 만들고, 벌어들이는 정밀도는 0.26%% 뿐입니다.")
print("    (모의 20만회: 동일 편향 +0.00001 SD 0.004260 / 정밀도 +0.00027 SD 0.004249)")
print("    **동일가중만 E[다섯평균]=delta 항등식을 지킵니다.**")
print()
print("  [02:20 정정] 역분산 합성 SD 는 0.004491 이 아니라 **0.004254** 입니다")
print("    (0.004491 은 e5 가 n=1 이던 때의 분모에서 나온 낡은 값).")
print("    다섯 동일가중 0.004260 과 **0.14% 차이로 동률**이므로, 다섯을 택하는")
print("    이유는 정밀도가 아니라 **보정이 필요 없다는 것**입니다 — 보정항은")
print("    랩탑 R 을 모르면 최대 40%% 틀리고, 항등식은 그 가정에 안 기댑니다.")
