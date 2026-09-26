# -*- coding: utf-8 -*-
"""MAGI-005 E-24g 후속 (Junseok) — C₂H₅ 50 % 실현 a(e24h_c2h5_050a, **막음**) 작동점 S_mix 3씨앗 · 물 지수 4씨앗(1.30 막음). "먼저 띄움"(자격은 판정 뒤).
등록 ASSIGN_MAGI5B §HKHOME 21차 후속 등록 12:20(2aba255f, 자료 0건) · 데스크탑 부탁 "E-24e 드라이버 틀 · CO₂ 1.65 · N₂ 1.82 막음 / 물 1.30 막음(E-24e 방식)".
magi5_e24e_junseok.py(E-24e) 사본 — 바꾼 것: 대상(TAG) · 막음 파일(E-24g Zeo++ e24g_zeo_runs/<tag>/block{1.65,1.82,1.30}) · 실행 폴더 · 출력 이름 ·
  기준값(물 지수 분모 K_H(CO₂ ON, 막음 1.65) · S_Henry 막음 = results_e24g_blockpockets_junseok.json, 차단 없음 S_ON = 데스크탑 Widom JSON)을 원자료에서 읽음 ·
  [A] Zeo++ 는 새로 안 돌림(같은 명령 `-ha -block 1.30 50000` 산출이 E-24g 에 있음 — 그 행을 기록만) · 물은 등록된 1.30 막음 4씨앗만(E-24e 의 서술 1.65 막음 4씨앗 뺌) ·
  E-24e 등록 예측 (1)(2) 계산 줄 뺌(이 등록엔 해당 예측 없음 — 후속 결과는 E-23 최종 1위 규칙으로 종합자가). 자 · 막음 삽입 · 관문 · 씨앗 간격은 원판 그대로.
출력 results_e24g_e24h_c2h5_050a_mix_junseok.json · results_e24g_e24h_c2h5_050a_water_junseok.json · 실행 폴더 e24g_blk_runs_e24h_c2h5_050a/.
사용: python e24g_c2h5a_block_junseok.py   (E24E_DRY=1 이면 계획 · 입력 확인만). 원판 머리말:
MAGI-005 E-24e (Junseok 16차) — 4,8-(C₂H₅)₂ 의 작동점 S_mix · 물 지수(막음 조건). 등록 ASSIGN_MAGI5B §Junseok 16차(b7efe63f, 자료 0건).

[A] Zeo++ `-ha -block 1.3 50000`(물 탐침) + `-ha -chan 1.3`(서술) — relax_tnf/e24c_c2h5_100_relaxed.cif. RASPA 보다 먼저, 한 번에 한 건 · RSS 장치.
[B] RASPA(워커 6 = 물리 코어 상한):
   · S_mix 3씨앗 = run_tj1_mix 틀(0.15/0.85 · 1e5 Pa · 298 K · 5,000+15,000 · 이동 0.5/0.3/0.1/1.0 · 같은 CIF charged_v3/e24c_c2h5_100_DDEC6.cif)
     + 성분별 BlockPockets: CO₂ = E-24c ① block1.65 · N₂ = block1.82. 판정 = run_tj1_mix.judge_output(완주 표지 + 두 성분 적재 각 1줄) + 반환코드 0
     + 성분마다 .data 머리의 "Number of pockets blocked in a unitcell" = 구 수 × 단위셀 수 · "Pockets are blocked for this component" · 막음 파일 이름 확인.
   · 물 4씨앗(등록, 막음 1.3) + 서술 4씨앗(막음 1.65) = E-24 물 Widom 틀(= E-19 · run_e22c_water: TIP5P-Ew 5자리 water.def 6fc8850d ·
     15,000 + 3,000 · 298 K · 전하 ON · read_kh(water) · 머리말 관문) + BlockPockets. 막음 관문은 E-24c 막음과 같음.
   · 작업 i 는 T0 + 15 s × i 이전엔 시작 안 함(씨앗 고유) · 끝에 씨앗 겹침 감사.
[지수] K_H(H₂O) 4씨앗 평균(± = ±̄/√4) / K_H(CO₂ ON, 막음) 2.26037e-3 ± 1.55457e-5(E-24c 막음 Widom). 단위 = d/√(±₁²+±₂²).
[등록 예측] (1) C₂H₅ S_mix(막음, 3씨앗 평균, ±̄/√3)가 CH₃ S_mix 128.62(±̄/√3 4.63)보다 1.5 단위 넘게 위.
           (2) C₂H₅ 물 지수(막음 1.3, 4씨앗)가 모체 0.0147 ± 0.0003 보다 1.5 단위 넘게 아래. (3) 서술: S_mix/S_Henry(막음) · 1.65 막음 물 지수 · 차단 없음 대비.
출력 results_e24e_c2h5_mix_junseok.json · results_e24e_c2h5_water_junseok.json(+ e24e_zeo/ · e24e_runs/). 기계적 사실뿐 — 판정은 종합자.
사용: python magi5_e24e_junseok.py   (E24E_DRY=1 이면 계획 · 입력 확인만)
"""
import fcntl
import glob
import hashlib
import json
import math
import os
import re
import shutil
import statistics as st
import subprocess
import sys
import time
from concurrent.futures import ProcessPoolExecutor, as_completed

HERE = '/home/mangwon/mof_project/21_ZIF69_MTV'
ROOT = '/home/mangwon/mof_project'
sys.path.insert(0, HERE)
import run_aryl_gcmc as rg                               # noqa: E402
import ff_gate                                           # noqa: E402
import run_tj1_mix as M                                  # noqa: E402  (judge_output · seed_of · 조건 상수만 씀)
from run_tb2_water_kh import read_kh, count_sites        # noqa: E402

TAG = 'e24h_c2h5_050a'
NAME = TAG + '_DDEC6'
CIF = os.path.join(HERE, 'charged_v3', NAME + '.cif')
RELAXED = os.path.join(HERE, 'relax_tnf', TAG + '_relaxed.cif')
ZEO = '/home/mangwon/miniconda3/envs/czeromof/bin/network'
ZBASE = os.path.join(HERE, 'e24g_zeo_runs', TAG)                  # E-24g Zeo++(이 기기) — 막음 파일 셋 다 여기
RUNS = os.path.join(HERE, f'e24g_blk_runs_{TAG}')
OUT_MIX = os.path.join(HERE, f'results_e24g_{TAG}_mix_junseok.json')
OUT_W = os.path.join(HERE, f'results_e24g_{TAG}_water_junseok.json')
ASSIGN = 'ASSIGN_MAGI5B_20260925.md §HKHOME 21차 후속 등록 12:20(2aba255f)'
BLOCK = {r: os.path.join(ZBASE, f'block{r:.2f}', TAG + '_relaxed.block') for r in (1.65, 1.82, 1.30)}
WATER_DEF = os.path.join(ROOT, '19_WaterCompetition', 'water.def')
WATER_MD5 = '6fc8850d3d22a56a17e5643f35a6f731'
NS = 50000
GUARD_MB = 5000
STAGGER = 15.0
WORKERS = 6
NOT_FOUND = "'Blocking-pocket' file not found"
BPJ = os.path.join(HERE, 'results_e24g_blockpockets_junseok.json')     # E-24g 막음 Widom(이 기기) — 물 지수 분모 · S_Henry(막음)
UBJ = os.path.join(HERE, f'results_magi5_e3_{TAG}_widom_hkhome.json')   # 데스크탑 차단 없음 Widom — 서술


def _refs():
    """기준값은 원자료 JSON 에서 읽음(판정표 값 입력 금지, 2026-09-26 규칙). 막음 Widom 행이 ok · 0 아님이어야 함."""
    e = json.load(open(BPJ, encoding='utf-8'))['per_structure'][TAG]
    w = e['rows']['on_CO2@1.65']
    if w.get('status') != 'ok' or w.get('KH_effectively_zero') or e.get('S_ON_blocked') is None:
        raise SystemExit(f'!! 막음 Widom 기준 없음 · 실패 · 0 ({BPJ})')
    u = [r for r in json.load(open(UBJ, encoding='utf-8'))['rows'] if r['charges'] == 'on'][0]
    return w['KH'], w['KH_err'], e['S_ON_blocked'], e['S_ON_blocked_err'], u['selectivity']


KCO2, EKCO2, SH_BLOCK, ESH_BLOCK, SH_UNBLOCK = _refs()
MOVES = ('            TranslationProbability    0.5\n'
         '            RotationProbability       0.3\n'
         '            ReinsertionProbability    0.1\n'
         '            SwapProbability           1.0\n'
         '            CreateNumberOfMolecules   0\n')


def avail_mb():
    for ln in open('/proc/meminfo'):
        if ln.startswith('MemAvailable:'):
            return int(ln.split()[1]) // 1024
    return 0


def rss_mb(pid):
    try:
        for ln in open(f'/proc/{pid}/status'):
            if ln.startswith('VmRSS:'):
                return int(ln.split()[1]) // 1024
    except OSError:
        pass
    return 0


def run_guarded(args, cwd, out):
    t0 = time.time()
    with open(os.path.join(cwd, out), 'w') as fh:
        p = subprocess.Popen(args, cwd=cwd, stdout=fh, stderr=subprocess.STDOUT)
        peak, stopped = 0, False
        while p.poll() is None:
            peak = max(peak, rss_mb(p.pid))
            if avail_mb() < GUARD_MB:
                p.kill()
                stopped = True
            time.sleep(1)
    return p.returncode, round(time.time() - t0, 1), peak, stopped


def zeo_water():
    """[A] 새로 안 돌림 — E-24g Zeo++(이 기기, results_e24g_access_junseok.json)의 이 대상 1.30 행을 기록만(같은 명령 -ha -block 1.30 50000 · -chan 1.30)."""
    row = [r for r in json.load(open(os.path.join(HERE, 'results_e24g_access_junseok.json'), encoding='utf-8'))['rows'] if r['tag'] == TAG][0]
    return {'source': 'results_e24g_access_junseok.json', **row['r1.30']}


def nsph(r):
    return int(open(BLOCK[r]).read().split()[0])


def block_audit(txt):
    """성분별(Component N [이름] (Adsorbate molecule) 절) 막음 줄 — 첫 출현만."""
    cur, out = None, {}
    for ln in txt.splitlines():
        m = re.match(r'Component (\d+) \[(\w+)\] \(Adsorbate molecule\)', ln)
        if m:
            cur = m.group(2)
            out.setdefault(cur, {'n_blocked': None, 'blocked_line': False, 'block_file': None})
            continue
        if cur is None:
            continue
        c = out[cur]
        m = re.search(r'Number of pockets blocked in a unitcell:\s*(\d+)', ln)
        if m and c['n_blocked'] is None:
            c['n_blocked'] = int(m.group(1))
        if 'Pockets are blocked for this component' in ln:
            c['blocked_line'] = True
        m = re.search(r'Block-pockets Filename:\s*(\S+)', ln)
        if m and c['block_file'] is None:
            c['block_file'] = m.group(1)
    return out


def wait_turn(i, t0):
    """작업 i 는 T0 + 15 s × i 이전엔 시작 안 함. 풀의 뒷작업은 자리가 빈 순간 뜨므로, 두 작업이 같은 초에 끝나면 같은 초에 떠 씨앗(착수 초)이
    같아질 수 있음 → 잠금 파일로 착수 사이를 2 s 이상 벌림."""
    w = t0 + i * STAGGER - time.time()
    if w > 0:
        time.sleep(w)
    with open(os.path.join(RUNS, '.start.lock'), 'a+') as f:
        fcntl.flock(f, fcntl.LOCK_EX)
        try:
            f.seek(0)
            s = f.read().split()
            gap = (float(s[-1]) + 2.0 - time.time()) if s else 0
            if gap > 0:
                time.sleep(gap)
            f.write(f'{time.time():.3f}\n')
            f.flush()
        finally:
            fcntl.flock(f, fcntl.LOCK_UN)


def mix_job(args):
    i, k, t0 = args
    wait_turn(i, t0)
    d = os.path.join(RUNS, f'mix_{TAG}_s{k}')
    os.makedirs(d)
    shutil.copy(CIF, os.path.join(d, NAME + '.cif'))
    shutil.copy(BLOCK[1.65], os.path.join(d, f'{TAG}_co2.block'))
    shutil.copy(BLOCK[1.82], os.path.join(d, f'{TAG}_n2.block'))
    na, nb, nc = rg.unit_cells(rg.read(CIF))
    with open(os.path.join(d, 'simulation.input'), 'w') as f:
        f.write(f"""SimulationType                MonteCarlo
NumberOfCycles                {M.CYCLES}
NumberOfInitializationCycles  {M.INIT}
PrintEvery                    {M.CYCLES}
RestartFile                   no

Forcefield                    UFF_MOF
CutOff                        {rg.CUTOFF}
UseChargesFromCIFFile         yes
ChargeMethod                  Ewald
EwaldPrecision                1e-6

Framework 0
FrameworkName                 {NAME}
UnitCells                     {na} {nb} {nc}
ExternalTemperature           {M.TEMP}
ExternalPressure              {M.P_TOT}

Component 0 MoleculeName              CO2
            MoleculeDefinition        TraPPE
            MolFraction               {M.X_CO2:.6f}
            BlockPockets              yes
            BlockPocketsFileName      {TAG}_co2
{MOVES}
Component 1 MoleculeName              N2
            MoleculeDefinition        TraPPE
            MolFraction               {1 - M.X_CO2:.6f}
            BlockPockets              yes
            BlockPocketsFileName      {TAG}_n2
{MOVES}""")
    tt = time.time()
    with open(os.path.join(d, 'stderr.txt'), 'w') as ef:
        try:
            cp = subprocess.run([rg.SIMULATE, 'simulation.input'], cwd=d, stdout=subprocess.DEVNULL, stderr=ef, timeout=259200, check=False)
            rc = cp.returncode
        except subprocess.TimeoutExpired:
            return 'mix', k, {'status': 'timeout'}
    row = {'seed_idx': k, 'unit_cells': [na, nb, nc], 'returncode': rc, 'minutes': round((time.time() - tt) / 60, 1),
           'n_expected': {'CO2': nsph(1.65) * na * nb * nc, 'N2': nsph(1.82) * na * nb * nc}}
    outs = glob.glob(os.path.join(d, 'Output', 'System_0', '*.data'))
    if len(outs) != 1:
        row['status'] = f'.data {len(outs)}개'
        return 'mix', k, row
    txt = open(outs[0], encoding='utf-8', errors='ignore').read()
    err = open(os.path.join(d, 'stderr.txt'), encoding='utf-8', errors='ignore').read()
    v, stj = M.judge_output(outs[0])
    ba = block_audit(txt)
    row.update(seed=M.seed_of(outs[0]), judge=stj, block=ba, stderr_not_found=NOT_FOUND in err, data=os.path.relpath(outs[0], HERE))
    blk_ok = all(ba.get(g, {}).get('blocked_line') and ba.get(g, {}).get('n_blocked') == row['n_expected'][g] for g in ('CO2', 'N2'))
    if v:
        (nc2, ec2), (nn2, en2) = v['CO2'], v['N2']
        row.update(N_CO2=nc2, N_CO2_err=ec2, N_N2=nn2, N_N2_err=en2)
        if nc2 > 0 and nn2 > 0:
            s = (nc2 / nn2) / (M.X_CO2 / (1 - M.X_CO2))
            row.update(S_mix=s, S_mix_err=s * math.hypot(ec2 / nc2, en2 / nn2))
    row['status'] = ('ok' if (stj == 'ok' and rc == 0 and blk_ok and not row['stderr_not_found'] and row.get('S_mix')) else
                     f"실패(judge {stj} · rc {rc} · 막음 {blk_ok} · not-found {row['stderr_not_found']})")
    for sub in ('VTK', 'Movies', 'Restart'):
        shutil.rmtree(os.path.join(d, sub), ignore_errors=True)
    return 'mix', k, row


def water_job(args):
    i, r, k, t0 = args
    wait_turn(i, t0)
    d = os.path.join(RUNS, f'water_b{r:.2f}_{TAG}_s{k}')
    os.makedirs(d)
    shutil.copy(CIF, os.path.join(d, NAME + '.cif'))
    shutil.copy(WATER_DEF, os.path.join(d, 'water.def'))
    shutil.copy(BLOCK[r], os.path.join(d, NAME + '.block'))
    na, nb, nc = rg.unit_cells(rg.read(CIF))
    with open(os.path.join(d, 'simulation.input'), 'w') as f:
        f.write(f"""SimulationType                MonteCarlo
NumberOfCycles                15000
NumberOfInitializationCycles  3000
PrintEvery                    1500
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
            BlockPockets              yes
            BlockPocketsFileName      {NAME}
            WidomProbability          1.0
            CreateNumberOfMolecules   0
""")
    tt = time.time()
    with open(os.path.join(d, 'stderr.txt'), 'w') as ef:
        cp = subprocess.run([rg.SIMULATE, 'simulation.input'], cwd=d, stdout=subprocess.DEVNULL, stderr=ef, check=False)
    row = {'block_radius': r, 'seed_idx': k, 'unit_cells': [na, nb, nc], 'returncode': cp.returncode, 'minutes': round((time.time() - tt) / 60, 1),
           'n_expected': nsph(r) * na * nb * nc}
    outs = sorted(glob.glob(os.path.join(d, 'Output', 'System_0', '*.data')))
    if len(outs) != 1:
        row['status'] = f'.data {len(outs)}개'
        return 'water', (r, k), row
    txt = open(outs[0], encoding='utf-8', errors='ignore').read()
    err = open(os.path.join(d, 'stderr.txt'), encoding='utf-8', errors='ignore').read()
    kh, ekh, rerr = read_kh(outs[0], comp='water')
    hg = ff_gate.read_ff_header(outs[0])
    ba = block_audit(txt).get('water', {})
    row.update(KH_water=kh, KH_water_err=ekh, read_error=rerr, header_gate_ok=hg.get('ok'), marker_finished=rg.finished(outs[0]),
               seed=M.seed_of(outs[0]), water_sites_in_rundir=count_sites(os.path.join(d, 'water.def')), block=ba,
               stderr_not_found=NOT_FOUND in err, data=os.path.relpath(outs[0], HERE))
    blk_ok = ba.get('blocked_line') and ba.get('n_blocked') == row['n_expected'] and not row['stderr_not_found']
    row['status'] = ('ok' if (kh is not None and hg.get('ok') and row['marker_finished'] and row['water_sites_in_rundir'] == 5 and cp.returncode == 0 and blk_ok)
                     else f"실패(관문 {hg.get('ok')} · 표지 {row['marker_finished']} · rc {cp.returncode} · 막음 {blk_ok})")
    for sub in ('VTK', 'Movies', 'Restart'):
        shutil.rmtree(os.path.join(d, sub), ignore_errors=True)
    return 'water', (r, k), row


def summarize(mix, water, zeo, t_start, ffm, wm, final=False):
    ok = [mix[k] for k in sorted(mix) if mix[k].get('status') == 'ok']
    ms = {'n': len(ok), 'S_mix_each': [x['S_mix'] for x in ok], 'S_mix_err_each': [x['S_mix_err'] for x in ok], 'seeds': [x['seed'] for x in ok]}
    if ok:
        ms['S_mix_mean'] = st.mean(ms['S_mix_each'])
        ms['S_mix_mean_err'] = st.mean(ms['S_mix_err_each']) / math.sqrt(len(ok))
        ms['seed_SD'] = st.stdev(ms['S_mix_each']) if len(ok) > 1 else None
        r = ms['S_mix_mean'] / SH_BLOCK
        ms['ratio_Smix_over_SHenry_blocked'] = r
        ms['ratio_err'] = r * math.hypot(ms['S_mix_mean_err'] / ms['S_mix_mean'], ESH_BLOCK / SH_BLOCK)
        ms['ratio_vs_unblocked_SHenry_descriptive'] = ms['S_mix_mean'] / SH_UNBLOCK
    json.dump({'test': f'MAGI-005 E-24g 후속 — {TAG}(C₂H₅ 50 % a) S_mix 3씨앗(성분별 막음)', 'assign': ASSIGN, 'machine': 'junseok', 'ported_from': 'magi5_e24e_junseok.py (E-24e)',
               'protocol': 'run_tj1_mix 틀(0.15/0.85 · 1e5 Pa · 298 K · 5,000+15,000) + CO₂ BlockPockets block1.65 · N₂ block1.82 (E-24g Zeo++ e24g_zeo_runs)',
               'reference': {'S_Henry_blocked': [SH_BLOCK, ESH_BLOCK], 'S_Henry_unblocked_descriptive': SH_UNBLOCK, 'src': [os.path.basename(BPJ), os.path.basename(UBJ)]},
               'ff_md5': ffm, 'rows': [mix[k] for k in sorted(mix)], 'summary': ms, 'final': final, 'written': time.strftime('%F %T'), 'elapsed_s': round(time.time() - t_start),
               'note': '기계적 사실뿐 — 판정은 종합자. S_mix ± = 두 적재 상대 ± 제곱합, 평균 ± = ±̄/√3.'},
              open(OUT_MIX, 'w', encoding='utf-8'), indent=2, ensure_ascii=False)
    wsum = {}
    for r in (1.30,):
        rows = [water[x] for x in sorted(water) if x[0] == r and water[x].get('status') == 'ok']
        s = {'n': len(rows), 'KH_each': [x['KH_water'] for x in rows], 'KH_err_each': [x['KH_water_err'] for x in rows], 'seeds': [x['seed'] for x in rows]}
        if rows:
            s['KH_mean'] = st.mean(s['KH_each'])
            s['KH_mean_err'] = st.mean(s['KH_err_each']) / math.sqrt(len(rows))
            s['seed_SD_rel'] = st.stdev(s['KH_each']) / s['KH_mean'] if len(rows) > 1 else None
            ix = s['KH_mean'] / KCO2
            s['index'] = ix
            s['index_err'] = ix * math.hypot(s['KH_mean_err'] / s['KH_mean'], EKCO2 / KCO2)
        wsum[f'block{r:.2f}'] = s
    json.dump({'test': f'MAGI-005 E-24g 후속 — {TAG}(C₂H₅ 50 % a) 물 Widom 4씨앗(막음 1.3)', 'assign': ASSIGN, 'ported_from': 'magi5_e24e_junseok.py (E-24e)',
               'machine': 'junseok', 'protocol': 'E-24 물 Widom 틀(= E-19: TIP5P-Ew 5자리 · 15,000 + 3,000 · 298 K · 전하 ON · read_kh(water) · 머리말 관문) + BlockPockets',
               'ff_md5': ffm, 'water_def_md5': wm, 'zeo_water_probe': zeo,
               'denominator_KH_CO2_ON_blocked': [KCO2, EKCO2], 'denominator_src': os.path.basename(BPJ) + ' ' + TAG + ' on_CO2@1.65',
               'rows': [water[x] for x in sorted(water)], 'summary': wsum, 'final': final, 'written': time.strftime('%F %T'), 'elapsed_s': round(time.time() - t_start),
               'note': '기계적 사실뿐 — 판정은 종합자. 평균 ± = ±̄/√4, 지수 ± = 두 상대 ± 제곱합.'},
              open(OUT_W, 'w', encoding='utf-8'), indent=2, ensure_ascii=False)
    return ms, wsum


def main():
    t_start = time.time()
    ok, ffm = ff_gate.md5_gate(verbose=True)
    wm = hashlib.md5(open(WATER_DEF, 'rb').read()).hexdigest()
    if not ok or ffm != ff_gate.FF_MD5 or wm != WATER_MD5 or count_sites(WATER_DEF) != 5:
        print(f'!! 관문 실패(힘장 {ffm} · water.def {wm})', flush=True)
        return 3
    for r in (1.65, 1.82, 1.30):
        if not os.path.exists(BLOCK[r]):
            print(f'!! 막음 파일 없음 {BLOCK[r]}', flush=True)
            return 2
    print(f'E-24g 후속 {TAG} — CIF {os.path.relpath(CIF, HERE)} · 막음 CO₂ {nsph(1.65)} 구 · N₂ {nsph(1.82)} 구 · 물 {nsph(1.30)} 구 · 단위셀 {rg.unit_cells(rg.read(CIF))} · '
          f'워커 {WORKERS} · S_mix 3 + 물 1.3 ×4 · 기준(원자료) K_H(CO₂ ON 막음) {KCO2} ± {EKCO2} · S_Henry 막음 {SH_BLOCK} ± {ESH_BLOCK} · 차단 없음 {SH_UNBLOCK}', flush=True)
    if os.environ.get('E24E_DRY'):
        return 0
    n = lambda x: subprocess.run(['pgrep', '-xc', x], capture_output=True, text=True).stdout.strip()
    if n('simulate') not in ('', '0') or n('network') not in ('', '0') or n('lmp_serial') not in ('', '0'):
        print('!! simulate · network · lmp_serial 중 도는 것 있음 — 중단', flush=True)
        return 1
    for p in (RUNS, OUT_MIX, OUT_W):
        if os.path.exists(p):
            print(f'!! 이전 산출 있음 {p} — 중단', flush=True)
            return 1
    zeo = zeo_water()
    print(f'[A] 새로 안 돌림 — E-24g Zeo++ 1.30 기록: {json.dumps(zeo, ensure_ascii=False)[:300]}', flush=True)
    os.makedirs(RUNS)
    t0 = time.time() + 2
    jobs = [('mix', (i, k, t0)) for i, k in enumerate((1, 2, 3))]
    jobs += [('water', (3 + i, 1.30, k, t0)) for i, k in enumerate((1, 2, 3, 4))]
    print(f'[B] RASPA {len(jobs)}작업 · 워커 {WORKERS} 착수 {time.strftime("%T")}', flush=True)
    mix, water = {}, {}
    with ProcessPoolExecutor(max_workers=WORKERS) as ex:
        futs = [ex.submit(mix_job if kind == 'mix' else water_job, a) for kind, a in jobs]
        for fu in as_completed(futs):
            kind, key, row = fu.result()
            (mix if kind == 'mix' else water)[key] = row
            summarize(mix, water, zeo, t_start, ffm, wm, final=False)      # 중간 저장(final False)
            if kind == 'mix':
                print(f"  [{row.get('status')[:6]:>6}] S_mix s{key} {row.get('S_mix')} ± {row.get('S_mix_err')} · N_CO2 {row.get('N_CO2')} · N_N2 {row.get('N_N2')} · "
                      f"막음 {json.dumps(row.get('block'), ensure_ascii=False)} · rc {row.get('returncode')} · 씨앗 {row.get('seed')} · {row.get('minutes')} 분", flush=True)
            else:
                print(f"  [{row.get('status')[:6]:>6}] 물 막음{key[0]:.2f} s{key[1]} K_H {row.get('KH_water')} ± {row.get('KH_water_err')} · N {row.get('block', {}).get('n_blocked')}/"
                      f"{row.get('n_expected')} · 관문 {row.get('header_gate_ok')} · 표지 {row.get('marker_finished')} · rc {row.get('returncode')} · 씨앗 {row.get('seed')} · {row.get('minutes')} 분", flush=True)
    seeds = [x.get('seed') for x in list(mix.values()) + list(water.values())]
    print(f'씨앗 {len(seeds)}개 · 겹침 {len(seeds) - len(set(seeds))}', flush=True)
    ms, wsum = summarize(mix, water, zeo, t_start, ffm, wm, final=True)
    print(f'\n저장 {OUT_MIX}\n저장 {OUT_W}', flush=True)
    print(f"  S_mix {json.dumps({k: v for k, v in ms.items() if not isinstance(v, list)}, ensure_ascii=False)}", flush=True)
    for k, s in wsum.items():
        print(f"  물 {k} {json.dumps({kk: v for kk, v in s.items() if not isinstance(v, list)}, ensure_ascii=False)}", flush=True)
    return 0


if __name__ == '__main__':
    sys.exit(main())
