# -*- coding: utf-8 -*-
"""§AV 결과 — **우리 조성을 CoRE 모집단 위에 놓는다. 환산 없이.**

등록 `COREPOP_REGISTRATION_20260921.md` §5(예측)·§6(사용 제한)을 그대로 따릅니다.
§6 (ㄴ) 백분위는 **항상 풀의 정의와 함께** · (ㄷ) 범위 밖이면 백분위가 아니라 "풀 최대보다 위" ·
(ㅁ) 우리 값은 **그대로** 얹습니다(같은 러너에서 나왔다는 것이 전제).
"""
import json
import math
import statistics as st

POOL_DEF = "관문 통과 · SI 출처 CIF · ≤400원자 · UFF_MOF 표현 가능 **524종**"

m = json.load(open('core_pop_merged.json', encoding='utf-8'))
core = [r for r in m['rows'] if r.get('KH_CO2') and r.get('KH_N2')]
ours = json.load(open('results_v3.json', encoding='utf-8'))
if isinstance(ours, dict):
    ours = ours.get('rows', ours)
if isinstance(ours, dict):
    ours = [dict(v, tag=k) for k, v in ours.items()]
ours = [r for r in ours if r.get('KH_CO2') and r.get('KH_N2')]

print(f'CoRE 모집단 (우리 자) n = **{len(core)}** / 524   [{POOL_DEF}]')
print(f'우리 조성 n = {len(ours)}   — 같은 러너·같은 프로토콜, **환산 없음**\n')


def pct(v, arr):
    a = sorted(arr)
    if v > a[-1]:
        return None
    return sum(1 for x in a if x <= v) / len(a) * 100


def q(arr, p):
    a = sorted(arr)
    return a[min(len(a) - 1, int(p * len(a)))]


for name, fc, fo in (('K_H(CO2) [mmol/g/Pa]', lambda r: r['KH_CO2'], lambda r: r['KH_CO2']),
                     ('선택도 CO2/N2', lambda r: r['selectivity'],
                      lambda r: r['KH_CO2'] / r['KH_N2'])):
    C = [fc(r) for r in core]
    O = [(r.get('tag') or r.get('name'), fo(r)) for r in ours]
    O.sort(key=lambda t: -t[1])
    print(f'=== {name} ===')
    print(f'  CoRE 모집단  최소 {min(C):.3e} · 25% {q(C,.25):.3e} · 중앙 {st.median(C):.3e} · '
          f'75% {q(C,.75):.3e} · 최대 {max(C):.3e}')
    print(f'  우리 계열    최소 {min(v for _,v in O):.3e} · 중앙 {st.median([v for _,v in O]):.3e} · '
          f'최대 {max(v for _,v in O):.3e}')
    print('  우리 조성의 자리 (상위 6 + 중앙 + 최하):')
    idx = list(range(4)) + [len(O)//2] + [len(O)-1]
    for i in idx:
        nm, v = O[i]
        p = pct(v, C)
        s = f'{p:5.1f} %' if p is not None else '**풀 최대보다 위**'
        print(f'    {nm:<12} {v:.3e}   백분위 {s}')
    above = sum(1 for _, v in O if pct(v, C) is None)
    top10 = sum(1 for _, v in O if (pct(v, C) or 100) >= 90)
    print(f'  우리 {len(O)}조성 중 90 %tile 이상 **{top10}**개 · 풀 최대 초과 {above}개\n')
