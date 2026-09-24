import json, sys, zipfile, re
from scipy.stats import spearmanr
exec(open(sys.argv[2]).read().split("X = json.load")[0])
X = json.load(open(sys.argv[1])); z = zipfile.ZipFile(D + 'core_pop_cifs.zip')
for x in X:
    d = desc(z.read(x['file']).decode('utf-8', 'ignore')); x['q'] = d['qfree'] or 0.0
def uniq(h):   # ASR/FSR 판본 중복을 줄이는 느슨한 열쇠: 계열 + 조성 격자(PLD·LCD 반올림)
    seen = {}; 
    for x in h:
        k = (re.sub(r'\[(ASR|FSR|ION)\]\d+', '', x['key']), round(x['PLD'], 2), round(x['LCD'], 2))
        seen.setdefault(k, x)
    return list(seen.values())
for kind in ('N-only', 'N+O', 'O-only'):
    for lab, lo, hi in (('LCD<5', 0, 5), ('LCD 5~7', 5, 7), ('LCD>=7', 7, 99)):
        h = [x for x in X if x['kind'] == kind and lo <= x['LCD'] < hi]
        u = uniq(h)
        if len(u) < 6:
            print('  %-7s %-8s 행 %3d · 고유 %3d (너무 적음)' % (kind, lab, len(h), len(u))); continue
        r, p = spearmanr([x['q'] for x in u], [x['S'] for x in u])
        print('  %-7s %-8s 행 %3d · 고유 %3d · ρ(S,|q|자유) %+.2f (p %.2g)' % (kind, lab, len(h), len(u), r, p))
