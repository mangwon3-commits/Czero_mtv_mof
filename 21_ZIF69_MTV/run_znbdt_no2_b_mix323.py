# -*- coding: utf-8 -*-
"""ZNBDT −NO₂ 열린 자리(e24i_no2_open) 작동점 S_mix 323 K 3씨앗 — 사용자 11-07 "일단 돌려". `run_znbdt_c2_b_mix323.py` 사본(바꾼 것: 대상 · CIF 이름 _DDEC6 · md5 · S_Henry 출처 · 폴더 · 출력 · 문구).
`run_znbdt_b_mix323.py`(B) 사본 — 바꾼 것: 대상(znbdt_c2_apolarU 3씨앗) · CIF 이름(_DDEC6mod) · md5 · S_Henry 출처(apolarU 298 K Widom ON) · 실행 폴더 · 출력 · 기록 문구.
나머지(323 K · 0.15/0.85 · 1 bar · 5,000+15,000 · 완주 표지 + 두 성분 적재 각 한 번 · 반환코드 · 착수 간격 15 s · 착수 전 관문)는 B 와 같음. run_tj1_mix 무수정 import.
환경: ZNBDT_B_MACHINE(기본 hkhome) · ZNBDT_B_WORKERS(기본 3) · ZNBDT_B_DRY=1(계획만).
"""
import hashlib
import json
import os
import subprocess
import sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import run_tj1_mix as M   # noqa: E402
from ase.io import read   # noqa: E402

M.TEMP = 323.0
M.MACHINE = os.environ.get('ZNBDT_B_MACHINE', 'hkhome')
M.WORKERS = int(os.environ.get('ZNBDT_B_WORKERS', '3'))
M.RUNS = os.path.join(HERE, 'znbdt_no2_b_mix323_runs')
M.OUT = os.path.join(HERE, f'results_znbdt_no2_b_mix323_{M.MACHINE}.json')
M.TEST = 'ZNBDT −NO2 열린 자리 작동점 S_mix 323 K'
M.ASSIGN_REF = '사용자 11-07 일단 돌려 · 사슬 틀 ASSIGN_ZNBDT_C1_20261105.md §1'
M.REG_REF = '등록 보완 대기(종합자 · 첫 결과 읽기 전)'

FAM = (('e24i_no2_open', 'results_magi5_e3_e24i_no2_open_widom_hkhome.json'),)
CIF_MD5 = {'e24i_no2_open': '3a2a53acd57a784be9c7bd5710f3c12d'}   # charge_tnf.py 11-07 18:29 산출


def _son(path):
    d = json.load(open(os.path.join(HERE, path))); on = [r for r in d['rows'] if r['charges'] == 'on'][0]
    return on['selectivity'], on['selectivity_err']


def _md5(p):
    return hashlib.md5(open(p, 'rb').read()).hexdigest()


def targets():
    t = []
    for n, src in FAM:
        s, e = _son(src)
        for k in (1, 2, 3):
            t.append({'name': f'{n}_s{k}', 'cif': os.path.join(HERE, 'charged_v3', f'{n}_DDEC6.cif'), 'group': '형판 설계 후보(−NO₂ 열린 자리)', 'dim': 3,
                      'S_Henry': s, 'S_Henry_err': e, 'S_Henry_src': src + ' ON (298 K) — 온도 다름 · 비 인용 금지', 'L': None, 'L_src': '—'})
    for x in t:
        a = read(x['cif']); uc = M.rg.unit_cells(a); x['unit_cells'] = uc; x['N_super'] = len(a) * uc[0] * uc[1] * uc[2]
    return sorted(t, key=lambda x: -x['N_super'])


def prelaunch():
    bad = []
    nz = subprocess.run(['pgrep', '-xc', 'network'], capture_output=True, text=True).stdout.strip() or '0'
    if nz != '0':
        bad.append(f'Zeo++ network {nz}개 도는 중(CLAUDE.md §5)')
    for p in (M.RUNS, M.OUT):
        if os.path.exists(p):
            bad.append(f'이전 산출 있음: {p}')
    for n, _ in FAM:
        p = os.path.join(HERE, 'charged_v3', f'{n}_DDEC6.cif')
        m = _md5(p) if os.path.exists(p) else None
        if m != CIF_MD5[n]:
            bad.append(f'{n} CIF md5 {m} ≠ {CIF_MD5[n]}(11-07 PACMAN 산출)')
    return bad


M.targets = targets
if __name__ == '__main__':
    bad = prelaunch()
    if os.environ.get('ZNBDT_B_DRY'):
        for x in M.targets():
            print(x['name'], x['N_super'], x['unit_cells'], round(x['S_Henry'], 2), os.path.relpath(x['cif'], HERE), _md5(x['cif']), flush=True)
        print('TEMP', M.TEMP, 'OUT', M.OUT, 'RUNS', M.RUNS, 'WORKERS', M.WORKERS, 'SIMULATE', M.rg.SIMULATE, '관문', bad or 'ok', flush=True)
        sys.exit(0)
    if bad:
        print('!! 착수 전 관문 실패 — RASPA 안 띄움:\n   ' + '\n   '.join(bad), flush=True)
        sys.exit(2)
    sys.exit(M.main())
