"""다중 data 블록 CIF(CCDC 일괄 다운로드본)를 구조별로 분리해 압력별 PLD를 측정한다.

CCDC에서 여러 등재번호를 한 번에 받으면 .cif 하나에 data 블록이 여러 개 들어온다.
ASE의 read()는 기본적으로 첫 블록만 읽으므로, 그대로 재면 나머지 7개를 놓친다.

Moggach et al. Angew. Chem. 2009 (CCDC 739161-739168)의 블록 이름은 압력을 담고 있다:
    zf8000 = 0.00 GPa (상압) ... zf8147 = 1.47 GPa (ZIF-8-II, 게이트 열린 상)
"""
import os
import re
import subprocess
import sys
import tempfile

from ase.io import read, write

HERE = os.path.dirname(os.path.abspath(__file__))
PROBE_R = 1.82
PROBE_D = PROBE_R * 2
WORK = tempfile.mkdtemp()


def split_blocks(path):
    """data_ 블록 단위로 잘라 개별 CIF 파일로 저장하고 (블록명, 경로) 목록을 반환."""
    txt = open(path, encoding='utf-8', errors='ignore').read()
    parts = re.split(r'(?m)^(data_\S+)\s*$', txt)
    out = []
    for i in range(1, len(parts), 2):
        name = parts[i].replace('data_', '')
        body = parts[i] + '\n' + parts[i + 1]
        p = os.path.join(WORK, f'{name}.cif')
        open(p, 'w', encoding='utf-8').write(body)
        out.append((name, p))
    return out


def cif_field(path, *tags):
    txt = open(path, encoding='utf-8', errors='ignore').read()
    for t in tags:
        m = re.search(rf'{t}\s+(\S+)', txt)
        if m:
            return m.group(1)
    return None


def zeopp(cif):
    base = os.path.join(WORK, os.path.basename(cif).replace('.cif', '') + '_z')
    lcd = pld = av = vf = 0.0
    try:
        subprocess.run(['network', '-ha', '-res', base + '.res', cif],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        p = open(base + '.res').readline().split()
        lcd, pld = float(p[1]), float(p[2])
    except Exception:
        pass
    try:
        subprocess.run(['network', '-ha', '-vol', str(PROBE_R), str(PROBE_R), '20000',
                        base + '.vol', cif],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        t = open(base + '.vol').read()
        m = re.search(r'AV_A\^3:\s*([0-9.eE+-]+)', t)
        v = re.search(r'AV_Volume_fraction:\s*([0-9.eE+-]+)', t)
        if m:
            av = float(m.group(1))
        if v:
            vf = float(v.group(1))
    except Exception:
        pass
    return lcd, pld, av, vf


def main(src):
    blocks = split_blocks(src)
    print(f'{os.path.basename(src)} -> data 블록 {len(blocks)}개\n')
    print(f'N2 프로브 지름 {PROBE_D:.2f} A 기준\n')
    print(f'{"블록":<10} {"압력":>10} {"원자":>5} {"a(A)":>8} {"LCD":>7} {"PLD":>7} '
          f'{"PLD/a":>7} {"AV(A^3)":>9} {"VF":>7}  판정')
    print('-' * 100)

    rows = []
    for name, p in blocks:
        try:
            a = read(p)
        except Exception as e:
            print(f'{name:<10} 파싱 실패: {type(e).__name__}')
            continue
        # 레거시 대칭 태그로 변환해 Zeo++가 확실히 읽게 한다
        conv = os.path.join(WORK, name + '_p1.cif')
        write(conv, a)
        t = open(conv).read()
        for old, new in (('_space_group_name_H-M_alt', '_symmetry_space_group_name_H-M'),
                         ('_space_group_IT_number', '_symmetry_Int_Tables_number'),
                         ('_space_group_symop_operation_xyz', '_symmetry_equiv_pos_as_xyz')):
            t = t.replace(old, new)
        open(conv, 'w').write(t)

        cell = a.cell.cellpar()[0]
        lcd, pld, av, vf = zeopp(conv)
        press = cif_field(p, '_diffrn_ambient_pressure', '_cell_measurement_pressure')
        # 블록 이름에서 압력 추정 (zf8147 -> 1.47 GPa)
        m = re.search(r'zf8_?(\d+)', name)
        guess = ''
        if press is None and m:
            digits = m.group(1)
            if len(digits) == 3:
                guess = f'~{int(digits) / 100:.2f} GPa'
            elif len(digits) == 2:
                guess = f'~0.{digits} GPa'
        plabel = press if press else guess or '-'

        verdict = '*** 게이트 열림 ***' if pld >= PROBE_D else '닫힘'
        print(f'{name:<10} {plabel:>10} {len(a):>5} {cell:>8.3f} {lcd:>7.3f} {pld:>7.3f} '
              f'{pld / cell:>7.4f} {av:>9.1f} {vf:>7.4f}  {verdict}')
        rows.append((name, plabel, cell, pld, av, vf, conv))

    best = max(rows, key=lambda r: r[3]) if rows else None
    if best:
        print(f'\n>> 최대 PLD: {best[0]} ({best[1]}), PLD={best[3]:.3f} A, AV={best[4]:.1f} A^3')
        if best[4] > 0:
            dst = os.path.join(HERE, f'ZIF8_gateopen_{best[0]}.cif')
            import shutil
            shutil.copy(best[6], dst)
            print(f'>> 열린 상 구조를 저장했습니다: {dst}')


if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, '739161-739168.cif'))
