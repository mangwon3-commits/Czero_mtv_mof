# -*- coding: utf-8 -*-
"""MAGI-005 E-4b (a) Widom (Junseok) — Zeo++ 요약(zeo_summary.json)을 읽어 **채널이 남는 경우만** 그 .block 으로
CO₂@1.65 · N₂@1.82 Widom(전하 ON, 298 K). `ASSIGN_MAGI5B_20260925.md` §Junseok 4차.

[자·입력] E-2b 드라이버(`magi5_e2b_junseok.py`)와 같음 — run_one 의 Widom 틀 + 성분 절 `BlockPockets yes` · `BlockPocketsFileName`.
         CIF 는 charged_v3/e4zif<NN>_DDEC6.cif (이완본과 셀·분율 좌표 같음 — 착수 전 확인, 최대 차 5e-9).
[관문]   E-2b 그대로: stderr 에 "'Blocking-pocket' file not found" 없음 · .data N = 구 수 × 단위셀 수(등식) · Simulation finished.
[0 판정] E-2b 후처리 기준을 처음부터 적용: K_H − ± ≤ 0 이고 K_H < 1e-6 × 차단 없음 참조 → "0 과 구별 안 됨"(S 는 null + 이유, 원값 *_raw).
[안 돌린 칸] channel 0 인 (구조, 반경)은 Widom 을 돌리지 않고 '통로 없음(0 channel)' 표지 — 배정문대로.
[참조]   차단 없음 E-4 ON 값: zif7 = Junseok · zif8·zif90 = laptop(results_magi5_e3_e4zif<NN>_widom_desktop-nvsrr9m.json).
판정문은 종합자 몫.
"""
import datetime
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

HERE = '/home/mangwon/mof_project/21_ZIF69_MTV'
sys.path.insert(0, HERE)
import run_aryl_gcmc as rg   # noqa: E402
import ff_gate               # noqa: E402

BASE = os.path.join(HERE, 'magi5_e4b_runs')
OUT = os.path.join(HERE, 'results_magi5_e4b_blockpockets_junseok.json')
SIM = '/home/mangwon/miniconda3/envs/czeromof/bin/simulate'
GAS_AT = {1.65: 'CO2', 1.82: 'N2'}
STAGGER = 15.0
NOT_FOUND = "'Blocking-pocket' file not found"
REL = 1e-6
REF_FILES = {7: 'results_magi5_e3_e4zif7_widom_junseok.json', 8: 'results_magi5_e3_e4zif8_widom_desktop-nvsrr9m.json',
             90: 'results_magi5_e3_e4zif90_widom_desktop-nvsrr9m.json'}


def widom(args):
    tag, r, gas, btxt, nsph, delay = args
    time.sleep(delay)
    name = f'{tag}_DDEC6'
    d = os.path.join(BASE, f'{tag}_r{r:.2f}', f'widom_{gas}_{name}')
    if os.path.exists(d):
        return tag, r, gas, {'status': '폴더있음(이어받기 안 함)'}
    os.makedirs(d)
    cif = os.path.join(d, name + '.cif')
    shutil.copy(os.path.join(HERE, 'charged_v3', name + '.cif'), cif)
    open(os.path.join(d, name + '.block'), 'w').write(btxt)
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
            BlockPockets              yes
            BlockPocketsFileName      {name}
            WidomProbability          1.0
            CreateNumberOfMolecules   0
""")
    t0 = time.time()
    with open(os.path.join(d, 'stderr.txt'), 'w') as ef:
        try:
            subprocess.run([SIM, 'simulation.input'], cwd=d, stdout=subprocess.DEVNULL, stderr=ef, timeout=28800, check=False)
        except subprocess.TimeoutExpired:
            return tag, r, gas, {'status': 'timeout'}
    row = {'minutes': round((time.time() - t0) / 60, 1), 'unit_cells': [na, nb, nc], 'n_spheres_per_uc': nsph,
           'n_expected': nsph * na * nb * nc}
    outs = glob.glob(os.path.join(d, 'Output', 'System_0', '*.data'))
    if not outs:
        row['status'] = 'no-output'
        return tag, r, gas, row
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
    if row['stderr_not_found'] or row['n_blocked_reported'] != row['n_expected'] or not row['pockets_blocked_line']:
        row['status'] = 'no-block'
    elif not row['marker_finished']:
        row['status'] = '미완주'
    elif kh is None:
        row['status'] = '값없음'
    else:
        row['status'] = 'ok'
    for sub in ('VTK', 'Movies', 'Restart'):
        shutil.rmtree(os.path.join(d, sub), ignore_errors=True)
    return tag, r, gas, row


def main():
    t_start = time.time()
    ok, m = ff_gate.md5_gate(verbose=True)
    if not ok or m != ff_gate.FF_MD5:
        print(f'!! 힘장 관문 실패 ({m}) — 중단', flush=True)
        return 3
    zs = json.load(open(os.path.join(BASE, 'zeo_summary.json'), encoding='utf-8'))
    ref = {}
    for n, fn in REF_FILES.items():
        on = [r for r in json.load(open(os.path.join(HERE, fn), encoding='utf-8'))['rows'] if r['charges'] == 'on'][0]
        ref[f'e4zif{n}'] = {'source': fn, 'KH_CO2': on['KH_CO2'], 'KH_CO2_err': on['KH_CO2_err'], 'KH_N2': on['KH_N2'],
                            'KH_N2_err': on['KH_N2_err'], 'S': on['selectivity'], 'S_err': on['selectivity_err']}
    jobs = []
    for z in zs['rows']:
        if z['channels'] and z['channels'] >= 1 and z['block_file']:
            btxt = open(os.path.join(HERE, z['block_file'])).read()
            jobs.append((z['tag'], z['probe_radius_A'], GAS_AT[z['probe_radius_A']], btxt, z['n_spheres'], STAGGER * len(jobs)))
    print(f'E-4b (a) Widom {len(jobs)}작업: {[(j[0], j[1], j[2]) for j in jobs]}', flush=True)
    res = {}
    if jobs:
        with ProcessPoolExecutor(max_workers=len(jobs)) as ex:
            futs = [ex.submit(widom, j) for j in jobs]
            for fu in as_completed(futs):
                tag, r, gas, row = fu.result()
                res[(tag, r)] = row
                print(f'  [{row.get("status"):>6}] {tag} r={r:.2f} {gas} K_H {row.get("KH")} ± {row.get("KH_err")} · '
                      f'N {row.get("n_blocked_reported")}/{row.get("n_expected")} · 표지 {row.get("marker_finished")} · 씨앗 {row.get("seed")} · {row.get("minutes")} 분', flush=True)
    rows, canon = [], {}
    for z in zs['rows']:
        tag, r = z['tag'], z['probe_radius_A']
        gas = GAS_AT[r]
        w = res.get((tag, r))
        if w and w.get('status') == 'ok':
            refk, refe = ref[tag]['KH_' + gas], ref[tag]['KH_' + gas + '_err']
            w['KH_over_unblocked'] = w['KH'] / refk
            w['KH_units_from_unblocked'] = round(abs(w['KH'] - refk) / max(w['KH_err'] or 0, refe), 2)
            w['KH_effectively_zero'] = bool(w['KH'] - (w['KH_err'] or 0) <= 0 and w['KH'] < REL * refk)
        rows.append({'tag': tag, 'probe_radius_A': r, 'gas': gas,
                     'zeo': {k: z[k] for k in ('channels', 'pockets', 'nodes', 'accessible_nodes', 'n_spheres', 'sphere_radii',
                                               'coord_max', 'block_file', 'seconds', 'peak_rss_MB', 'stopped_by_guard', 'res')},
                     'widom': w if w else {'status': 'not-run', 'why': '0 channel — 통로 없음(배정: 채널 남는 경우만 Widom)'}})
    for tag in sorted({z['tag'] for z in zs['rows']}, key=lambda t: int(t[5:])):
        c = next(x for x in rows if x['tag'] == tag and x['probe_radius_A'] == 1.65)
        n = next(x for x in rows if x['tag'] == tag and x['probe_radius_A'] == 1.82)
        cw, nw = c['widom'], n['widom']
        cz = c['zeo']['channels'] == 0
        nz = n['zeo']['channels'] == 0
        entry = {'pair': 'CO₂@1.65 / N₂@1.82', 'reference_unblocked': ref[tag]}
        if cz and nz:
            entry.update(S=None, note='두 반경 모두 0 channel — CO₂ · N₂ 둘 다 통로 없음 → 차단 없음 S_ON 은 탐침 규약값')
        elif nz and cw.get('status') == 'ok' and not cw.get('KH_effectively_zero'):
            entry.update(S=None, divergent=True, note='N₂@1.82 0 channel(통로 없음) · CO₂@1.65 통로 있음 → 정식 짝 발산(E-2b 형)')
        elif cw.get('status') == 'ok' and nw.get('status') == 'ok':
            kc, kn = cw['KH'], nw['KH']
            if cw.get('KH_effectively_zero') or nw.get('KH_effectively_zero'):
                entry.update(S=None, note='한쪽 이상이 0 과 구별 안 됨', S_raw=(kc / kn if kn else None))
            else:
                S = kc / kn
                entry.update(S=S, S_err=S * math.hypot(cw['KH_err'] / kc, nw['KH_err'] / kn), S_over_unblocked=S / ref[tag]['S'])
        else:
            entry.update(S=None, note='정식 짝 계산 불가 — 행별 상태 참조')
        canon[tag] = entry
    out = {'test': 'MAGI-005 E-4b (a) — 탐침 규약 검사(BlockPockets) ZIF-7 · 8 · 90', 'assign': 'ASSIGN_MAGI5B_20260925.md §Junseok 4차 (06:56, 자료 0건)',
           'machine': 'junseok', 'zeo': {'samples': zs['samples'], 'flags': '-ha', 'input': 'relax_tnf/e4zif<NN>_relaxed.cif'},
           'protocol': {'widom_init': rg.WIDOM_INIT, 'widom_cycles': rg.WIDOM_CYCLES, 'forcefield': 'UFF_MOF', 'ff_md5': m, 'cutoff': rg.CUTOFF,
                        'temp_K': rg.TEMP, 'charges': 'UseChargesFromCIFFile yes (charged_v3 DDEC6)', 'input': 'run_one Widom 틀 + BlockPockets'},
           'gate': "stderr 에 Blocking-pocket not-found 없음 · .data N = 구 수 × 단위셀 수(등식) · Simulation finished",
           'zero_criterion': f'K_H − ± ≤ 0 이고 K_H < {REL:g} × 차단 없음 참조 → 0 과 구별 안 됨',
           'registered': 'ZIF-7 두 반경 0 channel · ZIF-8 1.65 에서 0 channel(경계) · ZIF-90 1.65 channel ≥ 1 / 1.82 0 channel · 기각: ZIF-7 channel ≥ 1 — 판정문은 종합자',
           'elapsed_s': round(time.time() - t_start), 'finished': time.strftime('%F %T'), 'rows': rows, 'canonical': canon}
    json.dump(out, open(OUT, 'w', encoding='utf-8'), indent=2, ensure_ascii=False)
    print(f'\n저장 {OUT}', flush=True)
    for tag, e in canon.items():
        print(f"  {tag}: 정식 짝 S {e.get('S')} · {e.get('note') or ''} (차단 없음 S_ON {ref[tag]['S']:.2f})", flush=True)
    return 0


if __name__ == '__main__':
    sys.exit(main())
