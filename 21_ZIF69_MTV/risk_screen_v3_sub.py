"""안정성 관문 — 부분집합(env RISK_SUB_TAGS 로 지정). risk_screen_v3ens_nb050.py 복제, 이름만 일반화(09-08). 출력 risk_results_v3sub.json (덧붙임이 아니라 덮어씀 — 실행 전 기존 파일 이름 바꿔 둘 것).
출력: risk_results_v3sub.json  대상: RISK_SUB_TAGS 또는 relax_v3/ZIF69_nbIm050*_relaxed.cif
"""
import os as _os

# ============================================================================
# [2026-08-28] 이완이 **비결정론적**이었습니다. 여기서 고정합니다.
#
#   lammps_interface/lammps_main.py:318
#       angles = set([j['potential'].name for ... ])
#
#   문자열 `set` 을 순회해 `angle_style hybrid <이름들>` 순서를 냅니다.
#   PYTHONHASHSEED 가 미설정이면 파이썬이 **프로세스마다** 문자열 해시를
#   무작위화하므로 순서가 실행마다 바뀝니다. LAMMPS 가 다른 순서로 합을
#   내면 부동소수점 반올림이 달라지고 최소점이 달라집니다.
#
#   실측 (같은 CIF · 같은 기기 · 같은 빌드):
#       시드 미고정 6회   cosine 먼저 4 · fourier 먼저 2
#       PYTHONHASHSEED=0  6회 전부 동일
#       base after LCD    cosine 먼저 7.61978  ·  fourier 먼저 7.63144
#
#   risk_screen.py:346 이 max_tasks_per_child=1 이라 **구조마다 새 프로세스 =
#   새 시드**입니다. 그래서 한 실행 안에서도 구조마다 순서가 달랐습니다
#   (데스크탑 lmp_v3grid: saIm0667 만 cosine, 나머지는 fourier).
#
#   ⚠️ **이 고정은 앞으로의 재현성을 위한 것이지 과거를 맞추는 것이 아닙니다.**
#      어느 값으로 고정해도 과거의 절반은 재현되지 않습니다.
#      `0` 은 `fourier` 먼저 = base 7.63144 쪽입니다.
#
#   ⚠️ 그래서 **base 를 같은 실행에 포함하는 것**이 유일한 방어입니다.
#      빌드 차이라면 기기별 상수라 보정할 수 있지만, 해시 순서는 구조마다
#      무작위라 보정이 불가능합니다.
#
#   setdefault 이므로 기동 시 `PYTHONHASHSEED=... python runner.py` 로 덮을 수
#   있습니다. 이 줄은 lammps-interface 를 **자식 프로세스로** 부르는
#   risk_screen.py:220 에 상속되어 거기서 효력을 냅니다.
# ============================================================================
_os.environ.setdefault("PYTHONHASHSEED", "0")

import glob
import json
import os
import re
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
RELAX = os.path.join(HERE, "relax_v3")
STAGE = os.path.join(HERE, "structures_v3sub_stage")
PARENT = os.path.join(HERE, "relax_fixcell", "base_relaxed_gfnff_fixcell.cif")

# 실현 접미사 규약. `nbIm0500` 처럼 자릿수가 늘어난 다른 조성은 거부합니다.
_REAL = re.compile(r"nbIm050(?:[-_]?[a-z]+\d*|[-_]\d+)\Z")


def _discover():
    env = os.environ.get("RISK_SUB_TAGS", "").strip()
    if env:
        tags = [t.strip() for t in env.split(",") if t.strip()]
        return (["base"] if tags and tags[0] != "base" else []) + tags
    found = []
    for p in sorted(glob.glob(os.path.join(RELAX, "ZIF69_nbIm050*_relaxed.cif"))):
        tag = os.path.basename(p)[len("ZIF69_"):-len("_relaxed.cif")]
        if tag == "nbIm050" or _REAL.match(tag):
            found.append(tag)
    real = sorted(t for t in found if t != "nbIm050")
    head = ["base"] + (["nbIm050"] if "nbIm050" in found else [])
    return head + real


TARGETS = _discover()

# [spawn 안전] 아래 세 줄은 반드시 모듈 최상위여야 합니다.
sys.argv = ["risk_screen.py", "risk_v3sub_index.json", "v3sub"]
sys.path.insert(0, HERE)
import risk_screen as rs  # noqa: E402

rs.STRUCT = STAGE
rs.BASE_SRC = os.path.join(STAGE, "ZIF69_base.cif")

ZEO_GB = float(os.environ.get("ZEO_GB_PER_JOB", "9.5"))
MEM_FLOOR_GB = 4.0


def _avail_gb():
    try:
        for line in open("/proc/meminfo"):
            if line.startswith("MemAvailable:"):
                return int(line.split()[1]) / (1024.0 * 1024.0)
    except Exception:      # noqa: BLE001
        pass
    return 8.0


_avail = _avail_gb()
rs.MAX_WORKERS = max(1, int((_avail - MEM_FLOOR_GB) // ZEO_GB))


def stage():
    os.makedirs(STAGE, exist_ok=True)
    n, missing = 0, []
    for tag in TARGETS:
        src = (PARENT if tag == "base"
               else os.path.join(RELAX, f"ZIF69_{tag}_relaxed.cif"))
        if not os.path.exists(src):
            missing.append(tag)
            continue
        shutil.copyfile(src, os.path.join(STAGE, f"ZIF69_{tag}.cif"))
        n += 1
    return n, missing


def main():
    r = subprocess.run(["pgrep", "-x", "simulate"], capture_output=True, text=True)
    nsim = len(r.stdout.split())
    if nsim:
        print(f"  !! RASPA simulate {nsim}건이 돌고 있습니다. Zeo++ 를 얹지 "
              f"않습니다.\n     끝난 뒤에 다시 부르세요.")
        return 2

    if not shutil.which("python"):
        print("  !! PATH 에 `python` 이 없습니다. lammps-interface 가 그것을 "
              "부릅니다.\n     lammps_mof 환경을 PATH 에 넣고 다시 부르십시오.")
        return 1

    print(f"  안정성 관문 — 부분집합 RISK_SUB_TAGS (총 {len(TARGETS)}종)")
    print(f"  대상     {' '.join(TARGETS)}")

    if len(TARGETS) < 2:                       # 부분집합 판: base + 대상 1개 이상이면 됩니다 (nbIm050 요구 제거, 09-08)
        print(f"  !! 대상이 {TARGETS} 입니다. base + 대상 1개 이상이 필요합니다. 중단합니다.")
        return 1
    if TARGETS[0] != "base":
        print("  !! base 가 첫 대상이 아닙니다. 중단합니다.")
        return 1

    n, missing = stage()
    print(f"  staging  {n}종 -> {STAGE}")
    if missing:
        print(f"  !! 이완 CIF 없음: {missing}")
        return 1

    print(f"  STRUCT   {rs.STRUCT}")
    print(f"  결과     {rs.RESULT}")
    print(f"  워커     {rs.MAX_WORKERS}  (Zeo++ {ZEO_GB} GB/건, 가용 {_avail:.1f} GB)")
    print(f"  python   {shutil.which('python')}")
    assert rs.STRUCT.endswith("structures_v3sub_stage"), "경로가 안 잡혔습니다"

    idx = os.path.join(HERE, "risk_v3sub_index.json")
    json.dump([{"tag": t, "pass": True} for t in TARGETS],
              open(idx, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    print(f"  대상 {len(TARGETS)}종\n", flush=True)
    return rs.main()


if __name__ == "__main__":
    sys.exit(main())
