"""MOSAEC 일괄 실행: 프로젝트의 모든 검사 대상 구조를 한 번에 돌린다.

평가판 라이선스가 30일 한정이므로, 활성화되면 최대한 많은 구조를 한 번에 처리하도록
검사 대상 폴더를 미리 모아두었다. ccdc가 없으면 즉시 안내하고 종료한다.

    conda activate coremof_tools
    python ~/mof_project/08_MOSAEC/run_mosaec.py            # 기본 대상 전체
    python ~/mof_project/08_MOSAEC/run_mosaec.py <폴더>      # 특정 폴더만
"""
import glob
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, '..')

# 검사 대상 -- 라벨: 폴더
TARGETS = {
    'generated_MTV_ZIF8': os.path.join(ROOT, '03_Generated_MTV_ZIFs'),
    'ligand_library':     os.path.join(ROOT, '05_MTV_Ligand_Library'),
    'zif8_sources':       os.path.join(ROOT, '06_ZIF8_Sources'),
    'bracketed_pairs':    os.path.join(ROOT, '07_Bracketed_MTV'),
    'source_cifs':        os.path.join(ROOT, '01_CIF_Cleaned'),
}


def main():
    try:
        from CoREMOF.curate import run_MOSAEC
    except Exception as e:
        print(f'MOSAEC을 사용할 수 없습니다: {type(e).__name__}: {e}')
        print('먼저 실행: python', os.path.join(HERE, 'preflight.py'))
        return 1

    targets = ({os.path.basename(sys.argv[1].rstrip('/')): sys.argv[1]}
               if len(sys.argv) > 1 else TARGETS)

    os.makedirs(os.path.join(HERE, 'results'), exist_ok=True)
    summary = {}

    for label, folder in targets.items():
        if not os.path.isdir(folder):
            print(f'[건너뜀] {label}: 폴더 없음 ({folder})')
            continue
        cifs = glob.glob(os.path.join(folder, '*.cif'))
        if not cifs:
            print(f'[건너뜀] {label}: CIF 없음')
            continue

        out = os.path.join(HERE, 'results', label)
        os.makedirs(out, exist_ok=True)
        print(f'[실행] {label}: CIF {len(cifs)}개 -> {out}')
        try:
            res = run_MOSAEC(folder, save_path=out, max_workers=8)
            summary[label] = {'n_cifs': len(cifs), 'result': res}
        except Exception as e:
            print(f'  [오류] {type(e).__name__}: {e}')
            summary[label] = {'n_cifs': len(cifs), 'error': f'{type(e).__name__}: {e}'}

    path = os.path.join(HERE, 'results', 'mosaec_summary.json')
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2, ensure_ascii=False, default=str)
    print(f'\n[OK] 요약 저장: {path}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
