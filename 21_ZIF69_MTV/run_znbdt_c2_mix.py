# -*- coding: utf-8 -*-
"""ZNBDT-C2 무극성 −CN 작동점 S_mix 3씨앗 — `run_e24i_mix.py` 를 그대로 import 하고(그 안에서 run_tj1_mix 무수정) 대상 CIF · 실행 폴더 · 출력만 바꿈.
등록: ASSIGN_ZNBDT_C2_20261105.md §1(자료 0건). 규약은 −CN 6씨앗과 같음: CO₂/N₂ 0.15/0.85 · 100 kPa · 298 K · 5,000+15,000 · 착수 15 s 간격.
환경: ZC2_VARIANT = U | I | L (필수 · L 은 §7 C2-L) · E24G_MACHINE(기본 hkhome) · E24MIX_WORKERS(기본 3).
씨앗 겹침 방지: 두 판을 함께 띄울 때는 둘째 판을 첫 판 착수 60 s 뒤에 띄웁니다(러너 씨앗 = 초 단위 시각).
S_Henry 열은 자리 채움(Widom 파일 이름이 run_e24i_mix 의 glob 과 다름) — 판정은 znbdt_c2_judge.py 가 원자료로 다시 냅니다."""
import os, sys
V = os.environ['ZC2_VARIANT']
assert V in ('U', 'I', 'L'), V   # L = §7 C2-L 민감도 판(종합자 등록 ebde94fb) — U·I 경로는 그대로
os.environ['E24G_TAG'] = f'znbdt_c2_apolar{V}'
os.environ.setdefault('E24G_MACHINE', 'hkhome')
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import run_e24i_mix as R          # noqa: E402
from ase.io import read           # noqa: E402
M = R.M; TAG = R.TAG
M.RUNS = os.path.join(HERE, f'znbdt_c2_mix_runs_{TAG}')
M.OUT = os.path.join(HERE, f'results_znbdt_c2_{TAG}_mix_{M.MACHINE}.json')
M.TEST = f'ZNBDT-C2 무극성 −CN({V}판) 작동점 S_mix 3씨앗'
M.ASSIGN_REF = 'ASSIGN_ZNBDT_C2_20261105.md §1'
M.REG_REF = 'ASSIGN_ZNBDT_C2_20261105.md §2 — N₂ 추가 배제비 판정(znbdt_c2_judge.py)'
CIF = os.path.join(HERE, 'charged_v3', f'{TAG}_DDEC6mod.cif')


def targets():
    t = []
    for k in (1, 2, 3):
        t.append({'name': f'{TAG}_s{k}', 'cif': CIF, 'group': '기제 판별 대조(계산 전용)', 'dim': 3,
                  'S_Henry': 1.0, 'S_Henry_err': 0.0, 'S_Henry_src': '자리 채움 1.0 — 비 인용 금지(판정은 znbdt_c2_judge.py)',
                  'L': None, 'L_src': '—'})
    for x in t:
        a = read(x['cif']); uc = M.rg.unit_cells(a); x['unit_cells'] = uc; x['N_super'] = len(a) * uc[0] * uc[1] * uc[2]
    return t


M.targets = targets
if __name__ == '__main__':
    sys.exit(M.main())
