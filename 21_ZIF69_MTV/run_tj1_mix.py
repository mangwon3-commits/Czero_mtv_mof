# -*- coding: utf-8 -*-
"""T-J1′ — 이원 GCMC CO₂/N₂ = 0.15/0.85, 전압 1 bar, 298 K. 헨리 S 가 작동점 순위를 지키는가(Junseok R1 J-13).

배정: `ASSIGN_MAGI5B_20260925.md` §laptop 5차(07:38) · 등록: `MAGI/MAGI-005_R1_junseok.md` §T-J1′ + R3 J-13(대조 교체).
예측·기각은 그 원문 그대로 — 이 러너는 값과 표지만 냅니다. 판정은 종합자.

[자]  초기화 5,000 + 생산 15,000 · UFF_MOF(md5 8e8ec933) · PACMAN DDEC6(CIF) · 12 Å · Ewald 1e-6 · `unit_cells()` · 강체 · 298 K ·
      ExternalPressure 1e5 Pa · Component 0 CO₂ MolFraction 0.15 · Component 1 N₂ MolFraction 0.85 ·
      이동 = run_humid_wc.py 의 MolFraction 블록과 같은 것(Translation 0.5 · Rotation 0.3 · Reinsertion 0.1 · Swap 1.0). 차단 없음.

[§0 결함 방지 — 배정 필수]
    · 완주 표지 `Simulation finished`(run_aryl_gcmc.finished) **그리고** 두 성분 적재가 **각각 정확히 한 번** 인쇄됐을 때만 ok.
      (run_water.parse_components 는 성분별 '첫 일치' 를 쓰는데, 지금 그 문구가 최종 요약에만 한 번 나오는 것은 **우연의 보호**입니다 —
       CLAUDE.md §0 "우연이 지켜 주는 자리는 지켜지는 게 아닙니다". 여기서는 세어서 1 이 아니면 거부합니다.)
    · 이어받기도 같은 조건. RASPA 반환코드를 기록하고 0 이 아니면 값이 있어도 '반환코드' 표지.
    · ContinueAfterCrash 안 씀(run_water 주석: 그 경로에서 SIGSEGV 사례).
[운영] LPT = N_super(원자 수 × 셀 수) 내림차순 · submit + as_completed · 행마다 중간 저장 · 착수 간격 15 s(seed).
"""
import glob, json, math, os, re, shutil, subprocess, sys, time
from concurrent.futures import ProcessPoolExecutor, as_completed

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import run_aryl_gcmc as rg          # noqa: E402  finished · unit_cells · occupied_by_other · SIMULATE · CUTOFF
from ff_gate import FF_MD5, md5_gate  # noqa: E402
from ase.io import read             # noqa: E402

TEMP, P_TOT, X_CO2 = 298.0, 1.0e5, 0.15
CYCLES, INIT = 15000, 5000
WORKERS = int(os.environ.get('TJ1_WORKERS', '8'))
STAGGER = 15.0
MACHINE = os.environ.get('TJ1_MACHINE', 'laptop')
RUNS = os.path.join(HERE, 'tj1_mix_runs')
OUT = os.path.join(HERE, f'results_tj1_mix_{MACHINE}.json')

OURS = ['base', 'nbIm100', 'saIm050', 'mslm050', 'sa50nb50']
CORE = [('2016_Co__sql_2_FSR_19', 'L<0.2'), ('2024_Ni__sql_2_FSR_4', 'L<0.2'), ('2017_Zn__dia_3_FSR_1', 'L<0.2(주)'),
        ('2012_Co__dia_3_ASR_3', '대조'), ('2010_Zn__pts_3_ASR_1', '대조')]
# 07:41 보완(ASSIGN §laptop 5차 보완 줄, 자료 0건): 깨끗한 대조 1 을 **따로 뒤에** 붙임 — 도는 10 작업을 재기동하지 않기 위해 환경변수로.
#   TJ1_EXTRA="이름:군"  → 대상에 더함 · TJ1_ONLY_EXTRA=1 → 추가분만 돌림(출력 파일은 TJ1_MACHINE 으로 가름)
if os.environ.get('TJ1_EXTRA'):
    CORE = CORE + [tuple(x.split(':', 1)) for x in os.environ['TJ1_EXTRA'].split(',') if x]
ONLY_EXTRA = bool(os.environ.get('TJ1_ONLY_EXTRA'))
# 결과 파일 머리 — E-21(`run_e21_mix.py`)이 import 해 덮어씀. T-J1′ 값은 그대로.
TEST = 'T-J1′ 이원 공동 지표 S_mix/S_Henry'
ASSIGN_REF = 'ASSIGN_MAGI5B_20260925.md §laptop 5차'
REG_REF = 'MAGI/MAGI-005_R1_junseok.md §T-J1′ + R3 J-13'


def targets():
    t = []
    v3 = {r['name']: r for r in json.load(open(os.path.join(HERE, 'results_v3.json')))['rows']}
    mx = json.load(open(os.path.join(HERE, 'results_v4mix.json')))
    mx = {r['name']: r for r in (mx['rows'] if isinstance(mx, dict) else mx) if isinstance(r, dict)}
    for n in OURS:
        src, r = ('results_v4mix.json', mx[n]) if (n == 'sa50nb50' or n not in v3) else ('results_v3.json', v3[n])
        L = r['loading_015bar'] / (r['KH_CO2'] * 15000.0)
        t.append({'name': n, 'cif': os.path.join(HERE, 'charged_v3', n + '_DDEC6.cif'), 'group': '우리', 'dim': 3,
                  'S_Henry': r['selectivity'], 'S_Henry_err': r.get('selectivity_err'), 'S_Henry_src': src, 'L': L,
                  'L_src': f'{src} loading_015bar/(KH_CO2·15 kPa)'})
    ann = {r['file']: r for r in json.load(open(os.path.join(HERE, 'core_pop_annotated.json')))['rows']}
    for n, g in CORE:
        r = ann[n + '.cif']
        t.append({'name': n, 'cif': os.path.join(HERE, 'core_pop_cifs', n + '.cif'), 'group': g, 'dim': r.get('dim'),
                  'S_Henry': r['selectivity'], 'S_Henry_err': None, 'S_Henry_src': 'core_pop_annotated.json(§AV Widom)',
                  'L': r.get('L'), 'L_src': 'core_pop_annotated.json L', 'flexible': r.get('flexible')})
    if ONLY_EXTRA:
        extra = {n for n, _ in CORE[5:]}
        t = [x for x in t if x['name'] in extra]
    for x in t:
        a = read(x['cif']); uc = rg.unit_cells(a)
        x['unit_cells'] = uc; x['N_super'] = len(a) * uc[0] * uc[1] * uc[2]
    return sorted(t, key=lambda x: -x['N_super'])            # LPT


def loads(path):
    """성분별 'Average loading absolute [mol/kg framework]' — 세어서 각 1 개일 때만."""
    cur, hits = None, {}
    for ln in open(path, encoding='utf-8', errors='ignore'):
        m = re.search(r'Component\s+\d+\s+\[(\w+)\]', ln)
        if m:
            cur = m.group(1)
        if cur and 'Average loading absolute [mol/kg framework]' in ln:
            v = re.search(r':?\s*([0-9.eE+-]+)\s*\+/-\s*([0-9.eE+-]+)', ln)
            if v:
                hits.setdefault(cur, []).append((float(v.group(1)), float(v.group(2))))
    return hits


def seed_of(p):
    for ln in open(p, encoding='utf-8', errors='ignore'):
        m = re.match(r'\s*Random number seed:\s*(\d+)', ln)
        if m:
            return int(m.group(1))


def judge_output(p):
    if not rg.finished(p):
        return None, '미완주'
    h = loads(p)
    if set(h) != {'CO2', 'N2'} or any(len(v) != 1 for v in h.values()):
        return None, f"적재줄 이상 {{{', '.join(f'{k}:{len(v)}' for k, v in h.items())}}}"
    return {'CO2': h['CO2'][0], 'N2': h['N2'][0]}, 'ok'


def run_one(arg):
    idx, x = arg
    name = x['name']; d = os.path.join(RUNS, f'mix_{name}')
    done = glob.glob(os.path.join(d, 'Output', 'System_0', '*.data'))
    if done:
        v, st = judge_output(done[0])
        if st == 'ok':
            return name, v, 'cached', None, seed_of(done[0]), None
        return name, None, f'실행폴더에 미완 출력({st}) — 섞지 않으려 착수 안 함(CLAUDE.md §3)', None, None, None
    if rg.occupied_by_other(d):
        return name, None, '다른세션실행중', None, None, None
    time.sleep((idx % max(1, WORKERS)) * STAGGER)
    os.makedirs(d, exist_ok=True)
    fw = os.path.basename(x['cif'])[:-4]
    shutil.copy(x['cif'], os.path.join(d, fw + '.cif'))
    na, nb, nc = x['unit_cells']
    moves = ('            TranslationProbability    0.5\n'
             '            RotationProbability       0.3\n'
             '            ReinsertionProbability    0.1\n'
             '            SwapProbability           1.0\n'
             '            CreateNumberOfMolecules   0\n')
    with open(os.path.join(d, 'simulation.input'), 'w') as f:
        f.write(f"""SimulationType                MonteCarlo
NumberOfCycles                {CYCLES}
NumberOfInitializationCycles  {INIT}
PrintEvery                    {CYCLES}
RestartFile                   no

Forcefield                    UFF_MOF
CutOff                        {rg.CUTOFF}
UseChargesFromCIFFile         yes
ChargeMethod                  Ewald
EwaldPrecision                1e-6

Framework 0
FrameworkName                 {fw}
UnitCells                     {na} {nb} {nc}
ExternalTemperature           {TEMP}
ExternalPressure              {P_TOT}

Component 0 MoleculeName              CO2
            MoleculeDefinition        TraPPE
            MolFraction               {X_CO2:.6f}
{moves}
Component 1 MoleculeName              N2
            MoleculeDefinition        TraPPE
            MolFraction               {1 - X_CO2:.6f}
{moves}""")
    t0 = time.time()
    try:
        cp = subprocess.run([rg.SIMULATE, 'simulation.input'], cwd=d, stdout=subprocess.DEVNULL,
                            stderr=subprocess.DEVNULL, timeout=259200, check=False)
        rc = cp.returncode
    except subprocess.TimeoutExpired:
        return name, None, 'timeout', None, None, round((time.time() - t0) / 60, 1)
    mins = round((time.time() - t0) / 60, 1)
    outs = glob.glob(os.path.join(d, 'Output', 'System_0', '*.data'))
    if len(outs) != 1:
        return name, None, f'.data {len(outs)}개', rc, None, mins
    v, st = judge_output(outs[0])
    if st == 'ok' and rc != 0:
        st = f'반환코드 {rc}(값 있음 — 표지)'
    if st == 'ok':
        for sub in ('VTK', 'Movies', 'Restart'):
            shutil.rmtree(os.path.join(d, sub), ignore_errors=True)
    return name, v, st, rc, seed_of(outs[0]), mins


def row_of(x, v, st, rc, seed, mins):
    r = {k: x[k] for k in ('name', 'group', 'dim', 'S_Henry', 'S_Henry_err', 'S_Henry_src', 'L', 'L_src', 'unit_cells', 'N_super')}
    r.update({'cif': os.path.relpath(x['cif'], HERE), 'status': st, 'returncode': rc, 'seed': seed, 'minutes': mins,
              'ff_md5': FF_MD5, 'machine': MACHINE, 'flexible': x.get('flexible')})
    if x['group'] != '우리' and x['dim'] == 2:
        r['flag'] = '2D 층간 틈(맹점 ③)'
    if v:
        (nc, ec), (nn, en) = v['CO2'], v['N2']
        r.update({'N_CO2': nc, 'N_CO2_err': ec, 'N_N2': nn, 'N_N2_err': en})
        if nc > 0 and nn > 0:
            s = (nc / nn) / (X_CO2 / (1 - X_CO2)); rel = math.hypot(ec / nc, en / nn)
            r.update({'S_mix': s, 'S_mix_err': s * rel, 'ratio_Smix_over_SHenry': s / x['S_Henry'],
                      'ratio_err': s * rel / x['S_Henry']})
            if x.get('S_Henry_err'):   # 합성 ± (T-J1′ 판정 뒤 종합자 병기 방식) — ratio_err 는 S_mix ± 만
                r['ratio_err_with_SHenry'] = s / x['S_Henry'] * math.hypot(rel, x['S_Henry_err'] / x['S_Henry'])
        r['finished'] = time.strftime('%F %T')
    return r


def main():
    ok, m = md5_gate()
    if not ok:
        return 3
    T = targets()
    for x in T:
        if not os.path.exists(x['cif']):
            print(f"!! CIF 없음 {x['cif']}", flush=True); return 2
    os.makedirs(RUNS, exist_ok=True)
    print(f'T-J1′ 이원 GCMC CO₂/N₂ {X_CO2}/{1 - X_CO2:.2f} · {P_TOT:.0f} Pa · {TEMP} K · {INIT}+{CYCLES} · 워커 {WORKERS} · md5 {m}', flush=True)
    for x in T:
        print(f"  {x['name']:24s} N_super {x['N_super']:6d} 셀 {x['unit_cells']} · S_Henry {x['S_Henry']:.1f} ({x['S_Henry_src']}) · L {x['L']}", flush=True)
    rows = {x['name']: row_of(x, None, 'pending', None, None, None) for x in T}
    bx = {x['name']: x for x in T}

    def save(note=''):
        json.dump({'test': TEST, 'assign': ASSIGN_REF,
                   'registration': REG_REF,
                   'protocol': {'mix': {'CO2': X_CO2, 'N2': 1 - X_CO2}, 'P_Pa': P_TOT, 'T_K': TEMP, 'init': INIT, 'cycles': CYCLES,
                                'forcefield': 'UFF_MOF', 'ff_md5': FF_MD5, 'cutoff': rg.CUTOFF, 'ewald': 1e-6, 'blocking': False},
                   'note': ('판정 없음(종합자). ± 는 RASPA 95 % CI, S_mix ± 는 두 적재의 상대 ± 제곱합. '
                            'ok = 완주 표지 + 두 성분 적재 각 1줄 + 반환코드 0. ' + note),
                   'rows': [rows[k] for k in sorted(rows, key=lambda k: -bx[k]['N_super'])]},
                  open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    save('진행 중')
    t0 = time.time()
    with ProcessPoolExecutor(max_workers=WORKERS) as ex:
        futs = {ex.submit(run_one, (i, x)): x['name'] for i, x in enumerate(T)}
        for fu in as_completed(futs):
            name, v, st, rc, seed, mins = fu.result()
            rows[name] = row_of(bx[name], v, st, rc, seed, mins)
            r = rows[name]
            print(f"  [{st[:28]}] {name:24s} S_mix {r.get('S_mix')} · 비 {r.get('ratio_Smix_over_SHenry')} · {mins} min · "
                  f"경과 {(time.time() - t0) / 3600:.2f} h", flush=True)
            save('진행 중')
    seeds = [r['seed'] for r in rows.values() if r.get('seed')]
    save(f'완료 · seed {len(seeds)}개 겹침 {len(seeds) - len(set(seeds))}건 · 벽시계 {(time.time() - t0) / 3600:.2f} h')
    print('저장', OUT, flush=True)
    return 0


if __name__ == '__main__':
    sys.exit(main())
