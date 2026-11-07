# MAGI-006 추론 그래프 생성기 — MAGI-005_graph.json 스키마(nodes{id,type,seat,text,grade,footnotes} · edges{src,dst,type,text})
import re, json, sys, os
ROOT='/home/mangwon1/mof_project/21_ZIF69_MTV/MAGI'
files={'M':'MAGI-006_R1_laptop.md','J':'MAGI-006_R1_junseok.md','B':'MAGI-006_R1_balthasar_hkhome-sub.md'}
r2='MAGI-006_R2_attack.md'
r3={'M':'MAGI-006_R3_laptop.md','J':'MAGI-006_R3_junseok.md','B':'MAGI-006_R3_balthasar_hkhome-sub.md'}
nodes={}; edges=[]
def add(nid,typ,seat,text,grade=None,fns=None):
    if nid not in nodes: nodes[nid]={'id':nid,'type':typ,'seat':seat,'text':text[:400],'grade':grade,'footnotes':fns or []}
grade_re=re.compile(r'\[(산술|가설|전문|요지|미확인|양산[^\]]*|FEM[^\]]*|모의|추정)\]')
for seat,fn in files.items():
    p=os.path.join(ROOT,fn)
    if not os.path.exists(p): continue
    txt=open(p,encoding='utf-8').read()
    # claims: lines beginning with **M-1.** / M-1. / J-1 / B-1 (bold or plain)
    for m in re.finditer(r'^\s*(?:\*\*|-\s*|\|\s*)?('+seat+r'-\d+[a-d]?)\.?\s*(.+?)$', txt, re.M):
        cid,body=m.group(1),m.group(2)
        g=grade_re.findall(body); fns=re.findall(r'\[\^([A-Za-z0-9]+)\]',body)
        add(cid,'claim',seat,f'{cid}. {body.strip("* ")}', g[0] if g else None, fns)
        for f in fns:
            add(f'{seat}:fn{f}','footnote',seat,f'[^{f}]'); edges.append({'src':cid,'dst':f'{seat}:fn{f}','type':'footnote','text':''})
    # footnote bodies
    for m in re.finditer(r'^\s*\[\^([A-Za-z0-9]+)\]:?\s*(.+)$', txt, re.M):
        fid=f'{seat}:fn{m.group(1)}'
        if fid in nodes: nodes[fid]['text']=m.group(2)[:400]
        else: add(fid,'footnote',seat,m.group(2)[:400])
# R2 attacks
p=os.path.join(ROOT,r2)
if os.path.exists(p):
    txt=open(p,encoding='utf-8').read()
    for m in re.finditer(r'^\*\*(A-(?:[MJB]?\d+))\.\s*(.+?)\*\*', txt, re.M):
        aid,body=m.group(1),m.group(2); add(aid,'attack','HK',f'{aid}. {body}')
        # targets: [[M §2-3]] [[J-9]] [[B-7]] etc → link to claim nodes when id-like
        seg=txt[m.end():m.end()+600]
        for t in re.findall(r'\[\[([MJB])[ -]?(\d+[a-d]?)\]\]', seg):
            tid=f'{t[0]}-{t[1]}'
            if tid in nodes: edges.append({'src':aid,'dst':tid,'type':'attacks','text':''})
        for t in re.findall(r'\[\[([MJB]) §[^\]]+\]\]', seg):
            edges.append({'src':aid,'dst':f'{t}:R1','type':'attacks-section','text':''}); add(f'{t}:R1','document',t,f'{t} R1')
# R3 defenses
for seat,fn in r3.items():
    p=os.path.join(ROOT,fn)
    if not os.path.exists(p): continue
    txt=open(p,encoding='utf-8').read()
    for m in re.finditer(r'^###\s*(D-(?:[MJB]?\d+))\s*←\s*(A-(?:[MJB]?\d+))\s*\((수용|반박|수정)[^)]*\)', txt, re.M):
        did,aid,verdict=m.group(1),m.group(2),m.group(3)
        nid=f'{seat}:{did}'; add(nid,'defense',seat,f'{did} ← {aid} ({verdict})',verdict)
        edges.append({'src':nid,'dst':aid,'type':f'defends-{verdict}','text':''})
        seg=txt[m.end():m.end()+1500]
        for t in re.findall(r'\[\[([MJB])[ -]?(\d+[a-d]?)\]\]', seg):
            tid=f'{t[0]}-{t[1]}'
            if tid in nodes and t[0]!=seat: edges.append({'src':nid,'dst':tid,'type':'cites-other-seat','text':''})
        for f in re.findall(r'\[\^([A-Za-z0-9]+)\]',seg):
            add(f'{seat}:fn{f}','footnote',seat,f'[^{f}]'); edges.append({'src':nid,'dst':f'{seat}:fn{f}','type':'footnote','text':''})
out={'nodes':list(nodes.values()),'edges':edges}
json.dump(out,open(os.path.join(ROOT,'MAGI-006_graph.json'),'w',encoding='utf-8'),ensure_ascii=False,indent=1)
from collections import Counter
print('nodes',len(nodes),Counter(n['type'] for n in nodes.values()),'edges',len(edges),Counter(e['type'] for e in edges))
print('claims per seat',Counter(n['seat'] for n in nodes.values() if n['type']=='claim'))
print('cross-seat cites',Counter((e['src'].split(':')[0],e['dst'][0]) for e in edges if e['type']=='cites-other-seat'))
