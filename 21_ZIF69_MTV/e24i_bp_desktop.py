# -*- coding: utf-8 -*-
"""MAGI-005 E-24i (데스크탑) 막음 Widom — `e24g_bp_desktop.py` 사본(막음 파일 폴더 e24i_zeo_runs · 출력만). 원판: MAGI-005 E-24g · E-24h (데스크탑) 막음 Widom — 닿지 않는 주머니가 나온 새 치환체의 BlockPockets Widom, 전하 ON/OFF.
Junseok `magi5_e24c_bp_junseok.py`(db4346e2, E-24c 막음 Widom)의 **데스크탑 이식** — 바꾼 것: 경로 · 막음 파일 폴더(e24g_zeo_runs) ·
출력 이름 · 차단 없음 참조를 태그 정확 일치로(원판은 치환기 이름 부분 일치라 e24c 파일을 잡을 수 있음) · 문구. 입력 · 관문 · 계산 그대로.
등록 `ASSIGN_MAGI5B_20260925.md` §HKHOME 21차. 원판 머리말:
MAGI-005 E-24c 막음 Widom (Junseok) — 닿지 않는 주머니가 나온 형판 치환체(−OCH₃ · −C₂H₅)의 BlockPockets Widom, 전하 ON/OFF.

등록 ASSIGN_MAGI5B E-24c 보완 02:14(3efe1d37, 자료 0건): E-24b "판정의 뜻"대로 주머니가 있는 후보는 막음 Widom 뒤에만 (1)~(3) 에.
자: magi5_e4b_junseok.py(E-2b · E-4b 드라이버)와 같음 — run_aryl_gcmc 의 Widom 틀(3,000 + 15,000 · UFF_MOF · 12 Å · Ewald 1e-6 · 298 K ·
    unit_cells()) + 성분 절 `BlockPockets yes` · `BlockPocketsFileName`(작업 폴더의 <이름>.block). 막음 파일 = E-24c ① Zeo++ `-ha -block r 50000` 산출
    (e24c_zeo_runs/<tag>/block<r>/<tag>_relaxed.block). 짝: CO₂@1.65 · N₂@1.82. 이 배정에서 더한 것: 전하 OFF — run_magi5_widom.zero_charge_copy
    (골격 _atom_site_charge = 0, 흡착질 전하 · Ewald 유지) 사본을 같은 이름으로 OFF 폴더에 → S_ON · S_OFF · G 모두 막음판.
[관문] stderr 에 "'Blocking-pocket' file not found" 없음 · .data "Number of pockets blocked in a unitcell" = 구 수 × 단위셀 수(등식) ·
       "Pockets are blocked for this component" 줄 · Simulation finished. 착수 전: 이완본(Zeo++ 입력) · 전하본(RASPA 입력) 분율 좌표 · 셀 같음(최대 차 기록).
[0 판정] E-4b 와 같음: K_H − ± ≤ 0 이고(차단 없음 참조가 있으면) K_H < 1e-6 × 참조 → "0 과 구별 안 됨". 참조(데스크탑 차단 없음 Widom)는 있으면 서술로만 병기.
출력 results_e24c_och3_blockpockets_junseok.json(배정 이름 — C₂H₅ 도 같은 파일에 행으로). 기계적 사실뿐 — 판정문은 종합자.
사용: python magi5_e24c_bp_junseok.py --tags e24c_och3_100,e24c_c2h5_100   (E24C_BP_DRY=1 이면 계획만)
"""
import argparse
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

import numpy as np

HERE = '/home/mangwon1/mof_project/21_ZIF69_MTV'
sys.path.insert(0, HERE)
import run_aryl_gcmc as rg                       # noqa: E402
import ff_gate                                   # noqa: E402
from run_magi5_widom import zero_charge_copy     # noqa: E402
from ase.io import read                          # noqa: E402

BASE = os.path.join(HERE, 'e24i_bp_runs')
OUT = os.path.join(HERE, 'results_e24i_blockpockets_hkhome.json')
SIM = '/home/mangwon1/miniconda3/envs/czeromof/bin/simulate'
PAIR = ((1.65, 'CO2'), (1.82, 'N2'))
STAGGER = 15.0
NOT_FOUND = "'Blocking-pocket' file not found"
REL = 1e-6


def block_file(tag, r):
    return os.path.join(HERE, 'e24i_zeo_runs', tag, f'block{r:.2f}', f'{tag}_relaxed.block')


def coord_check(tag):
    a = read(os.path.join(HERE, 'relax_tnf', f'{tag}_relaxed.cif'))
    b = read(os.path.join(HERE, 'charged_v3', f'{tag}_DDEC6.cif'))
    d = a.get_scaled_positions() - b.get_scaled_positions()
    d -= np.round(d)
    return {'n_atoms': [len(a), len(b)], 'symbols_same': a.get_chemical_symbols() == b.get_chemical_symbols(),
            'cell_max_diff': float(np.abs(a.cell.array - b.cell.array).max()), 'frac_max_diff': float(np.abs(d).max())}


def widom(args):
    tag, r, gas, ch, btxt, nsph, delay = args
    time.sleep(delay)
    name = f'{tag}_DDEC6'
    d = os.path.join(BASE, tag, f'{ch}_r{r:.2f}_{gas}')
    if os.path.exists(d):
        return tag, r, gas, ch, {'status': '폴더있음(이어받기 안 함)'}
    os.makedirs(d)
    cif = os.path.join(d, name + '.cif')
    src = os.path.join(HERE, 'charged_v3', name + '.cif')
    if ch == 'on':
        shutil.copy(src, cif)
        nq0 = None
    else:
        nq0 = zero_charge_copy(src, cif)          # 같은 이름, 골격 전하 0
    bp = nsph > 0                                 # 구 0 개면 막을 것이 없음 — BlockPockets 없이(같은 계)
    if bp:
        open(os.path.join(d, name + '.block'), 'w').write(btxt)
    bplines = (f'            BlockPockets              yes\n            BlockPocketsFileName      {name}\n' if bp else '')
    na, nb, nc = rg.unit_cells(rg.read(cif))
    cyc, init, press = rg.WIDOM_CYCLES, rg.WIDOM_INIT, 1e-5
    with open(os.path.join(d, 'simulation.input'), 'w') as f:
        f.write(f"""SimulationType                MonteCarlo
NumberOfCycles                {cyc}
NumberOfInitializationCycles  {init}
PrintEvery                    {cyc}
RestartFile                   no

Forcefield                    UFF_MOF
CutOff                        {rg.CUTOFF}
UseChargesFromCIFFile         yes
ChargeMethod                  Ewald
EwaldPrecision                1e-6

Framework 0
FrameworkName                 {name}
UnitCells                     {na} {nb} {nc}
ExternalTemperature           {rg.TEMP}
ExternalPressure              {press}

Component 0 MoleculeName              {gas}
            MoleculeDefinition        TraPPE
{bplines}            WidomProbability          1.0
            CreateNumberOfMolecules   0
""")
    t0 = time.time()
    with open(os.path.join(d, 'stderr.txt'), 'w') as ef:
        try:
            cp = subprocess.run([SIM, 'simulation.input'], cwd=d, stdout=subprocess.DEVNULL, stderr=ef, timeout=28800, check=False)
            rc = cp.returncode
        except subprocess.TimeoutExpired:
            return tag, r, gas, ch, {'status': 'timeout'}
    row = {'minutes': round((time.time() - t0) / 60, 1), 'unit_cells': [na, nb, nc], 'n_spheres_per_uc': nsph,
           'n_expected': nsph * na * nb * nc, 'returncode': rc, 'zero_charge_atoms': nq0, 'block_pockets_used': bp}
    outs = glob.glob(os.path.join(d, 'Output', 'System_0', '*.data'))
    if len(outs) != 1:
        row['status'] = f'.data {len(outs)}개'
        return tag, r, gas, ch, row
    txt = open(outs[0], encoding='utf-8', errors='ignore').read()
    err = open(os.path.join(d, 'stderr.txt'), encoding='utf-8', errors='ignore').read()
    m = re.search(r'Number of pockets blocked in a unitcell:\s*(\d+)', txt)
    s = re.search(r'Random number seed:\s*(\d+)', txt)
    row.update(data=os.path.relpath(outs[0], HERE), seed=int(s.group(1)) if s else None,
               n_blocked_reported=int(m.group(1)) if m else None,
               pockets_blocked_line='Pockets are blocked for this component' in txt,
               stderr_not_found=NOT_FOUND in err, marker_finished=rg.finished(outs[0]))
    kh, ekh, u, eu, _l, _e = rg.parse(outs[0])
    row.update(KH=kh, KH_err=ekh, dU=u, dU_err=eu)
    if bp and (row['stderr_not_found'] or row['n_blocked_reported'] != row['n_expected'] or not row['pockets_blocked_line']):
        row['status'] = 'no-block'
    elif not row['marker_finished']:
        row['status'] = '미완주'
    elif kh is None:
        row['status'] = '값없음'
    else:
        row['status'] = 'ok'
    for sub in ('VTK', 'Movies', 'Restart'):
        shutil.rmtree(os.path.join(d, sub), ignore_errors=True)
    return tag, r, gas, ch, row


def unblocked_ref(tag):
    """데스크탑 · laptop2 의 차단 없음 Widom 결과(있으면) — 서술(주머니 포함 상한)로만."""
    fs = sorted(set(glob.glob(os.path.join(HERE, f'results_magi5_e3_{tag}_widom_*.json'))))   # 데스크탑 이식: 태그 정확 일치
    for f in fs:
        try:
            dd = json.load(open(f, encoding='utf-8'))
            rows = {x['charges']: x for x in dd['rows']}
            if rows.get('on', {}).get('KH_CO2') and rows.get('off', {}).get('KH_CO2'):
                return {'file': os.path.basename(f), 'on': rows['on'], 'off': rows['off']}
        except (OSError, ValueError, KeyError):
            continue
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--tags', required=True)
    a = ap.parse_args()
    tags = [t for t in a.tags.split(',') if t]
    t_start = time.time()
    ok, m = ff_gate.md5_gate(verbose=True)
    if not ok or m != ff_gate.FF_MD5:
        print(f'!! 힘장 관문 실패 ({m}) — 중단', flush=True)
        return 3
    plan, checks, jobs = {}, {}, []
    for t in tags:
        checks[t] = coord_check(t)
        c = checks[t]
        if not (c['symbols_same'] and c['cell_max_diff'] < 1e-6 and c['frac_max_diff'] < 1e-6):
            print(f'!! {t} 이완본 · 전하본 좌표 다름 {c} — 중단', flush=True)
            return 2
        for r, gas in PAIR:
            bf = block_file(t, r)
            btxt = open(bf).read()
            nsph = int(btxt.split()[0])
            plan[f'{t} r{r:.2f} {gas}'] = {'block_file': os.path.relpath(bf, HERE), 'n_spheres': nsph}
            for ch in ('on', 'off'):
                jobs.append((t, r, gas, ch, btxt, nsph, STAGGER * len(jobs)))
    print(f'E-24g 막음 Widom {len(jobs)}작업 · 좌표 {json.dumps(checks)} · 계획 {json.dumps(plan, ensure_ascii=False)}', flush=True)
    if os.environ.get('E24C_BP_DRY'):
        return 0
    n = lambda x: subprocess.run(['pgrep', '-xc', x], capture_output=True, text=True).stdout.strip()
    if n('network') not in ('', '0') or n('lmp_serial') not in ('', '0'):   # 데스크탑 E-24i 사본: 이 드라이버는 Zeo++ 를 안 씀 — simulate 조건은 뺌(다른 RASPA 와 함께 돌 수 있음)
        print('!! network · lmp_serial 도는 것 있음 — 중단', flush=True)
        return 1
    if os.path.exists(BASE) or os.path.exists(OUT):
        print('!! 이전 산출(e24i_bp_runs · 결과) 있음 — 중단', flush=True)
        return 1
    res = {}
    with ProcessPoolExecutor(max_workers=len(jobs)) as ex:
        for fu in as_completed([ex.submit(widom, j) for j in jobs]):
            t, r, gas, ch, row = fu.result()
            res[(t, r, gas, ch)] = row
            print(f'  [{row.get("status"):>6}] {t} {ch} r={r:.2f} {gas} K_H {row.get("KH")} ± {row.get("KH_err")} · N {row.get("n_blocked_reported")}/{row.get("n_expected")} · '
                  f'표지 {row.get("marker_finished")} · rc {row.get("returncode")} · 씨앗 {row.get("seed")} · {row.get("minutes")} 분', flush=True)
    per = {}
    for t in tags:
        ref = unblocked_ref(t)
        e = {'coords': checks[t], 'unblocked_reference_descriptive': ({'file': ref['file'], 'S_ON': ref['on'].get('selectivity'), 'S_OFF': ref['off'].get('selectivity')}
                                                                      if ref else None), 'rows': {}}
        for r, gas in PAIR:
            for ch in ('on', 'off'):
                w = dict(res.get((t, r, gas, ch), {'status': 'not-run'}))
                if w.get('status') == 'ok':
                    refk = ref[ch].get(f'KH_{gas}') if ref else None
                    w['KH_effectively_zero'] = bool(w['KH'] - (w['KH_err'] or 0) <= 0 and (refk is None or w['KH'] < REL * refk))
                    if refk:
                        w['KH_over_unblocked'] = w['KH'] / refk
                e['rows'][f'{ch}_{gas}@{r:.2f}'] = w
        S = {}
        for ch in ('on', 'off'):
            c, nn = e['rows'][f'{ch}_CO2@1.65'], e['rows'][f'{ch}_N2@1.82']
            if c.get('status') == 'ok' and nn.get('status') == 'ok' and not c['KH_effectively_zero'] and not nn['KH_effectively_zero']:
                s = c['KH'] / nn['KH']
                S[ch] = (s, s * math.hypot(c['KH_err'] / c['KH'], nn['KH_err'] / nn['KH']))
        if 'on' in S:
            e['S_ON_blocked'], e['S_ON_blocked_err'] = S['on']
        if 'off' in S:
            e['S_OFF_blocked'], e['S_OFF_blocked_err'] = S['off']
        if 'on' in S and 'off' in S:
            g = S['on'][0] / S['off'][0]
            e['G_blocked'], e['G_blocked_err'] = g, g * math.hypot(S['on'][1] / S['on'][0], S['off'][1] / S['off'][0])
        per[t] = e
    ok_all = all(v.get('status') == 'ok' for v in res.values())
    seeds = [v.get('seed') for v in res.values()]
    out = {'test': 'MAGI-005 E-24g · E-24h 막음 Widom(BlockPockets) — 주머니 있는 새 치환체, 전하 ON/OFF', 'machine': 'hkhome', 'ported_from': 'junseok magi5_e24c_bp_junseok.py (db4346e2)',
           'assign': 'ASSIGN_MAGI5B_20260925.md §HKHOME 22차(E-24i)', 'zeo': 'E-24i Junseok -ha -block r 50000 (results_e24i_access_junseok.json)',
           'protocol': {'widom_init': rg.WIDOM_INIT, 'widom_cycles': rg.WIDOM_CYCLES, 'forcefield': 'UFF_MOF', 'ff_md5': m, 'cutoff': rg.CUTOFF, 'temp_K': rg.TEMP,
                        'charges_on': 'charged_v3 DDEC6', 'charges_off': 'run_magi5_widom.zero_charge_copy(골격 전하 0, 흡착질 전하 · Ewald 유지)',
                        'pair': 'CO₂@1.65 막음 / N₂@1.82 막음'},
           'gate': "stderr 에 Blocking-pocket not-found 없음 · .data N = 구 수 × 단위셀 수(등식) · 'Pockets are blocked' 줄 · Simulation finished",
           'all_ok': ok_all, 'seeds_distinct': None not in seeds and len(set(seeds)) == len(seeds),
           'per_structure': per, 'elapsed_s': round(time.time() - t_start), 'finished': time.strftime('%F %T'),
           'note': '기계적 사실뿐 — 판정문은 종합자. 차단 없음 참조는 서술(주머니 포함 상한)로만.'}
    tmp = OUT + '.tmp'
    json.dump(out, open(tmp, 'w', encoding='utf-8'), indent=2, ensure_ascii=False)
    os.replace(tmp, OUT)
    print(f'\n저장 {OUT}', flush=True)
    for t, e in per.items():
        print(f"  {t}: S_ON 막음 {e.get('S_ON_blocked')} ± {e.get('S_ON_blocked_err')} · S_OFF 막음 {e.get('S_OFF_blocked')} ± {e.get('S_OFF_blocked_err')} · "
              f"G 막음 {e.get('G_blocked')} ± {e.get('G_blocked_err')} · 차단 없음 참조 {e['unblocked_reference_descriptive']}", flush=True)
    return 0


if __name__ == '__main__':
    sys.exit(main())
