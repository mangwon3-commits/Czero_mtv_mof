# -*- coding: utf-8 -*-
"""MAGI-005 E-19 (Junseok) — 우리 경계 조성의 물 경쟁 지수 다씨앗 확인. `ASSIGN_MAGI5B §Junseok 10차`.

[대상] charged_v3/{mslm050, sa50nb50, nbIm100, nbIm050}_DDEC6.cif × 새 씨앗 3 = 12작업(15 s 어긋냄 → 씨앗 다름).
[자·관문] E-16/E-17 과 같음 — TIP5P-Ew 5자리(water.def md5 6fc8850d) · 15,000 + 3,000 · 298 K · 전하 ON · UFF_MOF 8e8ec933 · 12 Å · Ewald 1e-6 ·
          파서 run_tb2_water_kh.read_kh(comp='water') · 착수 전 10 사이클 머리말 관문(첫 대상) · 작업마다 본 계산 관문 + 표지 + 5자리.
[지수] 등록 그대로: K_H(H₂O) 4씨앗 평균(기존 seedfixed 1 + 새 3) / K_H(CO₂)(results_v3; sa50nb50 은 E-14b ON 1.872e-4) · 평균의 ± = ±̄/√4 ·
       단위 = d / √(±₁² + ±₂²) · 참조 saIm050 = 2.354e-4 ± 4.92e-5 / 1.757e-4 (E-16 보완 ⓑ, 1.3399 ± 0.2832).
[보조] nbIm050 은 laptop 의 v3w_water_kh_ours 3씨앗이 이미 있어 7씨앗 평균도 병기(등록 값은 4씨앗). (3) ρ(K_H(H₂O), G) 6조성 = 이 넷 + saIm050 · base
       (둘은 seedfixed 1 + ours 3). G: E-14(hkhome) · saIm050 은 E-1(laptop) · sa50nb50 은 E-14b(desktop-js1ib6u). 판정문은 종합자.
"""
import glob
import hashlib
import json
import math
import os
import shutil
import statistics as st
import subprocess
import sys
import time
from concurrent.futures import ProcessPoolExecutor, as_completed

HERE = '/home/mangwon/mof_project/21_ZIF69_MTV'
ROOT = '/home/mangwon/mof_project'
sys.path.insert(0, HERE)
import run_aryl_gcmc as rg                              # noqa: E402
import ff_gate                                          # noqa: E402
from run_tb2_water_kh import read_kh, count_sites       # noqa: E402

WATER_DEF = os.path.join(ROOT, '19_WaterCompetition', 'water.def')
WATER_MD5 = '6fc8850d3d22a56a17e5643f35a6f731'
RUNS = os.path.join(HERE, 'magi5_e19_runs')
OUT = os.path.join(HERE, 'results_magi5_e19_water_seeds_junseok.json')
NAMES = ('mslm050', 'sa50nb50', 'nbIm100', 'nbIm050')
NSEED = 3
STAGGER = 15.0
REF = {'index': 2.354e-4 / 1.75691e-4, 'src': 'E-16 보완 ⓑ — saIm050 4씨앗 2.354e-4 ± 4.92e-5 / results_v3 1.75691e-4'}
REF['index_err'] = REF['index'] * math.hypot(4.92e-5 / 2.354e-4, 5.56793e-6 / 1.75691e-4)


def write_input(d, name, cycles, init):
    shutil.copy(os.path.join(HERE, 'charged_v3', name + '_DDEC6.cif'), os.path.join(d, name + '_DDEC6.cif'))
    shutil.copy(WATER_DEF, os.path.join(d, 'water.def'))
    na, nb, nc = rg.unit_cells(rg.read(os.path.join(d, name + '_DDEC6.cif')))
    with open(os.path.join(d, 'simulation.input'), 'w') as f:
        f.write(f"""SimulationType                MonteCarlo
NumberOfCycles                {cycles}
NumberOfInitializationCycles  {init}
PrintEvery                    {max(1, cycles // 10)}
RestartFile                   no

Forcefield                    UFF_MOF
CutOff                        {rg.CUTOFF}
UseChargesFromCIFFile         yes
ChargeMethod                  Ewald
EwaldPrecision                1e-6

Framework 0
FrameworkName                 {name}_DDEC6
UnitCells                     {na} {nb} {nc}
ExternalTemperature           298.0
ExternalPressure              1e-05

Component 0 MoleculeName              water
            MoleculeDefinition        TraPPE
            WidomProbability          1.0
            CreateNumberOfMolecules   0
""")
    return [na, nb, nc]


def one(args):
    name, k, delay = args
    time.sleep(delay)
    d = os.path.join(RUNS, f'widom_water_{name}_s{k}')
    os.makedirs(d)
    uc = write_input(d, name, 15000, 3000)
    t0 = time.time()
    subprocess.run([rg.SIMULATE, 'simulation.input'], cwd=d, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False)
    outs = sorted(glob.glob(os.path.join(d, 'Output', 'System_0', '*.data')))
    row = {'name': name, 'seed_idx': k, 'unit_cells': uc, 'minutes': round((time.time() - t0) / 60, 1)}
    if len(outs) != 1:
        row['status'] = f'.data {len(outs)}개'
        return row
    kh, ekh, err = read_kh(outs[0], comp='water')
    hg = ff_gate.read_ff_header(outs[0])
    seed = None
    for ln in open(outs[0], encoding='utf-8', errors='ignore'):
        if 'Random number seed' in ln:
            seed = int(ln.split()[-1])
            break
    row.update(KH_water=kh, KH_water_err=ekh, read_error=err, header_gate_ok=hg.get('ok'), marker_finished=rg.finished(outs[0]), seed=seed,
               water_sites_in_rundir=count_sites(os.path.join(d, 'water.def')), data=os.path.relpath(outs[0], HERE))
    row['status'] = 'ok' if (kh is not None and hg.get('ok') and row['marker_finished'] and row['water_sites_in_rundir'] == 5) else '실패'
    return row


def rank(v):
    o = sorted(range(len(v)), key=lambda i: v[i])
    rk = [0.0] * len(v)
    i = 0
    while i < len(o):
        j = i
        while j + 1 < len(o) and v[o[j + 1]] == v[o[i]]:
            j += 1
        for k in range(i, j + 1):
            rk[o[k]] = (i + j) / 2 + 1
        i = j + 1
    return rk


def spearman(x, y):
    rx, ry = rank(x), rank(y)
    mx, my = st.mean(rx), st.mean(ry)
    den = math.sqrt(sum((a - mx) ** 2 for a in rx) * sum((b - my) ** 2 for b in ry))
    return sum((a - mx) * (b - my) for a, b in zip(rx, ry)) / den if den else float('nan')


def references():
    seedfixed = {r['name']: r for r in json.load(open(os.path.join(HERE, 'v3w_water_kh', 'water_kh_ALLw_hkhome_seedfixed.json')))['rows']}
    ours = {}
    for r in json.load(open(os.path.join(HERE, 'v3w_water_kh_ours', 'water_kh_ours_desktop-nvsrr9m.json')))['rows']:
        ours.setdefault(r['name'], []).append(r)
    v3 = {r['name']: r for r in json.load(open(os.path.join(HERE, 'results_v3.json')))['rows']}
    e14 = {r['name'].replace('_DDEC6', ''): r for r in json.load(open(os.path.join(HERE, 'results_magi5_e14_offwidom_hkhome.json')))['rows']}
    e1 = {r['name'].replace('_DDEC6', ''): r for r in json.load(open(os.path.join(HERE, 'results_magi5_e1_offwidom_laptop.json')))['rows']}
    e14b = {r['charges']: r for r in json.load(open(os.path.join(HERE, 'results_magi5_e3_e14b_sa50nb50_widom_desktop-js1ib6u.json')))['rows']}
    G = {}
    for n in ('base', 'mslm050', 'nbIm100', 'nbIm050'):
        G[n] = (e14[n]['S_ON'] / e14[n]['S_OFF'], 'E-14 hkhome')
    G['saIm050'] = (e1['saIm050']['S_ON'] / e1['saIm050']['S_OFF'], 'E-1 laptop')
    G['sa50nb50'] = (e14b['on']['selectivity'] / e14b['off']['selectivity'], 'E-14b desktop-js1ib6u')
    kco2 = {n: (v3[n]['KH_CO2'], v3[n]['KH_CO2_err'], 'results_v3') for n in ('base', 'saIm050', 'mslm050', 'nbIm100', 'nbIm050')}
    kco2['sa50nb50'] = (e14b['on']['KH_CO2'], e14b['on']['KH_CO2_err'], 'E-14b ON (desktop-js1ib6u)')
    return seedfixed, ours, kco2, G


def main():
    t_start = time.time()
    ok, m = ff_gate.md5_gate(verbose=True)
    if not ok or m != ff_gate.FF_MD5:
        print(f'!! 힘장 파일 관문 실패 ({m})', flush=True)
        return 3
    wm = hashlib.md5(open(WATER_DEF, 'rb').read()).hexdigest()
    if wm != WATER_MD5 or count_sites(WATER_DEF) != 5:
        print('!! water.def 정본 아님', flush=True)
        return 3
    if os.path.exists(RUNS) or os.path.exists(OUT):
        print('!! 이전 E-19 산출 있음 — 멈춤', flush=True)
        return 1
    seedfixed, ours, kco2, G = references()
    hd = os.path.join(RUNS, 'hdrcheck')
    os.makedirs(hd)
    write_input(hd, NAMES[0], 10, 0)
    subprocess.run([rg.SIMULATE, 'simulation.input'], cwd=hd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False)
    outs = sorted(glob.glob(os.path.join(hd, 'Output', 'System_0', '*.data')))
    hg0 = ff_gate.read_ff_header(outs[0]) if len(outs) == 1 else {'ok': False}
    print(f'  [착수 전 머리말 관문] ok {hg0.get("ok")} · HwHw {hg0.get("HwHw")} · OwHw {hg0.get("OwHw")} · OwLw {hg0.get("OwLw")} · '
          f'LwLw {hg0.get("LwLw")} · OwOw ε {hg0.get("OwOw_eps")}', flush=True)
    if not hg0.get('ok'):
        json.dump({'test': 'MAGI-005 E-19', 'status': 'header-gate-failed', 'header_gate_pre': hg0}, open(OUT, 'w', encoding='utf-8'), indent=2, ensure_ascii=False)
        print('!! 머리말 관문 실패 — 아무것도 안 띄움', flush=True)
        return 1
    jobs = [(n, k, STAGGER * i) for i, (n, k) in enumerate((n, k) for k in range(1, NSEED + 1) for n in NAMES)]
    print(f'E-19 {len(jobs)}작업 · 워커 {len(jobs)} · 착수 간격 {STAGGER:g} s · 착수 {time.strftime("%H:%M:%S")}', flush=True)
    res = []

    def write(final=False):
        comp = {}
        for n in NAMES + ('saIm050', 'base'):
            new = [r for r in res if r['name'] == n and r.get('status') == 'ok']
            sf = seedfixed[n]
            reg = [(sf['KH_water'], sf['KH_water_err'], 'seedfixed')] + [(r['KH_water'], r['KH_water_err'], f"E-19 s{r['seed_idx']}") for r in new]
            if n in ('saIm050', 'base'):
                reg = [(sf['KH_water'], sf['KH_water_err'], 'seedfixed')] + [(r['KH_water'], r['KH_water_err'], 'ours') for r in ours[n]]
            c = {'n_seeds': len(reg), 'seeds_src': [x[2] for x in reg], 'KH_water_each': [x[0] for x in reg]}
            if reg:
                mean = st.mean(x[0] for x in reg)
                emean = st.mean(x[1] for x in reg) / math.sqrt(len(reg))
                k, ek, ksrc = kco2[n]
                idx = mean / k
                eidx = idx * math.hypot(emean / mean, ek / k)
                c.update(KH_water_mean=mean, KH_water_mean_err=emean, seed_sd_rel=(st.stdev(x[0] for x in reg) / mean) if len(reg) > 1 else None,
                         KH_CO2=k, KH_CO2_err=ek, KH_CO2_src=ksrc, index=idx, index_err=eidx,
                         units_vs_saIm050=(idx - REF['index']) / math.hypot(eidx, REF['index_err']), G=G[n][0], G_src=G[n][1])
            if n == 'nbIm050' and ours.get('nbIm050'):
                all7 = reg + [(r['KH_water'], r['KH_water_err'], 'ours') for r in ours['nbIm050']]
                m7 = st.mean(x[0] for x in all7)
                c['supplementary_all_seeds'] = {'n': len(all7), 'KH_water_mean': m7, 'KH_water_mean_err': st.mean(x[1] for x in all7) / math.sqrt(len(all7)),
                                                'index': m7 / kco2['nbIm050'][0], 'note': 'laptop v3w_water_kh_ours 3씨앗 더함(등록 값 아님)'}
            comp[n] = c
        out = {'test': 'MAGI-005 E-19 — 우리 경계 조성 물 경쟁 지수 다씨앗', 'assign': 'ASSIGN_MAGI5B_20260925.md §Junseok 10차', 'machine': 'junseok',
               'final': final, 'ff_md5': m, 'water_def_md5': wm, 'header_gate_pre': hg0, 'reference_saIm050': REF,
               'registered': '(1) mslm050 지수 < saIm050 − 1.5 단위 · (2) sa50nb50 지수 가 saIm050 보다 1.5 단위 넘게 낮지 않음 · (3) 6조성 ρ 서술 — 판정문은 종합자',
               'runs': sorted(res, key=lambda r: (r['name'], r['seed_idx'])), 'compositions': comp}
        if final:
            six = [c for c in comp.values() if c.get('index') is not None]
            out['rho_KHwater_G_6'] = spearman([c['KH_water_mean'] for c in six], [c['G'] for c in six]) if len(six) == 6 else None
        out['elapsed_s'] = round(time.time() - t_start)
        tmp = OUT + '.tmp'
        json.dump(out, open(tmp, 'w', encoding='utf-8'), indent=2, ensure_ascii=False)
        os.replace(tmp, OUT)
        return out

    write()
    with ProcessPoolExecutor(max_workers=len(jobs)) as ex:
        for fu in as_completed([ex.submit(one, j) for j in jobs]):
            row = fu.result()
            res.append(row)
            write()
            print(f"  [{row.get('status'):>6}] {row['name']:<9} s{row['seed_idx']} K_H(H2O) {row.get('KH_water')} ± {row.get('KH_water_err')} · 관문 {row.get('header_gate_ok')} · "
                  f"표지 {row.get('marker_finished')} · 씨앗 {row.get('seed')} · {row.get('minutes')} 분", flush=True)
    out = write(final=True)
    print(f"\n저장 {OUT}", flush=True)
    for n, c in out['compositions'].items():
        print(f"  {n:<9} n {c.get('n_seeds')} · K_H(H2O) 평균 {c.get('KH_water_mean')} ± {c.get('KH_water_mean_err')} · 지수 {c.get('index')} ± {c.get('index_err')} · "
              f"saIm050 대비 {c.get('units_vs_saIm050')} 단위 · G {c.get('G')}", flush=True)
    print(f"  ρ(K_H(H2O), G) 6조성 {out.get('rho_KHwater_G_6')}", flush=True)
    return 0


if __name__ == '__main__':
    sys.exit(main())
