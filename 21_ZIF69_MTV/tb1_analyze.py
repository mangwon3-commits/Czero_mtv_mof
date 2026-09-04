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

def grab(txt, pat):
    m = re.findall(pat, txt)
    return [float(x) for x in m] if m else []

def main(path=None):
    if path is None:
        c = sorted(glob.glob('tb1_runs_n*/hvap/Output/System_0/*.data'),
                   key=os.path.getmtime)
        if not c: print('출력 없음'); return 1
        path = c[-1]
    txt = open(path, encoding='utf-8', errors='replace').read()
    print(f'출력 {path}\n')

    # 평균 분자간 에너지 [K] — RASPA 는 Adsorbate-Adsorbate 로 찍는다
    tot = grab(txt, r'Average Adsorbate-Adsorbate energy:\s*\n?\s*-*\s*\n?.*?Total\s+([-\d.]+)')
    if not tot:
        blk = re.search(r'Average Adsorbate-Adsorbate energy:(.{0,4000}?)Average Host-Host', txt, re.S)
        if blk: tot = grab(blk.group(1), r'Total\s+([-\d.eE+]+)')
    vol = grab(txt, r'Average Volume:\s*([\d.]+)')
    box = grab(txt, r'Average Box:\s*([\d.]+)')
    nmol = grab(txt, r'current number of integer/fractional/reaction molecules:\s*(\d+)')
    print(f'  파싱: U 후보 {len(tot)}개 · V {len(vol)}개 · Box {len(box)}개 · N {nmol[:1]}')
    if not tot or not vol:
        print('  !! 자동 파싱 실패 — 아래 후보를 눈으로 확인하십시오')
        for pat in ('Average Adsorbate-Adsorbate','Average Volume','Average Box'):
            for ln in [l for l in txt.splitlines() if pat in l][-3:]:
                print('   ', ln.strip()[:140])
        return 2
    N  = int(nmol[0]) if nmol else 1000
    U  = tot[-1] * K_TO_KJ          # kJ/mol (전체 상자)
    V  = vol[-1]
    L  = box[-1] if box else V ** (1/3)
    raw = -U / N + RT
    print(f'\n  N {N}   <V> {V:.2f} Å³   <L> {L:.4f} Å   T 298.15 K   RT {RT:.4f}')
    print(f'  <U_inter> {tot[-1]:.2f} K = {U:.3f} kJ/mol   ->  <U>/N = {U/N:.4f} kJ/mol')
    print(f'\n  ① raw                    {raw:8.3f} kJ/mol')
    print(f'  ② raw + 절단({TRUNC:+.3f})   {raw+TRUNC:8.3f}')
    print(f'  ③ raw − E_pol({E_POL:.3f})   {raw-E_POL:8.3f}')
    print(f'  ④ 둘 다                  {raw+TRUNC-E_POL:8.3f}')
    print(f'\n  판정 (|x−44| ≥ 3 이면 문구 교체)')
    for lab, x in (('①', raw), ('④', raw+TRUNC-E_POL)):
        d = abs(x - REF)
        print(f'    {lab} |{x:.3f} − 44| = {d:.3f}  ->  {"교체" if d>=TOL else "유지"}')
    a, b = abs(raw-REF) >= TOL, abs(raw+TRUNC-E_POL-REF) >= TOL
    print(f'\n  => {"두 축 일치: " + ("교체" if a else "유지") if a==b else "**두 축이 갈림 -> 기준 미확정, 판정 보류 (문구 불변)**"}')
    return 0

if __name__ == '__main__':
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else None))
