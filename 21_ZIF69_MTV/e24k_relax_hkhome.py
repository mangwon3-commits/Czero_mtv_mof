# -*- coding: utf-8 -*-
"""등록 L (L-0) — `e24k_me37_open` · `e24k_me37_100` 의 고정셀 GFN-FF 이완. 등록 `ASSIGN_NOON_20261112.md` §1-1("E-24i 와 같은 설정").
`relax_tnf.py`(dfe4d913 · fmax 0.05 eV/Å · 800단계 · FIRE maxstep 0.1 · 셀 고정 · E-24i · −NO₂ 열린 자리 이완에 쓴 코드)를 **무수정 import** 해 main 을 부름.
바꾸는 것 하나: xtb 스레드 2 → 1(부수 작업 규칙 "한 프로세스 · OMP_NUM_THREADS=1 · nice 19" — 원판은 `XTBGrad(…, nthreads=2)` 로 박혀 있어
그 클래스를 스레드만 1 로 고정한 하위 클래스로 바꿔 끼움 · 힘 계산 내용은 같음). 워커 1(RELAX_WORKERS=1) — 한 번에 하나, 주 구조 먼저.
출력: relax_tnf/<tag>_relaxed.cif(실패하면 아무것도 안 남김 — 원판 규칙) + results_e24k_relax_hkhome.json. 판정 없음(관문은 e24k_gate.py).
실행: spectra 파이썬(ase + xtb) — 21_ZIF69_MTV 에서 `RELAX_WORKERS=1 python e24k_relax_hkhome.py`
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
os.environ['RELAX_WORKERS'] = '1'
import relax_tnf as RT   # noqa: E402


class XTBGrad1(RT.XTBGrad):
    def __init__(self, workdir, method='gfnff', nthreads=2, **kw):
        super().__init__(workdir, method=method, nthreads=1, **kw)


RT.XTBGrad = XTBGrad1
JOBS = (('e24k_me37_open', 'e24k_candidates/E24k_ZnDia_Me37_open.cif'), ('e24k_me37_100', 'e24k_candidates/E24k_ZnDia_Me37_100.cif'))

if __name__ == '__main__':
    out = os.path.join(HERE, 'results_e24k_relax_hkhome.json')
    if os.path.exists(out) or any(os.path.exists(os.path.join(HERE, 'relax_tnf', f'{t}_relaxed.cif')) or os.path.exists(os.path.join(HERE, 'relax_tnf', t)) for t, _ in JOBS):
        raise SystemExit('!! 이전 이완 산출(results_e24k_relax_hkhome.json · relax_tnf/e24k_*) 있음 — 중단')
    argv = ['--out', out]
    for t, c in JOBS:
        argv += ['--job', f'{t}={os.path.join(HERE, c)}']
    sys.exit(RT.main(argv))
