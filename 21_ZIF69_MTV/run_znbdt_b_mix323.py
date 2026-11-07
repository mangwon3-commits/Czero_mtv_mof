# -*- coding: utf-8 -*-
"""ZnBDT 보강 B — 열린 자리 −CN · −Br(격자 고정 구조)의 작동점 S_mix 를 323 K 에서. 등록 `ASSIGN_ZNBDT_SUPP_20261103.md` §B.
`run_e27_mix323.py`(E-27) 사본 — run_tj1_mix.py(수정 없이) import, 온도만 323 K(모듈 전역 TEMP; 입력의 ExternalTemperature 와
결과 protocol.T_K 가 이 값을 씀). 나머지(0.15/0.85 · 1 bar · 5,000+15,000 · 완주 표지 + 두 성분 적재 각 한 번 · 반환코드 · LPT · 착수 간격 15 s)는 T-J1′ 과 같음.
바꾼 것: 대상(e24i_cn_open · e24i_br_open 각 3씨앗 = 6작업) · 실행 폴더 · 출력 이름 · 기록 문구 · 착수 전 관문(아래). 막음 없음
(격자 고정 −CN · −Br 은 E-24i Zeo++ 에서 구 0 — `e24i_zeo_runs/<tag>/block1.65|1.82` 첫 줄 0).
CIF: `charged_v3/e24i_cn_open_DDEC6.cif` · `e24i_br_open_DDEC6.cif` — 지금 S_mix 139.8 · 127.9(298 K, 6씨앗, FINAL_RANKING_SMIX_20260930 §G)를 낸
`results_e24i_e24i_{cn,br}_open_mix{,_s456}_*.json` 의 행 `cif` 와 같은 파일. md5 를 착수 전에 대조(아래 CIF_MD5 — 다르면 안 띄움).
S_Henry 칸: **298 K** Widom ON(run_e24i_mix 와 같은 출처) — 온도가 다름 · 비 인용 금지. 모체 대조는 E-27(`results_e27_mix323_laptop.json`) — 다시 돌리지 않음.
착수 거부: 실행 폴더 · 결과 파일이 있으면(이어받기가 cached 로 섞지 않게) · Zeo++(network) 가 돌면(CLAUDE.md §5) · CIF md5 가 다르면.
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
M.RUNS = os.path.join(HERE, 'znbdt_b_mix323_runs')
M.OUT = os.path.join(HERE, f'results_znbdt_b_mix323_{M.MACHINE}.json')
M.TEST = 'ZnBDT 보강 B — 열린 자리 −CN · −Br(격자 고정) 작동점 S_mix 323 K'
M.ASSIGN_REF = 'ASSIGN_ZNBDT_SUPP_20261103.md §B'
M.REG_REF = 'ASSIGN_ZNBDT_SUPP_20261103.md §B 읽는 법(자료 0건에서 등록)'

FAM = (('e24i_cn_open', 'results_magi5_e3_e24i_cn_open_widom_desktop-nvsrr9m.json'),
       ('e24i_br_open', 'results_magi5_e3_e24i_br_open_widom_hkhome.json'))
CIF_MD5 = {'e24i_cn_open': '8fd4fc85cf94e797ce0927300eeab584', 'e24i_br_open': '4015ec2d0cc2f00b5d9cf1040df7b26c'}   # 2026-11-04 HKHOME 실측(git 3a80f01c 이후 무변경)


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
            t.append({'name': f'{n}_s{k}', 'cif': os.path.join(HERE, 'charged_v3', f'{n}_DDEC6.cif'), 'group': '형판 설계(비-ZIF) · 격자 고정', 'dim': 3,
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
            bad.append(f'{n} CIF md5 {m} ≠ {CIF_MD5[n]}(S_mix 139.8 · 127.9 를 낸 판)')
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
