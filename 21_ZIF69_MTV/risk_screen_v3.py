"""구조 안정성 v3 — 이완된 구조로 LAMMPS + Zeo++ 를 돌린다.

[왜 감싸야 하는가 -- 조용히 v1 을 읽는 문제]
    risk_screen.py 는 146행에서 이렇게 구조를 찾습니다.

        src = BASE_SRC if name == "base" else os.path.join(STRUCT, ...)

    STRUCT 는 모듈 전역이고 기본값이 structures/ -- **v1 폴더**입니다. 그대로
    부르면 v3 라고 이름 붙인 결과가 v1 구조에서 나옵니다. 실패하지도 않습니다.
    이 프로젝트가 반복해서 데인 유형 그대로입니다.

[왜 이름을 바꿔 담는가]
    이완 결과는 relax_v3/ZIF69_<tag>_relaxed.cif 인데 risk_screen 은
    ZIF69_<tag>.cif 를 찾습니다. **찾는 쪽 로직을 건드리지 않습니다** --
    검증된 코드를 고치는 대신 기대하는 이름으로 staging 폴더를 만들어 줍니다.
    무치환 모체도 v3 이완본으로 갈아 끼웁니다. BASE_SRC 를 그냥 두면 모체만
    미이완 구조가 되어 비교가 깨집니다.

[사전 등록 -- 돌리기 전에 적는다]
    이 계산은 순위를 만들지 않습니다. **탈락시키는 관문**입니다.
        LCD 감소 20% 초과       -> 기공 붕괴로 판정
        최소 원자간 거리 < 0.7 A -> 구조 파탄
        접근가능부피 < 20 A^3    -> 담을 자리 없음
    통과한 것들 사이의 순위는 여기서 매기지 않습니다.

[자원 -- 08-12 먹통을 낸 바로 그 조합]
    이완 후 슈퍼셀에 Zeo++ 를 돌리면 한 건이 3.2 GB 입니다. 8워커로 25.6 GB 를
    써서 OOM 이 났고 dbus 까지 죽어 WSL 이 통째로 멈췄습니다.
    **RASPA 가 돌고 있으면 시작하지 않습니다.** 기본 워커 4(12.8 GB).
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
JUDGED = os.path.join(HERE, "relax_v3_judged.json")

# [2026-08-18 랩탑이 잡은 결함 -- 대입은 반드시 모듈 최상위에 있어야 한다]
#
#   원래 이 세 줄이 main() 안에 있었습니다. 그런데 risk_screen.py 는 워커를
#   ProcessPoolExecutor(..., max_tasks_per_child=1) 로 만듭니다.
#   **max_tasks_per_child 는 spawn 기동을 강제합니다**(fork 와 배타적이라
#   mp_context=fork 를 주면 ValueError 로 죽습니다). spawn 자식은 부모 메모리를
#   물려받지 않고 이 파일을 __mp_main__ 으로 다시 실행하는데, 그때는
#   __name__ != "__main__" 이라 main() 이 돌지 않습니다. 결과가 이렇습니다.
#
#       부모: STRUCT = structures_v3_stage   <- 화면에는 이렇게 찍힘
#       자식: STRUCT = structures            <- run_one 이 실제로 읽는 값
#
#   랩탑에는 structures/ 가 없어 FileNotFoundError 로 발각됐습니다.
#   **그 폴더가 있는 데스크탑에서는 죽지 않고 v3 라는 이름으로 v1 결과가
#   나옵니다.** 이 파일의 docstring 이 막으려던 바로 그 사고가 다른 경로로
#   재현된 것이고, 화면 출력이 정상으로 보여 눈으로도 안 잡힙니다.
#
#   최상위에 두면 spawn 자식이 파일을 다시 실행할 때도 그대로 적용됩니다.
sys.argv = ["risk_screen.py", "risk_v3_index.json", "v3"]
sys.path.insert(0, HERE)
import risk_screen as rs  # noqa: E402

rs.STRUCT = STAGE
rs.BASE_SRC = os.path.join(STAGE, "ZIF69_base.cif")

# [2026-08-18 랩탑 OOM -- 4 는 이 기기의 숫자가 아니었다]
#
#   CLAUDE.md 와 이 프로젝트의 모든 문서가 Zeo++ 워커 상한을 4 로 적었습니다.
#   그 4 는 **20 GB 를 쓰는 데스크탑에서** 측정한 값입니다(4 x 3.2 = 12.8 GB).
#   그것을 랩탑 지시서에 그대로 옮겨 적었고, 랩탑이 OOM 으로 무너졌습니다.
#
#   WSL2 는 기본으로 **호스트 RAM 의 절반**만 씁니다. 16 GB 랩탑이면 WSL 은
#   8 GB 이고, 거기에 4 x 3.2 = 12.8 GB 를 요구하면 반드시 죽습니다. 게다가
#   OOM 이 dbus-daemon 을 같이 죽이면 배포판이 통째로 먹통이 되어, 밖에서
#   wsl --shutdown 을 해야 복구됩니다(08-12 에 데스크탑에서 겪은 것과 동일).
#
#   그래서 상수를 쓰지 않고 **그 기기의 실제 가용 메모리에서 계산**합니다.
#   숫자를 문서에서 베끼면 기기가 바뀌는 순간 틀립니다.
# [2026-08-19] 3.2 도 베낀 숫자였습니다. 랩탑이 실제로 쟀습니다.
#
#   08-18 에 이 상수를 3.2 로 두고 "기기에서 계산한다" 고 적었지만, 정작
#   3.2 자체가 v1 구조에서 나온 옛 측정입니다. v3 는 이완으로 셀이 34%
#   수축했고 슈퍼셀 원자 수가 늘어, 랩탑 실측이 **한 건에 약 9.5 GB** 였습니다
#   (꾸러미의 zeo_peak.log). 3.2 를 믿으면 24 GB 기기에서 상한이 6 으로
#   계산되고, 6 x 9.5 = 57 GB 를 요구해 08-18 랩탑 OOM 이 그대로 재현됩니다.
#
#   측정값을 쓰되, 다른 기기에서 또 달라질 수 있으므로 환경변수로 덮을 수
#   있게 둡니다. **문서에서 베끼지 말고 그 기기에서 재세요.**
ZEO_GB = float(os.environ.get("ZEO_GB_PER_JOB", "9.5"))
MEM_FLOOR_GB = 4.0          # WSL 자체와 dbus 가 살아 있을 여유


def _avail_gb():
    try:
        for line in open("/proc/meminfo"):
            if line.startswith("MemAvailable:"):
                return int(line.split()[1]) / (1024.0 * 1024.0)
    except Exception:      # noqa: BLE001
        pass
    return 8.0


_avail = _avail_gb()
_cap = max(1, int((_avail - MEM_FLOOR_GB) // ZEO_GB))
_asked = int(os.environ.get("RISK_WORKERS", "4"))
rs.MAX_WORKERS = min(_asked, _cap)
if rs.MAX_WORKERS < _asked:
    print(f"  !! 워커를 {_asked} -> {rs.MAX_WORKERS} 로 낮춥니다. "
          f"가용 메모리 {_avail:.1f} GB, Zeo++ {ZEO_GB} GB/건, "
          f"여유 {MEM_FLOOR_GB} GB 확보.")


def stage():
    os.makedirs(STAGE, exist_ok=True)
    n = 0
    for f in os.listdir(RELAX):
        if not f.endswith("_relaxed.cif"):
            continue
        tag = f[: -len("_relaxed.cif")]
        shutil.copyfile(os.path.join(RELAX, f), os.path.join(STAGE, tag + ".cif"))
        n += 1
    if os.path.exists(PARENT):
        shutil.copyfile(PARENT, os.path.join(STAGE, "ZIF69_base.cif"))
    return n


def main():
    if not os.path.exists(JUDGED):
        print("  relax_v3_judged.json 이 없습니다. judge_relax_v3.py 를 먼저.")
        return 1
    r = subprocess.run(["pgrep", "-x", "simulate"], capture_output=True, text=True)
    nsim = len(r.stdout.split())
    if nsim:
        print(f"  !! RASPA simulate {nsim}건이 돌고 있습니다. Zeo++ 를 얹지 않습니다.")
        print("     끝난 뒤에 다시 부르세요(bash bgstate.sh 로 확인).")
        return 2

    j = json.load(open(JUDGED, encoding="utf-8"))
    ok = [x["name"].replace("ZIF69_", "") for x in j["rows"] if x.get("pass")]
    if os.path.exists(PARENT):
        ok = ["base"] + ok
    if os.environ.get("RISK_V3_SMOKE"):
        ok = ok[:1]
        print("  ** 연기 시험: 1종만 돌립니다 **")

    n = stage()
    print(f"  staging {n}종 -> {STAGE}", flush=True)
    idx = os.path.join(HERE, "risk_v3_index.json")
    json.dump([{"tag": t, "pass": True} for t in ok],
              open(idx, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    print(f"  대상 {len(ok)}종", flush=True)

    import risk_screen as rs
    print(f"  STRUCT   {rs.STRUCT}")
    print(f"  결과     {rs.RESULT}")
    print(f"  워커     {rs.MAX_WORKERS}  (Zeo++ {ZEO_GB} GB/건, 가용 "
          f"{_avail:.1f} GB)")
    assert rs.STRUCT.endswith("structures_v3_stage"), "v3 경로가 안 잡혔습니다"
    print(flush=True)
    return rs.main()


if __name__ == "__main__":
    sys.exit(main())
