"""RH90 유지율 재계산 — laptop2 몫 7종, 조각 실행 (WATER_FIX_20260906 §4).

**설정은 랩탑 `run_water_v3w.py` 에서 그대로 물려받는다.** 내가 다시 안 적는다.

## import 순서가 중요하다
`run_water_chunked` 가 `run_water_v3grid` 를 import 하고, 그것이 `rw.HERE/RUNS/
CHARGED/WATER_DEF` 를 **v3grid 경로로 덮는다.** 그러므로

    1) run_water_chunked 를 먼저 import  (v3grid 가 rw 를 v3grid 로 설정)
    2) run_water_v3w 를 그 뒤에 import    (rw 를 **v3w 로 다시 설정** — 이게 최종)

## 출력 경로
chunked 의 `main()` 은 `os.path.join(HERE, 'water_runs_chunked', ...)` 로 짓는데
그 `HERE` 는 스크립트 폴더라 **옛 `water_runs_chunked/` 로 간다.** 등록문이
"옛 water_runs_* 이어받기 금지" 라 했으므로 `rw.RUNS` 아래로 돌린다.

그런데 같은 `HERE` 가 97행에서 `run_water.py` 원본을 읽는 데도 쓰인다. 그래서
**템플릿 검사를 먼저 제대로 돌린 뒤** HERE 를 바꾸고, main() 안의 중복 호출만
막는다. (검사를 건너뛰는 것이 아니라 **한 번 제대로 하고 두 번째를 막는 것**이다.)
"""
import os, sys, time

HERE_REAL = "/home/leehk/mof_project/21_ZIF69_MTV"
sys.path.insert(0, HERE_REAL)
os.chdir(HERE_REAL)

import run_water_chunked as rc          # v3grid 를 끌고 들어온다
import run_water_v3w as v3w             # rw 를 v3w 로 되돌린다 (최종)
import run_water as rw

TARGETS = ["base", "saIm0875", "saIm0917", "saIm0958",
           "saIm100", "mslm050", "sa50nb50"]


def main():
    only = sys.argv[1:] or TARGETS
    bad = [t for t in only if t not in TARGETS]
    if bad:
        print(f"!! §4 laptop2 목록에 없는 이름: {bad}")
        return 2

    if v3w.ff_gate() is None:            # 힘장 md5 관문 — 랩탑 것을 그대로 씀
        return 1

    print("RH90 유지율 재계산 — v3w 계열, **조각 실행** (laptop2 7종)", flush=True)
    print(f"  HERE     {rw.HERE}", flush=True)
    print(f"  CHARGED  {rw.CHARGED}", flush=True)
    print(f"  RH {rw.RH_LIST} · 사이클 {rw.INIT}+{rw.CYCLES} · 조각 {rc.CHUNKS}",
          flush=True)

    # 템플릿 검사를 **HERE 가 아직 실제 폴더일 때** 한 번 제대로 돌린다
    rc._assert_template_matches()
    rc._assert_template_matches = lambda: None   # main() 안의 중복 호출만 막음

    out_root = os.path.join(rw.RUNS, "chunked")
    os.makedirs(out_root, exist_ok=True)
    rc.HERE = rw.RUNS                    # -> water_runs_v3w/water_runs_chunked/...
    print(f"  출력     **{os.path.join(rw.RUNS, 'water_runs_chunked')}**", flush=True)
    print(f"  대상 {len(only)}종: {', '.join(only)}", flush=True)

    rcs = []
    for i, name in enumerate(only, 1):
        t0 = time.time()
        print(f"\n[{i}/{len(only)}] {name} RH90  시작 {time.strftime('%H:%M:%S')}",
              flush=True)
        sys.argv = ["run_water_chunked.py", "--name", name, "--rh", "0.9"]
        try:
            r = rc.main()
        except SystemExit as e:
            r = e.code
        dt = (time.time() - t0) / 3600
        print(f"[{i}/{len(only)}] {name} 종료 rc={r}  {dt:.2f} h", flush=True)
        rcs.append((name, r, round(dt, 2)))

    print("\n=== 요약 ===", flush=True)
    for n, r, h in rcs:
        print(f"  {n:<10} rc={r}  {h} h", flush=True)
    return 0 if all(r in (0, None) for _, r, _ in rcs) else 1


if __name__ == "__main__":
    sys.exit(main() or 0)
