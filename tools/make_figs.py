# -*- coding: utf-8 -*-
"""보고서 그림 생성 — 네이비/오렌지/세이지 팔레트.

방침: 그래프 위에 제목·화살표 주석·설명 문구를 넣지 않는다.
축 이름과 범례만 둔다. 해설은 보고서 본문 캡션이 맡는다.
"""
import json, math, os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
import numpy as np

FP = '/mnt/c/Windows/Fonts/malgun.ttf'
fm.fontManager.addfont(FP); fm.fontManager.addfont('/mnt/c/Windows/Fonts/malgunbd.ttf')
plt.rcParams['font.family'] = fm.FontProperties(fname=FP).get_name()
plt.rcParams['axes.unicode_minus'] = False        # Malgun 에 U+2212 없음
plt.rcParams['font.size'] = 9
plt.rcParams['axes.edgecolor'] = '#4A4A4A'
plt.rcParams['axes.linewidth'] = 0.8

NAVY  = '#1F3B57'
ORANGE= '#E08A3C'
SAGE  = '#8FA37E'
SAGE_L= '#D6DFCC'      # 세이지 음영
ORNG_L= '#F5DCC2'      # 오렌지 음영
GREY  = '#9A9A9A'
GREY_L= '#ECECEC'

Z = '21_ZIF69_MTV/'
OUT = '04_Analysis/figs/'
SUB = '-SO$_3$H 치환율 (%)'
os.makedirs(OUT, exist_ok=True)

rows = {}
for f in ('results_v3.json', 'results_v3grid.json', 'results_v4mix.json'):
    for r in json.load(open(Z + f))['rows']:
        if r.get('status') == 'ok':
            rows[r['name']] = r
risk = {}
for f in ('risk_results_v3grid.json', 'risk_results_v3.json'):
    for r in json.load(open(Z + f))['rows']:
        risk[r['name']] = r['LCD_drop_pct']


def finish(fig, name):
    fig.savefig(OUT + name, dpi=220, bbox_inches='tight', facecolor='white')
    plt.close(fig)
    print('  ', name)


# ── 그림 2 : 치환율 사다리 ───────────────────────────────
tags = [('base', 0), ('saIm025', 25), ('saIm050', 50), ('saIm0583', 58.3),
        ('saIm075', 75), ('saIm0875', 87.5), ('saIm100', 100)]
x = [f for _, f in tags]
q = [rows[t]['Qst_CO2'] for t, _ in tags]
qe = [rows[t]['Qst_CO2_err'] for t, _ in tags]
ld = [rows[t]['loading_015bar'] for t, _ in tags]
le = [rows[t]['loading_015bar_err'] for t, _ in tags]

fig, ax = plt.subplots(figsize=(6.2, 3.2))
ax.axhspan(30, 40, color=SAGE_L, alpha=.75, zorder=0)
ax.errorbar(x, q, yerr=qe, marker='o', color=NAVY, lw=1.7, ms=5.5,
            capsize=3, zorder=3, label='Q$_{st}$ (좌축)')
ax.set_xlabel(SUB); ax.set_ylabel('Q$_{st}$ (kJ/mol)', color=NAVY)
ax.tick_params(axis='y', labelcolor=NAVY)
ax.set_ylim(20, 42); ax.set_xlim(-4, 104)
ax2 = ax.twinx()
ax2.errorbar(x, ld, yerr=le, marker='s', color=ORANGE, lw=1.7, ms=5.5,
             capsize=3, ls='--', label='0.15 bar 로딩 (우축)')
ax2.set_ylabel('0.15 bar CO$_2$ 로딩 (mol/kg)', color=ORANGE)
ax2.tick_params(axis='y', labelcolor=ORANGE); ax2.set_ylim(0.4, 1.75)
h1, l1 = ax.get_legend_handles_labels(); h2, l2 = ax2.get_legend_handles_labels()
ax.legend(h1 + h2, l1 + l2, loc='lower right', fontsize=8.5, framealpha=.92)
ax.grid(alpha=.25, ls=':', color=GREY)
finish(fig, 'fig2_ladder.png')


# ── 그림 3 : 수분 경쟁 ──────────────────────────────────
w = json.load(open(Z + 'v3_water/water_results.json'))
comp = ['base', 'saIm025', 'saIm050', 'saIm075', 'saIm100']
xs = [0, 25, 50, 75, 100]
ret, rerr, ratio = [], [], []
for c in comp:
    r0 = [r for r in w if r['name'] == c and r['RH'] == 0.0][0]
    r9 = [r for r in w if r['name'] == c and r['RH'] == 0.9][0]
    ret.append(r9['CO2_retention_pct'])
    rerr.append(r9['CO2_retention_pct'] * math.sqrt(
        (r9['CO2_err'] / r9['CO2_molkg']) ** 2 + (r0['CO2_err'] / r0['CO2_molkg']) ** 2))
    ratio.append(r9['H2O_over_CO2'])

fig, ax = plt.subplots(figsize=(6.2, 3.2))
ax.axhspan(80, 113, color=SAGE_L, alpha=.8, zorder=0)
ax.axhspan(50, 80, color=ORNG_L, alpha=.7, zorder=0)
ax.errorbar(xs, ret, yerr=rerr, marker='o', color=NAVY, lw=1.7, ms=6,
            capsize=3, zorder=3, label='RH90 유지율 (좌축)')
ax.set_xlabel(SUB); ax.set_ylabel('RH90 CO$_2$ 유지율 (%)', color=NAVY)
ax.tick_params(axis='y', labelcolor=NAVY)
ax.set_ylim(48, 113); ax.set_xlim(-5, 105)
ax2 = ax.twinx()
ax2.plot(xs, ratio, marker='^', color=ORANGE, lw=1.7, ms=6.5, ls='--',
         label='H$_2$O / CO$_2$ (우축)')
ax2.set_ylabel('흡착 시 H$_2$O / CO$_2$', color=ORANGE)
ax2.tick_params(axis='y', labelcolor=ORANGE); ax2.set_ylim(0.6, 2.88)
h1, l1 = ax.get_legend_handles_labels(); h2, l2 = ax2.get_legend_handles_labels()
ax.legend(h1 + h2, l1 + l2, loc='upper right', ncol=2, fontsize=8.5, framealpha=.92)
ax.grid(alpha=.25, ls=':', color=GREY)
finish(fig, 'fig3_water.png')


# ── 그림 4 : 두 관문 ────────────────────────────────────
g = [('saIm050', 50), ('saIm0583', 58.3), ('saIm0625', 62.5), ('saIm0667', 66.7),
     ('saIm075', 75), ('saIm0875', 87.5), ('saIm100', 100)]
gx = [f for _, f in g]
gq = [rows[t]['Qst_CO2'] for t, _ in g]
gqe = [rows[t]['Qst_CO2_err'] for t, _ in g]
gl = [risk[t] for t, _ in g]

fig, (a1, a2) = plt.subplots(2, 1, figsize=(6.2, 4.3), sharex=True,
                             gridspec_kw={'hspace': 0.12})
a1.axhspan(30, 35.6, color=SAGE_L, alpha=.75, zorder=0)
a1.axvspan(58.3, 75, color=GREY_L, alpha=.85, zorder=0)
a1.axhline(30, color=SAGE, ls='--', lw=1.3, zorder=2, label='흡착 문턱 30 kJ/mol')
a1.errorbar(gx, gq, yerr=gqe, marker='o', color=NAVY, lw=1.7, ms=5.5,
            capsize=3, zorder=3, label='Q$_{st}$')
a1.set_ylabel('Q$_{st}$ (kJ/mol)'); a1.set_ylim(27.5, 35.6)
a1.legend(loc='lower right', fontsize=8.5, framealpha=.92)
a1.grid(alpha=.25, ls=':', color=GREY)

a2.axhspan(12.5, 20, color=SAGE_L, alpha=.75, zorder=0)
a2.axvspan(58.3, 75, color=GREY_L, alpha=.85, zorder=0)
a2.axhline(20, color=ORANGE, ls='--', lw=1.3, zorder=2, label='안정성 탈락선 20%')
a2.plot(gx, gl, marker='s', color=NAVY, lw=1.7, ms=5.5, zorder=3,
        label='LCD 감소')
a2.set_ylabel('LCD 감소 (%)'); a2.set_xlabel(SUB)
a2.set_ylim(12.5, 23.5); a2.invert_yaxis()
a2.legend(loc='upper right', fontsize=8.5, framealpha=.92)
a2.grid(alpha=.25, ls=':', color=GREY)
a1.set_xlim(48, 102)
finish(fig, 'fig4_windows.png')


# ── 그림 5 : 습윤 작업 용량 ─────────────────────────────
hw = {}
for f in ('humid_working_capacity.json', 'humid_working_capacity_g0583.json'):
    for r in json.load(open(Z + 'v3_humid_wc/' + f))['rows']:
        hw[r['name']] = r
v4 = {}
for f in ('humid_working_capacity_v4m1.json', 'humid_working_capacity_v4ext.json'):
    for r in json.load(open(Z + 'v4_humid_wc/' + f))['rows']:
        v4[r['name']] = r

fig, (a1, a2) = plt.subplots(1, 2, figsize=(6.6, 3.1),
                             gridspec_kw={'width_ratios': [1.25, 1]})
names = [('base', '무치환', True), ('saIm050', '50%', True),
         ('saIm0583', '58.3%', True), ('saIm075', '75%', False),
         ('saIm100', '100%', False)]
xs = np.arange(len(names))
v = [hw[n]['working_capacity']['tsa']['value'] for n, _, _ in names]
e = [hw[n]['working_capacity']['tsa']['err'] for n, _, _ in names]
cols = [NAVY if ok else GREY for _, _, ok in names]
a1.bar(xs, v, yerr=e, capsize=3, color=cols, edgecolor='#3A3A3A', lw=.6)
a1.set_xticks(xs); a1.set_xticklabels([lb for _, lb, _ in names], fontsize=8.5)
a1.set_ylabel('습윤 TSA 작업 용량 (mol/kg)'); a1.set_ylim(0, 1.0)
a1.set_xlabel('-SO$_3$H 단독 치환')
a1.bar(0, 0, color=NAVY, label='안정성 관문 통과')
a1.bar(0, 0, color=GREY, label='관문 탈락')
a1.legend(fontsize=8, loc='upper left', framealpha=.92)
a1.grid(alpha=.25, ls=':', axis='y', color=GREY)

nm = [('-SO$_3$H\n58.3%', hw['saIm0583']['working_capacity']['tsa'], NAVY),
      ('-SO$_3$H50\n+-NO$_2$50', v4['sa50nb50']['working_capacity']['tsa'], ORANGE),
      ('-SO$_2$CH$_3$50\n+-NO$_2$50', v4['ms50nb50']['working_capacity']['tsa'], SAGE),
      ('-SO$_3$H25\n+-NO$_2$75', v4['sa25nb75']['working_capacity']['tsa'], SAGE)]
xs2 = np.arange(len(nm))
a2.bar(xs2, [d['value'] for _, d, _ in nm], yerr=[d['err'] for _, d, _ in nm],
       capsize=3, color=[c for _, _, c in nm], edgecolor='#3A3A3A', lw=.6)
a2.set_xticks(xs2); a2.set_xticklabels([lb for lb, _, _ in nm], fontsize=7.5)
a2.set_ylim(0, 1.0); a2.set_xlabel('단일 vs 혼합 치환')
a2.grid(alpha=.25, ls=':', axis='y', color=GREY)
fig.tight_layout()
finish(fig, 'fig5_wc.png')


# ── 그림 6 : Q_st 창 (모형 곡선) ────────────────────────
R = 8.314e-3; A, B = -13.979, 0.4511; T1, T2 = 298.0, 373.0; P = 15000.0


def KH(Q, T):
    return math.exp(A + B * (Q / (R * T1))) * math.exp((Q / R) * (1 / T - 1 / T1))


def wc(Q, ns):
    f = []
    for T in (T1, T2):
        b = KH(Q, T) / ns
        f.append(ns * b * P / (1 + b * P))
    return f[0] - f[1]


Qs = np.arange(18, 60.1, 0.25)
fig, ax = plt.subplots(figsize=(6.2, 3.1))
ax.axvspan(30, 40, color=SAGE_L, alpha=.8, zorder=0)
for ns, col, ls in ((2.0, SAGE, ':'), (2.5, NAVY, '-'), (4.0, ORANGE, '--')):
    E = [Q + 67.5 / wc(Q, ns) for Q in Qs]
    ax.plot(Qs, E, ls, lw=1.8, color=col, label=f'n$_{{sat}}$ = {ns} mol/kg')
    i = int(np.argmin(E))
    ax.plot(Qs[i], E[i], 'v', ms=7, color=col, mec='#3A3A3A', mew=.6)
ax.set_xlabel('Q$_{st}$ (kJ/mol)')
ax.set_ylabel('총 재생 에너지 (kJ/mol-CO$_2$)')
ax.set_ylim(50, 230); ax.set_xlim(18, 60)
ax.legend(fontsize=8.5, framealpha=.92)
ax.grid(alpha=.25, ls=':', color=GREY)
finish(fig, 'fig6_window.png')
print('\n완료 — 팔레트 navy %s / orange %s / sage %s' % (NAVY, ORANGE, SAGE))
