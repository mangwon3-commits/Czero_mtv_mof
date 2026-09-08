"""T-B2 물 K_H — **수정 힘장 계열(v3w)** 러너 래퍼. WATER_FIX_20260906 §3 ②.

run_tb2_water_kh.py 의 run_one 을 그대로 쓰되 경로만 새 계열로 바꾼다(CLAUDE.md §3: 옛 tb2_runs 를 이어받지 않는다).
대상 = tb2_targets.json 의 32종 + 확장 7종(run_tb2_ext.EXT, ②-전용). 대조 4건은 재실행하지 않는다.
행마다 forcefield/ff_check 를 찍는다(출력 머리말의 Hw-Hw 쌍을 정규식으로 — 오른쪽 정렬 주의, 22.14170 grep 금지).
사용: TB2_WORKERS=6 nice -n 10 python run_tb2w.py
"""
import glob, json, os, re, socket, sys
from multiprocessing import Pool
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import run_tb2_water_kh as T          # noqa: E402
import run_tb2_ext as X               # noqa: E402

T.RUNS = os.path.join(HERE, 'tb2w_runs')
T.OUT = os.path.join(HERE, 'v3w_water_kh')
FF_TAG = 'UFF_MOF+HwLw_none_20260906'
PAIR = re.compile(r'^\s*(\w+)\s+-\s+(\w+)\s+\[(\w+)\](?:\s+p_0/k_B:?\s+([0-9.]+))?')   # 09-06 18:3x: 실제 머리말은 'p_0/k_B:  89.63300 [K]' (콜론) — 첫 판이 콜론을 빼먹어 Ow-Ow 를 못 읽고 39건을 '실패' 로 찍음

def ff_check(name):
    """출력 머리말에서 물 쌍 4종이 ZERO_POTENTIAL 이고 Ow-Ow 가 89.633 인지."""
    res = {'HwHw': None, 'OwHw': None, 'OwOw_eps': None}
    for f in glob.glob(os.path.join(T.RUNS, f'widom_water_{name}', 'Output', 'System_0', '*.data')):
        for ln in open(f, errors='replace'):
            m = PAIR.match(ln)
            if not m:
                continue
            a, b, kind, eps = m.groups()
            pair = ''.join(sorted((a, b)))
            if pair == 'HwHw': res['HwHw'] = kind
            elif pair == 'HwOw': res['OwHw'] = kind
            elif pair == 'OwOw' and eps: res['OwOw_eps'] = float(eps)
            if all(v is not None for v in res.values()):
                break
        break
    res['ok'] = (res['HwHw'] == 'ZERO_POTENTIAL' and res['OwHw'] == 'ZERO_POTENTIAL'
                 and res['OwOw_eps'] is not None and abs(res['OwOw_eps'] - 89.633) < 1e-3)
    return res

def main():
    names = sorted(json.load(open(os.path.join(HERE, 'tb2_targets.json')))['names'])
    sel = names + [n for n in X.EXT if n not in names]
    tag = socket.gethostname().lower()
    os.makedirs(T.OUT, exist_ok=True); os.makedirs(T.RUNS, exist_ok=True)
    nsite = sum(1 for ln in open(T.WATER_DEF, encoding='utf-8')
                if len(ln.split()) > 4 and ln.split()[1] in ('Ow', 'Hw', 'Lw'))
    if nsite != 5:
        print('!! 5자리 물이 아닙니다. 중단.', flush=True); return 1
    print(f'T-B2w 물 K_H (수정 힘장) — {len(sel)}종, 워커 {T.WORKERS}, RUNS {T.RUNS}, OUT {T.OUT}', flush=True)
    rows = []
    with Pool(T.WORKERS) as p:
        for r in p.imap_unordered(T.run_one, sel, chunksize=1):
            r['forcefield'] = FF_TAG
            r['ff_check'] = ff_check(r['name'])
            if not r['ff_check']['ok']:
                r['ok'] = False
                r['WARN_ff_check'] = '출력 머리말에서 물 쌍 ZERO_POTENTIAL / Ow-Ow 89.633 확인 실패'
            rows.append(r)
            print(f"  [{'ok' if r['ok'] else '실패'}] {r['name']:12s} K_H {r['KH_water']}  ff {r['ff_check']}", flush=True)
    f = os.path.join(T.OUT, f'water_kh_ALLw_{tag}.json')
    json.dump({'half': 'ALL+EXT', 'tag': tag, 'forcefield': FF_TAG,
               'NumberOfInitializationCycles': T.INIT, 'NumberOfCycles': T.CYCLES,
               'note': 'WATER_FIX_20260906 §3 ②. 수정 힘장(Hw none/Lw none). 대조 4건 미포함. 문턱 5e-6 은 TIP4P 기준 한정어 필수',
               'rows': sorted(rows, key=lambda x: x['name'])}, open(f, 'w'), ensure_ascii=False, indent=2)
    print(f"\n[OK] {sum(1 for r in rows if r['ok'])}/{len(sel)} -> {f}", flush=True)
    return 0

if __name__ == '__main__':
    sys.exit(main())
