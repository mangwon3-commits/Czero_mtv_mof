# -*- coding: utf-8 -*-
"""CORE22 §F — CoRE 3차원 22종의 323 K 습윤 3성분 선택도 S_humid,323(RT-E 조건). 등록 `ASSIGN_CORE22_HUMID_PLAN_20261108.md` §F(자료 0건).
얇은 실행기 — `run_core22_e_humid3.py`(d24e8e2d · C 실행기)와 `run_znbdt_e_humid3_323.py`(7f83dc3c · RT-E 실행기)를 **둘 다 무수정 import**.
래퍼 `run_znbdt_e_humid3.py`(97023663) · 러너(run_humid_wc_v3w · run_humid_wc)도 무수정입니다.
  ① import 순서: C 실행기를 먼저 import 합니다. 래퍼 E 가 CoRE 대상 env 로 처음 import 되어 BASES · LPT · 막음 표 · patch_input · row_of · summarize 가
     C 판이 됩니다(E 는 BASES 를 import 순간 env 로 정하고 prep · summarize 가 그것을 씀). 이어 RT-E 실행기를 import 하면, 그 모듈이 등록 §1 의
     세 값(323 K · 물 11,114.1 Pa · N₂ 0.738859)을 E.hw.CONDITIONS · E.hw.P_H2O · E.Y 에 넣고, E.BLOCKS · 폴더 · 결과 이름 · 작업 목록을 자기 것으로 덮습니다.
  ② 그 뒤 여기서 바꾸는 것: E.BLOCKS 를 C 판(results_core22_blocks_laptop.json · 구 0 이면 그 성분 막음 없음)으로 되돌림 · 폴더
     (humid_wc_runs_v3w_323/core22_e3_323_<기기>) · 잠금 · 결과 이름(results_core22_e_humid3_323_<기기>.json + _audit.json) · 대상(CORE22_F_KEYS · 구조당 e3r1~3 · LPT 순).
     세 값은 RT-E 실행기가 넣은 그대로이고, 여기서는 그 값이 들어갔는지만 확인합니다(다르면 시작 안 함).
  ③ 끝에서 RT-E 의 fix_header() 를 그대로 불러 머리의 298 K 문자열(protocol.T_K · definition)을 323 K 판으로 바로잡고, 이어 test · assign 두 칸만
     F 판으로 바꿉니다(fix_header 가 Zn(bib)(bdtdc) RT-E 문자열을 쓰므로 · 바꾼 칸을 launcher_fix_F 에 적음). 값 · 행 · 감사는 건드리지 않습니다.
  ④ 코어 문(선택): CORE22_F_CORE_CAP=N 이면 기기 전체 simulate 가 N 개 미만일 때만 RASPA 를 띄움. 문 잠금은 G 실행기(run_core22_g_humid_wc.py)와
     **같은 파일**이라 두 실행기가 함께 돌아도 상한을 같이 셉니다. 기본 0 = 끔.
env  CORE22_F_KEYS 쉼표(core_pop key · 실행 · 스모크는 필수) · CORE22_F_MACHINE(기본 laptop) · CORE22_F_WORKERS(기본 8) · CORE22_F_BATCH(같은 기기 둘째 묶음부터 폴더 · 결과 이름에 붙임)
     CORE22_F_SMOKE=1 / CORE22_F_DRY=1 → 래퍼의 스모크(10 사이클 · r1) · 드라이(RASPA 안 띄우고 고친 입력만) · 폴더는 저장소 밖 · 드라이는 키 없으면 22종
     CORE22_F_CORE_CAP=N
판정 없음 — 종합자.
"""
import fcntl
import hashlib
import json
import os
import sys
import threading
import time

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
MACHINE = os.environ.get('CORE22_F_MACHINE', 'laptop')
SMOKE = bool(os.environ.get('CORE22_F_SMOKE'))
DRY = bool(os.environ.get('CORE22_F_DRY'))
KEYS = os.environ.get('CORE22_F_KEYS', '')
BATCH = os.environ.get('CORE22_F_BATCH', '')
CORE_CAP = int(os.environ.get('CORE22_F_CORE_CAP', '0'))
if not KEYS and not DRY:
    raise SystemExit('!! CORE22_F_KEYS 가 비었음 — 실행 · 스모크는 착수 글에 적은 구조를 줘야 함')
WANT = {'run_core22_e_humid3.py': 'd24e8e2d', 'run_znbdt_e_humid3_323.py': '7f83dc3c', 'run_znbdt_e_humid3.py': '97023663'}


def md5(p):
    return hashlib.md5(open(p, 'rb').read()).hexdigest()


for f, w in WANT.items():
    if not md5(os.path.join(HERE, f)).startswith(w):
        raise SystemExit(f'!! {f} md5 {md5(os.path.join(HERE, f))[:8]} ≠ {w} — 시작 안 함')

# ① C 실행기 먼저 — 래퍼 E 가 CoRE 대상 env 로 import 됨
os.environ['CORE22_E_SLOT'] = 'all'
os.environ['CORE22_E_MACHINE'] = MACHINE
os.environ['CORE22_E_WORKERS'] = os.environ.get('CORE22_F_WORKERS', '8')
if KEYS:
    os.environ['CORE22_E_KEYS'] = KEYS
else:
    os.environ.pop('CORE22_E_KEYS', None)
for v, on in (('CORE22_E_SMOKE', SMOKE), ('CORE22_E_DRY', DRY)):
    if on:
        os.environ[v] = '1'
    else:
        os.environ.pop(v, None)
import run_core22_e_humid3 as C     # noqa: E402
E = C.E
CBLOCKS = E.BLOCKS                  # C 판 막음 표
import run_znbdt_e_humid3_323 as W  # noqa: E402  (세 값 · 그리고 막음 · 폴더 · 이름 · 작업을 자기 것으로 덮음)

# ② 되돌리고 · F 판으로
E.BLOCKS = CBLOCKS
if not (E.Y == {'CO2': 0.15, 'N2': 0.738859, 'water': 0.111141} and E.hw.CONDITIONS == [('ads', 15000.0, 323.0, 12349.0)]
        and abs(E.hw.P_H2O - 11114.1) < 1e-6 and E.BASES == C.BASES):
    raise SystemExit(f'!! 323 K 세 값 · 대상이 기대와 다름 — Y {E.Y} · 조건 {E.hw.CONDITIONS} · 물 {E.hw.P_H2O} · BASES 같음 {E.BASES == C.BASES}')
MODE = C.MODE
ROOT = (os.path.join(E.CHAIN, f'core22_e3_323_{MODE}_{MACHINE}') if MODE
        else os.path.join(HERE, 'humid_wc_runs_v3w_323', f'core22_e3_323_{MACHINE}' + (f'_{BATCH}' if BATCH else '')))
NAME = f'results_core22_e_humid3_323_{MACHINE}' + (f'_{BATCH}' if BATCH else '')
E.ROOT = ROOT
E.hw.RUNS = os.path.join(ROOT, 'runs')
E.hw.CHARGED = os.path.join(ROOT, 'cifs')
E.SRC = os.path.join(ROOT, 'src')
E.OUT = os.path.join(ROOT, f'{NAME}_{MODE}.json') if MODE else os.path.join(HERE, f'{NAME}.json')
E.AUDIT = E.OUT.replace('.json', '_audit.json')
E.LOCK = os.path.join(E.CHAIN, f'.core22_e3_323_{MACHINE}_start.lock')
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
    d['test'] = 'CORE22 §F — CoRE 3차원 22종의 습윤 3성분 흡착점 S_humid,323(323 K · RH 90 % · RT-E 조건)'
    d['assign'] = 'ASSIGN_CORE22_HUMID_PLAN_20261108.md §F'
    d['thin_runner_F'] = {'file': os.path.basename(__file__), 'md5': md5(os.path.abspath(__file__)),
                          'imports': {f: md5(os.path.join(HERE, f)) for f in WANT}, 'core_cap': CORE_CAP, 'batch': BATCH,
                          'keys': list(C.KEYS)}
    d['launcher_fix_F'] = {'why': 'RT-E fix_header() 가 test · assign 을 Zn(bib)(bdtdc) RT-E 문자열로 씀 — F 판으로. 값 · 행 · 감사는 그대로', 'before': old}
    tmp = E.OUT + '.tmp'
    json.dump(d, open(tmp, 'w', encoding='utf-8'), ensure_ascii=False, indent=1, default=str)
    os.replace(tmp, E.OUT)


def main():
    print(f'CORE22 §F — 323 K · 물 {E.hw.P_H2O:.1f} Pa · y {E.Y} · 키 {len(C.KEYS)} · 작업 {len(E.JOBS)} · 코어 문 {CORE_CAP} · 폴더 {ROOT} · 결과 {E.OUT}', flush=True)
    E.T0 = time.time()
    rc = C.main()
    W.fix_header()
    fix_f()
    return rc


if __name__ == '__main__':
    sys.exit(main())
