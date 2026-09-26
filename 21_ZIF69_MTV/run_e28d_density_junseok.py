# -*- coding: utf-8 -*-
"""MAGI-005 E-28d (Junseok) — C₂H₅ 50 % 실현 a(e24h_c2h5_050a, **막음**) 습윤(RH90) 밀도 격자. 등록 ASSIGN_MAGI5B §HKHOME 21차 후속 등록 12:20(2aba255f, 자료 0건).
run_e28c_density.py(Junseok E-28c) 사본 — 바꾼 것: 대상(BASE_TAG) · 막음 파일(E-24g Zeo++ e24g_zeo_runs/<tag>/block1.65 · block1.30) · 감사 · rc 파일 이름(e28d_) · 문구.
자 · 막음 삽입 · 관문은 원판 그대로. 원판 머리말:
MAGI-005 E-28c (Junseok 18차) — 새 1 · 2위(−Cl · −C₂H₅) 습윤(RH90) 밀도 격자(포스터 그림). 등록 ASSIGN_MAGI5B §Junseok 18차(d490a429, 자료 0건).

자: E-28 습윤과 같음 — run_density_water_v3w.py(→ run_density_water_v3 → run_water.run_one) 무수정 import:
    CO₂ 15 kPa + H₂O 2852.1 Pa · 298 K · 5,000+15,000 · 90³ 격자(격자 주입 · VTK 보존은 run_density_water_v3 그대로). 대상마다 프로세스 1 —
    v3w 사용법 그대로 env DW_SUB(결과 폴더) · DW_EXTRA(대상 등록) · argv(대상).
C₂H₅ 만(env E28C_BLOCK=1): RASPA 호출 직전 simulation.input 두 성분 절에 BlockPockets 삽입 — CO₂ = E-24c block1.65 · 물 = E-24e block1.30
    (E-24f 와 같은 파일 · 같은 삽입; 자리가 성분마다 정확히 한 번이 아니면 RASPA 안 띄움) + stderr 파일 · 반환코드 기록. 격자 주입(v3)은 그 안쪽에서 그대로.
    Cl 은 주머니 0 이라 막음 없음 — 같은 래퍼를 E28C_BLOCK 없이.
끝에서(래퍼): 관문 감사(완주 · 씨앗 · C₂H₅ 는 성분마다 blocked 줄과 N = 구 × 단위셀) → <DW_SUB>/e28c_audit.json · COM 격자 VTK gzip(E-28 과 같이
    COMDensityProfile_{CO2,water}.vtk → .vtk.gz). 판정은 종합자.
사용: DW_SUB=tpl_<대상> DW_EXTRA=<대상> [E28C_BLOCK=1] python run_e28c_density.py <대상>
"""
import glob
import gzip
import json
import os
import re
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import run_density_water_v3w as W      # noqa: E402  D.OUT · rw.RUNS 를 env 로 정함
D = W.D
rw = D.rw

BASE_TAG = 'e24h_c2h5_050a'
BLOCK = {'CO2': os.path.join(HERE, 'e24g_zeo_runs', BASE_TAG, 'block1.65', BASE_TAG + '_relaxed.block'),
         'water': os.path.join(HERE, 'e24g_zeo_runs', BASE_TAG, 'block1.30', BASE_TAG + '_relaxed.block')}
KEY = {'CO2': 'co2', 'water': 'water'}
NOT_FOUND = "'Blocking-pocket' file not found"
BLOCKING = bool(os.environ.get('E28C_BLOCK'))


def nsph(comp):
    return int(open(BLOCK[comp]).read().split()[0])


def _inject(cwd):
    p = os.path.join(cwd, 'simulation.input')
    txt = open(p).read()
    if 'BlockPockets' in txt:
        return
    for comp in ('CO2', 'water'):
        pat = f'MoleculeName              {comp}\n            MoleculeDefinition        TraPPE\n'
        if txt.count(pat) != 1:
            raise RuntimeError(f'막음 삽입 자리 {comp} 가 {txt.count(pat)}번 — RASPA 안 띄움 ({cwd})')
        txt = txt.replace(pat, pat + f'            BlockPockets              yes\n            BlockPocketsFileName      {BASE_TAG}_{KEY[comp]}\n')
        shutil.copy(BLOCK[comp], os.path.join(cwd, f'{BASE_TAG}_{KEY[comp]}.block'))
    open(p, 'w').write(txt)
    print(f'    [막음] CO₂ {nsph("CO2")} 구 · 물 {nsph("water")} 구 삽입 — {os.path.basename(cwd)}', flush=True)


if BLOCKING:
    _inner = rw.subprocess.run          # = run_density_water_v3._run_with_grid(격자 주입) — 그 안쪽은 그대로

    def _run(cmd, *a, **k):
        cwd = k.get('cwd')
        if cwd and cmd and str(cmd[-1]) == 'simulation.input':
            _inject(cwd)
            ef = open(os.path.join(cwd, 'stderr.txt'), 'w')
            k['stderr'] = ef
            try:
                cp = _inner(cmd, *a, **k)
            finally:
                ef.close()
            with open(os.path.join(cwd, 'e28d_returncode.txt'), 'w') as f:
                f.write(f'{cp.returncode}\n')
            return cp
        return _inner(cmd, *a, **k)

    rw.subprocess.run = _run


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


def post(target, rc):
    d = os.path.join(rw.RUNS, f'rh{int(D.RH * 100):02d}_{target}')
    a = {'target': target, 'run_dir': os.path.relpath(d, HERE), 'blocking': BLOCKING, 'driver_rc': rc}
    outs = glob.glob(os.path.join(d, 'Output', 'System_0', '*.data'))
    if len(outs) == 1:
        txt = open(outs[0], encoding='utf-8', errors='ignore').read()
        inp = open(os.path.join(d, 'simulation.input')).read()
        uc = [int(x) for x in re.search(r'UnitCells\s+(\d+)\s+(\d+)\s+(\d+)', inp).groups()]
        s = re.search(r'Random number seed:\s*(\d+)', txt)
        a.update(finished=rw.finished(outs[0]), seed=int(s.group(1)) if s else None, unit_cells=uc,
                 grid_directive='ComputeDensityProfile3DVTKGrid    yes' in inp, blockpockets_in_input=inp.count('BlockPockets              yes'))
        if BLOCKING:
            n = uc[0] * uc[1] * uc[2]
            ba = block_audit(txt)
            rcf = os.path.join(d, 'e28d_returncode.txt')
            err = open(os.path.join(d, 'stderr.txt'), errors='ignore').read() if os.path.exists(os.path.join(d, 'stderr.txt')) else ''
            a.update(block=ba, n_expected={c: nsph(c) * n for c in ('CO2', 'water')}, stderr_not_found=NOT_FOUND in err,
                     returncode=int(open(rcf).read().strip()) if os.path.exists(rcf) else None)
            a['block_ok'] = all(ba.get(c, {}).get('blocked_line') and ba.get(c, {}).get('n_blocked') == a['n_expected'][c] for c in ('CO2', 'water')) \
                and not a['stderr_not_found'] and a['returncode'] == 0
    else:
        a['why'] = f'.data {len(outs)}개'
    gz = []
    for f in sorted(glob.glob(os.path.join(d, 'VTK', 'System_0', 'COMDensityProfile_*.vtk'))):
        with open(f, 'rb') as fi, gzip.open(f + '.gz', 'wb') as fo:
            shutil.copyfileobj(fi, fo)
        os.remove(f)
        gz.append(os.path.relpath(f + '.gz', HERE))
    a['com_grids_gz'] = gz
    json.dump(a, open(os.path.join(D.OUT, 'e28d_audit.json'), 'w', encoding='utf-8'), indent=2, ensure_ascii=False)
    print(f'감사 {json.dumps(a, ensure_ascii=False)}', flush=True)


if __name__ == '__main__':
    if len(sys.argv) != 2:
        sys.exit('대상 하나를 인자로')
    if BLOCKING:
        for c in ('CO2', 'water'):
            if not os.path.exists(BLOCK[c]):
                sys.exit(f'!! 막음 파일 없음 {BLOCK[c]}')
    print(f'E-28d 밀도 격자 — 대상 {sys.argv[1]} · 막음 {BLOCKING} · 결과 {D.OUT} · 작업 {rw.RUNS}', flush=True)
    rc = D.main()
    post(sys.argv[1], rc)
    sys.exit(rc)
