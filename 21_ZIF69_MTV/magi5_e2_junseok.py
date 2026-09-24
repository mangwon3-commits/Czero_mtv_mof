# -*- coding: utf-8 -*-
"""MAGI-005 E-2 (Junseok) — base · nbIm100 의 N₂ Widom ⟨U⟩ (+ CO₂ 검산). ASSIGN_MAGI5_20260925.md.

공용 러너는 고치지 않는다 — `run_aryl_gcmc.run_one`(= run_core_pop 의 자)을 import 해서 부르고
작업 폴더만 새로(`magi5_e2_runs/`) 준다(옛 폴더 이어받기 금지 — CLAUDE.md §3).
씨앗 = 착수 초이므로 작업마다 15 s 어긋내 띄운다. 완주는 `Simulation finished` 표지로만(run_one 이 검사).
판정문은 종합자 몫 — 여기서는 수와 등록 띠 안/밖(기계적 사실)만 적는다.
"""
import json, math, os, re, sys, time, glob, datetime
from concurrent.futures import ProcessPoolExecutor, as_completed

HERE = '/home/mangwon/mof_project/21_ZIF69_MTV'
sys.path.insert(0, HERE)
import run_aryl_gcmc as rg
import ff_gate

rg.RUNS = os.path.join(HERE, 'magi5_e2_runs')
OUT = os.path.join(HERE, 'results_magi5_e2_n2du_junseok.json')
R = 8.314462618e-3
RT = R * 298.0
STAGGER = 15.0
NAMES = ('base', 'nbIm100')


def timed(job):
    t0 = time.time()
    name, gas, mode, r, st = rg.run_one(job)
    return name, gas, mode, r, st, t0, time.time()


def seed_and_dir(name, gas):
    d = os.path.join(rg.RUNS, f'widom_{gas}_{name}')
    for f in glob.glob(os.path.join(d, 'Output', 'System_0', '*.data')):
        seed = rdir = None
        for ln in open(f, encoding='utf-8', errors='ignore'):
            m = re.match(r'\s*Random number seed:\s*(\d+)', ln)
            if m:
                seed = int(m.group(1))
            m = re.match(r'\s*RASPA directory set to:\s*(\S+)', ln)
            if m:
                rdir = m.group(1)
            if seed and rdir:
                break
        return seed, rdir, os.path.relpath(f, HERE)
    return None, None, None


def main():
    md5 = ff_gate.md5_gate(verbose=True)
    ffp = ff_gate.ff_path()
    import hashlib
    m = hashlib.md5(open(ffp, 'rb').read()).hexdigest()
    print(f'힘장 파일 {ffp}  md5 {m}', flush=True)
    if m != '8e8ec933f9013c7e932da04dc256efd3':
        print('!! 힘장 관문 실패 — 중단', flush=True)
        return 2
    ref = {r['name']: r for r in json.load(open(os.path.join(HERE, 'results_v3.json')))['rows']}
    jobs = [(os.path.join(HERE, 'charged_v3', f'{n}_DDEC6.cif'), g, 'widom') for g in ('N2', 'CO2') for n in NAMES]
    os.makedirs(rg.RUNS, exist_ok=True)
    print(f'E-2  {len(jobs)}작업 (N₂ 2 + CO₂ 검산 2) · 워커 4 · 착수 간격 {STAGGER:g} s · RUNS {rg.RUNS}', flush=True)
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
        seedN, rdirN, fN = seed_and_dir(nm, 'N2')
        seedC, rdirC, fC = seed_and_dir(nm, 'CO2')
        rv = ref[n]
        dU_CO2_ref = -(rv['Qst_CO2_rt_corrected'] - RT)          # 등록: −(Q_st 보정 − RT)
        row = {'name': n, 'cif': f'charged_v3/{n}_DDEC6.cif', 'ff_md5': m, 'raspa_dir': rdirN,
               'status_N2': sN, 'status_CO2': sC, 'seed_N2': seedN, 'seed_CO2': seedC,
               'minutes_N2': round((bN - aN) / 60, 1), 'minutes_CO2': round((bC - aC) / 60, 1),
               'unit_cells': rg.unit_cells(rg.read(os.path.join(HERE, 'charged_v3', f'{n}_DDEC6.cif'))),
               'KH_N2_ref': rv['KH_N2'], 'KH_N2_ref_err': rv['KH_N2_err'],
               'KH_CO2_ref': rv['KH_CO2'], 'KH_CO2_ref_err': rv['KH_CO2_err'],
               'dU_CO2_ref': round(dU_CO2_ref, 4), 'dU_CO2_ref_source': 'results_v3 Qst_CO2_rt_corrected − RT(298 K)'}
        if rN and rN[0] is not None:
            row.update(KH_N2=rN[0], KH_N2_err=rN[1], dU_N2=rN[2], dU_N2_err=rN[3])
            u = max(rN[1], rv['KH_N2_err'])
            row['KH_N2_check_units'] = round(abs(rN[0] - rv['KH_N2']) / u, 2)
            row['KH_N2_check'] = 'pass' if row['KH_N2_check_units'] < 1.5 else 'FAIL'
            row['ddU'] = round(rN[2] - dU_CO2_ref, 3)                  # ΔΔU = dU_N2 − dU_CO2
            row['ddU_band_10_15'] = 'in' if 10 <= row['ddU'] <= 15 else 'out'
            row['S273_over_S298'] = round(math.exp(row['ddU'] / R * (1 / 273.0 - 1 / 298.0)), 3)
        if rC and rC[0] is not None:
            row.update(KH_CO2=rC[0], KH_CO2_err=rC[1], dU_CO2=rC[2], dU_CO2_err=rC[3])
            u = max(rC[1], rv['KH_CO2_err'])
            row['KH_CO2_check_units'] = round(abs(rC[0] - rv['KH_CO2']) / u, 2)
            row['dU_CO2_check_kJ'] = round(rC[2] - dU_CO2_ref, 3)
            if row.get('dU_N2') is not None:
                row['ddU_samerun'] = round(row['dU_N2'] - rC[2], 3)
        row['status'] = 'ok' if (sN in ('ok', 'cached') and row.get('dU_N2') is not None) else f'N2 실패({sN})'
        rows.append(row)
    out = {'test': 'MAGI-005 E-2 (M R3 P8) — N₂ Widom ⟨U⟩', 'assign': 'ASSIGN_MAGI5_20260925.md §E-2', 'machine': 'junseok',
           'protocol': {'widom_init': rg.WIDOM_INIT, 'widom_cycles': rg.WIDOM_CYCLES, 'forcefield': 'UFF_MOF', 'cutoff': rg.CUTOFF,
                        'temp_K': rg.TEMP, 'charges': 'UseChargesFromCIFFile (charged_v3 PACMAN DDEC6)', 'ewald': '1e-6',
                        'supercell': 'run_aryl_gcmc.unit_cells() 최소거리 규칙', 'runner': 'run_aryl_gcmc.run_one (수정 없음)'},
           'registered_prediction': 'ΔΔU ∈ [10, 15] kJ/mol (M R3 P8) — 판정문은 종합자',
           'note': '머리말 관문(Hw/Lw)은 물이 없는 실행이라 해당 없음(null). 힘장 파일 md5 로 확인.',
           'rows': rows}
    json.dump(out, open(OUT, 'w', encoding='utf-8'), indent=2, ensure_ascii=False)
    print(f'\n저장 {OUT}', flush=True)
    for r in rows:
        print(f"  {r['name']:<8} KH_N2 {r.get('KH_N2')} (검산 {r.get('KH_N2_check_units')} 단위 {r.get('KH_N2_check')}) · dU_N2 {r.get('dU_N2')} ± {r.get('dU_N2_err')} · "
              f"ΔΔU {r.get('ddU')} ({r.get('ddU_band_10_15')}) · 같은 실행 ΔΔU {r.get('ddU_samerun')} · CO₂ 검산 {r.get('KH_CO2_check_units')} 단위 / dU {r.get('dU_CO2_check_kJ')} · "
              f"분 N₂ {r['minutes_N2']} CO₂ {r['minutes_CO2']}", flush=True)
    return 0


if __name__ == '__main__':
    sys.exit(main())
