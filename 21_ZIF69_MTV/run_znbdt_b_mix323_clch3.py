# -*- coding: utf-8 -*-
"""RT-B — 열린 자리 −Cl · −CH₃ 의 323 K 건조 작동점 S_mix 3씨앗 · laptop2. 등록 `ASSIGN_ZNBDT_REALTEMP_20261108.md` §4-S RT-B.

HKHOME B 러너 `run_znbdt_b_mix323.py`(md5 51702b07 · −CN · −Br 323 K 를 낸 판)를 **무수정 import** 하고 등록이 말한 대로 대상만 바꿉니다.
  ① 대상: e24i_cl_open · e24i_ch3_open 각 3씨앗(6작업). 전하 CIF 는 298 K E · RT-E 에 쓴 `charged_v3/<tag>_DDEC6.cif`(md5 아래 CIF_MD5).
     S_Henry 칸은 298 K Widom ON(`results_magi5_e3_<tag>_widom_hkhome.json`) — B 러너와 같이 온도가 다르므로 비는 인용하지 않습니다.
  ② 조건: B 와 같음(323 K · CO₂/N₂ 0.15/0.85 · 100 kPa · 5,000 + 15,000 · 막음 없음 · 착수 간격 15 s · LPT) — 값 만드는 부분은 B 러너와
     그 밑의 `run_tj1_mix.py`(md5 9535030b) 그대로입니다.
  ③ 폴더 · 결과: 실행 폴더 `znbdt_b_mix323_clch3_runs/` · 결과 `results_znbdt_b_mix323_clch3_<기기>.json`(등록 §4-S 이름). 기록 문구(test · assign ·
     registration)만 RT-B 판으로 적습니다.
  ④ 착수 전 관문: B 러너의 prelaunch 그대로(실행 폴더 · 결과 파일이 이미 있으면 · Zeo++ 가 돌면 · CIF md5 가 다르면 안 띄움). 두 모듈 md5 가 다르면 안 띄움.
환경: ZNBDT_B_MACHINE(기본 laptop2) · ZNBDT_B_WORKERS(기본 6) · ZNBDT_B_DRY=1(계획만).
"""
import os
import sys

os.environ.setdefault('ZNBDT_B_MACHINE', 'laptop2')
os.environ.setdefault('ZNBDT_B_WORKERS', '6')
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import run_znbdt_b_mix323 as B   # noqa: E402

WANT = {B.__file__: '51702b07d143dde56a2b94d1ed41176d', B.M.__file__: '9535030b173c5e2ad49c9f23198bfa3e'}
for p, w in WANT.items():
    m = B._md5(os.path.abspath(p))
    if m != w:
        sys.exit(f'  !! {os.path.basename(p)} md5 {m} ≠ {w} — 착수 안 함')

# ① 대상
B.FAM = (('e24i_cl_open', 'results_magi5_e3_e24i_cl_open_widom_hkhome.json'),
         ('e24i_ch3_open', 'results_magi5_e3_e24i_ch3_open_widom_hkhome.json'))
B.CIF_MD5 = {'e24i_cl_open': 'c1e97588cb5da6bd11d2ff71be9de919', 'e24i_ch3_open': 'a8e6a165aaa036205631d834ec82f6bb'}

# ③ 폴더 · 결과 · 기록 문구
M = B.M
M.RUNS = os.path.join(HERE, 'znbdt_b_mix323_clch3_runs')
M.OUT = os.path.join(HERE, f'results_znbdt_b_mix323_clch3_{M.MACHINE}.json')
M.TEST = 'ZnBDT RT-B — 열린 자리 −Cl · −CH₃(격자 고정) 작동점 S_mix 323 K(건조)'
M.ASSIGN_REF = 'ASSIGN_ZNBDT_REALTEMP_20261108.md §4-S RT-B(laptop2 · 실행기 run_znbdt_b_mix323_clch3.py → run_znbdt_b_mix323.py 51702b07)'
M.REG_REF = 'ASSIGN_ZNBDT_REALTEMP_20261108.md §4-S 읽는 법(자료 0건에서 등록 · FOLLOWUP §2 · R4 §6-2 와 같은 식 · 서술 · 문턱 없음)'

if __name__ == '__main__':
    bad = B.prelaunch()
    if os.environ.get('ZNBDT_B_DRY'):
        for x in M.targets():
            print(x['name'], x['N_super'], x['unit_cells'], round(x['S_Henry'], 2), os.path.relpath(x['cif'], HERE), B._md5(x['cif']), flush=True)
        print('TEMP', M.TEMP, 'OUT', M.OUT, 'RUNS', M.RUNS, 'WORKERS', M.WORKERS, 'SIMULATE', M.rg.SIMULATE, '관문', bad or 'ok', flush=True)
        sys.exit(0)
    if bad:
        print('!! 착수 전 관문 실패 — RASPA 안 띄움:\n   ' + '\n   '.join(bad), flush=True)
        sys.exit(2)
    sys.exit(M.main())
