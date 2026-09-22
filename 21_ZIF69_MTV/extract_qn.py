# -*- coding: utf-8 -*-
"""§AS (가) Q_st(n) — 72건 결과를 한 표로 모은다. **판정은 하지 않습니다**(등록 §3 은 종합자 몫).

등록: `QSTN_REGISTRATION_20260920.md` · 자료: `tnf_results_qn_<조성>_<T>K_<p>bar.json` 72개
출력: `qn_table.json` (조성×온도×압력 적재량) + 화면 표

09-21 23:0x 데스크탑. Q_st(n) 은 09-21 17:0x 에 **72/72 완주**했습니다.
"""
import glob
import json
import re

ROWS = []
for f in sorted(glob.glob('tnf_results_qn_*.json')):
    if f.endswith('_meta.json'):
        continue
    m = re.match(r'tnf_results_qn_(.+)_(\d+)K_([\d.]+)bar\.json$', f)
    if not m:
        continue
    comp, T, P = m.group(1), int(m.group(2)), float(m.group(3))
    d = json.load(open(f, encoding='utf-8'))
    d = d['rows'] if isinstance(d, dict) and 'rows' in d else d
    for r in d:
        ROWS.append(dict(comp=comp, T=T, P=P,
                         n=r.get('CO2_molkg'), err=r.get('CO2_err'),
                         RH=r.get('RH'), T_row=r.get('T')))

COMPS = sorted({r['comp'] for r in ROWS})
TS = sorted({r['T'] for r in ROWS})
PS = sorted({r['P'] for r in ROWS})
print(f'조성 {len(COMPS)} × 온도 {len(TS)} × 압력 {len(PS)} = {len(COMPS)*len(TS)*len(PS)} · 실제 행 {len(ROWS)}')
print(f'  온도 {TS} · 압력 {PS}')
ok = [r for r in ROWS if r['n'] is not None]
print(f'  적재값 있는 행 **{len(ok)}/{len(ROWS)}**')

print('\n건조 CO2 적재량 (mol/kg) — 행=조성, 열=압력(bar), 블록=온도')
for T in TS:
    print(f'\n  --- {T} K ---')
    print('  조성        ' + ''.join(f'{p:>10.2f}' for p in PS))
    for c in COMPS:
        cells = []
        for p in PS:
            v = [r for r in ROWS if r['comp'] == c and r['T'] == T and r['P'] == p]
            cells.append(f"{v[0]['n']:10.3f}" if v and v[0]['n'] is not None else f"{'—':>10}")
        print(f'  {c:<12}' + ''.join(cells))

json.dump({'note': '§AS (가) Q_st(n) 72건 모음. 판정 아님 — 등록 §3 은 종합자 몫.',
           'registration': 'QSTN_REGISTRATION_20260920.md',
           'comps': COMPS, 'temps': TS, 'pressures': PS, 'rows': ROWS},
          open('qn_table.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('\n저장 qn_table.json')
