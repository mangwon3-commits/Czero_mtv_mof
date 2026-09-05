"""실행 폴더의 텍스트 Restart 에서 O–O 구조를 잽니다 (조기 판독용).

등록 규약: COMMS/laptop.md 2026-09-05 13:5x
    판독 시점의 **사이클 수**를 반드시 병기합니다.
    연속 두 판독의 봉우리 차 ≤ 0.05 Å 이고 CN 차 ≤ 0.3 일 때만 "정상 상태".
    창 밖은 **반증이 아니라 "아직 이동 중"** 입니다.

사용:  python tb1_struct.py <실행폴더>
"""
import glob, os, sys
import numpy as np

WIN_PEAK = (2.75, 2.90)
WIN_G282 = 2.0
WIN_CN   = (4.0, 5.2)

def load(path):
    L = None; pos = []
    for ln in open(path, errors='replace'):
        if ln.startswith('cell-lengths:'):
            L = float(ln.split()[1])
        elif ln.startswith('Adsorbate-atom-position:'):
            p = ln.split()
            pos.append((int(p[1]), int(p[2]), float(p[3]), float(p[4]), float(p[5])))
    pos.sort(key=lambda t: (t[0], t[1]))
    n = max(p[0] for p in pos) + 1
    X = np.array([[p[2], p[3], p[4]] for p in pos]).reshape(n, 5, 3)
    return L, X[:, 0, :], n

def analyze(path):
    L, O, n = load(path)
    bins = np.arange(2.0, 8.001, 0.05)
    h = np.zeros(len(bins) - 1); cnt = 0; mn = 9.0
    for i in range(n):
        d = O[i + 1:] - O[i]; d -= L * np.round(d / L)
        r = np.sqrt((d * d).sum(1))
        if len(r):
            h += np.histogram(r, bins=bins)[0]
            mn = min(mn, r.min())
        d2 = O - O[i]; d2 -= L * np.round(d2 / L)
        r2 = np.sqrt((d2 * d2).sum(1))
        cnt += ((r2 < 3.5) & (r2 > 0.1)).sum()
    c = 0.5 * (bins[1:] + bins[:-1])
    g = h * 2 / (n * (n / L ** 3) * 4 * np.pi * c ** 2 * 0.05)
    m = (c >= 2.5) & (c <= 3.6)
    peak = float(c[m][np.argmax(g[m])])
    g282 = float(g[np.argmin(abs(c - 2.82))])
    return dict(L=L, n=n, peak=peak, g282=g282, cn=cnt / n, minoo=float(mn))

def cycles_of(rundir):
    """.data 의 마지막 사이클 표시. 판독 시점을 병기하기 위한 것."""
    fs = glob.glob(os.path.join(rundir, 'Output', 'System_0', '*.data'))
    if not fs: return None
    last = None
    for ln in open(fs[0], errors='replace'):
        if 'Current cycle:' in ln:
            last = ln.strip()
    return last

if __name__ == '__main__':
    d = sys.argv[1]
    rst = glob.glob(os.path.join(d, 'Restart', 'System_0', 'restart_*'))
    if not rst:
        print('  Restart 없음 — 아직 첫 인쇄 전입니다'); sys.exit(1)
    r = analyze(rst[0])
    print(f'  판독 시점  {cycles_of(d)}')
    print(f'  파일 시각  {__import__("time").strftime("%H:%M:%S", __import__("time").localtime(os.path.getmtime(rst[0])))}')
    print(f'  분자 {r["n"]}  L {r["L"]:.4f} Å')
    print(f'  O–O 첫 봉우리 **{r["peak"]:.2f} Å**   창 {WIN_PEAK}   '
          f'{"안" if WIN_PEAK[0] <= r["peak"] <= WIN_PEAK[1] else "**밖**"}')
    print(f'  g(2.82)       **{r["g282"]:.2f}**       창 ≥{WIN_G282}      '
          f'{"안" if r["g282"] >= WIN_G282 else "**밖**"}')
    print(f'  CN(3.5 Å)     **{r["cn"]:.2f}**       창 {WIN_CN}   '
          f'{"안" if WIN_CN[0] <= r["cn"] <= WIN_CN[1] else "**밖**"}')
    print(f'  최소 O–O      {r["minoo"]:.3f} Å')
    print('  기준틀: 씨앗 3.07 / 1.32 / 6.06,  본 실행(현행 힘장) 3.32 / 0.18 / 6.19')
    print('  ⚠️ 창 밖은 반증이 아니라 "아직 이동 중" 입니다 (등록 규약).')
