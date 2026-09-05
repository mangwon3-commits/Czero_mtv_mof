"""단위 시험 T1~T3 — 본 실행 전 필수 (덱 82afe50 §5, 데스크탑 승인).
합성 격자로 돌린다. RASPA 산출이 없어도 좌표·정규화·겹침 논리를 검증할 수 있다."""
import os, sys, numpy as np
sys.path.insert(0, "/home/leehk/mof_project/21_ZIF69_MTV")
from ase.io import read
import overlap_density as od

CIF = "/home/leehk/mof_project/21_ZIF69_MTV/charged_v3/base_DDEC6.cif"
atoms = read(CIF)
cell = np.array(atoms.get_cell()); L = atoms.get_cell().lengths()
ok = lambda b: "**통과**" if b else "**실패**"

print("=== T3  좌표 왕복 + 육방 차 재현 ===")
rng = np.random.default_rng(3)
f = rng.random((2000, 3))
back = (f @ cell) @ np.linalg.inv(cell)
e = np.abs(back - f).max()
print(f"  분율->데카르트->분율 최대오차 {e:.2e}   {ok(e < 1e-10)}")
wrong = np.abs((f @ cell) - (f * L)).max()
print(f"  셀행렬 대 길이방식 최대차 {wrong:.2f} A  (육방이므로 0 이면 안 됨)   {ok(wrong > 1.0)}")

print("\n=== T1  2x2x2 복제 불변 ===")
# 같은 물리 분포를 (a) 단위셀 격자 30^3, (b) 2x2x2 슈퍼셀 격자 60^3 으로 표현
d1 = np.array([30, 30, 30]); d2 = d1 * 2
def synth(dims, reps):
    """분율좌표의 매끄러운 함수 — 복제해도 같은 물리 분포."""
    idx = np.stack(np.meshgrid(*[np.arange(x) for x in dims], indexing="ij"), -1)
    fu = np.mod(idx.reshape(-1, 3) / dims * reps, 1.0)
    return (2.6 + np.sin(2*np.pi*fu[:,0]) * np.cos(2*np.pi*fu[:,1])
                + 0.5*np.sin(4*np.pi*fu[:,2])).reshape(dims)
g1a, g1b = synth(d1, 1), synth(d1, 1)*0 + synth(d1, 1)**1.5
g2a, g2b = synth(d2, 2), synth(d2, 2)*0 + synth(d2, 2)**1.5
a1, c1, _ = od.accessible_mask(atoms, d1, L)          # 단위셀 격자
a2, c2, _ = od.accessible_mask(atoms, d2, L*2)        # 슈퍼셀 격자
O1, B1 = od.overlap(od.normalise(g1a, a1), od.normalise(g1b, a1))
O2, B2 = od.overlap(od.normalise(g2a, a2), od.normalise(g2b, a2))
print(f"  단위셀 30^3  접근가능 {a1.sum():6d}/{a1.size}  O {O1:.6f}")
print(f"  2x2x2 60^3   접근가능 {a2.sum():6d}/{a2.size}  O {O2:.6f}")
print(f"  차 {abs(O1-O2):.6f}   {ok(abs(O1-O2) < 5e-3)}")
print(f"  접근가능 분율 {a1.sum()/a1.size:.4f} 대 {a2.sum()/a2.size:.4f}  "
      f"차 {abs(a1.sum()/a1.size - a2.sum()/a2.size):.4f}")

print("\n=== T2  자기 자신과의 겹침 = 1 ===")
p = od.normalise(g1a, a1)
O, B = od.overlap(p, p)
print(f"  O(p,p) = {O:.9f}   Bhattacharyya {B:.9f}   {ok(abs(O-1) < 1e-9 and abs(B-1) < 1e-9)}")

print("\n=== 덤  직교 격자에서 서로 다른 두 분포 ===")
q = od.normalise(g1b, a1)
O, B = od.overlap(p, q)
print(f"  O(p,q) = {O:.6f}  (0<O<1 이어야)   {ok(0 < O < 1)}   Bhattacharyya {B:.6f}")
