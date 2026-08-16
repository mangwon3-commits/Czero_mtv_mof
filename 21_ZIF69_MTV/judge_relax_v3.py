"""이완된 30종을 **바로잡은 기준**으로 다시 판정한다.

배치(`relax_series_v3.py`)는 돌면서 판정을 같이 찍는데, 그 판정의 ② 가 방향족
C-C 와 sp3 C-C 를 한 통에 넣는 버그를 갖고 있었습니다(`relax_criteria.py` 주석).
이완 자체는 멀쩡하고 결과 CIF 도 저장돼 있으므로, **다시 돌릴 필요 없이 읽어서
다시 재면 됩니다.** 몇 초 걸립니다.

배치가 끝난 뒤에 돌리세요. 아직 안 끝났으면 있는 것만 판정하고 남은 수를 알려 줍니다.
"""
import json
import os
import sys

from ase.io import read

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from relax_criteria import bonds, evaluate, min_distance   # noqa: E402

SRC = os.path.join(HERE, 'structures_v2')
OUT = os.path.join(HERE, 'relax_v3')
RESULT = os.path.join(HERE, 'relax_v3_judged.json')


def main():
    names = sorted(f[:-len('_relaxed.cif')] for f in os.listdir(OUT)
                   if f.endswith('_relaxed.cif'))
    if not names:
        print('  아직 이완된 구조가 없습니다.')
        return 1
    total = len([f for f in os.listdir(SRC) if f.endswith('.cif')])
    print(f'  판정 대상 {len(names)} / 전체 {total}\n')
    print(f'    {"구조":18s} {"C-H":>6} {"방향족C-C폭":>11} {"Zn-N":>15} '
          f'{"아릴-치환기":>16} {"최소":>6}  판정')

    rows, bad = [], []
    for n in names:
        before = read(os.path.join(SRC, f'{n}.cif'))
        after = read(os.path.join(OUT, f'{n}_relaxed.cif'))
        # 셀은 배치에서 이미 0.00e+00 으로 확인했지만, 파일에서 다시 잽니다.
        moved = float(abs(after.get_cell().array - before.get_cell().array).max())
        ok, num = evaluate(bonds(before), bonds(after), min_distance(after), moved)
        passed = all(ok.values())
        rows.append({'name': n, 'pass': passed, 'criteria': ok, **num})
        if not passed:
            bad.append((n, [k for k, v in ok.items() if not v]))
        sp3 = num['nonAromCC_range']
        print(f"    {n:18s} {num['CH_after']:6.3f} {num['aromCC_width_after']:11.4f} "
              f"{num['ZnN_min']:6.3f}~{num['ZnN_max']:.3f}({num['ZnN_pairs']:3d}) "
              f"{(f'{sp3[0]:.3f}~{sp3[1]:.3f}' if sp3 else '-'):>16} "
              f"{num['dmin']:6.3f}  {'통과' if passed else '실패'}")

    json.dump({'n': len(rows), 'failed': [b[0] for b in bad], 'rows': rows},
              open(RESULT, 'w'), indent=1, ensure_ascii=False)

    print()
    if bad:
        print(f'  !! 기준 미달 {len(bad)}종 — v3 GCMC 에 넣기 전에 개별로 봐야 합니다:')
        for n, which in bad:
            print(f'     {n}: {", ".join(which)}')
        return 2
    print(f'  {len(rows)}종 전부 통과. 다음: PACMAN 전하 -> charged_v3 -> GCMC 90')
    return 0


if __name__ == '__main__':
    sys.exit(main())
