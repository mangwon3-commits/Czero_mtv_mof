# -*- coding: utf-8 -*-
"""COREPOP-H323 — 다음 묶음의 Zeo++ 막음을 앞 묶음의 GCMC 가 도는 동안 돌리는 판(랩탑 · 사용자 결정 2026-11-16 01:1x "바로 시작해").
`corepop_blocks_keys_overlap.py`(e80fb0cd)와 같은 일을 하고 `corepop_blocks.py`(c00cd11a)를 **무수정 import** 합니다. 그 판과 다른 것은 셋입니다:
  ① 같이 돌아도 되는 simulate 수(env COREPOP_ZEO_ALLOW_SIM · 필수 · 정수)를 0 ~ 16 까지 받습니다(그 판은 0 ~ 2). 넘으면 원판과 똑같이 멈춥니다.
  ② 호출 순서를 단위셀 부피가 작은 구조부터로 바꿉니다. GCMC 가 메모리를 쓰는 동안에는 큰 구조가 가드에 걸리므로, 작은 구조를 먼저 끝내고
     큰 구조는 GCMC 작업이 줄어든 뒤에 시도하게 하려는 것입니다. 호출은 서로 독립이라 순서는 값에 닿지 않습니다. 결과 파일의 rows 도 그 순서입니다.
  ③ 끝의 직렬 재시도(원판: 실패한 호출을 한 번에 하나로 한 번 더)는 simulate 가 0 이 될 때까지 기다린 뒤에 합니다. GCMC 와 메모리를 나눠 써서
     가드에 걸린 호출을 "이 기기에서 안 되는 구조" 로 적지 않으려는 것입니다. 재시도는 빈 기기에서 도므로 그 실패는 원판의 실패와 같은 뜻입니다.
측정 · 파싱 · 메모리 가드(새 호출은 MemAvailable ≥ 8,000 MB · 호출 중 < 5,000 MB 면 kill) · 실패 표지 · 결과 이름은 그대로입니다.
실제 simulate 수는 호출마다 pre_counts 의 'simulate_overlap' 에 남기고, 첫 시도에서 실패한 호출은 결과 파일 머리 'overlap.first_pass_failed' 에 남깁니다.
사용: COREPOP_MACHINE=laptop COREPOP_KEYS_FILE=<키 파일> COREPOP_ZEO_PAR=1 COREPOP_ZEO_ALLOW_SIM=16 python corepop_blocks_keys_overlap2.py   (COREPOP_ZEO_DRY=1 이면 입력 대조 · 계획만)
"""
import hashlib
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
WANT = 'c00cd11a'
KF = os.environ.get('COREPOP_KEYS_FILE', '')
if not KF:
    raise SystemExit('!! COREPOP_KEYS_FILE 를 주세요')
try:
    ALLOW = int(os.environ['COREPOP_ZEO_ALLOW_SIM'])
except (KeyError, ValueError):
    raise SystemExit('!! COREPOP_ZEO_ALLOW_SIM(정수)을 주세요 — 같이 돌아도 되는 simulate 수')
if ALLOW < 0 or ALLOW > 16:
    raise SystemExit(f'!! COREPOP_ZEO_ALLOW_SIM {ALLOW} — 0 ~ 16 만 받습니다')
KJ = json.load(open(KF if os.path.isabs(KF) else os.path.join(HERE, KF), encoding='utf-8'))
SUB = KJ['keys']
TG = {r['key']: r for r in json.load(open(os.path.join(HERE, 'corepop_humid323_targets.json'), encoding='utf-8'))['rows']}
if not SUB or len(set(SUB)) != len(SUB) or any(k not in TG for k in SUB):
    raise SystemExit(f'!! 키 파일이 비었거나 중복 · 대상 목록 밖: {[k for k in SUB if k not in TG][:5]}')
BATS = sorted({TG[k]['batch'] for k in SUB})
os.environ['COREPOP_BATCHES'] = ','.join(BATS)
m = hashlib.md5(open(os.path.join(HERE, 'corepop_blocks.py'), 'rb').read()).hexdigest()
if not m.startswith(WANT):
    raise SystemExit(f'!! corepop_blocks.py md5 {m[:8]} ≠ {WANT} — 시작 안 함')
import corepop_blocks as cb  # noqa: E402

cb.KEYS = [k for k in cb.KEYS if k in set(SUB)]
if set(cb.KEYS) != set(SUB):
    raise SystemExit('!! 키 파일 구조가 묶음 대상과 어긋남')
cb.OUT = os.path.join(cb.D, f"results_corepop_blocks_{cb.MACHINE}_{'_'.join(BATS)}_heavy.json")
_orig_counts = cb.counts
_orig_inputs = cb.inputs
_orig_one_call = cb.one_call
SEEN = []
FIRST_FAIL = []
WAIT_S = int(os.environ.get('COREPOP_ZEO_RETRY_POLL_S', '60'))


def counts():
    """simulate 수가 ALLOW 이하이면 검사에는 0 으로 보이고 실제 수는 simulate_overlap 에 남깁니다. 넘으면 원판 값 그대로(원판이 멈춤)."""
    c = _orig_counts()
    n = c['simulate']
    if n <= ALLOW:
        SEEN.append(n)
        return {'simulate': 0, 'network': c['network'], 'simulate_overlap': n}
    return c


def inputs():
    """원판의 입력 대조를 그대로 한 뒤, 호출 순서만 단위셀 부피가 작은 구조부터로 바꿉니다(같으면 대상 순위 그대로 — 안정 정렬)."""
    rows, zinfo = _orig_inputs()
    rows.sort(key=lambda r: r['cell_volume_A3'])
    return rows, zinfo


def one_call(row, r):
    """폴더가 이미 있으면 재시도입니다(원판 one_call 이 같은 조건으로 폴더를 지움). 재시도는 simulate 0 을 기다린 뒤에 원판을 부릅니다."""
    bd = os.path.join(cb.BASE, row['file'][:-4], f'block{r:.2f}')
    retry = os.path.exists(bd)
    waited = 0
    if retry:
        t0 = time.time()
        while _orig_counts()['simulate'] > 0:
            if waited == 0:
                print(f"  재시도 대기: simulate 0 이 될 때까지 기다림({row['key']} r={r:.2f} 부터)", flush=True)
            time.sleep(WAIT_S)
            waited = round(time.time() - t0)
    x = _orig_one_call(row, r)
    if retry:
        x['retry_waited_for_simulate_0_s'] = waited
    elif not x['block_ok']:
        FIRST_FAIL.append({'key': row['key'], 'r': f'{r:.2f}', 'rc': x['rc'], 'seconds': x['seconds'], 'peak_rss_MB': x['peak_rss_MB'],
                           'stopped_by_guard': x['stopped_by_guard'], 'simulate_overlap': x['pre_counts'].get('simulate_overlap')})
    return x


cb.counts = counts
cb.inputs = inputs
cb.one_call = one_call

if __name__ == '__main__':
    print(f"무거운 구조 {len(cb.KEYS)} · 묶음 {BATS} · 키 파일 {os.path.basename(KF)} · 결과 {os.path.basename(cb.OUT)} · 병렬 {cb.PAR} · "
          f"같이 돌아도 되는 simulate ≤ {ALLOW} · 부피 작은 순 · 재시도는 simulate 0 뒤", flush=True)
    rc = cb.main()
    if os.path.exists(cb.OUT) and not cb.DRY:
        d = json.load(open(cb.OUT, encoding='utf-8'))
        d['overlap'] = {'allow_simulate': ALLOW, 'simulate_seen_max': max(SEEN) if SEEN else None, 'first_pass_failed': FIRST_FAIL,
                        'order': '단위셀 부피 작은 순(원판은 대상 순위 순)', 'retry': '직렬 재시도는 simulate 0 을 기다린 뒤(원판은 바로)',
                        'why': '사용자 결정 2026-11-16 01:1x "바로 시작해" — 앞 묶음(무거운 구조 b03 · b04)의 GCMC 가 도는 동안 다음 묶음의 Zeo++ 를 같이 돌림'
                               '(CLAUDE.md §5 의 동시 금지를 이 묶음에서 풂). 호출마다 pre_counts.simulate_overlap 이 실제 simulate 수',
                        'wrapper': 'corepop_blocks_keys_overlap2.py'}
        tmp = cb.OUT + '.tmp'
        json.dump(d, open(tmp, 'w', encoding='utf-8'), indent=2, ensure_ascii=False)
        os.replace(tmp, cb.OUT)
    sys.exit(rc)
