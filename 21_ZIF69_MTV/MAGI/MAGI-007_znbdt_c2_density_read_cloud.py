"""종합자 서술용 — ZNBDT-C2 후속 #1 밀도 격자 읽기 (등록 FOLLOWUP §1 · 문턱 없음 · 서술만). 자기 코드(numpy)."""
import gzip, json, sys, os, numpy as np
D = sys.argv[1]            # scratchpad/dens
CIF = sys.argv[2]          # charged_v3 dir
COV = {'C':0.76,'N':0.71,'O':0.66,'S':1.05,'Zn':1.22,'H':0.31}
def read_cif(p):
    cell={}; sym=[]; fr=[]; cols=[]; inloop=False
    for line in open(p):
        t=line.split()
        if not t: continue
        if t[0].startswith('_cell_'): cell[t[0]]=float(t[1]); continue
        if t[0]=='loop_': inloop=True; cols=[]; continue
        if inloop and t[0].startswith('_atom_site'): cols.append(t[0]); continue
        if inloop and cols and '_atom_site_fract_x' in cols and not t[0].startswith('_') and len(t)>=len(cols):
            sym.append(t[cols.index('_atom_site_type_symbol')]); fr.append([float(t[cols.index('_atom_site_fract_'+k)]) for k in 'xyz'])
    a,b,c=cell['_cell_length_a'],cell['_cell_length_b'],cell['_cell_length_c']
    al,be,ga=[np.radians(cell['_cell_angle_'+k]) for k in ('alpha','beta','gamma')]
    v=np.sqrt(1-np.cos(al)**2-np.cos(be)**2-np.cos(ga)**2+2*np.cos(al)*np.cos(be)*np.cos(ga))
    M=np.array([[a,0,0],[b*np.cos(ga),b*np.sin(ga),0],[c*np.cos(be),c*(np.cos(al)-np.cos(be)*np.cos(ga))/np.sin(ga),c*v/np.sin(ga)]])
    return np.array(sym), np.array(fr), M
def read_vtk(p):
    with gzip.open(p,'rt') as f:
        hdr=[next(f) for _ in range(10)]
        dims=[int(x) for x in [h for h in hdr if h.startswith('DIMENSIONS')][0].split()[1:]]
        vals=np.array([float(x) for x in f.read().split()])
    assert vals.size==dims[0]*dims[1]*dims[2], (vals.size, dims)
    return vals, dims
def super_positions(sym, fr, M, reps=(1,2,3)):
    S=np.diag(reps).astype(float); Ms=S@M      # supercell matrix (rows = a,b,c)
    pos=[]; syms=[]
    for i in range(reps[0]):
        for j in range(reps[1]):
            for k in range(reps[2]):
                f=(fr+np.array([i,j,k]))/np.array(reps); pos.append(f@Ms); syms+=list(sym)
    return np.array(syms), np.vstack(pos), Ms
def mic(dv, Ms):
    inv=np.linalg.inv(Ms); f=dv@inv; f-=np.round(f); return f@Ms
def min_dist_grid(centers, atoms, Ms, chunk=20000):
    out=np.empty(len(centers))
    for s in range(0,len(centers),chunk):
        c=centers[s:s+chunk]; d=np.full(len(c),1e9)
        for A in atoms:
            dv=mic(c-A, Ms); d=np.minimum(d, np.linalg.norm(dv,axis=1))
        out[s:s+chunk]=d
    return out
# --- structures
tags={'parent':'e22_parent_DDEC6.cif','cn':'e24i_cn_open_DDEC6.cif','ch3':'e24i_ch3_open_DDEC6.cif','apolarU':'znbdt_c2_apolarU_DDEC6mod.cif'}
dirs={'parent':'e22_parent__q_on','cn':'e24i_cn_open__q_on','ch3':'e24i_ch3_open__q_on','apolarU':'znbdt_c2_apolarU__q_on'}
res={r['name']:r for r in json.load(open(os.path.join(D,'results_znbdt_c2_density_laptop2.json')))['rows']}
N={'parent':res['e22_parent'],'cn':res['e24i_cn_open'],'ch3':res['e24i_ch3_open'],'apolarU':res['znbdt_c2_apolarU']}
struct={}
for k,f in tags.items():
    sym,fr,M=read_cif(os.path.join(CIF,f)); ssym,spos,Ms=super_positions(sym,fr,M); struct[k]=(ssym,spos,Ms,sym,fr,M)
Ms=struct['parent'][2]
# substituent heavy atoms: atoms of substituted CIF with no parent atom within 0.5 Å (supercell, mic), heavy only
def subst_atoms(k):
    ssym,spos,_,_,_,_=struct[k]; psym,ppos=struct['parent'][0],struct['parent'][1]
    ppos=ppos[psym!='H']                                   # 모체의 무거운 원자만과 견줌(치환기 첫 원자는 모체 H 자리 0.35 Å 곁에 옴)
    heavy=[i for i in range(len(ssym)) if ssym[i]!='H']
    out=[]
    for i in heavy:
        d=np.linalg.norm(mic(ppos-spos[i],Ms),axis=1)
        if d.min()>0.5: out.append(i)
    return out
SUB={k:subst_atoms(k) for k in ('cn','ch3','apolarU')}
for k,v in SUB.items(): print(k,'substituent heavy atoms',len(v), sorted(set(struct[k][0][v])))
# --- grids
G={}; dims=None
for k in tags:
    for g in ('CO2','N2'):
        vals,dims=read_vtk(os.path.join(D,dirs[k],'VTK','System_0',f'COMDensityProfile_{g}.vtk.gz'))
        G[(k,g)]=vals
nx,ny,nz=dims
# voxel centers under the two candidate orderings: VTK standard (x fastest) vs reversed
def centers(order):
    idx=np.arange(nx*ny*nz)
    if order=='x_fast': i=idx%nx; j=(idx//nx)%ny; kk=idx//(nx*ny)
    else: kk=idx%nz; j=(idx//nz)%ny; i=idx//(nz*ny)
    f=np.stack([(i+0.5)/nx,(j+0.5)/ny,(kk+0.5)/nz],axis=1); return f@Ms
fw_heavy=[struct['parent'][1][i] for i in range(len(struct['parent'][0])) if struct['parent'][0][i]!='H']
best=None
for order in ('x_fast','z_fast'):
    C=centers(order); w=G[('parent','CO2')]; top=np.argsort(w)[-3000:]
    dmin=min_dist_grid(C[top], fw_heavy, Ms)
    print(f'ordering {order}: top-3000 CO2 voxels — mean min dist to framework heavy atoms {dmin.mean():.2f} Å (pore → larger is right)')
    if best is None or dmin.mean()>best[1]: best=(order,dmin.mean())
order=best[0]; C=centers(order); print('chosen ordering', order)
# normalise to mol/kg per voxel
rho={}
for (k,g),v in G.items(): rho[(k,g)]=v/v.sum()*N[k][f'N_{g}']
# distance of every voxel to substituent heavy atoms (cn/apolarU share positions; ch3 own)
dist={}
for k in ('cn','ch3'):
    atoms=[struct[k][1][i] for i in SUB[k]]; dist[k]=min_dist_grid(C, atoms, Ms)
dist['apolarU']=dist['cn']
# nitrile N atoms only (cn) · methyl C (ch3)
nN=[struct['cn'][1][i] for i in SUB['cn'] if struct['cn'][0][i]=='N']; distN=min_dist_grid(C, nN, Ms)
shells=[(0,3.0),(3.0,4.5),(4.5,6.0),(6.0,99)]
print('\n=== N₂ 변화 Δρ = ρ(s) − ρ(모체) [mol/kg] — 치환기 무거운 원자까지의 거리 껍질별 합 (음 = 비움 · 양 = 채움)')
print(f"{'s':8s} {'ΔN_total':>9s} " + ' '.join(f"{a}-{b if b<99 else '∞'}Å".rjust(11) for a,b in shells) + '   | 비움만: 4.5 Å 안 비중')
for s in ('cn','apolarU','ch3'):
    d=rho[(s,'N2')]-rho[('parent','N2')]; tot=d.sum()
    cells=[d[(dist[s]>=a)&(dist[s]<b)].sum() for a,b in shells]
    neg=d.copy(); neg[neg>0]=0; near=neg[dist[s]<4.5].sum()/neg.sum() if neg.sum()!=0 else float('nan')
    print(f"{s:8s} {tot:+9.4f} " + ' '.join(f"{c:+11.4f}" for c in cells) + f"   | {near:5.2f}")
print('\n=== CO₂ 변화 Δρ = ρ(s) − ρ(모체) [mol/kg] — 같은 껍질')
print(f"{'s':8s} {'ΔN_total':>9s} " + ' '.join(f"{a}-{b if b<99 else '∞'}Å".rjust(11) for a,b in shells) + '   | 채움만: 4.5 Å 안 비중')
for s in ('cn','apolarU','ch3'):
    d=rho[(s,'CO2')]-rho[('parent','CO2')]; tot=d.sum()
    cells=[d[(dist[s]>=a)&(dist[s]<b)].sum() for a,b in shells]
    pos=d.copy(); pos[pos<0]=0; near=pos[dist[s]<4.5].sum()/pos.sum() if pos.sum()!=0 else float('nan')
    print(f"{s:8s} {tot:+9.4f} " + ' '.join(f"{c:+11.4f}" for c in cells) + f"   | {near:5.2f}")
print('\n=== 니트릴 N 원자 4.0 Å 안(cn 자리 · apolarU 같은 자리) 의 밀도 [mol/kg 몫] — 모체 대비')
for g in ('N2','CO2'):
    row=[]
    for s in ('parent','cn','apolarU','ch3'):
        row.append(rho[(s,g)][distN<4.0].sum())
    print(f"{g:4s} 모체 {row[0]:.4f} · cn {row[1]:.4f} ({row[1]/row[0]:.2f}×) · apolarU {row[2]:.4f} ({row[2]/row[0]:.2f}×) · ch3(같은 좌표) {row[3]:.4f} ({row[3]/row[0]:.2f}×)")
print('\n=== 자기 치환기 끝 원자 4.0 Å 안의 밀도 — 모체 같은 좌표 대비 (cn · apolarU = 니트릴 N 자리 · ch3 = 메틸 C 자리)')
endatoms={'cn':nN,'apolarU':nN,'ch3':[struct['ch3'][1][i] for i in SUB['ch3'] if struct['ch3'][0][i]=='C']}
for s in ('cn','apolarU','ch3'):
    de=min_dist_grid(C, endatoms[s], Ms); m=de<4.0
    print(f"{s:8s} N₂ {rho[(s,'N2')][m].sum():.4f} / 모체 {rho[('parent','N2')][m].sum():.4f} = {rho[(s,'N2')][m].sum()/rho[('parent','N2')][m].sum():.2f}×   CO₂ {rho[(s,'CO2')][m].sum():.4f} / 모체 {rho[('parent','CO2')][m].sum():.4f} = {rho[(s,'CO2')][m].sum()/rho[('parent','CO2')][m].sum():.2f}×   (복셀 {m.sum()})")
print('\n=== 전체 상대 변화(참고: 적재 비)')
for s in ('cn','apolarU','ch3'):
    print(f"{s:8s} N_N2 {N[s]['N_N2']/N['parent']['N_N2']:.3f}× · N_CO2 {N[s]['N_CO2']/N['parent']['N_CO2']:.3f}×")
# where is the biggest N2 loss? centroid distance stats of the 2 % most-depleted voxels
print('\n=== N₂ 가 가장 많이 빈 복셀(상위 2 %) 의 치환기 거리 중앙값 / 니트릴 N 거리 중앙값')
for s in ('cn','apolarU','ch3'):
    d=rho[(s,'N2')]-rho[('parent','N2')]; idx=np.argsort(d)[:int(0.02*d.size)]
    print(f"{s:8s} 치환기 {np.median(dist[s][idx]):.2f} Å · 니트릴 N 자리 {np.median(distN[idx]):.2f} Å · 그 복셀들의 비움 합 {d[idx].sum():+.4f} (전체 비움 {d[d<0].sum():+.4f})")
try:
    import matplotlib; print('\nmatplotlib', matplotlib.__version__)
except Exception as e: print('\nmatplotlib 없음:', e)
