# -*- coding: utf-8 -*-
"""COREPOP-H323 준비 — CoRE 모집단 3D(CORE22 제외)의 Zeo++ 막음 파일, 세 탐침(CO₂ 1.65 · N₂ 1.82 · 물 1.30 Å). 사용자 지시 2026-11-14.
`core22_blocks_laptop.py`(CORE22 막음 파일을 만든 호출) 사본 — 측정 · 파싱 · 실패 표지(n_spheres None ≠ 구 0)는 원판 그대로. 바꾼 것:
  · 대상: `corepop_humid323_targets.json` 의 묶음(env COREPOP_BATCHES, 예 b01,b02) · CIF 는 `core_pop_cifs.zip` 바이트를 저장소 밖
    `~/.mof_chain/corepop_1114/cifs/` 에 풀어 md5 대조(CLAUDE.md §0 09-23) · 원자 수 = NAtoms 대조.
  · 병렬: env COREPOP_ZEO_PAR(기본 1). 새 호출은 MemAvailable ≥ COREPOP_START_MB(기본 8,000) 일 때만 띄움 · 호출마다 MemAvailable <
    ZEO_GUARD_MB(기본 5,000) 이면 kill(원판 그대로). **simulate 가 하나라도 있으면 띄우지 않고 멈춤**(CLAUDE.md §5 — Zeo++ 와 RASPA 동시 금지).
    원판의 "network 가 있으면 멈춤" 은 병렬이라 뺐음(자기 호출끼리). 가드 kill · rc≠0 인 호출은 묶음 끝에서 **한 번에 하나로** 한 번 더.
  · 폴더 `corepop_zeo_runs/<파일 이름>/block<r>/` · 결과 `results_corepop_blocks_<기기>_<묶음>.json`(env COREPOP_MACHINE).
    저장소에 올리는 것은 `.block` 과 결과 JSON 뿐(CIF 사본 · zeo_block.out 은 안 올림 — CORE22 관례).
기계적 사실뿐 — 판정은 종합자.
사용: COREPOP_MACHINE=laptop COREPOP_BATCHES=b01 COREPOP_ZEO_PAR=3 python corepop_blocks.py   (COREPOP_ZEO_DRY=1 이면 입력 대조 · 계획만)
"""
import glob
import hashlib
import json
import math
import os
import re
import shutil
import subprocess
import sys
import threading
import time
import zipfile
from concurrent.futures import ThreadPoolExecutor

from ase.io import read

D = os.path.dirname(os.path.abspath(__file__))
HOME = os.path.expanduser('~')
ZEO = os.path.join(HOME, 'miniconda3/envs/czeromof/bin/network')
CIFS = os.path.join(HOME, '.mof_chain/corepop_1114/cifs')
ZIP = os.path.join(D, 'core_pop_cifs.zip')
ANN = os.path.join(D, 'core_pop_annotated.json')
TGT = os.path.join(D, 'corepop_humid323_targets.json')
BASE = os.path.join(D, 'corepop_zeo_runs')
MACHINE = os.environ.get('COREPOP_MACHINE', '')
BATCHES = [b for b in os.environ.get('COREPOP_BATCHES', '').split(',') if b]
PAR = int(os.environ.get('COREPOP_ZEO_PAR', '1'))
START_MB = int(os.environ.get('COREPOP_START_MB', '8000'))
OUT = os.path.join(D, f"results_corepop_blocks_{MACHINE}_{'_'.join(BATCHES)}.json")
NS = 50000
RADII = (1.65, 1.82, 1.30)
GAS = {1.65: 'CO2', 1.82: 'N2', 1.30: 'water'}
GUARD_MB = int(os.environ.get('ZEO_GUARD_MB', '5000'))
DRY = bool(os.environ.get('COREPOP_ZEO_DRY'))
if not MACHINE or not BATCHES:
    raise SystemExit('!! COREPOP_MACHINE · COREPOP_BATCHES 를 주세요')
_T = json.load(open(TGT, encoding='utf-8'))
KEYS = [r['key'] for r in _T['rows'] if r['batch'] in BATCHES]
if not KEYS:
    raise SystemExit(f'!! 묶음 {BATCHES} 에 대상 없음')
_LAUNCH = threading.Lock()


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


def counts():
    n = lambda x: subprocess.run(['pgrep', '-xc', x], capture_output=True, text=True).stdout.strip() or '0'
    return {'simulate': int(n('simulate')), 'network': int(n('network'))}


def run_guarded(args, cwd, out):
    with _LAUNCH:                                   # 띄우기는 한 번에 하나 · 메모리 여유를 보고
        while True:
            c = counts()
            if c['simulate']:
                raise RuntimeError(f'Zeo++ 직전 검사: {c} — simulate 있음 · 멈춤(CLAUDE.md §5)')
            if avail_mb() >= START_MB:
                break
            time.sleep(5)
        t0 = time.time()
        fh = open(os.path.join(cwd, out), 'w')
        p = subprocess.Popen(args, cwd=cwd, stdout=fh, stderr=subprocess.STDOUT)
        time.sleep(3)
    with fh:
        peak, stopped = 0, False
        while p.poll() is None:
            peak = max(peak, rss_mb(p.pid))
            if avail_mb() < GUARD_MB:
                p.kill()
                stopped = True
            time.sleep(1)
    return p.returncode, round(time.time() - t0, 1), peak, stopped, c


def md5b(b):
    return hashlib.md5(b).hexdigest()


def md5(p):
    return md5b(open(p, 'rb').read())


def inputs():
    """zip namelist · md5 대조 · 원자 수 대조. 하나라도 어긋나면 SystemExit."""
    ann = {r['key']: r for r in json.load(open(ANN, encoding='utf-8'))['rows']}
    zf = zipfile.ZipFile(ZIP)
    names = set(zf.namelist())
    rows = []
    for k in KEYS:
        r = ann[k]
        f = r['file']
        if f not in names:
            raise SystemExit(f'!! zip 에 {f} 없음 ({k})')
        zb = zf.read(f)
        p = os.path.join(CIFS, f)
        if not os.path.exists(p):
            os.makedirs(CIFS, exist_ok=True)
            open(p, 'wb').write(zb)                     # 저장소 밖 · 대조는 바로 아래
        if not os.path.exists(p) or md5(p) != md5b(zb):
            raise SystemExit(f'!! 풀린 {p} 가 없거나 zip 안 바이트와 md5 다름')
        a = read(p)
        if len(a) != r['NAtoms']:
            raise SystemExit(f'!! {f} 원자 수 {len(a)} ≠ core_pop_annotated NAtoms {r["NAtoms"]}')
        rows.append({'key': k, 'file': f, 'cif_md5': md5b(zb), 'n_atoms': len(a), 'cell_volume_A3': a.get_volume(),
                     'cellpar': [float(x) for x in a.cell.cellpar()], 'PLD_core': r['PLD'], 'LCD_core': r['LCD']})
    return rows, {'zip': os.path.basename(ZIP), 'zip_md5': md5(ZIP), 'zip_n_entries': len(names), 'keys_in_namelist': len(rows)}


def one_call(row, r):
    stem = row['file'][:-4]
    src = os.path.join(CIFS, row['file'])
    bd = os.path.join(BASE, stem, f'block{r:.2f}')
    if os.path.exists(bd):                      # 재시도: 지우고 처음부터(이어받기 없음 — CLAUDE.md §3)
        shutil.rmtree(bd)
    os.makedirs(bd)
    shutil.copy(src, bd)
    rc, sec, peak, stop, pre = run_guarded([ZEO, '-ha', '-block', f'{r:.2f}', str(NS), row['file']], bd, 'zeo_block.out')
    txt = open(os.path.join(bd, 'zeo_block.out'), errors='ignore').read()
    m = re.search(r'Identified (\d+) channels and (\d+) pockets', txt)
    an = re.search(r'Voronoi network with (\d+) nodes\. (\d+) of them are accessible', txt)
    bf = glob.glob(os.path.join(bd, '*.block'))
    nsph, rad = None, []
    ok = bool(rc == 0 and not stop and len(bf) == 1 and os.path.getsize(bf[0]) > 0)
    if ok:                                      # 빈 파일 · 가드 kill · rc≠0 은 구 0 이 아니라 None
        lines = [ln.split() for ln in open(bf[0]).read().strip().splitlines()]
        nsph = int(lines[0][0])
        rad = [float(ln[3]) for ln in lines[1:1 + nsph]]
        ok = len(rad) == nsph
    vsum = sum(4.0 / 3.0 * math.pi * x ** 3 for x in rad)
    return {'gas': GAS[r], 'channels': int(m.group(1)) if m else None, 'pockets': int(m.group(2)) if m else None,
            'nodes': int(an.group(1)) if an else None, 'accessible_nodes': int(an.group(2)) if an else None,
            'n_spheres': nsph, 'sphere_radii': [round(x, 3) for x in rad], 'sphere_volume_sum_A3': vsum,
            'sphere_volume_pct_of_cell': 100.0 * vsum / row['cell_volume_A3'],
            'block_file': os.path.relpath(bf[0], D) if bf else None, 'block_md5': md5(bf[0]) if bf else None,
            'n_block_files': len(bf), 'block_ok': ok, 'blockpockets_needed': (nsph > 0) if ok else None,
            'rc': rc, 'seconds': sec, 'peak_rss_MB': peak, 'stopped_by_guard': stop, 'pre_counts': pre}


def main():
    rows, zinfo = inputs()
    print(f"입력 대조 통과: zip {zinfo['zip_n_entries']}개 중 대상 {zinfo['keys_in_namelist']}/{len(KEYS)} · 묶음 {BATCHES} · 풀린 파일 md5 = zip 바이트 · "
          f"원자 수 = NAtoms ({min(r['n_atoms'] for r in rows)}~{max(r['n_atoms'] for r in rows)}) · 계획 {len(rows) * len(RADII)}건(-block · 병렬 {PAR})", flush=True)
    if DRY:
        for r in rows:
            print(f"  {r['key']:24s} {r['file']:30s} {r['cif_md5'][:8]} 원자 {r['n_atoms']:4d} 부피 {r['cell_volume_A3']:9.1f} Å³", flush=True)
        return 0
    c = counts()
    if c['simulate']:
        print(f'!! simulate 도는 중 {c} — Zeo++ 안 띄움(CLAUDE.md §5)', flush=True)
        return 1
    if os.path.exists(OUT) or any(os.path.exists(os.path.join(BASE, r['file'][:-4])) for r in rows):
        print(f'!! 결과 파일 또는 이 묶음 구조의 폴더가 이미 있음 — 중단', flush=True)
        return 1
    t_all = time.time()
    out = {'test': 'COREPOP-H323 준비 — CoRE 모집단 3D(CORE22 제외) Zeo++ 막음 파일(세 탐침)', 'assign': 'ASSIGN_COREPOP_HUMID323_20261114.md',
           'machine': MACHINE, 'batches': BATCHES, 'ported_from': 'core22_blocks_laptop.py (CORE22 막음) — 병렬 · 묶음만 바꿈',
           'started': time.strftime('%F %T'), 'zeo': ZEO, 'flags': '-ha', 'block_samples': NS, 'radii': list(RADII),
           'probe_gas': {f'{r:.2f}': g for r, g in GAS.items()}, 'input_cell': '단위셀 그대로(CIF · P 1) — 초격자 아님',
           'guard_MB': GUARD_MB, 'start_MB': START_MB, 'parallel': PAR, 'inputs': zinfo, 'rows': rows,
           'note': '기계적 사실뿐. 구 0 = 그 탐침에서 막을 주머니 없음(그 성분 막음 없음). n_spheres None = 실패(구 0 과 다름). 주머니 부피 = .block 구 부피 합(겹침 무시).'}
    lock = threading.Lock()

    def save(final=False):
        with lock:
            out['elapsed_s'] = round(time.time() - t_all)
            if final:
                out['finished'] = time.strftime('%F %T')
            tmp = OUT + '.tmp'
            json.dump(out, open(tmp, 'w', encoding='utf-8'), indent=2, ensure_ascii=False)
            os.replace(tmp, OUT)

    def task(row, r, tries):
        x = one_call(row, r)
        x['tries'] = tries
        row[f'r{r:.2f}'] = x
        save()
        print(f"  {row['key']:24s} r={r:.2f}({GAS[r]:5s}): {'ok' if x['block_ok'] else '실패'} · 통로 {x['channels']} · "
              f"주머니 {x['pockets']} · 구 {x['n_spheres']} · {x['seconds']} s · 최대 {x['peak_rss_MB']} MB{' · 멈춤!' if x['stopped_by_guard'] else ''}"
              f"{' · 재시도' if tries > 1 else ''}", flush=True)

    try:
        with ThreadPoolExecutor(max_workers=PAR) as ex:
            futs = [ex.submit(task, row, r, 1) for row in rows for r in RADII]
            for f in futs:
                f.result()
        redo = [(row, r) for row in rows for r in RADII if not row[f'r{r:.2f}']['block_ok']]
        if redo:
            print(f'  실패 {len(redo)}건 — 한 번에 하나로 한 번 더', flush=True)
        for row, r in redo:
            task(row, r, 2)
    except RuntimeError as e:
        out['aborted'] = str(e)
        save()
        print(f'!! {e}', flush=True)
        return 5
    out['summary'] = {r['key']: {f'spheres_{x:.2f}': r[f'r{x:.2f}']['n_spheres'] for x in RADII} for r in rows}
    out['all_blocks_ok'] = all(r[f'r{x:.2f}']['block_ok'] for r in rows for x in RADII)
    out['n_needing_blockpockets'] = {f'{x:.2f}': sum(bool(r[f'r{x:.2f}']['blockpockets_needed']) for r in rows) for x in RADII}
    save(final=True)
    print(f"저장 {OUT} ({out['elapsed_s']} s) · 전부 ok {out['all_blocks_ok']} · 막음 필요 구조 수 {out['n_needing_blockpockets']}", flush=True)
    return 0


if __name__ == '__main__':
    sys.exit(main())
