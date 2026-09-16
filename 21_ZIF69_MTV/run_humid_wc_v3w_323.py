"""습윤 작업 용량 v3w — **실온도 판(323 K)**. run_humid_wc.py 위에 조건만 바꿔 얹는 래퍼
(2026-09-16, 등록 `REALTEMP_WC_REGISTRATION_20260916.md`; 자료 0건에서 등록. 독립 검토 3렌즈 반영판 §8).

[무엇이 다른가] 온도와 물 분압 둘뿐. 나머지(CLAUDE.md §1 고정값·사이클 5,000+15,000·힘장·전하·이동 확률·2×2×2)는
    run_humid_wc.py 의 run_one() 을 그대로 부른다 — 이 파일은 그 함수를 복제하지 않고 **앞뒤로 감싼다**(아래 [감싸는 것]).
        ads   323 K, CO₂ 0.15 bar, H₂O 11,114.1 Pa  -> RH 90 %    (psat 323.15 K = 12,349 Pa, Buck — TEMP_POINT_REGISTRATION §2 와 같은 값)
        tsa   373 K, CO₂ 0.15 bar, H₂O 11,114.1 Pa  -> RH 11.0 %
        vsa   323 K, CO₂ 0.05 bar, H₂O 11,114.1 Pa  -> RH 90 %
    물 분압은 세 조건 공통 고정 — 298 K 계열이 2,852.1 Pa 를 공통으로 둔 것과 같은 규약(run_humid_wc.py 머리말).
    그래서 298 K 계열의 tsa 잔류(RH 2.8 %)와 이 판의 tsa 잔류(RH 11 %)는 **잔류끼리 견주지 않는다** — 견주는 것은 WC 뿐.

[분리] 결과 `v3w_humid_wc_323/`, 실행 폴더 `humid_wc_runs_v3w_323/`. 298 K 계열과 폴더를 섞지 않는다(CLAUDE.md §3).

[감싸는 것 — 검토가 잡은 "실패가 결과처럼 보이는" 구멍 넷을 여기서 막는다]
    ① 출처 검사: run_one 은 폴더에 .data 가 있으면 무조건 'cached' 로 회수한다(온도·분압을 안 본다). 그래서 돌리기 전에
       .data 파일명(`_<T:%f>_<P:%g>.data`, RASPA 규약)과 머리말(External temperature / External Pressure)을 등록 조건과 대조하고,
       다르면 돌리지도 회수하지도 않고 상태 '다른조건 .data' 로 적는다. 사전검사에서도 같은 검사를 걸어 착수 전에 죽는다.
    ② 재개 가드: 재개(ContinueAfterCrash)는 **분자 배치만 복원하고 20,000 사이클을 다시 돈다**(시간 이득 0, CHUNKED_PROTOCOL §6)
       — 그리고 그 경로에 SIGSEGV 전력이 있다. run_water.guard_crash_restart 로 한 번만 시도하고 두 번째는 CrashRestart 를 버린다.
    ③ 'ok' 인데 요약 줄 없음(머리말만 쓰고 죽은 실행)은 'no-averages' 결측으로 적는다 — 원 러너는 이것을 'ok', CO2 '-' 로 찍는다.
    ④ 완주 판정: 원 러너는 전부 실패해도 JSON 을 쓰고 [OK]·종료코드 0 이다. 여기서는 작업 상태를 JSONL 로 남기고, 끝에서
       결측·머리말 관문을 세어 하나라도 모자라면 결과를 `*.PARTIAL.json` 으로 쓰고 **2 로 종료**한다. `<RESULT>.json` 이 있다 = 48/48 완주.
    이 감싸기는 전부 **모듈 최상위**에 있다 — fork 든 spawn/forkserver 든 자식이 __main__ 을 다시 읽어도 같은 함수를 본다.
    그래도 믿지 않고 _preflight 가 자식 프로세스에서 P_H2O·조건·폴더·run_one 이름을 읽어 와 대조한다.

[환경변수]
    HWC_323_TARGETS   쉼표 목록(필수; 비우면 중단 — 기본 대상을 두지 않는다). 순서 = 착수 순서(등록 §2).
    HWC_323_WORKERS   기본 8
    HWC_323_RESULT    파일명(v3w_humid_wc_323/ 아래, 기본 humid_wc_323.json). 동시에 도는 인스턴스는 반드시 다른 이름.
    HWC_323_MACHINE   결과 JSON 에 적을 기기 이름(기본 hostname — laptop2 의 hostname 이 DESKTOP-… 이라 손으로 주는 편이 낫다)
    HWC_323_DRYRUN=1  관문·사전검사·조건표·작업 목록만 찍고 종료(아무것도 안 돌린다)
"""
import glob
import json
import multiprocessing
import os
import re
import socket
import sys
import time
from concurrent.futures import ProcessPoolExecutor

import ff_gate
import run_humid_wc as hw
import run_water as rw

REAL = os.path.dirname(os.path.abspath(__file__))
V3W = os.path.join(REAL, "v3w_humid_wc_323")
os.makedirs(V3W, exist_ok=True)

P_SAT_323 = 12349.0                      # Pa, Buck, 323.15 K — TEMP_POINT_REGISTRATION_20260911.md §2
EXPECT_P_H2O = 0.90 * P_SAT_323          # 11,114.1 Pa
OWOW_EPS = 89.633                        # 머리말 관문 기준(FF_GATES_20260907.md)

# ---- 모듈 최상위 덮어쓰기 ----
hw.HERE = V3W
hw.CHARGED = os.path.join(REAL, "charged_v3")
hw.RUNS = os.path.join(REAL, "humid_wc_runs_v3w_323")
hw.RESULT = os.path.join(V3W, os.environ.get("HWC_323_RESULT", "humid_wc_323.json"))
hw.TARGETS = [t.strip() for t in os.environ.get("HWC_323_TARGETS", "").split(",") if t.strip()]
hw.MAX_WORKERS = int(os.environ.get("HWC_323_WORKERS", "8"))
hw.P_SAT_323 = P_SAT_323
hw.P_H2O = EXPECT_P_H2O
hw.CONDITIONS = [
    ("ads", 0.15e5, 323.0, P_SAT_323),
    ("tsa", 0.15e5, 373.0, hw.P_SAT_373),
    ("vsa", 0.05e5, 323.0, P_SAT_323),
]
EXPECT_CONDS = [("ads", 15000.0, 323.0, 12349.0), ("tsa", 15000.0, 373.0, 101325.0), ("vsa", 5000.0, 323.0, 12349.0)]
STATUS_LOG = hw.RESULT + ".status.jsonl"


def _folder(tag, label):
    return os.path.join(hw.RUNS, f"{label}_{tag}")


def _data_files(d):
    return sorted(glob.glob(os.path.join(d, "Output", "System_0", "*.data")))


def _stale_data(job):
    """폴더의 .data 가 이 등록의 조건으로 만들어진 것이 아니면 그 이유를 돌려준다. 없거나 맞으면 None."""
    tag, label, p_co2, temp, _ = job
    p_tot = p_co2 + hw.P_H2O
    want = f"_{temp:.6f}_{p_tot:g}.data"
    for fp in _data_files(_folder(tag, label)):
        b = os.path.basename(fp)
        if not fp.endswith(want):
            return f"{b} != *{want}"
        head = open(fp, encoding="utf-8", errors="ignore").read(65536)
        mT = re.search(r"External temperature:\s*([0-9.]+)", head, re.I)
        mP = re.search(r"External Pressure:\s*([0-9.]+)", head, re.I)
        if not (mT and mP) or abs(float(mT.group(1)) - temp) > 1e-3 or abs(float(mP.group(1)) - p_tot) > 0.05:
            return f"{b} 머리말 T={mT and mT.group(1)} P={mP and mP.group(1)} (등록 {temp} K / {p_tot:g} Pa)"
    return None


def _seed(d):
    for fn in _data_files(d):
        for ln in open(fn, encoding="utf-8", errors="ignore"):
            m = re.match(r"\s*Random number seed:\s*(\d+)", ln)
            if m:
                return int(m.group(1))
            if ln.startswith("Number of cycles"):
                break
    return None


def _header_gate(d):
    """조성별 폴더 하나의 머리말 관문. 반환 (ok|None, 상세)."""
    if not _data_files(d):
        return None, None
    try:
        h = ff_gate.read_ff_header(d)
    except Exception as e:          # noqa: BLE001
        return False, {"error": str(e)[:120]}
    eps = h.get("OwOw_eps")
    pairs = [k for k in ("HwHw", "OwHw", "OwLw", "LwLw") if k in h]
    ok = (eps is not None and abs(eps - OWOW_EPS) < 0.01
          and bool(pairs) and all("ZERO_POTENTIAL" in str(h[k]) for k in pairs))
    return ok, h


_orig_run_one = hw.run_one


def run_one_323(job):
    """run_humid_wc.run_one 을 앞뒤로 감싼다(머리말 [감싸는 것] ①②③). 상태는 STATUS_LOG 에 남긴다."""
    tag, label = job[0], job[1]
    d = _folder(tag, label)
    stale = _stale_data(job)
    if stale:
        print(f"  !! {label} {tag}: 다른 조건의 .data — {stale}", flush=True)
        out = (tag, label, None, "다른조건 .data")
    else:
        if not any(rw.finished(p) for p in _data_files(d)):
            rw.guard_crash_restart(d, f"{label}_{tag}")
        tag, label, r, st = _orig_run_one(job)
        if st in ("ok", "cached") and not (r and "CO2" in r):
            out = (tag, label, None, "no-averages")
        else:
            out = (tag, label, r, st)
    with open(STATUS_LOG, "a", encoding="utf-8") as f:
        f.write(json.dumps({"tag": out[0], "label": out[1], "status": out[3],
                            "t": time.strftime("%F %T"), "pid": os.getpid()}, ensure_ascii=False) + "\n")
    return out


hw.run_one = run_one_323


def _child_view():
    """자식 프로세스가 실제로 보는 값 — 부모의 믿음이 아니라."""
    return (hw.P_H2O, [tuple(c) for c in hw.CONDITIONS], hw.RUNS, hw.CHARGED, hw.CYCLES, hw.INIT, hw.run_one.__name__)


def _die(msg, code):
    print(f"\n  !! {msg}\n  ** 아무것도 안 돌리고 중단합니다. **", flush=True)
    sys.exit(code)


def _preflight():
    ok, md5 = ff_gate.md5_gate()
    print(f"  파일 관문 md5 {md5} {'일치' if ok else '불일치 — 중단'}", flush=True)
    if not ok:
        sys.exit(3)
    if not hw.TARGETS:
        _die("HWC_323_TARGETS 가 비어 있습니다(기본 대상 없음 — 등록 §2 의 목록을 그대로 주십시오).", 1)
    missing = [t for t in hw.TARGETS if not os.path.exists(os.path.join(hw.CHARGED, t + "_DDEC6.cif"))]
    if missing:
        _die(f"charged_v3 에 없음: {missing}", 1)
    if abs(hw.P_H2O - EXPECT_P_H2O) > 0.05 or [tuple(c) for c in hw.CONDITIONS] != EXPECT_CONDS:
        _die("부모 쪽 조건이 등록과 다릅니다(파일이 손상됐거나 편집됨).", 4)
    for p, what in ((hw.rg.SIMULATE, "simulate"), (hw.rw.WATER_DEF, "water.def")):
        if not os.path.exists(p):
            _die(f"{what} 없음: {p}", 1)
    try:
        multiprocessing.set_start_method("fork", force=True)   # 리눅스에서 늘 가능. 3.14 기본(forkserver)을 쓰지 않는다.
    except RuntimeError:
        pass
    with ProcessPoolExecutor(max_workers=1) as ex:
        p, conds, runs, charged, cyc, ini, fname = ex.submit(_child_view).result(timeout=120)
    bad = []
    if abs(p - EXPECT_P_H2O) > 0.05:
        bad.append(f"P_H2O 자식 {p} ≠ {EXPECT_P_H2O}")
    if conds != EXPECT_CONDS:
        bad.append(f"CONDITIONS 자식 {conds}")
    if runs != hw.RUNS or charged != hw.CHARGED:
        bad.append(f"폴더 자식 RUNS={runs} CHARGED={charged}")
    if (cyc, ini) != (15000, 5000):
        bad.append(f"사이클 자식 {cyc}/{ini} (CLAUDE.md §1 은 15,000/5,000)")
    if fname != "run_one_323":
        bad.append(f"자식의 run_one 이 감싸지지 않음({fname})")
    if bad:
        _die("자식 프로세스가 보는 값이 등록과 다릅니다: " + " · ".join(bad), 4)
    # 기존 .data — 재개인지, 다른 조건의 잔존물인지
    jobs = [(t, lab, pco2, T, ps) for t in hw.TARGETS for lab, pco2, T, ps in hw.CONDITIONS]
    have = [(t, lab) for t, lab, *_ in jobs if _data_files(_folder(t, lab))]
    stale = [(t, lab, _stale_data(j)) for j in jobs for t, lab in [(j[0], j[1])] if _stale_data(j)]
    if stale:
        for t, lab, why in stale:
            print(f"  !! {lab}_{t}: {why}", flush=True)
        _die(f"실행 폴더에 다른 조건의 .data 가 {len(stale)}건 있습니다 — 폴더를 비우거나 RUNS 를 확인한 뒤 다시 부르십시오.", 5)
    print(f"  자식 대조   P_H2O {p:.1f} Pa · 조건 3 · 사이클 {ini}+{cyc} · run_one={fname} · start_method {multiprocessing.get_start_method()} — 일치", flush=True)
    print(f"  python      {sys.executable} ({sys.version.split()[0]})", flush=True)
    print(f"  simulate    {hw.rg.SIMULATE}", flush=True)
    print(f"  RASPA_DIR   {os.environ.get('RASPA_DIR', '(없음 — ~/RASPA/simulations 기본)')}", flush=True)
    print(f"  water.def   {os.path.realpath(hw.rw.WATER_DEF)}", flush=True)
    for k in ("CHARGED", "RUNS", "RESULT", "TARGETS", "MAX_WORKERS"):
        print(f"  {k:12s} {getattr(hw, k)}", flush=True)
    print(f"  기존 .data  {len(have)}/{len(jobs)} 작업 (0 이면 첫 착수, >0 이면 재개 — 다른 조건 잔존물 0)", flush=True)
    for lab, pco2, T, ps in hw.CONDITIONS:
        print(f"  {lab:<4} CO2 {pco2/1e5:>5.2f} bar  {T:>5.1f} K  H2O {hw.P_H2O:>8.1f} Pa -> RH {hw.P_H2O/ps*100:>5.1f} %", flush=True)
    return jobs


def _finalize():
    """주석·씨앗·상태·머리말 관문을 JSON 에 넣고, 모자라면 PARTIAL 로 이름을 바꾼다. 반환 종료코드."""
    with open(hw.RESULT, encoding="utf-8") as f:
        d = json.load(f)
    d["note"] = ("실온도 판: 물 분압 11,114.1 Pa(RH90 @ 323 K) 세 조건 공통 고정. TSA 는 승온만으로 RH 90 -> 11.0 %. "
                 "등록 REALTEMP_WC_REGISTRATION_20260916.md. 298 K 계열(v3w_humid_wc/)과 tsa 잔류끼리 견주지 말 것.")
    d["p_sat_323_Pa"] = P_SAT_323
    d["runner"] = "run_humid_wc_v3w_323.py"
    d["machine"] = os.environ.get("HWC_323_MACHINE") or socket.gethostname()
    d["ff_md5"] = ff_gate.FF_MD5
    st = []
    if os.path.exists(STATUS_LOG):
        st = [json.loads(l) for l in open(STATUS_LOG, encoding="utf-8") if l.strip()]
    n_expect = len(hw.TARGETS) * len(hw.CONDITIONS)
    n_have = sum(len(r.get("loadings", {})) for r in d["rows"])
    d["jobs"] = {"expected": n_expect, "with_loading": n_have, "status": st}
    hg, bad_hdr = {}, []
    for row in d["rows"]:
        row["raspa_seed"] = {}
        for lab, *_ in hw.CONDITIONS:
            fd = _folder(row["name"], lab)
            row["raspa_seed"][lab] = _seed(fd)
            ok, h = _header_gate(fd)
            hg[f"{lab}_{row['name']}"] = {"ok": ok, "header": h}
            if ok is False:
                bad_hdr.append(f"{lab}_{row['name']}")
    d["header_gate"] = hg
    missing = n_expect - n_have
    d["complete"] = (missing == 0 and not bad_hdr)
    out = hw.RESULT if d["complete"] else hw.RESULT.replace(".json", ".PARTIAL.json")
    with open(out, "w", encoding="utf-8") as f:
        json.dump(d, f, indent=2, ensure_ascii=False)
    if out != hw.RESULT:
        os.remove(hw.RESULT)
        print(f"\n  !! 미완 — 결측 {missing}/{n_expect} · 머리말 관문 실패 {bad_hdr} → {os.path.basename(out)} (완주 파일 아님, 종료 2)", flush=True)
        return 2
    print(f"  완주 {n_have}/{n_expect} · 머리말 관문 전부 통과 · machine={d['machine']} · 씨앗 기록 → {os.path.basename(out)}", flush=True)
    return 0


if __name__ == "__main__":
    print("습윤 작업 용량 v3w — 실온도 판(323 K 흡착 · 373 K TSA · 323 K VSA)", flush=True)
    jobs = _preflight()
    if os.environ.get("HWC_323_DRYRUN"):
        print(f"\n  DRYRUN — 작업 {len(jobs)}개(대상 {len(hw.TARGETS)} × 조건 3), 순서 = 대상 순서(조건은 ads·tsa·vsa 로 섞임):")
        print("  " + " ".join(f"{t}:{l}" for t, l, *_ in jobs), flush=True)
        sys.exit(0)
    print(flush=True)
    rc = hw.main()
    if rc == 0 and os.path.exists(hw.RESULT):
        rc = _finalize()
    elif rc == 0:
        print("  !! main 이 0 을 돌려줬는데 결과 파일이 없습니다 — 미완(종료 2)", flush=True)
        rc = 2
    sys.exit(rc)
