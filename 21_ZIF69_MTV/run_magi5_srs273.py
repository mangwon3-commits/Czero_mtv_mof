# -*- coding: utf-8 -*-
"""E-9b — srs FSR_1(HSTC-1 원상) **273 K · 15 kPa CO₂ GCMC 1건** — 다른 시험(온도만 실측에 맞춤).

등록: `E9B_SRS273_REGISTRATION_20260925.md`(자료 0건, 2026-09-25 01:48 HKHOME). 제안: laptop2 E-9 개정판.

[자]  `run_aryl_gcmc.run_one` **무수정** — 전역 TEMP / PRESSURE / RUNS / MAX_WORKERS 만 덮는다.
      GCMC 5,000 + 15,000 · UFF_MOF(md5 8e8ec933) · 12 Å · Ewald 1e-6 · unit_cells() 규칙 · García-Sánchez CO₂ · 전하 ON(CIF 안 DDEC6).
[⚠]  298 K 자가 아니다 — 결과는 `results_magi5_e9b_srs273_hkhome.json` 에 따로. core_wc·results_v3 와 섞지 말 것.
      실행 뿌리는 새 폴더(`magi5_e9b_runs_srs<T>/`) — 같은 이름의 실행 폴더를 다른 온도와 공유하면 이어받기가 뒤섞인다(CLAUDE.md §3).
[환경] E9B_TEMP(기본 273.0) · E9B_PBAR(0.15) · E9B_CIF · E9B_OUT
"""
import json
import os
import socket
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import run_aryl_gcmc as rg   # noqa: E402
import ff_gate               # noqa: E402

TEMP = float(os.environ.get('E9B_TEMP', '273.0'))
P_BAR = float(os.environ.get('E9B_PBAR', '0.15'))
CIF = os.environ.get('E9B_CIF') or os.path.join(HERE, 'core_pop_cifs', '2024_Zn__srs_3_FSR_1.cif')
OUT = os.environ.get('E9B_OUT') or os.path.join(HERE, 'results_magi5_e9b_srs273_hkhome.json')
EXP_MMOL_G = 0.20            # ESI Fig. S1b 273 K 15 kPa 흡착 가지 [그림 판독 ±10 %] — E-9 개정판 §1
EXP_ERR_FRAC = 0.10

rg.TEMP = TEMP
rg.PRESSURE = P_BAR * 1e5
rg.RUNS = os.path.join(HERE, f'magi5_e9b_runs_srs{TEMP:g}')
rg.MAX_WORKERS = 1
os.makedirs(rg.RUNS, exist_ok=True)


def main():
    host = socket.gethostname()
    ok, msg = ff_gate.md5_gate()
    print(f'  [파일 관문] {msg}', flush=True)
    if not ok:
        print('!! 힘장 md5 불일치 — 착수 안 함', flush=True)
        return 3
    if not os.path.exists(CIF):
        print(f'!! CIF 없음 {CIF}', flush=True)
        return 2
    print(f'=== E-9b GCMC CO2 {TEMP:g} K · {P_BAR:g} bar · {os.path.basename(CIF)} · 뿌리 {os.path.basename(rg.RUNS)} · 착수 {time.strftime("%F %T")}', flush=True)
    t0 = time.time()
    name, gas, mode, r, stt = rg.run_one((CIF, 'CO2', 'gcmc'))
    el = time.time() - t0
    row = {'name': name, 'key': '2024[Zn][srs]3[FSR]1', 'identity': 'HSTC-1 원상 (E9_SRS_IDENTITY_20260925.md §3, FSR_1)',
           'cif': os.path.relpath(CIF, HERE), 'charges': 'on (CIF DDEC6)', 'temp_K': TEMP, 'pressure_bar': P_BAR,
           'status': stt, 'elapsed_s': round(el), 'machine': 'hkhome', 'host': host}
    if r is not None and r[4] is not None:
        row['n_mmol_g'], row['n_mmol_g_err'] = r[4], r[5]
        row['exp_mmol_g'] = EXP_MMOL_G
        row['exp_err_frac'] = EXP_ERR_FRAC
        R = r[4] / EXP_MMOL_G
        row['R'] = R
        # 두 오차를 따로: RASPA ± (95 % CI) 와 그림 판독 ±10 % — 합친 구간은 [n−±]/[0.22] ~ [n+±]/[0.18]
        row['R_lo'] = (r[4] - (r[5] or 0)) / (EXP_MMOL_G * (1 + EXP_ERR_FRAC))
        row['R_hi'] = (r[4] + (r[5] or 0)) / (EXP_MMOL_G * (1 - EXP_ERR_FRAC))
        row['ref_298K_mmol_g'] = 3.3779584687   # core_wc_results_ext_laptop.json (랩탑, 298 K) — 참고
    d = {'test': 'MAGI-005 E-9b — srs FSR_1 273 K·15 kPa CO2 GCMC (다른 시험: 온도만 실측에 맞춤)',
         'registration': 'E9B_SRS273_REGISTRATION_20260925.md',
         'protocol': {'gcmc_cycles': rg.GCMC_CYCLES, 'gcmc_init': rg.GCMC_INIT, 'forcefield': 'UFF_MOF',
                      'ff_md5': ff_gate.FF_MD5, 'cutoff': rg.CUTOFF, 'temp_K': TEMP, 'pressure_bar': P_BAR,
                      'charges': 'UseChargesFromCIFFile yes (CoRE CIF 의 PACMAN DDEC6)', 'supercell': 'unit_cells() 규칙',
                      'co2': 'García-Sánchez 2009 (경로 TraPPE/CO2.def, TraPPE 아님)'},
         'note': '판정 없음(종합자가 등록 문턱으로 씀). 298 K 자가 아니므로 core_wc·results_v3 와 섞지 말 것.',
         'host': host, 'finished': time.strftime('%F %T'), 'rows': [row]}
    json.dump(d, open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print(f'  [{stt}] {name} n={row.get("n_mmol_g")} ± {row.get("n_mmol_g_err")} mmol/g · R={row.get("R")} · {el/60:.1f} min → {OUT}', flush=True)
    return 0 if stt in ('ok', 'cached') else 1


if __name__ == '__main__':
    sys.exit(main())
