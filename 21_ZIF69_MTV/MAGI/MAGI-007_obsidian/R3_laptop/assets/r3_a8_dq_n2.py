# MAGI-007 R3 laptop (A-8, A-2): Widom 원자료에서 ΔQ(CO2)−ΔQ(N2) 의 치환체−모체 차를 다시 내고 323 K 비를 재계산
import json, math, subprocess
R = 'refs/remotes/origin/master'
F = {'parent': '21_ZIF69_MTV/results_magi5_e3_e22_parent_widom_desktop-js1ib6u.json',
     'cn': '21_ZIF69_MTV/results_magi5_e3_e24i_cn_open_widom_desktop-nvsrr9m.json',
     'br': '21_ZIF69_MTV/results_magi5_e3_e24i_br_open_widom_hkhome.json',
     'cl': '21_ZIF69_MTV/results_magi5_e3_e24i_cl_open_widom_hkhome.json',
     'ch3': '21_ZIF69_MTV/results_magi5_e3_e24i_ch3_open_widom_hkhome.json'}
SMIX = {'parent': 75.43, 'cn': 139.77, 'br': 127.92, 'cl': 111.15, 'ch3': 108.67}  # 순위표 판(R2 §0 재현값)
def on(tag):
    d = json.loads(subprocess.check_output(['git', 'show', f'{R}:{F[tag]}']))
    r = [x for x in d['rows'] if x['charges'] == 'on' and x['temp_K'] == 298.0][0]
    assert r['status_CO2'] == 'ok' and r['status_N2'] == 'ok'
    return r
Rg = 8.314462618e-3
X = 1/298 - 1/323
dQ0 = -math.log(50.48/75.43) / X * Rg       # 모체 323/298 비에서 맞춘 ΔQ (R1 M-10)
p = on('parent')
print(f'dQ0 = {dQ0:.3f} kJ/mol  (parent ratio {50.48/75.43:.4f})')
print('tag  dQco2  dQn2  delta(co2-n2)  ratio_R1(co2only)  ratio_A8  KHgain  WPgain  WP/KH  ratio_HenryLimit')
out = {}
for t in ['cn', 'br', 'cl', 'ch3']:
    s = on(t)
    dco2 = -(s['dU_CO2'] - p['dU_CO2'])          # Q_st 차(RT 는 상쇄)
    dn2 = -(s['dU_N2'] - p['dU_N2'])
    e_co2 = math.hypot(s['dU_CO2_err'], p['dU_CO2_err']); e_n2 = math.hypot(s['dU_N2_err'], p['dU_N2_err'])
    delta = dco2 - dn2
    r_r1 = math.exp(-(dQ0 + dco2) / Rg * X)
    r_a8 = math.exp(-(dQ0 + delta) / Rg * X)
    khg = (s['KH_CO2']/s['KH_N2']) / (p['KH_CO2']/p['KH_N2'])
    wpg = SMIX[t] / SMIX['parent']
    # 극단: 323 K 에서 작동점 이득이 헨리 이득까지 완전히 꺼지는 경우
    r_lim = r_a8 * khg / wpg
    out[t] = dict(dQ_CO2=dco2, dQ_CO2_err=e_co2, dQ_N2=dn2, dQ_N2_err=e_n2, delta=delta,
                  ratio_R1=r_r1, ratio_A8=r_a8, KH_gain=khg, WP_gain=wpg, WP_over_KH=wpg/khg, ratio_henry_limit=r_lim)
    print(f'{t:4s} {dco2:+.2f}±{e_co2:.2f} {dn2:+.2f}±{e_n2:.2f} {delta:+.2f}  {r_r1:.3f}  {r_a8:.3f}  {khg:.3f}  {wpg:.3f}  {wpg/khg:.2f}  {r_lim:.3f}')
json.dump(dict(dQ0=dQ0, rows=out), open(__file__.replace('.py', '.json'), 'w'), indent=1, ensure_ascii=False)
