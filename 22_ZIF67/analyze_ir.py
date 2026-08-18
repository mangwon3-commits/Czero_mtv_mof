"""xtb 결과에서 IR 표지 밴드를 **계산으로** 골라낸다.

[왜 눈대중으로 고르지 않나]
    "2200 근처에 큰 봉우리가 있으니 C≡N 이겠지" 는 추측입니다. 이 프로젝트에서
    추측으로 원인을 짚었다가 두 번 틀렸습니다(STRUCTURE_DEFECT.md 판1·2).

    대신 **각 모드가 그 결합을 실제로 늘이는가**를 잽니다. 정규모드 변위 v 를
    따라 원자를 미소 이동시키고 결합 길이의 변화율 |dd/dQ| 을 구하면, 그 결합의
    신축 모드가 최댓값을 갖습니다. 결합을 지정하는 것은 사람이지만
    **어느 모드가 그 결합의 신축인가는 숫자가 정합니다.**

[GFN2-xTB 진동수의 정확도]
    반경험적이라 절대 진동수는 ±수십 cm-1 수준입니다. 그래서 이 표는
    **"어느 창을 보라"** 와 **"어느 밴드가 어느 작용기인가"** 에 쓰는 것이고,
    실측 봉우리 위치를 예언하는 데 쓰는 것이 아닙니다. 그 목적에는 충분합니다 --
    C≡N(~2200)과 고리 모드(<1600)는 수백 cm-1 떨어져 있어 오차가 판정을
    뒤집지 않습니다.

[출력]
    spectra/ir_bands.json  전 모드
    표준출력            표지 밴드 요약과 정량용 창
"""
import glob
import json
import os
import re
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
RUNS = os.path.join(HERE, 'spectra', 'runs')
COV = {'H': 0.31, 'C': 0.76, 'N': 0.71, 'O': 0.66}
Z2SYM = {1: 'H', 6: 'C', 7: 'N', 8: 'O'}
EPS = 0.01          # 변위 크기 (Å). 수치미분용


def read_xyz(p):
    lines = open(p).read().splitlines()
    n = int(lines[0].split()[0])
    sym, pos = [], []
    for ln in lines[2:2 + n]:
        f = ln.split()
        sym.append(f[0])
        pos.append([float(x) for x in f[1:4]])
    return sym, np.array(pos)


def read_g98(p):
    """g98.out 에서 (진동수, IR세기, 변위벡터) 를 읽는다."""
    txt = open(p).read().splitlines()
    freqs, inten, modes = [], [], []
    k = 0
    while k < len(txt):
        if txt[k].strip().startswith('Frequencies --'):
            f = [float(x) for x in txt[k].split('--')[1].split()]
            ir = None
            j = k
            while j < len(txt) and not txt[j].strip().startswith('Atom AN'):
                if txt[j].strip().startswith('IR Inten'):
                    ir = [float(x) for x in txt[j].split('--')[1].split()]
                j += 1
            # 마지막 블록은 모드가 3개가 아닐 수 있어 열 수가 다릅니다.
            # 열 수를 고정하지 않고 **그 블록의 진동수 개수(len(f))에서 유도**합니다.
            # 고정하면 여기서 ValueError 로 죽습니다(실제로 겪었습니다).
            ncol = 3 * len(f)
            block = []
            j += 1
            while j < len(txt) and re.match(r'\s*\d+\s+\d+\s+-?\d', txt[j]):
                vals = [float(x) for x in txt[j].split()[2:]]
                if len(vals) < ncol:
                    break
                block.append(vals[:ncol])
                j += 1
            arr = np.array(block)                       # (natoms, 3*nmode)
            for m in range(len(f)):
                freqs.append(f[m])
                inten.append(ir[m] if ir else 0.0)
                modes.append(arr[:, 3 * m:3 * m + 3])
            k = j
        else:
            k += 1
    return np.array(freqs), np.array(inten), np.array(modes)


def bonds(sym, pos, scale=1.3):
    out = []
    n = len(sym)
    for a in range(n):
        for b in range(a + 1, n):
            d = np.linalg.norm(pos[a] - pos[b])
            if d < scale * (COV[sym[a]] + COV[sym[b]]):
                out.append((a, b, d))
    return out


def stretch_strength(pos, mode, a, b):
    """정규모드를 따라 결합 a-b 가 얼마나 늘어나는가 (|dd/dQ|)."""
    p, m = pos, mode
    d1 = np.linalg.norm((p[a] + EPS * m[a]) - (p[b] + EPS * m[b]))
    d2 = np.linalg.norm((p[a] - EPS * m[a]) - (p[b] - EPS * m[b]))
    return abs(d1 - d2) / (2 * EPS)


def find_targets(sym, pos, bd):
    """표지로 쓸 결합을 화학적 역할로 찾는다."""
    nb = {k: [] for k in range(len(sym))}
    for a, b, d in bd:
        nb[a].append(b)
        nb[b].append(a)
    tg = {}
    for a, b, d in bd:
        pair = tuple(sorted((sym[a], sym[b])))
        # 나이트릴: C-N 이 짧고(<1.25) 그 N 은 결합이 하나뿐
        if pair == ('C', 'N') and d < 1.25:
            nn = a if sym[a] == 'N' else b
            if len(nb[nn]) == 1:
                tg.setdefault('C≡N (나이트릴)', []).append((a, b))
        # 나이트로: N 이 O 두 개를 가짐
        if pair == ('N', 'O'):
            nn = a if sym[a] == 'N' else b
            if sum(1 for x in nb[nn] if sym[x] == 'O') == 2:
                tg.setdefault('N–O (나이트로)', []).append((a, b))
        if pair == ('H', 'N'):
            tg.setdefault('N–H (전구체만)', []).append((a, b))
    return tg


def main():
    results = {}
    for d in sorted(glob.glob(os.path.join(RUNS, '*'))):
        name = os.path.basename(d)
        g98, xyz = os.path.join(d, 'g98.out'), os.path.join(d, 'xtbopt.xyz')
        if not (os.path.exists(g98) and os.path.exists(xyz)):
            continue
        sym, pos = read_xyz(xyz)
        fr, ir, md = read_g98(g98)
        keep = fr > 20.0                                # 병진·회전 제거
        fr, ir, md = fr[keep], ir[keep], md[keep]
        bd = bonds(sym, pos)
        tg = find_targets(sym, pos, bd)

        marks = {}
        for label, pairs in tg.items():
            best = None
            for k in range(len(fr)):
                s = sum(stretch_strength(pos, md[k], a, b) for a, b in pairs)
                if best is None or s > best[0]:
                    best = (s, k)
            k = best[1]
            marks[label] = {'freq': round(float(fr[k]), 1),
                            'ir': round(float(ir[k]), 2),
                            'stretch': round(float(best[0]), 3)}
        # 정량 창이 정말 비어 있는지.
        #
        # 첫 판은 창을 2100~2300 으로 잡았는데, GFN2 가 낸 C≡N 이 2323 이라
        # **표지 자신이 창 밖으로 나가** 모든 분자에서 "비어 있음"이 나왔습니다.
        # 문헌 실측(~2230)을 기준으로 창을 잡되 계산값의 과대평가를 감안해
        # 넉넉히 1900~2500 으로 봅니다.
        win = [(round(float(f), 1), round(float(i), 2))
               for f, i in zip(fr, ir) if 1900 <= f <= 2500 and i > 1.0]
        results[name] = {'n_modes': int(len(fr)),
                         'fmax': round(float(fr.max()), 1),
                         'markers': marks, 'window_1900_2500': win,
                         'top_ir': sorted(
                             [(round(float(f), 1), round(float(i), 1))
                              for f, i in zip(fr, ir)],
                             key=lambda t: -t[1])[:6]}

    with open(os.path.join(HERE, 'spectra', 'ir_bands.json'), 'w',
              encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=1)

    print('=' * 86)
    print('표지 밴드 (GFN2-xTB, 절대값은 ±수십 cm-1 -- 창과 귀속에 쓰는 표입니다)')
    print('=' * 86)
    for name in sorted(results):
        r = results[name]
        print(f'\n  {name}')
        if not r['markers']:
            print('    (표지 결합 없음 -- 모체)')
        for lab, m in r['markers'].items():
            print(f"    {lab:<16} {m['freq']:>8.1f} cm-1   IR {m['ir']:>8.2f} km/mol")
        print(f"    1900~2500 창: "
              f"{r['window_1900_2500'] if r['window_1900_2500'] else '비어 있음'}")
        print(f"    IR 최강 6개: {r['top_ir']}")

    # --- 전구체 -> 골격 이동량. 이것이 '정말 들어갔는가' 의 지표다 ---
    print('\n' + '=' * 86)
    print('중성(전구체) -> 음이온(골격 내) 이동 — **도입 여부의 지표**')
    print('=' * 86)
    for fam in ('mIm', 'cnIm', 'nIm'):
        a, n = results.get(f'{fam}_anion'), results.get(f'{fam}_neutral')
        if not (a and n):
            continue
        print(f'\n  {fam}')
        for lab in set(a['markers']) | set(n['markers']):
            fa = a['markers'].get(lab, {}).get('freq')
            fn = n['markers'].get(lab, {}).get('freq')
            if fa is not None and fn is not None:
                print(f'    {lab:<16} {fn:>8.1f} -> {fa:>8.1f}   '
                      f'이동 {fa - fn:>+7.1f} cm-1')
            elif fn is not None:
                print(f'    {lab:<16} {fn:>8.1f} -> **소멸**   '
                      f'(탈양성자화되면 사라짐)')
    print()
    return 0


if __name__ == '__main__':
    sys.exit(main())
