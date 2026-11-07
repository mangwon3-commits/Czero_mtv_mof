# -*- coding: utf-8 -*-
"""#5′ 격자 이완 수용 시험 — HKHOME. 등록 `ASSIGN_ZNBDT_NO2_PLACEMENT_20261107.md` §5-3 · §7 ③④(종합자 21:1x · 자료 0건).
겹침 고리판 −Cl · −Br(laptop2 GFN-FF 고정셀 이완본 `relax_tnf/e24j_{cl,br}_ovl_relaxed.cif` · 2e5acbac)을 **관문 ⑤ 처리 그대로**
(UFF4MOF 셀 이완 · `risk_screen.run_one` 무수정 import · 판정식은 `run_e24i_gate5.py` 와 같음)로 풀고, 이완본에 (0a)(0b) 를 다시 잽니다.

입력: 이 기기 작업트리에는 postman reset 으로 그 파일들이 없어서, 추적 경로는 건드리지 않고 `git show HEAD:…` 로
      실행 폴더(e24j_cr_stage/)에만 꺼냅니다 — blob md5 · 출처 커밋을 기록합니다.
이완본: LAMMPS 슈퍼셀(min_<tag>.data)의 복제 0 을 단위셀로 접습니다. 복제끼리의 분수좌표 편차를 재서 기록합니다(0 이면 접기 정확 —
      −NO₂ 관문 ⑤ 산출물에서 12 복제 모두 같았음). 원점의 강체 이동(중앙값)은 뺍니다. 원자 순서는 질량에서 읽은 원소로 확인합니다.
(0a) = `e24j_measure.py`(laptop2 · #3 `znbdt_no2_measure.py` 와 같은 측정) 그대로: 이종–H 최소 ≥ 1.8 Å · 골격 최대 변위 ≤ 1.0 Å.
      변위의 기준(빌드본)은 **이완 셀로 분수좌표 그대로 옮긴 것** — 셀 변형 몫은 빼고 원자 자리 움직임만 잽니다(셀 변화율은 따로 열).
(0b) = `clash_gate.check` 그대로. 모체 X선 기준 원자를 이완 셀로 분수좌표 그대로 옮겨 넘깁니다(0.8 Å 짝짓기가 셀 변형에 끊기지 않게).
      짝짓기 확인: 치환기 원자 수 n_sub_atoms 가 고정셀 입력과 같아야 합니다 — 다르면 `sub_count_match` False.
검사기 확인: 같은 코드로 **고정셀 입력**도 재서 laptop2 `results_e24j_screen_laptop2.json` 값과 대조합니다(재현 열).
Zeo++ 가 처리 앞뒤로 들어 있으므로 **RASPA(`simulate`)가 0 일 때만** 띄웁니다(CLAUDE §5) — 돌고 있으면 착수 거부.
산출: results_e24j_cellrelax_hkhome.json(처리 · 셀 변화율 · LCD · PLD · EDiff) · results_e24j_screen_cellrelax_hkhome.json((0a)(0b)).
판정은 종합자. 실행: lammps_mof 파이썬 — `python -u run_e24j_cellrelax.py`(21_ZIF69_MTV 에서)."""
import collections, hashlib, json, os, socket, subprocess, sys, time, warnings
import numpy as np
warnings.filterwarnings('ignore')
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE); os.chdir(HERE)
import risk_screen as rs   # noqa: E402
import clash_gate          # noqa: E402
from ase.io import read, write                    # noqa: E402
from ase.neighborlist import neighbor_list        # noqa: E402
from ase.data import covalent_radii               # noqa: E402
from ase.geometry import find_mic                 # noqa: E402

JOBS = {'e24j_cl_ovl': ('e24j_candidates/e24j_cl_ovl.cif', 'relax_tnf/e24j_cl_ovl_relaxed.cif', 'Cl'),
        'e24j_br_ovl': ('e24j_candidates/e24j_br_ovl.cif', 'relax_tnf/e24j_br_ovl_relaxed.cif', 'Br')}
HET_H = ('H···O', 'H···N', 'F···H', 'Cl···H', 'H···S', 'Br···H')
REF = json.load(open('results_e22b_gate5_hkhome.json'))['rows']['e22_parent']['after']['LCD']
STAGE = os.path.join(HERE, 'e24j_cr_stage'); rs.STRUCT = STAGE; rs.WORK = os.path.join(HERE, 'lmp_e24j_cr')
OUTD = os.path.join(HERE, 'e24j_cellrelax')
HOST = socket.gethostname().lower()
OUT1 = os.path.join(HERE, f'results_e24j_cellrelax_{HOST}.json')
OUT2 = os.path.join(HERE, f'results_e24j_screen_cellrelax_{HOST}.json')
DRY = bool(os.environ.get('E24J_CR_DRY'))   # 1 이면 LAMMPS · Zeo++ 없이 입력 꺼내기 · 고정셀 재현 측정만


def md5(p): return hashlib.md5(open(p, 'rb').read()).hexdigest()


def git_out(path):
    """HEAD 의 blob 을 실행 폴더로 꺼냄(작업트리 추적 경로는 안 건드림)."""
    blob = subprocess.run(['git', 'show', f'HEAD:21_ZIF69_MTV/{path}'], cwd=HERE, capture_output=True, check=True).stdout
    src_commit = subprocess.run(['git', 'log', '-1', '--format=%h', 'HEAD', '--', path], cwd=HERE, capture_output=True, text=True).stdout.strip()
    dst = os.path.join(STAGE, 'src', path.replace('/', '__'))
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    open(dst, 'wb').write(blob)
    return dst, {'path': path, 'from': f'git show HEAD:21_ZIF69_MTV/{path}', 'commit': src_commit, 'md5': md5(dst)}


def graph(a):
    cuts = [covalent_radii[z] * 1.15 if a[k].symbol != 'Zn' else 1.45 for k, z in enumerate(a.numbers)]
    i, j = neighbor_list('ij', a, cuts); G = collections.defaultdict(set)
    for x, y in zip(i, j): G[x].add(y)
    return G


def contacts(a, G):
    ii, jj, dd = neighbor_list('ijd', a, 3.6); s = a.get_chemical_symbols(); best = {}
    for x, y, d in zip(ii, jj, dd):
        if x >= y or 'Zn' in (s[x], s[y]): continue
        if y in ({x} | G[x] | {w for v in G[x] for w in G[v]}): continue
        p = '···'.join(sorted((s[x], s[y])))
        if p not in best or d < best[p][0]: best[p] = (round(float(d), 3), f'{s[x]}{x}', f'{s[y]}{y}')
    return best


def strained(atoms, cell):
    x = atoms.copy(); x.set_cell(cell, scale_atoms=True); return x


def measure(tag, a0, a1, path1, X, par):
    """e24j_measure.py 의 측정 그대로. a0 = 빌드본, a1 = 잴 구조(path1 은 그 CIF). 빌드본 · 모체는 a1 의 셀로 분수좌표 그대로 옮김."""
    assert len(a0) == len(a1)
    b0 = strained(a0, a1.cell); ps = strained(par, a1.cell); P = ps.get_positions()
    X0 = b0.get_positions(); P1 = a1.get_positions(); dmax, nfw = 0.0, 0
    for k in range(len(b0)):
        _, dl = find_mic(P - X0[k], b0.cell, pbc=True); j = int(np.argmin(dl))
        if dl[j] < 0.3 and ps[j].symbol == b0[k].symbol:
            nfw += 1; _, d1 = find_mic(P1 - X0[k], a1.cell, pbc=True)
            dmax = max(dmax, min(d1[m] for m in range(len(a1)) if a1[m].symbol == b0[k].symbol))
    G = graph(a1); s = a1.get_chemical_symbols(); c = contacts(a1, G)
    het = [(v[0], p, v[1], v[2]) for p, v in c.items() if p in HET_H]; hh = min(het)
    g = clash_gate.check(path1, parent=ps)
    ii, jj, dd = neighbor_list('ijd', a1, 3.6)
    sites = []
    for x in [n for n in range(len(a1)) if s[n] == X]:
        cs = [y for y in G[x] if s[y] == 'C']
        ring_c = cs[0] if cs else None
        n1 = (G[ring_c] - {x}) if ring_c is not None else set()
        excl = ({ring_c} | n1 | {w for v in n1 for w in G[v] if w != x}) if ring_c is not None else set()
        best = (9.9, None); xo = (9.9, None); w_in = (-9.9, None)
        for p_, q_, d in zip(ii, jj, dd):
            if p_ != x or q_ == x or s[q_] == 'Zn' or q_ in excl: continue
            if d < best[0]: best = (round(float(d), 3), f'{X}{x}···{s[q_]}{q_}')
            if s[q_] == 'O' and d < xo[0]: xo = (round(float(d), 3), f'{X}{x}···O{q_}')
            if s[q_] != 'H':
                m = clash_gate.BONDI[X] + clash_gate.BONDI[s[q_]] - d
                if m > w_in[0]: w_in = (round(float(m), 3), f'{X}{x}···{s[q_]}{q_} {d:.3f}')
        sites.append({'X': int(x), 'ipso_C': None if ring_c is None else int(ring_c),
                      'graph_neighbors_of_X': sorted(f'{s[y]}{y}' for y in G[x]),
                      'graph_nonC_neighbor': any(s[y] != 'C' for y in G[x]),
                      'closest_contact_any': best, 'min_X_O': xo, 'max_bondi_overlap_from_X': w_in})
    ok_a = hh[0] >= 1.8 and dmax <= 1.0
    return {'measured': path1, 'n_framework_matched': nfw, 'max_framework_disp_A': round(float(dmax), 3),
            'min_heteroatom_H': hh, 'gate0a_pass': ok_a, 'gate0b': g, 'gate0b_pass': g['pass_0b'],
            'gate_all_pass': ok_a and g['pass_0b'], 'sites': sites, 'contacts': c}


def fold(after, before):
    """LAMMPS 슈퍼셀 → 단위셀(복제 0). 복제 사이 편차 · 강체 이동 · 원소 순서 확인을 같이 돌려줌."""
    N = len(before); rep = len(after) // N
    n = np.rint(after.cell.lengths() / before.cell.lengths()).astype(int)
    assert int(n.prod()) == rep and rep * N == len(after), (n, rep, len(after), N)
    order_ok = after.get_chemical_symbols() == list(before.get_chemical_symbols()) * rep   # 질량에서 읽은 원소
    fa = after.get_scaled_positions(wrap=False) * n; fb = before.get_scaled_positions()
    rs_ = []
    for k in range(rep):
        d = fa[k * N:(k + 1) * N] - fb; img = np.rint(np.median(d, axis=0)); r = d - img; r -= np.rint(r); rs_.append(r)
    dev = max(float(np.abs((r - rs_[0]) - np.rint(r - rs_[0])).max()) for r in rs_)
    shift = np.median(rs_[0], axis=0)
    cell1 = np.array(after.cell) / n[:, None]
    a1 = before.copy(); a1.set_cell(cell1, scale_atoms=False); a1.set_scaled_positions((fb + rs_[0] - shift) % 1.0)
    return a1, {'supercell_n': n.tolist(), 'rep': rep, 'symbol_order_ok': bool(order_ok),
                'replica_max_frac_dev_vs_r0': round(dev, 6), 'rigid_shift_frac_removed': np.round(shift, 5).tolist()}


def cell_change(c0, c1):
    p0, p1 = c0.cellpar(), c1.cellpar(); v0, v1 = c0.volume, c1.volume
    return {'before_cellpar': np.round(p0, 4).tolist(), 'after_cellpar': np.round(p1, 4).tolist(),
            'd_len_pct': np.round((p1[:3] - p0[:3]) / p0[:3] * 100, 3).tolist(), 'd_angle_deg': np.round(p1[3:] - p0[3:], 3).tolist(),
            'd_volume_pct': round(float((v1 - v0) / v0 * 100), 3)}


def busy():
    r = subprocess.run(['pgrep', '-x', 'simulate'], capture_output=True, text=True)
    return len(r.stdout.split())


def main():
    if not DRY and busy():
        sys.exit(f'  !! RASPA simulate {busy()}건이 돌고 있음 — Zeo++ 동시 금지(CLAUDE §5) · 착수 안 함')
    for p in (OUT1, OUT2):
        if os.path.exists(p) and not DRY:
            sys.exit(f'  !! {os.path.basename(p)} 이미 있음 — 덮어쓰지 않음')
    os.makedirs(STAGE, exist_ok=True); os.makedirs(rs.WORK, exist_ok=True); os.makedirs(OUTD, exist_ok=True)
    par = read(clash_gate.PARENT)
    lap = json.load(open('results_e24j_screen_laptop2.json'))['rows']
    t0 = time.time()
    r1 = {'test': '#5′ 격자 이완 수용 시험 — 겹침 고리판 −Cl · −Br 의 관문 ⑤ 처리(UFF4MOF 셀 이완) · HKHOME',
          'assign': 'ASSIGN_ZNBDT_NO2_PLACEMENT_20261107.md §5-3 · §7 ③④', 'code': 'run_e24j_cellrelax.py · risk_screen.run_one 무수정',
          'rule': 'risk_screen.py:414~423, LCD_ref = e22_parent 같은 처리 뒤 LCD(사용자 결정 4 (다)) — results_e22b_gate5_hkhome.json',
          'LCD_ref_family': REF, 'machine': HOST, 'dry': DRY, 'rows': {}}
    r2 = {'test': '#5′ — 셀 이완본의 관문 (0a)(0b)(e24j_measure.py 측정 · clash_gate.check) · 고정셀 입력 재현 열 포함',
          'assign': 'ASSIGN_ZNBDT_NO2_PLACEMENT_20261107.md §5-3', 'relax_record': os.path.basename(OUT1),
          'frame_note': '빌드본 · 모체 기준 원자는 잴 구조의 셀로 분수좌표 그대로 옮겨 씀(셀 변형 몫 제외) — 셀 변화율은 relax_record',
          'machine': HOST, 'dry': DRY, 'rows': {}, 'note': '판정은 종합자.'}
    for tag, (B0p, B1p, X) in JOBS.items():
        b0_path, src0 = git_out(B0p); b1_path, src1 = git_out(B1p)
        a0, aR = read(b0_path), read(b1_path)
        # 검사기 확인: 고정셀 입력을 같은 코드로 재서 laptop2 값과 대조
        rep_ = measure(tag, a0, aR, b1_path, X, par)
        L = lap.get(tag, {})
        repro = {'laptop2_gate0b_min_margin': L.get('gate0b', {}).get('min_margin_A'), 'hkhome_gate0b_min_margin': rep_['gate0b']['min_margin_A'],
                 'laptop2_max_disp': L.get('max_framework_disp_A'), 'hkhome_max_disp': rep_['max_framework_disp_A'],
                 'laptop2_min_het_H': (L.get('min_heteroatom_H') or [None])[0], 'hkhome_min_het_H': rep_['min_heteroatom_H'][0]}
        repro['match'] = (repro['laptop2_gate0b_min_margin'] == repro['hkhome_gate0b_min_margin'] and
                          repro['laptop2_max_disp'] == repro['hkhome_max_disp'] and repro['laptop2_min_het_H'] == repro['hkhome_min_het_H'])
        print(f"{tag}: 고정셀 재현 {'일치' if repro['match'] else '불일치!'} {repro}", flush=True)
        row1 = {'inputs': [src0, src1]}
        row2 = {'substituent': X, 'inputs': [src0, src1], 'fixedcell_repro': repro,
                'fixedcell': {k: rep_[k] for k in ('max_framework_disp_A', 'min_heteroatom_H', 'gate0a_pass', 'gate0b', 'gate0b_pass', 'gate_all_pass')}}
        if not DRY:
            import shutil
            shutil.copy(b1_path, os.path.join(STAGE, f'ZIF69_{tag}.cif'))
            ts = time.time(); n, m0, m1, st = rs.run_one(tag)
            row1.update({'status': st, 'before': m0, 'after': m1, 'minutes': round((time.time() - ts) / 60, 1)})
            if st == 'ok' and m1 and m1.get('LCD'):
                drop = (REF - m1['LCD']) / REF * 100
                checks = {'PLD': (m0['PLD'] or 0) > rs.CO2_KINETIC, 'LCD_drop': drop < rs.LCD_DROP_LIMIT,
                          'AV': (m0.get('AV_per_cell') or 0) > rs.AV_FLOOR, 'min_dist': m1['min_dist'] > rs.MIN_DIST_LIMIT}
                row1.update({'LCD_drop_pct': round(drop, 2), 'checks': checks, 'pass': all(checks.values())})
            ed, loops = rs.final_ediff(tag); row1['final_EDiff'] = ed; row1['outer_loops'] = loops
            row1['converged_to_min_eval_1e-4'] = (ed is not None and abs(ed) < 1e-4)
            dat = os.path.join(rs.WORK, tag, f'min_{tag}.data')
            if st == 'ok' and os.path.exists(dat):
                after = read(dat, format='lammps-data', atom_style='full')
                a1, fl = fold(after, aR)
                p1 = os.path.join(OUTD, f'{tag}_cellrelaxed.cif'); write(p1, a1)
                row1.update({'fold': fl, 'cell_change': cell_change(aR.cell, a1.cell), 'cellrelaxed_cif': os.path.relpath(p1, HERE), 'cellrelaxed_md5': md5(p1)})
                a1r = read(p1)   # CIF 로 쓴 뒤 다시 읽은 것으로 잼(clash_gate 가 파일을 읽으므로 같은 것)
                m = measure(tag, a0, a1r, p1, X, par)
                m['sub_count_match'] = (m['gate0b']['n_sub_atoms'] == rep_['gate0b']['n_sub_atoms'])
                m['sub_count_fixedcell'] = rep_['gate0b']['n_sub_atoms']
                row2['cellrelaxed'] = m
                print(f"{tag}: 셀 이완 {st} · {row1['minutes']} 분 · 접기 복제편차 {fl['replica_max_frac_dev_vs_r0']} · 원소순서 {fl['symbol_order_ok']} · "
                      f"짝짓기 {m['sub_count_match']} — 값은 파일에", flush=True)
            else:
                print(f"{tag}: 셀 이완 {st} — 측정 안 함", flush=True)
        r1['rows'][tag] = row1; r2['rows'][tag] = row2
        if not DRY:
            json.dump(r1, open(OUT1, 'w', encoding='utf-8'), ensure_ascii=False, indent=1, default=str)
            json.dump(r2, open(OUT2, 'w', encoding='utf-8'), ensure_ascii=False, indent=1, default=str)
    r1['elapsed_min'] = r2['elapsed_min'] = round((time.time() - t0) / 60, 1)
    r1['finished'] = r2['finished'] = True
    if DRY:
        p = os.path.join(STAGE, 'dry_screen.json'); json.dump(r2, open(p, 'w', encoding='utf-8'), ensure_ascii=False, indent=1, default=str); print('드라이 →', p)
        return 0
    json.dump(r1, open(OUT1, 'w', encoding='utf-8'), ensure_ascii=False, indent=1, default=str)
    json.dump(r2, open(OUT2, 'w', encoding='utf-8'), ensure_ascii=False, indent=1, default=str)
    ok = all(r1['rows'][t].get('status') == 'ok' and 'cellrelaxed' in r2['rows'][t] for t in JOBS)
    print('끝', 'ok' if ok else '!! 일부 실패', flush=True)
    return 0 if ok else 2


if __name__ == '__main__':
    sys.exit(main())
