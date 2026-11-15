# -*- coding: utf-8 -*-
"""COREPOP-H323 — 키 파일 구조의 Zeo++ 막음을 RASPA 작업이 조금 남은 채로 돌리는 판(랩탑 · 사용자 결정 2026-11-15 23:2x "같이 돌려. 시간이 없다").
`corepop_blocks_keys.py`(c2a71d4c)와 같은 일을 하고 `corepop_blocks.py`(c00cd11a)를 **무수정 import** 합니다. 다른 것은 하나뿐입니다:
  · 원판은 simulate 가 하나라도 있으면 Zeo++ 를 띄우지 않습니다(CLAUDE.md §5). 이 판은 simulate 수가 env COREPOP_ZEO_ALLOW_SIM(필수 · 정수) 이하이면 띄웁니다.
    그 수를 넘으면 원판과 똑같이 멈춥니다. 실제 simulate 수는 호출마다 pre_counts 의 'simulate_overlap' 에 남기고, 결과 파일 머리에 'overlap' 을 적습니다.
측정 · 파싱 · 메모리 가드(새 호출은 MemAvailable ≥ 8,000 MB · 호출 중 < 5,000 MB 면 kill) · 실패 표지 · 직렬 재시도 · 결과 이름은 그대로입니다.
사용: COREPOP_MACHINE=laptop COREPOP_KEYS_FILE=<키 파일> COREPOP_ZEO_PAR=1 COREPOP_ZEO_ALLOW_SIM=1 python corepop_blocks_keys_overlap.py   (COREPOP_ZEO_DRY=1 이면 입력 대조 · 계획만)
"""
import hashlib
import json
import os
import sys

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
if ALLOW < 0 or ALLOW > 2:
    raise SystemExit(f'!! COREPOP_ZEO_ALLOW_SIM {ALLOW} — 0 ~ 2 만 받습니다')
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
SEEN = []


def counts():
    """simulate 수가 ALLOW 이하이면 검사에는 0 으로 보이고 실제 수는 simulate_overlap 에 남깁니다. 넘으면 원판 값 그대로(원판이 멈춤)."""
    c = _orig_counts()
    n = c['simulate']
    if n <= ALLOW:
        SEEN.append(n)
        return {'simulate': 0, 'network': c['network'], 'simulate_overlap': n}
    return c


cb.counts = counts

if __name__ == '__main__':
    print(f"무거운 구조 {len(cb.KEYS)} · 묶음 {BATS} · 키 파일 {os.path.basename(KF)} · 결과 {os.path.basename(cb.OUT)} · 병렬 {cb.PAR} · "
          f"같이 돌아도 되는 simulate ≤ {ALLOW}", flush=True)
    rc = cb.main()
    if os.path.exists(cb.OUT) and not cb.DRY:
        d = json.load(open(cb.OUT, encoding='utf-8'))
        d['overlap'] = {'allow_simulate': ALLOW, 'simulate_seen_max': max(SEEN) if SEEN else None,
                        'why': '사용자 결정 2026-11-15 23:2x — b05 의 마지막 GCMC 한 작업이 도는 동안 Zeo++ 를 같이 돌림(CLAUDE.md §5 의 동시 금지를 이번만 풂). '
                               '호출마다 pre_counts.simulate_overlap 이 실제 simulate 수', 'wrapper': 'corepop_blocks_keys_overlap.py'}
        tmp = cb.OUT + '.tmp'
        json.dump(d, open(tmp, 'w', encoding='utf-8'), indent=2, ensure_ascii=False)
        os.replace(tmp, cb.OUT)
    sys.exit(rc)
