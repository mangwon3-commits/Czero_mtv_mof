# -*- coding: utf-8 -*-
"""MAGI-005 E-27b — 새 1 · 2위(−Cl · −C₂H₅ 막음)의 작동점 S_mix 를 323 K 에서. 등록 `ASSIGN_MAGI5B_20260925.md` §HKHOME 20차 + laptop 10차.
`run_e27_mix323.py`(E-27) 와 같음 — `run_tj1_mix` **수정 없이** import, 온도만 323 K. 대상은 환경변수 E27B_SET(cl | c2h5)로 가름(기기별 분담).
C₂H₅ 는 **성분별 BlockPockets**(CO₂ block1.65 · N₂ block1.82, `e28b_blocks/` = Junseok E-24c ① 산출, 구 2 × 셀 6 = 12) — E-24e 와 같은 막음.
  삽입 방법: `run_tj1_mix.run_one` 이 simulation.input 을 쓴 뒤 `subprocess.run([SIMULATE, 'simulation.input'], cwd=d)` 를 부르므로,
  그 호출을 감싸 **두 성분 절에 두 줄씩** 넣고(앵커가 정확히 한 번이 아니면 RASPA 를 안 띄움) 막음 파일을 실행 폴더로 복사.
  (`run_density_water_v3.py` 의 `_run_with_grid` 와 같은 수 — 러너 수정 없음.)
판정 전 관문(끝에 자동 기록): 완주 표지 · 두 성분 적재(러너 judge) · 반환코드 0 · 씨앗 고유 + C₂H₅ 는 성분마다 'Number of pockets blocked in a unitcell: 12' · 'Pockets are blocked for this component' · not-found 0.
"""
import glob, json, os, shutil, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import run_tj1_mix as M   # noqa: E402
from ase.io import read   # noqa: E402

SET = os.environ.get('E27B_SET', 'cl')
M.TEMP = 323.0
M.MACHINE = os.environ.get('E27B_MACHINE', 'hkhome')
M.WORKERS = int(os.environ.get('E27B_WORKERS', '3'))
M.RUNS = os.path.join(HERE, f'e27b_mix323_runs_{SET}')
M.OUT = os.path.join(HERE, f'results_e27b_mix323_{SET}_{M.MACHINE}.json')
M.TEST = f'MAGI-005 E-27b 새 1 · 2위 작동점 S_mix 323 K ({SET})'
M.ASSIGN_REF = 'ASSIGN_MAGI5B_20260925.md §HKHOME 20차 + laptop 10차'
M.REG_REF = 'ASSIGN_MAGI5B_20260925.md §HKHOME 20차 + laptop 10차 예측 (1)~(3)'
TAG = {'cl': 'e24c_cl_100', 'c2h5': 'e24c_c2h5_100'}[SET]
BLOCK = {'CO2': os.path.join(HERE, 'e28b_blocks', 'e24c_c2h5_100_block1.65.block'),
         'N2': os.path.join(HERE, 'e28b_blocks', 'e24c_c2h5_100_block1.82.block')} if SET == 'c2h5' else {}
# 러너가 S_Henry 를 숫자로 찍으므로 None 을 못 줌(04:12 첫 기동이 여기서 죽음) — **298 K** 값을 넣고 비는 인용 금지로 표지.
SH = {'cl': (128.33, 2.90, '298 K E-24c Widom ON(results_magi5_e3_e24c_cl_100_widom_hkhome.json) — 온도 다름 · 비 인용 금지'),
      'c2h5': (188.56, 4.27, '298 K E-24c 막음 Widom ON(Junseok results_e24c_och3_blockpockets_junseok.json) — 온도 다름 · 비 인용 금지')}[SET]
ANCH = {g: f"Component {i} MoleculeName              {g}\n            MoleculeDefinition        TraPPE\n" for i, g in ((0, 'CO2'), (1, 'N2'))}


def targets():
    t = []
    for k in (1, 2, 3):
        t.append({'name': f'{TAG}_s{k}', 'cif': os.path.join(HERE, 'charged_v3', f'{TAG}_DDEC6.cif'), 'group': '형판 설계(새 1 · 2위)',
                  'dim': 3, 'S_Henry': SH[0], 'S_Henry_err': SH[1], 'S_Henry_src': SH[2], 'L': None, 'L_src': '—'})
    for x in t:
        a = read(x['cif']); uc = M.rg.unit_cells(a); x['unit_cells'] = uc; x['N_super'] = len(a) * uc[0] * uc[1] * uc[2]
    return t


_real_run = M.subprocess.run


def _run_blocked(cmd, **kw):
    d = kw.get('cwd')
    if BLOCK and d and cmd and str(cmd[-1]) == 'simulation.input':
        p = os.path.join(d, 'simulation.input'); s = open(p).read()
        if 'BlockPockets' not in s:
            for g, a in ANCH.items():
                if s.count(a) != 1:
                    raise RuntimeError(f'{g} 성분 앵커가 정확히 한 번이 아님 — 막음 삽입 중단, RASPA 안 띄움')
                s = s.replace(a, a + f"            BlockPockets              yes\n            BlockPocketsFileName      c2h5_{g.lower()}\n")
            open(p, 'w').write(s)
            for g, f in BLOCK.items():
                shutil.copy(f, os.path.join(d, f'c2h5_{g.lower()}.block'))
    return _real_run(cmd, **kw)


M.subprocess.run = _run_blocked
M.targets = targets


def audit():
    rows = json.load(open(M.OUT))['rows']
    res = {'seeds_unique': len({r.get('seed') for r in rows}) == len(rows), 'rows': {}}
    for r in rows:
        d = os.path.join(M.RUNS, f"mix_{r['name']}")   # run_tj1_mix.run_one 의 실행 폴더는 mix_<이름> (04:19 laptop 지적 — 처음엔 접두사 없이 봐 전 행 거짓 경보)
        if not os.path.isdir(d):
            raise RuntimeError(f'감사: 실행 폴더 없음 {d} — 거짓 경보를 내지 않고 멈춤')
        dat = glob.glob(os.path.join(d, 'Output', 'System_0', '*.data'))
        txt = open(dat[0], errors='ignore').read() if dat else ''
        res['rows'][r['name']] = {'status': r['status'], 'finished_marker': 'Simulation finished' in txt,
                                  'n_blocked_lines_12': txt.count('Number of pockets blocked in a unitcell: 12'),
                                  'blocked_for_component': txt.count('Pockets are blocked for this component'),
                                  'not_found': "'Blocking-pocket' file not found" in txt}
    json.dump(res, open(M.OUT.replace('.json', '_audit.json'), 'w'), ensure_ascii=False, indent=1)
    print('감사', json.dumps(res, ensure_ascii=False), flush=True)


if __name__ == '__main__':
    if os.environ.get('E27B_AUDIT_ONLY'):
        audit(); sys.exit(0)
    rc = M.main()
    audit()
    sys.exit(rc)
