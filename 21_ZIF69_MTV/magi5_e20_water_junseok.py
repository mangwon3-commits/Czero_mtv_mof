# -*- coding: utf-8 -*-
"""MAGI-005 E-20 ② (Junseok) — ms50nb50 · sa25nb75 물 Widom 새 씨앗 4/구조 = 8작업. `ASSIGN_MAGI5B §Junseok 11차`.
자·관문은 E-19(`magi5_e19_water_junseok.py`)와 같음 — 그 모듈의 write_input · one · 파서 · 관문을 그대로 import 하고 대상·실행 뿌리·출력만 바꾼다.
지수(K_H(H₂O) 4씨앗 평균 / ① ON K_H(CO₂))는 ① 결과가 있어야 하므로 따로(e20 분석)에서 셈. 여기서는 4씨앗 평균(±̄/√4)과 seedfixed 를 더한 5씨앗 보조만."""
import glob
import hashlib
import importlib.util
import json
import math
import os
import statistics as st
import subprocess
import sys
import time
from concurrent.futures import ProcessPoolExecutor, as_completed

# 이름으로 import 해야 ProcessPoolExecutor 가 E19.one 을 피클할 수 있다(13:38 첫 기동이 importlib 임시 이름 'e19' 로 피클 실패 — 작업 0 에서 죽음).
sys.path.insert(0, '/home/mangwon/.junseok_chain')
import magi5_e19_water as E19   # noqa: E402
HERE = E19.HERE
E19.RUNS = os.path.join(HERE, 'magi5_e20_runs')     # one()·write_input() 이 이 전역을 씀
OUT = os.path.join(HERE, 'results_magi5_e20_water_junseok.json')
NAMES = ('ms50nb50', 'sa25nb75')
NSEED = 4
STAGGER = 15.0


def main():
    t_start = time.time()
    ok, m = E19.ff_gate.md5_gate(verbose=True)
    if not ok or m != E19.ff_gate.FF_MD5:
        print(f'!! 힘장 파일 관문 실패 ({m})', flush=True)
        return 3
    wm = hashlib.md5(open(E19.WATER_DEF, 'rb').read()).hexdigest()
    if wm != E19.WATER_MD5 or E19.count_sites(E19.WATER_DEF) != 5:
        print('!! water.def 정본 아님', flush=True)
        return 3
    if os.path.exists(E19.RUNS):
        print('!! 이전 E-20 물 실행 폴더 있음 — 멈춤', flush=True)
        return 1
    if os.path.exists(OUT):
        prev = json.load(open(OUT, encoding='utf-8'))
        if prev.get('final') or prev.get('runs'):
            print('!! 이전 E-20 물 결과(작업 있음) — 멈춤', flush=True)
            return 1
        print('  이전 결과 파일은 13:38 첫 기동의 빈 대기판(작업 0) — 덮어씀', flush=True)
    seedfixed = {r['name']: r for r in json.load(open(os.path.join(HERE, 'v3w_water_kh', 'water_kh_ALLw_hkhome_seedfixed.json')))['rows']}
    hd = os.path.join(E19.RUNS, 'hdrcheck')
    os.makedirs(hd)
    E19.write_input(hd, NAMES[0], 10, 0)
    subprocess.run([E19.rg.SIMULATE, 'simulation.input'], cwd=hd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False)
    outs = sorted(glob.glob(os.path.join(hd, 'Output', 'System_0', '*.data')))
    hg0 = E19.ff_gate.read_ff_header(outs[0]) if len(outs) == 1 else {'ok': False}
    print(f'  [착수 전 머리말 관문] ok {hg0.get("ok")} · HwHw {hg0.get("HwHw")} · OwHw {hg0.get("OwHw")} · OwLw {hg0.get("OwLw")} · '
          f'LwLw {hg0.get("LwLw")} · OwOw ε {hg0.get("OwOw_eps")}', flush=True)
    if not hg0.get('ok'):
        json.dump({'test': 'MAGI-005 E-20 ②', 'status': 'header-gate-failed', 'header_gate_pre': hg0}, open(OUT, 'w', encoding='utf-8'), indent=2, ensure_ascii=False)
        return 1
    jobs = [(n, k, STAGGER * i) for i, (n, k) in enumerate((n, k) for k in range(1, NSEED + 1) for n in NAMES)]
    print(f'E-20 ② {len(jobs)}작업 · 워커 {len(jobs)} · 착수 간격 {STAGGER:g} s · 착수 {time.strftime("%H:%M:%S")}', flush=True)
    res = []

    def write(final=False):
        comp = {}
        for n in NAMES:
            new = [r for r in res if r['name'] == n and r.get('status') == 'ok']
            c = {'n_new': len(new), 'KH_water_each': [r['KH_water'] for r in new], 'seeds': [r['seed'] for r in new]}
            if new:
                c['KH_water_mean4'] = st.mean(r['KH_water'] for r in new)
                c['KH_water_mean4_err'] = st.mean(r['KH_water_err'] for r in new) / math.sqrt(len(new))
                c['seed_sd_rel'] = st.stdev(r['KH_water'] for r in new) / c['KH_water_mean4'] if len(new) > 1 else None
                sf = seedfixed.get(n)
                if sf:
                    allv = [r['KH_water'] for r in new] + [sf['KH_water']]
                    alle = [r['KH_water_err'] for r in new] + [sf['KH_water_err']]
                    c['supplementary_with_seedfixed'] = {'n': len(allv), 'KH_water_mean': st.mean(allv), 'KH_water_mean_err': st.mean(alle) / math.sqrt(len(allv)),
                                                         'seedfixed': [sf['KH_water'], sf['KH_water_err']], 'note': '등록 값 아님(등록 = 새 4씨앗)'}
            comp[n] = c
        out = {'test': 'MAGI-005 E-20 ② — ms50nb50 · sa25nb75 물 Widom 4씨앗', 'assign': 'ASSIGN_MAGI5B_20260925.md §Junseok 11차', 'machine': 'junseok',
               'final': final, 'ff_md5': m, 'water_def_md5': wm, 'header_gate_pre': hg0,
               'protocol': 'E-19 와 같음(TIP5P-Ew 5자리 · 15,000 + 3,000 · 298 K · 전하 ON · read_kh(water) · 관문 착수 전·후)',
               'runs': sorted(res, key=lambda r: (r['name'], r['seed_idx'])), 'compositions': comp, 'elapsed_s': round(time.time() - t_start)}
        tmp = OUT + '.tmp'
        json.dump(out, open(tmp, 'w', encoding='utf-8'), indent=2, ensure_ascii=False)
        os.replace(tmp, OUT)
        return out

    write()
    with ProcessPoolExecutor(max_workers=len(jobs)) as ex:
        for fu in as_completed([ex.submit(E19.one, j) for j in jobs]):
            row = fu.result()
            res.append(row)
            write()
            print(f"  [{row.get('status'):>6}] {row['name']:<9} s{row['seed_idx']} K_H(H2O) {row.get('KH_water')} ± {row.get('KH_water_err')} · 관문 {row.get('header_gate_ok')} · "
                  f"표지 {row.get('marker_finished')} · 씨앗 {row.get('seed')} · {row.get('minutes')} 분", flush=True)
    out = write(final=True)
    print(f"\n저장 {OUT}", flush=True)
    for n, c in out['compositions'].items():
        print(f"  {n:<9} 새 {c['n_new']} · 평균 {c.get('KH_water_mean4')} ± {c.get('KH_water_mean4_err')} · 씨앗 간 SD {c.get('seed_sd_rel')}", flush=True)
    return 0


if __name__ == '__main__':
    sys.exit(main())
