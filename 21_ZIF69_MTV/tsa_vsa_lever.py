"""TSA 와 VSA 의 지렛대 크기를 같은 단위로 환산한다 (Part 0-C 2-2절의 근거).

[무엇을 계산하나]
    "온도를 298 -> 373 K 로 올리는 것은 압력을 몇 배로 낮추는 것과 같은가."
    같은 흡착량을 유지하는 조건에서 van't Hoff:

        (d ln P / d(1/T))_n = -Q_st / R
        P2/P1 = exp[ (Q_st/R) (1/T1 - 1/T2) ]

    이 값이 TSA 의 지렛대입니다. VSA 의 지렛대는 그냥 압력비(0.15/0.05 = 3)이고
    **Q_st 와 무관하게 고정**입니다.

[왜 이 비교가 중요한가]
    TSA 지렛대는 지수 안에 Q_st 가 들어 있어 **강하게 잡는 물질일수록 커집니다.**
    VSA 는 안 커집니다. 그래서 치환율을 올릴수록 TSA 는 유리해지고 VSA 는
    불리해집니다.

    **이 부분은 항등식이라 자료 판본에 안 흔들립니다** — 지렛대 비교 자체는
    van't Hoff 와 압력비만으로 나옵니다. 흔들리는 것은 아래 예시 숫자입니다.

[2026-08-27 — v2 숫자가 박혀 있었습니다]
    이 파일은 `ROWS` 에 Q_st 와 회수율을 **손으로 적어** 두고 있었고, 그 값들이
    `results_v2.json` 과 소수점까지 일치했습니다. **판본 표기는 어디에도
    없었습니다.** v3 로 다시 내면:

        조성        Qst v2 -> v3     VSA 회수율 v2 -> v3
        base        21.08 -> 22.42      64.2 -> 60.0
        saIm025     24.45 -> 27.97      61.2 -> 54.8
        saIm050     26.97 -> 29.51      55.6 -> 54.3
        saIm075     32.32 -> 31.42      42.3 -> 48.9
        mslm075   **36.90 -> 29.01**      —  -> 53.2

    **`mslm075` 가 21% 낮아지면서 Q_st 순위가 뒤집힙니다** — v2 에서는 1위였고
    v3 에서는 `saIm075`·`saIm050` 아래 3위입니다. 이 표를 보고 "−SO₂CH₃ 가
    TSA 지렛대가 제일 크다" 고 읽으면 **폐기된 자료를 인용하는 것**입니다.

    그래서 이제 **`results_v3.json` 과 `v3_wc/` 에서 직접 읽습니다.** 조성을
    손으로 적지 않으므로 새 조성이 생기면 저절로 붙고, 판본이 섞일 수 없습니다.

[v3 로 고치니 논증이 오히려 깨끗해졌습니다]
    v2 판에서는 TSA 회수율이 50% 까지 오르다 75% 에서 꺾여서, 그 꺾임을 "단일
    Q_st 가정의 한계" 로 설명하는 단락이 필요했습니다. **v3 에서는 꺾임이
    없습니다:**

        실측 TSA 회수율   83.9 ~ 86.4%   폭 2.4%p    거의 안 변함
        실측 VSA 회수율   60.0 -> 47.0%  폭 13.0%p   치환율 따라 떨어짐

    이것이 지렛대 논증이 **예상하는 바로 그 모양**입니다 — TSA 는 Q_st 가 커진
    만큼 지렛대도 같이 커져 회수율을 지켜내고, VSA 는 지렛대가 3배로 고정이라
    못 버팁니다. v2 의 꺾임은 설명이 필요한 예외였는데, v3 에서는 설명할 것이
    없습니다.

[한계]
    단일 Q_st 를 가정합니다. 실제 골격은 자리마다 결합 세기가 다르고, 치환기가
    늘면 유난히 센 소수의 자리가 생깁니다. 이 표는 평균 하나로 낸 것입니다.

    회수율은 **생산 실현 하나씩**의 값입니다. TSA 쪽 폭 2.4%p 는 건조 로딩
    배치 산포(6.7%) 안이라 **조성 간 순위로 읽으면 안 됩니다.** VSA 쪽 13.0%p
    는 그보다 큽니다.
"""
import glob
import json
import math
import os

R = 8.314e-3          # kJ/(mol K)
T1, T2 = 298.0, 373.0
P_ADS, P_VSA05, P_VSA10 = 0.15, 0.05, 0.10

HERE = os.path.dirname(os.path.abspath(__file__))

# 보기 좋은 이름. 없는 조성은 태그를 그대로 씁니다 — 손으로 적은 목록이 아니라
# 표시용 사전이라, 빠져도 행이 사라지지 않습니다.
LABEL = {'base': '무치환', 'saIm025': 'SO3H 25%', 'saIm050': 'SO3H 50%',
         'saIm0583': 'SO3H 58.3%', 'saIm075': 'SO3H 75%', 'saIm100': 'SO3H 100%',
         'mslm050': 'SO2CH3 50%', 'mslm075': 'SO2CH3 75%'}


def load_qst():
    """v3 건조 GCMC 에서 Q_st. 앙상블이 있는 조성은 실현 평균을 씁니다."""
    q = {}
    for f in ('results_v3.json', 'results_v3grid.json', 'results_v3cliff.json',
              'results_v4mix.json'):
        p = os.path.join(HERE, f)
        if not os.path.exists(p):
            continue
        d = json.load(open(p, encoding='utf-8'))
        for r in (d['rows'] if isinstance(d, dict) and 'rows' in d else d):
            if isinstance(r, dict) and r.get('Qst_CO2'):
                q.setdefault(r['name'], r['Qst_CO2'])
    # 앙상블은 평균으로 덮어씁니다 — 실현 하나보다 낫습니다
    for p in glob.glob(os.path.join(HERE, 'results_v3ens*.json')):
        d = json.load(open(p, encoding='utf-8'))
        rows = d['rows'] if isinstance(d, dict) and 'rows' in d else d
        vals = [r['Qst_CO2'] for r in rows if isinstance(r, dict) and r.get('Qst_CO2')]
        if vals:
            base = rows[0]['name'].rsplit('e', 1)[0]
            q[base] = sum(vals) / len(vals)
    return q


def load_recovery():
    """v3 건조 작업 용량에서 회수율 = WC / 흡착량."""
    rec = {}
    for p in glob.glob(os.path.join(HERE, 'v3_wc', '*.json')):
        d = json.load(open(p, encoding='utf-8'))
        for r in (d['rows'] if isinstance(d, dict) and 'rows' in d else d):
            if not isinstance(r, dict) or 'working_capacity' not in r:
                continue
            ads = r.get('loadings', {}).get('ads', {}).get('mol_per_kg')
            if not ads:
                continue
            wc = r['working_capacity']
            rec[r['name']] = (wc.get('tsa', {}).get('value', 0) / ads * 100,
                              wc.get('vsa05', {}).get('value', 0) / ads * 100)
    return rec


def main():
    qst, rec = load_qst(), load_recovery()
    # 표는 **회수율까지 있는 조성**만 싣습니다. 지렛대와 실측을 나란히 놓는 것이
    # 이 표의 목적이라, Q_st 만 있는 조성은 빈 칸만 늘립니다. 손으로 고르는 게
    # 아니라 자료 보유 여부로 갈리므로 새 측정이 생기면 저절로 붙습니다.
    shown = sorted([n for n in qst if n in rec], key=lambda n: qst[n])
    only_q = [n for n in qst if n not in rec]

    inv = 1.0 / T1 - 1.0 / T2
    print('자료: results_v3*.json + v3_wc/  (판본 v3, 손으로 적은 조성 목록 없음)')
    print(f'1/T1 - 1/T2 = {inv:.6e}  (T1={T1:.0f} K, T2={T2:.0f} K)')
    print(f'VSA 지렛대 = P_ads/P_des = {P_ADS/P_VSA05:.1f} 배 (0.05 bar), '
          f'{P_ADS/P_VSA10:.1f} 배 (0.10 bar) — Q_st 와 무관하게 고정\n')

    print(f'{"조성":<12} {"Q_st":>6} {"지수":>7} {"TSA 지렛대":>11} '
          f'{"VSA 지렛대":>10} {"TSA/VSA":>8} | {"실측 TSA":>9} {"실측 VSA":>9}')
    print('-' * 92)
    for n in shown:
        q = qst[n]
        ex = (q / R) * inv
        lev = math.exp(ex)
        rt, rv = rec[n]
        print(f'{LABEL.get(n, n):<12} {q:>6.2f} {ex:>7.4f} {lev:>10.1f}배 '
              f'{P_ADS/P_VSA05:>9.1f}배 {lev/(P_ADS/P_VSA05):>7.1f}배 | '
              f'{rt:>8.1f}% {rv:>8.1f}%')
    print('-' * 92)

    lo, hi = qst[shown[0]], qst[shown[-1]]
    print('\n지수 안에 Q_st 가 들어 있으므로 TSA 지렛대는 Q_st 에 **지수적으로** 커집니다.')
    print(f'{LABEL.get(shown[0], shown[0])} {math.exp(lo/R*inv):.1f}배 -> '
          f'{LABEL.get(shown[-1], shown[-1])} {math.exp(hi/R*inv):.1f}배. '
          f'VSA 는 내내 {P_ADS/P_VSA05:.0f}배입니다.')

    # 실측이 모형을 어떻게 따라가는가 — 두 축을 각각 봅니다
    tsa = [rec[n][0] for n in shown]
    vsa = [rec[n][1] for n in shown]
    print(f'\n실측 TSA 회수율 {min(tsa):.1f} ~ {max(tsa):.1f}% (폭 {max(tsa)-min(tsa):.1f}%p) — '
          f'치환율이 올라도 **거의 안 변합니다**')
    print(f'실측 VSA 회수율 {max(vsa):.1f} -> {min(vsa):.1f}% (폭 {max(vsa)-min(vsa):.1f}%p) — '
          f'치환율이 오를수록 **떨어집니다**')
    print('지렛대 논증이 예상하는 모양입니다. TSA 는 Q_st 가 커진 만큼 지렛대도 커져')
    print('회수율을 지켜내고, VSA 는 지렛대가 3배로 고정이라 못 버팁니다.')

    print('\n회수율은 생산 실현 하나씩의 값입니다. TSA 쪽 폭은 건조 로딩 배치')
    print('산포(6.7%) 안이라 조성 간 순위로 읽으면 안 됩니다. VSA 쪽 폭은 그보다 큽니다.')
    if only_q:
        print(f'\nQ_st 만 있고 회수율이 없는 조성 {len(only_q)}개는 표에서 뺐습니다 '
              f'(측정되면 저절로 붙습니다).')


if __name__ == '__main__':
    main()
