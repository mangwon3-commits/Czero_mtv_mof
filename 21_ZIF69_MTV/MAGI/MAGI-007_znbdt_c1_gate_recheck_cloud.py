import sys, numpy as np
BONDI = {'C':1.70,'N':1.55,'O':1.52,'F':1.47,'S':1.80,'Cl':1.75,'Br':1.85,'Zn':1.39,'H':1.20}
COV = {'C':0.76,'N':0.71,'O':0.66,'S':1.05,'Zn':1.22,'H':0.31,'Cl':1.02,'Br':1.20,'F':0.57}
def read_cif(p):
    cell={}; sym=[]; fr=[]; inloop=False; cols=[]
    for line in open(p):
        t=line.split()
        if not t: continue
        if t[0].startswith('_cell_'): cell[t[0]]=float(t[1]); continue
        if t[0]=='loop_': inloop=True; cols=[]; continue
        if inloop and t[0].startswith('_atom_site'): cols.append(t[0]); continue
        if inloop and cols and not t[0].startswith('_') and len(t)>=len(cols) and '_atom_site_fract_x' in cols:
            sym.append(t[cols.index('_atom_site_type_symbol')]); fr.append([float(t[cols.index('_atom_site_fract_'+k)]) for k in 'xyz'])
        elif inloop and t[0].startswith('_'): pass
        elif inloop and cols and '_atom_site_fract_x' not in cols: pass
    a,b,c=cell['_cell_length_a'],cell['_cell_length_b'],cell['_cell_length_c']
    al,be,ga=[np.radians(cell['_cell_angle_'+k]) for k in ('alpha','beta','gamma')]
    v=np.sqrt(1-np.cos(al)**2-np.cos(be)**2-np.cos(ga)**2+2*np.cos(al)*np.cos(be)*np.cos(ga))
    M=np.array([[a,0,0],[b*np.cos(ga),b*np.sin(ga),0],[c*np.cos(be),c*(np.cos(al)-np.cos(be)*np.cos(ga))/np.sin(ga),c*v/np.sin(ga)]])
    return np.array(sym), np.array(fr)@M, M
def mic_d(pos,M):
    # all-pairs minimum-image distances via 27 images
    n=len(pos); D=np.full((n,n),1e9)
    for i in (-1,0,1):
        for j in (-1,0,1):
            for k in (-1,0,1):
                sh=i*M[0]+j*M[1]+k*M[2]
                d=np.linalg.norm(pos[:,None,:]-(pos[None,:,:]+sh),axis=2); D=np.minimum(D,d)
    np.fill_diagonal(D,1e9); return D
def bonds(sym,D):
    n=len(sym); nb=[[] for _ in range(n)]
    for i in range(n):
        for j in range(i+1,n):
            cut=(COV[sym[i]]+COV[sym[j]])*1.15 if 'Zn' not in (sym[i],sym[j]) else 2.45
            if D[i,j]<cut: nb[i].append(j); nb[j].append(i)
    return nb
def analyse(p, label):
    sym,pos,M=read_cif(p); D=mic_d(pos,M); nb=bonds(sym,D); n=len(sym)
    het=[i for i in range(n) if sym[i] in ('N','O','S','Zn')]; H=[i for i in range(n) if sym[i]=='H']
    dHhet=min((D[h,x],h,x) for h in H for x in het)
    # alkyne detection: C with 2 neighbours, one C at <1.25 A
    alk=[]
    for i in range(n):
        if sym[i]!='C' or len(nb[i])!=2: continue
        cc=[j for j in nb[i] if sym[j]=='C' and D[i,j]<1.25]
        if cc: alk.append(i)
    term=[i for i in alk if any(sym[j]=='H' for j in nb[i])]
    nitrile=[i for i in range(n) if sym[i]=='N' and len(nb[i])==1 and D[i,nb[i][0]]<1.2]
    print(f"--- {label}: {n} atoms · alkyne C {len(alk)} · terminal C {len(term)} · nitrile N {len(nitrile)}")
    print(f"(0a) min H···{{N,O,S,Zn}} = {dHhet[0]:.3f} Å  ({sym[dHhet[1]]}{dHhet[1]+1}···{sym[dHhet[2]]}{dHhet[2]+1})  threshold ≥ 1.8 → {'PASS' if dHhet[0]>=1.8 else 'FAIL'}")
    # (0b) for substituent groups: alkyne C's + their H ; or nitrile C+N
    groups=[]
    for t in term:
        inner=[j for j in nb[t] if sym[j]=='C'][0]; h=[j for j in nb[t] if sym[j]=='H'][0]; anchor=[j for j in nb[inner] if j!=t][0]
        groups.append(([t,inner,h],anchor))
    for nn in nitrile:
        c=nb[nn][0]; anchor=[j for j in nb[c] if j!=nn][0]; groups.append(([nn,c],anchor))
    worst=(1e9,None)
    rows=[]
    for g,anchor in groups:
        excl=set(g)|{anchor}|set(nb[anchor])
        for u in g:
            if sym[u]=='H': continue
            for k in range(n):
                if k in excl or sym[k]=='H': continue
                m=D[u,k]-(BONDI[sym[u]]+BONDI[sym[k]])
                if m<worst[0]: worst=(m,(u,k))
        # per group: terminal heavy atom to nearest O, and H to nearest O
        heavy_end=g[0]; dO=min((D[heavy_end,k],k) for k in range(n) if sym[k]=='O')
        hO=None
        hs=[x for x in g if sym[x]=='H']
        if hs: hO=min((D[hs[0],k],k) for k in range(n) if sym[k]=='O')
        rows.append((sym[heavy_end]+str(heavy_end+1), round(dO[0],3), (round(hO[0],3) if hO else None)))
    if groups:
        u,k=worst[1]
        print(f"(0b) min margin = {worst[0]:+.3f} Å ({sym[u]}{u+1}···{sym[k]}{k+1} d={D[u,k]:.3f}, Bondi sum {BONDI[sym[u]]+BONDI[sym[k]]:.2f}) threshold overlap < 0.4 → {'PASS' if worst[0]>-0.4 else 'FAIL'}")
        print("     per group: end atom · end···O min · terminal H···O min:", rows)
for p,l in zip(sys.argv[1::2], sys.argv[2::2]): analyse(p,l)
