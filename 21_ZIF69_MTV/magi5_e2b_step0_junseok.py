# -*- coding: utf-8 -*-
"""MAGI-005 E-2b 0단계 (Junseok) — RASPA 가 실행 폴더(cwd)의 <FrameworkName>.block 을 읽는가. ASSIGN_MAGI5B §E-2b.

두 길을 다 잰다(ASSIGN_DENSW §2-1 의 규율):
  cwd_block      cwd 에 임의 1점 .block (0.5 0.5 0.5 · 1.0 Å) → .data 에 "Pockets are blocked" · N = 1 이어야 함
  no_block_file  같은 입력, .block 없음           → stderr 에 "'Blocking-pocket' file not found" · .data "NOT blocked" 예상
                 (조용한 실패 ① 의 실측 — run_one 은 stderr 를 버리므로 회수 관문이 .data 줄이어야 하는 이유)
$RASPA_DIR/share/raspa/structures/block/ 은 이 기기에 없다 → cwd_block 이 N = 1 이면 출처는 cwd 뿐.
Widom N₂ 100 사이클(초기화 0) — 값은 쓰지 않는다. 입력은 run_aryl_gcmc.run_one 의 Widom 틀 + 성분 절 두 줄.
"""
import glob
import json
import os
import re
import subprocess
import sys
import time
import zipfile

HERE = '/home/mangwon/mof_project/21_ZIF69_MTV'
sys.path.insert(0, HERE)
import run_aryl_gcmc as rg   # noqa: E402

NAME = '2016_Co__pts_3_ASR_5'
BASE = os.path.join(HERE, 'magi5_e2b_runs')
SIM = '/home/mangwon/miniconda3/envs/czeromof/bin/simulate'
SHARE_BLOCK = os.path.join(os.environ['RASPA_DIR'], 'share', 'raspa', 'structures', 'block')


def write_input(d, na, nb, nc):
    with open(os.path.join(d, 'simulation.input'), 'w') as f:
        f.write(f"""SimulationType                MonteCarlo
NumberOfCycles                100
NumberOfInitializationCycles  0
PrintEvery                    100
RestartFile                   no

Forcefield                    UFF_MOF
CutOff                        {rg.CUTOFF}
UseChargesFromCIFFile         yes
ChargeMethod                  Ewald
EwaldPrecision                1e-6

Framework 0
FrameworkName                 {NAME}
UnitCells                     {na} {nb} {nc}
ExternalTemperature           298.0
ExternalPressure              1e-5

Component 0 MoleculeName              N2
            MoleculeDefinition        TraPPE
            BlockPockets              yes
            BlockPocketsFileName      {NAME}
            WidomProbability          1.0
            CreateNumberOfMolecules   0
""")


def main():
    assert not os.path.exists(os.path.join(SHARE_BLOCK, NAME + '.block'))
    print(f'  share block 디렉터리 {SHARE_BLOCK}: {"있음" if os.path.isdir(SHARE_BLOCK) else "없음"}', flush=True)
    z = zipfile.ZipFile(os.path.join(HERE, 'core_pop_cifs.zip'))
    cif_bytes = z.read(NAME + '.cif')
    cases = ('cwd_block', 'no_block_file')
    procs = {}
    for c in cases:
        d = os.path.join(BASE, f'step0_{c}')
        if os.path.exists(d):
            print(f'!! {d} 이미 있음 — 중단', flush=True)
            return 1
        os.makedirs(d)
        open(os.path.join(d, NAME + '.cif'), 'wb').write(cif_bytes)
        na, nb, nc = rg.unit_cells(rg.read(os.path.join(d, NAME + '.cif')))
        write_input(d, na, nb, nc)
        if c == 'cwd_block':
            open(os.path.join(d, NAME + '.block'), 'w').write('1\n0.5 0.5 0.5 1.0\n')
        procs[c] = (d, subprocess.Popen([SIM, 'simulation.input'], cwd=d, stdout=subprocess.DEVNULL,
                                        stderr=open(os.path.join(d, 'stderr.txt'), 'w')), time.time())
        print(f'  착수 {c}  단위셀 {na}×{nb}×{nc}  {time.strftime("%H:%M:%S")}', flush=True)
        time.sleep(2)
    res = {}
    for c, (d, p, t0) in procs.items():
        rc = p.wait(timeout=1800)
        f = (glob.glob(os.path.join(d, 'Output', 'System_0', '*.data')) or [None])[0]
        txt = open(f, encoding='utf-8', errors='ignore').read() if f else ''
        m = re.search(r'Number of pockets blocked in a unitcell:\s*(\d+)', txt)
        blocked_line = re.search(r'Pockets are (NOT )?blocked for this component', txt)
        err = open(os.path.join(d, 'stderr.txt'), encoding='utf-8', errors='ignore').read().strip()
        res[c] = {'rc': rc, 'minutes': round((time.time() - t0) / 60, 2),
                  'n_blocked_per_uc': int(m.group(1)) if m else None,
                  'pockets_line': blocked_line.group(0) if blocked_line else None,
                  'finished': 'Simulation finished' in txt,
                  'stderr': err[:300], 'data': os.path.relpath(f, HERE) if f else None}
        print(f'  [{c}] rc={rc} N={res[c]["n_blocked_per_uc"]} · "{res[c]["pockets_line"]}" · 표지={res[c]["finished"]} · '
              f'stderr="{res[c]["stderr"][:120]}" · {res[c]["minutes"]} 분', flush=True)
    a, b = res['cwd_block'], res['no_block_file']
    verdict = ('cwd 에서 읽음 → 환경 변경 없음, 진행 가능' if (a['n_blocked_per_uc'] or 0) > 0 and a['pockets_line'] == 'Pockets are blocked for this component'
               else 'cwd 에서 안 읽음 → 멈추고 보고(환경 변경 = 사용자 결정)')
    json.dump({'test': 'MAGI-005 E-2b 0단계 — cwd .block 읽기', 'share_block_dir_exists': os.path.isdir(SHARE_BLOCK),
               'cases': res, 'result': verdict}, open(os.path.join(BASE, 'step0_result.json'), 'w', encoding='utf-8'),
              indent=2, ensure_ascii=False)
    print(f'  결과: {verdict}', flush=True)
    return 0


if __name__ == '__main__':
    sys.exit(main())
