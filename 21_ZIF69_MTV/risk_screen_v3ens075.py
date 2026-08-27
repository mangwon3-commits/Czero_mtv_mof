"""안정성 관문 자기 산포 — 2단계. `base` + `saIm075` + 그 앙상블 실현.

[왜 2단계가 발동했는가]
    1단계(`saIm0583` 11실현, 08-27 완주)에서
        s_LCD(전체 11) = **3.2326 %p**  >>  등록 문턱 1.0 %p
    가 나와, 등록 판정 ③ **"관문이 이 구간을 분해하지 못한다"** 로 확정됐습니다.
    `JUNSEOK_20260827.md` 3절이 그 경우 2단계를 지시합니다.

[1단계 결과를 그대로 옮겨 쓰지 않는 이유]
    3-1 절: *"이 산포를 `saIm0583`(15.71%)에서 재서 `saIm075`(20.26%)에
    적용하는 것은 **빌려오는 것**입니다. 조성이 다르면 산포도 다를 수 있고,
    그래서 2단계가 있습니다."* 그래서 `saIm075` 를 **직접** 잽니다.

[★ base 를 반드시 함께 넣습니다 — 1단계에서 잡은 결함]
    `risk_screen.py:350` 이 이번 실행 결과에서 base 의 after LCD 를 찾고,
    못 찾으면 `:360` 에서 **`risk_results.json`(v1)** 으로 대체합니다.
    그 값이 7.83298 인데 v3 판정이 쓴 자는 7.63144 라 **2.17%p 오차**입니다.
    조사 중인 마진이 0.26~0.87%p 이므로 오차가 신호의 2.5~8배입니다.
    공유 `risk_screen.py` 를 고치지 않고 **base 를 이 실행에 포함**해
    기준이 같은 런에서 나오게 합니다(1단계와 동일한 처리).

    참고: 이 기기의 base after LCD 는 **7.61978** 입니다(데스크탑 기록 7.63144
    와 다르고, 원인은 LAMMPS 빌드 번호 차이 — 08-27 진단 ③ 독립 잡음).
    **절대 drop 을 데스크탑 기록과 같은 표에 놓지 마십시오.**

[대상을 손으로 안 적고 찾는 이유]
    데스크탑이 넘길 실현의 접미사(`e1..e5` 인지 `r1..r5` 인지)가 착수 시점에
    정해지지 않았습니다. 그래서 `relax_v3/ZIF69_saIm075*_relaxed.cif` 를
    훑어 구성합니다. **글롭은 모듈 최상위에서 한 번만** 도므로 spawn 자식도
    같은 목록을 봅니다.

[무인 착수]
    `stage2_watch.sh` 가 cron 에서 이 러너를 부릅니다. 그 감시자는 **구조
    파일이 도착했을 때만** 걸고, 실행하는 코드는 이 파일 하나입니다 —
    저장소에서 온 스크립트를 실행하지 않습니다.
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
STAGE = os.path.join(HERE, "structures_v3ens075_stage")

# base 는 v3 판정이 쓴 것과 **같은 모체 파일**입니다.
PARENT = os.path.join(HERE, "relax_fixcell", "base_relaxed_gfnff_fixcell.cif")


# 실현 접미사 규약. 데스크탑이 어떤 형태로 넘길지 착수 시점에 안 정해져서
# 넉넉히 받습니다 — `e1` `r5` `_e1` `-e1` `_1` 전부 받고,
# **`saIm0750` 처럼 자릿수가 늘어난 다른 조성은 거부**합니다.
_REAL = re.compile(r"saIm075(?:[-_]?[a-z]+\d*|[-_]\d+)\Z")


def _discover():
    """relax_v3 에서 saIm075 계열을 찾는다. 모듈 최상위에서 한 번만 돈다.

    `ENS075_TAGS` 가 있으면 그것을 그대로 씁니다(쉼표 구분). 감시자가 이미
    확인한 목록을 넘길 때 씁니다 — 정규식 추측보다 그쪽이 확실합니다.
    """
    env = os.environ.get("ENS075_TAGS", "").strip()
    if env:
        tags = [t.strip() for t in env.split(",") if t.strip()]
        return (["base"] if tags and tags[0] != "base" else []) + tags

    found = []
    for p in sorted(glob.glob(os.path.join(RELAX, "ZIF69_saIm075*_relaxed.cif"))):
        tag = os.path.basename(p)[len("ZIF69_"):-len("_relaxed.cif")]
        if tag == "saIm075" or _REAL.match(tag):
            found.append(tag)
    # base, saIm075 가 앞에 오고 실현이 정렬되어 뒤따른다.
    real = sorted(t for t in found if t != "saIm075")
    head = ["base"] + (["saIm075"] if "saIm075" in found else [])
    return head + real


TARGETS = _discover()

# [spawn 안전] 아래 세 줄은 **반드시 모듈 최상위**여야 합니다.
# risk_screen 이 max_tasks_per_child=1 로 spawn 을 강제하고, spawn 자식은
# 이 파일을 __mp_main__ 으로 다시 실행하는데 그때 main() 은 안 돕니다.
# main() 안에 두면 자식이 STRUCT 를 v1 폴더로 읽습니다(08-18 실사고).
sys.argv = ["risk_screen.py", "risk_v3ens075_index.json", "v3ens075"]
sys.path.insert(0, HERE)
import risk_screen as rs  # noqa: E402

rs.STRUCT = STAGE
rs.BASE_SRC = os.path.join(STAGE, "ZIF69_base.cif")

# [2026-08-27] 이 상수를 내리지 마십시오. 워커 4로 올렸다가 network 4개가
# 합 24.0 GB 를 써 global OOM 이 났고 WSL 이 통째로 내려갔습니다. OOM 로그의
# total-vm 9470844 kB 가 9.5 와 정확히 일치합니다. 이전에 근거로 삼았던
# "RSS 1.21 GB" 는 zeo(before) 의 `-res` 단계이고, 비싼 것은 zeo(after) 의
# `network`(-vol/-sa) 단계입니다. 워커 1에서는 network 가 한 번에 하나뿐이라
# free 합계가 낮게 보입니다 — **동시성이 필요한 값을 동시성 1에서 재지 마십시오**
# (COMMS.md 규약 ⑦-2).
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
    # [CLAUDE.md §5] Zeo++ 와 RASPA 를 같이 띄우지 않습니다. 08-12 에 그 조합이
    # OOM 을 내고 dbus 까지 죽여 WSL 이 통째로 먹통이 됐습니다.
    r = subprocess.run(["pgrep", "-x", "simulate"], capture_output=True,
                       text=True)
    nsim = len(r.stdout.split())
    if nsim:
        print(f"  !! RASPA simulate {nsim}건이 돌고 있습니다. Zeo++ 를 얹지 "
              f"않습니다.\n     끝난 뒤에 다시 부르세요(bash bgstate.sh).")
        return 2

    # 실행 환경 확인. 08-27 에 재기동 때 PATH 를 안 옮겨 lammps-interface 가
    # `python` 을 못 찾아 12종 중 7종이 조용히 실패했습니다. 그 실패는 status
    # 에만 적히고 행 수는 그대로라 자동 푸시가 "완주" 로 알렸습니다.
    if not shutil.which("python"):
        print("  !! PATH 에 `python` 이 없습니다. lammps-interface 가 "
              "`python` 을 부릅니다.\n     conda 환경을 PATH 에 넣고 다시 "
              "부르십시오(lammps_mof).")
        return 1

    print(f"  안정성 관문 자기 산포 2단계 — base + saIm075 계열 "
          f"(총 {len(TARGETS)}종)")
    print(f"  대상     {' '.join(TARGETS)}")

    # 최소 구성 검사를 **staging 보다 먼저** 합니다. 거부될 실행이 폴더를
    # 만들고 파일을 복사해 두면, 다음 판단이 그 찌꺼기를 보고 헷갈립니다.
    # 실현이 하나도 없으면 2단계가 아니라 1종 재측정이므로 거부합니다.
    if len(TARGETS) < 3 or "saIm075" not in TARGETS:
        print(f"  !! 대상이 {TARGETS} 입니다. base + saIm075 + 실현 1개 이상이 "
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
    print(f"  워커     {rs.MAX_WORKERS}  (Zeo++ {ZEO_GB} GB/건, 가용 "
          f"{_avail:.1f} GB)")
    print(f"  python   {shutil.which('python')}")
    assert rs.STRUCT.endswith("structures_v3ens075_stage"), "경로가 안 잡혔습니다"

    idx = os.path.join(HERE, "risk_v3ens075_index.json")
    json.dump([{"tag": t, "pass": True} for t in TARGETS],
              open(idx, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    print(f"  대상 {len(TARGETS)}종\n", flush=True)
    return rs.main()


if __name__ == "__main__":
    sys.exit(main())
