"""Δ40 — 블록 길이에 무관한 표류 지표. `V3W_CHUNK_VS_SINGLE_20260907.md` 등록.

    Δ40 = (뒤 40 % 블록 평균) / (앞 40 % 블록 평균) − 1

⚠️ **`%/블록` 을 쓰지 마십시오.** 사슬은 25블록(600 사이클), 단일은 5블록(3,000)이라
   같은 이름의 **다른 양**입니다(09-07 에 그것으로 한 번 틀렸습니다). Δ40 은 비라서
   블록 길이에 무관합니다.

⚠️ 사슬 러너에는 힘장 관문이 없습니다. 그래서 **조각마다** 머리말을 확인합니다.
"""
import glob, os, re, sys, statistics as st

def blocks(path, comp=(1, 'water')):
    txt = open(path, encoding='utf-8', errors='ignore').read()
    i = txt.rfind(f'Component {comp[0]} [{comp[1]}]')
    if i < 0: return []
    return [float(m.group(1)) for m in
            re.finditer(r'Block\[\s*\d+\]\s+([\d.eE+-]+)', txt[i:i+1200])][:5]

def ff_ok(path):
    """머리말에서 Hw-Hw / Ow-Ow 확인. 이름은 **오른쪽 정렬 패딩**입니다."""
    hw = ow = None
    with open(path, encoding='utf-8', errors='ignore') as f:
        for ln in f:
            if hw is None and re.match(r'^\s*Hw\s+-\s+Hw\s', ln):
                hw = 'ZERO_POTENTIAL' in ln
            elif ow is None and re.match(r'^\s*Ow\s+-\s+Ow\s', ln):
                g = re.findall(r'[-+]?\d*\.?\d+(?:[eE][-+]?\d+)?', ln)
                ow = abs(float(g[1]) - 89.633) < 1e-3 if len(g) > 1 else False
            if hw is not None and ow is not None: break
    return bool(hw) and bool(ow)

def d40(b):
    if len(b) < 5: return None
    n = len(b); k = max(1, round(n * 0.4))
    front, back = st.mean(b[:k]), st.mean(b[-k:])
    return (back / front - 1) if front else None

def series(rundir):
    """단일이면 출력 1개(5블록), 사슬이면 chunk*/ 를 이어 붙여 25블록."""
    ch = sorted(glob.glob(os.path.join(rundir, 'chunk*')),
                key=lambda p: int(re.search(r'chunk(\d+)', p).group(1)))
    if ch:
        b, ffs = [], []
        for c in ch:
            o = glob.glob(os.path.join(c, 'Output', 'System_0', '*.data'))
            if not o: return None, None, f'{os.path.basename(c)} 출력 없음'
            b += blocks(o[0]); ffs.append(ff_ok(o[0]))
        return b, all(ffs), f'사슬 {len(ch)}조각 · 블록 {len(b)} · 힘장 {sum(ffs)}/{len(ffs)} 통과'
    o = glob.glob(os.path.join(rundir, 'Output', 'System_0', '*.data'))
    if not o: return None, None, '출력 없음'
    b = blocks(o[0])
    return b, ff_ok(o[0]), f'단일 · 블록 {len(b)}'

if __name__ == '__main__':
    pats = sys.argv[1:] or ['water_runs_v3w/*/', 'water_runs_v3w_chunk/*/', 'water_runs_v3w_rep/*/']
    out = {}
    for pat in pats:
        for d in sorted(glob.glob(pat)):
            b, ff, note = series(d.rstrip('/'))
            tag = os.path.basename(d.rstrip('/'))
            grp = d.split('/')[0]
            if b is None or len(b) < 5:
                print(f'  {grp:<24} {tag:<20} — {note}'); continue
            v = d40(b)
            out.setdefault(grp, []).append(v)
            print(f'  {grp:<24} {tag:<20} **Δ40 {100*v:+6.1f} %**   {note}'
                  f'   {"" if ff else "  ⚠️ **힘장 확인 실패**"}')
    for grp, v in out.items():
        if len(v) > 1:
            print(f'\n  {grp}  n={len(v)}  Δ40 **{100*min(v):+.1f} ~ {100*max(v):+.1f} %**  '
                  f'중앙 {100*st.median(v):+.1f}  SD {100*st.stdev(v):.1f}')
