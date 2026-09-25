# -*- coding: utf-8 -*-
"""Junseok 5차 ③ — T-J1′ 새 대조 2019_Ni__pcu_3_ASR_1: Zeo++ -ha -block 1.65 + 정식 짝 차단 Widom(CO₂@1.65 · N₂@1.82).
`ASSIGN_MAGI5B_20260925.md` §Junseok 5차 ③ (자료 0건 등록). 예측(종합자): S_정식 / S_ON(44.4) ∈ [1.0, 1.4] · > 1.4 → T-J1′ 새 대조를 오염 대조로 표지.

순서: E-15 가 끝나 simulate 0 일 때 사슬이 부른다. ① Zeo++(RASPA 없음, network RSS 감시·가용 5 GB 밑이면 멈춤) → ② Widom 2(동시, 15 s 어긋냄).
Widom 입력·관문은 E-2b 그대로: run_one Widom 틀 + BlockPockets · stderr 'Blocking-pocket' not-found 없음 · N = 구 수 × 단위셀 수(등식) · 표지.
0 판정도 E-2b 후처리 기준(K_H − ± ≤ 0 이고 K_H < 1e-6 × 차단 없음 참조). 판정문은 종합자.
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
import zipfile
from concurrent.futures import ProcessPoolExecutor, as_completed

HERE = '/home/mangwon/mof_project/21_ZIF69_MTV'
sys.path.insert(0, HERE)
import run_aryl_gcmc as rg   # noqa: E402
import ff_gate               # noqa: E402

NAME = '2019_Ni__pcu_3_ASR_1'
W = os.path.join(HERE, 'magi5_tj1c_zeo')
RUNS = os.path.join(HERE, 'magi5_tj1c_runs')
OUT = os.path.join(HERE, 'results_magi5_tj1c_blockpockets_junseok.json')
ZEO = '/home/mangwon/miniconda3/envs/czeromof/bin/network'
SIM = '/home/mangwon/miniconda3/envs/czeromof/bin/simulate'
NOT_FOUND = "'Blocking-pocket' file not found"
REL = 1e-6


def avail_mb():
    for ln in open('/proc/meminfo'):
        if ln.startswith('MemAvailable:'):
            return int(ln.split()[1]) // 1024
    return 0


def zeo_block(r):
    d = os.path.join(W, f'r{r:.2f}')
    if os.path.exists(os.path.join(d, 'zeo_block.out')):
        print(f'  r={r:.2f} Zeo++ 산출 이미 있음 — 그대로 씀', flush=True)
    else:
        os.makedirs(d, exist_ok=True)
        shutil.copy(os.path.join(W, NAME + '.cif'), d)
        t0 = time.time()
        with open(os.path.join(d, 'zeo_block.out'), 'w') as fh:
            p = subprocess.Popen([ZEO, '-ha', '-block', f'{r:.2f}', '50000', NAME + '.cif'], cwd=d, stdout=fh, stderr=subprocess.STDOUT)
            peak = 0
            while p.poll() is None:
                try:
                    for ln in open(f'/proc/{p.pid}/status'):
                        if ln.startswith('VmRSS:'):
                            peak = max(peak, int(ln.split()[1]) // 1024)
                except OSError:
                    pass
                if avail_mb() < 5000:
                    p.kill()
                    print('!! 가용 5 GB 밑 — Zeo++ 멈춤', flush=True)
                time.sleep(1)
        print(f'  r={r:.2f} Zeo++ {time.time() - t0:.0f} s · 최대 {peak} MB', flush=True)
    txt = open(os.path.join(d, 'zeo_block.out'), errors='ignore').read()
    m = re.search(r'Identified (\d+) channels and (\d+) pockets', txt)
    bf = os.path.join(d, NAME + '.block')
    btxt = open(bf).read() if os.path.exists(bf) and os.path.getsize(bf) > 0 else None
    n = int(btxt.split()[0]) if btxt else None
    return {'probe_radius_A': r, 'channels': int(m.group(1)) if m else None, 'pockets': int(m.group(2)) if m else None,
            'n_spheres': n, 'block_file': os.path.relpath(bf, HERE) if btxt else None}, btxt


def widom(args):
    r, gas, btxt, nsph, delay = args
    time.sleep(delay)
    d = os.path.join(RUNS, f'r{r:.2f}', f'widom_{gas}_{NAME}')
    if os.path.exists(d):
        return r, gas, {'status': '폴더있음(이어받기 안 함)'}
    os.makedirs(d)
    cif = os.path.join(d, NAME + '.cif')
    shutil.copy(os.path.join(W, NAME + '.cif'), cif)
    open(os.path.join(d, NAME + '.block'), 'w').write(btxt)
    na, nb, nc = rg.unit_cells(rg.read(cif))
    with open(os.path.join(d, 'simulation.input'), 'w') as f:
        f.write(f"""SimulationType                MonteCarlo
NumberOfCycles                {rg.WIDOM_CYCLES}
NumberOfInitializationCycles  {rg.WIDOM_INIT}
PrintEvery                    {rg.WIDOM_CYCLES}
RestartFile                   no

Forcefield                    UFF_MOF
CutOff                        {rg.CUTOFF}
UseChargesFromCIFFile         yes
ChargeMethod                  Ewald
EwaldPrecision                1e-6

Framework 0
FrameworkName                 {NAME}
UnitCells                     {na} {nb} {nc}
ExternalTemperature           {rg.TEMP}
ExternalPressure              1e-05

Component 0 MoleculeName              {gas}
            MoleculeDefinition        TraPPE
            BlockPockets              yes
            BlockPocketsFileName      {NAME}
            WidomProbability          1.0
            CreateNumberOfMolecules   0
""")
    t0 = time.time()
    with open(os.path.join(d, 'stderr.txt'), 'w') as ef:
        try:
            subprocess.run([SIM, 'simulation.input'], cwd=d, stdout=subprocess.DEVNULL, stderr=ef, timeout=28800, check=False)
        except subprocess.TimeoutExpired:
            return r, gas, {'status': 'timeout'}
    row = {'minutes': round((time.time() - t0) / 60, 1), 'unit_cells': [na, nb, nc], 'n_spheres_per_uc': nsph, 'n_expected': nsph * na * nb * nc}
    outs = glob.glob(os.path.join(d, 'Output', 'System_0', '*.data'))
    if not outs:
        row['status'] = 'no-output'
        return r, gas, row
    txt = open(outs[0], encoding='utf-8', errors='ignore').read()
    err = open(os.path.join(d, 'stderr.txt'), encoding='utf-8', errors='ignore').read()
    m = re.search(r'Number of pockets blocked in a unitcell:\s*(\d+)', txt)
    s = re.search(r'Random number seed:\s*(\d+)', txt)
    row.update(data=os.path.relpath(outs[0], HERE), seed=int(s.group(1)) if s else None,
               n_blocked_reported=int(m.group(1)) if m else None, pockets_blocked_line='Pockets are blocked for this component' in txt,
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
    return r, gas, row


def main():
    t_start = time.time()
    if subprocess.run(['pgrep', '-xc', 'simulate'], capture_output=True, text=True).stdout.strip() not in ('', '0'):
        print('!! simulate 도는 중 — Zeo++ 안 띄움', flush=True)
        return 1
    ok, m = ff_gate.md5_gate(verbose=True)
    if not ok or m != ff_gate.FF_MD5:
        print(f'!! 힘장 관문 실패 ({m})', flush=True)
        return 3
    if not os.path.exists(os.path.join(W, NAME + '.cif')):
        open(os.path.join(W, NAME + '.cif'), 'wb').write(zipfile.ZipFile(os.path.join(HERE, 'core_pop_cifs.zip')).read(NAME + '.cif'))
    ann = {r['file']: r for r in json.load(open(os.path.join(HERE, 'core_pop_annotated.json'), encoding='utf-8'))['rows']}[NAME + '.cif']
    ref = {'source': 'core_pop_annotated.json', 'KH_CO2': ann['KH_CO2'], 'KH_CO2_err': ann['KH_CO2_err'], 'KH_N2': ann['KH_N2'],
           'KH_N2_err': ann['KH_N2_err']}
    ref['S'] = ref['KH_CO2'] / ref['KH_N2']
    ref['S_err'] = ref['S'] * math.hypot(ref['KH_CO2_err'] / ref['KH_CO2'], ref['KH_N2_err'] / ref['KH_N2'])
    z165, b165 = zeo_block(1.65)
    z182, b182 = zeo_block(1.82)
    print(f'  Zeo++ 1.65: {z165} · 1.82: {z182}', flush=True)
    if b165 is None or b182 is None:
        print('!! .block 없음 — Widom 안 함', flush=True)
        return 1
    if subprocess.run(['pgrep', '-xc', 'network'], capture_output=True, text=True).stdout.strip() not in ('', '0'):
        print('!! network 가 아직 돎 — Widom 안 함', flush=True)
        return 1
    jobs = [(1.65, 'CO2', b165, z165['n_spheres'], 0.0), (1.82, 'N2', b182, z182['n_spheres'], 15.0)]
    res = {}
    with ProcessPoolExecutor(max_workers=2) as ex:
        for fu in as_completed([ex.submit(widom, j) for j in jobs]):
            r, gas, row = fu.result()
            k = ref['KH_' + gas]
            if row.get('status') == 'ok':
                row['KH_over_unblocked'] = row['KH'] / k
                row['KH_effectively_zero'] = bool(row['KH'] - (row['KH_err'] or 0) <= 0 and row['KH'] < REL * k)
            res[gas] = row
            print(f"  [{row.get('status'):>6}] r={r:.2f} {gas} K_H {row.get('KH')} ± {row.get('KH_err')} · N {row.get('n_blocked_reported')}/"
                  f"{row.get('n_expected')} · 표지 {row.get('marker_finished')} · 씨앗 {row.get('seed')} · {row.get('minutes')} 분", flush=True)
    c, n = res.get('CO2', {}), res.get('N2', {})
    canon = {'pair': 'CO₂@1.65 / N₂@1.82', 'S_ON_unblocked': ref['S'], 'S_ON_unblocked_err': ref['S_err']}
    if c.get('status') == 'ok' and n.get('status') == 'ok' and not c.get('KH_effectively_zero') and not n.get('KH_effectively_zero'):
        S = c['KH'] / n['KH']
        eS = S * math.hypot(c['KH_err'] / c['KH'], n['KH_err'] / n['KH'])
        rS = S / ref['S']
        erS = rS * math.hypot(eS / S, ref['S_err'] / ref['S'])
        canon.update(S=S, S_err=eS, S_over_S_ON=rS, S_over_S_ON_err=erS,
                     band_1_0_to_1_4='in' if 1.0 <= rS <= 1.4 else ('above' if rS > 1.4 else 'below'))
    else:
        canon.update(S=None, note='한쪽 이상이 실패이거나 0 과 구별 안 됨 — 행 상태 참조')
    out = {'test': 'Junseok 5차 ③ — T-J1′ 새 대조 Ni pcu 정식 짝 차단 Widom', 'assign': 'ASSIGN_MAGI5B_20260925.md §Junseok 5차 ③',
           'registered': 'S_정식 / S_ON(44.4) ∈ [1.0, 1.4] · > 1.4 → 오염 대조 표지 — 판정문은 종합자',
           'machine': 'junseok', 'ff_md5': m, 'zeo': [z165, z182], 'widom': res, 'canonical': canon, 'reference_unblocked': ref,
           'gate': "stderr 에 Blocking-pocket not-found 없음 · .data N = 구 수 × 단위셀 수(등식) · Simulation finished",
           'elapsed_s': round(time.time() - t_start), 'finished': time.strftime('%F %T')}
    json.dump(out, open(OUT, 'w', encoding='utf-8'), indent=2, ensure_ascii=False)
    print(f'\n저장 {OUT}', flush=True)
    print(f"  정식 짝 S {canon.get('S')} · S/S_ON {canon.get('S_over_S_ON')} · 띠 {canon.get('band_1_0_to_1_4')}", flush=True)
    return 0


if __name__ == '__main__':
    sys.exit(main())
