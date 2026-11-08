# -*- coding: utf-8 -*-
"""등록 E — 323 K 물 밀도 격자(모체 · −CN · −NO₂ 열린 자리) · laptop2. 등록 `ASSIGN_ZNBDT_6SEED_CORE_20261108.md` §E.

E-28c 실행기 `run_e28c_density.py`(md5 39dfddf3)를 **무수정 import** 합니다. 그 밑의 `run_density_water_v3w.py`(e4df6077) →
`run_density_water_v3.py`(27fc1c1b · 90³ 격자 지시 주입 · VTK 보존) → `run_water.py`(94650685 · 입력 쓰기 · run_one)도 그대로입니다.
바꾸는 것은 등록 §E 가 말한 둘(온도 · 물 분압)과 −NO₂ 물 막음 · 폴더 · 대상 등록뿐입니다.
  ① 조건: run_water 의 모듈 전역 TEMP = 323.0 · P_SAT_298 = 12,349 Pa(Buck 323 K · T-RT-1 값) → run_one 이 p_h2o = 0.90 × 12,349 = 11,114.1 Pa ·
     전압 = CO₂ 15,000 + 물 11,114.1 = 26,114.1 Pa 로 씁니다(전역 이름의 '298' 은 원판 이름일 뿐 · 입력에 쓰이는 값은 위 둘).
     사이클 · 격자 90³ · 셀 규칙 · 힘장 · 전하 · 물 모형은 E-28 그대로입니다.
  ② −NO₂ 만 물 막음: RASPA 호출 직전 simulation.input 의 water 성분 절(MoleculeDefinition 줄 다음)에 BlockPockets 두 줄 삽입 ·
     막음 파일 = `znbdt_no2_zeo_runs/e24i_no2_open/block1.30/e24i_no2_open_relaxed.block`(md5 46b306e3 · 구 4 · 298 K −NO₂ E · ⑩ · RT-E 와 같은 파일).
     CO₂ 는 1.65 Å 주머니 0 이라 막음 없음(298 K 표 그대로). 삽입 자리가 정확히 한 번이 아니면 RASPA 를 띄우지 않습니다.
     끝에서 물 성분의 blocked 줄 · 차단 수 = 구 4 × 단위셀 수 · not-found 없음을 감사합니다.
  ③ 폴더: 작업 `water_runs_density_v3w_323/rh90_<대상>/` · 적재 JSON `density_water_v3w_323/<DW_SUB>/water_results.json` · 감사 `e28c_audit.json`
     (+ −NO₂ 는 `e28_323_block_audit.json`). 298 K 계열 폴더와 섞지 않습니다(CLAUDE.md §3).
사용: python run_e28_density_323.py <대상>     (대상마다 프로세스 1 · 3 동시 · DW_SUB · DW_EXTRA 는 이 파일이 정함)
      E28_323_DRY=1 이면 RASPA 를 띄우지 않고 저장소 밖(~/.mof_chain/e28_323_dry)에 입력만 써서 보여 줍니다.
"""
import hashlib
import json
import os
import shutil
import sys
import subprocess

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
if len(sys.argv) != 2:
    sys.exit('대상 하나를 인자로')
TARGET = sys.argv[1]
DRY = bool(os.environ.get('E28_323_DRY'))
DRYBASE = os.path.expanduser('~/.mof_chain/e28_323_dry')
SUB = f'rt_{TARGET}'
# W 는 import 때 density_water_v3w/<DW_SUB> 를 만듭니다 — 절대 경로를 주어 298 K 폴더에 빈 폴더가 생기지 않게 합니다.
os.environ['DW_SUB'] = os.path.join(DRYBASE, 'out', SUB) if DRY else os.path.join(HERE, 'density_water_v3w_323', SUB)
os.environ['DW_EXTRA'] = TARGET
import run_e28c_density as E28   # noqa: E402  E28C_BLOCK 은 주지 않음(그 막음은 C₂H₅ 파일 고정)
D, rw = E28.D, E28.rw


def md5(p):
    return hashlib.md5(open(p, 'rb').read()).hexdigest()


WANT = {E28.__file__: '39dfddf3c82a620d668343049e7cf367', E28.W.__file__: 'e4df6077',
        D.__file__: '27fc1c1b', rw.__file__: '94650685af2439da16cf8344307a315b'}
for p, w in WANT.items():
    m = md5(os.path.abspath(p))
    if not m.startswith(w):
        sys.exit(f'  !! {os.path.basename(p)} md5 {m} ≠ {w} — 착수 안 함')
if os.environ.get('E28C_BLOCK'):
    sys.exit('  !! E28C_BLOCK 은 C₂H₅ 막음 파일 고정 — 이 실행기에서는 쓰지 않음')

CIFS = {'e22_parent': 'f15ce100dbbaa49714fdb2e5dabfe9ff', 'e24i_cn_open': '8fd4fc85cf94e797ce0927300eeab584',
        'e24i_no2_open': '3a2a53acd57a784be9c7bd5710f3c12d'}
if TARGET not in CIFS:
    sys.exit(f'  !! 등록 §E 대상이 아님: {TARGET}')
cif = os.path.join(HERE, 'charged_v3', f'{TARGET}_DDEC6.cif')
if md5(cif) != CIFS[TARGET]:
    sys.exit(f'  !! 전하 CIF md5 {md5(cif)} ≠ {CIFS[TARGET]}')

# ① 조건
rw.TEMP = 323.0
rw.P_SAT_298 = 12349.0
assert abs(rw.P_SAT_298 * D.RH - 11114.1) < 1e-6

# ③ 폴더
D.OUT = os.environ['DW_SUB']
rw.RUNS = os.path.join(DRYBASE, 'runs') if DRY else os.path.join(HERE, 'water_runs_density_v3w_323')
rw.HERE = D.OUT
os.makedirs(D.OUT, exist_ok=True)
RUN_DIR = os.path.join(rw.RUNS, f'rh{int(D.RH * 100):02d}_{TARGET}')

# ② −NO₂ 물 막음
BLOCK = os.path.join(HERE, 'znbdt_no2_zeo_runs', 'e24i_no2_open', 'block1.30', 'e24i_no2_open_relaxed.block')
BLOCK_MD5 = '46b306e39cc368360e8e74d6459ad123'
BLOCKING = TARGET == 'e24i_no2_open'
NAME = 'e24i_no2_open_water'
if BLOCKING:
    if md5(BLOCK) != BLOCK_MD5:
        sys.exit(f'  !! 물 막음 파일 md5 {md5(BLOCK)} ≠ {BLOCK_MD5}')
    NSPH = int(open(BLOCK).read().split()[0])
_inner = rw.subprocess.run      # = run_density_water_v3._run_with_grid(격자 주입) — 그 안쪽은 그대로
if DRY:
    D._real_run = lambda cmd, **kw: subprocess.CompletedProcess(cmd, 0)   # RASPA 를 띄우지 않음


def _run(cmd, *a, **k):
    cwd = k.get('cwd')
    if cwd and cmd and str(cmd[-1]) == 'simulation.input':
        if BLOCKING:
            p = os.path.join(cwd, 'simulation.input')
            txt = open(p).read()
            if 'BlockPockets' not in txt:
                pat = 'MoleculeName              water\n            MoleculeDefinition        TraPPE\n'
                if txt.count(pat) != 1:
                    raise RuntimeError(f'물 막음 삽입 자리가 {txt.count(pat)}번 — RASPA 안 띄움 ({cwd})')
                txt = txt.replace(pat, pat + f'            BlockPockets              yes\n            BlockPocketsFileName      {NAME}\n')
                shutil.copy(BLOCK, os.path.join(cwd, f'{NAME}.block'))
                open(p, 'w').write(txt)
                print(f'    [막음] 물 {NSPH} 구 삽입 — {os.path.basename(cwd)}', flush=True)
        ef = open(os.path.join(cwd, 'stderr.txt'), 'w')
        k['stderr'] = ef
        try:
            cp = _inner(cmd, *a, **k)
        finally:
            ef.close()
        with open(os.path.join(cwd, 'e28_323_returncode.txt'), 'w') as f:
            f.write(f'{cp.returncode}\n')
        return cp
    return _inner(cmd, *a, **k)


rw.subprocess.run = _run


def block_audit():
    import glob
    import re
    outs = glob.glob(os.path.join(RUN_DIR, 'Output', 'System_0', '*.data'))
    a = {'target': TARGET, 'block_file': os.path.relpath(BLOCK, HERE), 'block_md5': BLOCK_MD5, 'n_spheres': NSPH}
    if len(outs) != 1:
        a.update(ok=False, why=f'.data {len(outs)}개')
        return a
    txt = open(outs[0], encoding='utf-8', errors='ignore').read()
    inp = open(os.path.join(RUN_DIR, 'simulation.input')).read()
    uc = [int(x) for x in re.search(r'UnitCells\s+(\d+)\s+(\d+)\s+(\d+)', inp).groups()]
    ba = E28.block_audit(txt)
    err = open(os.path.join(RUN_DIR, 'stderr.txt'), errors='ignore').read() if os.path.exists(os.path.join(RUN_DIR, 'stderr.txt')) else ''
    rcf = os.path.join(RUN_DIR, 'e28_323_returncode.txt')
    n_exp = NSPH * uc[0] * uc[1] * uc[2]
    w = ba.get('water', {})
    a.update(block=ba, n_expected_water=n_exp, stderr_not_found=E28.NOT_FOUND in err,
             returncode=int(open(rcf).read().strip()) if os.path.exists(rcf) else None,
             blockpockets_in_input=inp.count('BlockPockets              yes'))
    a['ok'] = bool(w.get('blocked_line') and w.get('n_blocked') == n_exp and not ba.get('CO2', {}).get('blocked_line')
                   and a['blockpockets_in_input'] == 1 and not a['stderr_not_found'] and a['returncode'] == 0)
    return a


if __name__ == '__main__':
    print(f'등록 E 323 K 물 밀도 격자 — 대상 {TARGET} · T {rw.TEMP} K · 물 {rw.P_SAT_298 * D.RH:.1f} Pa · CO₂ {rw.P_CO2:.0f} Pa · '
          f'막음 {"물 1.30 구 %d" % NSPH if BLOCKING else "없음"} · 드라이 {DRY} · 결과 {D.OUT} · 작업 {rw.RUNS}', flush=True)
    if not DRY and os.path.exists(RUN_DIR):
        sys.exit(f'  !! 작업 폴더가 이미 있음 {RUN_DIR} — 이어받기로 섞지 않으려 착수 안 함')
    if DRY:
        shutil.rmtree(RUN_DIR, ignore_errors=True)
    rc = D.main()
    if DRY:
        print(open(os.path.join(RUN_DIR, 'simulation.input')).read(), flush=True)
        sys.exit(0)
    E28.post(TARGET, rc)
    if BLOCKING:
        a = block_audit()
        json.dump(a, open(os.path.join(D.OUT, 'e28_323_block_audit.json'), 'w', encoding='utf-8'), indent=2, ensure_ascii=False)
        print(f'막음 감사 {json.dumps(a, ensure_ascii=False)}', flush=True)
        if not a['ok']:
            rc = rc or 2
    sys.exit(rc)
