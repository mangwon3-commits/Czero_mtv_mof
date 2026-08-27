"""`mslm050` 도전 판정 — `MSLM050_CHALLENGE_20260827.md` 3절 식을 그대로 적용한다.

**이 파일은 수를 보기 전에 작성됐습니다** (2026-08-27 17:5x, 계산 착수 17:44,
첫 완주 전). 판정을 손으로 계산하면 그 자리에서 식을 고를 여지가 생기므로,
등록된 식을 코드로 박아 둡니다.

[등록된 식 — 한 글자도 안 바꿉니다]

    d      = |WC(mslm050) - 0.7306|
    SE_ref = 0.0580 / sqrt(6) = 0.0237      6실현 평균의 SE
    SD_new = 0.0794 x WC(mslm050)           습윤 WC 상대 배치 산포 7.94%
                                            saIm0583 앙상블 **n=6** 에서 빌려온 값
                                            (등록 원판은 4.6% = n=5. 아래 정정 참조)
    단위   = d / sqrt(SE_ref^2 + SD_new^2)

[결론 매핑 — 등록문 3절 표 그대로]

    mslm050 이 1.5 단위 이상 높다   ->  **1등 교체**
    차이가 1.5 단위 미만            ->  **띠가 넓어짐. (라) 폐기**
    saIm0583 이 1.5 단위 이상 높다  ->  **(라) 확보**

[반드시 함께 적을 것 — 등록문 지시]
    `mslm050` 은 **실현 하나**입니다. 7.94% 는 `mslm` 계열에서 미측정이라
    빌려온 값이고, 어느 결과가 나오든 **깨지는 f 를 같이 적습니다**
    (COMMS 규약 ⑥-(라)).

[왜 .data 를 직접 읽나]
    `run_humid_wc` 는 세 작업이 다 끝난 뒤 JSON 을 한 번만 씁니다. 판정에
    필요한 것은 ads 와 tsa 뿐이라(WC_tsa = ads - tsa) **vsa 를 기다리지 않고**
    읽을 수 있습니다. 08-27 `saIm050` 앙상블도 같은 이유로 14/15 에서
    판정이 났습니다.

    읽기만 합니다. 아무것도 쓰지 않습니다.

사용:
    python judge_mslm050.py
"""
import glob
import math
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
RUNS = os.path.join(HERE, 'humid_wc_runs_v3mslm050')

# 등록된 상수. 고치지 마십시오 — 고치면 사전 등록이 아니게 됩니다.
M_REF = 0.7306        # saIm0583 6실현 평균 습윤 TSA WC
S_REF = 0.0580        # 그 배치 SD
N_REF = 6
# [2026-08-28 05:xx 정정 — 등록식이 같은 산포를 두 값으로 쓰고 있었습니다]
#   SE_ref 의 0.0580 은 **n=6** SD, SD_new 의 0.046 은 **n=5** SD(0.03271/0.7306
#   = 4.48%) 였습니다. 한 식 안에 같은 모집단의 SD 가 둘 있었고 1.77배 다릅니다.
#   랩탑이 원자료로 확인했습니다(데스크탑에는 ens0583 JSON 이 없음):
#       e1 0.6647 e2 0.6865 e3 0.7401 e4 0.7289 e5 0.7303  생산 0.8328
#       n=5  평균 0.71010  SD 0.03271     n=6  평균 0.73055  SD 0.05801
#
#   **n=6 으로 통일합니다.** 기준 평균이 n=6 이므로 SD 도 같은 6개에서 나온
#   것을 두 항에 씁니다. 0.8328 이 높다는 것은 **사후**에 안 것이고 사전에는
#   다른 다섯과 같은 자격입니다 — 대표값으로 안 쓰는 것과 SD 모집단에서
#   빼는 것은 다른 일입니다.
#
#   ⚠️ **이 정정은 우리에게 유리하지 않습니다.** 중간 구간(=(라) 폐기 분기)이
#   [0.673, 0.795] 폭 0.122 에서 **[0.646, 0.836] 폭 0.190** 으로 넓어집니다.
REL_BATCH = 0.0794    # = 0.05801 / 0.73055.  n=6 일관
THRESHOLD = 1.5

COMP = re.compile(
    r'Component\s+(\d+)\s+\[(\w+)\].*?'
    r'Average loading absolute \[mol/kg framework\]\s+'
    r'([\d.eE+-]+)\s*\+/-\s*([\d.eE+-]+)', re.S)


def read_cond(cond):
    """조건 하나의 완주 결과를 읽는다. 미완주면 None."""
    d = os.path.join(RUNS, f'{cond}_mslm050')
    hits = glob.glob(os.path.join(d, '**', 'System_0', '*.data'), recursive=True)
    if not hits:
        return None
    txt = open(hits[0], encoding='utf-8', errors='ignore').read()
    if 'Simulation finished' not in txt:
        return None
    out = {}
    for _i, name, val, err in COMP.findall(txt):
        out[name] = (float(val), float(err))
    return out or None


def breaking_f(wc):
    """이 차이를 1.5 단위 아래로 눌러 버리는 상대 배치 산포.

    분모에서 SD_new 만 f 에 비례하므로 닫힌 해가 있습니다:
        d / sqrt(SE_ref^2 + (f*wc)^2) = 1.5
    """
    d = abs(wc - M_REF)
    se = S_REF / math.sqrt(N_REF)
    inner = (d / THRESHOLD) ** 2 - se ** 2
    if inner <= 0:
        return 0.0            # 통계만으로도 문턱을 못 넘음
    return math.sqrt(inner) / wc


def main():
    ads, tsa, vsa = read_cond('ads'), read_cond('tsa'), read_cond('vsa')
    print('mslm050 도전 판정 — MSLM050_CHALLENGE_20260827.md 3절')
    print(f'  자료 {RUNS}')
    print(f'  완주  ads {"O" if ads else "-"}  tsa {"O" if tsa else "-"} '
          f' vsa {"O" if vsa else "-"}   (판정에는 ads·tsa 만 필요)')
    if not (ads and tsa):
        print('\n  ads 또는 tsa 미완주. 판정 불가.')
        return 1

    a, ea = ads['CO2']
    t, et = tsa['CO2']
    wc = a - t
    print(f'\n  ads CO2  {a:.4f} ± {ea:.4f}     물 {ads.get("water", (0,))[0]:.4f}')
    print(f'  tsa CO2  {t:.4f} ± {et:.4f}     물 {tsa.get("water", (0,))[0]:.4f}')
    print(f'  **습윤 TSA WC = {wc:.4f} mol/kg**')
    if vsa:
        v = vsa['CO2'][0]
        print(f'  (참고) vsa CO2 {v:.4f}  -> VSA WC {a - v:.4f}')

    se = S_REF / math.sqrt(N_REF)
    sd = REL_BATCH * wc
    den = math.hypot(se, sd)
    d = abs(wc - M_REF)
    u = d / den

    print(f'\n=== 등록된 식 ===')
    print(f'  d      = |{wc:.4f} - {M_REF}| = {d:.4f}')
    print(f'  SE_ref = {S_REF}/sqrt({N_REF}) = {se:.4f}')
    print(f'  SD_new = {REL_BATCH} x {wc:.4f} = {sd:.4f}   <- **빌려온 값**')
    print(f'  단위   = {d:.4f} / {den:.4f} = **{u:.2f}**    문턱 {THRESHOLD}')

    print(f'\n=== 결론 (등록문 3절 표) ===')
    if u >= THRESHOLD and wc > M_REF:
        print('  **1등 교체** — 대표 조성을 mslm050 으로 바꾸고')
        print('  그 계열로 앙상블·저압을 다시 짠다.')
    elif u >= THRESHOLD:
        print('  **(라) 확보** — 관문 통과 상대를 이겼으므로')
        print('  (라)가 처음으로 제대로 선다.')
    else:
        print('  **띠가 넓어진다** — 1등은 "치환기 종류가 아니라 치환 자체".')
        print('  (라)를 폐기하고 두 계열을 나란히 적는다.')

    f = breaking_f(wc)
    print(f'\n=== 규약 ⑥-(라) — 깨지는 배치 산포 ===')
    if u >= THRESHOLD:
        print(f'  f = **{f:.1%}**   빌려온 {REL_BATCH:.1%} 의 {f/REL_BATCH:.2f}배')
        print(f'  -> mslm 계열 배치 산포가 이보다 크면 이 판정이 무너집니다.')
    else:
        print(f'  이미 문턱 아래라 f 를 논할 대상이 아닙니다.')
        need = d / THRESHOLD
        print(f'  참고: 1.5 단위가 되려면 분모가 {need:.4f} 이하여야 하는데')
        print(f'        SE_ref 만으로 이미 {se:.4f} 입니다.')

    print(f'\n※ mslm050 은 **실현 하나**입니다. {REL_BATCH:.2%} 는 mslm 계열 미측정이고')
    print(f'  saIm0583 앙상블에서 빌려왔습니다 (등록문이 명시한 한계).')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
