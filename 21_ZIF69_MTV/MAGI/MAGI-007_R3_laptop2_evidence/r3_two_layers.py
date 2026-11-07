#!/usr/bin/env python3
"""MAGI-007 R3 (laptop2 · Balthasar) — A-2 · A-14 의 두 층을 원자료로 나눕니다.

계산은 새로 돌리지 않습니다. master 고정 커밋의 결과 JSON 을 `git show` 로 읽어 산술만 합니다.
  헨리 층   Widom ON 의 K_H(CO₂) · K_H(N₂)  (mol/kg/Pa, 298 K)
  작동점 층 건조 15:85 · 100 kPa · 298 K 혼합 GCMC 의 N_CO₂ · N_N₂ (mol/kg) — R1 근거 묶음 evidence.json 과 같은 원자료
  잔류비 r_i = N_i(혼합) / (K_H,i · p_i)   — 헨리 직선이 그 분압에서 예측하는 적재 가운데 실제로 남은 몫
  N_i / N_i,모체 = (K_H,i / K_H,i,모체) × (r_i / r_i,모체)   — 헨리 층 × 작동점 층
  S_mix = S_Henry × (r_CO₂ / r_N₂)
−C₂H₅ 는 혼합이 막음 계산이므로 헨리 값도 막음 Widom(results_e24i_blockpockets_hkhome.json on_CO2@1.65 · on_N2@1.82)을 씁니다.
E 3성분 결과는 [E 결과 인용] 으로 따로 둡니다(A-7 답에만 씀).
"""
import json, math, subprocess, sys, hashlib

REV = sys.argv[1] if len(sys.argv) > 1 else 'origin/master'
P_CO2, P_N2 = 15000.0, 85000.0


def show(path):
    b = subprocess.run(['git', 'show', f'{REV}:{path}'], capture_output=True, check=True).stdout
    return json.loads(b), hashlib.md5(b).hexdigest()


SRC = {}
W = {
    'parent': '21_ZIF69_MTV/results_magi5_e3_e22_parent_widom_desktop-js1ib6u.json',
    'cn': '21_ZIF69_MTV/results_magi5_e3_e24i_cn_open_widom_desktop-nvsrr9m.json',
    'br': '21_ZIF69_MTV/results_magi5_e3_e24i_br_open_widom_hkhome.json',
    'cl': '21_ZIF69_MTV/results_magi5_e3_e24i_cl_open_widom_hkhome.json',
    'ch3': '21_ZIF69_MTV/results_magi5_e3_e24i_ch3_open_widom_hkhome.json',
}
KH = {}
for k, p in W.items():
    d, h = show(p); SRC[p] = h
    on = [r for r in d['rows'] if r['charges'] == 'on']
    assert len(on) == 1 and on[0].get('status_CO2', 'ok') == 'ok' and on[0].get('status_N2', 'ok') == 'ok', (k, on)
    r = on[0]
    KH[k] = dict(KC=r['KH_CO2'], KC_err=r['KH_CO2_err'], KN=r['KH_N2'], KN_err=r['KH_N2_err'],
                 dUC=r['dU_CO2'], dUN=r['dU_N2'], cif=d.get('cif'), src=p)

# −C₂H₅ 막음 Widom
bp = '21_ZIF69_MTV/results_e24i_blockpockets_hkhome.json'
d, h = show(bp); SRC[bp] = h
rows_c2 = d['per_structure']['e24i_c2h5_open']['rows']
for key in ('on_CO2@1.65', 'on_N2@1.82'):
    r = rows_c2[key]
    assert r['status'] == 'ok' and r['marker_finished'] and r['block_pockets_used'] and r['returncode'] == 0, key
    assert r['n_blocked_reported'] == r['n_expected'], key
KH['c2h5'] = dict(KC=rows_c2['on_CO2@1.65']['KH'], KC_err=rows_c2['on_CO2@1.65']['KH_err'],
                  KN=rows_c2['on_N2@1.82']['KH'], KN_err=rows_c2['on_N2@1.82']['KH_err'],
                  dUC=rows_c2['on_CO2@1.65']['dU'], dUN=rows_c2['on_N2@1.82']['dU'],
                  cif='(막음 Widom)', src=bp)

# 작동점 적재: R1 근거 묶음(공개 · 해시 대조 끝)의 evidence.json
evp = '21_ZIF69_MTV/MAGI/MAGI-007_R1_laptop2_evidence/evidence.json'
ev, h = show(evp); SRC[evp] = h
MIX = {k: dict(NC=v['N_CO2_mean'], NN=v['N_N2_mean'], S=v['S_mix_mean'], n=v['n']) for k, v in ev['smix_298_open'].items()}
par = ev['parent_298'][0]
MIX['parent'] = dict(NC=sum(par[6]) / 3, NN=sum(par[7]) / 3, S=sum(par[2]) / 3, n=3)

out = dict(rev=subprocess.run(['git', 'rev-parse', REV], capture_output=True, text=True).stdout.strip(),
           p=dict(CO2=P_CO2, N2=P_N2), sources_md5=SRC, rows={})
base = None
for k in ['parent', 'cn', 'br', 'cl', 'ch3', 'c2h5']:
    kh, mx = KH[k], MIX[k]
    rC = mx['NC'] / (kh['KC'] * P_CO2)
    rN = mx['NN'] / (kh['KN'] * P_N2)
    row = dict(KH_CO2=kh['KC'], KH_N2=kh['KN'], S_Henry=kh['KC'] / kh['KN'], dU_CO2=kh['dUC'], dU_N2=kh['dUN'],
               N_CO2=mx['NC'], N_N2=mx['NN'], S_mix=mx['S'], n_mix=mx['n'],
               ideal_CO2=kh['KC'] * P_CO2, ideal_N2=kh['KN'] * P_N2, r_CO2=rC, r_N2=rN,
               S_mix_over_S_Henry=mx['S'] / (kh['KC'] / kh['KN']), rC_over_rN=rC / rN)
    if k == 'parent':
        base = row
    else:
        row['vs_parent'] = dict(
            KH_CO2=row['KH_CO2'] / base['KH_CO2'], KH_N2=row['KH_N2'] / base['KH_N2'],
            N_CO2=row['N_CO2'] / base['N_CO2'], N_N2=row['N_N2'] / base['N_N2'],
            r_CO2=row['r_CO2'] / base['r_CO2'], r_N2=row['r_N2'] / base['r_N2'],
            S_Henry=row['S_Henry'] / base['S_Henry'], S_mix=row['S_mix'] / base['S_mix'])
        lnN = math.log(row['N_N2'] / base['N_N2'])
        row['N2_drop_share'] = dict(henry=math.log(row['KH_N2'] / base['KH_N2']) / lnN,
                                    working_point=math.log(row['r_N2'] / base['r_N2']) / lnN)
        # 작동점 층 안에서: CO₂ 가 남긴 빈자리만큼 N₂ 가 줄었는가(공유 빈자리 경쟁이면 1)
        row['N2_extra_exclusion'] = (row['r_N2'] / base['r_N2']) / (row['r_CO2'] / base['r_CO2'])
        lnS = math.log(row['S_mix'] / base['S_mix'])
        row['S_gain_share'] = dict(henry=math.log(row['S_Henry'] / base['S_Henry']) / lnS,
                                   working_point=math.log(row['rC_over_rN'] / base['rC_over_rN']) / lnS)
    out['rows'][k] = row

# [E 결과 인용] — A-7 답에만
ep = '21_ZIF69_MTV/results_znbdt_e_humid3_laptop2.json'
e, h = show(ep); SRC[ep] = h
yN_ratio = e['protocol']['y']['N2'] / 0.85
tag = {'e22_parent': 'parent', 'e24i_cn_open': 'cn', 'e24i_br_open': 'br', 'e24i_cl_open': 'cl', 'e24i_ch3_open': 'ch3'}
out['E_cited'] = {'note': '[E 결과 인용] A-7 답에만 씀 · R1 예측 수치는 고치지 않음', 'pN2_humid_over_dry': yN_ratio, 'rows': {}}
for m, v in e['materials'].items():
    k = tag[m]
    out['E_cited']['rows'][k] = dict(S_humid=v['S_humid_mean'], S_humid_pm=v['S_humid_pm'],
                                     retention=v['S_humid_mean'] / MIX[k]['S'],
                                     N_CO2_humid_over_dry=v['N_CO2_mean'] / MIX[k]['NC'],
                                     N_N2_humid_over_dry=v['N_N2_mean'] / MIX[k]['NN'],
                                     N_N2_beyond_pressure=v['N_N2_mean'] / MIX[k]['NN'] / yN_ratio,
                                     N_H2O=v['N_H2O_mean'])
json.dump(out, sys.stdout, ensure_ascii=False, indent=1)
