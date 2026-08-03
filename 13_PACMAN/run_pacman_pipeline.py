"""닫힌 상 구조에 PACMAN(DDEC6) 전하를 부여하고 RASPA 재계산 입력을 준비한다.

배경:
    EQeq는 니트로기의 전하 분리를 제대로 재현하지 못한다. 실측 비교(nIm 50% 구조):
        니트로 N 최대전하   EQeq +0.025  ->  PACMAN +0.590
        니트로 O 평균전하   EQeq -0.124  ->  PACMAN -0.278
    즉 이 프로젝트의 핵심 EWG인 NO2의 정전기 효과가 EQeq에서는 거의 사라진다.
    PACMAN은 DDEC6(양자계산 기반)를 ML로 재현하므로 이 문제를 해결한다.

[주의] PACMAN의 predict()는 부작용으로 '입력 CIF 자체를 정규화해 덮어쓴다'.
    원본을 잃지 않도록 반드시 작업 사본에서 실행할 것 (이 스크립트가 그렇게 한다).

[주의] PACMAN 출력 CIF는 _symmetry_* 구형 태그를 이미 쓰므로 RASPA/Zeo++와
    바로 호환된다. 다만 data_ 블록 이름이 <파일명>_pacman 으로 바뀌므로
    RASPA의 FrameworkName과 파일명을 일치시켜야 한다.
"""
import glob
import os
import shutil
import sys
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, '..', '07_Bracketed_MTV')
OUT = os.path.join(HERE, 'structures')


def charge_summary(path):
    lines = open(path, encoding='utf-8').read().split('\n')
    tags = [i for i, l in enumerate(lines) if l.strip().startswith('_atom_site')]
    if not tags:
        return None
    names = [lines[i].strip() for i in tags]
    ci = [i for i, n in enumerate(names) if 'charge' in n]
    if not ci:
        return None
    ci = ci[0]
    si = names.index('_atom_site_type_symbol')
    d = defaultdict(list)
    for l in lines[tags[-1] + 1:]:
        s = l.split()
        if len(s) <= max(ci, si):
            continue
        try:
            d[s[si]].append(float(s[ci]))
        except ValueError:
            continue
    return d


def main():
    from PACMANCharge import pmcharge
    os.makedirs(OUT, exist_ok=True)

    # 닫힌 상만 -- 0.15 bar에서 실제로 존재하는 상이다
    srcs = sorted(glob.glob(os.path.join(SRC, '*__closed.cif')))
    print(f'대상: 닫힌 상 {len(srcs)}개\n')

    rows = []
    for s in srcs:
        name = os.path.basename(s).replace('__closed.cif', '')
        work = os.path.join(OUT, name + '.cif')
        shutil.copy(s, work)          # 사본에서 작업 (PACMAN이 입력을 덮어씀)

        eq = charge_summary(s)
        try:
            pmcharge.predict(cif_file=work, charge_type='DDEC6', digits=6,
                             atom_type=True, neutral=True, keep_connect=False)
        except Exception as e:
            print(f'  [실패] {name}: {type(e).__name__}: {e}')
            continue

        pac_file = work.replace('.cif', '_pacman.cif')
        if not os.path.exists(pac_file):
            print(f'  [실패] {name}: 출력 없음')
            continue
        # RASPA FrameworkName과 맞추기 위해 최종 파일명을 정리
        final = os.path.join(OUT, name + '_DDEC6.cif')
        os.replace(pac_file, final)
        os.remove(work)

        pc = charge_summary(final)
        row = {'name': name}
        for el in ('N', 'O', 'Cl', 'Zn'):
            if eq and el in eq:
                row[f'eq_{el}_max'] = max(eq[el])
                row[f'eq_{el}_mean'] = sum(eq[el]) / len(eq[el])
            if pc and el in pc:
                row[f'pac_{el}_max'] = max(pc[el])
                row[f'pac_{el}_mean'] = sum(pc[el]) / len(pc[el])
        rows.append(row)

        tot = sum(sum(v) for v in pc.values())
        nmax_e = f"{max(eq['N']):+.3f}" if eq and 'N' in eq else '-'
        nmax_p = f"{max(pc['N']):+.3f}" if pc and 'N' in pc else '-'
        omean_e = f"{sum(eq['O'])/len(eq['O']):+.3f}" if eq and 'O' in eq else '-'
        omean_p = f"{sum(pc['O'])/len(pc['O']):+.3f}" if pc and 'O' in pc else '-'
        print(f'  [OK] {name:<26} 전하합 {tot:+.4f} | '
              f'N최대 {nmax_e}->{nmax_p} | O평균 {omean_e}->{omean_p}')

    print(f'\n[OK] {OUT} 에 DDEC6 전하 구조 저장')
    return 0


if __name__ == '__main__':
    sys.exit(main())
