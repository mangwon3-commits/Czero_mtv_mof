"""종합자 독립 재계산 — 후속 #2: 무극성 −CN(U판) 323 K N₂ 풀림 r_T = N_N₂(323)/N_N₂(298).
읽는 법은 ASSIGN_ZNBDT_C2_FOLLOWUP_20261105.md §2 그대로(기준 모체 1.00 · −CN 1.24 · 1.5 단위 · 「B 와 같은 식」 ± 전파).
HKHOME znbdt_c2_b_judge.py 를 쓰지 않고 원자료 JSON 에서 다시 냅니다. 실행: 21_ZIF69_MTV 에서 python3 MAGI/MAGI-007_znbdt_c2_b323_read_cloud.py"""
import json, math
D = {  # 구조: (298 K 파일들, 323 K 파일들, 행 이름 접두)
    'parent': (['results_e23_mix_desktop.json'], ['results_e27_mix323_laptop.json'], 'e22_parent_s'),
    'cn': (['results_e24i_e24i_cn_open_mix_hkhome.json', 'results_e24i_e24i_cn_open_mix_s456_hkhome.json'], ['results_znbdt_b_mix323_hkhome.json'], 'e24i_cn_open_s'),
    'br': (['results_e24i_e24i_br_open_mix_laptop2.json', 'results_e24i_e24i_br_open_mix_s456_hkhome.json'], ['results_znbdt_b_mix323_hkhome.json'], 'e24i_br_open_s'),
    'U': (['results_znbdt_c2_znbdt_c2_apolarU_mix_hkhome.json'], ['results_znbdt_c2_b_mix323_hkhome.json'], 'znbdt_c2_apolarU_s')}
def load(files, pre):
    rows = []
    for f in files:
        rows += [r for r in json.load(open(f))['rows'] if r['name'].startswith(pre)]
    marks = dict(n=len(rows), status=sorted({r['status'] for r in rows}), rc=sorted({r.get('returncode') for r in rows}),
                 seeds_unique=len({r['seed'] for r in rows}) == len(rows), cif=sorted({r['cif'].split('/')[-1] for r in rows}), T=sorted({r.get('temp_K', r.get('T', None)) for r in rows}))
    n = len(rows); NN = sum(r['N_N2'] for r in rows) / n
    e_rel = (sum(r['N_N2_err'] for r in rows) / n) / math.sqrt(n) / NN   # 회차 ± 평균 / √n ÷ 평균
    S = sum(r['S_mix'] for r in rows) / n
    return NN, e_rel, S, marks
out = {}
for k, (f298, f323, pre) in D.items():
    a, ea, Sa, ma = load(f298, pre); c, ec, Sc, mc = load(f323, pre)
    r = c / a; er = r * math.hypot(ea, ec)
    out[k] = dict(r=r, er=er, N298=a, N323=c, Sr=Sc / Sa, m298=ma, m323=mc)
    print(f"{k:7s} N_N₂ {a:.4f} → {c:.4f}  r_T {r:.3f} ± {er:.3f}  S(323)/S(298) {Sc/Sa:.3f}  n {ma['n']}/{mc['n']}  status {mc['status']} rc {mc['rc']} seeds_unique {mc['seeds_unique']} cif323 {mc['cif']}")
print('재현 관문(표 1.00 · 1.24 · 1.19 와 소수 둘째 자리):', {k: round(out[k]['r'], 2) for k in ('parent', 'cn', 'br')})
d = {k: abs(out['U']['r'] - out[k]['r']) / math.hypot(out['U']['er'], out[k]['er']) for k in ('parent', 'cn', 'br')}
print(f"apolarU 단위 거리: 모체 {d['parent']:.2f} · −CN {d['cn']:.2f} · −Br {d['br']:.2f}")
if d['parent'] < 1.5 <= d['cn']: v = '−CN 의 323 K 풀림은 전하가 만든 경쟁 몫(극성 쪽 표지)'
elif d['cn'] < 1.5 <= d['parent']: v = '풀림은 전하 없이도 남음 — 모양/다른 원인'
else: v = '판별 불가(서술만)'
print('§2 판독:', v)
