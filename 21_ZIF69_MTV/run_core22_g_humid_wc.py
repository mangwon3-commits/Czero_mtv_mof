# -*- coding: utf-8 -*-
"""CORE22 §G — CoRE 3차원 22종의 298 K 습윤 TSA 회수량. 등록 `ASSIGN_CORE22_HUMID_PLAN_20261108.md` §G(자료 0건).
`run_e24i_no2_humid_wc.py`(c2d4673a · 물 막음 삽입이 있는 판)를 import 하는 얇은 실행기 — 틀 · 러너(run_humid_wc_v3w · run_humid_wc) 원판 무수정.
바꾸는 것(등록 §G 실행기 줄):
  ① 대상: CoRE CIF — `core_pop_cifs.zip` 안의 바이트(md5 대조). C 실행기(`run_core22_e_humid3.py`)와 같은 방식으로 저장소 밖
     `~/.mof_chain/core22_1108/cifs/` 에 풀고, 실행 뿌리 아래 `cifs/<base>_h{1,2,3}_DDEC6.cif` 바이트 같은 사본 셋.
     base = `core22_<파일 이름 줄기>` · `_DDEC6` 는 러너의 파일 이름 규칙일 뿐이고 전하는 CoRE CIF 의 것.
  ② 막음 표: `results_core22_blocks_laptop.json` 에서 1.65 → CO₂ · 1.30 → 물, 구 수 > 0 인 성분만(ads · tsa · vsa 같은 표).
     N₂ 는 이 계산에 없음. 틀의 `_inject`(물 고정)만 구조별 표로 바꿈 — 앵커 · 삽입 두 줄의 문자열은 틀과 같고,
     앵커가 성분마다 정확히 한 번이 아니거나 입력에 이미 BlockPockets 가 있으면 RASPA 를 띄우지 않음.
  ③ 감사: 틀 ⑩ 의 관문을 표에 맞춤 — 막은 성분마다 `Pockets are blocked for this component` · 차단 수 = 구 × 셀 수,
     막지 않은 성분은 출력에 그 성분이 있고 그 줄이 없음 · 입력 `BlockPockets` 낱말 수 = 2 × 표의 성분 수 · not-found 0 · finished ·
     반환코드 0 · 씨앗 · 러너 결과 행에 그 조건의 적재가 있음(순전하 이상 · 출력 없음이면 없음). 씨앗 고유는 기기 전체에서 셈.
  ④ 기기 · 실행 뿌리(`humid_wc_runs_v3w/core22_g_<기기>`, gitignore) · 잠금 · 결과 이름 — 구조마다
     `v3w_humid_wc/humid_working_capacity_w2_<base>_<기기>.json`(러너 결과에서 그 구조의 행만) + 요약 `results_<base>_humid_summary_<기기>.json`(감사 포함).
     러너 결과 전체는 실행 뿌리의 `runner_result_all.json`.
  ⑤ 순서: 착수 글에 적은 구조(CORE22_G_KEYS)를 LPT(N_super = 원자 수 × unit_cells() 셀 수 큰 순 · 같으면 등록 순서) ·
     구조 안 h1 → h2 → h3 · 조건 ads → tsa → vsa(러너 순서). 2017[Zn][dia]3[FSR]1 은 D(laptop2)와 같은 계산이라 받지 않음(등록 §0).
조건은 틀 그대로(A 와 같음): ads 298 K · CO₂ 15 kPa · 물 2,852.1 Pa(RH 90 %) → tsa 373 K → vsa 298 K · 5 kPa · 5,000 + 15,000 · UFF_MOF ·
전하 CIF 그대로 · 착수 간격 15 s + 2 s 잠금(씨앗 = 착수 초).
env  CORE22_G_KEYS 쉼표(core_pop key · 실행은 필수) · CORE22_G_MACHINE(기본 laptop) · CORE22_G_WORKERS(기본 8)
     CORE22_G_SMOKE=1 (10 사이클 · h1 만 · 저장소 밖) · CORE22_G_DRY=1 (RASPA 안 띄우고 입력만 · h1 만 · 저장소 밖 · 키 기본 21종)
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
CIFS = os.path.expanduser(os.environ.get('CORE22_CIFS', '~/.mof_chain/core22_1108/cifs'))
ZIP = os.path.join(HERE, 'core_pop_cifs.zip')
ANN = os.path.join(HERE, 'core_pop_annotated.json')
BLK = os.path.join(HERE, os.environ.get('CORE22_BLOCKS', 'results_core22_blocks_laptop.json'))
TEMPLATE = os.path.join(HERE, 'run_e24i_no2_humid_wc.py')
TEMPLATE_MD5 = 'c2d4673a41523ddee59295f2a8938200'
ALL22 = ('2021[Zn][srs]3[FSR]1', '2017[Zn][dia]3[ASR]1', '2017[Zn][dia]3[FSR]1', '2024[Cu][srs]3[FSR]2', '2024[Co][pcu]3[ASR]1',
         '2024[Co][pcu]3[FSR]1', '2024[Zn][ths]3[ASR]1', '2024[Zn][ths]3[FSR]1', '2014[Cu][dia]3[FSR]6', '2014[Cu][dia]3[FSR]2',
         '2014[Cu][dia]3[ASR]5', '2014[Cu][dia]3[ASR]1', '2018[Cd][dia]3[FSR]5', '2018[Cd][dia]3[ASR]6', '2019[Ni][pcu]3[ASR]1',
         '2018[Cd][dia]3[ASR]5', '2018[Cd][dia]3[FSR]3', '2018[Cd][dia]3[ASR]4', '2018[Cd][dia]3[FSR]4', '2021[Co][dia]3[ASR]1',
         '2021[Co][dia]3[FSR]1', '2019[Zn][pcu]3[ASR]1')                     # 등록 §C 대상 22 · 등록 순서
FC_UNKNOWN = {'2024[Cu][srs]3[FSR]2', '2024[Zn][ths]3[ASR]1', '2024[Zn][ths]3[FSR]1', '2014[Cu][dia]3[FSR]2', '2014[Cu][dia]3[ASR]1',
              '2019[Ni][pcu]3[ASR]1'}
D_KEY = '2017[Zn][dia]3[FSR]1'                                              # D(laptop2)의 행을 G 의 이 행으로 씀 — 여기서 안 돌림
GAS = (('1.65', 'CO2'), ('1.30', 'water'))
MACHINE = os.environ.get('CORE22_G_MACHINE', 'laptop')
SMOKE = bool(os.environ.get('CORE22_G_SMOKE'))
DRY = bool(os.environ.get('CORE22_G_DRY'))
MODE = 'smoke' if SMOKE else ('dry' if DRY else None)
_k = os.environ.get('CORE22_G_KEYS', '')
KEYS = [k for k in _k.split(',') if k] if _k else ([k for k in ALL22 if k != D_KEY] if DRY else [])
if not KEYS:
    raise SystemExit('!! CORE22_G_KEYS 가 비었음 — 실행 · 스모크는 착수 글에 적은 구조를 줘야 함')
if len(set(KEYS)) != len(KEYS) or any(k not in ALL22 for k in KEYS):
    raise SystemExit(f'!! CORE22_G_KEYS 가 등록 22종의 부분집합(중복 없음)이 아님: {KEYS}')
if D_KEY in KEYS:
    raise SystemExit(f'!! {D_KEY} 는 D(laptop2)가 같은 계산 — G 에서 안 돌림(등록 §0)')
REPS = (1,) if MODE else (1, 2, 3)
CHAIN = os.path.expanduser('~/.mof_chain'); os.makedirs(CHAIN, exist_ok=True)


def md5b(b):
    return hashlib.md5(b).hexdigest()


def md5(p):
    return md5b(open(p, 'rb').read())


if md5(TEMPLATE) != TEMPLATE_MD5:
    raise SystemExit(f'!! 틀 {os.path.basename(TEMPLATE)} md5 {md5(TEMPLATE)[:8]} ≠ master c2d4673a — 중단')

import run_aryl_gcmc as rg       # noqa: E402
from ase.io import read          # noqa: E402

ANNR = {r['key']: r for r in json.load(open(ANN, encoding='utf-8'))['rows']}
os.makedirs(CIFS, exist_ok=True)
with zipfile.ZipFile(ZIP) as _zf:
    for k in KEYS:
        _p = os.path.join(CIFS, ANNR[k]['file'])
        if not os.path.exists(_p):
            open(_p, 'wb').write(_zf.read(ANNR[k]['file']))          # 다른 기기용 — 대조는 stage() 에서 zip 바이트와 md5
KINFO = {}
for k in KEYS:
    a = read(os.path.join(CIFS, ANNR[k]['file']))
    uc = rg.unit_cells(a)
    KINFO[k] = {'key': k, 'file': ANNR[k]['file'], 'n_atoms': len(a), 'unit_cells': list(uc), 'N_super': len(a) * uc[0] * uc[1] * uc[2],
                'fc_unknown': k in FC_UNKNOWN, 'base': 'core22_' + ANNR[k]['file'][:-4]}
KEYS.sort(key=lambda k: (-KINFO[k]['N_super'], ALL22.index(k)))            # LPT
BASES = [KINFO[k]['base'] for k in KEYS]
B2K = {KINFO[k]['base']: k for k in KEYS}
TAGS = [f'{b}_h{r}' for b in BASES for r in REPS]

# ② 막음 표 — C 준비 결과에서 1.65(CO₂) · 1.30(물) 구 수 > 0 인 성분만
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

# 틀 import 전에 env — 틀은 setdefault 이므로 여기 값이 씀
os.environ['HWC_V3W_TARGETS'] = ','.join(TAGS)
os.environ['HWC_V3W_WORKERS'] = os.environ.get('CORE22_G_WORKERS', '8')
os.environ['HWC_V3W_RESULT'] = f'humid_working_capacity_w2_core22_g_{MACHINE}_all.json'     # 아래에서 실행 뿌리로 옮김
if DRY:
    os.environ['E24I_DRY'] = '1'
else:
    os.environ.pop('E24I_DRY', None)
import run_e24i_no2_humid_wc as T   # noqa: E402  (import 순간 러너의 subprocess.run · run_one 이 틀의 것으로 감싸짐)
import ff_gate                      # noqa: E402
hw = T.hw
V = T.V

ROOT = os.path.join(CHAIN, f'core22_g_{MODE}_{MACHINE}') if MODE else os.path.join(HERE, 'humid_wc_runs_v3w', f'core22_g_{MACHINE}')
hw.RUNS = os.path.join(ROOT, 'runs')
hw.CHARGED = os.path.join(ROOT, 'cifs')
hw.RESULT = os.path.join(ROOT, 'runner_result_all.json')
OUTDIR = ROOT if MODE else V.V3W
SUMDIR = ROOT if MODE else HERE
if SMOKE:
    hw.CYCLES, hw.INIT = 10, 0
if DRY:
    T.STAGGER = 0.5
if hw.TARGETS != TAGS:
    raise SystemExit(f'!! 러너 대상 {hw.TARGETS[:3]}… ≠ 실행기 대상 {TAGS[:3]}…')
T.JOBS = [(t, lab, p, TT, ps) for t in hw.TARGETS for lab, p, TT, ps in hw.CONDITIONS]   # hw.main 과 같은 순서
T.LOCK = os.path.join(CHAIN, f'.core22_g_{MACHINE}_start.lock')

BP = '            BlockPockets              yes\n            BlockPocketsFileName      {}\n'          # 틀 _inject 와 같은 두 줄
ANCH = {g: f'MoleculeName              {g}\n            MoleculeDefinition        TraPPE\n' for g in ('CO2', 'water')}


def base_of(tag):
    return re.sub(r'_h\d+$', '', tag)


def res_name(base):
    return os.path.join(OUTDIR, f'humid_working_capacity_w2_{base}_{MACHINE}.json')


def sum_name(base):
    return os.path.join(SUMDIR, f'results_{base}_humid_summary_{MACHINE}.json')


def _inject(cwd):
    """틀 _inject 의 구조별 판 — 표에 있는 성분에만 BlockPockets 두 줄 · 막음 파일 사본."""
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


T._inject = _inject               # 틀 _run 이 호출 때 모듈 전역에서 찾음


def stage():
    """CoRE CIF → cifs/<base>_h{r}_DDEC6.cif 바이트 같은 사본(zip 바이트 md5 대조)."""
    zf = zipfile.ZipFile(ZIP)
    names = set(zf.namelist())
    os.makedirs(hw.CHARGED, exist_ok=True)
    info = {}
    for k in KEYS:
        f = ANNR[k]['file']
        if f not in names:
            raise SystemExit(f'!! zip 에 {f} 없음')
        m = md5b(zf.read(f))
        p = os.path.join(CIFS, f)
        if md5(p) != m:
            raise SystemExit(f'!! 풀린 {p} md5 ≠ zip 바이트')
        b = KINFO[k]['base']
        for r in REPS:
            dst = os.path.join(hw.CHARGED, f'{b}_h{r}_DDEC6.cif')
            if not os.path.exists(dst):
                shutil.copyfile(p, dst)
            if md5(dst) != m:
                raise SystemExit(f'!! 사본 {dst} md5 ≠ zip 바이트')
        info[b] = {'file': f, 'md5': m}
    return info


def audit():
    res = json.load(open(hw.RESULT, encoding='utf-8')) if os.path.exists(hw.RESULT) else None
    loaded = {(r['name'], lab) for r in res['rows'] for lab in r['loadings']} if res else set()
    rows = []
    for t in hw.TARGETS:
        base = base_of(t)
        gs = BLOCKS.get(base, {})
        for lab, *_ in hw.CONDITIONS:
            d = os.path.join(hw.RUNS, f'{lab}_{t}')
            row = {'target': t, 'core_key': B2K[base], 'condition': lab, 'blocked_components': sorted(gs)}
            outs = glob.glob(os.path.join(d, 'Output', 'System_0', '*.data'))
            if len(outs) != 1:
                row.update(ok=False, why=f'.data {len(outs)}개')
                rows.append(row)
                continue
            txt = open(outs[0], encoding='utf-8', errors='ignore').read()
            inp = open(os.path.join(d, 'simulation.input')).read()
            uc = [int(x) for x in re.search(r'UnitCells\s+(\d+)\s+(\d+)\s+(\d+)', inp).groups()]
            ncell = uc[0] * uc[1] * uc[2]
            s = re.search(r'Random number seed:\s*(\d+)', txt)
            rcf = os.path.join(d, 'e24g_returncode.txt')
            ef = os.path.join(d, 'stderr.txt')
            err = open(ef, errors='ignore').read() if os.path.exists(ef) else None
            ba = T.block_audit(txt)
            row.update(unit_cells=uc, seed=int(s.group(1)) if s else None, finished=rg.finished(outs[0]),
                       returncode=int(open(rcf).read().strip()) if os.path.exists(rcf) else None, block=ba,
                       blockpockets_in_input=inp.count('BlockPockets'), n_expected={g: gs[g]['n_spheres'] * ncell for g in gs},
                       stderr_not_found=(T.NOT_FOUND in err) if err is not None else None, not_found_in_output=T.NOT_FOUND in txt,
                       runner_loading=(t, lab) in loaded)
            gates = [row['blockpockets_in_input'] == 2 * len(gs), row['finished'], row['returncode'] == 0, row['stderr_not_found'] is False,
                     not row['not_found_in_output'], row['seed'] is not None, row['runner_loading']]
            for g in ('CO2', 'water'):
                c = ba.get(g, {})
                if g in gs:
                    gates += [c.get('blocked_line') is True, c.get('n_blocked') == row['n_expected'][g]]
                else:
                    gates.append(c.get('blocked_line') is False)          # 성분이 출력에 있고 막힘 줄이 없음
            row['ok'] = bool(all(gates))
            rows.append(row)
    seeds = [r.get('seed') for r in rows]
    return rows, {'n': len(rows), 'n_ok': sum(1 for r in rows if r['ok']),
                  'seeds_distinct': None not in seeds and len(set(seeds)) == len(seeds)}


def dry_check():
    """드라이 — 입력만 봄: 막음 낱말 수 · 막음 파일 md5 · 단위셀 · 성분 절."""
    out = []
    for t in hw.TARGETS:
        gs = BLOCKS.get(base_of(t), {})
        for lab, *_ in hw.CONDITIONS:
            d = os.path.join(hw.RUNS, f'{lab}_{t}')
            p = os.path.join(d, 'simulation.input')
            if not os.path.exists(p):
                out.append((lab, t, 'input 없음'))
                continue
            inp = open(p).read()
            blk = {g: md5(os.path.join(d, f'blk_{g.lower()}.block')) == gs[g]['md5'] if os.path.exists(os.path.join(d, f'blk_{g.lower()}.block')) else False
                   for g in gs}
            extra = sorted(os.path.basename(x) for x in glob.glob(os.path.join(d, '*.block')) if os.path.basename(x)[4:-6] not in [g.lower() for g in gs])
            ucs = re.search(r'UnitCells\s+(.+)', inp).group(1)
            tk = re.search(r'ExternalTemperature\s+(\S+)', inp).group(1)
            pp = re.search(r'ExternalPressure\s+(\S+)', inp).group(1)
            out.append((lab, t, f"막음 낱말 {inp.count('BlockPockets')} (기대 {2 * len(gs)}) · 파일 md5 {blk} · 남는 .block {extra} · "
                                f"UnitCells {ucs} · T {tk} · P {pp}"))
    return out


def summarize(rows, aud, info):
    res = json.load(open(hw.RESULT, encoding='utf-8')) if os.path.exists(hw.RESULT) else None
    me = md5(os.path.abspath(__file__))
    outs = {}
    for b in BASES:
        k = B2K[b]
        tags = [t for t in hw.TARGETS if base_of(t) == b]
        brows = [r for r in rows if r['target'] in tags]
        seeds = [r.get('seed') for r in brows]
        if res:
            sub = {kk: vv for kk, vv in res.items() if kk != 'rows'}
            sub.update(rows=[r for r in res['rows'] if r['name'] in tags], split_from=os.path.relpath(hw.RESULT, HERE), core_key=k)
            tmp = res_name(b) + '.tmp'
            json.dump(sub, open(tmp, 'w', encoding='utf-8'), indent=2, ensure_ascii=False)
            os.replace(tmp, res_name(b))
        out = {'test': f'CORE22 §G — CoRE 22 의 298 K 습윤 TSA 회수량 — {k}', 'assign': 'ASSIGN_CORE22_HUMID_PLAN_20261108.md §G',
               'ported_from': 'run_e24i_no2_humid_wc.py (c2d4673a) — _inject 만 구조별 막음 표로', 'thin_runner': 'run_core22_g_humid_wc.py',
               'thin_runner_md5': me, 'machine': MACHINE, 'made': time.strftime('%F %T'), 'mode': MODE,
               'runner_result': os.path.relpath(res_name(b), HERE) if not MODE else res_name(b),
               'core22': {**KINFO[k], 'cif_md5': info[b]['md5'], 'blocked_components': sorted(BLOCKS.get(b, {}))},
               'inputs': {'cif_source': {'zip': os.path.basename(ZIP), 'zip_md5': md5(ZIP), 'unpacked': CIFS},
                          'copies': {t: os.path.relpath(os.path.join(hw.CHARGED, f'{t}_DDEC6.cif'), HERE) for t in tags},
                          'blocks_source': {'file': os.path.basename(BLK), 'md5': md5(BLK)}},
               'blocking': {g: {kk: (os.path.relpath(vv, HERE) if kk == 'file' else vv) for kk, vv in v.items()} for g, v in BLOCKS.get(b, {}).items()},
               'audit_summary': {'n': len(brows), 'n_ok': sum(1 for r in brows if r['ok']),
                                 'seeds_distinct_within_structure': None not in seeds and len(set(seeds)) == len(seeds),
                                 'seeds_distinct_machine': aud['seeds_distinct']},
               'audit': brows, 'note': '기계적 사실뿐 — 판정은 종합자. 평균 ± = ±̄/√n · SD 병기. 구 0 인 성분은 막음 없음. 전하는 CoRE CIF 의 것.'}
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
    ok, fm = ff_gate.md5_gate()
    print(f"  파일 관문 md5 {fm} {'일치' if ok else '불일치 — 중단'}", flush=True)
    if not ok:
        return 3
    print(f'CORE22 §G — 기기 {MACHINE} · {len(KEYS)}종 · 모드 {MODE or "실행"} · 작업 {len(T.JOBS)} · 사이클 {hw.CYCLES}+{hw.INIT} · '
          f'워커 {hw.MAX_WORKERS} · 막음 표 {os.path.basename(BLK)}', flush=True)
    for k in KEYS:
        i = KINFO[k]
        print(f"  {k:24s} N_super {i['N_super']:5d} · 셀 {i['unit_cells']} · 막음 "
              f"{ {g: v['n_spheres'] for g, v in BLOCKS.get(i['base'], {}).items()} or '없음'}{' · fc 미상' if i['fc_unknown'] else ''}", flush=True)
    for kk in ('CHARGED', 'RUNS', 'RESULT', 'MAX_WORKERS'):
        print(f'  {kk:12s} {getattr(hw, kk)}', flush=True)
    if (os.path.exists(hw.RESULT) or any(os.path.exists(os.path.join(hw.RUNS, f'{lab}_{t}')) for t in hw.TARGETS for lab, *_ in hw.CONDITIONS)
            or any(os.path.exists(res_name(b)) or os.path.exists(sum_name(b)) for b in BASES)):
        print('  !! 이전 결과 · 실행 폴더 있음 — 중단(러너가 cached 로 재사용하므로)', flush=True)
        return 1
    info = stage()
    T.T0 = time.time()
    rc = hw.main()
    rows, aud = audit()
    outs = summarize(rows, aud, info)
    print(f"감사 {json.dumps(aud, ensure_ascii=False)}", flush=True)
    if DRY:
        for lab, t, s in dry_check():
            print(f'  드라이 {lab:<4} {t:40s} {s}', flush=True)
    for r in rows:
        print(f"  {r['condition']:<4} {r['target']:40s} ok {r['ok']} · 막음 {r['blocked_components']} · 낱말 {r.get('blockpockets_in_input')} · "
              f"차단 { {g: (r.get('block', {}).get(g, {}).get('n_blocked'), r.get('n_expected', {}).get(g)) for g in r['blocked_components']} } · "
              f"막지 않은 성분 줄 { {g: r.get('block', {}).get(g, {}).get('blocked_line') for g in ('CO2', 'water') if g not in r['blocked_components']} } · "
              f"완주 {r.get('finished')} · rc {r.get('returncode')} · 씨앗 {r.get('seed')}{' · ' + r['why'] if 'why' in r else ''}", flush=True)
    for b, o in outs.items():
        s = {kk: vv for kk, vv in o.get('summary', {}).items() if kk != 'loadings'}
        print(f"  요약 {B2K[b]:24s} {o['audit_summary']} · {json.dumps(s, ensure_ascii=False)[:300]}", flush=True)
    return rc or 0


if __name__ == '__main__':
    sys.exit(main())
