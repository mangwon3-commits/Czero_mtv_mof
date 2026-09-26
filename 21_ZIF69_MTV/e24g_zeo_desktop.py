# -*- coding: utf-8 -*-
"""MAGI-005 E-24g · E-24h (데스크탑) — 새 치환체의 접근성: Zeo++ `-ha -res` · `-ha -chan r` · `-ha -block r 50000`.
Junseok `magi5_e24b_zeo_junseok.py`(255cf19e, E-24b ① · E-24c ① 에 쓴 것)의 **데스크탑 이식** — 바꾼 것: 경로 · 대상(`--names`) · 출력 이름 ·
탐침에 1.30(물, 서술 · 막음 물 대비 — 등록 (2a))을 더함 · 끝의 E-24b 전용 요약을 대상 무관한 요약으로. 측정 · 파싱 · 메모리 가드는 그대로.
등록 `ASSIGN_MAGI5B_20260925.md` §HKHOME 21차. RASPA 가 돌면 시작하지 않는다(CLAUDE.md §5). 한 번에 한 건.
출력 results_e24g_access_hkhome.json · 실행 폴더 e24g_zeo_runs/. 기계적 사실뿐 — 판정은 판정문에서.
"""
import glob
import json
import math
import os
import re
import shutil
import subprocess
import sys
import time

from ase.io import read

D = '/home/mangwon1/mof_project/21_ZIF69_MTV'
ZEO = '/home/mangwon1/miniconda3/envs/czeromof/bin/network'
BASE = os.path.join(D, 'e24g_zeo_runs')
OUT = os.path.join(D, 'results_e24g_access_hkhome.json')
NS = 50000
RADII = (1.65, 1.82, 1.30)
NAMES = tuple(sys.argv[1].split(',')) if len(sys.argv) > 1 else ()
PLD_MIN = 3.64
GUARD_MB = 5000


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


def run_guarded(args, cwd, out):
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
    return p.returncode, round(time.time() - t0, 1), peak, stopped


def busy():
    n = lambda x: subprocess.run(['pgrep', '-xc', x], capture_output=True, text=True).stdout.strip()
    return n('simulate') not in ('', '0') or n('network') not in ('', '0')


def main():
    if not NAMES:
        print('사용: e24g_zeo_desktop.py tag1,tag2,...', flush=True)
        return 1
    if busy():
        print('!! simulate 또는 network 도는 중 — Zeo++ 안 띄움(CLAUDE.md §5)', flush=True)
        return 1
    if os.path.exists(BASE) or os.path.exists(OUT):
        print(f'!! {BASE} 또는 결과 파일 이미 있음 — 중단', flush=True)
        return 1
    t_all = time.time()
    rows = []
    for tag in NAMES:
        cif = os.path.join(D, 'relax_tnf', f'{tag}_relaxed.cif')
        sd = os.path.join(BASE, tag)
        os.makedirs(sd)
        shutil.copy(cif, sd)
        a = read(cif)
        vol = a.get_volume()
        row = {'tag': tag, 'cif': os.path.relpath(cif, D), 'n_atoms': len(a), 'cell_volume_A3': vol, 'runs': []}
        rc, sec, peak, stop = run_guarded([ZEO, '-ha', '-res', f'{tag}.res', f'{tag}_relaxed.cif'], sd, 'zeo_res.out')
        try:
            raw = open(os.path.join(sd, f'{tag}.res')).read().split()
            row.update(LCD_Di=float(raw[1]), PLD_Df=float(raw[2]), Dif=float(raw[3]))
        except (OSError, IndexError, ValueError):
            row.update(LCD_Di=None, PLD_Df=None, Dif=None)
        row['runs'].append({'cmd': '-ha -res', 'rc': rc, 'seconds': sec, 'peak_rss_MB': peak, 'stopped_by_guard': stop})
        print(f"  {tag} ({len(a)} 원자) -res LCD {row['LCD_Di']} · PLD {row['PLD_Df']} · Dif {row['Dif']} ({sec} s, 최대 {peak} MB{', 멈춤' if stop else ''})", flush=True)
        for r in RADII:
            # -chan: 통로 수 · 차원
            cd = os.path.join(sd, f'chan{r:.2f}')
            os.makedirs(cd)
            shutil.copy(cif, cd)
            rc, sec, peak, stop = run_guarded([ZEO, '-ha', '-chan', f'{r:.2f}', f'{tag}.chan', f'{tag}_relaxed.cif'], cd, 'zeo_chan.out')
            ctxt = open(os.path.join(cd, f'{tag}.chan'), errors='ignore').read() if os.path.exists(os.path.join(cd, f'{tag}.chan')) else ''
            otxt = open(os.path.join(cd, 'zeo_chan.out'), errors='ignore').read()
            mc = re.search(r'(\d+)\s+channels identified of dimensionality\s*([\d\s]*)', ctxt)
            mo = re.search(r'Identified (\d+) channels and (\d+) pockets', otxt)
            chan = {'n_channels_chanfile': int(mc.group(1)) if mc else None,
                    'dimensionality': [int(x) for x in mc.group(2).split()] if mc and mc.group(2).strip() else [],
                    'channels_stdout': int(mo.group(1)) if mo else None, 'pockets_stdout': int(mo.group(2)) if mo else None,
                    'chan_file_head': ctxt.strip().splitlines()[:3], 'rc': rc, 'seconds': sec, 'peak_rss_MB': peak, 'stopped_by_guard': stop}
            # -block: 닿지 않는 주머니 수 · 막음 구
            bd = os.path.join(sd, f'block{r:.2f}')
            os.makedirs(bd)
            shutil.copy(cif, bd)
            rc, sec, peak, stop = run_guarded([ZEO, '-ha', '-block', f'{r:.2f}', str(NS), f'{tag}_relaxed.cif'], bd, 'zeo_block.out')
            txt = open(os.path.join(bd, 'zeo_block.out'), errors='ignore').read()
            m = re.search(r'Identified (\d+) channels and (\d+) pockets', txt)
            an = re.search(r'Voronoi network with (\d+) nodes\. (\d+) of them are accessible', txt)
            bf = glob.glob(os.path.join(bd, '*.block'))
            nsph, rad = None, []
            if bf and os.path.getsize(bf[0]) > 0:
                lines = [ln.split() for ln in open(bf[0]).read().strip().splitlines()]
                nsph = int(lines[0][0])
                rad = [float(ln[3]) for ln in lines[1:1 + nsph]]
            elif bf:
                nsph = 0
            vsum = sum(4.0 / 3.0 * math.pi * x ** 3 for x in rad)
            block = {'channels': int(m.group(1)) if m else None, 'pockets': int(m.group(2)) if m else None,
                     'nodes': int(an.group(1)) if an else None, 'accessible_nodes': int(an.group(2)) if an else None,
                     'n_spheres': nsph, 'sphere_radii': [round(x, 3) for x in rad], 'sphere_volume_sum_A3': vsum,
                     'sphere_volume_pct_of_cell': 100.0 * vsum / vol, 'block_file': os.path.relpath(bf[0], D) if bf else None,
                     'rc': rc, 'seconds': sec, 'peak_rss_MB': peak, 'stopped_by_guard': stop}
            row[f'r{r:.2f}'] = {'chan': chan, 'block': block}
            print(f"  {tag} r={r:.2f}: -chan {chan['n_channels_chanfile']} 통로 · 차원 {chan['dimensionality']} (stdout 통로 {chan['channels_stdout']} · 주머니 {chan['pockets_stdout']}) | "
                  f"-block 통로 {block['channels']} · 주머니 {block['pockets']} · 구 {nsph} · 구 부피 {vsum:.1f} Å³({block['sphere_volume_pct_of_cell']:.2f} %) · "
                  f"{block['seconds']} s · 최대 {peak} MB{' · 멈춤!' if stop else ''}", flush=True)
        rows.append(row)
    by = {r['tag']: r for r in rows}

    def pockets(tag, r):
        return by[tag][f'r{r:.2f}']['block']['pockets']

    reg = {t: {'PLD': by[t]['PLD_Df'], 'LCD': by[t]['LCD_Di'], 'PLD_lt_3.64': by[t]['PLD_Df'] is not None and by[t]['PLD_Df'] < PLD_MIN,
               **{f'channels_{r:.2f}': by[t][f'r{r:.2f}']['chan']['n_channels_chanfile'] for r in RADII},
               **{f'pockets_{r:.2f}': pockets(t, r) for r in RADII},
               **{f'spheres_{r:.2f}': by[t][f'r{r:.2f}']['block']['n_spheres'] for r in RADII}} for t in by}
    out = {'test': 'MAGI-005 E-24g · E-24h — 새 치환체 접근성(Zeo++)', 'assign': 'ASSIGN_MAGI5B_20260925.md §HKHOME 21차', 'machine': 'hkhome',
           'ported_from': 'junseok magi5_e24b_zeo_junseok.py (255cf19e)',
           'made': time.strftime('%F %T'), 'zeo': ZEO, 'flags': '-ha', 'block_samples': NS, 'radii': list(RADII), 'PLD_threshold': PLD_MIN,
           'guard_MB': GUARD_MB, 'rows': rows, 'summary': reg, 'elapsed_s': round(time.time() - t_all),
           'note': '기계적 사실뿐. 주머니 부피 = .block 구 부피 합(겹침 무시). PLD = Df · LCD = Di (-res). 1.30 은 물 탐침(서술).'}
    tmp = OUT + '.tmp'
    json.dump(out, open(tmp, 'w', encoding='utf-8'), indent=2, ensure_ascii=False)
    os.replace(tmp, OUT)
    print(f"저장 {OUT} ({out['elapsed_s']} s)", flush=True)
    for t, v in reg.items():
        print(f"  {t} {json.dumps(v, ensure_ascii=False)}", flush=True)
    return 0


if __name__ == '__main__':
    sys.exit(main())
