"""종합자 독립 재계산 — ZNBDT-C2 X(N₂ 추가 배제비). 등록 ASSIGN_ZNBDT_C2 §2 의 식. HKHOME judge 코드를 쓰지 않음."""
import json, math, sys, os
C2 = sys.argv[1]  # dir with the four C2 files
P = {'CO2': 15000.0, 'N2': 85000.0}
WID = {'parent': 'results_magi5_e3_e22_parent_widom_desktop-js1ib6u.json', 'cn': 'results_magi5_e3_e24i_cn_open_widom_desktop-nvsrr9m.json',
       'br': 'results_magi5_e3_e24i_br_open_widom_hkhome.json', 'cl': 'results_magi5_e3_e24i_cl_open_widom_hkhome.json', 'ch3': 'results_magi5_e3_e24i_ch3_open_widom_hkhome.json',
       'U': os.path.join(C2, 'results_magi5_e3_znbdt_c2_apolarU_widom_hkhome.json'), 'I': os.path.join(C2, 'results_magi5_e3_znbdt_c2_apolarI_widom_hkhome.json'),
       'L': os.path.join(C2, 'results_magi5_e3_znbdt_c2_apolarL_widom_hkhome.json')}
MIX = {'parent': (['results_e23_mix_desktop.json'], 'e22_parent_s'), 'cn': (['results_e24i_e24i_cn_open_mix_hkhome.json', 'results_e24i_e24i_cn_open_mix_s456_hkhome.json'], 'e24i_cn_open_s'),
       'br': (['results_e24i_e24i_br_open_mix_laptop2.json', 'results_e24i_e24i_br_open_mix_s456_hkhome.json'], 'e24i_br_open_s'), 'cl': (['results_e24i_e24i_cl_open_mix_junseok.json'], 'e24i_cl_open_s'),
       'ch3': (['results_e24i_e24i_ch3_open_mix_laptop2.json'], 'e24i_ch3_open_s'),
       'U': ([os.path.join(C2, 'results_znbdt_c2_znbdt_c2_apolarU_mix_hkhome.json')], 'znbdt_c2_apolarU_s'), 'I': ([os.path.join(C2, 'results_znbdt_c2_znbdt_c2_apolarI_mix_hkhome.json')], 'znbdt_c2_apolarI_s'),
       'L': ([os.path.join(C2, 'results_znbdt_c2_znbdt_c2_apolarL_mix_hkhome.json')], 'znbdt_c2_apolarL_s')}
def widom(k):
    d = json.load(open(WID[k])); rows = [r for r in d['rows'] if r.get('charges') == 'on' and r.get('status_CO2') == 'ok' and r.get('status_N2') == 'ok']
    assert len(rows) == 1, (k, len(rows)); r = rows[0]
    return r['KH_CO2'], r['KH_CO2_err'] / r['KH_CO2'], r['KH_N2'], r['KH_N2_err'] / r['KH_N2'], r.get('dU_CO2')
def mix(k):
    files, pre = MIX[k]; rows = []
    for f in files: rows += [r for r in json.load(open(f))['rows'] if r['name'].startswith(pre)]
    ok = [r for r in rows if r.get('status') == 'ok' and r.get('returncode') == 0 and r.get('N_CO2') is not None]
    seeds = [r.get('seed') for r in ok]; assert len(set(seeds)) == len(seeds), ('seed dup', k)
    n = len(ok); NC = sum(r['N_CO2'] for r in ok) / n; NN = sum(r['N_N2'] for r in ok) / n
    eNC = (sum(r['N_CO2_err'] for r in ok) / n) / math.sqrt(n) / NC; eNN = (sum(r['N_N2_err'] for r in ok) / n) / math.sqrt(n) / NN
    S = sum(r['S_mix'] for r in ok) / n
    return NC, NN, eNC, eNN, S, n
out = {}
for k in ('parent', 'cn', 'br', 'cl', 'ch3', 'U', 'I', 'L'):
    KC, eKC, KN, eKN, dU = widom(k); NC, NN, eNC, eNN, S, n = mix(k)
    rC = NC / (KC * P['CO2']); rN = NN / (KN * P['N2'])
    out[k] = dict(KC=KC, KN=KN, NC=NC, NN=NN, S=S, n=n, rC=rC, rN=rN, SH=KC / KN, e=math.sqrt(eKC**2 + eKN**2 + eNC**2 + eNN**2), dU=dU, eKC=eKC, eKN=eKN)
b = out['parent']
for k, o in out.items():
    o['X'] = (o['rN'] / b['rN']) / (o['rC'] / b['rC']); o['eX'] = o['X'] * o['e']
    o['KC_ratio'] = o['KC'] / b['KC']; o['KN_ratio'] = o['KN'] / b['KN']; o['op_over_henry'] = (o['S'] / o['SH']) / (b['S'] / b['SH'])
print(f"{'k':7s} {'X':>7s} {'±':>6s} {'KC/par':>7s} {'KN/par':>7s} {'N_CO2':>7s} {'N_N2':>7s} {'S_mix':>7s} {'op/H':>5s} {'n':>2s} {'dU_CO2':>7s}")
for k, o in out.items():
    print(f"{k:7s} {o['X']:7.3f} {o['eX']:6.3f} {o['KC_ratio']:7.3f} {o['KN_ratio']:7.3f} {o['NC']:7.3f} {o['NN']:7.4f} {o['S']:7.1f} {o['op_over_henry']:5.2f} {o['n']:2d} {o['dU']:7.1f}")
def dist(a, r): return abs(out[a]['X'] - out[r]['X']) / math.sqrt(out[a]['eX']**2 + out[r]['eX']**2)
def read(a):
    dCN, dCH = dist(a, 'cn'), dist(a, 'ch3')
    f = (out[a]['X'] - out['cn']['X']) / (out['ch3']['X'] - out['cn']['X'])
    ef = math.sqrt(out[a]['eX']**2 + out['cn']['eX']**2) / abs(out['ch3']['X'] - out['cn']['X'])
    if dCN < 1.5 and dCH < 1.5: v = '판별 불가(둘 다 1.5 안)'
    elif dCN < 1.5: v = '모양'
    elif dCH < 1.5: v = '극성'
    else: v = '중간'
    print(f"{a}: d_CN {dCN:.2f} · d_CH3 {dCH:.2f} · d_Br {dist(a,'br'):.2f} · d_Cl {dist(a,'cl'):.2f} → {v} · f = {f:.2f} ± {ef:.2f}")
    return v
vU, vI = read('U'), read('I')
print('전체(C2 §2-5 · U 대 I):', '보정 방식에 민감 — 판별 불가 (U ≠ I)' if vU != vI else vU)
if 'L' in out:   # §7 C2-L (2026-11-05 등록 · 2026-11-06 자료) — U 대 L
    vL = read('L')
    print('C2-L 전체(§7 · U 대 L):', ('같은 갈래 → C2 닫는 판독 = ' + vU) if vU == vL else '전하 끄기 대조는 보정 방식에 민감 — 닫지 않음 (U ≠ L)')
    def kdist(a, r, g='KC'):   # 모체비 거리 — 모체 항은 양쪽에 같아 지워지므로 자 = 두 판 Widom 상대 ± 합성
        ra, rr = out[a][g] / b[g], out[r][g] / b[g]; ea, er = out[a]['e' + g], out[r]['e' + g]
        return abs(ra - rr) / math.sqrt((ra * ea)**2 + (rr * er)**2)
    print(f"§7 보조: K_H(CO₂) 모체비 L {out['L']['KC_ratio']:.3f} · U {out['U']['KC_ratio']:.3f} · I {out['I']['KC_ratio']:.3f} → L–U {kdist('L','U'):.2f} 단위 · L–I {kdist('L','I'):.2f} 단위")
    print('§10 자료 후 규칙(K_H(CO₂) 모체비가 −CN 과 1.5 단위 안인 판만 허용) — 종합자 재계산:')
    for v in ('U', 'L', 'I'):
        dc, dn = kdist(v, 'cn'), kdist(v, 'cn', 'KN')
        print(f"  {v}: K_H(CO₂) −CN 과 {dc:.2f} 단위 → {'허용' if dc < 1.5 else '불허'} · (서술) K_H(N₂) −CN 과 {dn:.2f} 단위")
print('재현 관문(표 0.72 · 1.01 · 0.86 · 0.85 와 소수 둘째 자리):', {k: round(out[k]['X'], 2) for k in ('cn', 'ch3', 'br', 'cl')})
