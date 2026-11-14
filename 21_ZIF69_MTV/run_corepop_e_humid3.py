# -*- coding: utf-8 -*-
"""COREPOP-H323 — CoRE 모집단 3D(CORE22 제외)의 습윤 3성분 흡착점. 사용자 지시 2026-11-14 · `ASSIGN_COREPOP_HUMID323_20261114.md`.
`run_core22_e_humid3.py`(d24e8e2d · CORE22 §C 실행기) 사본 — 래퍼 `run_znbdt_e_humid3.py`(97023663) · 러너 원판 무수정 import. 원판과 다른 것:
  ① 대상: `corepop_humid323_targets.json` 의 묶음(COREPOP_E_BATCHES, 예 b01) 또는 key 목록(COREPOP_E_KEYS). 원판의 "등록 22종의 부분집합" 검사 대신
     "대상 목록 안" 검사. CIF 는 `core_pop_cifs.zip` 바이트(저장소 밖 `~/.mof_chain/corepop_1114/cifs/` · md5 대조 · 원판 그대로).
  ② 막음 표: `corepop_blocks.py` 결과 파일들(COREPOP_BLOCKS 쉼표 · 완주 파일만). 대상 중 세 탐침이 모두 block_ok 가 아닌 구조가 있으면
     시작하지 않음(COREPOP_E_KEYS 로 빼고 착수 글에 적음). 구 0 인 성분은 막음 없음 · BlockPockets 넣는 법 · ok 다시 세기는 원판 그대로.
  ③ 반복 수: COREPOP_E_REPS(기본 1 — 끝난 만큼 쓰는 계산이라 구조 수 먼저). LPT = N_super 큰 순 × r1..(원판 자 그대로) · 홀짝 나누기 없음(묶음 단위).
  ④ 이름: base = corepop_<파일 이름> · 실행 뿌리 · 잠금 · 결과 이름의 core22 → corepop. fc 미상 꼬리표 없음(대상이 formal_charge_nonzero False 만).
조건은 원판(298 K E)이고, 323 K 세 값은 `run_corepop_e_humid3_323.py` 가 RT-E 실행기를 import 해 넣습니다(CORE22 §F 와 같은 방식).
판정 없음 — 종합자.
"""
import hashlib
import json
import os
import shutil
import sys
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
CIFS = os.path.expanduser(os.environ.get('COREPOP_CIFS', '~/.mof_chain/corepop_1114/cifs'))   # 없는 파일은 zip 바이트에서 풂(저장소 밖)
ZIP = os.path.join(HERE, 'core_pop_cifs.zip')
ANN = os.path.join(HERE, 'core_pop_annotated.json')
BLKS = [os.path.join(HERE, f) for f in os.environ.get('COREPOP_BLOCKS', '').split(',') if f]
TGT = os.path.join(HERE, 'corepop_humid323_targets.json')
TGTJ = json.load(open(TGT, encoding='utf-8'))
TROWS = {r['key']: r for r in TGTJ['rows']}
TORDER = [r['key'] for r in TGTJ['rows']]
FC_UNKNOWN = set()                                                         # 대상이 formal_charge_nonzero False 만
GAS = (('1.65', 'CO2'), ('1.82', 'N2'), ('1.30', 'water'))
_BATCHES = [x for x in os.environ.get('COREPOP_E_BATCHES', '').split(',') if x]
KEYS = [k for k in os.environ.get('COREPOP_E_KEYS', '').split(',') if k] or [r['key'] for r in TGTJ['rows'] if r['batch'] in _BATCHES]
SLOT = 'all'
MACHINE = os.environ.get('COREPOP_E_MACHINE', '')
REPS = int(os.environ.get('COREPOP_E_REPS', '1'))
SMOKE = bool(os.environ.get('COREPOP_E_SMOKE'))
DRY = bool(os.environ.get('COREPOP_E_DRY'))
if not MACHINE:
    raise SystemExit('!! COREPOP_E_MACHINE 를 주세요')
if not KEYS or len(set(KEYS)) != len(KEYS) or any(k not in TROWS for k in KEYS):
    raise SystemExit(f'!! 대상이 비었거나 corepop_humid323_targets.json 밖(또는 중복): {KEYS[:5]}')
if _BATCHES and any(TROWS[k]['batch'] not in _BATCHES for k in KEYS):
    raise SystemExit(f'!! COREPOP_E_KEYS 가 묶음 {_BATCHES} 밖: {[k for k in KEYS if TROWS[k]["batch"] not in _BATCHES]}')

import run_aryl_gcmc as rg       # noqa: E402  (ZNBDT_E_* env 와 무관)
from ase.io import read          # noqa: E402

ANNR = {r['key']: r for r in json.load(open(ANN, encoding='utf-8'))['rows']}


def md5b(b):
    return hashlib.md5(b).hexdigest()


def md5(p):
    return md5b(open(p, 'rb').read())


def base_of_key(k):
    return 'corepop_' + ANNR[k]['file'][:-4]


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
                'fc_unknown': k in FC_UNKNOWN, 'base': base_of_key(k)}
KEYS.sort(key=lambda k: (-KINFO[k]['N_super'], TORDER.index(k)))           # LPT(원판 자) · 같으면 대상 순위
BASES = [KINFO[k]['base'] for k in KEYS]
B2K = {KINFO[k]['base']: k for k in KEYS}

os.environ['ZNBDT_E_TARGETS'] = ','.join(BASES)
os.environ['ZNBDT_E_MACHINE'] = MACHINE
os.environ['ZNBDT_E_WORKERS'] = os.environ.get('COREPOP_E_WORKERS', '8')
os.environ['ZNBDT_E_REPS'] = str(REPS)
for v, on in (('ZNBDT_E_SMOKE', SMOKE), ('ZNBDT_E_DRY', DRY)):
    if on:
        os.environ[v] = '1'
    else:
        os.environ.pop(v, None)
import run_znbdt_e_humid3 as E   # noqa: E402  (import 순간 위 env 로 대상 · 반복 · 작업 순서가 정해짐)

MODE = 'smoke' if SMOKE else ('dry' if DRY else None)
ROOT = os.path.join(E.CHAIN, f'corepop_e3_{MODE}_{MACHINE}') if MODE else os.path.join(HERE, 'humid_wc_runs_v3w', f'corepop_e3_{MACHINE}')
E.hw.RUNS = os.path.join(ROOT, 'runs')
E.hw.CHARGED = os.path.join(ROOT, 'cifs')
E.SRC = os.path.join(ROOT, 'src')
E.OUT = (os.path.join(ROOT, f'results_corepop_e_humid3_{MACHINE}_{MODE}.json') if MODE
         else os.path.join(HERE, f'results_corepop_e_humid3_{MACHINE}.json'))
E.AUDIT = E.OUT.replace('.json', '_audit.json')
E.LOCK = os.path.join(E.CHAIN, f'.corepop_e3_{MACHINE}_start.lock')

# ④ LPT 목록(구조 큰 순 × r1 · r2 · r3)과 홀짝 나누기 — 스모크 · 드라이는 래퍼대로 r1 만(나누기 없음)
LPT = [f'{b}_e3r{k}' for b in BASES for k in range(1, REPS + 1)]
if not MODE:
    if E.REPS_RUN != list(range(1, REPS + 1)):
        raise SystemExit(f'!! 래퍼 반복 {E.REPS_RUN} ≠ 1..{REPS}')
    SEL = [t for i, t in enumerate(LPT, 1) if SLOT == 'all' or (i % 2 == 1) == (SLOT == 'odd')]
    E.TAGS = SEL
    E.hw.TARGETS = SEL
    E.JOBS = [(t, lab, p, T, ps) for t in SEL for lab, p, T, ps in E.hw.CONDITIONS]

# ② BLOCKS 표 — C 준비 결과에서 구 수 > 0 인 (구조, 성분)만
_brow = {}
for _f in BLKS:
    _bj = json.load(open(_f, encoding='utf-8'))
    if 'finished' not in _bj:
        raise SystemExit(f'!! {os.path.basename(_f)} 가 완주 파일이 아님 — 중단')
    for _r in _bj['rows']:
        _brow[_r['key']] = _r
SKIPPED = [k for k in KEYS if k not in _brow or any(_brow[k].get(f'r{r}', {}).get('block_ok') is not True
                                                     or _brow[k].get(f'r{r}', {}).get('n_spheres') is None for r, _ in GAS)]
if SKIPPED:
    raise SystemExit(f'!! 막음 결과가 없거나 ok 가 아닌 구조 {len(SKIPPED)}: {SKIPPED} — COREPOP_E_KEYS 로 빼고 다시(착수 글에 적기)')
BLOCKS = {}
for k in KEYS:
    for r, g in GAS:
        x = _brow[k][f'r{r}']
        if x['n_spheres'] > 0:
            BLOCKS.setdefault(KINFO[k]['base'], {})[g] = (os.path.join(HERE, x['block_file']), x['block_md5'])
E.BLOCKS = BLOCKS

_orig_patch = E.patch_input
_orig_row = E.row_of
_orig_sum = E.summarize
BP = '            BlockPockets              yes\n            BlockPocketsFileName      blk_{}\n'


def patch_input(s, base):
    s = _orig_patch(s, None)                     # 원판 그대로 · 막음 없음(None 은 BLOCKS 에 없음)
    gs = BLOCKS.get(base, {})
    for i, g in ((0, 'CO2'), (1, 'water'), (2, 'N2')):
        if g not in gs:
            continue
        a = E.head(i, g)
        if s.count(a) != 1:
            raise RuntimeError(f'{g} 막음 앵커가 {s.count(a)}회 — RASPA 안 띄움')
        s = s.replace(a, a + BP.format(g.lower()))
    n = s.count('BlockPockets              yes')
    if n != len(gs):
        raise RuntimeError(f'막음 줄 {n} ≠ 표의 성분 수 {len(gs)} — RASPA 안 띄움')
    return s


def row_of(tag, status, info):
    r = _orig_row(tag, status, info)
    if 'why' in r:                               # .data 개수 이상 — 원판이 이미 ok False
        return r
    base = E.base_of(tag)
    gs = BLOCKS.get(base, {})
    gates = [r['finished'], r['loading_line_counts'] == {'CO2': 1, 'N2': 1, 'water': 1}, r['returncode'] == 0,
             r['stderr_not_found'] is False, not r['not_found_in_output'], r['net_charge_ok'], r['input_components'] == 3,
             r['component2_N2_in_output'], r['seed'] is not None]
    for g in gs:
        c = r['block'][g]
        gates += [c.get('blocked_line') is True, c.get('n_blocked_eq_spheres_x_cells') is True]
    gates.append(r['input_blockpockets_lines'] == len(gs))
    d = os.path.join(E.hw.RUNS, f'ads_{tag}')
    data = E.glob.glob(os.path.join(d, 'Output', 'System_0', '*.data'))
    ba = E.block_audit(open(data[0], encoding='utf-8', errors='ignore').read()) if len(data) == 1 else {}
    clean = {g: ba.get(g, {}).get('blocked_line') is False for g in ('CO2', 'N2', 'water') if g not in gs}
    gates.append(all(clean.values()))
    r.update(ok_wrapper_original=r['ok'], ok=bool(all(gates)), blocked_components=sorted(gs), unblocked_components_clean=clean,
             core_key=B2K.get(base))
    return r


def summarize(rows, info, t_start):
    out = _orig_sum(rows, info, t_start)
    out.update(test='COREPOP-H323 — CoRE 모집단 3D 습윤 3성분 흡착점',
               assign='ASSIGN_COREPOP_HUMID323_20261114.md',
               thin_runner='run_corepop_e_humid3.py', thin_runner_md5=md5(os.path.abspath(__file__)),
               batches=_BATCHES, reps=REPS, lpt_list=LPT, selected=list(E.TAGS),
               corepop={b: {**KINFO[B2K[b]], 'rank': TROWS[B2K[b]]['rank'], 'batch': TROWS[B2K[b]]['batch'], 'cif_md5': info['cifs'][b]['md5'],
                            'blocked_components': sorted(BLOCKS.get(b, {}))} for b in BASES},
               blocks_source=[{'file': os.path.basename(f), 'md5': md5(f)} for f in BLKS],
               targets_source={'file': os.path.basename(TGT), 'md5': md5(TGT)},
               cif_source={'zip': os.path.basename(ZIP), 'zip_md5': md5(ZIP), 'unpacked': CIFS},
               note='CIF 이름의 _DDEC6 는 래퍼 규칙일 뿐 — 전하는 CoRE CIF 의 것. 구 0 인 성분은 막음 없음. ok 는 얇은 실행기가 다시 셈(ok_wrapper_original 병기).')
    for b, m in out['materials'].items():
        m['core_key'] = B2K.get(b)
        m['blocked_components'] = sorted(BLOCKS.get(b, {}))
        m['fc_unknown'] = KINFO[B2K[b]]['fc_unknown']
    tmp = E.OUT + '.tmp'
    json.dump(out, open(tmp, 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
    os.replace(tmp, E.OUT)
    return out


E.patch_input = patch_input
E.row_of = row_of
E.summarize = summarize


def stage():
    """CoRE CIF → src/<base>_DDEC6.cif 바이트 같은 사본(zip 바이트 md5 대조)."""
    zf = zipfile.ZipFile(ZIP)
    names = set(zf.namelist())
    os.makedirs(E.SRC, exist_ok=True)
    for k in KEYS:
        f = ANNR[k]['file']
        if f not in names:
            raise SystemExit(f'!! zip 에 {f} 없음')
        m = md5b(zf.read(f))
        p = os.path.join(CIFS, f)
        if md5(p) != m:
            raise SystemExit(f'!! 풀린 {p} md5 ≠ zip 바이트')
        dst = os.path.join(E.SRC, KINFO[k]['base'] + '_DDEC6.cif')
        if not os.path.exists(dst):
            shutil.copyfile(p, dst)
        if md5(dst) != m:
            raise SystemExit(f'!! 사본 {dst} md5 ≠ zip 바이트')


def main():
    print(f'COREPOP-H — 기기 {MACHINE} · {len(KEYS)}종 · 묶음 {_BATCHES} · 반복 {REPS} · 모드 {MODE or "실행"} · 작업 {len(E.TAGS)} · '
          f'막음 표 {[os.path.basename(f) for f in BLKS]}', flush=True)
    if not MODE:
        for i, t in enumerate(LPT, 1):
            print(f"  LPT {i:2d} {'●' if t in E.TAGS else '·'} {B2K[E.base_of(t)]:24s} r{t[-1]}", flush=True)
    for k in KEYS:
        i = KINFO[k]
        print(f"  {k:24s} N_super {i['N_super']:5d} · 셀 {i['unit_cells']} · 막음 {sorted(BLOCKS.get(i['base'], {})) or '없음'}"
              f"{' · fc 미상' if i['fc_unknown'] else ''}", flush=True)
    if os.path.exists(E.OUT) or any(os.path.exists(os.path.join(E.hw.RUNS, f'ads_{t}')) for t in E.TAGS):
        print('  !! 이전 결과 · 실행 폴더 있음 — 중단', flush=True)
        return 1
    stage()
    return E.main()


if __name__ == '__main__':
    sys.exit(main())
