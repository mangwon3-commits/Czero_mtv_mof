#!/usr/bin/env python3
"""막은 구 안 CO2 밀도 확인(클라우드 검증석 7회차) — RASPA COM 밀도 VTK(90^3, 초격자) 와 Zeo++ .block 구를 겹쳐 구 안 밀도 합을 셈. 표준 파이썬만."""
import gzip, math, subprocess, sys
def load_vtk(p):
    with gzip.open(p,'rt') as f:
        hdr=[next(f) for _ in range(10)]
        cp=[float(x) for x in hdr[1].split()[1:]]
        dims=[int(x) for x in hdr[4].split()[1:]]
        vals=[float(l) for l in f if l.strip()]
    return cp,dims,vals
def mat(a,b,c,al,be,ga):
    al,be,ga=map(math.radians,(al,be,ga))
    cx=c*math.cos(be); cy=c*(math.cos(al)-math.cos(be)*math.cos(ga))/math.sin(ga); cz=math.sqrt(c*c-cx*cx-cy*cy)
    return ((a,0,0),(b*math.cos(ga),b*math.sin(ga),0),(cx,cy,cz))
blk=subprocess.run(['git','show','origin/master:21_ZIF69_MTV/e28b_blocks/e24c_c2h5_100_block1.65.block'],capture_output=True,text=True).stdout.split('\n')
sph=[list(map(float,l.split())) for l in blk[1:] if l.strip()]
rep=(1,2,3)
S=[((x+i)/rep[0],(y+j)/rep[1],(z+k)/rep[2],r) for x,y,z,r in sph for i in range(rep[0]) for j in range(rep[1]) for k in range(rep[2])]
for lab in ('q_on','q_off'):
    cp,dims,v=load_vtk(f'density_v3_tpl2/e24c_c2h5_100__{lab}/VTK/System_0/COMDensityProfile_CO2.vtk.gz')
    M=mat(*cp); n=dims; tot=sum(v)
    for off,name in ((0.0,'점=i/N'),(0.5,'점=(i+.5)/N')):
        for shrink in (0.0,0.5):
            inside=0.0; nin=0; nvox=0
            for idx,val in enumerate(v):
                i=idx%n[0]; j=(idx//n[0])%n[1]; k=idx//(n[0]*n[1])
                f=((i+off)/n[0],(j+off)/n[1],(k+off)/n[2])
                hit=False
                for sx,sy,sz,r in S:
                    d=[f[0]-sx,f[1]-sy,f[2]-sz]; d=[t-round(t) for t in d]
                    cx=d[0]*M[0][0]+d[1]*M[1][0]+d[2]*M[2][0]; cy=d[0]*M[0][1]+d[1]*M[1][1]+d[2]*M[2][1]; cz=d[0]*M[0][2]+d[1]*M[1][2]+d[2]*M[2][2]
                    rr=r-shrink
                    if cx*cx+cy*cy+cz*cz<=rr*rr: hit=True; break
                if hit:
                    nin+=1; inside+=val
            print(f"{lab} {name} 반지름-{shrink}: 구 안 격자 {nin}/{len(v)} ({100*nin/len(v):.1f} %) · 구 안 밀도 합 {inside:.4g} / 전체 {tot:.4g} ({100*inside/tot:.3f} %)")
        break  # q_on · q_off 각각 점=i/N 규약만(0.5 칸 이동 규약은 생략)
