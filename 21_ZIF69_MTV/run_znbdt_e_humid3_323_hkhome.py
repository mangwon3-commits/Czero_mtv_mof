# -*- coding: utf-8 -*-
"""RT-E(323 K · RH 90 %) HKHOME 발사기 — 등록 `ASSIGN_ZNBDT_REALTEMP_20261108.md` §3 [11:4x 재배정] · 종합자 cloud.md 11-08 11:4x ①.

laptop2 실행기 `run_znbdt_e_humid3_323.py`(md5 7f83dc3c · master) 를 **무수정 import** 하고 둘만 바꿉니다.
  ① 기기 이름: env ZNBDT_E_MACHINE=hkhome(실행기의 setdefault 보다 먼저) → 폴더 humid_wc_runs_v3w_323/znbdt_e3_323_hkhome/ ·
     결과 results_znbdt_e_humid3_323_hkhome.json + _audit.json · 착수 잠금 ~/.mof_chain/.znbdt_e3_hkhome_start.lock.
  ② 착수 간격 60 s(종합자 11:4x "착수 60 s 간격") — 래퍼 `STAGGER` 15 → 60. 작업 i 는 T0 + 60 s × i 전에 띄우지 않음 + 래퍼 2 s 잠금 그대로.
     값을 만드는 부분(조건 · 사이클 · 막음 · 대상 · 씨앗 규칙)은 실행기 그대로입니다.
워커는 env ZNBDT_E_WORKERS(사슬이 줌). 실행기의 fix_header 를 그대로 부르고, 그 뒤 `hkhome_launcher` 칸 하나만 더합니다(값 · 행 · 감사 무수정).
"""
import json
import os
import sys

os.environ['ZNBDT_E_MACHINE'] = 'hkhome'
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)

WANT_R = '7f83dc3c57f5c89d357d877664139e5d'
import hashlib                                              # noqa: E402
_rp = os.path.join(HERE, 'run_znbdt_e_humid3_323.py')
_got = hashlib.md5(open(_rp, 'rb').read()).hexdigest()
if _got != WANT_R:
    sys.exit(f'  !! RT-E 실행기 md5 불일치 — 착수 안 함 ({_got} ≠ {WANT_R})')

import run_znbdt_e_humid3_323 as R                          # noqa: E402
E = R.E
assert E.MACHINE == 'hkhome', E.MACHINE
E.STAGGER = 60.0


def add_note():
    if not os.path.exists(E.OUT):
        return
    d = json.load(open(E.OUT, encoding='utf-8'))
    d['hkhome_launcher'] = {'file': os.path.basename(__file__), 'md5': E.md5(os.path.abspath(__file__)),
                            'runner': os.path.basename(_rp), 'runner_md5': WANT_R, 'stagger_s': E.STAGGER,
                            'workers': E.hw.MAX_WORKERS,
                            'why': 'REALTEMP §3 [11:4x 재배정] — laptop2 무응답(01:55~) → RT-E 를 HKHOME 이 맡음 · 착수 60 s 간격(종합자 11:4x)'}
    json.dump(d, open(E.OUT, 'w', encoding='utf-8'), ensure_ascii=False, indent=1, default=str)


if __name__ == '__main__':
    rc = E.main()
    R.fix_header()
    add_note()
    sys.exit(rc)
