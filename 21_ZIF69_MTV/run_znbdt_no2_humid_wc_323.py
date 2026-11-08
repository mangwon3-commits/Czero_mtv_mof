"""Zn(bib)(bdtdc) −NO₂ 열린 자리 실온도 습윤 TSA 작업 용량(RT-WC · 물 막음) — 등록 `ASSIGN_ZNBDT_REALTEMP_20261108.md` §1 · §3
(01:3x 예비 배정 · 자료 0건: HKHOME 이 11-08 09:00 까지 RT-WC 착수 글이 없으면 랩탑이 27작업 뒤 −NO₂ 몫을 맡음).

틀: `run_znbdt_humid_wc_323.py`(랩탑 · md5 53677257 · 막음 없는 대상 전용) **사본**. 등록 §3 의 문장
"−NO₂ 는 laptop2 ⑩ 실행기의 E-24f 식 물 막음 삽입(1.30 · 구 4)을 323 K 판에 얹은 사본으로" 대로, 바꾼 것은 아래 넷뿐입니다.
  ① 대상 e24i_no2_open 고정 — 바이트 같은 사본 charged_v3/e24i_no2_open_h{1,2,3}_DDEC6.cif(원본 md5 3a2a53ac 대조 · 없으면 만듦 ·
     laptop2 ⑩ `run_e24i_no2_humid_wc.py`(c2d4673a) 의 prep() 와 같음). 다른 대상이 오면 착수 전에 멈춤.
  ② 막음 — RASPA 호출 직전 실행 폴더 simulation.input 의 **물 성분 절에만** BlockPockets 두 줄 삽입. 삽입 자리 · 문자열 · 파일은
     ⑩ 의 `_inject` 와 같습니다: znbdt_no2_zeo_runs/e24i_no2_open/block1.30/e24i_no2_open_relaxed.block(md5 46b306e3 · 구 4 ·
     298 K −NO₂ E 와 ⑩ 이 쓴 파일). CO₂ 는 1.65 구 0 이라 넣지 않습니다. 삽입 자리가 정확히 한 번이 아니면 RASPA 를 띄우지 않고 예외.
  ③ 감사 — ⑩ 의 E-24f 관문으로 바꿈: 입력 BlockPockets 줄 2 · 물 `Pockets are blocked for this component` · 물 차단 수 = 구 4 × 단위셀 수 ·
     CO₂ 막음 줄 없음 · not-found 0(stderr · 출력) · finished · rc 0 · 씨앗 · 씨앗 전부 고유 · 온도 줄.
  ④ 이름 — 요약 results_znbdt_no2_humid_wc_323_summary_<기기>.json · 잠금 .znbdt323no2_<기기>_start.lock · 스모크 폴더 znbdt323no2_smoke.
값을 만드는 부분(`run_humid_wc_v3w_323.py` 무수정 import → run_one_323 · 조건 ads 323 K/15 kPa · tsa 373 K · vsa 323 K/5 kPa ·
물 11,114.1 Pa · 사이클 5,000+15,000 · 힘장 · 전하 · 2×2×2)과 착수 간격(15 s × i + 2 s 잠금) · 반환코드 · stderr 기록 ·
기존 결과 · 폴더 착수 거부는 틀 그대로입니다. 판정은 종합자 — 요약은 기계적 사실뿐.

env: HWC_323_TARGETS(쉼표 · 필수 · e24i_no2_open_h1~h3 만) · HWC_323_WORKERS · HWC_323_RESULT(v3w_humid_wc_323/ 아래) · HWC_323_MACHINE(필수)
     HWC_323_DRYRUN=1  사전검사 · 작업 목록 · 착수 간격만 찍고 끝
     ZNBDT323_SMOKE=1  사이클 10 · 초기화 0 · 실행 폴더 · 결과를 저장소 밖(~/.mof_chain/znbdt323no2_smoke)으로 — 막음 삽입이 RASPA 에
                       먹는지(차단 수 = 구 4 × 단위셀) · 착수 간격 · 감사를 먼저 봄. 스모크 값은 결과로 쓰지 않습니다.
"""
import fcntl
import hashlib
import json
import math
import os
import re
import shutil
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
BASE_TAG = 'e24i_no2_open'
REPS = tuple(f'{BASE_TAG}_h{k}' for k in (1, 2, 3))
SRC_CIF = os.path.join(HERE, 'charged_v3', f'{BASE_TAG}_DDEC6.cif')
SRC_MD5_PREFIX = '3a2a53ac'
WBLOCK = os.path.join(HERE, 'znbdt_no2_zeo_runs', BASE_TAG, 'block1.30', f'{BASE_TAG}_relaxed.block')
WBLOCK_MD5 = '46b306e39cc368360e8e74d6459ad123'
WKEY = f'{BASE_TAG}_water'
WPAT = 'MoleculeName              water\n            MoleculeDefinition        TraPPE\n'
MACHINE = os.environ.get('HWC_323_MACHINE', '')
SMOKE = bool(os.environ.get('ZNBDT323_SMOKE'))
CHAIN = os.path.expanduser('~/.mof_chain'); os.makedirs(CHAIN, exist_ok=True)
LOCK = os.path.join(CHAIN, f'.znbdt323no2_{MACHINE or "x"}_start.lock')
SUMMARY = os.path.join(HERE, f'results_znbdt_no2_humid_wc_323_summary_{MACHINE or "x"}.json')
RCFILE = 'znbdt323_returncode.txt'
if SMOKE:
    SM = os.path.join(CHAIN, 'znbdt323no2_smoke'); os.makedirs(SM, exist_ok=True)
    hw.RUNS = os.path.join(SM, 'runs')
    hw.RESULT = os.path.join(SM, 'smoke_result.json')
    R.STATUS_LOG = hw.RESULT + '.status.jsonl'
    SUMMARY = os.path.join(SM, 'smoke_summary.json')
    LOCK = os.path.join(SM, '.start.lock')
JOBS = [(t, lab, p, T, ps) for t in hw.TARGETS for lab, p, T, ps in hw.CONDITIONS]   # hw.main 과 같은 순서
INDEX = {f'{lab}_{t}': i for i, (t, lab, *_r) in enumerate(JOBS)}
T0 = time.time()                      # fork 로 워커에 물려짐


def md5(p):
    return hashlib.md5(open(p, 'rb').read()).hexdigest()


def nsph():
    return int(open(WBLOCK).read().split()[0])


def _inject(cwd):
    """물 성분 절에만 BlockPockets 두 줄(⑩ `_inject` 와 같은 자리 · 같은 문자열). 자리가 한 번이 아니면 RASPA 를 안 띄움."""
    p = os.path.join(cwd, 'simulation.input')
    txt = open(p).read()
    if 'BlockPockets' in txt:
        raise RuntimeError(f'입력에 이미 BlockPockets 가 있음 — RASPA 안 띄움 ({cwd})')
    if txt.count(WPAT) != 1:
        raise RuntimeError(f'막음 삽입 자리 water 가 {txt.count(WPAT)}번 — RASPA 안 띄움 ({cwd})')
    txt = txt.replace(WPAT, WPAT + f'            BlockPockets              yes\n            BlockPocketsFileName      {WKEY}\n')
    shutil.copy(WBLOCK, os.path.join(cwd, f'{WKEY}.block'))
    open(p, 'w').write(txt)


_real_run = hw.subprocess.run


def _run(args, *a, **k):
    """simulate 호출만: 막음 삽입(②) → 착수 간격 → stderr · 반환코드 기록. 다른 호출은 그대로 통과."""
    cwd = k.get('cwd')
    if not (cwd and args and args[0] == rg.SIMULATE):
        return _real_run(args, *a, **k)
    i = INDEX.get(os.path.basename(os.path.normpath(cwd)))
    if i is None:
        raise RuntimeError(f'작업 목록에 없는 실행 폴더: {cwd}')
    _inject(cwd)
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


def prep():
    """바이트 같은 사본 셋(원본 md5 대조) · 막음 파일 md5 — ⑩ prep() 와 같음."""
    m = md5(SRC_CIF)
    if not m.startswith(SRC_MD5_PREFIX):
        _die(f'원본 전하 CIF md5 {m[:8]} ≠ 등록 {SRC_MD5_PREFIX}')
    if md5(WBLOCK) != WBLOCK_MD5:
        _die(f'물 막음 파일 md5 {md5(WBLOCK)} ≠ {WBLOCK_MD5}')
    copies = {}
    for t in hw.TARGETS:
        dst = os.path.join(hw.CHARGED, f'{t}_DDEC6.cif')
        if not os.path.exists(dst):
            shutil.copyfile(SRC_CIF, dst)
        if md5(dst) != m:
            _die(f'사본 {dst} 가 원본과 바이트가 다름')
        copies[t] = os.path.relpath(dst, HERE)
    return {'src': os.path.relpath(SRC_CIF, HERE), 'src_md5': m, 'copies': copies,
            'water_block': {'file': os.path.relpath(WBLOCK, HERE), 'md5': WBLOCK_MD5, 'n_spheres': nsph()}, 'co2_block': None}


def block_audit(txt):
    """성분별 막음 표지(⑩ block_audit 와 같음)."""
    cur, out = None, {}
    for ln in txt.splitlines():
        m = re.match(r'Component (\d+) \[(\w+)\] \(Adsorbate molecule\)', ln)
        if m:
            cur = m.group(2)
            out.setdefault(cur, {'n_blocked': None, 'blocked_line': False, 'block_file': None})
            continue
        if cur is None:
            continue
        c = out[cur]
        m = re.search(r'Number of pockets blocked in a unitcell:\s*(\d+)', ln)
        if m and c['n_blocked'] is None:
            c['n_blocked'] = int(m.group(1))
        if 'Pockets are blocked for this component' in ln:
            c['blocked_line'] = True
        m = re.search(r'Block-pockets Filename:\s*(\S+)', ln)
        if m and c['block_file'] is None:
            c['block_file'] = m.group(1)
    return out


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
        uc = [int(x) for x in re.search(r'UnitCells\s+(\d+)\s+(\d+)\s+(\d+)', inp).groups()]
        ncell = uc[0] * uc[1] * uc[2]
        s = re.search(r'Random number seed:\s*(\d+)', txt)
        rcf = os.path.join(d, RCFILE)
        errf = os.path.join(d, 'stderr.txt')
        err = open(errf, errors='ignore').read() if os.path.exists(errf) else None
        ba = block_audit(txt)
        row.update(unit_cells=uc, seed=int(s.group(1)) if s else None, finished=rg.finished(outs[0]),
                   returncode=int(open(rcf).read().strip()) if os.path.exists(rcf) else None, block=ba,
                   blockpockets_in_input=inp.count('BlockPockets'), n_expected_water=nsph() * ncell,
                   stderr_not_found=(NOT_FOUND in err) if err is not None else None, not_found_in_output=NOT_FOUND in txt,
                   temperature_line=(re.search(r'External temperature:\s*([0-9.]+)', txt, re.I) or [None, None])[1])
        w, c = ba.get('water', {}), ba.get('CO2', {})
        row['ok'] = bool(row['blockpockets_in_input'] == 2 and w.get('blocked_line') and w.get('n_blocked') == row['n_expected_water']
                         and not c.get('blocked_line') and row['finished'] and row['returncode'] == 0
                         and row['stderr_not_found'] is False and not row['not_found_in_output'] and row['seed'])
        rows.append(row)
    seeds = [r.get('seed') for r in rows]
    return rows, {'n': len(rows), 'n_expected': len(JOBS), 'n_ok': sum(1 for r in rows if r.get('ok')),
                  'seeds_distinct': None not in seeds and len(set(seeds)) == len(seeds)}


def summarize(rows, aud, info):
    path = hw.RESULT if os.path.exists(hw.RESULT) else hw.RESULT.replace('.json', '.PARTIAL.json')
    res = json.load(open(path, encoding='utf-8')) if os.path.exists(path) else None
    out = {'test': 'Zn(bib)(bdtdc) −NO₂ 열린 자리 실온도 습윤 TSA 작업 용량(RT-WC · 323 K · RH 90 % · 물 막음 1.30 구 4)',
           'assign': 'ASSIGN_ZNBDT_REALTEMP_20261108.md §1 · §3(01:3x 예비 배정)', 'wrapper': 'run_humid_wc_v3w_323.py (무수정 import)',
           'ported_from': 'run_znbdt_humid_wc_323.py (53677257) + run_e24i_no2_humid_wc.py (c2d4673a) 의 물 막음 삽입 · 감사',
           'runner': os.path.basename(__file__), 'machine': MACHINE, 'made': time.strftime('%F %T'), 'smoke': SMOKE,
           'runner_result': os.path.basename(path), 'complete': (res or {}).get('complete'),
           'stagger_s': STAGGER, 'gap_s': GAP, 'inputs': info, 'blocking': {'water': 'block1.30 구 4', 'CO2': '없음(1.65 구 0)'},
           'audit_summary': aud, 'audit': rows,
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
    print(f'RT-WC Zn(bib)(bdtdc) −NO₂(물 막음) — 323 K 래퍼 무수정 import · 착수 간격 {STAGGER:.0f} s + {GAP:.0f} s 잠금 · '
          f'작업 {len(JOBS)} · 스모크 {SMOKE}', flush=True)
    if not MACHINE:
        _die('HWC_323_MACHINE 이 비어 있습니다')
    bad = [t for t in hw.TARGETS if t not in REPS]
    if bad or not hw.TARGETS:
        _die(f'이 실행기는 {list(REPS)} 전용입니다(받은 대상 {hw.TARGETS})')
    info = prep()                     # 사본이 있어야 래퍼 사전검사가 대상 CIF 를 찾음
    print(f"  막음        물 {info['water_block']['file']} (md5 {WBLOCK_MD5[:8]} · 구 {info['water_block']['n_spheres']}) · CO₂ 없음", flush=True)
    print(f"  사본        원본 md5 {info['src_md5'][:8]} · {len(info['copies'])}개 바이트 같음", flush=True)
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
    out = summarize(rows, aud, info)
    print(f"감사 {json.dumps(aud, ensure_ascii=False)}", flush=True)
    for r in rows:
        w = (r.get('block') or {}).get('water', {})
        print(f"  {r['condition']:<4} {r['target']:<20} ok {r.get('ok')} · 완주 {r.get('finished')} · rc {r.get('returncode')} · "
              f"입력 막음 줄 {r.get('blockpockets_in_input')} · 물 차단 {w.get('n_blocked')}/{r.get('n_expected_water')} · "
              f"CO₂ 막음 {((r.get('block') or {}).get('CO2') or {}).get('blocked_line')} · not-found {r.get('stderr_not_found')} · "
              f"T {r.get('temperature_line')} · 씨앗 {r.get('seed')}", flush=True)
    for b, e in (out.get('summary') or {}).items():
        print(f"  {b:<16} n {e['n']} · WC_TSA {e.get('WC_TSA_mean')} ± {e.get('WC_TSA_mean_err')} (SD {e.get('WC_TSA_seed_SD')}) · "
              f"WC_VSA {e.get('WC_VSA_mean')} ± {e.get('WC_VSA_mean_err')}", flush=True)
    if aud['n_ok'] != aud['n_expected'] or not aud['seeds_distinct']:
        print('  !! 감사 미통과 — 결과로 쓰지 마십시오(종료 2)', flush=True)
        rc = rc or 2
    sys.exit(rc)
