"""수분 경쟁 결과 배치 병합·판정 — 기기별 출처를 지키면서.

[왜 필요한가]
    격자 16작업이 여러 기기에 흩어졌습니다. 그런데 러너는 전부 같은
    `v3_water_grid/water_results.json` 경로에 씁니다. 기기별 파일을 그냥
    복사해 덮으면 **먼저 있던 행이 조용히 사라집니다.** 그리고 사라진 것을
    알아챌 방법이 없습니다 — 파일은 멀쩡해 보입니다.

    NEW_MACHINE_20260822.md 5 절이 "사람이 합친다"고 한 것은 그래서입니다.
    이 도구는 그 병합을 **사람이 검산할 수 있게** 만듭니다. 자동으로
    합치지 않습니다 — 합쳐도 되는지 검사하고, 안 되면 이유를 댑니다.

[무엇을 하나]
    1. 기기별 결과 파일을 읽어 (조성, RH) 마다 출처를 붙입니다
    2. 같은 (조성, RH) 이 두 기기에서 나오면 **덮지 않고 교차 검증 쌍**으로
       분리합니다 — 그것이 원래 하려던 빌드 대조입니다
    3. 사전 등록된 수분 관문을 적용합니다 (유지율 >=80 유효 / 50~80 조건부
       / <50 종료). **유지율만 쓰면 결론이 거꾸로 읽히므로 절대 로딩을
       반드시 병기합니다** — 비율이라 분모가 조성마다 크게 다릅니다
    4. 세대(v2/v3/격자)를 섞으려 하면 거부합니다

[유지율 σ 의 정의]
    run_water.py:325 와 **같은 정의**를 씁니다. 비율의 오차가 아니라
    RH90 로딩이 RH0 로딩과 다르다는 것의 유의도입니다:

        sigma = |c_rh90 - c_rh0| / sqrt(sigma_rh90^2 + sigma_rh0^2)

    새 정의를 만들지 않았습니다. 기존 결과와 같은 축에 놓으려면 같은 자를
    써야 합니다.

사용:
    python merge_water_batches.py --selftest
    python merge_water_batches.py v3_water_grid/water_results_cloud4c.json \\
                                  v3_water_grid/water_results_desktop16.json
"""
import argparse
import json
import math
import os
import sys

# 사전 등록된 수분 관문. 결과를 보고 고치지 않습니다.
GATE = ((80.0, '유효'), (50.0, '조건부'), (0.0, '노선 종료'))

# 세대가 다르면 섞을 수 없습니다 (CLAUDE.md 2 절).
GENERATION_HINTS = (('v2_water', 'v2'), ('v3_water_grid', 'v3격자'), ('v3_water', 'v3'))


def generation_of(path):
    for frag, gen in GENERATION_HINTS:
        if frag in path.replace(os.sep, '/'):
            return gen
    return '알수없음'


def machine_of(path):
    """파일명 끝의 기기 이름. water_results_cloud4c.json -> cloud4c."""
    base = os.path.basename(path)
    stem = base[:-len('.json')] if base.endswith('.json') else base
    if stem.startswith('water_results_'):
        return stem[len('water_results_'):]
    return stem


def load(path):
    with open(path, encoding='utf-8') as f:
        rows = json.load(f)
    if not isinstance(rows, list):
        raise SystemExit(f'{path}: 리스트가 아닙니다 ({type(rows).__name__})')
    return rows


def retention(c_rh90, e_rh90, c_rh0, e_rh0):
    """run_water.py:325 와 같은 정의."""
    if not c_rh0:
        return float('nan'), float('nan')
    pct = c_rh90 / c_rh0 * 100.0
    den = math.sqrt(e_rh90 ** 2 + e_rh0 ** 2)
    sig = abs(c_rh90 - c_rh0) / den if den else float('nan')
    return pct, sig


def verdict(pct):
    for lo, name in GATE:
        if pct >= lo:
            return name
    return '판정불가'


def collect(paths):
    """(조성, RH) -> {기기: 행}. 충돌을 덮지 않고 모읍니다."""
    table, gens = {}, {}
    for p in paths:
        gen = generation_of(p)
        gens.setdefault(gen, []).append(p)
        mach = machine_of(p)
        for r in load(p):
            table.setdefault((r['name'], r['RH']), {})[mach] = r
    return table, gens


def main():
    ap = argparse.ArgumentParser(description='수분 경쟁 배치 병합·판정')
    ap.add_argument('files', nargs='*', help='기기별 water_results_<기기>.json')
    ap.add_argument('--selftest', action='store_true',
                    help='기존 v3_water/water_results.json 으로 자기 검증')
    a = ap.parse_args()

    if a.selftest:
        return selftest()
    if not a.files:
        ap.error('파일을 주거나 --selftest 를 쓰세요')

    table, gens = collect(a.files)

    if len(gens) > 1:
        print('!! 세대가 섞였습니다. 병합을 거부합니다 (CLAUDE.md 2 절):')
        for g, ps in sorted(gens.items()):
            print(f'   {g}: {", ".join(ps)}')
        return 1

    dup = {k: v for k, v in table.items() if len(v) > 1}
    names = sorted({n for n, _ in table})

    print(f'조성 {len(names)}종 · 점 {len(table)}개 · 파일 {len(a.files)}개')
    print(f'세대 {list(gens)[0]}')
    if dup:
        print(f'\n교차 검증 쌍 {len(dup)}개 — 덮지 않고 분리했습니다')
        print(f'{"조성":<12} {"RH":>5} {"기기":<22} {"CO2 [mol/kg]":>20} {"편차":>8}')
        print('-' * 72)
        for (n, rh), by in sorted(dup.items()):
            ms = sorted(by)
            vals = [(m, by[m]['CO2_molkg'], by[m].get('CO2_err', 0.0)) for m in ms]
            for m, c, e in vals:
                print(f'{n:<12} {int(rh*100):>4}% {m:<22} {c:>11.4f} ± {e:<6.4f}')
            (m1, c1, e1), (m2, c2, e2) = vals[0], vals[1]
            den = math.sqrt(e1 ** 2 + e2 ** 2)
            s = abs(c1 - c2) / den if den else float('nan')
            flag = '일관' if s < 2.0 else ('조건부' if s < 3.0 else '불일치')
            print(f'{"":<12} {"":>5} {"-> 편차":<22} {"":>20} {s:>7.2f}σ  {flag}')
        print('\n등록된 문턱: <2.0σ 일관 / 2.0~3.0σ 조건부 / >=3.0σ 불일치')
        print('(COMMS/desktop.md 13:55 항목. 수를 보고 고치지 않습니다.)')

    print(f'\n{"조성":<12} {"출처":<14} {"RH0 CO2":>18} {"RH90 CO2":>18} '
          f'{"유지율":>9} {"유의도":>8}  판정')
    print('-' * 98)
    rc = 0
    for n in names:
        def pick(rh):
            """쌍이면 알파벳 첫 기기. 어느 기기였는지와 미해소 여부를 함께 돌려준다.

            [2026-08-22] 원래는 값만 돌려주고 출처를 안 적었다. 그러면 표만 읽는
            사람은 그것이 어느 기기 값인지도, 쌍이 아직 안 맞은 상태인지도
            알 수 없다. 더 나쁜 것은 쌍이 조건부/불일치인데도 관문 판정이
            찍혀 나온다는 것 -- 화해되지 않은 수로 채운 칸이 완성된 칸처럼
            보인다. 이 저장소가 반복해서 데인 유형이라 판정을 보류로 바꾼다.
            """
            by = table.get((n, rh))
            if not by:
                return None
            ms = sorted(by)
            r = by[ms[0]]
            unresolved = False
            if len(ms) > 1:
                c1, e1 = by[ms[0]]['CO2_molkg'], by[ms[0]].get('CO2_err', 0.0)
                c2, e2 = by[ms[1]]['CO2_molkg'], by[ms[1]].get('CO2_err', 0.0)
                den = math.sqrt(e1 ** 2 + e2 ** 2)
                unresolved = den and abs(c1 - c2) / den >= 2.0
            return r['CO2_molkg'], r.get('CO2_err', 0.0), ms[0], len(ms) > 1, unresolved
        p0, p90 = pick(0.0), pick(0.9)
        if not p0 or not p90:
            print(f'{n:<12} {"RH0 또는 RH90 없음 — 유지율 계산 불가":>60}')
            rc = 1
            continue
        pct, sig = retention(p90[0], p90[1], p0[0], p0[1])
        src = p0[2] if p0[2] == p90[2] else f'{p0[2]}/{p90[2]}'
        if p0[3] or p90[3]:
            src += '*'
        if p0[4] or p90[4]:
            note = '보류(쌍 미해소)'
            rc = 1
        else:
            note = verdict(pct)
        print(f'{n:<12} {src:<14} {p0[0]:>11.4f} ± {p0[1]:<5.4f} '
              f'{p90[0]:>11.4f} ± {p90[1]:<5.4f} '
              f'{pct:>8.1f}% {sig:>7.2f}σ  {note}')
    if any(len(v) > 1 for v in table.values()):
        print('\n* = 그 점에 교차 검증 쌍이 있습니다. 표의 값은 알파벳 첫 기기 것이고,')
        print('  쌍이 2.0σ 이상 벌어졌으면 판정을 내지 않고 보류로 적습니다.')
    print('\n유지율은 비율이라 분모가 조성마다 다릅니다 — 위 표의 절대 로딩과')
    print('반드시 함께 읽으세요. 유지율만 인용하면 결론이 거꾸로 읽힙니다.')
    return rc


def selftest():
    """기존 v3_water 20행으로 검증. 저장된 값을 재현해야 통과."""
    p = 'v3_water/water_results.json'
    if not os.path.exists(p):
        print(f'!! {p} 가 없어 자기 검증을 건너뜁니다')
        return 1
    rows = load(p)
    by = {(r['name'], r['RH']): r for r in rows}
    bad = 0
    print(f'자기 검증 — {p} {len(rows)}행')
    print(f'{"조성":<12} {"RH":>5} {"저장된 유지율":>14} {"재계산":>12} {"저장 σ":>9} {"재계산 σ":>10}')
    print('-' * 70)
    for (n, rh), r in sorted(by.items()):
        base = by.get((n, 0.0))
        if not base:
            continue
        pct, sig = retention(r['CO2_molkg'], r.get('CO2_err', 0.0),
                             base['CO2_molkg'], base.get('CO2_err', 0.0))
        sp, ss = r.get('CO2_retention_pct'), r.get('retention_sigma')
        ok = (sp is None or abs(pct - sp) < 1e-6) and (ss is None or abs(sig - ss) < 1e-6)
        if not ok:
            bad += 1
        mark = '' if ok else '   <-- 불일치'
        print(f'{n:<12} {int(rh*100):>4}% {sp:>13.4f}% {pct:>11.4f}% '
              f'{ss:>8.4f} {sig:>9.4f}{mark}')
    print()
    if bad:
        print(f'!! {bad}개 불일치 — 유지율·σ 정의가 러너와 다릅니다. 쓰지 마세요.')
        return 1
    print(f'통과 — {len(rows)}행 전부 저장된 유지율·σ 를 재현했습니다.')
    print('러너(run_water.py:325)와 같은 정의를 쓰고 있음이 확인됐습니다.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
