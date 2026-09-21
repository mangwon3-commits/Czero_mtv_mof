# -*- coding: utf-8 -*-
"""§AV 비용 눈금 — **T-BR-1 실행 폴더에서 24점 크기 주사를 뽑는다.**

왜: 09-21 15:0x 에 두 기기의 눈금이 서로 모순됐다.
    랩탑   N_super 1520 -> 18.0 분 (8워커)  -> 선형 가정으로 19.3 h
    laptop2 N_super  396 -> 13.1 분 (12워커) -> 같은 선형 가정이면 54.6 h
    두 값이 **같은 법칙 아래 동시에 참일 수 없다.** 크기 지수를 따로 재야 풀린다.

무엇으로: T-BR-1 의 `bridge_core_runs/` 가 남아 있다. **24작업 · 2워커 · 같은 러너 · 같은 기체 ·
    N_super 640~3726.** 경합이 거의 없는 조건의 **같은 계 실측**이고, 지금 유일하게 지수를 주는 자료다.
    시작 = `simulation.input` mtime(러너가 subprocess 직전에 씀) · 끝 = `.data` mtime.
    (디렉터리 ctime 은 리눅스에서 나중에 갱신되므로 쓰면 안 된다 — 전부 0 이 나온다.)

실행: ~/miniconda3/envs/czeromof/bin/python cost_scan_core_pop.py
"""
import datetime as dt
import glob
import json
import math
import os

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))

# 각 기기가 자기 묶음에서 낸 실측 눈금 (host, 워커, N_super, 분, 착수시각)
ANCHORS = [('laptop', 8, 1520, 18.03, '2026-09-21 14:25:05'),
           ('laptop2', 12, 396, 13.10, '2026-09-21 14:24:32')]


def scan():
    byfile = {os.path.splitext(p['file'])[0]: p
              for p in json.load(open(os.path.join(HERE, 'bridge_core_pick.json'), encoding='utf-8'))}
    rows = []
    for d in sorted(glob.glob(os.path.join(HERE, 'bridge_core_runs', 'widom_*'))):
        dat = glob.glob(os.path.join(d, 'Output', 'System_0', '*.data'))
        inp = os.path.join(d, 'simulation.input')
        if not dat or not os.path.exists(inp):
            continue
        gas, name = os.path.basename(d).split('_', 2)[1:3]
        p = byfile.get(name)
        if not p:
            continue
        dur = (os.path.getmtime(dat[0]) - os.path.getmtime(inp)) / 60
        if dur > 0.5:
            rows.append((p['N_super'], gas, name, dur))
    return sorted(rows)


def main():
    rows = scan()
    xs = np.log([n for n, _, _, _ in rows])
    ys = np.log([t for _, _, _, t in rows])
    b, a = np.polyfit(xs, ys, 1)
    r = float(np.corrcoef(xs, ys)[0, 1])
    print(f'T-BR-1 크기 주사  n={len(rows)} · N_super {rows[0][0]}~{rows[-1][0]} · 2워커')
    for n, g, nm, t in rows:
        print(f'  {n:6} {g:>3} {t:6.1f} 분  {nm}')
    print(f'\n**지수 b = {b:.3f}**   (로그-로그 r = {r:+.3f})')
    print(f'  데스크탑 2워커 예측: 396 {math.exp(a)*396**b:.1f}분 · 1520 {math.exp(a)*1520**b:.1f} · '
          f'3200 {math.exp(a)*3200**b:.1f} · 5670 {math.exp(a)*5670**b:.1f}\n')

    pick = json.load(open(os.path.join(HERE, 'core_pop_pick.json'), encoding='utf-8'))
    for host, w, aN, aT, t0 in ANCHORS:
        k = aT / aN ** b
        s = [p for p in pick if p['assign'] == host]
        tot = sum(2 * k * p['N_super'] ** b for p in s) / 60
        mx = max(k * p['N_super'] ** b for p in s) / 60
        div = tot / w
        eta = max(mx, div)
        st = dt.datetime.strptime(t0, '%Y-%m-%d %H:%M:%S')
        cont = aT / (math.exp(a) * aN ** b)
        print(f'{host:8} 워커 {w:2} · 눈금 {aN}->{aT:.1f}분 · **경합 배수 {cont:.2f}x** (데스크탑 2워커 대비)')
        print(f'         작업합 {tot:.1f} h · ÷{w} = {div:.2f} h · 최장 단일 {mx:.2f} h · '
              f'묶는 쪽 **{"작업합/워커" if div > mx else "최장 단일"}**')
        print(f'         완주 예상 **{(st + dt.timedelta(hours=eta)).strftime("%m-%d %H:%M")}**')
    print('\n감도 (각자 자기 눈금 고정)')
    print(f'{"지수":>6} {"laptop h":>10} {"laptop2 h":>11}')
    for bb in (0.4, 0.5, b, 0.75, 0.9, 1.0):
        o = []
        for host, w, aN, aT, _ in ANCHORS:
            kk = aT / aN ** bb
            s = [p for p in pick if p['assign'] == host]
            o.append(sum(2 * kk * p['N_super'] ** bb for p in s) / 60 / w)
        print(f'{bb:6.3f} {o[0]:10.1f} {o[1]:11.1f}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
