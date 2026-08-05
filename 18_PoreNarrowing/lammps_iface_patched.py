"""lammps-interface의 초원자가 황 타이핑 버그를 우회하는 래퍼.

증상:
    -SO3H 를 포함한 구조에서 lammps-interface가 KeyError: 'S_3' 로 죽는다.

원인:
    UFF의 황 원자 타입은 산화수를 명시한 S_3+2 / S_3+4 / S_3+6 뿐이고 'S_3'라는
    이름은 존재하지 않는다(UFF_DATA, UFF4MOF_DATA 어느 쪽에도 없다). 그런데
    lammps-interface의 원자 타이핑 루틴이 4배위 황에 'S_3'를 붙여버린다.
    즉 파라미터가 없는 게 아니라 이름을 잘못 짓는 것이다.

수정:
    술폰산의 황은 산소 3개 + 탄소 1개로 사면체(109.47도)를 이루는 6가 황이므로
    UFF 규약상 정확히 S_3+6 에 해당한다. 그 파라미터를 'S_3' 키로 별칭 등록한다.
    LJ 항(sigma 4.035, eps 0.274)은 S_3+2/+4/+6 이 모두 동일하고 결합 반지름과
    각도만 다르므로, 이 매핑은 흡착 계산에 쓰는 비결합 항에는 애초에 영향이 없고
    이완 단계의 결합 기하만 올바르게 잡아준다.

사용법은 lammps-interface CLI와 동일하다.
"""
import sys

from lammps_interface.uff import UFF_DATA
from lammps_interface.uff4mof import UFF4MOF_DATA

# 술폰산 황 = 6가 사면체 황
for table in (UFF_DATA, UFF4MOF_DATA):
    if 'S_3' not in table and 'S_3+6' in table:
        table['S_3'] = table['S_3+6']

from lammps_interface.cli import main  # noqa: E402  (패치 후 임포트해야 한다)


# ---------------------------------------------------------------------------
# [2026-08-06 추가] 축퇴 이면각 제거
#
# 증상:
#     ERROR on proc 0: Invalid atom ID in Dihedrals section of data file:
#       23   4   5   4   692   5
#     ZIF-69 + SO3H 계열 전부가 여기서 죽는다(무치환 모체는 통과).
#
# 원인:
#     형식은 'id type a1 a2 a3 a4' 로 맞는데 a1 과 a4 가 같은 원자다. 한 이면각에
#     같은 원자가 두 번 들어가면 정의가 성립하지 않고 LAMMPS 가 거부한다.
#     술폰산기가 붙은 뒤 결합 인식이 짧은 셀 방향으로 주기 이미지를 자기 자신과
#     이어버리면서 생기는 것으로 보인다.
#
# 처리:
#     원자 번호가 중복된 항목만 버리고 나머지를 다시 번호 매긴다. 헤더의 개수도
#     함께 고친다. Angles/Impropers 도 같은 검사를 한다. 버리는 것은 애초에 물리적
#     의미가 없는 항이므로 이완 결과를 왜곡하지 않는다.
# ---------------------------------------------------------------------------
_SECTIONS = {'Angles': 3, 'Dihedrals': 4, 'Impropers': 4}
_COUNT_KEY = {'Angles': 'angles', 'Dihedrals': 'dihedrals', 'Impropers': 'impropers'}


def clean_degenerate_topology(path, verbose=True):
    """LAMMPS data 파일에서 원자 번호가 중복된 각/이면각/개선각을 제거한다.

    반환: {섹션: 제거한 개수}
    """
    lines = open(path, encoding='utf-8', errors='ignore').read().splitlines()

    # 섹션 경계 찾기
    heads = {}
    for i, l in enumerate(lines):
        s = l.strip()
        if s in _SECTIONS:
            heads[s] = i

    removed = {}
    for sec, natom in _SECTIONS.items():
        if sec not in heads:
            continue
        start = heads[sec] + 1
        while start < len(lines) and not lines[start].strip():
            start += 1
        end = start
        while end < len(lines) and lines[end].strip():
            end += 1

        kept, drop = [], 0
        for l in lines[start:end]:
            f = l.split()
            if len(f) < 2 + natom:
                kept.append(l)
                continue
            ids = f[2:2 + natom]
            if len(set(ids)) == natom:
                kept.append(l)
            else:
                drop += 1
        if not drop:
            continue
        # 번호 다시 매기기 — LAMMPS 는 연속일 필요는 없지만 개수는 헤더와 맞아야 한다
        renum = []
        for k, l in enumerate(kept, start=1):
            f = l.split()
            f[0] = str(k)
            renum.append('     ' + '     '.join(f))
        lines[start:end] = renum
        removed[sec] = drop
        # 헤더 개수 수정
        key = _COUNT_KEY[sec]
        for i, l in enumerate(lines[:heads[sec]]):
            if l.strip().endswith(key) and l.split()[0].isdigit():
                lines[i] = l.replace(l.split()[0], str(len(renum)), 1)
                break
        # 뒤 섹션 인덱스가 밀렸으므로 다시 찾는다
        heads = {}
        for i, l in enumerate(lines):
            s = l.strip()
            if s in _SECTIONS:
                heads[s] = i

    if removed:
        open(path, 'w', encoding='utf-8').write('\n'.join(lines) + '\n')
        if verbose:
            detail = ', '.join(f'{k} {v}개' for k, v in removed.items())
            print(f'    축퇴 토폴로지 제거: {detail}  ({os.path.basename(path)})',
                  flush=True)
    return removed


import os  # noqa: E402  (위 함수에서만 쓴다)

if __name__ == '__main__':
    sys.exit(main())
