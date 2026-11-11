# -*- coding: utf-8 -*-
"""등록 L (L-0) **점검 — 등록 밖의 다른 시험**: 대칭 깨기. `e24k_me37_open` 이완본에서 카복실레이트 비틀림이 0.1~0.5° 로 거의 안 변했음 —
형판(X선)의 카복실레이트가 티오펜 평면과 정확히 같은 면(비틀림 0.0°)이라 면 밖 힘이 0 에 가까워 **안장점에 멈춘 것인지** 봄.
빌드본 좌표를 무작위로 0.03 Å(표준편차 · 씨앗 기록) 흩뜨린 뒤 같은 이완(`relax_tnf.py` 무수정 · fmax 0.05 · 800단계 · 고정셀 · xtb 스레드 1)을 돌림.
산출: e24k_candidates/E24k_ZnDia_Me37_open_rattle{seed}.cif · relax_tnf/e24k_me37_open_rattle{seed}_relaxed.cif · results_e24k_symcheck_relax_hkhome.json.
관문 판정(L-1 로 갈지)은 등록 절차의 이완본(`e24k_me37_open`)으로만 함 — 이 점검은 그 결과가 안장점 탓인지 가리는 자료.
실행: spectra 파이썬 — `python e24k_symcheck_hkhome.py [seed …]`(기본 1)
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
os.environ['RELAX_WORKERS'] = '1'
import relax_tnf as RT   # noqa: E402
from ase.io import read   # noqa: E402

sys.path.insert(0, HERE)


class XTBGrad1(RT.XTBGrad):
    def __init__(self, workdir, method='gfnff', nthreads=2, **kw):
        super().__init__(workdir, method=method, nthreads=1, **kw)


RT.XTBGrad = XTBGrad1
SRC = os.path.join(HERE, 'e24k_candidates', 'E24k_ZnDia_Me37_open.cif')
STDEV = 0.03

if __name__ == '__main__':
    seeds = [int(x) for x in sys.argv[1:]] or [1]
    argv = ['--out', os.path.join(HERE, 'results_e24k_symcheck_relax_hkhome.json')]
    for sd in seeds:
        tag = f'e24k_me37_open_rattle{sd}'
        dst = os.path.join(HERE, 'e24k_candidates', f'E24k_ZnDia_Me37_open_rattle{sd}.cif')
        if os.path.exists(dst) or os.path.exists(os.path.join(HERE, 'relax_tnf', f'{tag}_relaxed.cif')) or os.path.exists(os.path.join(HERE, 'relax_tnf', tag)):
            raise SystemExit(f'!! {tag} 산출이 이미 있음 — 중단')
        a = read(SRC)
        a.rattle(stdev=STDEV, seed=sd)
        a.write(dst)
        argv += ['--job', f'{tag}={dst}']
    sys.exit(RT.main(argv))
