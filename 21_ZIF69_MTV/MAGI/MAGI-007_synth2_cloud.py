"""11-13 종합 — H(CoRE 22 의 323 K 회수량) · I(2021 Zn srs 우리 앞단판) · M(−Cl 혼합 배치 회수량) · N(물 수 고정 회수량).
종합자 자기 코드 · 원자료 JSON 만. A · B · C · G · F 는 MAGI-007_core22_synth_cloud.json(같은 날 다시 돌린 판)에서 읽음."""
import json, glob, os, math, statistics as st, itertools
HERE=os.path.dirname(os.path.abspath(__file__)); R=os.path.dirname(HERE)
L=lambda p: json.load(open(os.path.join(R,p)))
S1=json.load(open(os.path.join(HERE,'MAGI-007_core22_synth_cloud.json')))
A=S1['A']; B=S1['B']; C=S1['C']; G=S1['G']; F=S1['F']; S298=S1['S298_ours']; S323=S1['S323_ours']
OUR=[('e22_parent','모체'),('e24i_cn_open','−CN'),('e24i_no2_open','−NO₂'),('e24i_cl_open','−Cl'),('e24i_ch3_open','−CH₃'),('e24i_br_open','−Br')]
def ms(vals, errs):
    n=len(vals); return dict(m=st.mean(vals), pm=st.mean(errs)/math.sqrt(n), sd=(st.stdev(vals) if n>1 else float('nan')), n=n)
def units(a,b): return (a['m']-b['m'])/math.hypot(a['pm'],b['pm'])
def wcstat(rows):
    o={}
    for k in ('tsa','vsa'): o[k]=ms([r['working_capacity'][k]['value'] for r in rows],[r['working_capacity'][k]['err'] for r in rows])
    o['ads_co2']=st.mean(r['loadings']['ads']['CO2']['mol_per_kg'] for r in rows); o['tsa_res']=st.mean(r['loadings']['tsa']['CO2']['mol_per_kg'] for r in rows)
    o['ads_h2o']=st.mean(r['loadings']['ads']['water']['mol_per_kg'] for r in rows); o['regen']=1-o['tsa_res']/o['ads_co2']; return o
def audit_ok(S):
    aud=S['audit']; return len(aud)==9 and all(x['ok'] and x['finished'] and x['returncode']==0 for x in aud), [x['seed'] for x in aud]
out={}
_ann=L('core_pop_annotated.json'); ann={r['key']:r for r in (_ann if isinstance(_ann,list) else _ann['rows'])}
stem=lambda k: ann[k]['file'][:-4]
C323=[(323.0,15000.0),(373.0,15000.0),(323.0,5000.0)]; C298=[(298.0,15000.0),(373.0,15000.0),(298.0,5000.0)]
cond=lambda d:[(c['T_K'],c['p_co2_Pa']) for c in d['conditions']]
# ---------- H: CoRE 22 323 K 회수량
H={}; hseeds=[]
for k in G:
    f=[x for x in glob.glob(os.path.join(R,f'v3w_humid_wc_323/humid_wc_323_core22_{stem(k)}_*.json'))]; s=glob.glob(os.path.join(R,f'results_core22_{stem(k)}_humid_wc_323_summary_*.json'))
    assert len(f)==1 and len(s)==1,(k,f,s)
    d=json.load(open(f[0])); S=json.load(open(s[0])); assert d['complete'] and S['complete'] and d['p_h2o_Pa']==11114.1 and cond(d)==C323 and len(d['rows'])==3,k
    assert all(v['ok'] for v in d['header_gate'].values()),k
    ok,seeds=audit_ok(S); o=wcstat(d['rows']); o['audit_ok']=ok; hseeds+=seeds; o['machine']=d['machine']; o['tag']=G[k]['tag']
    o['blocked']=sorted({c for x in S['audit'] for c in (x.get('blocked_components') or [g for g,b in (x.get('block') or {}).items() if b.get('n_blocked')])})
    o['R']=o['tsa']['m']/G[k]['tsa']['m']; o['R_pm']=o['R']*math.hypot(o['tsa']['pm']/o['tsa']['m'], G[k]['tsa']['pm']/G[k]['tsa']['m']); H[k]=o
print(f"=== H  CoRE 22 습윤 TSA 회수량 323 K (3씨앗) + 우리 6(6씨앗) · 구조 {len(H)}/22 · 감사 전부 ok {all(H[k]['audit_ok'] for k in H)} · 씨앗 {len(hseeds)} 고유 {len(set(hseeds))}")
allH={**H, **{nm:B[nm] for _,nm in OUR}}
for k in sorted(allH,key=lambda k:-allH[k]['tsa']['m']):
    v=allH[k]; pre='  ** ' if k not in H else '  '
    print(f"{pre}{k:24s} WC_TSA,323 {v['tsa']['m']:.3f} ± {v['tsa']['pm']:.3f} (SD {v['tsa']['sd']:.3f}) VSA {v['vsa']['m']:.3f} ads {v['ads_co2']:.3f} 재생 {v['regen']*100:5.1f}% 물 {v['ads_h2o']:.3f} R {v['R']:.3f}±{v['R_pm']:.3f} " + (f"{v['machine']} 막음 {'/'.join(v['blocked']) or '—'} {v['tag']} · −CN 대 {units(v['tsa'],B['−CN']['tsa']):+.2f}" if k in H else ''))
cmpH={}
for _,nm in OUR:
    ab=[k for k in H if units(B[nm]['tsa'],H[k]['tsa'])>1.5]; be=[k for k in H if units(B[nm]['tsa'],H[k]['tsa'])<-1.5]; cmpH[nm]=(len(ab),22-len(ab)-len(be),len(be))
print('  우리 행이 CoRE 22 보다 1.5 단위 위 / 구별 불가 / 아래:', cmpH)
print('  −CN 보다 1.5 단위 넘게 위인 CoRE:', [(k,round(H[k]['tsa']['m'],3),round(units(H[k]['tsa'],B['−CN']['tsa']),2)) for k in H if units(H[k]['tsa'],B['−CN']['tsa'])>1.5])
print('  −CN 과 구별 불가:', [(k,round(H[k]['tsa']['m'],3),round(units(H[k]['tsa'],B['−CN']['tsa']),2)) for k in H if abs(units(H[k]['tsa'],B['−CN']['tsa']))<=1.5])
Rs=sorted(H[k]['R'] for k in H); print(f"  CoRE R(323/298) 중앙 {st.median(Rs):.3f} · 범위 {Rs[0]:.3f}~{Rs[-1]:.3f} · 우리 여섯 {min(B[n]['R'] for _,n in OUR):.3f}~{max(B[n]['R'] for _,n in OUR):.3f}")
print('  R 이 −CN(%.3f) 보다 1.5 단위 넘게 큰 CoRE:'%B['−CN']['R'], [(k,round(H[k]['R'],3)) for k in H if (H[k]['R']-B['−CN']['R'])/math.hypot(H[k]['R_pm'],B['−CN']['R_pm'])>1.5])
out['H']=H; out['H_cmp']=cmpH
# ---------- I: 2021 Zn srs 우리 앞단판
KI='2021[Zn][srs]3[FSR]1'
dg=L('v3w_humid_wc/humid_working_capacity_w2_i_znsrs_ourfe_hkhome.json'); sg=L('results_i_znsrs_ourfe_humid_summary_hkhome.json')
assert dg['p_h2o_Pa']==2852.1 and cond(dg)==C298 and len(dg['rows'])==3
okg,seedg=audit_ok(sg); IG=wcstat(dg['rows'])
dh=L('v3w_humid_wc_323/humid_wc_323_i_znsrs_ourfe_hkhome.json'); sh=L('results_i_znsrs_ourfe_humid_wc_323_summary_hkhome.json')
assert dh['complete'] and sh['complete'] and dh['p_h2o_Pa']==11114.1 and cond(dh)==C323 and len(dh['rows'])==3 and all(v['ok'] for v in dh['header_gate'].values())
okh,seedh=audit_ok(sh); IH=wcstat(dh['rows'])
dc=L('results_i_znsrs_ourfe_e_humid3_hkhome.json'); rc=dc['rows']; assert len(rc)==3 and all(r['ok'] and r['finished'] and r['returncode']==0 for r in rc)
assert {json.dumps(r['input_molfractions'],sort_keys=True) for r in rc}=={json.dumps({"CO2":"0.150000","N2":"0.821479","water":"0.028521"},sort_keys=True)}
Y298=0.15/0.821479
Sv=[(r['N_CO2']/r['N_N2'])/Y298 for r in rc]; Se=[s*math.hypot(r['N_CO2_err']/r['N_CO2'], r['N_N2_err']/r['N_N2']) for r,s in zip(rc,Sv)]; IC=ms(Sv,Se); IC['N_H2O']=st.mean(r['N_H2O'] for r in rc)
seedc=[r['seed'] for r in rc]; alls=seedg+seedh+seedc
blk=L('results_i_blocks_hkhome.json')
print(f"=== I  2021 Zn srs 우리 앞단판 · 감사 G {okg} H {okh} · 씨앗 {len(alls)} 고유 {len(set(alls))} · 막음 필요 {blk.get('n_needing_blockpockets')} all_blocks_ok {blk.get('all_blocks_ok')}")
print(f"  298 K WC {IG['tsa']['m']:.4f} ± {IG['tsa']['pm']:.4f} (SD {IG['tsa']['sd']:.4f}) ads {IG['ads_co2']:.3f} 재생 {IG['regen']*100:.1f}% 물 {IG['ads_h2o']:.3f} | −CN {A['−CN']['tsa']['m']:.4f} ± {A['−CN']['tsa']['pm']:.4f} → {units(IG['tsa'],A['−CN']['tsa']):+.2f} 단위 | CoRE 판 {G[KI]['tsa']['m']:.4f} ± {G[KI]['tsa']['pm']:.4f} → 앞단 효과 {IG['tsa']['m']/G[KI]['tsa']['m']-1:+.1%} ({units(IG['tsa'],G[KI]['tsa']):+.2f} 단위)")
print(f"  323 K WC {IH['tsa']['m']:.4f} ± {IH['tsa']['pm']:.4f} (SD {IH['tsa']['sd']:.4f}) ads {IH['ads_co2']:.3f} 재생 {IH['regen']*100:.1f}% 물 {IH['ads_h2o']:.3f} | −CN {B['−CN']['tsa']['m']:.4f} ± {B['−CN']['tsa']['pm']:.4f} → {units(IH['tsa'],B['−CN']['tsa']):+.2f} 단위 | CoRE 판 {H[KI]['tsa']['m']:.4f} ± {H[KI]['tsa']['pm']:.4f} → 앞단 효과 {IH['tsa']['m']/H[KI]['tsa']['m']-1:+.1%} ({units(IH['tsa'],H[KI]['tsa']):+.2f} 단위)")
print(f"  323 K: 나머지 우리 다섯 대비", {nm:round(units(IH['tsa'],B[nm]['tsa']),2) for _,nm in OUR})
Ri=IH['tsa']['m']/IG['tsa']['m']; print(f"  R(323/298) {Ri:.3f} · CoRE 판 R {H[KI]['R']:.3f} · −CN R {B['−CN']['R']:.3f}")
print(f"  S_humid,298 {IC['m']:.2f} ± {IC['pm']:.2f} (SD {IC['sd']:.2f}) 물 {IC['N_H2O']:.3f} | CoRE 판 {C[KI]['m']:.2f} ± {C[KI]['pm']:.2f} → {IC['m']/C[KI]['m']-1:+.1%} | −CN {S298['−CN']['m']:.1f}")
out['I']=dict(G=IG,H=IH,C=IC,R=Ri)
# ---------- M: −Cl 혼합 배치
print('=== M  −Cl 혼합 배치 두 실현 298 K 습윤 TSA 회수량(3씨앗) 대 열린 배치 −Cl · 모체(6씨앗)')
M={}; mseeds=[]
for t in ('e24h_cl_050a','e24h_cl_050b'):
    d=L(f'v3w_humid_wc/humid_working_capacity_w2_{t}_hkhome.json'); S=L(f'results_e24i_{t}_humid_summary_hkhome.json'); assert d['p_h2o_Pa']==2852.1 and cond(d)==C298 and len(d['rows'])==3
    ok,seeds=audit_ok(S); mseeds+=seeds; o=wcstat(d['rows']); o['audit_ok']=ok; M[t]=o
    print(f"  {t} WC {o['tsa']['m']:.4f} ± {o['tsa']['pm']:.4f} (SD {o['tsa']['sd']:.4f}) VSA {o['vsa']['m']:.3f} ads {o['ads_co2']:.3f} 잔류 {o['tsa_res']:.3f} 재생 {o['regen']*100:.1f}% 물 {o['ads_h2o']:.3f} | 열린 −Cl 대 {units(o['tsa'],A['−Cl']['tsa']):+.2f} · 모체 대 {units(o['tsa'],A['모체']['tsa']):+.2f} · −CN 대 {units(o['tsa'],A['−CN']['tsa']):+.2f} | 감사 {ok}")
print(f"  두 실현의 차 {units(M['e24h_cl_050a']['tsa'],M['e24h_cl_050b']['tsa']):+.2f} 단위 · 평균 {(M['e24h_cl_050a']['tsa']['m']+M['e24h_cl_050b']['tsa']['m'])/2:.4f} · 씨앗 {len(mseeds)} 고유 {len(set(mseeds))} · 열린 −Cl {A['−Cl']['tsa']['m']:.4f} ± {A['−Cl']['tsa']['pm']:.4f} ads {A['−Cl']['ads_co2']:.3f} 재생 {A['−Cl']['regen']*100:.1f}% · 모체 {A['모체']['tsa']['m']:.4f} ± {A['모체']['tsa']['pm']:.4f}")
out['M']=M
# ---------- N: 물 수 고정
print('=== N  물 수 고정(셀당 8) 회수량')
rows=[];
for f in sorted(glob.glob(os.path.join(R,'results_fixedwater_wc_*.json'))):
    d=json.load(open(f)); assert d.get('complete') is True,(f);
    for r in d['rows']: r['_m']=d['machine']; rows.append(r)
assert len(rows)==72 and all(r['status']=='ok' and r['finished'] and r['returncode']==0 and r['net_charge_ok'] and not r['stderr_not_found'] and r['water_per_cell']==8.0 and r['n_water_fixed']==48 for r in rows)
assert len({r['seed'] for r in rows})==72 and len({json.load(open(f))['runner_md5'] for f in glob.glob(os.path.join(R,'results_fixedwater_wc_*.json'))})==1
CN=('ads298','ads323','des373')
def q(tag,c,mach=None):
    rr=[r for r in rows if r['tag']==tag and r['condition']==c and (mach is None or r['_m'] in mach)]
    if not rr: return dict(m=float('nan'),pm=float('nan'),sd=float('nan'),n=0)
    return ms([r['N_CO2'] for r in rr],[r['N_CO2_err'] for r in rr])
def wc(a,d): return dict(m=a['m']-d['m'], pm=math.hypot(a['pm'],d['pm']))
# 조건별 반복 SD(구조 · 조건 칸 안 편차를 모음)
psd={}
for c in CN:
    ss=0; df=0
    for t,_ in OUR:
        v=[r['N_CO2'] for r in rows if r['tag']==t and r['condition']==c]; mu=st.mean(v); ss+=sum((x-mu)**2 for x in v); df+=len(v)-1
    psd[c]=math.sqrt(ss/df); e1=st.mean(r['N_CO2_err'] for r in rows if r['condition']==c)/2.776
    print(f"  반복 SD {c}: {psd[c]:.4f} (자유도 {df}) · 한 번 계산의 ±/2.776 = {e1:.4f} → {psd[c]/e1:.1f}배")
def wc_sig(n_a,n_d,c): return math.hypot(psd[c]/math.sqrt(n_a), psd['des373']/math.sqrt(n_d))
N={}
def block(mach, label):
    T={}
    for t,nm in OUR:
        qa={c:q(t,c,mach) for c in CN}
        if qa['ads298']['n']==0: continue
        T[nm]=dict(q=qa, wc298=wc(qa['ads298'],qa['des373']), wc323=wc(qa['ads323'],qa['des373']))
        T[nm]['s298']=wc_sig(qa['ads298']['n'],qa['des373']['n'],'ads298'); T[nm]['s323']=wc_sig(qa['ads323']['n'],qa['des373']['n'],'ads323')
    return T
ALL=block(None,'전체')
for nm in [n for _,n in OUR]:
    v=ALL[nm]; print(f"  {nm:5s} q298 {v['q']['ads298']['m']:.3f}(n{v['q']['ads298']['n']}) q323 {v['q']['ads323']['m']:.3f} q373 {v['q']['des373']['m']:.3f} | WC_N,298 {v['wc298']['m']:.3f} ± {v['wc298']['pm']:.3f} (σ {v['s298']:.3f}) · WC_N,323 {v['wc323']['m']:.3f} ± {v['wc323']['pm']:.3f} (σ {v['s323']:.3f}) | /A {v['wc298']['m']/A[nm]['tsa']['m']:.2f} /B {v['wc323']['m']/B[nm]['tsa']['m']:.2f} · q298/ads_A {v['q']['ads298']['m']/A[nm]['ads_co2']:.2f} · q323/ads_B {v['q']['ads323']['m']/B[nm]['ads_co2']:.2f}")
def rank(T,key,skey,title):
    cn=T['−CN']; print('  '+title+': −CN − 구조 =', {nm:f"{cn[key]['m']-T[nm][key]['m']:+.3f} = {units(cn[key],T[nm][key]):+.2f} 단위 ({(cn[key]['m']-T[nm][key]['m'])/math.hypot(cn[skey],T[nm][skey]):+.2f} σ)" for nm in T if nm!='−CN'})
rank(ALL,'wc298','s298','§2 그대로(전 행 합침) 298 K'); rank(ALL,'wc323','s323','§2 그대로(전 행 합침) 323 K')
# §6 두 묶음 대조
LAP=block({'laptop','laptop2','hkhome'},'기본 54'); HK2=block({'hkhome2'},'추가 18')
print('  §6 두 묶음 대조(기본 묶음 대 hkhome2):')
for nm in ('모체','−CN'):
    for c in CN: print(f"    {nm} {c}: {LAP[nm]['q'][c]['m']:.3f} ± {LAP[nm]['q'][c]['pm']:.3f} 대 {HK2[nm]['q'][c]['m']:.3f} ± {HK2[nm]['q'][c]['pm']:.3f} → {units(LAP[nm]['q'][c],HK2[nm]['q'][c]):+.2f} 단위")
    for k in ('wc298','wc323'): print(f"    {nm} {k}: {LAP[nm][k]['m']:.3f} ± {LAP[nm][k]['pm']:.3f} 대 {HK2[nm][k]['m']:.3f} ± {HK2[nm][k]['pm']:.3f} → {units(LAP[nm][k],HK2[nm][k]):+.2f} 단위")
print('  묶음별 −CN − 모체: 298 K 기본 %+.3f (%+.2f 단위) · hkhome2 %+.3f (%+.2f 단위) | 323 K 기본 %+.3f (%+.2f) · hkhome2 %+.3f (%+.2f)'%(
    LAP['−CN']['wc298']['m']-LAP['모체']['wc298']['m'], units(LAP['−CN']['wc298'],LAP['모체']['wc298']), HK2['−CN']['wc298']['m']-HK2['모체']['wc298']['m'], units(HK2['−CN']['wc298'],HK2['모체']['wc298']),
    LAP['−CN']['wc323']['m']-LAP['모체']['wc323']['m'], units(LAP['−CN']['wc323'],LAP['모체']['wc323']), HK2['−CN']['wc323']['m']-HK2['모체']['wc323']['m'], units(HK2['−CN']['wc323'],HK2['모체']['wc323'])))
# §6 대로: 298 K 는 합치지 않고 묶음별 — 기본 묶음(여섯 다 n=3 · 같은 묶음) 안의 순위와, hkhome2 의 −CN · 모체를 기본 묶음의 나머지 넷과 견준 값
rank(LAP,'wc298','s298','기본 묶음(여섯 다 n 3) 298 K'); rank(LAP,'wc323','s323','기본 묶음 323 K')
print('  hkhome2 묶음의 −CN 대 기본 묶음 넷(298 K):', {nm:f"{units(HK2['−CN']['wc298'],LAP[nm]['wc298']):+.2f}" for nm in ('−Cl','−NO₂','−CH₃','−Br')}, '· hkhome2 모체 대 넷:', {nm:f"{units(HK2['모체']['wc298'],LAP[nm]['wc298']):+.2f}" for nm in ('−Cl','−NO₂','−CH₃','−Br')})
# 실행 하나씩의 값(−CN · 모체 ads298)
for t,nm in OUR[:2]: print(f"  {nm} ads298 실행별:", [(r['_m'],r['rep'],round(r['N_CO2'],3),round(r['N_CO2_err'],3)) for r in rows if r['tag']==t and r['condition']=='ads298'])
# (3) 방향: 물 때문에 줄어든 비율 순서
red={nm:1-ALL[nm]['q']['ads298']['m']/A[nm]['ads_co2'] for _,nm in OUR}; print('  298 K 흡착 CO₂ 감소율(1 − q/ads_A) 큰 순:', [(k,round(v,3)) for k,v in sorted(red.items(),key=lambda x:-x[1])], '· 물 친화 순서 −Br < −Cl < −CH₃ < 모체 < −NO₂ < −CN')
print('  물 mol/kg(셀당 8 고정):', {nm:round(st.mean(r['N_H2O'] for r in rows if r['tag']==t),3) for t,nm in OUR})
out['N']=dict(all=ALL, base=LAP, extra=HK2, pooled_sd=psd)
json.dump(out, open(os.path.join(HERE,'MAGI-007_synth2_cloud.json'),'w'), indent=1, ensure_ascii=False, default=str)
