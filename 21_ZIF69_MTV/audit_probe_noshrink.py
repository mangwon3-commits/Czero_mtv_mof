#!/usr/bin/env python
"""T-3 탐침 무수축 감사 (DESIGN_STUDY_20260903.md §5-A, 사전 등록).

문제: risk_screen_v3 의 UFF4MOF 탐침에서 base 는 LCD 8.898 → 7.631 로 수축하는데
fbIm075/100, mbIm075/100 은 수축하지 않는다(오히려 +). "결함이 결과처럼 보이는" 전형이라
(CLAUDE.md §0) 인용하기 전에 구조부터 의심한다.

검사 대상 기하
  (a) GFN-FF 이완본  relax_v3/ZIF69_<tag>_relaxed.cif  (base 는 relax_fixcell/…)
  (b) UFF4MOF 탐침 후 min_<name>.data  — lmp_v3/ 가 정리돼 지금은 없음. --probe-data 로
      디렉터리를 주면 같은 검사를 돌린다. 없으면 (a) 만 하고 재실행 필요를 적는다.

지표 (구조마다 원자 단위)
  Zn–N 길이, Zn 배위수, N–Zn–N 각, 고리(5원·6원) 평면성 RMSD, 최소 원자간 거리,
  H 가 낀 원소쌍별 최소 거리(v2 빌더 결함이 F–H 0.56~0.70 Å 였다).

판정 (T-3 그대로, 결과 보고 고치지 않는다)
  base 분포(평균±3σ) 밖 원자/각/고리가 1개라도 있거나 최소 원자간 거리 < 0.7 Å
  → '깨진 구조' 표기, 인용 금지.  아니면 '정상 — 탐침 무수축 원인 미해명'.
  base 자신에도 같은 규칙을 걸어 규칙이 판별력이 있는지(base 가 스스로를 깨진 구조로
  찍으면 규칙이 아니라 σ 가 문제) 같이 보고한다. 문턱은 바꾸지 않는다.

실행:  nice -n 19 ~/miniconda3/envs/czeromof/bin/python audit_probe_noshrink.py
       (전체 거리 행렬을 만들지 않는다 — neighbor_list 만. 4800원자 슈퍼셀도 안전.)
"""
import argparse
import collections
import json
import os
import sys

import numpy as np
from ase.io import read
from ase.neighborlist import neighbor_list

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from relax_criteria import COV  # noqa: E402  — relax_v3 판정과 같은 공유 반지름

DEFAULT_TAGS = ['base', 'fbIm025', 'fbIm050', 'fbIm075', 'fbIm100',
                'mbIm025', 'mbIm050', 'mbIm075', 'mbIm100']
ZN_N_CUT = 2.5        # Å, 배위 판정. UFF/GFN-FF 의 Zn–N 은 1.95~2.05
MIN_DIST_LIMIT = 0.7  # Å, risk_results_v3.json criteria.min_dist_limit 과 동일
NSIG = 3.0


def cif_path(tag):
    if tag == 'base':
        return os.path.join(HERE, 'relax_fixcell', 'base_relaxed_gfnff_fixcell.cif')
    return os.path.join(HERE, 'relax_v3', f'ZIF69_{tag}_relaxed.cif')


def bond_graph(atoms):
    """1.25×(COV_a+COV_b) 이내를 결합으로. Zn–N 은 여기 포함되지 않는다(1.25×1.93=2.41 은
    포함되지만 배위는 따로 센다). 돌려주는 것: adjacency dict, 최소상 벡터 dict."""
    syms = atoms.get_chemical_symbols()
    uniq = sorted(set(syms))
    cut = {(a, b): 1.25 * (COV[a] + COV[b]) for a in uniq for b in uniq}
    i, j, D = neighbor_list('ijD', atoms, cut)
    adj = collections.defaultdict(list)
    vec = {}
    for a, b, d in zip(i, j, D):
        adj[a].append(b)
        vec[(a, b)] = d
    return adj, vec


def zn_metrics(atoms):
    syms = np.array(atoms.get_chemical_symbols())
    i, j, d, D = neighbor_list('ijdD', atoms, ZN_N_CUT)
    sel = (syms[i] == 'Zn') & (syms[j] == 'N')
    lengths = []
    per_zn = collections.defaultdict(list)
    for a, b, dd, DD in zip(i[sel], j[sel], d[sel], D[sel]):
        lengths.append((int(a), int(b), float(dd)))
        per_zn[int(a)].append(DD)
    coord = {int(z): len(per_zn[int(z)]) for z in np.where(syms == 'Zn')[0]}
    angles = []
    for z, vs in per_zn.items():
        for p in range(len(vs)):
            for q in range(p + 1, len(vs)):
                c = np.dot(vs[p], vs[q]) / (np.linalg.norm(vs[p]) * np.linalg.norm(vs[q]))
                angles.append((z, float(np.degrees(np.arccos(np.clip(c, -1, 1))))))
    return lengths, coord, angles


def find_rings(adj, syms, sizes=(5, 6)):
    """수소를 뺀 결합 그래프에서 5·6원 단순 고리. 각 고리는 정렬된 tuple 로 중복 제거."""
    heavy = {a: [b for b in nb if syms[b] != 'H' and syms[b] != 'Zn'] for a, nb in adj.items()
             if syms[a] not in ('H', 'Zn')}
    rings = set()
    maxlen = max(sizes)

    def dfs(start, cur, path, visited):
        for nxt in heavy.get(cur, []):
            if nxt == start and len(path) in sizes:
                rings.add(tuple(sorted(path)) + ('ORDER',) + tuple(path))
            elif nxt not in visited and len(path) < maxlen and nxt > start:
                dfs(start, nxt, path + [nxt], visited | {nxt})

    for s in heavy:
        dfs(s, s, [s], {s})
    # 같은 원자 집합의 고리는 하나만 (방향·시작점 중복)
    out = {}
    for r in rings:
        k = r[:r.index('ORDER')]
        out.setdefault(k, r[r.index('ORDER') + 1:])
    return list(out.values())


def ring_planarity(ring, vec, atoms):
    """고리를 그래프 따라 언랩한 뒤 최적 평면에서의 RMS 편차(Å)."""
    pos = {ring[0]: np.zeros(3)}
    for a, b in zip(ring, ring[1:]):
        pos[b] = pos[a] + vec[(a, b)]
    P = np.array([pos[a] for a in ring])
    P -= P.mean(axis=0)
    _, s, _ = np.linalg.svd(P)
    return float(s[-1] / np.sqrt(len(ring)))


def min_distances(atoms):
    """최소 원자간 거리와, H 가 낀 원소쌍별 최소 거리. 컷 사다리로 빈 결과를 피한다."""
    syms = np.array(atoms.get_chemical_symbols())
    for cut in (2.0, 4.0, 8.0):
        i, j, d = neighbor_list('ijd', atoms, cut)
        if len(d):
            break
    dmin = float(d.min()) if len(d) else float('inf')
    pair_min = {}
    for a, b, dd in zip(i, j, d):
        if a >= b:
            continue
        key = '-'.join(sorted((syms[a], syms[b])))
        if dd < pair_min.get(key, 9e9):
            pair_min[key] = float(dd)
    return dmin, pair_min


def audit(atoms):
    syms = atoms.get_chemical_symbols()
    adj, vec = bond_graph(atoms)
    lengths, coord, angles = zn_metrics(atoms)
    rings = find_rings(adj, syms)
    rp = {5: [], 6: []}
    for r in rings:
        rp[len(r)].append(ring_planarity(r, vec, atoms))
    dmin, pair_min = min_distances(atoms)
    return {
        'n_atoms': len(atoms),
        'formula': atoms.get_chemical_formula(),
        'ZnN': [l[2] for l in lengths],
        'Zn_coord': collections.Counter(coord.values()),
        'NZnN': [a[1] for a in angles],
        'ring5_rmsd': rp[5],
        'ring6_rmsd': rp[6],
        'n_ring5': len(rp[5]),
        'n_ring6': len(rp[6]),
        'dmin': dmin,
        'pair_min': pair_min,
    }


def stats(x):
    x = np.asarray(x, float)
    if len(x) == 0:
        return {'n': 0, 'mean': None, 'sd': None, 'min': None, 'max': None}
    return {'n': int(len(x)), 'mean': float(x.mean()), 'sd': float(x.std(ddof=1)) if len(x) > 1 else 0.0,
            'min': float(x.min()), 'max': float(x.max())}


def outliers(x, ref):
    """base 분포 mean±3σ 밖 개수와 최대 |z|."""
    x = np.asarray(x, float)
    if len(x) == 0 or ref['n'] < 2 or ref['sd'] == 0:
        return {'n_out': None, 'max_z': None}
    z = (x - ref['mean']) / ref['sd']
    return {'n_out': int((np.abs(z) > NSIG).sum()), 'max_z': float(np.abs(z).max())}


METRICS = ['ZnN', 'NZnN', 'ring5_rmsd', 'ring6_rmsd']


def judge(m, ref):
    per = {k: outliers(m[k], ref[k]) for k in METRICS}
    n_out = sum(v['n_out'] or 0 for v in per.values())
    broken = n_out > 0 or m['dmin'] < MIN_DIST_LIMIT
    coord_bad = any(k != 4 for k in m['Zn_coord'])
    return {
        'outliers': per,
        'n_out_total': n_out,
        'dmin_ok': m['dmin'] >= MIN_DIST_LIMIT,
        'Zn_coord_all4': not coord_bad,  # 판정 항목 아님, 정보용
        'verdict': '깨진 구조 — 인용 금지' if broken else '정상 — 탐침 무수축 원인 미해명',
    }


def load_probe(dirpath, tag):
    """risk_screen 이 남긴 min_<name>.data (LAMMPS full, nocoeff). 질량으로 원소 추정."""
    name = 'base' if tag == 'base' else f'ZIF69_{tag}'
    for cand in (f'min_{name}.data', f'min_{tag}.data'):
        p = os.path.join(dirpath, cand)
        if os.path.exists(p):
            return read(p, format='lammps-data', style='full', units='real')
    return None


def risk_context():
    p = os.path.join(HERE, 'risk_results_v3.json')
    if not os.path.exists(p):
        return {}
    rows = json.load(open(p))['rows']
    out = {}
    for r in rows:
        tag = r['name'].replace('ZIF69_', '')
        out[tag] = {'LCD_before': r['before'].get('LCD'), 'LCD_after': r['after'].get('LCD'),
                    'LCD_drop_pct': r.get('LCD_drop_pct'), 'final_EDiff': r.get('final_EDiff'),
                    'converged': r.get('converged')}
    return out


def fmt(s, nd=3):
    return '—' if s is None else f'{s:.{nd}f}'


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--tags', nargs='*', default=DEFAULT_TAGS)
    ap.add_argument('--all', action='store_true', help='relax_v3 의 전 조성')
    ap.add_argument('--probe-data', default=None, help='min_<name>.data 가 있는 디렉터리')
    ap.add_argument('--out', default=os.path.join(HERE, 'audit_probe_noshrink.json'))
    args = ap.parse_args()

    tags = list(args.tags)
    if args.all:
        import glob
        tags = ['base'] + sorted(os.path.basename(p)[6:-12] for p in
                                 glob.glob(os.path.join(HERE, 'relax_v3', 'ZIF69_*_relaxed.cif')))
    if 'base' not in tags:
        tags.insert(0, 'base')

    ctx = risk_context()
    results = {}
    for stage, loader in (('gfnff', lambda t: read(cif_path(t))),
                          ('probe', lambda t: load_probe(args.probe_data, t) if args.probe_data else None)):
        stage_res = {}
        for t in tags:
            try:
                atoms = loader(t)
            except FileNotFoundError:
                atoms = None
            if atoms is None:
                continue
            stage_res[t] = audit(atoms)
        if 'base' not in stage_res:
            if stage == 'probe':
                print('[probe] 탐침 후 기하 없음 — lmp_v3/ 는 정리됐다. 재실행 필요:\n'
                      '        lammps_mof 환경에서 risk_screen_v3.py 를 데이터 보존 옵션으로 다시 돌리고\n'
                      '        --probe-data 로 넘길 것 (RASPA 가 도는 동안 Zeo++ 단계는 같이 띄우지 말 것).')
            else:
                sys.exit('base 이완본이 없어 기준 분포를 만들 수 없음')
            continue
        ref = {k: stats(stage_res['base'][k]) for k in METRICS}
        print(f'\n=== [{stage}] base 기준 분포 (n, mean, sd, min, max) ===')
        for k in METRICS:
            r = ref[k]
            print(f'  {k:11s} n={r["n"]:4d}  mean={fmt(r["mean"])}  sd={fmt(r["sd"], 4)}  '
                  f'[{fmt(r["min"])}, {fmt(r["max"])}]')
        hdr = (f'{"tag":8s} {"ZnN 3σ밖":>9s} {"maxz":>5s} {"NZnN 3σ밖":>10s} {"maxz":>5s} '
               f'{"ring5":>6s} {"ring6":>6s} {"dmin":>6s} {"배위4":>5s} {"LCD전→후":>14s} {"EDiff":>6s}  판정')
        print(f'\n=== [{stage}] 판정 (T-3: 3σ 밖 1개 이상 또는 dmin<{MIN_DIST_LIMIT} → 깨진 구조) ===')
        print(hdr)
        for t in tags:
            m = stage_res.get(t)
            if m is None:
                print(f'{t:8s}  (파일 없음)')
                continue
            j = judge(m, ref)
            m['judge'] = j
            o = j['outliers']
            c = ctx.get(t, {})
            lcd = (f'{c["LCD_before"]:.3f}→{c["LCD_after"]:.3f}'
                   if c.get('LCD_before') is not None and c.get('LCD_after') is not None else '—')
            ed = fmt(c.get('final_EDiff'))
            print(f'{t:8s} {str(o["ZnN"]["n_out"]):>9s} {fmt(o["ZnN"]["max_z"], 1):>5s} '
                  f'{str(o["NZnN"]["n_out"]):>10s} {fmt(o["NZnN"]["max_z"], 1):>5s} '
                  f'{str(o["ring5_rmsd"]["n_out"]):>6s} {str(o["ring6_rmsd"]["n_out"]):>6s} '
                  f'{m["dmin"]:6.3f} {"예" if j["Zn_coord_all4"] else "아니오":>5s} {lcd:>14s} {ed:>6s}  {j["verdict"]}')
            hpairs = {k: v for k, v in m['pair_min'].items() if 'H' in k.split('-')}
            close = sorted(hpairs.items(), key=lambda kv: kv[1])[:4]
            print('          H 쌍 최소거리: ' + ', '.join(f'{k} {v:.3f}' for k, v in close)
                  + f' | ZnN [{min(m["ZnN"]):.3f}, {max(m["ZnN"]):.3f}] NZnN [{min(m["NZnN"]):.1f}, {max(m["NZnN"]):.1f}]'
                  + f' | 고리 RMSD 최대(Å) 5원 {max(m["ring5_rmsd"]):.4f}/{m["n_ring5"]}개'
                  + f' 6원 {max(m["ring6_rmsd"]):.4f}/{m["n_ring6"]}개')
        base_j = stage_res['base']['judge']
        if base_j['n_out_total'] > 0:
            print(f'  ※ base 자신이 자기 분포 3σ 밖 원자 {base_j["n_out_total"]}개 — 규칙의 판별력 주의. '
                  '문턱은 바꾸지 않고 이 사실만 기록한다.')
        results[stage] = {'reference': ref, 'rows': stage_res}

    # JSON: 원자별 목록은 통계로 줄여 저장
    dump = {'criteria': {'nsig': NSIG, 'min_dist_limit': MIN_DIST_LIMIT, 'ZnN_cut': ZN_N_CUT,
                         'metrics': METRICS, 'source': 'DESIGN_STUDY_20260903.md §5-A T-3'},
            'stages': {}}
    for stage, sr in results.items():
        rows = {}
        for t, m in sr['rows'].items():
            rows[t] = {k: stats(m[k]) for k in METRICS}
            rows[t].update({'n_atoms': m['n_atoms'], 'formula': m['formula'],
                            'Zn_coord': dict(m['Zn_coord']), 'dmin': m['dmin'],
                            'pair_min': m['pair_min'], 'judge': m['judge'],
                            'risk_v3': ctx.get(t)})
        dump['stages'][stage] = {'reference': sr['reference'], 'rows': rows}
    json.dump(dump, open(args.out, 'w'), indent=1, ensure_ascii=False)
    print(f'\n저장: {args.out}')


if __name__ == '__main__':
    main()
