"""군 B 저압 확장 — `sa50nb50` 앙상블 e1~e5 × RH 5/10/15 (15작업).

[무엇을 메우는가 — 물 헨리 상수의 배치 산포]
    `LOWRH_18_ANALYSIS.md` 의 모든 판정이 **기준 배치 산포 16.7~18.3%** 에
    걸려 있습니다. 그 값은 `saIm0583` 앙상블의 **물 로딩** 산포이지 **K_H**
    산포가 아닙니다. K_H 는 로딩이 아니라 P→0 기울기라 산포가 같으리란
    보장이 없습니다.

    군 A(`saIm0583` 저압 앙상블, 데스크탑 08-27 12:39 착수)가 단일 치환기
    쪽을 잽니다. **이 러너는 군 B — 24자리 전부가 두 치환기로 찬 혼합 —**
    을 잽니다. 둘은 다른 것을 잽니다:

        군 A   14/24 한 치환기, 빈 자리 10   충돌회피 경로
        군 B   24/24 두 치환기, 빈 자리 0    무작위 경로

    **빈 자리가 없으면 "어느 자리를 비울지" 를 못 고르므로 배열 자유도의
    성격이 다릅니다.** 08-26 대조군 판정(null)은 군 A 쪽 상황에서 잰 것이라
    여기 그대로 옮길 수 없습니다.

[이 값이 무엇을 확정하나]
    `LOWRH_18_ANALYSIS.md` 2절에서 여유가 가장 얇은 두 칸이 혼합 조성입니다:

        ms50nb50 -> sa50nb50   f 19.0%   여유 1.04~1.14배
        sa25nb75 -> sa50nb50   f 23.5%   여유 1.28~1.41배

    **군 B 산포가 19% 를 넘으면 첫 칸이 죽습니다.** 그것이 "−OH 가 물
    친화도를 올린다(12자리)" 를 조건부에서 확정 또는 폐기로 옮깁니다.

[사전 등록 — 수 보기 전에 적습니다]
    예측: K_H 배치 산포는 **17% 안팎**. 근거는 `saIm0583` 앙상블에서 물
    로딩 산포가 조건이 크게 달라도(RH2.8%/373K 대 RH90%/298K) 16.7~18.3%
    로 거의 안 변하고, 실현간 순위 상관이 +0.799 라 **차이의 상당 부분이
    척도인자**이기 때문입니다. 척도인자면 기울기 산포 = 로딩 산포입니다.

    **벗어나면 그것이 "로딩 산포를 기울기에 쓰면 안 된다" 는 증거입니다.**

    ⚠️ **검출력 한계도 미리 적습니다.** n=5 면 F(0.95, 4, 4) = 6.39 이므로
    **SD 비가 2.53배는 되어야 잡힙니다.** 결과가 "군 A 와 구별 안 됨" 으로
    나와도 그것은 **"같다" 가 아니라 "2.5배 미만은 못 본다"** 입니다.
    결과를 보고 이 해석을 고치지 않습니다.

[계산은 한 글자도 안 바꿉니다]
    `run_water.py` 를 그대로 씁니다 — 엔진·힘장·CO2 모델·물 정의(TIP5P-Ew
    5사이트)·CO2 분압 0.15 bar·15000 사이클 동일. `RH_LIST` 와 `TARGETS`
    만 다릅니다. 저압 18점과 **같은 자로 재야** 비교가 됩니다.

[출력을 분리하는 이유]
    `v3_water_lowrh/` 는 6조성 18점이 모인 곳입니다. 앙상블 점을 같은
    파일에 넣으면 이어받기가 섞고 조성별 점 수가 비대칭해집니다. 따로 받고
    사람이 합칩니다 (CLAUDE.md §3).

사용:
    WATER_GRPB_WORKERS=5 python run_water_lowrh_grpb.py
"""
import os
import shutil
import sys

import run_water as rw

REAL = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(REAL, 'v3_water_lowrh_grpb')
os.makedirs(OUT, exist_ok=True)

rw.HERE = OUT
rw.CHARGED = os.path.join(REAL, 'charged_v3')
rw.RUNS = os.path.join(REAL, 'water_runs_lowrh_grpb')
rw.WATER_DEF = os.path.join(REAL, '..', '19_WaterCompetition', 'water.def')
rw.MAX_WORKERS = int(os.environ.get('WATER_GRPB_WORKERS', '5'))

# 저압 18점과 동일한 세 점. 비싼 것 먼저(LPT).
rw.RH_LIST = [0.15, 0.10, 0.05]

rw.TARGETS = [(f'sa50nb50e{i}', f'SO3H 50% + NO2 50% — 실현 {i}') for i in range(1, 6)]

# 원소 정확 일치 검사. 빌더가 시드에 따라 원자 수를 조용히 바꾼 전력이
# 있습니다(08-21). 다섯 실현이 **같은 조성**이어야 배치 산포만 재집니다.
EXPECT_EL = {'C': 240, 'H': 156, 'N': 132, 'O': 108, 'S': 12, 'Zn': 24}


def elements(path):
    import collections
    import re
    c = collections.Counter()
    for ln in open(path, encoding='utf-8', errors='ignore'):
        t = ln.split()
        if len(t) >= 5 and re.match(r'^[A-Z][a-z]?\d*$', t[0]):
            c[re.match(r'^([A-Z][a-z]?)', t[0]).group(1)] += 1
    return dict(c)


if __name__ == '__main__':
    print('군 B 저압 — sa50nb50 앙상블 e1~e5 × RH 5/10/15 (15작업)', flush=True)
    print(f'  입력   {rw.CHARGED}', flush=True)
    print(f'  작업   {rw.RUNS}', flush=True)
    print(f'  결과   {os.path.join(rw.HERE, "water_results.json")}', flush=True)
    print(f'  워커   {rw.MAX_WORKERS}', flush=True)
    print(f'  RH     {rw.RH_LIST}', flush=True)
    print(f'  대상   {" ".join(n for n, _ in rw.TARGETS)}', flush=True)

    if len(rw.TARGETS) != 5 or rw.RH_LIST != [0.15, 0.10, 0.05]:
        print('  !! 등록된 15작업이 아닙니다. 중단합니다.', flush=True)
        sys.exit(1)
    for p, label in ((rw.CHARGED, '전하 CIF 폴더'), (rw.WATER_DEF, '물 정의')):
        if not os.path.exists(p):
            print(f'  !! {label} 없음: {p}', flush=True)
            sys.exit(1)

    # 다섯 실현의 조성이 전부 같은지 확인합니다. 하나라도 다르면 재는 것이
    # 배치 산포가 아니라 조성 산포가 섞인 것이 됩니다.
    bad = []
    for n, _ in rw.TARGETS:
        cif = os.path.join(rw.CHARGED, n + '_DDEC6.cif')
        if not os.path.exists(cif):
            bad.append(f'{n} 없음')
            continue
        el = elements(cif)
        if {k: el.get(k, 0) for k in EXPECT_EL} != EXPECT_EL or sum(el.values()) != sum(EXPECT_EL.values()):
            bad.append(f'{n} 조성 불일치 {el}')
    if bad:
        print('  !! ' + ' / '.join(bad), flush=True)
        sys.exit(1)
    print(f'  조성 검사 5/5 통과 (총 {sum(EXPECT_EL.values())}원자, S 12, Cl 0)', flush=True)

    # 배포본 water.def 는 3자리라 조용히 다른 물로 계산됩니다.
    nsite = sum(1 for ln in open(rw.WATER_DEF, encoding='utf-8')
                if len(ln.split()) > 4 and ln.split()[1] in ('Ow', 'Hw', 'Lw'))
    print(f'  물 정의 사이트 {nsite}개 (TIP5P-Ew 는 5)', flush=True)
    if nsite != 5:
        print('  !! 5자리 물이 아닙니다. 중단합니다.', flush=True)
        sys.exit(1)
    print(flush=True)

    rc = rw.main()

    src = os.path.join(rw.HERE, 'water_results.json')
    if rc == 0 and os.path.exists(src):
        tag = os.environ.get('WATER_BATCH_TAG') or os.uname().nodename.lower()
        shutil.copy(src, os.path.join(rw.HERE, f'water_results_{tag}.json'))
        print(f'  기기명 사본 저장: water_results_{tag}.json', flush=True)

    sys.exit(rc)
