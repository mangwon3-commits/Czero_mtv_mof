#!/usr/bin/env python
"""T-NF 앞단 ① — 비-ZIF-69 골격의 GFN-FF 셀 고정 이완 (2026-09-10 신설).

등록문 `TNF_REGISTRATION_20260910.md` §1 의 "xtb GFN-FF 이완(셀 고정)" 단계입니다.

    ⚠️ 새 파일입니다. `relax_series_v3.py` · `judge_relax_v3.py` · `relax_criteria.py`
       는 **한 줄도 고치지 않았습니다.** 살아 있는 v3 계열이 그 위에서 돕니다
       (CLAUDE.md §6).

## 왜 `relax_series_v3.py` 를 그대로 못 쓰나
`REUSE_V3_SCRIPTS_FOR_NONZIF69_20260910.md` §1~§2 가 실측으로 적은 세 가지입니다.

    (가) SRC 가 `structures_v2/` glob, OUT 이 `relax_v3/` — 다른 계열을 v3 서랍에
         넣으면 `judge_relax_v3.py` 가 `structures_v2/<n>.cif` 를 못 찾아 죽고,
         그 파일이 `charge_v3.py` 의 관문이라 **v3 전체의 전하 단계가 멈춥니다.**
    (나) 판정 ③ `3_ZnN` 이 Zn 없는 골격에서 `None` 서식 폭탄을 내고 **배치를 통째로**
         죽입니다(MUF-16 은 Co 카복실레이트라 반드시 걸립니다).
    (다) 판정 ② 방향족 C-C 폭이 이웃 3 인 **알데하이드/카복시 탄소**(-CHO, -COOH)를
         고리 C-C 와 한 통에 넣어 ZIF-90/93/94/96/97 을 전부 거짓 실패로 찍습니다
         (2026-08-16 `cf3Im075` 오탐과 같은 계열).

그래서 SRC/OUT 을 분리한 얇은 사본을 새로 씁니다 — `charge_anchor_zif93.py`(08-21)
가 이미 보여 준 형태입니다.

## 이 파일은 **판정하지 않습니다 — 잽니다**
등록문 §1 의 앞단에는 이완 통과/탈락 문턱이 등록돼 있지 않습니다(등록된 문턱은
㉠~㉣ 이고 전부 GCMC·Zeo++ 쪽입니다). 결과를 본 뒤 문턱을 만들면 CLAUDE.md §2
위반입니다. 그래서 여기서는 다섯 수를 **재서 JSON 에 남기기만** 합니다:

    C-H 중앙값 · 방향족 C-C 폭(O 이웃 탄소 제외) · 금속-N/금속-O 범위 ·
    최소 원자간 거리 · 셀 변화량

금속은 `Zn` 으로 박지 않고 **구조에 있는 금속**을 씁니다. 금속이 N 과 결합하지
않는 골격(MUF-16 은 카복실레이트 O 배위)에서는 그 항이 `null` 입니다 —
**`false` 가 아닙니다.** "검사에 걸렸다" 와 "검사 대상이 아니다" 는 다릅니다.

## 실패하면 아무것도 남기지 않습니다
`relax_series_v3.py:104` 의 2026-08-19 교훈 그대로입니다. xtb 가 없는 기기에서
0단계로 죽으면 원본 기하가 `_relaxed.cif` 로 나가고, "있으면 건너뜀" 규칙과
맞물려 가짜가 고착됩니다. `err is None and ncalls > 0` 일 때만 씁니다.

## 사용
    RELAX_WORKERS=2 nice -n 19 python relax_tnf.py --job zif71=external_cif/ZIF-71_RASPAdist_P1.cif
    (--job 은 여러 번 줄 수 있습니다. 출력 relax_tnf/<tag>_relaxed.cif)
"""
import argparse
import collections
import json
import multiprocessing as mp
import os
import sys
import time

import numpy as np
from ase.io import read, write
from ase.neighborlist import neighbor_list
from ase.optimize import FIRE

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from relax_fixcell import XTBGrad          # noqa: E402
from relax_criteria import COV             # noqa: E402

OUT = os.path.join(HERE, 'relax_tnf')
RESULT = os.path.join(HERE, 'relax_tnf_results.json')
FMAX = 0.05
STEPS = 800
METALS = ('Zn', 'Co', 'Mn', 'Ni', 'Cu', 'Fe', 'Mg', 'Cd', 'Zr', 'Al')


def measure(atoms):
    """원소쌍별 결합 길이. 방향족 C-C 통에서 O 를 이웃으로 갖는 탄소를 뺍니다."""
    syms = sorted(set(atoms.get_chemical_symbols()))
    missing = [s for s in syms if s not in COV]
    if missing:
        return {'error': f'COV 에 없는 원소: {missing}'}
    cut = {(a, b): 1.25 * (COV[a] + COV[b]) for a in syms for b in syms}
    i, j, d = neighbor_list('ijd', atoms, cut)
    s = atoms.get_chemical_symbols()
    deg = collections.Counter(i)
    has_O = collections.defaultdict(bool)
    for a, b in zip(i, j):
        if s[b] == 'O':
            has_O[a] = True
    out = collections.defaultdict(list)
    for a, b, dd in zip(i, j, d):
        if a >= b:
            continue
        key = tuple(sorted((s[a], s[b])))
        if key == ('C', 'C'):
            sp2 = (deg[a] == 3 and deg[b] == 3
                   and not has_O[a] and not has_O[b])
            key = ('C', 'C') if sp2 else ('C', 'C_other')
        out[key].append(float(dd))
    arr = {k: np.array(v) for k, v in out.items()}

    def rng(k):
        v = arr.get(k)
        return None if v is None else [float(v.min()), float(v.max()), int(len(v))]

    metal = [m for m in METALS if m in syms]
    cc = arr.get(('C', 'C'))
    ch = arr.get(('C', 'H'))
    m = {
        'metals': metal,
        'CH_median': float(np.median(ch)) if ch is not None else None,
        'CH_n': int(len(ch)) if ch is not None else 0,
        'aromCC_width': float(cc.max() - cc.min()) if cc is not None else None,
        'aromCC_n': int(len(cc)) if cc is not None else 0,
        'aromCC_range': rng(('C', 'C')),
        'otherCC_range': rng(('C', 'C_other')),
        'metal_N': {mm: rng(tuple(sorted((mm, 'N')))) for mm in metal},
        'metal_O': {mm: rng(tuple(sorted((mm, 'O')))) for mm in metal},
    }
    # 금속-N 이 없는 골격은 null 입니다 (false 가 아닙니다).
    return m


def min_distance(atoms):
    d = neighbor_list('d', atoms, 1.3)
    return float(d.min()) if len(d) else float('inf')


def one(job):
    tag, cif = job
    wd = os.path.join(OUT, tag)
    dst = os.path.join(OUT, f'{tag}_relaxed.cif')
    if os.path.exists(dst):
        return {'tag': tag, 'src': cif, 'skipped': True, 'out': dst}
    os.makedirs(wd, exist_ok=True)

    t0 = time.time()
    atoms = read(cif)
    order = np.argsort(atoms.get_chemical_symbols(), kind='stable')
    atoms = atoms[order]
    cell0 = atoms.get_cell().copy()
    before = measure(atoms)
    dmin0 = min_distance(atoms)

    calc = XTBGrad(wd, method='gfnff', nthreads=2)
    atoms.calc = calc
    opt = FIRE(atoms, trajectory=os.path.join(wd, 'relax.traj'), maxstep=0.1,
               logfile=os.path.join(wd, 'opt.log'))
    try:
        opt.run(fmax=FMAX, steps=STEPS)
        err = None
    except Exception as e:                                  # noqa: BLE001
        err = f'{type(e).__name__}: {e}'

    moved = float(np.abs(atoms.get_cell() - cell0).max())
    after = measure(atoms)
    dmin1 = min_distance(atoms)

    wrote = err is None and calc.ncalls > 0
    if wrote:
        write(dst, atoms)
    else:
        print(f'  [실패] {tag:12s} 결과 CIF 를 쓰지 않습니다 — '
              f"{err or '0단계에서 끝남 (xtb 가 이 기기에 있습니까?)'}", flush=True)
    for f in ('gfnff_topo', 'POSCAR', 'gradient', 'energy', 'charges', 'xtbrestart'):
        p = os.path.join(wd, f)
        if os.path.exists(p):
            os.remove(p)

    row = {'tag': tag, 'src': os.path.abspath(cif), 'skipped': False,
           'error': err, 'steps': calc.ncalls,
           'minutes': round((time.time() - t0) / 60, 1),
           'fmax_reached': (float(np.abs(atoms.get_forces()).max())
                            if err is None else None),
           'wrote_cif': wrote, 'out': dst if wrote else None,
           'cell_moved': moved, 'dmin_before': dmin0, 'dmin_after': dmin1,
           'before': before, 'after': after,
           'note': '측정값입니다. 등록문 §1 앞단에는 이완 통과 문턱이 없습니다 '
                   '(CLAUDE.md §2 — 결과를 보고 문턱을 만들지 않습니다).'}
    print(f'  [{"이완" if wrote else "실패"}] {tag:12s} '
          f'{row["minutes"]:5.1f}분 {calc.ncalls:4d}단계  '
          f'C-H {after.get("CH_median")}  C-C폭 {after.get("aromCC_width")}  '
          f'최소거리 {dmin1:.3f}  셀변화 {moved:.2e}', flush=True)
    return row


def main(argv=None):
    ap = argparse.ArgumentParser(description='T-NF 앞단 GFN-FF 셀 고정 이완')
    ap.add_argument('--job', action='append', required=True,
                    metavar='tag=path', help='여러 번 줄 수 있습니다')
    ap.add_argument('--out', default=RESULT)
    a = ap.parse_args(argv)

    jobs = []
    for spec in a.job:
        if '=' not in spec:
            print(f'!! --job 형식은 tag=path 입니다: {spec}')
            return 2
        tag, path = spec.split('=', 1)
        path = path if os.path.isabs(path) else os.path.join(HERE, path)
        if not os.path.exists(path):
            print(f'!! 구조 없음: {path}  (tag {tag})')
            return 2
        jobs.append((tag, path))

    os.makedirs(OUT, exist_ok=True)
    nw = max(1, int(os.environ.get('RELAX_WORKERS', 2)))
    print(f'  T-NF 이완 {len(jobs)}종, 워커 {nw} x 스레드 2, 셀 고정, '
          f'fmax {FMAX} / {STEPS}단계', flush=True)
    print(f'  출력 {OUT}/<tag>_relaxed.cif  (v3 서랍 relax_v3/ 에 섞지 않습니다)',
          flush=True)

    rows = []
    if nw == 1 or len(jobs) == 1:
        for j in jobs:
            rows.append(one(j))
    else:
        with mp.Pool(processes=nw, maxtasksperchild=1) as pool:
            for r in pool.imap_unordered(one, jobs, chunksize=1):
                rows.append(r)

    prior = []
    if os.path.exists(a.out):
        try:
            prior = json.load(open(a.out, encoding='utf-8'))
        except Exception:                                   # noqa: BLE001
            prior = []
    merged = {r['tag']: r for r in prior if isinstance(r, dict) and 'tag' in r}
    for r in rows:
        merged[r['tag']] = r
    json.dump([merged[k] for k in sorted(merged)],
              open(a.out, 'w', encoding='utf-8'), indent=2, ensure_ascii=False)
    print(f'[OK] {a.out}', flush=True)
    bad = [r['tag'] for r in rows if not r.get('skipped') and not r.get('wrote_cif')]
    return 1 if bad else 0


if __name__ == '__main__':
    sys.exit(main())
