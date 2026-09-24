# -*- coding: utf-8 -*-
"""MAGI-005 E-1 (P6′) — 골격 전하 OFF Widom(CO₂·N₂) 6작업. 랩탑(Melchior) 몫.

배정: `ASSIGN_MAGI5_20260925.md` §E-1 · 등록: `MAGI/MAGI-005_R3_laptop.md` 재등록안 P6′(자료 0건 시점).
판정문은 종합자가 씁니다 — 이 러너는 값과 표지만 냅니다.

[왜 사본인가]
    공용 `run_aryl_gcmc.run_one` 은 입력에 `UseChargesFromCIFFile yes` 를 박아 둡니다. 공용 파일을 고치지 않고
    (배정 규율) 그 함수의 입력 쓰기 부분만 이 파일에 옮겼습니다. 파서·완주 판정·셀 규칙·점유 검사는
    **공용 모듈의 것을 그대로 import** 합니다 — 파서가 둘이면 어긋납니다.

[자 — run_core_pop.py 와 같음, 전하만 다름]
    Widom 초기화 3,000 + 15,000 · 298 K · UFF_MOF · 12 Å · Ewald 1e-6 · unit_cells() 규칙 · CO₂ García-Sánchez · N₂ TraPPE.
    OFF = `UseChargesFromCIFFile no` + `ChargeMethod Ewald` 유지(흡착질 전하 유지) — `run_density_map.py:90` 의 q_off 와 같은 규약.

[관문]
    ① 파일 관문: `ff_gate.md5_gate()` — 힘장 md5 8e8ec933… 아니면 착수 안 함.
    ② 머리말 관문(작업마다, RASPA 가 **인쇄한** 것을 봄):
       · 골격 pseudo atom(Framework-atom: yes) 중 전하 ≠ 0 인 것의 수 == 0   ← OFF 가 실제로 먹었는가
         (실측 근거: density_v3/base__q_on 600/600 비영 · base__q_off 0/600 — 2026-09-25 이 세션)
       · C_co2 29.933/2.745 · O_co2 85.671/3.017 · N_n2 38.298/3.306 LJ 줄이 인쇄됐는가
    ③ 완주 표지 `Simulation finished` + 값 — 공용 `finished()`/`parse()`.

[seed]
    RASPA seed 는 착수 시각에서 옵니다. 작업을 12 s 간격으로 착수하고, 끝나면 seed 겹침을 셉니다.
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
from concurrent.futures import ProcessPoolExecutor, as_completed

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import run_aryl_gcmc as rg          # noqa: E402  parse · finished · unit_cells · occupied_by_other · SIMULATE
from ff_gate import FF_MD5, md5_gate   # noqa: E402
from ase.io import read             # noqa: E402

WORKERS = int(os.environ.get('MAGI5_WORKERS', '6'))
STAGGER = float(os.environ.get('MAGI5_STAGGER', '12'))
MACHINE = os.environ.get('MAGI5_MACHINE', 'laptop')
RUNS = os.path.join(HERE, 'magi5_e1_runs')
OUT = os.path.join(HERE, f'results_magi5_e1_offwidom_{MACHINE}.json')

# 대상 · ON 참조값(다시 안 돌림) · 정체 표지. ON 값의 출처를 행에 같이 적는다.
TARGETS = [
    {'name': '2010_Zn__pts_3_ASR_1', 'cif': os.path.join(HERE, 'core_pop_cifs', '2010_Zn__pts_3_ASR_1.cif'),
     'key': '2010[Zn][pts]3[ASR]1', 'dim': 3,
     'identity': '미확인',
     'identity_note': ('CIF 결합 분석(ase, 2026-09-25 이 세션): C32H24O32Zn4 · 92원자 · Zn–O4(1.98~1.99 Å) · N 0 → 카복실레이트([[J-8]] 와 일치), '
                       'N–N 0 · N–H 0(N 없음) · C–H 24 · 제미널 H–H(<1.75 Å) 8쌍 = CH2 로 보임. CoRE 메타 슬라이스의 2010·Zn 행은 1개(ic101935f_si_002, '
                       '428원자, LCD 13.58)뿐이라 짝 안 맞음 → DOI·상·유연성 미확인. 차원 3(키).'),
     'on_ref': {'src': 'core_pop_results_laptop.json', 'KH_CO2': 9.09385e-05, 'KH_CO2_err': 2.50868e-06,
                'KH_N2': 6.24809e-07, 'KH_N2_err': 1.05811e-08, 'dU_CO2': -32.8238496629}},
    {'name': '2012_Co__dia_3_ASR_3', 'cif': os.path.join(HERE, 'core_pop_cifs', '2012_Co__dia_3_ASR_3.cif'),
     'key': '2012[Co][dia]3[ASR]3', 'dim': 3,
     'identity': '미확인(링커형만 확인)',
     'identity_note': 'Co–N4 사면체 1.99 Å · N–N 0 · N 당 C 이웃 2 → 이미다졸레이트형(MAGI-005 R3 D-2). DOI 미확인.',
     'on_ref': {'src': 'core_pop_results_laptop.json', 'KH_CO2': 6.51574e-05, 'KH_CO2_err': 7.63249e-07,
                'KH_N2': 1.90798e-06, 'KH_N2_err': 2.17754e-08, 'dU_CO2': -28.9098865529}},
    {'name': 'saIm050_DDEC6', 'cif': os.path.join(HERE, 'charged_v3', 'saIm050_DDEC6.cif'),
     'key': 'saIm050', 'dim': 3,
     'identity': '우리 v3 조성(ZIF-69 gme, −SO3H 50 %)', 'identity_note': 'results_v3.json 의 saIm050 과 같은 CIF 계열(charged_v3).',
     'on_ref': {'src': 'results_v3.json', 'KH_CO2': 0.000175691, 'KH_CO2_err': 5.56793e-06,
                'KH_N2': 2.69441e-06, 'KH_N2_err': 1.60465e-08, 'dU_CO2': None}},
]

PROTOCOL = {
    'widom_cycles': rg.WIDOM_CYCLES, 'widom_init': rg.WIDOM_INIT, 'forcefield': 'UFF_MOF', 'ff_md5': FF_MD5,
    'cutoff': rg.CUTOFF, 'temp_K': rg.TEMP, 'charges': 'OFF — UseChargesFromCIFFile no, ChargeMethod Ewald(흡착질 전하 유지)',
    'supercell': 'unit_cells() 규칙', 'co2': 'García-Sánchez 2009 (경로 TraPPE/CO2.def, TraPPE 아님)', 'n2': 'TraPPE N2(3자리)',
}
LJ_EXPECT = {'C_co2': (29.933, 2.745), 'O_co2': (85.671, 3.017), 'N_n2': (38.298, 3.306)}


def header_gate(path, gas):
    """RASPA 가 인쇄한 머리말로 OFF·흡착질 모형을 확인한다."""
    n_fw = nz = 0
    lj = {}
    lines = open(path, encoding='utf-8', errors='ignore').read().splitlines()
    for i, ln in enumerate(lines):
        if ln.startswith('Pseudo Atom[') and i + 2 < len(lines):
            if re.search(r'Framework-atom:\s+yes', lines[i + 2]):
                n_fw += 1
                m = re.search(r'Charge=([-+0-9.eE]+)', lines[i + 1])
                if m and abs(float(m.group(1))) > 0.0:
                    nz += 1
        for a, (eps, sig) in LJ_EXPECT.items():
            if a not in lj and re.match(r'^\s*' + a + r'\s+-\s+' + a + r'\s+\[LENNARD_JONES\]', ln):
                g = re.findall(r'[-+]?\d*\.\d+', ln)
                lj[a] = (float(g[0]), float(g[1])) if len(g) >= 2 else None
    need = ['C_co2', 'O_co2'] if gas == 'CO2' else ['N_n2']
    lj_ok = all(lj.get(a) and abs(lj[a][0] - LJ_EXPECT[a][0]) < 1e-3 and abs(lj[a][1] - LJ_EXPECT[a][1]) < 1e-3
                for a in need)
    return {'framework_pseudo_atoms': n_fw, 'framework_nonzero_charge': nz,
            'charges_off_ok': (n_fw > 0 and nz == 0), 'lj': {a: lj.get(a) for a in need}, 'lj_ok': lj_ok,
            'ok': (n_fw > 0 and nz == 0 and lj_ok)}


def seed_of(path):
    for ln in open(path, encoding='utf-8', errors='ignore'):
        m = re.match(r'\s*Random number seed:\s*(\d+)', ln)
        if m:
            return int(m.group(1))
    return None


def total_time(path):
    t = None
    for ln in open(path, encoding='utf-8', errors='ignore'):
        m = re.match(r'\s*total time:\s*([0-9.]+)', ln)
        if m:
            t = float(m.group(1))
    return t


def run_one_off(job):
    """`rg.run_one` 과 같은 흐름 — 입력의 전하 줄만 no. 실행 폴더는 따로(magi5_e1_runs)."""
    idx, cif, gas = job
    name = os.path.basename(cif).replace('.cif', '')
    d = os.path.join(RUNS, f'widom_{gas}_{name}_qoff')

    done = glob.glob(os.path.join(d, 'Output', 'System_0', '*.data'))
    if done and rg.finished(done[0]):
        r = rg.parse(done[0])
        hg = header_gate(done[0], gas)
        if r[0] is not None and hg['ok']:
            return name, gas, r, 'cached', hg, seed_of(done[0]), total_time(done[0])
    if rg.occupied_by_other(d):
        return name, gas, None, '다른세션실행중', None, None, None

    time.sleep(idx * STAGGER)                      # seed 겹침 방지(착수 간격)
    os.makedirs(d, exist_ok=True)
    shutil.copy(cif, os.path.join(d, name + '.cif'))
    na, nb, nc = rg.unit_cells(read(cif))
    with open(os.path.join(d, 'simulation.input'), 'w') as f:
        f.write(f"""SimulationType                MonteCarlo
NumberOfCycles                {rg.WIDOM_CYCLES}
NumberOfInitializationCycles  {rg.WIDOM_INIT}
PrintEvery                    {rg.WIDOM_CYCLES}
RestartFile                   no

Forcefield                    UFF_MOF
CutOff                        {rg.CUTOFF}
UseChargesFromCIFFile         no
ChargeMethod                  Ewald
EwaldPrecision                1e-6

Framework 0
FrameworkName                 {name}
UnitCells                     {na} {nb} {nc}
ExternalTemperature           {rg.TEMP}
ExternalPressure              1e-5

Component 0 MoleculeName              {gas}
            MoleculeDefinition        TraPPE
            WidomProbability          1.0
            CreateNumberOfMolecules   0
""")
    try:
        subprocess.run([rg.SIMULATE, 'simulation.input'], cwd=d, stdout=subprocess.DEVNULL,
                       stderr=subprocess.DEVNULL, timeout=28800, check=False)
    except subprocess.TimeoutExpired:
        return name, gas, None, 'timeout', None, None, None
    outs = glob.glob(os.path.join(d, 'Output', 'System_0', '*.data'))
    if not outs:
        return name, gas, None, 'no-output', None, None, None
    if not rg.finished(outs[0]):                   # 값이 아니라 표지가 자(CLAUDE.md §0)
        return name, gas, None, '미완주', header_gate(outs[0], gas), seed_of(outs[0]), None
    res = rg.parse(outs[0])
    hg = header_gate(outs[0], gas)
    if res[0] is None:
        return name, gas, None, '값없음', hg, seed_of(outs[0]), total_time(outs[0])
    if not hg['ok']:
        return name, gas, res, '머리말관문실패', hg, seed_of(outs[0]), total_time(outs[0])
    for sub in ('VTK', 'Movies', 'Restart'):
        shutil.rmtree(os.path.join(d, sub), ignore_errors=True)
    return name, gas, res, 'ok', hg, seed_of(outs[0]), total_time(outs[0])


def sel(kc, ekc, kn, ekn):
    s = kc / kn
    rel = math.sqrt((ekc / kc) ** 2 + (ekn / kn) ** 2)   # ± 는 RASPA 95 % CI — 같은 자끼리 상대오차 합성
    return s, s * rel, rel


def write(rows, note=''):
    json.dump({'test': 'MAGI-005 E-1 (P6′) 골격 전하 OFF Widom', 'assign': 'ASSIGN_MAGI5_20260925.md §E-1',
               'registration': 'MAGI/MAGI-005_R3_laptop.md 재등록안 P6′', 'machine': MACHINE, 'workers': WORKERS,
               'protocol': PROTOCOL,
               'note': ('판정 없음(종합자가 씀). ± 는 RASPA 95 % CI. S_OFF ± 는 두 K_H 의 상대 ± 를 제곱합으로 합성. '
                        'ln_ratio = ln S_OFF / ln S_ON (점추정). 외부 계열(CoRE) 행은 우리 물질 결과가 아님. ' + note),
               'rows': rows}, open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)


def main():
    ok, m = md5_gate()
    if not ok:
        print('!! 파일 관문 실패 — 착수 안 함', flush=True)
        return 3
    for t in TARGETS:
        if not os.path.exists(t['cif']):
            print(f"!! CIF 없음 {t['cif']}", flush=True)
            return 2
    os.makedirs(RUNS, exist_ok=True)
    jobs = [(i, t['cif'], g) for i, (t, g) in enumerate((t, g) for t in TARGETS for g in ('CO2', 'N2'))]
    print(f'E-1 전하 OFF Widom  {len(jobs)}작업 · 워커 {WORKERS} · 착수 간격 {STAGGER:.0f} s · 힘장 md5 {m}', flush=True)
    got = {}
    t0 = time.time()
    with ProcessPoolExecutor(max_workers=WORKERS) as ex:
        futs = [ex.submit(run_one_off, j) for j in jobs]
        for n, fu in enumerate(as_completed(futs), 1):
            name, gas, r, stt, hg, seed, tt = fu.result()
            got.setdefault(name, {})[gas] = (r, stt, hg, seed, tt)
            gate = '' if hg is None else f"  관문 OFF {hg['framework_nonzero_charge']}/{hg['framework_pseudo_atoms']} 비영 · LJ {'ok' if hg['lj_ok'] else 'X'}"
            print(f'  [{stt:>8}] {gas:<3} {name}  ({n}/{len(jobs)}, {((time.time() - t0) / 60):.1f} min){gate}', flush=True)
            rows = []
            for t in TARGETS:
                g = got.get(t['name'], {})
                row = {'name': t['name'], 'key': t['key'], 'cif': os.path.relpath(t['cif'], HERE), 'charges': 'off',
                       'identity': t['identity'], 'identity_note': t['identity_note'], 'dim': t['dim'],
                       'ff_md5': m, 'machine': MACHINE, 'status': 'pending'}
                for gg in ('CO2', 'N2'):
                    if gg in g:
                        r, s_, hg_, sd, tt_ = g[gg]
                        row[f'run_status_{gg}'] = s_
                        row[f'header_gate_{gg}'] = hg_
                        row[f'seed_{gg}'] = sd
                        row[f'total_time_s_{gg}'] = tt_
                        if r is not None and s_ in ('ok', 'cached'):
                            row[f'KH_{gg}'], row[f'KH_{gg}_err'] = r[0], r[1]
                            row[f'dU_{gg}'], row[f'dU_{gg}_err'] = r[2], r[3]
                on = t['on_ref']
                row['on_ref'] = on
                s_on, e_on, _ = sel(on['KH_CO2'], on['KH_CO2_err'], on['KH_N2'], on['KH_N2_err'])
                row['S_ON'], row['S_ON_err'] = s_on, e_on
                if row.get('KH_CO2') and row.get('KH_N2'):
                    s_off, e_off, rel = sel(row['KH_CO2'], row['KH_CO2_err'], row['KH_N2'], row['KH_N2_err'])
                    row['S_OFF'], row['S_OFF_err'] = s_off, e_off
                    row['lnS_OFF'], row['lnS_OFF_err'] = math.log(s_off), rel
                    row['lnS_ON'] = math.log(s_on)
                    row['ln_ratio'] = math.log(s_off) / math.log(s_on)
                    row['dlnKH_CO2_off_minus_on'] = math.log(row['KH_CO2'] / on['KH_CO2'])
                    row['dlnKH_N2_off_minus_on'] = math.log(row['KH_N2'] / on['KH_N2'])
                    row['status'] = 'ok'
                elif len(g) == 2:
                    row['status'] = f"실패({g['CO2'][1]}/{g['N2'][1]})"
                rows.append(row)
            write(rows)
    seeds = [v[3] for g in got.values() for v in g.values() if v[3] is not None]
    dup = len(seeds) - len(set(seeds))
    write(rows, f'seed {len(seeds)}개 · 겹침 {dup}건 · 벽시계 {(time.time() - t0) / 60:.1f} min')
    print(f'\n저장 {OUT} — ok {sum(r["status"] == "ok" for r in rows)}/{len(rows)} · seed 겹침 {dup}건 · 벽시계 {(time.time() - t0) / 60:.1f} min', flush=True)
    return 0 if all(r['status'] == 'ok' for r in rows) and dup == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
