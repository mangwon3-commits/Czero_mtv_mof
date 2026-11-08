# -*- coding: utf-8 -*-
"""6SEED_CORE §C — CoRE 3차원 22종의 습윤 3성분 선택도 S_humid. 등록 `ASSIGN_ZNBDT_6SEED_CORE_20261108.md` §C(+ 19:2x 순찰 11/20 순서 변경).
`run_znbdt_e_humid3.py`(97023663)를 import 하는 얇은 실행기 — 래퍼 · 러너(run_humid_wc_v3w · run_humid_wc) 원판 무수정. 바꾸는 것(등록 §C 실행기 줄):
  ① 대상: CoRE CIF — `core_pop_cifs.zip` 안의 바이트 그대로(§AV 와 같은 파일 · CoRE 기하 · CoRE 전하). 저장소 밖
     `~/.mof_chain/core22_1108/cifs/` 에 풀린 파일을 **zip 안 바이트와 md5 대조**한 뒤, 실행 뿌리 아래 `src/<base>_DDEC6.cif` 로 바이트 같은 사본.
     `_DDEC6` 는 래퍼의 파일 이름 규칙일 뿐이고 전하는 CoRE CIF 의 것입니다. base = `core22_<파일 이름에서 .cif 뺀 것>`.
     풀린 폴더(CORE22_CIFS)에 없는 파일은 import 때 zip 에서 그 바이트를 풀어 둡니다(다른 기기용 · 저장소 밖).
  ② BLOCKS 표: C 준비 결과(`results_core22_blocks_laptop.json`)에서 구 수 > 0 인 (구조, 성분)만 — 1.65 → CO₂ · 1.82 → N₂ · 1.30 → 물.
     **구 0 인 성분은 막음 없음**(등록 §C 준비). 래퍼는 막음 대상 구조의 세 성분을 모두 막도록 짜여 있어 두 곳만 감쌉니다.
       · patch_input: 래퍼 원판을 막음 없이 부른 뒤, 표에 있는 성분에만 BlockPockets 두 줄을 넣음(앵커는 성분마다 정확히 한 번).
       · row_of: 래퍼 원판의 행을 받아 ok 를 같은 표지로 다시 셈. 다른 점은 둘 — 막음 줄 수 조건(원판 "== 3" → "== 표의 성분 수")과,
         막지 않은 성분의 출력에 `Pockets are blocked for this component` 가 **없다**는 조건 하나를 더함.
  ③ 기기 · 실행 뿌리(`humid_wc_runs_v3w/core22_e3_<기기>`, gitignore) · 잠금 · 결과 이름(`results_core22_e_humid3_<기기>.json` + `_audit.json`).
  ④ 순서 · 나누기: **LPT 목록 66 = 22종 × 반복 r1 · r2 · r3** — N_super(= 원자 수 × unit_cells() 셀 수) 큰 순, 같으면 등록 순서,
     구조 안에서는 r1 → r2 → r3(CLAUDE.md §5 의 자). **홀수 번째 33 = 랩탑 · 짝수 번째 33 = HKHOME**(20:5x 순찰 14/20 · 등록 [20:5x 갱신]).
     CORE22_E_SLOT = odd | even | all 로 고릅니다. 한 구조의 세 반복이 두 기기에 2 · 1 로 갈립니다(바이트 같은 사본 · 씨앗 = 착수 초).
조건 E 그대로: 298 K · 100 kPa · y 0.150000/0.821479/0.028521 · 5,000 + 15,000 · UFF_MOF · 전하 CIF 그대로 · 단위셀은 래퍼 규칙(unit_cells()) ·
3씨앗(바이트 같은 사본 · 씨앗 = 착수 초 · 15 s 간격 + 2 s 잠금).
env  CORE22_E_SLOT odd | even | all(기본 odd) · CORE22_E_MACHINE(기본 laptop) · CORE22_E_WORKERS(기본 8)
     CORE22_E_KEYS 쉼표(core_pop key · 기본 = 22종 전부 · 스모크 · 드라이에서 일부만 볼 때)
     CORE22_BLOCKS(기본 results_core22_blocks_laptop.json)
     CORE22_E_SMOKE=1 / CORE22_E_DRY=1 → 래퍼의 스모크(10 사이클 · r1) · 드라이(RASPA 안 띄우고 고친 입력만). 실행 뿌리는 저장소 밖
     `~/.mof_chain/core22_e3_{smoke,dry}_<기기>`.
판정 없음 — 종합자.
"""
import hashlib
import json
import os
import shutil
import sys
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
CIFS = os.path.expanduser(os.environ.get('CORE22_CIFS', '~/.mof_chain/core22_1108/cifs'))   # 없는 파일은 zip 바이트에서 풂(저장소 밖)
ZIP = os.path.join(HERE, 'core_pop_cifs.zip')
ANN = os.path.join(HERE, 'core_pop_annotated.json')
BLK = os.path.join(HERE, os.environ.get('CORE22_BLOCKS', 'results_core22_blocks_laptop.json'))
ALL22 = ('2021[Zn][srs]3[FSR]1', '2017[Zn][dia]3[ASR]1', '2017[Zn][dia]3[FSR]1', '2024[Cu][srs]3[FSR]2', '2024[Co][pcu]3[ASR]1',
         '2024[Co][pcu]3[FSR]1', '2024[Zn][ths]3[ASR]1', '2024[Zn][ths]3[FSR]1', '2014[Cu][dia]3[FSR]6', '2014[Cu][dia]3[FSR]2',
         '2014[Cu][dia]3[ASR]5', '2014[Cu][dia]3[ASR]1', '2018[Cd][dia]3[FSR]5', '2018[Cd][dia]3[ASR]6', '2019[Ni][pcu]3[ASR]1',
         '2018[Cd][dia]3[ASR]5', '2018[Cd][dia]3[FSR]3', '2018[Cd][dia]3[ASR]4', '2018[Cd][dia]3[FSR]4', '2021[Co][dia]3[ASR]1',
         '2021[Co][dia]3[FSR]1', '2019[Zn][pcu]3[ASR]1')                     # 등록 §C 대상 22 · 등록 순서
FC_UNKNOWN = {'2024[Cu][srs]3[FSR]2', '2024[Zn][ths]3[ASR]1', '2024[Zn][ths]3[FSR]1', '2014[Cu][dia]3[FSR]2', '2014[Cu][dia]3[ASR]1',
              '2019[Ni][pcu]3[ASR]1'}                                       # 등록 §C "fc 미상" 6행 — 표에 꼬리표
GAS = (('1.65', 'CO2'), ('1.82', 'N2'), ('1.30', 'water'))
KEYS = [k for k in os.environ.get('CORE22_E_KEYS', ','.join(ALL22)).split(',') if k]
SLOT = os.environ.get('CORE22_E_SLOT', 'odd')
MACHINE = os.environ.get('CORE22_E_MACHINE', 'laptop')
SMOKE = bool(os.environ.get('CORE22_E_SMOKE'))
DRY = bool(os.environ.get('CORE22_E_DRY'))
if not KEYS or len(set(KEYS)) != len(KEYS) or any(k not in ALL22 for k in KEYS):
    raise SystemExit(f'!! CORE22_E_KEYS 가 등록 22종의 부분집합(중복 없음)이 아님: {KEYS}')
if SLOT not in ('odd', 'even', 'all'):
    raise SystemExit(f'!! CORE22_E_SLOT 은 odd · even · all 중 하나: {SLOT}')

import run_aryl_gcmc as rg       # noqa: E402  (ZNBDT_E_* env 와 무관)
from ase.io import read          # noqa: E402

ANNR = {r['key']: r for r in json.load(open(ANN, encoding='utf-8'))['rows']}


def md5b(b):
    return hashlib.md5(b).hexdigest()


def md5(p):
    return md5b(open(p, 'rb').read())


def base_of_key(k):
    return 'core22_' + ANNR[k]['file'][:-4]


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
KEYS.sort(key=lambda k: (-KINFO[k]['N_super'], ALL22.index(k)))            # LPT
BASES = [KINFO[k]['base'] for k in KEYS]
B2K = {KINFO[k]['base']: k for k in KEYS}

os.environ['ZNBDT_E_TARGETS'] = ','.join(BASES)
os.environ['ZNBDT_E_MACHINE'] = MACHINE
os.environ['ZNBDT_E_WORKERS'] = os.environ.get('CORE22_E_WORKERS', '8')
os.environ['ZNBDT_E_REPS'] = '3'
for v, on in (('ZNBDT_E_SMOKE', SMOKE), ('ZNBDT_E_DRY', DRY)):
    if on:
        os.environ[v] = '1'
    else:
        os.environ.pop(v, None)
import run_znbdt_e_humid3 as E   # noqa: E402  (import 순간 위 env 로 대상 · 반복 · 작업 순서가 정해짐)

MODE = 'smoke' if SMOKE else ('dry' if DRY else None)
ROOT = os.path.join(E.CHAIN, f'core22_e3_{MODE}_{MACHINE}') if MODE else os.path.join(HERE, 'humid_wc_runs_v3w', f'core22_e3_{MACHINE}')
E.hw.RUNS = os.path.join(ROOT, 'runs')
E.hw.CHARGED = os.path.join(ROOT, 'cifs')
E.SRC = os.path.join(ROOT, 'src')
E.OUT = (os.path.join(ROOT, f'results_core22_e_humid3_{MACHINE}_{MODE}.json') if MODE
         else os.path.join(HERE, f'results_core22_e_humid3_{MACHINE}.json'))
E.AUDIT = E.OUT.replace('.json', '_audit.json')
E.LOCK = os.path.join(E.CHAIN, f'.core22_e3_{MACHINE}_start.lock')

# ④ LPT 목록(구조 큰 순 × r1 · r2 · r3)과 홀짝 나누기 — 스모크 · 드라이는 래퍼대로 r1 만(나누기 없음)
LPT = [f'{b}_e3r{k}' for b in BASES for k in (1, 2, 3)]
if not MODE:
    if E.REPS_RUN != [1, 2, 3]:
        raise SystemExit(f'!! 래퍼 반복 {E.REPS_RUN} ≠ [1, 2, 3]')
    SEL = [t for i, t in enumerate(LPT, 1) if SLOT == 'all' or (i % 2 == 1) == (SLOT == 'odd')]
    E.TAGS = SEL
    E.hw.TARGETS = SEL
    E.JOBS = [(t, lab, p, T, ps) for t in SEL for lab, p, T, ps in E.hw.CONDITIONS]

# ② BLOCKS 표 — C 준비 결과에서 구 수 > 0 인 (구조, 성분)만
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
    out.update(test='6SEED_CORE §C — CoRE 3차원 22종 습윤 3성분 선택도 S_humid',
               assign='ASSIGN_ZNBDT_6SEED_CORE_20261108.md §C · [20:5x 갱신](LPT 목록 66 의 홀수 번째 = 랩탑 · 짝수 번째 = HKHOME)',
               thin_runner='run_core22_e_humid3.py', thin_runner_md5=md5(os.path.abspath(__file__)),
               slot=None if MODE else SLOT, lpt_list=LPT, selected=list(E.TAGS),
               core22={b: {**KINFO[B2K[b]], 'cif_md5': info['cifs'][b]['md5'], 'blocked_components': sorted(BLOCKS.get(b, {}))} for b in BASES},
               blocks_source={'file': os.path.basename(BLK), 'md5': md5(BLK)},
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
    print(f'CoRE 22 §C — 기기 {MACHINE} · {len(KEYS)}종 · 모드 {MODE or "실행"} · 몫 {"래퍼 r1" if MODE else SLOT} · 작업 {len(E.TAGS)} · '
          f'막음 표 {os.path.basename(BLK)}', flush=True)
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
