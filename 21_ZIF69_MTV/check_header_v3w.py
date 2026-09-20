"""읽기 전용 머리말 관문 점검기 — 298 K 습윤 WC 실행 폴더(`humid_wc_runs_v3w/`).

[왜]
    `run_humid_wc_v3w.py` 는 **파일 관문(md5)만** 합니다(그 머리말 §9). RASPA 가 실제로
    인쇄한 쌍은 안 읽고, 결과 JSON 에도 `header_gate` 를 안 남깁니다 — 323 K 래퍼
    (`run_humid_wc_v3w_323.py` `_header_gate`)와 갈립니다. 09-05 에 "설정은 맞는데 지역
    힘장이 안 먹은 채 완주" 한 사례가 있었고, 파일 관문만으로는 그것을 못 잡습니다
    (`FF_GATES_20260907.md`, 랩탑 09-20 10:0x 지적).

[무엇]
    실행 폴더를 **조성별로** 훑어 `ff_gate.read_ff_header` 로 머리말을 읽고,
    Ow-Ow ε = 89.633 · Hw/Lw 네 쌍 ZERO_POTENTIAL 을 확인합니다. **아무것도 쓰지 않고
    아무것도 안 띄웁니다** — 돌고 있는 배치 위에서 안전하게 돌릴 수 있습니다
    (CLAUDE.md §6: 러너는 안 건드립니다).

[가족이 여럿입니다 — 랩탑 09-20 10:3x 지적]
    기본값 한 가족(`humid_wc_runs_v3w`)만 보면 **다른 가족이 통째로 안 보입니다.**
    랩탑에 일곱(v3ens0500·v3ens0583·v3nb3·v3g0583·v3grid·v3mslm050·v3w),
    데스크탑에 넷(v3w·v3w_323·v3mslm075·v4m1)이 있었습니다. 그래서 **기본값은 이제
    `humid_wc_runs*` 전부**입니다. 한 가족만 보려면 `--runs` 로 찍으십시오.

⚠️ **파일 이름에 `$(hostname)` 을 쓰지 마십시오** — 랩탑의 hostname 이
   `DESKTOP-NVSRR9M` 이라 `header_gate_v3w_desktop-nvsrr9m.json` 이 되어 데스크탑 판
   옆에서 **기기가 뒤집혀 읽힙니다**(랩탑 09-20 10:3x, desktop.md 08-29 "전달자가
   측정자로 기록됨"). 323 K 결과와 같은 기기 태그(`desktop`·`laptop`·`laptop2`)를 쓰십시오.

사용:
    python3 check_header_v3w.py                            # humid_wc_runs* 전 가족
    python3 check_header_v3w.py --json header_gate_v3w_laptop.json
    python3 check_header_v3w.py --runs humid_wc_runs_v3w   # 한 가족만
"""
import argparse
import json
import os
import sys

import ff_gate

OWOW_EPS = 89.633                      # FF_GATES_20260907.md


def gate_one(d):
    """조성 폴더 하나. 반환 (ok|None, 상세). None = .data 아직 없음(진행 중)."""
    has = any(f.endswith(".data") for _, _, fs in os.walk(d) for f in fs)
    if not has:
        return None, None
    try:
        h = ff_gate.read_ff_header(d)
    except Exception as e:             # noqa: BLE001
        return False, {"error": str(e)[:120]}
    eps = h.get("OwOw_eps")
    pairs = [k for k in ("HwHw", "OwHw", "OwLw", "LwLw") if k in h]
    ok = (eps is not None and abs(eps - OWOW_EPS) < 0.01
          and bool(pairs) and all("ZERO_POTENTIAL" in str(h[k]) for k in pairs))
    return ok, {"OwOw_eps": eps, "pairs": {k: str(h[k])[:40] for k in pairs}}


def scan(runs):
    """가족 하나. 반환 (결과 dict, 통과, 불통과, 진행중)."""
    out, ok_n, bad, pend = {}, 0, 0, 0
    subs = sorted(d for d in os.listdir(runs)
                  if os.path.isdir(os.path.join(runs, d)))
    for s_ in subs:
        ok, det = gate_one(os.path.join(runs, s_))
        out[s_] = {"ok": ok, "detail": det}
        if ok is None:
            pend += 1
            mark = "…진행 중(.data 없음)"
        elif ok:
            ok_n += 1
            mark = "통과"
        else:
            bad += 1
            mark = f"!! 불통과  {det}"
        print(f"    {s_:34} {mark}")
    return out, ok_n, bad, pend


def main():
    ap = argparse.ArgumentParser(description="습윤 WC 머리말 관문(읽기 전용, 전 가족)")
    ap.add_argument("--runs", default=None,
                    help="한 가족만 본다(기본: humid_wc_runs* 전부)")
    ap.add_argument("--json", default=None, help="결과를 이 파일에 쓴다(기본: 안 씀)")
    a = ap.parse_args()
    fams = ([a.runs] if a.runs
            else sorted(d for d in os.listdir(".")
                        if d.startswith("humid_wc_runs") and os.path.isdir(d)))
    fams = [f for f in fams if os.path.isdir(f)]
    if not fams:
        print("!! 습윤 WC 실행 폴더 가족을 못 찾았습니다(humid_wc_runs*)")
        return 2
    all_out, tot = {}, [0, 0, 0]
    print(f"  머리말 관문 — 가족 {len(fams)}개, 기준 Ow-Ow {OWOW_EPS} (읽기 전용)")
    for f in fams:
        print(f"  [{f}]")
        out, ok_n, bad, pend = scan(f)
        all_out[f] = out
        tot = [tot[0] + ok_n, tot[1] + bad, tot[2] + pend]
        print(f"    -- {f}: 통과 {ok_n} · 불통과 {bad} · 진행 중 {pend}")
    print(f"  합계  통과 {tot[0]} · 불통과 {tot[1]} · 진행 중 {tot[2]}")
    if tot[1]:
        print("  !! 불통과는 09-06 물 힘장 수정 **이전** 실행이면 정상입니다"
              " (WATER_FIX_20260906.md — 그 계열은 v3w_* 가 아닙니다)."
              " 실행일과 결과 폴더를 같이 보십시오.")
    if a.json:
        json.dump(all_out, open(a.json, "w", encoding="utf-8"),
                  indent=1, ensure_ascii=False)
        print(f"  기록 {a.json}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
