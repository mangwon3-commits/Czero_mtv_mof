# -*- coding: utf-8 -*-
"""ZNBDT-C2 §10 「다른 길」 허용 기준에 대한 laptop2 공격의 산술 — 새 계산 없음 · master 원자료 Widom JSON 만 읽음.
물음(HKHOME 11-06 부탁): "U 만 K_H(CO₂) 를 −CN 과 같게 남겼다" 를 허용 기준으로 삼은 것이 결과를 보고 고른 것인가.
여기서 내는 수: 구조마다 K_H(CO₂) · K_H(N₂) 의 전하 ON/OFF 비(정전기가 헨리 층에 보태는 배수)와 그 모체비.
전하 끈 판(U · L · I)은 기하가 −CN 과 원자 단위로 같아 OFF 값이 −CN 의 OFF 와 같은 계입니다(ASSIGN_C2 §1 "OFF 는 −CN 의 OFF 와 같은 계라 안 돎").
실행: python3 -I c2_s10_attack.py <21_ZIF69_MTV 경로> → 표 출력 · c2_s10_attack.json"""
import json, math, os, sys
D = sys.argv[1]
F = {'parent': 'results_magi5_e3_e22_parent_widom_desktop-js1ib6u.json',
     'CN': 'results_magi5_e3_e24i_cn_open_widom_desktop-nvsrr9m.json',
     'CH3': 'results_magi5_e3_e24i_ch3_open_widom_hkhome.json',
     'U': 'results_magi5_e3_znbdt_c2_apolarU_widom_hkhome.json',
     'L': 'results_magi5_e3_znbdt_c2_apolarL_widom_hkhome.json',
     'I': 'results_magi5_e3_znbdt_c2_apolarI_widom_hkhome.json'}


def rows(k):
    d = json.load(open(os.path.join(D, F[k])))
    return {r['charges']: r for r in d['rows'] if r.get('status_CO2') == 'ok' and r.get('status_N2') == 'ok'}


R = {k: rows(k) for k in F}
for k in ('U', 'L', 'I'):
    R[k]['off'] = R['CN']['off']          # 같은 기하 → −CN 의 OFF


def val(k, ch, g):
    r = R[k][ch]; return r[f'KH_{g}'], r[f'KH_{g}_err']


out = {}
print(f"{'':7} {'KH_CO2 ON/OFF':>16} {'KH_N2 ON/OFF':>14} {'ON 모체비 CO2':>14} {'OFF 모체비 CO2':>15} {'정전기 배수 모체비 CO2':>22}")
for k in F:
    row = {}
    for g in ('CO2', 'N2'):
        on, eon = val(k, 'on', g); off, eoff = val(k, 'off', g)
        q = on / off; eq = q * math.hypot(eon / on, eoff / off)
        row[f'{g}_on_off'] = (q, eq)
        pon, _ = val('parent', 'on', g); poff, _ = val('parent', 'off', g)
        row[f'{g}_on_ratio_parent'] = on / pon
        row[f'{g}_off_ratio_parent'] = off / poff
    pq = row['CO2_on_off'][0] / (val('parent', 'on', 'CO2')[0] / val('parent', 'off', 'CO2')[0])
    row['CO2_elec_factor_ratio_parent'] = pq
    out[k] = row
    print(f"{k:7} {row['CO2_on_off'][0]:9.3f} ± {row['CO2_on_off'][1]:.3f} {row['N2_on_off'][0]:9.3f} ± {row['N2_on_off'][1]:.3f} "
          f"{row['CO2_on_ratio_parent']:14.3f} {row['CO2_off_ratio_parent']:15.3f} {pq:22.3f}")
# 두 구조 사이 ON/OFF 배수의 단위 거리(상대 ± 합성)
def dist(a, b, g):
    (qa, ea), (qb, eb) = out[a][f'{g}_on_off'], out[b][f'{g}_on_off']
    return abs(qa - qb) / math.hypot(ea, eb)
pairs = [('CN', 'parent'), ('U', 'CN'), ('U', 'parent'), ('L', 'CN'), ('I', 'CN')]
dd = {f'{a}-{b}': {g: round(dist(a, b, g), 2) for g in ('CO2', 'N2')} for a, b in pairs}
for k, v in dd.items():
    print(f"  ON/OFF 배수 단위 거리 {k:10} CO2 {v['CO2']:5.2f} · N2 {v['N2']:5.2f}")
json.dump({'source_files': F, 'note': 'U·L·I 의 OFF 는 −CN 의 OFF(같은 기하) · 단위 거리 = |차| / 두 ± 합성',
           'rows': out, 'unit_distance_on_off': dd}, open(sys.argv[2], 'w'), indent=1, ensure_ascii=False)
