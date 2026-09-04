"""T-2 — LCD–로딩 교락 표 (DESIGN_STUDY_20260903 5-A T-2, §0-0 항목 1 지시).

**판정 없음.** 저장소 자료로 두 자를 나란히 놓고 상관을 다시 재는 기술 작업입니다.
§1-3 의 상관표는 report4(외부 종합본) 수치로 계산됐습니다. 여기서는 같은 것을
**저장소 파일에서** 다시 계산합니다.

두 개의 LCD (GLOSSARY.md 102~115행, DESIGN_STUDY §0-0 항목 1):
  (a) GCMC 기하 LCD  results_v3.json 의 `LCD` — GFN-FF 이완본, GCMC 에 실제 쓴 기하
  (b) 관문 LCD 감소%  risk_results_v3.json 의 `LCD_drop_pct` — (a) 에 LAMMPS/UFF4MOF
      12루프 안정성 탐침을 한 번 더 걸어 잰 값을, **같은 탐침을 거친 base(7.631)**
      에 대해 상대화. base 자신이 탐침에서 14.2% 수축한다(8.898 -> 7.631)

산출: t2_confound.json
"""
import json
import os
import sys
from statistics import mean

HERE = os.path.dirname(os.path.abspath(__file__))


def pearson(x, y):
    mx, my = mean(x), mean(y)
    sxy = sum((a - mx) * (b - my) for a, b in zip(x, y))
    sxx = sum((a - mx) ** 2 for a in x)
    syy = sum((b - my) ** 2 for b in y)
    return sxy / (sxx * syy) ** 0.5 if sxx and syy else float('nan')


def rows(name):
    d = json.load(open(os.path.join(HERE, name), encoding='utf-8'))
    return d['rows'] if isinstance(d, dict) and 'rows' in d else d


def main():
    g = {r['name']: r for r in rows('results_v3.json')}
    risk = {r['name']: r for r in rows('risk_results_v3.json')}
    base = g['base']['LCD']

    m = []
    for n in sorted(set(g) & set(risk)):
        if risk[n].get('LCD_drop_pct') is None or g[n].get('loading_015bar') is None:
            continue
        m.append({'name': n,
                  'gate_drop_pct': risk[n]['LCD_drop_pct'],
                  'gcmc_LCD': g[n]['LCD'],
                  'gcmc_LCD_delta_pct': 100 * (g[n]['LCD'] - base) / base,
                  'loading_015bar': g[n]['loading_015bar'],
                  'Qst': g[n].get('Qst_CO2')})

    drop = [x['gate_drop_pct'] for x in m]
    lcd = [x['gcmc_LCD'] for x in m]
    dlt = [x['gcmc_LCD_delta_pct'] for x in m]
    q = [x['loading_015bar'] for x in m]

    def sub(pred, label, key='gate_drop_pct'):
        s = [x for x in m if pred(x)]
        return {'label': label, 'n': len(s),
                'r': pearson([x[key] for x in s], [x['loading_015bar'] for x in s])
                if len(s) > 2 else None}

    corr = {
        'gate_drop_vs_loading_all': {'n': len(m), 'r': pearson(drop, q)},
        'gcmc_LCD_vs_loading_all': {'n': len(m), 'r': pearson(lcd, q)},
        'gate_drop_vs_gcmc_delta': {'n': len(m), 'r': pearson(drop, dlt)},
        'subsets': [
            sub(lambda x: x['gate_drop_pct'] > 5, '관문 감소 > 5%'),
            sub(lambda x: abs(x['gate_drop_pct']) < 3, '|관문 감소| < 3%'),
            sub(lambda x: x['name'].startswith('saIm') or x['name'] == 'base',
                'saIm 사다리 + base (관문 자)'),
        ],
        'saIm_ladder_gcmc_ruler': {
            'n': len([x for x in m if x['name'].startswith('saIm') or x['name'] == 'base']),
            'r': pearson([x['gcmc_LCD'] for x in m
                          if x['name'].startswith('saIm') or x['name'] == 'base'],
                         [x['loading_015bar'] for x in m
                          if x['name'].startswith('saIm') or x['name'] == 'base'])},
    }

    # 배치 간 상관 — 앙상블이 있는 조성 전부 (§0-0 은 0583 만 적었다)
    # 생산 실현을 넣은 n=6 도 같이 낸다 — STAGE2_SAIM075_20260828.md 322행의
    # 사전 등록("r 의 부호만")이 n=6 기준이다.
    prod = {'saIm0583': ('results_v3grid.json', 'saIm0583'),
            'saIm075': ('results_v3.json', 'saIm075')}
    batch = []
    for f, lab in (('results_v3ens0583.json', 'saIm0583'),
                   ('results_v3ens075.json', 'saIm075')):
        try:
            rs = [r for r in rows(f) if r.get('LCD') and r.get('loading_015bar')]
        except FileNotFoundError:
            continue
        if len(rs) <= 2:
            continue
        x = [r['LCD'] for r in rs]
        y = [r['loading_015bar'] for r in rs]
        e = {'label': lab, 'n_e_only': len(rs), 'r_e_only': pearson(x, y),
             'members': [r['name'] for r in rs]}
        pf, pn = prod[lab]
        hit = [r for r in rows(pf) if r.get('name') == pn and r.get('LCD')]
        if hit:
            e['n_with_production'] = len(rs) + 1
            e['r_with_production'] = pearson(x + [hit[0]['LCD']],
                                             y + [hit[0]['loading_015bar']])
            e['production_source'] = pf
        batch.append(e)

    out = {'note': '판정 없음 — 기술. 두 자의 정의는 GLOSSARY.md 102~115행',
           'base_gcmc_LCD': base, 'base_gate_LCD_after_probe': 7.63144,
           'rows': m, 'correlations': corr, 'batch_level': batch}
    json.dump(out, open(os.path.join(HERE, 't2_confound.json'), 'w',
                        encoding='utf-8'), indent=2, ensure_ascii=False)

    print('=== T-2 두 자를 나란히 (저장소 자료 재계산) ===\n')
    print(f'  {"조성":<10}{"관문 감소%":>11}{"GCMC LCD":>10}{"Δ vs base":>11}'
          f'{"로딩":>9}')
    print('  ' + '-' * 52)
    for x in sorted(m, key=lambda t: -t['gate_drop_pct']):
        print(f'  {x["name"]:<10}{x["gate_drop_pct"]:>+11.2f}{x["gcmc_LCD"]:>10.4f}'
              f'{x["gcmc_LCD_delta_pct"]:>+11.2f}{x["loading_015bar"]:>9.4f}')
    print('\n=== 상관 ===')
    print(f'  r(관문 감소%, 로딩)      n={corr["gate_drop_vs_loading_all"]["n"]:>2}  '
          f'{corr["gate_drop_vs_loading_all"]["r"]:+.3f}')
    print(f'  r(GCMC 기하 LCD, 로딩)   n={corr["gcmc_LCD_vs_loading_all"]["n"]:>2}  '
          f'{corr["gcmc_LCD_vs_loading_all"]["r"]:+.3f}')
    print(f'  **r(두 자 사이)**        n={corr["gate_drop_vs_gcmc_delta"]["n"]:>2}  '
          f'{corr["gate_drop_vs_gcmc_delta"]["r"]:+.3f}   <- 두 자는 같은 것을 재지 않는다')
    for s in corr['subsets']:
        if s['r'] is not None:
            print(f'  {s["label"]:<26} n={s["n"]:>2}  {s["r"]:+.3f}')
    print(f'  saIm 사다리 + base (GCMC 자)  n={corr["saIm_ladder_gcmc_ruler"]["n"]:>2}  '
          f'{corr["saIm_ladder_gcmc_ruler"]["r"]:+.3f}   <- 같은 구조·같은 로딩, 자만 다름')
    print('\n=== 배치 간 (실현체 사이) ===')
    for b in batch:
        line = (f'  {b["label"]:<10} e1~e5 n={b["n_e_only"]}  '
                f'r={b["r_e_only"]:+.3f}')
        if 'r_with_production' in b:
            line += (f'   | 생산 실현 포함 n={b["n_with_production"]}  '
                     f'r={b["r_with_production"]:+.3f}  <- 등록(STAGE2 322행)은 이 쪽')
        print(line)
    print('\n-> t2_confound.json')
    return 0


if __name__ == '__main__':
    sys.exit(main())
