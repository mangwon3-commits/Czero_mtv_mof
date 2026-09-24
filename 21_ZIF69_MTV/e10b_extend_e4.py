"""E-10b 확장: E-4 사다리 점을 더해 Spearman rho(G, 예측자) 재계산 (등록 E10B_G_PREDICTOR_20260925.md, 예측자 정의 그대로)."""
import json, glob, re, math, random
import numpy as np
from pymatgen.io.cif import CifParser
base = json.load(open('e10b_g_predictor.json'))
POL = {'O', 'N', 'F', 'S', 'Cl'}

def charges(cif):
    p = CifParser(cif); blk = list(p.as_dict().values())[0]
    q = np.array([float(x) for x in blk['_atom_site_charge']])
    el = [re.sub(r'[^A-Za-z]', '', x) for x in blk['_atom_site_type_symbol']]
    s = p.parse_structures(primitive=False)[0] if hasattr(p, 'parse_structures') else p.get_structures(primitive=False)[0]
    return q, el, s.volume

def rows_e4():
    zeo = json.load(open('e4_zeo_relaxed.json')); out = []
    for f in sorted(glob.glob('results_magi5_e3_e4zif*_widom_*.json')):
        d = json.load(open(f)); rs = d if isinstance(d, list) else d['rows']
        tag = re.search(r'(e4zif\d+)', f).group(1)
        on = [r for r in rs if r['charges'] == 'on'][0]; off = [r for r in rs if r['charges'] == 'off'][0]
        q, el, V = charges(f'charged_v3/{tag}_DDEC6.cif'); a = np.sort(np.abs(q))[::-1]
        k = max(1, int(round(0.1 * len(a))))
        out.append(dict(name=tag, G=on['selectivity'] / off['selectivity'], LCD=zeo[tag]['LCD'], n=len(q),
                        rms=float(np.sqrt((q ** 2).mean())), top10=float(a[:k].mean()), sumq_V=float(np.abs(q).sum() / V),
                        pol=sum(e in POL for e in el) / len(el), src='E-4'))
    return out

from scipy.stats import spearmanr
def rho(x, y): return float(spearmanr(x, y)[0])
def boot(x, y, B=5000, seed=1):
    rnd = random.Random(seed); n = len(x); v = []
    for _ in range(B):
        idx = [rnd.randrange(n) for _ in range(n)]
        xs = [x[i] for i in idx]; ys = [y[i] for i in idx]
        if len(set(xs)) > 1 and len(set(ys)) > 1: v.append(rho(xs, ys))
    v.sort(); return v[int(0.025 * len(v))], v[int(0.975 * len(v))]

if __name__ == '__main__':
    e4 = rows_e4(); allr = [dict(r, src=r.get('src', 'E-10b')) for r in base] + e4
    for r in e4: print(f"{r['name']:9s} G {r['G']:.2f} top10 {r['top10']:.3f} rms {r['rms']:.3f} sumq_V {r['sumq_V']:.4f} pol {r['pol']:.3f} n {r['n']}")
    res = {}
    for lab, rows in (('n15', base), ('E4only', e4), ('all', allr)):
        G = [r['G'] for r in rows]; res[lab] = {'n': len(rows)}
        for p in ('rms', 'top10', 'sumq_V', 'LCD', 'pol'):
            pr = [(r[p], r['G']) for r in rows if r.get(p) is not None]; x = [a for a, _ in pr]; G = [b for _, b in pr]
            lo, hi = boot(x, G); res[lab][p] = [round(rho(x, G), 3), round(lo, 3), round(hi, 3), len(x)]
        print(lab, res[lab])
    json.dump({'rows': allr, 'spearman': res}, open('e10b_g_predictor_e4.json', 'w'), indent=1)
