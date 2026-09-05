"""T-B2 확장 — 관문 탈락 saIm 7종 물 K_H (②-전용) + `base` 대조 2건.

[왜] `TB2_CRITERION_NOTE_20260905.md` 가 결과 전에 등록한 결정입니다.
     등록 32종과 유지율 보유 17종의 **교집합이 5종**뿐이라 기준 ② 를 n=5 에서
     잴 수 없습니다(순열 정확 양측 5% 임계 |ρ| = **1.000**). 관문 탈락 saIm
     7종을 더해 **n=12** 로 올립니다(임계 0.587).

[한정] 이 7종은 **관문 탈락 구조**입니다.
       · **②-전용**입니다. **기준 ① 과 후보 선정에는 넣지 않습니다.**
       · 등록 32종이 먼저입니다(A -> B -> 이 확장).
       · 판정문에는 병기 넷을 답니다 — 임계 여유 0.013 / 계열 표본 3 /
         순위 잡음(K_H 인접 쌍 둘이 씨앗 재현성 3.0% 안) / 관문 탈락.
       그래서 **별도 JSON** 으로 씁니다. 32종 파일에 섞지 않습니다.

[대조] 두 건이고 **서로 다른 질문**입니다. 판정 기준은 측정 전에
       `TB2_CONTROLS_20260905.md` 에 등록했습니다.

       (가) `base` **CO2 Widom** — 이 러너 경로(단위셀·입력 조립·출력 파싱·단위)를
            저장소 기존값과 대조합니다. `results_v3.json` 의 base K_H_CO2 =
            **5.33337e-05 +/- 1.14459e-06** 이 같은 자로 나온 값입니다.
            어긋나면 물 K_H 전량이 같은 의심을 받으므로 판정을 보류합니다.

       (나) `base` **3자리 물 Widom** — 문턱 5e-6 은 **TIP4P(3자리) 기준**인데
            우리는 **TIP5P-Ew(5자리)** 입니다. 같은 구조를 배포본 3자리 물로
            재서 비 R = K_H(5자리)/K_H(3자리) 로 **물 모델의 몫**을 뗍니다.

       (다) `base` **`Hw none` 물 Widom** — 09-05 에 `UFF_MOF` 혼합규칙에 `Hw` 항이
            없어 RASPA 가 앞자리 일치로 `H_`(UFF 수소, eps 22.1417 / sigma 2.57113)를
            물려준 것이 확인됐습니다(`WATER_FF_CONFIRM_20260905.md`). TIP5P 수소는
            LJ 가 없어야 합니다. **실행 폴더 지역 힘장 사본**에 `Hw none`/`Lw none`
            두 줄만 더해 같은 구조를 다시 재고, 비 D = K_H(현행)/K_H(수정) 로
            **결함이 K_H 를 얼마나 움직이는지** 뗍니다.

       !! (나)(다)는 **진단 전용**입니다. 규약 물 정의·규약 힘장이 아니므로 어떤
          결과 집합에도 넣지 않고 순위에도 쓰지 않습니다. 폴더·JSON 이름에
          water3site / hwnone 을 박습니다. **공용 힘장 파일은 건드리지 않습니다**
          (CLAUDE.md §1 — 사용자 판단 사항).

[자] 러너를 고쳐 쓰지 않고 `run_tb2_water_kh.run_one` 을 **그대로 불러**
     씁니다(규약 표류 방지). CO2 만 여기서 따로 조립하고 사이클·힘장·컷오프·
     Ewald 는 그 모듈 상수를 씁니다.

[인터프리터] ase 가 필요합니다. **시스템 python3 에는 없습니다.**
     /home/mangwon1/miniconda3/envs/czeromof/bin/python 으로 띄우십시오.

사용:  <conda python> run_tb2_ext.py
"""
import json, os, re, shutil, socket, subprocess, sys
from multiprocessing import Pool

import run_tb2_water_kh as T

EXT = ['saIm0625', 'saIm0667', 'saIm075', 'saIm0875',
       'saIm0917', 'saIm0958', 'saIm100']
CONTROL_GAS = 'CO2'
CONTROL_STRUCT = 'base'
WATER3 = os.path.join(T.HERE, '..', '00_Migration', 'raspa_share', 'raspa',
                      'molecules', 'TraPPE', 'water.def')   # 배포본 3자리 — 진단 전용
FFSRC = os.path.join(T.HERE, '..', '00_Migration', 'raspa_share', 'raspa',
                     'forcefield', 'UFF_MOF')
WORKERS = int(os.environ.get('TB2_WORKERS', '8'))


def run_gas(args):
    """대조용: 같은 자로 기체 하나를 Widom."""
    name, gas = args
    cif = os.path.join(T.CHARGED, name + '_DDEC6.cif')
    fw = name + '_DDEC6'
    d = os.path.join(T.RUNS, f'widom_{gas.lower()}_{name}')
    os.makedirs(d, exist_ok=True)
    shutil.copy(cif, os.path.join(d, fw + '.cif'))
    na, nb, nc = T.unit_cells(cif)
    with open(os.path.join(d, 'simulation.input'), 'w') as f:
        f.write(f"""SimulationType                MonteCarlo
NumberOfCycles                {T.CYCLES}
NumberOfInitializationCycles  {T.INIT}
PrintEvery                    {T.CYCLES}
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

Component 0 MoleculeName              {gas}
            MoleculeDefinition        TraPPE
            WidomProbability          1.0
            CreateNumberOfMolecules   0
""")
    subprocess.run([T.SIMULATE, 'simulation.input'], cwd=d,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False)
    sysdir = os.path.join(d, 'Output', 'System_0')
    kh = ekh = None
    if os.path.isdir(sysdir):
        for p in [os.path.join(sysdir, x) for x in os.listdir(sysdir)]:
            for line in open(p, encoding='utf-8', errors='ignore'):
                if 'Average Henry coefficient:' in line:
                    m = re.search(r':\s*([0-9.eE+-]+)\s*\+/-\s*([0-9.eE+-]+)', line)
                    if m:
                        kh, ekh = float(m.group(1)), float(m.group(2))
    return {'name': name, 'gas': gas, 'KH': kh, 'KH_err': ekh,
            'unit_cells': [na, nb, nc], 'ok': kh is not None}


def run_water3(name):
    """진단 전용: 배포본 3자리 물로 같은 구조를 잰다. 규약 물이 아니다."""
    cif = os.path.join(T.CHARGED, name + '_DDEC6.cif')
    fw = name + '_DDEC6'
    d = os.path.join(T.RUNS, 'widom_water3site_' + name)
    os.makedirs(d, exist_ok=True)
    shutil.copy(cif, os.path.join(d, fw + '.cif'))
    shutil.copy(WATER3, os.path.join(d, 'water.def'))
    na, nb, nc = T.unit_cells(cif)
    with open(os.path.join(d, 'simulation.input'), 'w') as f:
        f.write(f"""SimulationType                MonteCarlo
NumberOfCycles                {T.CYCLES}
NumberOfInitializationCycles  {T.INIT}
PrintEvery                    {T.CYCLES}
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

Component 0 MoleculeName              water
            MoleculeDefinition        TraPPE
            WidomProbability          1.0
            CreateNumberOfMolecules   0
""")
    subprocess.run([T.SIMULATE, 'simulation.input'], cwd=d,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False)
    sysdir = os.path.join(d, 'Output', 'System_0')
    kh = ekh = None
    if os.path.isdir(sysdir):
        for p in [os.path.join(sysdir, x) for x in os.listdir(sysdir)]:
            for line in open(p, encoding='utf-8', errors='ignore'):
                if 'Average Henry coefficient:' in line:
                    m = re.search(r':\s*([0-9.eE+-]+)\s*\+/-\s*([0-9.eE+-]+)', line)
                    if m:
                        kh, ekh = float(m.group(1)), float(m.group(2))
    return {'name': name, 'water_sites': 3, 'KH': kh, 'KH_err': ekh,
            'unit_cells': [na, nb, nc], 'ok': kh is not None,
            'WARN': '진단 전용 — 규약 물 정의(TIP5P-Ew 5자리)가 아님. '
                    '어떤 결과 집합에도 넣지 말 것.'}


def make_local_ff(rundir):
    """실행 폴더 안 UFF_MOF 지역 사본. `Hw none` / `Lw none` 두 줄만 더한다.

    !! 꼬리(`# general mixing rule` / `Lorentz-Berthelot`) **앞**에 넣습니다.
       파일 끝에 붙이면 RASPA 가 그 두 줄을 항으로 읽어 **수정이 무시됩니다**
       (랩탑 09-05 첫 시도가 그랬고 `Hw-Hw` 가 UFF 값 그대로 남았습니다).
    """
    d = os.path.join(rundir, 'UFF_MOF')
    os.makedirs(d, exist_ok=True)
    shutil.copy(os.path.join(FFSRC, 'pseudo_atoms.def'), d)
    src = os.path.join(FFSRC, 'force_field_mixing_rules.def')
    lines = open(src, encoding='utf-8').read().splitlines()
    tail = next(i for i, ln in enumerate(lines)
                if ln.strip().startswith('# general mixing rule'))
    lines[5] = str(int(lines[5].strip()) + 2)          # 6행 = 항 개수
    lines[tail:tail] = ['Hw             none', 'Lw             none']
    open(os.path.join(d, 'force_field_mixing_rules.def'), 'w',
         encoding='utf-8').write('\n'.join(lines) + '\n')
    return d


def run_hwnone(name):
    """진단 전용: `Hw none`/`Lw none` 지역 힘장으로 같은 구조의 물 K_H."""
    cif = os.path.join(T.CHARGED, name + '_DDEC6.cif')
    fw = name + '_DDEC6'
    d = os.path.join(T.RUNS, 'widom_hwnone_' + name)
    os.makedirs(d, exist_ok=True)
    shutil.copy(cif, os.path.join(d, fw + '.cif'))
    shutil.copy(T.WATER_DEF, os.path.join(d, 'water.def'))
    make_local_ff(d)
    na, nb, nc = T.unit_cells(cif)
    with open(os.path.join(d, 'simulation.input'), 'w') as f:
        f.write(f"""SimulationType                MonteCarlo
NumberOfCycles                {T.CYCLES}
NumberOfInitializationCycles  {T.INIT}
PrintEvery                    {T.CYCLES}
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

Component 0 MoleculeName              water
            MoleculeDefinition        TraPPE
            WidomProbability          1.0
            CreateNumberOfMolecules   0
""")
    subprocess.run([T.SIMULATE, 'simulation.input'], cwd=d,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False)
    sysdir = os.path.join(d, 'Output', 'System_0')
    kh = ekh = None
    hwhw = owhw = None
    if os.path.isdir(sysdir):
        for p in [os.path.join(sysdir, x) for x in os.listdir(sysdir)]:
            txt = open(p, encoding='utf-8', errors='ignore').read()
            for line in txt.splitlines():
                if 'Average Henry coefficient:' in line:
                    m = re.search(r':\s*([0-9.eE+-]+)\s*\+/-\s*([0-9.eE+-]+)', line)
                    if m:
                        kh, ekh = float(m.group(1)), float(m.group(2))
                m2 = re.search(r'Hw\s*-\s*Hw\s*\[LENNARD_JONES\].*?p_0/k_B:\s*([0-9.]+)', line)
                if m2:
                    hwhw = float(m2.group(1))
                m3 = re.search(r'Ow\s*-\s*Hw\s*\[LENNARD_JONES\].*?p_0/k_B:\s*([0-9.]+)', line)
                if m3:
                    owhw = float(m3.group(1))
    # **등록된 확인 조건** — 지역 힘장이 실제로 먹혔는가 (검사 9: 조용한 대체)
    applied = (hwhw in (None, 0.0)) and (owhw in (None, 0.0))
    return {'name': name, 'KH_water': kh, 'KH_water_err': ekh,
            'unit_cells': [na, nb, nc],
            'ff_applied': applied, 'HwHw_eps': hwhw, 'OwHw_eps': owhw,
            'ok': kh is not None and applied,
            'WARN': '진단 전용 — 규약 힘장이 아님(Hw none/Lw none 추가). '
                    'ff_applied 가 false 면 지역 사본이 안 먹은 것이므로 '
                    'K_H 를 쓰지 말 것.'}


def main():
    tag = socket.gethostname().lower()
    os.makedirs(T.OUT, exist_ok=True)
    nsite = sum(1 for ln in open(T.WATER_DEF, encoding='utf-8')
                if len(ln.split()) > 4 and ln.split()[1] in ('Ow', 'Hw', 'Lw'))
    if nsite != 5:
        print('  !! 5자리 물이 아닙니다. 중단.', flush=True)
        return 1
    missing = [n for n in EXT
               if not os.path.isfile(os.path.join(T.CHARGED, n + '_DDEC6.cif'))]
    if missing:
        print(f'  !! CIF 없음: {missing}. 중단.', flush=True)
        return 1
    n3 = sum(1 for ln in open(WATER3, encoding='utf-8')
             if len(ln.split()) > 4 and ln.split()[1] in ('Ow', 'Hw', 'Lw'))
    if n3 != 3:
        print(f'  !! 대조용 배포본 물이 3자리가 아닙니다({n3}). 중단.', flush=True)
        return 1
    print(f'T-B2 확장 — 관문 탈락 saIm {len(EXT)}종 (②-전용) + {CONTROL_STRUCT} 대조 2건'
          f'(CO2 Widom · 3자리 물 Widom), 워커 {WORKERS}', flush=True)
    print(f'  자: NumberOfCycles {T.CYCLES} / '
          f'NumberOfInitializationCycles {T.INIT}, UFF_MOF, 컷오프 {T.CUTOFF}, '
          f'Ewald 1e-6 — A/B 와 동일', flush=True)
    print(f'  물 정의 사이트 {nsite}개 (TIP5P-Ew 는 5)', flush=True)
    print('  확장 대상: ' + ', '.join(EXT), flush=True)

    water_rows, gas_rows, w3_rows, hw_rows = [], [], [], []
    jobs = ([('water', n) for n in EXT]
            + [('gas', (CONTROL_STRUCT, CONTROL_GAS))]
            + [('water3', CONTROL_STRUCT)]
            + [('hwnone', CONTROL_STRUCT)])
    with Pool(WORKERS) as p:
        for kind, r in p.imap_unordered(_dispatch, jobs, chunksize=1):
            {'water': water_rows, 'gas': gas_rows,
             'water3': w3_rows, 'hwnone': hw_rows}[kind].append(r)
            v = r['KH_water'] if kind in ('water', 'hwnone') else r['KH']
            lbl = (r['name'] if kind == 'water'
                   else f"{r['name']}/{r['gas']}" if kind == 'gas'
                   else f"{r['name']}/물3자리" if kind == 'water3'
                   else f"{r['name']}/Hw-none")
            print(f"  [{'ok' if r['ok'] else '실패'}] {lbl:14s} K_H {v}", flush=True)

    f1 = os.path.join(T.OUT, f'water_kh_EXT_{tag}.json')
    json.dump({'half': 'EXT', 'tag': tag, 'cycles_init': T.INIT,
               'cycles_production': T.CYCLES,
               'note': '관문 탈락 saIm 7종. ②-전용 — 기준 ① 과 후보 선정 제외. '
                       'TB2_CRITERION_NOTE_20260905.md 등록 결정. '
                       '판정문에 병기 넷 필수(임계 여유 0.013 / 계열 표본 3 / '
                       '순위 잡음 / 관문 탈락).',
               'rows': sorted(water_rows, key=lambda x: x['name'])},
              open(f1, 'w'), ensure_ascii=False, indent=2)

    f2 = os.path.join(T.OUT, f'widom_control_{CONTROL_GAS}_{tag}.json')
    json.dump({'tag': tag, 'cycles_init': T.INIT, 'cycles_production': T.CYCLES,
               'purpose': '물 K_H 가 문턱의 75~512배인 것이 "물이 비싸다" 인지 '
                          '"우리 물 정의(TIP5P-Ew 5자리)가 비싸다" 인지 가르는 대조. '
                          '같은 구조·같은 자.',
               'rows': gas_rows}, open(f2, 'w'), ensure_ascii=False, indent=2)

    f3 = os.path.join(T.OUT, f'widom_control_water3site_{tag}.json')
    json.dump({'tag': tag, 'cycles_init': T.INIT, 'cycles_production': T.CYCLES,
               'WARN': '진단 전용. 배포본 3자리 물(TraPPE/water.def)로 잰 값이며 '
                       '규약 물 정의(TIP5P-Ew 5자리)가 아니다. '
                       '어떤 결과 집합·순위에도 넣지 말 것.',
               'purpose': '문턱 5e-6 이 TIP4P(3자리) 기준이므로, '
                          'R = K_H(5자리)/K_H(3자리) 로 물 모델의 몫을 뗀다. '
                          '판정 기준은 TB2_CONTROLS_20260905.md 에 측정 전 등록.',
               'rows': w3_rows}, open(f3, 'w'), ensure_ascii=False, indent=2)

    f4 = os.path.join(T.OUT, f'widom_control_hwnone_{tag}.json')
    json.dump({'tag': tag, 'cycles_init': T.INIT, 'cycles_production': T.CYCLES,
               'WARN': '진단 전용. 지역 힘장 사본(Hw none/Lw none)으로 잰 값이며 '
                       '규약 힘장이 아니다. 어떤 결과 집합·순위에도 넣지 말 것.',
               'purpose': 'D = K_H(현행)/K_H(수정) 로 Hw LJ 결함이 물 K_H 를 '
                          '얼마나 움직이는지 뗀다. 판정 기준은 '
                          'TB2_CONTROLS_20260905.md 에 측정 전 등록.',
               'verify': '등록 확인 조건 — 출력에서 Hw-Hw 와 Ow-Hw 의 eps 가 0 '
                         '이거나 NO VDW 여야 지역 사본이 먹은 것. ff_applied 참조.',
               'rows': hw_rows}, open(f4, 'w'), ensure_ascii=False, indent=2)

    ok = len([r for r in water_rows if r['ok']])
    print(f'\n[OK] 확장 {ok}/{len(EXT)} -> {f1}', flush=True)
    print(f'[OK] 대조 CO2 {len([r for r in gas_rows if r["ok"]])}/1 -> {f2}', flush=True)
    print(f'[OK] 대조 물3자리 {len([r for r in w3_rows if r["ok"]])}/1 -> {f3}', flush=True)
    for r in hw_rows:
        if not r['ff_applied']:
            print('  !! Hw-none 대조: **지역 힘장이 안 먹었습니다** '
                  f"(Hw-Hw eps {r['HwHw_eps']}, Ow-Hw eps {r['OwHw_eps']}). "
                  'K_H 를 쓰지 마십시오.', flush=True)
    print(f'[OK] 대조 Hw-none {len([r for r in hw_rows if r["ok"]])}/1 -> {f4}', flush=True)
    return 0


def _dispatch(job):
    kind, payload = job
    if kind == 'water':
        return kind, T.run_one(payload)
    if kind == 'gas':
        return kind, run_gas(payload)
    if kind == 'water3':
        return kind, run_water3(payload)
    return kind, run_hwnone(payload)


if __name__ == '__main__':
    sys.exit(main())
