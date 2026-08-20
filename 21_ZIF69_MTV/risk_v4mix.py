"""v4 혼합 3종 구조 안정성 관문 — 생산 규약(cap 12) 그대로. risk_grid_v3 패턴."""
import json, os, shutil, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__))
RELAX = os.path.join(HERE, "relax_v3")
PARENT = os.path.join(HERE, "relax_fixcell", "base_relaxed_gfnff_fixcell.cif")
STAGE = os.path.join(HERE, "structures_v3_stage")
V4 = ["sa50nb50", "sa25nb75", "ms50nb50"]
sys.argv = ["risk_screen.py", "risk_v4_index.json", "v4mix"]
sys.path.insert(0, HERE)
import risk_screen as rs  # noqa: E402
rs.STRUCT = STAGE
rs.BASE_SRC = os.path.join(STAGE, "ZIF69_base.cif")
rs.MAX_WORKERS = 1

def main():
    for p in ("simulate", "xtb"):
        if subprocess.run(["pgrep", "-x", p], capture_output=True, text=True).stdout.split():
            print(f"  !! {p} 실행 중 — 시작 안 함"); return 2
    if sys.version_info < (3, 11):
        print("  !! python 3.11+ 필요 (lammps_mof 로 실행)"); return 1
    os.makedirs(STAGE, exist_ok=True)
    n = 0
    for f in os.listdir(RELAX):
        if f.endswith("_relaxed.cif"):
            shutil.copyfile(os.path.join(RELAX, f), os.path.join(STAGE, f[:-len("_relaxed.cif")] + ".cif")); n += 1
    shutil.copyfile(PARENT, os.path.join(STAGE, "ZIF69_base.cif"))
    json.dump([{"tag": "base", "pass": True}] + [{"tag": t, "pass": True} for t in V4],
              open(os.path.join(HERE, "risk_v4_index.json"), "w", encoding="utf-8"), indent=1)
    print(f"v4 안정성 관문 — cap {rs.OUTER_LOOP_CAP}, base + {' '.join(V4)}, staging {n}종", flush=True)
    assert rs.OUTER_LOOP_CAP == 12
    return rs.main()

if __name__ == "__main__":
    sys.exit(main())
