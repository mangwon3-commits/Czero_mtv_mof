"""T-NF-0q — 기존 T-NF-0k 출력에서 **ΔH 를 읽어 ΔΔG 를 엔탈피/엔트로피로 가릅니다**.

등록: `TNF0Q_REGISTRATION_20260911.md` (05:10:35, **`<U_gh>` 읽기 전**).
**새 RASPA 를 안 띄웁니다.** `khext_runs/` 를 읽기만 하고 지우지 않습니다.

    RT ln(K_H^vol 비) = ΔΔG = ΔΔH − TΔΔS
    ΔΔH 는 Widom `<U_gh>_1 - <U_h>_0` 에서 **직접 읽고**, 나머지를 ΔΔS 로 돌립니다.
    ⚠️ 옌센 부등식 때문에 **역산은 안 합니다** (등록문 §4).
"""
import json, os, re, statistics as st, sys

HERE = os.path.dirname(os.path.abspath(__file__))
# 외부 골격(T-NF-0k)과 우리 조성(보충 실행)이 서로 다른 폴더에 있습니다.
# 한쪽만 읽으면 (가) 비교의 분모가 조용히 빠집니다 — 실제로 초판이 그랬습니다.
RUNS_DIRS = [os.path.join(HERE, 'khext_runs'), os.path.join(HERE, 'khours_runs')]
R_KJ = 8.314462618e-3            # kJ/mol/K
T_K = 298.0
RT = R_KJ * T_K                  # 2.478 kJ/mol
K_B_KJ = 8.314462618e-3          # K -> kJ/mol 환산에 R 사용 (에너지가 K 단위로 나옴)


def read_dH(path, comp='water'):
    """파일 **끝의 블록 평균**을 읽습니다:

        Average adsorption energy <U_gh>_1-<U_h>_0 obtained from Widom-insertion:
        (Note: the total heat of adsorption is dH=<U_gh>_1-<U_h>_0 - <U_g> - RT)
            [water] Average  <U_gh>_1-<U_h>_0:  -1440.505 +/- 12.642 [K] ( -11.977 +/- 0.105 kJ/mol)

    ⚠️ **초판은 본문 중간의 `Energy <U_gh>...` 블록을 읽었습니다.** 그건
    **10,000/15,000 사이클 시점의 누적값**이고 ± 도 없습니다. 최종 블록 평균이 맞습니다
    (zif90 에서 -12.007 대 **-11.977**, 0.25 % 차이라 판정은 안 바뀌지만 ± 가 생깁니다).

    ⚠️ **그리고 이것은 ΔH 가 아닙니다.** RASPA 가 같은 자리에 적어 둡니다 —
    `dH = <U_gh>_1-<U_h>_0 - <U_g> - RT`. 강체 물은 `<U_g> = 0` 이므로 **RT 를 빼야** 합니다.
    **ΔΔH(차이)는 RT 가 상수라 영향받지 않습니다.** 절대 Q_st 만 달라집니다.
    """
    pat = re.compile(r'\[\s*(\S+?)\s*\]\s*Average\s+<U_gh>_1-<U_h>_0:\s*'
                     r'(-?[\d.eE+]+)\s*\+/-\s*([\d.eE+]+)\s*\[K\]\s*\(\s*'
                     r'(-?[\d.eE+]+)\s*\+/-\s*([\d.eE+]+)\s*kJ/mol\s*\)')
    hits = []
    for i, ln in enumerate(open(path, encoding='utf-8', errors='ignore'), 1):
        m = pat.search(ln)
        if m and m.group(1) == comp:
            hits.append((i, float(m.group(4)), float(m.group(5))))
    if not hits:
        return None
    if len(hits) > 1:
        return None                      # 다중 일치는 거부 — 어느 것인지 코드에 없습니다
    return hits[0][0], hits[0][1], hits[0][2], 'kJ/mol', 1


def main():
    live = [d for d in RUNS_DIRS if os.path.isdir(d)]
    if not live:
        print(f'  실행 폴더 없음: {RUNS_DIRS}'); return 1
    raw, nblocks, src = {}, {}, {}
    for RUNS in live:
      for rep in ('r1', 'r2', 'r3'):
          base = os.path.join(RUNS, rep)
          if not os.path.isdir(base):
              continue
          for d in sorted(os.listdir(base)):
              if not d.startswith('widom_water_'):
                  continue
              name = d[len('widom_water_'):]
              od = os.path.join(base, d, 'Output', 'System_0')
              outs = [os.path.join(od, x) for x in os.listdir(od)
                      if x.endswith('.data')] if os.path.isdir(od) else []
              if len(outs) != 1:
                  continue
              h = read_dH(outs[0])
              if h:
                  raw.setdefault(name, []).append(h[1])
                  nblocks.setdefault(name, []).append(h[2])   # 실행별 95% CI
                  src.setdefault(name, set()).add(os.path.basename(RUNS))
      if not raw:
          print('  <U_gh> 블록을 못 찾았습니다. 출력 형식 확인 필요.'); return 1

    A = {n: {'mean': sum(v) / len(v), 'sd': st.stdev(v) if len(v) > 1 else 0.0,
             'n': len(v), 'vals': v,
             'pm': (sum(q * q for q in nblocks[n]) ** 0.5) / len(nblocks[n]),
             # RASPA 주석: dH = <U_gh>-<U_h> - <U_g> - RT. 강체 물은 <U_g>=0.
             'dH': sum(v) / len(v) - RT} for n, v in raw.items()}
    print('  ═══ T-NF-0q · 무한희석 상호작용 에너지 (물 1분자) ═══\n')
    print(f"  {'골격':8s} {'n':>2s}  {'<U_gh>-<U_h>':>13s} {'±':>6s} {'실행SD':>7s}"
          f"  {'ΔH=-RT 보정':>12s}  {'Q_st':>7s}")
    for n, v in sorted(A.items(), key=lambda x: x[1]['mean']):
        print(f"  {n:8s} {v['n']:2d}  {v['mean']:13.3f} {v['pm']:6.3f} {v['sd']:7.3f}"
              f"  {v['dH']:12.3f}  {-v['dH']:7.3f}")
    print(f"  (RT = {RT:.3f} kJ/mol @ {T_K} K. 강체 물이라 <U_g>=0 으로 둡니다.)")

    # K_H^vol 은 TNF0V 판정문의 값을 그대로 씁니다 (재계산 아님)
    KV = {'zif71': 2.4378e-06, 'zif90': 5.4298e-06, 'zif93': 1.0365e-05,
          'mbIm025': 4.2664e-05}
    import math

    def judge(a, b, label):
        if a not in A or b not in A:
            print(f'\n  {label}: ΔH 부족 (있는 것: {sorted(A)})'); return
        ratio = KV[a] / KV[b]
        ddG = RT * math.log(ratio)
        ddH = A[a]['mean'] - A[b]['mean']
        sd = (A[a]['sd'] ** 2 + A[b]['sd'] ** 2) ** 0.5
        frac = abs(ddH) / abs(ddG) if ddG else float('inf')
        print(f"\n  ── {label} ──")
        print(f"  K_H^vol 비 {ratio:.3f}  ->  ΔΔG = **{ddG:+.3f}** kJ/mol")
        print(f"  ΔΔH = {A[a]['mean']:+.3f} − {A[b]['mean']:+.3f} = **{ddH:+.3f}** kJ/mol"
              f"   (반복 SD 합성 {sd:.3f})")
        print(f"  −TΔΔS = ΔΔG − ΔΔH = **{ddG - ddH:+.3f}** kJ/mol")
        print(f"  |ΔΔH|/|ΔΔG| = **{frac:.2f}**")
        if sd > 0.3 * abs(ddG):
            print(f'  -> **미결** — 반복 SD {sd:.3f} 가 문턱(0.3 x |ΔΔG| = '
                  f'{0.3*abs(ddG):.3f})보다 큽니다. 분해가 문턱보다 시끄럽습니다.')
        elif frac >= 0.7:
            print('  -> **자리 세기** — 모델이 더 깊은 우물을 줍니다')
        elif frac <= 0.3:
            print('  -> **자리 수 / 엔트로피** — 우물 깊이는 비슷하고 유리한 자리가 더 많습니다')
        else:
            print('  -> **혼합** — 둘 다 기여. 어느 쪽도 단독 설명이 아닙니다')

    judge('mbIm025', 'zif93', '(가) mbIm025 대 ZIF-93')
    judge('zif90', 'zif93', '(나) ZIF-90 대 ZIF-93')
    print('\n  ⚠️ ΔΔH 에서 K_H 비를 역산하지 않았습니다 (옌센, 등록문 §4).')
    return 0


if __name__ == '__main__':
    sys.exit(main())
