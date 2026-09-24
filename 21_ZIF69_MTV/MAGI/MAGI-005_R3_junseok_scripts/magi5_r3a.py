import json, sys, zipfile, statistics as st
from scipy.stats import spearmanr
exec(open(sys.argv[2]).read().split("X = json.load")[0])   # desc() 재사용
X = json.load(open(sys.argv[1])); z = zipfile.ZipFile(D + 'core_pop_cifs.zip')
g = [x for x in X if x['kind'] == 'N-only']
for x in g:
    d = desc(z.read(x['file']).decode('utf-8', 'ignore')); x['q'] = d['qfree'] or 0.0; x['fNO'] = d['fNO']
def rep(lab, h):
    if len(h) < 6: print('  %-28s n %d (너무 적음)' % (lab, len(h))); return
    r, p = spearmanr([x['q'] for x in h], [x['S'] for x in h])
    print('  %-28s n %3d · ρ(S, |q|자유) %+.2f (p %.2g) · 자유 |q|>0 인 행 %d' % (lab, len(h), r, p, sum(1 for x in h if x['q'] > 0)))
rep('N만 전체', g)
rep('N만 · PLD<4.5', [x for x in g if x['PLD'] < 4.5])
rep('N만 · LCD<5', [x for x in g if x['LCD'] < 5])
rep('N만 · LCD 5~7', [x for x in g if 5 <= x['LCD'] < 7])
rep('N만 · LCD>=7', [x for x in g if x['LCD'] >= 7])
print('  N만 · LCD<5 행:'); [print('    %-24s LCD %.2f PLD %.2f S %6.1f |q|자유 %.2f 자유N·O %.2f' % (x['key'][:24], x['LCD'], x['PLD'], x['S'], x['q'], x['fNO'])) for x in sorted([x for x in g if x['LCD'] < 5], key=lambda x: -x['S'])]
