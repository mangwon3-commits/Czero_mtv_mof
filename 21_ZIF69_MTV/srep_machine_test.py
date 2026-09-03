#!/usr/bin/env python
"""
ASSIGN_20260903 §7-4 비교 B(기기 축) + §7-5 분할 프로토콜 ± 동등성 — 등록 규칙의 구현.

    python srep_machine_test.py                 # v3_water_srep_whole/srep_whole_summary.json 을 읽음
    python srep_machine_test.py --values 0.79 0.80 0.79 0.80 --ci95 0.017 0.016 0.018 0.006
    python srep_machine_test.py --selftest      # r=0.30 가정으로 랩탑 8019c6c 의 p≈0.0205(대 1.76) 재현

규칙은 ASSIGN_20260903.md §7-4(최종, 13:00)·§7-5 가 정본입니다. 이 파일이 그와 다르면 문서가 맞습니다.
r1 완주 전(수치 아무도 못 봄)에 작성 — 결과를 보고 고치지 않습니다.

§7-4 요약
    r = s_rep / σ_stat,  σ_stat = 네 실행 ±/2.776 의 중앙값 (LAPTOP_R_20260829.md 3절)
    귀무  s_rep² ~ σ_b²·χ²(n−1)/(n−1),  σ_stat² ~ σ_w²·χ²(4n)/(4n)   (dof 4n 근사, 등록)
    T = log(r_laptop2 / r_기기), MC 200,000회 seed 20260903, 양측 p = 2·min(P(T≤t), P(T≥t))
    셋(데스크탑 1.17 n=4 · Junseok 1.18 n=8 · 랩탑 1.76 n=4) 전부 p<0.05 → "기기 축 실재"
    하나라도 아니면 "기기 축 미확인 — 남는 후보 우연, n=4 검정력 한계"
    B 는 비교 A 가 F ≥ 15.44 가 아닐 때만 유효.  근사는 반보수적 p 상대 ~5%(13:10 단서).
§7-5 요약
    F = s²(분할 σ_stat 합동, dof 16) / s²(통짜 σ_stat 합동, dof 16),  양측 5%: 0.362 / 2.761
"""
import argparse
import json
import math
import os
import sys
from statistics import mean, median, stdev

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, 'v3_water_srep_whole')
SUMMARY = os.path.join(ROOT, 'srep_whole_summary.json')
OUT = os.path.join(ROOT, 'srep_machine_test.json')

T95 = 2.776                     # RASPA ± = t(0.975,4)×SEM (ERROR_BARS.md)
N_BLOCK_DOF = 4                 # 블록 5개 → ± 의 dof 4
SEED = 20260903
N_MC = 200_000
N_L2 = 4

# §7-4 대조 셋 — 각 기기의 통짜 러너 r 점값 (등록된 중앙값 정의)
CONTROLS = [('데스크탑', 1.17, 4), ('Junseok', 1.18, 8), ('랩탑', 1.76, 4)]
ALPHA = 0.05
# §7-3 비교 A 임계 (dof 3,3) — B 의 적용 조건
F_A_HI, F_A_LO = 15.44, 0.0648
# §7-5 분할 σ_stat (laptop2 R 측정 4회, COMMS/laptop2.md 08-29) 와 임계 (dof 16,16)
SPLIT_SIGMA_STAT = [0.00627, 0.00598, 0.00645, 0.00227]
F5_HI, F5_LO = 2.761, 0.362
# LAPTOP_R 의 R 문턱 — laptop2 통짜에도 같은 식으로 병기
R_CONVERGE, R_ANOMALY = 2.0, 5.0


def null_T(rng, n_a, n_b, n_mc=N_MC):
    """귀무 r_A=r_B 아래 T = log(r̂_A/r̂_B). 공통 r 은 약분되어 T 의 귀무분포는 r 에 무관."""
    def log_rhat(n):
        chi_b = rng.chisquare(n - 1, n_mc) / (n - 1)          # s_rep²/σ_b²
        chi_w = rng.chisquare(N_BLOCK_DOF * n, n_mc) / (N_BLOCK_DOF * n)   # σ_stat²/σ_w²
        return 0.5 * (np.log(chi_b) - np.log(chi_w))
    return log_rhat(n_a) - log_rhat(n_b)


def two_sided_p(T, t_obs):
    lo = np.mean(T <= t_obs)
    hi = np.mean(T >= t_obs)
    return float(min(1.0, 2.0 * min(lo, hi)))


def machine_axis(r_l2):
    """§7-4 최종 규칙. 대조 셋 각각의 양측 p 와 판정."""
    rows = []
    for name, r_m, n_m in CONTROLS:
        # 비교마다 seed 20260903 로 새 흐름 — 세 비교가 난수 소비 순서에 안 걸리고, 어느 비교든
        # 단독 재현이 같은 p 를 냄(13:30 laptop2 대조: 순서 차이로 대 1.76 이 0.0216/0.0204 갈렸음)
        T = null_T(np.random.default_rng(SEED), N_L2, n_m)
        t_obs = math.log(r_l2 / r_m)
        p = two_sided_p(T, t_obs)
        rows.append({'machine': name, 'r_control': r_m, 'n_control': n_m,
                     't_obs': t_obs, 'p_two_sided': p, 'significant': p < ALPHA,
                     'near_boundary_0.048_0.050': 0.048 <= p <= 0.050})
    all_sig = all(x['significant'] for x in rows)
    verdict = ('기기 축 실재 (셋 전부 p<0.05)' if all_sig
               else '기기 축 미확인 — 남는 후보 우연, n=4 검정력 한계')
    return rows, verdict


def pooled_var(sigmas):
    # 각 σ_stat 이 dof 4 로 동일 → 합동 분산은 σ² 의 단순 평균, dof 4×개수
    return mean(s * s for s in sigmas), N_BLOCK_DOF * len(sigmas)


def chunked_equivalence(whole_sigma_stat):
    """§7-5. F = s²(분할 합동)/s²(통짜 합동)."""
    v_split, dof_split = pooled_var(SPLIT_SIGMA_STAT)
    v_whole, dof_whole = pooled_var(whole_sigma_stat)
    F = v_split / v_whole
    if F >= F5_HI:
        verdict = '주장 기각 — 분할 ± 가 더 큼. 분할 프로토콜 결과의 오차 표기 전수 재검토'
    elif F <= F5_LO:
        verdict = '주장 기각 — 분할 ± 가 더 작음(과소 표기). 같은 재검토, 방향 병기'
    else:
        verdict = '프로토콜의 "같은 추정량" 주장 유지'
    return {'F': F, 'dof': [dof_split, dof_whole], 'F_crit': [F5_LO, F5_HI],
            'pooled_sigma_split': math.sqrt(v_split), 'pooled_sigma_whole': math.sqrt(v_whole),
            'split_sigma_stat': SPLIT_SIGMA_STAT, 'whole_sigma_stat': whole_sigma_stat,
            'verdict': verdict,
            'note': 'σ_stat 의 산포 검정. 관문 넷의 평균 일치는 그대로 유효. dof 16 은 블록 독립 가정. '
                    '분할 0.00227 은 사전에 빼지 않음.'}


def r_threshold_line(s_rep, sig):
    ratio = s_rep / sig
    if ratio <= R_CONVERGE:
        tag = '수렴 (s_rep ≤ 2σ_stat)'
    elif ratio < R_ANOMALY:
        tag = '부분적 (2σ_stat < s_rep < 5σ_stat)'
    else:
        tag = '이상 (s_rep ≥ 5σ_stat)'
    return ratio, tag


def load_inputs(a):
    if a.selftest:
        # r=0.30 가정: 랩탑 8019c6c / laptop2 재현 — 대 1.76 p≈0.0205 (dof 4n 근사 아래)
        return None, None, 0.30, None
    if a.values:
        vals, cis = a.values, a.ci95
    else:
        if not os.path.exists(SUMMARY):
            sys.exit(f'{SUMMARY} 없음 — run_water_whole_nbim025_rep.py --summary 먼저')
        d = json.load(open(SUMMARY, encoding='utf-8'))
        vals, cis = d['values'], d['ci95']
    if len(vals) != N_L2 or len(cis) != N_L2:
        sys.exit(f'통짜 {len(vals)}회 — 등록은 n={N_L2}. 완주 후 다시.')
    if any(c <= 0 for c in cis):
        sys.exit('± 에 0 이 있음 — water_results.json 의 CO2_err 확인')
    return vals, cis, None, d.get('F') if not a.values else None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--values', type=float, nargs='+', help='통짜 4회 로딩 (mol/kg)')
    ap.add_argument('--ci95', type=float, nargs='+', help='통짜 4회 RASPA ±')
    ap.add_argument('--selftest', action='store_true')
    a = ap.parse_args()
    vals, cis, r_fixed, F_A = load_inputs(a)

    out = {'rule': 'ASSIGN_20260903 §7-4(최종 13:00)·§7-5', 'seed': SEED, 'n_mc': N_MC,
           'approx': 'σ_stat² ~ σ_w²χ²(4n)/(4n) — 반보수적, p 상대 약 5% (13:10 단서). '
                     '등록 p 가 0.048~0.050 이면 판정 유보 표기.'}

    if r_fixed is not None:
        print(f'[selftest] r_laptop2 = {r_fixed} 가정')
        rows, verdict = machine_axis(r_fixed)
        for x in rows:
            print(f"  대 {x['machine']:8s} r={x['r_control']:.2f} n={x['n_control']}  "
                  f"t_obs={x['t_obs']:+.4f}  p={x['p_two_sided']:.4f}")
        print(f'  → {verdict}   (랩탑 8019c6c: 대 1.76 p≈0.0205, 대조 확인용)')
        return 0

    s_rep = stdev(vals)
    sig_stat = [c / T95 for c in cis]
    sig_med = median(sig_stat)
    r_l2 = s_rep / sig_med
    ratio, rtag = r_threshold_line(s_rep, sig_med)

    print('laptop2 통짜 nbIm025 RH0 (n=4)')
    for v, c in zip(vals, cis):
        print(f'    {v:.4f} ± {c:.4f}   (σ_stat {c / T95:.5f})')
    print(f'  평균 {mean(vals):.4f}   s_rep {s_rep:.5f}   σ_stat 중앙값 {sig_med:.5f}   '
          f'r = s_rep/σ_stat = {r_l2:.3f}')
    print(f'  R 문턱(LAPTOP_R 식): s_rep/σ_stat = {ratio:.2f} → {rtag}')
    out.update({'values': vals, 'ci95': cis, 's_rep': s_rep, 'sigma_stat': sig_stat,
                'sigma_stat_median': sig_med, 'r_laptop2': r_l2,
                'R_threshold': {'ratio': ratio, 'tag': rtag}})

    # 비교 B 적용 조건 (§7-4 '언제')
    if F_A is not None:
        b_applies = not (F_A >= F_A_HI)
        print(f'\n비교 A: F = {F_A:.2f} (임계 {F_A_LO}/{F_A_HI}) → B {"적용" if b_applies else "하지 않음(F ≥ 15.44)"}')
        out['comparison_A_F'] = F_A
        out['B_applies'] = b_applies
    else:
        b_applies = True
        print('\n비교 A 의 F 를 모름(--values 입력) — B 를 계산하되 적용 조건은 §7-3 결과로 확인')
        out['B_applies'] = None

    print('\n§7-4 비교 B — 직접 검정 (MC 200,000, seed 20260903, dof 4n 근사)')
    rows, verdict = machine_axis(r_l2)
    for x in rows:
        flag = '  ※ 0.048~0.050 경계 — 근사 단서로 판정 유보 표기' if x['near_boundary_0.048_0.050'] else ''
        print(f"  대 {x['machine']:8s} r={x['r_control']:.2f} n={x['n_control']}  "
              f"t_obs={x['t_obs']:+.4f}  p={x['p_two_sided']:.4f}  "
              f"{'유의' if x['significant'] else '비유의'}{flag}")
    if not b_applies:
        print(f'  (참고만 — B 는 적용되지 않음)  {verdict}')
    else:
        print(f'  → {verdict}')
    out['B'] = {'controls': rows, 'verdict': verdict}

    print('\n§7-5 분할 프로토콜 ± 동등성 — F(16,16)')
    e = chunked_equivalence(sig_stat)
    print(f"  분할 합동 σ {e['pooled_sigma_split']:.5f}   통짜 합동 σ {e['pooled_sigma_whole']:.5f}   "
          f"F = {e['F']:.3f}   임계 {F5_LO} / {F5_HI}")
    print(f"  → {e['verdict']}")
    out['chunked_equivalence'] = e

    os.makedirs(ROOT, exist_ok=True)
    json.dump(out, open(OUT, 'w', encoding='utf-8'), indent=2, ensure_ascii=False)
    print(f'\n-> {OUT}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
