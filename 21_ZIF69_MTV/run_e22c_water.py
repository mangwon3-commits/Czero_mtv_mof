# -*- coding: utf-8 -*-
"""E-22c — Zn(bib)(bdtdc) e22_{parent,no2_050,no2_100} 물 Widom 4씨앗. 등록 ASSIGN_MAGI5B §HKHOME 8차.
프로토콜은 Junseok magi5_e19_water_junseok.py 와 같음(입력 문구 그대로; 그 파일은 경로가 그 기기라 import 불가 → 같은 입력을 여기서 씀)."""
import glob, hashlib, json, os, shutil, subprocess, sys, time
from concurrent.futures import ProcessPoolExecutor, as_completed
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE); sys.path.insert(0, HERE)
import run_aryl_gcmc as rg                      # noqa: E402
import ff_gate                                  # noqa: E402
from run_tb2_water_kh import read_kh, count_sites   # noqa: E402
WATER_DEF = os.path.join(ROOT, '19_WaterCompetition', 'water.def'); WATER_MD5 = '6fc8850d3d22a56a17e5643f35a6f731'
RUNS = os.path.join(HERE, 'e22c_runs'); OUT = os.path.join(HERE, 'results_e22c_water_hkhome.json')
NAMES = ('e22_parent', 'e22_no2_050', 'e22_no2_100'); NSEED = 4; STAGGER = 15.0


def write_input(d, name):
    shutil.copy(os.path.join(HERE, 'charged_v3', name + '_DDEC6.cif'), os.path.join(d, name + '_DDEC6.cif'))
    shutil.copy(WATER_DEF, os.path.join(d, 'water.def'))
    na, nb, nc = rg.unit_cells(rg.read(os.path.join(d, name + '_DDEC6.cif')))
    open(os.path.join(d, 'simulation.input'), 'w').write(f"""SimulationType                MonteCarlo
NumberOfCycles                15000
NumberOfInitializationCycles  3000
PrintEvery                    1500
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
    if os.path.exists(d):
        shutil.rmtree(d)
    os.makedirs(d)
    uc = write_input(d, name); t0 = time.time()
    r = subprocess.run([rg.SIMULATE, 'simulation.input'], cwd=d, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    outs = sorted(glob.glob(os.path.join(d, 'Output', 'System_0', '*.data')))
    row = {'name': name, 'seed_idx': k, 'unit_cells': uc, 'returncode': r.returncode, 'minutes': round((time.time() - t0) / 60, 1)}
    if len(outs) != 1:
        row['status'] = f'.data {len(outs)}개'; return row
    kh, ekh, err = read_kh(outs[0], comp='water'); hg = ff_gate.read_ff_header(outs[0])
    seed = next((int(ln.split()[-1]) for ln in open(outs[0], encoding='utf-8', errors='ignore') if 'Random number seed' in ln), None)
    row.update(KH_water=kh, KH_water_err=ekh, read_error=err, header_gate_ok=hg.get('ok'), marker_finished=rg.finished(outs[0]), seed=seed,
               water_sites_in_rundir=count_sites(os.path.join(d, 'water.def')))
    row['status'] = 'ok' if (kh is not None and hg.get('ok') and row['marker_finished'] and row['water_sites_in_rundir'] == 5 and r.returncode == 0) else '실패'
    return row


if __name__ == '__main__':
    ok, m = ff_gate.md5_gate(verbose=True)
    wm = hashlib.md5(open(WATER_DEF, 'rb').read()).hexdigest()
    if not ok or wm != WATER_MD5 or count_sites(WATER_DEF) != 5:
        print('!! 관문 실패 — 착수 안 함', ok, wm); sys.exit(3)
    os.makedirs(RUNS, exist_ok=True)
    jobs = [(n, k, STAGGER * (i % 8)) for i, (n, k) in enumerate((n, k) for k in range(1, NSEED + 1) for n in NAMES)]
    rows = []
    with ProcessPoolExecutor(max_workers=8) as ex:
        for fu in as_completed([ex.submit(one, j) for j in jobs]):
            r = fu.result(); rows.append(r); print(r['name'], r['seed_idx'], r['status'], r.get('KH_water'), r.get('minutes'), flush=True)
            json.dump({'test': 'E-22c', 'finished': False, 'ff_md5': m, 'water_def_md5': wm, 'rows': rows}, open(OUT, 'w'), indent=1)
    seeds = [r.get('seed') for r in rows]
    json.dump({'test': 'E-22c', 'finished': True, 'ff_md5': m, 'water_def_md5': wm, 'seed_dup': len(seeds) - len(set(seeds)), 'rows': rows}, open(OUT, 'w'), indent=1)
    print('E-22c 완주', flush=True)
