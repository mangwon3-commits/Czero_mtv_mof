# -*- coding: utf-8 -*-
"""BDT 링커 회전 · Zn–O · 병목 원자 분류(서술 도구, E-24i 판정문 §26-5 · E-24j).
analyse(): bdtdc 조각마다 φ = ∠(고리 평면 법선, 통로축 c 의 링커 긴 축 수직 성분) — X선 · GFN-FF 는 90°(거울면 위), 회전각 = 90° − φ.
링커 종류: bdtdc 조각의 C 가 12 개 초과거나 N · Br · Cl 이 있으면 '치환(열린)', 아니면 '비치환(붐빔)'. Zn–O = 2.4 Å 안 평균.
bottlenecks_path(): channel_pinch 의 통로별 병목 원자를 (원소 · 이웃 · 링커 종류 · 고리 자리)로 셈.
사용: python linker_rotation.py <cif> [...]
"""
import sys, collections, numpy as np
from ase.io import read
from ase.neighborlist import neighbor_list
from ase.data import covalent_radii
from ase.geometry import find_mic

def frags(a):
    s=a.get_chemical_symbols(); cuts=[covalent_radii[z]*1.15 for z in a.numbers]
    i,j,D=neighbor_list('ijD',a,cuts); G=collections.defaultdict(set); vec={}
    for x,y,d in zip(i,j,D):
        if s[x]!='Zn' and s[y]!='Zn': G[x].add(y); vec[(x,y)]=d
    seen=set(); out=[]
    for k in range(len(a)):
        if k in seen or s[k]=='Zn': continue
        comp=[]; st=[k]; pos={k:a.positions[k]}
        while st:
            u=st.pop()
            if u in seen: continue
            seen.add(u); comp.append(u)
            for w in G[u]:
                if w not in pos: pos[w]=pos[u]+vec[(u,w)]
                if w not in seen: st.append(w)
        out.append((comp,pos))
    return out,G

def analyse(path):
    a=read(path); s=a.get_chemical_symbols(); cell=np.array(a.cell); chat=cell[2]/np.linalg.norm(cell[2])
    F,G=frags(a); res=collections.defaultdict(list); info={}
    for comp,pos in F:
        el={s[u] for u in comp}
        if 'S' not in el: continue
        sub='치환(열린)' if any(s[u] in ('N','Br','Cl') for u in comp) or sum(1 for u in comp if s[u]=='C')>12 else '비치환(붐빔)'
        ring=[u for u in comp if s[u] in ('C','S') and len([w for w in G[u] if s[w] in ('C','S')])>=2 and not any(s[w]=='O' for w in G[u])]
        ring=[u for u in ring if not (s[u]=='C' and any(s[w]=='N' for w in G[u]) )]
        P=np.array([pos[u] for u in ring]); c0=P.mean(0); _,_,vt=np.linalg.svd(P-c0); n=vt[2]
        carb=[u for u in comp if s[u]=='C' and sum(1 for w in G[u] if s[w]=='O')==2]
        L=pos[carb[0]]-pos[carb[1]]; L/=np.linalg.norm(L)
        ref=chat-(chat@L)*L; ref/=np.linalg.norm(ref)
        phi=np.degrees(np.arccos(abs(n@ref)))       # 고리 평면 법선과 (통로 축의 L 수직 성분) 사이 각
        res[sub].append(round(float(phi),1))
        for u in comp: info[u]=sub
    # Zn–O(카복실, 2.4 Å 안)
    zn=[k for k in range(len(a)) if s[k]=='Zn']; ox=[k for k in range(len(a)) if s[k]=='O']
    d=[]
    for z in zn:
        _,dl=find_mic(a.positions[ox]-a.positions[z],cell,pbc=True); d+= [x for x in dl if x<2.4]
    return a,res,info,(np.mean(d) if d else None,len(d))


def bottlenecks_path(p):
    import channel_pinch as C
    a, res, info, _ = analyse(p); s = a.get_chemical_symbols(); cell = np.array(a.cell)
    ded, _ = C.analyse(p, 0.2); ox = [k for k in range(len(a)) if s[k] == 'O']; out = collections.Counter()
    for o in ded:
        k = o[3]; _, dl = find_mic(a.positions[ox] - a.positions[k], cell, pbc=True)
        pos = '티오펜 C3(카복실 옆)' if dl.min() < 3.3 else '벤젠/융합 고리'
        out[(s[k], C.label(a, k).split('(')[1][:-1], info.get(k, '?'), pos)] += 1
    return out


if __name__ == '__main__':
    for p in sys.argv[1:]:
        a, res, info, zno = analyse(p)
        print(p, {k: (len(v), round(90 - float(np.mean(v)), 1)) for k, v in res.items()}, 'Zn–O %.3f' % zno[0])
