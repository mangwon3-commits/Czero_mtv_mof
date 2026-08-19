"""안정성 관문 민감도 시험 — saIm075 의 0.26%p 가 얼마나 흔들리는 값인가.

[이 계산이 답하는 질문 — 하나뿐이다]
    saIm075 는 LCD 기준 20.26% 로 사전 등록 문턱 20% 를 **0.26%p** 넘겨
    탈락했습니다. 그런데 그 20.26% 는 **바깥 루프 12회에서 강제로 멈춰 세운**
    기하에서 잰 값입니다(risk_screen.OUTER_LOOP_CAP = 12).

    루프 예산을 늘리면 그 숫자가 어디로 가는가. 그것만 봅니다.

[판정은 바뀌지 않습니다 — 이것은 재시도가 아니라 다른 시험입니다]
    사전 등록 기준(LCD 20% 초과 탈락)은 결과가 어떻게 나오든 그대로입니다.
    CLAUDE.md 2절: 결과를 보고 기준을 고치지 않습니다.
    얻는 것은 한 줄입니다 — "이 값의 프로토콜 민감도는 ±X%p".
    실행 조건이 다르므로(cap 12 -> 24/36) 재시도가 아니라 별개 시험이고,
    결과 파일과 작업 폴더를 분리합니다(risk_results_sens*.json, lmp_sens*).

[왜 base 를 같이 도는가 — 기준선이 같이 움직이기 때문]
    risk_screen 의 LCD_drop 은 **이완 전 대비**가 아닙니다.

        drop = (base 의 이완 후 LCD  -  이 조성의 이완 후 LCD) / base 의 이완 후 LCD

    즉 **이완된 모체의 공동 대비 이 조성의 공동이 얼마나 좁은가** 입니다.
    실측으로 확인: base 이완 후 LCD 7.63144, saIm075 이완 후 6.08504
    -> (7.63144 - 6.08504) / 7.63144 = 20.26%  (랩탑 결과와 일치)

    그래서 루프 예산을 바꾸면 **분모인 base 도 같이 움직입니다.** base 를
    빼고 saIm075 만 돌리면 옛 기준선에 새 값을 대는 것이 되어 무의미합니다.

[예상 — 돌리기 전에 적어 둔다]
    risk_screen.py 220행대 실측 기록: 2026-08-09 에 상한 없이 돌렸을 때
    무치환은 50루프에서 EDiff 5.3e-08 로 수렴했지만 **saIm075 는 3.8 -> 123.7
    로 에너지가 오히려 올라갔고 3시간 타임아웃에 걸려 산출물이 없었습니다.**

    따라서 (a) cap 을 올려도 수렴하지 않을 가능성이 높고, (b) cap 36 은
    타임아웃에 걸릴 수 있습니다. **걸리는 것 자체가 결과입니다** — "예산을
    3배로 줘도 이 값은 정해지지 않는다" 가 되니까요.

사용:
    RISK_SENS_CAP=24 python risk_sens_v3.py
    RISK_SENS_CAP=36 python risk_sens_v3.py
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

CAP = int(os.environ.get("RISK_SENS_CAP", "24"))
SUFFIX = f"sens{CAP}"

# [모듈 최상위여야 합니다] risk_screen 은 max_tasks_per_child=1 로 spawn 을
# 강제하고, spawn 자식은 이 파일을 __mp_main__ 으로 다시 실행합니다. main()
# 안에서 대입하면 자식이 기본값(v1 폴더, cap 12)을 씁니다. 08-18 랩탑이
# 잡아낸 결함과 같은 자리입니다.
sys.argv = ["risk_screen.py", f"risk_sens_index_{CAP}.json", SUFFIX]
sys.path.insert(0, HERE)
import risk_screen as rs  # noqa: E402

rs.STRUCT = STAGE
rs.BASE_SRC = os.path.join(STAGE, "ZIF69_base.cif")
rs.OUTER_LOOP_CAP = CAP          # <- 이 시험의 유일한 변경점
rs.MAX_WORKERS = 1               # Zeo++ 실측 10.29 GB/건. 한 번에 하나만


def stage():
    os.makedirs(STAGE, exist_ok=True)
    n = 0
    for f in os.listdir(RELAX):
        if f.endswith("_relaxed.cif"):
            tag = f[: -len("_relaxed.cif")]
            shutil.copyfile(os.path.join(RELAX, f),
                            os.path.join(STAGE, tag + ".cif"))
            n += 1
    if os.path.exists(PARENT):
        shutil.copyfile(PARENT, os.path.join(STAGE, "ZIF69_base.cif"))
    return n


def main():
    for proc in ("simulate", "xtb", "network"):
        r = subprocess.run(["pgrep", "-x", proc], capture_output=True, text=True)
        if r.stdout.split():
            print(f"  !! {proc} {len(r.stdout.split())}건이 돌고 있습니다. "
                  f"시작하지 않습니다.")
            return 2
    if not os.path.exists(PARENT):
        print(f"  기준선 CIF 가 없습니다: {PARENT}")
        return 1

    n = stage()
    idx = os.path.join(HERE, f"risk_sens_index_{CAP}.json")
    json.dump([{"tag": "base", "pass": True},
               {"tag": "saIm075", "pass": True}],
              open(idx, "w", encoding="utf-8"), indent=1, ensure_ascii=False)

    print(f"안정성 민감도 시험 — 바깥 루프 상한 {CAP} (생산값 12)", flush=True)
    print(f"  staging {n}종 -> {STAGE}", flush=True)
    print(f"  대상     base, saIm075  (기준선이 같이 움직이므로 둘 다)", flush=True)
    print(f"  STRUCT   {rs.STRUCT}", flush=True)
    print(f"  결과     {rs.RESULT}", flush=True)
    print(f"  작업     {rs.WORK}", flush=True)
    print(f"  워커     {rs.MAX_WORKERS}", flush=True)
    assert rs.STRUCT.endswith("structures_v3_stage"), "v3 경로가 안 잡혔습니다"
    assert rs.OUTER_LOOP_CAP == CAP, "cap 이 안 잡혔습니다"
    print(flush=True)
    return rs.main()


if __name__ == "__main__":
    sys.exit(main())
