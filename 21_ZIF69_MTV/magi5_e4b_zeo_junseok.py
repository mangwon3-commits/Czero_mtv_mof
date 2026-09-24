# -*- coding: utf-8 -*-
"""MAGI-005 E-4b (a) 앞단 (Junseok) — Zeo++ `-ha -res` + `-ha -block r 50000` (r = 1.65 · 1.82) × e4zif{7,8,90}_relaxed.

`ASSIGN_MAGI5B_20260925.md` §Junseok 4차. 한 번에 한 건(동시 2건 상한 안) — ZIF-7 522원자라 E-2b ④(MAF-66 304원자 50,000 → 6.4 GB)보다 클 수 있음.
network 자신의 RSS 를 1 s 마다 재고 WSL MemAvailable < 5 GB 면 멈춘다. RASPA 가 돌면 시작하지 않는다(CLAUDE.md §5).
출력: magi5_e4b_runs/zeo/… 와 magi5_e4b_runs/zeo_summary.json (드라이버가 읽음).
"""
import glob
import json
import os
import re
import shutil
import subprocess
import sys
import time

D = '/home/mangwon/mof_project/21_ZIF69_MTV'
ZEO = '/home/mangwon/miniconda3/envs/czeromof/bin/network'
BASE = os.path.join(D, 'magi5_e4b_runs', 'zeo')
NS = 50000
RADII = (1.65, 1.82)
STRUCT = (7, 8, 90)
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


def main():
    if subprocess.run(['pgrep', '-xc', 'simulate'], capture_output=True, text=True).stdout.strip() not in ('', '0'):
        print('!! simulate 도는 중 — Zeo++ 안 띄움', flush=True)
        return 1
    if os.path.exists(BASE):
        print(f'!! {BASE} 이미 있음 — 중단', flush=True)
        return 1
    summary = {'samples': NS, 'guard_MB': GUARD_MB, 'rows': []}
    for s in STRUCT:
        tag = f'e4zif{s}'
        cif = os.path.join(D, 'relax_tnf', f'{tag}_relaxed.cif')
        sd = os.path.join(BASE, tag)
        os.makedirs(sd)
        shutil.copy(cif, sd)
        rc, sec, peak, stop = run_guarded([ZEO, '-ha', '-res', f'{tag}_relaxed.res', f'{tag}_relaxed.cif'], sd, 'zeo_res.out')
        try:
            raw = open(os.path.join(sd, f'{tag}_relaxed.res')).read().split()
            res = {'Di': float(raw[1]), 'Df': float(raw[2]), 'Dif': float(raw[3])}
        except (OSError, IndexError, ValueError):
            res = None
        print(f'  {tag} -res {res} ({sec} s, 최대 {peak} MB{", 멈춤" if stop else ""})', flush=True)
        for r in RADII:
            rd = os.path.join(sd, f'r{r:.2f}')
            os.makedirs(rd)
            shutil.copy(cif, rd)
            rc, sec, peak, stop = run_guarded([ZEO, '-ha', '-block', f'{r:.2f}', str(NS), f'{tag}_relaxed.cif'], rd, 'zeo_block.out')
            txt = open(os.path.join(rd, 'zeo_block.out'), errors='ignore').read()
            m = re.search(r'Identified (\d+) channels and (\d+) pockets', txt)
            a = re.search(r'Voronoi network with (\d+) nodes\. (\d+) of them are accessible', txt)
            bf = glob.glob(os.path.join(rd, '*.block'))
            nsph, radii_sph, cmax = None, [], None
            if bf and os.path.getsize(bf[0]) > 0:
                lines = [ln.split() for ln in open(bf[0]).read().strip().splitlines()]
                nsph = int(lines[0][0])
                sph = [[float(x) for x in ln[:4]] for ln in lines[1:1 + nsph]]
                radii_sph = [round(x[3], 3) for x in sph]
                cmax = max((abs(c) for x in sph for c in x[:3]), default=0.0)
            row = {'tag': tag, 'probe_radius_A': r, 'rc': rc, 'seconds': sec, 'peak_rss_MB': peak, 'stopped_by_guard': stop,
                   'channels': int(m.group(1)) if m else None, 'pockets': int(m.group(2)) if m else None,
                   'nodes': int(a.group(1)) if a else None, 'accessible_nodes': int(a.group(2)) if a else None,
                   'n_spheres': nsph, 'sphere_radii': radii_sph, 'coord_max': cmax,
                   'block_file': os.path.relpath(bf[0], D) if bf else None, 'res': res}
            summary['rows'].append(row)
            print(f'  {tag} r={r:.2f}: channels {row["channels"]} · pockets {row["pockets"]} · 접근 노드 {row["accessible_nodes"]}/{row["nodes"]} · '
                  f'구 {nsph} {radii_sph[:4]} · 좌표 최대 {cmax} · {sec} s · 최대 {peak} MB{" · 멈춤!" if stop else ""}', flush=True)
    json.dump(summary, open(os.path.join(D, 'magi5_e4b_runs', 'zeo_summary.json'), 'w', encoding='utf-8'), indent=2, ensure_ascii=False)
    print('  저장 magi5_e4b_runs/zeo_summary.json', flush=True)
    return 0


if __name__ == '__main__':
    sys.exit(main())
