#!/usr/bin/env python3
"""E-24i 판정(종합자 HKHOME) — 등록 ASSIGN_MAGI5B_20260925.md §HKHOME 22차(43ec8edc) · 보완 27f32f80(C₂H₅ 물 = 막음).
원자료만 읽음. 결과 파일은 **만든 기기의 가지**에서 집음(작업트리 사본은 낡을 수 있음 — 먼저 띄운 pending 판이 병합돼 있음).
자료가 모자라면 그 칸은 '미완비' 로 두고 판정량을 찍지 않음.

  (1) 적어도 하나 S_ON(주머니 있으면 막음값) ≥ 모체 87.80 ± 1.22 + 1.5 단위
  (2) E-23 규칙 1위(열린 자리 계열 — 후속 거친 · 관문 ⑤ 통과 후보)의 S_mix ≥ 모체 S_mix + 1.5 단위(±̄/√3 합성)
      E-23 규칙: ① S_mix 에서 누구에게도 1.5 단위 넘게 지지 않는 후보군 → ② 물 지수(낮을수록 위) 1.5 단위 안이면 공동 → 반복해 전체 순위
  단위 = d / √(±₁² + ±₂²) · S_mix ± = 씨앗 ±̄/√3 · 물 지수 ± = 두 상대 ± 제곱합(물 ±̄/√4)
"""
import json, math, os, statistics as st, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
FF = '8e8ec933f9013c7e932da04dc256efd3'
TAGS = ['e24i_ch3_open', 'e24i_cl_open', 'e24i_br_open', 'e24i_c2h5_open', 'e24i_cn_open']
TH = 1.5
BR = {'junseok': 'origin/junseok-20260822', 'laptop2': 'origin/laptop2-20260825',
      'desktop-nvsrr9m': 'origin/laptop-20260822', 'laptop': 'origin/laptop-20260822'}
SRC = {}


def load(name):
    """기기 접미사로 가지 선택 · hkhome/데스크탑은 작업트리. 없으면 None."""
    stem = name[:-5]
    ref = next((b for k, b in BR.items() if stem.endswith('_' + k)), None)
    try:
        if ref:
            txt = subprocess.run(['git', 'show', f'{ref}:21_ZIF69_MTV/{name}'], cwd=HERE, capture_output=True, text=True)
            if txt.returncode:
                return None
            SRC[name] = ref
            return json.loads(txt.stdout)
        p = os.path.join(HERE, name)
        if not os.path.exists(p):
            return None
        SRC[name] = '작업트리'
        return json.load(open(p, encoding='utf-8'))
    except ValueError:
        return None


def u(d, *e):
    s = math.sqrt(sum(x * x for x in e))
    return d / s if s else float('inf')


def widom(name):
    d = load(name)
    if d is None:
        return None, '파일 없음'
    if not d.get('finished') or d.get('ff_md5') != FF:
        return None, f"finished {d.get('finished')} · md5 {d.get('ff_md5')}"
    R = {r['charges']: r for r in d['rows']}
    for c in ('on', 'off'):
        if R.get(c, {}).get('status_CO2') != 'ok' or R.get(c, {}).get('status_N2') != 'ok':
            return None, f'{c} status'
    on, off = R['on'], R['off']
    S = on['KH_CO2'] / on['KH_N2']
    assert abs(S - on['selectivity']) < 1e-6 * S
    return dict(S=S, Se=on['selectivity_err'], KH=on['KH_CO2'], KHe=on['KH_CO2_err'], S_off=off['selectivity'], G=S / off['selectivity']), None


WID = {'e24i_ch3_open': 'hkhome', 'e24i_cl_open': 'hkhome', 'e24i_br_open': 'hkhome',
       'e24i_c2h5_open': 'desktop-nvsrr9m', 'e24i_cn_open': 'desktop-nvsrr9m'}
MIX = {'e24i_ch3_open': 'laptop2', 'e24i_br_open': 'laptop2', 'e24i_cl_open': 'junseok',
       'e24i_c2h5_open': 'junseok', 'e24i_cn_open': 'hkhome'}


def smix(tag):
    d = load(f'results_e24i_{tag}_mix_{MIX[tag]}.json')
    if d is None:
        return None, '파일 없음'
    if 'name' in (d.get('rows') or [{}])[0]:          # run_e24i_mix 틀(차단 없음)
        rows = [r for r in d['rows'] if r['name'].startswith(tag + '_s')]
        ok = [r for r in rows if r.get('status') == 'ok' and r.get('returncode') == 0 and r.get('ff_md5') == FF and r.get('finished')]
    else:                                               # Junseok 막음 틀(magi5_e24e 계열) — 성분마다 N = 구 × 셀 · 막음 줄 · judge ok
        rows = d.get('rows', [])
        ok = [r for r in rows if d.get('final') and d.get('ff_md5') == FF and r.get('status') == 'ok' and r.get('judge') == 'ok'
              and r.get('returncode') == 0 and not r.get('stderr_not_found')
              and all(r['block'][c]['blocked_line'] and r['block'][c]['n_blocked'] == r['n_expected'][c] for c in ('CO2', 'N2'))]
        if tag == 'e24i_c2h5_open':
            acc = load('results_e24i_access_junseok.json')['summary'][tag]
            assert all(r['n_expected']['CO2'] == acc['spheres_1.65'] * math.prod(r['unit_cells'])
                       and r['n_expected']['N2'] == acc['spheres_1.82'] * math.prod(r['unit_cells']) for r in ok)
    if len(ok) != 3:
        return None, f"ok {len(ok)}/3 · status {[r.get('status') for r in rows]}"
    if len({r['seed'] for r in ok}) != 3:
        return None, '씨앗 중복'
    s = [r['N_CO2'] / r['N_N2'] * (0.85 / 0.15) for r in ok]
    e = [x * math.hypot(r['N_CO2_err'] / r['N_CO2'], r['N_N2_err'] / r['N_N2']) for x, r in zip(s, ok)]
    for x, r in zip(s, ok):
        assert abs(x - r['S_mix']) < 1e-6 * x, (tag, x, r['S_mix'])
    return dict(S=st.mean(s), Se=st.mean(e) / math.sqrt(3), sd=st.stdev(s), each=s, NCO2=st.mean(r['N_CO2'] for r in ok)), None


def water_unblocked(tag, w):
    d = load('results_e24i_water_hkhome.json')
    if d is None:
        return None, '파일 없음'
    rs = [r for r in d.get('rows', []) if r.get('name') == tag]
    ok = [r for r in rs if r.get('status') == 'ok' and r.get('marker_finished') and r.get('header_gate_ok') and r.get('water_sites_in_rundir') == 5]
    if len(ok) != 4 or len({r['seed'] for r in ok}) != 4:
        return None, f'ok {len(ok)}/4'
    k = [r['KH_water'] for r in ok]
    m, me = st.mean(k), st.mean(r['KH_water_err'] for r in ok) / 2
    i = m / w['KH']
    return dict(idx=i, err=i * math.hypot(me / m, w['KHe'] / w['KH']), sd_rel=st.stdev(k) / m, src='차단 없음'), None


def bp(tag):
    d = load('results_e24i_blockpockets_hkhome.json')
    if d is None or not d.get('finished'):
        return None, '막음 Widom 미완'
    if not d.get('all_ok') or not d.get('seeds_distinct'):
        return None, f"all_ok {d.get('all_ok')} · seeds_distinct {d.get('seeds_distinct')}"
    e = d['per_structure'].get(tag)
    for rk, r in e['rows'].items():
        if not (r['status'] == 'ok' and r['marker_finished'] and r['pockets_blocked_line'] and not r['stderr_not_found']
                and r['n_blocked_reported'] == r['n_expected'] == r['n_spheres_per_uc'] * math.prod(r['unit_cells'])):
            return None, f'{rk} 관문 실패'
    on_c, on_n, off_c, off_n = (e['rows'][k] for k in ('on_CO2@1.65', 'on_N2@1.82', 'off_CO2@1.65', 'off_N2@1.82'))
    S = on_c['KH'] / on_n['KH']
    Se = S * math.hypot(on_c['KH_err'] / on_c['KH'], on_n['KH_err'] / on_n['KH'])
    So = off_c['KH'] / off_n['KH']
    if e.get('S_ON_blocked') is not None:
        assert abs(e['S_ON_blocked'] - S) < 1e-6 * S
    return dict(S=S, Se=Se, KH=on_c['KH'], KHe=on_c['KH_err'], S_off=So, G=S / So), None


def water_blocked(tag, wb):
    d = load(f'results_{tag}_water_blk_junseok.json')
    if d is None:
        return None, '파일 없음'
    rs = [r for r in d.get('rows', []) if abs(r.get('block_radius', 0) - 1.3) < 1e-6]
    ok = [r for r in rs if r.get('status') == 'ok' and r.get('marker_finished') and r.get('header_gate_ok')
          and r.get('water_sites_in_rundir') == 5 and not r.get('stderr_not_found')
          and r.get('block', {}).get('blocked_line') and r.get('block', {}).get('n_blocked') == r.get('n_expected')]
    if len(ok) != 4 or len({r['seed'] for r in ok}) != 4:
        return None, f'ok {len(ok)}/4'
    n130 = load('results_e24i_access_junseok.json')['summary'][tag]['spheres_1.30']
    if not all(r['n_expected'] == n130 * math.prod(r['unit_cells']) for r in ok):
        return None, 'N ≠ 구(1.30) × 셀'
    k = [r['KH_water'] for r in ok]
    m, me = st.mean(k), st.mean(r['KH_water_err'] for r in ok) / 2
    i = m / wb['KH']
    return dict(idx=i, err=i * math.hypot(me / m, wb['KHe'] / wb['KH']), sd_rel=st.stdev(k) / m, src='막음 1.30 ÷ 막음 1.65'), None


def gate5(tag):
    for host in ('desktop-nvsrr9m', 'laptop'):
        d = load(f'results_e24i_gate5_{host}.json')
        if d:
            r = d.get('rows', {}).get(tag)
            if r and r.get('status') == 'ok':
                return r.get('pass'), r.get('LCD_drop_pct')
    return None, None


def main():
    PW, why = widom('results_magi5_e3_e22_parent_widom_desktop-js1ib6u.json')
    pm = [r for r in json.load(open(os.path.join(HERE, 'results_e23_mix_desktop.json')))['rows'] if r['name'].startswith('e22_parent_s')]
    assert len(pm) == 3 and all(r['status'] == 'ok' for r in pm)
    ps = [r['N_CO2'] / r['N_N2'] * (0.85 / 0.15) for r in pm]
    pe = [x * math.hypot(r['N_CO2_err'] / r['N_CO2'], r['N_N2_err'] / r['N_N2']) for x, r in zip(ps, pm)]
    PM = dict(S=st.mean(ps), Se=st.mean(pe) / math.sqrt(3), sd=st.stdev(ps))
    pw = [r for r in json.load(open(os.path.join(HERE, 'results_e22c_water_hkhome.json')))['rows'] if r['name'] == 'e22_parent' and r['status'] == 'ok']
    assert len(pw) == 4
    m, me = st.mean(r['KH_water'] for r in pw), st.mean(r['KH_water_err'] for r in pw) / 2
    PWI = dict(idx=m / PW['KH'], err=m / PW['KH'] * math.hypot(me / m, PW['KHe'] / PW['KH']))
    print(f"기준(원자료): 모체 S_ON {PW['S']:.2f} ± {PW['Se']:.2f} · S_mix {PM['S']:.2f} ± {PM['Se']:.2f}(±̄/√3 · SD {PM['sd']:.2f}) · 물 지수 {PWI['idx']:.5f} ± {PWI['err']:.5f}")
    acc = load('results_e24i_access_junseok.json')['summary']
    print('\n## (1) S_ON(주머니 있으면 막음값) − 모체')
    SON, OUT = {}, {}
    for t in TAGS:
        w, why = widom(f'results_magi5_e3_{t}_widom_{WID[t]}.json')
        if w is None:
            print(f'  {t}: Widom 미완비 — {why}'); continue
        pk = acc[t]['spheres_1.65'] + acc[t]['spheres_1.82']
        if pk:
            v, why = bp(t)
            if v is None:
                print(f"  {t}: 주머니(구 {acc[t]['spheres_1.65']}·{acc[t]['spheres_1.82']}) — {why} · 차단 없는 {w['S']:.2f} 는 서술"); continue
            v['src'] = '막음'
        else:
            v = dict(w, src='차단 없음(주머니 0)')
        x = u(v['S'] - PW['S'], v['Se'], PW['Se'])
        SON[t] = dict(v, x=x, W=w)
        print(f"  {t}: S_ON {v['S']:.2f} ± {v['Se']:.2f} [{v['src']}] · S_OFF {v['S_off']:.1f} · G {v['G']:.2f} → {x:+.2f} 단위 → 후속 {'진입' if x >= TH else '제외'}")
    if SON:
        print(f"  → (1) {'성립' if any(v['x'] >= TH for v in SON.values()) else ('기각' if len(SON) == 5 else '미완비')}")
    print('\n## 후속 — S_mix · 물 지수 · 관문 ⑤')
    FAM = {}
    for t in TAGS:
        if t not in SON or SON[t]['x'] < TH:
            continue
        mx, w1 = smix(t)
        if SON[t]['src'] == '막음':
            wi, w2 = water_blocked(t, SON[t])
            wu, _ = water_unblocked(t, SON[t]['W'])
        else:
            wi, w2 = water_unblocked(t, SON[t]); wu = None
        g5, lcd = gate5(t)
        line = f"  {t}: S_mix " + (f"{mx['S']:.2f} ± {mx['Se']:.2f}(SD {mx['sd']:.2f} · 씨앗 {', '.join('%.1f' % x for x in mx['each'])} · N_CO₂ {mx['NCO2']:.3f})" if mx else f'미완비({w1})')
        line += ' · 물 지수 ' + (f"{wi['idx']:.5f} ± {wi['err']:.5f}[{wi['src']}]" if wi else f'미완비({w2})')
        if wu:
            line += f" (서술 차단 없음 {wu['idx']:.5f})"
        line += f' · 관문 ⑤ {g5}(LCD 감소 {lcd} %)'
        print(line)
        if mx:
            print(f"      S_mix − 모체: {u(mx['S'] - PM['S'], mx['Se'], PM['Se']):+.2f} 단위 · 씨앗 SEM 자(SD/√3) {u(mx['S'] - PM['S'], mx['sd'] / math.sqrt(3), PM['sd'] / math.sqrt(3)):+.2f}")
        if mx and wi and g5 is True:
            FAM[t] = dict(S=mx['S'], Se=mx['Se'], sd=mx['sd'], idx=wi['idx'], ie=wi['err'])
        elif mx and wi and g5 is False:
            print(f'      관문 ⑤ 탈락 → 순위 밖(서술)')
    want = [t for t in TAGS if t in SON and SON[t]['x'] >= TH]
    print('\n## (2) · E-23 규칙 — {E-24i 후속 · 모체}(ZIF 셋은 E-23 §1 에서 모체에 이미 1.5 단위 넘게 짐)')
    miss = [t for t in want if t not in FAM]
    if len(SON) < 5 or miss:
        print(f'  미완비 {miss if miss else [t for t in TAGS if t not in SON]} — 판정량 보류'); return
    P = dict(FAM, e22_parent=dict(S=PM['S'], Se=PM['Se'], sd=PM['sd'], idx=PWI['idx'], ie=PWI['err']))
    rest, rank = list(P), []
    while rest:
        cand = [a for a in rest if all(u(P[a]['S'] - P[b]['S'], P[a]['Se'], P[b]['Se']) > -TH for b in rest if b != a)]
        cand.sort(key=lambda t: P[t]['idx'])
        top = [cand[0]] + [t for t in cand[1:] if abs(u(P[t]['idx'] - P[cand[0]]['idx'], P[t]['ie'], P[cand[0]]['ie'])) < TH]
        rank.append((cand, top))
        rest = [t for t in rest if t not in top]
    for i, (cand, top) in enumerate(rank, 1):
        print(f"  {i}위 {top}{' (공동)' if len(top) > 1 else ''} ← ① 후보군 {cand}")
    first = rank[0][1]
    for t in first:
        x = u(P[t]['S'] - PM['S'], P[t]['Se'], PM['Se'])
        print(f"  (2) {t}: S_mix {P[t]['S']:.2f} − 모체 {PM['S']:.2f} → {x:+.2f} 단위 → {'성립 — 확장 설계 살아남음' if x >= TH else '기각 — 확장 설계 철회'}")
    print('\n  짝 비교(S_mix 단위 · 씨앗 SEM 자(SD/√3) | 물 지수 단위):')
    ks = [k for k in P]
    for i, a in enumerate(ks):
        for b in ks[i + 1:]:
            print(f"    {a} − {b}: {u(P[a]['S'] - P[b]['S'], P[a]['Se'], P[b]['Se']):+.2f} · {u(P[a]['S'] - P[b]['S'], P[a]['sd'] / 3 ** .5, P[b]['sd'] / 3 ** .5):+.2f} | {u(P[a]['idx'] - P[b]['idx'], P[a]['ie'], P[b]['ie']):+.2f}")
    print('\n출처:', json.dumps(SRC, ensure_ascii=False))


if __name__ == '__main__':
    main()
