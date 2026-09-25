# -*- coding: utf-8 -*-
"""MAGI-005 E-23 분석 — Junseok 몫(mslm050 · saIm050) (`ASSIGN_MAGI5B §HKHOME 12차 + Junseok 13차`). 계산 없음: 결과 JSON 만 읽는다.

[양] 등록 그대로: 조성마다 배치(n6: e0~e5) 평균 S_mix · 배치 SD · ±̄/√n. 비 S_mix/S_Henry 도 같은 방식.
     e1~e5 = results_e23_mix_junseok.json(S_Henry = 같은 실현의 S_ON, E-14c · E-14d 실현표).
     e0 = T-J1′ s1(laptop) + E-21b s2 · s3(Junseok) 세 씨앗 평균 — ± 는 평균의 ± (±̄/√3). e0 의 S_Henry = results_v3(= 실현표 e0 S_ON).
[자] RULER_DECISION(E-14c formula 줄): 배치 단위 = d/√(SD₁²+SD₂²)(판정 자) · 단위(±) = d/√((±̄₁/√n)²+(±̄₂/√n)²).
[이 기기 몫] 예측 (1) 의 mslm050 ↔ saIm050 짝만 셈(sa50nb50 · 형판은 데스크탑 결과 — 종합자). (4) 서술: 씨앗 SD(E-21b) 대 배치 SD ·
     배치 평균 비 대 배치 평균 G(E-14c · E-14d n6). 감사: 10행 status ok · 씨앗 다름 · 앞선 씨앗(T-J1′ · E-21b)과 겹침 · 힘장 md5.
기계적 사실뿐 — 판정문은 종합자.
"""
import json
import math
import os
import statistics as st
import sys
import time

HERE = '/home/mangwon/mof_project/21_ZIF69_MTV'
RES = os.path.join(HERE, 'results_e23_mix_junseok.json')
TJ1 = os.path.join(HERE, 'results_tj1_mix_laptop.json')
E21B = os.path.join(HERE, 'results_e21b_mix_junseok.json')
E14C = os.path.join(HERE, 'results_magi5_e14c_offwidom_laptop2.json')
E14D = os.path.join(HERE, 'results_magi5_e14d_offwidom_laptop2.json')
OUT = os.path.join(HERE, 'results_e23_summary_junseok.json')
COMPS = ('mslm050', 'saIm050')


def batch(vals, errs):
    n = len(vals)
    m = st.mean(vals)
    sd = st.stdev(vals) if n > 1 else None
    eb = st.mean(errs)
    return {'n': n, 'mean': m, 'SD': sd, 'CV': sd / m if sd is not None else None, 'err_mean': eb, 'err_mean_over_sqrt_n': eb / math.sqrt(n)}


def main(res=RES, out=OUT):
    d = json.load(open(res, encoding='utf-8'))
    rows = {r['name']: r for r in d['rows']}
    tj1 = {r['name']: r for r in json.load(open(TJ1, encoding='utf-8'))['rows']}
    e21b = {r['name']: r for r in json.load(open(E21B, encoding='utf-8'))['rows']}
    g6 = {'saIm050': json.load(open(E14C))['e14c_summary']['n6']['saIm050'], 'mslm050': json.load(open(E14D))['e14d_summary']['n6']['mslm050']}
    bad = [n for n, r in rows.items() if r.get('status') != 'ok']
    seeds = [r.get('seed') for r in rows.values()]
    old = {r.get('seed') for r in tj1.values()} | {r.get('seed') for r in e21b.values()}
    aud = {'n_jobs': len(rows), 'n_ok': len(rows) - len(bad), 'not_ok': bad, 'seeds_distinct': None not in seeds and len(set(seeds)) == len(seeds),
           'overlap_with_TJ1_or_E21b_seeds': sorted(set(seeds) & old), 'ff_md5': sorted({r.get('ff_md5') for r in rows.values()}),
           'returncodes': sorted({r.get('returncode') for r in rows.values()}, key=str), 'minutes': {n: r.get('minutes') for n, r in rows.items()},
           'machine': sorted({r.get('machine') for r in rows.values()}), 'note_runner': d.get('note')}
    per = {}
    for c in COMPS:
        three = [tj1[c], e21b[f'{c}_s2'], e21b[f'{c}_s3']]
        e0 = {'name': f'{c} e0 (T-J1′ s1 + E-21b s2 · s3)', 'seeds': [r['seed'] for r in three],
              'S_mix': st.mean(r['S_mix'] for r in three), 'S_mix_err': st.mean(r['S_mix_err'] for r in three) / math.sqrt(3),
              'S_Henry': tj1[c]['S_Henry'], 'S_mix_seed_SD': st.stdev(r['S_mix'] for r in three),
              'ratio': st.mean(r['ratio_Smix_over_SHenry'] for r in three), 'ratio_err': st.mean(r['ratio_err'] for r in three) / math.sqrt(3),
              'ratio_seed_SD': st.stdev(r['ratio_Smix_over_SHenry'] for r in three)}
        ex = []
        for e in range(1, 6):
            r = rows.get(f'{c}e{e}', {})
            if r.get('status') == 'ok':
                ex.append({'name': r['name'], 'seed': r['seed'], 'S_mix': r['S_mix'], 'S_mix_err': r['S_mix_err'], 'N_CO2': r['N_CO2'], 'N_N2': r['N_N2'],
                           'S_Henry': r['S_Henry'], 'S_Henry_err': r['S_Henry_err'], 'ratio': r['ratio_Smix_over_SHenry'], 'ratio_err': r['ratio_err'],
                           'ratio_err_with_SHenry': r.get('ratio_err_with_SHenry'), 'minutes': r.get('minutes')})
        allr = [e0] + ex
        per[c] = {'e0': e0, 'e1_e5': ex,
                  'n6_S_mix': batch([x['S_mix'] for x in allr], [x['S_mix_err'] for x in allr]),
                  'n6_ratio': batch([x['ratio'] for x in allr], [x['ratio_err'] for x in allr]),
                  'n5_e1_e5_S_mix': batch([x['S_mix'] for x in ex], [x['S_mix_err'] for x in ex]) if len(ex) > 1 else None,
                  'n6_G_E14': {'G_mean': g6[c]['G_mean'], 'G_SD': g6[c]['G_SD'], 'S_ON_mean': g6[c]['S_ON_mean'], 'S_ON_SD': g6[c]['S_ON_SD']}}
    pair = {}
    for q in ('n6_S_mix', 'n6_ratio'):
        a, b = per['mslm050'][q], per['saIm050'][q]
        dd = a['mean'] - b['mean']
        pair[q] = {'d_mslm050_minus_saIm050': dd, 'batch_units': dd / math.hypot(a['SD'], b['SD']),
                   'pm_units': dd / math.hypot(a['err_mean_over_sqrt_n'], b['err_mean_over_sqrt_n'])}
    pair['(1)_this_pair_within_1.5_batch_units'] = abs(pair['n6_S_mix']['batch_units']) <= 1.5
    desc4 = {c: {'seed_SD_S_mix_E21b': per[c]['e0']['S_mix_seed_SD'], 'batch_SD_S_mix_n6': per[c]['n6_S_mix']['SD'],
                 'seed_SD_ratio_E21b': per[c]['e0']['ratio_seed_SD'], 'batch_SD_ratio_n6': per[c]['n6_ratio']['SD'],
                 'batch_mean_ratio_n6': per[c]['n6_ratio']['mean'], 'batch_mean_G_n6_E14': g6[c]['G_mean']} for c in COMPS}
    outd = {'test': 'MAGI-005 E-23 — Junseok 몫(mslm050 · saIm050) 배치 평균 S_mix', 'assign': 'ASSIGN_MAGI5B_20260925.md §HKHOME 12차 + Junseok 13차',
            'machine': 'junseok', 'made': time.strftime('%F %T'), 'inputs': [os.path.basename(p) for p in (res, TJ1, E21B, E14C, E14D)],
            'conventions': '배치 n6 = e0~e5 · e0 = 세 씨앗 평균(± = ±̄/√3) · SD 표본(n−1) · 배치 단위 = d/√(SD₁²+SD₂²) · 단위(±) = d/√((±̄₁/√n)²+(±̄₂/√n)²)',
            'per_composition': per, 'pair_mslm050_saIm050': pair, 'descriptive_(4)': desc4, 'audit': aud,
            'note': '이 기기 몫의 기계적 사실뿐 — sa50nb50 · 형판(데스크탑)과의 짝, 예측 (1)~(3) 판정, 최종 순위는 종합자'}
    tmp = out + '.tmp'
    json.dump(outd, open(tmp, 'w', encoding='utf-8'), indent=2, ensure_ascii=False)
    os.replace(tmp, out)
    print(f'저장 {out}')
    for c in COMPS:
        p = per[c]
        print(f"  {c:<8} e0 S_mix {p['e0']['S_mix']:.2f} ± {p['e0']['S_mix_err']:.2f} · 비 {p['e0']['ratio']:.4f}")
        for x in p['e1_e5']:
            print(f"           {x['name']:<10} S_mix {x['S_mix']:.2f} ± {x['S_mix_err']:.2f} · S_Henry {x['S_Henry']:.2f} · 비 {x['ratio']:.4f} ± {x['ratio_err']:.4f} · {x['minutes']} 분")
        b, r = p['n6_S_mix'], p['n6_ratio']
        print(f"           n6 S_mix {b['mean']:.2f} · SD {b['SD']:.2f} · ±̄/√6 {b['err_mean_over_sqrt_n']:.2f} | 비 {r['mean']:.4f} · SD {r['SD']:.4f} · ±̄/√6 {r['err_mean_over_sqrt_n']:.4f} · G(E-14) {p['n6_G_E14']['G_mean']:.3f}")
    print(f"  짝 mslm050 − saIm050: S_mix d {pair['n6_S_mix']['d_mslm050_minus_saIm050']:+.2f} → 배치 {pair['n6_S_mix']['batch_units']:+.2f} · ± {pair['n6_S_mix']['pm_units']:+.2f} 단위 | "
          f"비 d {pair['n6_ratio']['d_mslm050_minus_saIm050']:+.4f} → 배치 {pair['n6_ratio']['batch_units']:+.2f} · ± {pair['n6_ratio']['pm_units']:+.2f}")
    print(f"  (4) {json.dumps({c: {k: round(v, 4) for k, v in x.items()} for c, x in desc4.items()}, ensure_ascii=False)}")
    print(f"  감사 {json.dumps({k: aud[k] for k in ('n_jobs', 'n_ok', 'not_ok', 'seeds_distinct', 'overlap_with_TJ1_or_E21b_seeds', 'ff_md5', 'returncodes')}, ensure_ascii=False)}")
    return 0


if __name__ == '__main__':
    a = sys.argv[1:]
    sys.exit(main(*a) if a else main())
