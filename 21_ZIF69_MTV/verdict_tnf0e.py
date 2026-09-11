"""T-NF-0e 판정 — `TNF0E_REGISTRATION_20260911.md` §4 + §9 를 **그대로** 코드로 옮긴 것.

**최종값을 보기 전에 씁니다.** ZIF-90 팔만 끝났고 우리 3조성은 생산 중입니다.

    (A) 주 판정   R_A = 최종적재(100 %) / 최종적재(50 %)
                  R_A ≤ 1.15 이고 1.5x± 안  -> 수렴
                  R_A ≥ 2.0  이고 1.5x± 밖  -> 이력
                  그 사이                   -> 미결
    (B) 보조      T-NF-0d 대조 (3조성만)
    §9 퇴화       두 팔이 다 분해능 아래면 비 대신 **유지분율**로 "수렴".
                  한쪽만 0 이면 **이상**으로 기록하고 판정 안 함.
"""
import json, os, statistics as st, sys, glob

HERE = os.path.dirname(os.path.abspath(__file__))
# 상자 골격 질량 [g/mol] — 분자 수 환산용. 2x2x2 = 8 셀.
CELL_G = {'zif90': 3066.5, 'mbIm050': None, 'saIm050': None, 'nbIm050': None}
# T-NF-0d 최종값 (from-above, 160 적재) — TNF0D_VERDICT §1
TNF0D = {'mbIm050': 0.2327, 'nbIm050': 0.1079, 'saIm050': 0.3218}
# 분해능: T-NF-0d 물 로딩 ± 의 대표값
RESOL = 0.0015

ARMS = [('zif90',   'zif90e050',  'zif90e100',   338, 676),
        ('mbIm050', 'mb50e050',   'mb50e100',    652, 1305),
        ('saIm050', 'sa50e050',   'sa50e100',    695, 1391),
        ('nbIm050', 'nb50e050',   'nb50e100',    743, 1486)]


def arm(tag):
    """태그의 씨앗 건들을 모읍니다.

    **버리는 것 셋** — 전부 실제로 이 판에서 나왔습니다:
      ① `.SEEDDUP.json`   씨앗 충돌본 (같은 초 착수, 값이 모든 자리 동일)
      ② `.ABORTED*.json`  중단된 실행의 잔재
      ③ `status != 'ok'` 또는 `H2O_molkg is None`
         -> **14:39:02 에 죽인 실행이 `status: no-output` · 전부 None 인 파일을 남겼습니다.**
            거르지 않으면 판정기가 죽거나(초판이 그랬습니다) 0 으로 섞입니다.
    버린 것은 **세어서 보고**합니다 — 조용히 빠지면 n 이 줄어든 것을 못 봅니다.
    """
    out, dropped = [], []
    for f in sorted(glob.glob(os.path.join(HERE, f'tnf_results_{tag}_s*.json'))):
        b = os.path.basename(f)
        if 'meta' in b:
            continue
        if 'SEEDDUP' in b or 'ABORTED' in b:
            dropped.append((b, '치운 파일')); continue
        x = json.load(open(f, encoding='utf-8'))
        x = x[0] if isinstance(x, list) else x
        if x.get('H2O_molkg') is None or x.get('status') not in (None, 'ok'):
            dropped.append((b, f"status={x.get('status')} H2O={x.get('H2O_molkg')}")); continue
        out.append((x['H2O_molkg'], x.get('H2O_err'), x.get('seed'), b))
    return out, dropped


def agg(rows):
    if not rows:
        return None
    v = [r[0] for r in rows]
    e = [r[1] for r in rows if r[1] is not None]
    return {'mean': sum(v) / len(v), 'n': len(v),
            'pm': (sum(q * q for q in e) ** 0.5) / len(e) if e else None,
            'sd': st.stdev(v) if len(v) > 1 else 0.0,
            'seeds': [r[2] for r in rows],
            'seeds_ok': len({r[2] for r in rows}) == len(rows)}


def main():
    print('  ═══ T-NF-0e · 포화 근처 적재 탈착 ═══\n')
    ok_all = True
    for name, t50, t100, p50, p100 in ARMS:
        r50, d50 = arm(t50); r100, d100 = arm(t100)
        for b, why in d50 + d100:
            print(f'  [제외] {b}  ({why})')
        a50, a100 = agg(r50), agg(r100)
        if not (a50 and a100):
            have = f"50%={a50['n'] if a50 else 0} 100%={a100['n'] if a100 else 0}"
            print(f'  {name:9s} — 결과 부족 ({have})'); ok_all = False; continue
        print(f'  ── {name} ──')
        for lab, a, pre in (('50 %', a50, p50), ('100 %', a100, p100)):
            flag = '' if a['seeds_ok'] else '  **씨앗 충돌**'
            print(f'   적재 {lab:5s} ({pre:4d}) n={a["n"]}  최종 **{a["mean"]:.6f}** mol/kg'
                  f'  ± {a["pm"]:.6f}  실행SD {a["sd"]:.6f}{flag}')
            if not a['seeds_ok']:
                ok_all = False
        comb = ((a50['pm'] or 0) ** 2 + (a100['pm'] or 0) ** 2) ** 0.5
        d = abs(a100['mean'] - a50['mean'])
        # §9 퇴화 처리 — 비보다 먼저 봅니다
        lo50, lo100 = a50['mean'] < RESOL, a100['mean'] < RESOL
        if lo50 and lo100:
            print(f'   §9 퇴화: 두 팔 다 분해능({RESOL}) 아래 -> **수렴**')
        elif lo50 != lo100:
            print(f'   §9 이상: **한쪽만 0** (50%={a50["mean"]:.6f} 100%={a100["mean"]:.6f})'
                  f' -> **판정 안 함**')
        else:
            R = a100['mean'] / a50['mean']
            u = d / comb if comb else float('inf')
            print(f'   **R_A = {R:.3f}**   차이 {d:.6f} = **{u:.2f} 단위** (문턱 1.5)')
            if R <= 1.15 and d <= 1.5 * comb:
                print('   -> **수렴** — 출발점과 무관한 유일 평형')
            elif R >= 2.0 and d > 1.5 * comb:
                print('   -> **이력 현상** — 응축 상이 힘장 안에서 안정/준안정')
            else:
                print('   -> **미결**')
        if name in TNF0D:
            print(f'   (B) T-NF-0d(160 적재) {TNF0D[name]:.4f} 대비: '
                  f'50% {a50["mean"]/TNF0D[name]:.3f} · 100% {a100["mean"]/TNF0D[name]:.3f}')
        print()
    print('  ── 종합 (§4) ──')
    print('  네 대상 전부 수렴 -> 협동 채움 갈래 **완전 배제**')
    print('  하나라도 이력     -> TNF0D 의 평형은 **저적재 가지에 한정**')
    print('  섞이면            -> **조성마다 다름**, 어느 조성인지 명시')
    return 0 if ok_all else 1


if __name__ == '__main__':
    sys.exit(main())
