# -*- coding: utf-8 -*-
"""CoRE 22 얇은 실행기용 코어 문(HKHOME · 일정 도구) — 기기 전체 `simulate` 가 CORE22_CORE_CAP 개 미만일 때만 RASPA 를 띄움.
G 실행기 `run_core22_g_humid_wc.py`(6a8a8eeb) ⑥ 의 코어 문과 같은 코드를 **실행기 밖에** 둔 것 — 실행기 파일은 건드리지 않고(무수정 import),
같은 기기에서 앞 묶음의 꼬리와 다음 묶음이 겹칠 때 코어가 놀지도 넘치지도 않게 함(CLAUDE.md §5 물리 8코어 · §9 유휴 방지).
값을 만드는 부분은 하나도 바꾸지 않음: 실행기 모듈을 import 한 뒤 그 모듈이 이미 감싸 둔 `subprocess.run` 을 한 겹 더 감싸 **착수 시각만 늦춤**.
문 잠금을 잡고 기다렸다가 띄운 뒤 5 s 에 타이머가 잠금을 풀므로, 다음 작업은 이 simulate 가 셈에 든 뒤에 셈(착수 사이 ≥ 5 s → 씨앗 = 착수 초가 겹치지 않음).
사용: CORE22_CORE_CAP=8 <실행기 env …> python -u core22_core_gate.py <실행기 모듈 이름>
      예) CORE22_CORE_CAP=8 CORE22_H_KEYS=… CORE22_H_MACHINE=hkhome CORE22_H_WORKERS=8 CORE22_H_BATCH=b2 python -u core22_core_gate.py run_core22_h_humid_wc_323
CORE22_CORE_CAP 이 없거나 0 이면 문 없이 실행기 main() 을 그대로 부름. 요약의 thin_runner_md5 는 실행기 파일의 것 그대로(이 파일은 요약에 안 적힘 — 사슬 기록에 md5 를 남김).
"""
import fcntl
import importlib
import os
import sys
import threading
import time

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
if len(sys.argv) != 2:
    raise SystemExit('사용: python -u core22_core_gate.py <실행기 모듈 이름>')
CORE_CAP = int(os.environ.get('CORE22_CORE_CAP', '0'))
mod = importlib.import_module(sys.argv[1])          # 실행기 최상위 실행(env 로 대상 · 뿌리 · 감싸기가 정해짐) — main() 은 아직 안 부름
hw = mod.hw
SIMULATE = mod.rg.SIMULATE
DRY = bool(getattr(mod, 'DRY', False))
GATE = os.path.join(os.path.expanduser('~/.mof_chain'), '.core22_core_gate.lock')
_t_run = hw.subprocess.run                          # 실행기가 감싸 둔 것(막음 삽입 → 착수 간격 → RASPA)


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
    if CORE_CAP and k.get('cwd') and args and args[0] == SIMULATE and not DRY:
        # 323 틀(run_znbdt_humid_wc_323)은 착수 간격(T0 + 15 s × i)을 RASPA 호출 **안에서** 기다림 — 문을 지난 뒤 기다리면
        # 그 사이 다음 작업이 같은 셈을 보고 문을 지나 CAP 을 넘김. 그래서 같은 대기를 문 **앞에서** 먼저 채움(틀 안의 대기는 0 이 됨).
        T = getattr(mod, 'T', None)
        if T is not None and all(hasattr(T, x) for x in ('INDEX', 'T0', 'STAGGER')):
            i = T.INDEX.get(os.path.basename(os.path.normpath(k['cwd'])))
            if i is not None:
                w = T.T0 + i * T.STAGGER - time.time()
                if w > 0:
                    time.sleep(w)
        f = open(GATE, 'a+')
        fcntl.flock(f, fcntl.LOCK_EX)
        while n_simulate() >= CORE_CAP:
            time.sleep(20)
        threading.Timer(5.0, f.close).start()
        return _t_run(args, *a, **k)
    return _t_run(args, *a, **k)


hw.subprocess.run = _gated
print(f'코어 문 — 실행기 {sys.argv[1]} · CORE22_CORE_CAP {CORE_CAP or "끔"} · 지금 simulate {n_simulate()} · 잠금 {GATE}', flush=True)
sys.exit(mod.main())
