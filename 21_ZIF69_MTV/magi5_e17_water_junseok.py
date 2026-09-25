# -*- coding: utf-8 -*-
"""MAGI-005 E-17 (Junseok) — CoRE 3D 열역학 상위 12행의 물: E-15 3D 12행 − E-16 = 11행 물 Widom. `ASSIGN_MAGI5B §Junseok 8차`.

[자·관문] E-16(`magi5_e16_water_junseok.py`)과 같음 — TIP5P-Ew 5자리(water.def md5 6fc8850d) · 15,000 + 3,000 · 298 K · 전하 ON(CoRE PACMAN DDEC6) ·
          UFF_MOF 8e8ec933 · 12 Å · Ewald 1e-6 · 1e-5 Pa · unit_cells · 파서 run_tb2_water_kh.read_kh(comp='water').
          **착수 전** 머리말 관문: 첫 대상 10 사이클 시험의 인쇄 쌍 표(ff_gate.read_ff_header — Hw/Lw ZERO · Ow–Ow 89.633). 실패면 아무것도 안 띄움.
          **작업마다** 본 계산 .data 로 같은 관문 + 표지 + water.def 5자리 → 셋 다여야 ok.
[표지]   has_OMS — CoRE 메타 슬라이스 짝짓기(금속 · 원자 수 · LCD/PLD < 0.01 Å · ASR/FSR 판 일치). 짝 없으면 None.
[통계]   E-16 행을 더해 12행: (1) Spearman ρ(K_H(H₂O), G) + 부트스트랩(10,000, 씨앗 20260925) (2) 지수 K_H(H₂O)/K_H(CO₂) 중앙
         (3) 12행 안의 ASR/FSR 짝 K_H(H₂O) |Δ| / max(±) 와 / √(±₁²+±₂²). 판정문은 종합자.
"""
import glob
import hashlib
import json
import math
import os
import random
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
RUNS = os.path.join(HERE, 'magi5_e17_runs')
OUT = os.path.join(HERE, 'results_magi5_e17_core3d_water_junseok.json')
E16 = os.path.join(HERE, 'results_magi5_e16_zndia_water_junseok.json')
E16_NAME = '2017_Zn__dia_3_ASR_1'
STAGGER = 15.0


def targets():
    e15 = json.load(open(os.path.join(HERE, 'results_magi5_e15_offwidom_junseok.json'), encoding='utf-8'))
    ann = {r['file']: r for r in json.load(open(os.path.join(HERE, 'core_pop_annotated.json'), encoding='utf-8'))['rows']}
    meta = json.load(open(os.path.join(ROOT, '23_SCREENING', 'data', 'CR_meta_data_SI_slice.json'), encoding='utf-8'))
    out = []
    for r in [x for x in e15['rows'] if x.get('set') == '3D']:
        a = ann[r['name'] + '.cif']
        hits = [k for k, m in meta.items()
                if (m.get('metal') or {}).get('metal_type') and a.get('metal') and a['metal'] in str((m.get('metal') or {}).get('metal_type'))
                and (m.get('structure_info') or {}).get('n_atoms') == a.get('NAtoms')
                and abs(((m.get('Zeopp') or {}).get('LCD') or 0) - a['LCD']) < 0.01
                and abs(((m.get('Zeopp') or {}).get('PLD') or 0) - a['PLD']) < 0.01]
        ext = 'ASR' if '_ASR_' in r['name'] else 'FSR'
        pick = [h for h in hits if f'_{ext}_' in h] or hits
        mm = meta[pick[0]] if len(pick) == 1 else None
        G = r['S_ON'] / r['S_OFF']
        out.append({'name': r['name'], 'key': r['key'], 'asr_fsr_pair': r.get('asr_fsr_pair'),
                    'G': G, 'G_err': G * math.hypot(r['S_ON_err'] / r['S_ON'], r['S_OFF_err'] / r['S_OFF']),
                    'S_ON': r['S_ON'], 'S_OFF': r['S_OFF'],
                    'KH_CO2_on': r['on_ref']['KH_CO2'], 'KH_CO2_on_err': r['on_ref']['KH_CO2_err'],
                    'meta_key': pick[0] if len(pick) == 1 else None, 'meta_hits': hits,
                    'has_OMS': (mm.get('metal') or {}).get('has_OMS') if mm else None,
                    'OMS_type': (mm.get('metal') or {}).get('OMS_type') if mm else None,
                    'DOI': (mm.get('reference') or {}).get('DOI') if mm else None})
    return out


def write_input(d, name, cycles, init):
    shutil.copy(os.path.join(HERE, 'core_pop_cifs', name + '.cif'), os.path.join(d, name + '.cif'))
    shutil.copy(WATER_DEF, os.path.join(d, 'water.def'))
    na, nb, nc = rg.unit_cells(rg.read(os.path.join(d, name + '.cif')))
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
FrameworkName                 {name}
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
    name, delay = args
    time.sleep(delay)
    d = os.path.join(RUNS, f'widom_water_{name}')
    os.makedirs(d)
    uc = write_input(d, name, 15000, 3000)
    t0 = time.time()
    subprocess.run([rg.SIMULATE, 'simulation.input'], cwd=d, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False)
    outs = sorted(glob.glob(os.path.join(d, 'Output', 'System_0', '*.data')))
    row = {'name': name, 'unit_cells': uc, 'minutes': round((time.time() - t0) / 60, 1)}
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
    row.update(KH_water=kh, KH_water_err=ekh, read_error=err, header_gate_ok=hg.get('ok'), header_gate=hg,
               marker_finished=rg.finished(outs[0]), seed=seed, water_sites_in_rundir=count_sites(os.path.join(d, 'water.def')),
               data=os.path.relpath(outs[0], HERE))
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


def main():
    t_start = time.time()
    ok, m = ff_gate.md5_gate(verbose=True)
    if not ok or m != ff_gate.FF_MD5:
        print(f'!! 힘장 파일 관문 실패 ({m})', flush=True)
        return 3
    wm = hashlib.md5(open(WATER_DEF, 'rb').read()).hexdigest()
    if wm != WATER_MD5 or count_sites(WATER_DEF) != 5:
        print(f'!! water.def 정본 아님 ({wm}, {count_sites(WATER_DEF)} 자리)', flush=True)
        return 3
    if os.path.exists(RUNS) or os.path.exists(OUT):
        print('!! 이전 E-17 산출 있음 — 멈춤', flush=True)
        return 1
    T = targets()
    e16 = json.load(open(E16, encoding='utf-8'))
    T11 = [t for t in T if t['name'] != E16_NAME]
    print(f'E-17 대상 {len(T11)}행 (3D {len(T)} − E-16) · has_OMS {[(t["name"], t["has_OMS"]) for t in T11]}', flush=True)
    if len(T11) != 11:
        print('!! 대상이 11행이 아님 — 멈춤', flush=True)
        return 2
    hd = os.path.join(RUNS, 'hdrcheck')
    os.makedirs(hd)
    write_input(hd, T11[0]['name'], 10, 0)
    subprocess.run([rg.SIMULATE, 'simulation.input'], cwd=hd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False)
    outs = sorted(glob.glob(os.path.join(hd, 'Output', 'System_0', '*.data')))
    hg0 = ff_gate.read_ff_header(outs[0]) if len(outs) == 1 else {'ok': False, 'why': f'.data {len(outs)}개'}
    print(f'  [착수 전 머리말 관문] ok {hg0.get("ok")} · HwHw {hg0.get("HwHw")} · OwHw {hg0.get("OwHw")} · OwLw {hg0.get("OwLw")} · '
          f'LwLw {hg0.get("LwLw")} · OwOw ε {hg0.get("OwOw_eps")}', flush=True)
    if not hg0.get('ok'):
        json.dump({'test': 'MAGI-005 E-17', 'status': 'header-gate-failed', 'header_gate_pre': hg0}, open(OUT, 'w', encoding='utf-8'),
                  indent=2, ensure_ascii=False)
        print('!! 머리말 관문 실패 — 아무것도 안 띄움(힘장 수정 = 사용자 결정)', flush=True)
        return 1
    by = {t['name']: t for t in T}
    res = {}

    def write(final=False):
        rows = []
        for t in T:
            row = dict(t)
            if t['name'] == E16_NAME:
                r16 = e16['row']
                row.update(source='E-16 (results_magi5_e16_zndia_water_junseok.json)', KH_water=r16['KH_water'], KH_water_err=r16['KH_water_err'],
                           status=r16['status'], header_gate_ok=r16['header_gate']['ok'], marker_finished=r16['marker_finished'], seed=r16['seed'])
            else:
                row.update(res.get(t['name'], {'status': 'pending'}))
                row['source'] = 'E-17'
            if row.get('status') == 'ok':
                row['index'] = row['KH_water'] / row['KH_CO2_on']
                row['index_err'] = row['index'] * math.hypot(row['KH_water_err'] / row['KH_water'], row['KH_CO2_on_err'] / row['KH_CO2_on'])
            rows.append(row)
        out = {'test': 'MAGI-005 E-17 — CoRE 3D 열역학 상위 12행의 물(정전기 이득 G 와 물 벌점)', 'assign': 'ASSIGN_MAGI5B_20260925.md §Junseok 8차',
               'machine': 'junseok', 'final': final, 'ff_md5': m, 'water_def_md5': wm, 'header_gate_pre': hg0,
               'protocol': 'E-16 과 같음 — TIP5P-Ew 5자리 · 15,000 + 3,000 · 298 K · 전하 ON · UFF_MOF · 12 Å · Ewald 1e-6 · read_kh(water)',
               'registered': '(1) ρ(K_H(H2O), G) ≥ 0.5 (12행, 기각 < 0) · (2) 지수 중앙 ≤ 1.34 (기각 > 1.34) · (3) ASR/FSR 짝 K_H(H2O) 1.5 단위 안 — 판정문은 종합자',
               'rows': rows}
        ok_rows = [r for r in rows if r.get('status') == 'ok']
        if final and len(ok_rows) >= 3:
            kw, G = [r['KH_water'] for r in ok_rows], [r['G'] for r in ok_rows]
            rho = spearman(kw, G)
            rnd = random.Random(20260925)
            boots = []
            for _ in range(10000):
                ix = [rnd.randrange(len(ok_rows)) for _ in ok_rows]
                b = spearman([kw[i] for i in ix], [G[i] for i in ix])
                if not math.isnan(b):
                    boots.append(b)
            boots.sort()
            pairs = []
            bk = {r['key']: r for r in ok_rows}
            seen = set()
            for r in ok_rows:
                p = r.get('asr_fsr_pair')
                if p in bk and (p, r['key']) not in seen:
                    q = bk[p]
                    seen.add((r['key'], p))
                    dk = abs(r['KH_water'] - q['KH_water'])
                    pairs.append({'a': r['key'], 'b': p, 'KH_water_a': r['KH_water'], 'KH_water_b': q['KH_water'],
                                  'units_max': dk / max(r['KH_water_err'], q['KH_water_err']),
                                  'units_comb': dk / math.hypot(r['KH_water_err'], q['KH_water_err'])})
            out['stats'] = {'n': len(ok_rows), 'rho_KHwater_G': rho,
                            'rho_boot95': [boots[int(0.025 * len(boots))], boots[int(0.975 * len(boots)) - 1]] if boots else None,
                            'index_median': st.median(r['index'] for r in ok_rows), 'index_range': [min(r['index'] for r in ok_rows), max(r['index'] for r in ok_rows)],
                            'pairs': pairs, 'pairs_outside_1p5_max': sum(p['units_max'] > 1.5 for p in pairs),
                            'pairs_outside_1p5_comb': sum(p['units_comb'] > 1.5 for p in pairs),
                            'has_OMS_split': {k: [r['name'] for r in ok_rows if r.get('has_OMS') == k] for k in ('Yes', 'No', None)}}
        out['elapsed_s'] = round(time.time() - t_start)
        tmp = OUT + '.tmp'
        json.dump(out, open(tmp, 'w', encoding='utf-8'), indent=2, ensure_ascii=False)
        os.replace(tmp, OUT)
        return out

    write()
    with ProcessPoolExecutor(max_workers=len(T11)) as ex:
        futs = [ex.submit(one, (t['name'], STAGGER * i)) for i, t in enumerate(T11)]
        for fu in as_completed(futs):
            row = fu.result()
            res[row['name']] = row
            write()
            print(f"  [{row.get('status'):>6}] {row['name']:<26} K_H(H2O) {row.get('KH_water')} ± {row.get('KH_water_err')} · 관문 {row.get('header_gate_ok')} · "
                  f"표지 {row.get('marker_finished')} · 씨앗 {row.get('seed')} · {row.get('minutes')} 분", flush=True)
    out = write(final=True)
    s = out.get('stats', {})
    print(f"\n저장 {OUT}", flush=True)
    print(f"  12행 ok {s.get('n')} · ρ(K_H(H2O), G) {s.get('rho_KHwater_G')} · 부트스트랩 {s.get('rho_boot95')} · 지수 중앙 {s.get('index_median')} · "
          f"짝 {len(s.get('pairs', []))} 중 1.5 단위 밖 max {s.get('pairs_outside_1p5_max')} / 합성 {s.get('pairs_outside_1p5_comb')}", flush=True)
    return 0


if __name__ == '__main__':
    sys.exit(main())
