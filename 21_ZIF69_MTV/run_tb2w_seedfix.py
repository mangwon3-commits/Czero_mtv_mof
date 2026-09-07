"""T-B2w **씨앗 충돌 4건**만 다시 돕니다 (2026-09-07, `ASSIGN_20260907.md`).

무엇이 문제였나 — 39행 중 **여섯 행이 씨앗 둘을 나눠 씁니다.**

    1788683950  brbIm025 · brbIm050 · brbIm100
    1788683951  base     · brbIm075 · cf3Im025

RASPA 는 씨앗을 **착수 시각(초)** 으로 정합니다(`SEED_TWO_MEANINGS_20260905.md`).
워커 6으로 한꺼번에 띄우면 같은 초에 시작한 것들이 **같은 씨앗 = 같은 난수열**을
받습니다. 값이 틀린 것은 아니지만 **서로 독립이 아니므로**, 이 여섯을 분산·재현성
논거에 쓰면 표본 수를 실제보다 많게 셉니다.

**하는 일**: 각 씨앗 무리에서 **뒤의 둘씩, 모두 넷**(brbIm050 · brbIm100 ·
brbIm075 · cf3Im025)을 **새 계열에서** 다시 돕니다. 무리마다 하나(brbIm025 · base)는
그대로 두므로 39행의 조성 구성은 변하지 않습니다.

**새 시험이 아닙니다.** 같은 조성·같은 설정·같은 힘장의 재실행이고 문턱을 새로
걸지 않습니다. 원본 JSON 은 **건드리지 않습니다** — 결과는 새 파일로 나오고, 병합은
사람이 봅니다.

    RUNS  tb2w_runs_seedfix/     OUT  v3w_water_kh_seedfix/
    워커 2, **작업마다 5초씩 어긋내 띄웁니다** — 같은 초 = 같은 씨앗이므로,
    고치러 와서 같은 충돌을 다시 만들면 안 됩니다

사용: TB2_WORKERS=2 nice -n 10 python run_tb2w_seedfix.py
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
import run_tb2_water_kh as T          # noqa: E402
from ff_gate import md5_gate, read_ff_header, FF_TAG   # noqa: E402

NAMES = ['brbIm050', 'brbIm100', 'brbIm075', 'cf3Im025']
T.RUNS = os.path.join(HERE, 'tb2w_runs_seedfix')
T.OUT = os.path.join(HERE, 'v3w_water_kh_seedfix')
STAGGER = 5                                    # 초. 같은 초에 두 개가 시작하지 않도록


def read_seed(name):
    """출력 머리말의 `Random number seed:` — `run_water_v3w.read_seed` 와 같은 정규식.
    (그쪽은 물 계열의 폴더 이름을 쓰므로 여기서 경로만 바꿔 부릅니다.)"""
    d = os.path.join(T.RUNS, 'widom_water_' + name, 'Output', 'System_0')
    if not os.path.isdir(d):
        return None
    for fn in sorted(x for x in os.listdir(d) if x.endswith('.data')):
        with open(os.path.join(d, fn), encoding='utf-8', errors='ignore') as f:
            for ln in f:
                m = re.match(r'\s*Random number seed:\s*(\d+)', ln)
                if m:
                    return int(m.group(1))
                if ln.startswith('Number of cycles'):
                    break
    return None


def one(arg):
    i, name = arg
    time.sleep(i * STAGGER)                    # 씨앗이 착수 시각이므로 어긋냅니다
    r = T.run_one(name)
    r['raspa_seed'] = read_seed(name)          # 폴더가 살아 있는 지금 찍습니다
    r['forcefield'] = FF_TAG
    r['ff_check'] = read_ff_header(os.path.join(T.RUNS, 'widom_water_' + name))
    if not r['ff_check']['ok']:
        r['ok'] = False
        r['WARN_ff_check'] = '머리말 관문 실패 — 이 행의 K 값을 쓰지 마십시오'
    return r


def main():
    ok, _ = md5_gate()                          # 파일 관문 (FF_GATES_20260907.md §1)
    if not ok:
        print('!! 힘장 파일 관문 실패. 중단.', flush=True)
        return 2
    nsite = sum(1 for ln in open(T.WATER_DEF, encoding='utf-8')
                if len(ln.split()) > 4 and ln.split()[1] in ('Ow', 'Hw', 'Lw'))
    if nsite != 5:
        print('!! 5자리 물이 아닙니다. 중단.', flush=True)
        return 1
    os.makedirs(T.OUT, exist_ok=True)
    os.makedirs(T.RUNS, exist_ok=True)
    print(f'T-B2w 씨앗 충돌 재실행 — {len(NAMES)}종, 워커 {T.WORKERS}, '
          f'{STAGGER}초 어긋내기\n  RUNS {T.RUNS}\n  OUT  {T.OUT}', flush=True)
    rows = []
    with Pool(T.WORKERS) as p:
        for r in p.imap_unordered(one, list(enumerate(NAMES)), chunksize=1):
            rows.append(r)
            print(f"  [{'ok' if r['ok'] else '실패'}] {r['name']:12s} "
                  f"K_H {r['KH_water']}  씨앗 {r.get('raspa_seed')}", flush=True)
    f = os.path.join(T.OUT, f'water_kh_seedfix_{socket.gethostname().lower()}.json')
    json.dump({'tag': 'seedfix', 'forcefield': FF_TAG,
               'NumberOfInitializationCycles': T.INIT, 'NumberOfCycles': T.CYCLES,
               'note': ('ASSIGN_20260907.md — 씨앗 충돌 4건 재실행. 원본 '
                        'water_kh_ALLw_hkhome.json 은 건드리지 않았습니다. '
                        '병합은 사람이 봅니다. 새 문턱 없음.'),
               'replaces_seeds': {'brbIm050': 1788683950, 'brbIm100': 1788683950,
                                  'brbIm075': 1788683951, 'cf3Im025': 1788683951},
               'rows': sorted(rows, key=lambda x: x['name'])},
              open(f, 'w'), ensure_ascii=False, indent=2)
    seeds = [r.get('raspa_seed') for r in rows]
    print(f"\n[OK] {sum(1 for r in rows if r['ok'])}/{len(NAMES)} -> {f}"
          f"\n  새 씨앗 {seeds}  (서로 달라야 합니다: "
          f"{'**예**' if len(set(seeds)) == len(seeds) else '**아니오 — 다시**'})",
          flush=True)
    return 0


if __name__ == '__main__':
    sys.exit(main())
