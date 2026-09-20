# -*- coding: utf-8 -*-
"""T-BR-1 판정 — 등록 `BRIDGE_CORE_REGISTRATION_20260920.md §3·§4·§5` 를 그대로 계산한다.

결과: `BRIDGE_CORE_RESULT_20260921.md` (2026-09-21 03:03 — 철회 판정).
실행: ~/miniconda3/envs/czeromof/bin/python 21_ZIF69_MTV/analyze_bridge_core.py
"""
import json
import math
import os

import numpy as np
from scipy.stats import spearmanr

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, 'bridge_core_results.json')

# 등록 §2 ⑦ 로 들어온 Zn 이미다졸레이트 3개 (P5 용)
IMID = {'2011[Zn][sod]3[FSR]2', '2015[Zn][sod]3[ASR]1', '2024[Zn][crb]3[ASR]4'}

AXES = (('K_H(CO2)', 'core_KH_CO2', 'KH_CO2'),
        ('선택도', 'core_selectivity', 'selectivity'))


def main():
    rows = [r for r in json.load(open(SRC, encoding='utf-8'))['rows'] if r['status'] == 'ok']
    print(f'n = {len(rows)}  (등록 §4 P6: 실패는 대체하지 않고 결번으로 둔다)\n')

    verdict = []
    for axis, ck, ok in AXES:
        x = np.array([math.log10(r[ck]) for r in rows])
        y = np.array([math.log10(r[ok]) for r in rows])
        b, a = np.polyfit(x, y, 1)
        res = y - (b * x + a)
        s = float(np.sqrt(np.sum(res ** 2) / (len(x) - 2)))     # 자유도 n-2
        xm = float(np.median(x))
        mult = 10 ** ((b * xm + a) - xm)                        # 중앙에서의 배율 = 우리/CoRE
        rho, p = spearmanr([r[ck] for r in rows], [r[ok] for r in rows])
        d = y - x                                               # β=1 고정(순수 평행이동)일 때

        ri = np.array([e for r_, e in zip(rows, res) if r_['key'] in IMID])
        ro = np.array([e for r_, e in zip(rows, res) if r_['key'] not in IMID])
        p5 = abs(ri.mean() - ro.mean())

        print(f'=== {axis} ===')
        print(f'  β = {b:+.4f}   |β−1| = {abs(b - 1):.4f}    [§4 P1 0.8~1.2 · §5 (ㄱ) >0.2]')
        print(f'  중앙 배율 = {mult:.3f}배                    [§4 P2 1.0~5.0]')
        print(f'  잔차 s = {s:.4f} 자릿수                     [§4 P3 · §5 (ㄴ) >0.5]')
        print(f'  β=1 고정: 평균 배율 {10 ** d.mean():.3f}배 · 잔차 s {d.std(ddof=1):.4f} 자릿수')
        print(f'  Spearman ρ = {rho:+.3f} (p={p:.3f})  — 순위가 이전되는가')
        print(f'  P5 이미다졸레이트 잔차차 {p5:.4f} = {p5 / s:.2f} s  → {"걸림" if p5 > s else "안 걸림"}')
        verdict.append((axis, abs(b - 1) > 0.2, s > 0.5, p5 > s))
        print()

    print('§5 포기 기준')
    trip = False
    for axis, g, n, d_ in verdict:
        print(f'  {axis:9} (ㄱ)|β−1|>0.2 {"걸림" if g else "안걸림"} · '
              f'(ㄴ)s>0.5 {"걸림" if n else "안걸림"} · (ㄷ)P5 {"걸림" if d_ else "안걸림"}')
        trip = trip or g or n or d_
    print(f'\n  → {"철회" if trip else "통과"}  '
          f'({"우리 물질을 CoRE 성능 축에 놓지 않습니다" if trip else "측정 배율로 환산해 얹되 배율·잔차를 그림에 적습니다"})')


if __name__ == '__main__':
    main()
