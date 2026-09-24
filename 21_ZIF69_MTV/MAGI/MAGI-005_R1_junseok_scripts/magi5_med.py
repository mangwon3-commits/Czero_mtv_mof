import json, sys, zipfile, statistics as st
import numpy as np
exec(open(sys.argv[2]).read().split("X = json.load")[0])   # desc()·charges() 재사용 (파일 위쪽 정의부만)
X = json.load(open(sys.argv[1])); z = zipfile.ZipFile(D + 'core_pop_cifs.zip')
for x in X:
    x['L'] = (x['n015'] / (x['KH_CO2'] * 15000.0)) if (x['n015'] and x['KH_CO2']) else None
for lab, g in (('S>75.8', [x for x in X if x['S'] > 75.8]), ('S 40~75.8', [x for x in X if 40 <= x['S'] <= 75.8]),
               ('S 20~40', [x for x in X if 20 <= x['S'] < 40]), ('S<20', [x for x in X if x['S'] < 20])):
    L = [x['L'] for x in g if x['L']]
    print('%-10s n %3d  L 중앙 %.3f (사분위 %.3f/%.3f)  LCD 중앙 %.2f  PLD 중앙 %.2f' % (lab, len(g), st.median(L), np.percentile(L, 25), np.percentile(L, 75),
          st.median([x['LCD'] for x in g]), st.median([x['PLD'] for x in g])))
top = [x for x in X if x['S'] > 75.8]
q = []
for x in top:
    d = desc(z.read(x['file']).decode('utf-8', 'ignore')); q.append(d['qfree'] or 0.0)
print('S>75.8 48행 |q|자유 중앙 %.2f e/nm3 (사분위 %.2f/%.2f) · 우리 saIm050 4.19 · sa50nb50 5.38 보다 큰 행 %d/48' % (
      st.median(q), np.percentile(q, 25), np.percentile(q, 75), sum(1 for v in q if v > 4.19)))
