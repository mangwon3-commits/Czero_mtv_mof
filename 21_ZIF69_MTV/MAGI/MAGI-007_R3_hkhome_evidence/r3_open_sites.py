"""MAGI-007 R3 (Caspar) A-12 근거 — 열린 고리(2 · 3)의 4,8-자리 넷이 기하로 어떻게 갈리는지. 빌더는 import 만(main 안 부름 · 쓰기 없음).
묻는 것: ① 한 고리의 두 자리가 반전(링커 중심)으로 같은가 ② 두 열린 고리 사이에서 자리 짝이 몇 가지 거리로 갈리는가
→ "4-CN-8-Br 을 열린 링커에만" 의 배열 수. 실행: python3 r3_open_sites.py (21_ZIF69_MTV 에서) → r3_open_sites.json"""
import itertools, json, os, sys
import numpy as np
from ase import Atoms
from ase.io import read
HERE = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, HERE); os.chdir(HERE)
import build_e24_bdtdc as E  # noqa: E402
B = E.B
a0 = read(B.SRC); a0 = Atoms(a0.get_chemical_symbols(), positions=a0.positions, cell=a0.cell, pbc=True)
G = B.graph(a0); S, nring = B.sites(a0, G)
OPEN = (2, 3)
op = [s for s in S if s["ring"] in OPEN]
sym = a0.get_chemical_symbols()
def mic(v):
    f = np.linalg.solve(a0.cell.T, v); f -= np.round(f); return a0.cell.T @ f
def dist(i, j): return float(np.linalg.norm(mic(a0.positions[j] - a0.positions[i])))
O = [k for k in range(len(a0)) if sym[k] == "O"]
rec = {"src": B.SRC, "n_sites": len(S), "n_rings": nring, "open_rings": OPEN, "sites": [], "ring_inversion": {}, "pairs": []}
for s in op:
    h = s["H"]
    rec["sites"].append({"ring": s["ring"], "C": s["C"], "H": h, "H_frac": [round(x, 4) for x in a0.get_scaled_positions()[h]],
                         "H_O_min": round(min(dist(h, o) for o in O), 3)})
for r in OPEN:
    hs = [s["H"] for s in op if s["ring"] == r]
    ringC = [k for s in S if s["ring"] == r for k in [s["C"]] + s["nbr"]]
    cen = a0.positions[ringC[0]] + np.mean([mic(a0.positions[k] - a0.positions[ringC[0]]) for k in set(ringC)], axis=0)
    mid = a0.positions[hs[0]] + 0.5 * mic(a0.positions[hs[1]] - a0.positions[hs[0]])
    rec["ring_inversion"][r] = {"H_H": round(dist(*hs), 3), "mid_minus_ringcentre_A": round(float(np.linalg.norm(mic(mid - cen))), 3)}
for (a, b) in itertools.combinations(op, 2):
    if a["ring"] != b["ring"]:
        rec["pairs"].append({"H_a": a["H"], "H_b": b["H"], "d_HH": round(dist(a["H"], b["H"]), 3)})
# 배열: 고리마다 CN 을 어느 H 에 둘지(2 × 2 = 4) → 다른 고리의 CN 과 거리로 묶음
r2 = [s["H"] for s in op if s["ring"] == 2]; r3 = [s["H"] for s in op if s["ring"] == 3]
arr = []
for c2 in r2:
    for c3 in r3:
        b2 = [h for h in r2 if h != c2][0]; b3 = [h for h in r3 if h != c3][0]
        arr.append({"CN_at": [c2, c3], "Br_at": [b2, b3], "d_CN_CN": round(dist(c2, c3), 3), "d_Br_Br": round(dist(b2, b3), 3)})
rec["arrangements_4CN8Br"] = arr
rec["distinct_by_(dCNCN,dBrBr)"] = sorted({(x["d_CN_CN"], x["d_Br_Br"]) for x in arr})
json.dump(rec, open("MAGI/MAGI-007_R3_hkhome_evidence/r3_open_sites.json", "w"), indent=1)
print(json.dumps({k: rec[k] for k in ("sites", "ring_inversion", "pairs", "arrangements_4CN8Br", "distinct_by_(dCNCN,dBrBr)")}, indent=1))
