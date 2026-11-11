"""11-11 종합 — A(298 K WC 6씨앗) · B(323 K WC 6씨앗) · C(CoRE 22 S_humid 298) · D/G(CoRE 22 WC 298) · F(CoRE S_humid 323 · 도착분). 종합자 자기 코드 · 원자료 JSON 만."""
import json, glob, os, re, math, statistics as st, itertools, sys
HERE=os.path.dirname(os.path.abspath(__file__)); R=os.path.dirname(HERE)
L=lambda p: json.load(open(os.path.join(R,p)))
def ms(vals, errs):
    n=len(vals); return dict(m=st.mean(vals), pm=st.mean(errs)/math.sqrt(n), sd=(st.stdev(vals) if n>1 else float('nan')), n=n)
def units(a,b): return (a['m']-b['m'])/math.hypot(a['pm'],b['pm'])
OUR=[('e22_parent','모체'),('e24i_cn_open','−CN'),('e24i_no2_open','−NO₂'),('e24i_cl_open','−Cl'),('e24i_ch3_open','−CH₃'),('e24i_br_open','−Br')]
out={}
# ---------- A: 298 K WC
A1={'e22_parent':'v3w_humid_wc/humid_working_capacity_w2_e22parent_laptop.json','e24i_cn_open':'v3w_humid_wc/humid_working_capacity_w2_e24i_cn_open_junseok.json','e24i_no2_open':'v3w_humid_wc/humid_working_capacity_w2_e24i_no2_open_laptop2.json',
    'e24i_cl_open':'v3w_humid_wc/humid_working_capacity_w2_e24i_cl_open_junseok.json','e24i_ch3_open':'v3w_humid_wc/humid_working_capacity_w2_e24i_ch3_open_laptop.json','e24i_br_open':'v3w_humid_wc/humid_working_capacity_w2_e24i_br_open_hkhome.json'}
def wcrows(d, base): return [r for r in d['rows'] if r['name'].startswith(base)]
def wcstat(rows):
    o={}
    for k in ('tsa','vsa'): o[k]=ms([r['working_capacity'][k]['value'] for r in rows],[r['working_capacity'][k]['err'] for r in rows])
    o['ads_co2']=st.mean(r['loadings']['ads']['CO2']['mol_per_kg'] for r in rows); o['tsa_res']=st.mean(r['loadings']['tsa']['CO2']['mol_per_kg'] for r in rows)
    o['ads_h2o']=st.mean(r['loadings']['ads']['water']['mol_per_kg'] for r in rows); o['regen']=1-o['tsa_res']/o['ads_co2']; return o
A={}
print('=== A  298 K 습윤 TSA 회수량 6씨앗')
for base,nm in OUR:
    f2=glob.glob(os.path.join(R,f'v3w_humid_wc/humid_working_capacity_w2_{base}_s456_*.json')); assert len(f2)==1,(base,f2)
    d1=L(A1[base]); d2=json.load(open(f2[0])); r1=wcrows(d1,base); r2=wcrows(d2,base); assert len(r1)==3 and len(r2)==3,(base,len(r1),len(r2))
    assert d1['p_h2o_Pa']==d2['p_h2o_Pa']==2852.1 and [(c['T_K'],c['p_co2_Pa']) for c in d2['conditions']]==[(298.0,15000.0),(373.0,15000.0),(298.0,5000.0)]
    s2=glob.glob(os.path.join(R,f'results_{base}_s456_humid_summary_*.json')); assert len(s2)==1,(base,s2); S2=json.load(open(s2[0])); aud=S2['audit']
    ok=all(x['ok'] and x['finished'] and x['returncode']==0 for x in aud) and len(aud)==9; seeds2=[x['seed'] for x in aud]
    s1=glob.glob(os.path.join(R,f'results_e24i_{base}_humid_summary_*.json')); seeds1=[x['seed'] for f in s1 for x in json.load(open(f))['audit']]
    blk={x['blockpockets_in_input'] for x in aud}
    a=wcstat(r1); b=wcstat(r2); six=wcstat(r1+r2); six['halves']=units(b['tsa'],a['tsa']); six['audit_ok']=ok; six['seeds_distinct']=len(set(seeds2))==9; six['overlap']=len(set(seeds1)&set(seeds2)); six['blk_lines']=sorted(blk)
    A[nm]=six
    print(f"  {nm:5s} s1-3 {a['tsa']['m']:.4f}±{a['tsa']['pm']:.4f} | s4-6 {b['tsa']['m']:.4f}±{b['tsa']['pm']:.4f} | 묶음 차 {six['halves']:+.2f} | 6: {six['tsa']['m']:.4f} ± {six['tsa']['pm']:.4f} (SD {six['tsa']['sd']:.4f}) | VSA {six['vsa']['m']:.3f} | ads {six['ads_co2']:.3f} 잔류 {six['tsa_res']:.3f} 재생 {six['regen']*100:.1f}% 물 {six['ads_h2o']:.3f} | 감사 {ok} 씨앗고유 {six['seeds_distinct']} 겹침 {six['overlap']}(옛 {len(seeds1)}) 막음줄 {six['blk_lines']}")
oa=sorted(A,key=lambda k:-A[k]['tsa']['m'])
print('  순서:', ' > '.join(f"{k} {A[k]['tsa']['m']:.3f}" for k in oa)); print('  쌍 거리:', {f'{x}|{y}':round(units(A[x]['tsa'],A[y]['tsa']),2) for x,y in itertools.combinations(oa,2)})
out['A']=A
# ---------- B: 323 K WC
B1={'e22_parent':'v3w_humid_wc_323/humid_wc_323_znbdt_parent_cn_laptop.json','e24i_cn_open':'v3w_humid_wc_323/humid_wc_323_znbdt_parent_cn_laptop.json','e24i_no2_open':'v3w_humid_wc_323/humid_wc_323_znbdt_no2_laptop.json',
    'e24i_cl_open':'v3w_humid_wc_323/humid_wc_323_znbdt_laptop.json','e24i_ch3_open':'v3w_humid_wc_323/humid_wc_323_znbdt_laptop.json','e24i_br_open':'v3w_humid_wc_323/humid_wc_323_znbdt_laptop.json'}
B2={'e22_parent':'v3w_humid_wc_323/humid_wc_323_znbdt_cn_parent_ch3_s456_laptop2.json','e24i_cn_open':'v3w_humid_wc_323/humid_wc_323_znbdt_cn_parent_ch3_s456_laptop2.json','e24i_ch3_open':'v3w_humid_wc_323/humid_wc_323_znbdt_cn_parent_ch3_s456_laptop2.json',
    'e24i_no2_open':'v3w_humid_wc_323/humid_wc_323_znbdt_no2_s456_laptop.json','e24i_cl_open':'v3w_humid_wc_323/humid_wc_323_znbdt_cl_s456_laptop2.json','e24i_br_open':'v3w_humid_wc_323/humid_wc_323_znbdt_br_s456_laptop.json'}
Bq={}
print('=== B  323 K 습윤 TSA 회수량 6씨앗')
for base,nm in OUR:
    d1=L(B1[base]); d2=L(B2[base]); r1=wcrows(d1,base); r2=wcrows(d2,base); assert len(r1)==3 and len(r2)==3,(base,len(r1),len(r2))
    for d in (d1,d2):
        assert d['complete'] and d['p_h2o_Pa']==11114.1 and [c['T_K'] for c in d['conditions']]==[323.0,373.0,323.0]
        assert all(v['ok'] for k,v in d['header_gate'].items() if base in k)
    s1=[v for r in r1 for v in r['raspa_seed'].values()]; s2=[v for r in r2 for v in r['raspa_seed'].values()]
    a=wcstat(r1); b=wcstat(r2); six=wcstat(r1+r2); six['halves']=units(b['tsa'],a['tsa']); six['seeds_ok']=(len(set(s1+s2))==18)
    R6=six['tsa']['m']/A[nm]['tsa']['m']; six['R']=R6; six['R_pm']=R6*math.hypot(six['tsa']['pm']/six['tsa']['m'], A[nm]['tsa']['pm']/A[nm]['tsa']['m'])
    Bq[nm]=six
    print(f"  {nm:5s} s1-3 {a['tsa']['m']:.4f}±{a['tsa']['pm']:.4f} | s4-6 {b['tsa']['m']:.4f}±{b['tsa']['pm']:.4f} | 묶음 차 {six['halves']:+.2f} | 6: {six['tsa']['m']:.4f} ± {six['tsa']['pm']:.4f} (SD {six['tsa']['sd']:.4f}) | VSA {six['vsa']['m']:.3f} | ads {six['ads_co2']:.3f} 재생 {six['regen']*100:.1f}% 물 {six['ads_h2o']:.3f} | R {six['R']:.3f} ± {six['R_pm']:.3f} | 씨앗 18 고유 {six['seeds_ok']}")
ob=sorted(Bq,key=lambda k:-Bq[k]['tsa']['m'])
print('  순서:', ' > '.join(f"{k} {Bq[k]['tsa']['m']:.3f}" for k in ob)); print('  쌍 거리:', {f'{x}|{y}':round(units(Bq[x]['tsa'],Bq[y]['tsa']),2) for x,y in itertools.combinations(ob,2)})
print('  R 쌍(−CN 대 나머지):', {k:round((Bq['−CN']['R']-Bq[k]['R'])/math.hypot(Bq['−CN']['R_pm'],Bq[k]['R_pm']),2) for k in ob if k!='−CN'})
out['B']=Bq
# ---------- our six S_humid (298 · 323) 6씨앗
def srows(files, base): return [r for f in files for r in L(f)['rows'] if r['base']==base]
def sstat(rows, yr):
    S=[(r['N_CO2']/r['N_N2'])/yr for r in rows]; E=[s*math.hypot(r['N_CO2_err']/r['N_CO2'], r['N_N2_err']/r['N_N2']) for r,s in zip(rows,S)]
    o=ms(S,E); o['N_H2O']=st.mean(r['N_H2O'] for r in rows); o['N_CO2']=st.mean(r['N_CO2'] for r in rows); o['N_N2']=st.mean(r['N_N2'] for r in rows); o['n2rel_max']=max(r['N_N2_err']/r['N_N2'] for r in rows); return o
E298=['results_znbdt_e_humid3_laptop2.json','results_znbdt_e_humid3_s456_laptop2.json','results_znbdt_e_humid3_cn_s456_laptop.json','results_znbdt_e_humid3_s456_hkhome.json','results_znbdt_no2_e_humid3_hkhome.json','results_znbdt_no2_e_humid3_laptop2.json']
E323=['results_znbdt_e_humid3_323_laptop2.json','results_znbdt_e_humid3_323_hkhome.json']
Y298=0.15/0.821479; Y323=0.15/0.738859
S298={nm:sstat(srows(E298,b),Y298) for b,nm in OUR}; S323={nm:sstat(srows(E323,b),Y323) for b,nm in OUR}
assert all(v['n']==6 for v in S298.values()) and all(v['n']==6 for v in S323.values())
out['S298_ours']=S298; out['S323_ours']=S323
# ---------- CoRE 22 목록 · 건조 S_mix
_ann=L('core_pop_annotated.json'); ann={r['key']:r for r in (_ann if isinstance(_ann,list) else _ann['rows'])}
blocks=L('results_core22_blocks_laptop.json')['summary']
dry={}
for line in open(os.path.join(os.path.dirname(R),'23_SCREENING','FINAL_RANKING_SMIX_20260930.md'),encoding='utf-8'):
    m=re.match(r'\|\s*\d+\s*\|[^|]*\|\s*(\d{4}) (\w+) (\w+) (\d) (ASR|FSR) (\d+)\s*\|\s*CoRE\s*\|[^|]*\|\s*\*\*([\d.]+) ± ([\d.]+)\*\*',line)
    if m: dry[f'{m.group(1)}[{m.group(2)}][{m.group(3)}]{m.group(4)}[{m.group(5)}]{m.group(6)}']=(float(m.group(7)),float(m.group(8)))
assert len(dry)==22,len(dry)
stem=lambda k: ann[k]['file'][:-4]
def tag(k):
    b=blocks[k]; t=[]
    if ann[k].get('formal_charge_nonzero') is None: t.append('fc미상')
    if b['spheres_1.82']>=100: t.append('N₂경계')
    if 'Cd' in k: t.append('막음큼')
    return ','.join(t)
# ---------- C: CoRE S_humid 298
crow=[r for f in ('results_core22_e_humid3_hkhome.json','results_core22_e_humid3_laptop.json') for r in L(f)['rows']]
assert len(crow)==66 and all(r['ok'] and r['finished'] and r['returncode']==0 and r['component2_N2_in_output'] for r in crow) and len({r['seed'] for r in crow})==66
assert {json.dumps(r['input_molfractions'],sort_keys=True) for r in crow}=={json.dumps({"CO2":"0.150000","N2":"0.821479","water":"0.028521"},sort_keys=True)}
C={}
for k in dry:
    rows=[r for r in crow if r['core_key']==k]; assert len(rows)==3,(k,len(rows))
    o=sstat(rows,Y298); o['blocked']=rows[0]['blocked_components']; o['dry']=dry[k][0]; o['ret']=o['m']/dry[k][0]; o['ret_pm']=o['ret']*math.hypot(o['pm']/o['m'],dry[k][1]/dry[k][0]); o['tag']=tag(k); C[k]=o
out['C']=C
print('=== C  CoRE 22 습윤 3성분 선택도 298 K (3씨앗) + 우리 6(6씨앗)')
allS={**{k:v for k,v in C.items()}, **{nm:S298[nm] for _,nm in OUR}}
for k in sorted(allS,key=lambda k:-allS[k]['m']):
    v=allS[k]
    if k in C: print(f"  {k:24s} {v['m']:7.2f} ± {v['pm']:5.2f} (SD {v['sd']:5.2f}) 건조 {v['dry']:6.1f} 유지비 {v['ret']:.3f}±{v['ret_pm']:.3f} 물 {v['N_H2O']:.3f} CO₂ {v['N_CO2']:.3f} N₂±max {v['n2rel_max']:.2f} 막음 {'/'.join(v['blocked']) or '—'} {v['tag']}")
    else: print(f"  ** {k:21s} {v['m']:7.2f} ± {v['pm']:5.2f} (SD {v['sd']:5.2f}) 물 {v['N_H2O']:.3f} CO₂ {v['N_CO2']:.3f}")
cmpS={}
for _,nm in OUR:
    ab=sum(1 for k in C if units(S298[nm],C[k])>1.5); be=sum(1 for k in C if units(S298[nm],C[k])<-1.5); cmpS[nm]=(ab, 22-ab-be, be)
print('  우리 행이 CoRE 22 보다 1.5 단위 위 / 구별 불가 / 아래:', cmpS); out['C_cmp']=cmpS
print('  유지비<1(1.5 단위 넘게):', sum(1 for k in C if (C[k]['ret']-1)/C[k]['ret_pm']<-1.5), '· 유지비 점추정<1:', sum(1 for k in C if C[k]['ret']<1), '/22 · 중앙', round(st.median(C[k]['ret'] for k in C),3))
# ---------- G(+D): CoRE WC 298
G={}
for k in dry:
    f=glob.glob(os.path.join(R,f'v3w_humid_wc/humid_working_capacity_w2_core22_{stem(k)}_*.json'))
    if f:
        d=json.load(open(f[0])); s=glob.glob(os.path.join(R,f'results_core22_{stem(k)}_humid_summary_*.json')); src='G'
    else:
        assert k=='2017[Zn][dia]3[FSR]1'; d=L('v3w_humid_wc/humid_working_capacity_w2_core_zn_dia_fsr1_laptop2.json'); s=[os.path.join(R,'results_core_zn_dia_fsr1_humid_summary_laptop2.json')]; src='D'
    assert len(s)==1,(k,s); S=json.load(open(s[0])); aud=S['audit']; rows=d['rows']; assert len(rows)==3 and len(aud)==9,(k,len(rows),len(aud))
    assert d['p_h2o_Pa']==2852.1 and [(c['T_K'],c['p_co2_Pa']) for c in d['conditions']]==[(298.0,15000.0),(373.0,15000.0),(298.0,5000.0)],k
    ok=all(x['ok'] and x['finished'] and x['returncode']==0 for x in aud); o=wcstat(rows); o['audit_ok']=ok; o['seeds']=[x['seed'] for x in aud]; o['src']=src; o['tag']=tag(k)
    o['blocked']=sorted({c for x in aud for c in (x.get('blocked_components') or [g for g,b in (x.get('block') or {}).items() if b.get('n_blocked')])})
    G[k]=o
allseeds=[s for k in G for s in G[k]['seeds']]; print('=== G(+D)  CoRE 22 습윤 TSA 회수량 298 K (3씨앗) + 우리 6(6씨앗) · 감사 전부 ok', all(G[k]['audit_ok'] for k in G), '· 씨앗', len(allseeds), '고유', len(set(allseeds)))
allW={**G, **{nm:A[nm] for _,nm in OUR}}
for k in sorted(allW,key=lambda k:-allW[k]['tsa']['m']):
    v=allW[k]; pre='  ** ' if k not in G else '  '
    print(f"{pre}{k:24s} WC_TSA {v['tsa']['m']:.3f} ± {v['tsa']['pm']:.3f} (SD {v['tsa']['sd']:.3f}) VSA {v['vsa']['m']:.3f} ads {v['ads_co2']:.3f} 잔류 {v['tsa_res']:.3f} 재생 {v['regen']*100:5.1f}% 물 {v['ads_h2o']:.3f} " + (f"{v['src']} 막음 {'/'.join(v['blocked']) or '—'} {v['tag']}" if k in G else ''))
cmpW={}
for _,nm in OUR:
    ab=[k for k in G if units(A[nm]['tsa'],G[k]['tsa'])>1.5]; be=[k for k in G if units(A[nm]['tsa'],G[k]['tsa'])<-1.5]; cmpW[nm]=(len(ab),22-len(ab)-len(be),len(be))
print('  우리 행이 CoRE 22 보다 1.5 단위 위 / 구별 불가 / 아래:', cmpW); out['G']={k:{kk:vv for kk,vv in v.items() if kk!='seeds'} for k,v in G.items()}; out['G_cmp']=cmpW
print('  −CN 보다 1.5 단위 넘게 위인 CoRE:', [(k,round(G[k]['tsa']['m'],3),round(units(G[k]['tsa'],A['−CN']['tsa']),2)) for k in G if units(G[k]['tsa'],A['−CN']['tsa'])>1.5])
print('  −CN 과 구별 불가:', [(k,round(G[k]['tsa']['m'],3),round(units(G[k]['tsa'],A['−CN']['tsa']),2)) for k in G if abs(units(G[k]['tsa'],A['−CN']['tsa']))<=1.5])
print('  WC_TSA ≥ 2.0 인 CoRE 수:', sum(1 for k in G if G[k]['tsa']['m']>=2.0))
dk='2017[Zn][dia]3[FSR]1'; print(f"  D: CoRE 판 모체 WC_TSA {G[dk]['tsa']['m']:.4f} ± {G[dk]['tsa']['pm']:.4f} 대 우리 모체 {A['모체']['tsa']['m']:.4f} ± {A['모체']['tsa']['pm']:.4f} → {units(G[dk]['tsa'],A['모체']['tsa']):+.2f} 단위 · S_humid {C[dk]['m']:.2f} ± {C[dk]['pm']:.2f} 대 {S298['모체']['m']:.2f} ± {S298['모체']['pm']:.2f} → {units(C[dk],S298['모체']):+.2f} 단위")
# ---------- F: 도착분
frow=[r for f in glob.glob(os.path.join(R,'results_core22_e_humid3_323_*.json')) if not f.endswith('_audit.json') for r in json.load(open(f))['rows']]
assert all(r['ok'] and r['finished'] and r['returncode']==0 for r in frow) and len({r['seed'] for r in frow})==len(frow)
assert {json.dumps(r['input_molfractions'],sort_keys=True) for r in frow}=={json.dumps({"CO2":"0.150000","N2":"0.738859","water":"0.111141"},sort_keys=True)}
F={}
for k in dry:
    rows=[r for r in frow if r['core_key']==k]
    if len(rows)==3:
        o=sstat(rows,Y323); o['Tratio']=o['m']/C[k]['m']; o['tag']=tag(k); F[k]=o
print(f'=== F  CoRE S_humid,323 도착 {len(F)}/22 구조 ({len(frow)}행) + 우리 6(6씨앗)')
allF={**F, **{nm:S323[nm] for _,nm in OUR}}
for k in sorted(allF,key=lambda k:-allF[k]['m']):
    v=allF[k]; pre='  ** ' if k not in F else '  '
    print(f"{pre}{k:24s} {v['m']:6.2f} ± {v['pm']:4.2f} (SD {v['sd']:4.2f}) 물 {v['N_H2O']:.3f} CO₂ {v['N_CO2']:.3f}" + (f" 온도 비 {v['Tratio']:.3f} N₂±max {v['n2rel_max']:.2f} {v['tag']}" if k in F else f" 온도 비 {v['m']/S298[k]['m']:.3f}"))
out['F']=F
json.dump(out, open(os.path.join(HERE,'MAGI-007_core22_synth_cloud.json'),'w'), indent=1, ensure_ascii=False, default=str)
