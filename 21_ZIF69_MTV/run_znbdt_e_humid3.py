# -*- coding: utf-8 -*-
"""Zn(bib)(bdtdc) 보강 E — 습윤 3성분(CO₂ · N₂ · H₂O) 흡착점의 선택도 S_humid. 등록 `ASSIGN_ZNBDT_SUPP_20261103.md` §E(f589c08b)
+ 사용자 11-04 결정 "−C₂H₅ 를 E 에 추가"(cloud.md §5 권고 첫 줄 · HKHOME COMMS/desktop.md 2578c3a2). laptop2 작성, 랩탑(Melchior)도 그대로 씀.

바탕: `run_e24i_humid_wc.py` — `run_humid_wc_v3w`(→ `run_humid_wc`) **무수정 import**(RH90 물 분압 2852.1 Pa · 5,000+15,000 · 물 5자리 ·
전하 ON · `unit_cells()`). 원 러너 `run_humid_wc*.py` 는 고치지 않습니다. 래퍼에서만 바꾸는 것:
  ① `hw.CONDITIONS` = ads 하나(298 K · CO₂ 0.15e5 · P_SAT_298). TSA · VSA 는 안 돌림(§E "조건 수").
  ② RASPA 호출 직전(`hw.subprocess.run` 을 감쌈) 실행 폴더의 simulation.input 을 고침 — `ExternalPressure` → 100000 ·
     CO₂ `MolFraction` → 0.150000 · water → 0.028521 · **N₂ 성분 절(Component 2, TraPPE, 같은 이동 확률)** 을 끝에 덧붙임(0.821479).
     **고칠 자리(앵커)가 각각 정확히 한 번이 아니면 RASPA 를 띄우지 않고 예외.**
  ③ 성분별 BlockPockets — 표 BLOCKS 의 대상만(지금은 e24i_c2h5_open: CO₂ block1.65 · N₂ block1.82 · 물 block1.30, E-24i 와 같은 파일,
     md5 고정 — 다르면 착수 거부). 앵커는 성분마다 정확히 한 번.
  ④ 착수 간격 15 s × i + 착수 사이 2 s 잠금(씨앗 = 착수 초) · 반환코드 파일 · stderr 를 파일로(not-found 를 보려고).
  ⑤ 반복 = **바이트 같은 사본** `<tag>_e3r{k}_DDEC6.cif`(charged_v3/<tag>_DDEC6.cif 에서, md5 대조) — 이름이 달라야 실행 폴더가 갈림.
     charged_v3 는 건드리지 않음(사본은 실행 뿌리 아래 cifs/).
  ⑥ 이전 결과 · 실행 폴더가 있으면 착수 거부(러너가 cached 로 섞지 않게).
완주(작업마다, 값이 아니라 표지로): `Simulation finished` · CO₂ · N₂ · water 의 `Average loading absolute [mol/kg framework]` **각각 정확히 한 번**
(run_water.parse_components 는 첫 일치를 쓰므로 여기서 셈) · rc 0 · 씨앗 고유 · 물 순전하 0 · 입력 성분 3 · 출력 `Component 2 [N2]` ·
막음 대상은 성분마다 `Pockets are blocked for this component` · not-found 0 · `Number of pockets blocked in a unitcell` = 구 수 × 셀 수.
정의: S_humid = (N_CO₂/N_N₂) / (0.150000/0.821479) · 상대 ± = √((e_C/N_C)² + (e_N/N_N)²)(E-23 · T-J1′ 의 S_mix 와 같은 전파).
3회 평균의 ± = ±̄/√n · 회차 SD 병기. **판정 없음 — 종합자.** §E 의 두 문턱(N₂ 상대 ± 20 % · S_humid 평균 상대 ± 10 %)은 넘었는지만 기계적으로 적음.

env  ZNBDT_E_TARGETS 쉼표(기본 = laptop2 몫 다섯: e22_parent · e24i_cn_open · e24i_br_open · e24i_cl_open · e24i_ch3_open)
     ZNBDT_E_MACHINE(기본 laptop2) · ZNBDT_E_WORKERS(기본 6) · ZNBDT_E_REPS(기본 3)
     ZNBDT_E_SMOKE=1  사이클 10 · 초기화 0 · 대상마다 r1 하나 · 실행 폴더 · 결과를 저장소 밖(~/.mof_chain/znbdt_e3_smoke_<기기>)
     ZNBDT_E_DRY=1    RASPA 를 띄우지 않고 고친 입력만 저장소 밖(~/.mof_chain/znbdt_e3_dry_<기기>)에 씀
결과: results_znbdt_e_humid3_<기기>.json + results_znbdt_e_humid3_<기기>_audit.json(둘 다 postman RESULT_PATTERNS 의 results_*.json).
"""
import fcntl
import glob
import hashlib
import json
import math
import os
import re
import shutil
import statistics as st
import sys
import time
from concurrent.futures import ProcessPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import ff_gate                   # noqa: E402
import run_humid_wc_v3w as V     # noqa: E402
import run_aryl_gcmc as rg       # noqa: E402
import run_water as rw           # noqa: E402
hw = V.hw

Y = {'CO2': 0.150000, 'N2': 0.821479, 'water': 0.028521}
P_TOT = 100000
DEFAULT = 'e22_parent,e24i_cn_open,e24i_br_open,e24i_cl_open,e24i_ch3_open'
BASES = [t for t in os.environ.get('ZNBDT_E_TARGETS', DEFAULT).split(',') if t]
MACHINE = os.environ.get('ZNBDT_E_MACHINE', 'laptop2')
REPS = int(os.environ.get('ZNBDT_E_REPS', '3'))
SMOKE = bool(os.environ.get('ZNBDT_E_SMOKE'))
DRY = bool(os.environ.get('ZNBDT_E_DRY'))
STAGGER = 15.0
NOT_FOUND = "'Blocking-pocket' file not found"
SRC = os.path.join(HERE, 'charged_v3')
ZB = os.path.join(HERE, 'e24i_zeo_runs', 'e24i_c2h5_open')
BLOCKS = {'e24i_c2h5_open': {'CO2': (os.path.join(ZB, 'block1.65', 'e24i_c2h5_open_relaxed.block'), '47e3a6df6472e1b04b6a0745b20d92d7'),
                             'N2': (os.path.join(ZB, 'block1.82', 'e24i_c2h5_open_relaxed.block'), 'c5b5eeb2f730d24b3fe53e8d8683e7d3'),
                             'water': (os.path.join(ZB, 'block1.30', 'e24i_c2h5_open_relaxed.block'), 'cdbdbee0f181178c95bb3bab2d9b8618')}}
CHAIN = os.path.expanduser('~/.mof_chain'); os.makedirs(CHAIN, exist_ok=True)

hw.CONDITIONS = [('ads', 0.15e5, 298.0, hw.P_SAT_298)]
hw.MAX_WORKERS = int(os.environ.get('ZNBDT_E_WORKERS', '6'))
if SMOKE or DRY:
    ROOT = os.path.join(CHAIN, f"znbdt_e3_{'smoke' if SMOKE else 'dry'}_{MACHINE}")
    hw.CYCLES, hw.INIT = 10, 0
    REPS_RUN = [1]
    OUT = os.path.join(ROOT, f"results_znbdt_e_humid3_{MACHINE}_{'smoke' if SMOKE else 'dry'}.json")
else:
    ROOT = os.path.join(HERE, 'humid_wc_runs_v3w', f'znbdt_e3_{MACHINE}')       # humid_wc_runs_v3w/ 는 gitignore
    REPS_RUN = list(range(1, REPS + 1))
    OUT = os.path.join(HERE, f'results_znbdt_e_humid3_{MACHINE}.json')
AUDIT = OUT.replace('.json', '_audit.json')
hw.RUNS = os.path.join(ROOT, 'runs')
hw.CHARGED = os.path.join(ROOT, 'cifs')
LOCK = os.path.join(CHAIN, f'.znbdt_e3_{MACHINE}_start.lock')
TAGS = [f'{b}_e3r{k}' for b in BASES for k in REPS_RUN]
hw.TARGETS = TAGS
JOBS = [(t, lab, p, T, ps) for t in TAGS for lab, p, T, ps in hw.CONDITIONS]
T0 = time.time()                 # fork 로 워커에 물려짐

MOVES = ('            TranslationProbability    0.5\n'
         '            RotationProbability       0.3\n'
         '            ReinsertionProbability    0.1\n'
         '            SwapProbability           1.0\n'
         '            CreateNumberOfMolecules   0\n')       # run_humid_wc.run_one 과 같은 문자열


def base_of(tag):
    return tag.rsplit('_e3r', 1)[0]


def md5(p):
    return hashlib.md5(open(p, 'rb').read()).hexdigest()


def head(i, g):
    return f"Component {i} MoleculeName              {g}\n            MoleculeDefinition        TraPPE\n"


def _once(pat, s, what):
    n = len(re.findall(pat, s, flags=re.M))
    if n != 1:
        raise RuntimeError(f'앵커 {what} 가 {n}회 — 정확히 한 번이 아님, RASPA 안 띄움')


def patch_input(s, base):
    pat = r'^ExternalPressure[ \t]+\S+[ \t]*$'
    _once(pat, s, 'ExternalPressure')
    s = re.sub(pat, f'ExternalPressure              {P_TOT}', s, flags=re.M)
    for i, g in ((0, 'CO2'), (1, 'water')):
        pat = re.escape(head(i, g)) + r'            MolFraction[ \t]+\S+\n'
        _once(pat, s, f'{g} MolFraction')
        s = re.sub(pat, lambda m, i=i, g=g: head(i, g) + f'            MolFraction               {Y[g]:.6f}\n', s)
    if 'Component 2' in s or re.search(r'MoleculeName\s+N2\b', s):
        raise RuntimeError('입력에 이미 Component 2 / N2 가 있음 — RASPA 안 띄움')
    if not s.endswith(MOVES):
        raise RuntimeError('입력 끝이 물 성분의 이동 확률 블록이 아님 — 덧붙일 자리 불명, RASPA 안 띄움')
    s = s + '\n' + head(2, 'N2') + f"            MolFraction               {Y['N2']:.6f}\n" + MOVES
    if base in BLOCKS:
        for i, g in ((0, 'CO2'), (1, 'water'), (2, 'N2')):
            a = head(i, g)
            if s.count(a) != 1:
                raise RuntimeError(f'{g} 막음 앵커가 {s.count(a)}회 — RASPA 안 띄움')
            s = s.replace(a, a + f'            BlockPockets              yes\n            BlockPocketsFileName      blk_{g.lower()}\n')
    n = len(re.findall(r'^Component \d+ MoleculeName', s, flags=re.M))
    if n != 3:
        raise RuntimeError(f'고친 입력의 성분 수 {n} ≠ 3 — RASPA 안 띄움')
    return s


_real_run = hw.subprocess.run


def _run(args, *a, **k):
    cwd = k.get('cwd')
    if cwd and args and args[0] == rg.SIMULATE:
        p = os.path.join(cwd, 'simulation.input')
        tag = os.path.basename(cwd).split('_', 1)[1]          # 실행 폴더 = ads_<tag>
        base = base_of(tag)
        s = patch_input(open(p).read(), base)
        with open(p, 'w') as f:
            f.write(s)
        if base in BLOCKS:
            for g, (src, _) in BLOCKS[base].items():
                shutil.copy(src, os.path.join(cwd, f'blk_{g.lower()}.block'))
        if DRY:
            with open(os.path.join(cwd, 'returncode.txt'), 'w') as f:
                f.write('dry\n')
            return hw.subprocess.CompletedProcess(args, 0)
        ef = open(os.path.join(cwd, 'stderr.txt'), 'w')
        k['stderr'] = ef
        try:
            cp = _real_run(args, *a, **k)
        finally:
            ef.close()
        with open(os.path.join(cwd, 'returncode.txt'), 'w') as f:
            f.write(f'{cp.returncode}\n')
        return cp
    return _real_run(args, *a, **k)


hw.subprocess.run = _run          # 러너의 RASPA 호출만 바뀜
_orig = hw.run_one


def staggered(job):
    i = JOBS.index(job)
    w = T0 + i * STAGGER - time.time()
    if w > 0:
        time.sleep(w)
    with open(LOCK, 'a+') as f:
        fcntl.flock(f, fcntl.LOCK_EX)
        try:
            f.seek(0)
            s = f.read().split()
            gap = (float(s[-1]) + 2.0 - time.time()) if s else 0
            if gap > 0:
                time.sleep(gap)
            f.write(f'{time.time():.3f}\n')
            f.flush()
        finally:
            fcntl.flock(f, fcntl.LOCK_UN)
    return _orig(job)


def prep():
    """반복 사본(바이트 같음, md5 대조) · 막음 파일 md5 · 구 수."""
    os.makedirs(hw.CHARGED, exist_ok=True)
    info = {'cifs': {}, 'blocks': {}}
    for b in BASES:
        src = os.path.join(SRC, f'{b}_DDEC6.cif')
        if not os.path.exists(src):
            raise SystemExit(f'  !! charged_v3 에 없음: {src}')
        m = md5(src)
        info['cifs'][b] = {'src': os.path.relpath(src, HERE), 'md5': m, 'copies': []}
        for k in REPS_RUN:
            dst = os.path.join(hw.CHARGED, f'{b}_e3r{k}_DDEC6.cif')
            if not os.path.exists(dst):
                shutil.copyfile(src, dst)
            if md5(dst) != m:
                raise SystemExit(f'  !! 사본 md5 불일치 {dst}')
            info['cifs'][b]['copies'].append(os.path.basename(dst))
        if b in BLOCKS:
            info['blocks'][b] = {}
            for g, (f, want) in BLOCKS[b].items():
                got = md5(f)
                if got != want:
                    raise SystemExit(f'  !! 막음 파일 md5 불일치 {f}: {got} ≠ {want}')
                n_sph = int(open(f).readline().split()[0])
                info['blocks'][b][g] = {'file': os.path.relpath(f, HERE), 'md5': got, 'n_spheres': n_sph}
    return info


def loads(txt):
    cur, hits = None, {}
    for ln in txt.splitlines():
        m = re.search(r'Component\s+\d+\s+\[(\w+)\]', ln)
        if m:
            cur = m.group(1)
        if cur and 'Average loading absolute [mol/kg framework]' in ln:
            v = re.search(r':?\s*([0-9.eE+-]+)\s*\+/-\s*([0-9.eE+-]+)', ln)
            if v:
                hits.setdefault(cur, []).append((float(v.group(1)), float(v.group(2))))
    return hits


def block_audit(txt):
    cur, out = None, {}
    for ln in txt.splitlines():
        m = re.match(r'Component (\d+) \[(\w+)\] \(Adsorbate molecule\)', ln)
        if m:
            cur = m.group(2)
            out.setdefault(cur, {'n_blocked': None, 'blocked_line': False, 'block_file': None})
            continue
        if cur is None:
            continue
        c = out[cur]
        m = re.search(r'Number of pockets blocked in a unitcell:\s*(\d+)', ln)
        if m and c['n_blocked'] is None:
            c['n_blocked'] = int(m.group(1))
        if 'Pockets are blocked for this component' in ln:
            c['blocked_line'] = True
        m = re.search(r'Block-pockets Filename:\s*(\S+)', ln)
        if m and c['block_file'] is None:
            c['block_file'] = m.group(1)
    return out


def row_of(tag, status, info):
    base = base_of(tag)
    d = os.path.join(hw.RUNS, f'ads_{tag}')
    r = {'name': tag, 'base': base, 'runner_status': status, 'dir': os.path.relpath(d, HERE) if d.startswith(HERE) else d}
    inp_p = os.path.join(d, 'simulation.input')
    inp = open(inp_p).read() if os.path.exists(inp_p) else ''
    r['input_components'] = len(re.findall(r'^Component \d+ MoleculeName', inp, flags=re.M))
    r['input_external_pressure'] = (re.search(r'^ExternalPressure\s+(\S+)', inp, flags=re.M) or [None, None])[1]
    r['input_molfractions'] = dict(re.findall(r'MoleculeName\s+(\w+)\n\s+MoleculeDefinition\s+\S+\n(?:\s+BlockPockets.*\n\s+BlockPocketsFileName.*\n)?\s+MolFraction\s+(\S+)', inp))
    r['input_blockpockets_lines'] = inp.count('BlockPockets              yes')
    m = re.search(r'UnitCells\s+(\d+)\s+(\d+)\s+(\d+)', inp)
    uc = [int(x) for x in m.groups()] if m else None
    r['unit_cells'] = uc
    outs = glob.glob(os.path.join(d, 'Output', 'System_0', '*.data'))
    if len(outs) != 1:
        r.update(ok=False, why=f'.data {len(outs)}개')
        return r
    txt = open(outs[0], encoding='utf-8', errors='ignore').read()
    h = loads(txt)
    s = re.search(r'Random number seed:\s*(\d+)', txt)
    rcf = os.path.join(d, 'returncode.txt')
    err_p = os.path.join(d, 'stderr.txt')
    err = open(err_p, errors='ignore').read() if os.path.exists(err_p) else None
    r.update(finished=rg.finished(outs[0]), loading_line_counts={k: len(v) for k, v in h.items()},
             component2_N2_in_output='Component 2 [N2]' in txt, net_charge_ok=rw.net_charge_ok(outs[0]),
             seed=int(s.group(1)) if s else None,
             returncode=(open(rcf).read().strip() if os.path.exists(rcf) else None),
             stderr_not_found=(NOT_FOUND in err) if err is not None else None, not_found_in_output=NOT_FOUND in txt)
    try:
        r['returncode'] = int(r['returncode'])
    except (TypeError, ValueError):
        pass
    gates = [r['finished'], set(h) == {'CO2', 'N2', 'water'} and all(len(v) == 1 for v in h.values()), r['returncode'] == 0,
             r['stderr_not_found'] is False, not r['not_found_in_output'], r['net_charge_ok'], r['input_components'] == 3,
             r['component2_N2_in_output'], r['seed'] is not None]
    if base in BLOCKS:
        ba = block_audit(txt)
        ncell = uc[0] * uc[1] * uc[2] if uc else None
        r['block'] = {}
        for g, bi in info['blocks'][base].items():
            c = ba.get(g, {})
            want = bi['n_spheres'] * ncell if ncell else None
            r['block'][g] = {**c, 'n_spheres': bi['n_spheres'], 'n_cells': ncell, 'expected_n_blocked': want,
                             'n_blocked_eq_spheres_x_cells': c.get('n_blocked') == want}
            gates += [c.get('blocked_line') is True, c.get('n_blocked') == want]
        gates.append(r['input_blockpockets_lines'] == 3)
    else:
        gates.append(r['input_blockpockets_lines'] == 0)
    r['ok'] = bool(all(gates))
    if set(h) >= {'CO2', 'N2', 'water'}:
        (nc, ec), (nn, en), (nw, ew) = h['CO2'][0], h['N2'][0], h['water'][0]
        r.update(N_CO2=nc, N_CO2_err=ec, N_N2=nn, N_N2_err=en, N_H2O=nw, N_H2O_err=ew)
        if nc > 0 and nn > 0:
            S = (nc / nn) / (Y['CO2'] / Y['N2'])
            r.update(S_humid=S, S_humid_err=S * math.hypot(ec / nc, en / nn), N2_rel_pm=en / nn)
    return r


def summarize(rows, info, t_start):
    seeds = [r.get('seed') for r in rows]
    aud = {'n': len(rows), 'n_ok': sum(1 for r in rows if r.get('ok')),
           'seeds_distinct': None not in seeds and len(set(seeds)) == len(seeds),
           'loading_line_counts_all_1': all(r.get('loading_line_counts') == {'CO2': 1, 'N2': 1, 'water': 1} for r in rows),
           'component2_N2_seen_all': all(r.get('component2_N2_in_output') for r in rows)}
    mats = {}
    for b in BASES:
        rs = [r for r in rows if r['base'] == b and r.get('ok') and 'S_humid' in r]
        m = {'n_ok': len(rs)}
        if rs:
            v = [r['S_humid'] for r in rs]; e = [r['S_humid_err'] for r in rs]
            m.update(S_humid_each=v, S_humid_err_each=e, S_humid_mean=st.mean(v), S_humid_pm=st.mean(e) / math.sqrt(len(e)),
                     S_humid_SD=st.stdev(v) if len(v) > 1 else None,
                     N_CO2_mean=st.mean(r['N_CO2'] for r in rs), N_N2_mean=st.mean(r['N_N2'] for r in rs), N_H2O_mean=st.mean(r['N_H2O'] for r in rs),
                     N2_rel_pm_each=[r['N2_rel_pm'] for r in rs])
            m['S_humid_rel_pm'] = m['S_humid_pm'] / m['S_humid_mean']
            m['flag_N2_rel_pm_gt_20pct'] = any(x > 0.20 for x in m['N2_rel_pm_each'])
            m['flag_S_rel_pm_gt_10pct'] = m['S_humid_rel_pm'] > 0.10
            m['blocked'] = b in BLOCKS
        mats[b] = m
    out = {'test': 'Zn(bib)(bdtdc) 보강 E — 습윤 3성분 흡착점 S_humid', 'assign': 'ASSIGN_ZNBDT_SUPP_20261103.md §E (f589c08b) + 사용자 11-04 −C₂H₅ 추가',
           'wrapper': 'run_znbdt_e_humid3.py', 'wrapper_md5': md5(os.path.abspath(__file__)), 'machine': MACHINE, 'smoke': SMOKE, 'dry': DRY,
           'started': time.strftime('%F %T', time.localtime(t_start)), 'made': time.strftime('%F %T'),
           'protocol': {'T_K': 298.0, 'P_Pa': P_TOT, 'y': Y, 'p_h2o_Pa_runner': hw.P_H2O, 'cycles': hw.CYCLES, 'init': hw.INIT,
                        'ff_md5_gate': ff_gate.md5_gate()[1], 'water': 'TIP5P-Ew 5자리(run_water.WATER_DEF) · Hw none/Lw none(ff_gate)',
                        'replicates': 'byte-identical copies, seed = 착수 초(15 s 간격 + 2 s 잠금)'},
           'definition': 'S_humid = (N_CO2/N_N2)/(0.150000/0.821479); 상대 ± = hypot(e_C/N_C, e_N/N_N); 평균 ± = ±̄/√n; SD = 회차 SD',
           'inputs': info, 'audit_summary': aud, 'materials': mats, 'rows': rows,
           'thresholds_registered': '§E: 회차 N₂ 상대 ± > 20 % 또는 평균 S_humid 상대 ± > 10 % → 사이클 연장안을 사용자에게(E′). 넘었는지만 적음.',
           'judgement': '없음 — 종합자'}
    for path, obj in ((OUT, out), (AUDIT, {'audit_summary': aud, 'smoke_ref': os.environ.get('ZNBDT_E_SMOKE_REF'),
                                            'rows': [{k: r.get(k) for k in ('name', 'ok', 'finished', 'loading_line_counts', 'component2_N2_in_output',
                                                                            'returncode', 'seed', 'stderr_not_found', 'net_charge_ok', 'input_components',
                                                                            'input_blockpockets_lines', 'block')} for r in rows]})):
        tmp = path + '.tmp'
        json.dump(obj, open(tmp, 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
        os.replace(tmp, path)
    return out


def main():
    t_start = time.time()
    ok, m = ff_gate.md5_gate()
    print(f"  파일 관문 md5 {m} {'일치' if ok else '불일치 — 중단'}", flush=True)
    if not ok:
        return 3
    print(f'Zn(bib)(bdtdc) E 습윤 3성분 — 기기 {MACHINE} · 대상 {BASES} · 반복 {REPS_RUN} · 작업 {len(JOBS)} · 워커 {hw.MAX_WORKERS} · '
          f'사이클 {hw.CYCLES}+{hw.INIT} · 스모크 {SMOKE} · 드라이 {DRY}', flush=True)
    print(f'  RUNS {hw.RUNS}\n  OUT  {OUT}', flush=True)
    if os.path.exists(OUT) or any(os.path.exists(os.path.join(hw.RUNS, f'ads_{t}')) for t in TAGS):
        print('  !! 이전 결과 · 실행 폴더 있음 — 중단(러너가 cached 로 재사용하므로)', flush=True)
        return 1
    info = prep()
    os.makedirs(hw.RUNS, exist_ok=True)
    stat = {}
    with ProcessPoolExecutor(max_workers=min(hw.MAX_WORKERS, len(JOBS))) as ex:
        for tag, label, r, s in ex.map(staggered, JOBS):
            stat[tag] = s
            print(f'  [{s:>12}] {label} {tag}  ' + (' · '.join(f'{k} {v[0]:.4g}' for k, v in r.items()) if r else '-') + f'  {time.strftime("%T")}', flush=True)
    rows = [row_of(t, stat.get(t), info) for t in TAGS]
    out = summarize(rows, info, t_start)
    print('감사', json.dumps(out['audit_summary'], ensure_ascii=False), flush=True)
    for r in rows:
        print(f"  {r['name']:<24} ok {r.get('ok')} · 완주 {r.get('finished')} · 적재줄 {r.get('loading_line_counts')} · C2[N2] {r.get('component2_N2_in_output')} · "
              f"rc {r.get('returncode')} · 씨앗 {r.get('seed')} · 막음 {json.dumps(r.get('block'), ensure_ascii=False) if r.get('block') else '-'} · "
              f"S_humid {r.get('S_humid', float('nan')):.2f} ± {r.get('S_humid_err', float('nan')):.2f}", flush=True)
    for b, mm in out['materials'].items():
        if mm.get('n_ok'):
            print(f"  {b:<18} n {mm['n_ok']} · S_humid {mm['S_humid_mean']:.2f} ± {mm['S_humid_pm']:.2f} · SD {mm['S_humid_SD']} · "
                  f"N₂ 상대 ± {[round(x, 3) for x in mm['N2_rel_pm_each']]}", flush=True)
    return 0 if (DRY or out['audit_summary']['n_ok'] == len(rows)) else 2


if __name__ == '__main__':
    sys.exit(main())
