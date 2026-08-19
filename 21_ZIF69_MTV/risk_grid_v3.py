"""격자 4종 구조 안정성 관문 — 랩탑 L4 크래시의 데스크탑 대행.

[왜 데스크탑인가]
    risk_screen.py:318 의 ProcessPoolExecutor(max_tasks_per_child=1) 은
    python 3.11+ 전용입니다. 랩탑에는 3.11 이 없고(czeromof 3.10.20,
    coremof_tools 3.9.25), 데스크탑 lammps_mof 가 3.11.15 입니다. 어제
    민감도 시험(cap 24/36)이 같은 조합으로 완주해 검증돼 있습니다.
    랩탑은 L5(RASPA)를 돌고 있지만 기기가 다르므로 RASPA·Zeo++ 동시
    금지 규칙에 걸리지 않습니다.

[규약 — 생산값 그대로]
    민감도 시험과 달리 여기는 **관문 본 실행의 연장**입니다. 31종과 같은
    표에 놓아야 하므로 OUTER_LOOP_CAP 12 를 포함해 아무것도 바꾸지 않습니다.
    base 를 같이 도는 이유는 LCD_drop 의 분모(이완된 모체의 LCD)가 같은
    프로토콜에서 나와야 하기 때문이고, 겸사겸사 랩탑 31종 실행의
    base(7.63144)와 재현 대조가 됩니다.

    결과   risk_results_v3grid.json   작업   lmp_v3grid/
"""
import json
import os
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
RELAX = os.path.join(HERE, "relax_v3")
PARENT = os.path.join(HERE, "relax_fixcell", "base_relaxed_gfnff_fixcell.cif")
STAGE = os.path.join(HERE, "structures_v3_stage")
GRID = ["saIm0583", "saIm0625", "saIm0667", "saIm0875"]

# 모듈 최상위 — spawn 자식도 같은 값을 보게 (08-18 랩탑이 잡은 결함)
sys.argv = ["risk_screen.py", "risk_grid_index.json", "v3grid"]
sys.path.insert(0, HERE)
import risk_screen as rs  # noqa: E402

rs.STRUCT = STAGE
rs.BASE_SRC = os.path.join(STAGE, "ZIF69_base.cif")
rs.MAX_WORKERS = 1        # Zeo++ 실측 10.29 GB/건, 이 기기 가용 ~17 GB


def stage():
    os.makedirs(STAGE, exist_ok=True)
    n = 0
    for f in os.listdir(RELAX):
        if f.endswith("_relaxed.cif"):
            shutil.copyfile(os.path.join(RELAX, f),
                            os.path.join(STAGE, f[:-len("_relaxed.cif")] + ".cif"))
            n += 1
    if os.path.exists(PARENT):
        shutil.copyfile(PARENT, os.path.join(STAGE, "ZIF69_base.cif"))
    return n


def main():
    for proc in ("simulate", "xtb"):
        r = subprocess.run(["pgrep", "-x", proc], capture_output=True, text=True)
        if r.stdout.split():
            print(f"  !! {proc} 가 이 기기에서 돌고 있습니다. 시작하지 않습니다.")
            return 2
    if sys.version_info < (3, 11):
        print(f"  !! python {sys.version.split()[0]} — risk_screen 은 3.11+ 필요"
              f" (max_tasks_per_child). lammps_mof 환경으로 도세요.")
        return 1
    n = stage()
    idx = os.path.join(HERE, "risk_grid_index.json")
    json.dump([{"tag": "base", "pass": True}]
              + [{"tag": t, "pass": True} for t in GRID],
              open(idx, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    print(f"격자 안정성 관문 — 생산 규약 그대로 (cap {rs.OUTER_LOOP_CAP})", flush=True)
    print(f"  staging {n}종 -> {STAGE}", flush=True)
    print(f"  대상     base + {' '.join(GRID)}", flush=True)
    print(f"  결과     {rs.RESULT}", flush=True)
    print(f"  워커     {rs.MAX_WORKERS}", flush=True)
    assert rs.STRUCT.endswith("structures_v3_stage")
    assert rs.OUTER_LOOP_CAP == 12, "생산 규약이 아닙니다"
    print(flush=True)
    return rs.main()


if __name__ == "__main__":
    sys.exit(main())
