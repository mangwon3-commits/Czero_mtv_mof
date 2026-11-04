# -*- coding: utf-8 -*-
"""ZNBDT-C2 판정 — 무극성 −CN(U판 주 · I판 민감도)의 N₂ 추가 배제비. 등록 `ASSIGN_ZNBDT_C2_20261105.md` §2 의 식을 그대로 코드로 둔 것(자료 0건에 커밋).
정의(MAGI-007 R3 laptop2 D-2 와 같음): r_i = N_i(혼합) / (K_H,i · p_i), p = CO₂ 15 kPa · N₂ 85 kPa
    X = (r_N₂ / r_N₂,모체) ÷ (r_CO₂ / r_CO₂,모체)
오차(등록 §2-2): Widom 상대 ± = KH_err/KH(RASPA 95 % CI) · 혼합 평균의 상대 ± = (회차 ± 의 평균)/√n ÷ 평균 (E24I_SEEDS 규칙 e = ±̄/√n).
    두 구조를 견줄 때 모체 항은 양쪽에 같아 지워지므로 뺌 → e_rel(X) = √(Σ 자기 넷의 상대 ±²) · 단위 거리 d = |X−R| / √(e_X² + e_R²).
판독(등록 §2-3): 기준 R_CN · R_CH3 를 원자료로 다시 내고, 표 값(0.72 · 1.01 · Br 0.86 · Cl 0.85)과 소수 둘째 자리까지 같아야 진행(재현 관문).
    주 판독 세 갈래: d_CN < 1.5 → 모양 · d_CH3 < 1.5 → 극성 · 둘 다 아님 → 중간(극성 몫 f = (X−X_CN)/(X_CH3−X_CN) ± 와 함께).
    C1 식 이분(X ≤ 0.86 모양 / > 0.86 극성)은 연속성 기록용으로만 함께 적음.  U 와 I 의 주 판독이 다르면 전체 = "보정 방식에 민감 — 판별 불가".
완주 표지: 혼합 3행 모두 status ok · returncode 0 · 씨앗 고유 / Widom ON 두 기체 status ok / CIF md5 = results_znbdt_c2_build_hkhome.json.
실행: python3 znbdt_c2_judge.py   (표준 라이브러리만) → results_znbdt_c2_judge_hkhome.json
"""
import glob, hashlib, json, math, os, sys

HERE = os.path.dirname(os.path.abspath(__file__)); os.chdir(HERE)
P = {'CO2': 15000.0, 'N2': 85000.0}
BOUND, UNIT = 0.86, 1.5
TABLE = {'cn': 0.72, 'ch3': 1.01, 'br': 0.86, 'cl': 0.85}
WIDOM = {'parent': 'results_magi5_e3_e22_parent_widom_desktop-js1ib6u.json',
         'cn': 'results_magi5_e3_e24i_cn_open_widom_desktop-nvsrr9m.json',
         'br': 'results_magi5_e3_e24i_br_open_widom_hkhome.json',
         'cl': 'results_magi5_e3_e24i_cl_open_widom_hkhome.json',
         'ch3': 'results_magi5_e3_e24i_ch3_open_widom_hkhome.json',
         'U': 'results_magi5_e3_znbdt_c2_apolarU_widom_hkhome.json',
         'I': 'results_magi5_e3_znbdt_c2_apolarI_widom_hkhome.json'}
MIX = {'parent': (['results_e23_mix_desktop.json'], 'e22_parent_s'),
       'cn': (['results_e24i_e24i_cn_open_mix_hkhome.json', 'results_e24i_e24i_cn_open_mix_s456_hkhome.json'], 'e24i_cn_open_s'),
       'br': (['results_e24i_e24i_br_open_mix_laptop2.json', 'results_e24i_e24i_br_open_mix_s456_hkhome.json'], 'e24i_br_open_s'),
       'cl': (['results_e24i_e24i_cl_open_mix_junseok.json'], 'e24i_cl_open_s'),
       'ch3': (['results_e24i_e24i_ch3_open_mix_laptop2.json'], 'e24i_ch3_open_s'),
       'U': (['results_znbdt_c2_znbdt_c2_apolarU_mix_hkhome.json'], 'znbdt_c2_apolarU_s'),
       'I': (['results_znbdt_c2_znbdt_c2_apolarI_mix_hkhome.json'], 'znbdt_c2_apolarI_s')}
md5 = lambda p: hashlib.md5(open(p, 'rb').read()).hexdigest()


def widom(k):
    d = json.load(open(WIDOM[k])); on = [r for r in d['rows'] if r['charges'] == 'on']
    assert len(on) == 1 and on[0].get('status_CO2') == 'ok' and on[0].get('status_N2') == 'ok', (k, on)
    r = on[0]
    return dict(KC=r['KH_CO2'], eKC=r['KH_CO2_err'] / r['KH_CO2'], KN=r['KH_N2'], eKN=r['KH_N2_err'] / r['KH_N2'],
                S_H=r['KH_CO2'] / r['KH_N2'], cif=d['cif'], src_md5=md5(WIDOM[k]))


def mix(k):
    files, pre = MIX[k]; rows = []
    for f in files:
        rows += [r for r in json.load(open(f))['rows'] if r['name'].startswith(pre)]
    bad = [(r['name'], r['status'], r.get('returncode')) for r in rows if r['status'] not in ('ok', 'cached') or r.get('returncode') not in (0, None)]
    seeds = [r['seed'] for r in rows]
    n = len(rows); m = lambda f: sum(r[f] for r in rows) / n
    out = dict(n=n, NC=m('N_CO2'), NN=m('N_N2'), S=m('S_mix'), bad=bad, seeds_unique=len(set(seeds)) == n,
               names=sorted(r['name'] for r in rows), src_md5={f: md5(f) for f in files})
    out['eNC'] = m('N_CO2_err') / math.sqrt(n) / out['NC']
    out['eNN'] = m('N_N2_err') / math.sqrt(n) / out['NN']
    return out


def row(k, base):
    w, x = widom(k), mix(k)
    rC = x['NC'] / (w['KC'] * P['CO2']); rN = x['NN'] / (w['KN'] * P['N2'])
    r = dict(KH_CO2=w['KC'], KH_N2=w['KN'], N_CO2=x['NC'], N_N2=x['NN'], S_mix=x['S'], n_mix=x['n'], r_CO2=rC, r_N2=rN,
             S_mix_over_S_Henry=x['S'] / w['S_H'], e_rel_own=math.sqrt(w['eKC'] ** 2 + w['eKN'] ** 2 + x['eNC'] ** 2 + x['eNN'] ** 2),
             marks=dict(mix_bad=x['bad'], seeds_unique=x['seeds_unique'], mix_rows=x['names'], widom_cif=w['cif']),
             src_md5={WIDOM[k]: w['src_md5'], **x['src_md5']})
    if base:
        r['X'] = (rN / base['r_N2']) / (rC / base['r_CO2'])
        r['e_X'] = r['X'] * r['e_rel_own']
        r['vs_parent'] = dict(KH_CO2=w['KC'] / base['KH_CO2'], KH_N2=w['KN'] / base['KH_N2'], N_CO2=x['NC'] / base['N_CO2'],
                              N_N2=x['NN'] / base['N_N2'], S_mix=x['S'] / base['S_mix'],
                              op_over_henry=r['S_mix_over_S_Henry'] / base['S_mix_over_S_Henry'])
    return r


def read_one(v, R):
    """등록 §2-3 — 세 갈래 주 판독 + C1 식 이분 판독(연속성용, 주 판독 아님)."""
    X, eX = R[v]['X'], R[v]['e_X']
    d = {ref: abs(X - R[ref]['X']) / math.hypot(eX, R[ref]['e_X']) for ref in ('cn', 'ch3', 'br', 'cl')}
    xc, xm, ec, em = R['cn']['X'], R['ch3']['X'], R['cn']['e_X'], R['ch3']['e_X']
    f = (X - xc) / (xm - xc)   # 니트릴 극성 몫: 0 = 전부 모양 · 1 = 전부 극성
    ef = math.sqrt(eX ** 2 + ((1 - f) * ec) ** 2 + (f * em) ** 2) / (xm - xc)
    if d['cn'] < UNIT and d['ch3'] < UNIT:
        verdict = '판별 불가 — 두 기준과 모두 가까움'
    elif d['cn'] < UNIT:
        verdict = '모양'
    elif d['ch3'] < UNIT:
        verdict = '극성'
    elif X < xc:
        verdict = '모양 이상 — 전하를 빼니 배제가 더 커짐(극성이 배제를 줄이던 쪽)'
    elif X > xm:
        verdict = '극성 이상 — 경쟁 몫보다도 덜 밀려남'
    else:
        verdict = '중간 — 두 몫이 섞임'
    return dict(X=X, e_X=eX, d_units=d, polarity_share=f, polarity_share_pm=ef, verdict=verdict,
                c1_binary='모양' if X <= BOUND else '극성')


def main():
    base = row('parent', None); R = {'parent': base}
    for k in ('cn', 'br', 'cl', 'ch3'):
        R[k] = row(k, base)
    repro = {k: (round(R[k]['X'], 2), TABLE[k]) for k in TABLE}
    repro_ok = all(a == b for a, b in repro.values())
    print('재현 관문 ' + ' · '.join(f'{k} {a:.2f}(표 {b:.2f})' for k, (a, b) in repro.items()) + f" → {'통과' if repro_ok else '탈락'}")
    out = dict(assign='ASSIGN_ZNBDT_C2_20261105.md §2', p_Pa=P, bound=BOUND, unit=UNIT, reproduce_gate=dict(values=repro, pass_=repro_ok), rows=R)
    if not repro_ok:
        json.dump(out, open('results_znbdt_c2_judge_hkhome.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
        print('!! 기준값 재현 실패 — 판독하지 않습니다'); return 2
    build = json.load(open('results_znbdt_c2_build_hkhome.json'))
    reads, marks_ok = {}, True
    for v in ('U', 'I'):
        if not (os.path.exists(WIDOM[v]) and all(os.path.exists(f) for f in MIX[v][0])):
            print(f'{v}판: 결과 파일 아직 없음'); continue
        R[v] = row(v, base)
        cif = R[v]['marks']['widom_cif']; want = build['variants'][v]['md5']
        ok = (R[v]['n_mix'] == 3 and not R[v]['marks']['mix_bad'] and R[v]['marks']['seeds_unique']
              and md5(cif) == want and os.path.basename(cif) == os.path.basename(build['variants'][v]['cif']))
        R[v]['marks']['complete'] = ok; marks_ok &= ok
        reads[v] = read_one(v, R)
        o = reads[v]
        print(f"{v}판 X = {o['X']:.3f} ± {o['e_X']:.3f} · 단위 거리 CN {o['d_units']['cn']:.2f} · CH₃ {o['d_units']['ch3']:.2f} · "
              f"Br {o['d_units']['br']:.2f} · Cl {o['d_units']['cl']:.2f} · 극성 몫 {o['polarity_share']:.2f} ± {o['polarity_share_pm']:.2f} → "
              f"{o['verdict']} (C1 식 이분: {o['c1_binary']}) · 표지 {'완비' if ok else '미비'}")
    if set(reads) == {'U', 'I'}:
        vu, vi = reads['U']['verdict'], reads['I']['verdict']
        overall = vu if vu == vi else '보정 방식에 민감 — 판별 불가'
        out['overall'] = overall if marks_ok else f'표지 미비 — 판독 보류({overall})'
        print('전체 판독:', out['overall'])
    out['reads'] = reads
    json.dump(out, open('results_znbdt_c2_judge_hkhome.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    return 0


if __name__ == '__main__':
    sys.exit(main())
