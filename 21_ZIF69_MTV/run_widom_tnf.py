#!/usr/bin/env python
"""T-NF-1 Widom Q_st(CO₂) — 비-ZIF 골격(MUF-16) 전하 CIF, 온도 지정 (2026-09-19 신설).

등록 `TNF_REGISTRATION_20260910.md §1`(09-19 보완) 의 앵커 ② "Widom Q_st 영피복 대 32.3 kJ/mol"
(MUF16_ANCHORS §4 (가)) 을 재는 러너입니다.

    ⚠️ 새 러너가 아니라 **얇은 래퍼**입니다. `run_aryl_gcmc.run_one()` — v2·v3 GCMC 의 Widom 을
       전부 낸 그 함수 — 를 그대로 부르고, 모듈 전역(TEMP · RUNS)만 **최상위에서** 덮습니다
       (`run_gcmc_v3.py` 와 같은 방식; 대입을 main() 안에 두면 spawn 자식이 못 봅니다 — 08-18 교훈).
    ⚠️ 기존 러너는 한 줄도 고치지 않았습니다.

무엇이 같은가 — Widom 사이클 15,000 + 초기화 3,000 · UFF_MOF · García-Sánchez CO₂ · Ewald 1e-6 ·
컷오프 12 Å · `unit_cells()` 는 **셀에서 계산**(수직 폭 ≥ 24 Å) → ZIF-69 는 2 2 2 그대로, MUF-16 은 2 6 1
(등록 §0 슈퍼셀 예외 — 이 수는 ZIF-69 표와 나란히 순위 매기지 않습니다).
무엇이 다른가 — 온도(--temp, 실측 앵커가 293 K) 와 폴더뿐.

Q_st = −<U_gh − U_h> + RT  (RASPA dH 정의, 09-18 부호 정정 — QST_RT_SIGN_20260911.md). run_one 이 돌려주는
kc[2] 가 <U_gh>_1−<U_h>_0 입니다. 씨앗은 이 빌드에서 **폴더 생성 초**이므로 반복은 --stagger 초로 어긋냅니다.

사용:
    python run_widom_tnf.py --cif charged_v3/muf16_DDEC6.cif --tag muf16 --temp 293 --reps 2 --dry-run
    python run_widom_tnf.py --cif charged_v3/muf16_DDEC6.cif --tag muf16 --temp 293 --reps 2
출력: tnf_widom_<tag>.json · 실행 폴더 tnf_widom_runs_<tag>_s<rep>/
"""
import argparse
import glob
import json
import os
import re
import sys
import time
from concurrent.futures import ProcessPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import run_aryl_gcmc as rg   # noqa: E402
import ff_gate               # noqa: E402

R_GAS = rg.R_GAS


def _seed_of(run_dir):
    for p in glob.glob(os.path.join(run_dir, "Output", "System_0", "*.data")):
        for line in open(p, encoding="utf-8", errors="ignore"):
            m = re.search(r"Random number seed:\s*(\d+)", line)
            if m:
                return int(m.group(1))
    return None


def _one(args):
    """자식에서 전역을 다시 세운다(spawn 대비). rg.RUNS 를 반복마다 다르게."""
    cif, temp, runs = args
    rg.TEMP = float(temp)
    rg.RUNS = runs
    name, gas, mode, res, st = rg.run_one((cif, "CO2", "widom"))
    return name, res, st, runs


def main():
    ap = argparse.ArgumentParser(description="Widom Q_st(CO2) — 온도 지정, run_aryl_gcmc.run_one 재사용")
    ap.add_argument("--cif", required=True)
    ap.add_argument("--tag", required=True)
    ap.add_argument("--temp", type=float, required=True)
    ap.add_argument("--reps", type=int, default=2)
    ap.add_argument("--stagger", type=float, default=7.0)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--out", default=None)
    a = ap.parse_args()

    ok, msg = ff_gate.md5_gate()
    print(f"  [파일 관문] {msg}")
    if not ok:
        print("  !! 힘장 파일 관문 실패 — 아무것도 돌리지 않습니다."); return 3
    if not os.path.exists(a.cif):
        print(f"  !! CIF 없음: {a.cif}"); return 2
    from ase.io import read
    atoms = read(a.cif)
    na, nb, nc = rg.unit_cells(atoms)
    print(f"  CIF {a.cif}  원자 {len(atoms)}  UnitCells {na} {nb} {nc}  → 슈퍼셀 {len(atoms)*na*nb*nc} 원자")
    print(f"  온도 {a.temp} K · Widom {rg.WIDOM_CYCLES}+{rg.WIDOM_INIT} · 반복 {a.reps} (시차 {a.stagger}s)")
    runs = [os.path.join(HERE, f"tnf_widom_runs_{a.tag}_s{i+1}") for i in range(a.reps)]
    for r in runs:
        print(f"  실행 폴더 {r}")
    if a.dry_run:
        print("  --dry-run: simulate 를 띄우지 않았습니다."); return 0

    out = a.out or os.path.join(HERE, f"tnf_widom_{a.tag}.json")
    rows = []
    with ProcessPoolExecutor(max_workers=a.reps) as ex:
        futs = []
        for i, r in enumerate(runs):
            futs.append(ex.submit(_one, (a.cif, a.temp, r)))
            time.sleep(a.stagger)
        for f in futs:
            name, res, st, r = f.result()
            row = {"rep": len(rows) + 1, "runs": os.path.basename(r), "status": st,
                   "raspa_seed": _seed_of(os.path.join(r, f"widom_CO2_{name}"))}
            if res and res[0] is not None:
                kh, ekh, u, eu = res[0], res[1], res[2], res[3]
                row.update({"KH_CO2": kh, "KH_CO2_err": ekh, "dU": u, "dU_err": eu,
                            "Qst_CO2": (-u + R_GAS * a.temp) if u is not None else None,
                            "Qst_CO2_err": eu})
            rows.append(row)
            print(f"  [{st:>7}] rep {row['rep']}  Q_st {row.get('Qst_CO2')}  K_H {row.get('KH_CO2')}  seed {row['raspa_seed']}")
    vals = [r["Qst_CO2"] for r in rows if r.get("Qst_CO2") is not None]
    summ = {"tag": a.tag, "cif": os.path.relpath(a.cif, HERE), "temp_K": a.temp,
            "unit_cells": [na, nb, nc], "n_atoms_cell": len(atoms),
            "widom_cycles": rg.WIDOM_CYCLES, "widom_init": rg.WIDOM_INIT,
            "forcefield_md5": ff_gate.FF_MD5, "qst_sign": "-dU + RT (QST_RT_SIGN_20260911)",
            "rows": rows,
            "Qst_mean": (sum(vals) / len(vals)) if vals else None,
            "seed_collisions": len(rows) - len({r["raspa_seed"] for r in rows if r["raspa_seed"]}) if rows else 0,
            "note": "등록 §0 슈퍼셀 예외 — ZIF-69 v3 표와 나란히 순위 매기지 않음. 앵커 ② 대조는 TNF_RESULTS."}
    json.dump(summ, open(out, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    print(f"[OK] {out}  ({len(vals)}/{a.reps} 값)")
    return 0 if len(vals) == a.reps else 1


if __name__ == "__main__":
    sys.exit(main())
