# -*- coding: utf-8 -*-
"""MAGI-005 E-12 — 물 K_H(Widom, TIP5P-Ew 5자리) · 랩탑(Melchior) 몫.

배정·등록: `ASSIGN_MAGI5B_20260925.md` §laptop 2차 E-12 (03:16 등록, 자료 0건). 판정은 종합자.

[자 — v3w 물 프로토콜 그대로]  `run_tb2_water_kh.py` 에서 **물 정의 경로·사이트 세기·성분별 K_H 파서·unit_cells** 를 import.
    NumberOfCycles 15000 · NumberOfInitializationCycles 3000 · 298 K · UFF_MOF(Hw/Lw none, md5 8e8ec933) · 12 Å · Ewald 1e-6 ·
    압력 1e-5 Pa · 전하 ON(UseChargesFromCIFFile yes) · 물 = 19_WaterCompetition/water.def 를 실행 폴더에 복사.

[원형에 없던 관문 — 추가]
    ① **완주 표지** `Simulation finished`(run_aryl_gcmc.finished) — 원형 run_tb2_water_kh.run_one 은 K_H 를 표지 없이 읽습니다.
       CLAUDE.md §0 여섯째 결함("값이 아니라 표지가 자")과 같은 무늬라 여기서는 표지 없으면 값을 내지 않습니다.
    ② 머리말 관문 `ff_gate.read_ff_header` — Hw/Lw 짝 ZERO_POTENTIAL · Ow-Ow ε 89.633 (원형과 같음).
    ③ 실행 폴더 water.def 사이트 = 5 (원형과 같음) · 파일 관문 md5.
    ④ ⟨U⟩(dU_water) 와 Q_st(보정) = −ΔU + RT (CLAUDE.md §0 RT 부호 정정 규약).

사용:  czeromof/python run_magi5_e12_waterkh.py maf66 [calf20 mof16 ...]
       이름은 charged_v3/<name>_DDEC6.cif. 결과 파일은 **행 단위로 합칩니다**(뒤에 온 구조를 같은 파일에 더함).
"""
import glob
import json
import math
import os
import re
import shutil
import subprocess
import sys
import time
from concurrent.futures import ProcessPoolExecutor, as_completed

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import run_tb2_water_kh as W                 # noqa: E402  WATER_DEF · count_sites · read_kh · unit_cells · CYCLES/INIT/TEMP/CUTOFF/PRESS
import run_aryl_gcmc as rg                   # noqa: E402  finished · parse(⟨U⟩) · SIMULATE
from ff_gate import FF_MD5, FF_TAG, md5_gate, read_ff_header, ZERO_PAIRS, OWOW_EPS   # noqa: E402

RUNS = os.path.join(HERE, 'magi5_e12_runs')
MACHINE = os.environ.get('MAGI5_MACHINE', 'laptop')
OUT = os.path.join(HERE, f'results_magi5_e12_waterkh_{MACHINE}.json')
STAGGER = 12.0
R = 8.314462618e-3


def seed_of(p):
    for ln in open(p, encoding='utf-8', errors='ignore'):
        m = re.match(r'\s*Random number seed:\s*(\d+)', ln)
        if m:
            return int(m.group(1))


def total_time(p):
    t = None
    for ln in open(p, encoding='utf-8', errors='ignore'):
        m = re.match(r'\s*total time:\s*([0-9.]+)', ln)
        if m:
            t = float(m.group(1))
    return t


def run_one(job):
    idx, name = job
    cif = os.path.join(HERE, 'charged_v3', name + '_DDEC6.cif')
    fw = name + '_DDEC6'
    d = os.path.join(RUNS, 'widom_water_' + name)
    row = {'name': name, 'cif': os.path.relpath(cif, HERE), 'ff_md5': FF_MD5, 'forcefield': FF_TAG, 'machine': MACHINE}
    if os.path.isdir(os.path.join(d, 'Output')):
        return {**row, 'status': '실행폴더있음 — 섞지 않으려 착수 안 함(CLAUDE.md §3)'}
    time.sleep(idx * STAGGER)
    os.makedirs(d, exist_ok=True)
    shutil.copy(cif, os.path.join(d, fw + '.cif'))
    shutil.copy(W.WATER_DEF, os.path.join(d, 'water.def'))
    na, nb, nc = W.unit_cells(cif)
    with open(os.path.join(d, 'simulation.input'), 'w') as f:
        f.write(f"""SimulationType                MonteCarlo
NumberOfCycles                {W.CYCLES}
NumberOfInitializationCycles  {W.INIT}
PrintEvery                    {W.CYCLES // 10}
RestartFile                   no

Forcefield                    UFF_MOF
CutOff                        {W.CUTOFF}
UseChargesFromCIFFile         yes
ChargeMethod                  Ewald
EwaldPrecision                1e-6

Framework 0
FrameworkName                 {fw}
UnitCells                     {na} {nb} {nc}
ExternalTemperature           {W.TEMP}
ExternalPressure              {W.PRESS}

Component 0 MoleculeName              water
            MoleculeDefinition        TraPPE
            WidomProbability          1.0
            CreateNumberOfMolecules   0
""")
    t0 = time.time()
    subprocess.run([rg.SIMULATE, 'simulation.input'], cwd=d, stdout=subprocess.DEVNULL,
                   stderr=subprocess.DEVNULL, check=False)
    row.update({'unit_cells': [na, nb, nc], 'minutes_wall': round((time.time() - t0) / 60, 1)})
    outs = sorted(glob.glob(os.path.join(d, 'Output', 'System_0', '*.data')))
    if len(outs) != 1:
        return {**row, 'status': f'출력 .data {len(outs)}개'}
    p = outs[0]
    row.update({'seed': seed_of(p), 'total_time_s': total_time(p),
                'water_sites_in_rundir': W.count_sites(os.path.join(d, 'water.def'))})
    ff = read_ff_header(p)
    ff['ok'] = (all(ff.get(k) == 'ZERO_POTENTIAL' for k in ZERO_PAIRS)
                and ff.get('OwOw_eps') is not None and abs(ff['OwOw_eps'] - OWOW_EPS) < 1e-3)
    row['ff_check'] = ff
    if not rg.finished(p):                                  # 값이 아니라 표지가 자
        return {**row, 'status': '미완주'}
    kh, ekh, err = W.read_kh(p, comp='water')
    _, _, u, eu, _, _ = rg.parse(p)
    if err or kh is None:
        return {**row, 'status': f'값없음({err})'}
    row.update({'KH_water': kh, 'KH_water_err': ekh, 'dU_water': u, 'dU_water_err': eu,
                'Qst_rt_corrected': (None if u is None else -u + R * W.TEMP)})
    bad = []
    if not ff['ok']:
        bad.append('머리말관문(Hw/Lw·Ow-Ow)')
    if row['water_sites_in_rundir'] != 5:
        bad.append(f"물사이트 {row['water_sites_in_rundir']}")
    row['status'] = 'ok' if not bad else '관문실패: ' + ', '.join(bad)
    return row


def main():
    names = sys.argv[1:]
    if not names:
        print('사용: run_magi5_e12_waterkh.py <name> [...]  (charged_v3/<name>_DDEC6.cif) — 기본값 없음', flush=True)
        return 2
    ok, m = md5_gate()
    if not ok:
        return 4
    nsite = W.count_sites(W.WATER_DEF)
    print(f'  물 정의 {W.WATER_DEF} 사이트 {nsite} (TIP5P-Ew 는 5)', flush=True)
    if nsite != 5:
        return 1
    for n in names:
        if not os.path.exists(os.path.join(HERE, 'charged_v3', n + '_DDEC6.cif')):
            print(f'!! CIF 없음 charged_v3/{n}_DDEC6.cif', flush=True)
            return 2
    prior = json.load(open(OUT, encoding='utf-8')) if os.path.exists(OUT) else {'rows': []}
    rows = {r['name']: r for r in prior.get('rows', [])}
    os.makedirs(RUNS, exist_ok=True)
    print(f'E-12 물 Widom  대상 {names} · Widom {W.CYCLES}+초기화 {W.INIT} · {W.TEMP} K · md5 {m}', flush=True)
    with ProcessPoolExecutor(max_workers=min(8, len(names))) as ex:
        futs = [ex.submit(run_one, (i, n)) for i, n in enumerate(names)]
        for fu in as_completed(futs):
            r = fu.result()
            rows[r['name']] = r
            print(f"  [{r['status']}] {r['name']}  K_H {r.get('KH_water')} ± {r.get('KH_water_err')}  "
                  f"Q_st(보정) {r.get('Qst_rt_corrected')}  {r.get('minutes_wall')} min", flush=True)
            json.dump({'test': 'MAGI-005 E-12 물 K_H (Widom, TIP5P-Ew)', 'assign': 'ASSIGN_MAGI5B_20260925.md §laptop 2차 E-12',
                       'forcefield': FF_TAG, 'ff_md5': FF_MD5, 'NumberOfCycles': W.CYCLES,
                       'NumberOfInitializationCycles': W.INIT, 'temp_K': W.TEMP,
                       'note': ('± 는 RASPA 95 % CI. Q_st(보정) = −ΔU + RT(CLAUDE.md §0). 판정 없음(종합자). '
                                '값은 완주 표지·머리말 관문·5자리 확인을 모두 통과한 행만 status ok.'),
                       'rows': sorted(rows.values(), key=lambda x: x['name'])},
                      open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print(f'저장 {OUT}', flush=True)
    return 0


if __name__ == '__main__':
    sys.exit(main())
