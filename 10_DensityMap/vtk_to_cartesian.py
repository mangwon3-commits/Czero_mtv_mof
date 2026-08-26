"""RASPA 밀도 VTK 를 골격과 같은 데카르트 좌표로 옮긴다.

[왜 필요한가 — 2026-08-22]
    RASPA 는 밀도 프로파일을 `DATASET STRUCTURED_POINTS` 로 씁니다. 그 형식은
    **직교 격자만 표현할 수 있습니다.** ZIF-69 는 gamma = 120 도인 육방 셀이라,
    ParaView 가 이 파일을 읽으면 격자를 0..a x 0..b 인 **직사각 상자**로 놓습니다.
    반면 같은 폴더의 FrameworkBonds.vtk 는 진짜 데카르트 좌표(평행사변형)입니다.

    실측 (density_v2/saIm100):
        밀도 격자 상자   x 0 .. 51.59   y 0 .. 51.59
        골격 좌표       x -35.37 .. 61.46   y -6.79 .. 51.97

    그대로 겹치면 등고면이 기공에 앉은 것처럼 **보이지만** 실제로는 x 로
    갈수록 어긋납니다. 주기 구조라 눈이 속습니다 — 이 저장소가 반복해서
    데인 유형(실패가 결과처럼 보이는 것)입니다.

    헤더의 CELL_PARAMETERS 줄에 각도가 있지만 VTK 는 그것을 읽지 않습니다.
    그래서 좌표를 우리가 직접 만들어 STRUCTURED_GRID 로 다시 씁니다.

        x = f1*a + f2*b*cos(gamma)
        y =        f2*b*sin(gamma)
        z =                          f3*c        (alpha = beta = 90 인 경우)

    f_i = i / N_i 입니다 (i/(N-1) 이 아닙니다). SPACING = a/N 이므로
    격자는 [0, 1) 을 N 등분한 것이지 [0, 1] 을 N-1 등분한 것이 아닙니다.

사용:
    python vtk_to_cartesian.py 입력.vtk [출력.vtk]
    python vtk_to_cartesian.py 폴더            # 폴더 안 *.vtk 전부
"""
import os
import sys

import numpy as np


def read_structured_points(path):
    with open(path, 'rb') as f:
        head = [f.readline().decode('utf-8', 'replace') for _ in range(10)]
        body = f.read()
    if 'STRUCTURED_POINTS' not in head[3]:
        raise SystemExit(f'{path}: STRUCTURED_POINTS 가 아닙니다 -> {head[3].strip()}')
    cellp = [float(x) for x in head[1].split()[1:7]]
    dims = [int(x) for x in head[4].split()[1:4]]
    name = head[8].split()[1] if head[8].startswith('SCALARS') else 'scalars'
    vals = np.fromstring(body.decode('utf-8', 'replace'), sep='\n')
    n = dims[0] * dims[1] * dims[2]
    if vals.size < n:
        raise SystemExit(f'{path}: 값 {vals.size} < 점 {n}')
    return vals[:n].astype(np.float32), dims, cellp, name


def cartesian_points(dims, cellp):
    """분율 좌표를 셀 행렬로 데카르트로. x 가 가장 빨리 변한다."""
    a, b, c, al, be, ga = cellp
    al, be, ga = np.deg2rad([al, be, ga])
    # 일반 삼사정계 셀 행렬 (a 를 x 축에, b 를 xy 평면에)
    cx = c * np.cos(be)
    cy = c * (np.cos(al) - np.cos(be) * np.cos(ga)) / np.sin(ga)
    cz = np.sqrt(max(c * c - cx * cx - cy * cy, 0.0))
    M = np.array([[a, 0.0, 0.0],
                  [b * np.cos(ga), b * np.sin(ga), 0.0],
                  [cx, cy, cz]])
    nx, ny, nz = dims
    fi = np.arange(nx) / nx
    fj = np.arange(ny) / ny
    fk = np.arange(nz) / nz
    # x 가 가장 빠르므로 (k, j, i) 순으로 쌓는다
    K, J, I = np.meshgrid(fk, fj, fi, indexing='ij')
    frac = np.stack([I.ravel(), J.ravel(), K.ravel()], axis=1)
    return (frac @ M).astype(np.float32)


def write_structured_grid(path, pts, vals, dims, name):
    with open(path, 'wb') as f:
        f.write(b'# vtk DataFile Version 3.0\n')
        f.write(b'RASPA density on Cartesian grid (vtk_to_cartesian.py)\n')
        f.write(b'BINARY\nDATASET STRUCTURED_GRID\n')
        f.write(f'DIMENSIONS {dims[0]} {dims[1]} {dims[2]}\n'.encode())
        f.write(f'POINTS {pts.shape[0]} float\n'.encode())
        f.write(pts.astype('>f4').tobytes())
        f.write(f'\nPOINT_DATA {vals.size}\n'.encode())
        f.write(f'SCALARS {name} float 1\n'.encode())
        f.write(b'LOOKUP_TABLE default\n')
        f.write(vals.astype('>f4').tobytes())
        f.write(b'\n')


def convert(src, dst):
    vals, dims, cellp, name = read_structured_points(src)
    pts = cartesian_points(dims, cellp)
    write_structured_grid(dst, pts, vals, dims, name)
    x, y, z = pts[:, 0], pts[:, 1], pts[:, 2]
    print(f'{os.path.basename(src):<38} -> {os.path.basename(dst)}')
    print(f'   셀 {cellp[0]:.3f} {cellp[1]:.3f} {cellp[2]:.3f} / '
          f'{cellp[3]:.0f} {cellp[4]:.0f} {cellp[5]:.0f}   격자 {dims}')
    print(f'   데카르트 범위  x {x.min():8.2f} .. {x.max():7.2f}   '
          f'y {y.min():7.2f} .. {y.max():7.2f}   z {z.min():6.2f} .. {z.max():6.2f}')


def main():
    if len(sys.argv) < 2:
        raise SystemExit(__doc__)
    src = sys.argv[1]
    if os.path.isdir(src):
        names = sorted(n for n in os.listdir(src)
                       if n.endswith('.vtk') and not n.endswith('_cart.vtk'))
        if not names:
            raise SystemExit(f'{src}: 변환할 .vtk 가 없습니다')
        for n in names:
            p = os.path.join(src, n)
            try:
                convert(p, p[:-4] + '_cart.vtk')
            except SystemExit as e:
                print(f'{n:<38} 건너뜀 — {e}')
        return 0
    dst = sys.argv[2] if len(sys.argv) > 2 else src[:-4] + '_cart.vtk'
    convert(src, dst)
    return 0


if __name__ == '__main__':
    sys.exit(main())
