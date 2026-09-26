#!/usr/bin/env python3
"""E-24i 습윤 TSA 작업 용량 표(서술 — 순위 규칙 밖) — 등록 ASSIGN §HKHOME 22차 습윤 WC 보완 · 37306c51(Cl 이중).
원자료만: 러너 결과 v3w_humid_wc/humid_working_capacity_w2_<tag>_<기기>.json + 감사 요약 results_e24i_<tag>_humid_summary_<기기>.json.
만든 기기 가지에서 집음. 평균 ± = ±̄/√3 · 씨앗 SD 병기. 모체 = E-25(laptop).
"""
import json, math, os, statistics as st, subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
BR = {'junseok': 'origin/junseok-20260822', 'laptop2': 'origin/laptop2-20260825', 'laptop': 'origin/laptop-20260822', 'hkhome': None}
RUNS = [('e24i_cn_open', 'junseok'), ('e24i_br_open', 'hkhome'), ('e24i_cl_open', 'junseok'), ('e24i_cl_open', 'laptop2'),
        ('e24i_ch3_open', 'laptop'), ('e24i_c2h5_open', 'junseok')]


def get(path, m):
    ref = BR[m]
    if ref is None:
        p = os.path.join(HERE, path)
        return json.load(open(p)) if os.path.exists(p) else None
    r = subprocess.run(['git', 'show', f'{ref}:21_ZIF69_MTV/{path}'], cwd=HERE, capture_output=True, text=True)
    return json.loads(r.stdout) if r.returncode == 0 else None


def summarize(d, stem):
    rows = [r for r in d['rows'] if r['name'].startswith(stem + '_h')]
    if len(rows) != 3:
        return None
    t = [r['working_capacity']['tsa']['value'] for r in rows]; te = [r['working_capacity']['tsa']['err'] for r in rows]
    v = [r['working_capacity']['vsa']['value'] for r in rows]; ve = [r['working_capacity']['vsa']['err'] for r in rows]
    L = lambda c, g: st.mean(r['loadings'][c][g]['mol_per_kg'] for r in rows)
    return dict(tsa=st.mean(t), tsa_e=st.mean(te) / 3 ** .5, tsa_sd=st.stdev(t), each=t, vsa=st.mean(v), vsa_e=st.mean(ve) / 3 ** .5,
                ads_co2=L('ads', 'CO2'), ads_w=L('ads', 'water'), tsa_co2=L('tsa', 'CO2'))


par = summarize(get('v3w_humid_wc/humid_working_capacity_w2_e22parent_laptop.json', 'laptop'), 'e22_parent')
print(f"모체(E-25): WC_TSA {par['tsa']:.3f} ± {par['tsa_e']:.3f}(SD {par['tsa_sd']:.3f}) · ads CO₂ {par['ads_co2']:.3f} · 물 {par['ads_w']:.3f}")
for tag, m in RUNS:
    d = get(f'v3w_humid_wc/humid_working_capacity_w2_{tag}_{m}.json', m)
    a = get(f'results_e24i_{tag}_humid_summary_{m}.json', m)
    if d is None or a is None:
        print(f'  {tag} [{m}]: 미완비'); continue
    au = a.get('audit_summary', {})
    ok = au.get('n') == 9 and au.get('n_ok') == 9 and au.get('seeds_distinct')
    s = summarize(d, tag)
    if not ok or s is None:
        print(f'  {tag} [{m}]: 관문 실패 {au}'); continue
    x = (s['tsa'] - par['tsa']) / math.hypot(s['tsa_e'], par['tsa_e'])
    xs = (s['tsa'] - par['tsa']) / math.hypot(s['tsa_sd'] / 3 ** .5, par['tsa_sd'] / 3 ** .5)
    print(f"  {tag} [{m}] 9/9: WC_TSA {s['tsa']:.3f} ± {s['tsa_e']:.3f}(SD {s['tsa_sd']:.3f} · {', '.join('%.3f' % q for q in s['each'])}) · 모체 대비 {x:+.2f} 단위 · 씨앗 SD/√3 자 {xs:+.2f}"
          f" · WC_VSA {s['vsa']:.3f} ± {s['vsa_e']:.3f} · ads CO₂ {s['ads_co2']:.3f} · 물 {s['ads_w']:.4f} · TSA 잔류 CO₂ {s['tsa_co2']:.3f} · 막음 {a.get('blocking')}")
