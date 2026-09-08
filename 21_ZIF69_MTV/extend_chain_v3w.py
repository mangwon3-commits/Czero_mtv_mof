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

# [09-07 랩탑] 절대 경로가 laptop2 로 박혀 있어 **다른 기기에서는 import 조차
# 안 됐습니다**(`FileNotFoundError` on `os.chdir`). 승인된 연장은 세 기기가
# 각자 자기 몫을 잇는 것이라(EXTEND_SCOPE_DECISION §1) 이 파일이 기기마다 돌아야
# 합니다. 파일 위치에서 뽑으면 laptop2 에서는 **값이 그대로**입니다(같은 체크아웃).
HERE_REAL = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE_REAL)
os.chdir(HERE_REAL)

import run_water_chunked as rc          # v3grid 를 끌고 들어온다
import run_water_v3w as v3w
import run_water as rw
# [2026-09-07 12:4x] **여기서 rw 를 v3w 계열로 되돌립니다 — import 만으로는 안 됩니다.**
# 예전에는 `import run_water_v3w` 가 import 시점에 rw.RUNS 를 덮어 "되돌리는" 부작용을
# 했고 위 주석이 그것에 기대고 있었습니다. 09-07 `053a806` 이 그 부작용을 `wire()` 로
# 뺐으므로(이유: 밀도 계열이 물 계열 폴더로 새던 지뢰, FF_GATES §4) 이 줄이 없으면
# rw.RUNS 가 chunked 가 끌어온 **water_runs_v3grid** 에 머물고, 이 도구는
# `water_runs_v3grid/water_runs_chunked` 를 뿌리로 봅니다 — 그 경로가 있으면 **결함판
# 시대 사슬을 연장**하고, 없으면 "사슬 없음" 으로 멈춥니다. 오류는 안 냅니다(09-07 여섯째).
v3w.wire()
assert rw.RUNS.endswith('water_runs_v3w'), rw.RUNS   # 뿌리를 잘못 잡으면 여기서 죽습니다
from check_water_equilibration import blocks   # 자는 하나

TARGETS = ["base", "saIm0875", "saIm0917", "saIm0958",
           "saIm100", "mslm050", "sa50nb50"]
BASE_CHUNKS = 5          # 본 실행이 만든 조각 수
MAX_ROUNDS = 4           # 상한 (MORNING_20260907 §2)
WINDOW_CYCLES = 15000    # Δ40 창 = **마지막 15,000 사이클** (§E, 등록문 문언)
WINDOW_CHUNKS = 5        # (옛 이름 — 보고 문구에만 남김)


# [09-07 랩탑] 사슬 뿌리를 env 로. **기본값은 그대로**라 laptop2 호출은 안 바뀝니다.
#   laptop2   <HERE>/water_runs_v3w/water_runs_chunked/rh90_<조성>
#   랩탑      <HERE>/water_runs_v3w_chunk/rh90_<조성>      (CHAIN_ROOT 로 지정)
# 기기마다 사슬을 어디에 뒀는지가 달라서, 이것 없이는 랩탑에서 "조각 0" 으로
# 조용히 나옵니다 — 실제로 --dry-run 이 그렇게 나왔습니다(있는 사슬을 못 봄).
CHAIN_ROOT = os.environ.get("CHAIN_ROOT", "")


def root(name):
    if CHAIN_ROOT:
        return os.path.join(HERE_REAL, CHAIN_ROOT, f"rh90_{name}")
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



def _chunk_cycles(name, k):
    """조각 k 의 simulation.input 에 적힌 NumberOfCycles (없으면 rc.CHUNK_CYCLES)."""
    inp = os.path.join(root(name), f"chunk{k}", "simulation.input")
    try:
        for ln in open(inp, encoding="utf-8", errors="ignore"):
            p = ln.split()
            if len(p) >= 2 and p[0] == "NumberOfCycles":
                return int(float(p[1]))
    except OSError:
        pass
    return rc.CHUNK_CYCLES

def chunk_cycles_per_block(name, k, nblocks):
    """그 조각의 **블록 하나가 몇 사이클인가**. `simulation.input` 에서 뽑습니다."""
    inp = os.path.join(root(name), f"chunk{k}", "simulation.input")
    n = None
    if os.path.exists(inp):
        for ln in open(inp, encoding="utf-8", errors="ignore"):
            q = ln.split()
            if len(q) >= 2 and q[0] == "NumberOfCycles":
                n = int(float(q[1]))
    if n is None or not nblocks:
        return None
    return n // nblocks


def window_series(name):
    """**마지막 15,000 사이클**의 (물, CO2) 블록열과 블록별 사이클.

    ⚠️ 예전 판은 `WINDOW_CHUNKS = 5`, 즉 **조각 개수**로 창을 잡았습니다.
    등록문(`MORNING §2` "이어 붙인 **마지막 15,000**", `EXTEND_APPROVED §2`)의
    창은 **사이클**이고, 조각 개수 구현은 **조각이 모두 3,000 일 때만** 그것과
    같았습니다. 단일 실행을 변환한 `chunk0`(15,000, 블록 3,000)이 섞이면
    "마지막 5조각" 이 27,000 사이클이 되어 등록문과 달라집니다.
    (`ASSIGN_20260907.md §E`, 09-07)
    """
    ks_all = done_chunks(name)
    # **블록 단위**로 뒤에서부터 모읍니다. 조각 단위로 모으면 넘칩니다 —
    # 변환된 chunk0(15,000) 하나가 통째로 들어와 창이 18,000 이 됩니다.
    # 등록문의 창은 "마지막 **15,000**" 이므로 정확히 그만큼만 씁니다.
    seq = []          # (값_물, 값_CO2, 그 블록의 사이클, 조각번호)
    for k in ks_all:
        f = glob.glob(os.path.join(root(name), f"chunk{k}",
                                   "Output", "System_0", "*.data"))
        if not f:
            continue
        d = blocks(f[0])
        bw_ = d.get("water", [])
        bc_ = d.get("CO2", [])
        cpb = chunk_cycles_per_block(name, k, len(bw_))
        if cpb is None:
            continue
        for i, x in enumerate(bw_):
            seq.append((x, bc_[i] if i < len(bc_) else float("nan"), cpb, k))
    w, c, cw, used, acc = [], [], [], [], 0
    for x, y, cpb, k in reversed(seq):
        if acc + cpb > WINDOW_CYCLES:
            break                       # 넘기지 않습니다 — 블록을 쪼개지 않습니다
        w.insert(0, x); c.insert(0, y); cw.insert(0, cpb)
        if k not in used:
            used.insert(0, k)
        acc += cpb
    return w, c, used, cw


def d40_band(v, cyc=None):
    """Δ40 — **사이클 기준** 앞 40 % 대 뒤 40 %.

    `cyc` 가 없으면 블록이 균일하다고 보고 옛 방식과 같게 셉니다.
    ⚠️ 경계가 블록 경계에 안 떨어지면 **계산을 거부**합니다(§E ③) —
    반 토막 블록을 반올림으로 넘기면 앞뒤가 다른 사이클을 덮습니다.
    """
    n = len(v)
    if cyc is None:
        cyc = [1] * n
    total = sum(cyc)
    target = total * 0.4
    def take(idx):
        acc, out = 0, []
        for i in idx:
            out.append(i); acc += cyc[i]
            if acc >= target - 1e-9:
                break
        return out, acc
    fi, fa = take(range(n))
    bi, ba = take(range(n - 1, -1, -1))
    if abs(fa - target) > 1e-6 or abs(ba - target) > 1e-6:
        raise ValueError(
            f"40 % 경계가 블록 경계에 안 떨어집니다 — 앞 {fa} · 뒤 {ba} · 목표 {target} "
            f"사이클 (블록 길이 {sorted(set(cyc))}). §E ③ 대로 계산을 거부합니다.")
    a = sum(v[i] * cyc[i] for i in fi) / fa
    b = sum(v[i] * cyc[i] for i in bi) / ba
    m = sum(v[i] * cyc[i] for i in range(n)) / total
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
        w, c, ks, cyc = window_series(n)
        if len(w) < 4:
            print(f"  {n:<10}{len(ks):>5}  블록 부족")
            allstop = False
            continue
        dw, bw, _mw = d40_band(w, cyc)
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
    # [09-07] `v3w.ff_gate()` 는 `e4fa98b` 에서 사라졌습니다(자는 `ff_gate.py` 한 자리).
    # 공개 이름을 지울 때 호출자를 grep 하지 않은 누락 — 오늘 일곱째. 파일 관문을 ff_gate 에서.
    from ff_gate import md5_gate
    if not md5_gate()[0]:
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
        # [09-08] 완주는 **조각 수가 아니라 사이클 수**로 잰다 — 변환된 chunk0(단일 실행 15,000 = 조각 1)은
        # 조각 수로 재면 "1/5" 라 막히지만 사이클로는 본 큐와 같다(ASSIGN §D-1, snapshot_to_chunk0).
        need = BASE_CHUNKS * rc.CHUNK_CYCLES
        have = sum(_chunk_cycles(n, k) for k in ks)
        if have < need:
            bad.append(f"완주 {have}/{need} 사이클(조각 {len(ks)}) — 본 큐가 아직 안 끝났다")
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
