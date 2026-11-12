# -*- coding: utf-8 -*-
"""완주한 RASPA 출력의 CO2 블록 평균 다섯 개(분자 수)를 읽어 한 실행 안의 흐름을 본다. 읽기 전용.
쓰기: python block_drift.py <실행 폴더 glob> [<glob> ...]   (폴더 = Output/System_0/*.data 를 품은 곳)"""
import glob, os, re, sys, statistics as st, math
def blocks(path, comp='CO2'):
    L = open(path, errors='replace').read().splitlines()
    if not any('Simulation finished' in x for x in L[-40:]): return 'unfinished'
    try: i = max(k for k, x in enumerate(L) if x.strip() == 'Number of molecules:')
    except ValueError: return None
    for k in range(i, len(L)):
        if re.match(r'Component \d+ \[%s\]' % re.escape(comp), L[k].strip()):
            b = []
            for x in L[k + 1:k + 12]:
                m = re.match(r'\s*Block\[\s*\d+\]\s+([-\d.eE+]+)\s+\[-\]', x)
                if m: b.append(float(m.group(1)))
            return b if len(b) == 5 else None
    return None
def main(pats):
    for pat in pats:
        rows = []
        for d in sorted(glob.glob(pat)):
            f = glob.glob(os.path.join(d, 'Output', 'System_0', '*.data'))
            if not f: continue
            b = blocks(f[0]); w = blocks(f[0], 'water')
            if not isinstance(b, list): print(f'   {os.path.basename(d)}: {b}'); continue
            rows.append((os.path.basename(d), b, w if isinstance(w, list) else None))
        print(f'\n[{pat}] 완주 {len(rows)}건 — CO2 블록 1~5(분자 수) · 뒤−앞 = (블록4+5)/2 − (블록1+2)/2 · 물 평균(분자 수)')
        dd = []
        for nm, b, w in rows:
            d = (b[3] + b[4]) / 2 - (b[0] + b[1]) / 2; m = st.mean(b); dd.append((nm, d, d / m))
            print(f"   {nm:30s} {' '.join(f'{x:6.2f}' for x in b)} · 평균 {m:6.2f} · 뒤−앞 {d:+.2f} ({100*d/m:+.1f} %)" + (f" · 물 {st.mean(w):.2f}" if w else ''))
        if len(dd) >= 2:
            r = [x[2] for x in dd]; se = st.stdev(r) / math.sqrt(len(r))
            print(f"   → 뒤−앞 상대값 평균 {100*st.mean(r):+.2f} % (SD {100*st.stdev(r):.2f} · n {len(r)} · t = {st.mean(r)/se:+.2f}) · 양수 {sum(1 for x in r if x > 0)}/{len(r)}")
if __name__ == '__main__': main(sys.argv[1:])
