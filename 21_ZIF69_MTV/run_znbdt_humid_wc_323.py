"""Zn(bib)(bdtdc) 실온도 습윤 TSA 작업 용량(RT-WC) — 등록 `ASSIGN_ZNBDT_REALTEMP_20261108.md` §1 · §3(자료 0건 · 00:1x).
**막음 없는 대상 전용**(298 K E 표에서 주머니 막음이 없는 구조: 모체 · −CN · −Br · −Cl · −CH₃ 열린 자리). −NO₂ 처럼 물 막음이
필요한 대상은 이 실행기로 돌리지 않습니다(아래 NEEDS_BLOCK 에 걸리면 착수 전에 멈춤 — 막음 삽입은 E-24f 식 실행기 몫).

자: `run_humid_wc_v3w_323.py`(T-RT-1 래퍼 · 출처 검사 · 재개 가드 · 결측 판정 · 머리말 관문) **무수정 import**.
    import 하는 순간 그 모듈 최상위가 env(HWC_323_TARGETS · _WORKERS · _RESULT)로 hw 전역 · 323 K 조건 · run_one_323 을 정합니다.
    조건(ads 323 K/15 kPa · tsa 373 K · vsa 323 K/5 kPa · 물 11,114.1 Pa 공통) · 사이클 5,000+15,000 · 힘장 · 전하 · 2×2×2 는 그 래퍼 그대로입니다.
대상: 바이트 같은 사본 `<구조>_h1~_h3`(charged_v3 · 298 K WC 와 같은 사본) = 3씨앗.

이 파일이 래퍼에 더하는 것(대상 말고는 아래 넷뿐 — 전부 RASPA 호출 자리 `hw.subprocess.run` 을 감싸서, 래퍼의 run_one_323 이름 검사와 부딪치지 않음):
  ① 착수 간격 — 작업 i 는 T0 + 15 s × i 전에 simulate 를 띄우지 않고, 착수 사이를 2 s 이상 벌림(잠금 파일).
     **왜**: RASPA 씨앗은 착수 시각(초)입니다. 래퍼만으로 돌리면 같은 초에 뜬 작업끼리 씨앗이 같아집니다
     (랩탑 T-RT-1 saIm025e: 8작업이 씨앗 1789800424 하나). 실현이 다른 구조였던 그때는 값이 같아지지 않았지만,
     **바이트 같은 사본 셋이 같은 씨앗을 받으면 같은 계산을 세 번 한 것이 3씨앗으로 보입니다.** E-24f · E-24i 틀(15 s + 2 s)과 같은 장치입니다.
  ② 반환코드(`znbdt323_returncode.txt`) · stderr(`stderr.txt`) 를 실행 폴더에 기록(러너는 둘 다 버림).
  ③ 첫 착수 전용: 결과 파일(완주 · PARTIAL) 이나 실행 폴더가 이미 있으면 멈춤(러너가 .data 를 표지 없이 cached 로 회수하므로 — CLAUDE.md §0 · §3).
  ④ 끝에서 감사(작업마다 .data 1 · finished · rc 0 · BlockPockets 줄 0 · 막음 줄 0 · 씨앗 · 씨앗 전부 고유) + 요약(구조별 3씨앗 평균 · ±̄/√3 · SD).
     판정은 종합자 — 요약은 기계적 사실뿐.

env: HWC_323_TARGETS(쉼표 · 필수) · HWC_323_WORKERS · HWC_323_RESULT(v3w_humid_wc_323/ 아래 파일명) · HWC_323_MACHINE(필수)
     HWC_323_DRYRUN=1  사전검사 · 작업 목록 · 착수 간격만 찍고 끝
     ZNBDT323_SMOKE=1  사이클 10 · 초기화 0 · 실행 폴더 · 결과를 저장소 밖(~/.mof_chain/znbdt323_smoke)으로 — 착수 간격 · 감사가 먹는지 먼저 봄.
                       (래퍼 사전검사는 15,000/5,000 을 요구하므로 사전검사 **뒤에** 사이클을 줄입니다. 스모크 값은 결과로 쓰지 않습니다.)
"""
import fcntl
import json
import math
import os
import re
import statistics as st
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import ff_gate                        # noqa: E402
import run_humid_wc_v3w_323 as R      # noqa: E402  무수정 import — env(HWC_323_*)로 hw 전역 · 조건 · run_one_323 을 정함
hw = R.hw
rg = hw.rg

STAGGER = 15.0
GAP = 2.0
NOT_FOUND = "'Blocking-pocket' file not found"
NEEDS_BLOCK = ('e24i_no2_open', 'e24i_c2h5_open')     # 298 K 표에서 막음이 있는 구조 — 이 실행기 밖
MACHINE = os.environ.get('HWC_323_MACHINE', '')
SMOKE = bool(os.environ.get('ZNBDT323_SMOKE'))
CHAIN = os.path.expanduser('~/.mof_chain'); os.makedirs(CHAIN, exist_ok=True)
LOCK = os.path.join(CHAIN, f'.znbdt323_{MACHINE or "x"}_start.lock')
SUMMARY = os.path.join(HERE, f'results_znbdt_humid_wc_323_summary_{MACHINE or "x"}.json')
RCFILE = 'znbdt323_returncode.txt'
if SMOKE:
    SM = os.path.join(CHAIN, 'znbdt323_smoke'); os.makedirs(SM, exist_ok=True)
    hw.RUNS = os.path.join(SM, 'runs')
    hw.RESULT = os.path.join(SM, 'smoke_result.json')
    R.STATUS_LOG = hw.RESULT + '.status.jsonl'
    SUMMARY = os.path.join(SM, 'smoke_summary.json')
    LOCK = os.path.join(SM, '.start.lock')
JOBS = [(t, lab, p, T, ps) for t in hw.TARGETS for lab, p, T, ps in hw.CONDITIONS]   # hw.main 과 같은 순서
INDEX = {f'{lab}_{t}': i for i, (t, lab, *_r) in enumerate(JOBS)}
T0 = time.time()                      # fork 로 워커에 물려짐

_real_run = hw.subprocess.run


def _run(args, *a, **k):
    """simulate 호출만: 착수 간격(①) → stderr · 반환코드 기록(②). 다른 호출은 그대로 통과."""
    cwd = k.get('cwd')
    if not (cwd and args and args[0] == rg.SIMULATE):
        return _real_run(args, *a, **k)
    i = INDEX.get(os.path.basename(os.path.normpath(cwd)))
    if i is None:
        raise RuntimeError(f'작업 목록에 없는 실행 폴더: {cwd}')
    w = T0 + i * STAGGER - time.time()
    if w > 0:
        time.sleep(w)
    with open(LOCK, 'a+') as f:
        fcntl.flock(f, fcntl.LOCK_EX)
        try:
            f.seek(0)
            s = f.read().split()
            gap = (float(s[-1]) + GAP - time.time()) if s else 0
            if gap > 0:
                time.sleep(gap)
            f.write(f'{time.time():.3f}\n')
            f.flush()
        finally:
            fcntl.flock(f, fcntl.LOCK_UN)
    ef = open(os.path.join(cwd, 'stderr.txt'), 'w')
    k['stderr'] = ef
    try:
        cp = _real_run(args, *a, **k)
    finally:
        ef.close()
    with open(os.path.join(cwd, RCFILE), 'w') as f:
        f.write(f'{cp.returncode}\n')
    return cp


hw.subprocess.run = _run


def _base(t):
    return re.sub(r'_h\d+$', '', t)


def audit():
    rows = []
    for t, lab, *_r in JOBS:
        d = os.path.join(hw.RUNS, f'{lab}_{t}')
        row = {'target': t, 'condition': lab, 'dir': os.path.relpath(d, HERE) if not SMOKE else d}
        outs = R._data_files(d)
        if len(outs) != 1:
            row.update(ok=False, why=f'.data {len(outs)}개')
            rows.append(row)
            continue
        txt = open(outs[0], encoding='utf-8', errors='ignore').read()
        inp = open(os.path.join(d, 'simulation.input')).read()
        s = re.search(r'Random number seed:\s*(\d+)', txt)
        rcf = os.path.join(d, RCFILE)
        errf = os.path.join(d, 'stderr.txt')
        err = open(errf, errors='ignore').read() if os.path.exists(errf) else None
        row.update(seed=int(s.group(1)) if s else None, finished=rg.finished(outs[0]),
                   returncode=int(open(rcf).read().strip()) if os.path.exists(rcf) else None,
                   blockpockets_in_input=inp.count('BlockPockets'),
                   blocked_line_in_output='Pockets are blocked for this component' in txt,
                   stderr_not_found=(NOT_FOUND in err) if err is not None else None,
                   temperature_line=(re.search(r'External temperature:\s*([0-9.]+)', txt, re.I) or [None, None])[1])
        row['ok'] = bool(row['finished'] and row['returncode'] == 0 and row['blockpockets_in_input'] == 0
                         and not row['blocked_line_in_output'] and row['stderr_not_found'] is False and row['seed'])
        rows.append(row)
    seeds = [r.get('seed') for r in rows]
    return rows, {'n': len(rows), 'n_expected': len(JOBS), 'n_ok': sum(1 for r in rows if r.get('ok')),
                  'seeds_distinct': None not in seeds and len(set(seeds)) == len(seeds)}


def summarize(rows, aud):
    path = hw.RESULT if os.path.exists(hw.RESULT) else hw.RESULT.replace('.json', '.PARTIAL.json')
    res = json.load(open(path, encoding='utf-8')) if os.path.exists(path) else None
    out = {'test': 'Zn(bib)(bdtdc) 실온도 습윤 TSA 작업 용량(RT-WC · 323 K · RH 90 % · 막음 없음)',
           'assign': 'ASSIGN_ZNBDT_REALTEMP_20261108.md §1 · §3', 'wrapper': 'run_humid_wc_v3w_323.py (무수정 import)',
           'runner': os.path.basename(__file__), 'machine': MACHINE, 'made': time.strftime('%F %T'), 'smoke': SMOKE,
           'runner_result': os.path.basename(path), 'complete': (res or {}).get('complete'),
           'stagger_s': STAGGER, 'gap_s': GAP, 'audit_summary': aud, 'audit': rows,
           'note': '기계적 사실뿐 — 판정은 종합자. 평균 ± = ±̄/√n · SD = 씨앗 SD.'}
    if res:
        by = {}
        for r in res['rows']:
            by.setdefault(_base(r['name']), []).append(r)
        s = {}
        for b, rs in by.items():
            e = {'n': len(rs), 'names': [r['name'] for r in rs]}
            for lab in ('tsa', 'vsa'):
                v = [r['working_capacity'][lab] for r in rs if lab in r.get('working_capacity', {})]
                if v:
                    e[f'WC_{lab.upper()}_each'] = [x['value'] for x in v]
                    e[f'WC_{lab.upper()}_mean'] = st.mean(x['value'] for x in v)
                    e[f'WC_{lab.upper()}_mean_err'] = st.mean(x['err'] for x in v) / math.sqrt(len(v))
                    e[f'WC_{lab.upper()}_seed_SD'] = st.stdev([x['value'] for x in v]) if len(v) > 1 else None
            e['loadings'] = {r['name']: r['loadings'] for r in rs}
            s[b] = e
        out['summary'] = s
    tmp = SUMMARY + '.tmp'
    json.dump(out, open(tmp, 'w', encoding='utf-8'), indent=2, ensure_ascii=False)
    os.replace(tmp, SUMMARY)
    return out


def _die(msg, code=1):
    print(f'  !! {msg} — 아무것도 안 돌리고 멈춥니다.', flush=True)
    sys.exit(code)


if __name__ == '__main__':
    print(f'RT-WC Zn(bib)(bdtdc) — 323 K 래퍼 무수정 import · 착수 간격 {STAGGER:.0f} s + {GAP:.0f} s 잠금 · 작업 {len(JOBS)} · 스모크 {SMOKE}', flush=True)
    if not MACHINE:
        _die('HWC_323_MACHINE 이 비어 있습니다')
    bad = [t for t in hw.TARGETS if _base(t) in NEEDS_BLOCK]
    if bad:
        _die(f'막음이 필요한 대상 {bad} — 이 실행기는 막음 삽입이 없습니다')
    nocopy = [t for t in hw.TARGETS if not re.search(r'_h\d+$', t)]
    if nocopy:
        _die(f'바이트 같은 사본(_hN)이 아닌 대상 {nocopy}')
    jobs = R._preflight()             # 파일 관문 · 대상 CIF · 조건 · 자식 대조(사이클 15,000/5,000 · run_one_323) · 다른 조건 .data
    olds = [p for p in (hw.RESULT, hw.RESULT.replace('.json', '.PARTIAL.json'), R.STATUS_LOG) if os.path.exists(p)]
    dirs = [k for k in INDEX if os.path.exists(os.path.join(hw.RUNS, k))]
    if olds or dirs:
        _die(f'이전 결과 {olds} · 실행 폴더 {len(dirs)}개 있음(러너가 cached 로 회수하므로 첫 착수만 받음)')
    print(f'  요약        {SUMMARY}', flush=True)
    print(f'  잠금        {LOCK}', flush=True)
    if os.environ.get('HWC_323_DRYRUN'):
        print(f'\n  DRYRUN — 작업 {len(JOBS)}(대상 {len(hw.TARGETS)} × 조건 3) · 착수 하한 T0 + 15 s × i:', flush=True)
        for i, (t, lab, p, T, ps) in enumerate(JOBS):
            print(f'    {i:>2} +{i * STAGGER:>5.0f} s  {lab:<4} {t:<20} CO2 {p:>7.0f} Pa  {T:.0f} K  H2O {hw.P_H2O:.1f} Pa', flush=True)
        sys.exit(0)
    if SMOKE:
        hw.CYCLES, hw.INIT = 10, 0        # 사전검사 뒤 — 자식은 hw.main 의 fork 때 이 값을 물려받음
        print(f'  스모크 사이클 {hw.CYCLES}+{hw.INIT} · RUNS {hw.RUNS}', flush=True)
    print(flush=True)
    rc = hw.main()
    if rc == 0 and os.path.exists(hw.RESULT):
        rc = R._finalize()
    elif rc == 0:
        print('  !! main 이 0 을 돌려줬는데 결과 파일이 없습니다 — 미완(종료 2)', flush=True)
        rc = 2
    rows, aud = audit()
    out = summarize(rows, aud)
    print(f"감사 {json.dumps(aud, ensure_ascii=False)}", flush=True)
    for r in rows:
        print(f"  {r['condition']:<4} {r['target']:<20} ok {r.get('ok')} · 완주 {r.get('finished')} · rc {r.get('returncode')} · "
              f"막음 줄 {r.get('blockpockets_in_input')} · not-found {r.get('stderr_not_found')} · T {r.get('temperature_line')} · 씨앗 {r.get('seed')}", flush=True)
    for b, e in (out.get('summary') or {}).items():
        print(f"  {b:<16} n {e['n']} · WC_TSA {e.get('WC_TSA_mean')} ± {e.get('WC_TSA_mean_err')} (SD {e.get('WC_TSA_seed_SD')}) · "
              f"WC_VSA {e.get('WC_VSA_mean')} ± {e.get('WC_VSA_mean_err')}", flush=True)
    if aud['n_ok'] != aud['n_expected'] or not aud['seeds_distinct']:
        print('  !! 감사 미통과 — 결과로 쓰지 마십시오(종료 2)', flush=True)
        rc = rc or 2
    sys.exit(rc)
