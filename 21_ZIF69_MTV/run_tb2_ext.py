"""T-B2 확장 — 관문 탈락 saIm 7종 물 K_H (②-전용) + `base` CO2 Widom 대조 1건.

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

[대조] `base` CO2 Widom 1건은 **다른 질문**입니다 — 물 K_H 가 전량 문턱의
       75~512배로 나온 것이 "물이 비싸다" 인지 "**우리 물 정의**가 비싸다"
       인지 가릅니다. 같은 구조·같은 자로 CO2 를 재서 비교합니다.
       측정 전 예상을 적어 둡니다: **문턱 5e-6 은 TIP4P 기준**이므로 5자리
       TIP5P-Ew 가 계통적으로 크면 CO2 는 그만큼 크지 않아야 합니다.

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
    print(f'T-B2 확장 — 관문 탈락 saIm {len(EXT)}종 (②-전용) '
          f'+ {CONTROL_STRUCT} {CONTROL_GAS} Widom 대조 1건, 워커 {WORKERS}', flush=True)
    print(f'  자: NumberOfCycles {T.CYCLES} / '
          f'NumberOfInitializationCycles {T.INIT}, UFF_MOF, 컷오프 {T.CUTOFF}, '
          f'Ewald 1e-6 — A/B 와 동일', flush=True)
    print(f'  물 정의 사이트 {nsite}개 (TIP5P-Ew 는 5)', flush=True)
    print('  확장 대상: ' + ', '.join(EXT), flush=True)

    water_rows, gas_rows = [], []
    jobs = [('water', n) for n in EXT] + [('gas', (CONTROL_STRUCT, CONTROL_GAS))]
    with Pool(WORKERS) as p:
        for kind, r in p.imap_unordered(_dispatch, jobs, chunksize=1):
            (water_rows if kind == 'water' else gas_rows).append(r)
            v = r['KH_water'] if kind == 'water' else r['KH']
            lbl = r['name'] if kind == 'water' else f"{r['name']}/{r['gas']}"
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

    ok = len([r for r in water_rows if r['ok']])
    print(f'\n[OK] 확장 {ok}/{len(EXT)} -> {f1}', flush=True)
    print(f'[OK] 대조 {len([r for r in gas_rows if r["ok"]])}/1 -> {f2}', flush=True)
    return 0


def _dispatch(job):
    kind, payload = job
    return (kind, T.run_one(payload)) if kind == 'water' else (kind, run_gas(payload))


if __name__ == '__main__':
    sys.exit(main())
