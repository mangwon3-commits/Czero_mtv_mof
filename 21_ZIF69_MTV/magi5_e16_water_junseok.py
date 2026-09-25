# -*- coding: utf-8 -*-
"""MAGI-005 E-16 ② (Junseok) — 2017_Zn__dia_3_ASR_1 물 Widom 1건(v3w 프로토콜, run_tb2_water_kh.py 형). `ASSIGN_MAGI5B §Junseok 7차`.

[자]   run_tb2_water_kh.py 와 같음: TIP5P-Ew 5자리(19_WaterCompetition/water.def, md5 6fc8850d 정본) · MoleculeName water ·
       NumberOfCycles 15000 · NumberOfInitializationCycles 3000 · UFF_MOF · 12 Å · Ewald 1e-6 · 1e-5 Pa · 298 K · 전하 ON(CIF DDEC6) ·
       unit_cells 규칙. 헨리 계수는 그 러너의 read_kh(성분 이름 'water', 다중 일치 거부)로 읽는다 — 파서 하나.
[관문] **착수 전**: 같은 입력을 10 사이클(초기화 0)로 먼저 돌려 RASPA 가 **인쇄한** 쌍 표를 ff_gate.read_ff_header 로 본다 —
       Hw–Hw · Ow–Hw · Ow–Lw · Lw–Lw = ZERO_POTENTIAL, Ow–Ow ε 89.633. 실패면 **본 계산을 띄우지 않고 멈춘다**(힘장 수정 = 사용자 결정,
       CLAUDE.md §9 경계 ①). 본 계산 뒤에도 같은 관문을 한 번 더 기록. 힘장 파일 md5 8e8ec933 은 ff_gate.md5_gate.
판정문은 종합자.
"""
import glob
import hashlib
import json
import math
import os
import shutil
import subprocess
import sys
import time

HERE = '/home/mangwon/mof_project/21_ZIF69_MTV'
sys.path.insert(0, HERE)
import run_aryl_gcmc as rg            # noqa: E402
import ff_gate                        # noqa: E402
from run_tb2_water_kh import read_kh, count_sites   # noqa: E402

NAME = '2017_Zn__dia_3_ASR_1'
CIF = os.path.join(HERE, 'core_pop_cifs', NAME + '.cif')
WATER_DEF = os.path.join(HERE, '..', '19_WaterCompetition', 'water.def')
WATER_MD5 = '6fc8850d3d22a56a17e5643f35a6f731'
RUNS = os.path.join(HERE, 'magi5_e16_runs')
OUT = os.path.join(HERE, 'results_magi5_e16_zndia_water_junseok.json')


def setup(d, cycles, init):
    os.makedirs(d)
    shutil.copy(CIF, os.path.join(d, NAME + '.cif'))
    shutil.copy(WATER_DEF, os.path.join(d, 'water.def'))
    na, nb, nc = rg.unit_cells(rg.read(CIF))
    with open(os.path.join(d, 'simulation.input'), 'w') as f:
        f.write(f"""SimulationType                MonteCarlo
NumberOfCycles                {cycles}
NumberOfInitializationCycles  {init}
PrintEvery                    {max(1, cycles // 10)}
RestartFile                   no

Forcefield                    UFF_MOF
CutOff                        {rg.CUTOFF}
UseChargesFromCIFFile         yes
ChargeMethod                  Ewald
EwaldPrecision                1e-6

Framework 0
FrameworkName                 {NAME}
UnitCells                     {na} {nb} {nc}
ExternalTemperature           298.0
ExternalPressure              1e-05

Component 0 MoleculeName              water
            MoleculeDefinition        TraPPE
            WidomProbability          1.0
            CreateNumberOfMolecules   0
""")
    return [na, nb, nc]


def run(d):
    t0 = time.time()
    subprocess.run([rg.SIMULATE, 'simulation.input'], cwd=d, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False)
    outs = sorted(glob.glob(os.path.join(d, 'Output', 'System_0', '*.data')))
    return outs, round((time.time() - t0) / 60, 1)


def seed_of(p):
    for ln in open(p, encoding='utf-8', errors='ignore'):
        if 'Random number seed' in ln:
            return int(ln.split()[-1])
    return None


def main():
    t_start = time.time()
    ok, m = ff_gate.md5_gate(verbose=True)
    if not ok or m != ff_gate.FF_MD5:
        print(f'!! 힘장 파일 관문 실패 ({m}) — 멈춤', flush=True)
        return 3
    wm = hashlib.md5(open(WATER_DEF, 'rb').read()).hexdigest()
    print(f'  water.def md5 {wm} ({"정본" if wm == WATER_MD5 else "!! 정본 아님"}) · 사이트 {count_sites(WATER_DEF)}', flush=True)
    if wm != WATER_MD5 or count_sites(WATER_DEF) != 5:
        return 3
    if os.path.exists(RUNS) or os.path.exists(OUT):
        print('!! 이전 E-16 산출 있음 — 멈춤', flush=True)
        return 1
    # ① 착수 전 머리말 관문 — 10 사이클 시험
    hd = os.path.join(RUNS, 'hdrcheck')
    setup(hd, 10, 0)
    outs, mins = run(hd)
    if len(outs) != 1:
        print(f'!! 시험 실행 .data {len(outs)}개 — 멈춤', flush=True)
        return 1
    hg0 = ff_gate.read_ff_header(outs[0])
    print(f'  [착수 전 머리말 관문] {hg0} ({mins} 분)', flush=True)
    if not hg0.get('ok'):
        print('!! 머리말 관문 실패 — Hw/Lw 쌍이 ZERO_POTENTIAL 이 아니거나 Ow–Ow 가 다름. 본 계산 안 띄움(힘장 수정 = 사용자 결정).', flush=True)
        json.dump({'test': 'MAGI-005 E-16 ② 물 Widom', 'status': 'header-gate-failed', 'header_gate_pre': hg0},
                  open(OUT, 'w', encoding='utf-8'), indent=2, ensure_ascii=False)
        return 1
    # ② 본 계산
    wd = os.path.join(RUNS, f'widom_water_{NAME}')
    uc = setup(wd, 15000, 3000)
    print(f'  본 계산 착수 {time.strftime("%H:%M:%S")} · 단위셀 {uc}', flush=True)
    outs, mins = run(wd)
    row = {'name': NAME, 'cif': os.path.relpath(CIF, HERE), 'unit_cells': uc, 'minutes': mins, 'header_gate_pre': hg0}
    if len(outs) != 1:
        row.update(status=f'.data {len(outs)}개')
    else:
        kh, ekh, err = read_kh(outs[0], comp='water')
        hg1 = ff_gate.read_ff_header(outs[0])
        row.update(KH_water=kh, KH_water_err=ekh, read_error=err, header_gate=hg1, marker_finished=rg.finished(outs[0]),
                   seed=seed_of(outs[0]), water_sites_in_rundir=count_sites(os.path.join(wd, 'water.def')),
                   data=os.path.relpath(outs[0], HERE))
        row['status'] = 'ok' if (kh is not None and hg1.get('ok') and row['marker_finished'] and row['water_sites_in_rundir'] == 5) else '실패'
    ann = {r['file']: r for r in json.load(open(os.path.join(HERE, 'core_pop_annotated.json'), encoding='utf-8'))['rows']}[NAME + '.cif']
    v3 = {r['name']: r for r in json.load(open(os.path.join(HERE, 'results_v3.json'), encoding='utf-8'))['rows']}['saIm050']
    wref = [r for r in json.load(open(os.path.join(HERE, 'v3w_water_kh', 'water_kh_ALLw_hkhome.json'), encoding='utf-8'))['rows']
            if r['name'] == 'saIm050'][0]
    ref_idx = wref['KH_water'] / v3['KH_CO2']
    ref_err = ref_idx * math.hypot(wref['KH_water_err'] / wref['KH_water'], v3['KH_CO2_err'] / v3['KH_CO2'])
    out = {'test': 'MAGI-005 E-16 ② — 2017_Zn__dia_3_ASR_1 물 Widom (물 경쟁 지수)', 'assign': 'ASSIGN_MAGI5B_20260925.md §Junseok 7차',
           'protocol': {'water': 'TIP5P-Ew 5자리 (19_WaterCompetition/water.def md5 6fc8850d)', 'NumberOfCycles': 15000,
                        'NumberOfInitializationCycles': 3000, 'forcefield': 'UFF_MOF', 'ff_md5': m, 'cutoff': rg.CUTOFF, 'ewald': '1e-6',
                        'temp_K': 298.0, 'pressure_Pa': 1e-5, 'charges': 'UseChargesFromCIFFile yes (CoRE PACMAN DDEC6)',
                        'kh_parser': 'run_tb2_water_kh.read_kh(comp=water)', 'header_gate': 'ff_gate.read_ff_header — 착수 전(10 사이클) + 본 계산 뒤'},
           'reference': {'saIm050_KH_water': wref['KH_water'], 'saIm050_KH_water_err': wref['KH_water_err'],
                         'saIm050_KH_water_src': 'v3w_water_kh/water_kh_ALLw_hkhome.json', 'saIm050_KH_CO2': v3['KH_CO2'],
                         'saIm050_KH_CO2_err': v3['KH_CO2_err'], 'saIm050_index': ref_idx, 'saIm050_index_err': ref_err},
           'KH_CO2_this': ann['KH_CO2'], 'KH_CO2_this_err': ann['KH_CO2_err'], 'KH_CO2_src': 'core_pop_annotated.json (ON)',
           'registered': '물 경쟁 지수 K_H(H2O)/K_H(CO2) ≥ saIm050 의 1.46 · 기각: 1.5 단위(합성 ±) 넘게 아래 — 판정문은 종합자',
           'row': row, 'elapsed_s': round(time.time() - t_start), 'finished': time.strftime('%F %T')}
    if row.get('status') == 'ok':
        idx = row['KH_water'] / ann['KH_CO2']
        eidx = idx * math.hypot(row['KH_water_err'] / row['KH_water'], ann['KH_CO2_err'] / ann['KH_CO2'])
        comb = math.hypot(eidx, ref_err)
        out.update(index=idx, index_err=eidx, index_minus_ref_units=(idx - ref_idx) / comb, combined_err=comb,
                   rejection_line_index=ref_idx - 1.5 * comb)
    json.dump(out, open(OUT, 'w', encoding='utf-8'), indent=2, ensure_ascii=False)
    print(f"\n저장 {OUT}", flush=True)
    print(f"  K_H(H2O) {row.get('KH_water')} ± {row.get('KH_water_err')} · 지수 {out.get('index')} ± {out.get('index_err')} · "
          f"saIm050 {ref_idx:.3f} ± {ref_err:.3f} · 단위 {out.get('index_minus_ref_units')} · 기각선(지수) {out.get('rejection_line_index')} · "
          f"관문 {row.get('header_gate', {}).get('ok')} · 표지 {row.get('marker_finished')} · {row.get('minutes')} 분", flush=True)
    return 0 if row.get('status') == 'ok' else 1


if __name__ == '__main__':
    sys.exit(main())
