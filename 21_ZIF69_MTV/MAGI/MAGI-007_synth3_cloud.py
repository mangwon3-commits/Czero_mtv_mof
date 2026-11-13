"""11-13 오후 — N 보강(물 수 고정 298 K 흡착 12행) · K″(같은 물 자리 출발 떼기 스캔). 등록 ASSIGN_N2_KPP_20261113.md 의 읽는 법 그대로. 종합자 자기 코드 · 원자료 JSON 만."""
import json, glob, os, math, statistics as st
HERE=os.path.dirname(os.path.abspath(__file__)); R=os.path.dirname(HERE); out={}
# ---------- N 보강
rows=[]; meta={}
for f in sorted(glob.glob(os.path.join(R,'results_fixedwater_wc_*.json'))):
    d=json.load(open(f)); assert d['complete'] is True and d['runner_md5'].startswith('0ed029a4') and not d['smoke'] and (d['protocol']['init'],d['protocol']['cycles'])==(5000,15000),f
    meta[d['machine']]=[c[0] for c in d['protocol']['conditions']]
    for r in d['rows']: r['_m']=d['machine']; rows.append(r)
assert set(meta)=={'hkhome','hkhome2','hkhome3','laptop','laptop2','laptop2b'} and meta['hkhome3']==['ads298'] and meta['laptop2b']==['ads298']
assert len(rows)==84 and all(r['status']=='ok' and r['finished'] and r['returncode']==0 and r['net_charge_ok'] and not r['stderr_not_found'] and r['water_per_cell']==8.0 and r['n_water_fixed']==48 for r in rows)
assert len({r['seed'] for r in rows})==84
def cell(t,c,mach=None):
    rr=[r for r in rows if r['tag']==t and r['condition']==c and (mach is None or r['_m'] in mach)]
    v=[r['N_CO2'] for r in rr]; e=[r['N_CO2_err'] for r in rr]; return dict(n=len(v), m=st.mean(v), pm=st.mean(e)/math.sqrt(len(v)), sd=st.stdev(v))
P298=cell('e22_parent','ads298'); C298=cell('e24i_cn_open','ads298'); P373=cell('e22_parent','des373'); C373=cell('e24i_cn_open','des373')
assert (P298['n'],C298['n'],P373['n'],C373['n'])==(12,12,6,6)
D=(C298['m']-C373['m'])-(P298['m']-P373['m']); pm=math.sqrt(sum(x['pm']**2 for x in (C298,P298,C373,P373))); sg=math.sqrt(sum(x['sd']**2/x['n'] for x in (C298,P298,C373,P373)))
print('=== N 보강  물 수 고정 298 K · 모체 · −CN 12행씩(행 84 · 표지 전부 통과 · 씨앗 84 고유 · 실행기 0ed029a4)')
for nm,x in (('모체 298 K',P298),('−CN 298 K',C298),('모체 373 K',P373),('−CN 373 K',C373)): print(f"  {nm}: n {x['n']} 평균 {x['m']:.4f} ± {x['pm']:.4f} · 표본 SD {x['sd']:.4f}")
print(f"  WC_N,298: −CN {C298['m']-C373['m']:.4f} · 모체 {P298['m']-P373['m']:.4f} · D = {D:+.4f} ({D/(P298['m']-P373['m']):+.1%})")
print(f"  등록 자 ± {pm:.4f} → {D/pm:+.2f} 단위(문턱 1.5) · 반복 SD 자 σ {sg:.4f} → {D/sg:+.2f} σ(문턱 2.0) → " + ('둘 다 넘음: "물 수 고정 298 K 에서도 −CN 이 모체보다 위"' if (D/pm>1.5 and D/sg>2.0) else '구별되지 않음'))
B=('laptop','hkhome2','hkhome3','laptop2b'); bd=[]
for m in B:
    p=cell('e22_parent','ads298',{m}); c=cell('e24i_cn_open','ads298',{m}); bd.append(c['m']-p['m']-(C373['m']-P373['m'])); print(f"  묶음 {m:9s} 모체 {p['m']:.3f} (SD {p['sd']:.3f}) · −CN {c['m']:.3f} (SD {c['sd']:.3f}) · 흡착 차 {c['m']-p['m']:+.3f} · 회수량 차 {bd[-1]:+.3f}")
print(f"  (서술 · 등록 밖) 묶음을 낱개로 보면 회수량 차 넷 평균 {st.mean(bd):+.3f} · SD {st.stdev(bd):.3f} · t = {st.mean(bd)/(st.stdev(bd)/2):.2f}(자유도 3)")
for t,nm in (('e22_parent','모체'),('e24i_cn_open','−CN')):
    a=cell(t,'ads298',{'hkhome2','hkhome3'}); b=cell(t,'ads298',{'laptop','laptop2b'}); print(f"  (서술 · 등록 밖) {nm}: HKHOME 6행 {a['m']:.3f} · 랩탑 · laptop2 6행 {b['m']:.3f} · 차 {a['m']-b['m']:+.3f} ({(a['m']-b['m'])/math.sqrt(a['sd']**2/6+b['sd']**2/6):+.2f} σ)")
S2=json.load(open(os.path.join(HERE,'MAGI-007_synth2_cloud.json')))['N']['all']
wcn=dict(m=C298['m']-C373['m'], pm=math.hypot(C298['pm'],C373['pm'])); wpn=dict(m=P298['m']-P373['m'], pm=math.hypot(P298['pm'],P373['pm']))
u=lambda a,b:(a['m']-b['m'])/math.hypot(a['pm'],b['pm'])
print('  298 K 나머지 넷 대비(넷은 n 3 그대로): −CN', {k:round(u(wcn,S2[k]['wc298']),2) for k in ('−Cl','−NO₂','−CH₃','−Br')}, '· 모체', {k:round(u(wpn,S2[k]['wc298']),2) for k in ('−Cl','−NO₂','−CH₃','−Br')})
out['N_boost']=dict(P298=P298,C298=C298,P373=P373,C373=C373,D=D,pm=pm,sigma=sg,units=D/pm,nsigma=D/sg,batch_wc_diff=dict(zip(B,bd)))
# ---------- K″
d=json.load(open(os.path.join(R,'results_znbdt_kpp_xtb_hkhome.json'))); CL=d['clusters']
assert d['counts']=={'states_run':90,'states_with_value':90,'clusters':9,'states_expected':90} and d['copy_of']['md5'].startswith('de1c721b')
assert all(v['markers_ok'] and v['converged'] and v['normal_termination'] for c in CL.values() for v in c['states'].values())
T={}
print('=== K″  같은 물 자리 출발 떼기 스캔(kJ/mol · 그 출발 상태 기준 · 클러스터 9 · 상태 90 · 표지 통과)')
for n,c in CL.items():
    T[n]={}
    for s_ in ('fNb','hbU'):
        s=c['states']; dE={p:s[f'kpp_{s_}_p{p}']['dE_kJmol'] for p in ('04','08','12','16')}; g=s[f'kpp_{s_}_p12']['geometry']; gr=s[f'kpp_{s_}_p12_release']['geometry']['carboxylate']['sub']
        T[n][s_]=dict(dE=dE, o12=[round(x,2) for x in g['carboxylate']['sub']['d_Zn_O_A']], ow12=round(g['d_Zn_Ow_A'],2), cn12=g['cn_Zn_within_2p5A'], release=('되붙음' if gr['attached_2p3'] else ('떨어진 채' if gr['detached_2p6'] else '사이')))
        print(f"  {n:20s} {s_} {[round(dE[p],1) for p in ('04','08','12','16')]} · +1.2 점 치환 쪽 O {T[n][s_]['o12']} Zn–O_w {T[n][s_]['ow12']} 배위수 {T[n][s_]['cn12']} · 풀기 {T[n][s_]['release']}")
rep=[('e22_parent_zn1','e22_parent_zn2'),('e24i_cn_open_zn1','e24i_cn_open_zn2')]
eps={s_:max(4,2*max(abs(T[a][s_]['dE'][p]-T[b][s_]['dE'][p]) for a,b in rep for p in ('12','16'))) for s_ in ('fNb','hbU')}; print('  ε″', eps)
p=T['e22_parent_zn1']; res={}
for n in CL:
    if 'parent' in n: continue
    v={f'{s_}_p{pt}':T[n][s_]['dE'][pt]-p[s_]['dE'][pt] for s_ in ('fNb','hbU') for pt in ('12','16')}
    ver='떼기 쉽게' if all(x< -eps[k[:3]] for k,x in v.items()) else ('떼기 어렵게' if all(x> eps[k[:3]] for k,x in v.items()) else '치환기 효과로 쓰지 않음'); res[n]=dict(dd=v,verdict=ver)
    print(f"  {n:20s} ΔΔ " + ' · '.join(f"{k} {x:+.1f}" for k,x in v.items()) + f" → {ver}")
print(f"  모체 fNb 출발 +1.2 점 {p['fNb']['dE']['12']:.1f} 대 K′ 의 −NO₂ 30.1 → 차 {p['fNb']['dE']['12']-30.1:+.1f} (ε″ {eps['fNb']}) → " + ('K′ 의 −NO₂ 값은 경로 차이였음' if abs(p['fNb']['dE']['12']-30.1)<=eps['fNb'] else '경로 차이로 설명 안 됨'))
out['Kpp']=dict(T=T,eps=eps,res=res)
json.dump(out, open(os.path.join(HERE,'MAGI-007_synth3_cloud.json'),'w'), indent=1, ensure_ascii=False)
