# -*- coding: utf-8 -*-
"""MAGI-005 E-2e (Junseok) — fbIm100 · saIm050 의 N₂ Widom ⟨U⟩ (+ CO₂ 검산). `ASSIGN_MAGI5B_20260925.md` §Junseok 2차.

E-2(`magi5_e2_junseok.py`)와 같은 자·같은 방식 — `run_aryl_gcmc.run_one` 무수정 import, 새 폴더 `magi5_e2e_runs/`, 15 s 어긋냄(씨앗).
행 형식은 E-2c(`results_magi5_e2c_n2du_hkhome.json`) + 등록 괄호(구조별) · 괄호 밖 거리 · 기각 표지(> 0.5 kJ/mol).
판정문은 종합자 몫 — 여기서는 수와 괄호 안/밖(기계적 사실)만.
"""
import datetime
import glob
import json
import math
import os
import re
import sys
import time
from concurrent.futures import ProcessPoolExecutor, as_completed

HERE = '/home/mangwon/mof_project/21_ZIF69_MTV'
sys.path.insert(0, HERE)
import run_aryl_gcmc as rg   # noqa: E402
import ff_gate               # noqa: E402

rg.RUNS = os.path.join(HERE, 'magi5_e2e_runs')
OUT = os.path.join(HERE, 'results_magi5_e2e_n2du_junseok.json')
R = 8.314462618e-3
RT = R * 298.0
STAGGER = 15.0
NAMES = ('fbIm100', 'saIm050')
BRACKET = {'fbIm100': (-12.5, -11.7), 'saIm050': (-13.6, -12.6)}    # 등록(04:56, 자료 0건)
REJECT_KJ = 0.5


def timed(job):
    t0 = time.time()
    name, gas, mode, r, st = rg.run_one(job)
    return name, gas, mode, r, st, t0, time.time()


def seed_of(name, gas):
    for f in glob.glob(os.path.join(rg.RUNS, f'widom_{gas}_{name}', 'Output', 'System_0', '*.data')):
        for ln in open(f, encoding='utf-8', errors='ignore'):
            m = re.match(r'\s*Random number seed:\s*(\d+)', ln)
            if m:
                return int(m.group(1)), rg.finished(f)
    return None, False


def main():
    t_start = time.time()
    ok, m = ff_gate.md5_gate(verbose=True)
    if not ok or m != ff_gate.FF_MD5:
        print(f'!! 힘장 관문 실패 ({m}) — 중단', flush=True)
        return 2
    ref = {r['name']: r for r in json.load(open(os.path.join(HERE, 'results_v3.json')))['rows']}
    jobs = [(os.path.join(HERE, 'charged_v3', f'{n}_DDEC6.cif'), g, 'widom') for g in ('N2', 'CO2') for n in NAMES]
    os.makedirs(rg.RUNS, exist_ok=True)
    print(f'E-2e  {len(jobs)}작업 (N₂ 2 + CO₂ 검산 2) · 워커 4 · 착수 간격 {STAGGER:g} s · RUNS {rg.RUNS}', flush=True)
    res = {}
    with ProcessPoolExecutor(max_workers=4) as ex:
        futs = []
        for i, j in enumerate(jobs):
            if i:
                time.sleep(STAGGER)
            futs.append(ex.submit(timed, j))
            print(f'  착수 {os.path.basename(j[0])} {j[1]}  {datetime.datetime.now():%H:%M:%S}', flush=True)
        for fu in as_completed(futs):
            name, gas, mode, r, st, t0, t1 = fu.result()
            res[(name, gas)] = (r, st, t0, t1)
            print(f'  [{st:>6}] {gas:<3} {name}  {(t1 - t0) / 60:.1f} 분', flush=True)

    rows = []
    for n in NAMES:
        nm = f'{n}_DDEC6'
        rN, sN, aN, bN = res.get((nm, 'N2'), (None, 'none', 0, 0))
        rC, sC, aC, bC = res.get((nm, 'CO2'), (None, 'none', 0, 0))
        seedN, fN = seed_of(nm, 'N2')
        seedC, fC = seed_of(nm, 'CO2')
        rv = ref[n]
        dU_CO2_ref = -(rv['Qst_CO2_rt_corrected'] - RT)
        lo, hi = BRACKET[n]
        row = {'name': n, 'cif': f'charged_v3/{n}_DDEC6.cif', 'gate5_note': '',
               'status_N2': sN, 'status_CO2': sC, 'marker_N2': fN, 'marker_CO2': fC, 'seed_N2': seedN, 'seed_CO2': seedC,
               'minutes_N2': round((bN - aN) / 60, 1), 'minutes_CO2': round((bC - aC) / 60, 1),
               'unit_cells': list(rg.unit_cells(rg.read(os.path.join(HERE, 'charged_v3', f'{n}_DDEC6.cif')))),
               'Qst_corr_ref': rv['Qst_CO2_rt_corrected'], 'dU_CO2_ref': dU_CO2_ref,
               'KH_N2_ref': rv['KH_N2'], 'KH_N2_ref_err': rv['KH_N2_err'],
               'KH_CO2_ref': rv['KH_CO2'], 'KH_CO2_ref_err': rv['KH_CO2_err'],
               'bracket': [lo, hi], 'ff_md5': m}
        if rN and rN[0] is not None:
            row.update(KH_N2=rN[0], KH_N2_err=rN[1], dU_N2=rN[2], dU_N2_err=rN[3])
            row['KH_N2_check_units'] = round(abs(rN[0] - rv['KH_N2']) / max(rN[1], rv['KH_N2_err']), 2)
            row['KH_N2_check'] = 'pass' if row['KH_N2_check_units'] < 1.5 else 'FAIL'
            du = rN[2]
            row['bracket_status'] = 'in' if lo <= du <= hi else 'out'
            row['outside_by_kJ'] = round(0.0 if lo <= du <= hi else (lo - du if du < lo else du - hi), 3)
            row['reject_gt_0.5'] = row['outside_by_kJ'] > REJECT_KJ
            row['ddU'] = du - dU_CO2_ref
            row['S273_over_S298'] = math.exp(row['ddU'] / R * (1 / 273.0 - 1 / 298.0))
        if rC and rC[0] is not None:
            row.update(KH_CO2=rC[0], KH_CO2_err=rC[1], dU_CO2=rC[2], dU_CO2_err=rC[3])
            row['KH_CO2_check_units'] = round(abs(rC[0] - rv['KH_CO2']) / max(rC[1], rv['KH_CO2_err']), 2)
            row['dU_CO2_check_kJ'] = round(rC[2] - dU_CO2_ref, 3)
            if row.get('dU_N2') is not None:
                row['ddU_samerun'] = round(row['dU_N2'] - rC[2], 3)
        row['status'] = 'ok' if (sN in ('ok', 'cached') and row.get('dU_N2') is not None) else f'N2 실패({sN})'
        rows.append(row)
    out = {'test': 'MAGI-005 E-2e — fbIm100·saIm050 N2 Widom ⟨U⟩ (인자표 완성)',
           'registration': 'ASSIGN_MAGI5B_20260925.md §Junseok 2차 (04:56, 자료 0건)',
           'protocol': {'widom_init': rg.WIDOM_INIT, 'widom_cycles': rg.WIDOM_CYCLES, 'forcefield': 'UFF_MOF', 'ff_md5': m,
                        'cutoff': rg.CUTOFF, 'temp_K': rg.TEMP, 'charges': 'on (charged_v3 DDEC6)', 'supercell': 'unit_cells()',
                        'runner': 'run_aryl_gcmc.run_one (수정 없음)'},
           'registered_prediction': 'fbIm100 dU_N2 ∈ [−12.5, −11.7] · saIm050 ∈ [−13.6, −12.6] · 기각: 밖으로 > 0.5 kJ/mol — 판정문은 종합자',
           'host': 'junseok', 'elapsed_s': round(time.time() - t_start), 'finished': time.strftime('%F %T'), 'rows': rows}
    json.dump(out, open(OUT, 'w', encoding='utf-8'), indent=2, ensure_ascii=False)
    print(f'\n저장 {OUT}', flush=True)
    for r in rows:
        print(f"  {r['name']:<8} dU_N2 {r.get('dU_N2')} ± {r.get('dU_N2_err')} · 괄호 {r['bracket']} {r.get('bracket_status')} "
              f"(밖 {r.get('outside_by_kJ')} kJ/mol · 기각표지 {r.get('reject_gt_0.5')}) · KH_N2 검산 {r.get('KH_N2_check_units')} 단위 · "
              f"CO₂ 검산 {r.get('KH_CO2_check_units')} 단위 / dU {r.get('dU_CO2_check_kJ')} · ΔΔU {r.get('ddU')} · 인자 {r.get('S273_over_S298')} · "
              f"분 N₂ {r['minutes_N2']} CO₂ {r['minutes_CO2']}", flush=True)
    return 0


if __name__ == '__main__':
    sys.exit(main())
