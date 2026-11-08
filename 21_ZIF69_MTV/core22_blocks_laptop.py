# -*- coding: utf-8 -*-
"""6SEED_CORE §C 준비 (랩탑 · 예비 배정 17:5x) — CoRE 3차원 22종의 Zeo++ 막음 파일, 세 탐침(CO₂ 1.65 · N₂ 1.82 · 물 1.30 Å).
등록 `ASSIGN_ZNBDT_6SEED_CORE_20261108.md` §C 준비 · §예비 배정(HKHOME 착수 글이 11-08 19:00 까지 없으면 랩탑이 A 뒤 · B 앞 RASPA 0 창에).
`znbdt_a_zeo.py`(883348e7 · HKHOME, `e24g_zeo_desktop.py` 이식 — E-24g · E-24i 막음 파일을 만든 호출) 사본 — 바꾼 것:
  · 입력: `core_pop_cifs.zip` 안의 22 CIF(§AV 와 같은 파일 · CoRE 기하 · CoRE 전하 · 전부 P 1) — 저장소 밖 `~/.mof_chain/core22_1108/cifs/` 에
    풀어 둔 것. 시작할 때 zip 을 다시 읽어 **namelist 에 22개가 있는지 · 풀린 파일 md5 = zip 안 바이트 md5** 를 대조합니다
    (CLAUDE.md §0 09-23: 풀어 둔 폴더는 판본이 있음).
  · 탐침: 1.65 · 1.82 · 1.30 셋 · `-block` 만(등록 §C 준비). `-chan` · `-res` 는 안 함. 단위셀 그대로(초격자 아님).
  · 폴더: `core22_zeo_runs/<파일 이름>/block<r>/` · 출력 `results_core22_blocks_laptop.json`. 저장소에 올리는 것은 `.block` 과 결과 JSON 뿐
    (`e24i_zeo_runs/` 와 같은 관례 — CIF 사본 · zeo_block.out 은 올리지 않음).
측정 · 파싱 · 가드는 원판 그대로: `network -ha -block r 50000 <cif>` · 한 번에 한 건 · **호출마다 직전에** simulate · network 수를 봄
  (하나라도 있으면 그 자리에서 멈춤 · CLAUDE.md §5) · MemAvailable < ZEO_GUARD_MB(기본 5,000) 이면 kill ·
  가드에 걸렸거나 rc ≠ 0 이거나 .block 이 비면 n_spheres = None · block_ok = False(**구 0 과 구별** — 원판 1차 시도의 결함 수정분 그대로).
구 0 = 그 탐침에서 닿지 않는 주머니가 없음 → 그 성분은 막음 없음(등록 §C 준비).
기계적 사실뿐 — 판정은 종합자.
사용: python core22_blocks_laptop.py      (CORE22_ZEO_DRY=1 이면 입력 대조 · 계획만, Zeo++ · 폴더 생성 없음)
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
import zipfile

from ase.io import read

D = os.path.dirname(os.path.abspath(__file__))
HOME = os.path.expanduser('~')
ZEO = os.path.join(HOME, 'miniconda3/envs/czeromof/bin/network')
CIFS = os.path.join(HOME, '.mof_chain/core22_1108/cifs')
ZIP = os.path.join(D, 'core_pop_cifs.zip')
ANN = os.path.join(D, 'core_pop_annotated.json')
BASE = os.path.join(D, 'core22_zeo_runs')
OUT = os.path.join(D, 'results_core22_blocks_laptop.json')
NS = 50000
RADII = (1.65, 1.82, 1.30)
GAS = {1.65: 'CO2', 1.82: 'N2', 1.30: 'water'}
GUARD_MB = int(os.environ.get('ZEO_GUARD_MB', '5000'))
DRY = bool(os.environ.get('CORE22_ZEO_DRY'))
KEYS = ('2021[Zn][srs]3[FSR]1', '2017[Zn][dia]3[ASR]1', '2017[Zn][dia]3[FSR]1', '2024[Cu][srs]3[FSR]2', '2024[Co][pcu]3[ASR]1',
        '2024[Co][pcu]3[FSR]1', '2024[Zn][ths]3[ASR]1', '2024[Zn][ths]3[FSR]1', '2014[Cu][dia]3[FSR]6', '2014[Cu][dia]3[FSR]2',
        '2014[Cu][dia]3[ASR]5', '2014[Cu][dia]3[ASR]1', '2018[Cd][dia]3[FSR]5', '2018[Cd][dia]3[ASR]6', '2019[Ni][pcu]3[ASR]1',
        '2018[Cd][dia]3[ASR]5', '2018[Cd][dia]3[FSR]3', '2018[Cd][dia]3[ASR]4', '2018[Cd][dia]3[FSR]4', '2021[Co][dia]3[ASR]1',
        '2021[Co][dia]3[FSR]1', '2019[Zn][pcu]3[ASR]1')          # 등록 §C 대상 22 · 순서 그대로


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
        if not os.path.exists(p) or md5(p) != md5b(zb):
            raise SystemExit(f'!! 풀린 {p} 가 없거나 zip 안 바이트와 md5 다름')
        a = read(p)
        if len(a) != r['NAtoms']:
            raise SystemExit(f'!! {f} 원자 수 {len(a)} ≠ core_pop_annotated NAtoms {r["NAtoms"]}')
        rows.append({'key': k, 'file': f, 'cif_md5': md5b(zb), 'n_atoms': len(a), 'cell_volume_A3': a.get_volume(),
                     'cellpar': [float(x) for x in a.cell.cellpar()], 'PLD_core': r['PLD'], 'LCD_core': r['LCD']})
    return rows, {'zip': os.path.basename(ZIP), 'zip_md5': md5(ZIP), 'zip_n_entries': len(names), 'keys_in_namelist': len(rows)}


def main():
    rows, zinfo = inputs()
    print(f"입력 대조 통과: zip {zinfo['zip_n_entries']}개 중 대상 {zinfo['keys_in_namelist']}/22 · 풀린 파일 md5 = zip 바이트 · 원자 수 = NAtoms "
          f"({min(r['n_atoms'] for r in rows)}~{max(r['n_atoms'] for r in rows)}) · 계획 {len(rows) * len(RADII)}건(-block · 한 번에 하나)", flush=True)
    if DRY:
        for r in rows:
            print(f"  {r['key']:24s} {r['file']:30s} {r['cif_md5'][:8]} 원자 {r['n_atoms']:4d} 부피 {r['cell_volume_A3']:9.1f} Å³", flush=True)
        return 0
    c = counts()
    if c['simulate'] or c['network']:
        print(f'!! simulate 또는 network 도는 중 {c} — Zeo++ 안 띄움(CLAUDE.md §5)', flush=True)
        return 1
    if os.path.exists(BASE) or os.path.exists(OUT):
        print(f'!! {BASE} 또는 결과 파일 이미 있음 — 중단', flush=True)
        return 1
    t_all = time.time()
    out = {'test': '6SEED_CORE §C 준비 — CoRE 3차원 22종 Zeo++ 막음 파일(세 탐침)', 'assign': 'ASSIGN_ZNBDT_6SEED_CORE_20261108.md §C 준비 · §예비 배정',
           'machine': 'laptop', 'ported_from': 'znbdt_a_zeo.py (883348e7 · HKHOME) ← e24g_zeo_desktop.py (E-24g/E-24i)', 'started': time.strftime('%F %T'),
           'zeo': ZEO, 'flags': '-ha', 'block_samples': NS, 'radii': list(RADII), 'probe_gas': {f'{r:.2f}': g for r, g in GAS.items()},
           'input_cell': '단위셀 그대로(CIF · P 1) — 초격자 아님', 'guard_MB': GUARD_MB, 'inputs': zinfo, 'rows': rows,
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
            stem = row['file'][:-4]
            src = os.path.join(CIFS, row['file'])
            for r in RADII:
                bd = os.path.join(BASE, stem, f'block{r:.2f}')
                os.makedirs(bd)
                shutil.copy(src, bd)
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
                print(f"  {row['key']:24s} r={r:.2f}({GAS[r]:5s}): {'ok' if ok else '실패'} · 통로 {row[f'r{r:.2f}']['channels']} · "
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
