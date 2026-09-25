# -*- coding: utf-8 -*-
"""MAGI-005 E-20 분석 (Junseok) — `ASSIGN_MAGI5B §Junseok 11차`. 계산 없음: ①·② 결과 JSON 과 실행 폴더만 읽는다.

[①] results_magi5_e3_e20_<n>_widom_<host>.json(run_magi5_widom.py — 같은 실행의 ON·OFF) → S_ON · S_OFF · G = S_ON/S_OFF.
     G 의 ± = G·√((±_ON/S_ON)² + (±_OFF/S_OFF)²) — E-14 와 같은 합성(mslm050 4.6948 ± 0.1507 이 이 식으로 다시 나옴).
[②] results_magi5_e20_water_junseok.json(E-19 자·관문) → K_H(H₂O) 새 4씨앗 평균, ± = ±̄/√4.
[지수] K_H(H₂O) 4씨앗 평균 / ① ON K_H(CO₂) — ± 는 두 상대 ± 의 제곱합. 단위 = d / √(±₁² + ±₂²).
[등록 예측] (1) G(ms50nb50) 가 mslm050(E-14)보다 1.5 단위 넘게 낮지 않음 — 강한 형: 1.5 단위 넘게 위 · 기각: 1.5 단위 넘게 아래
           (2) 지수(ms50nb50) 가 saIm050(E-16 보완 ⓑ 1.3399 ± 0.2832)보다 1.5 단위 넘게 낮음 — 원 문구 기각: 1.5 단위 안이거나 위.
               보완 13:56(b117ae02, 자료 0건) 세 갈래: 성립 = 1.5 단위 넘게 낮음 · 기각 = 지수 ≥ 1.340 · 판정 불가(띠) = 그 사이. 씨앗 간 SD 병기.
           (3) ① S_ON 이 results_v4mix 와 1.5 단위 안(재현). sa25nb75 는 서술(G · 지수).
[감사] 16작업 — .data 1개 · 'Simulation finished' 표지 · 씨앗(서로 다름, 앞선 씨앗과 겹침) · ① K_H 를 .data 에서 다시 읽어 JSON 과 대조 ·
       ② 머리말 관문 · 표지 · 씨앗 · K_H 를 .data 에서 다시 확인. 여기 적는 것은 기계적 사실뿐 — 판정문은 종합자.
사용: python magi5_e20_analyze_junseok.py [--out 경로]   (기본 출력 results_magi5_e20_summary_junseok.json)
"""
import argparse
import glob
import json
import math
import os
import statistics as st
import sys
import time

HERE = '/home/mangwon/mof_project/21_ZIF69_MTV'
sys.path.insert(0, HERE)
import run_aryl_gcmc as rg                     # noqa: E402
import ff_gate                                 # noqa: E402
from run_tb2_water_kh import read_kh           # noqa: E402

NAMES = ('ms50nb50', 'sa25nb75')
WATER = os.path.join(HERE, 'results_magi5_e20_water_junseok.json')
U = 1.5


def units(a, ea, b, eb):
    return (a - b) / math.hypot(ea, eb)


def ratio(a, ea, b, eb):
    r = a / b
    return r, r * math.hypot(ea / a, eb / b)


def seed_of(path):
    for ln in open(path, encoding='utf-8', errors='ignore'):
        if 'Random number seed' in ln:
            return int(ln.split()[-1])
    return None


def close(a, b):
    return a is not None and b is not None and abs(a - b) <= 1e-9 * max(abs(a), abs(b))


def references():
    e14 = {r.get('key'): r for r in json.load(open(os.path.join(HERE, 'results_magi5_e14_offwidom_hkhome.json')))['rows']}
    m = e14['mslm050']
    g, eg = ratio(m['S_ON'], m['S_ON_err'], m['S_OFF'], m['S_OFF_err'])
    e19 = json.load(open(os.path.join(HERE, 'results_magi5_e19_water_seeds_junseok.json')))
    v4 = {r['name']: r for r in json.load(open(os.path.join(HERE, 'results_v4mix.json')))['rows']}
    e1 = {r['name'].replace('_DDEC6', ''): r for r in json.load(open(os.path.join(HERE, 'results_magi5_e1_offwidom_laptop.json')))['rows']}
    sa = e1['saIm050']
    e14b = {r['charges']: r for r in json.load(open(os.path.join(HERE, 'results_magi5_e3_e14b_sa50nb50_widom_desktop-js1ib6u.json')))['rows']}
    ref = {'G_mslm050': {'value': g, 'err': eg, 'S_ON': m['S_ON'], 'S_ON_err': m['S_ON_err'], 'S_OFF': m['S_OFF'], 'S_OFF_err': m['S_OFF_err'],
                         'src': 'results_magi5_e14_offwidom_hkhome.json (S_ON = results_v3)'},
           'index_saIm050': {'value': e19['reference_saIm050']['index'], 'err': e19['reference_saIm050']['index_err'], 'src': e19['reference_saIm050']['src']},
           'S_ON_v4mix': {n: {'value': v4[n]['selectivity'], 'err': v4[n]['selectivity_err'], 'KH_CO2': v4[n]['KH_CO2'], 'KH_CO2_err': v4[n]['KH_CO2_err'],
                              'src': 'results_v4mix.json'} for n in NAMES},
           # 서술용 맥락(등록 비교 아님)
           'context': {'mslm050_index_E19': {'value': e19['compositions']['mslm050']['index'], 'err': e19['compositions']['mslm050']['index_err']},
                       'G_saIm050_E1': dict(zip(('value', 'err'), ratio(sa['S_ON'], sa['S_ON_err'], sa['S_OFF'], sa['S_OFF_err']))),
                       'S_OFF_saIm050_E1': {'value': sa['S_OFF'], 'err': sa['S_OFF_err']},
                       'G_sa50nb50_E14b': dict(zip(('value', 'err'), ratio(e14b['on']['selectivity'], e14b['on']['selectivity_err'],
                                                                             e14b['off']['selectivity'], e14b['off']['selectivity_err']))),
                       'S_OFF_mslm050_E14': {'value': m['S_OFF'], 'err': m['S_OFF_err']},
                       **{f'G_{k}_E14': dict(zip(('value', 'err'), ratio(e14[k]['S_ON'], e14[k]['S_ON_err'], e14[k]['S_OFF'], e14[k]['S_OFF_err'])))
                          for k in ('nbIm050', 'nbIm100', 'base')},
                       **{f'S_OFF_{k}_E14': {'value': e14[k]['S_OFF'], 'err': e14[k]['S_OFF_err']} for k in ('nbIm050', 'nbIm100')}}}
    old_seeds = {r['seed'] for r in e19['runs'] if r.get('seed') is not None}
    sf = json.load(open(os.path.join(HERE, 'v3w_water_kh', 'water_kh_ALLw_hkhome_seedfixed.json')))['rows']
    old_seeds |= {r['raspa_seed'] for r in sf if r.get('raspa_seed') is not None}
    return ref, old_seeds


def load_widom(n):
    fs = sorted(glob.glob(os.path.join(HERE, f'results_magi5_e3_e20_{n}_widom_*.json')))
    if len(fs) != 1:
        raise SystemExit(f'!! ① {n} 결과 파일 {len(fs)}개: {fs}')
    d = json.load(open(fs[0], encoding='utf-8'))
    rows = {r['charges']: r for r in d['rows']}
    runs = os.path.join(HERE, f'magi5_runs_e20_{n}')
    audit = []
    for ch, suf in (('on', ''), ('off', '_q0')):
        for gas in ('CO2', 'N2'):
            dd = os.path.join(runs, f'widom_{gas}_{n}_DDEC6{suf}')
            outs = sorted(glob.glob(os.path.join(dd, 'Output', 'System_0', '*.data')))
            a = {'job': f'{n} {ch} {gas}', 'n_data': len(outs), 'status': rows.get(ch, {}).get(f'status_{gas}')}
            if len(outs) == 1:
                p = rg.parse(outs[0])
                a.update(marker_finished=rg.finished(outs[0]), seed=seed_of(outs[0]), KH_reparse=p[0], KH_json=rows.get(ch, {}).get(f'KH_{gas}'))
                a['KH_match'] = close(p[0], a['KH_json'])
            a['ok'] = bool(a['n_data'] == 1 and a['status'] == 'ok' and a.get('marker_finished') and a.get('KH_match') and a.get('seed'))
            audit.append(a)
    on, off = rows['on'], rows['off']
    g, eg = ratio(on['selectivity'], on['selectivity_err'], off['selectivity'], off['selectivity_err'])
    return {'file': os.path.basename(fs[0]), 'finished': d.get('finished'), 'elapsed_s': d.get('elapsed_s'), 'ff_md5': d.get('ff_md5'),
            'S_ON': on['selectivity'], 'S_ON_err': on['selectivity_err'], 'S_OFF': off['selectivity'], 'S_OFF_err': off['selectivity_err'],
            'KH_CO2_ON': on['KH_CO2'], 'KH_CO2_ON_err': on['KH_CO2_err'], 'KH_N2_ON': on['KH_N2'], 'KH_N2_ON_err': on['KH_N2_err'],
            'KH_CO2_OFF': off['KH_CO2'], 'KH_CO2_OFF_err': off['KH_CO2_err'], 'KH_N2_OFF': off['KH_N2'], 'KH_N2_OFF_err': off['KH_N2_err'],
            'G': g, 'G_err': eg, 'lnG': math.log(g), 'audit': audit}


def load_water():
    w = json.load(open(WATER, encoding='utf-8'))
    if w.get('final') is not True:
        raise SystemExit('!! ② 물 결과가 final 아님')
    audit = []
    for r in w['runs']:
        p = os.path.join(HERE, r['data']) if r.get('data') else None
        a = {'job': f"{r['name']} water s{r['seed_idx']}", 'status': r.get('status'), 'seed': r.get('seed'), 'minutes': r.get('minutes')}
        if p and os.path.exists(p):
            hg = ff_gate.read_ff_header(p)
            kh = read_kh(p, comp='water')[0]
            a.update(header_gate_recheck=hg.get('ok'), marker_recheck=rg.finished(p), seed_recheck=seed_of(p) == r.get('seed'),
                     KH_match=close(kh, r.get('KH_water')), water_sites=r.get('water_sites_in_rundir'))
        a['ok'] = bool(a['status'] == 'ok' and r.get('header_gate_ok') and r.get('marker_finished') and a.get('header_gate_recheck')
                       and a.get('marker_recheck') and a.get('seed_recheck') and a.get('KH_match') and a.get('water_sites') == 5)
        audit.append(a)
    return w, audit


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', default=os.path.join(HERE, 'results_magi5_e20_summary_junseok.json'))
    a = ap.parse_args()
    ref, old_seeds = references()
    w, waudit = load_water()
    res = {}
    for n in NAMES:
        r = load_widom(n)
        c = w['compositions'][n]
        # 씨앗별 값·± 는 한 목록(seed_idx 순)으로 — 물 JSON 의 KH_water_each 는 끝난 순서라 ± 와 따로 늘어놓으면 짝이 어긋남(첫 판 버그)
        per = [{'seed_idx': x['seed_idx'], 'seed': x['seed'], 'KH_water': x['KH_water'], 'KH_water_err': x['KH_water_err']}
               for x in sorted((x for x in w['runs'] if x['name'] == n and x.get('status') == 'ok'), key=lambda x: x['seed_idx'])]
        r['water'] = {'n_new': c['n_new'], 'per_seed': per, 'KH_water_mean4': c.get('KH_water_mean4'),
                      'KH_water_mean4_err': c.get('KH_water_mean4_err'), 'seed_sd_rel': c.get('seed_sd_rel'),
                      'supplementary_with_seedfixed': c.get('supplementary_with_seedfixed')}
        if len(per) > 1:
            sd = st.stdev(p['KH_water'] for p in per)
            r['water']['seed_sd_abs'] = sd
            r['water']['sd_over_sqrt_n'] = sd / math.sqrt(len(per))   # 서술: 씨앗 간 SD 로 본 평균의 ± (등록 ± 는 ±̄/√4)
        if c.get('n_new') == 4:
            ix, eix = ratio(c['KH_water_mean4'], c['KH_water_mean4_err'], r['KH_CO2_ON'], r['KH_CO2_ON_err'])
            r['index'], r['index_err'] = ix, eix
            r['units_index_vs_saIm050'] = units(ix, eix, ref['index_saIm050']['value'], ref['index_saIm050']['err'])
            v = ref['S_ON_v4mix'][n]
            ixv, eixv = ratio(c['KH_water_mean4'], c['KH_water_mean4_err'], v['KH_CO2'], v['KH_CO2_err'])
            r['supplementary_index_v4mix_KH_CO2'] = {'index': ixv, 'err': eixv, 'note': '분모를 v4mix ON K_H(CO₂)로 — 등록 값 아님'}
            s5 = c.get('supplementary_with_seedfixed')
            if s5:
                ix5, eix5 = ratio(s5['KH_water_mean'], s5['KH_water_mean_err'], r['KH_CO2_ON'], r['KH_CO2_ON_err'])
                r['supplementary_index_5seed'] = {'index': ix5, 'err': eix5, 'units_vs_saIm050': units(ix5, eix5, ref['index_saIm050']['value'], ref['index_saIm050']['err']),
                                                  'note': 'seedfixed 1 + 새 4 = 5씨앗 — 등록 값 아님'}
        v = ref['S_ON_v4mix'][n]
        r['units_S_ON_vs_v4mix'] = units(r['S_ON'], r['S_ON_err'], v['value'], v['err'])
        r['units_KH_CO2_ON_vs_v4mix'] = units(r['KH_CO2_ON'], r['KH_CO2_ON_err'], v['KH_CO2'], v['KH_CO2_err'])
        res[n] = r
    ms = res['ms50nb50']
    gm = ref['G_mslm050']
    u1 = units(ms['G'], ms['G_err'], gm['value'], gm['err'])
    u2 = ms.get('units_index_vs_saIm050')
    reg = {'(1)': {'what': 'G(ms50nb50) 대 mslm050(E-14)', 'G': ms['G'], 'G_err': ms['G_err'], 'ref': [gm['value'], gm['err']], 'units': u1,
                   'not_more_than_1.5_below': u1 >= -U, 'strong_more_than_1.5_above': u1 > U, 'more_than_1.5_below(기각 조건)': u1 < -U},
           '(2)': {'what': '지수(ms50nb50) 대 saIm050(E-16 보완 ⓑ)', 'index': ms.get('index'), 'index_err': ms.get('index_err'),
                   'ref': [ref['index_saIm050']['value'], ref['index_saIm050']['err']], 'units': u2,
                   'more_than_1.5_below': (u2 < -U) if u2 is not None else None,
                   'index_ge_ref': (ms['index'] >= ref['index_saIm050']['value']) if ms.get('index') is not None else None,
                   'branch_amended': (None if u2 is None else '성립 쪽(1.5 단위 넘게 낮음)' if u2 < -U
                                      else '기각 쪽(지수 ≥ 참조)' if ms['index'] >= ref['index_saIm050']['value'] else '띠(낮은 쪽이나 1.5 단위 미만)'),
                   'rule_amended': 'ASSIGN_MAGI5B §Junseok 11차 보완 2026-09-25 13:56(b117ae02, 자료 0건): 성립 = 1.5 단위 넘게 낮음 · 기각 = 지수 ≥ 1.340 · 판정 불가(띠) = 그 사이',
                   'seed_sd_rel': ms['water'].get('seed_sd_rel'), 'seed_sd_abs': ms['water'].get('seed_sd_abs')},
           '(3)': {n: {'S_ON': res[n]['S_ON'], 'S_ON_err': res[n]['S_ON_err'], 'ref': [ref['S_ON_v4mix'][n]['value'], ref['S_ON_v4mix'][n]['err']],
                       'units': res[n]['units_S_ON_vs_v4mix'], 'within_1.5': abs(res[n]['units_S_ON_vs_v4mix']) <= U} for n in NAMES}}
    ctx = ref['context']
    desc = {'ms50nb50_vs_mslm050_index_E19': units(ms['index'], ms['index_err'], ctx['mslm050_index_E19']['value'], ctx['mslm050_index_E19']['err'])
            if ms.get('index') is not None else None,
            'ms50nb50_S_OFF_vs_mslm050_E14': units(ms['S_OFF'], ms['S_OFF_err'], ctx['S_OFF_mslm050_E14']['value'], ctx['S_OFF_mslm050_E14']['err']),
            'ms50nb50_G_vs_nbIm050_E14': units(ms['G'], ms['G_err'], ctx['G_nbIm050_E14']['value'], ctx['G_nbIm050_E14']['err']),
            'ms50nb50_G_vs_nbIm100_E14': units(ms['G'], ms['G_err'], ctx['G_nbIm100_E14']['value'], ctx['G_nbIm100_E14']['err'])}
    sa = res['sa25nb75']
    desc.update({'sa25nb75_G_vs_saIm050_E1': units(sa['G'], sa['G_err'], ctx['G_saIm050_E1']['value'], ctx['G_saIm050_E1']['err']),
                 'sa25nb75_G_vs_sa50nb50_E14b': units(sa['G'], sa['G_err'], ctx['G_sa50nb50_E14b']['value'], ctx['G_sa50nb50_E14b']['err']),
                 'sa25nb75_index_vs_saIm050': sa.get('units_index_vs_saIm050')})
    audit = [x for n in NAMES for x in res[n]['audit']] + waudit
    seeds = [x.get('seed') for x in audit]
    aud = {'n_jobs': len(audit), 'n_ok': sum(1 for x in audit if x['ok']), 'seeds_distinct': len(set(seeds)) == len(seeds) and None not in seeds,
           'seed_overlap_with_E19_or_seedfixed': sorted(set(seeds) & old_seeds), 'water_header_gate_pre': w.get('header_gate_pre', {}).get('ok'),
           'ff_md5': sorted({res[n]['ff_md5'] for n in NAMES} | {w.get('ff_md5')}), 'water_def_md5': w.get('water_def_md5'),
           'water_minutes': [min(x['minutes'] for x in waudit), max(x['minutes'] for x in waudit)]}
    out = {'test': 'MAGI-005 E-20 — 조합 ms50nb50 · sa25nb75 의 G 와 물 경쟁 지수', 'assign': 'ASSIGN_MAGI5B_20260925.md §Junseok 11차', 'machine': 'junseok',
           'made': time.strftime('%F %T'), 'inputs': {n: res[n]['file'] for n in NAMES} | {'water': os.path.basename(WATER)},
           'conventions': 'G ± = G·√((±_ON/S_ON)²+(±_OFF/S_OFF)²) · 물 평균 ± = ±̄/√4 · 지수 ± = 두 상대 ± 제곱합 · 단위 = d/√(±₁²+±₂²)',
           'references': ref, 'registered': reg, 'descriptive': desc, 'audit': aud, 'per_structure': res,
           'note': '기계적 사실뿐 — 판정문은 종합자'}
    tmp = a.out + '.tmp'
    json.dump(out, open(tmp, 'w', encoding='utf-8'), indent=2, ensure_ascii=False)
    os.replace(tmp, a.out)
    print(f'저장 {a.out}')
    for n in NAMES:
        r = res[n]
        print(f"  {n:<9} S_ON {r['S_ON']:.2f} ± {r['S_ON_err']:.2f}(v4mix {r['units_S_ON_vs_v4mix']:+.2f} 단위) · S_OFF {r['S_OFF']:.3f} ± {r['S_OFF_err']:.3f} · "
              f"G {r['G']:.3f} ± {r['G_err']:.3f} · K_H(CO₂) ON {r['KH_CO2_ON']:.4e} ± {r['KH_CO2_ON_err']:.2e}")
        wv = r['water']
        print(f"            물 4씨앗(s1~s4) {[format(p['KH_water'], '.3e') + ' ± ' + format(p['KH_water_err'] / p['KH_water'], '.0%') for p in wv['per_seed']]} → "
              f"{wv['KH_water_mean4']:.4e} ± {wv['KH_water_mean4_err']:.2e} "
              f"(씨앗 SD {wv['seed_sd_rel']:.1%}) · 지수 {r.get('index', float('nan')):.3f} ± {r.get('index_err', float('nan')):.3f} "
              f"(saIm050 대비 {r.get('units_index_vs_saIm050', float('nan')):+.2f} 단위)")
    print(f"  (1) G {ms['G']:.3f} ± {ms['G_err']:.3f} 대 mslm050 {gm['value']:.3f} ± {gm['err']:.3f} → {u1:+.2f} 단위")
    print(f"  (2) 지수 {ms.get('index')} 대 saIm050 {ref['index_saIm050']['value']:.3f} ± {ref['index_saIm050']['err']:.3f} → {u2} · 보완 세 갈래: {reg['(2)']['branch_amended']}")
    print(f"  (3) " + ' · '.join(f"{n} {reg['(3)'][n]['units']:+.2f}" for n in NAMES))
    print(f"  서술 {json.dumps(desc, ensure_ascii=False)}")
    print(f"  감사 {json.dumps(aud, ensure_ascii=False)}")
    return 0


if __name__ == '__main__':
    sys.exit(main())
