"""Q_st 목표대 재유도 — RT 부호 정정(QST_RT_SIGN_20260911.md) 뒤.

[무엇]
    QST_WINDOW_20260822.md(= tools/make_figs.py 그림 6)의 모형을 **보정 Q_st 척도**로 다시 푼다.
    회귀 ln K_H = A + B·(Q/RT) 의 Q 는 보정 전 값이었다. 모든 점이 같은 Δ = 2RT 만큼 옮겨지므로
    보정 척도의 회귀는 정확히  A' = A − 2B, 기울기 B 불변  이다(38점을 다시 맞출 필요가 없다 — 대수).
    반트호프 b(T) = b(298)·exp[(Q/R)(1/T−1/298)] 의 Q 는 **참 Q_st** 여야 하므로 보정값을 넣는다.
    여기서 옛 모형과 갈린다 — 같은 물질(같은 K_H)이 더 큰 Q 로 온도 스윙을 타므로 373 K 잔류가 줄고 WC 가 커진다.

[검증]
    --old 로 옛 모형을 그대로 풀면 QST_WINDOW_20260822.md 의 표(36.0/36.6/37.1/37.6/38.0)가 재현돼야 한다.

사용:  python qst_window_rt.py
"""
import math, sys

R = 8.314e-3                     # make_figs.py 와 같은 값(8.314462618 아님 — 재현을 위해)
A, B = -13.979, 0.4511           # 옛 회귀(보정 전 Q 척도), QST_WINDOW_20260822
T1, T2, P = 298.0, 373.0, 15000.0
DQ = 2 * R * T1                  # 4.955 kJ/mol
A_NEW = A - 2 * B                # 보정 척도 절편 (정확)
CP_TERM = 67.5                   # 현열 kJ/kg, Cp 0.9·ΔT 75


def KH(Q, T, a):
    return math.exp(a + B * Q / (R * T1)) * math.exp((Q / R) * (1 / T - 1 / T1))


def wc(Q, ns, a):
    f = []
    for T in (T1, T2):
        b = KH(Q, T, a) / ns
        f.append(ns * b * P / (1 + b * P))
    return f[0] - f[1]


def E(Q, ns, a):
    return Q + CP_TERM / wc(Q, ns, a)


def scan(a, lo=18.0, hi=60.0, step=0.05):
    Qs = [lo + i * step for i in range(int((hi - lo) / step) + 1)]
    return Qs


def table(a, label):
    print(f'\n== {label}:  ln K_H = {a:.3f} + {B}·(Q/RT) ==')
    print(f'{"n_sat":>6} {"WC최적Q":>8} {"E최적Q":>7} {"minE":>7} {"허용창(110%)":>16}')
    out = {}
    for ns in (2.0, 2.5, 3.0, 4.0, 6.0):
        Qs = scan(a)
        W = [wc(Q, ns, a) for Q in Qs]; Es = [E(Q, ns, a) for Q in Qs]
        iw = max(range(len(Qs)), key=lambda i: W[i]); ie = min(range(len(Qs)), key=lambda i: Es[i])
        lim = 1.10 * Es[ie]
        inside = [Qs[i] for i in range(len(Qs)) if Es[i] <= lim]
        lo, hi = min(inside), max(inside)
        hi_s = f'{hi:.1f}' if hi < 59.9 else '(>60)'
        print(f'{ns:6.1f} {Qs[iw]:8.1f} {Qs[ie]:7.1f} {Es[ie]:7.1f} {lo:7.1f} ~ {hi_s:>6}')
        out[ns] = (Qs[iw], Qs[ie], Es[ie], lo, hi)
    return out


def cost_table(a, label, ns=2.5):
    print(f'\n-- 창 밖의 대가 ({label}, n_sat {ns}) --')
    for Q in (20, 25, 30, 35, 40, 45, 50, 80):
        print(f'  Q {Q:5.1f}   WC {wc(Q, ns, a):6.3f}   E {E(Q, ns, a):7.1f}')


if __name__ == '__main__':
    old = table(A, '옛 모형(보정 전 척도) — QST_WINDOW_20260822 재현')
    new = table(A_NEW, '보정 모형(보정 Q 척도)')
    cost_table(A, '옛'); cost_table(A_NEW, '보정')
    print('\n-- 같은 물질의 모형값: 옛(Q_old) 대 보정(Q_old+Δ), n_sat 2.5 --')
    for name, qo in (('base', 22.42), ('saIm050', 28.51), ('saIm0583', 29.31), ('saIm100', 31.07)):
        qn = qo + DQ
        print(f'  {name:9s} Q {qo:5.2f}→{qn:5.2f}   K_H 같음 {KH(qo,T1,A):.3e}={KH(qn,T1,A_NEW):.3e}   '
              f'WC {wc(qo,2.5,A):.3f}→{wc(qn,2.5,A_NEW):.3f}   E {E(qo,2.5,A):6.1f}→{E(qn,2.5,A_NEW):6.1f}')
    print('\n-- 옛 창 30~40 을 보정 척도로 그대로 옮기면(평행이동) 34.96~44.96 — 위 보정 창과 견줄 것 --')
    print(f'Δ = {DQ:.4f}   A_new = {A_NEW:.4f}')
