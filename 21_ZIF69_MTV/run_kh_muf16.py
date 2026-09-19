"""T-NF-1w (a) — MUF-16 물 K_H (Widom, 298 K), 반복 3. 등록: `TNF_REGISTRATION_20260910.md §9` (자료 0건).

`run_kh_ext.py`(T-NF-0k) 를 import 해 대상·경로·출력 이름만 바꿉니다 — 자(CYCLES·INIT·컷오프·힘장·온도)는
32조성 축·외부 셋과 **같아야** 같은 표에 놓이므로 손대지 않습니다. UnitCells 는 `run_tb2_water_kh.unit_cells`
가 셀에서 정합니다(1×3×1 이완 셀 15.3/13.3/25.5 Å → 2 2 1, T-NF-1 과 같은 상자).

사용:  KHX_WORKERS=3 KHX_NREP=3 nice -n 5 ~/miniconda3/envs/czeromof/bin/python run_kh_muf16.py
"""
import json
import os
import socket
import sys
from multiprocessing import Pool

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import run_kh_ext as K                                          # noqa: E402

NAME = 'muf16'
K.FRAMEWORKS = [NAME]
K.N_REP = int(os.environ.get('KHX_NREP', 3))
K.T.WORKERS = int(os.environ.get('KHX_WORKERS', 3))
# (T-NF-1w-2, 09-19 23:1x) 온도를 환경변수로 — 기본 298 K(T-NF-1w (a) 와 같은 파일 이름·폴더). 다른 온도면 폴더·출력 이름에 온도를 붙여 298 K 판을 덮지 않는다.
K.T.TEMP = float(os.environ.get('KHX_TEMP', 298.0))
_sfx = '' if abs(K.T.TEMP - 298.0) < 1e-6 else f'_{int(round(K.T.TEMP))}K'
K.RUNS_ROOT = os.path.join(HERE, f'tnf1w_khw_runs{_sfx}')      # 기존 khext_runs 와 분리 (CLAUDE.md §3)
OUT = os.path.join(HERE, f'tnf_widom_water_muf16{_sfx}.json')   # postman 패턴 tnf_widom_*.json


def main():
    ok, _ = K.md5_gate()
    if not ok:
        print('!! 힘장 파일 관문 실패. 중단.', flush=True)
        return 2
    cif = os.path.join(K.T.CHARGED, NAME + '_DDEC6.cif')
    if not os.path.exists(cif):
        print(f'!! CIF 없음: {cif}', flush=True)
        return 3
    jobs = [(i, NAME, rep) for i, rep in enumerate(range(1, K.N_REP + 1))]
    print(f'T-NF-1w (a) MUF-16 물 K_H — 반복 {K.N_REP}, 워커 {K.T.WORKERS}, {K.STAGGER}초 어긋내기', flush=True)
    print(f'  자(32조성 축과 동일): NumberOfCycles {K.T.CYCLES} / NumberOfInitializationCycles {K.T.INIT}, '
          f'UFF_MOF, 컷오프 {K.T.CUTOFF}, {K.T.TEMP} K, Ewald 1e-6', flush=True)
    rows = []
    with Pool(K.T.WORKERS) as p:
        for r in p.imap_unordered(K.one, jobs, chunksize=1):
            rows.append(r)
            print(f"  [{'ok' if r['ok'] else '실패'}] {r['name']} r{r['rep']}  K_H {r['KH_water']} ± {r['KH_water_err']}  "
                  f"셀 {r.get('unit_cells')}  씨앗 {r.get('raspa_seed')}", flush=True)
    seeds = [r['raspa_seed'] for r in rows]
    collide = seeds if len(set(seeds)) != len(seeds) else None
    json.dump({'test': 'T-NF-1w (a)', 'registration': 'TNF_REGISTRATION_20260910.md §9',
               'tag': NAME, 'host': socket.gethostname().lower(),
               'forcefield': K.FF_TAG, 'ff_md5': K.T.FF_MD5, 'ff_path': K.T.FF_PATH,
               'NumberOfInitializationCycles': K.T.INIT, 'NumberOfCycles': K.T.CYCLES,
               'temperature_K': K.T.TEMP, 'cutoff_A': K.T.CUTOFF, 'pressure_Pa': K.T.PRESS,
               'comparison_axis': ['v3w_water_kh_ext/water_kh_extfw_*.json (T-NF-0k)',
                                   'v3w_water_kh/water_kh_ALLw_hkhome_seedfixed.json (32조성)'],
               'note': '무한희석 물 K_H, 32조성 축·외부 셋과 같은 자. 등록 §0 슈퍼셀 예외 계열 — 순위 표에 나란히 놓되 "다른 복제" 를 병기.',
               'seed_collision': collide,
               'rows': sorted(rows, key=lambda x: x['rep'])},
              open(OUT, 'w'), ensure_ascii=False, indent=2)
    nok = sum(1 for r in rows if r['ok'])
    print(f"\n[OK] {nok}/{len(jobs)} -> {OUT}", flush=True)
    if collide:
        print(f"  ⚠️ **씨앗 충돌** {collide} — 반복은 독립이 아닙니다.", flush=True)
    return 0 if nok == len(jobs) else 1


if __name__ == '__main__':
    sys.exit(main())
