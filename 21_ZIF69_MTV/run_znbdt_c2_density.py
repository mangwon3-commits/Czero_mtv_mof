# -*- coding: utf-8 -*-
"""ZNBDT-C2 후속 명령 #1 — CO₂/N₂ 혼합 질량중심(COM) 밀도 격자 4구조 · laptop2.
등록 `ASSIGN_ZNBDT_C2_FOLLOWUP_20261105.md` §1(종합자 b5991256). 관측용이며 판정은 없습니다(종합자 몫).

`run_density_map.py`(md5 56c591c5) 를 **무수정 import** 하고, 모듈 전역과 RASPA 호출만 감쌉니다.
  ① CHARGED → 실행 뿌리 아래 cifs/ — charged_v3 의 **바이트 같은 사본** `<tag>_DDEC6.cif`(md5 대조).
     apolarU 원본 이름은 `_DDEC6mod.cif` 여서 run_one 이 찾는 이름으로 사본만 맞춥니다. charged_v3 는 건드리지 않습니다.
  ② OUT → density_znbdt_c2/ · CYCLES 15000 · INIT 5000(등록 5,000+15,000, run_tj1_mix 와 같음).
     GRID 90 · TEMP 298 · CUTOFF 12 · UFF_MOF · 전하 ON(DDEC6) · Ewald 는 모듈 그대로입니다.
  ③ RASPA 호출 직전 simulation.input 고침 — run_tj1_mix 의 혼합 입력과 같은 꼴:
     ExternalPressure → 100000 · CO₂ 절에 MolFraction 0.150000 · N₂ 절(TraPPE · 같은 이동 확률 · MolFraction 0.850000) 덧붙임.
     고칠 자리(앵커)가 각각 정확히 한 번이 아니면 RASPA 를 띄우지 않고 예외를 냅니다.
  ④ run_one 은 반환코드를 버리므로 호출을 감싸 rc.txt(반환코드 · 시작 · 끝 시각)에 씁니다. 착수 간격 15 s × i.
완주(작업마다, 값이 아니라 표지로): `Simulation finished` · CO2 · N2 의 `Average loading absolute [mol/kg framework]` **각각 정확히 한 번** ·
rc 0 · `VTK/System_0/COMDensityProfile_CO2.vtk` · `_N2.vtk` 존재(존재만으로는 완주가 아님 — CLAUDE.md §0 09-24).
env  ZNBDT_C2D_DRY=1  RASPA 를 띄우지 않고 고친 입력만 저장소 밖(~/.mof_chain/znbdt_c2_density_dry)에 씁니다.
     ZNBDT_C2D_WORKERS(기본 4)
결과: results_znbdt_c2_density_laptop2.json(표지 수 · 적재 · 씨앗 · 시간 · 격자 파일). 1씨앗이라 산포는 재지 않으며 수치 비교에 쓰지 않습니다.
"""
import glob
import hashlib
import json
import os
import re
import subprocess as _sp
import sys
import time
import types
from concurrent.futures import ProcessPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import run_density_map as dm     # noqa: E402

DM_MD5 = '56c591c508e3505d6b75dc8995c5fc46'
MACHINE = 'laptop2'
DRY = bool(os.environ.get('ZNBDT_C2D_DRY'))
WORKERS = int(os.environ.get('ZNBDT_C2D_WORKERS', '4'))
STAGGER = 15.0
P_TOT = 100000
Y = {'CO2': 0.150000, 'N2': 0.850000}
SRC = os.path.join(HERE, 'charged_v3')
# tag → (charged_v3 원본 이름, md5 앞 8자리 — 원본 확인용; apolarU 는 등록문 값)
TARGETS = {'e22_parent':       ('e22_parent_DDEC6.cif', 'f15ce100'),
           'e24i_cn_open':     ('e24i_cn_open_DDEC6.cif', '8fd4fc85'),
           'e24i_ch3_open':    ('e24i_ch3_open_DDEC6.cif', 'a8e6a165'),
           'znbdt_c2_apolarU': ('znbdt_c2_apolarU_DDEC6mod.cif', '3e079487')}
ORDER = list(TARGETS)
CHAIN = os.path.expanduser('~/.mof_chain'); os.makedirs(CHAIN, exist_ok=True)
ROOT = os.path.join(CHAIN, 'znbdt_c2_density_dry') if DRY else os.path.join(HERE, 'density_znbdt_c2')
OUT = os.path.join(ROOT if DRY else HERE, f"results_znbdt_c2_density_{MACHINE}{'_dry' if DRY else ''}.json")

dm.OUT = ROOT
dm.CHARGED = os.path.join(ROOT, 'cifs')
dm.CYCLES, dm.INIT = 15000, 5000

MOVES = ('            TranslationProbability    0.5\n'
         '            RotationProbability       0.3\n'
         '            ReinsertionProbability    0.1\n'
         '            SwapProbability           1.0\n'
         '            CreateNumberOfMolecules   0\n')      # run_density_map.write_input · run_tj1_mix 와 같은 문자열
HEAD_CO2 = ('Component 0 MoleculeName              CO2\n'
            '            MoleculeDefinition        TraPPE\n')


def md5(p):
    return hashlib.md5(open(p, 'rb').read()).hexdigest()


def _once(pat, s, what, flags=0):
    n = len(re.findall(pat, s, flags=flags))
    if n != 1:
        raise RuntimeError(f'앵커 {what} 가 {n}회 — 정확히 한 번이 아님, RASPA 안 띄움')


def patch_input(s):
    pat = r'^ExternalPressure[ \t]+\S+[ \t]*$'
    _once(pat, s, 'ExternalPressure', re.M)
    s = re.sub(pat, f'ExternalPressure              {P_TOT}', s, flags=re.M)
    _once(re.escape(HEAD_CO2 + MOVES), s, 'CO2 절')
    if 'Component 1' in s or re.search(r'MoleculeName\s+N2\b', s) or 'MolFraction' in s:
        raise RuntimeError('입력에 이미 Component 1 / N2 / MolFraction 이 있음 — RASPA 안 띄움')
    s = s.replace(HEAD_CO2, HEAD_CO2 + f"            MolFraction               {Y['CO2']:.6f}\n", 1)
    s = s.rstrip('\n') + '\n\n' + ('Component 1 MoleculeName              N2\n'
                                   '            MoleculeDefinition        TraPPE\n'
                                   f"            MolFraction               {Y['N2']:.6f}\n") + MOVES
    return s


def _run(args, *a, **k):
    """run_density_map.run_one 안의 subprocess.run 자리 — 입력을 고치고, 착수 간격을 두고, 반환코드를 남깁니다."""
    cwd = k.get('cwd')
    p = os.path.join(cwd, 'simulation.input')
    s = patch_input(open(p).read())
    with open(p, 'w') as f:
        f.write(s)
    tag = os.path.basename(cwd).rsplit('__', 1)[0]
    if DRY:
        with open(os.path.join(cwd, 'rc.txt'), 'w') as f:
            f.write('dry\n')
        return _sp.CompletedProcess(args, 0)
    time.sleep(STAGGER * ORDER.index(tag))
    t0 = time.time()
    cp = _sp.run(args, *a, **k)
    with open(os.path.join(cwd, 'rc.txt'), 'w') as f:
        f.write(f'{cp.returncode} {t0:.0f} {time.time():.0f}\n')
    return cp


dm.subprocess = types.SimpleNamespace(run=_run, DEVNULL=_sp.DEVNULL, TimeoutExpired=_sp.TimeoutExpired)


def loads(path):
    """성분별 'Average loading absolute [mol/kg framework]' 줄을 모두 셉니다(run_tj1_mix.loads 와 같은 규칙)."""
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


def row_of(tag, st, info):
    d = os.path.join(ROOT, f'{tag}__q_on')
    r = {'name': tag, 'dir': os.path.relpath(d, HERE), 'status': st, **info[tag]}
    rc = os.path.join(d, 'rc.txt')
    if os.path.exists(rc):
        w = open(rc).read().split()
        r['returncode'] = None if w[0] == 'dry' else int(w[0])
        if len(w) == 3:
            r['minutes'] = round((int(w[2]) - int(w[1])) / 60, 1)
    outs = glob.glob(os.path.join(d, 'Output', 'System_0', '*.data'))
    r['n_data'] = len(outs)
    if outs:
        o = outs[0]
        txt = open(o, encoding='utf-8', errors='ignore').read()
        r['finished'] = 'Simulation finished' in txt
        h = loads(o)
        r['loading_line_counts'] = {g: len(h.get(g, [])) for g in ('CO2', 'N2')}
        for g in ('CO2', 'N2'):
            if len(h.get(g, [])) == 1:
                r[f'N_{g}'], r[f'N_{g}_err'] = h[g][0]
        s = re.search(r'Random number seed:\s*(\d+)', txt)
        r['seed'] = int(s.group(1)) if s else None
    vt = {}
    for g in ('CO2', 'N2'):
        f = os.path.join(d, 'VTK', 'System_0', f'COMDensityProfile_{g}.vtk')
        vt[g] = {'vtk': os.path.exists(f), 'vtk_bytes': os.path.getsize(f) if os.path.exists(f) else None,
                 'gz_md5': md5(f + '.gz') if os.path.exists(f + '.gz') else None}
    r['com_grids'] = vt
    r['ok'] = bool(not DRY and r.get('finished') and r.get('returncode') == 0
                   and r.get('loading_line_counts') == {'CO2': 1, 'N2': 1} and all(v['vtk'] for v in vt.values()))
    return r


def prep():
    os.makedirs(dm.CHARGED, exist_ok=True)
    info = {}
    for tag, (fn, want8) in TARGETS.items():
        src = os.path.join(SRC, fn)
        if not os.path.exists(src):
            raise SystemExit(f'  !! charged_v3 에 없음: {src}')
        m = md5(src)
        if not m.startswith(want8):
            raise SystemExit(f'  !! 원본 md5 불일치 {fn}: {m} (등록 {want8})')
        dst = os.path.join(dm.CHARGED, f'{tag}_DDEC6.cif')
        if not os.path.exists(dst):
            with open(src, 'rb') as fi, open(dst, 'wb') as fo:
                fo.write(fi.read())
        if md5(dst) != m:
            raise SystemExit(f'  !! 사본 md5 불일치 {dst}')
        info[tag] = {'cif_src': os.path.relpath(src, HERE), 'cif_md5': m, 'cif_copy': os.path.relpath(dst, HERE)}
    return info


def main():
    got = md5(os.path.abspath(dm.__file__))
    if got != DM_MD5:
        print(f'  !! run_density_map.py md5 불일치 — 착수 안 함 ({got} ≠ {DM_MD5})', flush=True)
        return 3
    print(f'ZNBDT-C2 밀도 격자 — {MACHINE} · 대상 {ORDER} · 사이클 {dm.CYCLES}+{dm.INIT} · 격자 {dm.GRID}^3 · '
          f'P {P_TOT} · y {Y} · 워커 {WORKERS} · 드라이 {DRY}\n  ROOT {ROOT}\n  OUT  {OUT}', flush=True)
    if os.path.exists(OUT) or any(os.path.exists(os.path.join(ROOT, f'{t}__q_on')) for t in ORDER):
        print('  !! 이전 결과 · 실행 폴더 있음 — 중단(run_one 이 cached 로 재사용하므로)', flush=True)
        return 1
    info = prep()
    t_start = time.time()
    stat = {}
    with ProcessPoolExecutor(max_workers=min(WORKERS, len(ORDER))) as ex:
        for tag, label, v, e, st in ex.map(dm._star, [(t, True) for t in ORDER]):
            stat[tag] = st
            print(f'  [{st:>28}] {tag:<18} CO2 {v}  {time.strftime("%T")}', flush=True)
    rows = [row_of(t, stat.get(t), info) for t in ORDER]
    out = {'registration': 'ASSIGN_ZNBDT_C2_FOLLOWUP_20261105.md §1 (b5991256)', 'machine': MACHINE, 'dry': DRY,
           'launcher': os.path.basename(__file__), 'launcher_md5': md5(os.path.abspath(__file__)),
           'module': 'run_density_map.py', 'module_md5': got,
           'conditions': {'T_K': dm.TEMP, 'P_Pa': P_TOT, 'y': Y, 'cycles': dm.CYCLES, 'init': dm.INIT, 'grid': dm.GRID,
                          'cutoff': dm.CUTOFF, 'forcefield': 'UFF_MOF', 'charges': 'DDEC6 on (Ewald)', 'seeds_per_structure': 1},
           'note': '관측용 1씨앗 — 산포 없음, 수치 비교에 쓰지 않음. 판정 없음(종합자).',
           'n_ok': sum(1 for r in rows if r['ok']), 'n_rows': len(rows),
           'wall_minutes': round((time.time() - t_start) / 60, 1), 'rows': rows}
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, 'w', encoding='utf-8') as f:
        json.dump(out, f, indent=1, ensure_ascii=False)
    for r in rows:
        print(f"  {r['name']:<18} ok {r['ok']} · 완주 {r.get('finished')} · 적재줄 {r.get('loading_line_counts')} · rc {r.get('returncode')} · "
              f"씨앗 {r.get('seed')} · VTK {[g for g, v in r['com_grids'].items() if v['vtk']]} · "
              f"N_CO2 {r.get('N_CO2')} · N_N2 {r.get('N_N2')} · {r.get('minutes')} 분", flush=True)
    print(f"  n_ok {out['n_ok']}/{out['n_rows']} · {out['wall_minutes']} 분 · {OUT}", flush=True)
    return 0 if (DRY or out['n_ok'] == len(rows)) else 2


if __name__ == '__main__':
    sys.exit(main())
