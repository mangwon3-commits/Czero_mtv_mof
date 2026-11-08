# -*- coding: utf-8 -*-
"""−NO₂ 298 K 습윤 TSA 회수량 반복 4~6 — HKHOME 발사기. 등록 `ASSIGN_ZNBDT_6SEED_CORE_20261108.md` §A(HKHOME 몫 −CN · −NO₂).

laptop2 ⑩ 실행기 `run_e24i_no2_humid_wc.py`(md5 c2d4673a) 를 **무수정 import** 합니다. 그 실행기는 기기 이름(`MACHINE='laptop2'`)과
요약 경로(`SUMMARY`)를 모듈 안에 고정해 두어, 그대로 돌리면 이 기기에서 laptop2 의 ⑩ 요약 파일
(`results_e24i_e24i_no2_open_humid_summary_laptop2.json` · master 추적)을 덮어씁니다. 그래서 둘만 바꿉니다.
  ① 대상 · 워커 · 결과 이름: env HWC_V3W_TARGETS = e24i_no2_open_h4,h5,h6 · HWC_V3W_WORKERS(사슬이 줌) ·
     HWC_V3W_RESULT = humid_working_capacity_w2_e24i_no2_open_s456_hkhome.json(등록 §A 이름) — 실행기의 setdefault 보다 먼저.
  ② `MACHINE` = 'hkhome' · `SUMMARY` = results_e24i_no2_open_s456_humid_summary_hkhome.json(등록 §A 이름).
막음(물 1.30 구 4 · CO₂ 없음) · 삽입 · 감사 · 착수 간격(15 s + 2 s 잠금) · 사본 만들기(원본 3a2a53ac 대조)는 실행기 그대로이고,
아래 본문은 실행기의 `if __name__ == '__main__'` 절과 같은 순서입니다(파일 관문 → 기존 결과 · 폴더 거부 → prep → hw.main → audit → summarize).
E24I_DRY=1 이면 실행기의 드라이(저장소 밖 · 사이클 10 · RASPA 안 띄움) 그대로.
"""
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
os.environ['HWC_V3W_TARGETS'] = ','.join(f'e24i_no2_open_h{k}' for k in (4, 5, 6))
os.environ['HWC_V3W_RESULT'] = 'humid_working_capacity_w2_e24i_no2_open_s456_hkhome.json'
os.environ.setdefault('HWC_V3W_WORKERS', '4')

WANT = 'c2d4673a41523ddee59295f2a8938200'
_rp = os.path.join(HERE, 'run_e24i_no2_humid_wc.py')
_got = hashlib.md5(open(_rp, 'rb').read()).hexdigest()
if _got != WANT:
    sys.exit(f'  !! −NO₂ 실행기 md5 불일치 — 착수 안 함 ({_got} ≠ {WANT})')

import run_e24i_no2_humid_wc as N                           # noqa: E402

N.MACHINE = 'hkhome'
if not N.DRY:
    N.SUMMARY = os.path.join(HERE, 'results_e24i_no2_open_s456_humid_summary_hkhome.json')
hw = N.hw
assert hw.TARGETS == ['e24i_no2_open_h4', 'e24i_no2_open_h5', 'e24i_no2_open_h6'], hw.TARGETS

if __name__ == '__main__':
    ok, fm = N.ff_gate.md5_gate()
    print(f"  파일 관문 md5 {fm} {'일치' if ok else '불일치 — 중단'}", flush=True)
    if not ok:
        sys.exit(3)
    print(f"−NO₂ 습윤 회수량 반복 4~6(HKHOME) — 착수 간격 {N.STAGGER:.0f} s(+ 2 s 잠금) · 작업 {len(N.JOBS)} · 드라이 {N.DRY} · "
          f"사이클 {hw.CYCLES}+{hw.INIT} · 요약 {N.SUMMARY}", flush=True)
    for k in ('CHARGED', 'RUNS', 'RESULT', 'TARGETS', 'MAX_WORKERS'):
        print(f'  {k:12s} {getattr(hw, k)}', flush=True)
    if os.path.exists(hw.RESULT) or os.path.exists(N.SUMMARY) or any(os.path.exists(os.path.join(hw.RUNS, f'{lab}_{t}')) for t in hw.TARGETS for lab, *_ in hw.CONDITIONS):
        print('  !! 이전 결과 · 요약 · 실행 폴더 있음 — 중단(러너가 cached 로 재사용하므로)', flush=True)
        sys.exit(1)
    info = N.prep()
    rc = hw.main()
    rows, aud = N.audit()
    out = N.summarize(rows, aud, info)
    d = json.load(open(N.SUMMARY, encoding='utf-8'))
    d['assign'] = 'ASSIGN_ZNBDT_6SEED_CORE_20261108.md §A (HKHOME 반복 4~6)'
    d['hkhome_launcher'] = {'file': os.path.basename(__file__), 'md5': N.md5(os.path.abspath(__file__)), 'runner': os.path.basename(_rp),
                            'runner_md5': WANT, 'why': '실행기의 MACHINE · SUMMARY 고정값만 바꿈(laptop2 ⑩ 요약 덮어쓰기 방지)'}
    json.dump(d, open(N.SUMMARY, 'w', encoding='utf-8'), indent=2, ensure_ascii=False)
    print(f"감사 {json.dumps(aud, ensure_ascii=False)}", flush=True)
    for r in rows:
        print(f"  {r['condition']:<4} {r['target']:<20} ok {r['ok']} · 입력 막음 줄 {r.get('blockpockets_in_input')} · 물 차단 {r.get('block', {}).get('water', {}).get('n_blocked')}"
              f"/{r.get('n_expected_water')} · 완주 {r.get('finished')} · rc {r.get('returncode')} · not-found {r.get('stderr_not_found')} · 씨앗 {r.get('seed')}", flush=True)
    print(f"요약 저장 {N.SUMMARY}", flush=True)
    sys.exit(rc or 0)
