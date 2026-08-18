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

    sys.argv = ["risk_screen.py", "risk_v3_index.json", "v3"]
    sys.path.insert(0, HERE)
    import risk_screen as rs
    rs.STRUCT = STAGE
    rs.BASE_SRC = os.path.join(STAGE, "ZIF69_base.cif")
    rs.MAX_WORKERS = int(os.environ.get("RISK_WORKERS", "4"))
    print(f"  STRUCT   {rs.STRUCT}")
    print(f"  결과     {rs.RESULT}")
    print(f"  워커     {rs.MAX_WORKERS}  (Zeo++ 3.2 GB/건)")
    assert rs.STRUCT.endswith("structures_v3_stage"), "v3 경로가 안 잡혔습니다"
    print(flush=True)
    return rs.main()


if __name__ == "__main__":
    sys.exit(main())
