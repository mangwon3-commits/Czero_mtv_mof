# -*- coding: utf-8 -*-
"""ZNBDT-C2 §10 「다른 길」 허용 관문에 대한 랩탑 공격의 산술 — 새 계산 없음 · master 원자료만 읽음.
물음(HKHOME 11-06 부탁): "U 만 K_H(CO₂) 를 −CN 과 같게 남겼다" 를 허용 기준으로 삼은 것이 결과를 보고 고른 것인가.
여기서 재는 것: 관문의 양(K_H(CO₂) 모체비)이 C2 의 두 끝점(−CN = 모양 끝 · −CH₃ = 극성 끝)을 가르는가.
자 = 관문과 같은 자(두 구조 Widom 상대 ± 합성 · 모체 항 소거) — znbdt_c2_judge 의 widom/row 를 그대로 씀(무수정 import).
실행: 21_ZIF69_MTV 에서 python3 MAGI/MAGI-007_znbdt_c2_s10_attack_laptop.py → MAGI/MAGI-007_znbdt_c2_s10_attack_laptop.json"""
import json, math, os, sys
HERE = os.getcwd(); sys.path.insert(0, HERE)
import znbdt_c2_judge as J   # noqa: E402

base = J.row('parent', None); R = {'parent': base}
KEYS = ('cn', 'ch3', 'br', 'cl', 'U', 'L', 'I')
for k in KEYS:
    R[k] = J.row(k, base)
repro = {k: (round(R[k]['X'], 2), J.TABLE[k]) for k in J.TABLE}
assert all(a == b for a, b in repro.values()), repro


def ratio(k, gas):
    w = J.widom(k); p = R['parent']
    key, ek = ('KH_CO2', 'eKC') if gas == 'CO2' else ('KH_N2', 'eKN')
    r = w['KC' if gas == 'CO2' else 'KN'] / p[key]
    return r, r * w[ek]


def d(a, b, gas):
    (x, ex), (y, ey) = ratio(a, gas), ratio(b, gas)
    return abs(x - y) / math.hypot(ex, ey)


out = {'what': '§10 허용 관문의 양이 C2 의 두 끝점(−CN 모양 끝 · −CH₃ 극성 끝)을 가르는가 — 관문과 같은 자',
       'unit': J.UNIT, 'reproduce_gate_X': repro, 'rows': {}, 'gate_distance': {}}
print(f"{'':6} {'K_H(CO2)/모체':>16} {'K_H(N2)/모체':>16} {'X':>13}")
for k in KEYS:
    c, n = ratio(k, 'CO2'), ratio(k, 'N2')
    out['rows'][k] = {'KH_CO2_vs_parent': c, 'KH_N2_vs_parent': n, 'X': R[k]['X'], 'e_X': R[k].get('e_X')}
    ex = R[k].get('e_X'); exs = f"{ex:.3f}" if isinstance(ex, float) else '-'
    print(f"{k:6} {c[0]:8.3f} ± {c[1]:.3f} {n[0]:8.3f} ± {n[1]:.3f} {R[k]['X']:7.3f} ± {exs}")
pairs = [('ch3', 'cn'), ('U', 'cn'), ('U', 'ch3'), ('br', 'cn'), ('cl', 'cn'), ('L', 'cn'), ('L', 'ch3'), ('I', 'cn')]
for a, b in pairs:
    out['gate_distance'][f'{a}-{b}'] = {g: round(d(a, b, g), 2) for g in ('CO2', 'N2')}
    print(f"  단위 거리 {a:>4}–{b:<4} K_H(CO2) {d(a, b, 'CO2'):6.2f} · K_H(N2) {d(a, b, 'N2'):6.2f}"
          f"  {'← 관문 안' if d(a, b, 'CO2') < J.UNIT else ''}")
json.dump(out, open('MAGI/MAGI-007_znbdt_c2_s10_attack_laptop.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
