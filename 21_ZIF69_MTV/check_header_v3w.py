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

사용:
    python3 check_header_v3w.py                      # humid_wc_runs_v3w/ 전부
    python3 check_header_v3w.py --runs <폴더> --json out.json
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


def main():
    ap = argparse.ArgumentParser(description="298 K 습윤 WC 머리말 관문(읽기 전용)")
    ap.add_argument("--runs", default="humid_wc_runs_v3w")
    ap.add_argument("--json", default=None, help="결과를 이 파일에 쓴다(기본: 안 씀)")
    a = ap.parse_args()
    if not os.path.isdir(a.runs):
        print(f"!! 실행 폴더 없음: {a.runs}")
        return 2
    subs = sorted(d for d in os.listdir(a.runs)
                  if os.path.isdir(os.path.join(a.runs, d)))
    if not subs:
        print(f"!! {a.runs} 아래 조성 폴더가 없습니다")
        return 2
    out, bad, pend = {}, 0, 0
    print(f"  머리말 관문 — {a.runs}  ({len(subs)}개 폴더, 기준 Ow-Ow {OWOW_EPS})")
    for s in subs:
        ok, det = gate_one(os.path.join(a.runs, s))
        out[s] = {"ok": ok, "detail": det}
        if ok is None:
            pend += 1
            mark = "…진행 중(.data 없음)"
        elif ok:
            mark = "통과"
        else:
            bad += 1
            mark = f"!! 불통과  {det}"
        print(f"    {s:34} {mark}")
    print(f"  통과 {len(subs) - bad - pend} · 불통과 {bad} · 진행 중 {pend}")
    if a.json:
        json.dump(out, open(a.json, "w", encoding="utf-8"),
                  indent=1, ensure_ascii=False)
        print(f"  기록 {a.json}")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
