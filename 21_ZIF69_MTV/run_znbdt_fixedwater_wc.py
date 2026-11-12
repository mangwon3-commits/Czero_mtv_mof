# -*- coding: utf-8 -*-
"""등록 N — 물 수 고정 회수량(스트레스 시험). 등록문 `ASSIGN_FIXEDWATER_20261112.md`(읽는 법 · 예측은 거기 · 자료 0건에서 씀).

물음: 물이 결정 구조에서 관측된 양(셀당 8분자 = Zn 당 2 · 모체 기준 3.76 mol/kg)만큼 기공에 있을 때 CO₂ 흡착량과 회수량 순위가 어떻게 되는가.
방법: 습윤 회수량 러너(`run_humid_wc.py`)의 입력과 같되 **물 성분만** `SwapProbability 0.0` · `CreateNumberOfMolecules 8 × 셀수` —
      물은 들어오거나 나가지 못하고(개수 고정) 이동 · 회전 · 재배치만 한다. CO₂ 는 그대로 삽입 · 삭제. 힘장 · 물 모델 · 사이클 · 컷오프 · Ewald · 단위셀은 CLAUDE.md §1 그대로.
조건: ads298(298 K) · ads323(323 K) · des373(373 K) — CO₂ 분압 15 kPa · 구조 여섯 · 반복 3 = 54작업. 기체의 물 몰분율은 A · B 러너와 같게 둠(물이 교환되지 않으므로 CO₂ 분압 15 kPa 를 맞추는 데만 쓰임).
표지: 작업마다 `Simulation finished` · 반환코드 0 · CO₂ 적재 줄 · 물 순전하 · **물 분자 수가 셀당 8 로 유지** · 씨앗 고유(착수 사이 2 s 이상 · 잠금). 이전 결과 · 실행 폴더가 있으면 멈춤(이어받지 않음).
환경변수: FXW_MACHINE(필수) · FXW_TAGS(쉼표) · FXW_WORKERS(기본 8) · FXW_CORE_CAP(simulate 상한 · 기본 = 워커) · FXW_SMOKE=1(10 사이클 · 씨앗 1) · FXW_ROOT(스모크 폴더).
결과: results_fixedwater_wc_<기기>.json(작업 행 · 감사 · 판정 없음). 값의 평균 · 순위 · 판정은 여기서 내지 않는다(종합자)."""
import fcntl
import glob
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import time
from concurrent.futures import ProcessPoolExecutor, as_completed

from ase.io import read

import ff_gate
import run_aryl_gcmc as rg
import run_water as rw

HERE = os.path.dirname(os.path.abspath(__file__))
MACHINE = os.environ.get('FXW_MACHINE', '')
SMOKE = os.environ.get('FXW_SMOKE') == '1'
WORKERS = int(os.environ.get('FXW_WORKERS', '8'))
CAP = int(os.environ.get('FXW_CORE_CAP', str(WORKERS)))
NW_CELL = 8                                   # 셀당 물 분자 수(등록 고정 · Zn 당 2)
CYCLES, INIT = (10, 0) if SMOKE else (15000, 5000)
SEEDS = (1,) if SMOKE else (1, 2, 3)
ALLOWED = {                                   # 대상 전하 CIF 와 md5(A · B · E 와 같은 파일)
    'e22_parent': 'f15ce100', 'e24i_cn_open': '8fd4fc85', 'e24i_no2_open': '3a2a53ac',
    'e24i_cl_open': 'c1e97588', 'e24i_br_open': '4015ec2d', 'e24i_ch3_open': 'a8e6a165',
}
# (라벨, CO2 분압 Pa, 온도 K, 기체의 물 분압 Pa — A · B 러너와 같은 값)
CONDS = [('ads298', 15000.0, 298.0, 2852.1), ('ads323', 15000.0, 323.0, 11114.1), ('des373', 15000.0, 373.0, 2852.1)]
ROOT = os.environ.get('FXW_ROOT') or os.path.join(HERE, 'fixedwater_runs', MACHINE or 'none')
RESULT = (os.path.join(ROOT, 'smoke_result.json') if SMOKE else os.path.join(HERE, f'results_fixedwater_wc_{MACHINE}.json'))
LOCK = os.path.expanduser(f'~/.mof_chain/.fxw_{MACHINE or "none"}_start.lock')
md5 = lambda p: hashlib.md5(open(p, 'rb').read()).hexdigest()


def n_sim():
    try:
        return int(subprocess.run(['pgrep', '-xc', 'simulate'], capture_output=True, text=True).stdout.strip() or 0)
    except Exception:
        return 0


def water_per_cell(txt):
    cur = None
    for line in txt.splitlines():
        m = re.search(r'Component\s+(\d+)\s+\[(\w+)\]', line)
        if m:
            cur = m.group(2)
        if cur == 'water' and 'Average loading absolute [molecules/unit cell]' in line:
            v = re.search(r'cell\]\s*([0-9.eE+-]+)\s*\+/-\s*([0-9.eE+-]+)', line)
            if v:
                return float(v.group(1)), float(v.group(2))
    return None, None


def run_one(job):
    tag, label, p_co2, temp, p_h2o, k = job
    row = {'tag': tag, 'condition': label, 'rep': k, 'T_K': temp, 'p_CO2_Pa': p_co2, 'status': None}
    cif = os.path.join(HERE, 'charged_v3', f'{tag}_DDEC6.cif')
    d = os.path.join(ROOT, 'runs', f'{label}_{tag}_s{k}')
    if os.path.exists(d):
        row['status'] = '실행 폴더 있음'
        return row
    os.makedirs(d)
    name = f'{tag}_DDEC6'
    shutil.copy(cif, os.path.join(d, name + '.cif'))
    shutil.copy(rw.WATER_DEF, os.path.join(d, 'water.def'))
    na, nb, nc = rg.unit_cells(read(cif))
    nw = NW_CELL * na * nb * nc
    p_tot = p_co2 + p_h2o
    x_co2, x_h2o = p_co2 / p_tot, p_h2o / p_tot
    row.update(unit_cells=[na, nb, nc], n_water_fixed=nw, dir=os.path.relpath(d, HERE) if d.startswith(HERE) else d)
    with open(os.path.join(d, 'simulation.input'), 'w') as f:
        f.write(f"""SimulationType                MonteCarlo
NumberOfCycles                {CYCLES}
NumberOfInitializationCycles  {INIT}
PrintEvery                    {CYCLES}
RestartFile                   no

Forcefield                    UFF_MOF
CutOff                        {rg.CUTOFF}
UseChargesFromCIFFile         yes
ChargeMethod                  Ewald
EwaldPrecision                1e-6

Framework 0
FrameworkName                 {name}
UnitCells                     {na} {nb} {nc}
ExternalTemperature           {temp}
ExternalPressure              {p_tot:.4f}

Component 0 MoleculeName              CO2
            MoleculeDefinition        TraPPE
            MolFraction               {x_co2:.6f}
            TranslationProbability    0.5
            RotationProbability       0.3
            ReinsertionProbability    0.1
            SwapProbability           1.0
            CreateNumberOfMolecules   0

Component 1 MoleculeName              water
            MoleculeDefinition        TraPPE
            MolFraction               {x_h2o:.6f}
            TranslationProbability    0.5
            RotationProbability       0.3
            ReinsertionProbability    0.1
            SwapProbability           0.0
            CreateNumberOfMolecules   {nw}
""")
    os.makedirs(os.path.dirname(LOCK), exist_ok=True)
    with open(LOCK, 'a+') as lf:                       # 착수 문: simulate 상한 + 착수 사이 2 s 이상(씨앗 = 착수 초)
        fcntl.flock(lf, fcntl.LOCK_EX)
        while n_sim() >= CAP:
            time.sleep(5)
        time.sleep(2.2)
        t0 = time.time()
        p = subprocess.Popen([rg.SIMULATE, 'simulation.input'], cwd=d, stdout=subprocess.DEVNULL,
                             stderr=open(os.path.join(d, 'stderr.txt'), 'w'))
        time.sleep(1.0)
        fcntl.flock(lf, fcntl.LOCK_UN)
    try:
        rc = p.wait(timeout=259200)
    except subprocess.TimeoutExpired:
        p.kill()
        rc = -9
    open(os.path.join(d, 'fxw_returncode.txt'), 'w').write(str(rc))
    row.update(returncode=rc, minutes=round((time.time() - t0) / 60, 1))
    outs = glob.glob(os.path.join(d, 'Output', 'System_0', '*.data'))
    if not outs:
        row['status'] = 'no-output'
        return row
    txt = open(outs[0], encoding='utf-8', errors='ignore').read()
    s = re.search(r'Random number seed:\s*(\d+)', txt)
    res = rw.parse_components(outs[0])
    wpc, wpc_err = water_per_cell(txt)
    err = open(os.path.join(d, 'stderr.txt'), errors='ignore').read()
    row.update(seed=int(s.group(1)) if s else None, finished='Simulation finished' in txt, net_charge_ok=rw.net_charge_ok(outs[0]),
               stderr_not_found="'Blocking-pocket' file not found" in err, water_per_cell=wpc, water_per_cell_err=wpc_err,
               N_CO2=res.get('CO2', (None, None))[0], N_CO2_err=res.get('CO2', (None, None))[1],
               N_H2O=res.get('water', (None, None))[0], N_H2O_err=res.get('water', (None, None))[1])
    ok = (row['finished'] and rc == 0 and row['N_CO2'] is not None and row['net_charge_ok'] and not row['stderr_not_found']
          and row['seed'] is not None and wpc is not None and abs(wpc - NW_CELL) < 1e-6)
    row['status'] = 'ok' if ok else '표지 미달'
    for sub in ('VTK', 'Movies', 'Restart'):
        shutil.rmtree(os.path.join(d, sub), ignore_errors=True)
    return row


def dump(rows, info, complete):
    seeds = [r.get('seed') for r in rows]
    aud = {'n': len(rows), 'n_expected': info['n_expected'], 'n_ok': sum(1 for r in rows if r.get('status') == 'ok'),
           'seeds_distinct': None not in seeds and len(set(seeds)) == len(seeds)}
    out = dict(info, made=time.strftime('%F %T'), complete=bool(complete and aud['n_ok'] == aud['n_expected'] and aud['seeds_distinct']),
               audit_summary=aud, rows=sorted(rows, key=lambda r: (r['tag'], r['condition'], r['rep'])))
    tmp = RESULT + '.tmp'
    json.dump(out, open(tmp, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    os.replace(tmp, RESULT)
    return aud


def main():
    tags = [t for t in os.environ.get('FXW_TAGS', '').split(',') if t]
    if not MACHINE or not tags:
        print('!! FXW_MACHINE · FXW_TAGS 가 필요합니다 — 중단', flush=True)
        return 1
    bad = [t for t in tags if t not in ALLOWED]
    if bad:
        print(f'!! 등록 밖 대상 {bad} — 중단', flush=True)
        return 1
    for t in tags:
        m = md5(os.path.join(HERE, 'charged_v3', f'{t}_DDEC6.cif'))[:8]
        if m != ALLOWED[t]:
            print(f'!! {t} CIF md5 {m} ≠ 등록 {ALLOWED[t]} — 중단', flush=True)
            return 1
    ok, ffm = ff_gate.md5_gate()
    if not ok:
        print('!! 힘장 파일 관문 불일치 — 중단', flush=True)
        return 1
    if not SMOKE and (os.path.exists(RESULT) or os.path.exists(os.path.join(ROOT, 'runs'))):
        print(f'!! 이전 결과 {os.path.basename(RESULT)} 또는 실행 폴더가 있음 — 중단(이어받지 않음)', flush=True)
        return 1
    jobs = [(t, lab, p, T, ph, k) for k in SEEDS for t in tags for lab, p, T, ph in CONDS]
    info = {'test': '등록 N — 물 수 고정 회수량(스트레스 시험)', 'assign': 'ASSIGN_FIXEDWATER_20261112.md', 'machine': MACHINE, 'smoke': SMOKE,
            'runner': os.path.basename(__file__), 'runner_md5': md5(os.path.abspath(__file__)), 'started': time.strftime('%F %T'),
            'protocol': {'cycles': CYCLES, 'init': INIT, 'forcefield': 'UFF_MOF', 'ff_md5': ffm, 'cutoff': rg.CUTOFF, 'ewald': 1e-6,
                         'water': f'TIP5P-Ew 5자리(run_water.WATER_DEF) · 개수 고정(SwapProbability 0.0) · 셀당 {NW_CELL}분자', 'water_def_md5': md5(rw.WATER_DEF),
                         'conditions': [list(c) for c in CONDS], 'reps': list(SEEDS), 'blocking': False},
            'inputs': {t: ALLOWED[t] for t in tags}, 'n_expected': len(jobs), 'workers': WORKERS, 'core_cap': CAP,
            'note': '기계적 사실뿐 — 평균 · 순위 · 판정은 종합자(등록문의 읽는 법). ± 는 RASPA 95 % CI.'}
    print(f"등록 N — 기기 {MACHINE} · 대상 {tags} · 작업 {len(jobs)} · 워커 {WORKERS} · simulate 상한 {CAP} · 사이클 {INIT}+{CYCLES} · 셀당 물 {NW_CELL} · 힘장 {ffm[:8]} · 실행기 {info['runner_md5'][:8]}", flush=True)
    os.makedirs(ROOT, exist_ok=True)
    rows = []
    with ProcessPoolExecutor(max_workers=WORKERS) as ex:
        futs = [ex.submit(run_one, j) for j in jobs]
        for fu in as_completed(futs):
            r = fu.result()
            rows.append(r)
            print(f"  {r['condition']:7s} {r['tag']:14s} s{r['rep']} {r['status']} · rc {r.get('returncode')} · 완주 {r.get('finished')} · 물/셀 {r.get('water_per_cell')} · "
                  f"씨앗 {r.get('seed')} · {r.get('minutes')}분 ({len(rows)}/{len(jobs)})", flush=True)
            dump(rows, info, False)
    aud = dump(rows, info, True)
    print(f"감사 {json.dumps(aud, ensure_ascii=False)}", flush=True)
    return 0 if (aud['n_ok'] == aud['n_expected'] and aud['seeds_distinct']) else 2


if __name__ == '__main__':
    sys.exit(main())
