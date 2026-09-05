"""T-B1 완주 출력에서 ΔH_vap 을 낸다. 덱·판정은 COMMS/laptop.md 09-04 19:5x~20:2x 등록분.

    ΔH_vap = -<U_inter>/N + RT      RT(298.15 K) = 2.4790 kJ/mol
    ① raw   ② raw+절단(+0.212)   ③ raw-E_pol(-3.983)   ④ raw+절단-E_pol(-3.771)
    판정은 ①과 ④ 에 대해 |ΔH_vap - 44| >= 3  (ASSIGN_20260904 §3-1, 730859d)
"""
import re, sys, glob, os, math

K_TO_KJ = 0.00831446261815324
RT      = 8.314462618 * 298.15 / 1000.0
TRUNC   = +0.2125      # 문헌 관례로 옮길 때 더함
E_POL   = 3.983        # 보정 시 뺌
REF, TOL = 44.0, 3.0
CTL_LO, CTL_HI = 40.0, 48.0   # 대조 단일 창 (09-05 13:4x 등록, COMMS/laptop.md:1862)

def parse_energy(txt):
    """`Average Adsorbate-Adsorbate energy:` 절에서 5블록·평균·± 를 뽑는다 [K].

    실제 형식(완료된 RASPA 출력에서 확인, 09-05):
        Average Adsorbate-Adsorbate energy:
        ===================================
        \tBlock[ 0] -12621.25084   Van der Waals: ...  Coulomb: ...  [K]
        ...
        \t------------------------------------------------
        \tAverage   -13016.70475   Van der Waals: ...   Coulomb: ...  [K]
        \t      +/- 777.56727            +/- ...             +/- ...   [K]
    """
    m = re.search(r'Average Adsorbate-Adsorbate energy:\s*\n=+\n(.*?)\n\s*\n', txt, re.S)
    if not m:
        return None, None, []
    blk = m.group(1)
    blocks = [float(x) for x in re.findall(r'Block\[\s*\d+\]\s+(-?[\d.eE+]+)', blk)]
    avg = re.search(r'Average\s+(-?[\d.eE+]+)', blk)
    err = re.search(r'\+/-\s+([\d.eE+]+)', blk)
    return (float(avg.group(1)) if avg else None,
            float(err.group(1)) if err else None, blocks)


def grab(txt, pat):
    m = re.findall(pat, txt)
    return [float(x) for x in m] if m else []


def main(path=None):
    if path is None:
        # ⚠️ 09-05: 실행이 둘이 됐습니다(`tb1_runs_n1000` 본 실행, `tb1_runs_ffctl` 대조).
        #    원래 글롭은 `tb1_runs_n*` 라 **대조를 못 잡고 본 실행을 조용히 집었습니다.**
        #    넓히면 이번엔 **둘 중 아무거나 조용히 집습니다.** 둘 다 나쁩니다.
        #    -> 하나면 쓰고, 둘 이상이면 **거부하고 목록을 보여 줍니다.**
        #       (`scope_report.py` 와 같은 규율: 막지 말고 말하게 하되, 애매하면 멈춘다)
        c = sorted(glob.glob('tb1_runs_*/hvap/Output/System_0/*.data'))
        if not c:
            print('출력 없음 — `tb1_runs_*/hvap/Output/System_0/*.data` 가 비었습니다')
            return 1
        if len(c) > 1:
            print(f'  실행이 **{len(c)}개** 잡혔습니다. 어느 것인지 인자로 주십시오:')
            for f in c:
                print(f'    python tb1_analyze.py {f}')
            return 2
        path = c[0]
    txt = open(path, encoding='utf-8', errors='replace').read()
    print(f'출력 {path}\n')

    U_K, dU_K, blocks = parse_energy(txt)
    vol  = grab(txt, r'Average Volume:\s*([\d.]+)')
    box  = grab(txt, r'Average Box:\s*([\d.]+)')
    boxc = grab(txt, r'Current Box:\s*([\d.]+)')
    nmol = grab(txt, r'current number of integer/fractional/reaction molecules:\s*(\d+)')

    if U_K is None:
        print('  !! 에너지 절을 못 찾았습니다 — 완주 전이거나 형식이 다릅니다')
        for ln in [l for l in txt.splitlines() if 'Adsorbate-Adsorbate' in l][-3:]:
            print('   ', ln.strip()[:120])
        return 2

    N   = next((int(x) for x in nmol if int(x) > 0), 0)
    if N <= 0:
        print(f'  !! 분자 수를 못 읽었습니다 (후보 {nmol[:3]}). 이 출력은 T-B1 이 아닙니다.')
        print(f'     참고로 에너지 파싱은 성공: <U> {U_K:.4f} ± {dU_K:.4f} K, 5블록 {len(blocks)}개')
        return 3
    U   = U_K * K_TO_KJ / N          # kJ/mol/분자
    dU  = (dU_K or 0.0) * K_TO_KJ / N
    V   = vol[-1] if vol else float('nan')
    raw = -U + RT

    print(f'  N {N}   <V> {V:.2f} Å³   T 298.15 K   RT {RT:.4f} kJ/mol')
    print(f'  <U_inter> {U_K:.2f} ± {dU_K:.2f} K  ->  <U>/N = {U:.4f} ± {dU:.4f} kJ/mol')
    print(f'  5블록 [K]: ' + ' '.join(f'{b:.1f}' for b in blocks))
    print(f'\n  ① raw                    {raw:8.3f} ± {dU:.3f} kJ/mol')
    print(f'  ② raw + 절단({TRUNC:+.3f})   {raw+TRUNC:8.3f}')
    print(f'  ③ raw − E_pol({E_POL:.3f})   {raw-E_POL:8.3f}')
    print(f'  ④ 둘 다                  {raw+TRUNC-E_POL:8.3f}')

    print(f'\n  [충분성 점검] 5블록 ± = {dU:.4f} kJ/mol  (문턱 0.3)  -> '
          f'{"통과" if dU <= 0.3 else "**미달 — 연장 필요, 연장 사실을 판정문에 기재**"}')

    if boxc:
        import statistics as st
        tail = boxc[len(boxc)//2:]
        m, sd = st.mean(tail), st.pstdev(tail)
        print(f'  [최소 이미지] <L> {m:.4f} ± σ {sd:.4f}  ->  <L>−3σ = {m-3*sd:.4f} '
              f'(하한 24)  -> {"통과" if m-3*sd > 24 else "**미달**"}   표본 {len(tail)}')

    # --- 덱 선택 -------------------------------------------------------------
    # 09-06: 두 실행의 **등록 덱이 다릅니다.** 여기서 자동으로 고르되 **이름을 인쇄**합니다.
    #   본 실행 `tb1_runs_n1000`  : ①/④ 두 조합에 |x−44| ≥ 3   (09-04 19:5x~20:2x 등록)
    #   대조   `tb1_runs_ffctl`   : raw 단일 창 40~48 + 구조 3창 (09-05 13:4x 등록)
    # 이 분기가 없던 판이 대조에 본 실행 덱을 대어 **없는 "보류" 를 인쇄**했습니다
    # (TB1_VERDICT_20260905.md §4-1 의 붉은 상자).
    deck = os.environ.get('TB1_DECK') or ('ctl' if 'ffctl' in os.path.abspath(path) else 'main')
    if deck == 'ctl':
        print(f'\n  판정 [덱 = **대조** — 09-05 13:4x 등록, raw 단일 창 40~48]')
        print( '    ⚠️ 대조의 **주 판정은 구조 3창**입니다. 아래는 **부(열역학)** 뿐입니다.')
        ok = CTL_LO <= raw <= CTL_HI
        print(f'    ΔH_vap(raw) {raw:.3f}   창 {CTL_LO:g} ~ {CTL_HI:g}  ->  '
              f'{"**안** — 갈래 (가) 쪽" if ok else "**밖** — 갈래 (나) 쪽"}')
        print( '    (①/④ 덱은 대조에 등록된 적이 없습니다. 섞어 읽지 마십시오.)')
    else:
        print(f'\n  판정 [덱 = **본 실행** — 09-04 등록, |x−44| ≥ 3 이면 문구 교체]')
        for lab, x in (('①', raw), ('④', raw+TRUNC-E_POL)):
            d = abs(x - REF)
            print(f'    {lab} |{x:.3f} − 44| = {d:.3f}  ->  {"교체" if d>=TOL else "유지"}')
        a, b = abs(raw-REF) >= TOL, abs(raw+TRUNC-E_POL-REF) >= TOL
        print(f'\n  => ' + (f'두 축 일치: {"교체" if a else "유지"}' if a == b
                            else '**두 축이 갈림 -> 기준 미확정, 판정 보류 (저장소 문구 불변)**'))
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else None))
