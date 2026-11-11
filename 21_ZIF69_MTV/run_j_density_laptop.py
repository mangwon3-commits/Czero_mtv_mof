# -*- coding: utf-8 -*-
"""등록 J — 물 밀도 격자 4작업(J1 −Cl · J2 −Br · J3 −CH₃ 323 K · J4 −NO₂ 298 K) · **랩탑 예비판**.
등록 `ASSIGN_DURABILITY_JK_20261111.md` §J-1 · 지시 `ASSIGN_MIDNIGHT_20261111.md` §4-1(laptop2 의 J 착수 글이 랩탑 F 완주 때까지 없을 때만 씀).

등록 E 실행기 `run_e28_density_323.py`(b2d94f91)의 사본이고, 등록 §J-1 이 허용한 것만 바꿨습니다 — 대상 표 · 온도 값 · 폴더.
그 밑의 `run_e28c_density.py`(39dfddf3) → `run_density_water_v3w.py`(e4df6077) → `run_density_water_v3.py`(27fc1c1b · 90³ 격자 · VTK 보존) →
`run_water.py`(94650685)는 무수정 import 입니다.
  ① 조건: J1~J3 은 E 실행기와 같은 323 K(TEMP 323.0 · 포화압 12,349 → 물 11,114.1 Pa · 전압 26,114.1 Pa).
     J4 는 298 K 판(TEMP 298.0 · 포화압 3,169.0 → 물 2,852.1 Pa · E-28 조건 · 전압 17,852.1 Pa). 사이클 · 격자 · 셀 규칙 · 힘장 · 전하 · 물 모형은 E-28 그대로.
  ② 막음: J4(−NO₂)만 물 1.30 구 4(`znbdt_no2_zeo_runs/e24i_no2_open/block1.30/e24i_no2_open_relaxed.block` 46b306e3 · CO₂ 없음) — E 실행기와 같은 삽입 · 같은 감사.
     J1~J3 은 막음 없음.
  ③ 폴더: J1~J3 은 323 K 계열(`water_runs_density_v3w_323/rh90_<대상>` · `density_water_v3w_323/rt_<대상>`),
     J4 는 298 K 계열(`water_runs_density_v3w/rh90_e24i_no2_open` · `density_water_v3w/tpl_e24i_no2_open`) — 등록 §J-1 표 그대로.
     감사 `e28c_audit.json`(+ J4 는 `j_block_audit.json`) · 반환코드 `j_returncode.txt`.
사용: python run_j_density_laptop.py <대상>     (대상마다 프로세스 1 · 4 동시 · 착수 사이 15 s)
      J_DRY=1 이면 RASPA 를 띄우지 않고 저장소 밖(~/.mof_chain/j_dry_laptop)에 입력만 써서 보여 줍니다.
판정 없음 — 종합자.
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
DRY = bool(os.environ.get('J_DRY'))
DRYBASE = os.path.expanduser('~/.mof_chain/j_dry_laptop')
# 대상 → (전하 CIF md5, 온도 K, 포화압 Pa, 결과 계열 폴더, 결과 하위 폴더, 작업 계열 폴더)   — 등록 §J-1 표
J = {'e24i_cl_open': ('c1e97588cb5da6bd11d2ff71be9de919', 323.0, 12349.0, 'density_water_v3w_323', 'rt_e24i_cl_open', 'water_runs_density_v3w_323'),
     'e24i_br_open': ('4015ec2d0cc2f00b5d9cf1040df7b26c', 323.0, 12349.0, 'density_water_v3w_323', 'rt_e24i_br_open', 'water_runs_density_v3w_323'),
     'e24i_ch3_open': ('a8e6a165aaa036205631d834ec82f6bb', 323.0, 12349.0, 'density_water_v3w_323', 'rt_e24i_ch3_open', 'water_runs_density_v3w_323'),
     'e24i_no2_open': ('3a2a53acd57a784be9c7bd5710f3c12d', 298.0, 3169.0, 'density_water_v3w', 'tpl_e24i_no2_open', 'water_runs_density_v3w')}
if TARGET not in J:
    sys.exit(f'  !! 등록 §J 대상이 아님: {TARGET}')
CIF_MD5, TEMP, PSAT, OUTSER, SUB, RUNSER = J[TARGET]
# W 는 import 때 density_water_v3w/<DW_SUB> 를 만듭니다 — 절대 경로를 주어 엉뚱한 계열 폴더에 빈 폴더가 생기지 않게 합니다.
os.environ['DW_SUB'] = os.path.join(DRYBASE, 'out', SUB) if DRY else os.path.join(HERE, OUTSER, SUB)
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

cif = os.path.join(HERE, 'charged_v3', f'{TARGET}_DDEC6.cif')
if md5(cif) != CIF_MD5:
    sys.exit(f'  !! 전하 CIF md5 {md5(cif)} ≠ {CIF_MD5}')

# ① 조건
rw.TEMP = TEMP
rw.P_SAT_298 = PSAT
assert abs(rw.P_SAT_298 * D.RH - (11114.1 if TEMP == 323.0 else 2852.1)) < 1e-6

# ③ 폴더
D.OUT = os.environ['DW_SUB']
rw.RUNS = os.path.join(DRYBASE, 'runs') if DRY else os.path.join(HERE, RUNSER)
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
        with open(os.path.join(cwd, 'j_returncode.txt'), 'w') as f:
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
    rcf = os.path.join(RUN_DIR, 'j_returncode.txt')
    n_exp = NSPH * uc[0] * uc[1] * uc[2]
    w = ba.get('water', {})
    a.update(block=ba, n_expected_water=n_exp, stderr_not_found=E28.NOT_FOUND in err,
             returncode=int(open(rcf).read().strip()) if os.path.exists(rcf) else None,
             blockpockets_in_input=inp.count('BlockPockets              yes'))
    a['ok'] = bool(w.get('blocked_line') and w.get('n_blocked') == n_exp and not ba.get('CO2', {}).get('blocked_line')
                   and a['blockpockets_in_input'] == 1 and not a['stderr_not_found'] and a['returncode'] == 0)
    return a


if __name__ == '__main__':
    print(f'등록 J 물 밀도 격자(랩탑 예비) — 대상 {TARGET} · T {rw.TEMP} K · 물 {rw.P_SAT_298 * D.RH:.1f} Pa · CO₂ {rw.P_CO2:.0f} Pa · '
          f'막음 {"물 1.30 구 %d" % NSPH if BLOCKING else "없음"} · 드라이 {DRY} · 결과 {D.OUT} · 작업 {rw.RUNS}', flush=True)
    if not DRY and os.path.exists(RUN_DIR):
        sys.exit(f'  !! 작업 폴더가 이미 있음 {RUN_DIR} — 이어받기로 섞지 않으려 착수 안 함')
    if not DRY and os.path.exists(os.path.join(D.OUT, 'water_results.json')):
        sys.exit(f'  !! 결과가 이미 있음 {D.OUT} — 착수 안 함')
    if DRY:
        shutil.rmtree(RUN_DIR, ignore_errors=True)
    rc = D.main()
    if DRY:
        print(open(os.path.join(RUN_DIR, 'simulation.input')).read(), flush=True)
        sys.exit(0)
    E28.post(TARGET, rc)
    if BLOCKING:
        a = block_audit()
        json.dump(a, open(os.path.join(D.OUT, 'j_block_audit.json'), 'w', encoding='utf-8'), indent=2, ensure_ascii=False)
        print(f'막음 감사 {json.dumps(a, ensure_ascii=False)}', flush=True)
        if not a['ok']:
            rc = rc or 2
    sys.exit(rc)
