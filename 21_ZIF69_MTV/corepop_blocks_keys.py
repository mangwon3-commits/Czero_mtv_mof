# -*- coding: utf-8 -*-
"""COREPOP-H323 — 다른 기기에서 막음이 안 된 무거운 구조만 다시 막음(사용자 지시 2026-11-15 "랩탑으로 넘겨").
`corepop_blocks.py`(c00cd11a) **무수정 import** 래퍼. 바꾼 것 둘뿐:
  · 대상 = env COREPOP_KEYS_FILE(JSON, 'keys' 목록)의 구조만(대상 목록 순서 유지). COREPOP_BATCHES 는 그 구조들의 묶음으로 자동.
  · 결과 이름 = results_corepop_blocks_<기기>_<묶음들>_heavy.json
측정 · 파싱 · 가드(새 호출은 MemAvailable ≥ 8,000 MB · 호출 중 < 5,000 MB 면 kill) · simulate 있으면 멈춤 · 실패 표지 · 끝의 직렬 재시도는 원판 그대로.
무거운 구조라 병렬은 COREPOP_ZEO_PAR=1 권장. COREPOP_ZEO_DRY=1 이면 입력 대조 · 계획만.
사용: COREPOP_MACHINE=laptop COREPOP_KEYS_FILE=corepop_heavy_keys_20261115.json COREPOP_ZEO_PAR=1 python corepop_blocks_keys.py
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
print(f"무거운 구조 {len(cb.KEYS)} · 묶음 {BATS} · 키 파일 {os.path.basename(KF)} · 결과 {os.path.basename(cb.OUT)} · 병렬 {cb.PAR}", flush=True)
sys.exit(cb.main())
