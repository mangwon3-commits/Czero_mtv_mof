# -*- coding: utf-8 -*-
"""MAGI-005 E-29b (HKHOME 18차) — CH₃ · Cl 의 UFF4MOF 닫힘은 **수렴(EDiff < 1e-4)** 에서도 남는가. 등록 ASSIGN_MAGI5B §HKHOME 18차(자료 0건).
Junseok `run_e29_relax60.py`(E-29) 를 데스크탑으로 옮김 — 바꾼 것: 대상 · 상한 300 · 폴더 · 출력 · 기록 문구 · classify 대상. 아래는 원문 설명.


자: run_e24_gate5.py 와 같은 처리 — risk_screen.run_one(무수정 import · UFF4MOF · lammps_mof). 바꾸는 것:
  · rs.OUTER_LOOP_CAP = 300 (E-29 는 60, 관문 ⑤ 는 12 — 래퍼에서 덮음, risk_screen.py 수정 없음)
  · rs.STRUCT = e29b_stage · rs.WORK = lmp_e29b (새 폴더 — run_one 은 min_<이름>.data 가 있으면 재사용하므로 관문 ⑤ 의 lmp_e24 를 쓰면 안 됨)
  · 세 구조의 LAMMPS 는 병렬, Zeo++ 호출만 파일 잠금으로 한 번에 하나(이 기기 Zeo++ 동시 상한 — 초격자 -vol, risk_screen._zeo_worker_cap 과 같은 걱정).
    rs.zeo 를 잠금으로 감쌀 뿐 계산 내용은 같음.
측정(등록): 처리 뒤 PLD · LCD · AV(1.65 Å, /셀) = run_one 의 m1 · `network -ha -chan 1.65`(처리 전 before.cif · 처리 뒤 after.cif) ·
      셀 상수(a b c α β γ V) 전후(처리 뒤 초격자는 축별 배수로 나눈 값도) · 최종 EDiff · 루프 수(rs.final_ediff).
관문 ⑤ 결과(results_e24_gate5_junseok.json)는 건드리지 않음. 출력 results_e29b_relax300_hkhome.json. 기계적 사실뿐 — 판정은 종합자.
E29_DRY=1: 대상 · 경로 · 상한만 찍고 끝.
"""
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

TAGS = ['e24_ch3_100', 'e24c_cl_100']
CAP = 300
STAGE = os.path.join(HERE, 'e29b_stage')
WORK = os.path.join(HERE, 'lmp_e29b')
OUT = os.path.join(HERE, 'results_e29b_relax300_hkhome.json')
LOCK = os.path.join(WORK, '.zeo.lock')
rs.OUTER_LOOP_CAP = CAP
rs.STRUCT = STAGE
rs.WORK = WORK
_zeo = rs.zeo


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
    shutil.copy(os.path.join(HERE, 'relax_tnf', f'{tag}_relaxed.cif'), os.path.join(STAGE, f'ZIF69_{tag}.cif'))
    t0 = time.time()
    n, m0, m1, st = rs.run_one(tag)
    ed, loops = rs.final_ediff(tag)
    d = os.path.join(WORK, tag)
    row = {'status': st, 'before': m0, 'after': m1, 'final_EDiff': ed, 'outer_loops': loops, 'minutes': round((time.time() - t0) / 60, 1)}
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


def classify(rows):
    reg = {}
    for key, t in (('(1)_CH3', 'e24_ch3_100'), ('(2)_Cl', 'e24c_cl_100')):
        r = rows.get(t, {})
        a = r.get('after') or {}
        pld, av = a.get('PLD'), a.get('AV_per_cell')
        if pld is None or av is None:
            continue
        if pld < 3.3 or av < 20:
            b = '성립 쪽(닫힘 유지: PLD < 3.3 이거나 AV/셀 < 20)'
        elif pld >= 3.64 and av > 20:
            b = '기각 쪽(다시 열림: PLD ≥ 3.64 이고 AV/셀 > 20)'
        else:
            b = '띠(3.3 ≤ PLD < 3.64, AV/셀 ≥ 20)'
        ed = r.get('final_EDiff')
        reg[key] = {'PLD_after': pld, 'AV_per_cell_after': av, 'branch': b, 'final_EDiff': ed, 'outer_loops': r.get('outer_loops'),
                    'converged': (ed is not None and ed < 1e-4)}
    return reg


def save(res):
    tmp = OUT + '.tmp'
    json.dump(res, open(tmp, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    os.replace(tmp, OUT)


if __name__ == '__main__':
    print(f'E-29b — 대상 {TAGS} · OUTER_LOOP_CAP {rs.OUTER_LOOP_CAP} · INNER {rs.INNER_ITER_CAP} · STRUCT {rs.STRUCT} · WORK {rs.WORK} · '
          f'NETWORK {rs.NETWORK} · LMP {rs.LMP} · IFACE 존재 {os.path.exists(rs.IFACE)} · python {sys.executable}', flush=True)
    if os.environ.get('E29B_DRY'):
        print('입력', {t: os.path.exists(os.path.join(HERE, 'relax_tnf', f'{t}_relaxed.cif')) for t in TAGS}, '· 출력 존재', os.path.exists(OUT),
              '· 폴더 존재', os.path.exists(STAGE), os.path.exists(WORK), flush=True)
        sys.exit(0)
    n = lambda x: subprocess.run(['pgrep', '-xc', x], capture_output=True, text=True).stdout.strip()
    if n('simulate') not in ('', '0') or n('network') not in ('', '0') or n('lmp_serial') not in ('', '0'):
        print('!! simulate · network · lmp_serial 중 도는 것 있음 — 중단', flush=True)
        sys.exit(1)
    if os.path.exists(OUT) or os.path.exists(STAGE) or os.path.exists(WORK):
        print('!! 이전 E-29b 산출(출력 · e29b_stage · lmp_e29b) 있음 — 중단', flush=True)
        sys.exit(1)
    os.makedirs(STAGE)
    os.makedirs(WORK)
    t0 = time.time()
    res = {'test': 'MAGI-005 E-29b — CH₃ · Cl 닫힘 · UFF4MOF 이완 수렴(상한 300)', 'assign': 'ASSIGN_MAGI5B_20260925.md §HKHOME 18차', 'machine': 'hkhome',
           'rule': 'risk_screen.run_one 무수정 · OUTER_LOOP_CAP 300(래퍼) · INNER 2000 · min_eval 1e-4 · Zeo++ 호출 잠금(순차)', 'cap': CAP,
           'started': time.strftime('%F %T'), 'rows': {t: {'status': 'pending'} for t in TAGS}}
    save(res)
    with ProcessPoolExecutor(max_workers=len(TAGS)) as ex:
        futs = [ex.submit(job, t) for t in TAGS]
        for fu in as_completed(futs):
            tag, row = fu.result()
            res['rows'][tag] = row
            res['registered'] = classify(res['rows'])
            save(res)
            a = row.get('after') or {}
            print(f"{tag} {row['status']} · 루프 {row['outer_loops']} · EDiff {row['final_EDiff']} · 처리 뒤 PLD {a.get('PLD')} · LCD {a.get('LCD')} · "
                  f"AV/셀 {a.get('AV_per_cell')} · chan {row.get('chan_after', {}).get('n_channels')} {row.get('chan_after', {}).get('dimensionality')} · "
                  f"셀 변화 {row.get('cell_change_pct')} · {row['minutes']} 분", flush=True)
    res['finished'] = True
    res['elapsed_min'] = round((time.time() - t0) / 60, 1)
    save(res)
    print(f"저장 {OUT} · {res['elapsed_min']} 분 · 등록 {json.dumps(res.get('registered'), ensure_ascii=False)}", flush=True)
