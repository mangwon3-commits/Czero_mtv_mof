# -*- coding: utf-8 -*-
"""MAGI-005 E-3b (Junseok) — MAF-66 등온선 대조 GCMC 4작업. `ASSIGN_MAGI5B_20260925.md` §E-3b.

[자]   `run_aryl_gcmc.run_one` **무수정** — 작업마다 전역 TEMP / PRESSURE / RUNS 만 덮는다(`run_magi5_srs273.py` 본뜸).
       GCMC 5,000 + 15,000 · UFF_MOF(md5 8e8ec933) · 12 Å · Ewald 1e-6 · unit_cells() 규칙 · García-Sánchez CO₂ · TraPPE N₂ ·
       전하 ON(CIF 안 PACMAN DDEC6).
[뿌리] (기체·T·P)마다 새 폴더 `magi5_e3b_runs_<gas>_<T>K_<P>bar/` — 같은 이름의 실행 폴더를 다른 조건과 공유하면
       이어받기가 뒤섞인다(CLAUDE.md §3). 워커 프로세스 안에서 전역을 덮으므로 작업끼리 섞이지 않는다.
[씨앗] 착수 초 → 15 s 어긋냄. 완주는 `Simulation finished` 표지로만(run_one 이 검사, 여기서 한 번 더 찍음).
[판정] 종합자 몫 — 여기서는 수와 배정문이 정한 양(R₂₉₈ · R₂₇₃ · ΔQ = −RT ln R, 보고만)만 적는다.
[저장] 작업이 끝날 때마다 결과 JSON 을 다시 쓴다(끝나지 않은 행은 status 'pending').
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

CIF = os.path.join(HERE, 'charged_v3', 'maf66_DDEC6.cif')
OUT = os.path.join(HERE, 'results_magi5_e3b_maf66_gcmc_junseok.json')
STAGGER = 15.0
R_KJ = 8.314462618e-3
JOBS = [('CO2', 298.0, 1.0), ('CO2', 298.0, 0.15), ('CO2', 273.0, 1.0), ('N2', 298.0, 1.0)]
# Lin 2012 (Inorg. Chem. 51, 9950) 초록 — CO₂ 19.4 wt% @298 K·1 atm, 27.6 wt% @273 K·1 atm → wt%/44.01×10 (종합자 02:0x 재확인)
EXP = {('CO2', 298.0, 1.0): 4.41, ('CO2', 273.0, 1.0): 6.27}


def root(gas, T, P):
    return os.path.join(HERE, f'magi5_e3b_runs_{gas}_{T:g}K_{P:g}bar')


def job(args):
    gas, T, P = args
    rg.TEMP = T
    rg.PRESSURE = P * 1e5
    rg.RUNS = root(gas, T, P)
    os.makedirs(rg.RUNS, exist_ok=True)
    t0 = time.time()
    name, _g, _m, r, st = rg.run_one((CIF, gas, 'gcmc'))
    return gas, T, P, name, r, st, t0, time.time()


def data_meta(gas, T, P, name):
    d = os.path.join(root(gas, T, P), f'gcmc_{gas}_{name}')
    for f in glob.glob(os.path.join(d, 'Output', 'System_0', '*.data')):
        seed = None
        for ln in open(f, encoding='utf-8', errors='ignore'):
            m = re.match(r'\s*Random number seed:\s*(\d+)', ln)
            if m:
                seed = int(m.group(1))
                break
        return seed, rg.finished(f), os.path.relpath(f, HERE)
    return None, False, None


def main():
    ok, m = ff_gate.md5_gate(verbose=True)
    if not ok or m != ff_gate.FF_MD5:
        print(f'!! 힘장 관문 실패 ({m}) — 착수 안 함', flush=True)
        return 3
    if not os.path.exists(CIF):
        print(f'!! CIF 없음 {CIF}', flush=True)
        return 2
    atoms = rg.read(CIF)
    uc = list(rg.unit_cells(atoms))
    spec_vol = atoms.get_volume() * 1e-24 * 6.02214076e23 / atoms.get_masses().sum()     # cm³/g (셀 전체)
    name = os.path.basename(CIF).replace('.cif', '')
    rows = {}
    for gas, T, P in JOBS:
        rows[(gas, T, P)] = {'gas': gas, 'temp_K': T, 'pressure_bar': P, 'status': 'pending',
                             'run_root': os.path.relpath(root(gas, T, P), HERE)}

    def write(final=False):
        out = {'test': 'MAGI-005 E-3b — MAF-66 등온선 대조 GCMC (T-J3′ 후속: 문헌 225 대 우리 15.5 의 원인 가르기)',
               'assign': 'ASSIGN_MAGI5B_20260925.md §E-3b', 'machine': 'junseok', 'final': final,
               'cif': 'charged_v3/maf66_DDEC6.cif (2×2×1 초격자 304원자 · PACMAN DDEC6)',
               'protocol': {'gcmc_init': rg.GCMC_INIT, 'gcmc_cycles': rg.GCMC_CYCLES, 'forcefield': 'UFF_MOF',
                            'ff_md5': m, 'cutoff': rg.CUTOFF, 'ewald': '1e-6',
                            'charges': 'UseChargesFromCIFFile yes (CIF 안 PACMAN DDEC6)',
                            'co2': 'García-Sánchez 2009 (경로 TraPPE/CO2.def, TraPPE 아님)', 'n2': 'TraPPE',
                            'supercell': 'run_aryl_gcmc.unit_cells() 규칙', 'runner': 'run_aryl_gcmc.run_one (수정 없음)'},
               'reference': 'Lin 2012 Inorg. Chem. 51, 9950 초록 — CO₂ 4.41 mmol/g @298 K·1 atm · 6.27 mmol/g @273 K·1 atm',
               'quantities': 'R = n(1 bar)/문헌(1 atm) · ΔQ = −RT ln R (보고만) — 판정문은 종합자',
               'note': ('적재는 RASPA absolute. 문헌값은 excess — 차이 상한 = 기체 밀도(P/RT) × 셀 전체 비부피 '
                        f'{spec_vol:.4f} cm³/g (행마다 abs_minus_excess_upper_mmol_g). 1 atm 대 1.0 bar 차 1.3 % 는 병기만.'),
               'rows': [rows[k] for k in JOBS]}
        tmp = OUT + '.tmp'
        json.dump(out, open(tmp, 'w', encoding='utf-8'), indent=2, ensure_ascii=False)
        os.replace(tmp, OUT)

    print(f'E-3b  {len(JOBS)}작업 · 워커 {len(JOBS)} · 착수 간격 {STAGGER:g} s · 단위셀 {uc} · CIF {os.path.relpath(CIF, HERE)}', flush=True)
    with ProcessPoolExecutor(max_workers=len(JOBS)) as ex:
        futs = []
        for i, j in enumerate(JOBS):
            if i:
                time.sleep(STAGGER)
            futs.append(ex.submit(job, j))
            print(f'  착수 {j[0]} {j[1]:g} K {j[2]:g} bar  {datetime.datetime.now():%H:%M:%S}', flush=True)
        write()
        for fu in as_completed(futs):
            gas, T, P, nm, r, st, t0, t1 = fu.result()
            seed, marker, rel = data_meta(gas, T, P, nm)
            row = rows[(gas, T, P)]
            row.update(status=st, marker_finished=marker, seed=seed, minutes=round((t1 - t0) / 60, 1),
                       unit_cells=uc, ff_md5=m, data=rel)
            row['abs_minus_excess_upper_mmol_g'] = round(P * 1e5 / (8.314462618 * T) * 1e-6 * spec_vol * 1e3, 4)
            if r is not None and r[4] is not None:
                row['n_mmol_g'], row['n_mmol_g_err'] = r[4], r[5]
                exp = EXP.get((gas, T, P))
                if exp:
                    row['exp_mmol_g_1atm'] = exp
                    row['R'] = round(r[4] / exp, 4)
                    row['R_lo'] = round((r[4] - (r[5] or 0)) / exp, 4)
                    row['R_hi'] = round((r[4] + (r[5] or 0)) / exp, 4)
                    row['dQ_kJ_mol'] = round(-R_KJ * T * math.log(r[4] / exp), 3)
            write()
            print(f'  [{st:>6}] {gas:<3} {T:g} K {P:g} bar  n={row.get("n_mmol_g")} ± {row.get("n_mmol_g_err")} mmol/g'
                  f'  R={row.get("R")}  표지={marker}  씨앗={seed}  {(t1 - t0) / 60:.1f} 분', flush=True)
    write(final=True)
    print(f'\n저장 {OUT}', flush=True)
    return 0 if all(rows[k]['status'] in ('ok', 'cached') for k in JOBS) else 1


if __name__ == '__main__':
    sys.exit(main())
