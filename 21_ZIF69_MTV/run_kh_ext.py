"""T-NF-0k — **외부 골격(ZIF-71 · 90 · 93) 물 K_H (Widom)**, 골격당 3회.

등록: `TNF0K_REGISTRATION_20260911.md` (2026-09-11 03:46, **자료 0건에서 작성**).

무엇을 가르나 — 등온선 축에서는 **원리적으로** 못 가르는 두 갈래:
    A  골격–물 **교차항 자체**가 약하다        (무한희석에서 이미 분리 실패)
    B  교차항은 순위를 맞추고 **물–물 협동성**이 부족하다  (무한희석은 맞음)
K_H 는 정의상 물 **한 분자**와 골격만 봅니다. 물–물 항이 안 들어갑니다.

**러너를 안 고칩니다.** `run_tb2_water_kh.py` 를 import 해 대상·경로만 바꿉니다
(`run_tb2w_seedfix.py` 와 같은 방식). 자는 32조성 축과 **같아야** 하므로
CYCLES·INIT·컷오프·힘장을 **건드리지 않습니다** — 그래야 같은 표에 놓입니다.

⚠️ **씨앗**: 이 빌드는 `RandomSeed` 를 안 받고 씨앗 = **폴더 생성 시각(초)** 입니다
(`RASPA_SEED_20260828.md`). 09-07 에 데스크탑이 같은 초에 뜬 6행에서 씨앗을 나눠 썼습니다.
**같은 골격의 반복이 같은 씨앗을 받으면 n=3 이 n=1 입니다** — 반복 산포를 재려는 이 판에서는
그게 곧 자를 0으로 만듭니다. 그래서 **작업마다 어긋내 띄우고 씨앗을 회수해 대조**합니다.

반복은 **폴더로** 가릅니다(`khext_runs/r1/…`). CIF 를 복제하지 않습니다 —
사본을 만들면 `charged_v3/` 에 같은 구조가 여러 이름으로 남아 나중에 대상 목록을 오염시킵니다.

사용:  KHX_WORKERS=6 nice -n 5 ~/miniconda3/envs/czeromof/bin/python run_kh_ext.py
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

# LPT — 비싼 것부터(`CLAUDE.md §5`). 2x2x2 원자 수: 93 > 71 > 90
FRAMEWORKS = ['zif93', 'zif71', 'zif90']
N_REP = int(os.environ.get('KHX_NREP', 3))
RUNS_ROOT = os.path.join(HERE, 'khext_runs')       # 기존 tb2w_runs 와 분리 (CLAUDE.md §3)
OUT = os.path.join(HERE, 'v3w_water_kh_ext')
STAGGER = 3                                        # 초. 같은 초 = 같은 씨앗
T.WORKERS = int(os.environ.get('KHX_WORKERS', 6))


def runs_dir(rep):
    return os.path.join(RUNS_ROOT, f'r{rep}')


def read_seed(name, rep):
    """출력 머리말 `Random number seed:` — `run_tb2w_seedfix.read_seed` 와 같은 정규식."""
    d = os.path.join(runs_dir(rep), 'widom_water_' + name, 'Output', 'System_0')
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
    i, name, rep = arg
    time.sleep(i * STAGGER)              # 씨앗이 착수 시각이므로 어긋냅니다
    T.RUNS = runs_dir(rep)               # 워커는 fork 사본이라 프로세스별로 안전합니다
    os.makedirs(T.RUNS, exist_ok=True)
    r = T.run_one(name)
    r['rep'] = rep
    r['raspa_seed'] = read_seed(name, rep)
    r['forcefield'] = FF_TAG
    r['ff_check'] = read_ff_header(os.path.join(T.RUNS, 'widom_water_' + name))
    if not r['ff_check']['ok']:
        r['ok'] = False
        r['WARN_ff_check'] = '머리말 관문 실패 — 이 행의 K 값을 쓰지 마십시오'
    return r


def main():
    ok, _ = md5_gate()                                  # 파일 관문
    if not ok:
        print('!! 힘장 파일 관문 실패. 중단.', flush=True)
        return 2
    nsite = sum(1 for ln in open(T.WATER_DEF, encoding='utf-8')
                if len(ln.split()) > 4 and ln.split()[1] in ('Ow', 'Hw', 'Lw'))
    print(f'  물 정의 사이트 {nsite}개 (TIP5P-Ew 는 5)', flush=True)
    if nsite != 5:
        print('!! 5자리 물이 아닙니다. 중단.', flush=True)
        return 1
    for n in FRAMEWORKS:                                # 재료 관문 — 없으면 착수 안 함
        p = os.path.join(T.CHARGED, n + '_DDEC6.cif')
        if not os.path.exists(p):
            print(f'!! CIF 없음: {p}', flush=True)
            return 3
    os.makedirs(OUT, exist_ok=True)
    jobs = [(i, n, rep) for i, (n, rep) in
            enumerate((n, rep) for n in FRAMEWORKS for rep in range(1, N_REP + 1))]
    print(f'T-NF-0k 외부 골격 물 K_H — 골격 {len(FRAMEWORKS)} x 반복 {N_REP} = {len(jobs)}건, '
          f'워커 {T.WORKERS}, {STAGGER}초 어긋내기', flush=True)
    print(f'  자(32조성 축과 동일): NumberOfCycles {T.CYCLES} / '
          f'NumberOfInitializationCycles {T.INIT}, UFF_MOF, 컷오프 {T.CUTOFF}, '
          f'{T.TEMP} K, Ewald 1e-6', flush=True)
    print(f'  RUNS {RUNS_ROOT}/r*\n  OUT  {OUT}', flush=True)
    rows = []
    with Pool(T.WORKERS) as p:
        for r in p.imap_unordered(one, jobs, chunksize=1):
            rows.append(r)
            print(f"  [{'ok' if r['ok'] else '실패'}] {r['name']:8s} r{r['rep']}  "
                  f"K_H {r['KH_water']}  ± {r['KH_water_err']}  씨앗 {r.get('raspa_seed')}",
                  flush=True)

    # 씨앗 대조 — **골격 안에서** 겹치면 그 골격의 반복은 독립이 아닙니다.
    collide = {}
    for n in FRAMEWORKS:
        sd = [r['raspa_seed'] for r in rows if r['name'] == n]
        if len(set(sd)) != len(sd):
            collide[n] = sd
    f = os.path.join(OUT, f'water_kh_extfw_{socket.gethostname().lower()}.json')
    json.dump({'test': 'T-NF-0k', 'registration': 'TNF0K_REGISTRATION_20260911.md',
               'tag': socket.gethostname().lower(),
               'forcefield': FF_TAG, 'ff_md5': T.FF_MD5, 'ff_path': T.FF_PATH,
               'NumberOfInitializationCycles': T.INIT, 'NumberOfCycles': T.CYCLES,
               'temperature_K': T.TEMP, 'cutoff_A': T.CUTOFF, 'pressure_Pa': T.PRESS,
               'comparison_axis': 'v3w_water_kh/water_kh_ALLw_hkhome_seedfixed.json',
               'note': ('외부 골격 무한희석 물 K_H. 32조성 축과 **같은 자**. '
                        '판정 규칙은 등록문 §6 (R>=10 갈래B / R<3 갈래A / 그 사이 미결). '
                        '단일 링커 정렬 구조라 배치 단위는 해당 없음 — 자는 ± 1.5배.'),
               'seed_collision': collide or None,
               'rows': sorted(rows, key=lambda x: (x['name'], x['rep']))},
              open(f, 'w'), ensure_ascii=False, indent=2)
    nok = sum(1 for r in rows if r['ok'])
    print(f"\n[OK] {nok}/{len(jobs)} -> {f}", flush=True)
    if collide:
        print(f"  ⚠️ **씨앗 충돌** {collide} — 그 골격의 반복은 독립이 아닙니다. "
              f"산포를 인용하지 마십시오.", flush=True)
    else:
        print('  씨앗: 골격 안에서 전부 다름 — 반복은 독립입니다.', flush=True)
    return 0 if nok == len(jobs) else 1


if __name__ == '__main__':
    sys.exit(main())
