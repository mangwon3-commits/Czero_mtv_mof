"""꾸러미에 넣을 파이썬 모듈을 의존성 폐포로 모으고, 문서와 대조해 검증한다.

[왜 이 파일이 따로 있는가 -- 같은 결함이 세 번 났다]
    prepare_handoff.sh 가 넣을 파일을 손으로 골랐고, 그때마다 빠졌습니다.

        1차: run_working_capacity.py, run_gcmc_v2.py  -> 랩탑에서 ModuleNotFound
        2차: run_density_v3.py 계열                   -> 랩탑 지시가 부를 수 없음
        3차: risk_screen_v3.py, risk_screen.py        -> 안정성 배정이 실행 불가

    목록을 사람이 관리하는 한 계속 빠집니다. 그래서 두 가지를 자동화합니다.

      (1) 씨앗에서 import 를 따라가되 **형제 폴더까지** 뒤집니다.
          risk_screen.py 는 ../18_PoreNarrowing/lammps_iface_patched.py 를
          import 합니다. 한 폴더만 보는 폐포로는 절대 안 잡힙니다.

      (2) 꾸러미에 넣은 **문서가 부르는 .py 가 실제로 들어갔는지** 대조합니다.
          지시서가 부르는 파일이 없는 것이 지금까지의 실패 형태 전부였습니다.
          이 검사가 통과하지 못하면 꾸러미를 만들지 않습니다.

사용: python pack_scripts.py <프로젝트루트> <목적지_21_ZIF69_MTV> <씨앗...>
"""
import ast
import os
import re
import shutil
import sys

# import 를 찾을 폴더들. 첫 번째가 주 폴더이고 나머지는 형제 모듈 자리입니다.
SUBDIRS = ['21_ZIF69_MTV', '18_PoreNarrowing', '19_WaterCompetition',
           '20_ParentScan', '05_MTV_Ligand_Library']


def find(root, name):
    for d in SUBDIRS:
        p = os.path.join(root, d, name)
        if os.path.exists(p):
            return p
    return None


def closure(root, seeds):
    seen, queue = {}, [s for s in seeds if find(root, s)]
    while queue:
        f = queue.pop()
        if f in seen:
            continue
        src = find(root, f)
        if not src:
            continue
        seen[f] = src
        tree = ast.parse(open(src, encoding='utf-8').read())
        names = []
        for n in ast.walk(tree):
            if isinstance(n, ast.Import):
                names += [a.name for a in n.names]
            elif isinstance(n, ast.ImportFrom) and n.level == 0 and n.module:
                names.append(n.module)
        for m in names:
            cand = m.split('.')[0] + '.py'
            if cand not in seen and find(root, cand):
                queue.append(cand)
    return seen


def main():
    root, dst = sys.argv[1], sys.argv[2]
    seeds = sys.argv[3:]
    got = closure(root, seeds)
    os.makedirs(dst, exist_ok=True)
    for name, src in sorted(got.items()):
        shutil.copy(src, os.path.join(dst, name))
    print(f'  모듈 {len(got)}개: {" ".join(sorted(got))}')

    # 문서가 부르는 .py 가 전부 들어갔는지 대조합니다. 여기서 걸리면 실패입니다.
    docroot = os.path.dirname(dst)
    missing = []
    for md in sorted(os.listdir(docroot)):
        if not md.endswith('.md'):
            continue
        text = open(os.path.join(docroot, md), encoding='utf-8').read()
        for ref in sorted(set(re.findall(r'\b(run_[a-z0-9_]+\.py|risk_[a-z0-9_]+\.py)',
                                         text))):
            if ref not in got:
                missing.append(f'{md} -> {ref}')
    if missing:
        print('  !! 문서가 부르는데 꾸러미에 없는 스크립트:')
        for m in missing:
            print(f'       {m}')
        return 1
    print('  문서 대조 통과 — 지시서가 부르는 스크립트가 전부 들어 있습니다')
    return 0


if __name__ == '__main__':
    sys.exit(main())
