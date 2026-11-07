# -*- coding: utf-8 -*-
"""ZnBDT 보강 A — 격자를 움직인 구조(UFF4MOF 상한 300 이완본)의 작동점 S_mix, 성분별 막음. 등록 `ASSIGN_ZNBDT_SUPP_20261103.md` §A.

바탕(배정 지정): `run_e24i_mix.py`(→ `run_tj1_mix` **수정 없이** import, 3씨앗 = 실행 폴더 _s1~_s3 · 착수 간격 idx×15 s)
  + 막음 삽입은 `run_e27b_mix323.py` 의 `_run_blocked` 와 같은 수 — 단 **온도는 298 K**(run_tj1_mix 기본값 그대로, 아래에서 명시).
자: 건조 CO₂/N₂ 0.15/0.85 · 1 bar · 298 K · 5,000 + 15,000 · UFF_MOF(md5 관문) · PACMAN DDEC6(CIF) · 12 Å · Ewald 1e-6 · `unit_cells()` · 강체.
대상: e22_parent · e24i_cn_open · e24i_br_open 의 `charged_v3/<tag>_uff300_DDEC6.cif`(원본 `uff300_e24i/<tag>_after.cif` = 2×2×3 초격자 12셀) × 3씨앗 = 9작업.
막음: CO₂ ← `znbdt_a_zeo_runs/<tag>/block1.65/<tag>_after.block` · N₂ ← `.../block1.82/<tag>_after.block`(`znbdt_a_zeo.py` 산출,
      Zeo++ `-ha -block r 50000` — E-24i 막음 파일과 같은 호출, 입력만 이완본). 구가 0 인 성분은 BlockPockets 를 넣지 않음
      (`e24i_bp_desktop.py` 의 `bp = nsph > 0` 과 같은 수 — 같은 계).

바꾼 것(원 러너는 한 줄도 안 고침):
  · `M.subprocess.run` 감쌈(e27b 와 같은 수): simulation.input 의 두 성분 앵커가 **각각 정확히 한 번**이 아니면 예외(RASPA 안 띄움) ·
    성분 절에 `BlockPockets yes` · `BlockPocketsFileName <tag>_<gas>` 두 줄 · 막음 파일을 실행 폴더로 복사 ·
    RASPA stdout/stderr 를 실행 폴더 파일로 받음(원 러너는 DEVNULL — 'Blocking-pocket' not-found 문구를 보려고).
  · `M.run_one` 감쌈: 원 판정(완주 표지 + 두 성분 적재 각 한 번 + 반환코드 0) 뒤에 **막음 관문**을 더 봄 — 실패면 status 'no-block(…)'.
      성분마다(.data 의 그 성분 절 안에서) 'Number of pockets blocked in a unitcell: N' · 'Pockets are blocked for this component' ·
      'Block-pockets Filename' 을 세고, N = 구 수 × 단위셀 수(e24i_bp_desktop 의 등식) · not-found 문구 0(.data · stdout · stderr).
      결과는 실행 폴더의 block_audit.json 에도 남김.
  · 결과 JSON: 원 러너의 save() 가 `protocol.blocking: False` 를 박으므로, 저장될 때마다 `protocol.blocking` 을 실제 막음 기록으로
      바꾸고 `gate` · 행별 `block_audit` 을 넣음(아래 _J — json.dump 한 곳만 거침).
  · 착수 거부: 실행 폴더 · 결과 파일이 있으면(원 러너의 이어받기가 cached 로 섞지 않게) · Zeo++(network) 가 돌면(CLAUDE.md §5) ·
      전하본이 이완본과 원자 수 · 원소 순서 · 셀 · 분율 좌표가 다르면 · 순전하 |Σq| > ZNBDT_A_NETQ_TOL(기본 5e-5 = charge_tnf/charge_v2 관문) ·
      막음 파일이 없으면.
S_Henry 칸: 이완본 Widom 이 없음 → 자리 채움 1.0(run_e24i_mix 의 Widom 전 기동과 같은 표지) — **ratio 비 인용 금지**.
판정 없음 — 값과 관문만(종합자). 사용자 제시 막힌 구 수(−CN 60 · 모체 24 · −Br 0, 12셀 기준)와의 대조는 gate 에 원자료로만 적음.

환경: ZNBDT_A_MACHINE(기본 hkhome) · ZNBDT_A_WORKERS(기본 5) · ZNBDT_A_NETQ_TOL(기본 5e-5) · ZNBDT_A_DRY=1(계획만) ·
      ZNBDT_A_SMOKE=1(저장소 밖 ZNBDT_A_SMOKE_DIR, 기본 ~/.mof_smoke_znbdt_a · 사이클 10 · 초기화 0 · 씨앗 1).
"""
import glob
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import run_tj1_mix as M   # noqa: E402
from ase.io import read   # noqa: E402

TAGS = ('e22_parent', 'e24i_cn_open', 'e24i_br_open')
PAIR = (('CO2', 1.65), ('N2', 1.82))
USER_SPHERES_12CELL = {'e22_parent': 24, 'e24i_cn_open': 60, 'e24i_br_open': 0}   # ASSIGN §A "막힌 구 수" (사용자 제시 · −Br 은 예상)
NOT_FOUND = "'Blocking-pocket' file not found"
SMOKE = bool(os.environ.get('ZNBDT_A_SMOKE'))
NETQ_TOL = float(os.environ.get('ZNBDT_A_NETQ_TOL', '5e-5'))

M.TEMP = 298.0
M.MACHINE = os.environ.get('ZNBDT_A_MACHINE', 'hkhome')
M.WORKERS = int(os.environ.get('ZNBDT_A_WORKERS', '5'))
M.RUNS = os.path.join(HERE, 'znbdt_a_uff300mix_runs')
M.OUT = os.path.join(HERE, f'results_znbdt_a_uff300mix_{M.MACHINE}.json')
M.TEST = 'ZnBDT 보강 A — UFF4MOF 상한 300 이완본 작동점 S_mix(성분별 막음, 298 K)'
M.ASSIGN_REF = 'ASSIGN_ZNBDT_SUPP_20261103.md §A'
M.REG_REF = 'ASSIGN_ZNBDT_SUPP_20261103.md §A 읽는 법(자료 0건에서 등록)'
SEEDS = (1, 2, 3)
if SMOKE:
    _sd = os.path.expanduser(os.environ.get('ZNBDT_A_SMOKE_DIR', '~/.mof_smoke_znbdt_a'))
    if os.path.realpath(_sd).startswith(os.path.realpath(os.path.dirname(HERE))):
        raise SystemExit('!! 스모크 폴더가 저장소 안 — 중단')
    M.CYCLES, M.INIT = 10, 0
    M.RUNS = os.path.join(_sd, 'runs')
    M.OUT = os.path.join(_sd, 'results_smoke.json')
    M.TEST = '[스모크 — 인용 금지] ' + M.TEST
    SEEDS = (1,)


def _md5(p):
    return hashlib.md5(open(p, 'rb').read()).hexdigest()


def cif_of(tag):
    return os.path.join(HERE, 'charged_v3', f'{tag}_uff300_DDEC6.cif')


def block_info():
    """성분별 막음 파일 — 이름 · md5 · 구 수 · 탐침 반지름."""
    out = {}
    for t in TAGS:
        out[t] = {}
        for g, r in PAIR:
            p = os.path.join(HERE, 'znbdt_a_zeo_runs', t, f'block{r:.2f}', f'{t}_after.block')
            if not os.path.exists(p):
                out[t][g] = {'file': os.path.relpath(p, HERE), 'exists': False}
                continue
            txt = open(p).read()
            n = int(txt.split()[0]) if txt.split() else None
            out[t][g] = {'file': os.path.relpath(p, HERE), 'exists': True, 'md5': _md5(p), 'n_spheres': n, 'probe_radius_A': r,
                         'inserted': bool(n and n > 0), 'raspa_name': f'{t}_{g.lower()}'}
    return out


BINFO = block_info()
TAG_OF = {f'{t}_uff300_s{k}': t for t in TAGS for k in (1, 2, 3)}
ANCH = {g: f"Component {i} MoleculeName              {g}\n            MoleculeDefinition        TraPPE\n" for i, g in ((0, 'CO2'), (1, 'N2'))}


def targets():
    t = []
    for tag in TAGS:
        for k in SEEDS:
            t.append({'name': f'{tag}_uff300_s{k}', 'cif': cif_of(tag), 'group': '형판 설계(비-ZIF) · UFF4MOF 상한 300 이완본',
                      'dim': 3, 'S_Henry': 1.0, 'S_Henry_err': 0.0,
                      'S_Henry_src': '자리 채움 1.0 — 이완본 Widom 없음 · ratio 비 인용 금지', 'L': None, 'L_src': '—'})
    for x in t:
        a = read(x['cif']); uc = M.rg.unit_cells(a); x['unit_cells'] = uc; x['N_super'] = len(a) * uc[0] * uc[1] * uc[2]
    return sorted(t, key=lambda x: -x['N_super'])          # LPT


# ---- 막음 삽입(e27b _run_blocked 와 같은 수) ----
_real_run = M.subprocess.run


def _run_blocked(cmd, **kw):
    d = kw.get('cwd')
    if not (d and cmd and str(cmd[-1]) == 'simulation.input'):
        return _real_run(cmd, **kw)
    name = os.path.basename(d)[len('mix_'):]
    tag = TAG_OF.get(name)
    if tag is None:
        raise RuntimeError(f'실행 폴더 이름에서 대상을 못 가름: {d} — RASPA 안 띄움')
    p = os.path.join(d, 'simulation.input'); s = open(p).read()
    if 'BlockPockets' in s:
        raise RuntimeError('simulation.input 에 이미 BlockPockets — 예상 밖 상태, RASPA 안 띄움')
    for g, a in ANCH.items():
        if s.count(a) != 1:
            raise RuntimeError(f'{g} 성분 앵커가 정확히 한 번이 아님({s.count(a)}) — 막음 삽입 중단, RASPA 안 띄움')
        b = BINFO[tag][g]
        if b['inserted']:
            s = s.replace(a, a + f"            BlockPockets              yes\n            BlockPocketsFileName      {b['raspa_name']}\n")
            shutil.copy(os.path.join(HERE, b['file']), os.path.join(d, b['raspa_name'] + '.block'))
    open(p, 'w').write(s)
    with open(os.path.join(d, 'raspa_stdout.txt'), 'w') as fo, open(os.path.join(d, 'raspa_stderr.txt'), 'w') as fe:
        kw['stdout'], kw['stderr'] = fo, fe
        return _real_run(cmd, **kw)


M.subprocess.run = _run_blocked


# ---- 막음 관문(.data 의 성분 절 안에서 셈) ----
def audit_dir(d, tag, uc):
    cells = uc[0] * uc[1] * uc[2]
    dat = glob.glob(os.path.join(d, 'Output', 'System_0', '*.data'))
    txt = open(dat[0], encoding='utf-8', errors='ignore').read() if len(dat) == 1 else ''
    side = ''.join(open(os.path.join(d, f), errors='ignore').read() for f in ('raspa_stdout.txt', 'raspa_stderr.txt')
                   if os.path.exists(os.path.join(d, f)))
    comp, per = None, {g: {'n_blocked_lines': [], 'blocked_for_component': 0, 'not_blocked_line': 0, 'block_filename_lines': []} for g, _ in PAIR}
    for ln in txt.splitlines():
        m = re.match(r'Component\s+\d+\s+\[(\w+)\]\s+\(Adsorbate molecule\)', ln)
        if m:
            comp = m.group(1)
            continue
        if ln.startswith('Framework') or ln.startswith('Current cycle') or ln.startswith('Starting simulation'):
            comp = None
        if comp in per:
            mm = re.search(r'Number of pockets blocked in a unitcell:\s*(\d+)', ln)
            if mm:
                per[comp]['n_blocked_lines'].append(int(mm.group(1)))
            if 'Pockets are blocked for this component' in ln:
                per[comp]['blocked_for_component'] += 1
            if 'Pockets are NOT blocked for this component' in ln:
                per[comp]['not_blocked_line'] += 1
            mf = re.search(r'Block-pockets Filename:\s*(\S+)', ln)
            if mf:
                per[comp]['block_filename_lines'].append(mf.group(1))
    nf = txt.count(NOT_FOUND) + side.count(NOT_FOUND)
    ncell = {ax: (int(m.group(1)) if m else None) for ax in 'abc'
             for m in [re.search(rf'Number of unitcells \[{ax}\]:\s*(\d+)', txt)]}
    fails = []
    for g, _ in PAIR:
        b, c = BINFO[tag][g], per[g]
        exp = (b['n_spheres'] or 0) * cells
        c.update({'block_file': b['file'], 'block_md5': b.get('md5'), 'n_spheres_file': b.get('n_spheres'), 'probe_radius_A': b.get('probe_radius_A'),
                  'inserted': b['inserted'], 'raspa_unit_cells': list(uc), 'raspa_cells_product': cells,
                  'equation_spheres_x_cells': f"{b.get('n_spheres')} × {cells} = {exp}",
                  'raspa_reported': c['n_blocked_lines'][0] if len(c['n_blocked_lines']) == 1 else c['n_blocked_lines'],
                  'spec_product_reported_x_cells': (c['n_blocked_lines'][0] * cells if len(c['n_blocked_lines']) == 1 else None)})
        if b['inserted']:
            if c['n_blocked_lines'] != [exp]:
                fails.append(f'{g}:N{c["n_blocked_lines"]}≠{exp}')
            if c['blocked_for_component'] != 1:
                fails.append(f'{g}:blocked줄{c["blocked_for_component"]}')
        elif c['blocked_for_component']:
            fails.append(f'{g}:구0인데 blocked줄')
    if nf:
        fails.append(f'not-found {nf}')
    if not txt:
        fails.append('.data 없음/여럿')
    a = {'tag': tag, 'data': os.path.relpath(dat[0], d) if len(dat) == 1 else None, 'per_component': per, 'not_found_count': nf,
         'raspa_number_of_unitcells': ncell, 'framework_net_charge_line': (re.search(r'Framework has net charge:\s*(\S+)', txt) or [None, None])[1],
         'pass': not fails, 'fails': fails}
    json.dump(a, open(os.path.join(d, 'block_audit.json'), 'w'), ensure_ascii=False, indent=1)
    return a


_real_one = M.run_one


def _run_one_gated(arg):
    name, v, st, rc, seed, mins = _real_one(arg)
    d = os.path.join(M.RUNS, f'mix_{name}')
    if os.path.isdir(os.path.join(d, 'Output')):
        a = audit_dir(d, TAG_OF[name], arg[1]['unit_cells'])
        if st == 'ok' and not a['pass']:
            st = 'no-block(' + ';'.join(a['fails'])[:60] + ')'
    return name, v, st, rc, seed, mins


M.run_one = _run_one_gated


# ---- 결과 JSON 에 막음 기록 · 관문(원 러너 save() 의 blocking: False 를 실제 값으로) ----
PRE = {}


def _gate_section():
    rows = {}
    for f in sorted(glob.glob(os.path.join(M.RUNS, 'mix_*', 'block_audit.json'))):
        rows[os.path.basename(os.path.dirname(f))[len('mix_'):]] = json.load(open(f, encoding='utf-8'))
    cmp_ = {}
    for t in TAGS:
        uc = PRE.get(t, {}).get('raspa_unit_cells')
        cells = uc[0] * uc[1] * uc[2] if uc else None
        ex = {g: BINFO[t][g].get('n_spheres') for g, _ in PAIR}
        rep = {}
        for n, a in rows.items():
            if a['tag'] == t:
                for g, _ in PAIR:
                    rep.setdefault(g, set()).add(str(a['per_component'][g]['raspa_reported']))
        cmp_[t] = {'user_value_12cell': USER_SPHERES_12CELL[t], 'n_spheres_file': ex, 'raspa_unit_cells': uc,
                   'raspa_reported_by_component': {g: sorted(v) for g, v in rep.items()},
                   'note': '원자료 나란히 — 어느 쪽이 사용자 기준인지(구 수 · Zeo++ -chan 주머니 수 · RASPA N · N×셀) 이 파일은 가르지 않음'}
    return {'block_rule': "성분마다: 'Number of pockets blocked in a unitcell: N' 한 번, N = 구 수 × 단위셀 수 · "
                          "'Pockets are blocked for this component' 한 번(구 > 0 인 성분) · not-found 0(.data·stdout·stderr) · "
                          "완주 표지 · 두 성분 적재 각 한 번 · 반환코드 0 · 씨앗 고유",
            'pre_launch': PRE, 'user_comparison': cmp_, 'per_run_audit': rows,
            'all_runs_block_pass': bool(rows) and all(a['pass'] for a in rows.values())}


class _J:
    load, loads, dumps = staticmethod(json.load), staticmethod(json.loads), staticmethod(json.dumps)

    @staticmethod
    def dump(obj, fp, **kw):
        if isinstance(obj, dict) and isinstance(obj.get('protocol'), dict) and obj.get('test') == M.TEST:
            obj['protocol']['blocking'] = {'per_component': True, 'files': BINFO, 'zeo': 'network -ha -block r 50000 (znbdt_a_zeo.py)',
                                           'rule_zero_spheres': '구 0 인 성분은 BlockPockets 미삽입(e24i_bp_desktop bp = nsph > 0)'}
            obj['protocol']['charges'] = 'PACMAN DDEC6 charged_v3/<tag>_uff300_DDEC6.cif (charge_tnf.py, 원본 uff300_e24i/<tag>_after.cif)'
            obj['gate'] = _gate_section()
            seeds = [r.get('seed') for r in obj.get('rows', []) if r.get('seed')]
            obj['gate']['seeds_unique'] = len(seeds) == len(set(seeds))
            if SMOKE:
                obj['smoke'] = {'cycles': M.CYCLES, 'init': M.INIT, 'note': '스모크 — 값 인용 금지'}
        return json.dump(obj, fp, **kw)


M.json = _J      # run_tj1_mix 는 targets()(여기서 교체) 와 save() 에서만 json 을 씀


def prelaunch():
    """착수 전 관문 — 하나라도 실패하면 RASPA 를 띄우지 않음."""
    bad = []
    nz = subprocess.run(['pgrep', '-xc', 'network'], capture_output=True, text=True).stdout.strip() or '0'
    if nz != '0':
        bad.append(f'Zeo++ network {nz}개 도는 중(CLAUDE.md §5)')
    for p in (M.RUNS, M.OUT):
        if os.path.exists(p):
            bad.append(f'이전 산출 있음: {p}')
    import numpy as np
    for t in TAGS:
        src, chg = os.path.join(HERE, 'uff300_e24i', f'{t}_after.cif'), cif_of(t)
        if not os.path.exists(chg):
            bad.append(f'전하본 없음 {chg}'); continue
        a, b = read(src), read(chg)
        dd = a.get_scaled_positions() - b.get_scaled_positions(); dd -= np.round(dd)
        q = float(np.sum(b.get_initial_charges())) if b.has('initial_charges') else None
        if q is None:
            from charge_v2 import net_charge
            q = net_charge(chg)[0]
        uc = M.rg.unit_cells(b)
        PRE[t] = {'after_cif': os.path.relpath(src, HERE), 'after_md5': _md5(src), 'charged_cif': os.path.relpath(chg, HERE), 'charged_md5': _md5(chg),
                  'n_atoms': [len(a), len(b)], 'symbols_same': a.get_chemical_symbols() == b.get_chemical_symbols(),
                  'cell_max_diff_A': float(np.abs(a.cell.array - b.cell.array).max()), 'frac_max_diff': float(np.abs(dd).max()),
                  'net_charge': q, 'netq_tol': NETQ_TOL, 'raspa_unit_cells': uc, 'blocks': BINFO[t]}
        c = PRE[t]
        if not (c['n_atoms'][0] == c['n_atoms'][1] and c['symbols_same'] and c['cell_max_diff_A'] < 1e-6 and c['frac_max_diff'] < 1e-6):
            bad.append(f'{t} 이완본 · 전하본 다름')
        if abs(q) > NETQ_TOL:
            bad.append(f'{t} 순전하 {q:+.2e} > {NETQ_TOL:g}')
        for g, _ in PAIR:
            if not BINFO[t][g]['exists'] or BINFO[t][g]['n_spheres'] is None:
                bad.append(f'{t} {g} 막음 파일 없음/빈 파일')
    # Zeo++ 산출 기록과 대조 — 가드 kill · rc≠0 · 빈 파일(znbdt_a_zeo.py 1차 시도 결함)인 막음 파일은 쓰지 않음
    acc = os.path.join(HERE, 'results_znbdt_a_access_hkhome.json')
    if not os.path.exists(acc):
        bad.append('results_znbdt_a_access_hkhome.json 없음')
    else:
        rows = {r['tag']: r for r in json.load(open(acc, encoding='utf-8'))['rows']}
        for t in TAGS:
            for g, r in PAIR:
                z = rows.get(t, {}).get(f'r{r:.2f}', {}).get('block', {})
                b = BINFO[t][g]
                if not (z.get('block_ok') and z.get('block_md5') == b.get('md5') and z.get('n_spheres') == b.get('n_spheres')):
                    bad.append(f"{t} {g} 막음 파일이 Zeo++ 기록과 안 맞음(block_ok {z.get('block_ok')} · md5 {z.get('block_md5')} · 구 {z.get('n_spheres')})")
                b['zeo_record'] = {k: z.get(k) for k in ('block_ok', 'channels', 'pockets', 'rc', 'seconds', 'peak_rss_MB')}
    return bad


def main():
    bad = prelaunch()
    print(f"ZnBDT A — {'스모크 ' if SMOKE else ''}{M.INIT}+{M.CYCLES} · {M.TEMP} K · 워커 {M.WORKERS} · 출력 {M.OUT}", flush=True)
    for t in TAGS:
        print(f"  {t}: {json.dumps({k: v for k, v in PRE.get(t, {}).items() if k != 'blocks'}, ensure_ascii=False)}", flush=True)
        for g, _ in PAIR:
            print(f"    {g}: {json.dumps(BINFO[t][g], ensure_ascii=False)}", flush=True)
    if bad:
        print('!! 착수 전 관문 실패 — RASPA 안 띄움:\n   ' + '\n   '.join(bad), flush=True)
        return 2
    if os.environ.get('ZNBDT_A_DRY'):
        for x in targets():
            print('  계획', x['name'], x['unit_cells'], x['N_super'], os.path.relpath(x['cif'], HERE), flush=True)
        return 0
    M.targets = targets
    return M.main()


if __name__ == '__main__':
    sys.exit(main())
