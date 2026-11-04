# -*- coding: utf-8 -*-
"""ZnBDT 보강 A — 격자를 움직인 구조(UFF4MOF 상한 300 이완본)의 막음 파일. 등록 `ASSIGN_ZNBDT_SUPP_20261103.md` §A.
`e24g_zeo_desktop.py`(E-24g · E-24i 막음 파일을 만든 Zeo++ 호출의 데스크탑 이식) 사본 — 바꾼 것:
  · 입력: `uff300_e24i/<tag>_after.cif`(2×2×3 초격자 = 12셀, UFF4MOF 상한 300 이완본). 기존 `e24i_zeo_runs/` 의 막음 파일은
    **격자 고정 구조용**이라 쓰지 않음(ASSIGN §A).
  · 탐침: 1.65(CO₂) · 1.82(N₂) 둘만(E-27b · E-24e 와 같은 자). `-res` 는 안 함(relax300 결과에 PLD · LCD 있음).
  · 폴더: `znbdt_a_zeo_runs/<tag>/{chan,block}<r>/` · 출력 `results_znbdt_a_access_hkhome.json`.
  · **Zeo++ 호출마다 직전에** simulate · network 수를 봄 — 하나라도 있으면 그 자리에서 멈춤(CLAUDE.md §5, 이 배정의 지시).
측정 · 파싱은 원판 그대로: `network -ha -chan r` · `network -ha -block r 50000`. 한 번에 한 건.
[2026-11-04 12:51 1차 시도 기록] 모체 1.65 `-block` 이 921 s · 최대 RSS 13,620 MB 에서 가드(MemAvailable < 5,000 MB)에 걸려 kill —
  빈 .block(0 바이트)을 원판 파서가 **구 0** 으로 읽었음(원판 e24g_zeo_desktop.py 의 `elif bf: nsph = 0` — 실패가 결과처럼 보임).
  고친 것: ① 가드에 걸렸거나 rc ≠ 0 이거나 .block 이 비면 n_spheres = None · block_ok = False(구 0 과 구별) ·
  ② 가드 문턱을 환경변수 ZEO_GUARD_MB 로(기본 5,000 그대로; 2차는 RASPA 0 · 다른 계산 0 에서 1,500 으로 — 스왑 8 GB 별도) ·
  ③ -chan 을 먼저 전부(싸다), 그다음 -block 을 한 건씩. 1차 산출은 저장소 밖 ~/.claude_work/znbdt_a_zeo_attempt1/ 로 옮김.
기계적 사실뿐 — 판정은 종합자.
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

D = '/home/mangwon1/mof_project/21_ZIF69_MTV'
ZEO = '/home/mangwon1/miniconda3/envs/czeromof/bin/network'
BASE = os.path.join(D, 'znbdt_a_zeo_runs')
OUT = os.path.join(D, 'results_znbdt_a_access_hkhome.json')
NS = 50000
RADII = (1.65, 1.82)
TAGS = ('e22_parent', 'e24i_cn_open', 'e24i_br_open')
GUARD_MB = int(os.environ.get('ZEO_GUARD_MB', '5000'))


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


def main():
    c = counts()
    if c['simulate'] or c['network']:
        print(f'!! simulate 또는 network 도는 중 {c} — Zeo++ 안 띄움(CLAUDE.md §5)', flush=True)
        return 1
    if os.path.exists(BASE) or os.path.exists(OUT):
        print(f'!! {BASE} 또는 결과 파일 이미 있음 — 중단', flush=True)
        return 1
    t_all = time.time()
    rows = []
    out = {'test': 'ZnBDT 보강 A — UFF4MOF 상한 300 이완본 막음 파일(Zeo++)', 'assign': 'ASSIGN_ZNBDT_SUPP_20261103.md §A', 'machine': 'hkhome',
           'ported_from': 'e24g_zeo_desktop.py (E-24g/E-24i 데스크탑 이식)', 'started': time.strftime('%F %T'), 'zeo': ZEO, 'flags': '-ha',
           'block_samples': NS, 'radii': list(RADII), 'guard_MB': GUARD_MB, 'rows': rows,
           'note': '기계적 사실뿐. 입력은 2×2×3 초격자(12셀) — 구 · 통로 · 주머니 수는 초격자 기준. 주머니 부피 = .block 구 부피 합(겹침 무시).'}

    def save(final=False):
        out['elapsed_s'] = round(time.time() - t_all)
        if final:
            out['finished'] = time.strftime('%F %T')
        tmp = OUT + '.tmp'
        json.dump(out, open(tmp, 'w', encoding='utf-8'), indent=2, ensure_ascii=False)
        os.replace(tmp, OUT)

    out['attempt1'] = {'when': '2026-11-04 12:36~12:51', 'what': 'e22_parent r=1.65 -block · guard 5000 MB · 921.2 s · peak RSS 13620 MB · rc -9(가드 kill) · .block 0 바이트',
                       'moved_to': '~/.claude_work/znbdt_a_zeo_attempt1/ (저장소 밖)'}
    try:
        info = {}
        for tag in TAGS:
            cif = os.path.join(D, 'uff300_e24i', f'{tag}_after.cif')
            sd = os.path.join(BASE, tag)
            os.makedirs(sd)
            a = read(cif)
            row = {'tag': tag, 'cif': os.path.relpath(cif, D), 'cif_md5': md5(cif), 'n_atoms': len(a), 'cell_volume_A3': a.get_volume(),
                   'cellpar': [float(x) for x in a.cell.cellpar()], 'runs': []}
            rows.append(row)
            info[tag] = (cif, os.path.basename(cif), sd, a.get_volume(), row)
        for tag in TAGS:                                            # ① -chan 전부(싸다)
            cif, base, sd, vol, row = info[tag]
            for r in RADII:
                cd = os.path.join(sd, f'chan{r:.2f}')
                os.makedirs(cd)
                shutil.copy(cif, cd)
                rc, sec, peak, stop, pre = run_guarded([ZEO, '-ha', '-chan', f'{r:.2f}', f'{tag}.chan', base], cd, 'zeo_chan.out')
                cf = os.path.join(cd, f'{tag}.chan')
                ctxt = open(cf, errors='ignore').read() if os.path.exists(cf) else ''
                otxt = open(os.path.join(cd, 'zeo_chan.out'), errors='ignore').read()
                mc = re.search(r'(\d+)\s+channels identified of dimensionality\s*([\d\s]*)', ctxt)
                mo = re.search(r'Identified (\d+) channels and (\d+) pockets', otxt)
                chan = {'n_channels_chanfile': int(mc.group(1)) if mc else None,
                        'dimensionality': [int(x) for x in mc.group(2).split()] if mc and mc.group(2).strip() else [],
                        'channels_stdout': int(mo.group(1)) if mo else None, 'pockets_stdout': int(mo.group(2)) if mo else None,
                        'chan_file_head': ctxt.strip().splitlines()[:3], 'rc': rc, 'seconds': sec, 'peak_rss_MB': peak,
                        'stopped_by_guard': stop, 'pre_counts': pre}
                row[f'r{r:.2f}'] = {'chan': chan}
                save()
                print(f"  {tag} r={r:.2f}: -chan {chan['n_channels_chanfile']} 통로 · 차원 {chan['dimensionality']} "
                      f"(stdout 통로 {chan['channels_stdout']} · 주머니 {chan['pockets_stdout']}) · {sec} s · 최대 {peak} MB{' · 멈춤!' if stop else ''}", flush=True)
        for tag in TAGS:                                            # ② -block 한 건씩
            cif, base, sd, vol, row = info[tag]
            for r in RADII:
                bd = os.path.join(sd, f'block{r:.2f}')
                os.makedirs(bd)
                shutil.copy(cif, bd)
                rc, sec, peak, stop, pre = run_guarded([ZEO, '-ha', '-block', f'{r:.2f}', str(NS), base], bd, 'zeo_block.out')
                txt = open(os.path.join(bd, 'zeo_block.out'), errors='ignore').read()
                m = re.search(r'Identified (\d+) channels and (\d+) pockets', txt)
                an = re.search(r'Voronoi network with (\d+) nodes\. (\d+) of them are accessible', txt)
                bf = glob.glob(os.path.join(bd, '*.block'))
                nsph, rad = None, []
                ok = bool(rc == 0 and not stop and len(bf) == 1 and os.path.getsize(bf[0]) > 0)
                if ok:                                  # 빈 파일 · 가드 kill · rc≠0 은 구 0 이 아니라 None(1차 시도의 결함)
                    lines = [ln.split() for ln in open(bf[0]).read().strip().splitlines()]
                    nsph = int(lines[0][0])
                    rad = [float(ln[3]) for ln in lines[1:1 + nsph]]
                    ok = len(rad) == nsph
                vsum = sum(4.0 / 3.0 * math.pi * x ** 3 for x in rad)
                block = {'channels': int(m.group(1)) if m else None, 'pockets': int(m.group(2)) if m else None,
                         'nodes': int(an.group(1)) if an else None, 'accessible_nodes': int(an.group(2)) if an else None,
                         'n_spheres': nsph, 'sphere_radii': [round(x, 3) for x in rad], 'sphere_volume_sum_A3': vsum,
                         'sphere_volume_pct_of_cell': 100.0 * vsum / vol, 'block_file': os.path.relpath(bf[0], D) if bf else None,
                         'block_md5': md5(bf[0]) if bf else None, 'n_block_files': len(bf), 'block_ok': ok,
                         'rc': rc, 'seconds': sec, 'peak_rss_MB': peak, 'stopped_by_guard': stop, 'pre_counts': pre}
                row[f'r{r:.2f}']['block'] = block
                save()
                print(f"  {tag} r={r:.2f}: -block {'ok' if ok else '실패'} · 통로 {block['channels']} · 주머니 {block['pockets']} · 구 {nsph} · "
                      f"구 부피 {vsum:.1f} Å³({block['sphere_volume_pct_of_cell']:.3f} %) · {sec} s · 최대 {peak} MB{' · 멈춤!' if stop else ''}", flush=True)
    except RuntimeError as e:
        out['aborted'] = str(e)
        save()
        print(f'!! {e}', flush=True)
        return 5
    out['summary'] = {r['tag']: {f'{k}_{x:.2f}': r[f'r{x:.2f}'][s][f] for x in RADII
                                 for k, s, f in (('channels', 'chan', 'n_channels_chanfile'), ('chan_pockets', 'chan', 'pockets_stdout'),
                                                 ('block_pockets', 'block', 'pockets'), ('spheres', 'block', 'n_spheres'),
                                                 ('block_ok', 'block', 'block_ok'))} for r in rows}
    out['all_blocks_ok'] = all(r[f'r{x:.2f}']['block']['block_ok'] for r in rows for x in RADII)
    save(final=True)
    print(f"저장 {OUT} ({out['elapsed_s']} s)", flush=True)
    for t, v in out['summary'].items():
        print(f"  {t} {json.dumps(v, ensure_ascii=False)}", flush=True)
    return 0


if __name__ == '__main__':
    sys.exit(main())
