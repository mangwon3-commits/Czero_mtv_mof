# -*- coding: utf-8 -*-
"""MAGI-005 E-24f (Junseok 17차) — 4,8-(C₂H₅)₂ 습윤 TSA 작업 용량(막음). 등록 ASSIGN_MAGI5B §Junseok 17차 + laptop2 13차(d3006da3, 자료 0건).

자: E-25 · E-26 과 같음 — run_humid_wc_v3w.py(→ run_humid_wc.run_one) 무수정 import(RH90 · ads 298 K/15 kPa · TSA 373 K · VSA 298 K/5 kPa ·
    5,000+15,000 · 물 5자리 · 전하 ON). 대상 = 바이트 같은 사본 e24c_c2h5_100_h{1,2,3}(3씨앗) · env HWC_V3W_TARGETS · HWC_V3W_WORKERS · HWC_V3W_RESULT.
래퍼에서만 바꾸는 것:
  ① 착수 시각 — 작업 i 는 T0 + 15 s × i 이전에 시작 안 함(E-25 래퍼와 같음) + 착수 사이 2 s 이상(잠금 — 풀 뒷작업이 같은 초에 떠 씨앗이 같아지는 것 막음).
  ② 막음 — RASPA 호출 직전(hw.subprocess.run 을 감쌈) 실행 폴더의 simulation.input 두 성분 절(MoleculeDefinition 줄 다음)에 BlockPockets 줄 삽입:
     CO₂ = E-24c ① block1.65 · 물 = E-24e block1.30. 삽입 자리가 성분마다 정확히 한 번이 아니면 RASPA 를 띄우지 않고 예외.
  ③ 반환코드 기록(e24f_returncode.txt) · stderr 를 파일로(러너는 DEVNULL — 'Blocking-pocket' not found 를 보려고).
관문(끝에서 작업마다): 성분마다 blocked 줄 · N = 구 수 × 단위셀 수 · not-found 0 · finished · 반환코드 0 · 씨앗 고유 · 러너 상태 ok.
결과: v3w_humid_wc/$HWC_V3W_RESULT(러너 그대로) + 요약 results_e24f_c2h5_summary_junseok.json(감사 · 3씨앗 평균 WC · ±̄/√3 · CH₃ 대비 단위 ·
      셀당 환산). CH₃ 기준은 원자료(v3w_humid_wc/humid_working_capacity_w2_e24ch3_laptop.json)에서 읽음. 판정은 종합자.
E24F_SMOKE=1: 사이클 10 · 초기화 0 · 대상 h1 · 실행 폴더 · 결과를 저장소 밖(~/.junseok_chain)으로 — 막음 삽입이 먹는지 먼저 봄.
"""
import fcntl
import glob
import json
import math
import os
import re
import shutil
import statistics as st
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import ff_gate                   # noqa: E402
import run_humid_wc_v3w as V     # noqa: E402  env(HWC_V3W_*)로 hw 전역을 정함
import run_aryl_gcmc as rg       # noqa: E402
from ase.io import read          # noqa: E402
hw = V.hw

BASE_TAG = 'e24c_c2h5_100'
BLOCK = {'CO2': os.path.join(HERE, 'e24c_zeo_runs', BASE_TAG, 'block1.65', BASE_TAG + '_relaxed.block'),
         'water': os.path.join(HERE, 'e24e_zeo', 'block1.30', BASE_TAG + '_relaxed.block')}
KEY = {'CO2': 'co2', 'water': 'water'}
STAGGER = 15.0
NOT_FOUND = "'Blocking-pocket' file not found"
CHAIN = '/home/mangwon/.junseok_chain'
LOCK = os.path.join(CHAIN, '.e24f_start.lock')
SMOKE = bool(os.environ.get('E24F_SMOKE'))
SUMMARY = os.path.join(HERE, 'results_e24f_c2h5_summary_junseok.json')
CH3_REF = os.path.join(HERE, 'v3w_humid_wc', 'humid_working_capacity_w2_e24ch3_laptop.json')
CH3_CIF = os.path.join(HERE, 'charged_v3', 'e24_ch3_100_DDEC6.cif')
if SMOKE:
    hw.CYCLES, hw.INIT = 10, 0
    hw.TARGETS = [BASE_TAG + '_h1']
    hw.RUNS = os.path.join(CHAIN, 'e24f_smoke_runs')
    hw.RESULT = os.path.join(CHAIN, 'e24f_smoke_result.json')
    SUMMARY = os.path.join(CHAIN, 'e24f_smoke_summary.json')
JOBS = [(t, lab, p, T, ps) for t in hw.TARGETS for lab, p, T, ps in hw.CONDITIONS]   # hw.main 과 같은 순서
T0 = time.time()                 # fork 로 워커에 물려짐


def nsph(comp):
    return int(open(BLOCK[comp]).read().split()[0])


def _inject(cwd):
    p = os.path.join(cwd, 'simulation.input')
    txt = open(p).read()
    if 'BlockPockets' in txt:
        return
    for comp in ('CO2', 'water'):
        pat = f'MoleculeName              {comp}\n            MoleculeDefinition        TraPPE\n'
        if txt.count(pat) != 1:
            raise RuntimeError(f'막음 삽입 자리 {comp} 가 {txt.count(pat)}번 — RASPA 안 띄움 ({cwd})')
        txt = txt.replace(pat, pat + f'            BlockPockets              yes\n            BlockPocketsFileName      {BASE_TAG}_{KEY[comp]}\n')
        shutil.copy(BLOCK[comp], os.path.join(cwd, f'{BASE_TAG}_{KEY[comp]}.block'))
    open(p, 'w').write(txt)


_real_run = hw.subprocess.run


def _run(args, *a, **k):
    cwd = k.get('cwd')
    if cwd and args and args[0] == rg.SIMULATE:
        _inject(cwd)
        ef = open(os.path.join(cwd, 'stderr.txt'), 'w')
        k['stderr'] = ef
        try:
            cp = _real_run(args, *a, **k)
        finally:
            ef.close()
        with open(os.path.join(cwd, 'e24f_returncode.txt'), 'w') as f:
            f.write(f'{cp.returncode}\n')
        return cp
    return _real_run(args, *a, **k)


hw.subprocess.run = _run          # 러너의 subprocess.run(RASPA) 호출만 바뀜 — 다른 호출(pgrep 등)은 그대로 통과
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
            rcf = os.path.join(d, 'e24f_returncode.txt')
            ba = block_audit(txt)
            err = open(os.path.join(d, 'stderr.txt'), errors='ignore').read() if os.path.exists(os.path.join(d, 'stderr.txt')) else None
            row.update(unit_cells=uc, seed=int(s.group(1)) if s else None, finished=rg.finished(outs[0]),
                       returncode=int(open(rcf).read().strip()) if os.path.exists(rcf) else None, block=ba,
                       n_expected={c: nsph(c) * ncell for c in ('CO2', 'water')}, stderr_not_found=(NOT_FOUND in err) if err is not None else None)
            blk = all(ba.get(c, {}).get('blocked_line') and ba.get(c, {}).get('n_blocked') == row['n_expected'][c] for c in ('CO2', 'water'))
            row['ok'] = bool(blk and row['finished'] and row['returncode'] == 0 and row['stderr_not_found'] is False and row['seed'])
            rows.append(row)
    seeds = [r.get('seed') for r in rows]
    return rows, {'n': len(rows), 'n_ok': sum(1 for r in rows if r['ok']), 'seeds_distinct': None not in seeds and len(set(seeds)) == len(seeds)}


def cell_mass(cif):
    return float(sum(read(cif).get_masses()))       # g/mol per 단위셀


def summarize(rows, aud):
    res = json.load(open(hw.RESULT, encoding='utf-8')) if os.path.exists(hw.RESULT) else None
    out = {'test': 'MAGI-005 E-24f — C₂H₅ 습윤 TSA 작업 용량(막음)', 'assign': 'ASSIGN_MAGI5B_20260925.md §Junseok 17차 + laptop2 13차',
           'machine': 'junseok', 'made': time.strftime('%F %T'), 'smoke': SMOKE, 'runner_result': hw.RESULT,
           'blocking': {c: {'file': os.path.relpath(BLOCK[c], HERE), 'n_spheres': nsph(c)} for c in ('CO2', 'water')},
           'audit_summary': aud, 'audit': rows, 'note': '기계적 사실뿐 — 판정은 종합자. 평균 ± = ±̄/√n, 단위 = d/√(±₁²+±₂²).'}
    if res:
        wc = {r['name']: r['working_capacity'] for r in res['rows']}
        tsa = [wc[t]['tsa'] for t in hw.TARGETS if 'tsa' in wc.get(t, {})]
        vsa = [wc[t]['vsa'] for t in hw.TARGETS if 'vsa' in wc.get(t, {})]
        s = {}
        if tsa:
            s['WC_TSA_each'] = [x['value'] for x in tsa]
            s['WC_TSA_mean'] = st.mean(x['value'] for x in tsa)
            s['WC_TSA_mean_err'] = st.mean(x['err'] for x in tsa) / math.sqrt(len(tsa))
        if vsa:
            s['WC_VSA_each'] = [x['value'] for x in vsa]
            s['WC_VSA_mean'] = st.mean(x['value'] for x in vsa)
            s['WC_VSA_mean_err'] = st.mean(x['err'] for x in vsa) / math.sqrt(len(vsa))
        s['loadings'] = {r['name']: r['loadings'] for r in res['rows']}
        if os.path.exists(CH3_REF) and tsa:
            ch3 = json.load(open(CH3_REF, encoding='utf-8'))['rows']
            ct = [r['working_capacity']['tsa'] for r in ch3]
            cm, ce = st.mean(x['value'] for x in ct), st.mean(x['err'] for x in ct) / math.sqrt(len(ct))
            s['CH3_reference'] = {'file': os.path.relpath(CH3_REF, HERE), 'WC_TSA_each': [x['value'] for x in ct], 'mean': cm, 'mean_err': ce}
            s['units_WC_TSA_vs_CH3'] = (s['WC_TSA_mean'] - cm) / math.hypot(s['WC_TSA_mean_err'], ce)
            s['(1)_more_than_1.5_below_CH3'] = s['units_WC_TSA_vs_CH3'] < -1.5
            mc2, mch3 = cell_mass(os.path.join(HERE, 'charged_v3', BASE_TAG + '_DDEC6.cif')), cell_mass(CH3_CIF)
            s['per_cell_descriptive'] = {'cell_mass_g_per_mol': {'C2H5': mc2, 'CH3': mch3},
                                         'WC_TSA_molecules_per_cell': {'C2H5': s['WC_TSA_mean'] * mc2 / 1000.0, 'CH3': cm * mch3 / 1000.0}}
        out['summary'] = s
    tmp = SUMMARY + '.tmp'
    json.dump(out, open(tmp, 'w', encoding='utf-8'), indent=2, ensure_ascii=False)
    os.replace(tmp, SUMMARY)
    return out


if __name__ == '__main__':
    ok, md5 = ff_gate.md5_gate()
    print(f"  파일 관문 md5 {md5} {'일치' if ok else '불일치 — 중단'}", flush=True)
    if not ok:
        sys.exit(3)
    for c in ('CO2', 'water'):
        if not os.path.exists(BLOCK[c]):
            print(f'  !! 막음 파일 없음 {BLOCK[c]}', flush=True)
            sys.exit(2)
    print(f"E-24f 습윤 작업 용량(C₂H₅ 막음) — 착수 간격 {STAGGER:.0f} s(+ 2 s 잠금) · 작업 {len(JOBS)} · 막음 CO₂ {nsph('CO2')} 구 · 물 {nsph('water')} 구 · "
          f"스모크 {SMOKE} · 사이클 {hw.CYCLES}+{hw.INIT}", flush=True)
    for k in ('CHARGED', 'RUNS', 'RESULT', 'TARGETS', 'MAX_WORKERS'):
        print(f'  {k:12s} {getattr(hw, k)}', flush=True)
    missing = [t for t in hw.TARGETS if not os.path.exists(os.path.join(hw.CHARGED, t + '_DDEC6.cif'))]
    if missing:
        print(f'  !! charged_v3 에 없음: {missing}', flush=True)
        sys.exit(1)
    if os.path.exists(hw.RESULT) or any(os.path.exists(os.path.join(hw.RUNS, f'{lab}_{t}')) for t in hw.TARGETS for lab, *_ in hw.CONDITIONS):
        print('  !! 이전 결과 · 실행 폴더 있음 — 중단(러너가 cached 로 재사용하므로)', flush=True)
        sys.exit(1)
    rc = hw.main()
    rows, aud = audit()
    out = summarize(rows, aud)
    print(f"감사 {json.dumps(aud, ensure_ascii=False)}", flush=True)
    for r in rows:
        print(f"  {r['condition']:<4} {r['target']:<18} ok {r['ok']} · 막음 {json.dumps(r.get('block'), ensure_ascii=False)} · 기대 {r.get('n_expected')} · "
              f"rc {r.get('returncode')} · not-found {r.get('stderr_not_found')} · 씨앗 {r.get('seed')}", flush=True)
    print(f"요약 저장 {SUMMARY} · {json.dumps({k: v for k, v in out.get('summary', {}).items() if k != 'loadings'}, ensure_ascii=False)[:900]}", flush=True)
    sys.exit(rc or 0)
