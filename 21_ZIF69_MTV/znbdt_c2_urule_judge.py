# -*- coding: utf-8 -*-
"""ZNBDT-C2 「다른 길」 판독 — **자료를 본 뒤의 규칙(사용자 결정 2026-11-06 "다른 길로 계산해")**.
원 등록 판독(C2 "보정 방식에 민감 — 판별 불가" · C2-L "전하 끄기 대조는 보정 방식에 민감 — 닫지 않음")은 그대로 남고, 이 판독은 따로 적습니다.
규칙(이 파일에 고정 · `ASSIGN_ZNBDT_C2_20261105.md` §10):
  허용 관문 — 전하 끄기 판(U · I · L) 가운데 **K_H(CO₂) 모체비가 실제 −CN 과 1.5 단위 안인 판만** 무극성 대조로 받습니다.
     자 = 두 구조 Widom 상대 ±(RASPA 95 % CI)의 합성 · 모체 항은 양쪽에 같아 지워짐(znbdt_c2_judge 보조 검사와 같은 자).
     근거: 빠진 니트릴 전하를 어디에 싣느냐가 CO₂ 친화를 바꾸고 X 가 그것을 따라 움직였으므로(§9), CO₂ 친화를 −CN 과 같게 둔 판만 "니트릴 전하만 끈" 판으로 봄.
  판독 — 허용된 판의 주 판독(§2-4 세 갈래, znbdt_c2_judge.read_one 그대로)이 모두 같으면 그것을 이 규칙 아래 C2 판독으로 적음 · 갈리면 "허용 판끼리도 갈림" · 허용 0 이면 "허용 판 없음".
  #2(323 K r_T)는 U판으로 돌았으므로, U 가 허용되면 그 판독(znbdt_c2_b_judge)을 이 규칙 아래 함께 적음.
  서술 열: K_H(N₂) 모체비도 같은 자로 −CN 과의 단위 거리를 적음(관문 아님).
실행: python3 znbdt_c2_urule_judge.py   (표준 라이브러리만) → results_znbdt_c2_urule_judge_hkhome.json
"""
import json, math, os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); os.chdir(HERE); sys.path.insert(0, HERE)
import znbdt_c2_judge as J   # noqa: E402

UNIT = J.UNIT


def ratio(R, k, gas):
    w = J.widom(k); p = R['parent']
    key, ek = ('KH_CO2', 'eKC') if gas == 'CO2' else ('KH_N2', 'eKN')
    r = w['KC' if gas == 'CO2' else 'KN'] / p[key]
    return r, r * w[ek]


def main():
    base = J.row('parent', None); R = {'parent': base}
    for k in ('cn', 'br', 'cl', 'ch3', 'U', 'I', 'L'):
        R[k] = J.row(k, base)
    repro = {k: (round(R[k]['X'], 2), J.TABLE[k]) for k in J.TABLE}
    assert all(a == b for a, b in repro.values()), repro
    build = json.load(open('results_znbdt_c2_build_hkhome.json'))['variants']
    out = dict(rule='자료 후 규칙 — 사용자 결정 2026-11-06 "다른 길로 계산해" (ASSIGN_ZNBDT_C2_20261105.md §10)',
               registered_readings_kept=dict(C2='보정 방식에 민감 — 판별 불가', C2L='전하 끄기 대조는 보정 방식에 민감 — 닫지 않음'),
               unit=UNIT, reproduce_gate=repro, variants={})
    cn_c, cn_n = ratio(R, 'cn', 'CO2'), ratio(R, 'cn', 'N2')
    print(f"−CN K_H(CO₂)/모체 {cn_c[0]:.3f} ± {cn_c[1]:.3f} · K_H(N₂)/모체 {cn_n[0]:.3f} ± {cn_n[1]:.3f}")
    adm = []
    for v in ('U', 'L', 'I'):
        c, n = ratio(R, v, 'CO2'), ratio(R, v, 'N2')
        dc = abs(c[0] - cn_c[0]) / math.hypot(c[1], cn_c[1]); dn = abs(n[0] - cn_n[0]) / math.hypot(n[1], cn_n[1])
        cif_ok = J.md5(R[v]['marks']['widom_cif']) == build[v]['md5']
        rd = J.read_one(v, R)
        ok = dc < UNIT and cif_ok
        if ok: adm.append(v)
        out['variants'][v] = dict(KH_CO2_vs_parent=c, KH_N2_vs_parent=n, d_units_KH_CO2_vs_CN=dc, d_units_KH_N2_vs_CN_desc=dn,
                                  admitted=ok, X=rd['X'], e_X=rd['e_X'], verdict=rd['verdict'], polarity_share=rd['polarity_share'],
                                  polarity_share_pm=rd['polarity_share_pm'], d_units=rd['d_units'])
        print(f"{v}판 K_H(CO₂)/모체 {c[0]:.3f} ± {c[1]:.3f} → −CN 과 {dc:.2f} 단위 {'허용' if ok else '불허'} · (서술) K_H(N₂) {n[0]:.3f} −CN 과 {dn:.2f} 단위"
              f" · X {rd['X']:.3f} ± {rd['e_X']:.3f} → {rd['verdict']} · f {rd['polarity_share']:.2f} ± {rd['polarity_share_pm']:.2f}")
    vs = {out['variants'][v]['verdict'] for v in adm}
    if not adm:
        overall = '허용 판 없음'
    elif len(vs) == 1:
        overall = vs.pop()
    else:
        overall = '허용 판끼리도 갈림'
    out['admitted'] = adm; out['overall_under_rule'] = overall
    print(f"허용 판 {adm} → 이 규칙 아래 C2 판독: {overall}")
    if 'U' in adm:
        b = json.load(open('results_znbdt_c2_b_judge_hkhome.json'))
        out['b323_under_rule'] = dict(r_T=b['read']['r_T'], e_r=b['read']['e_r'], d_units=b['read']['d_units'], verdict=b['read']['verdict'])
        print(f"#2(U판 323 K) 이 규칙 아래: r_T {b['read']['r_T']:.3f} ± {b['read']['e_r']:.3f} → {b['read']['verdict']}")
    json.dump(out, open('results_znbdt_c2_urule_judge_hkhome.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    return 0


if __name__ == '__main__':
    sys.exit(main())
