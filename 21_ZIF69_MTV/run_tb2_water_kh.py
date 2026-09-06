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

사용:  ~/miniconda3/envs/czeromof/bin/python run_tb2_water_kh.py A|B|ALL
       (`python3` 에는 ase 가 없습니다. `ALL` 은 단일 기기 전용입니다.)
"""
import hashlib, json, os, re, shutil, socket, subprocess, sys
from multiprocessing import Pool

HERE = os.path.dirname(os.path.abspath(__file__))
CHARGED = os.path.join(HERE, 'charged_v3')
WATER_DEF = os.path.join(HERE, '..', '19_WaterCompetition', 'water.def')
SIMULATE = shutil.which('simulate') or os.path.expanduser(
    '~/miniconda3/envs/czeromof/bin/simulate')
# WATER_FIX_20260906.md §2 — **수정 힘장 계열은 새 경로**. 러너의 이어받기는
# 출력 존재만 보고 힘장을 안 봅니다(CLAUDE.md §3). 옛 경로를 그대로 두면
# 결함판 출력을 조용히 주워 옵니다.
RUNS = os.path.join(HERE, 'tb2w_runs')
OUT = os.path.join(HERE, 'v3w_water_kh')

def _ff_path():
    """힘장 실물 경로. **기기마다 다릅니다.**

    ⚠️ 초판은 `~/RASPA/simulations/...` 로 박혀 있었습니다. 이 러너를 다른 기기가
    import 하면(데스크탑 `run_tb2w.py`) **그 기기의 RASPA 가 다른 곳에 있을 때
    md5 관문이 파일을 못 찾아 `return 4` 로 착수를 막습니다.** 자동 착수 체인에서는
    아무도 안 보고 있는 사이에 그렇게 됩니다.
    RASPA 자신이 쓰는 `$RASPA_DIR` 를 먼저 봅니다.
    """
    cands = []
    if os.environ.get('RASPA_DIR'):
        cands.append(os.path.join(os.environ['RASPA_DIR'], 'share', 'raspa',
                                  'forcefield', 'UFF_MOF',
                                  'force_field_mixing_rules.def'))
    cands.append(os.path.expanduser(
        '~/RASPA/simulations/share/raspa/forcefield/UFF_MOF/'
        'force_field_mixing_rules.def'))
    for c in cands:
        if os.path.exists(c):
            return c
    return cands[0]


FF_PATH = _ff_path()
FF_MD5 = '8e8ec933f9013c7e932da04dc256efd3'      # WATER_FIX §1 ①
FF_TAG = 'UFF_MOF+HwLw_none_20260906'
CONDA_PY = '~/miniconda3/envs/czeromof/bin/python'

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


def count_sites(water_def):
    """`water.def` 의 Ow/Hw/Lw 줄 수. **원본이 아니라 넘겨준 경로**를 셉니다."""
    if not os.path.exists(water_def):
        return -1
    return sum(1 for ln in open(water_def, encoding='utf-8', errors='ignore')
               if len(ln.split()) > 4 and ln.split()[1] in ('Ow', 'Hw', 'Lw'))


def read_kh(path, comp='water'):
    """헨리 계수를 **성분 이름으로** 읽습니다. 옛 판의 결함 둘을 막습니다.

    (ㄷ) 옛 판은 성분을 안 보고 `Average Henry coefficient:` 의 **마지막 일치**를
         썼습니다. 성분이 둘이면 어느 것인지 코드에 없습니다.
    (ㄹ) 한 파일 안 다중 일치도 **뒤엣것이 조용히 이겼습니다.** 여기서는 세어서
         2개 이상이면 **거부하고 행 번호를 돌려줍니다.**
    """
    cur, hits = None, []
    for i, ln in enumerate(open(path, encoding='utf-8', errors='ignore'), 1):
        m = re.search(r'Component\s+\d+\s*\[\s*(\S+?)\s*\]', ln)
        if m:
            cur = m.group(1)
        if 'Average Henry coefficient:' in ln:
            g = re.search(r':\s*([0-9.eE+-]+)\s*\+/-\s*([0-9.eE+-]+)', ln)
            if g:
                hits.append((i, cur, float(g.group(1)), float(g.group(2))))
    mine = [h for h in hits if h[1] == comp]
    if not mine:
        return None, None, (f"성분 '{comp}' 의 헨리 계수 없음 "
                            f"(찾은 성분: {sorted({h[1] for h in hits})})")
    if len(mine) > 1:
        return None, None, (f"성분 '{comp}' 일치가 {len(mine)}개 — "
                            f"행 {[h[0] for h in mine]} 값 {[h[2] for h in mine]}")
    return mine[0][2], mine[0][3], None


def read_ff_header(path):
    """RASPA 가 **인쇄한** 쌍으로 힘장을 확인합니다 (WATER_FIX §1 ③).

    ⚠️ 쌍 이름은 **오른쪽 정렬로 채워집니다** — 실제 줄이
        `     Hw -      Hw [ZERO_POTENTIAL]`
    이라 `'Hw - Hw' in ln` 은 **절대 안 맞습니다**(09-06 실측).

    ⚠️ 그리고 **`22.14170` 을 grep 하지 마십시오.** 고친 판의 출력에도 그 수가
       **12,246번** 나옵니다 — 골격 수소 `H_` 의 정당한 UFF 값입니다. 결함은 그
       수의 존재가 아니라 **`Hw` 쌍이 그 값을 갖는 것**이었습니다.
    """
    RX = {a + b: re.compile(r'^\s*' + a + r'\s+-\s+' + b + r'\s')
          for a, b in (('Hw', 'Hw'), ('Ow', 'Hw'), ('Ow', 'Lw'),
                       ('Lw', 'Lw'), ('Ow', 'Ow'))}
    out = {}
    with open(path, encoding='utf-8', errors='ignore') as f:
        for ln in f:
            for k, rx in RX.items():
                if k not in out and rx.match(ln):
                    if k == 'OwOw':
                        g = re.findall(r'[-+]?\d*\.?\d+(?:[eE][-+]?\d+)?', ln)
                        out['OwOw'] = ln.strip()[:100]
                        out['OwOw_eps'] = float(g[1]) if len(g) > 1 else None
                    else:
                        out[k] = ('ZERO_POTENTIAL' if 'ZERO_POTENTIAL' in ln
                                  else ln.strip()[:100])
            if len(set(RX) & set(out)) == len(RX):
                break
    out['ok'] = (all(out.get(k) == 'ZERO_POTENTIAL'
                     for k in ('HwHw', 'OwHw', 'OwLw', 'LwLw'))
                 and out.get('OwOw_eps') is not None
                 and abs(out['OwOw_eps'] - 89.633) < 1e-3)
    return out


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
PrintEvery                    {CYCLES // 10}
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
    od = os.path.join(d, 'Output', 'System_0')
    outs = sorted(os.path.join(od, x) for x in os.listdir(od)
                  if x.endswith('.data')) if os.path.isdir(od) else []
    if len(outs) != 1:
        # 파일이 둘 이상이면 어느 것이 이번 실행인지 **모릅니다.** 옛 판은
        # 전부 훑어 마지막 일치를 썼습니다 — 조용히 다른 실행을 읽는 길입니다.
        return {'name': name, 'KH_water': None, 'KH_water_err': None,
                'unit_cells': [na, nb, nc], 'ok': False,
                'error': f'출력 .data 가 {len(outs)}개 — 1개여야 합니다: {outs}'}
    kh, ekh, err = read_kh(outs[0], comp='water')
    ff = read_ff_header(outs[0])
    nsite_run = count_sites(os.path.join(d, 'water.def'))
    if nsite_run != 5:
        err = (err or '') + f' | 실행 폴더 water.def 사이트 {nsite_run} (5여야 함)'
    return {'name': name, 'KH_water': kh, 'KH_water_err': ekh,
            'unit_cells': [na, nb, nc], 'forcefield': FF_TAG, 'ff_check': ff,
            'water_sites_in_rundir': nsite_run,
            'ok': kh is not None and ff.get('ok') and nsite_run == 5,
            **({'error': err} if err else {})}


def main():
    # (ㄱ) ase 관문 — **여기서** 막습니다.
    # `unit_cells()` 가 함수 안에서 `from ase.io import read` 하고 그 함수는
    # Pool 워커에서 처음 불립니다. 그래서 옛 판은 **폴더를 만들고 CIF·water.def 를
    # 복사한 뒤에야** 터졌습니다. 09-06 실측: 이 파일의 독스트링이 시키는
    # `python3` 에 ase 가 없습니다(conda 환경 셋에만 있음).
    try:
        import ase  # noqa: F401
    except ImportError:
        print(f'!! ase 가 없습니다. 이 인터프리터로 도십시오:\n'
              f'   {CONDA_PY} {os.path.basename(__file__)} A|B|ALL', flush=True)
        return 3

    # 착수 전 힘장 관문 (WATER_FIX §1 ①)
    if os.path.exists(FF_PATH):
        m = hashlib.md5(open(FF_PATH, 'rb').read()).hexdigest()
        print(f'  힘장 md5 {m}  ({"**일치**" if m == FF_MD5 else "**불일치 — 중단**"})',
              flush=True)
        if m != FF_MD5:
            return 4
    else:
        print(f'!! 힘장 파일 없음: {FF_PATH}', flush=True); return 4

    if len(sys.argv) < 2 or sys.argv[1] not in ('A', 'B', 'ALL'):
        print(f'사용: {CONDA_PY} run_tb2_water_kh.py A|B|ALL\n'
              '      기본값 없음 — 대상을 정하는 인자라 반드시 명시. '
              'ALL 은 단일 기기 전용.', flush=True)
        return 2
    half = sys.argv[1]
    if half == 'ALL':
        # (ㅁ) `ALL` 은 **한 기기 전용**입니다. 산출물 이름이 호스트명으로 갈려
        # 파일은 안 겹치지만 **32조성이 통째로 중복**되고, 같은 조성의 서로 다른
        # 실현이 두 파일에 남습니다. A/B 교차 분담이 있는 이유가 그것입니다.
        print('  ⚠️ ALL 은 **단일 기기 전용**입니다. 두 기기로 나눌 때는 A / B 를 쓰십시오.',
              flush=True)
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
    ffc = next((r['ff_check'] for r in rows if r.get('ff_check', {}).get('ok')), None)
    bad = [r['name'] for r in rows if not r['ok']]
    print(f'  [힘장 확인] {"통과" if ffc else "**실패 — K 값을 쓰지 마십시오**"}'
          + (f'  실패 행: {bad}' if bad else ''), flush=True)
    json.dump({'half': half, 'tag': tag,
               # (ㅂ) 힘장 출처를 최상단과 **행마다** 둘 다 남깁니다. 이 파일은
               # dict 라 최상단 키가 판독기를 안 깨뜨립니다(water_results.json 과
               # 다른 점). 행 표기는 행이 다른 파일로 복사될 때를 위한 것입니다.
               'forcefield': FF_TAG, 'ff_md5': FF_MD5, 'ff_path': FF_PATH,
               'ff_check': ffc,
               # 배열 대신 키 이름으로 — 배열은 어느 쪽이 초기화인지 안 알려 준다.
               # 09-05 에 '5000+2000' 이 반대로 읽힌 사례가 있었고, 독스트링·로그만
               # 고치고 **산출물을 안 고치면** 그 함정이 파일에 그대로 남는다.
               'NumberOfInitializationCycles': INIT,
               'NumberOfCycles': CYCLES,
               'note': 'Widom 물 K_H. 문턱 5e-6 mmol/g/Pa 는 TIP4P 기준 — '
                       'TIP5P-Ew 값에 적용한다는 한정어 필수',
               'rows': sorted(rows, key=lambda x: x['name'])}, open(f, 'w'),
              ensure_ascii=False, indent=2)
    print(f'\n[OK] {len([r for r in rows if r["ok"]])}/{len(sel)} -> {f}', flush=True)
    return 0


if __name__ == '__main__':
    sys.exit(main())
