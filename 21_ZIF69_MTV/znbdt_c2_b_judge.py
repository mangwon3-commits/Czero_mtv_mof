# -*- coding: utf-8 -*-
"""ZNBDT-C2 후속 #2 판독 — 무극성 −CN(U판)의 323 K N₂ 풀림 r_T. 명령 `ASSIGN_ZNBDT_C2_FOLLOWUP_20261105.md` §2 의 읽는 법을
그대로 코드로 둔 것(자료 0건에 커밋 · HKHOME 계산 · 판정은 종합자). 보류 해제 = `ASSIGN_ZNBDT_C2_20261105.md` §7(사용자 결정 ③).
정의: r_T = N_N₂(323) / N_N₂(298)  (298 = ZNBDT-C2 apolarU S_mix 3씨앗 평균 · 323 = run_znbdt_c2_b_mix323.py 3씨앗 평균)
기준(MAGI-007 R3 HKHOME `r3_competition.py` 와 같은 원자료): 모체 1.00(E-23 298 · E-27 323) · −CN 1.24 · −Br 1.19(298 6씨앗 · B 323 3씨앗)
   → 원자료로 다시 내고 표 값과 소수 둘째 자리까지 같아야 진행(재현 관문).
자(「B 와 같은 식」 — 씩 ± 전파): 온도마다 평균 적재의 상대 ± = (회차 ± 의 평균)/√n ÷ 평균(E24I_SEEDS 규칙 e = ±̄/√n, znbdt_c2_judge 와 같음)
   e_rel(r_T) = √(e₃₂₃² + e₂₉₈²) · 단위 거리 d = |r − R| / √(e_r² + e_R²) · 문턱 1.5 단위.
읽기(§2): d_모체 < 1.5 이고 d_CN ≥ 1.5 → "−CN 의 323 K 풀림은 전하가 만든 경쟁 몫"(Caspar ③ 극성 쪽 표지)
          d_CN < 1.5 이고 d_모체 ≥ 1.5 → "풀림은 전하 없이도 남음 — 모양/다른 원인"
          둘 다 안 · 둘 다 밖 → "판별 불가(서술만)".  보조: S_mix(323)/S_mix(298)(−CN 0.591 · 모체 0.669).
ZNBDT-C2(-L) 주 판독과 따로 적습니다(한 수로 다른 층을 말하지 않음 — R4 교훈 ㄱ).
완주 표지: 323 K 3행 status ok · returncode 0 · 씨앗 고유 · 실행 CIF md5 = 빌드 기록 U(3e079487).
실행: python3 znbdt_c2_b_judge.py   (표준 라이브러리만) → results_znbdt_c2_b_judge_hkhome.json
"""
import hashlib, json, math, os, sys

HERE = os.path.dirname(os.path.abspath(__file__)); os.chdir(HERE)
UNIT = 1.5
TABLE = {'parent': 1.00, 'cn': 1.24, 'br': 1.19}
D298 = {'parent': (['results_e23_mix_desktop.json'], 'e22_parent_s'),
        'cn': (['results_e24i_e24i_cn_open_mix_hkhome.json', 'results_e24i_e24i_cn_open_mix_s456_hkhome.json'], 'e24i_cn_open_s'),
        'br': (['results_e24i_e24i_br_open_mix_laptop2.json', 'results_e24i_e24i_br_open_mix_s456_hkhome.json'], 'e24i_br_open_s'),
        'U': (['results_znbdt_c2_znbdt_c2_apolarU_mix_hkhome.json'], 'znbdt_c2_apolarU_s')}
D323 = {'parent': (['results_e27_mix323_laptop.json'], 'e22_parent_s'),
        'cn': (['results_znbdt_b_mix323_hkhome.json'], 'e24i_cn_open_s'),
        'br': (['results_znbdt_b_mix323_hkhome.json'], 'e24i_br_open_s'),
        'U': (['results_znbdt_c2_b_mix323_hkhome.json'], 'znbdt_c2_apolarU_s')}
md5 = lambda p: hashlib.md5(open(p, 'rb').read()).hexdigest()


def agg(spec):
    files, pre = spec; rows = []
    for f in files:
        rows += [r for r in json.load(open(f))['rows'] if r['name'].startswith(pre)]
    n = len(rows); m = lambda k: sum(r[k] for r in rows) / n
    bad = [(r['name'], r['status'], r.get('returncode')) for r in rows if r['status'] not in ('ok', 'cached') or r.get('returncode') not in (0, None)]
    return dict(n=n, NN=m('N_N2'), eNN=m('N_N2_err') / math.sqrt(n) / m('N_N2'), S=m('S_mix'), bad=bad,
                seeds_unique=len({r['seed'] for r in rows}) == n, cifs=sorted({r['cif'] for r in rows}),
                names=sorted(r['name'] for r in rows), src_md5={f: md5(f) for f in files})


def rT(k):
    a, b = agg(D298[k]), agg(D323[k])
    r = b['NN'] / a['NN']; e = r * math.hypot(a['eNN'], b['eNN'])
    return dict(r_T=r, e_r=e, N_N2_298=a['NN'], N_N2_323=b['NN'], S_ratio_323_298=b['S'] / a['S'], n298=a['n'], n323=b['n'],
                marks=dict(bad298=a['bad'], bad323=b['bad'], seeds_unique=a['seeds_unique'] and b['seeds_unique'], cif323=b['cifs'], rows323=b['names']),
                src_md5={**a['src_md5'], **b['src_md5']})


def main():
    R = {k: rT(k) for k in ('parent', 'cn', 'br')}
    repro = {k: (round(R[k]['r_T'], 2), TABLE[k]) for k in TABLE}
    ok = all(a == b for a, b in repro.values())
    print('재현 관문 ' + ' · '.join(f'{k} {a:.2f}(표 {b:.2f})' for k, (a, b) in repro.items()) + f" → {'통과' if ok else '탈락'}")
    out = dict(assign='ASSIGN_ZNBDT_C2_FOLLOWUP_20261105.md §2 (보류 해제 = ASSIGN_ZNBDT_C2_20261105.md §7)', unit=UNIT,
               reproduce_gate=dict(values=repro, pass_=ok), rows=R)
    if ok and all(os.path.exists(f) for f in D323['U'][0]):
        u = R['U'] = rT('U')
        build = json.load(open('results_znbdt_c2_build_hkhome.json'))['variants']['U']
        cif_ok = [os.path.basename(c) for c in u['marks']['cif323']] == [os.path.basename(build['cif'])] and md5(u['marks']['cif323'][0]) == build['md5']
        complete = u['n323'] == 3 and not u['marks']['bad323'] and u['marks']['seeds_unique'] and cif_ok
        u['marks']['complete'] = complete
        d = {k: abs(u['r_T'] - R[k]['r_T']) / math.hypot(u['e_r'], R[k]['e_r']) for k in ('parent', 'cn', 'br')}
        if d['parent'] < UNIT <= d['cn']:
            v = '−CN 의 323 K 풀림은 전하가 만든 경쟁 몫(Caspar ③ 극성 쪽 표지)'
        elif d['cn'] < UNIT <= d['parent']:
            v = '풀림은 전하 없이도 남음 — 모양/다른 원인'
        else:
            v = '판별 불가(서술만) — ' + ('두 기준 모두 1.5 단위 안' if max(d['parent'], d['cn']) < UNIT else '두 기준 모두 1.5 단위 밖')
        out['read'] = dict(r_T=u['r_T'], e_r=u['e_r'], d_units=d, verdict=v if complete else f'표지 미비 — 판독 보류({v})',
                           aux_S_ratio=dict(U=u['S_ratio_323_298'], cn=R['cn']['S_ratio_323_298'], parent=R['parent']['S_ratio_323_298']))
        print(f"apolarU r_T = {u['r_T']:.3f} ± {u['e_r']:.3f} · 단위 거리 모체 {d['parent']:.2f} · CN {d['cn']:.2f} · Br {d['br']:.2f}"
              f" · S(323)/S(298) {u['S_ratio_323_298']:.3f} → {out['read']['verdict']} · 표지 {'완비' if complete else '미비'}")
    elif ok:
        print('apolarU 323 K 결과 파일 아직 없음')
    json.dump(out, open('results_znbdt_c2_b_judge_hkhome.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    return 0 if ok else 2


if __name__ == '__main__':
    sys.exit(main())
