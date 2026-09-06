"""RH90 사슬 잇기 — 7종을 **라운드 병렬**로 한 조각씩 늘린다 (09-07 준비).

**사용자의 명시적 승인 뒤에만 돌린다.** 동료 세션의 착수 명령으로는 안 돌린다.
승인 전에는 `--dry-run` 만 쓴다 — 계산을 하지 않고 관문만 본다.

왜 라운드 병렬인가 (조성별 순차가 아니라)
------------------------------------------
1. 실측상 7병렬 페널티가 **1.12배뿐**이다(COST_REFERENCE §2b). 순차면 조각
   하나에 조성 시간의 합(~17 h), 병렬이면 가장 느린 하나(~5~6 h)다.

2. **더 중요한 이유** — 순차로 늘리면 조성마다 조각 수가 달라진다. 유지율은
   **조성 간 비교**로 쓰는 수인데, 조각 수가 다르면 통계 폭이 달라지고
   "정지 시 남는 물" 이 조성마다 벌어진다(STOPRULE_AND_CO2 §2). 비교하는
   수들은 **같은 엄격함에서 멈춰야** 한다.

그래서 정지도 조성별이 아니라 **라운드 단위**다. **전 조성이 만족해야 멈춘다.**
한 조성이 남으면 다 같이 한 라운드 더 간다 — 어차피 병렬이라 벽시계는 같다.

환경
----
`czeromof` 로 돈다 — 지금 도는 simulate 가 그 env 것이다(`/proc` 로 확인).
`python3` 로 돌리면 numpy 가 없어 import 에서 죽는다.

    ~/miniconda3/envs/czeromof/bin/python extend_chain_v3w.py --dry-run

자는 하나만 쓴다
----------------
Δ40 은 `check_water_equilibration.blocks` 로 읽는다. 여기서 다시 안 짠다.
창은 **마지막 15,000 사이클**(= 마지막 5조각 = 25블록)로 고정한다. 조각이
늘어도 창은 그대로다.
"""
import argparse
import glob
import math
import os
import re
import shutil
import subprocess
import sys
import time

HERE_REAL = "/home/leehk/mof_project/21_ZIF69_MTV"
sys.path.insert(0, HERE_REAL)
os.chdir(HERE_REAL)

import run_water_chunked as rc          # v3grid 를 끌고 들어온다
import run_water_v3w as v3w             # rw 를 v3w 로 되돌린다 (최종)
import run_water as rw
from check_water_equilibration import blocks   # 자는 하나

TARGETS = ["base", "saIm0875", "saIm0917", "saIm0958",
           "saIm100", "mslm050", "sa50nb50"]
BASE_CHUNKS = 5          # 본 실행이 만든 조각 수
MAX_ROUNDS = 4           # 상한 (MORNING_20260907 §2)
WINDOW_CHUNKS = 5        # Δ40 창 = 마지막 5조각 = 15,000 사이클


def root(name):
    return os.path.join(rw.RUNS, "water_runs_chunked", f"rh90_{name}")


def done_chunks(name):
    """**완주한** 조각 번호들. Restart 파일 존재로 판정하지 않는다 —
    WriteBinaryRestartFileEvery 가 실행 중에도 쓰기 때문이다."""
    out = []
    for k in range(50):
        f = glob.glob(os.path.join(root(name), f"chunk{k}",
                                   "Output", "System_0", "*.data"))
        if not f:
            break
        if rw.finished(f[0]) and rw.net_charge_ok(f[0]):
            out.append(k)
        else:
            break
    return out


def seed_of(name, k):
    f = glob.glob(os.path.join(root(name), f"chunk{k}",
                               "Output", "System_0", "*.data"))
    if not f:
        return None
    for ln in open(f[0], errors="ignore"):
        if "Random number seed:" in ln:
            return ln.split(":")[1].strip()
        if "Number of cycles" in ln:
            break
    return None


def molkg(name, ks):
    """창 안 조각들의 물 평균을 **mol/kg 로** 읽는다.

    ⚠️ 블록 값(Block[0..4])은 mol/kg 이 아니다 — `base` 가 블록 ~10.8 인데
    mol/kg 은 0.185 다. "남는 물" 을 mol/kg 으로 적으려면 여기서 읽어야 한다.
    건조 리허설에서 이 단위 착오를 잡았다.
    """
    vals = []
    for k in ks:
        f = glob.glob(os.path.join(root(name), f"chunk{k}",
                                   "Output", "System_0", "*.data"))
        if not f:
            continue
        cur = None
        for ln in open(f[0], errors="ignore"):
            m = re.match(r"\s*Component (\d+) \[(\w+)\]", ln)
            if m:
                cur = m.group(2)
            if "Average loading absolute [mol/kg framework]" in ln and cur == "water":
                mm = re.search(r":?\s*([0-9.eE+-]+)\s*\+/-", ln)
                if mm:
                    vals.append(float(mm.group(1)))
    return sum(vals) / len(vals) if vals else float("nan")


def window_series(name):
    """마지막 WINDOW_CHUNKS 조각의 (물, CO2) 블록열."""
    ks = done_chunks(name)[-WINDOW_CHUNKS:]
    w, c = [], []
    for k in ks:
        f = glob.glob(os.path.join(root(name), f"chunk{k}",
                                   "Output", "System_0", "*.data"))
        d = blocks(f[0])
        if "water" in d:
            w += d["water"]
        if "CO2" in d:
            c += d["CO2"]
    return w, c, ks


def d40_band(v):
    k = max(1, int(round(len(v) * 0.4)))
    a = sum(v[:k]) / k
    b = sum(v[-k:]) / k
    n = len(v)
    m = sum(v) / n
    sd = math.sqrt(sum((x - m) ** 2 for x in v) / (n - 1))
    return 100 * (b - a) / a, 100 * 2.776 * sd / math.sqrt(n) / m, m


def report(names):
    """라운드 끝 보고. 정지 판정은 **전 조성이 만족할 때만** True."""
    print()
    print(f"  {'조성':<10}{'조각':>5}{'물 Δ40':>10}{'폭':>8}"
          f"{'남는 물':>10}{'판정':>8}")
    print("  " + "-" * 52)
    allstop = True
    for n in names:
        w, c, ks = window_series(n)
        if len(w) < 4:
            print(f"  {n:<10}{len(ks):>5}  블록 부족")
            allstop = False
            continue
        dw, bw, _mw = d40_band(w)
        left = bw / 100 * molkg(n, ks)      # **mol/kg** 로 환산해서 적는다
        ok = abs(dw) < bw
        allstop &= ok
        print(f"  {n:<10}{len(ks):>5}{dw:>+9.1f}%{bw:>7.1f}%"
              f"{left:>10.3f}{'정지' if ok else '계속':>8}")
    print()
    print("  '남는 물' 은 정지 시 남는 물 표류의 절대량(mol/kg)이다 —")
    print("  유지율 옆에 **병기**할 수다(WATER_FIX §8). 문턱이 아니다.")
    print(f"  라운드 판정: **{'전 조성 정지' if allstop else '계속'}**"
          " (한 조성이라도 남으면 다 같이 간다)")
    return allstop


def gates(names):
    """돌리기 전에 보는 것들. 하나라도 걸리면 안 돈다."""
    print("=== 관문 ===", flush=True)
    if v3w.ff_gate() is None:
        print("  !! 힘장 관문 실패 — 사슬 중간에 힘장이 바뀌면 조용히 망가진다.")
        return False
    print("  힘장 md5 ✓")

    nsite = sum(1 for ln in open(rw.WATER_DEF, encoding="utf-8")
                if len(ln.split()) > 4 and ln.split()[1] in ("Ow", "Hw", "Lw"))
    if nsite != 5:
        print(f"  !! 물 사이트 {nsite}개 — TIP5P-Ew 는 5")
        return False
    print("  물 5사이트 ✓")

    ok = True
    for n in names:
        ks = done_chunks(n)
        cif = os.path.join(rw.CHARGED, n + "_DDEC6.cif")
        last = ks[-1] if ks else None
        rst = glob.glob(os.path.join(root(n), f"chunk{last}",
                                     "Restart", "System_0", "restart*")) if ks else []
        lastlab = f"chunk{last}" if ks else "없음"
        bad = []
        if len(ks) < BASE_CHUNKS:
            bad.append(f"완주 조각 {len(ks)}/{BASE_CHUNKS} — 본 큐가 아직 안 끝났다")
        if not os.path.exists(cif):
            bad.append("전하 CIF 없음")
        if not rst:
            bad.append(f"{lastlab} 에 Restart 파일 없음")
        s = seed_of(n, last) if ks else None
        print(f"  {n:<10} 완주 {len(ks)}조각  마지막 {lastlab}  "
              f"Restart {len(rst)}개  씨앗 {s}"
              + ("   !! " + "; ".join(bad) if bad else "   ✓"))
        ok &= not bad
    return ok


def run_round(names, k, dry):
    """조각 k 를 7종 **동시에**. 앞 조각의 Restart 를 이어받는다."""
    procs = []
    for n in names:
        d = os.path.join(root(n), f"chunk{k}")
        prev = os.path.join(root(n), f"chunk{k-1}")
        if dry:
            print(f"  [{n}] {d}  <- {prev}/Restart  (건조: 안 돈다)")
            continue
        os.makedirs(d, exist_ok=True)
        shutil.copy(os.path.join(rw.CHARGED, n + "_DDEC6.cif"),
                    os.path.join(d, n + "_DDEC6.cif"))
        shutil.copy(rw.WATER_DEF, os.path.join(d, "water.def"))
        okc, msg = rc.carry_restart(prev, d)
        print(f"  [{n}] 조각 {k} 이어 넘기기 — {msg}", flush=True)
        if not okc:
            print(f"  !! {n} 사슬이 끊겼다. 이 조성만 건너뛴다.", flush=True)
            continue
        rc.write_input(d, n, 0.9, k)      # k>0 -> 초기화 0, RestartFile yes
        procs.append((n, subprocess.Popen(
            [rw.SIMULATE, "simulation.input"], cwd=d,
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)))
    for n, p in procs:
        p.wait()
        print(f"  [{n}] 조각 {k} 종료 rc={p.returncode}  "
              f"{time.strftime('%H:%M:%S')}", flush=True)


def main():
    ap = argparse.ArgumentParser(description="RH90 사슬 잇기 (라운드 병렬)")
    ap.add_argument("--rounds", type=int, default=MAX_ROUNDS)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--names", nargs="*", default=TARGETS)
    a = ap.parse_args()

    if a.rounds > MAX_ROUNDS:
        print(f"!! 상한 {MAX_ROUNDS} 라운드 (MORNING_20260907 §2)")
        return 2

    print("RH90 사슬 잇기 — 라운드 병렬, 전 조성 동일 조각 수", flush=True)
    print(f"  뿌리 {os.path.join(rw.RUNS, 'water_runs_chunked')}", flush=True)
    print(f"  라운드 {a.rounds} (조각당 {rc.CHUNK_CYCLES} 사이클, 창은 "
          f"마지막 {WINDOW_CHUNKS}조각 고정)", flush=True)
    print(flush=True)

    passed = gates(a.names)
    if not passed and not a.dry_run:
        print("\n!! 관문에 걸렸다. 돌리지 않는다.", flush=True)
        return 1

    print("\n=== 현재 상태 (라운드 0) ===", flush=True)
    report(a.names)

    if a.dry_run:
        print("\n--dry-run 이므로 계산은 하지 않았다.", flush=True)
        if not passed:
            print("관문 미통과 — 위 !! 가 다 사라져야 실제 실행이 가능하다.",
                  flush=True)
        print("**사용자의 명시적 승인 뒤에** --rounds N 으로 돈다.", flush=True)
        return 0 if passed else 1

    start = max(done_chunks(n)[-1] for n in a.names) + 1
    for r in range(a.rounds):
        k = start + r
        print(f"\n=== 라운드 {r+1}/{a.rounds} — 조각 {k}, {len(a.names)}종 동시 ===",
              flush=True)
        t0 = time.time()
        run_round(a.names, k, False)
        print(f"  라운드 {r+1} 벽시계 {(time.time()-t0)/3600:.2f} h", flush=True)
        if report(a.names):
            print(f"\n전 조성이 정지 조건을 만족했다. {r+1} 라운드에서 멈춘다.",
                  flush=True)
            break
    return 0


if __name__ == "__main__":
    sys.exit(main() or 0)
