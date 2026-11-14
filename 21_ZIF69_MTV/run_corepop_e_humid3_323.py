# -*- coding: utf-8 -*-
"""COREPOP-H323 — CoRE 모집단 3D(CORE22 제외)의 323 K 습윤 3성분 흡착점 S_humid,323(RT-E 조건 · CORE22 §F 와 같은 조건).
사용자 지시 2026-11-14 · `ASSIGN_COREPOP_HUMID323_20261114.md`. `run_core22_e_humid3_323.py`(b975bd93 · CORE22 §F 실행기) 사본 — 다른 것은
import 대상(`run_corepop_e_humid3.py` e05cbc1b · `run_znbdt_e_humid3_323.py` 7f83dc3c 무수정) · env 이름(COREPOP_F_*) · 폴더 · 결과 이름 · 머리 문자열뿐.
323 K 세 값(323 K · 물 11,114.1 Pa · N₂ 0.738859)은 RT-E 실행기가 넣고 여기서는 들어갔는지만 확인(다르면 시작 안 함) — §F 원판 그대로.
env  COREPOP_F_MACHINE(필수) · COREPOP_F_BATCHES(예 b01) 또는 COREPOP_F_KEYS · COREPOP_F_BLOCKS(막음 결과 파일 쉼표) · COREPOP_F_WORKERS(기본 8) ·
     COREPOP_F_REPS(기본 1) · COREPOP_F_SMOKE=1 / COREPOP_F_DRY=1 · COREPOP_F_CORE_CAP=N(기기 전체 simulate 상한 · 기본 0 = 끔)
결과 results_corepop_e_humid3_323_<기기>_<묶음>.json + _audit.json. 판정 없음 — 종합자.
"""
import fcntl
import hashlib
import json
import os
import sys
import threading
import time

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
MACHINE = os.environ.get('COREPOP_F_MACHINE', '')
SMOKE = bool(os.environ.get('COREPOP_F_SMOKE'))
DRY = bool(os.environ.get('COREPOP_F_DRY'))
KEYS = os.environ.get('COREPOP_F_KEYS', '')
BATCHES = os.environ.get('COREPOP_F_BATCHES', '')
BATCH = BATCHES.replace(',', '_') if BATCHES else ('keys' if KEYS else '')
CORE_CAP = int(os.environ.get('COREPOP_F_CORE_CAP', '0'))
if not MACHINE or not (KEYS or BATCHES):
    raise SystemExit('!! COREPOP_F_MACHINE 와 COREPOP_F_BATCHES(또는 COREPOP_F_KEYS) 를 주세요')
WANT = {'run_corepop_e_humid3.py': 'e05cbc1b', 'run_znbdt_e_humid3_323.py': '7f83dc3c', 'run_znbdt_e_humid3.py': '97023663'}


def md5(p):
    return hashlib.md5(open(p, 'rb').read()).hexdigest()


for f, w in WANT.items():
    if not md5(os.path.join(HERE, f)).startswith(w):
        raise SystemExit(f'!! {f} md5 {md5(os.path.join(HERE, f))[:8]} ≠ {w} — 시작 안 함')

# ① C 실행기(사본) 먼저 — 래퍼 E 가 CoRE 대상 env 로 import 됨
os.environ['COREPOP_E_MACHINE'] = MACHINE
os.environ['COREPOP_E_WORKERS'] = os.environ.get('COREPOP_F_WORKERS', '8')
os.environ['COREPOP_E_REPS'] = os.environ.get('COREPOP_F_REPS', '1')
os.environ['COREPOP_BLOCKS'] = os.environ.get('COREPOP_F_BLOCKS', '')
for v, val in (('COREPOP_E_KEYS', KEYS), ('COREPOP_E_BATCHES', BATCHES)):
    if val:
        os.environ[v] = val
    else:
        os.environ.pop(v, None)
for v, on in (('COREPOP_E_SMOKE', SMOKE), ('COREPOP_E_DRY', DRY)):
    if on:
        os.environ[v] = '1'
    else:
        os.environ.pop(v, None)
import run_corepop_e_humid3 as C    # noqa: E402
E = C.E
CBLOCKS = E.BLOCKS                  # C 판 막음 표
import run_znbdt_e_humid3_323 as W  # noqa: E402  (세 값 · 그리고 막음 · 폴더 · 이름 · 작업을 자기 것으로 덮음)

# ② 되돌리고 · F 판으로
E.BLOCKS = CBLOCKS
if not (E.Y == {'CO2': 0.15, 'N2': 0.738859, 'water': 0.111141} and E.hw.CONDITIONS == [('ads', 15000.0, 323.0, 12349.0)]
        and abs(E.hw.P_H2O - 11114.1) < 1e-6 and E.BASES == C.BASES):
    raise SystemExit(f'!! 323 K 세 값 · 대상이 기대와 다름 — Y {E.Y} · 조건 {E.hw.CONDITIONS} · 물 {E.hw.P_H2O} · BASES 같음 {E.BASES == C.BASES}')
MODE = C.MODE
ROOT = (os.path.join(E.CHAIN, f'corepop_e3_323_{MODE}_{MACHINE}') if MODE
        else os.path.join(HERE, 'humid_wc_runs_v3w_323', f'corepop_e3_323_{MACHINE}' + (f'_{BATCH}' if BATCH else '')))
NAME = f'results_corepop_e_humid3_323_{MACHINE}' + (f'_{BATCH}' if BATCH else '')
E.ROOT = ROOT
E.hw.RUNS = os.path.join(ROOT, 'runs')
E.hw.CHARGED = os.path.join(ROOT, 'cifs')
E.SRC = os.path.join(ROOT, 'src')
E.OUT = os.path.join(ROOT, f'{NAME}_{MODE}.json') if MODE else os.path.join(HERE, f'{NAME}.json')
E.AUDIT = E.OUT.replace('.json', '_audit.json')
E.LOCK = os.path.join(E.CHAIN, f'.corepop_e3_323_{MACHINE}_start.lock')
E.TAGS = [f'{b}_e3r1' for b in C.BASES] if MODE else list(C.LPT)
E.hw.TARGETS = E.TAGS
E.JOBS = [(t, lab, p, T, ps) for t in E.TAGS for lab, p, T, ps in E.hw.CONDITIONS]

# ④ 코어 문 — G 실행기와 같은 잠금 파일
GATE = os.path.join(E.CHAIN, f'.core22_g_{MACHINE}_gate.lock')
_e_run = E.hw.subprocess.run        # 래퍼 _run(입력 고침 · 막음 파일 → RASPA)


def n_simulate():
    n = 0
    for p in os.listdir('/proc'):
        if p.isdigit():
            try:
                with open(f'/proc/{p}/comm') as f:
                    n += f.read().strip() == 'simulate'
            except OSError:
                pass
    return n


def _gated(args, *a, **k):
    if CORE_CAP and k.get('cwd') and args and args[0] == C.rg.SIMULATE and not DRY:
        f = open(GATE, 'a+')
        fcntl.flock(f, fcntl.LOCK_EX)
        while n_simulate() >= CORE_CAP:
            time.sleep(20)
        threading.Timer(5.0, f.close).start()
        return _e_run(args, *a, **k)
    return _e_run(args, *a, **k)


E.hw.subprocess.run = _gated


def fix_f():
    if not os.path.exists(E.OUT):
        return
    d = json.load(open(E.OUT, encoding='utf-8'))
    old = {k: d.get(k) for k in ('test', 'assign')}
    d['test'] = 'COREPOP-H323 — CoRE 모집단 3D 습윤 3성분 흡착점 S_humid,323(323 K · RH 90 % · RT-E 조건 · CORE22 §F 와 같은 조건)'
    d['assign'] = 'ASSIGN_COREPOP_HUMID323_20261114.md'
    d['thin_runner_F'] = {'file': os.path.basename(__file__), 'md5': md5(os.path.abspath(__file__)),
                          'imports': {f: md5(os.path.join(HERE, f)) for f in WANT}, 'core_cap': CORE_CAP, 'batch': BATCH,
                          'keys': list(C.KEYS)}
    d['launcher_fix_F'] = {'why': 'RT-E fix_header() 가 test · assign 을 Zn(bib)(bdtdc) RT-E 문자열로 씀 — COREPOP 판으로. 값 · 행 · 감사는 그대로', 'before': old}
    tmp = E.OUT + '.tmp'
    json.dump(d, open(tmp, 'w', encoding='utf-8'), ensure_ascii=False, indent=1, default=str)
    os.replace(tmp, E.OUT)


def main():
    print(f'COREPOP-H323 — 323 K · 물 {E.hw.P_H2O:.1f} Pa · y {E.Y} · 키 {len(C.KEYS)} · 작업 {len(E.JOBS)} · 코어 문 {CORE_CAP} · 폴더 {ROOT} · 결과 {E.OUT}', flush=True)
    E.T0 = time.time()
    rc = C.main()
    W.fix_header()
    fix_f()
    return rc


if __name__ == '__main__':
    sys.exit(main())
