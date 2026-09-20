# -*- coding: utf-8 -*-
"""스크리닝 그림 — `make_figs.py` 와 같은 팔레트·같은 방침.

방침(그대로): 그래프 위에 제목·화살표 주석·설명 문구를 넣지 않는다. 축 이름과 범례만 둔다.

[무엇을 그리나 — 그리고 무엇을 **안** 그리나]
    그립니다   · CoRE 관문 통과 집단의 **기하 축**(PLD) 위에 우리 조성  — Zeo++ 로 같은 방식으로 잰 양이라 온전합니다.
               · CoRE 물 분류 문턱(되찾은 규칙) 위에 우리 물 K_H       — 분류 경계라 눈금 문제가 없습니다.
               · 우리 계열 안의 선택도 대 물 친화도                     — 같은 프로토콜끼리입니다.
    안 그립니다 · 우리 값과 CoRE 값을 **같은 성능 축**에 섞는 그림.
               힘장이 달라 중앙값 비가 K_H 1.2~3.1배·선택도 2.3~3.5배이고, 그 오프셋이 주장하려는 효과와
               같은 크기입니다(`23_SCREENING/OURS_VS_CORE_20260920.md §0`).
               T-BR-1 이 그 배율을 쟀고, **2026-09-21 03:03 에 등록 §5 (ㄱ)에 걸려 철회됐습니다** —
               두 눈금은 배수 관계가 아닙니다 (K_H β=0.333 · 선택도 β=-0.184).
               판정 `21_ZIF69_MTV/BRIDGE_CORE_RESULT_20260921.md`
               등록 `21_ZIF69_MTV/BRIDGE_CORE_REGISTRATION_20260920.md §5`.
               **환산 패널은 붙이지 않습니다.** 아래 세 그림이 최종 구성입니다.
"""
import json
import os

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt                      # noqa: E402
import numpy as np                                   # noqa: E402
from matplotlib import font_manager as fm            # noqa: E402

FP = '/mnt/c/Windows/Fonts/malgun.ttf'
fm.fontManager.addfont(FP)
fm.fontManager.addfont('/mnt/c/Windows/Fonts/malgunbd.ttf')
plt.rcParams['font.family'] = fm.FontProperties(fname=FP).get_name()
plt.rcParams['axes.unicode_minus'] = False
# Malgun 에 U+2212 가 없어 로그 눈금의 10^-4 가 깨집니다. **수식만** DejaVu 로 못 박습니다.
# (fontset='dejavusans' 만으로는 \mathdefault 가 여전히 font.family 를 따라가 안 고쳐집니다.)
plt.rcParams['mathtext.fontset'] = 'custom'
plt.rcParams['mathtext.rm'] = 'DejaVu Sans'
plt.rcParams['mathtext.it'] = 'DejaVu Sans:italic'
plt.rcParams['mathtext.bf'] = 'DejaVu Sans:bold'
plt.rcParams['font.size'] = 9
plt.rcParams['axes.edgecolor'] = '#4A4A4A'
plt.rcParams['axes.linewidth'] = 0.8

NAVY, ORANGE, SAGE = '#1F3B57', '#E08A3C', '#8FA37E'
SAGE_L, ORNG_L = '#D6DFCC', '#F5DCC2'
GREY, GREY_L = '#9A9A9A', '#ECECEC'

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
Z = os.path.join(ROOT, '21_ZIF69_MTV') + os.sep
SC = os.path.join(ROOT, '23_SCREENING') + os.sep
OUT = os.path.join(ROOT, '04_Analysis', 'figs') + os.sep
SUB = '-SO$_3$H 치환율 (%)'
os.makedirs(OUT, exist_ok=True)

import sys                                           # noqa: E402
sys.path.insert(0, SC)
from screen_core import apply_gates, extract, load_core   # noqa: E402
from water_class import THRESH_KH, SAFE_MARGIN           # noqa: E402


def log_ticks(ax, axis='y'):
    """로그 눈금 라벨을 **직접** 씁니다.

    matplotlib 의 LogFormatter 는 `\\mathdefault{10^{-4}}` 를 내는데, 그 경로가
    `axes.unicode_minus` 도 `mathtext.*` rcParam 도 안 따라가서 Malgun 에 없는
    U+2212 가 그대로 나갑니다(`10¤4` 로 깨짐). 같은 내용을 우리가 쓰면 멀쩡합니다.
    """
    from matplotlib.ticker import LogLocator, NullFormatter
    a = ax.yaxis if axis == 'y' else ax.xaxis
    lo, hi = (ax.get_ylim() if axis == 'y' else ax.get_xlim())
    exps = list(range(int(np.floor(np.log10(lo))), int(np.ceil(np.log10(hi))) + 1))
    ticks = [10.0 ** e for e in exps]
    labs = ['$10^{%d}$' % e for e in exps]
    if sum(1 for t in ticks if lo <= t <= hi) < 3:          # 한두 자릿수 안이면 라벨이 너무 성깁니다
        ticks, labs = [], []
        for e in exps:
            for m in (1, 2, 5):
                v = m * 10.0 ** e
                if lo <= v <= hi:
                    ticks.append(v)
                    labs.append('$10^{%d}$' % e if m == 1 else r'$%d{\times}10^{%d}$' % (m, e))
    a.set_ticks(ticks)
    a.set_ticklabels(labs)
    a.set_minor_locator(LogLocator(base=10.0, subs=tuple(np.arange(2, 10) * 0.1) + tuple(range(2, 10))))
    a.set_minor_formatter(NullFormatter())          # 소눈금에 라벨이 붙으면 같은 버그를 또 만납니다
    if axis == 'y':
        ax.set_ylim(lo, hi)                          # 눈금을 세우며 늘어난 범위를 되돌립니다
    else:
        ax.set_xlim(lo, hi)


def finish(fig, name):
    fig.savefig(OUT + name, dpi=220, bbox_inches='tight', facecolor='white')
    plt.close(fig)
    print('  ', name)


# ── 자료 ────────────────────────────────────────────────────────────────────
ours = {}
for f in ('results_v3.json', 'results_v3grid.json', 'results_v4mix.json'):
    for r in json.load(open(Z + f, encoding='utf-8'))['rows']:
        if r.get('status') == 'ok':
            ours[r['name']] = r

_w = json.load(open(Z + 'v3w_water_kh/water_kh_ALLw_hkhome_seedfixed.json', encoding='utf-8'))
water = {}
for r in (_w['rows'] if isinstance(_w, dict) and 'rows' in _w else _w):
    kh = next((r[k] for k in r if k.upper().startswith('KH')), None)
    if kh:
        water[r.get('tag') or r.get('name')] = kh

core_rows, _ = extract(load_core(SC + 'data/CR_meta_data_SI_slice.json'))
_, core_pass = apply_gates(core_rows)
print(f'  CoRE 관문 통과 {len(core_pass)} · 우리 CO2 {len(ours)} · 우리 물 {len(water)}')


def sub_pct(name):
    """-SO3H 치환율(%). 술폰산이 아닌 계열은 None."""
    if not name.startswith('saIm'):
        return None
    d = name[4:]
    return float(d[:1] + '.' + d[1:]) * 100 if len(d) > 2 else float(d)


FAM = [('saIm', '-SO$_3$H 단독', 'o'),
       ('sa', '-SO$_3$H 혼합', 'D'),
       ('', '다른 치환기', 's')]


def family(name):
    if name.startswith('saIm'):
        return 0
    if name.startswith('sa') or name.startswith('ms'):
        return 1
    return 2


# ── 그림 7 : 관문 두 개 위의 우리 위치 ──────────────────────────────────────
fig, (a1, a2) = plt.subplots(1, 2, figsize=(6.8, 3.1),
                             gridspec_kw=dict(width_ratios=[1, 1], wspace=0.34))

pld_core = [r['PLD'] for r in core_pass]
a1.hist(pld_core, bins=np.arange(3.0, 12.2, 0.3), color=GREY_L,
        edgecolor=GREY, linewidth=0.5, label=f'CoRE 관문 통과 (n={len(pld_core)})')
op = sorted(r['PLD'] for r in ours.values() if r.get('PLD'))
a1.plot(op, [-3.5] * len(op), '|', color=NAVY, markersize=9, markeredgewidth=1.1,
        clip_on=False, label=f'우리 조성 (n={len(op)})')
a1.axvline(3.3, color=ORANGE, linewidth=1.2, linestyle='--', label='PLD 관문 3.3 Å')
a1.set_xlabel('PLD (Å)')
a1.set_ylabel('CoRE 구조 수')
a1.set_xlim(3.0, 12.0)
a1.legend(frameon=False, fontsize=7.4, loc='upper right')

names = sorted([n for n in water if n in ours], key=lambda n: water[n])
xs = np.arange(len(names))
cols = [ORANGE if family(n) == 0 else (SAGE if family(n) == 1 else NAVY) for n in names]
a2.scatter(xs, [water[n] for n in names], s=16, c=cols, zorder=3)
a2.axhline(THRESH_KH, color='#B03A2E', linewidth=1.2,
           label='CoRE 물 분류 문턱 (되찾은 규칙)')
a2.axhspan(THRESH_KH / SAFE_MARGIN, THRESH_KH, color=ORNG_L, zorder=0,
           label=f'판정 보류 폭 ({SAFE_MARGIN:.0f}배)')
a2.set_yscale('log')
a2.set_xlabel('조성 (물 친화도 오름차순)')
a2.set_ylabel('물 $K_H$ (mmol g$^{-1}$ Pa$^{-1}$)')
a2.set_xticks([])
a2.legend(frameon=False, fontsize=7.4, loc='lower right')
log_ticks(a2, 'y')
finish(fig, 'fig7_screen_gates.png')


# ── 그림 8 : 선택도 대 물 친화도 (우리 계열 안) ─────────────────────────────
fig, ax = plt.subplots(figsize=(6.2, 3.5))
ax.axvspan(THRESH_KH / SAFE_MARGIN, THRESH_KH, color=ORNG_L, zorder=0)
ax.axvline(THRESH_KH, color='#B03A2E', linewidth=1.2, zorder=1)

pts = [n for n in water if n in ours and ours[n].get('selectivity')]
for fi, (_, lab, mk) in enumerate(FAM):
    sel = [n for n in pts if family(n) == fi]
    if not sel:
        continue
    x = [water[n] for n in sel]
    y = [ours[n]['selectivity'] for n in sel]
    ye = [ours[n].get('selectivity_err') or 0 for n in sel]
    if fi == 0:
        c = [sub_pct(n) or 0 for n in sel]
        sc = ax.scatter(x, y, c=c, cmap='YlOrBr', vmin=0, vmax=100, s=34,
                        marker=mk, edgecolor='#7A4A12', linewidth=0.5, zorder=3, label=lab)
        cb = fig.colorbar(sc, ax=ax, pad=0.015, fraction=0.04)
        cb.set_label(SUB, fontsize=8)
        cb.ax.tick_params(labelsize=7.5)
    else:
        ax.scatter(x, y, s=26, marker=mk, color=(SAGE if fi == 1 else NAVY),
                   edgecolor='white', linewidth=0.4, zorder=3, label=lab)
    ax.errorbar(x, y, yerr=ye, fmt='none', ecolor=GREY, elinewidth=0.7,
                capsize=1.6, zorder=2)
ax.set_xscale('log')
ax.set_yscale('log')
ax.set_xlabel('물 $K_H$ (mmol g$^{-1}$ Pa$^{-1}$)   →  친수성')
ax.set_ylabel('CO$_2$/N$_2$ 선택도  ($K_H$ 비)')
ax.legend(frameon=False, fontsize=7.8, loc='upper left')
log_ticks(ax, 'x')
log_ticks(ax, 'y')
finish(fig, 'fig8_screen_tradeoff.png')

print('  (오차 막대는 RASPA 95 % 신뢰구간 — 문턱 1.5 단위는 순위에만 씁니다)')


# ── 그림 9 : Frontier 맵 — **원본 노트북의 방식** ───────────────────────────
#
# 원본(`MOF_Screening.ipynb` 셀 81 `draw_quadrant_frontier`)의 방식을 그대로 씁니다:
#   x = CO2 친화도(Widom K_H) · y = CO2/N2 선택도 · **양쪽 로그** · 점선 격자(which='both')
#   색 = 범주 · 마커 = 두 번째 범주 · 상위 물질에 이름표 · 범례는 그림 바깥 오른쪽
#
# 바꾼 것과 그 이유:
#   · 4분할(Core/Robust × DAC/FlueGas) **안 함** — 사용자 지시. 그 분할은 금속·위상 목록으로
#     내습성을 정하는 사후 규칙이었고(D3), 우리 조성은 전부 Zn 이라 가르는 뜻도 없습니다.
#   · 색: 금속 → **-SO3H 치환율**. 우리는 전부 Zn 이라 금속이 정보를 안 담습니다.
#   · 마커: OMS → 치환기 계열. 우리 구조에 열린 금속 자리가 없습니다.
#   · **오차 막대를 넣습니다** — 원본에는 없었습니다(D4). RASPA 95 % 신뢰구간입니다.
#   · 이름표: "점수 상위 3개" → **비지배 집합(파레토 전선) 전부**.
#     원본의 점수는 0.6×선택도 + 0.4×용량 + 상위 5 % 클리핑이라 가중치 근거가 없었습니다(D5).
#     비지배는 가중치가 필요 없습니다 — 어떤 가중치를 써도 최적은 이 집합 안에 있습니다.
#   · 제목 없음 — 이 저장소 방침(`make_figs.py` 머리말).
import seaborn as sns                                  # noqa: E402

sns.set_theme(style='whitegrid')
plt.rcParams['font.family'] = fm.FontProperties(fname=FP).get_name()
plt.rcParams['axes.unicode_minus'] = False
plt.rcParams['font.size'] = 9

pts = [n for n in ours if ours[n].get('selectivity') and ours[n].get('KH_CO2')]
X = {n: ours[n]['KH_CO2'] for n in pts}
Y = {n: ours[n]['selectivity'] for n in pts}


def pareto(names):
    """비지배 집합 — 두 축 모두에서 자기보다 나은 것이 없는 조성."""
    out = []
    for n in names:
        if not any(X[m] > X[n] and Y[m] > Y[n] for m in names if m != n):
            out.append(n)
    return sorted(out, key=lambda n: X[n])


front = pareto(pts)

fig, ax = plt.subplots(figsize=(6.6, 4.2))
for fi, (_, lab, mk) in enumerate(FAM):
    sel = [n for n in pts if family(n) == fi]
    if not sel:
        continue
    x = [X[n] for n in sel]
    y = [Y[n] for n in sel]
    ax.errorbar(x, y, yerr=[ours[n].get('selectivity_err') or 0 for n in sel],
                xerr=[ours[n].get('KH_CO2_err') or 0 for n in sel],
                fmt='none', ecolor=GREY, elinewidth=0.7, capsize=1.5, zorder=2)
    if fi == 0:
        sc = ax.scatter(x, y, c=[sub_pct(n) or 0 for n in sel], cmap='YlOrBr',
                        vmin=0, vmax=100, s=60, marker=mk, edgecolor='#5A3A0E',
                        linewidth=0.7, zorder=3, label=lab)
        cb = fig.colorbar(sc, ax=ax, pad=0.012, fraction=0.04)
        cb.set_label(SUB, fontsize=8)
        cb.ax.tick_params(labelsize=7.5)
    else:
        ax.scatter(x, y, s=44, marker=mk, color=(SAGE if fi == 1 else NAVY),
                   edgecolor='white', linewidth=0.5, zorder=3, label=lab)

# 비지배 집합. 두 축이 같은 방향으로 움직이면(우리 경우) 집합이 한 점으로 줄어듭니다 —
# 그 자체가 결과입니다: **이 두 축에는 상충이 없습니다.** 상충은 물 축에서 나타납니다(fig8).
if len(front) > 1:
    ax.plot([X[n] for n in front], [Y[n] for n in front], '-', color='#B03A2E',
            linewidth=1.1, alpha=0.85, zorder=1, label=f'비지배 전선 (n={len(front)})')
else:
    n0 = front[0]
    ax.scatter([X[n0]], [Y[n0]], s=210, facecolor='none', edgecolor='#B03A2E',
               linewidth=1.3, zorder=1, label=f'비지배 (n=1) — 두 축 모두 최고')

label_me = sorted(set(sorted(pts, key=lambda n: -Y[n])[:5]) | set(front),
                  key=lambda n: -Y[n])
# 이름표가 서로 겹칩니다(saIm0875 / saIm075 가 선택도 94.7 대 94.5 로 사실상 같은 자리).
# 위·아래로 번갈아 밀어 둡니다 — 값은 그대로, 읽기만 돕습니다.
for k, n in enumerate(label_me):
    dy = 6 if k % 2 == 0 else -11
    ax.annotate(n, (X[n], Y[n]), xytext=(7, dy), textcoords='offset points',
                fontsize=7.2, color='#5A2A1E')

ax.set_xscale('log')
ax.set_yscale('log')
ax.set_xlabel('CO$_2$ 친화도  Widom $K_H$ (mmol g$^{-1}$ Pa$^{-1}$)')
ax.set_ylabel('선택도  CO$_2$ / N$_2$')
ax.grid(True, which='both', ls='--', alpha=0.4)
ax.set_xlim(min(X.values()) * 0.7, max(X.values()) * 2.2)
ax.set_ylim(min(Y.values()) * 0.75, max(Y.values()) * 1.9)
ax.legend(bbox_to_anchor=(1.18, 1.0), loc='upper left', frameon=False, fontsize=7.8)
log_ticks(ax, 'x')
log_ticks(ax, 'y')
finish(fig, 'fig9_frontier.png')
