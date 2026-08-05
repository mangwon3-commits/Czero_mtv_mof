"""공동 크기가 CO2 분산력에 얼마나 기여하는지 해석적으로 계산한다.

[왜 필요한가]
    Part 1에서 Qst 천장이 기하학적 원인임을 밝혔다 -- CO2가 한쪽 벽에서 3.4 A에
    붙어 있는데 ZIF-8 공동이 11.4 A라 반대편 벽이 너무 멀어 분산력을 못 받는다.
    Part 2에서는 ZIF-8을 치환해서 공동을 줄이는 게 불가능함을 확인했다(C2 치환기가
    창구를 향하지 케이지 중심이 아니라서).
    따라서 남은 길은 '애초에 케이지가 작은 모체'인데, 그럼 **얼마나 작아야
    얼마나 이득인지**를 알아야 한다. 이 스크립트가 그 답을 낸다.

[모형]
    골격 원자가 반지름 R 구면에 균일하게 분포한다고 보고, 그 안의 CO2가 받는
    LJ 12-6 퍼텐셜을 구면 전체에 대해 적분한다. 탐침이 중심에서 a 만큼 떨어져
    있을 때, 거리 r 의 -n 제곱을 구면적분하면 닫힌 형태가 나온다.

        I_n(a) = 2*pi*R^2 * INT_{-1}^{1} du / (A - B*u)^(n/2),  A=R^2+a^2, B=2*R*a

        I_6  = (pi*R/(2a)) * [ 1/(R-a)^4  - 1/(R+a)^4  ]
        I_12 = (pi*R/(5a)) * [ 1/(R-a)^10 - 1/(R+a)^10 ]

    비교 기준은 '무한 평면 벽'이다(공동이 무한히 클 때의 극한).

        I_6(flat)  = pi / (2 d^4)
        I_12(flat) = pi / (5 d^10)

    표면 원자밀도와 eps 는 비(比)를 취할 때 소거되므로, **순수하게 기하학적인
    증폭 배율**이 나온다. 맞출 파라미터가 없다는 게 이 계산의 장점이다.

[한계]
    구면 근사이고 CO2를 단일 사이트로 다룬다. 실제 sod 케이지는 구가 아니고
    CO2는 길이 5.4 A 의 선형 분자라, 공동이 작아지면 **배향이 제한되어 엔트로피
    손실**이 생긴다. 이 모형은 그걸 못 본다. 따라서 아래 배율은 **엔탈피 이득의
    상한**으로 읽어야 한다.
"""
import numpy as np

SIGMA = 3.2      # A, CO2-골격탄소 혼합 LJ 지름 (UFF/TraPPE 조합 근사)
R_VDW = 1.7      # A, 골격 탄소 반데르발스 반지름 (Zeo++ LCD -> 원자중심 반지름 환산용)


def I6_sphere(R, a):
    if a < 1e-9:
        return 4 * np.pi / R**4          # 중심에 있을 때의 극한
    return (np.pi * R / (2 * a)) * (1 / (R - a)**4 - 1 / (R + a)**4)


def I12_sphere(R, a):
    if a < 1e-9:
        return 4 * np.pi / R**10
    return (np.pi * R / (5 * a)) * (1 / (R - a)**10 - 1 / (R + a)**10)


def U_sphere(R, a, sigma=SIGMA):
    """표면밀도*4eps 를 1로 둔 상대 퍼텐셜 (비를 취할 것이므로 무방)."""
    return sigma**12 * I12_sphere(R, a) - sigma**6 * I6_sphere(R, a)


def U_flat(d, sigma=SIGMA):
    return sigma**12 * np.pi / (5 * d**10) - sigma**6 * np.pi / (2 * d**4)


def best_in_sphere(R, sigma=SIGMA):
    """구형 공동 안에서 가장 유리한 위치와 그때의 퍼텐셜."""
    a_grid = np.linspace(0.0, max(R - 1.5, 1e-6), 4000)
    u = np.array([U_sphere(R, a, sigma) for a in a_grid])
    i = int(np.argmin(u))
    return a_grid[i], u[i]


def best_on_flat(sigma=SIGMA):
    d = np.linspace(2.0, 12.0, 8000)
    u = U_flat(d, sigma)
    i = int(np.argmin(u))
    return d[i], u[i]


def enhancement(lcd, sigma=SIGMA):
    """Zeo++ LCD(자유 구 지름) -> 평면 벽 대비 분산력 증폭 배율.

    공동이 LJ 지름보다 작으면 어느 위치에서도 퍼텐셜이 양수다(사방이 반발벽).
    그 경우 '증폭'이라는 개념 자체가 성립하지 않으므로 None 을 돌려준다.
    """
    R = lcd / 2 + R_VDW                 # 원자 중심이 놓인 구면 반지름
    _, u_s = best_in_sphere(R, sigma)
    _, u_f = best_on_flat(sigma)
    if u_s >= 0:                        # 인력 우물이 없다 = CO2 가 못 들어간다
        return None
    return u_s / u_f


def main():
    d_f, u_f = best_on_flat()
    print(f'기준: 무한 평면 벽, 최적 거리 {d_f:.2f} A (증폭 1.00배)\n')

    # 우리가 직접 측정한 값 + 문헌값
    parents = [
        ('ZIF-8  (sod, 2-메틸Im)',      11.39, 3.41, '측정'),
        ('ZIF-69 (gme, cbIm/nIm)',      8.76, 4.96, '측정'),
        ('ZIF-68 (gme)',               10.3, 7.5, '문헌'),
        ('ZIF-90 (sod, Im-알데하이드)',  11.2, 3.5, '문헌'),
        ('ZIF-71 (rho, 디클로로Im)',     16.5, 4.2, '문헌'),
        ('ZIF-11 (rho, 벤즈Im)',        14.6, 3.0, '문헌'),
        ('ZIF-7  (sod, 벤즈Im)',         4.3, 3.0, '문헌'),
        ('ZIF-4  (cag, Im)',             2.0, 2.1, '문헌'),
    ]
    ref = enhancement(11.39)            # ZIF-8 기준
    q_pure_zif8 = 14.04                 # 측정 Qst (순수 ZIF-8, 정전기 기여 1.9%)
    q_elec_so3h = 23.88 - 14.04         # SO3H 50% 가 더해준 정전기분

    # 작용기를 붙일 여유가 있는가 -- CO2(3.3 A)를 넣고 남는 반경
    # SO3H 는 부착점에서 대략 2.8 A 뻗는다. 공동이 작을수록 붙일 자리가 없다.
    SO3H_EXTENT = 2.8

    print(f'{"모체":<26} {"LCD":>6} {"PLD":>6} {"출처":>5} {"증폭":>7} '
          f'{"예상 Qst(순수)":>14} {"+SO3H 50%":>11}')
    print('-' * 92)
    for name, lcd, pld, src in parents:
        e = enhancement(lcd)
        if e is None:
            print(f'{name:<26} {lcd:>6.2f} {pld:>6.2f} {src:>5} '
                  f'{"--":>7} {"CO2 진입 불가 (공동이 LJ 지름 미만)":>28}')
            continue
        rel = e / ref
        q_pure = q_pure_zif8 * rel
        room = (lcd - 3.3) / 2          # 한쪽 벽에 남는 반경 여유
        flags = []
        if pld < 3.3:
            flags.append('창구<3.3A')
        if room < SO3H_EXTENT:
            flags.append(f'SO3H 공간부족({room:.1f}<{SO3H_EXTENT})')
        q_so3h = f'{q_pure + q_elec_so3h:.1f}' if room >= SO3H_EXTENT else '불가'
        print(f'{name:<26} {lcd:>6.2f} {pld:>6.2f} {src:>5} {e:>7.2f} '
              f'{q_pure:>14.1f} {q_so3h:>11}'
              + ('   ' + ', '.join(flags) if flags else ''))

    print(f'\n(증폭은 평면 벽 대비. ZIF-8 = {ref:.2f}배가 기준선)')
    print('예상 Qst = 14.04 x (증폭비) + SO3H 정전기분 9.84 kJ/mol')
    print('목표 30~40 kJ/mol\n')

    print('공동 크기 스캔:')
    print(f'{"LCD":>6} {"증폭":>7} {"ZIF-8 대비":>10} {"예상 Qst(순수)":>14} {"+SO3H":>8}')
    print('-' * 50)
    for lcd in [3.2, 3.5, 4.0, 4.5, 5.0, 5.5, 6.0, 7.0, 8.0, 9.0, 10.0, 11.39, 14.0, 16.5]:
        e = enhancement(lcd)
        rel = e / ref
        print(f'{lcd:>6.2f} {e:>7.2f} {rel:>10.2f} '
              f'{q_pure_zif8*rel:>14.1f} {q_pure_zif8*rel + q_elec_so3h:>8.1f}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
