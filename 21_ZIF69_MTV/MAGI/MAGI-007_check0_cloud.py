"""점검⓪ (C R3 D-13 정의) — 모체 CO₂ 밀도 격자(density_v3_tpl/e22_parent__q_on)에서 bib 접촉 비율 f_bib 대 f₀. 종합자 자기 코드."""
import gzip, sys, numpy as np, json
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
VTK=sys.argv[1]; CIF=sys.argv[2]
sym,fr,M=read_cif(CIF); ssym,spos,Ms=super_positions(sym,fr,M,(1,2,3))
# 리간드 분류: Zn 뗀 결합 그래프의 연결 성분 — N 있으면 bib · S/O 있으면 bdtdc
COV={'C':0.76,'N':0.71,'O':0.66,'S':1.05,'Zn':1.22,'H':0.31}
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
    kind[cc]='bib' if 'N' in el else ('bdtdc' if ('S' in el or 'O' in el) else '?')
is_bib=np.array([comp[i]!=-1 and kind[comp[i]]=='bib' for i in range(n)]); is_zn=np.array([s=='Zn' for s in ssym])
print('성분 수', c, '· 종류', {k:sum(1 for v in kind.values() if v==k) for k in set(kind.values())}, '· 원자 bib', is_bib.sum(), '· bdtdc', (~is_bib & ~is_zn).sum(), '· Zn', is_zn.sum())
f0_all=is_bib.sum()/n; f0_noZn=is_bib.sum()/(n-is_zn.sum())
vals,dims=read_vtk(VTK); nx,ny,nz=dims
idx=np.arange(vals.size); i=idx%nx; j=(idx//nx)%ny; kk=idx//(nx*ny)
C=(np.stack([(i+0.5)/nx,(j+0.5)/ny,(kk+0.5)/nz],axis=1))@Ms
top=np.argsort(vals)[-int(0.05*vals.size):]          # 상위 5 % 복셀
# 접촉: 복셀 중심 4.0 Å 안 골격 원자(중심) — 원자별로 세어 비율
cnt=np.zeros(n); wcnt=np.zeros(n)
Ct=C[top]; w=vals[top]
for a in range(n):
    dv=mic(Ct-spos[a],Ms); d=np.linalg.norm(dv,axis=1); m=d<4.0
    cnt[a]=m.sum(); wcnt[a]=w[m].sum()
tot=cnt.sum(); f_bib=cnt[is_bib].sum()/tot; f_bib_w=wcnt[is_bib].sum()/wcnt.sum()
f_bib_noZn=cnt[is_bib].sum()/cnt[~is_zn].sum()
print(f'f₀(bib 원자 비율) 전체 {f0_all:.3f} · Zn 제외 {f0_noZn:.3f}')
print(f'상위 5 % 복셀 {len(top)} · 접촉 원자-복셀 짝 {int(tot)} · f_bib {f_bib:.3f} · 밀도 가중 {f_bib_w:.3f} · Zn 제외 분모 {f_bib_noZn:.3f}')
# 보조: 접촉 원자 종류별
for lab,mask in (('bib',is_bib),('bdtdc',~is_bib & ~is_zn),('Zn',is_zn)):
    print(f'   {lab:6s} 접촉 몫 {cnt[mask].sum()/tot:.3f} · 가중 {wcnt[mask].sum()/wcnt.sum():.3f} · 원자 비율 {mask.sum()/n:.3f}')
r=f_bib/f0_all
print(f'판독(D-13): f_bib/f₀ = {r:.2f} → ' + ('f_bib ≥ f₀ → bib 빌더 등록' if f_bib>=f0_all else ('f_bib ≤ 0.5 f₀ → bib 축 닫음' if f_bib<=0.5*f0_all else '사이 → 서술만')))
