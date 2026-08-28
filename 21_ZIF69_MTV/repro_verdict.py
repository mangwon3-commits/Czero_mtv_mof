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
