# -*- coding: utf-8 -*-
"""§AW·§AW-2 판정 — 등록 `COREWC_REGISTRATION_20260923.md §4` · `COREWC2_REGISTRATION_20260923.md §5`.

자료: `core_wc_results*.json` 전부(작업트리 + origin 모든 ref). 같은 구조가 여러 기기에 있으면
모집단엔 **하나만** 넣습니다(§AV `merge_core_pop.py` 와 같은 규약, 나머지는 짝 자료).
"""
import json, glob, os, subprocess, statistics as st
G = '/home/mangwon1/mof_project'
H = os.path.join(G, '21_ZIF69_MTV')


def sh(*a):
    return subprocess.run(a, cwd=G, capture_output=True, text=True).stdout


def load_all():
    rows, pairs = {}, {}
    srcs = [('tree', f, open(f, encoding='utf-8', errors='ignore').read())
            for f in glob.glob(os.path.join(H, 'core_wc_results*.json'))]
    refs = [l.strip() for l in sh('git', 'for-each-ref', '--format=%(refname:short)',
                                  'refs/remotes/origin').splitlines() if l.strip() and 'HEAD' not in l]
    for rb in refs:
        for p in sh('git', 'ls-tree', '-r', '--name-only', rb, '21_ZIF69_MTV/').splitlines():
            b = p.split('/')[-1]
            if b.startswith('core_wc_results') and b.endswith('.json'):
                srcs.append((rb, b, sh('git', 'show', '%s:%s' % (rb, p))))
    for tag, f, txt in srcs:
        try:
            rs = json.loads(txt).get('rows', [])
        except Exception:
            continue
        for r in rs:
            if r.get('n_0.15bar') is None or r.get('n_0.01bar') is None:
                continue
            k = r['file']
            if k in rows:
                if r.get('machine') != rows[k].get('machine'):
                    pairs.setdefault(k, []).append(r)
            else:
                rows[k] = r
    return rows, pairs


def pct(sorted_vals, x):
    """x 이하인 비율 [%]. 백분위 정의를 한 군데로 고정합니다."""
    n = len(sorted_vals)
    return 100.0 * sum(1 for v in sorted_vals if v <= x) / n


def main():
    rows, pairs = load_all()
    ours = json.load(open(os.path.join(H, 'results_v3.json')))['rows']
    L = sorted(r['n_0.15bar'] for r in rows.values())
    W = [r['n_0.15bar'] - r['n_0.01bar'] for r in rows.values()]
    ourL = sorted(r['loading_015bar'] for r in ours if r.get('loading_015bar'))
    saim100 = max(ourL)
    ourmed = st.median(ourL)

    print('=' * 78)
    print('§AW + §AW-2 판정 — 모집단 %d종 (두 압력 완주) · 우리 %d조성' % (len(rows), len(ourL)))
    print('  겹쳐 돈 구조(짝 자료): %d종 — 모집단엔 하나만 넣었습니다' % len(pairs))
    print('=' * 78)

    med = st.median(L)
    print('\nP1  풀 0.15 bar 적재 중앙값 %.4f mmol/g   [0.3, 1.5]  → %s'
          % (med, '적중' if 0.3 <= med <= 1.5 else '빗나감'))
    print('      최소 %.4f · 25%% %.4f · 75%% %.4f · 최대 %.4f'
          % (L[0], L[len(L)//4], L[3*len(L)//4], L[-1]))

    p2 = pct(L, saim100)
    print('\nP2  saIm100 (%.3f) 백분위 %.1f %%   [70, 95]  → %s'
          % (saim100, p2, '적중' if 70 <= p2 <= 95 else '빗나감'))
    p3 = pct(L, ourmed)
    print('P3  우리 중앙 (%.3f) 백분위 %.1f %%   [40, 70]  → %s'
          % (ourmed, p3, '적중' if 40 <= p3 <= 70 else '빗나감'))

    ratios = sorted(w / r['n_0.15bar'] for w, r in zip(W, rows.values()) if r['n_0.15bar'] > 0)
    rmed = st.median(ratios)
    print('\nP4  VSA 작업용량 / 0.15 bar 적재, 중앙 구조 %.3f   ≥ 0.70  → %s'
          % (rmed, '적중' if rmed >= 0.70 else '빗나감'))
    print('      25%% %.3f · 75%% %.3f · 0.70 미만인 구조 %d/%d'
          % (ratios[len(ratios)//4], ratios[3*len(ratios)//4],
             sum(1 for x in ratios if x < 0.70), len(ratios)))

    band = [f for f, r in rows.items() if 7.0 <= r['n_0.15bar'] <= 12.0]
    print('\nP5 ★ 7~12 mmol/g 대 구조 수 %d   = 0  → %s   **D8 의 직접 검정**'
          % (len(band), '적중' if not band else '빗나감(반증)'))
    print('      풀 최대 %.4f mmol/g — 7 의 %.2f 배' % (L[-1], L[-1] / 7.0))
    print('      우리 31조성 최대 %.3f · 노트북이 낸 대역 7~12' % saim100)

    pop = json.load(open(os.path.join(H, 'core_pop_merged.json')))
    poprows = pop['rows'] if isinstance(pop, dict) else pop
    tgt = ({q['file'] for q in json.load(open(os.path.join(H, 'core_wc_pick2.json')))}
           | {q['file'] for q in json.load(open(os.path.join(H, 'core_wc_pick.json')))})
    print('\nP6  실패율 %d/%d = %.1f %%   ≤ 5 %%  → %s'
          % (len(tgt) - len(rows), len(tgt), 100.0 * (len(tgt) - len(rows)) / len(tgt),
             '적중' if (len(tgt) - len(rows)) / len(tgt) <= 0.05 else '빗나감'))

    pick72 = {q['file'] for q in json.load(open(os.path.join(H, 'core_wc_pick.json')))}
    L72 = sorted(r['n_0.15bar'] for f, r in rows.items() if f in pick72)
    a2, a3 = pct(L72, saim100), pct(L72, ourmed)
    d2, d3 = abs(a2 - p2), abs(a3 - p3)
    print('\nP7 ★ 72종 표본 대 %d종 모집단 백분위' % len(rows))
    print('      saIm100    72종 %.1f %%  대  전체 %.1f %%   차 %.1f %%p' % (a2, p2, d2))
    print('      우리 중앙   72종 %.1f %%  대  전체 %.1f %%   차 %.1f %%p' % (a3, p3, d3))
    print('      ±5 %%p 안  → %s%s' % ('적중' if max(d2, d3) <= 5 else '빗나감',
          '' if max(d2, d3) <= 5 else '  ⇒ §AW 백분위에서 "72종 중" 단서를 떼면 안 됩니다'))

    # ⚠ `our_KH_CO2` 는 §AW 의 72종 pick 에만 실려 있습니다(pick2 를 `core_pop_merged` 에서 만들 때
    #   그 필드를 안 옮겼습니다 — 제 pick 생성 누락). 등록된 양은 **514종 전체**이므로
    #   §AV 의 원자료에서 파일 키로 직접 잇습니다.
    popkh = {}
    for r in poprows:
        v = r.get('KH_CO2') or r.get('our_KH_CO2')
        if v:
            popkh[r['file']] = v
    kh = [(popkh[f], r['n_0.15bar'] - r['n_0.01bar']) for f, r in rows.items() if f in popkh]
    def rank(v):
        s = sorted(range(len(v)), key=lambda i: v[i]); out = [0]*len(v)
        for j, i in enumerate(s): out[i] = j
        return out
    rx, ry = rank([a for a, _ in kh]), rank([b for _, b in kh])
    n = len(rx); mx, my = st.mean(rx), st.mean(ry)
    num = sum((a-mx)*(b-my) for a, b in zip(rx, ry))
    den = (sum((a-mx)**2 for a in rx) * sum((b-my)**2 for b in ry)) ** 0.5
    rho = num/den
    print('\nP8  스피어만 ρ(우리 자 K_H, VSA 작업용량) = %.3f  (n=%d)   ≥ 0.70  → %s'
          % (rho, n, '적중' if rho >= 0.70 else '빗나감'))
    print('=' * 78)


if __name__ == '__main__':
    main()
