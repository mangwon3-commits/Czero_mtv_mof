# -*- coding: utf-8 -*-
"""E-22f — 꼭짓점 E(e22f_hnorm, H 정규화) 물 Widom 4씨앗. 등록 ASSIGN_MAGI5B §HKHOME 10차.
E-22c 러너(run_e22c_water.one · write_input)를 수정 없이 import — 대상·실행 폴더·출력만 바꿈. 워커 4(같은 기기 Widom 4 와 합쳐 8코어)."""
import hashlib, json, os, sys
from concurrent.futures import ProcessPoolExecutor, as_completed
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import run_e22c_water as rw                     # noqa: E402
import ff_gate                                  # noqa: E402
from run_tb2_water_kh import count_sites        # noqa: E402
rw.RUNS = os.path.join(HERE, 'e22f_runs')
OUT = os.path.join(HERE, 'results_e22f_water_hkhome.json')
NAMES = ('e22f_hnorm',); NSEED = 4; WORKERS = 4

if __name__ == '__main__':
    ok, m = ff_gate.md5_gate(verbose=True)
    wm = hashlib.md5(open(rw.WATER_DEF, 'rb').read()).hexdigest()
    if not ok or wm != rw.WATER_MD5 or count_sites(rw.WATER_DEF) != 5:
        print('!! 관문 실패 — 착수 안 함', ok, wm); sys.exit(3)
    for n in NAMES:
        assert os.path.exists(os.path.join(HERE, 'charged_v3', n + '_DDEC6.cif')), n
    os.makedirs(rw.RUNS, exist_ok=True)
    jobs = [(n, k, rw.STAGGER * (i % WORKERS)) for i, (n, k) in enumerate((n, k) for k in range(1, NSEED + 1) for n in NAMES)]
    rows = []
    with ProcessPoolExecutor(max_workers=WORKERS) as ex:
        for fu in as_completed([ex.submit(rw.one, j) for j in jobs]):
            r = fu.result(); rows.append(r); print(r['name'], r['seed_idx'], r['status'], r.get('KH_water'), r.get('minutes'), flush=True)
            json.dump({'test': 'E-22f', 'finished': False, 'ff_md5': m, 'water_def_md5': wm, 'rows': rows}, open(OUT, 'w'), indent=1)
    seeds = [r.get('seed') for r in rows]
    json.dump({'test': 'E-22f', 'finished': True, 'ff_md5': m, 'water_def_md5': wm, 'seed_dup': len(seeds) - len(set(seeds)), 'rows': rows}, open(OUT, 'w'), indent=1)
    print('E-22f 물 완주', flush=True)
