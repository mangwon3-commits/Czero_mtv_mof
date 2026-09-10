#!/usr/bin/env python
"""T-NF 시험용 **일반 골격** CO₂/H₂O GCMC 드라이버 (2026-09-10 신설).

등록문은 `21_ZIF69_MTV/TNF_REGISTRATION_20260910.md` 입니다. 이 파일은 그 등록의
T-NF-1(MUF-16 이원) · T-NF-0(순수 물 등온) · T-NF-2(ZIF-94 RH0/RH90, 2온도)를
**한 러너로** 돌기 위해 있습니다.

    ⚠️ 새 러너입니다. 기존 러너(`run_water.py` · `run_water_v3w.py` …)는
       **한 줄도 고치지 않았습니다.** 살아 있는 계열이 그 위에서 돌고 있습니다.

## 무엇이 v3w 와 같고 무엇이 다른가

**같아야 하는 것 — `CLAUDE.md §1` 고정값. 입력 템플릿을 `run_water.py:214-235`
에서 글자 그대로 옮겼습니다**(사이클 5,000+15,000 · `PrintEvery = 생산 사이클` ·
`RestartFile no` · `ContinueAfterCrash yes` · `WriteBinaryRestartFileEvery 500` ·
`Forcefield UFF_MOF` · `CutOff 12.0` · `UseChargesFromCIFFile yes` ·
`ChargeMethod Ewald` · `EwaldPrecision 1e-6` · 이동 확률 다섯 줄 ·
CO₂ 는 `MoleculeDefinition TraPPE`(기하만! LJ·전하는 UFF_MOF) ·
물은 `19_WaterCompetition/water.def`(5자리 TIP5P-Ew)를 **실행 폴더로 복사**해
같은 이름 `TraPPE` 로 가로채는 방식).

**다른 것 — 등록문 §0 의 슈퍼셀 예외뿐입니다.**
`UnitCells` 를 2×2×2 로 박지 않고 **셀에서 계산**합니다: 축마다 수직 폭이
≥ 24 Å 이 되는 최소 정수 복제. ZIF-69 v3 셀(26.084/26.084/19.408, 수직 폭
22.59/22.59/19.41)에서는 이 규칙이 **2 2 2 를 그대로 돌려줍니다** — 즉 v3/v3w 와
숫자가 갈리지 않고, 비-ZIF 골격(MUF-16 b=4.42 Å 등)에서만 달라집니다.
그 밖에 온도·압력은 CLI 로 받습니다(등록문 §1~§3 의 조건).

> **이 예외로 얻은 수는 ZIF-69 v3/v3w 표와 나란히 순위 매기지 않습니다**(등록문 §0).

## 힘장 관문 (FF_GATES_20260907.md)

    파일 관문    착수 **전** md5 == ff_gate.FF_MD5    아니면 **즉시 중단**(--dry-run 도)
    머리말 관문  실행 폴더 **하나씩** 출력 .data 머리말을 읽어 행에 찍습니다
                 (`ff_gate.read_ff_header`; 폴더 뿌리를 주면 한 실행이 다른
                  실행을 대신 통과시킵니다 — 09-07 `5c30af6`)

    ⚠️ **물이 없는 실행(RH0, CO₂ 단일)에는 머리말 관문이 답하지 않습니다.**
       `Hw`·`Lw` 쌍이 애초에 인쇄되지 않기 때문입니다. 그 행은 `ff_check.ok`
       을 **null** 로 두고 `note` 에 그렇게 적습니다. **false 로 적으면 안 됩니다**
       — "검사에 걸렸다" 와 "검사 대상이 아니다" 는 다릅니다.

## 씨앗

RASPA 는 `RandomSeed` 를 안 받는 이 빌드에서 **착수 시각(초)** 으로 씨앗을 만듭니다
(`RASPA_SEED_20260828.md` §1). 그래서 같은 초에 뜬 작업들이 **같은 난수열**을 받습니다
(09-07 T-B2w 39행 중 6행이 그렇게 충돌). `--seed-stagger` 초만큼 어긋내 띄우고,
**끝난 뒤 씨앗 중복을 세어 결과 JSON 에 적습니다**(`seed_collisions`).
씨앗은 **폴더가 살아 있을 때** 출력 머리말에서 회수합니다 — `CLAUDE.md §7` 이
결과 JSON 이 있으면 실행 폴더를 지워도 된다고 하므로 미루면 함께 사라집니다.

## 이어받기

출력 `.data` 에 `Simulation finished` 가 있고 물 알짜전하가 0 이면 `cached` 로
회수합니다. **이어받기는 어떤 설정으로 만들어졌는지 보지 않습니다**(`CLAUDE.md §3`)
— 조건(T·압력·복제)을 바꿨으면 `--runs-root` 를 **새로** 주거나 폴더를 지우십시오.
폴더 이름에 `rh·tag·T·pCO2` 를 전부 박아 둔 것이 그 사고를 좁히는 장치입니다.

## 사용

    python run_tnf.py --cif charged_v3/mslm025e1_DDEC6.cif --tag dryrun_mslm025e1 \
        --temp 303 --pco2 0.14 --rh 0,50,70,90 --dry-run --runs-root 21_ZIF69_MTV/tnf_dryrun

    --pco2 0        순수 물 등온 (CO₂ 성분 자체를 뺍니다) — T-NF-0
    --pco2 0.14 --rh 0   CO₂ 단일 (물 성분을 뺍니다)
    --psat <Pa>     주지 않으면 T 에서 계산 (아래 P_SAT 참조)

⚠️ **T-NF-2 의 373 K 다리는 `--psat 3169` 를 손으로 주어야 합니다.** 등록문 §3 이
373 K 에서도 p_H₂O 를 **2852.1 Pa 로 고정**(= 0.9 × 3169)한다고 적었기 때문입니다.
373 K 의 실제 P_sat(≈101 kPa)로 계산하면 등록과 다른 시험이 됩니다.
"""
import argparse
import glob
import hashlib
import json
import math
import os
import re
import shutil
import socket
import subprocess
import sys
import time
from multiprocessing import Pool

import numpy as np
from ase.io import read

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

# `ff_gate` 는 프로젝트 안의 무엇도 import 하지 않으므로 어디서 불러도 안전합니다
# (FF_GATES_20260907.md §4·§7). **`run_water*` 는 import 하지 않습니다** — 그 모듈들은
# 서로의 전역(`rw.RUNS` 등)을 덮어써서 import 하는 것만으로 산출물이 남의 계열 폴더로
# 샙니다(같은 문서 §8). 파서 세 개는 그래서 여기에 **복사**해 두었습니다.
from ff_gate import (FF_MD5, FF_TAG, OWOW_EPS, ZERO_PAIRS,  # noqa: E402
                     ff_path, md5_gate, read_ff_header)

WATER_DEF = os.path.join(HERE, '..', '19_WaterCompetition', 'water.def')
SIMULATE = shutil.which('simulate') or os.path.expanduser(
    '~/miniconda3/envs/czeromof/bin/simulate')

# --- CLAUDE.md §1 고정값. 여기서 바꾸면 기존 결과와 합칠 수 없습니다 ---------
CYCLES, INIT = 15000, 5000
CUTOFF = 12.0
CRASH_EVERY = 500
MIN_WIDTH = 2.0 * CUTOFF          # 등록문 §0: 축마다 수직 폭 ≥ 24 Å
TIMEOUT = 259200                  # 72 h (run_water.py 의 교훈: 8 h 상수가 결과 5건을 날렸습니다)

# --- P_sat -----------------------------------------------------------------
# **저장소에 등록된 값이 먼저입니다.** 이 두 수가 기존 표(그리고 등록문 §1·§2)의
# 분모이므로 공식이 소수점에서 갈리면 옛 행과 못 합칩니다.
#     298 K -> 3169 Pa   (run_water.py:48 · T-NF-0 등록)
#     303 K -> 4247 Pa   (T-NF-1 등록: RH50/70/90 = 2123.5/2972.9/3822.3 Pa)
# 표에 없는 T 는 Buck(1981) 식으로 계산하고 **그렇게 계산했다고 출력에 적습니다.**
# (Buck 은 위 두 점에서 3168.4 / 4244.2 Pa 로 0.02~0.07 % 낮게 나옵니다. 그래서
#  표를 이깁니다 — 공식이 옳고 표가 틀린 것이 아니라, **표가 등록된 자**입니다.)
P_SAT_TABLE = {298: 3169.0, 303: 4247.0}


def p_sat(temp):
    """(값 Pa, 출처 문자열)."""
    key = int(round(temp))
    if key in P_SAT_TABLE and abs(temp - key) < 0.2:
        return P_SAT_TABLE[key], f'저장소 등록값 ({key} K)'
    tc = temp - 273.15
    v = 611.21 * math.exp((18.678 - tc / 234.5) * (tc / (257.14 + tc)))
    return v, 'Buck(1981) 계산값 — **등록 표에 없는 온도입니다**'


# --- 복제 수 (등록문 §0 의 예외 규칙) ---------------------------------------
def unit_cells(cif):
    """축마다 **수직 폭**(perpendicular width)이 ≥ 24 Å 이 되는 최소 정수 복제.

    수직 폭은 축 길이가 아니라 `V / |a_j × a_k|` 입니다 — 비스듬한 셀에서 축 길이로
    재면 최소상 조건을 깨고도 통과합니다. 반환: (reps, widths).
    """
    cell = np.array(read(cif).get_cell())
    vol = abs(np.linalg.det(cell))
    reps, widths = [], []
    for i in range(3):
        j, k = (i + 1) % 3, (i + 2) % 3
        w = vol / np.linalg.norm(np.cross(cell[j], cell[k]))
        widths.append(w)
        reps.append(max(1, int(math.ceil(MIN_WIDTH / w))))
    return reps, widths


# --- 출력 파서 (run_water.py:103-135 와 같은 규약) ---------------------------
def parse_components(path):
    """성분별 (평균 절대 로딩 mol/kg, ±). RASPA 는 Component 블록마다 같은 문구를
    반복하므로 어느 성분 블록인지 추적해야 합니다."""
    out, cur = {}, None
    for line in open(path, encoding='utf-8', errors='ignore'):
        m = re.search(r'Component\s+(\d+)\s+\[(\w+)\]', line)
        if m:
            cur = m.group(2)
        if cur and 'Average loading absolute [mol/kg framework]' in line:
            v = re.search(r':?\s*([0-9.eE+-]+)\s*\+/-\s*([0-9.eE+-]+)', line)
            if v and cur not in out:
                out[cur] = (float(v.group(1)), float(v.group(2)))
    return out


def net_charge_ok(path):
    """5자리 물 정의가 실제로 잡혔는지 (3자리를 쓰면 분자당 알짜 +0.482)."""
    for line in open(path, encoding='utf-8', errors='ignore'):
        if 'net charge of' in line:
            m = re.search(r'net charge of\s*([0-9.eE+-]+)', line)
            if m and abs(float(m.group(1))) > 1e-4:
                return False
    return True


def finished(path):
    """완주 판정. **파일 존재만으로는 안 됩니다** — 중간에 죽어도 수십 MB 를 남깁니다."""
    try:
        return 'Simulation finished' in open(
            path, encoding='utf-8', errors='ignore').read()
    except OSError:
        return False


def read_seed(d):
    """그 작업의 RASPA 난수 씨앗을 **출력 머리말에서** 회수합니다
    (`run_water_v3w.read_seed` 와 같은 정규식)."""
    od = os.path.join(d, 'Output', 'System_0')
    if not os.path.isdir(od):
        return None
    for fn in sorted(x for x in os.listdir(od) if x.endswith('.data')):
        with open(os.path.join(od, fn), encoding='utf-8', errors='ignore') as f:
            for ln in f:
                m = re.match(r'\s*Random number seed:\s*(\d+)', ln)
                if m:
                    return int(m.group(1))
                if ln.startswith('Number of cycles'):
                    break
    return None


# --- 입력 작성 --------------------------------------------------------------
MOVES = ('            TranslationProbability    0.5\n'
         '            RotationProbability       0.3\n'
         '            ReinsertionProbability    0.1\n'
         '            SwapProbability           1.0\n'
         '            CreateNumberOfMolecules   0\n')


def job_dir(cfg, rh):
    """폴더 이름에 조건을 전부 박습니다 — 이어받기가 설정을 보지 않으므로
    (`CLAUDE.md §3`) **이름이 유일한 방벽**입니다."""
    return os.path.join(cfg['runs_root'],
                        f'rh{int(round(rh * 100)):02d}_{cfg["tag"]}'
                        f'_{cfg["temp"]:g}K_co2{cfg["pco2"]:g}bar'
                        + (f'_pre{cfg["preload"]}' if cfg.get('preload') else ''))


def write_input(cfg, rh):
    """실행 폴더를 만들고 `simulation.input`(+CIF, 필요하면 water.def)을 씁니다.
    반환: (폴더, 입력 문자열, 압력 dict)."""
    d = job_dir(cfg, rh)
    os.makedirs(d, exist_ok=True)
    shutil.copy(cfg['cif'], os.path.join(d, cfg['fw'] + '.cif'))

    p_co2 = cfg['pco2'] * 1e5                      # bar -> Pa
    p_h2o = cfg['psat'] * rh
    p_tot = p_co2 + p_h2o
    # v3w 규약 그대로: **ExternalPressure = 전체 압력**, 성분은 **분압비 몰분율**.
    # RASPA 가 각 성분의 퓨가시티를 이 둘에서 만듭니다(아래 '의문' 주석 참조).
    comps, n = '', 0
    if p_co2 > 0:
        comps += (f"Component {n} MoleculeName              CO2\n"
                  f"            MoleculeDefinition        TraPPE\n"
                  f"            MolFraction               {p_co2 / p_tot:.6f}\n"
                  f"{MOVES}")
        n += 1
    if p_h2o > 0:
        shutil.copy(WATER_DEF, os.path.join(d, 'water.def'))
        comps += (('\n' if n else '')
                  + f"Component {n} MoleculeName              water\n"
                  f"            MoleculeDefinition        TraPPE\n"
                  f"            MolFraction               {p_h2o / p_tot:.6f}\n"
                  f"{MOVES.replace('CreateNumberOfMolecules   0', 'CreateNumberOfMolecules   ' + str(cfg.get('preload') or 0))}")

    na, nb, nc = cfg['reps']
    txt = f"""SimulationType                MonteCarlo
NumberOfCycles                {CYCLES}
NumberOfInitializationCycles  {INIT}
PrintEvery                    {CYCLES}
RestartFile                   no
ContinueAfterCrash            yes
WriteBinaryRestartFileEvery   {CRASH_EVERY}

Forcefield                    UFF_MOF
CutOff                        {CUTOFF}
UseChargesFromCIFFile         yes
ChargeMethod                  Ewald
EwaldPrecision                1e-6

Framework 0
FrameworkName                 {cfg['fw']}
UnitCells                     {na} {nb} {nc}
ExternalTemperature           {cfg['temp']:.1f}
ExternalPressure              {p_tot:.4f}

{comps}"""
    with open(os.path.join(d, 'simulation.input'), 'w') as f:
        f.write(txt)
    return d, txt, {'p_co2': p_co2, 'p_h2o': p_h2o, 'p_tot': p_tot}


# --- 한 작업 ----------------------------------------------------------------
def guard_crash_restart(d, tag):
    """이어받기 경로에서 RASPA 가 SIGSEGV 를 내면 무한 재시도가 됩니다
    (`run_water.guard_crash_restart` 와 같은 장치). 한 번만 이어받고 그다음은 처음부터."""
    cr = os.path.join(d, 'CrashRestart')
    mark = os.path.join(d, '.resume_attempted')
    if not os.path.isdir(cr):
        return
    if os.path.exists(mark):
        print(f'  [체크포인트 폐기] {tag} — 이어받기가 이미 한 번 실패했습니다.', flush=True)
        shutil.rmtree(cr, ignore_errors=True)
        os.remove(mark)
        return
    open(mark, 'w').close()
    print(f'  [이어받기 시도] {tag}', flush=True)


def ff_check_of(d, want_water):
    """**실행 폴더 하나**의 머리말 관문. 물이 없는 실행은 판정 대상이 아닙니다."""
    if not want_water:
        return {'ok': None,
                'note': '물 성분 없음 — Hw/Lw 쌍이 인쇄되지 않아 머리말 관문의 '
                        '대상이 아닙니다. 파일 관문(md5)만으로 받칩니다.'}
    c = read_ff_header(d)
    c['ok'] = (all(c.get(k) == 'ZERO_POTENTIAL' for k in ZERO_PAIRS)
               and c.get('OwOw_eps') is not None
               and abs(c['OwOw_eps'] - OWOW_EPS) < 1e-3)
    return c


def run_one(arg):
    i, cfg, rh = arg
    tagj = f'rh{int(round(rh * 100)):02d}_{cfg["tag"]}'
    d = job_dir(cfg, rh)
    want_water = cfg['psat'] * rh > 0

    done = glob.glob(os.path.join(d, 'Output', 'System_0', '*.data'))
    if done and finished(done[0]) and net_charge_ok(done[0]):
        return row(cfg, rh, parse_components(done[0]), d, want_water, 'cached')

    # 씨앗 = 착수 시각(초). 같은 초에 두 개가 뜨면 **같은 난수열**입니다.
    time.sleep((i % max(1, cfg['workers'])) * cfg['stagger'])

    guard_crash_restart(d, tagj)
    write_input(cfg, rh)
    try:
        subprocess.run([SIMULATE, 'simulation.input'], cwd=d,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                       timeout=TIMEOUT, check=False)
    except subprocess.TimeoutExpired:
        print(f'  [타임아웃 72h] {tagj}', flush=True)
        return row(cfg, rh, None, d, want_water, 'timeout')
    outs = glob.glob(os.path.join(d, 'Output', 'System_0', '*.data'))
    if not outs:
        return row(cfg, rh, None, d, want_water, 'no-output')
    if not finished(outs[0]):
        return row(cfg, rh, None, d, want_water, 'unfinished')
    if not net_charge_ok(outs[0]):
        return row(cfg, rh, None, d, want_water, '물 알짜전하 != 0')
    r = row(cfg, rh, parse_components(outs[0]), d, want_water, 'ok')
    # 완주 뒤에만 지웁니다. `Restart` 는 **남깁니다** — 사슬 연장의 유일한 수단이고
    # 09-07 에 그것을 지워 랩탑 9건이 연장 불가가 됐습니다(`RESTART_LOSS_20260907.md`).
    for sub in ('VTK', 'Movies', 'CrashRestart'):
        shutil.rmtree(os.path.join(d, sub), ignore_errors=True)
    return r


def row(cfg, rh, res, d, want_water, status):
    """결과 JSON 한 행. **유지율은 여기서 계산하지 않습니다** — 등록문대로
    보고서에서 CO₂(rh)/CO₂(rh0) 로 냅니다(분모를 행에 박으면 나중에 분모가
    바뀌었을 때 어느 값이 옛 분모인지 구별이 안 됩니다)."""
    res = res or {}
    co2 = res.get('CO2', (None, None))
    h2o = res.get('water', (None, None))
    ffc = ff_check_of(d, want_water) if os.path.isdir(d) else {'ok': None}
    return {
        'tag': cfg['tag'], 'framework': cfg['fw'], 'cif': cfg['cif'],
        'cif_md5': cfg['cif_md5'],
        'T': cfg['temp'], 'pco2_bar': cfg['pco2'], 'RH': rh,
        'psat_Pa': cfg['psat'], 'psat_source': cfg['psat_src'], 'preload_water': cfg.get('preload') or 0,
        'p_h2o_Pa': round(cfg['psat'] * rh, 4),
        'p_tot_Pa': round(cfg['pco2'] * 1e5 + cfg['psat'] * rh, 4),
        'CO2_molkg': co2[0], 'CO2_err': co2[1],
        'H2O_molkg': (h2o[0] if want_water else 0.0), 'H2O_err': h2o[1],
        'seed': read_seed(d), 'unitcells': cfg['reps'],
        'cell_widths_A': [round(w, 4) for w in cfg['widths']],
        'forcefield': FF_TAG, 'ff_md5': FF_MD5, 'ff_path': cfg['ff_path'],
        'ff_check': ffc, 'status': status,
        'host': socket.gethostname().lower(),
        'series': 'T-NF (TNF_REGISTRATION_20260910.md)',
        'supercell_rule': f'축별 수직 폭 >= {MIN_WIDTH:g} A 최소 정수 복제 '
                          f'(등록문 §0 예외 — 2x2x2 를 박지 않음)',
    }


def main(argv=None):
    ap = argparse.ArgumentParser(
        description='T-NF 일반 골격 CO2/H2O GCMC 드라이버 '
                    '(TNF_REGISTRATION_20260910.md)')
    ap.add_argument('--cif', required=True, help='전하 CIF (DDEC6 포함)')
    ap.add_argument('--tag', required=True, help='결과·폴더 이름')
    ap.add_argument('--temp', type=float, default=303.0)
    ap.add_argument('--pco2', type=float, default=0.14,
                    help='bar. 0 이면 CO2 성분을 뺍니다(순수 물)')
    ap.add_argument('--rh', default='0,50,70,90', help='퍼센트, 쉼표 구분')
    ap.add_argument('--psat', type=float, default=None,
                    help='Pa. 주지 않으면 T 에서 (298->3169, 303->4247, 그 밖은 Buck)')
    ap.add_argument('--preload-water', type=int, default=0,
                    help='물 분자를 미리 넣고 시작(상자 전체 개수; T-NF-0c 탈착 방향 진단용). 0 = 기본')
    ap.add_argument('--workers', type=int, default=4)
    ap.add_argument('--seed-stagger', type=float, default=5.0,
                    help='초. 같은 초에 뜬 작업은 같은 RASPA 씨앗을 받습니다')
    ap.add_argument('--dry-run', action='store_true',
                    help='폴더와 simulation.input 만 쓰고 **simulate 를 띄우지 않고** 종료')
    ap.add_argument('--out', default=None, help='결과 JSON (기본 tnf_results_<tag>.json)')
    ap.add_argument('--runs-root', default=None, help='실행 폴더 뿌리')
    a = ap.parse_args(argv)

    cif = os.path.abspath(a.cif)
    if not os.path.exists(cif):
        print(f'!! CIF 없음: {cif}'); return 2
    runs_root = os.path.abspath(a.runs_root or os.path.join(HERE, 'tnf_runs_' + a.tag))
    out = os.path.abspath(a.out or os.path.join(HERE, f'tnf_results_{a.tag}.json'))
    rhs = sorted({float(x) / 100.0 for x in a.rh.split(',') if x.strip() != ''},
                 reverse=True)           # LPT: 습한 것이 느립니다 (CLAUDE.md §5)
    psat, psrc = (a.psat, '--psat 로 지정') if a.psat is not None else p_sat(a.temp)
    reps, widths = unit_cells(cif)
    fw = os.path.basename(cif)[:-4]

    print('T-NF GCMC 드라이버 — 등록문 TNF_REGISTRATION_20260910.md', flush=True)
    print(f'  CIF   {cif}\n  골격  {fw}\n  RUNS  {runs_root}\n  OUT   {out}', flush=True)
    print(f'  조건  {a.temp:g} K · CO2 {a.pco2:g} bar · RH '
          + ','.join(f'{int(round(r*100))}' for r in sorted(rhs)), flush=True)
    print(f'  P_sat {psat:.1f} Pa  [{psrc}]  ->  p_H2O '
          + ' · '.join(f'RH{int(round(r*100))}={psat*r:.1f}' for r in sorted(rhs)) + ' Pa',
          flush=True)
    print(f'  복제  UnitCells {reps[0]} {reps[1]} {reps[2]}  '
          f'(수직 폭 {widths[0]:.2f}/{widths[1]:.2f}/{widths[2]:.2f} A -> '
          f'{reps[0]*widths[0]:.2f}/{reps[1]*widths[1]:.2f}/{reps[2]*widths[2]:.2f} A '
          f'>= {MIN_WIDTH:g} A, 등록문 §0)', flush=True)
    if any(r * w < MIN_WIDTH - 1e-6 for r, w in zip(reps, widths)):
        print('!! 복제 규칙 위반 — 중단'); return 2
    if a.pco2 <= 0 and max(rhs) <= 0:
        print('!! CO2 0 bar 이고 RH 도 0 — 성분이 없습니다.'); return 2
    if a.pco2 <= 0:
        print('  [순수 물] CO2 성분을 뺍니다 (T-NF-0 류)', flush=True)
    if not os.path.exists(WATER_DEF) and max(rhs) > 0:
        print(f'!! 5자리 물 정의 없음: {WATER_DEF}'); return 2

    # 파일 관문 — 착수 **전**. --dry-run 에서도 답을 보고 가야 합니다.
    ok, md5 = md5_gate()
    if not ok:
        print('!! 힘장 파일 관문 실패 — 아무것도 돌리지 않습니다 '
              f'(기대 {FF_MD5}, 실제 {md5}).'); return 2

    cfg = {'cif': cif, 'fw': fw, 'tag': a.tag, 'temp': a.temp, 'pco2': a.pco2, 'preload': a.preload_water,
           'psat': psat, 'psat_src': psrc, 'reps': reps, 'widths': widths,
           'runs_root': runs_root, 'workers': max(1, a.workers),
           'stagger': a.seed_stagger, 'ff_path': ff_path(),
           'cif_md5': hashlib.md5(open(cif, 'rb').read()).hexdigest()}
    os.makedirs(runs_root, exist_ok=True)

    if a.dry_run:
        print('\n--dry-run: 폴더와 simulation.input 만 씁니다. '
              'simulate 를 띄우지 않습니다.\n', flush=True)
        for rh in sorted(rhs):
            d, txt, p = write_input(cfg, rh)
            print('=' * 78)
            print(f'{d}/simulation.input   '
                  f'(p_CO2 {p["p_co2"]:.1f} + p_H2O {p["p_h2o"]:.1f} = {p["p_tot"]:.1f} Pa)')
            print('=' * 78)
            print(txt)
        print('[dry-run 종료] 계산은 시작되지 않았습니다.', flush=True)
        return 0

    jobs = [(i, cfg, rh) for i, rh in enumerate(rhs)]
    rows = []
    with Pool(processes=cfg['workers']) as pool:
        for r in pool.imap_unordered(run_one, jobs, chunksize=1):
            rows.append(r)
            print(f'  [{r["status"]:>16}] RH{int(round(r["RH"]*100)):>3}% '
                  f'CO2 {r["CO2_molkg"]}  H2O {r["H2O_molkg"]}  '
                  f'seed {r["seed"]}  ff_ok {r["ff_check"].get("ok")}', flush=True)

    # 씨앗 충돌 — 09-07 T-B2w 에서 6행이 씨앗 둘을 나눠 썼습니다. 세어서 남깁니다.
    seen = {}
    for r in rows:
        if r['seed'] is not None:
            seen.setdefault(r['seed'], []).append(int(round(r['RH'] * 100)))
    coll = {s: v for s, v in seen.items() if len(v) > 1}
    if coll:
        print(f'  ⚠ 씨앗 충돌 {coll} — 이 행들은 서로 독립이 아닙니다 '
              f'(--seed-stagger 를 늘리고 해당 행만 새 뿌리에서 다시 도십시오).',
              flush=True)

    prior = json.load(open(out, encoding='utf-8')) if os.path.exists(out) else []
    merged = {(x['tag'], x['T'], x['pco2_bar'], x['RH']): x for x in prior}
    for r in rows:
        merged[(r['tag'], r['T'], r['pco2_bar'], r['RH'])] = r
    final = sorted(merged.values(), key=lambda x: (x['tag'], x['T'], x['pco2_bar'], x['RH']))
    json.dump(final, open(out, 'w', encoding='utf-8'), indent=2, ensure_ascii=False)
    json.dump({'series': 'T-NF', 'registration': 'TNF_REGISTRATION_20260910.md',
               'forcefield': FF_TAG, 'ff_md5': FF_MD5, 'ff_path': ff_path(),
               'host': socket.gethostname().lower(), 'tag': a.tag,
               'unitcells': reps, 'supercell_rule': f'>= {MIN_WIDTH:g} A per axis',
               'psat_Pa': psat, 'psat_source': psrc,
               'seed_collisions': coll,
               'note': '슈퍼셀 예외(등록문 §0) 계열. ZIF-69 v3/v3w 표와 나란히 '
                       '순위 매기지 말 것. 유지율은 보고서에서 CO2(rh)/CO2(rh0).'},
              open(out[:-5] + '_meta.json', 'w', encoding='utf-8'),
              indent=2, ensure_ascii=False)
    bad = [r for r in rows if r['status'] != 'ok' and r['status'] != 'cached']
    ffbad = [r for r in rows if r['ff_check'].get('ok') is False]
    print(f'[OK] {out} — 이번 실행 {len(rows)}행, 합계 {len(final)}행 '
          f'(실패 {len(bad)} · 머리말 관문 실패 {len(ffbad)})', flush=True)
    return 0 if not bad and not ffbad else 1


if __name__ == '__main__':
    sys.exit(main())
