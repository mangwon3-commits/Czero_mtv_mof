"""T-1 앙상블 재표기 — 습윤 TSA 작업 용량 (DESIGN_STUDY_20260903 5-A T-1).

판정 규칙은 `ASSIGN_20260904.md` §2 D3 에 **수를 보기 전에** 등록됐습니다.
여기서 규칙을 바꾸지 않습니다.

    ±       앙상블은 **2.776 x SEM**(n=실현체 수). 배치 SD 는 병기만 하고
            `±` 로 쓰지 않는다 (CLAUDE.md §2 — RASPA 의 ± 도 95% CI 다)
    동급    |Δ평균| < 1.5 x 합성 ±,  합성 ± = sqrt(±A² + ±B²)
    유보    단일 실현 대 앙상블은 **분모 비대칭** — 동급으로도 우세로도
            굳히지 않는다. 성립하는 비교는 앙상블-앙상블, 단일-단일 뿐

산출: t1_ensemble.json + T1_ENSEMBLE_TABLE.md
"""
import glob
import hashlib
import json
import os
import re
import sys
from statistics import mean, stdev

HERE = os.path.dirname(os.path.abspath(__file__))
T95 = 2.776          # t(0.975, 4) — 블록 5개
THRESH = 1.5         # 등록된 동급 문턱 (단위는 `±`)

WET_DIRS = ('v3_humid_wc', 'v4_humid_wc', 'v3_humid_wc_ens')
E_SUFFIX = re.compile(r'^(?P<base>.+?)e(?P<idx>\d+)$')


def load_wet():
    """{조성: [ {realization, tsa, err, src} ]} — 바이트 동일 파일은 한 번만."""
    seen_md5 = {}
    per = {}
    for sub in WET_DIRS:
        for f in sorted(glob.glob(os.path.join(HERE, sub, '*.json'))):
            raw = open(f, 'rb').read()
            h = hashlib.md5(raw).hexdigest()
            if h in seen_md5:
                per.setdefault('__dupes__', []).append(
                    {'file': os.path.relpath(f, HERE),
                     'same_as': seen_md5[h], 'md5': h})
                continue
            seen_md5[h] = os.path.relpath(f, HERE)
            d = json.loads(raw.decode('utf-8'))
            for r in (d['rows'] if isinstance(d, dict) and 'rows' in d else d):
                w = r['working_capacity']['tsa']
                m = E_SUFFIX.match(r['name'])
                base = m.group('base') if m else r['name']
                per.setdefault(base, []).append(
                    {'realization': r['name'], 'tsa': w['value'],
                     'err95': w['err'], 'src': os.path.relpath(f, HERE)})
    return per


def summarize(rows):
    v = [r['tsa'] for r in rows]
    n = len(v)
    out = {'n': n, 'values': v, 'mean': mean(v)}
    if n >= 2:
        sd = stdev(v)
        out['batch_sd'] = sd
        out['sem'] = sd / n ** 0.5
        out['ci95'] = T95 * sd / n ** 0.5      # <- 이것이 `±`
        out['pm_source'] = '앙상블 2.776 x SEM'
    else:
        out['batch_sd'] = None
        out['ci95'] = rows[0]['err95']          # RASPA 95% CI (통계오차만)
        out['pm_source'] = 'RASPA 통계 ± (배치 산포 없음)'
    return out


def compare(a, b, sa, sb):
    comb = (sa['ci95'] ** 2 + sb['ci95'] ** 2) ** 0.5
    d = abs(sa['mean'] - sb['mean'])
    units = d / comb if comb else float('inf')
    asym = (sa['n'] == 1) != (sb['n'] == 1)
    if asym:
        verdict = '판정 유보 — 분모 비대칭(단일 실현 대 앙상블)'
    elif units < THRESH:
        verdict = '동급'
    else:
        verdict = f'차이 있음 ({units:.2f} 단위 ≥ {THRESH})'
    return {'a': a, 'b': b, 'delta': d, 'combined_pm': comb,
            'units': units, 'asymmetric': asym, 'verdict': verdict}


def main():
    per = load_wet()
    dupes = per.pop('__dupes__', [])
    summ = {k: summarize(v) for k, v in sorted(per.items())}

    ens = [k for k, s in summ.items() if s['n'] >= 2]
    single = [k for k, s in summ.items() if s['n'] == 1]

    pairs = []
    keys = sorted(summ)
    for i, a in enumerate(keys):
        for b in keys[i + 1:]:
            pairs.append(compare(a, b, summ[a], summ[b]))

    # [감도, 판정 아님] 단일 실현의 ± 에는 배치 산포가 없습니다. saIm0583 의
    # 배치 SD 를 모든 조성에 공통으로 대입하면 쌍 비교가 어떻게 움직이는지만
    # 봅니다. **등록 문턱도 판정도 바꾸지 않습니다** — 병기용입니다.
    sd0583 = summ['saIm0583']['batch_sd'] if 'saIm0583' in summ else None
    sens = []
    if sd0583:
        for p_ in pairs:
            if p_['asymmetric']:
                continue
            ex = []
            for k in (p_['a'], p_['b']):
                stat = summ[k]['ci95'] if summ[k]['n'] == 1 else summ[k]['ci95']
                ex.append((stat ** 2 + (T95 * sd0583 / summ[k]['n'] ** 0.5) ** 2) ** 0.5
                          if summ[k]['n'] == 1 else summ[k]['ci95'])
            comb = (ex[0] ** 2 + ex[1] ** 2) ** 0.5
            u = p_['delta'] / comb
            sens.append({'a': p_['a'], 'b': p_['b'], 'units_registered': p_['units'],
                         'units_with_batch': u,
                         'flips_to_equal': p_['units'] >= THRESH and u < THRESH})

    out = {'quantity': '습윤 TSA 작업 용량 (mol/kg)',
           'rule': 'ASSIGN_20260904 §2 D3 (결과 전 등록)',
           't95': T95, 'threshold_units': THRESH,
           'duplicate_files_skipped': dupes,
           'compositions': summ, 'pairs': pairs,
           'sensitivity_batch_sd_from_saIm0583': {
               'batch_sd': sd0583,
               'note': '감도일 뿐 판정이 아니다. 등록 문턱 1.5 와 등록 ± 규약은 불변',
               'rows': sens}}
    json.dump(out, open(os.path.join(HERE, 't1_ensemble.json'), 'w',
                        encoding='utf-8'), indent=2, ensure_ascii=False)

    print('=== T-1 습윤 TSA 작업 용량 — 앙상블 재표기 ===\n')
    if dupes:
        print('바이트 동일 파일을 한 번만 셌습니다 (08-23 이중 계수 유형):')
        for d in dupes:
            print(f'    {d["file"]}  ==  {d["same_as"]}')
        print()
    print(f'  {"조성":<12}{"n":>3}{"평균":>10}{"±(등록 규약)":>14}'
          f'{"배치 SD":>10}   ± 의 출처')
    print('  ' + '-' * 74)
    for k in keys:
        s = summ[k]
        sd = f'{s["batch_sd"]:.4f}' if s['batch_sd'] is not None else '—'
        print(f'  {k:<12}{s["n"]:>3}{s["mean"]:>10.4f}{s["ci95"]:>14.4f}'
              f'{sd:>10}   {s["pm_source"]}')
    print(f'\n  앙상블 {len(ens)}개: {", ".join(ens) or "없음"}')
    print(f'  단일 실현 {len(single)}개: {", ".join(single)}')

    print('\n=== 쌍 비교 (등록 문턱 1.5 단위) ===')
    for p in sorted(pairs, key=lambda x: -x['units']):
        mark = '유보' if p['asymmetric'] else ('동급' if p['units'] < THRESH else '차이')
        print(f'  {p["a"]:<12} vs {p["b"]:<12} Δ={p["delta"]:.4f} '
              f'합성±={p["combined_pm"]:.4f}  {p["units"]:>6.2f} 단위  [{mark}]')
    if sens:
        flip = [x for x in sens if x['flips_to_equal']]
        print(f'\n=== [감도, 판정 아님] 단일 실현에 saIm0583 배치 SD({sd0583:.4f})를 대입하면 ===')
        print(f'  단일-단일 쌍 {len(sens)}개 중 **{len(flip)}개**가 1.5 단위 아래로 내려갑니다.')
        for x in sorted(flip, key=lambda y: -y['units_with_batch'])[:12]:
            print(f'    {x["a"]:<12} vs {x["b"]:<12} '
                  f'{x["units_registered"]:>6.2f} -> {x["units_with_batch"]:>5.2f} 단위')
        print('  등록 판정은 위 표 그대로입니다. 이 줄은 **배치 산포가 빠져 있다는 사실의 크기**만')
        print('  보여 줍니다 — 문턱도 ± 규약도 바꾸지 않았습니다.')
    print('\n-> t1_ensemble.json')
    return 0


if __name__ == '__main__':
    sys.exit(main())
