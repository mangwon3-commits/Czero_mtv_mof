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

if __name__ == '__main__':
    sys.exit(main())
