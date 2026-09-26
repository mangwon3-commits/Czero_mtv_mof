"""E-28 밀도 격자 **미리보기 그림** — 형판 Zn(bib)(bdtdc) 모체 · 4,8-치환체 (2026-09-26).

포스터 본 그림은 ParaView/VESTA 로 VTK 를 직접 그립니다(`tools/build_poster.py` 머리말 — 그림 자리 비움).
이 스크립트는 **무엇이 보이는지 먼저 확인하는 2D 투영**입니다.

[무엇을 그리나]
  - 격자는 1×2×3 슈퍼셀 위(90³, 분율 좌표 등간격). **단위셀로 접어**(b 2개 · c 3개 평균 → 90 × 45 × 30) 잡음을 줄인 뒤
    **통로 축 c 방향으로 합**해 ab 면에 투영합니다. ab 면은 γ = 90° 라 직사각형 그대로 그려도 왜곡이 없습니다
    (β 99.61° 는 ac 사이각 — c 로 투영하면 c 성분이 a 로 0.17 만큼 기울어 **흐려질 뿐** 자리가 옮지는 않음: 아래 주의).
  - 통로 축 확인(모체 ON): c 투영 빈칸 90.5 % · max/mean 53.6 — b 71.7 % · 14.5, a 73.1 % · 20.1 → c 가 통로.
  - ON · OFF 는 각각 총합 1 로 정규화(%), 차분 = ON − OFF(%p) — `export_diff_vtk.py` 와 같은 정의.
  - 골격 원자(CIF 분율 좌표)를 ab 면에 겹칩니다: Zn(회색) · S(노랑) · N(파랑) · O(빨강) · F(초록), **치환기 무거운 원자는 연두 별**
    (모체에서 같은 원소가 0.6 Å 안에 없는 원자 — `new_atoms()`).
[주의] 투영은 c 방향 합이라 **깊이 정보가 사라집니다.** 봉우리 위치를 한 복셀로 지목하지 마세요
  (`DENSITY_GRID_TWO_GENERATIONS_20260906.md` — 씨앗만 달라도 최댓값 위치 최대 23 Å 이동). β 기울기 때문에 c 투영은
  a 방향으로 최대 c·cosβ 폭(≈ 1.55 Å)만큼 번집니다.
사용: python plot_density_tpl.py  → figs_e28/*.png
"""
import gzip
import os
import sys

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from ase.io import read

HERE = os.path.dirname(os.path.abspath(__file__))
DRY = os.path.join(HERE, 'density_v3_tpl')
WET = os.path.join(HERE, 'water_runs_density_v3w')
OUT = os.path.join(HERE, 'figs_e28')
NAMES = [('e22_parent', '모체 Zn(bib)(bdtdc)'), ('e24_ch3_100', '4,8-(CH₃)₂'), ('e24_cn_100', '4,8-(CN)₂'),
         ('e24_f_100', '4,8-F₂'), ('e22_no2_100', '4,8-(NO₂)₂')]
REP = (1, 2, 3)            # a b c 복제 — unit_cells() 산출과 같음(로그 확인)
plt.rcParams['font.family'] = ['Malgun Gothic', 'NanumGothic', 'DejaVu Sans']
for fp in ('/mnt/c/Windows/Fonts/malgun.ttf',):
    if os.path.exists(fp):
        from matplotlib import font_manager
        font_manager.fontManager.addfont(fp)
        plt.rcParams['font.family'] = font_manager.FontProperties(fname=fp).get_name()
plt.rcParams['axes.unicode_minus'] = False


def read_grid(path):
    op = gzip.open if path.endswith('.gz') else open
    with op(path, 'rt') as f:
        head = [f.readline() for _ in range(10)]
        dims = [int(x) for x in head[4].split()[1:4]]
        v = np.array(f.read().split(), dtype=float)
    assert v.size == dims[0] * dims[1] * dims[2], (path, v.size, dims)
    return v.reshape(dims[2], dims[1], dims[0])          # [c][b][a] — VTK 는 x(a) 가 가장 빠름


def fold(g):
    nc, nb, na = g.shape
    return g.reshape(REP[2], nc // REP[2], REP[1], nb // REP[1], na // REP[0]).mean(axis=(0, 2))


def proj_c(g):
    u = fold(g)
    p = u.sum(axis=0)                                  # (b, a)
    return p / p.sum() * 100.0


def atoms_ab(tag):
    at = read(os.path.join(HERE, 'charged_v3', tag + '_DDEC6.cif'))
    fr = at.get_scaled_positions() % 1.0
    sym = np.array(at.get_chemical_symbols())
    return fr, sym, at.cell.cellpar()


def new_atoms(tag):
    """치환기 무거운 원자 = 모체에서 같은 원소가 0.6 Å 안에 없는 원자(주기 경계 포함). 모체는 빈 배열."""
    if tag == 'e22_parent':
        return np.zeros(0, dtype=int)
    at = read(os.path.join(HERE, 'charged_v3', tag + '_DDEC6.cif'))
    ref = read(os.path.join(HERE, 'charged_v3', 'e22_parent_DDEC6.cif'))
    cell = at.cell.array
    out = []
    for i, (el, f) in enumerate(zip(at.get_chemical_symbols(), at.get_scaled_positions())):
        if el == 'H':
            continue
        m = np.array(ref.get_chemical_symbols()) == el
        if not m.any():
            out.append(i); continue
        d = ref.get_scaled_positions()[m] - f
        d -= np.round(d)
        if np.min(np.linalg.norm(d @ cell, axis=1)) > 0.6:
            out.append(i)
    return np.array(out, dtype=int)


def overlay(ax, tag, a_len, b_len):
    fr, sym, _ = atoms_ab(tag)
    sub = new_atoms(tag)
    if sub.size:
        ax.scatter(fr[sub, 0] * a_len, fr[sub, 1] * b_len, s=22, marker='*', c='#39ff14', edgecolors='k',
                   linewidths=0.3, alpha=0.9, zorder=4)
    style = {'Zn': ('#7a7a7a', 28), 'S': ('#c9a400', 14), 'N': ('#3050f8', 6), 'F': ('#2e9e2e', 10), 'O': ('#ff2020', 4)}
    for el, (c, s) in style.items():
        m = sym == el
        ax.scatter(fr[m, 0] * a_len, fr[m, 1] * b_len, s=s, c=c, edgecolors='none', alpha=0.55, zorder=3)


def panel(ax, img, a_len, b_len, cmap, vmin, vmax, title):
    im = ax.imshow(img, origin='lower', extent=[0, a_len, 0, b_len], cmap=cmap, vmin=vmin, vmax=vmax,
                   interpolation='bilinear', aspect='equal')
    ax.set_title(title, fontsize=9)
    ax.set_xticks([]); ax.set_yticks([])
    return im


def dry():
    rows = [(t, lab) for t, lab in NAMES
            if all(os.path.exists(os.path.join(DRY, f'{t}__q_{s}', 'VTK', 'System_0', 'COMDensityProfile_CO2.vtk.gz'))
                   for s in ('on', 'off'))]
    if not rows:
        print('건조 격자 없음'); return
    fig, axs = plt.subplots(len(rows), 3, figsize=(9.6, 2.35 * len(rows)))
    axs = np.atleast_2d(axs)
    P = {}
    for t, _ in rows:
        on = proj_c(read_grid(os.path.join(DRY, f'{t}__q_on', 'VTK', 'System_0', 'COMDensityProfile_CO2.vtk.gz')))
        off = proj_c(read_grid(os.path.join(DRY, f'{t}__q_off', 'VTK', 'System_0', 'COMDensityProfile_CO2.vtk.gz')))
        P[t] = (on, off, on - off)
    vmax = max(max(p[0].max(), p[1].max()) for p in P.values())
    dmax = max(abs(p[2]).max() for p in P.values())
    for i, (t, lab) in enumerate(rows):
        _, _, cp = atoms_ab(t)
        a_len, b_len = cp[0], cp[1]
        on, off, d = P[t]
        im1 = panel(axs[i, 0], on, a_len, b_len, 'magma', 0, vmax, f'{lab} — 전하 ON')
        panel(axs[i, 1], off, a_len, b_len, 'magma', 0, vmax, f'{lab} — 전하 OFF')
        im3 = panel(axs[i, 2], d, a_len, b_len, 'RdBu_r', -dmax, dmax, f'{lab} — ON-OFF 차분')
        for j in range(3):
            overlay(axs[i, j], t, a_len, b_len)
    fig.colorbar(im1, ax=axs[:, :2], shrink=0.6, label='CO₂ 밀도 (c 투영, 합 100 %)')
    fig.colorbar(im3, ax=axs[:, 2], shrink=0.6, label='정전기 차분 (%p)')
    fig.suptitle('E-28 건조 CO₂ 밀도 — 0.15 bar · 298 K · 통로 축 c 투영 (단위셀로 접음, ab 면 a→ b↑)', fontsize=10)
    os.makedirs(OUT, exist_ok=True)
    p = os.path.join(OUT, 'e28_dry_on_off_diff.png')
    fig.savefig(p, dpi=200, bbox_inches='tight'); plt.close(fig)
    print('저장', p)


def wet():
    rows = [(t, lab) for t, lab in NAMES[:3]
            if all(os.path.exists(os.path.join(WET, f'rh90_{t}', 'VTK', 'System_0', f'COMDensityProfile_{m}.vtk.gz'))
                   for m in ('CO2', 'water'))]
    if not rows:
        print('습윤 격자 없음'); return
    fig, axs = plt.subplots(len(rows), 2, figsize=(6.6, 2.35 * len(rows)))
    axs = np.atleast_2d(axs)
    for i, (t, lab) in enumerate(rows):
        _, _, cp = atoms_ab(t)
        a_len, b_len = cp[0], cp[1]
        for j, m in enumerate(('CO2', 'water')):
            g = proj_c(read_grid(os.path.join(WET, f'rh90_{t}', 'VTK', 'System_0', f'COMDensityProfile_{m}.vtk.gz')))
            panel(axs[i, j], g, a_len, b_len, 'magma' if m == 'CO2' else 'Blues', 0, g.max(),
                  f'{lab} — {"CO₂" if m == "CO2" else "H₂O (성김 — 자리 주장 금지)"}')
            overlay(axs[i, j], t, a_len, b_len)
    fig.suptitle('E-28 습윤 — CO₂ 15 kPa + H₂O 2852 Pa (RH90) · 298 K · c 투영', fontsize=10)
    os.makedirs(OUT, exist_ok=True)
    p = os.path.join(OUT, 'e28_humid_co2_water.png')
    fig.savefig(p, dpi=200, bbox_inches='tight'); plt.close(fig)
    print('저장', p)


def dry2():
    """E-28b — 새 1 · 2위(Cl · C₂H₅ 막음). C₂H₅ 의 막음 구(block1.65)를 ab 면에 원으로 겹침(구의 c 투영 = 반지름 r 원)."""
    D2 = os.path.join(HERE, 'density_v3_tpl2')
    rows = [('e24c_cl_100', 'Cl₂ (규칙 1위)'), ('e24c_c2h5_100', '(C2H5)2 막음')]   # 맑은 고딕에 ₅ 글리프 없음 — ASCII
    P = {}
    for t, _ in rows:
        on = proj_c(read_grid(os.path.join(D2, f'{t}__q_on', 'VTK', 'System_0', 'COMDensityProfile_CO2.vtk.gz')))
        off = proj_c(read_grid(os.path.join(D2, f'{t}__q_off', 'VTK', 'System_0', 'COMDensityProfile_CO2.vtk.gz')))
        P[t] = (on, off, on - off)
    vmax = max(max(p[0].max(), p[1].max()) for p in P.values()); dmax = max(abs(p[2]).max() for p in P.values())
    fig, axs = plt.subplots(2, 3, figsize=(10.4, 5.4))
    blk = [l.split() for l in open(os.path.join(HERE, 'e28b_blocks', 'e24c_c2h5_100_block1.65.block')).read().split('\n')[1:] if l.strip()]
    for i, (t, lab) in enumerate(rows):
        _, _, cp = atoms_ab(t); a_len, b_len = cp[0], cp[1]
        on, off, d = P[t]
        im1 = panel(axs[i, 0], on, a_len, b_len, 'magma', 0, vmax, f'{lab} — 전하 ON')
        panel(axs[i, 1], off, a_len, b_len, 'magma', 0, vmax, f'{lab} — 전하 OFF')
        im3 = panel(axs[i, 2], d, a_len, b_len, 'RdBu_r', -dmax, dmax, f'{lab} — ON-OFF 차분')
        for j in range(3):
            overlay(axs[i, j], t, a_len, b_len)
            if t == 'e24c_c2h5_100':
                for bb in blk:
                    fa, fb, r = float(bb[0]), float(bb[1]), float(bb[3])
                    for sa in (-1, 0, 1):
                        for sb in (-1, 0, 1):
                            axs[i, j].add_patch(plt.Circle(((fa + sa) * a_len, (fb + sb) * b_len), r, fill=False, ls='--', lw=0.8, ec='#00e5ff'))
                axs[i, j].set_xlim(0, a_len); axs[i, j].set_ylim(0, b_len)
    fig.colorbar(im1, ax=axs[:, :2], shrink=0.6, label='CO₂ 밀도 (c 투영, 합 100 %)')
    fig.colorbar(im3, ax=axs[:, 2], shrink=0.6, label='정전기 차분 (%p)')
    fig.suptitle('E-28b 건조 CO₂ 밀도 — 새 1 · 2위(4,8-Cl2 · 4,8-(C2H5)2) · 0.15 bar · 298 K · c 투영\n(C2H5: 점선 원 = 막은 주머니 — 안쪽 밀도 0, 앞단 강건 1위)', fontsize=10)
    os.makedirs(OUT, exist_ok=True)
    p = os.path.join(OUT, 'e28b_dry_cl_c2h5.png'); fig.savefig(p, dpi=200, bbox_inches='tight'); plt.close(fig); print('저장', p)


def wet2(base=None):
    """E-28c — 새 1 · 2위 습윤(RH90). base = 격자 폴더 루트(기본 water_runs_density_v3w). C₂H₅ 는 CO₂ 막은 구(block1.65)를 점선 원으로."""
    base = base or WET
    rows = [('e24c_cl_100', 'Cl2'), ('e24c_c2h5_100', '(C2H5)2 막음')]
    blk = [l.split() for l in open(os.path.join(HERE, 'e28b_blocks', 'e24c_c2h5_100_block1.65.block')).read().split('\n')[1:] if l.strip()]
    fig, axs = plt.subplots(2, 2, figsize=(7.4, 5.4))
    for i, (t, lab) in enumerate(rows):
        _, _, cp = atoms_ab(t); a_len, b_len = cp[0], cp[1]
        for j, m in enumerate(('CO2', 'water')):
            g = proj_c(read_grid(os.path.join(base, f'rh90_{t}', 'VTK', 'System_0', f'COMDensityProfile_{m}.vtk.gz')))
            panel(axs[i, j], g, a_len, b_len, 'magma' if m == 'CO2' else 'Blues', 0, g.max(), f'{lab} — {"CO₂" if m == "CO2" else "H₂O (영역 서술만)"}')
            overlay(axs[i, j], t, a_len, b_len)
            if t == 'e24c_c2h5_100':
                for bb in blk:
                    fa, fb, r = float(bb[0]), float(bb[1]), float(bb[3])
                    for sa in (-1, 0, 1):
                        for sb in (-1, 0, 1):
                            axs[i, j].add_patch(plt.Circle(((fa + sa) * a_len, (fb + sb) * b_len), r, fill=False, ls='--', lw=0.8, ec='#00e5ff'))
                axs[i, j].set_xlim(0, a_len); axs[i, j].set_ylim(0, b_len)
    fig.suptitle('E-28c 습윤 — CO2 15 kPa + H2O 2852 Pa (RH90) · 298 K · c 투영\n(C2H5: 점선 원 = CO2 가 못 가는 통로 — 물의 64 % 가 여기에)', fontsize=10)
    os.makedirs(OUT, exist_ok=True)
    p = os.path.join(OUT, 'e28c_humid_cl_c2h5.png'); fig.savefig(p, dpi=200, bbox_inches='tight'); plt.close(fig); print('저장', p)


E28D_ROWS = [('e24g_br_100', 'Br2', 'laptop'), ('e24h_cl_050a', 'Cl2 50 % (a)', 'laptop'), ('e24h_c2h5_050a', '(C2H5)2 50 % (a) 막음', 'junseok')]
E28D_BLOCK = {'e24h_c2h5_050a': os.path.join(HERE, 'e24g_zeo_runs', 'e24h_c2h5_050a', 'block1.65', 'e24h_c2h5_050a_relaxed.block')}


def _circles(ax, t, a_len, b_len):
    if t not in E28D_BLOCK:
        return
    blk = [l.split() for l in open(E28D_BLOCK[t]).read().split('\n')[1:] if l.strip()]
    for bb in blk:
        fa, fb, r = float(bb[0]), float(bb[1]), float(bb[3])
        for sa in (-1, 0, 1):
            for sb in (-1, 0, 1):
                ax.add_patch(plt.Circle(((fa + sa) * a_len, (fb + sb) * b_len), r, fill=False, ls='--', lw=0.8, ec='#00e5ff'))
    ax.set_xlim(0, a_len); ax.set_ylim(0, b_len)


def dry3():
    """E-28d — E-24g · E-24h 새 치환체(Br · Cl 50 % a · C₂H₅ 50 % a 막음) 건조 CO₂ 격자 ON/OFF/차분. 격자는 density_v3_tpl3/<기기>/."""
    P = {}
    for t, _, m in E28D_ROWS:
        D = os.path.join(HERE, 'density_v3_tpl3', m)
        on = proj_c(read_grid(os.path.join(D, f'{t}__q_on', 'VTK', 'System_0', 'COMDensityProfile_CO2.vtk.gz')))
        off = proj_c(read_grid(os.path.join(D, f'{t}__q_off', 'VTK', 'System_0', 'COMDensityProfile_CO2.vtk.gz')))
        P[t] = (on, off, on - off)
    vmax = max(max(p[0].max(), p[1].max()) for p in P.values()); dmax = max(abs(p[2]).max() for p in P.values())
    fig, axs = plt.subplots(3, 3, figsize=(10.4, 8.0))
    for i, (t, lab, _) in enumerate(E28D_ROWS):
        _, _, cp = atoms_ab(t); a_len, b_len = cp[0], cp[1]
        on, off, d = P[t]
        im1 = panel(axs[i, 0], on, a_len, b_len, 'magma', 0, vmax, f'{lab} — 전하 ON')
        panel(axs[i, 1], off, a_len, b_len, 'magma', 0, vmax, f'{lab} — 전하 OFF')
        im3 = panel(axs[i, 2], d, a_len, b_len, 'RdBu_r', -dmax, dmax, f'{lab} — ON-OFF 차분')
        for j in range(3):
            overlay(axs[i, j], t, a_len, b_len); _circles(axs[i, j], t, a_len, b_len)
    fig.colorbar(im1, ax=axs[:, :2], shrink=0.6, label='CO₂ 밀도 (c 투영, 합 100 %)')
    fig.colorbar(im3, ax=axs[:, 2], shrink=0.6, label='정전기 차분 (%p)')
    fig.suptitle('E-28d 건조 CO₂ 밀도 — 새 치환체 · 0.15 bar · 298 K · c 투영\n(C2H5 50 %: 점선 원 = 막은 주머니)', fontsize=10)
    os.makedirs(OUT, exist_ok=True)
    p = os.path.join(OUT, 'e28d_dry_br_cl50_c2h550.png'); fig.savefig(p, dpi=200, bbox_inches='tight'); plt.close(fig); print('저장', p)


def wet3():
    """E-28d — 같은 셋의 습윤(RH90) CO₂ · 물 격자. water_runs_density_v3w/rh90_<tag>/."""
    fig, axs = plt.subplots(3, 2, figsize=(7.4, 8.0))
    for i, (t, lab, _) in enumerate(E28D_ROWS):
        _, _, cp = atoms_ab(t); a_len, b_len = cp[0], cp[1]
        for j, m in enumerate(('CO2', 'water')):
            g = proj_c(read_grid(os.path.join(WET, f'rh90_{t}', 'VTK', 'System_0', f'COMDensityProfile_{m}.vtk.gz')))
            panel(axs[i, j], g, a_len, b_len, 'magma' if m == 'CO2' else 'Blues', 0, g.max(), f'{lab} — {"CO₂" if m == "CO2" else "H₂O (영역 서술만)"}')
            overlay(axs[i, j], t, a_len, b_len); _circles(axs[i, j], t, a_len, b_len)
    fig.suptitle('E-28d 습윤 — CO2 15 kPa + H2O 2852 Pa (RH90) · 298 K · c 투영\n(물 적재가 작아 물 격자는 잡음 큼 — 영역 서술만)', fontsize=10)
    os.makedirs(OUT, exist_ok=True)
    p = os.path.join(OUT, 'e28d_humid_br_cl50_c2h550.png'); fig.savefig(p, dpi=200, bbox_inches='tight'); plt.close(fig); print('저장', p)


if __name__ == '__main__':
    what = sys.argv[1:] or ['dry', 'wet']
    if 'dry' in what: dry()
    if 'wet' in what: wet()
    if 'dry2' in what: dry2()
    if 'wet2' in what: wet2(os.environ.get('E28C_BASE'))
    if 'dry3' in what: dry3()
    if 'wet3' in what: wet3()
