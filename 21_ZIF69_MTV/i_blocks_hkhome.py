# -*- coding: utf-8 -*-
"""CORE22 §I 준비 (HKHOME) — `2021[Zn][srs]3[FSR]1` **우리 앞단판**(E-22e 이완 + PACMAN)의 Zeo++ 막음 파일, 세 탐침(CO₂ 1.65 · N₂ 1.82 · 물 1.30 Å).
등록 `SYNTH_20261111.md` §8 · `ASSIGN_CORE22_HUMID_PLAN_20261108.md` 11-11 갱신(새 항목 I · 자료 0건) · `COMMS/cloud.md` 11-11 10:5x ①.
`core22_blocks_laptop.py`(c7c8ca40 · 랩탑 · CoRE 22종의 막음 파일을 만든 호출) 사본 — 바꾼 것:
  · 입력: `charged_v3/e22e_2021_Zn__srs_3_FSR_1_DDEC6.cif` 하나(md5 bf0f3c9a 대조 · 256원자 · CoRE 셀의 2×1×1). zip · core_pop_annotated 대조는 없음(대상이 zip 밖).
  · 폴더: `i_zeo_runs/<CIF 줄기>/block<r>/` · 출력 `results_i_blocks_hkhome.json`(행 모양은 원판과 같음 — G · C · H 계열 실행기가 같은 식으로 읽음).
    저장소에 올리는 것은 `.block` 과 결과 JSON 뿐(원판과 같은 관례).
측정 · 파싱 · 가드는 원판 그대로: `network -ha -block r 50000 <cif>` · 한 번에 한 건 · **호출마다 직전에** simulate · network 수를 봄
  (하나라도 있으면 그 자리에서 멈춤 · CLAUDE.md §5) · MemAvailable < ZEO_GUARD_MB(기본 5,000) 이면 kill ·
  가드에 걸렸거나 rc ≠ 0 이거나 .block 이 비면 n_spheres = None · block_ok = False(**구 0 과 구별**).
구 0 = 그 탐침에서 닿지 않는 주머니가 없음 → 그 성분은 막음 없음.
기계적 사실뿐 — 판정은 종합자.
사용: python i_blocks_hkhome.py      (I_ZEO_DRY=1 이면 입력 대조 · 계획만, Zeo++ · 폴더 생성 없음)
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
import time

from ase.io import read

D = os.path.dirname(os.path.abspath(__file__))
HOME = os.path.expanduser('~')
ZEO = os.path.join(HOME, 'miniconda3/envs/czeromof/bin/network')
KEY = 'e22e_2021_Zn__srs_3_FSR_1'                     # 우리 앞단판의 이름(전하 CIF 줄기)
CORE_KEY = '2021[Zn][srs]3[FSR]1'
SRC = os.path.join(D, 'charged_v3', f'{KEY}_DDEC6.cif')
SRC_MD5 = 'bf0f3c9aa1f8e30a4bac001d02bbc732'
BASE = os.path.join(D, 'i_zeo_runs')
OUT = os.path.join(D, 'results_i_blocks_hkhome.json')
NS = 50000
RADII = (1.65, 1.82, 1.30)
GAS = {1.65: 'CO2', 1.82: 'N2', 1.30: 'water'}
GUARD_MB = int(os.environ.get('ZEO_GUARD_MB', '5000'))
DRY = bool(os.environ.get('I_ZEO_DRY'))


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
    c = counts()
    if c['simulate'] or c['network']:
        raise RuntimeError(f'Zeo++ 직전 검사: {c} — 멈춤(CLAUDE.md §5)')
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
    return p.returncode, round(time.time() - t0, 1), peak, stopped, c


def md5(p):
    return hashlib.md5(open(p, 'rb').read()).hexdigest()


def inputs():
    """원본 전하 CIF md5 대조. 어긋나면 SystemExit."""
    if not os.path.exists(SRC) or md5(SRC) != SRC_MD5:
        raise SystemExit(f'!! {SRC} 가 없거나 md5 ≠ {SRC_MD5[:8]}')
    a = read(SRC)
    f = os.path.basename(SRC)
    return [{'key': KEY, 'core_key': CORE_KEY, 'file': f, 'cif_md5': SRC_MD5, 'n_atoms': len(a), 'cell_volume_A3': a.get_volume(),
             'cellpar': [float(x) for x in a.cell.cellpar()]}]


def main():
    rows = inputs()
    print(f"입력 대조 통과: {rows[0]['file']} md5 {SRC_MD5[:8]} · 원자 {rows[0]['n_atoms']} · 부피 {rows[0]['cell_volume_A3']:.1f} Å³ · "
          f"계획 {len(rows) * len(RADII)}건(-block · 한 번에 하나)", flush=True)
    if DRY:
        return 0
    c = counts()
    if c['simulate'] or c['network']:
        print(f'!! simulate 또는 network 도는 중 {c} — Zeo++ 안 띄움(CLAUDE.md §5)', flush=True)
        return 1
    if os.path.exists(BASE) or os.path.exists(OUT):
        print(f'!! {BASE} 또는 결과 파일 이미 있음 — 중단', flush=True)
        return 1
    t_all = time.time()
    out = {'test': 'CORE22 §I 준비 — 2021[Zn][srs]3[FSR]1 우리 앞단판(E-22e 이완 + PACMAN) Zeo++ 막음 파일(세 탐침)',
           'assign': 'SYNTH_20261111.md §8 · ASSIGN_CORE22_HUMID_PLAN_20261108.md 11-11 갱신(항목 I)',
           'machine': 'hkhome', 'ported_from': 'core22_blocks_laptop.py (c7c8ca40 · 랩탑) ← znbdt_a_zeo.py (883348e7 · HKHOME)', 'started': time.strftime('%F %T'),
           'zeo': ZEO, 'flags': '-ha', 'block_samples': NS, 'radii': list(RADII), 'probe_gas': {f'{r:.2f}': g for r, g in GAS.items()},
           'input_cell': '전하 CIF 그대로(P 1 · CoRE 셀의 2×1×1) — 초격자 아님', 'guard_MB': GUARD_MB,
           'inputs': {'source': os.path.relpath(SRC, D), 'source_md5': SRC_MD5}, 'rows': rows,
           'note': '기계적 사실뿐. 구 0 = 그 탐침에서 막을 주머니 없음(그 성분 막음 없음). n_spheres None = 실패(구 0 과 다름). 주머니 부피 = .block 구 부피 합(겹침 무시).'}

    def save(final=False):
        out['elapsed_s'] = round(time.time() - t_all)
        if final:
            out['finished'] = time.strftime('%F %T')
        tmp = OUT + '.tmp'
        json.dump(out, open(tmp, 'w', encoding='utf-8'), indent=2, ensure_ascii=False)
        os.replace(tmp, OUT)

    try:
        for row in rows:
            for r in RADII:
                bd = os.path.join(BASE, KEY, f'block{r:.2f}')
                os.makedirs(bd)
                shutil.copy(SRC, bd)
                rc, sec, peak, stop, pre = run_guarded([ZEO, '-ha', '-block', f'{r:.2f}', str(NS), row['file']], bd, 'zeo_block.out')
                txt = open(os.path.join(bd, 'zeo_block.out'), errors='ignore').read()
                m = re.search(r'Identified (\d+) channels and (\d+) pockets', txt)
                an = re.search(r'Voronoi network with (\d+) nodes\. (\d+) of them are accessible', txt)
                bf = glob.glob(os.path.join(bd, '*.block'))
                nsph, rad = None, []
                ok = bool(rc == 0 and not stop and len(bf) == 1 and os.path.getsize(bf[0]) > 0)
                if ok:                                  # 빈 파일 · 가드 kill · rc≠0 은 구 0 이 아니라 None
                    lines = [ln.split() for ln in open(bf[0]).read().strip().splitlines()]
                    nsph = int(lines[0][0])
                    rad = [float(ln[3]) for ln in lines[1:1 + nsph]]
                    ok = len(rad) == nsph
                vsum = sum(4.0 / 3.0 * math.pi * x ** 3 for x in rad)
                row[f'r{r:.2f}'] = {'gas': GAS[r], 'channels': int(m.group(1)) if m else None, 'pockets': int(m.group(2)) if m else None,
                                    'nodes': int(an.group(1)) if an else None, 'accessible_nodes': int(an.group(2)) if an else None,
                                    'n_spheres': nsph, 'sphere_radii': [round(x, 3) for x in rad], 'sphere_volume_sum_A3': vsum,
                                    'sphere_volume_pct_of_cell': 100.0 * vsum / row['cell_volume_A3'],
                                    'block_file': os.path.relpath(bf[0], D) if bf else None, 'block_md5': md5(bf[0]) if bf else None,
                                    'n_block_files': len(bf), 'block_ok': ok, 'blockpockets_needed': (nsph > 0) if ok else None,
                                    'rc': rc, 'seconds': sec, 'peak_rss_MB': peak, 'stopped_by_guard': stop, 'pre_counts': pre}
                save()
                print(f"  {row['key']:28s} r={r:.2f}({GAS[r]:5s}): {'ok' if ok else '실패'} · 통로 {row[f'r{r:.2f}']['channels']} · "
                      f"주머니 {row[f'r{r:.2f}']['pockets']} · 구 {nsph} · {sec} s · 최대 {peak} MB{' · 멈춤!' if stop else ''}", flush=True)
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
