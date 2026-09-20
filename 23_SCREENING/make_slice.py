import json,os,hashlib,sys
SRC=sys.argv[1]; DST=sys.argv[2]
src=json.load(open(SRC))
DROP_TOP={'RACs'}                 # 분자 서술자 150여 개 — 관문·순위에 안 씁니다
DROP_WATER={'GEMC'}               # 물 등온선 원문(수십 줄/건). 우리 규약과 달라 인용 안 합니다.
out={}
for k,v in src.items():
    r={}
    for f,x in v.items():
        if f in DROP_TOP: continue
        if f=='water' and isinstance(x,dict):
            r[f]={a:b for a,b in x.items() if a not in DROP_WATER}
        else:
            r[f]=x
    out[k]=r
json.dump(out,open(DST,'w'),ensure_ascii=False,separators=(',',':'))
a=os.path.getsize(SRC); b=os.path.getsize(DST)
print('원본 %.1f MB → 슬라이스 %.2f MB  (%.1f %%)'%(a/2**20,b/2**20,100*b/a))
print('md5 슬라이스 %s'%hashlib.md5(open(DST,'rb').read()).hexdigest())
print('레코드 %d · 보존 필드 %s'%(len(out),sorted(next(iter(out.values())))))
