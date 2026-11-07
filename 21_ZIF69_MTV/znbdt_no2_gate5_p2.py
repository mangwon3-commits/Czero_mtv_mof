# -*- coding: utf-8 -*-
"""ZNBDT −NO₂ 열린 자리 관문 ⑤ ′2 서술 열 — HKHOME. 등록 `ASSIGN_ZNBDT_NO2_PLACEMENT_20261107.md` §5-1 서술 · §7 ④(종합자 21:1x).
묻는 것: 관문 ⑤ 처리(UFF4MOF 셀 이완) 뒤 PLD 가 3.64 아래로 내려갔으므로, **처리 뒤 구조에서 CO₂ 1.65 · N₂ 1.82 탐침 통로가 남는지**.
입력: `lmp_znbdt_no2_g5/e24i_no2_open/min_e24i_no2_open.data`(관문 ⑤ 산출 · 슈퍼셀) → `run_e24j_cellrelax.fold` 로 단위셀로 접음
      (복제 사이 편차 · 원소 순서 확인을 같이 기록). 처리 전 같은 탐침 값은 `results_znbdt_no2_access_hkhome.json`(이완 전 단위셀)에 있습니다.
Zeo++ `-ha -res` · `-ha -chan 1.65` · `-ha -chan 1.82`(처리 전 접근성과 같은 명령). **RASPA 가 0 일 때만**(CLAUDE §5).
산출: results_znbdt_no2_gate5_p2_hkhome.json — 판정은 종합자. 실행: lammps_mof 파이썬(21_ZIF69_MTV 에서)."""
import json, os, re, socket, subprocess, sys, time
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE); os.chdir(HERE)
import run_e24j_cellrelax as CR   # noqa: E402  (fold · md5 · busy)
import risk_screen as rs          # noqa: E402
from ase.io import read, write    # noqa: E402

TAG = 'e24i_no2_open'
D = os.path.join(HERE, 'lmp_znbdt_no2_g5', TAG)
WD = os.path.join(HERE, 'znbdt_no2_g5p2_runs')
OUT = os.path.join(HERE, f'results_znbdt_no2_gate5_p2_{socket.gethostname().lower()}.json')


def main():
    if CR.busy():
        sys.exit(f'  !! RASPA simulate {CR.busy()}건이 돌고 있음 — Zeo++ 동시 금지(CLAUDE §5) · 착수 안 함')
    if os.path.exists(OUT):
        sys.exit(f'  !! {os.path.basename(OUT)} 이미 있음 — 덮어쓰지 않음')
    os.makedirs(WD, exist_ok=True)
    before_p = os.path.join(D, f'{TAG}.cif'); dat = os.path.join(D, f'min_{TAG}.data')
    before = read(before_p); after = read(dat, format='lammps-data', atom_style='full')
    a1, fl = CR.fold(after, before)
    p = os.path.join(WD, f'{TAG}_g5treated.cif'); write(p, a1); rs.fix_tags(p)
    res = {'test': '−NO₂ 열린 자리 관문 ⑤ 처리 뒤 1.65 · 1.82 통로 수(′2 서술 열)', 'assign': 'ASSIGN_ZNBDT_NO2_PLACEMENT_20261107.md §5-1 · §7 ④',
           'inputs': {'treated_data': os.path.relpath(dat, HERE), 'treated_data_md5': CR.md5(dat), 'before_cif': os.path.relpath(before_p, HERE),
                      'before_cif_md5': CR.md5(before_p)},
           'fold': fl, 'cell_change_vs_before': CR.cell_change(before.cell, a1.cell), 'treated_unitcell_cif': os.path.relpath(p, HERE),
           'treated_unitcell_md5': CR.md5(p), 'pre_treatment_ref': 'results_znbdt_no2_access_hkhome.json (r1.65 · r1.82 chan)',
           'machine': socket.gethostname().lower(), 'runs': {}}
    t0 = time.time()
    r = subprocess.run([rs.NETWORK, '-ha', '-res', p + '.res', p], cwd=WD, capture_output=True, text=True, timeout=1800)
    v = open(p + '.res').read().split() if os.path.exists(p + '.res') else []
    res['runs']['res'] = {'rc': r.returncode, 'LCD': float(v[1]) if len(v) > 2 else None, 'PLD': float(v[2]) if len(v) > 2 else None}
    for rad in (1.65, 1.82):
        cf = os.path.join(WD, f'{TAG}_g5treated_r{rad:.2f}.chan')
        r = subprocess.run([rs.NETWORK, '-ha', '-chan', f'{rad:.2f}', cf, p], cwd=WD, capture_output=True, text=True, timeout=1800)
        ctxt = open(cf, errors='ignore').read() if os.path.exists(cf) else ''
        mc = re.search(r'(\d+)\s+channels identified of dimensionality\s*([\d\s]*)', ctxt)
        mo = re.search(r'Identified (\d+) channels and (\d+) pockets', r.stdout + r.stderr)
        res['runs'][f'chan{rad:.2f}'] = {'rc': r.returncode, 'n_channels_chanfile': int(mc.group(1)) if mc else None,
                                        'dimensionality': mc.group(2).split() if mc else None,
                                        'channels_stdout': int(mo.group(1)) if mo else None, 'pockets_stdout': int(mo.group(2)) if mo else None,
                                        'chan_file_head': ctxt.strip().splitlines()[:3]}
    res['elapsed_s'] = round(time.time() - t0, 1)
    ok = all(x['rc'] == 0 for x in res['runs'].values()) and res['runs']['res']['PLD'] is not None and \
        all(res['runs'][f'chan{r_:.2f}']['n_channels_chanfile'] is not None for r_ in (1.65, 1.82))
    res['status'] = 'ok' if ok else 'fail'; res['finished'] = True
    json.dump(res, open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, indent=1, default=str)
    print(f"′2 {res['status']} · 접기 복제편차 {fl['replica_max_frac_dev_vs_r0']} · 원소순서 {fl['symbol_order_ok']} · {res['elapsed_s']} s — 값은 파일에", flush=True)
    return 0 if ok else 2


if __name__ == '__main__':
    sys.exit(main())
