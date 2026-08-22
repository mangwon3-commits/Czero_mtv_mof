"""자리 배치 앙상블 판정 — ENSEMBLE_0583_PROTOCOL.md 의 등록 기준을 적용한다.

[이 파일이 결과보다 먼저 쓰인 이유]
    사전 등록의 요점은 문턱만 미리 정하는 것이 아니라 **계산 방법도** 미리
    정하는 것입니다. 자료를 본 뒤에 통계를 고르면, 문턱을 안 건드려도
    결론을 고를 수 있습니다. 그래서 GCMC 가 6/15 인 시점에 씁니다.

[적용하는 기준 — 프로토콜 원문]
    s_ens = 6개 실현의 표본 표준편차(ddof=1)
    sigma_stat = 개별 실행 통계 오차의 중앙값

    s_ens <= 1.0 sigma_stat        배치 분산은 분해능 아래. 단일 실현 유지
    1.0 < s_ens <= 1.5 sigma_stat  구별 불가 구간. s_ens 를 상한으로 병기
    s_ens > 1.5 sigma_stat         배치 분산 실재. 이후 비교에
                                   sigma_total = sqrt(sigma_stat^2 + s_ens^2)

    어느 경우에도 판정 지표(습윤 TSA WC)와 관문 문턱은 바뀌지 않습니다.

[N=5 병기 규칙]
    프로토콜에 추가 등록된 대로, s_ens 가 문턱 근처(0.8~1.7 배)면 e5 를 뺀
    N=5 값도 함께 찍습니다. 한 실현이 결론을 좌우하는지 보이기 위해서입니다.

사용:
    python analyze_ensemble_0583.py
"""
import argparse
import json
import os
import statistics as st
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ENS = os.path.join(HERE, 'results_v3ens0583.json')
PROD = os.path.join(HERE, 'results_v3grid.json')
PROD_TAG = 'saIm0583'
ENS_TAGS = [f'saIm0583e{i}' for i in range(1, 6)]

# 프로토콜에 적힌 계산 전 예측. 빗나가면 빗나갔다고 적기 위해 코드에 둔다.
PREDICTED = {'loading_015bar': (0.01, 0.03),   # 상대 1~3%
             'Qst_CO2': (0.2, 0.5)}            # kJ/mol


def rows_of(path):
    if not os.path.exists(path):
        return {}
    d = json.load(open(path, encoding='utf-8'))
    return {r['name']: r for r in d.get('rows', d if isinstance(d, list) else [])}


def band(ratio):
    if ratio <= 1.0:
        return '분해능 아래 — 단일 실현 프로토콜 유지'
    if ratio <= 1.5:
        return '구별 불가 — s_ens 를 상한으로 병기'
    return '배치 분산 실재 — 이후 비교에 sigma_total 사용'


def report(metric, err_key, unit, vals, errs, tags):
    n = len(vals)
    mean = st.mean(vals)
    s_ens = st.stdev(vals) if n > 1 else float('nan')
    sig = st.median(errs)
    ratio = s_ens / sig if sig else float('nan')
    print(f'\n=== {metric} ({unit}) ===')
    for t, v, e in zip(tags, vals, errs):
        mark = '  <- 생산 seed 0' if t == PROD_TAG else ''
        print(f'  {t:12s} {v:12.4f} ± {e:.4f}{mark}')
    print(f'  {"평균":12s} {mean:12.4f}   (N={n})')
    print(f'  s_ens        {s_ens:12.4f}   실현 간 표본 표준편차 (ddof=1)')
    print(f'  sigma_stat   {sig:12.4f}   개별 실행 통계오차의 중앙값')
    print(f'  s_ens/sigma  {ratio:12.2f}   -> {band(ratio)}')
    rel = s_ens / mean if mean else float('nan')
    print(f'  상대 s_ens   {rel*100:11.2f}%')
    lo, hi = PREDICTED[metric]
    pred = f'{lo*100:.0f}~{hi*100:.0f}%' if metric == 'loading_015bar' else f'{lo}~{hi}'
    got = rel if metric == 'loading_015bar' else s_ens
    hit = lo <= got <= hi
    print(f'  계산 전 예측 {pred}  -> {"적중" if hit else "빗나감"}')
    return ratio, s_ens, sig


def main():
    # [2026-08-22] 경로를 인자로 뺍니다.
    #
    #   이 스크립트를 합성 자료로 검증할 때 생산 파일(results_v3grid.json)을
    #   잠시 덮어썼습니다. 복구를 확인했지만 그럴 필요가 없는 일이었습니다 --
    #   검사기를 시험하려고 생산 자료를 건드리는 것은 이 저장소가 경계하는
    #   유형입니다. 다음부터는 --prod 로 사본을 주세요.
    ap = argparse.ArgumentParser(description='앙상블 판정 (기준은 프로토콜 문서)')
    ap.add_argument('--ens', default=ENS, help='앙상블 결과 JSON')
    ap.add_argument('--prod', default=PROD, help='생산 seed 0 결과 JSON')
    a = ap.parse_args()
    ens, prod = rows_of(a.ens), rows_of(a.prod)
    if not ens:
        print(f'!! {a.ens} 가 아직 없습니다. GCMC 가 끝난 뒤 다시 도세요.')
        return 1
    missing = [t for t in ENS_TAGS if t not in ens]
    if missing:
        print(f'!! 실현 누락: {missing} — 완주 후 다시 도세요.')
        return 1
    if PROD_TAG not in prod:
        print(f'!! 생산 seed 0 ({PROD_TAG}) 을 {a.prod} 에서 못 찾았습니다.')
        return 1

    print('자리 배치 앙상블 — saIm0583 (−SO3H 14/24)')
    print('기준: ENSEMBLE_0583_PROTOCOL.md (계산 전 등록)')
    tags = [PROD_TAG] + ENS_TAGS
    rowmap = {PROD_TAG: prod[PROD_TAG], **{t: ens[t] for t in ENS_TAGS}}

    near = []
    for metric, err_key, unit in (('loading_015bar', 'loading_015bar_err', 'mol/kg'),
                                  ('Qst_CO2', 'Qst_CO2_err', 'kJ/mol')):
        vals = [rowmap[t][metric] for t in tags]
        errs = [rowmap[t][err_key] for t in tags]
        ratio, s_ens, sig = report(metric, err_key, unit, vals, errs, tags)
        if 0.8 <= ratio <= 1.7:
            near.append((metric, err_key))

    # 프로토콜의 N=5 병기 규칙
    for metric, err_key in near:
        t5 = [t for t in tags if t != 'saIm0583e5']
        vals = [rowmap[t][metric] for t in t5]
        errs = [rowmap[t][err_key] for t in t5]
        print(f'\n--- {metric}: 문턱 근처이므로 e5 제외 N=5 도 병기 (프로토콜 등록) ---')
        s5 = st.stdev(vals)
        r5 = s5 / st.median(errs)
        print(f'  N=5  s_ens {s5:.4f}  s_ens/sigma {r5:.2f}  -> {band(r5)}')

    print('\n주의: 이 결과는 판정 지표(습윤 TSA 작업 용량)와 관문 문턱을')
    print('      바꾸지 않습니다. 바뀌는 것은 조성 간 비교에 쓸 오차뿐입니다.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
