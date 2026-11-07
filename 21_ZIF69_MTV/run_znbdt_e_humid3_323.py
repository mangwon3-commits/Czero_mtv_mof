# -*- coding: utf-8 -*-
"""RT-E — Zn(bib)(bdtdc) 습윤 3성분 선택도의 실온도 판(323 K · RH 90 %) · laptop2. 등록 `ASSIGN_ZNBDT_REALTEMP_20261108.md` §1 · §3.

laptop2 자기 E 래퍼 `run_znbdt_e_humid3.py`(md5 9702366) 를 **무수정 import** 하고, 등록 §1 이 말한 셋(온도 · 물 분압 · N₂ 분압)과
대상 · 막음 · 폴더 · 결과 이름만 바꿉니다.
  ① 조건: ads 323 K · 전압 100 kPa · CO₂ 15,000 Pa(0.150000) · 물 11,114.1 Pa(0.111141 = 0.90 × Buck 12,349 Pa · T-RT-1 값)
     · N₂ 나머지 73,885.9 Pa(0.738859 — 등록 "73,886" 의 반올림 전 값 · 몰분율 합 1).
     `hw.CONDITIONS` = [('ads', 15000, 323.0, 12349.0)] → 입력의 ExternalTemperature 323 · `hw.P_H2O` = 11,114.1 · 래퍼 몰분율 표 `E.Y` 를 위 값으로.
     S_humid,323 = (N_CO₂/N_N₂)/(0.150000/0.738859) — 래퍼가 `E.Y` 로 셈.
  ② 대상 여섯(등록 §2): e22_parent · e24i_cn_open · e24i_br_open · e24i_cl_open · e24i_ch3_open · e24i_no2_open. 전하 CIF md5 를 298 K E 의 기록과 대조.
  ③ 막음: 298 K 때의 표 그대로 — −NO₂ 만 물 1.30 구 4(CO₂ 1.65 · N₂ 1.82 파일은 구 0, 298 K −NO₂ E 실행기와 같은 파일 · md5). 나머지 다섯은 막음 없음.
  ④ 폴더: 298 K 계열과 섞지 않도록 humid_wc_runs_v3w_323/znbdt_e3_323_laptop2/(CLAUDE.md §3). 반복 1~3 · 워커 6 · 착수 간격 15 s(래퍼 기본).
  ⑤ 결과 results_znbdt_e_humid3_323_laptop2.json + _audit.json(등록 §1). 래퍼가 결과 머리에 298 K 판의 문자열(protocol.T_K 298 ·
     definition 의 0.821479 · test · assign)을 고정으로 쓰므로, main 이 끝난 뒤 그 네 칸만 323 K 판으로 바로잡고 `launcher_fix` 에 바꾼 칸을 적습니다.
     값 · 행 · 감사는 건드리지 않습니다.
완주 표지 · 앵커 · 씨앗 · 막음 감사는 래퍼 그대로입니다. 래퍼 md5 가 다르면 착수하지 않습니다.
"""
import json
import os
import sys

BASES = ['e22_parent', 'e24i_cn_open', 'e24i_br_open', 'e24i_cl_open', 'e24i_ch3_open', 'e24i_no2_open']
os.environ['ZNBDT_E_TARGETS'] = ','.join(BASES)
os.environ.setdefault('ZNBDT_E_MACHINE', 'laptop2')
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import run_znbdt_e_humid3 as E                             # noqa: E402

WANT = '9702366386edf93755c50d2527dbbe92'
if E.md5(os.path.abspath(E.__file__)) != WANT:
    sys.exit(f'  !! 래퍼 md5 불일치 — 착수 안 함 ({E.md5(os.path.abspath(E.__file__))} ≠ {WANT})')
CIFS = {'e22_parent': 'f15ce100dbbaa49714fdb2e5dabfe9ff', 'e24i_cn_open': '8fd4fc85cf94e797ce0927300eeab584',
        'e24i_br_open': '4015ec2d0cc2f00b5d9cf1040df7b26c', 'e24i_cl_open': 'c1e97588cb5da6bd11d2ff71be9de919',
        'e24i_ch3_open': 'a8e6a165aaa036205631d834ec82f6bb', 'e24i_no2_open': '3a2a53ac'}
for b, want in CIFS.items():
    p = os.path.join(HERE, 'charged_v3', f'{b}_DDEC6.cif')
    if not os.path.exists(p) or not E.md5(p).startswith(want):
        sys.exit(f'  !! 전하 CIF {b} 없음 또는 md5 가 298 K 기록 {want[:8]} 와 다름 — 착수 안 함')

# ① 조건
P_SAT_323 = 12349.0
P_H2O_323 = 0.90 * P_SAT_323                                # 11,114.1 Pa
E.hw.P_H2O = P_H2O_323
E.hw.CONDITIONS = [('ads', 0.15e5, 323.0, P_SAT_323)]
E.Y = {'CO2': 0.150000, 'N2': round(1 - 0.150000 - round(P_H2O_323 / E.P_TOT, 6), 6), 'water': round(P_H2O_323 / E.P_TOT, 6)}
assert E.Y == {'CO2': 0.15, 'N2': 0.738859, 'water': 0.111141}, E.Y

# ③ 막음 — 298 K −NO₂ E 와 같은 표
_ZB = os.path.join(HERE, 'znbdt_no2_zeo_runs', 'e24i_no2_open')
E.BLOCKS = {'e24i_no2_open': {
    'CO2': (os.path.join(_ZB, 'block1.65', 'e24i_no2_open_relaxed.block'), '897316929176464ebc9ad085f31e7284'),
    'N2': (os.path.join(_ZB, 'block1.82', 'e24i_no2_open_relaxed.block'), '897316929176464ebc9ad085f31e7284'),
    'water': (os.path.join(_ZB, 'block1.30', 'e24i_no2_open_relaxed.block'), '46b306e39cc368360e8e74d6459ad123')}}

# ④ 폴더 · 작업
if E.SMOKE or E.DRY:
    E.ROOT = os.path.join(E.CHAIN, f"znbdt_e3_323_{'smoke' if E.SMOKE else 'dry'}_{E.MACHINE}")
else:
    E.ROOT = os.path.join(HERE, 'humid_wc_runs_v3w_323', f'znbdt_e3_323_{E.MACHINE}')
E.hw.RUNS = os.path.join(E.ROOT, 'runs')
E.hw.CHARGED = os.path.join(E.ROOT, 'cifs')
E.TAGS = [f'{b}_e3r{k}' for b in E.BASES for k in E.REPS_RUN]
E.hw.TARGETS = E.TAGS
E.JOBS = [(t, lab, p, T, ps) for t in E.TAGS for lab, p, T, ps in E.hw.CONDITIONS]

# ⑤ 결과
if E.SMOKE or E.DRY:
    E.OUT = os.path.join(E.ROOT, f"results_znbdt_e_humid3_323_{E.MACHINE}_{'smoke' if E.SMOKE else 'dry'}.json")
else:
    E.OUT = os.path.join(HERE, f'results_znbdt_e_humid3_323_{E.MACHINE}.json')
E.AUDIT = E.OUT.replace('.json', '_audit.json')


def fix_header():
    if not os.path.exists(E.OUT):
        return
    d = json.load(open(E.OUT, encoding='utf-8'))
    old = {k: d.get(k) for k in ('test', 'assign', 'definition')}
    old['protocol.T_K'] = d['protocol'].get('T_K')
    d['test'] = 'Zn(bib)(bdtdc) RT-E — 습윤 3성분 흡착점 S_humid,323(323 K · RH 90 %)'
    d['assign'] = 'ASSIGN_ZNBDT_REALTEMP_20261108.md §1 · §3(laptop2 RT-E)'
    d['definition'] = 'S_humid,323 = (N_CO2/N_N2)/(0.150000/0.738859); 상대 ± = hypot(e_C/N_C, e_N/N_N); 평균 ± = ±̄/√n; SD = 회차 SD'
    d['protocol']['T_K'] = 323.0
    d['protocol']['p_sat_Pa_Buck_323'] = P_SAT_323
    d['launcher'] = {'file': os.path.basename(__file__), 'md5': E.md5(os.path.abspath(__file__))}
    d['launcher_fix'] = {'why': '래퍼 summarize() 가 298 K 판 문자열을 고정으로 씀 — 값 · 행 · 감사는 그대로', 'before': old}
    json.dump(d, open(E.OUT, 'w', encoding='utf-8'), ensure_ascii=False, indent=1, default=str)


if __name__ == '__main__':
    rc = E.main()
    fix_header()
    sys.exit(rc)
