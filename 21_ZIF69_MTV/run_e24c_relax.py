# -*- coding: utf-8 -*-
"""MAGI-005 E-24c ② · ③ (Junseok) — 형판 −Cl · −OCH₃ · −C₂H₅ 의 UFF4MOF 처리(risk_screen.run_one 무수정 import · lammps_mof).

  ② 관문 ⑤ 등록판: `--cap 12 --gate5` → results_e24c_gate5_junseok.json. 판정식은 run_e24_gate5.py 와 같음(risk_screen.py:414~423 —
     PLD 전 > 3.3 · LCD 감소 < 20 % · AV/셀 전 > 20 · 최소거리 후 > 0.7), LCD_ref = results_e22b_gate5_hkhome.json 의 e22_parent after LCD(5.24089,
     run_e24_gate5 와 같은 곳에서 읽음). 처리 뒤 PLD · AV/셀 도 같이 적음(등록 (4) 서술 양 — E-24b ③ 표지와 같은 양).
  ③ 서술(판정 아님): `--cap 60` → results_e24c_relax60_junseok.json (E-29 방식).
자: E-29 래퍼(run_e29_relax60.py)와 같음 — rs.OUTER_LOOP_CAP 만 덮음 · 새 STRUCT/WORK 폴더(run_one 은 min_<이름>.data 가 있으면 재사용) ·
    세 구조 LAMMPS 병렬 · Zeo++ 호출(rs.zeo · -chan)만 파일 잠금으로 차례. 측정: 처리 전후 PLD · LCD · AV/셀 · 최소거리 · -chan 1.65 전후 ·
    셀 a b c α β γ V 전후(초격자는 축별 배수로 나눔) · 최종 EDiff · 루프 수. 기계적 사실뿐 — 판정은 종합자.
사용: python run_e24c_relax.py --cap 12 --gate5  /  python run_e24c_relax.py --cap 60   (E24C_DRY=1 이면 설정만 찍고 끝)
"""
import argparse
import fcntl
import json
import os
import re
import shutil
import subprocess
import sys
import time
from concurrent.futures import ProcessPoolExecutor, as_completed

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import risk_screen as rs   # noqa: E402
from ase.io import read    # noqa: E402

TAGS = ['e24c_cl_100', 'e24c_och3_100', 'e24c_c2h5_100']
LOCK = os.path.join(HERE, '.zeo_e24c.lock')
REF = json.load(open(os.path.join(HERE, 'results_e22b_gate5_hkhome.json')))['rows']['e22_parent']['after']['LCD']
_zeo = rs.zeo
GATE5 = False


def zeo_locked(*a, **k):
    with open(LOCK, 'a') as f:
        fcntl.flock(f, fcntl.LOCK_EX)
        try:
            return _zeo(*a, **k)
        finally:
            fcntl.flock(f, fcntl.LOCK_UN)


rs.zeo = zeo_locked        # run_one 은 모듈 전역 zeo 를 부르므로 이것이 쓰임(포크된 워커에도 물려짐)


def chan(path, r=1.65):
    out = f'{path}.chan{r:.2f}'
    with open(LOCK, 'a') as f:
        fcntl.flock(f, fcntl.LOCK_EX)
        try:
            cp = subprocess.run([rs.NETWORK, '-ha', '-chan', f'{r:.2f}', out, path], capture_output=True, text=True, timeout=3600)
        finally:
            fcntl.flock(f, fcntl.LOCK_UN)
    txt = open(out, errors='ignore').read() if os.path.exists(out) else ''
    m = re.search(r'(\d+)\s+channels identified of dimensionality\s*([\d\s]*)', txt)
    mo = re.search(r'Identified (\d+) channels and (\d+) pockets', cp.stdout)
    return {'probe_radius': r, 'rc': cp.returncode, 'n_channels': int(m.group(1)) if m else None,
            'dimensionality': [int(x) for x in m.group(2).split()] if m and m.group(2).strip() else [],
            'channels_stdout': int(mo.group(1)) if mo else None, 'pockets_stdout': int(mo.group(2)) if mo else None,
            'chan_file_head': txt.strip().splitlines()[:4]}


def cell(path):
    a = read(path)
    p = [float(x) for x in a.cell.cellpar()]
    return {'a': p[0], 'b': p[1], 'c': p[2], 'alpha': p[3], 'beta': p[4], 'gamma': p[5], 'V': float(a.get_volume()), 'n_atoms': len(a)}


def job(tag):
    shutil.copy(os.path.join(HERE, 'relax_tnf', f'{tag}_relaxed.cif'), os.path.join(rs.STRUCT, f'ZIF69_{tag}.cif'))
    t0 = time.time()
    n, m0, m1, st = rs.run_one(tag)
    ed, loops = rs.final_ediff(tag)
    d = os.path.join(rs.WORK, tag)
    row = {'status': st, 'before': m0, 'after': m1, 'final_EDiff': ed, 'outer_loops': loops, 'minutes': round((time.time() - t0) / 60, 1)}
    if GATE5 and st == 'ok' and m1 and m1.get('LCD'):          # run_e24_gate5.py 와 같은 식
        drop = (REF - m1['LCD']) / REF * 100
        checks = {'PLD': (m0['PLD'] or 0) > rs.CO2_KINETIC, 'LCD_drop': drop < rs.LCD_DROP_LIMIT,
                  'AV': (m0.get('AV_per_cell') or 0) > rs.AV_FLOOR, 'min_dist': m1['min_dist'] > rs.MIN_DIST_LIMIT}
        row.update({'LCD_drop_pct': round(drop, 2), 'checks': checks, 'pass': all(checks.values())})
    bp, ap = os.path.join(d, 'before.cif'), os.path.join(d, 'after.cif')
    if os.path.exists(bp):
        row['cell_before'] = cell(bp)
        row['chan_before'] = chan(bp)
    if st == 'ok' and os.path.exists(ap):
        ca = cell(ap)
        row['cell_after_supercell'] = ca
        cb = row.get('cell_before')
        if cb:
            k = {x: max(1, round(ca[x] / cb[x])) for x in ('a', 'b', 'c')}
            row['cell_after_per_cell'] = {'rep_abc': [k['a'], k['b'], k['c']], 'a': ca['a'] / k['a'], 'b': ca['b'] / k['b'], 'c': ca['c'] / k['c'],
                                          'alpha': ca['alpha'], 'beta': ca['beta'], 'gamma': ca['gamma'], 'V': ca['V'] / (k['a'] * k['b'] * k['c']),
                                          'rep_product_eq_supercell_rep': k['a'] * k['b'] * k['c'] == (m1 or {}).get('supercell_rep')}
            pc = row['cell_after_per_cell']
            row['cell_change_pct'] = {x: 100.0 * (pc[x] - cb[x]) / cb[x] for x in ('a', 'b', 'c', 'V')}
            row['cell_change_deg'] = {x: pc[x] - cb[x] for x in ('alpha', 'beta', 'gamma')}
        row['chan_after'] = chan(ap)
    return tag, row


def save(res, out):
    tmp = out + '.tmp'
    json.dump(res, open(tmp, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    os.replace(tmp, out)


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--cap', type=int, required=True)
    ap.add_argument('--gate5', action='store_true')
    a = ap.parse_args()
    GATE5 = a.gate5
    rs.OUTER_LOOP_CAP = a.cap
    rs.STRUCT = os.path.join(HERE, f'e24c{a.cap}_stage')
    rs.WORK = os.path.join(HERE, f'lmp_e24c{a.cap}')
    out = os.path.join(HERE, 'results_e24c_gate5_junseok.json' if a.gate5 else f'results_e24c_relax{a.cap}_junseok.json')
    print(f'E-24c 처리 — 대상 {TAGS} · OUTER_LOOP_CAP {rs.OUTER_LOOP_CAP} · INNER {rs.INNER_ITER_CAP} · 관문 ⑤ 판정식 {GATE5} · LCD_ref {REF} · '
          f'STRUCT {rs.STRUCT} · WORK {rs.WORK} · 출력 {out} · NETWORK {rs.NETWORK} · LMP {rs.LMP} · python {sys.executable}', flush=True)
    if os.environ.get('E24C_DRY'):
        print('입력', {t: os.path.exists(os.path.join(HERE, 'relax_tnf', f'{t}_relaxed.cif')) for t in TAGS}, '· 출력 존재', os.path.exists(out),
              '· 폴더 존재', os.path.exists(rs.STRUCT), os.path.exists(rs.WORK), flush=True)
        sys.exit(0)
    n = lambda x: subprocess.run(['pgrep', '-xc', x], capture_output=True, text=True).stdout.strip()
    if n('simulate') not in ('', '0') or n('network') not in ('', '0') or n('lmp_serial') not in ('', '0'):
        print('!! simulate · network · lmp_serial 중 도는 것 있음 — 중단', flush=True)
        sys.exit(1)
    if os.path.exists(out) or os.path.exists(rs.STRUCT) or os.path.exists(rs.WORK):
        print('!! 이전 산출(출력 · STRUCT · WORK) 있음 — 중단', flush=True)
        sys.exit(1)
    os.makedirs(rs.STRUCT)
    os.makedirs(rs.WORK)
    t0 = time.time()
    res = {'test': f"MAGI-005 E-24c {'② 관문 ⑤ 등록판(상한 12)' if GATE5 else f'③ 서술 — 상한 {a.cap} 처리 뒤'}", 'machine': 'junseok',
           'assign': 'ASSIGN_MAGI5B_20260925.md E-24c(1ca1d4f7) · 보완(c702c7e4) · (0)(3e1245a1)',
           'rule': (f'risk_screen.run_one 무수정 · OUTER_LOOP_CAP {a.cap} · INNER {rs.INNER_ITER_CAP} · min_eval 1e-4 · Zeo++ 호출 잠금(차례)'
                    + (' · 판정식 risk_screen.py:414~423(run_e24_gate5.py 와 같음)' if GATE5 else ' · 판정 없음(서술)')),
           'LCD_ref_family': REF if GATE5 else None, 'cap': a.cap, 'started': time.strftime('%F %T'), 'rows': {t: {'status': 'pending'} for t in TAGS}}
    save(res, out)
    with ProcessPoolExecutor(max_workers=len(TAGS)) as ex:
        futs = [ex.submit(job, t) for t in TAGS]
        for fu in as_completed(futs):
            tag, row = fu.result()
            res['rows'][tag] = row
            save(res, out)
            b, af = row.get('before') or {}, row.get('after') or {}
            print(f"{tag} {row['status']} · 루프 {row['outer_loops']} · EDiff {row['final_EDiff']} · 전 PLD {b.get('PLD')} · AV/셀 {b.get('AV_per_cell')} | "
                  f"뒤 PLD {af.get('PLD')} · LCD {af.get('LCD')} · AV/셀 {af.get('AV_per_cell')} · 최소거리 {af.get('min_dist')} · "
                  f"chan {row.get('chan_after', {}).get('n_channels')} · 감소 {row.get('LCD_drop_pct')} % · pass {row.get('pass')} · "
                  f"셀 변화 {({k: round(v, 2) for k, v in row.get('cell_change_pct', {}).items()})} · {row['minutes']} 분", flush=True)
    res['finished'] = True
    res['elapsed_min'] = round((time.time() - t0) / 60, 1)
    save(res, out)
    print(f"저장 {out} · {res['elapsed_min']} 분", flush=True)
