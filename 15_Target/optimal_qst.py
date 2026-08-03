"""flue gas 조건에서 Q_st 최적값을 우리 데이터로 직접 계산한다.

왜 다시 따지는가:
    핸드오버 문서의 "30~40 kJ/mol Goldilocks Zone"이 어떤 공정 기준인지 불명확하다.
    DAC(400 ppm = 0.0004 bar)와 flue gas(0.15 bar)는 CO2 분압이 375배 차이나므로
    같은 피복률을 얻는 데 필요한 결합에너지가 RT*ln(375) = 14.7 kJ/mol 만큼 다르다.
    목표치를 그대로 쓰면 "미달" 판정이 잘못될 수 있다.

방법:
    Q_st만으로는 성능을 못 정한다. 실제 공정 성능은 '작업용량(working capacity)'이다.
        TSA: 흡착 313 K -> 탈착 393 K, P_CO2 = 0.15 bar 고정
        VSA: 313 K 등온, 0.15 bar -> 0.05 bar

    Langmuir로 유한 포화를 반영한다(Q_st가 커지면 흡착 조건에서 포화되어
    탈착이 안 되므로 최적값이 생긴다):
        n(T,P) = n_sat * b(T)P / (1 + b(T)P),   b(T) = b0 * exp(Q_st/RT)

    b0(전지수 인자)는 우리가 측정한 (Q_st, K_H) 8쌍을 van't Hoff로 회귀해 얻는다.
    즉 가상의 파라미터가 아니라 이 골격 계열이 실제로 따르는 관계를 외삽한다.
"""
import json
import os

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
R = 8.314462618e-3          # kJ/mol/K
T_ADS, T_DES = 313.0, 393.0  # TSA
P_ADS, P_VAC = 0.15e5, 0.05e5  # Pa
N_SAT = 10.0                # mol/kg, ZIF-8 계열 포화용량 근사


def load_data():
    pts = []
    for f, key in [('../13_PACMAN/ddec6_results.json', None),
                   ('../14_Strategies/ddec6_results.json', None)]:
        p = os.path.join(HERE, f)
        if not os.path.exists(p):
            continue
        for r in json.load(open(p)):
            if r.get('Qst_CO2') and r.get('KH_CO2'):
                pts.append((r['name'], r['Qst_CO2'], r['KH_CO2']))
    return pts


def main():
    pts = load_data()
    q = np.array([p[1] for p in pts])
    kh = np.array([p[2] for p in pts])

    # van't Hoff 회귀: ln K_H = ln b0' + Q/(R*298)
    x = q / (R * 298.0)
    A = np.vstack([x, np.ones_like(x)]).T
    slope, intercept = np.linalg.lstsq(A, np.log(kh), rcond=None)[0]
    resid = np.log(kh) - (slope * x + intercept)
    r2 = 1 - resid.var() / np.log(kh).var()
    print(f'측정 {len(pts)}개로 van\'t Hoff 회귀: 기울기 {slope:.3f} (이상적 1.0), R²={r2:.3f}')
    print('  -> 기울기가 1에서 벗어나는 건 구조마다 엔트로피(전지수 인자)가 다르기 때문.')
    print('     경향 외삽에는 쓸 수 있으나 절대 예측은 아니다.\n')

    # 두 모델로 나눠 본다. 결론이 둘 다에서 같아야 신뢰할 수 있다.
    #   (A) 보상 모델: 우리 데이터 회귀 그대로. 엔탈피-엔트로피 보상을 반영하지만
    #       Q=14~23 구간의 관계를 Q=60까지 외삽하는 무리가 있다.
    #   (B) 고정 전지수 모델: 최고 성능 구조의 전지수 인자를 고정하고 순수 van't Hoff.
    #       보상을 무시하므로 고Q 성능을 낙관적으로 본다 -> 상한 역할.
    best_pt = max(pts, key=lambda p: p[1])
    A_fixed = best_pt[2] * np.exp(-best_pt[1] / (R * 298.0))

    def KH_of(Q, T, model='A'):
        if model == 'A':
            kh298 = np.exp(slope * Q / (R * 298.0) + intercept)
        else:
            kh298 = A_fixed * np.exp(Q / (R * 298.0))
        return kh298 * np.exp((Q / R) * (1.0 / T - 1.0 / 298.0))

    def loading(Q, T, P, model='A'):
        b = KH_of(Q, T, model) / N_SAT      # Langmuir b [1/Pa]
        return N_SAT * b * P / (1 + b * P)

    Qs = np.arange(10, 81, 1.0)
    out = {}
    for m in ('A', 'B'):
        out[m] = {
            'tsa': np.array([loading(Q, T_ADS, P_ADS, m) - loading(Q, T_DES, P_ADS, m)
                             for Q in Qs]),
            'vsa': np.array([loading(Q, T_ADS, P_ADS, m) - loading(Q, T_ADS, P_VAC, m)
                             for Q in Qs]),
        }
    tsa, vsa = out['A']['tsa'], out['A']['vsa']

    print(f'{"Q_st":>6} {"TSA 작업용량":>13} {"VSA 작업용량":>13}   (mol/kg)')
    print('-' * 46)
    for Q in range(10, 61, 5):
        i = int(Q - 10)
        print(f'{Q:>6} {tsa[i]:>13.4f} {vsa[i]:>13.4f}')

    print()
    print('모델별 최적값 및 실용 기준 도달 지점')
    print('-' * 66)

    def reach(arr, tgt):
        if arr.max() < tgt:
            return None
        return Qs[int(np.argmax(arr >= tgt))]

    for m, lbl in (('A', '보상 모델(우리 회귀)'), ('B', '고정 전지수(낙관 상한)')):
        t, v = out[m]['tsa'], out[m]['vsa']
        r1, r2 = reach(t, 1.0), reach(t, 2.0)
        print(f'  [{lbl}]')
        print(f'    TSA 최대 {t.max():.2f} mol/kg @ Q={Qs[t.argmax()]:.0f} | '
              f'VSA 최대 {v.max():.2f} @ Q={Qs[v.argmax()]:.0f}')
        s1 = f'{r1:.0f}' if r1 else '미도달'
        s2 = f'{r2:.0f}' if r2 else '미도달'
        print(f'    TSA 작업용량 1.0 mol/kg 도달 Q_st = {s1}')
        print(f'    TSA 작업용량 2.0 mol/kg 도달 Q_st = {s2}')

    # 우리 최고 성능 대비
    best = max(pts, key=lambda p: p[1])
    i_best = int(round(best[1] - 10))
    print(f'\n우리 최고: {best[0]} Q_st={best[1]:.2f}')
    print(f'  TSA 작업용량 = {tsa[i_best]:.4f} mol/kg '
          f'(최적 대비 {tsa[i_best]/tsa.max()*100:.0f}%)')
    print(f'  VSA 작업용량 = {vsa[i_best]:.4f} mol/kg '
          f'(최적 대비 {vsa[i_best]/vsa.max()*100:.0f}%)')

    # 재생 에너지(현열 제외, 탈착열만) 개략
    print(f'\n{"Q_st":>6} {"TSA용량":>10} {"탈착열":>12} {"용량/열":>12}')
    print(f'{"":6} {"(mol/kg)":>10} {"(kJ/mol CO2)":>12} {"(상대)":>12}')
    print('-' * 44)
    eff = tsa / Qs
    for Q in range(15, 51, 5):
        i = int(Q - 10)
        print(f'{Q:>6} {tsa[i]:>10.4f} {Q:>12} {eff[i]/eff.max():>12.2f}')
    print(f'\n에너지 효율(용량/탈착열) 최적 Q_st = {Qs[eff.argmax()]:.0f} kJ/mol')

    with open(os.path.join(HERE, 'target_analysis.json'), 'w', encoding='utf-8') as f:
        json.dump({'slope': slope, 'intercept': intercept, 'r2': r2,
                   'tsa_opt_Q': float(Qs[tsa.argmax()]),
                   'vsa_opt_Q': float(Qs[vsa.argmax()]),
                   'eff_opt_Q': float(Qs[eff.argmax()]),
                   'measured': [{'name': n, 'Qst': qq, 'KH': k} for n, qq, k in pts]},
                  f, indent=2, ensure_ascii=False)
    print(f'\n[OK] 저장: target_analysis.json')


if __name__ == '__main__':
    main()
