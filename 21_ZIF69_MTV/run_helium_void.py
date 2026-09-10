"""T-NF-0v — **헬륨 Widom 공극률**, 외부 3 + 우리 6 골격, 반복 2.

등록: `TNF0V_REGISTRATION_20260911.md` (2026-09-11 04:34, **자료 0건**).

`TNF0K_VERDICT §5-1·§5-2` 의 이상 둘이 *"K_H 는 질량당이라 세공 부피가 섞인다"* 로 끝났습니다.
부피를 나누면 둘이 갈립니다. 정규화 자를 **K_H 와 같은 코드·셀·힘장**으로 재는 것이 요점이라
Zeo++ 대신 RASPA 헬륨 Widom 을 씁니다(기존 Zeo++ AV 는 **CO₂ 탐침 1.65 Å** 라 물에 안 맞습니다).

**러너를 안 고칩니다.** `run_tb2_water_kh.py` 를 import 해 성분·경로·대상만 바꿉니다.

⚠️ **`molecules/TraPPE/helium.def` 를 쓰지만 TraPPE 가 아닙니다.** LJ 는 `UFF_MOF` 의
`He lennard-jones 10.9 2.64` 에서 옵니다. 문서에 "TraPPE 헬륨" 이라 쓰면 틀립니다.

⚠️ **접두 일치 관문**: `Hw` 가 `H_`(22.1417) 를 물려받은 사고가 있었습니다. `He` 는 자기 항이
있지만 **가정하지 않고 출력에서 `He - He` 쌍을 읽어** 10.9/2.64 인지 확인합니다.

사용:  HEV_WORKERS=6 nice -n 5 ~/miniconda3/envs/czeromof/bin/python run_helium_void.py
"""
import json
import os
import re
import shutil
import socket
import subprocess
import sys
import time
from multiprocessing import Pool

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import run_tb2_water_kh as T                                  # noqa: E402
from ff_gate import md5_gate                                  # noqa: E402

EXT = ['zif93', 'zif71', 'zif90']                             # LPT: 큰 것부터
OURS = ['saIm100', 'saIm050', 'nbIm050', 'mbIm050', 'base', 'mbIm025']
NAMES = EXT + OURS
N_REP = int(os.environ.get('HEV_NREP', 2))
RUNS_ROOT = os.path.join(HERE, 'hev_runs')
OUT = os.path.join(HERE, 'v3w_helium_void')
STAGGER = 3
WORKERS = int(os.environ.get('HEV_WORKERS', 6))

HE_DEF = os.path.expanduser(
    '~/RASPA/simulations/share/raspa/molecules/TraPPE/helium.def')
HE_EPS, HE_SIG = 10.9, 2.64            # UFF_MOF 40행. 출력과 대조할 값


def runs_dir(rep):
    return os.path.join(RUNS_ROOT, f'r{rep}')


def read_rosenbluth(path, comp='helium'):
    """`[helium] Average Widom Rosenbluth-weight:  X +/- Y [-]` — **성분 이름으로**.

    `run_tb2_water_kh.read_kh` 와 같은 규율: 다중 일치는 조용히 뒤엣것이 이기므로 **거부**합니다.
    """
    hits = []
    pat = re.compile(r'\[\s*(\S+?)\s*\]\s*Average Widom Rosenbluth-weight:\s*'
                     r'([0-9.eE+-]+)\s*\+/-\s*([0-9.eE+-]+)')
    for i, ln in enumerate(open(path, encoding='utf-8', errors='ignore'), 1):
        m = pat.search(ln)
        if m:
            hits.append((i, m.group(1), float(m.group(2)), float(m.group(3))))
    mine = [h for h in hits if h[1] == comp]
    if not mine:
        return None, None, f"성분 '{comp}' 의 Rosenbluth 무게 없음 (찾은 것: {sorted({h[1] for h in hits})})"
    if len(mine) > 1:
        return None, None, f"성분 '{comp}' 일치 {len(mine)}개 — 행 {[h[0] for h in mine]}"
    return mine[0][2], mine[0][3], None


def read_he_pair(path):
    """머리말의 `He - He` 쌍. **쌍 이름으로** 봅니다 — 값을 grep 하면 안 됩니다."""
    for ln in open(path, encoding='utf-8', errors='ignore'):
        if re.match(r'\s*He\s*-\s*He\s*\[', ln):
            g = re.search(r'p_0/k_B:\s*([0-9.]+).*?p_1:\s*([0-9.]+)', ln)
            if g:
                eps, sig = float(g.group(1)), float(g.group(2))
                ok = abs(eps - HE_EPS) < 0.05 and abs(sig - HE_SIG) < 0.01
                return {'eps': eps, 'sigma': sig, 'ok': ok, 'line': ln.strip()}
            return {'ok': False, 'line': ln.strip()}
    return {'ok': False, 'line': None, 'note': 'He - He 쌍이 머리말에 없음'}


def cell_props(cif):
    """결정 밀도 ρ [g/cm³] 와 셀 부피 — CIF 원자 질량 합 / 셀 부피."""
    from ase.io import read
    import numpy as np
    a = read(cif)
    V = abs(np.linalg.det(np.asarray(a.get_cell())))           # Å³
    m = float(sum(a.get_masses()))                             # amu
    rho = m / V * 1.66053906660                                # amu/Å³ -> g/cm³
    return {'cell_volume_A3': V, 'cell_mass_amu': m, 'density_g_cm3': rho,
            'n_atoms': len(a)}


def one(arg):
    i, name, rep = arg
    time.sleep(i * STAGGER)
    runs = runs_dir(rep)
    cif = os.path.join(T.CHARGED, name + '_DDEC6.cif')
    fw = name + '_DDEC6'
    d = os.path.join(runs, 'widom_he_' + name)
    os.makedirs(d, exist_ok=True)
    shutil.copy(cif, os.path.join(d, fw + '.cif'))
    shutil.copy(HE_DEF, os.path.join(d, 'helium.def'))
    na, nb, nc = T.unit_cells(cif)
    open(os.path.join(d, 'simulation.input'), 'w').write(f"""SimulationType                MonteCarlo
NumberOfCycles                {T.CYCLES}
NumberOfInitializationCycles  {T.INIT}
PrintEvery                    {T.CYCLES // 10}
RestartFile                   no

Forcefield                    UFF_MOF
CutOff                        {T.CUTOFF}
UseChargesFromCIFFile         yes
ChargeMethod                  Ewald
EwaldPrecision                1e-6

Framework 0
FrameworkName                 {fw}
UnitCells                     {na} {nb} {nc}
ExternalTemperature           {T.TEMP}
ExternalPressure              {T.PRESS}

Component 0 MoleculeName              helium
            MoleculeDefinition        TraPPE
            WidomProbability          1.0
            CreateNumberOfMolecules   0
""")
    subprocess.run([T.SIMULATE, 'simulation.input'], cwd=d,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False)
    od = os.path.join(d, 'Output', 'System_0')
    outs = sorted(os.path.join(od, x) for x in os.listdir(od)
                  if x.endswith('.data')) if os.path.isdir(od) else []
    r = {'name': name, 'rep': rep, 'unit_cells': [na, nb, nc], **cell_props(cif)}
    if len(outs) != 1:
        return {**r, 'phi': None, 'ok': False,
                'error': f'출력 .data 가 {len(outs)}개 — 1개여야 합니다'}
    phi, ephi, err = read_rosenbluth(outs[0])
    he = read_he_pair(outs[0])
    seed = None
    for ln in open(outs[0], encoding='utf-8', errors='ignore'):
        m = re.match(r'\s*Random number seed:\s*(\d+)', ln)
        if m:
            seed = int(m.group(1)); break
    if not he['ok']:
        err = (err or '') + f" | **He-He 쌍 관문 실패**: {he.get('line')}"
    return {**r, 'phi': phi, 'phi_err': ephi, 'he_pair': he, 'raspa_seed': seed,
            'ok': phi is not None and he['ok'], **({'error': err} if err else {})}


def main():
    ok, _ = md5_gate()
    if not ok:
        print('!! 힘장 파일 관문 실패. 중단.', flush=True); return 2
    if not os.path.exists(HE_DEF):
        print(f'!! helium.def 없음: {HE_DEF}', flush=True); return 3
    for n in NAMES:
        p = os.path.join(T.CHARGED, n + '_DDEC6.cif')
        if not os.path.exists(p):
            print(f'!! CIF 없음: {p}', flush=True); return 3
    # RASPA 가 돌고 있으면 착수 안 함 (자원 규칙)
    if subprocess.run(['pgrep', '-x', 'simulate'], capture_output=True).returncode == 0:
        print('!! `simulate` 가 이미 돌고 있습니다. 중단.', flush=True); return 4
    os.makedirs(OUT, exist_ok=True)
    jobs = [(i, n, rep) for i, (n, rep) in
            enumerate((n, rep) for n in NAMES for rep in range(1, N_REP + 1))]
    print(f'T-NF-0v 헬륨 공극률 — {len(NAMES)}구조 x 반복 {N_REP} = {len(jobs)}건, '
          f'워커 {WORKERS}, {STAGGER}초 어긋내기', flush=True)
    print(f'  자(T-NF-0k 와 동일): 사이클 {T.CYCLES}/{T.INIT}, UFF_MOF, 컷오프 {T.CUTOFF}, '
          f'{T.TEMP} K\n  He LJ 대조값: eps {HE_EPS} / sigma {HE_SIG} (UFF_MOF 40행)', flush=True)
    rows = []
    with Pool(WORKERS) as p:
        for r in p.imap_unordered(one, jobs, chunksize=1):
            rows.append(r)
            print(f"  [{'ok' if r['ok'] else '실패'}] {r['name']:9s} r{r['rep']}  "
                  f"phi {r['phi']}  rho {r['density_g_cm3']:.4f}  씨앗 {r.get('raspa_seed')}"
                  + (f"  !! {r.get('error')}" if r.get('error') else ''), flush=True)
    collide = {n: s for n in NAMES
               if len(set(s := [x['raspa_seed'] for x in rows if x['name'] == n])) != len(s)}
    f = os.path.join(OUT, f'helium_void_{socket.gethostname().lower()}.json')
    json.dump({'test': 'T-NF-0v', 'registration': 'TNF0V_REGISTRATION_20260911.md',
               'tag': socket.gethostname().lower(),
               'forcefield': 'UFF_MOF+HwLw_none_20260906', 'ff_md5': T.FF_MD5,
               'NumberOfInitializationCycles': T.INIT, 'NumberOfCycles': T.CYCLES,
               'temperature_K': T.TEMP, 'cutoff_A': T.CUTOFF,
               'he_lj_reference': {'eps_K': HE_EPS, 'sigma_A': HE_SIG,
                                   'source': 'UFF_MOF force_field_mixing_rules.def 40행'},
               'note': ('헬륨 Widom Rosenbluth 무게 = 공극률. helium.def 경로가 TraPPE 지만 '
                        'LJ 는 UFF_MOF 에서 옵니다 — "TraPPE 헬륨" 이라 쓰면 틀립니다. '
                        '정규화 대상은 v3w_water_kh_ext + water_kh_ALLw_hkhome_seedfixed.'),
               'seed_collision': collide or None,
               'rows': sorted(rows, key=lambda x: (x['name'], x['rep']))},
              open(f, 'w'), ensure_ascii=False, indent=2)
    nok = sum(1 for r in rows if r['ok'])
    print(f"\n[OK] {nok}/{len(jobs)} -> {f}", flush=True)
    print(f"  씨앗: {'**충돌 ' + str(collide) + '**' if collide else '구조 안에서 전부 다름'}",
          flush=True)
    return 0 if nok == len(jobs) else 1


if __name__ == '__main__':
    sys.exit(main())
