"""실행 간 재현성 직접 측정 — `saIm0583e1`·`e5` RH0 를 **새 시드로** 다시 돌립니다.

[왜]
    랩탑과 제 건조 로딩이 갈립니다(χ²=36.09, dof=5, p<0.0001). 구조는 같고
    (해시 10개 전부 일치) 기록된 조건도 같습니다. 남은 설명은 **실행 잡음**인데,
    원인이 나왔습니다 — **`RandomSeed` 가 입력에 없습니다.**

        내 v3ens 배치      시드 1787540797  (e1~e5 · RH0·RH90 전부)
        내 mslm050 배치    시드 1787837442
        랩탑 실행          또 다른 배치 -> 또 다른 시드

    RASPA 의 `±` 는 **한 궤적 안 블록 평균 다섯의 95%CI** 입니다. **다른 궤적으로
    다시 돌렸을 때의 흩어짐이 아닙니다.** 랩탑 χ² 로 환산하면 참 실행간 SD 가
    보고된 `±` 의 **2.69배**입니다.

[무엇을 재는가]
    같은 코드 · 같은 조건 · **새 시드** 로 두 건을 다시 돌려, 내 값이 다시
    나오는지 봅니다. 기기 간 비교가 아니라 **우리 파이프라인 자체의 실행 간
    재현성**입니다 — 기기·빌드·구조 차이가 전부 배제됩니다.

        1차 (08-24 배치, 시드 1787540797)   e1 1.2024 +- 0.0251   e5 1.1716 +- 0.0179
        2차 (이 실행, 새 시드)              ?                     ?

    두 값이 `±` 안이면 다)가 약해지고, `±` 를 크게 넘으면 다)가 확정됩니다.

[왜 e1 과 e5 인가]
    랩탑과 가장 크게 갈린 둘입니다(+3.02 · +4.53). 갈림이 크면 신호도 큽니다.

[하지 않는 것]
    시드를 손으로 고정하지 않습니다. **지금 파이프라인이 실제로 하는 대로**
    돌려야 재현성을 재는 것이 됩니다. 고정은 이 측정이 끝난 뒤 결정할 일입니다.
"""
import os
import shutil
import subprocess
import sys

os.environ.setdefault("PYTHONHASHSEED", "0")

import run_water as rw

REAL = os.path.dirname(os.path.abspath(__file__))
# [2026-08-28] 랩탑 지적: 2구조 x 1회는 dof 2 라 R 추정이 약합니다. 한 구조를
# 여러 번 반복하는 쪽이 낫습니다 - 구조 간 차이가 안 섞이니까요.
# REPRO_TAG 로 인스턴스를 나눠 병렬 반복하고, REPRO_ONLY 로 대상을 좁힙니다.
TAG = os.environ.get('REPRO_TAG', '')
OUT = os.path.join(REAL, 'v3_water_repro' + (('_' + TAG) if TAG else ''))
os.makedirs(OUT, exist_ok=True)

rw.HERE = OUT
rw.CHARGED = os.path.join(REAL, 'charged_v3')
rw.RUNS = os.path.join(REAL, 'water_runs_repro' + (('_' + TAG) if TAG else ''))
rw.WATER_DEF = os.path.join(REAL, '..', '19_WaterCompetition', 'water.def')
rw.MAX_WORKERS = int(os.environ.get('REPRO_WORKERS', '2'))

rw.RH_LIST = [0.0]
rw.TARGETS = [
    ('saIm0583e1', '재현성 시험 — 1차 1.2024 ± 0.0251'),
    ('saIm0583e5', '재현성 시험 — 1차 1.1716 ± 0.0179'),
]

if __name__ == '__main__':
    print('실행 간 재현성 측정 — saIm0583e1 · e5 · RH0 · 새 시드', flush=True)
    print(f'  입력   {rw.CHARGED}', flush=True)
    print(f'  작업   {rw.RUNS}', flush=True)
    print(f'  결과   {os.path.join(rw.HERE, "water_results.json")}', flush=True)
    print(f'  워커   {rw.MAX_WORKERS}   RH {rw.RH_LIST}', flush=True)
    print(f'  대상   {" ".join(n for n, _ in rw.TARGETS)}', flush=True)

    # [2026-08-29] REPRO_ONLY 를 **필터가 아니라 지정**으로 바꿉니다.
    # 필터였을 때 REPRO_ONLY=saIm0583e2 가 목록에 없어 빈 대상이 됐고,
    # 가드가 막아 안 돌았습니다(태그 k·l·m). 선택 편향 없는 시험을 하려면
    # 애초에 목록에 없던 구조를 재실행할 수 있어야 합니다 — 랩탑 지적.
    only = os.environ.get('REPRO_ONLY', '').strip()
    if only:
        known = dict(rw.TARGETS)
        rw.TARGETS = [(t.strip(), known.get(t.strip(), '재현성 반복'))
                      for t in only.split(',') if t.strip()]
        print('  REPRO_ONLY -> ' + ' '.join(n for n, _ in rw.TARGETS), flush=True)
    if not rw.TARGETS or rw.RH_LIST != [0.0]:
        print('  !! 대상이 비었거나 RH 가 [0.0] 이 아닙니다. 중단합니다.', flush=True)
        sys.exit(1)
    for p, label in ((rw.CHARGED, '전하 CIF 폴더'), (rw.WATER_DEF, '물 정의')):
        if not os.path.exists(p):
            print(f'  !! {label} 없음: {p}', flush=True)
            sys.exit(1)
    missing = [n for n, _ in rw.TARGETS
               if not os.path.exists(os.path.join(rw.CHARGED, n + '_DDEC6.cif'))]
    if missing:
        print(f'  !! 전하 CIF 없음: {" ".join(missing)}', flush=True)
        sys.exit(1)

    nsite = sum(1 for ln in open(rw.WATER_DEF, encoding='utf-8')
                if len(ln.split()) > 4 and ln.split()[1] in ('Ow', 'Hw', 'Lw'))
    print(f'  물 정의 사이트 {nsite}개 (RH0 라 안 쓰이지만 확인)', flush=True)

    busy = subprocess.run(['pgrep', '-f', 'risk_screen|/network'],
                          capture_output=True, text=True).stdout.strip()
    if busy:
        print('  !! Zeo++ 계열이 돌고 있습니다. 중단합니다.', flush=True)
        sys.exit(2)

    print(f'  simulate {rw.SIMULATE}', flush=True)
    if not (rw.SIMULATE and os.path.exists(rw.SIMULATE)):
        print('  !! simulate 를 찾을 수 없습니다. 중단합니다.', flush=True)
        sys.exit(1)

    print(flush=True)
    rc = rw.main()

    src = os.path.join(rw.HERE, 'water_results.json')
    if rc == 0 and os.path.exists(src):
        tag = os.environ.get('WATER_BATCH_TAG') or os.uname().nodename.lower()
        dst = os.path.join(rw.HERE, f'water_results_{tag}.json')
        shutil.copy(src, dst)
        print(f'  기기명 사본 저장: {dst}', flush=True)

    # 이번 실행이 실제로 쓴 시드를 남깁니다 — 이 측정의 핵심 메타데이터입니다.
    import glob
    for n, _ in rw.TARGETS:
        for f in glob.glob(os.path.join(rw.RUNS, f'rh00_{n}', 'Output', '*', '*.data')):
            for ln in open(f, errors='ignore'):
                if 'Random number seed' in ln:
                    print(f'  시드 {n}: {ln.split(":")[-1].strip()}', flush=True)
                    break
            break

    sys.exit(rc)
