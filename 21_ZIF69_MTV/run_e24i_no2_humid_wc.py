# -*- coding: utf-8 -*-
"""ZNBDT −NO₂ 열린 자리 습윤 TSA 작업 용량 3씨앗(물 막음) — laptop2 ⑩. 등록 `ASSIGN_ZNBDT_LADDER_20261108.md` §3(자료 0건).

틀: `run_e24i_humid_wc.py`(md5 953d0fe4 · E-24i 습윤 WC · 차단 없음) **사본** — 바꾼 것은 등록 §3 의 막음과 그에 딸린 감사뿐입니다.
  ① 대상 e24i_no2_open 고정 · 바이트 같은 사본 charged_v3/e24i_no2_open_h{1,2,3}_DDEC6.cif(원본 md5 3a2a53ac 대조 · 없으면 만듦).
  ② 막음 — RASPA 호출 직전 실행 폴더 simulation.input 의 **물 성분 절에만** BlockPockets 줄 삽입(`run_e24f_humid_wc.py` E-24f 의 `_inject` 와 같은 자리 ·
     같은 문자열). 파일 = znbdt_no2_zeo_runs/e24i_no2_open/block1.30/e24i_no2_open_relaxed.block(md5 46b306e3 · 구 4 · 298 K −NO₂ E 와 같은 파일).
     CO₂ 는 1.65 구 0 이라 막음 줄을 넣지 않습니다(등록 §3). 삽입 자리가 정확히 한 번이 아니면 RASPA 를 띄우지 않고 예외.
  ③ 감사 — E-24f 관문: 물 `Pockets are blocked for this component` · 물 차단 수 = 구 4 × 단위셀 수 · CO₂ 막음 줄 없음 · 입력의 BlockPockets 줄 2
     · not-found 0 · finished · 반환코드 0 · 씨앗 9 고유 · 러너 상태(결과 JSON 의 행).
  ④ env 기본값: HWC_V3W_TARGETS = 사본 셋 · HWC_V3W_WORKERS 6 · HWC_V3W_RESULT humid_working_capacity_w2_e24i_no2_open_laptop2.json ·
     요약 results_e24i_e24i_no2_open_humid_summary_laptop2.json(등록 §3 의 이름에서 기기만 laptop2).
  ⑤ E24I_DRY=1 — RASPA 를 띄우지 않고(반환 0 흉내) 고친 입력만 저장소 밖(~/.mof_chain/e24i_no2_hwc_dry)에 씀 · 사이클 10.
자(run_humid_wc_v3w.py → run_humid_wc.run_one 무수정 import · RH90 · ads 298 K/15 kPa · TSA 373 K · VSA 298 K/5 kPa · 5,000+15,000 · 물 5자리 · 전하 ON)
· 착수 간격(15 s + 2 s 잠금)은 틀 그대로입니다. 판정은 종합자.
"""
import fcntl
import glob
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
BASE_TAG = 'e24i_no2_open'
MACHINE = 'laptop2'
DRY = bool(os.environ.get('E24I_DRY'))
CHAIN = os.path.expanduser('~/.mof_chain'); os.makedirs(CHAIN, exist_ok=True)
REPS = [f'{BASE_TAG}_h{k}' for k in (1, 2, 3)]
os.environ.setdefault('HWC_V3W_TARGETS', ','.join(REPS))
os.environ.setdefault('HWC_V3W_WORKERS', '6')
os.environ.setdefault('HWC_V3W_RESULT', f'humid_working_capacity_w2_{BASE_TAG}_{MACHINE}.json')
import ff_gate                   # noqa: E402
import run_humid_wc_v3w as V     # noqa: E402  env(HWC_V3W_*)로 hw 전역을 정함
import run_aryl_gcmc as rg       # noqa: E402
from ase.io import read          # noqa: E402
hw = V.hw

SRC_CIF = os.path.join(HERE, 'charged_v3', f'{BASE_TAG}_DDEC6.cif')
SRC_MD5_PREFIX = '3a2a53ac'
WBLOCK = os.path.join(HERE, 'znbdt_no2_zeo_runs', BASE_TAG, 'block1.30', f'{BASE_TAG}_relaxed.block')
WBLOCK_MD5 = '46b306e39cc368360e8e74d6459ad123'
WKEY = f'{BASE_TAG}_water'
STAGGER = 15.0
NOT_FOUND = "'Blocking-pocket' file not found"
LOCK = os.path.join(CHAIN, f'.{BASE_TAG}_hwc_start.lock')
SUMMARY = os.path.join(HERE, f'results_e24i_{BASE_TAG}_humid_summary_{MACHINE}.json')
if DRY:
    hw.CYCLES, hw.INIT = 10, 0
    hw.RUNS = os.path.join(CHAIN, 'e24i_no2_hwc_dry', 'runs')
    hw.RESULT = os.path.join(CHAIN, 'e24i_no2_hwc_dry', 'result.json')
    SUMMARY = os.path.join(CHAIN, 'e24i_no2_hwc_dry', 'summary.json')
    os.makedirs(os.path.dirname(hw.RESULT), exist_ok=True)
JOBS = [(t, lab, p, T, ps) for t in hw.TARGETS for lab, p, T, ps in hw.CONDITIONS]   # hw.main 과 같은 순서
T0 = time.time()                 # fork 로 워커에 물려짐


def md5(p):
    return hashlib.md5(open(p, 'rb').read()).hexdigest()


def nsph():
    return int(open(WBLOCK).read().split()[0])


def _inject(cwd):
    p = os.path.join(cwd, 'simulation.input')
    txt = open(p).read()
    if 'BlockPockets' in txt:
        raise RuntimeError(f'입력에 이미 BlockPockets 가 있음 — RASPA 안 띄움 ({cwd})')
    pat = 'MoleculeName              water\n            MoleculeDefinition        TraPPE\n'
    if txt.count(pat) != 1:
        raise RuntimeError(f'막음 삽입 자리 water 가 {txt.count(pat)}번 — RASPA 안 띄움 ({cwd})')
    txt = txt.replace(pat, pat + f'            BlockPockets              yes\n            BlockPocketsFileName      {WKEY}\n')
    shutil.copy(WBLOCK, os.path.join(cwd, f'{WKEY}.block'))
    open(p, 'w').write(txt)


_real_run = hw.subprocess.run


def _run(args, *a, **k):
    cwd = k.get('cwd')
    if cwd and args and args[0] == rg.SIMULATE:
        _inject(cwd)
        if DRY:
            with open(os.path.join(cwd, 'e24g_returncode.txt'), 'w') as f:
                f.write('dry\n')
            return hw.subprocess.CompletedProcess(args, 0)
        ef = open(os.path.join(cwd, 'stderr.txt'), 'w')
        k['stderr'] = ef
        try:
            cp = _real_run(args, *a, **k)
        finally:
            ef.close()
        with open(os.path.join(cwd, 'e24g_returncode.txt'), 'w') as f:
            f.write(f'{cp.returncode}\n')
        return cp
    return _real_run(args, *a, **k)


hw.subprocess.run = _run          # 러너의 subprocess.run(RASPA) 호출만 바뀜
_orig = hw.run_one


def staggered(job):
    i = JOBS.index(job)
    w = T0 + i * STAGGER - time.time()
    if w > 0:
        time.sleep(w)
    with open(LOCK, 'a+') as f:
        fcntl.flock(f, fcntl.LOCK_EX)
        try:
            f.seek(0)
            s = f.read().split()
            gap = (float(s[-1]) + 2.0 - time.time()) if s else 0
            if gap > 0:
                time.sleep(gap)
            f.write(f'{time.time():.3f}\n')
            f.flush()
        finally:
            fcntl.flock(f, fcntl.LOCK_UN)
    return _orig(job)


hw.run_one = staggered


def block_audit(txt):
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


def prep():
    """바이트 같은 사본 셋(원본 md5 대조) · 막음 파일 md5."""
    m = md5(SRC_CIF)
    if not m.startswith(SRC_MD5_PREFIX):
        raise SystemExit(f'  !! 원본 전하 CIF md5 {m[:8]} ≠ 등록 {SRC_MD5_PREFIX} — 착수 안 함')
    if md5(WBLOCK) != WBLOCK_MD5:
        raise SystemExit(f'  !! 물 막음 파일 md5 {md5(WBLOCK)} ≠ {WBLOCK_MD5} — 착수 안 함')
    copies = {}
    for t in hw.TARGETS:
        dst = os.path.join(hw.CHARGED, f'{t}_DDEC6.cif')
        if not os.path.exists(dst):
            shutil.copyfile(SRC_CIF, dst)
        if md5(dst) != m:
            raise SystemExit(f'  !! 사본 {dst} 가 원본과 바이트가 다름 — 착수 안 함')
        copies[t] = os.path.relpath(dst, HERE)
    return {'src': os.path.relpath(SRC_CIF, HERE), 'src_md5': m, 'copies': copies,
            'water_block': {'file': os.path.relpath(WBLOCK, HERE), 'md5': WBLOCK_MD5, 'n_spheres': nsph()}, 'co2_block': None}


def audit():
    rows = []
    for t in hw.TARGETS:
        for lab, *_ in hw.CONDITIONS:
            d = os.path.join(hw.RUNS, f'{lab}_{t}')
            row = {'target': t, 'condition': lab, 'dir': d}
            outs = glob.glob(os.path.join(d, 'Output', 'System_0', '*.data'))
            if len(outs) != 1:
                row.update(ok=False, why=f'.data {len(outs)}개')
                rows.append(row)
                continue
            txt = open(outs[0], encoding='utf-8', errors='ignore').read()
            inp = open(os.path.join(d, 'simulation.input')).read()
            uc = [int(x) for x in re.search(r'UnitCells\s+(\d+)\s+(\d+)\s+(\d+)', inp).groups()]
            ncell = uc[0] * uc[1] * uc[2]
            s = re.search(r'Random number seed:\s*(\d+)', txt)
            rcf = os.path.join(d, 'e24g_returncode.txt')
            ba = block_audit(txt)
            err = open(os.path.join(d, 'stderr.txt'), errors='ignore').read() if os.path.exists(os.path.join(d, 'stderr.txt')) else None
            row.update(unit_cells=uc, seed=int(s.group(1)) if s else None, finished=rg.finished(outs[0]),
                       returncode=int(open(rcf).read().strip()) if os.path.exists(rcf) else None, block=ba,
                       blockpockets_in_input=inp.count('BlockPockets'), n_expected_water=nsph() * ncell,
                       stderr_not_found=(NOT_FOUND in err) if err is not None else None, not_found_in_output=NOT_FOUND in txt)
            w, c = ba.get('water', {}), ba.get('CO2', {})
            row['ok'] = bool(row['blockpockets_in_input'] == 2 and w.get('blocked_line') and w.get('n_blocked') == row['n_expected_water']
                             and not c.get('blocked_line') and row['finished'] and row['returncode'] == 0
                             and row['stderr_not_found'] is False and not row['not_found_in_output'] and row['seed'])
            rows.append(row)
    seeds = [r.get('seed') for r in rows]
    return rows, {'n': len(rows), 'n_ok': sum(1 for r in rows if r['ok']), 'seeds_distinct': None not in seeds and len(set(seeds)) == len(seeds)}


def summarize(rows, aud, info):
    res = json.load(open(hw.RESULT, encoding='utf-8')) if os.path.exists(hw.RESULT) else None
    out = {'test': f'ZNBDT 습윤 TSA 작업 용량(물 막음 1.30 구 4) — {BASE_TAG}', 'assign': 'ASSIGN_ZNBDT_LADDER_20261108.md §3 (laptop2 ⑩)',
           'ported_from': 'run_e24i_humid_wc.py (953d0fe4) + run_e24f_humid_wc.py 의 물 막음 삽입',
           'machine': MACHINE, 'made': time.strftime('%F %T'), 'dry': DRY, 'runner_result': hw.RESULT,
           'inputs': info, 'blocking': {'water': 'block1.30 구 4', 'CO2': '없음(1.65 구 0)'},
           'audit_summary': aud, 'audit': rows, 'note': '기계적 사실뿐 — 판정은 종합자. 평균 ± = ±̄/√n · SD 병기.'}
    if res:
        wc = {r['name']: r['working_capacity'] for r in res['rows']}
        s = {}
        for key in ('tsa', 'vsa'):
            xs = [wc[t][key] for t in hw.TARGETS if key in wc.get(t, {})]
            if xs:
                v = [x['value'] for x in xs]
                s[f'WC_{key.upper()}_each'] = v
                s[f'WC_{key.upper()}_mean'] = st.mean(v)
                s[f'WC_{key.upper()}_mean_err'] = st.mean(x['err'] for x in xs) / math.sqrt(len(xs))
                s[f'WC_{key.upper()}_SD'] = st.stdev(v) if len(v) > 1 else None
        s['loadings'] = {r['name']: r['loadings'] for r in res['rows']}
        out['summary'] = s
    tmp = SUMMARY + '.tmp'
    json.dump(out, open(tmp, 'w', encoding='utf-8'), indent=2, ensure_ascii=False)
    os.replace(tmp, SUMMARY)
    return out


if __name__ == '__main__':
    ok, fm = ff_gate.md5_gate()
    print(f"  파일 관문 md5 {fm} {'일치' if ok else '불일치 — 중단'}", flush=True)
    if not ok:
        sys.exit(3)
    print(f"ZNBDT −NO₂ 습윤 작업 용량(물 막음) — 착수 간격 {STAGGER:.0f} s(+ 2 s 잠금) · 작업 {len(JOBS)} · 드라이 {DRY} · "
          f"사이클 {hw.CYCLES}+{hw.INIT}", flush=True)
    for k in ('CHARGED', 'RUNS', 'RESULT', 'TARGETS', 'MAX_WORKERS'):
        print(f'  {k:12s} {getattr(hw, k)}', flush=True)
    if os.path.exists(hw.RESULT) or any(os.path.exists(os.path.join(hw.RUNS, f'{lab}_{t}')) for t in hw.TARGETS for lab, *_ in hw.CONDITIONS):
        print('  !! 이전 결과 · 실행 폴더 있음 — 중단(러너가 cached 로 재사용하므로)', flush=True)
        sys.exit(1)
    info = prep()
    rc = hw.main()
    rows, aud = audit()
    out = summarize(rows, aud, info)
    print(f"감사 {json.dumps(aud, ensure_ascii=False)}", flush=True)
    for r in rows:
        print(f"  {r['condition']:<4} {r['target']:<20} ok {r['ok']} · 입력 막음 줄 {r.get('blockpockets_in_input')} · 물 차단 {r.get('block', {}).get('water', {}).get('n_blocked')}"
              f"/{r.get('n_expected_water')} · 완주 {r.get('finished')} · rc {r.get('returncode')} · not-found {r.get('stderr_not_found')} · 씨앗 {r.get('seed')}", flush=True)
    print(f"요약 저장 {SUMMARY} · {json.dumps({k: v for k, v in out.get('summary', {}).items() if k != 'loadings'}, ensure_ascii=False)[:900]}", flush=True)
    sys.exit(rc or 0)
