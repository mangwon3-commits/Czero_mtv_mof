"""MOSAEC 실행 전 사전 점검: 무엇이 준비됐고 무엇이 빠졌는지 한눈에 보여준다.

MOSAEC (Metal Oxidation State Automated Error Checker)
    White, Gibaldi, Burner, Mayo, Woo, JACS 2025, 147, 17579-17583
    https://doi.org/10.1021/jacs.5c04914 | https://github.com/uowoolab/MOSAEC

MOSAEC은 금속의 산화수를 자동 할당해 "계산 준비된(computation-ready)" MOF DB에
숨어 있는 구조 오류를 잡아낸다. mofchecker(원자 겹침/배위수)나 MOFClassifier(ML 판별)가
못 잡는 종류의 오류 -- 화학적으로 불가능한 산화수 조합 -- 를 담당한다.

    conda activate coremof_tools
    python ~/mof_project/08_MOSAEC/preflight.py
"""
import glob
import importlib
import os
import sys

CHECKS = [
    ('mendeleev', '원소 물성 조회 (MOSAEC 필수)', False),
    ('typing_extensions', 'Literal 백포트 (py3.9)', False),
    ('numpy', '수치 연산', False),
    ('pandas', '결과 표', False),
    ('ccdc', 'CSD Python API -- 라이선스 필요', True),
]


def main():
    print('=' * 72)
    print('MOSAEC 사전 점검')
    print('=' * 72)
    missing_licensed = []
    missing_free = []

    for mod, desc, licensed in CHECKS:
        try:
            m = importlib.import_module(mod)
            ver = getattr(m, '__version__', '?')
            print(f'  [ OK ] {mod:<20} {ver:<10} {desc}')
        except ImportError:
            mark = '라이선스' if licensed else '설치필요'
            print(f'  [{mark}] {mod:<20} {"-":<10} {desc}')
            (missing_licensed if licensed else missing_free).append(mod)

    print()
    # [주의] CoREMOF.curate는 mosaec 임포트를 try/except로 감싸므로, ccdc가 없어도
    # run_MOSAEC 자체는 임포트된다. 임포트 성공을 실행 가능으로 오해하면 안 되고
    # (호출 시점에 NameError로 실패), 실제 백엔드 모듈까지 확인해야 한다.
    try:
        from CoREMOF.curate import run_MOSAEC  # noqa: F401
        importlib.import_module('CoREMOF.mosaec')
        print('  [ OK ] CoREMOF.mosaec 백엔드 로드됨 -- 실행 준비 완료')
        ready = True
    except Exception as e:
        print(f'  [대기] CoREMOF.mosaec 백엔드 사용 불가 ({type(e).__name__})')
        print('         run_MOSAEC 함수는 임포트되지만 호출 시 실패합니다.')
        ready = False

    print()
    if missing_free:
        print(f'설치 필요(무료): pip install {" ".join(missing_free)}')
    if missing_licensed:
        print('CSD Python API(ccdc)가 없습니다. 아래 절차는 사용자 본인이 수행해야 합니다')
        print('(CCDC 계정 로그인과 라이선스 약관 동의가 필요하며, 대리 수행 대상이 아닙니다):')
        print()
        print('  1. https://www.ccdc.cam.ac.uk/solutions/csd-core/components/csd-python-api/')
        print('     에서 30일 평가판(또는 기관 라이선스) 신청')
        print('  2. CCDC 포털에서 리눅스용 CSD Portfolio 설치본 다운로드')
        print('  3. 설치 후 라이선스 활성화:')
        print('       ccdc_activator -a -k <라이선스키>')
        print('     또는 환경변수: export CCDC_LICENSING_CONFIGURATION=la-code:<키>')
        print('  4. 이 conda 환경에 API 설치 (경로는 설치본 위치에 맞게):')
        print('       conda activate coremof_tools')
        print('       pip install /opt/CCDC/Python_API_<버전>/csd-python-api/*.whl')
        print('  5. 확인: python ~/mof_project/08_MOSAEC/preflight.py')
        print()
        print('  주의: 평가판은 30일 한정이므로, 활성화 직후 검사 대상 구조를 한 번에')
        print('        돌려두는 편이 유리합니다 (run_mosaec.py가 폴더 단위 일괄 실행).')

    # [대상 목록을 여기서도 보여 준다]
    #   평가판 시계가 도는 순간 무엇을 돌릴 수 있는지 미리 알아야, 라이선스를
    #   켠 뒤에 대상을 고르느라 시간을 쓰지 않습니다.
    print()
    print('-' * 72)
    print('검사 대상 (우선순위 순 -- run_mosaec.py 의 TARGETS)')
    print('-' * 72)
    try:
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        import run_mosaec as R
        total = 0
        for label, rel, why in R.TARGETS:
            folder = os.path.join(R.ROOT, rel)
            n = len(glob.glob(os.path.join(folder, '*.cif')))
            total += n
            print(f'  {label:<16} {n:>4} CIF   {why}')
        print(f'  {"합계":<16} {total:>4} CIF')
        print()
        print('  v3_charged 가 08-21 장표의 후보입니다. 이것부터 돌리세요:')
        print('    python ~/mof_project/08_MOSAEC/run_mosaec.py --only v3_charged')
    except Exception as e:                                   # noqa: BLE001
        print(f'  (목록을 읽지 못했습니다: {type(e).__name__}: {e})')

    if ready:
        print('\n다음 단계: python ~/mof_project/08_MOSAEC/run_mosaec.py')
    else:
        print('\n라이선스 없이 지금 할 수 있는 것:')
        print('  python ~/mof_project/08_MOSAEC/run_mosaec.py --dry-run   대상 점검')
        print('  python ~/mof_project/08_MOSAEC/join_scores.py            빈 칸 표')
    return 0 if ready else 1


if __name__ == '__main__':
    sys.exit(main())
