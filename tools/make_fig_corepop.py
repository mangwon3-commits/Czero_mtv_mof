# -*- coding: utf-8 -*-
"""그림 10 — §AW·§AW-2 판정의 그림: **세 축에서 우리 물질이 어디 있나** (524종, 우리 자).

판정 `COREWC_VERDICT_20260924.md` + 정정 `GATE_SAIM100_20260924.md`.
⚠ 대표는 **관문 통과** 조성입니다. `saIm100`(LCD 감소 22.5 %)은 **쓰지 않습니다.**
"""
import json, os, sys
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
import numpy as np
import statistics as st

FP = '/mnt/c/Windows/Fonts/malgun.ttf'
fm.fontManager.addfont(FP); fm.fontManager.addfont('/mnt/c/Windows/Fonts/malgunbd.ttf')
plt.rcParams['font.family'] = fm.FontProperties(fname=FP).get_name()
plt.rcParams['axes.unicode_minus'] = False
# ⚠ 로그 축 눈금(10^-5)은 **mathtext** 로 그려지고, mathtext 는 위 `font.family` 가 아니라
#   `mathtext.fontset` 을 씁니다. Malgun 에 U+2212(−)가 없어 `10¤5` 로 깨졌습니다.
#   `axes.unicode_minus=False` 는 **일반 눈금에만** 듣습니다 — 그래서 둘 다 필요합니다.
plt.rcParams['mathtext.fontset'] = 'dejavusans'
plt.rcParams['font.size'] = 9
plt.rcParams['axes.edgecolor'] = '#4A4A4A'
plt.rcParams['axes.linewidth'] = 0.8

NAVY, ORANGE, SAGE = '#1F3B57', '#E08A3C', '#8FA37E'
SAGE_L, GREY, GREY_L = '#D6DFCC', '#9A9A9A', '#ECECEC'
H = '21_ZIF69_MTV'
OUT = '04_Analysis/figs/'
sys.path.insert(0, H)
import analyze_core_wc as A                      # 판정과 **같은** load_all·pct 를 씁니다

rows, _ = A.load_all()
L = sorted(r['n_0.15bar'] for r in rows.values())
pop = json.load(open(os.path.join(H, 'core_pop_merged.json')))
pr = pop['rows'] if isinstance(pop, dict) else pop
SEL = sorted(r['selectivity'] for r in pr if r.get('selectivity'))
KH = sorted(r['KH_CO2'] for r in pr if r.get('KH_CO2'))

gate = {}
for f in ('risk_results_v3.json', 'risk_results_v3grid.json'):
    for r in json.load(open(os.path.join(H, f)))['rows']:
        gate[r['name']] = r['pass']
ours = {r['name']: r for r in json.load(open(os.path.join(H, 'results_v3.json')))['rows']}
# ⚠ 「우리 조성」의 정의는 **등록 그대로 `results_v3.json` 의 31조성**입니다
#   (`COREPOP_REGISTRATION §5` · `COREWC_REGISTRATION §4`). 그중 **관문 통과 28**.
#   `saIm0583` 은 격자 파일(`results_v3grid`)에 있어 **그 28 에 안 들어갑니다** —
#   대표로 따로 표시하되 **중앙값 계산에는 안 넣습니다.** 기록된 정정문(28조성 중앙 0.730)과
#   같은 수를 내기 위해서입니다. 수를 하나 더 넣으면 중앙이 0.7315 로 **조용히** 달라집니다.
G = [n for n in ours if gate.get(n)]              # 관문 통과 28
grid = {r['name']: r for r in json.load(open(os.path.join(H, 'results_v3grid.json')))['rows']}

CAND = grid['saIm0583']                           # 설계 후보 = 관문 통과 상한(격자 파일)
AXES = [
    ('CO$_2$/N$_2$ 선택도', SEL, CAND['selectivity'],
     [ours[n]['selectivity'] for n in G], True),
    ('K$_H$(CO$_2$)  [mol/kg/Pa]', KH, CAND['KH_CO2'],
     [ours[n]['KH_CO2'] for n in G], True),
    ('0.15 bar CO$_2$ 적재  [mmol/g]', L, CAND['loading_015bar'],
     [ours[n]['loading_015bar'] for n in G], False),
]

fig, axes = plt.subplots(3, 1, figsize=(6.6, 5.4))
for ax, (name, pool, v, mine, logx) in zip(axes, AXES):
    p = A.pct(pool, v)
    lo, hi = min(pool), max(pool)
    bins = (np.logspace(np.log10(lo), np.log10(hi), 46) if logx
            else np.linspace(lo, hi, 46))
    ax.hist(pool, bins=bins, color=GREY_L, edgecolor=GREY, linewidth=.35, zorder=1)
    if logx:
        ax.set_xscale('log')
        # ⚠ 로그 눈금의 기본 서식은 mathtext 이고 거기 음수 부호가 **U+2212** 입니다.
        #   Malgun 에 그 글리프가 없어 `10¤5` 로 깨집니다(`mathtext.fontset` 로도 안 잡힘).
        #   그래서 **ASCII 만으로** 직접 씁니다. 깨진 축은 그림의 결함이지 취향이 아닙니다.
        import matplotlib.ticker as mt

        def _lab(v, _):
            e = int(round(np.log10(v)))
            if abs(v - 10.0 ** e) > 1e-9 * max(1.0, abs(v)):
                return ''
            return ('%g' % v) if -2 <= e <= 3 else ('1e%d' % e)

        ax.xaxis.set_major_formatter(mt.FuncFormatter(_lab))
        ax.xaxis.set_minor_formatter(mt.NullFormatter())
    ax.scatter(mine, [ax.get_ylim()[1] * .13] * len(mine), marker='|', s=90,
               color=SAGE, linewidths=1.1, zorder=3, label='우리 관문 통과 %d조성' % len(mine))
    ax.axvline(st.median(pool), color=GREY, ls=':', lw=1.2, zorder=2,
               label='풀 중앙 (524종)')
    ax.axvline(v, color=ORANGE, lw=2.0, zorder=4)
    ax.annotate('saIm0583\n%s %.1f %%' % ('상위' if p > 50 else '백분위',
                                          (100 - p) if p > 50 else p),
                xy=(v, ax.get_ylim()[1] * .62), xytext=(6, 0),
                textcoords='offset points', color=ORANGE, fontsize=8.6,
                va='center', ha='left', weight='bold')
    ax.set_xlabel(name); ax.set_ylabel('구조 수')
    ax.grid(alpha=.22, ls=':', color=GREY, axis='y')
    ax.tick_params(labelsize=8)

axes[0].legend(loc='upper right', fontsize=7.8, framealpha=.92)
fig.suptitle('같은 자(524종·우리 프로토콜) 위에서 세 축의 자리는 다릅니다',
             fontsize=10.5, y=.995)
fig.text(.5, .003,
         '대표 = saIm0583 (구조 관문 통과 상한). saIm100 은 관문 탈락(LCD 감소 22.5 %)이라 쓰지 않습니다.',
         ha='center', fontsize=7.6, color=GREY)
fig.tight_layout(rect=[0, .022, 1, .975])
os.makedirs(OUT, exist_ok=True)
fig.savefig(OUT + 'fig10_corepop_axes.png', dpi=220, bbox_inches='tight',
            facecolor='white')
print('  fig10_corepop_axes.png')
for name, pool, v, mine, _ in AXES:
    print('  %-28s saIm0583 %-12.4g 백분위 %5.1f %%  (우리 통과 %d조성 중앙 %.4g)'
          % (name.split('  ')[0], v, A.pct(pool, v), len(mine), st.median(mine)))
