# -*- coding: utf-8 -*-
"""E-16 ② 후처리 — 보완 참조(ASSIGN_MAGI5B §Junseok 7차 보완 ⓑ, 817d89ed 11:16 — 결과 11:24:30 **전** 커밋)로 단위 거리를 더한다.
드라이버가 적은 원래 참조(saIm050 한 씨앗 ± 67 %, 판별력 0)는 지우지 않고 'superseded' 로 표지. 판정문은 종합자."""
import json
import math
import time

D = '/home/mangwon/mof_project/21_ZIF69_MTV/'
P = D + 'results_magi5_e16_zndia_water_junseok.json'
d = json.load(open(P, encoding='utf-8'))
assert d['row']['status'] == 'ok' and 'amended_reference' not in d
KW_REF, KW_REF_ERR = 2.354e-4, 4.92e-5          # 보완 ⓑ 원문: saIm050 4씨앗 평균 · ±̄/√4
kc, ekc = d['reference']['saIm050_KH_CO2'], d['reference']['saIm050_KH_CO2_err']
ref = KW_REF / kc
eref = ref * math.hypot(KW_REF_ERR / KW_REF, ekc / kc)
idx, eidx = d['index'], d['index_err']
comb = math.hypot(eref, eidx)
u = (idx - ref) / comb
d['amended_reference'] = {'src': 'ASSIGN_MAGI5B_20260925.md §Junseok 7차 보완 ⓑ (master 817d89ed, 11:16 — 결과 전)',
                          'saIm050_KH_water_mean4': KW_REF, 'saIm050_KH_water_mean4_err': KW_REF_ERR,
                          'saIm050_KH_CO2': kc, 'index': ref, 'index_err': eref}
d['index_minus_amended_units'] = u
d['amended_rule'] = '단위 = d / √(±_ref² + ±_new²) · ≥ −1.5 성립 · < −1.5 기각("좁은 3D 카복실레이트는 물에 덜 취약") · > +1.5 강한 성립'
d['amended_band'] = 'below(>1.5 units)' if u < -1.5 else ('above(>1.5 units)' if u > 1.5 else 'within 1.5 units')
d['superseded'] = {'note': "드라이버의 'reference'·'index_minus_ref_units'(saIm050 한 씨앗, 지수 1.46 ± 0.98) 는 판별력 0 — 보완 ⓑ 로 대체"}
d['components'] = {'KH_water_over_saIm050_mean4': d['row']['KH_water'] / KW_REF, 'KH_CO2_over_saIm050': d['KH_CO2_this'] / kc}
d['postprocess'] = {'script': 'magi5_e16_post_junseok.py', 'time': time.strftime('%F %T')}
json.dump(d, open(P, 'w', encoding='utf-8'), indent=2, ensure_ascii=False)
print(f"  보완 참조 지수 {ref:.4f} ± {eref:.4f} · 새 지수 {idx:.4f} ± {eidx:.4f} · d {idx - ref:.4f} · 합성 ± {comb:.4f} · **{u:.2f} 단위** → {d['amended_band']}")
print(f"  성분: K_H(H2O) / saIm050 4씨앗 평균 {d['components']['KH_water_over_saIm050_mean4']:.3f} · K_H(CO2) / saIm050 {d['components']['KH_CO2_over_saIm050']:.2f}")
