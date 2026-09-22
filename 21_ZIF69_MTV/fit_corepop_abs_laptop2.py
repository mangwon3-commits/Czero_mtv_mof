# -*- coding: utf-8 -*-
"""§AV 절대시간 직접 적합 — 배수를 거치지 않는다. 데스크탑 값을 일절 쓰지 않는다.

t(분) = A · N_super^b  를 laptop2 실측만으로 긋는다.
시작 = simulation.input mtime · 끝 = .data mtime (완주 표지 있는 것만).
"""
import glob
import json
import math
import os
import statistics as st

RUNS = 'core_pop_runs'
pick = {x['file'][:-4]: x for x in json.load(open('core_pop_pick.json'))
        if x['assign'] == 'laptop2'}

pts = []          # (N_super, 분, gas)
skipped = 0
for d in sorted(os.listdir(RUNS)):
    p = os.path.join(RUNS, d)
    if not os.path.isdir(p) or not d.startswith('widom_'):
        continue
    gas, name = d.split('_', 2)[1], d.split('_', 2)[2]
    if name not in pick:
        skipped += 1
        continue
    f = glob.glob(os.path.join(p, 'Output', 'System_0', '*.data'))
    if not f:
        continue
    try:
        with open(f[0], encoding='utf-8', errors='ignore') as fh:
            if 'Simulation finished' not in fh.read():
                continue
    except OSError:
        continue
    i = os.path.join(p, 'simulation.input')
    if not os.path.exists(i):
        continue
    mins = (os.stat(f[0]).st_mtime - os.stat(i).st_mtime) / 60.0
    if mins <= 0:
        skipped += 1
        continue
    pts.append((pick[name]['N_super'], mins, gas))

print('완주 작업 %d개 · 제외 %d' % (len(pts), skipped))
print('크기 점(서로 다른 N_super) **%d개**' % len(set(p[0] for p in pts)))


def fit(sub, label):
    X = [math.log(n) for n, t, _ in sub]
    Y = [math.log(t) for n, t, _ in sub]
    mx, my = st.mean(X), st.mean(Y)
    sxx = sum((x - mx) ** 2 for x in X)
    b = sum((x - mx) * (y - my) for x, y in zip(X, Y)) / sxx
    a = my - b * mx
    res = [y - (a + b * x) for x, y in zip(X, Y)]
    dof = len(X) - 2
    s = math.sqrt(sum(r * r for r in res) / dof)
    seb = s / math.sqrt(sxx)
    r = (sum((x - mx) * (y - my) for x, y in zip(X, Y))
         / math.sqrt(sxx * sum((y - my) ** 2 for y in Y)))
    lo, hi = b - 1.96 * seb, b + 1.96 * seb
    print('  %-14s n=%4d · b = **%.4f** · SE %.4f · dof %d · 95%%CI [%.3f, %.3f] · r %+.4f · A %.4f'
          % (label, len(X), b, seb, dof, lo, hi, r, math.exp(a)))
    print('                 잔차 로그SD %.4f (= 산포 %.1f %%)' % (s, 100 * (math.exp(s) - 1)))
    return math.exp(a), b


print()
print('=== 절대시간 직접 적합 (laptop2 실측만, 12워커) ===')
A, b = fit(pts, '전체')
fit([p for p in pts if p[2] == 'CO2'], 'CO2만')
fit([p for p in pts if p[2] == 'N2'], 'N2만')

done = set()
for d in os.listdir(RUNS):
    if d.startswith('widom_CO2_'):
        done.add(d[len('widom_CO2_'):])
rows = json.load(open('core_pop_results_laptop2.json'))['rows']
finished = set(r['file'][:-4] for r in rows)
rest = [x for k, x in pick.items() if k not in finished]
left = sum(2 * A * x['N_super'] ** b for x in rest) / 60.0 / 12
print()
print('=== 남은 %d종 견적 (이 적합으로) ===' % len(rest))
print('  남은 작업합 %.1f h ÷ 12워커 = **%.2f h**' % (left * 12, left))
