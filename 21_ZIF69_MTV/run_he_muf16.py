"""T-NF-1w (b) — MUF-16 헬륨 Widom 공극률, 반복 2. 등록: `TNF_REGISTRATION_20260910.md §9` (자료 0건).

`run_helium_void.py`(T-NF-0v) 를 import 해 대상·경로·출력 이름만 바꿉니다. LJ 는 UFF_MOF 의 He 10.9/2.64
(`molecules/TraPPE/helium.def` 는 기하만 — "TraPPE 헬륨" 이라 쓰면 틀립니다). 출력의 `He - He` 쌍을 읽어 확인합니다.

사용:  HEV_WORKERS=2 HEV_NREP=2 nice -n 5 ~/miniconda3/envs/czeromof/bin/python run_he_muf16.py
"""
import json
import os
import socket
import sys
from multiprocessing import Pool

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import run_helium_void as H                                     # noqa: E402
from ff_gate import md5_gate                                    # noqa: E402

NAME = 'muf16'
H.N_REP = int(os.environ.get('HEV_NREP', 2))
H.RUNS_ROOT = os.path.join(HERE, 'tnf1w_hev_runs')
H.WORKERS = int(os.environ.get('HEV_WORKERS', 2))
OUT = os.path.join(HERE, 'tnf_widom_he_muf16.json')             # postman 패턴 tnf_widom_*.json


def main():
    ok, _ = md5_gate()
    if not ok:
        print('!! 힘장 파일 관문 실패. 중단.', flush=True)
        return 2
    cif = os.path.join(H.T.CHARGED, NAME + '_DDEC6.cif')
    if not os.path.exists(cif):
        print(f'!! CIF 없음: {cif}', flush=True)
        return 3
    jobs = [(i, NAME, rep) for i, rep in enumerate(range(1, H.N_REP + 1))]
    print(f'T-NF-1w (b) MUF-16 헬륨 공극률 — 반복 {H.N_REP}, 워커 {H.WORKERS}', flush=True)
    rows = []
    with Pool(H.WORKERS) as p:
        for r in p.imap_unordered(H.one, jobs, chunksize=1):
            rows.append(r)
            print(f"  [{'ok' if r['ok'] else '실패'}] {r['name']} r{r['rep']}  phi {r.get('phi')} ± {r.get('phi_err')}  "
                  f"rho {r.get('density_g_cm3')}  셀 {r.get('unit_cells')}  He쌍 {r.get('he_pair', {}).get('ok')}  씨앗 {r.get('raspa_seed')}",
                  flush=True)
    seeds = [r.get('raspa_seed') for r in rows]
    collide = seeds if len(set(seeds)) != len(seeds) else None
    json.dump({'test': 'T-NF-1w (b)', 'registration': 'TNF_REGISTRATION_20260910.md §9',
               'tag': NAME, 'host': socket.gethostname().lower(),
               'he_lj': {'eps_K': H.HE_EPS, 'sigma_A': H.HE_SIG, 'source': 'UFF_MOF force_field_mixing_rules.def (helium.def 는 기하만)'},
               'NumberOfInitializationCycles': H.T.INIT, 'NumberOfCycles': H.T.CYCLES,
               'temperature_K': H.T.TEMP, 'cutoff_A': H.T.CUTOFF,
               'comparison_axis': 'v3w_helium_void/*.json (T-NF-0v, 외부 3 + 우리 6)',
               'note': 'K_H^vol = K_H × rho / phi 정규화용. 판정 없음(기록).',
               'seed_collision': collide,
               'rows': sorted(rows, key=lambda x: x['rep'])},
              open(OUT, 'w'), ensure_ascii=False, indent=2)
    nok = sum(1 for r in rows if r['ok'])
    print(f"\n[OK] {nok}/{len(jobs)} -> {OUT}", flush=True)
    return 0 if nok == len(jobs) else 1


if __name__ == '__main__':
    sys.exit(main())
