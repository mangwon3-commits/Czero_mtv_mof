"""안정성 관문의 **자기 산포** — LCD 감소가 실현마다 얼마나 흔들리는가.

[사전 등록] `JUNSEOK_20260827.md`. 수를 보기 전에 판정을 고정했습니다.

[왜 이것을 재는가 — 관문이 벤치마크 대역을 자르고 있습니다]
    Q_st 벤치마크 대역(29.8~41 kJ/mol)에 드는 조성이 다섯인데 **전부 안정성
    관문 탈락**입니다:

        saIm100  34.01  LCD감소 22.50%   saIm0958 33.87
        saIm075  31.42  LCD감소 20.26%   saIm0875 31.12  LCD감소 21.21%
        saIm0917 30.86

    그리고 문턱(20%)을 넘긴 폭이 **`saIm075` 0.26%p · `saIm0667` 0.65%p ·
    `saIm0625` 0.87%p** 입니다. 통과 최상단(`saIm0583` 15.71%)과는 4.55%p
    간격이 있는데, **탈락 셋은 문턱에 붙어 있습니다.**

    그런데 **LCD 감소의 배치 산포는 아무도 안 쟀습니다** — 조성당 실현 하나
    입니다. 08-25~27 에 잰 모든 양이 배치 산포가 통계오차의 5배였습니다.
    LCD 감소도 그렇다면 **저 셋의 기각은 판정이 아니라 미해결**입니다.

[★ 관문을 바꾸는 것이 아닙니다]
    문턱 20% 는 **그대로**입니다. 이 계산이 묻는 것은
    **"자가 분해능이 있는가"** 이지 "자가 맞는가" 가 아닙니다.

    08-24 V5 감사가 이미 LCD/PLD 문제를 보고도 **LCD 관문을 존치**했습니다
    ("기존 판정 불변"). 그 판단을 뒤집지 않습니다. 산포를 재는 것과 문턱을
    옮기는 것은 다른 일입니다.

[무엇을 쓰는가 — 새 구조를 안 만듭니다]
    `saIm0583` 이 **실현 11개**를 갖고 있습니다:

        saIm0583          생산 (seed 0, 충돌 회피)
        saIm0583e1~e5     앙상블 (시드 1~5, 충돌 회피)
        saIm0583r1~r5     배치 대조군 (무작위 배치)

    이완 CIF 가 `relax_v3/` 에 전부 있습니다. **추가 빌드·이완 없이 안정성
    스크린만 11번 돌립니다.**

[한계 — 미리 적습니다]
    산포를 `saIm0583`(15.71%)에서 재서 `saIm075`(20.26%)에 적용하는 것은
    **빌려오는 것**입니다. 08-27 에 하루 종일 잡은 바로 그 형태입니다.
    조성이 다르면 산포도 다를 수 있습니다.

    그래서 이것은 **1단계**입니다 — 산포가 문턱 폭(0.26~0.87%p)에 견줘
    무시할 만하면 거기서 끝이고, 크면 **2단계로 `saIm075` 앙상블을 직접**
    만들어 잽니다(데스크탑 빌드 → Junseok 스크린).

[Zeo++ 는 메모리 병목입니다 — 그래서 Junseok 몫입니다]
    한 건에 약 9.5 GB(v3 실측)이고 워커 수를 `/proc/meminfo` 에서 계산합니다.
    **`RISK_WORKERS` 를 손으로 주지 마십시오**(CLAUDE.md §5).
    그리고 **RASPA 와 같이 띄우면 안 됩니다** — 08-12 에 OOM 이 dbus 까지
    죽여 WSL 이 통째로 먹통이 됐습니다. 이 러너가 `simulate` 를 세어
    돌고 있으면 **종료코드 2 로 거부**합니다.

사용:
    python3 risk_screen_v3ensA.py
"""
import json
import os
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
RELAX = os.path.join(HERE, "relax_v3")
STAGE = os.path.join(HERE, "structures_v3ensA_stage")

# 대상 — saIm0583 의 11실현. 손으로 적습니다(작업 지시서지 요약표가 아님).
TARGETS = (["saIm0583"]
           + [f"saIm0583e{i}" for i in range(1, 6)]
           + [f"saIm0583r{i}" for i in range(1, 6)])

# [spawn 안전] 아래 세 줄은 **반드시 모듈 최상위**여야 합니다.
# risk_screen 이 max_tasks_per_child=1 로 spawn 을 강제하고, spawn 자식은
# 이 파일을 __mp_main__ 으로 다시 실행하는데 그때 main() 은 안 돕니다.
# main() 안에 두면 자식이 STRUCT 를 v1 폴더로 읽습니다(08-18 실사고).
sys.argv = ["risk_screen.py", "risk_v3ensA_index.json", "v3ensA"]
sys.path.insert(0, HERE)
import risk_screen as rs  # noqa: E402

rs.STRUCT = STAGE
rs.BASE_SRC = os.path.join(STAGE, "ZIF69_base.cif")   # 이 배치에는 base 없음

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
        src = os.path.join(RELAX, f"ZIF69_{tag}_relaxed.cif")
        if not os.path.exists(src):
            missing.append(tag)
            continue
        shutil.copyfile(src, os.path.join(STAGE, f"ZIF69_{tag}.cif"))
        n += 1
    return n, missing


def main():
    r = subprocess.run(["pgrep", "-x", "simulate"], capture_output=True,
                       text=True)
    nsim = len(r.stdout.split())
    if nsim:
        print(f"  !! RASPA simulate {nsim}건이 돌고 있습니다. Zeo++ 를 얹지 "
              f"않습니다.\n     끝난 뒤에 다시 부르세요(bash bgstate.sh).")
        return 2

    n, missing = stage()
    print(f"  안정성 관문 자기 산포 — saIm0583 {len(TARGETS)}실현")
    print(f"  staging {n}종 -> {STAGE}")
    if missing:
        print(f"  !! 이완 CIF 없음: {missing}")
        return 1
    print(f"  STRUCT   {rs.STRUCT}")
    print(f"  결과     {rs.RESULT}")
    print(f"  워커     {rs.MAX_WORKERS}  (Zeo++ {ZEO_GB} GB/건, 가용 "
          f"{_avail:.1f} GB)")
    assert rs.STRUCT.endswith("structures_v3ensA_stage"), "경로가 안 잡혔습니다"
    assert len(TARGETS) == 11, "대상이 11실현이 아닙니다"

    idx = os.path.join(HERE, "risk_v3ensA_index.json")
    json.dump([{"tag": t, "pass": True} for t in TARGETS],
              open(idx, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    print(f"  대상 {len(TARGETS)}종\n", flush=True)
    return rs.main()


if __name__ == "__main__":
    sys.exit(main())
