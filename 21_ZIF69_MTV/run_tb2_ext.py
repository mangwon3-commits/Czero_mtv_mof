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


def component_net_charge(sysdir):
    """출력 머리말의 **흡착질 성분** 순전하. 정의 파일을 바꾸는 진단의 확인 조건.

    !! **"계" 의 순전하가 아닙니다.** 골격이 있는 실행에서도 이 줄은
       `Component 0 [water]` 에 대한 것이고 **골격 DDEC6 전하 합은 안 들어갑니다.**
       이름을 `net_charge` 로 두면 나중에 **골격 검사로 오독**됩니다
       (검사 5: 같은 이름의 다른 양). 골격 쪽은 CIF 의 전하 열을 따로 합해야 하고,
       09-05 랩탑 측정으로 `charged_v3/*.cif` **90종 전부 |합| < 1e-3**
       (최대 mbIm050 +7.9e-05) 입니다.

    09-05: 배포본 3자리 `water.def` 를 넣었더니 `Lw` 가 없어 순전하가 **+0.482**
    가 됐고(우리 `pseudo_atoms.def` 는 TIP5P-Ew 배치라 음전하가 `Lw` 에 있음),
    전하 골격 안 양이온이라 K_H 가 **29만 배**로 나왔습니다. RASPA 는 오류를
    내지 않고 머리말에만 적었습니다. **정의 파일은 자기 짝의 `pseudo_atoms.def`
    를 전제합니다 — 한쪽만 바꾸면 조용히 다른 분자가 됩니다.**
    """
    if not os.path.isdir(sysdir):
        return None
    files = sorted(x for x in os.listdir(sysdir) if x.endswith('.data'))
    if len(files) != 1:
        return None
    for line in open(os.path.join(sysdir, files[0]), encoding='utf-8',
                     errors='ignore'):
        m = re.search(r'net charge of\s*([0-9.eE+-]+)', line)
        if m:
            return float(m.group(1))
    return None


def read_kh(sysdir, comp=None):
    """`Output/System_0` 에서 헨리 상수를 읽는다. **애매하면 거부한다.**

    [왜] 09-05 에 랩탑이 자기 분석기에서 `glob` + mtime 최신 집기가 **두 방향으로
         다 틀리는 것**을 찾았습니다(엉뚱한 실행을 조용히 고르거나, 대조를 아예
         안 잡거나). 제 파서도 같은 종류였습니다 — `os.listdir` 를 돌며
         **마지막 일치를 덮어쓰기**로 취해서, 파일이 둘이면 **listdir 순서**가
         값을 정합니다.

    [왜 안 터졌나] RASPA 출력 파일명이 조건을 담습니다
         (`output_<구조>_<셀>_<T>_<P>.data`). 같은 조건이면 **덮어써서** 하나만
         남습니다. **즉 맞은 값이 나온 이유가 설계가 아니라 이름 규칙입니다** —
         사이클이나 압력을 바꾸면 두 파일이 공존하고 그때 조용히 틀립니다.

    [규약] 0개면 None, **2개 이상이면 거부하고 목록을 남긴다**, 1개면 읽는다.

    [한 파일 안의 다중 일치 — 09-05 검산] `Average Henry coefficient` 는 실물에서
         **2줄**입니다: 값 없는 **머리말** 한 줄과 `[<성분>] ... 값 +/- 오차` 한 줄.
         제가 처음 *"마지막 일치를 쓴다(RASPA 가 끝에 다시 찍으므로)"* 라고 적었는데
         **틀렸습니다** — 다시 찍는 게 아니라 **파싱 가능한 줄이 하나뿐**이고
         "마지막" 은 우연이었습니다. 랩탑이 이 층을 짚어 검산했습니다.

         **그리고 성분이 둘이면 조용히 틀립니다** — `[water]` 와 `[CO2]` 가 각각
         한 줄씩 나오고 마지막이 이깁니다. 그래서 **성분 이름을 명시해 맞춥니다.**
    """
    if not os.path.isdir(sysdir):
        return None, None, 'Output/System_0 없음'
    files = sorted(x for x in os.listdir(sysdir) if x.endswith('.data'))
    if not files:
        return None, None, '.data 없음'
    if len(files) > 1:
        return None, None, ('.data 가 %d개라 거부: %s — 어느 실행의 값인지 '
                            '정해지지 않습니다' % (len(files), ', '.join(files)))
    pat = re.compile(r'\[([^\]]+)\]\s*Average Henry coefficient:\s*'
                     r'([0-9.eE+-]+)\s*\+/-\s*([0-9.eE+-]+)')
    found = {}
    for line in open(os.path.join(sysdir, files[0]), encoding='utf-8',
                     errors='ignore'):
        m = pat.search(line)
        if m:
            found[m.group(1)] = (float(m.group(2)), float(m.group(3)))
    if not found:
        return None, None, '헨리 상수 줄 없음'
    if comp is not None:
        if comp not in found:
            return None, None, ('성분 %s 가 없습니다: %s' % (comp, list(found)))
        kh, ekh = found[comp]
        return kh, ekh, None
    if len(found) > 1:
        return None, None, ('성분이 %d개라 거부: %s — comp 를 지정하십시오'
                            % (len(found), ', '.join(found)))
    (kh, ekh), = found.values()
    return kh, ekh, None


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
    kh, ekh, why = read_kh(os.path.join(d, 'Output', 'System_0'), comp=gas)
    return {'name': name, 'gas': gas, 'KH': kh, 'KH_err': ekh,
            'unit_cells': [na, nb, nc], 'ok': kh is not None, 'why': why}


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
    kh, ekh, why = read_kh(sysdir, comp='water')
    q = component_net_charge(sysdir)
    # **등록 확인 조건 (09-05 추가)**: 정의 파일을 바꾸는 진단은 순전하가 0 이어야 함
    if q is None or abs(q) > 1e-6:
        why = (f'**성분** 순전하 {q} — 0 이 아니므로 다른 분자입니다. '
               'K_H 를 쓰지 마십시오. (골격 전하 합은 별개 검사)')
        kh = ekh = None
    return {'name': name, 'water_sites': 3, 'component_net_charge': q, 'KH': kh, 'KH_err': ekh, 'why': why,
            'unit_cells': [na, nb, nc], 'ok': kh is not None,
            'WARN': '진단 전용 — 규약 물 정의(TIP5P-Ew 5자리)가 아님. '
                    '어떤 결과 집합에도 넣지 말 것. '
                    '**성분 순전하가 0 이 아니면 다른 분자이므로 무효.** '
                    '(이 값은 흡착질 성분이며 골격 전하 합이 아님)'}


def make_local_ff(rundir):
    """실행 폴더 안에 **RASPA_DIR 트리**를 만들고 그 경로를 돌려준다.

    !! 09-05 실패: `<rundir>/UFF_MOF/` 에 사본을 두고 `Forcefield UFF_MOF` 로
       돌렸더니 **RASPA 가 그것을 안 보고 전역 힘장을 썼습니다**(출력 짝표가
       `Hw-Hw 22.1417` 그대로). **지역 사본을 만든 것과 RASPA 가 그것을 읽는
       것은 다릅니다** — 확인 조건이 그걸 잡았습니다.

       RASPA 는 `$RASPA_DIR/share/raspa/{forcefield,molecules,structures}` 를
       봅니다. 그래서 **그 구조를 그대로 만들고 `forcefield/UFF_MOF` 만 실물로
       두고 나머지는 심볼릭 링크**합니다. 공용 파일은 안 건드립니다.

    !! 항 목록 **뒤**의 `# general mixing rule` / `Lorentz-Berthelot` 꼬리
       **앞**에 두 줄을 넣습니다. 뒤에 붙이면 RASPA 가 그것을 항으로 읽어
       수정이 조용히 무시됩니다(랩탑 09-05).
    """
    share = os.path.abspath(os.path.join(FFSRC, '..', '..'))     # .../share/raspa
    root = os.path.join(os.path.abspath(rundir), 'ffroot')
    dst = os.path.join(root, 'share', 'raspa')
    os.makedirs(dst, exist_ok=True)
    for sub in os.listdir(share):
        link = os.path.join(dst, sub)
        if sub == 'forcefield' or os.path.lexists(link):
            continue
        os.symlink(os.path.join(share, sub), link)
    ffdir = os.path.join(dst, 'forcefield')
    os.makedirs(ffdir, exist_ok=True)
    for sub in os.listdir(os.path.join(share, 'forcefield')):
        link = os.path.join(ffdir, sub)
        if sub == 'UFF_MOF' or os.path.lexists(link):
            continue
        os.symlink(os.path.join(share, 'forcefield', sub), link)
    d = os.path.join(ffdir, 'UFF_MOF')
    os.makedirs(d, exist_ok=True)
    shutil.copy(os.path.join(FFSRC, 'pseudo_atoms.def'), d)
    lines = open(os.path.join(FFSRC, 'force_field_mixing_rules.def'),
                 encoding='utf-8').read().splitlines()
    tail = next(i for i, ln in enumerate(lines)
                if ln.strip().startswith('# general mixing rule'))
    lines[5] = str(int(lines[5].strip()) + 2)
    lines[tail:tail] = ['Hw             none', 'Lw             none']
    open(os.path.join(d, 'force_field_mixing_rules.def'), 'w',
         encoding='utf-8').write('\n'.join(lines) + '\n')
    return root


def run_water_ff(name, local_ff):
    """물 K_H 1건. `local_ff` 참이면 `Hw none`/`Lw none` 지역 힘장을 쓴다.

    **분자와 분모를 같은 배치에서 잽니다** — D 는 비이므로 기기·씨앗·동시성·
    러너가 모두 같아야 하고, 다른 것은 **혼합규칙 두 줄뿐**이어야 합니다.
    (랩탑 09-05 지적: `base` K_H 가 둘이라 어느 것을 분모로 쓸지 정해야 함)
    """
    cif = os.path.join(T.CHARGED, name + '_DDEC6.cif')
    fw = name + '_DDEC6'
    d = os.path.join(T.RUNS, ('widom_hwnone_' if local_ff else 'widom_current_') + name)
    os.makedirs(d, exist_ok=True)
    shutil.copy(cif, os.path.join(d, fw + '.cif'))
    shutil.copy(T.WATER_DEF, os.path.join(d, 'water.def'))
    env = None
    if local_ff:
        env = dict(os.environ, RASPA_DIR=make_local_ff(d))
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
    subprocess.run([T.SIMULATE, 'simulation.input'], cwd=d, env=env,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False)
    sysdir = os.path.join(d, 'Output', 'System_0')
    kh, ekh, why = read_kh(sysdir, comp='water')
    hwhw = owhw = None
    if why is None or '헨리' in (why or ''):
        f1 = sorted(x for x in os.listdir(sysdir) if x.endswith('.data'))[0]
        for line in open(os.path.join(sysdir, f1), encoding='utf-8',
                         errors='ignore'):
            m2 = re.search(r'Hw\s*-\s*Hw\s*\[LENNARD_JONES\].*?p_0/k_B:\s*([0-9.]+)', line)
            if m2:
                hwhw = float(m2.group(1))
            m3 = re.search(r'Ow\s*-\s*Hw\s*\[LENNARD_JONES\].*?p_0/k_B:\s*([0-9.]+)', line)
            if m3:
                owhw = float(m3.group(1))
    # **등록된 확인 조건** — 분자·분모 각자의 짝표가 의도대로인가 (검사 9)
    # !! 09-05: 이 if/else 를 넣는 편집이 **조용히 실패**했고(str.replace 미매칭)
    #    구문 검사만 통과해 분모가 분자의 규칙으로 판정됐습니다. 그래서 assert 를 답니다.
    if local_ff:
        applied = (hwhw in (None, 0.0)) and (owhw in (None, 0.0))
    else:
        applied = hwhw is not None and abs(hwhw - 22.1417) < 1e-3
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
    if '--controls' in sys.argv:
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

    water_rows, gas_rows, w3_rows, hw_rows, cur_rows = [], [], [], [], []
    # ---- (8) 대조 분리 -----------------------------------------------------
    # `WATER_FIX_20260906.md` §3 ②: **대조 4건 재실행 불필요.**
    # 그리고 `hwnone`/`current` 쌍은 힘장 수정 뒤 **질문 자체가 사라졌습니다** —
    # 그 둘은 *"지역 사본으로 Hw 를 끄면 K_H 가 얼마나 달라지는가"*(D = 8.63)를
    # 물었는데, 이제 **`current` 가 곧 `hwnone`** 입니다. 그대로 돌리면 같은 것을
    # 두 번 재고 비율 1.0 을 "결과" 처럼 적게 됩니다.
    #    `--controls` 를 주면 옛 4건을 함께 돕니다(진단 목적, 기본 아님).
    with_controls = '--controls' in sys.argv
    jobs = [('water', n) for n in EXT]
    if with_controls:
        print('  ⚠️ --controls: 대조 4건을 함께 돕니다. `hwnone`/`current` 는 힘장 수정 뒤\n'
              '     같은 힘장을 두 번 재는 것이라 비율 1.0 이 기대값입니다 — 진단으로만.',
              flush=True)
        jobs += ([('gas', (CONTROL_STRUCT, CONTROL_GAS))]
                 + [('water3', CONTROL_STRUCT)]
                 + [('hwnone', CONTROL_STRUCT)]
                 + [('current', CONTROL_STRUCT)])
    else:
        print(f'  대조 4건 **제외** (WATER_FIX §3 ② "재실행 불필요"). '
              f'필요하면 `--controls`. 이번 작업 {len(jobs)}건.', flush=True)
    with Pool(WORKERS) as p:
        for kind, r in p.imap_unordered(_dispatch, jobs, chunksize=1):
            {'water': water_rows, 'gas': gas_rows, 'water3': w3_rows,
             'hwnone': hw_rows, 'current': cur_rows}[kind].append(r)
            v = r['KH_water'] if kind in ('water', 'hwnone', 'current') else r['KH']
            lbl = (r['name'] if kind == 'water'
                   else f"{r['name']}/{r['gas']}" if kind == 'gas'
                   else f"{r['name']}/물3자리" if kind == 'water3'
                   else f"{r['name']}/Hw-none" if kind == 'hwnone'
                   else f"{r['name']}/현행(분모)")
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
               'rows': hw_rows, 'denominator_rows': cur_rows},
              open(f4, 'w'), ensure_ascii=False, indent=2)

    ok = len([r for r in water_rows if r['ok']])
    print(f'\n[OK] 확장 {ok}/{len(EXT)} -> {f1}', flush=True)
    print(f'[OK] 대조 CO2 {len([r for r in gas_rows if r["ok"]])}/1 -> {f2}', flush=True)
    print(f'[OK] 대조 물3자리 {len([r for r in w3_rows if r["ok"]])}/1 -> {f3}', flush=True)
    for r in hw_rows:
        if not r['ff_applied']:
            print('  !! Hw-none 대조: **지역 힘장이 안 먹었습니다** '
                  f"(Hw-Hw eps {r['HwHw_eps']}, Ow-Hw eps {r['OwHw_eps']}). "
                  'K_H 를 쓰지 마십시오.', flush=True)
    print(f'[OK] 대조 Hw-none {len([r for r in hw_rows if r["ok"]])}/1 '
          f'+ 분모(현행) {len([r for r in cur_rows if r["ok"]])}/1 -> {f4}', flush=True)
    if hw_rows and cur_rows and hw_rows[0]['ok'] and cur_rows[0]['ok']:
        num, den = hw_rows[0], cur_rows[0]
        D = den['KH_water'] / num['KH_water']
        rel = ((den['KH_water_err'] / den['KH_water']) ** 2
               + (num['KH_water_err'] / num['KH_water']) ** 2) ** 0.5
        print(f'  D = K_H(현행)/K_H(수정) = **{D:.3f}**  상대± {rel*100:.1f}%  '
              f'(창 0.67~1.5 / 지배 D>=3 또는 <=0.33)', flush=True)
    return 0


def _dispatch(job):
    kind, payload = job
    if kind == 'water':
        return kind, T.run_one(payload)
    if kind == 'gas':
        return kind, run_gas(payload)
    if kind == 'water3':
        return kind, run_water3(payload)
    return kind, run_water_ff(payload, kind == 'hwnone')


if __name__ == '__main__':
    sys.exit(main())

