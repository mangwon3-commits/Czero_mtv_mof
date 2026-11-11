# -*- coding: utf-8 -*-
"""CORE22 §I — `2021[Zn][srs]3[FSR]1` **우리 앞단판**(`charged_v3/e22e_2021_Zn__srs_3_FSR_1_DDEC6.cif` · E-22e 이완 + PACMAN · md5 bf0f3c9a)의
323 K 습윤 TSA 회수량 3씨앗(9작업 · H 와 같은 조건). 등록 `SYNTH_20261111.md` §8 · `ASSIGN_CORE22_HUMID_PLAN_20261108.md` 11-11 갱신(새 항목 I · 자료 0건).
`run_core22_h_humid_wc_323.py`(d34e88e6) **사본** — 바꾼 것은 등록 I 의 "대상 · 막음 표만"과 그에 딸린 이름뿐:
  · 대상: zip 의 CoRE CIF 대신 위 전하 CIF 하나(md5 대조 · 바이트 같은 사본 셋). 대상 고르는 env(CORE22_H_KEYS)는 읽지 않음.
  · 막음 표: `results_i_blocks_hkhome.json`(HKHOME · 같은 CIF 의 Zeo++ `-block` 세 탐침 · 행 이름 e22e_2021_Zn__srs_3_FSR_1).
  · 이름: base = `i_znsrs_ourfe` → 실행 뿌리 · 잠금 · 결과 이름이 `core22_…` 대신 `i_znsrs_ourfe…`(`humid_wc_runs_v3w_323/i_znsrs_ourfe_h_<기기>` · `v3w_humid_wc_323/humid_wc_323_i_znsrs_ourfe_<기기>.json` · `results_i_znsrs_ourfe_humid_wc_323_summary_<기기>.json`).
  · 요약 · 감사 행의 `core_key` 칸에는 이 대상의 이름(e22e_2021_Zn__srs_3_FSR_1)이 들어가고, CoRE key 는 `core22.core_key` 에 적힘.
조건 · 틀 · 래퍼 · 러너 · 막음 삽입 · 감사 관문 · 착수 간격은 원판 그대로. 판정 없음 — 종합자.

[아래는 원판 머리말 — 위 넷 말고는 그대로 적용됨]
CORE22 §H — CoRE 3차원 22종의 323 K 습윤 TSA 회수량(T-RT-1 조건). 등록 `ASSIGN_CORE22_HUMID_PLAN_20261108.md` §H(자료 0건) ·
같은 파일 11-11 갱신(당기는 순서만 바꿈 · 읽는 법 · 예측 불변) · `SYNTH_20261111.md` §8.
틀 `run_znbdt_humid_wc_323.py`(53677257 · 막음 없는 대상 전용 · T-RT-1 래퍼 `run_humid_wc_v3w_323.py` b9a006b1 무수정 import)를
import 하는 얇은 실행기 — 틀 · 래퍼 · 러너(run_humid_wc) 원판 무수정. G 실행기 `run_core22_g_humid_wc.py`(6a8a8eeb)와 같은 짜임.
바꾸는 것(등록 §H 실행기 줄: CoRE 대상 · 막음 표(G 와 같은 표 · 물 1.30 · CO₂ 1.65) · 기기 · 이름):
  ① 대상: CoRE CIF — `core_pop_cifs.zip` 안의 바이트(md5 대조). G · C 실행기와 같은 방식으로 저장소 밖
     `~/.mof_chain/core22_1108/cifs/` 에 풀고, 실행 뿌리 아래 `cifs/<base>_h{1,2,3}_DDEC6.cif` 바이트 같은 사본 셋.
     base = `core22_<파일 이름 줄기>` · `_DDEC6` 는 러너의 파일 이름 규칙일 뿐이고 전하는 그 CIF 의 것(I 사본에서는 우리 앞단 PACMAN DDEC6).
  ② 막음 표: `results_core22_blocks_laptop.json` 에서 1.65 → CO₂ · 1.30 → 물, 구 수 > 0 인 성분만(ads · tsa · vsa 같은 표).
     틀에는 막음 삽입이 없으므로 틀의 `_run`(착수 간격 → stderr · 반환코드 기록 → RASPA) **앞에** G 실행기의 `_inject`(구조별 표 ·
     앵커 · 삽입 두 줄의 문자열 같음)를 얹음 — 순서는 `run_znbdt_no2_humid_wc_323.py`(de1461c2)와 같음(삽입 → 간격 → RASPA).
     앵커가 성분마다 정확히 한 번이 아니거나 입력에 이미 BlockPockets 가 있으면 RASPA 를 띄우지 않음.
  ③ 감사: G ③ 의 관문 — 막은 성분마다 `Pockets are blocked for this component` · 차단 수 = 구 × 셀 수, 막지 않은 성분은 출력에
     그 성분이 있고 그 줄이 없음 · 입력 `BlockPockets` 낱말 수 = 2 × 표의 성분 수 · not-found 0 · finished · 반환코드 0 · 씨앗 ·
     러너 결과 행에 그 조건의 적재가 있음. 여기에 래퍼의 조건 대조(`_stale_data`: .data 이름 · 머리말의 온도 · 전압력이 등록 조건과 같음)를
     끝난 뒤에도 한 번 더 봄. 씨앗 고유는 이 묶음 전체에서 셈. block_audit 는 ⑩(`run_e24i_no2_humid_wc.py`)과 같은 글자.
  ④ 기기 · 실행 뿌리(`humid_wc_runs_v3w_323/i_znsrs_ourfe_h_<기기>[_<묶음>]`, gitignore) · 잠금 · 결과 이름 — 구조마다
     `v3w_humid_wc_323/humid_wc_323_<base>_<기기>.json`(+ `.status.jsonl` · 러너 결과에서 그 구조의 행 · 상태 · 머리말 관문만.
     그 구조의 9작업이 다 차고 머리말 관문이 전부 통과일 때만 이 이름이고 아니면 `.PARTIAL.json`)
     + 요약 `results_<base>_humid_wc_323_summary_<기기>.json`(감사 포함). 러너 결과 전체는 실행 뿌리의 `runner_result_all.json`.
  ⑤ 순서: 착수 글에 적은 구조(CORE22_H_KEYS)를 묶음 안에서 LPT(N_super = 원자 수 × unit_cells() 셀 수 큰 순 · 같으면 등록 순서) ·
     구조 안 h1 → h2 → h3 · 조건 ads → tsa → vsa(러너 순서). **어느 구조를 가져갈지**는 11-11 갱신의 당기는 순서(H_ORDER)로 정하고,
     이 실행기는 받은 묶음 안의 착수 순서만 정함. 2017[Zn][dia]3[FSR]1 도 H 대상(G 와 달리 빼지 않음).
조건은 래퍼 그대로(T-RT-1): ads 323 K · CO₂ 15 kPa · 물 11,114.1 Pa(RH 90 % @ 323 K) → tsa 373 K → vsa 323 K · 5 kPa ·
5,000 + 15,000 · UFF_MOF · 전하 CIF 그대로 · 착수 간격 15 s × i + 2 s 잠금(씨앗 = 착수 초 · 틀 그대로).
env  CORE22_H_KEYS 쉼표(core_pop key · 실행 · 스모크는 필수) · CORE22_H_MACHINE(필수) · CORE22_H_WORKERS(기본 8)
     CORE22_H_BATCH=<이름> (선택) — 같은 기기의 둘째 묶음부터 실행 뿌리를 i_znsrs_ourfe_h_<기기>_<이름> 으로 가름(앞 묶음 결과가 있으면 멈추므로)
     CORE22_H_SMOKE=1 (10 사이클 · h1 만 · 저장소 밖) · CORE22_H_DRY=1 (RASPA 안 띄우고 입력만 · h1 만 · 저장소 밖 · 키 기본 22종)
     CORE22_CIFS · CORE22_BLOCKS (선택 · G 실행기와 같은 뜻)
판정 없음 — 종합자.
"""
import glob
import hashlib
import json
import math
import os
import re
import shutil
import statistics as st
import sys
import time
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
SRC = os.path.join(HERE, 'charged_v3', 'e22e_2021_Zn__srs_3_FSR_1_DDEC6.cif')      # 우리 앞단판(E-22e 이완 + PACMAN)
SRC_MD5 = 'bf0f3c9aa1f8e30a4bac001d02bbc732'
I_KEY = 'e22e_2021_Zn__srs_3_FSR_1'                                                # 막음 표(results_i_blocks_hkhome.json)의 행 이름
CORE_KEY = '2021[Zn][srs]3[FSR]1'
I_BASE = 'i_znsrs_ourfe'
BLK = os.path.join(HERE, os.environ.get('CORE22_BLOCKS', 'results_i_blocks_hkhome.json'))
FRAME = os.path.join(HERE, 'run_znbdt_humid_wc_323.py')
FRAME_MD5 = '536772571b726e37ba45a463cf1ae6cd'
WRAPPER = os.path.join(HERE, 'run_humid_wc_v3w_323.py')
WRAPPER_MD5 = 'b9a006b1e07357368be66a425dfbe1bc'
ALL22 = (I_KEY,)                                                          # 대상 하나(등록 I)
FC_UNKNOWN = set()
GAS = (('1.65', 'CO2'), ('1.30', 'water'))
MACHINE = os.environ.get('CORE22_H_MACHINE', '')
SMOKE = bool(os.environ.get('CORE22_H_SMOKE'))
DRY = bool(os.environ.get('CORE22_H_DRY'))
MODE = 'smoke' if SMOKE else ('dry' if DRY else None)
if not MACHINE:
    raise SystemExit('!! CORE22_H_MACHINE 이 비어 있음')
KEYS = [I_KEY]                                                            # 대상 고정 — KEYS env 는 읽지 않음
REPS = (1,) if MODE else (1, 2, 3)
CHAIN = os.path.expanduser('~/.mof_chain'); os.makedirs(CHAIN, exist_ok=True)


def md5b(b):
    return hashlib.md5(b).hexdigest()


def md5(p):
    return md5b(open(p, 'rb').read())


for _p, _m in ((FRAME, FRAME_MD5), (WRAPPER, WRAPPER_MD5)):
    if md5(_p) != _m:
        raise SystemExit(f'!! {os.path.basename(_p)} md5 {md5(_p)[:8]} ≠ master {_m[:8]} — 중단')

import run_aryl_gcmc as rg       # noqa: E402
from ase.io import read          # noqa: E402

if md5(SRC) != SRC_MD5:
    raise SystemExit(f'!! {os.path.relpath(SRC, HERE)} md5 {md5(SRC)[:8]} ≠ {SRC_MD5[:8]} — 중단')
KINFO = {}
for k in KEYS:
    a = read(SRC)
    uc = rg.unit_cells(a)
    KINFO[k] = {'key': k, 'core_key': CORE_KEY, 'file': os.path.relpath(SRC, HERE), 'n_atoms': len(a), 'unit_cells': list(uc),
                'N_super': len(a) * uc[0] * uc[1] * uc[2], 'fc_unknown': False, 'base': I_BASE}
KEYS.sort(key=lambda k: (-KINFO[k]['N_super'], ALL22.index(k)))            # 묶음 안 LPT
BASES = [KINFO[k]['base'] for k in KEYS]
B2K = {KINFO[k]['base']: k for k in KEYS}
TAGS = [f'{b}_h{r}' for b in BASES for r in REPS]

# ② 막음 표 — C 준비 결과에서 1.65(CO₂) · 1.30(물) 구 수 > 0 인 성분만 (G 실행기와 같은 글자)
BJ = json.load(open(BLK, encoding='utf-8'))
if BJ.get('all_blocks_ok') is not True or 'finished' not in BJ:
    raise SystemExit(f'!! {os.path.basename(BLK)} 가 완주 · 전부 ok 가 아님 — 중단')
_brow = {r['key']: r for r in BJ['rows']}
BLOCKS = {}
for k in KEYS:
    if k not in _brow:
        raise SystemExit(f'!! 막음 결과에 {k} 없음 — 중단')
    for r, g in GAS:
        x = _brow[k][f'r{r}']
        if x.get('block_ok') is not True or x.get('n_spheres') is None:
            raise SystemExit(f'!! {k} r={r} 막음 결과가 ok 아님 — 중단')
        if x['n_spheres'] > 0:
            f = os.path.join(HERE, x['block_file'])
            if md5(f) != x['block_md5'] or int(open(f).read().split()[0]) != x['n_spheres']:
                raise SystemExit(f'!! {f} md5 · 구 수가 막음 결과와 다름 — 중단')
            BLOCKS.setdefault(KINFO[k]['base'], {})[g] = {'file': f, 'md5': x['block_md5'], 'n_spheres': x['n_spheres'], 'probe_A': float(r)}

# 틀 import 전에 env — 래퍼는 import 순간 이 값으로 hw 전역 · 조건 · run_one_323 을 정함
os.environ['HWC_323_TARGETS'] = ','.join(TAGS)
os.environ['HWC_323_WORKERS'] = os.environ.get('CORE22_H_WORKERS', '8')
os.environ['HWC_323_RESULT'] = f'humid_wc_323_i_znsrs_ourfe_h_{MACHINE}_all.json'     # 아래에서 실행 뿌리로 옮김(이 이름의 파일은 만들지 않음)
os.environ['HWC_323_MACHINE'] = MACHINE
os.environ.pop('ZNBDT323_SMOKE', None)                                        # 틀의 스모크 갈래는 쓰지 않음(뿌리 · 사이클은 여기서)
os.environ.pop('HWC_323_DRYRUN', None)
import run_znbdt_humid_wc_323 as T   # noqa: E402  (import 순간 러너의 subprocess.run 이 틀의 _run 으로 감싸짐)
R = T.R
hw = T.hw

BATCH = os.environ.get('CORE22_H_BATCH', '')         # 같은 기기의 둘째 묶음부터 실행 뿌리를 가름
ROOT = (os.path.join(CHAIN, f'i_znsrs_ourfe_h_{MODE}_{MACHINE}') if MODE
        else os.path.join(HERE, 'humid_wc_runs_v3w_323', f'i_znsrs_ourfe_h_{MACHINE}' + (f'_{BATCH}' if BATCH else '')))
hw.RUNS = os.path.join(ROOT, 'runs')
hw.CHARGED = os.path.join(ROOT, 'cifs')
hw.RESULT = os.path.join(ROOT, 'runner_result_all.json')
R.STATUS_LOG = hw.RESULT + '.status.jsonl'
PARTIAL = hw.RESULT.replace('.json', '.PARTIAL.json')
OUTDIR = ROOT if MODE else R.V3W
SUMDIR = ROOT if MODE else HERE
if hw.TARGETS != TAGS:
    raise SystemExit(f'!! 러너 대상 {hw.TARGETS[:3]}… ≠ 실행기 대상 {TAGS[:3]}…')
T.JOBS = [(t, lab, p, TT, ps) for t in hw.TARGETS for lab, p, TT, ps in hw.CONDITIONS]   # hw.main 과 같은 순서
T.INDEX = {f'{lab}_{t}': i for i, (t, lab, *_r) in enumerate(T.JOBS)}
T.LOCK = os.path.join(CHAIN, f'.i_znsrs_ourfe_h_{MACHINE}{"_" + MODE if MODE else ""}_start.lock')

BP = '            BlockPockets              yes\n            BlockPocketsFileName      {}\n'          # G 실행기 · ⑩ _inject 와 같은 두 줄
ANCH = {g: f'MoleculeName              {g}\n            MoleculeDefinition        TraPPE\n' for g in ('CO2', 'water')}


def base_of(tag):
    return re.sub(r'_h\d+$', '', tag)


def res_name(base, complete=True):
    return os.path.join(OUTDIR, f'humid_wc_323_{base}_{MACHINE}' + ('.json' if complete else '.PARTIAL.json'))


def sum_name(base):
    return os.path.join(SUMDIR, f'results_{base}_humid_wc_323_summary_{MACHINE}.json')


def _inject(cwd):
    """G 실행기 `_inject` 와 같은 글자 — 표에 있는 성분에만 BlockPockets 두 줄 · 막음 파일 사본."""
    p = os.path.join(cwd, 'simulation.input')
    txt = open(p).read()
    if 'BlockPockets' in txt:
        raise RuntimeError(f'입력에 이미 BlockPockets 가 있음 — RASPA 안 띄움 ({cwd})')
    tag = os.path.basename(os.path.normpath(cwd)).split('_', 1)[1]
    base = base_of(tag)
    if base not in B2K:
        raise RuntimeError(f'실행기 대상이 아닌 구조 {base} — RASPA 안 띄움 ({cwd})')
    gs = BLOCKS.get(base, {})
    for g in ('CO2', 'water'):
        a = ANCH[g]
        if txt.count(a) != 1:
            raise RuntimeError(f'막음 앵커 {g} 가 {txt.count(a)}번 — RASPA 안 띄움 ({cwd})')
        if g in gs:
            key = f'blk_{g.lower()}'
            txt = txt.replace(a, a + BP.format(key))
            shutil.copy(gs[g]['file'], os.path.join(cwd, f'{key}.block'))
    if txt.count('BlockPockets') != 2 * len(gs):
        raise RuntimeError(f'BlockPockets 낱말 {txt.count("BlockPockets")} ≠ 2 × {len(gs)} — RASPA 안 띄움 ({cwd})')
    open(p, 'w').write(txt)


_t_run = hw.subprocess.run       # 틀의 _run(착수 간격 → stderr · 반환코드 → RASPA)


def _run(args, *a, **k):
    """simulate 호출만: 막음 삽입(②) → 틀의 _run. 드라이는 삽입까지만 하고 RASPA 를 띄우지 않음. 다른 호출은 그대로 통과."""
    cwd = k.get('cwd')
    if cwd and args and args[0] == rg.SIMULATE:
        _inject(cwd)
        if DRY:
            with open(os.path.join(cwd, T.RCFILE), 'w') as f:
                f.write('dry\n')
            return hw.subprocess.CompletedProcess(args, 0)
    return _t_run(args, *a, **k)


hw.subprocess.run = _run


def block_audit(txt):
    """성분별 막음 표지(⑩ block_audit 와 같은 글자)."""
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


def stage():
    """우리 앞단판 전하 CIF → cifs/<base>_h{r}_DDEC6.cif 바이트 같은 사본(원본 md5 대조)."""
    os.makedirs(hw.CHARGED, exist_ok=True)
    info = {}
    for k in KEYS:
        b = KINFO[k]['base']
        for r in REPS:
            dst = os.path.join(hw.CHARGED, f'{b}_h{r}_DDEC6.cif')
            if not os.path.exists(dst):
                shutil.copyfile(SRC, dst)
            if md5(dst) != SRC_MD5:
                raise SystemExit(f'!! 사본 {dst} md5 ≠ 원본 {SRC_MD5[:8]}')
        info[b] = {'file': os.path.relpath(SRC, HERE), 'md5': SRC_MD5}
    return info


def result_path():
    for p in (hw.RESULT, PARTIAL):
        if os.path.exists(p):
            return p
    return None


def audit():
    rp = result_path()
    res = json.load(open(rp, encoding='utf-8')) if rp else None
    loaded = {(r['name'], lab) for r in res['rows'] for lab in r['loadings']} if res else set()
    rows = []
    for job in T.JOBS:
        t, lab = job[0], job[1]
        base = base_of(t)
        gs = BLOCKS.get(base, {})
        d = os.path.join(hw.RUNS, f'{lab}_{t}')
        row = {'target': t, 'core_key': B2K[base], 'condition': lab, 'blocked_components': sorted(gs)}
        outs = R._data_files(d)
        if len(outs) != 1:
            row.update(ok=False, why=f'.data {len(outs)}개')
            rows.append(row)
            continue
        txt = open(outs[0], encoding='utf-8', errors='ignore').read()
        inp = open(os.path.join(d, 'simulation.input')).read()
        uc = [int(x) for x in re.search(r'UnitCells\s+(\d+)\s+(\d+)\s+(\d+)', inp).groups()]
        ncell = uc[0] * uc[1] * uc[2]
        s = re.search(r'Random number seed:\s*(\d+)', txt)
        rcf = os.path.join(d, T.RCFILE)
        ef = os.path.join(d, 'stderr.txt')
        err = open(ef, errors='ignore').read() if os.path.exists(ef) else None
        rc_txt = open(rcf).read().strip() if os.path.exists(rcf) else None
        ba = block_audit(txt)
        row.update(unit_cells=uc, seed=int(s.group(1)) if s else None, finished=rg.finished(outs[0]),
                   returncode=int(rc_txt) if rc_txt is not None and re.fullmatch(r'-?\d+', rc_txt) else rc_txt, block=ba,
                   blockpockets_in_input=inp.count('BlockPockets'), n_expected={g: gs[g]['n_spheres'] * ncell for g in gs},
                   stderr_not_found=(T.NOT_FOUND in err) if err is not None else None, not_found_in_output=T.NOT_FOUND in txt,
                   temperature_line=(re.search(r'External temperature:\s*([0-9.]+)', txt, re.I) or [None, None])[1],
                   condition_mismatch=R._stale_data(job), runner_loading=(t, lab) in loaded)
        gates = [row['blockpockets_in_input'] == 2 * len(gs), row['finished'], row['returncode'] == 0, row['stderr_not_found'] is False,
                 not row['not_found_in_output'], row['seed'] is not None, row['condition_mismatch'] is None, row['runner_loading']]
        for g in ('CO2', 'water'):
            c = ba.get(g, {})
            if g in gs:
                gates += [c.get('blocked_line') is True, c.get('n_blocked') == row['n_expected'][g]]
            else:
                gates.append(c.get('blocked_line') is False)          # 성분이 출력에 있고 막힘 줄이 없음
        row['ok'] = bool(all(gates))
        rows.append(row)
    seeds = [r.get('seed') for r in rows]
    return rows, {'n': len(rows), 'n_expected': len(T.JOBS), 'n_ok': sum(1 for r in rows if r['ok']),
                  'seeds_distinct': None not in seeds and len(set(seeds)) == len(seeds)}


def dry_check():
    """드라이 — 입력만 봄: 막음 낱말 수 · 막음 파일 md5 · 단위셀 · 온도 · 압력 · 사이클 · 몰분율."""
    out = []
    for t, lab, pco2, TT, _ps in T.JOBS:
        gs = BLOCKS.get(base_of(t), {})
        d = os.path.join(hw.RUNS, f'{lab}_{t}')
        p = os.path.join(d, 'simulation.input')
        if not os.path.exists(p):
            out.append((lab, t, False, 'input 없음'))
            continue
        inp = open(p).read()
        blk = {g: md5(os.path.join(d, f'blk_{g.lower()}.block')) == gs[g]['md5'] if os.path.exists(os.path.join(d, f'blk_{g.lower()}.block')) else False
               for g in gs}
        extra = sorted(os.path.basename(x) for x in glob.glob(os.path.join(d, '*.block')) if os.path.basename(x)[4:-6] not in [g.lower() for g in gs])
        ucs = re.search(r'UnitCells\s+(.+)', inp).group(1)
        tk = float(re.search(r'ExternalTemperature\s+(\S+)', inp).group(1))
        pp = float(re.search(r'ExternalPressure\s+(\S+)', inp).group(1))
        cyc = int(re.search(r'NumberOfCycles\s+(\d+)', inp).group(1))
        ini = int(re.search(r'NumberOfInitializationCycles\s+(\d+)', inp).group(1))
        mf = re.findall(r'MolFraction\s+(\S+)', inp)
        ok = (inp.count('BlockPockets') == 2 * len(gs) and all(blk.values()) and not extra and abs(tk - TT) < 1e-6
              and abs(pp - (pco2 + hw.P_H2O)) < 0.01 and (cyc, ini) == (15000, 5000) and len(mf) == 2
              and abs(float(mf[0]) - pco2 / (pco2 + hw.P_H2O)) < 1e-6)
        out.append((lab, t, ok, f"막음 낱말 {inp.count('BlockPockets')} (기대 {2 * len(gs)}) · 파일 md5 {blk} · 남는 .block {extra} · "
                                f"UnitCells {ucs} · T {tk} · P {pp} · 사이클 {ini}+{cyc} · 몰분율 {mf}"))
    return out


def summarize(rows, aud, info):
    rp = result_path()
    res = json.load(open(rp, encoding='utf-8')) if rp else None
    me = md5(os.path.abspath(__file__))
    stl = ([json.loads(ln) for ln in open(R.STATUS_LOG, encoding='utf-8') if ln.strip()] if os.path.exists(R.STATUS_LOG) else [])
    outs = {}
    for b in BASES:
        k = B2K[b]
        tags = [t for t in hw.TARGETS if base_of(t) == b]
        brows = [r for r in rows if r['target'] in tags]
        seeds = [r.get('seed') for r in brows]
        complete, rname = None, None
        if res:
            sub = {kk: vv for kk, vv in res.items() if kk not in ('rows', 'jobs', 'header_gate', 'complete')}
            srows = [r for r in res['rows'] if r['name'] in tags]
            hg = {kk: vv for kk, vv in (res.get('header_gate') or {}).items() if kk.split('_', 1)[1] in tags}
            n_exp = len(tags) * len(hw.CONDITIONS)
            n_have = sum(len(r.get('loadings', {})) for r in srows)
            complete = bool(n_have == n_exp and len(hg) == n_exp and all(v.get('ok') is True for v in hg.values()))
            sub.update(rows=srows, jobs={'expected': n_exp, 'with_loading': n_have, 'status': [s for s in stl if s.get('tag') in tags]},
                       header_gate=hg, complete=complete, split_from=os.path.relpath(rp, HERE) if not MODE else rp, core_key=k,
                       thin_runner='run_core22_i_h_humid_wc_323.py', thin_runner_md5=me)
            rname = res_name(b, complete)
            tmp = rname + '.tmp'
            json.dump(sub, open(tmp, 'w', encoding='utf-8'), indent=2, ensure_ascii=False)
            os.replace(tmp, rname)
            with open(res_name(b) + '.status.jsonl', 'w', encoding='utf-8') as f:
                for s in stl:
                    if s.get('tag') in tags:
                        f.write(json.dumps(s, ensure_ascii=False) + '\n')
        out = {'test': f'CORE22 §I — 2021[Zn][srs]3[FSR]1 우리 앞단판의 323 K 습윤 TSA 회수량(H 와 같은 조건) — {k}', 'assign': 'SYNTH_20261111.md §8 · ASSIGN_CORE22_HUMID_PLAN_20261108.md 11-11 갱신(항목 I)',
               'ported_from': 'run_znbdt_humid_wc_323.py (53677257) 무수정 import + run_core22_g_humid_wc.py (6a8a8eeb) 의 구조별 막음 삽입 · 감사',
               'wrapper': 'run_humid_wc_v3w_323.py (b9a006b1 · 무수정 import)', 'thin_runner': 'run_core22_i_h_humid_wc_323.py', 'copied_from': 'run_core22_h_humid_wc_323.py (d34e88e6) — 대상 · 막음 표 · 이름만',
               'thin_runner_md5': me, 'machine': MACHINE, 'made': time.strftime('%F %T'), 'mode': MODE, 'batch': BATCH,
               'batch_keys': list(KEYS), 'runner_result': (os.path.relpath(rname, HERE) if not MODE else rname) if rname else None,
               'complete': complete, 'stagger_s': T.STAGGER, 'gap_s': T.GAP,
               'core22': {**KINFO[k], 'cif_md5': info[b]['md5'], 'blocked_components': sorted(BLOCKS.get(b, {}))},
               'inputs': {'cif_source': {'file': os.path.relpath(SRC, HERE), 'md5': SRC_MD5, 'front_end': 'E-22e 이완 + PACMAN DDEC6'},
                          'copies': {t: (os.path.relpath(os.path.join(hw.CHARGED, f'{t}_DDEC6.cif'), HERE) if not MODE
                                         else os.path.join(hw.CHARGED, f'{t}_DDEC6.cif')) for t in tags},
                          'blocks_source': {'file': os.path.basename(BLK), 'md5': md5(BLK)}},
               'blocking': {g: {kk: (os.path.relpath(vv, HERE) if kk == 'file' else vv) for kk, vv in v.items()} for g, v in BLOCKS.get(b, {}).items()},
               'audit_summary': {'n': len(brows), 'n_ok': sum(1 for r in brows if r['ok']),
                                 'seeds_distinct_within_structure': None not in seeds and len(set(seeds)) == len(seeds),
                                 'seeds_distinct_batch': aud['seeds_distinct']},
               'audit': brows, 'note': '기계적 사실뿐 — 판정은 종합자. 평균 ± = ±̄/√n · SD = 씨앗 SD. 구 0 인 성분은 막음 없음. 전하는 그 CIF 의 것(I 사본에서는 우리 앞단 PACMAN DDEC6). '
                                       '물 분압 11,114.1 Pa 세 조건 공통(RH 90 % @ 323 K).'}
        if res:
            wc = {r['name']: r['working_capacity'] for r in res['rows'] if r['name'] in tags}
            s = {}
            for key in ('tsa', 'vsa'):
                xs = [wc[t][key] for t in tags if key in wc.get(t, {})]
                if xs:
                    v = [x['value'] for x in xs]
                    s[f'WC_{key.upper()}_each'] = v
                    s[f'WC_{key.upper()}_mean'] = st.mean(v)
                    s[f'WC_{key.upper()}_mean_err'] = st.mean(x['err'] for x in xs) / math.sqrt(len(xs))
                    s[f'WC_{key.upper()}_SD'] = st.stdev(v) if len(v) > 1 else None
            s['loadings'] = {r['name']: r['loadings'] for r in res['rows'] if r['name'] in tags}
            out['summary'] = s
        tmp = sum_name(b) + '.tmp'
        json.dump(out, open(tmp, 'w', encoding='utf-8'), indent=2, ensure_ascii=False)
        os.replace(tmp, sum_name(b))
        outs[b] = out
    return outs


def main():
    print(f'CORE22 §I(323 K 회수량 · H 사본) — 기기 {MACHINE} · {len(KEYS)}종 · 모드 {MODE or "실행"} · 묶음 {BATCH or "(없음)"} · 작업 {len(T.JOBS)} · '
          f'워커 {hw.MAX_WORKERS} · 막음 표 {os.path.basename(BLK)} · 틀 {FRAME_MD5[:8]} · 래퍼 {WRAPPER_MD5[:8]}', flush=True)
    for k in KEYS:
        i = KINFO[k]
        print(f"  {k:24s} N_super {i['N_super']:5d} · 셀 {i['unit_cells']} · 막음 "
              f"{ {g: v['n_spheres'] for g, v in BLOCKS.get(i['base'], {}).items()} or '없음'}{' · fc 미상' if i['fc_unknown'] else ''}", flush=True)
    olds = [p for p in (hw.RESULT, PARTIAL, R.STATUS_LOG) if os.path.exists(p)]
    olds += [p for b in BASES for p in (res_name(b), res_name(b, False), res_name(b) + '.status.jsonl', sum_name(b)) if os.path.exists(p)]
    dirs = [x for x in T.INDEX if os.path.exists(os.path.join(hw.RUNS, x))]
    if olds or dirs:
        print(f'  !! 이전 결과 {olds} · 실행 폴더 {len(dirs)}개 있음 — 중단(러너가 cached 로 회수하므로 첫 착수만 받음)', flush=True)
        return 1
    info = stage()                    # 사본이 있어야 래퍼 사전검사가 대상 CIF 를 찾음
    R._preflight()                    # 파일 관문 · 대상 CIF · 조건 · 자식 대조(사이클 15,000/5,000 · run_one_323 · 폴더) · 다른 조건 .data
    print(f'  잠금        {T.LOCK}', flush=True)
    if SMOKE:
        hw.CYCLES, hw.INIT = 10, 0    # 사전검사 뒤 — 자식은 hw.main 의 fork 때 이 값을 물려받음
        print(f'  스모크 사이클 {hw.CYCLES}+{hw.INIT} · RUNS {hw.RUNS}', flush=True)
    print(flush=True)
    T.T0 = time.time()
    rc = hw.main()
    if not DRY:
        if rc == 0 and os.path.exists(hw.RESULT):
            rc = R._finalize()
        elif rc == 0:
            print('  !! main 이 0 을 돌려줬는데 결과 파일이 없습니다 — 미완(종료 2)', flush=True)
            rc = 2
    rows, aud = audit()
    outs = summarize(rows, aud, info)
    print(f"감사 {json.dumps(aud, ensure_ascii=False)}", flush=True)
    if DRY:
        dc = dry_check()
        for lab, t, ok, s in dc:
            print(f'  드라이 {lab:<4} {t:40s} {"ok" if ok else "!!"} · {s}', flush=True)
        print(f'드라이 입력 검사 {sum(1 for x in dc if x[2])}/{len(dc)} ok', flush=True)
        return 0 if all(x[2] for x in dc) else 2
    for r in rows:
        print(f"  {r['condition']:<4} {r['target']:40s} ok {r['ok']} · 막음 {r['blocked_components']} · 낱말 {r.get('blockpockets_in_input')} · "
              f"차단 { {g: (r.get('block', {}).get(g, {}).get('n_blocked'), r.get('n_expected', {}).get(g)) for g in r['blocked_components']} } · "
              f"막지 않은 성분 줄 { {g: r.get('block', {}).get(g, {}).get('blocked_line') for g in ('CO2', 'water') if g not in r['blocked_components']} } · "
              f"완주 {r.get('finished')} · rc {r.get('returncode')} · T {r.get('temperature_line')} · 조건 어긋남 {r.get('condition_mismatch')} · "
              f"씨앗 {r.get('seed')}{' · ' + r['why'] if 'why' in r else ''}", flush=True)
    for b, o in outs.items():
        s = {kk: vv for kk, vv in o.get('summary', {}).items() if kk != 'loadings'}
        print(f"  요약 {B2K[b]:24s} complete {o['complete']} · {o['audit_summary']} · {json.dumps(s, ensure_ascii=False)[:300]}", flush=True)
    if aud['n_ok'] != aud['n_expected'] or not aud['seeds_distinct']:
        print('  !! 감사 미통과 — 결과로 쓰지 마십시오(종료 2)', flush=True)
        rc = rc or 2
    return rc or 0


if __name__ == '__main__':
    sys.exit(main())
