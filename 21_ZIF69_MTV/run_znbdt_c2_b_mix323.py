# -*- coding: utf-8 -*-
"""ZNBDT-C2 후속 #2 — 무극성 −CN(U판) 작동점 S_mix 323 K 3씨앗. 명령 `ASSIGN_ZNBDT_C2_FOLLOWUP_20261105.md` §2(종합자 · 자료 0건 · 사용자 밤샘 위임).
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
M.RUNS = os.path.join(HERE, 'znbdt_c2_b_mix323_runs')
M.OUT = os.path.join(HERE, f'results_znbdt_c2_b_mix323_{M.MACHINE}.json')
M.TEST = 'ZNBDT-C2 후속 #2 — 무극성 −CN(U판) 작동점 S_mix 323 K'
M.ASSIGN_REF = 'ASSIGN_ZNBDT_C2_FOLLOWUP_20261105.md §2'
M.REG_REF = 'ASSIGN_ZNBDT_C2_FOLLOWUP_20261105.md §2 읽는 법(자료 0건에서 등록)'

FAM = (('znbdt_c2_apolarU', 'results_magi5_e3_znbdt_c2_apolarU_widom_hkhome.json'),)
CIF_MD5 = {'znbdt_c2_apolarU': '3e079487bf8fdd5302ff507084362229'}   # results_znbdt_c2_build_hkhome.json(6a78619d) · 명령 §2


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
            t.append({'name': f'{n}_s{k}', 'cif': os.path.join(HERE, 'charged_v3', f'{n}_DDEC6mod.cif'), 'group': '기제 판별 대조(계산 전용)', 'dim': 3,
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
        p = os.path.join(HERE, 'charged_v3', f'{n}_DDEC6mod.cif')
        m = _md5(p) if os.path.exists(p) else None
        if m != CIF_MD5[n]:
            bad.append(f'{n} CIF md5 {m} ≠ {CIF_MD5[n]}(ZNBDT-C2 298 K 를 낸 판)')
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
