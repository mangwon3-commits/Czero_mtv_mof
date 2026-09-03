"""T-B5 관문 + T-C1 사다리 — results_tb5.json 을 **등록된 문턱 그대로** 읽어 찍는다.

[사전 등록] DESIGN_STUDY_20260903.md
    T-B5  LCD 변화 |Δ| < 2% (δ 불변) + 기하 감사(judge_relax_v3) 통과.
          |Δ| > 5% → 이완 문제 또는 N 이 Zn 창 기하를 바꿈 → T-3 와 같은 감사.
    T-C1  Q_st(az100) − base ≥ +4 (하한 +3 = 1.5 단위 규칙)
          Q_st(az100) − Q_st(bIm100) ≥ +3
          로딩(az100, 0.15 bar) ≥ 1.0 mol/kg
          Q_st 이득이 bIm100 에도 있으면 효과는 Cl 제거.

[읽는 규율 — CLAUDE.md §2]
    RASPA ± 는 95% 신뢰구간(2.776 × SEM)이고 이 글의 "단위" 입니다. 두 값의
    차이는 σ_diff = √(±₁² + ±₂²) 로 합치고, 차이가 1.5 단위 미만이면 순위를
    매기지 않습니다. 진짜 σ 로 환산하지 않습니다.

    base 는 같은 파일(같은 기기에서 다시 돈 것)을 우선 쓰고, 없으면
    results_v3.json(데스크탑)을 쓰되 그렇게 적습니다.

이 스크립트는 판정문을 만들지 않습니다 — 수와 문턱을 나란히 놓을 뿐이고,
판정문은 사람이 COMMS 에 씁니다.
"""
import json
import os
import sys
from statistics import mean, stdev

HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(HERE, sys.argv[1] if len(sys.argv) > 1 else 'results_tb5.json')

GROUPS = {
    'azbIm025': ['azbIm025', 'azbIm025e1', 'azbIm025e2', 'azbIm025e3', 'azbIm025e4'],
    'azbIm050': ['azbIm050', 'azbIm050e1', 'azbIm050e2', 'azbIm050e3', 'azbIm050e4'],
    'azbIm075': ['azbIm075', 'azbIm075e1', 'azbIm075e2', 'azbIm075e3', 'azbIm075e4'],
    'azbIm100': ['azbIm100'],
    'bIm025':   ['bIm025', 'bIm025e1', 'bIm025e2', 'bIm025e3', 'bIm025e4'],
    'bIm100':   ['bIm100'],
}


def load_rows(path):
    if not os.path.exists(path):
        return {}
    d = json.load(open(path, encoding='utf-8'))
    return {r['name']: r for r in d['rows'] if r.get('status') == 'ok'}


def main():
    rows = load_rows(RES)
    if not rows:
        print(f'결과 없음: {RES}')
        return 1
    base_src = os.path.basename(RES)
    base = rows.get('base')
    if base is None:
        base = load_rows(os.path.join(HERE, 'results_v3.json')).get('base')
        base_src = 'results_v3.json (데스크탑 — 기기 다름)'
    if base is None:
        print('base 행이 없어 비교 불가')
        return 1

    judged = {}
    jp = os.path.join(HERE, 'relax_v3_judged.json')
    if os.path.exists(jp):
        judged = {r['name'].replace('ZIF69_', ''): r
                  for r in json.load(open(jp, encoding='utf-8'))['rows']}

    print(f'T-B5 / T-C1 — {os.path.basename(RES)}   base 출처: {base_src}')
    print(f'  base  LCD {base["LCD"]:.3f}  Q_st {base["Qst_CO2"]:.2f} ± {base["Qst_CO2_err"]:.2f}'
          f'  로딩 {base["loading_015bar"]:.4f} ± {base["loading_015bar_err"]:.4f}\n')

    # ---- T-B5: LCD 관문 + 기하 판정
    print('== T-B5 관문 (LCD |Δ| < 2%, 5% 초과는 감사 대상) ==')
    print(f'  {"태그":<12} {"LCD":>7} {"Δ%":>7} {"관문":<6} {"기하판정":<8}')
    tb5_pass, tb5_flag = [], []
    for g, tags in GROUPS.items():
        for t in tags:
            r = rows.get(t)
            j = judged.get(t, {})
            jtxt = '통과' if j.get('pass') else ('미달' if j else '없음')
            if r is None:
                print(f'  {t:<12} {"-":>7} {"-":>7} {"미완":<6} {jtxt:<8}')
                continue
            dl = 100 * (r['LCD'] - base['LCD']) / base['LCD']
            gate = '통과' if abs(dl) < 2 else ('감사!' if abs(dl) > 5 else '초과')
            (tb5_pass if gate == '통과' and j.get('pass') else tb5_flag).append(t)
            print(f'  {t:<12} {r["LCD"]:>7.3f} {dl:>+7.2f} {gate:<6} {jtxt:<8}')
    print(f'  관문+기하 통과 {len(tb5_pass)}  /  걸림 {len(tb5_flag)}: {" ".join(tb5_flag) or "없음"}\n')

    # ---- 조성별 요약 (앙상블은 e0~e4 평균 ± s_rep, n 병기)
    print('== 조성별 (앙상블은 평균 · s_rep(n) — ± 는 실현 하나의 95% CI) ==')
    print(f'  {"조성":<10} {"n":>2} {"Q_st":>7} {"s_rep":>6} {"로딩":>7} {"s_rep":>7}')
    for g, tags in GROUPS.items():
        rs = [rows[t] for t in tags if t in rows]
        if not rs:
            continue
        q = [r['Qst_CO2'] for r in rs]
        l = [r['loading_015bar'] for r in rs]
        sq = f'{stdev(q):.2f}' if len(q) > 1 else f'±{rs[0]["Qst_CO2_err"]:.2f}'
        sl = f'{stdev(l):.4f}' if len(l) > 1 else f'±{rs[0]["loading_015bar_err"]:.4f}'
        print(f'  {g:<10} {len(rs):>2} {mean(q):>7.2f} {sq:>6} {mean(l):>7.4f} {sl:>7}')
    print()

    # ---- T-C1 사다리
    print('== T-C1 사다리 (등록 문턱) ==')
    az = rows.get('azbIm100')
    bi = rows.get('bIm100')
    if az is None:
        print('  azbIm100 결과 없음 — T-C1 판정 불가')
        return 0

    def diff(a, b, label, thr):
        d = a['Qst_CO2'] - b['Qst_CO2']
        s = (a['Qst_CO2_err'] ** 2 + b['Qst_CO2_err'] ** 2) ** 0.5
        rank = '순위 가능' if abs(d) >= 1.5 * s else '순위 불가(1.5 단위 미만)'
        print(f'  {label:<26} {d:>+6.2f}  σ_diff {s:.2f}  문턱 {thr:+.0f}  '
              f'{"충족" if d >= thr else "미달"}  [{rank}]')

    diff(az, base, 'Q_st(az100) − base', 4)
    if bi is not None:
        diff(az, bi, 'Q_st(az100) − Q_st(bIm100)', 3)
        diff(bi, base, '(참고) Q_st(bIm100) − base', 0)
    else:
        print('  bIm100 결과 없음 — az100 − bIm100 항목 판정 불가')
    ld = az['loading_015bar']
    print(f'  {"로딩(az100, 0.15 bar)":<26} {ld:>6.4f} ± {az["loading_015bar_err"]:.4f}  문턱 1.0  '
          f'{"충족" if ld >= 1.0 else "미달"}')
    print('\n  주: 판정문은 사람이 씁니다. 하한 +3 은 1.5 단위 규칙의 여유이지 별도 문턱이 아닙니다.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
