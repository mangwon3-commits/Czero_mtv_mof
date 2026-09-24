# -*- coding: utf-8 -*-
"""E-2c — brbIm100·saIm100 의 N₂ Widom ⟨U⟩ (+CO₂ 검산) 4작업. 등록 MAGI5_E2_VERDICT_20260925.md §6 (자료 0건).
자: run_aryl_gcmc.run_one widom 무수정(2×2×2 는 unit_cells() 가 정함) · 전하 ON · 298 K. 뿌리 magi5_e2c_runs/(새 폴더)."""
import json, os, sys, time, socket
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import run_aryl_gcmc as rg   # noqa: E402
import ff_gate               # noqa: E402
rg.RUNS = os.path.join(HERE, 'magi5_e2c_runs'); os.makedirs(rg.RUNS, exist_ok=True)
rg.MAX_WORKERS = 4
OUT = os.path.join(HERE, 'results_magi5_e2c_n2du_hkhome.json')
R = 8.314e-3
TAGS = ['brbIm100', 'saIm100']

def main():
    ok, msg = ff_gate.md5_gate(); print(f'  [파일 관문] {msg}', flush=True)
    if not ok: return 3
    v3 = json.load(open(os.path.join(HERE, 'results_v3.json'), encoding='utf-8')); v3rows = v3.get('rows', v3)
    jobs = [(os.path.join(HERE, 'charged_v3', f'{t}_DDEC6.cif'), g, 'widom') for t in TAGS for g in ('N2', 'CO2')]
    rows = {t: {'name': t, 'cif': f'charged_v3/{t}_DDEC6.cif', 'gate5_note': '관문 ⑤ 탈락(LCD 22.5 %)' if t == 'saIm100' else ''} for t in TAGS}
    from concurrent.futures import ProcessPoolExecutor, as_completed
    t0 = time.time()
    with ProcessPoolExecutor(max_workers=4) as ex:
        futs = []
        for j in jobs:
            futs.append(ex.submit(rg._star, j)); time.sleep(15)
        for fu in as_completed(futs):
            name, gas, mode, r, stt = fu.result()
            t = name.replace('_DDEC6', ''); row = rows[t]
            row[f'status_{gas}'] = stt
            if r is not None:
                row[f'KH_{gas}'], row[f'KH_{gas}_err'], row[f'dU_{gas}'], row[f'dU_{gas}_err'] = r[0], r[1], r[2], r[3]
            print(f'  [{stt}] {t} {gas} {r[:4] if r else None} ({(time.time()-t0)/60:.1f} min)', flush=True)
    for t, row in rows.items():
        ref = v3rows.get(t) if isinstance(v3rows, dict) else next((x for x in v3rows if x.get('name') == t), None)
        if ref:
            qc = ref.get('Qst_CO2'); row['Qst_corr_ref'] = qc + 4.9554 if qc is not None else None
            row['dU_CO2_ref'] = -(row['Qst_corr_ref'] - R * 298) if qc is not None else None
            row['KH_N2_ref'], row['KH_N2_ref_err'] = ref.get('KH_N2'), ref.get('KH_N2_err')
            if row.get('dU_N2') is not None and row.get('dU_CO2_ref') is not None:
                row['ddU'] = row['dU_N2'] - row['dU_CO2_ref']
                row['S273_over_S298'] = pow(2.718281828, row['ddU'] / R * (1 / 273 - 1 / 298))
                row['bracket_-12.5_-11.7'] = 'in' if -12.5 <= row['dU_N2'] <= -11.7 else 'out'
    json.dump({'test': 'MAGI-005 E-2c — brbIm100·saIm100 N2 Widom ⟨U⟩ (괄호 가정 시험)', 'registration': 'MAGI5_E2_VERDICT_20260925.md §6',
               'protocol': {'widom_init': rg.WIDOM_INIT, 'widom_cycles': rg.WIDOM_CYCLES, 'forcefield': 'UFF_MOF', 'ff_md5': ff_gate.FF_MD5, 'cutoff': rg.CUTOFF, 'temp_K': rg.TEMP, 'charges': 'on (charged_v3 DDEC6)', 'supercell': 'unit_cells()'},
               'host': socket.gethostname(), 'elapsed_s': round(time.time() - t0), 'finished': time.strftime('%F %T'), 'rows': list(rows.values())},
              open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('저장', OUT, flush=True); return 0

if __name__ == '__main__':
    sys.exit(main())
