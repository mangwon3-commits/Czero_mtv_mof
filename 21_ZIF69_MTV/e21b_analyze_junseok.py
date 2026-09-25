# -*- coding: utf-8 -*-
"""MAGI-005 E-21b 분석 (Junseok) — `ASSIGN_MAGI5B §Junseok 12차`. 계산 없음: results_e21b_mix_junseok.json 과 T-J1′(laptop) 결과만 읽는다.

[비] ratio = S_mix / S_Henry, ratio_err = S_mix ± 만(러너 그대로 — S_Henry 는 같은 조성의 반복에서 같은 분모라 비교에서 빠짐).
[등록 예측] (1) 반복 비가 T-J1′ 값(mslm050 0.676 · saIm050 0.643)과 각각 1.5 단위(S_mix ± 기준) 안. 기각: 한쪽이라도 밖.
               단위 = d / √(±₁² + ±₂²). 새 씨앗 하나하나와 새 두 씨앗 평균(± = ±̄/√2) 을 모두 적는다(어느 것으로 읽을지는 종합자).
           (2) 씨앗 SD(3개 = T-J1′ + 새 2) 가 두 조성의 비 차(0.033 = T-J1′ 0.676 − 0.643)보다 작다 — 작지 않으면 가릴 수 없음(서술).
           (3) sa25nb75: 서술(S_mix · 비). 분모 = run_tj1_mix 규칙(v4mix 56.98); E-20 같은 실행 S_ON 54.37 로 나눈 비도 서술로.
[감사] status ok(완주 표지 + 두 성분 적재 각 1줄 + 반환코드 0) · 씨앗 서로 다름 · T-J1′ 씨앗과 겹침 · 힘장 md5.
기계적 사실뿐 — 판정문은 종합자.
"""
import json
import math
import os
import statistics as st
import sys
import time

HERE = '/home/mangwon/mof_project/21_ZIF69_MTV'
RES = os.path.join(HERE, 'results_e21b_mix_junseok.json')
TJ1 = os.path.join(HERE, 'results_tj1_mix_laptop.json')
E20 = os.path.join(HERE, 'results_magi5_e20_summary_junseok.json')
OUT = os.path.join(HERE, 'results_e21b_summary_junseok.json')
U = 1.5
COMPS = ('mslm050', 'saIm050')


def units(a, ea, b, eb):
    return (a - b) / math.hypot(ea, eb)


def main(res=RES, out=OUT):
    d = json.load(open(res, encoding='utf-8'))
    rows = {r['name']: r for r in d['rows']}
    tj1 = {r['name']: r for r in json.load(open(TJ1, encoding='utf-8'))['rows']}
    bad = [n for n, r in rows.items() if r.get('status') != 'ok']
    seeds = [r.get('seed') for r in rows.values()]
    tj1_seeds = {r.get('seed') for r in tj1.values()}
    aud = {'n_jobs': len(rows), 'n_ok': len(rows) - len(bad), 'not_ok': bad, 'seeds': {n: r.get('seed') for n, r in rows.items()},
           'seeds_distinct': None not in seeds and len(set(seeds)) == len(seeds), 'overlap_with_TJ1_seeds': sorted(set(seeds) & tj1_seeds),
           'ff_md5': sorted({r.get('ff_md5') for r in rows.values()}), 'returncodes': {n: r.get('returncode') for n, r in rows.items()},
           'minutes': {n: r.get('minutes') for n, r in rows.items()}, 'machine': sorted({r.get('machine') for r in rows.values()}), 'note_runner': d.get('note')}
    per, reg1, sds = {}, {}, {}
    for c in COMPS:
        ref = tj1[c]
        new = [rows[f'{c}_s{k}'] for k in (2, 3) if rows.get(f'{c}_s{k}', {}).get('status') == 'ok']
        each = [{'name': r['name'], 'seed': r['seed'], 'S_mix': r['S_mix'], 'S_mix_err': r['S_mix_err'], 'N_CO2': r['N_CO2'], 'N_N2': r['N_N2'],
                 'ratio': r['ratio_Smix_over_SHenry'], 'ratio_err': r['ratio_err'],
                 'units_vs_TJ1': units(r['ratio_Smix_over_SHenry'], r['ratio_err'], ref['ratio_Smix_over_SHenry'], ref['ratio_err'])} for r in new]
        for e in each:
            e['within_1.5'] = abs(e['units_vs_TJ1']) <= U
        m = {}
        if len(new) == 2:
            m['ratio_mean2'] = st.mean(e['ratio'] for e in each)
            m['ratio_mean2_err'] = st.mean(e['ratio_err'] for e in each) / math.sqrt(2)
            m['units_vs_TJ1'] = units(m['ratio_mean2'], m['ratio_mean2_err'], ref['ratio_Smix_over_SHenry'], ref['ratio_err'])
            m['within_1.5'] = abs(m['units_vs_TJ1']) <= U
        three = [ref['ratio_Smix_over_SHenry']] + [e['ratio'] for e in each]
        sds[c] = {'ratios_3': three, 'mean3': st.mean(three), 'sd3': st.stdev(three) if len(three) > 1 else None,
                  'S_mix_3': [ref['S_mix']] + [e['S_mix'] for e in each]}
        per[c] = {'TJ1': {'seed': ref['seed'], 'S_mix': ref['S_mix'], 'S_mix_err': ref['S_mix_err'], 'ratio': ref['ratio_Smix_over_SHenry'],
                          'ratio_err': ref['ratio_err'], 'S_Henry': ref['S_Henry'], 'machine': 'laptop'},
                  'new': each, 'new_mean2': m, 'S_Henry': rows[f'{c}_s2']['S_Henry'] if f'{c}_s2' in rows else None}
        reg1[c] = {'each_units': [e['units_vs_TJ1'] for e in each], 'each_within_1.5': [e['within_1.5'] for e in each],
                   'mean2_units': m.get('units_vs_TJ1'), 'mean2_within_1.5': m.get('within_1.5')}
    gap = tj1['mslm050']['ratio_Smix_over_SHenry'] - tj1['saIm050']['ratio_Smix_over_SHenry']
    reg2 = {'gap_TJ1': gap, 'sd3': {c: sds[c]['sd3'] for c in COMPS},
            'sd3_lt_gap': {c: (sds[c]['sd3'] < gap) if sds[c]['sd3'] is not None else None for c in COMPS},
            'mean3': {c: sds[c]['mean3'] for c in COMPS}, 'gap_mean3': sds['mslm050']['mean3'] - sds['saIm050']['mean3'],
            'pooled_sd3': math.sqrt((sds['mslm050']['sd3'] ** 2 + sds['saIm050']['sd3'] ** 2) / 2) if all(sds[c]['sd3'] is not None for c in COMPS) else None}
    if reg2['pooled_sd3']:
        # 서술: 세 씨앗 평균 차를 씨앗 SD 로 본 단위(평균의 ± = SD/√3, 두 평균 차의 ± = √(SD₁²/3 + SD₂²/3))
        reg2['gap_mean3_units_by_seed_sd'] = reg2['gap_mean3'] / math.sqrt(sds['mslm050']['sd3'] ** 2 / 3 + sds['saIm050']['sd3'] ** 2 / 3)
    sa = rows.get('sa25nb75', {})
    reg3 = {k: sa.get(k) for k in ('S_mix', 'S_mix_err', 'N_CO2', 'N_CO2_err', 'N_N2', 'N_N2_err', 'S_Henry', 'S_Henry_err', 'S_Henry_src',
                                    'ratio_Smix_over_SHenry', 'ratio_err', 'ratio_err_with_SHenry', 'status', 'seed')}
    if sa.get('S_mix') and os.path.exists(E20):
        e20 = json.load(open(E20, encoding='utf-8'))['per_structure']['sa25nb75']
        r = sa['S_mix'] / e20['S_ON']
        reg3['descriptive_ratio_vs_E20_S_ON'] = {'S_ON': e20['S_ON'], 'S_ON_err': e20['S_ON_err'], 'ratio': r,
                                                 'ratio_err_with_SON': r * math.hypot(sa['S_mix_err'] / sa['S_mix'], e20['S_ON_err'] / e20['S_ON']),
                                                 'note': 'E-20 같은 실행 ON/OFF 의 S_ON 으로 나눈 비 — 등록 분모 아님'}
    # 맥락(서술): T-J1′ 우리 조성의 비
    ctx = {n: {'ratio': r['ratio_Smix_over_SHenry'], 'ratio_err': r['ratio_err']} for n, r in tj1.items() if r.get('group') == '우리' and r.get('ratio_Smix_over_SHenry')}
    outd = {'test': 'MAGI-005 E-21b — 작동점 벌점 비의 씨앗 산포 + sa25nb75', 'assign': 'ASSIGN_MAGI5B_20260925.md §Junseok 12차', 'machine': 'junseok',
            'made': time.strftime('%F %T'), 'inputs': [os.path.basename(res), os.path.basename(TJ1), os.path.basename(E20)],
            'conventions': 'ratio_err = S_mix ± 만(러너) · 단위 = d/√(±₁²+±₂²) · 새 두 씨앗 평균 ± = ±̄/√2 · SD 는 표본 SD(n−1)',
            'registered': {'(1)': reg1, '(2)': reg2, '(3)': reg3}, 'per_composition': per, 'context_TJ1_ours': ctx, 'audit': aud,
            'note': '기계적 사실뿐 — 판정문은 종합자'}
    tmp = out + '.tmp'
    json.dump(outd, open(tmp, 'w', encoding='utf-8'), indent=2, ensure_ascii=False)
    os.replace(tmp, out)
    print(f'저장 {out}')
    for c in COMPS:
        p = per[c]
        print(f"  {c:<8} T-J1′ 비 {p['TJ1']['ratio']:.4f} ± {p['TJ1']['ratio_err']:.4f} (S_mix {p['TJ1']['S_mix']:.2f})")
        for e in p['new']:
            print(f"           {e['name']:<11} S_mix {e['S_mix']:.2f} ± {e['S_mix_err']:.2f} · 비 {e['ratio']:.4f} ± {e['ratio_err']:.4f} → {e['units_vs_TJ1']:+.2f} 단위")
        if p['new_mean2']:
            print(f"           새 2 평균 {p['new_mean2']['ratio_mean2']:.4f} ± {p['new_mean2']['ratio_mean2_err']:.4f} → {p['new_mean2']['units_vs_TJ1']:+.2f} 단위 · "
                  f"3씨앗 SD {sds[c]['sd3']:.4f} (평균 {sds[c]['mean3']:.4f})")
    print(f"  (2) 비 차(T-J1′) {gap:.4f} · SD3 {json.dumps({c: round(v, 4) if v else v for c, v in reg2['sd3'].items()})} · 3씨앗 평균 차 {reg2['gap_mean3']:.4f}")
    print(f"  (3) sa25nb75 {json.dumps(reg3, ensure_ascii=False)[:400]}")
    print(f"  감사 {json.dumps({k: aud[k] for k in ('n_jobs', 'n_ok', 'not_ok', 'seeds_distinct', 'overlap_with_TJ1_seeds', 'ff_md5', 'minutes')}, ensure_ascii=False)}")
    return 0


if __name__ == '__main__':
    a = sys.argv[1:]
    sys.exit(main(*a) if a else main())
