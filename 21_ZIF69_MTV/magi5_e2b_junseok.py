# -*- coding: utf-8 -*-
"""MAGI-005 E-2b (Junseok) — Co(p-Me₂-bdp) `2016[Co][pts]3[ASR]5` BlockPockets S(r). `ASSIGN_MAGI5B_20260925.md` §E-2b.

[0단계] 통과(02:11, `magi5_e2b_runs/step0_result.json`) — RASPA 는 cwd 의 `<FrameworkName>.block` 을 읽는다.
        share `structures/block/` 은 이 기기에 없으므로 환경 변경 없음.
[차례] ① E-3b 드라이버가 끝나고 simulate 0 이 될 때까지 기다린다 — **Zeo++ 와 RASPA 동시 금지**(CLAUDE.md §5·§9).
       ② Zeo++ `network -ha -res` (PLD 재확인) + `-ha -block r 50000` (r = 1.50 · 1.65 · 1.82 · 2.00 Å), 반경마다 새 폴더.
       ③ 반경마다 CO₂·N₂ Widom — 8작업 · 워커 8 · 15 s 어긋냄(씨앗 = 착수 초).
[자]   입력은 `run_aryl_gcmc.run_one` 의 Widom 틀 **그대로** + 성분 절 두 줄(`BlockPockets yes` · `BlockPocketsFileName`).
       공용 러너는 고치지 않는다(run_one 은 입력을 스스로 쓰므로 부를 수 없음 — 틀을 옮기고 parse/finished/unit_cells 는 import).
[회수 관문] 세 가지 다: (a) stderr 에 "'Blocking-pocket' file not found" 없음 (b) .data "Number of pockets blocked in a unitcell"
       = (파일의 구 수) × (단위셀 수) — **등식** (c) `Simulation finished`.
       ⚠ 0단계 음성 대조: 파일이 없어도 .data 는 "Pockets are blocked for this component" 를 찍고 N = 0 만 다르다.
         그래서 "blocked" 줄만으로는 조용한 실패를 못 거른다. 구 0개(막을 주머니 없음)도 (a)+(b) 로 가려진다.
[판정] 종합자 몫 — 여기서는 수(K_H ± · S ± · 정식 짝 · 113.4 와의 단위 거리)만.
"""
import datetime
import glob
import json
import math
import os
import re
import shutil
import subprocess
import sys
import time
import zipfile
from concurrent.futures import ProcessPoolExecutor, as_completed

HERE = '/home/mangwon/mof_project/21_ZIF69_MTV'
sys.path.insert(0, HERE)
import run_aryl_gcmc as rg   # noqa: E402
import ff_gate               # noqa: E402

NAME = '2016_Co__pts_3_ASR_5'
KEY = '2016[Co][pts]3[ASR]5'
BASE = os.path.join(HERE, 'magi5_e2b_runs')
OUT = os.path.join(HERE, 'results_magi5_e2b_blockpockets_junseok.json')
SIM = '/home/mangwon/miniconda3/envs/czeromof/bin/simulate'
ZEO = '/home/mangwon/miniconda3/envs/czeromof/bin/network'
RADII = (1.50, 1.65, 1.82, 2.00)
NSAMP = 50000
GASES = ('CO2', 'N2')
STAGGER = 15.0
CANON = {'CO2': 1.65, 'N2': 1.82}
S_REF_NOMINAL = 113.4
NOT_FOUND = "'Blocking-pocket' file not found"


def log(msg):
    print(msg, flush=True)


def cif_bytes():
    return zipfile.ZipFile(os.path.join(HERE, 'core_pop_cifs.zip')).read(NAME + '.cif')


def e3b_running():
    ps = subprocess.run(['ps', '-eo', 'args'], capture_output=True, text=True).stdout
    return any('.junseok_chain/magi5_e3b.py' in ln for ln in ps.splitlines())


def n_simulate():
    p = subprocess.run(['pgrep', '-xc', 'simulate'], capture_output=True, text=True)
    return int(p.stdout.strip() or 0)


def wait_clear():
    said = False
    while e3b_running() or n_simulate() > 0:
        if not said:
            log(f'  대기 — E-3b 드라이버 {e3b_running()} · simulate {n_simulate()} (Zeo++ 와 RASPA 동시 금지)  {time.strftime("%H:%M:%S")}')
            said = True
        time.sleep(60)
    log(f'  비었음 — Zeo++ 착수  {time.strftime("%H:%M:%S")}')


def zeo_all():
    zd = os.path.join(BASE, 'zeo')
    os.makedirs(zd)
    open(os.path.join(zd, NAME + '.cif'), 'wb').write(cif_bytes())
    t0 = time.time()
    p = subprocess.run([ZEO, '-ha', '-res', NAME + '.res', NAME + '.cif'], cwd=zd, capture_output=True, text=True, timeout=1800)
    geo = None
    try:
        raw = open(os.path.join(zd, NAME + '.res')).read().split()      # "<파일> Di Df Dif"
        geo = {'Di': float(raw[1]), 'Df': float(raw[2]), 'Dif': float(raw[3]), 'raw': ' '.join(raw)}
        log(f'  Zeo++ -ha -res  원문 "{geo["raw"]}" → Di {geo["Di"]:.3f} · Df(PLD) {geo["Df"]:.3f} · Dif {geo["Dif"]:.3f} Å'
            f'  (CoRE PLD 3.571 · LCD 4.233)  {time.time() - t0:.0f} s')
    except (OSError, IndexError, ValueError) as e:
        log(f'!! Zeo++ -res 실패 rc={p.returncode} · {e} · {p.stderr.strip()[:200]} — 기하 없이 계속')
    blocks = {}
    for r in RADII:
        d = os.path.join(zd, f'r{r:.2f}')
        os.makedirs(d)
        open(os.path.join(d, NAME + '.cif'), 'wb').write(cif_bytes())
        t0 = time.time()
        p = subprocess.run([ZEO, '-ha', '-block', f'{r:.2f}', str(NSAMP), NAME + '.cif'], cwd=d,
                           capture_output=True, text=True, timeout=3600)
        fs = glob.glob(os.path.join(d, '*.block'))
        if p.returncode != 0 or not fs:
            log(f'!! Zeo++ -block {r:.2f} 실패 rc={p.returncode} · {p.stderr.strip()[:200]}')
            blocks[r] = None
            continue
        txt = open(fs[0]).read()
        lines = [ln.split() for ln in txt.strip().splitlines()]
        n = int(lines[0][0])
        sph = [[float(x) for x in ln[:4]] for ln in lines[1:1 + n]]
        assert len(sph) == n, (r, n, len(sph))
        cmax = max((abs(c) for s in sph for c in s[:3]), default=0.0)
        if cmax > 1.5:
            log(f'!! r={r:.2f} 구 좌표 최대 {cmax:.2f} — 분율 좌표가 아닌 듯(RASPA 는 분율로 읽음) · 이 반경 건너뜀')
            blocks[r] = None
            continue
        rads = [s[3] for s in sph]
        blocks[r] = {'text': txt, 'n_spheres': n, 'file': os.path.relpath(fs[0], HERE),
                     'sphere_radius_min': min(rads) if rads else None, 'sphere_radius_max': max(rads) if rads else None,
                     'zeo_seconds': round(time.time() - t0, 1)}
        log(f'  Zeo++ -ha -block {r:.2f} {NSAMP}  구 {n}개 · 반지름 {blocks[r]["sphere_radius_min"]}~{blocks[r]["sphere_radius_max"]} Å · '
            f'좌표 최대 {cmax:.3f}  {time.time() - t0:.0f} s')
    return geo, blocks


def widom(args):
    r, gas, btxt, nsph = args
    d = os.path.join(BASE, f'r{r:.2f}', f'widom_{gas}_{NAME}')
    if os.path.exists(d):
        return r, gas, {'status': '폴더있음(이어받기 안 함)'}
    os.makedirs(d)
    cif = os.path.join(d, NAME + '.cif')
    open(cif, 'wb').write(cif_bytes())
    open(os.path.join(d, NAME + '.block'), 'w').write(btxt)
    na, nb, nc = rg.unit_cells(rg.read(cif))
    cyc, init, press = rg.WIDOM_CYCLES, rg.WIDOM_INIT, 1e-5
    with open(os.path.join(d, 'simulation.input'), 'w') as f:
        f.write(f"""SimulationType                MonteCarlo
NumberOfCycles                {cyc}
NumberOfInitializationCycles  {init}
PrintEvery                    {cyc}
RestartFile                   no

Forcefield                    UFF_MOF
CutOff                        {rg.CUTOFF}
UseChargesFromCIFFile         yes
ChargeMethod                  Ewald
EwaldPrecision                1e-6

Framework 0
FrameworkName                 {NAME}
UnitCells                     {na} {nb} {nc}
ExternalTemperature           {rg.TEMP}
ExternalPressure              {press}

Component 0 MoleculeName              {gas}
            MoleculeDefinition        TraPPE
            BlockPockets              yes
            BlockPocketsFileName      {NAME}
            WidomProbability          1.0
            CreateNumberOfMolecules   0
""")
    t0 = time.time()
    with open(os.path.join(d, 'stderr.txt'), 'w') as ef:
        try:
            subprocess.run([SIM, 'simulation.input'], cwd=d, stdout=subprocess.DEVNULL, stderr=ef, timeout=28800, check=False)
        except subprocess.TimeoutExpired:
            return r, gas, {'status': 'timeout'}
    row = {'minutes': round((time.time() - t0) / 60, 1), 'unit_cells': [na, nb, nc], 'n_spheres_per_uc': nsph,
           'n_expected': nsph * na * nb * nc}
    outs = glob.glob(os.path.join(d, 'Output', 'System_0', '*.data'))
    if not outs:
        row['status'] = 'no-output'
        return r, gas, row
    txt = open(outs[0], encoding='utf-8', errors='ignore').read()
    err = open(os.path.join(d, 'stderr.txt'), encoding='utf-8', errors='ignore').read()
    m = re.search(r'Number of pockets blocked in a unitcell:\s*(\d+)', txt)
    s = re.search(r'Random number seed:\s*(\d+)', txt)
    row.update(data=os.path.relpath(outs[0], HERE), seed=int(s.group(1)) if s else None,
               n_blocked_reported=int(m.group(1)) if m else None,
               pockets_blocked_line='Pockets are blocked for this component' in txt,
               stderr_not_found=NOT_FOUND in err, marker_finished=rg.finished(outs[0]))
    kh, ekh, u, eu, _l, _e = rg.parse(outs[0])
    row.update(KH=kh, KH_err=ekh, dU=u, dU_err=eu)
    if row['stderr_not_found'] or row['n_blocked_reported'] != row['n_expected'] or not row['pockets_blocked_line']:
        row['status'] = 'no-block'
    elif not row['marker_finished']:
        row['status'] = '미완주'
    elif kh is None:
        row['status'] = '값없음'
    else:
        row['status'] = 'ok'
    for sub in ('VTK', 'Movies', 'Restart'):
        shutil.rmtree(os.path.join(d, sub), ignore_errors=True)
    return r, gas, row


def ratio(c, n):
    """S = K_CO2/K_N2 · ± 는 두 95 % 폭을 제곱합으로 전파(근사). K_N2 = 0 이면 None."""
    if not c or not n or c.get('KH') is None or n.get('KH') is None or n['KH'] <= 0:
        return None, None
    S = c['KH'] / n['KH']
    e = S * math.hypot((c['KH_err'] or 0) / c['KH'] if c['KH'] else 0, (n['KH_err'] or 0) / n['KH'])
    return S, e


def main():
    ok, m = ff_gate.md5_gate(verbose=True)
    if not ok or m != ff_gate.FF_MD5:
        log(f'!! 힘장 관문 실패 ({m}) — 착수 안 함')
        return 3
    if os.path.exists(OUT) or os.path.exists(os.path.join(BASE, 'zeo')) or glob.glob(os.path.join(BASE, 'r*')):
        log('!! 이전 E-2b 산출이 있음 — 이어받지 않음, 중단')
        return 1
    step0 = json.load(open(os.path.join(BASE, 'step0_result.json'), encoding='utf-8'))
    if not step0['result'].startswith('cwd 에서 읽음'):
        log('!! 0단계가 통과가 아님 — 멈춤(환경 변경 = 사용자 결정)')
        return 1
    ref = next(r for r in json.load(open(os.path.join(HERE, 'core_pop_results_laptop2.json'), encoding='utf-8'))['rows']
               if r['file'] == NAME + '.cif')
    s_ref, e_ref = ratio({'KH': ref['KH_CO2'], 'KH_err': ref['KH_CO2_err']}, {'KH': ref['KH_N2'], 'KH_err': ref['KH_N2_err']})
    log(f'E-2b  {KEY} · 반경 {RADII} · 표본 {NSAMP} · 기체 {GASES} · 참조(차단 없음, laptop2) S {s_ref:.2f} ± {e_ref:.2f}')
    wait_clear()
    geo, blocks = zeo_all()
    if n_simulate() > 0:
        log('!! Zeo++ 뒤 simulate 가 이미 돎 — 누가 띄웠는지 확인 필요(계속 진행)')
    jobs = [(r, g, blocks[r]['text'], blocks[r]['n_spheres']) for r in RADII if blocks.get(r) for g in GASES]
    res = {}

    def write(final=False):
        rows = []
        for r in RADII:
            c, n = res.get((r, 'CO2')), res.get((r, 'N2'))
            S, eS = ratio(c, n) if (c and n and c.get('status') == 'ok' and n.get('status') == 'ok') else (None, None)
            rows.append({'probe_radius_A': r, 'zeo_block': {k: v for k, v in (blocks.get(r) or {}).items() if k != 'text'} or None,
                         'CO2': c or {'status': 'pending' if blocks.get(r) else 'zeo 실패'},
                         'N2': n or {'status': 'pending' if blocks.get(r) else 'zeo 실패'},
                         'S': S, 'S_err': eS,
                         'S_note': ('K_H(N₂) = 0 → S 발산(차단이 N₂ 삽입을 전부 막음)'
                                    if n and n.get('status') == 'ok' and n.get('KH') == 0 else None)})
        c, n = res.get((CANON['CO2'], 'CO2')), res.get((CANON['N2'], 'N2'))
        Sc, eSc = ratio(c, n) if (c and n and c.get('status') == 'ok' and n.get('status') == 'ok') else (None, None)
        canon = {'pair': 'CO₂@1.65 + N₂@1.82', 'S': Sc, 'S_err': eSc,
                 'S_over_ref': round(Sc / s_ref, 3) if Sc else None,
                 'units_from_ref': round(abs(Sc - s_ref) / max(eSc, e_ref), 2) if Sc else None,
                 'note': ('K_H(N₂@1.82) = 0 → S 발산' if n and n.get('status') == 'ok' and n.get('KH') == 0 else None)}
        out = {'test': 'MAGI-005 E-2b — Co(p-Me₂-bdp) ASR_5 BlockPockets S(r) (맹점 ① 의 크기)',
               'assign': 'ASSIGN_MAGI5B_20260925.md §E-2b', 'machine': 'junseok', 'final': final, 'key': KEY,
               'cif': f'core_pop_cifs.zip:{NAME}.cif (CoRE PACMAN DDEC6)', 'step0': 'magi5_e2b_runs/step0_result.json (cwd 읽기 통과)',
               'protocol': {'widom_init': rg.WIDOM_INIT, 'widom_cycles': rg.WIDOM_CYCLES, 'forcefield': 'UFF_MOF', 'ff_md5': m,
                            'cutoff': rg.CUTOFF, 'temp_K': rg.TEMP, 'ewald': '1e-6', 'charges': 'UseChargesFromCIFFile yes',
                            'supercell': 'run_aryl_gcmc.unit_cells() 규칙', 'input': 'run_one Widom 틀 + BlockPockets yes · BlockPocketsFileName',
                            'zeo': f'network -ha -block r {NSAMP} (반경마다 새 폴더) · -ha -res'},
               'gate': "stderr 에 file-not-found 없음 · .data N = 구 수 × 단위셀 수(등식) · Simulation finished",
               'zeo_res': geo,
               'reference_unblocked': {'source': 'core_pop_results_laptop2.json (laptop2 측정)', 'KH_CO2': ref['KH_CO2'],
                                       'KH_CO2_err': ref['KH_CO2_err'], 'KH_N2': ref['KH_N2'], 'KH_N2_err': ref['KH_N2_err'],
                                       'S': s_ref, 'S_err': e_ref},
               'registered': 'S_정식 ≥ 2 × 113.4 · 기각: S_정식 이 113.4 의 1.5 단위 안 — 판정문은 종합자',
               'S_err_note': '± 는 두 RASPA 95 % 폭을 제곱합으로 전파(근사)',
               'rows': rows, 'canonical': canon}
        tmp = OUT + '.tmp'
        json.dump(out, open(tmp, 'w', encoding='utf-8'), indent=2, ensure_ascii=False)
        os.replace(tmp, OUT)

    write()
    log(f'  Widom {len(jobs)}작업 · 워커 {len(jobs)} · 착수 간격 {STAGGER:g} s')
    with ProcessPoolExecutor(max_workers=max(1, len(jobs))) as ex:
        futs = []
        for i, j in enumerate(jobs):
            if i:
                time.sleep(STAGGER)
            futs.append(ex.submit(widom, j))
            log(f'  착수 r={j[0]:.2f} {j[1]}  {datetime.datetime.now():%H:%M:%S}')
        for fu in as_completed(futs):
            r, g, row = fu.result()
            res[(r, g)] = row
            write()
            log(f'  [{row.get("status"):>6}] r={r:.2f} {g:<3} K_H {row.get("KH")} ± {row.get("KH_err")} · N {row.get("n_blocked_reported")}'
                f'/{row.get("n_expected")} · 표지 {row.get("marker_finished")} · 씨앗 {row.get("seed")} · {row.get("minutes")} 분')
    write(final=True)
    log(f'\n저장 {OUT}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
