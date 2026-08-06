"""ZIF-69 −SO₃H 계열의 CO₂/H₂O 경쟁 흡착 — 이 노선의 존폐 조건.

[왜 이게 결정적인가]
    ZIF-69 + SO₃H 100% 가 Q_st 31.07, 선택도 102, 로딩 2.16 으로 목표권에 처음
    들어왔다. 그런데 술폰산은 강한 흡습성 관능기이고, 여기서는 벤조환 24개에
    **전부** 달려 있다.

    ZIF-8 계열(19_WaterCompetition)에서 물 흡수량이 −SO₃H 밀도에 거의 선형으로
    따라갔다: 0% -> 0.017~0.031, 25% -> 0.481, 50% -> 1.262~1.854 mol/kg.
    ZIF-69 의 100% 밀도면 외삽으로 3~4 mol/kg 이다.

    그리고 ZIF-8 이 살아남은 해석은 **"11.4 A 공동이 넓어서 물과 CO2 가 자리를
    나눠 썼다"** 였다(Part 3). ZIF-69 는 공동이 7.2 A 라 그 여유가 없다.
    즉 Part 3 의 해석이 옳다면 여기서는 무너져야 한다. 이 계산이 그 시험이다.

[물 모델 — MIGRATION.md 3-4]
    RASPA 배포본 TraPPE/water.def 는 3원자(Ow,Hw,Hw)인데 UFF_MOF 의 물 파라미터는
    TIP5P-Ew 용이다. 음전하가 전부 더미 사이트 Lw 에 있어서 3원자 파일을 쓰면
    물 한 분자가 알짜전하 +0.482 를 갖고 Ewald 합이 무의미해진다.
    **19_WaterCompetition/water.def(5사이트)를 실행 디렉터리로 복사해서 쓴다.**
    정상이면 출력에 'Component has a net charge of 0.000000' 이 찍힌다.
"""
import glob
import json
import math
import os
import re
import shutil
import subprocess
import sys
from concurrent.futures import ProcessPoolExecutor

import numpy as np
from ase.io import read

HERE = os.path.dirname(os.path.abspath(__file__))
CHARGED = os.path.join(HERE, 'charged')
RUNS = os.path.join(HERE, 'water_runs')
# 5사이트 정의를 재사용한다(중복 사본을 만들면 한쪽만 고쳐질 위험이 있다).
WATER_DEF = os.path.join(HERE, '..', '19_WaterCompetition', 'water.def')

SIMULATE = shutil.which('simulate') or os.path.expanduser(
    '~/miniconda3/envs/czeromof/bin/simulate')

TEMP = 298.0
CUTOFF = 12.0
P_CO2 = 0.15e5
P_SAT_298 = 3169.0
RH_LIST = [0.0, 0.25, 0.50, 0.90]
CYCLES, INIT = 15000, 5000
# [2026-08-06] 12 -> 8. **메모리 때문이 아니라 물리 코어 수 때문이다.**
#
# 처음에는 이 스크립트가 15 GB 머신에서 OOM 을 낸 줄 알았다:
#     Out of memory: Killed process (python) anon-rss:14419068kB
# 그런데 실제로 재보니 RASPA 한 프로세스는 **471 MB** 밖에 안 쓴다(ZIF-69,
# 4800원자 슈퍼셀, 이원 GCMC 기준). 12개를 띄워도 5.6 GB 라 한도와 거리가 멀다.
# 14.4 GB 를 쓴 건 구조 감사 루프의 ASE get_all_distances(mic=True) 였고,
# 이 계산은 그 여파(systemd 불안정)에 휩쓸린 피해자였다.
#
# 그래서 8 로 두는 근거는 메모리가 아니라 **물리 코어가 8개**라는 것이다.
# RASPA 는 작업당 단일 스레드 CPU 바운드라 물리 코어 수가 처리량 상한이고,
# 그 이상 띄우면 문맥 전환만 늘어난다.
#
# 재확인 명령:
#     ps -eo rss,args --sort=-rss | grep simulate | head -3
MAX_WORKERS = 8

TARGETS = [
    ('base',     'ZIF-69 원본 (Cl, 대조군)'),
    ('saIm025',  'SO3H 25%'),
    ('saIm050',  'SO3H 50%'),
    ('saIm075',  'SO3H 75%'),
    ('saIm100',  'SO3H 100% (목표권 진입 조성)'),
]


def unit_cells(atoms, cutoff=CUTOFF):
    cell = atoms.get_cell()
    vol = abs(np.linalg.det(cell))
    reps = []
    for i in range(3):
        j, k = (i + 1) % 3, (i + 2) % 3
        width = vol / np.linalg.norm(np.cross(cell[j], cell[k]))
        reps.append(max(1, int(np.ceil(2.0 * cutoff / width))))
    return reps


def parse_components(path):
    """성분별 (값, 오차). RASPA 출력은 Component 블록마다 같은 문구를 반복하므로
    어느 성분 블록인지 추적해야 한다."""
    out = {}
    cur = None
    for line in open(path, encoding='utf-8', errors='ignore'):
        m = re.search(r'Component\s+(\d+)\s+\[(\w+)\]', line)
        if m:
            cur = m.group(2)
        if cur and 'Average loading absolute [mol/kg framework]' in line:
            v = re.search(r':?\s*([0-9.eE+-]+)\s*\+/-\s*([0-9.eE+-]+)', line)
            if v and cur not in out:
                out[cur] = (float(v.group(1)), float(v.group(2)))
    return out


def net_charge_ok(path):
    """물 정의가 5사이트로 제대로 잡혔는지 확인 (MIGRATION.md 3-4)."""
    for line in open(path, encoding='utf-8', errors='ignore'):
        if 'net charge of' in line:
            m = re.search(r'net charge of\s*([0-9.eE+-]+)', line)
            if m and abs(float(m.group(1))) > 1e-4:
                return False
    return True


def finished(path):
    """완주 판정. 파일 존재만으로는 안 된다 — 중간에 죽은 실행도 30 MB 를 남긴다."""
    try:
        return 'Average loading absolute [mol/kg framework]' in open(
            path, encoding='utf-8', errors='ignore').read()
    except OSError:
        return False


def run_one(job):
    name, rh = job
    cif = os.path.join(CHARGED, name + '_DDEC6.cif')
    fw = name + '_DDEC6'
    d = os.path.join(RUNS, f'rh{int(rh*100):02d}_{name}')

    # [2026-08-06] 작업 단위 이어받기.
    #
    # 원래는 water_results.json 만 보고 건너뛰었는데, 그 파일은 20작업이 **전부**
    # 끝나야 쓰인다. 즉 19개를 끝내고 죽으면 이어받을 지점이 0 이었다. 실제로
    # 그 일이 났다 — 데스크탑이 절전에 들어갔다가 깨어났고, 그때 살아남은 완주
    # 작업 2개도 재시작하면 버려질 뻔했다.
    #
    # 한 작업이 77분 이상이라 재계산 비용이 크므로, 출력 파일에 최종 로딩 줄이
    # 있으면 그대로 읽어 쓴다.
    done = glob.glob(os.path.join(d, 'Output', 'System_0', '*.data'))
    if done and finished(done[0]) and net_charge_ok(done[0]):
        return name, rh, parse_components(done[0]), 'cached'

    os.makedirs(d, exist_ok=True)
    shutil.copy(cif, os.path.join(d, fw + '.cif'))
    shutil.copy(WATER_DEF, os.path.join(d, 'water.def'))
    na, nb, nc = unit_cells(read(cif))

    p_h2o = P_SAT_298 * rh
    p_tot = P_CO2 + p_h2o
    x_co2, x_h2o = P_CO2 / p_tot, p_h2o / p_tot

    moves = ('            TranslationProbability    0.5\n'
             '            RotationProbability       0.3\n'
             '            ReinsertionProbability    0.1\n'
             '            SwapProbability           1.0\n'
             '            CreateNumberOfMolecules   0\n')
    comp = f"""Component 0 MoleculeName              CO2
            MoleculeDefinition        TraPPE
            MolFraction               {x_co2:.6f}
{moves}"""
    if rh > 0:
        comp += f"""
Component 1 MoleculeName              water
            MoleculeDefinition        TraPPE
            MolFraction               {x_h2o:.6f}
{moves}"""

    with open(os.path.join(d, 'simulation.input'), 'w') as f:
        f.write(f"""SimulationType                MonteCarlo
NumberOfCycles                {CYCLES}
NumberOfInitializationCycles  {INIT}
PrintEvery                    {CYCLES}
RestartFile                   no

Forcefield                    UFF_MOF
CutOff                        {CUTOFF}
UseChargesFromCIFFile         yes
ChargeMethod                  Ewald
EwaldPrecision                1e-6

Framework 0
FrameworkName                 {fw}
UnitCells                     {na} {nb} {nc}
ExternalTemperature           {TEMP}
ExternalPressure              {p_tot:.4f}

{comp}""")
    # [2026-08-06] 8시간(28800) -> 72시간. **이 상수가 결과를 5개 날렸다.**
    #
    # 다른 스크립트에서 그대로 복사해 온 값인데, 저쪽은 단일 성분 CO2 GCMC 라
    # 8시간이 넉넉했다. 여기는 5사이트 물이 붙은 이원 GCMC 이고, 술폰산이 많을수록
    # 물 삽입 수용률이 떨어져 같은 15000 사이클이 몇 배로 길어진다. 실측:
    #     건조 무치환  77분
    #     습윤 saIm050 8시간 초과  <- 여기서부터 타임아웃에 걸려 죽었다
    #
    # 죽는 방식이 나빴다. subprocess.run 의 timeout 은 프로세스를 죽이고
    # TimeoutExpired 를 던지는데, 워커는 그걸 받아 다음 작업으로 넘어간다. 즉
    # **로그도 예외도 남지 않고 조용히 구멍만 남는다.** 감시 스크립트는 완주 수만
    # 세고 있었으므로 "느린 것"과 "죽은 것"이 구별되지 않았다.
    #
    # 실제로 rh50/rh90_saIm025 와 rh25/rh50/rh90_saIm050 다섯 개가 이렇게 사라졌고,
    # 그중 saIm050 습윤 계열은 통째로 비었다.
    try:
        subprocess.run([SIMULATE, 'simulation.input'], cwd=d,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                       timeout=259200, check=False)
    except subprocess.TimeoutExpired:
        print(f'  [타임아웃 72시간 초과] rh{int(rh*100):02d}_{name}', flush=True)
        return name, rh, None, 'timeout'
    outs = glob.glob(os.path.join(d, 'Output', 'System_0', '*.data'))
    if not outs:
        return name, rh, None, 'no-output'
    if not net_charge_ok(outs[0]):
        return name, rh, None, '물 알짜전하 != 0'
    res = parse_components(outs[0])
    for sub in ('VTK', 'Movies', 'Restart'):
        shutil.rmtree(os.path.join(d, sub), ignore_errors=True)
    return name, rh, res, 'ok'


def _star(a):
    return run_one(a)


def main():
    missing = [n for n, _ in TARGETS
               if not os.path.exists(os.path.join(CHARGED, n + '_DDEC6.cif'))]
    if missing:
        print('전하 구조 없음:', missing)
        return 1
    os.makedirs(RUNS, exist_ok=True)

    # 이어받기 — 이원 GCMC 는 한 작업이 길어 중단·재개가 실제로 생긴다.
    res = {}
    part = os.path.join(HERE, 'water_results.json')
    if os.path.exists(part):
        for r in json.load(open(part, encoding='utf-8')):
            d = {'CO2': (r['CO2_molkg'], r.get('CO2_err', 0.0))}
            if r['RH'] > 0:
                d['water'] = (r['H2O_molkg'], r.get('H2O_err', 0.0))
            res.setdefault(r['name'], {})[r['RH']] = d
        print(f'이어받기: 완료 {sum(len(v) for v in res.values())}개 건너뜀', flush=True)

    jobs = [(n, rh) for n, _ in TARGETS for rh in RH_LIST if rh not in res.get(n, {})]
    print(f'구조 {len(TARGETS)}개 x RH {len(RH_LIST)}단계 중 실행 {len(jobs)}개', flush=True)
    print(f'CO2 {P_CO2/1e5:.2f} bar 고정, 298 K, TIP5P-Ew(5사이트), {CYCLES} 사이클\n',
          flush=True)

    with ProcessPoolExecutor(max_workers=MAX_WORKERS) as ex:
        for name, rh, r, st in ex.map(_star, jobs):
            res.setdefault(name, {})[rh] = r
            co2 = r.get('CO2', (float('nan'),))[0] if r else float('nan')
            h2o = r.get('water', (0.0,))[0] if r else float('nan')
            print(f'  [{st:>16}] RH{int(rh*100):>3}% {name:<10} '
                  f'CO2 {co2:>7.4f}  H2O {h2o:>8.4f}', flush=True)

    label = dict(TARGETS)
    print('\n' + '=' * 108)
    print(f'{"구조":<32} {"RH":>5} {"CO2 [mol/kg]":>20} {"H2O [mol/kg]":>20} '
          f'{"건조대비":>18} {"H2O/CO2":>9}')
    print('-' * 108)
    rows = []
    for n, lb in TARGETS:
        dry = res.get(n, {}).get(0.0)
        c0 = dry['CO2'][0] if dry and dry.get('CO2') else None
        e0 = dry['CO2'][1] if dry and dry.get('CO2') else 0.0
        for rh in RH_LIST:
            r = res.get(n, {}).get(rh)
            if not r:
                continue
            c, ec = r.get('CO2', (float('nan'), 0.0))
            w, ew = r.get('water', (0.0, 0.0))
            ret = sigma = float('nan')
            if c0:
                ret = c / c0 * 100
                den = math.sqrt(ec ** 2 + e0 ** 2)
                sigma = abs(c - c0) / den if den else float('nan')
            print(f'{lb:<32} {int(rh*100):>4}% {c:>11.4f} ± {ec:<6.4f} '
                  f'{w:>11.4f} ± {ew:<6.4f} {ret:>10.1f}% ({sigma:>3.1f}σ) '
                  f'{(w/c if c else 0):>9.2f}')
            rows.append({'name': n, 'label': lb, 'RH': rh,
                         'CO2_molkg': c, 'CO2_err': ec,
                         'H2O_molkg': w, 'H2O_err': ew,
                         'CO2_retention_pct': ret, 'retention_sigma': sigma,
                         'H2O_over_CO2': (w / c if c else None)})
        print()

    with open(os.path.join(HERE, 'water_results.json'), 'w', encoding='utf-8') as f:
        json.dump(rows, f, indent=2, ensure_ascii=False)
    print('[OK] water_results.json')
    print('\n판정 기준(19_WaterCompetition 과 동일, 계산 전 확정):')
    print('  RH90 유지율 80% 이상 -> 유효 / 50~80% -> 조건부(전처리 건조 비용) / 50% 미만 -> 종료')
    print('  차이의 유의성은 1.5σ 를 기준으로 본다.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
