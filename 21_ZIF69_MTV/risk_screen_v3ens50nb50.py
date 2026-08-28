"""안정성 관문 자기 산포 — `base` + `sa50nb50` 앙상블.

[왜 이 조성인가 — 교락을 못 끊지만 한 걸음은 갑니다]
    랩탑이 `sa50nb50` 저압 물 산포를 **80.2%** 로 쟀고 같은 자리 `saIm0583` 이
    **19.6%** 입니다(F(2,4)=16.7, p=0.011). 그런데 두 조성이 **두 가지로**
    다릅니다:

        saIm0583   모체 0.417   14/24   치환기 1종
        sa50nb50   모체 0.000   24/24   치환기 2종

    그리고 랩탑이 **이 교락은 실험으로 못 끊는다**는 것을 보였습니다 —
    24/24 에서 배열 자유도를 가지려면 치환기가 2종 이상이어야 하기 때문입니다
    (`C(24,24)=1`). 데스크탑이 `saIm100` 으로 끊자고 했다가 그것으로 반박당했습니다.

    **다만 조합적 설명 하나는 이미 죽었습니다:**

        saIm050    SO3H 12 + 모체 12   C(24,12) = 2,704,156   물 산포 17.7%
        sa50nb50   SO3H 12 + NO2  12   C(24,12) = 2,704,156   물 산포 **80.2%**

    배열 개수가 한 자리도 안 다른데 4.5배입니다.

[무엇을 가르나 — 귀속이 아니라 기제]
    기하에서 이미 산포가 크면   물 산포는 그것의 **결과**일 수 있다
    기하는 평평한데 물만 크면   **물 특유**의 것 (강한 흡착 자리 접근성)

    **교락은 여전히 안 끊깁니다** — `sa50nb50` 은 24/24 **이면서** 혼합입니다.
    그래도 어느 쪽이 나오든 지금보다 압니다.

[보고에 반드시 넣을 것 — 랩탑이 단 조건 둘]
    (가) `n` 을 병기한다. n 이 다르면 SD 의 정밀도가 다르다.
         saIm0583 n=11 · saIm075 n=6 · 이번 n=6
         그리고 `|z|` 상한 `(n−1)/√n` 도 같이 적는다(n=6 이면 2.041).
    (나) **`s_LCD` 와 물 로딩 산포는 다른 양이다.** "기하 산포로 물 산포를
         설명한다" 가 아니라 "기하 산포가 크다/작다" 까지만 적는다.

[★ base 를 반드시 포함합니다]
    `risk_screen.py:350` 이 이번 실행에서 base 를 못 찾으면 `:360` 에서
    **v1(`risk_results.json`, 7.83298)** 으로 대체합니다. v3 판정이 쓴 자는
    7.63144, 이 기기 실측은 **7.61978** 입니다. 2.17%p 오차가 납니다.

    이 기기 기대값은 **7.61978** 입니다(LAMMPS `nompi_3`). 08-27·08-28 두 번
    소수 5자리까지 재현됐습니다. 다르게 나오면 그 자체가 신호입니다.

[ZEO_GB_PER_JOB 을 내리지 마십시오]
    08-27 에 4.0 으로 내렸다가 `network` 4개가 합 24.0 GB 를 써 global OOM 이
    났고 WSL 이 통째로 내려갔습니다. OOM 로그의 `total-vm 9470844 kB` 가 9.5 와
    일치합니다. **동시성이 필요한 값을 동시성 1에서 재지 마십시오**(규약 ⑦-2).
"""
import glob
import json
import os
import re
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
RELAX = os.path.join(HERE, "relax_v3")
STAGE = os.path.join(HERE, "structures_v3ens50nb50_stage")
PARENT = os.path.join(HERE, "relax_fixcell", "base_relaxed_gfnff_fixcell.cif")

# 실현 접미사 규약. `sa50nb500` 처럼 자릿수가 늘어난 다른 조성은 거부합니다.
_REAL = re.compile(r"sa50nb50(?:[-_]?[a-z]+\d*|[-_]\d+)\Z")


def _discover():
    env = os.environ.get("ENS50NB50_TAGS", "").strip()
    if env:
        tags = [t.strip() for t in env.split(",") if t.strip()]
        return (["base"] if tags and tags[0] != "base" else []) + tags
    found = []
    for p in sorted(glob.glob(os.path.join(RELAX, "ZIF69_sa50nb50*_relaxed.cif"))):
        tag = os.path.basename(p)[len("ZIF69_"):-len("_relaxed.cif")]
        if tag == "sa50nb50" or _REAL.match(tag):
            found.append(tag)
    real = sorted(t for t in found if t != "sa50nb50")
    head = ["base"] + (["sa50nb50"] if "sa50nb50" in found else [])
    return head + real


TARGETS = _discover()

# [spawn 안전] 아래 세 줄은 반드시 모듈 최상위여야 합니다.
sys.argv = ["risk_screen.py", "risk_v3ens50nb50_index.json", "v3ens50nb50"]
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

    print(f"  안정성 관문 자기 산포 — base + sa50nb50 계열 (총 {len(TARGETS)}종)")
    print(f"  대상     {' '.join(TARGETS)}")

    if len(TARGETS) < 3 or "sa50nb50" not in TARGETS:
        print(f"  !! 대상이 {TARGETS} 입니다. base + sa50nb50 + 실현 1개 이상이 "
              f"필요합니다. 중단합니다.")
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
    assert rs.STRUCT.endswith("structures_v3ens50nb50_stage"), "경로가 안 잡혔습니다"

    idx = os.path.join(HERE, "risk_v3ens50nb50_index.json")
    json.dump([{"tag": t, "pass": True} for t in TARGETS],
              open(idx, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    print(f"  대상 {len(TARGETS)}종\n", flush=True)
    return rs.main()


if __name__ == "__main__":
    sys.exit(main())
