"""저압 앙상블 — `saIm0583` 5실현 x RH 5/10/15 (15작업). **군 A K_H 배치 산포.**

[사전 등록] `ASSIGN_36H_20260826.md` 12절 (나). Junseok 몫이었으나 08-27 12:3x
현재 그 기기가 여전히 다운(마지막 소식 08-25 17:02)이라 데스크탑이 회수합니다.

[무엇을 재는가 — 지금 K_H 판정 전부가 빌려온 숫자 위에 서 있습니다]
    저압 K_H 사다리의 판정에 쓴 배치 산포 **17.9%** 는 `saIm0583` 앙상블의
    **RH90 물 로딩** 산포입니다. K_H 는 고원값이 아니라 **초기 기울기**라
    산포 성질이 다를 수 있는데, **K_H 자체의 산포는 아무도 안 쟀습니다.**

    이 15작업이 그것을 직접 잽니다. 전하 CIF 가 이미 있어 추가 빌드가
    없습니다(`charged_v3/saIm0583e{1..5}_DDEC6.cif`).

[랩탑이 미리 등록한 예측 — 이 계산이 그것을 시험합니다]
    랩탑이 08-26 에 **"K_H 산포는 17% 안팎일 것"** 을 앙상블 없이 예측해
    등록했습니다. 근거는 앙상블이 이미 가진 두 조건(RH2.8%·373K 와
    RH90%·298K, RH 32배 차)에서 **실현간 순위 상관 r=+0.799, 상대 산포
    18.3%/16.7% 로 거의 안 변한다**는 것 — 실현 차이의 상당 부분이
    척도인자라는 뜻입니다.

    **벗어나면 그 자체가 "로딩 산포를 기울기에 쓰면 안 된다" 는 증거**입니다.
    예측을 먼저 박아 둔 것이라 결과를 보고 고치지 않습니다.

[검출력 한계 — 미리 적습니다]
    n=5 대 n=5 면 F(0.95,4,4)=6.39 이라 **SD 비가 2.53배는 되어야 잡힙니다.**
    "구별 안 됨" 이 나와도 그것은 **"같다" 가 아니라 "2.5배 미만은 못 본다"**
    입니다. 랩탑이 08-27 에 짚었고 그대로 옮겨 적습니다.

[왜 출력을 분리하나]
    저압 18점(6조성 x 3RH)이 `v3_water_lowrh/` 에 있습니다. 앙상블을 같은
    파일에 넣으면 `saIm0583` 이 여섯 벌이 되어 조성별 표가 비대칭해지고,
    이어받기가 섞습니다. **`v3_water_lowrh_ensA/` 로 따로 받습니다.**
    `generation_of()` 는 'v3_water' 를 부분문자열로 잡아 둘 다 세대 **v3**
    이므로 나중에 합칠 수 있습니다.

사용:
    WATER_ENSA_WORKERS=8 python run_water_lowrh_ensA.py
"""
import os
import shutil
import sys

REAL = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, REAL)

import run_water as rw                                        # noqa: E402

ENSA = os.path.join(REAL, 'v3_water_lowrh_ensA')
os.makedirs(ENSA, exist_ok=True)

rw.HERE = ENSA
rw.CHARGED = os.path.join(REAL, 'charged_v3')
rw.RUNS = os.path.join(REAL, 'water_runs_lowrh_ensA')
rw.WATER_DEF = os.path.join(REAL, '..', '19_WaterCompetition', 'water.def')
rw.MAX_WORKERS = int(os.environ.get('WATER_ENSA_WORKERS', '8'))

# 저압 18점과 **같은 세 점**. 다르면 같은 표에 못 놓습니다(규약 ⑥).
# 비싼 것 먼저 넣습니다 — CLAUDE.md §5 (LPT).
rw.RH_LIST = [0.15, 0.10, 0.05]

rw.TARGETS = [
    ('saIm0583e1', 'SO3H 58.3% 실현 1'),
    ('saIm0583e2', 'SO3H 58.3% 실현 2'),
    ('saIm0583e3', 'SO3H 58.3% 실현 3'),
    ('saIm0583e4', 'SO3H 58.3% 실현 4'),
    ('saIm0583e5', 'SO3H 58.3% 실현 5'),
]

if __name__ == '__main__':
    print('저압 앙상블 — saIm0583 5실현 x RH 5/10/15 (15작업)', flush=True)
    print(f'  입력   {rw.CHARGED}', flush=True)
    print(f'  작업   {rw.RUNS}', flush=True)
    print(f'  결과   {os.path.join(rw.HERE, "water_results.json")}', flush=True)
    print(f'  워커   {rw.MAX_WORKERS}   RH {rw.RH_LIST}', flush=True)
    print(f'  대상   {" ".join(n for n, _ in rw.TARGETS)}', flush=True)

    # 좁힌 러너가 공용 파일을 덮어쓴 전력이 있어(08-25 d0b6f50) 범위를 검사합니다.
    if len(rw.TARGETS) != 5 or rw.RH_LIST != [0.15, 0.10, 0.05]:
        print('  !! 대상·RH 범위가 어긋납니다. 중단합니다.', flush=True)
        sys.exit(1)
    if not rw.HERE.endswith('ensA'):
        print('  !! 출력 경로가 앙상블 전용이 아닙니다. 중단합니다.', flush=True)
        sys.exit(1)
    missing = [n for n, _ in rw.TARGETS
               if not os.path.exists(os.path.join(rw.CHARGED, n + '_DDEC6.cif'))]
    if missing:
        print(f'  !! 전하 CIF 없음: {missing}', flush=True)
        sys.exit(1)

    # 물 정의가 5자리인지. 배포본 TraPPE/water.def 는 3자리라 조용히 다른
    # 물로 계산됩니다 — 실패가 결과처럼 보이는 그 유형입니다.
    nsite = sum(1 for ln in open(rw.WATER_DEF, encoding='utf-8')
                if len(ln.split()) > 4 and ln.split()[1] in ('Ow', 'Hw', 'Lw'))
    print(f'  물 정의 사이트 {nsite}개 (TIP5P-Ew 는 5)', flush=True)
    if nsite != 5:
        print('  !! 5자리 물이 아닙니다. 중단합니다.', flush=True)
        sys.exit(1)
    print(flush=True)

    rc = rw.main()

    # 기기 태그 사본. merge_water_batches.machine_of 가 파일명에서 출처를
    # 읽으므로 태그가 없으면 거부됩니다(08-23 79dfa04).
    src = os.path.join(rw.HERE, 'water_results.json')
    if rc == 0 and os.path.exists(src):
        tag = os.environ.get('WATER_BATCH_TAG') or os.uname().nodename.lower()
        shutil.copy(src, os.path.join(rw.HERE, f'water_results_{tag}.json'))
        print(f'  기기명 사본 저장: water_results_{tag}.json', flush=True)

    sys.exit(rc)
