"""물이 어디에 모이는가 — WATER_SITE_E22_20261108.md §2 그대로. 종합자 자기 코드(check0 의 CIF/VTK 읽기 재사용)."""
import gzip, sys, json, os, numpy as np
HERE=os.path.dirname(os.path.abspath(__file__)); ROOT=os.path.dirname(HERE)
COV={'C':0.76,'N':0.71,'O':0.66,'S':1.05,'Zn':1.22,'H':0.31,'Cl':1.02,'Br':1.20}
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
    return np.array(sym), np.array(fr), M, (a,b,c)
def read_vtk(p):
    with gzip.open(p,'rt') as f:
        hdr=[next(f) for _ in range(10)]
        dims=[int(x) for x in [h for h in hdr if h.startswith('DIMENSIONS')][0].split()[1:]]
        cellp=[float(x) for x in [h for h in hdr if h.startswith('CELL_PARAMETERS')][0].split()[1:]]
        vals=np.array([float(x) for x in f.read().split()])
    assert vals.size==dims[0]*dims[1]*dims[2]
    return vals, dims, cellp
def super_positions(sym, fr, M, reps):
    Ms=np.diag(reps).astype(float)@M; pos=[]; syms=[]
    for i in range(reps[0]):
        for j in range(reps[1]):
            for k in range(reps[2]):
                pos.append(((fr+np.array([i,j,k]))/np.array(reps))@Ms); syms+=list(sym)
    return np.array(syms), np.vstack(pos), Ms
def mic(dv, Ms):
    inv=np.linalg.inv(Ms); f=dv@inv; f-=np.round(f); return f@Ms
def classify(ssym, spos, Ms):
    n=len(ssym); D=np.full((n,n),1e9)
    for i in (-1,0,1):
        for j in (-1,0,1):
            for k in (-1,0,1):
                sh=i*Ms[0]+j*Ms[1]+k*Ms[2]; d=np.linalg.norm(spos[:,None,:]-(spos[None,:,:]+sh),axis=2); D=np.minimum(D,d)
    np.fill_diagonal(D,1e9)
    adj=[[j for j in range(n) if ssym[i]!='Zn' and ssym[j]!='Zn' and D[i,j]<(COV[ssym[i]]+COV[ssym[j]])*1.15] for i in range(n)]
    comp=[-1]*n; c=0
    for i in range(n):
        if comp[i]!=-1 or ssym[i]=='Zn': continue
        stack=[i]; comp[i]=c
        while stack:
            u=stack.pop()
            for v in adj[u]:
                if comp[v]==-1: comp[v]=c; stack.append(v)
        c+=1
    kind={}
    for cc in range(c):
        el={ssym[i] for i in range(n) if comp[i]==cc}
        kind[cc]='bib' if ('N' in el and 'S' not in el) else ('bdt' if ('S' in el or 'O' in el) else '?')
    zn=[i for i in range(n) if ssym[i]=='Zn']
    cls=[]
    for i in range(n):
        s=ssym[i]
        if s=='Zn': cls.append('Zn'); continue
        lig=kind[comp[i]]; dzn=min(D[i,z] for z in zn)
        if s=='O': cls.append('O_n' if any(ssym[j]=='N' for j in adj[i]) else ('O_c' if dzn<2.4 else 'O_f'))   # [11-13 · J-2 등록] 니트로 O(N 에 붙은 O)를 따로 셈
        elif s=='N': cls.append(('N_c' if dzn<2.4 else 'N_a') if lig=='bib' else 'N_bdt')
        elif s=='S': cls.append('S')
        elif s in ('Cl','Br'): cls.append('X_bdt')
        else: cls.append(f'{s}_{lig}')
    return np.array(cls)
def nearest(centers, spos, Ms, chunk=30000):
    dmin=np.empty(len(centers)); amin=np.empty(len(centers),dtype=int)
    for s in range(0,len(centers),chunk):
        c=centers[s:s+chunk]; d=np.full(len(c),1e9); a=np.zeros(len(c),dtype=int)
        for ai in range(len(spos)):
            dv=mic(c-spos[ai],Ms); dd=np.linalg.norm(dv,axis=1); m=dd<d; d[m]=dd[m]; a[m]=ai
        dmin[s:s+chunk]=d; amin[s:s+chunk]=a
    return dmin, amin
def within(centers, w, atoms, Ms, r=3.5, chunk=30000):
    hit=np.zeros(len(centers),dtype=bool)
    for s in range(0,len(centers),chunk):
        c=centers[s:s+chunk]; h=np.zeros(len(c),dtype=bool)
        for A in atoms:
            dv=mic(c-A,Ms); h|=np.linalg.norm(dv,axis=1)<r
        hit[s:s+chunk]=h
    return float(w[hit].sum()/w.sum()) if w.sum()>0 else float('nan')
def analyse(name):
    cif=os.path.join(ROOT,'charged_v3',f'{name}_DDEC6.cif'); vdir=os.path.join(ROOT,os.environ.get('WATER_SITE_RUNS','water_runs_density_v3w'),f'rh90_{name}','VTK','System_0')   # [11-11] 323 K 격자(등록 E)는 WATER_SITE_RUNS=water_runs_density_v3w_323
    sym,fr,M,(a,b,c)=read_cif(cif)
    vals_w,dims,cellp=read_vtk(os.path.join(vdir,'COMDensityProfile_water.vtk.gz'))
    vals_c,dims2,cellp2=read_vtk(os.path.join(vdir,'COMDensityProfile_CO2.vtk.gz'))
    reps=tuple(int(round(cellp[i]/x)) for i,x in enumerate((a,b,c)))
    assert all(abs(cellp[i]-reps[i]*x)<0.05 for i,x in enumerate((a,b,c))), (cellp, (a,b,c))
    ssym,spos,Ms=super_positions(sym,fr,M,reps); cls=classify(ssym,spos,Ms)
    nx,ny,nz=dims; idx=np.arange(vals_w.size); i=idx%nx; j=(idx//nx)%ny; k=idx//(nx*ny)
    C=(np.stack([(i+0.5)/nx,(j+0.5)/ny,(k+0.5)/nz],axis=1))@Ms
    dmin,amin=nearest(C,spos,Ms); ncls=cls[amin]
    pore=dmin>2.6
    out={'name':name,'reps':reps,'n_atoms':int(len(ssym)),'classes':{c_:int((cls==c_).sum()) for c_ in sorted(set(cls))},
         'grid':{'dims':dims,'pore_voxels':int(pore.sum())}}
    for tag,vals in (('water',vals_w),('CO2',vals_c)):
        nz_=vals>0; minnz=vals[nz_].min(); nsamp=vals.sum()/minnz
        wmed=lambda d,w: float(np.interp(0.5, np.cumsum(w[np.argsort(d)])/w.sum(), np.sort(d)))
        res={'nonzero_voxels':int(nz_.sum()),'max_count':int(round(1/minnz)),'n_samples':float(nsamp),
             'median_nearest_any_weighted':wmed(dmin[nz_],vals[nz_])}
        # [16:1x 정정] 상위 5 % 는 0 이 아닌 복셀 안에서 고름 — 0 값 동률이 섞이면(모체 물: 0 아닌 복셀 20,622 < 36,450) 골격 안 복셀이 '최근접 Zn' 으로 잡힘
        ntop=min(int(0.05*vals.size), int(nz_.sum())); top=np.argsort(vals)[-ntop:]
        res['n_top']=int(ntop)
        f_top={c_:float((ncls[top]==c_).mean()) for c_ in sorted(set(cls))}
        f_pore={c_:float((ncls[pore]==c_).mean()) for c_ in sorted(set(cls))}
        w=vals[nz_]; f_w={c_:float(w[ncls[nz_]==c_].sum()/w.sum()) for c_ in sorted(set(cls))}
        res['f_top']=f_top; res['f_pore']=f_pore; res['f_weighted']=f_w
        res['E_top']={c_:(f_top[c_]/f_pore[c_] if f_pore[c_]>0 else None) for c_ in f_top}
        res['E_weighted']={c_:(f_w[c_]/f_pore[c_] if f_pore[c_]>0 else None) for c_ in f_w}
        groups={'Zn':['Zn'],'O_f':['O_f'],'O_n':['O_n'],'O_c':['O_c'],'bib':['N_c','N_a','C_bib','H_bib'],'bdt_ring':['C_bdt','H_bdt','S'],'N_bdt':['N_bdt'],'X_bdt':['X_bdt']}
        Cz=C[nz_]; wz=vals[nz_]; Cp=C[pore]; wp=np.ones(pore.sum())
        res['within35']={}; res['within35_pore']={}
        for g,members in groups.items():
            atoms=spos[np.isin(cls,members)]
            if len(atoms)==0: continue
            res['within35'][g]=within(Cz,wz,atoms,Ms); res['within35_pore'][g]=within(Cp,wp,atoms,Ms)
        res['median_dist_weighted']={}
        for g,members in (('Zn',['Zn']),('O_f',['O_f']),('O_n',['O_n']),('O_c',['O_c']),('N_c',['N_c']),('N_bdt',['N_bdt'])):
            atoms=spos[np.isin(cls,members)]
            if len(atoms)==0: continue
            d,_=nearest(Cz,atoms,Ms); res['median_dist_weighted'][g]=wmed(d,wz)
        out[tag]=res
    return out
if __name__=='__main__':
    names=sys.argv[1:] or ['e22_parent']
    res=[analyse(n) for n in names]
    outp=os.path.join(HERE,'MAGI-007_water_site_cloud'+os.environ.get('WATER_SITE_SUFFIX','')+'.json')
    old=[]
    if os.path.exists(outp):
        old=[r for r in json.load(open(outp)) if r['name'] not in names]
    json.dump(old+res, open(outp,'w'), indent=1, ensure_ascii=False)
    for r in res:
        for tag in ('water','CO2'):
            t=r[tag]; Et=t['E_top']; order=sorted(Et, key=lambda c_: -(Et[c_] or 0))
            print(f"{r['name']} {tag}: samples {t['n_samples']:.0f} max {t['max_count']} med_any {t['median_nearest_any_weighted']:.2f} | top5 nearest:", ', '.join(f"{c_} f={t['f_top'][c_]:.2f} E={Et[c_]:.2f}" for c_ in order[:5] if Et[c_]), '| within3.5:', {g:round(v,3) for g,v in t['within35'].items()}, '| pore:', {g:round(v,3) for g,v in t['within35_pore'].items()}, '| med d:', {g:round(v,2) for g,v in t['median_dist_weighted'].items()})
