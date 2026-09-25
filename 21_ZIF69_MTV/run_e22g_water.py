# -*- coding: utf-8 -*-
"""E-22g — E-22e 다섯 행 × (coregeom · 이완본) 물 Widom 4씨앗. 등록 ASSIGN_MAGI5B §HKHOME 11차.
E-22c 러너(run_e22c_water.one · write_input)를 수정 없이 import — 대상·실행 폴더·출력만 인자로. LPT(N_super = 원자 × 셀수, 큰 것부터)."""
import argparse, hashlib, json, os, sys
from concurrent.futures import ProcessPoolExecutor, as_completed
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import run_e22c_water as rw                     # noqa: E402
import run_aryl_gcmc as rg                      # noqa: E402
import ff_gate                                  # noqa: E402
from run_tb2_water_kh import count_sites        # noqa: E402
NSEED = 4

if __name__ == '__main__':
    ap = argparse.ArgumentParser(); ap.add_argument('--names', required=True); ap.add_argument('--out', required=True)
    ap.add_argument('--runs', default='e22g_runs'); ap.add_argument('--workers', type=int, default=8)
    a = ap.parse_args(); names = a.names.split(',')
    out = os.path.join(HERE, a.out); rw.RUNS = os.path.join(HERE, a.runs)
    ok, m = ff_gate.md5_gate(verbose=True)
    wm = hashlib.md5(open(rw.WATER_DEF, 'rb').read()).hexdigest()
    if not ok or wm != rw.WATER_MD5 or count_sites(rw.WATER_DEF) != 5:
        print('!! 관문 실패 — 착수 안 함', ok, wm); sys.exit(3)
    nsup = {}
    for n in names:
        c = os.path.join(HERE, 'charged_v3', n + '_DDEC6.cif'); assert os.path.exists(c), c
        at = rg.read(c); uc = rg.unit_cells(at)
        nsup[n] = len(at) * uc[0] * uc[1] * uc[2]
    print('N_super', nsup, flush=True)
    os.makedirs(rw.RUNS, exist_ok=True)
    order = sorted(((n, k) for n in names for k in range(1, NSEED + 1)), key=lambda x: (-nsup[x[0]], x[1]))
    jobs = [(n, k, rw.STAGGER * (i % a.workers) if i < a.workers else 0.0) for i, (n, k) in enumerate(order)]
    rows = []
    meta = {'test': 'E-22g', 'registration': 'ASSIGN_MAGI5B_20260925.md §HKHOME 11차', 'names': names, 'N_super': nsup, 'ff_md5': m, 'water_def_md5': wm}
    with ProcessPoolExecutor(max_workers=a.workers) as ex:
        for fu in as_completed([ex.submit(rw.one, j) for j in jobs]):
            r = fu.result(); rows.append(r); print(r['name'], r['seed_idx'], r['status'], r.get('KH_water'), r.get('minutes'), flush=True)
            json.dump(dict(meta, finished=False, rows=rows), open(out, 'w'), indent=1)
    seeds = [r.get('seed') for r in rows]
    json.dump(dict(meta, finished=True, seed_dup=len(seeds) - len(set(seeds)), rows=rows), open(out, 'w'), indent=1)
    print('E-22g 물 묶음 완주', flush=True)
