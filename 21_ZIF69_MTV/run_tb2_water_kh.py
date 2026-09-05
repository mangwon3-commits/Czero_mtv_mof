"""T-B2 — 물 K_H (Widom 삽입), v3 관문 통과 32조성.

[대상] `tb2_targets.json` (기계 추출, LCD 감소 <20%). **32조성이고 base 가 그 안**입니다.
       `saIm075` 는 관문 미해결이라 **여기 없습니다** — 관찰 전용 1건으로 따로 돕니다.

[자] 저장소 기존 Widom 관례 그대로. **덧셈 표기를 쓰지 않고 키 이름으로 적습니다** —
     "5000+2000" 이 기기마다 반대로 읽힌 사례가 09-05 에 있었습니다:
         NumberOfCycles                15000
         NumberOfInitializationCycles   3000
     UFF_MOF, 컷오프 12, Ewald 1e-6, 압력 1e-5 Pa (run_aryl_gcmc.py:147 경로 그대로).
     CO2/N2 K_H 가 이 자로 나왔으므로 **같은 자여야 순위 비교가 성립**합니다.
     물 정의는 §1 의 TIP5P-Ew 5사이트(19_WaterCompetition/water.def)를 복사해 씁니다.

[분담] 인자로 절반을 지정합니다. **기본값을 두지 않습니다** —
       09-05 환경변수 감사에서 "대상을 정하는 변수에 기본값이 있으면 조용히 다른
       대상이 된다"(RREP_INDEX 사례)를 확인했기 때문입니다. 인자 없이 돌리면 죽습니다.

           A = 정렬 목록의 **짝수 번째**,  B = **홀수 번째**  (0-기반)
       계열이 한쪽에 몰리지 않도록 교차 배분합니다 — 한쪽이 죽어도 남은 절반이
       모든 계열을 덮습니다.

[삭제] 이 러너는 **아무것도 지우지 않습니다.** 남의 러너를 감싸지 않으므로
       그쪽 정리 로직도 물려받지 않습니다(09-05 laptop2 격자 유실 건).

사용:  python3 run_tb2_water_kh.py A     또는  B     (또는 ALL)
"""
import json, os, re, shutil, socket, subprocess, sys
from multiprocessing import Pool

HERE = os.path.dirname(os.path.abspath(__file__))
CHARGED = os.path.join(HERE, 'charged_v3')
WATER_DEF = os.path.join(HERE, '..', '19_WaterCompetition', 'water.def')
SIMULATE = shutil.which('simulate') or os.path.expanduser(
    '~/miniconda3/envs/czeromof/bin/simulate')
RUNS = os.path.join(HERE, 'tb2_runs')
OUT = os.path.join(HERE, 'v3_water_kh')

CYCLES, INIT = 15000, 3000          # 저장소 Widom 관례
TEMP, CUTOFF, PRESS = 298.0, 12.0, 1e-5
WORKERS = int(os.environ.get('TB2_WORKERS', '6'))   # 자원 배분 — 규약값 아님


def unit_cells(cif):
    """최소 이미지: 각 수직폭 > 2 x 컷오프."""
    from ase.io import read
    import numpy as np
    a = read(cif)
    c = np.asarray(a.get_cell())
    V = abs(np.linalg.det(c))
    n = []
    for i in range(3):
        j, k = (i + 1) % 3, (i + 2) % 3
        area = np.linalg.norm(np.cross(c[j], c[k]))
        n.append(max(1, int(-(-(2 * CUTOFF) // (V / area)))))
    return n


def run_one(name):
    cif = os.path.join(CHARGED, name + '_DDEC6.cif')
    fw = name + '_DDEC6'
    d = os.path.join(RUNS, 'widom_water_' + name)
    os.makedirs(d, exist_ok=True)
    shutil.copy(cif, os.path.join(d, fw + '.cif'))
    shutil.copy(WATER_DEF, os.path.join(d, 'water.def'))
    na, nb, nc = unit_cells(cif)
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
ExternalPressure              {PRESS}

Component 0 MoleculeName              water
            MoleculeDefinition        TraPPE
            WidomProbability          1.0
            CreateNumberOfMolecules   0
""")
    subprocess.run([SIMULATE, 'simulation.input'], cwd=d,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False)
    outs = [os.path.join(d, 'Output', 'System_0', x)
            for x in os.listdir(os.path.join(d, 'Output', 'System_0'))] \
        if os.path.isdir(os.path.join(d, 'Output', 'System_0')) else []
    kh = ekh = None
    for p in outs:
        for line in open(p, encoding='utf-8', errors='ignore'):
            if 'Average Henry coefficient:' in line:
                m = re.search(r':\s*([0-9.eE+-]+)\s*\+/-\s*([0-9.eE+-]+)', line)
                if m:
                    kh, ekh = float(m.group(1)), float(m.group(2))
    return {'name': name, 'KH_water': kh, 'KH_water_err': ekh,
            'unit_cells': [na, nb, nc], 'ok': kh is not None}


def main():
    if len(sys.argv) < 2 or sys.argv[1] not in ('A', 'B', 'ALL'):
        print('사용: python3 run_tb2_water_kh.py A|B|ALL   '
              '(기본값 없음 — 대상을 정하는 인자라 반드시 명시)', flush=True)
        return 2
    half = sys.argv[1]
    names = sorted(json.load(open(os.path.join(HERE, 'tb2_targets.json')))['names'])
    sel = names if half == 'ALL' else names[0::2] if half == 'A' else names[1::2]
    tag = socket.gethostname().lower()
    os.makedirs(OUT, exist_ok=True)
    print(f'T-B2 물 K_H (Widom) — 절반 {half}, {len(sel)}/{len(names)}종, 워커 {WORKERS}',
          flush=True)
    print(f'  자: NumberOfCycles {CYCLES} / NumberOfInitializationCycles {INIT}, '
          f'UFF_MOF, 컷오프 {CUTOFF}, Ewald 1e-6 (저장소 Widom 관례 그대로)', flush=True)
    nsite = sum(1 for ln in open(WATER_DEF, encoding='utf-8')
                if len(ln.split()) > 4 and ln.split()[1] in ('Ow', 'Hw', 'Lw'))
    print(f'  물 정의 사이트 {nsite}개 (TIP5P-Ew 는 5)', flush=True)
    if nsite != 5:
        print('  !! 5자리 물이 아닙니다. 중단.', flush=True); return 1
    print('  대상: ' + ', '.join(sel), flush=True)
    rows = []
    with Pool(WORKERS) as p:
        for r in p.imap_unordered(run_one, sel, chunksize=1):
            rows.append(r)
            print(f"  [{'ok' if r['ok'] else '실패'}] {r['name']:12s} "
                  f"K_H {r['KH_water']}", flush=True)
    f = os.path.join(OUT, f'water_kh_{half}_{tag}.json')
    json.dump({'half': half, 'tag': tag, 'cycles': [INIT, CYCLES],
               'note': 'Widom 물 K_H. 문턱 5e-6 mmol/g/Pa 는 TIP4P 기준 — '
                       'TIP5P-Ew 값에 적용한다는 한정어 필수',
               'rows': sorted(rows, key=lambda x: x['name'])}, open(f, 'w'),
              ensure_ascii=False, indent=2)
    print(f'\n[OK] {len([r for r in rows if r["ok"]])}/{len(sel)} -> {f}', flush=True)
    return 0


if __name__ == '__main__':
    sys.exit(main())
