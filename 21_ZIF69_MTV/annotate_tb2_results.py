"""T-B2 결과 JSON 에 병기를 **파일 안에** 박습니다.

[왜] 병기를 판정문에만 적으면 **인용할 때 떨어져 나갑니다.** 그리고 러너를
     고쳐도 **이미 만들어진 출력은 그대로**입니다(랩탑 09-05 지적).

[박는 것]
     ① 물 힘장 결함 — `UFF_MOF` 혼합규칙에 `Hw` 항이 없어 RASPA 가 앞자리
        일치로 `H_`(UFF 수소, eps 22.1417 / sigma 2.57113)를 물려줬습니다.
        **TIP5P 수소는 LJ 가 없어야 합니다.** 이 값들은 **수소결합이 없는
        물**로 잰 것입니다. `WATER_FF_CONFIRM_20260905.md`
     ② 출력이 진행을 안 보여 줌 — `PrintEvery = NumberOfCycles` 라 실행
        중에는 `.data` 가 안 자랍니다. **살아 있음의 판정에 쓰지 마십시오**
        (`pgrep -x simulate` 개수와 `ps -o time` 을 쓰십시오).
     ③ `cycles` 배열 -> 키 이름. 배열은 어느 쪽이 초기화인지 안 알려 줍니다.

[안 하는 것] **측정값은 건드리지 않습니다.** 주석만 더합니다.

사용:  python3 annotate_tb2_results.py v3_water_kh/*.json
"""
import json, sys

WARN_FF = ('물 힘장 결함: UFF_MOF 혼합규칙에 Hw 항이 없어 RASPA 가 앞자리 '
           '일치로 H_(UFF 수소, eps 22.1417 K / sigma 2.57113 A)를 물려줬다. '
           'TIP5P 수소는 LJ 가 없어야 한다. **이 K_H 는 수소결합이 없는 물로 '
           '잰 값이다.** 확인: 출력 머리말 Hw-Hw p_0/k_B = 22.14170. '
           '근거 문서 WATER_FF_CONFIRM_20260905.md / WATER_FF_DEFECT_20260905.md')
WARN_PRINT = ('이 실행의 출력은 진행을 보여 주지 않는다: PrintEvery = '
              'NumberOfCycles 라 .data 가 처음과 끝에만 쓰인다. 실행 중 '
              '.data 정지는 정상이며 죽음의 신호가 아니다(완주한 실행에서 '
              '25분 침묵 확인). 살아 있음은 `pgrep -x simulate` 개수와 '
              '`ps -o etime,time` 의 CPU 시간 증가로 본다.')


def fix(p):
    d = json.load(open(p, encoding='utf-8'))
    ch = []
    if 'cycles' in d and isinstance(d['cycles'], list) and len(d['cycles']) == 2:
        init, cyc = d.pop('cycles')
        d['NumberOfInitializationCycles'] = init
        d['NumberOfCycles'] = cyc
        ch.append(f'cycles{[init, cyc]} -> 키 이름')
    if d.get('WARN_forcefield') != WARN_FF:
        d['WARN_forcefield'] = WARN_FF
        ch.append('WARN_forcefield')
    if d.get('WARN_output') != WARN_PRINT:
        d['WARN_output'] = WARN_PRINT
        ch.append('WARN_output')
    if ch:
        json.dump(d, open(p, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
    print(f'{p}: {", ".join(ch) if ch else "변경 없음"}')


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print(__doc__); sys.exit(2)
    for p in sys.argv[1:]:
        fix(p)
