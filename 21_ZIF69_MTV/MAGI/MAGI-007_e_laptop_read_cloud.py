"""종합자 E 읽기(랩탑 6작업) — ASSIGN §E 정의로 원자료 N 에서 S_humid 재계산(JSON 의 S_humid 필드는 대조용)."""
import json, math, sys
L = json.load(open(sys.argv[1])); L2 = json.load(open(sys.argv[2]))
Y = 0.150000/0.821479
def stats(rows):
    ok=[r for r in rows if r.get('ok') and r.get('finished') and r.get('returncode')==0 and all(v==1 for v in r['loading_line_counts'].values())]
    assert len({r['seed'] for r in ok})==len(ok)
    S=[(r['N_CO2']/r['N_N2'])/Y for r in ok]; rel=[math.hypot(r['N_CO2_err']/r['N_CO2'], r['N_N2_err']/r['N_N2']) for r in ok]
    pm=[s*e for s,e in zip(S,rel)]; n=len(S); m=sum(S)/n; sd=(sum((s-m)**2 for s in S)/(n-1))**0.5
    return dict(n=n, S=m, pm=sum(pm)/n/math.sqrt(n), sd=sd, n2rel=max(r['N_N2_err']/r['N_N2'] for r in ok), srel=(sum(pm)/n/math.sqrt(n))/m,
                NC=sum(r['N_CO2'] for r in ok)/n, NN=sum(r['N_N2'] for r in ok)/n, NW=sum(r['N_H2O'] for r in ok)/n, each=[round(s,2) for s in S], json_each=[round(r['S_humid'],2) for r in ok])
R={}
for base in ('mslm050','e24i_c2h5_open'): R[base]=stats([r for r in L['rows'] if r['base']==base])
for base in ('e22_parent','e24i_cn_open','e24i_br_open','e24i_cl_open','e24i_ch3_open'): R[base]=stats([r for r in L2['rows'] if r['base']==base])
print('관문(랩탑): n', L['audit_summary'], '· 래퍼 md5', L['wrapper_md5'], '· 몰분율', L['protocol']['y'], '· P', L['protocol']['P_Pa'])
for k,v in R.items(): print(f"{k:16s} S_humid {v['S']:7.2f} ± {v['pm']:5.2f} (SD {v['sd']:4.2f}) · 씨앗 {v['each']} (JSON {v['json_each']}) · N₂상대± max {v['n2rel']:.3f} · S상대± {v['srel']:.3f} · N CO₂ {v['NC']:.3f} N₂ {v['NN']:.4f} H₂O {v['NW']:.4f}")
def d(a,b):
    A,B=R[a],R[b]; u=math.hypot(A['pm'],B['pm']); usd=math.hypot(A['sd'],B['sd'])
    return (A['S']-B['S'])/u, (A['S']-B['S'])/usd
print('\n(E-1) −C₂H₅ 짝 비교 [단위 · 씨앗 SD 자]')
for b in ('e24i_cn_open','e24i_br_open','e24i_cl_open','e24i_ch3_open','e22_parent'):
    x,y=d('e24i_c2h5_open',b); print(f"  c2h5 − {b:14s}: {x:+6.2f} 단위 · {y:+6.2f} 씨앗SD → {'순위' if abs(x)>=1.5 else '공동'}")
print('\n(E-3) 각 행 − mslm050 [단위 · 씨앗 SD 자]')
for a in ('e24i_cn_open','e24i_br_open','e24i_cl_open','e24i_ch3_open','e24i_c2h5_open','e22_parent'):
    x,y=d(a,'mslm050'); print(f"  {a:16s} − mslm050: {x:+6.2f} 단위 · {y:+6.2f} 씨앗SD → {'순위(위)' if x>=1.5 else ('순위(아래)' if x<=-1.5 else '공동')}")
