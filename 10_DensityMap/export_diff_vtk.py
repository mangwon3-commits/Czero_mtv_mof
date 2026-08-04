"""정전기 차분맵을 ParaView용 VTK로 내보낸다.

    dρ(r) = ρ_on(r) - ρ_off(r)     (각각 총합 1로 정규화 후)

LJ(분산력) 항은 전하 유무와 무관하므로 이 차분에서 완전히 소거된다. 남는 것은
'전하를 켰을 때 CO2가 어디로 이동했는가'만이다. ParaView에서
    양수 등고면(빨강) = 정전기가 CO2를 새로 끌어들인 자리
    음수 등고면(파랑) = 정전기 때문에 CO2가 빠져나간 자리
로 보면 된다. 실험으로는 분리할 수 없는 양이다.

같이 내보내는 rho_on은 절대 밀도이므로 '어디에 많은가'만 보여주고 원인은 못
가린다. 두 개를 겹쳐 봐야 "여기 몰린 게 넓어서인지 끌려서인지"가 구별된다.
"""
import os
import re
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'diff_vtk')


def read_vtk_grid(path):
    with open(path) as f:
        head = [f.readline() for _ in range(10)]
        cellp = head[1]
        dims = [int(x) for x in head[4].split()[1:4]]
        spacing = head[6]
        vals = np.fromstring(f.read(), sep='\n')
    n = dims[0] * dims[1] * dims[2]
    return vals[:n], dims, cellp, spacing


def write_vtk(path, vals, dims, cellp, spacing, name='electrostatic_gain'):
    with open(path, 'w') as f:
        f.write('# vtk DataFile Version 1.0\n')
        f.write(cellp if cellp.endswith('\n') else cellp + '\n')
        f.write('ASCII\nDATASET STRUCTURED_POINTS\n')
        f.write(f'DIMENSIONS {dims[0]} {dims[1]} {dims[2]}\n')
        f.write('ORIGIN 0.0 0.0 0.0\n')
        f.write(spacing if spacing.endswith('\n') else spacing + '\n')
        f.write(f'POINT_DATA {vals.size}\n')
        f.write(f'SCALARS {name} double\nLOOKUP_TABLE default\n')
        f.write('\n'.join(f'{v:.8g}' for v in vals))
        f.write('\n')


def main():
    os.makedirs(OUT, exist_ok=True)
    dirs = [d for d in os.listdir(HERE) if os.path.isdir(os.path.join(HERE, d))]
    pairs = {}
    for d in dirs:
        m = re.match(r'(.+)__(closed|open)__q_(on|off)$', d)
        if m:
            pairs.setdefault(f'{m.group(1)}__{m.group(2)}', {})[m.group(3)] = d

    print(f'{"구조":<34} {"전체밀도 최대":>13} {"정전기이득 최대":>15} {"최강자리 정전기기원":>18}')
    print('-' * 88)
    n = 0
    for tag, dd in sorted(pairs.items()):
        if 'on' not in dd or 'off' not in dd:
            continue
        fn = os.path.join('VTK', 'System_0', 'COMDensityProfile_CO2.vtk')
        p_on, p_off = os.path.join(HERE, dd['on'], fn), os.path.join(HERE, dd['off'], fn)
        if not (os.path.exists(p_on) and os.path.exists(p_off)):
            continue
        v_on, dims, cellp, sp = read_vtk_grid(p_on)
        v_off, _, _, _ = read_vtk_grid(p_off)
        if v_on.sum() <= 0 or v_off.sum() <= 0:
            continue
        r_on, r_off = v_on / v_on.sum(), v_off / v_off.sum()
        d = r_on - r_off

        write_vtk(os.path.join(OUT, tag + '__ELECTROSTATIC_GAIN.vtk'),
                  d * 100, dims, cellp, sp, 'electrostatic_gain_pct')
        write_vtk(os.path.join(OUT, tag + '__RHO_total.vtk'),
                  r_on * 100, dims, cellp, sp, 'co2_density_pct')

        # 최대 밀도 자리에서 정전기가 차지하는 비율
        i = int(np.argmax(r_on))
        frac = d[i] / r_on[i] * 100 if r_on[i] > 0 else float('nan')
        print(f'{tag:<34} {r_on.max()*100:>12.4f}% {d.max()*100:>14.4f}%p '
              f'{frac:>17.1f}%')
        n += 1
    print(f'\n[OK] {n*2}개 VTK -> {OUT}')
    print('ParaView: 두 파일을 함께 열고 ELECTROSTATIC_GAIN에 Contour를 걸어')
    print('          양수 등고면(정전기가 끌어온 자리)과 음수 등고면(밀려난 자리)을 본다.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
