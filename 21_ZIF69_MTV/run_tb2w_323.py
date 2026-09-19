"""T-B2w-323 — 32조성 물 K_H (Widom) **323 K**, 각 1회. 등록: `TB2W_323_REGISTRATION_20260919.md` (자료 0건).

`run_tb2_water_kh.py`(T-B2w, 298 K) 를 import 해 온도·경로·출력 이름만 바꿉니다 — 자(CYCLES 15,000 / INIT 3,000 ·
12 Å · UFF_MOF · Ewald 1e-6)는 298 K 판과 **같아야** 비가 섭니다. 씨앗 = 폴더 생성 시각(초)이므로 작업마다 3 s 어긋내고
출력 머리말에서 회수해 대조합니다(T-B2w seedfix 교훈).

사용:  TB2W323_WORKERS=8 nice -n 5 ~/miniconda3/envs/czeromof/bin/python run_tb2w_323.py
"""
import json
import os
import re
import socket
import sys
import time
from multiprocessing import Pool

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import run_tb2_water_kh as T                                    # noqa: E402
from ff_gate import md5_gate, read_ff_header, FF_TAG            # noqa: E402

TEMP = 323.0
T.TEMP = TEMP
T.RUNS = os.path.join(HERE, 'tb2w323_runs')                     # 298 K 의 tb2w_runs 와 분리 (CLAUDE.md §3)
T.WORKERS = int(os.environ.get('TB2W323_WORKERS', 8))
OUT_DIR = os.path.join(HERE, 'v3w_water_kh')                    # postman 패턴 v3w_water*/*.json
STAGGER = 3


def read_seed(name):
    d = os.path.join(T.RUNS, 'widom_water_' + name, 'Output', 'System_0')
    if not os.path.isdir(d):
        return None
    for fn in sorted(x for x in os.listdir(d) if x.endswith('.data')):
        for ln in open(os.path.join(d, fn), encoding='utf-8', errors='ignore'):
            m = re.match(r'\s*Random number seed:\s*(\d+)', ln)
            if m:
                return int(m.group(1))
            if ln.startswith('Number of cycles'):
                break
    return None


def one(arg):
    i, name = arg
    time.sleep(i * STAGGER)
    os.makedirs(T.RUNS, exist_ok=True)
    r = T.run_one(name)
    r['raspa_seed'] = read_seed(name)
    r['temperature_K'] = TEMP
    r['forcefield'] = FF_TAG
    r['ff_check'] = read_ff_header(os.path.join(T.RUNS, 'widom_water_' + name))
    if not r['ff_check']['ok']:
        r['ok'] = False
        r['WARN_ff_check'] = '머리말 관문 실패 — 이 행의 K 값을 쓰지 마십시오'
    return r


def main():
    ok, _ = md5_gate()
    if not ok:
        print('!! 힘장 파일 관문 실패. 중단.', flush=True)
        return 2
    nsite = sum(1 for ln in open(T.WATER_DEF, encoding='utf-8')
                if len(ln.split()) > 4 and ln.split()[1] in ('Ow', 'Hw', 'Lw'))
    if nsite != 5:
        print('!! 5자리 물이 아닙니다. 중단.', flush=True)
        return 1
    names = sorted(json.load(open(os.path.join(HERE, 'tb2_targets.json')))['names'])
    missing = [n for n in names if not os.path.exists(os.path.join(T.CHARGED, n + '_DDEC6.cif'))]
    if missing:
        print(f'!! CIF 없음: {missing}', flush=True)
        return 3
    if os.environ.get('DRY') == '1':
        print(f'DRY: {len(names)}종, {TEMP} K, RUNS {T.RUNS}, 워커 {T.WORKERS}, 자 {T.CYCLES}/{T.INIT}/{T.CUTOFF}', flush=True)
        return 0
    os.makedirs(OUT_DIR, exist_ok=True)
    print(f'T-B2w-323 물 K_H (Widom) — {len(names)}종 × 1, {TEMP} K, 워커 {T.WORKERS}, {STAGGER}초 어긋내기', flush=True)
    print(f'  자(298 K 판과 동일): NumberOfCycles {T.CYCLES} / NumberOfInitializationCycles {T.INIT}, UFF_MOF, 컷오프 {T.CUTOFF}, Ewald 1e-6', flush=True)
    rows = []
    with Pool(T.WORKERS) as p:
        for r in p.imap_unordered(one, list(enumerate(names)), chunksize=1):
            rows.append(r)
            print(f"  [{'ok' if r['ok'] else '실패'}] {r['name']:12s} K_H {r['KH_water']}  ± {r['KH_water_err']}  씨앗 {r.get('raspa_seed')}", flush=True)
    seeds = [r.get('raspa_seed') for r in rows]
    dup = sorted({s for s in seeds if s is not None and seeds.count(s) > 1})
    tag = socket.gethostname().lower()
    f = os.path.join(OUT_DIR, f'water_kh_323_ALL_{tag}.json')
    json.dump({'test': 'T-B2w-323', 'registration': 'TB2W_323_REGISTRATION_20260919.md', 'tag': tag,
               'temperature_K': TEMP, 'forcefield': FF_TAG, 'ff_md5': T.FF_MD5, 'ff_path': T.FF_PATH,
               'NumberOfInitializationCycles': T.INIT, 'NumberOfCycles': T.CYCLES, 'cutoff_A': T.CUTOFF,
               'comparison_axis': 'v3w_water_kh/water_kh_ALLw_hkhome_seedfixed.json (298 K, 같은 자)',
               'seed_duplicates': dup or None,
               'note': '323 K 물 K_H. 298 K 판과 같은 자. 비 K_H(298)/K_H(323) 은 등록 §3.',
               'rows': sorted(rows, key=lambda x: x['name'])}, open(f, 'w'), ensure_ascii=False, indent=2)
    nok = sum(1 for r in rows if r['ok'])
    print(f"\n[OK] {nok}/{len(names)} -> {f}" + (f"  ⚠️ 씨앗 중복 {dup}" if dup else "  씨앗 전부 다름"), flush=True)
    return 0 if nok == len(names) else 1


if __name__ == '__main__':
    sys.exit(main())
