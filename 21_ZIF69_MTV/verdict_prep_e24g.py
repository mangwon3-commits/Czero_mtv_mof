#!/usr/bin/env python3
"""E-24g · E-24h 판정 준비(클라우드 검증석 cloud 2차 ② — ASSIGN_MAGI5B §cloud 2차, 1cf7ee81).

등록 `ASSIGN_MAGI5B_20260925.md` §HKHOME 21차(0ad35b96, 자료 0건) **문구만으로** 짠 기계적 계산.
판정문은 종합자가 씀 — 이 스크립트는 판정 가지와 그 가지의 "판정의 뜻"(등록에 미리 적힌 것)만 보임.

규약(final_close_check.py 와 같음):
  · **자료가 다 차기 전에는 그 예측의 판정량을 한 개도 찍지 않음**(진행 · 관문 문제만).
  · 기준값은 **원자료 JSON 에서** 읽음(판정표 값 입력 금지 — 09-26 규칙).
  · 단위 = 차 ÷ √(±₁² + ±₂²)(RASPA ± = 95 % CI 그대로) · 문턱 1.5.
  · 주머니(CO₂ 1.65 또는 N₂ 1.82 탐침에서 닿지 않는 주머니 > 0)가 있으면 S_ON 은 **막음값**(E-24b 판정의 뜻 · 등록 (1) "주머니가 있으면 막음값으로").
    주머니 여부를 모르면(Zeo++ 미도착) 그 후보의 S_ON 판정량을 내지 않음.

  python verdict_prep_e24g.py                              # 작업 트리
  python verdict_prep_e24g.py --ref access=origin/junseok-20260822 --ref widom=origin/master
      # 키: widom · access · bp · relax · fit (가지 최종판 직접 집기)
"""
import json, math, os, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
FF = "8e8ec933f9013c7e932da04dc256efd3"
REFS = {}
for i, a in enumerate(sys.argv):
    if a == "--ref":
        k, v = sys.argv[i + 1].split("=", 1)
        REFS[k] = v

FULL = ["e24g_br_100", "e24g_cch_100", "e24g_cf3_100", "e24g_nc3h7_100"]
HALF_C2H5 = ["e24h_c2h5_050a", "e24h_c2h5_050b"]
HALF_CL = ["e24h_cl_050a", "e24h_cl_050b"]
ALL = FULL + HALF_C2H5 + HALF_CL
PLD_MIN, TH = 3.64, 1.5


def load(rel, key=None):
    ref = REFS.get(key) if key else None
    if ref:
        cp = subprocess.run(["git", "show", f"{ref}:21_ZIF69_MTV/{rel}"], cwd=HERE, capture_output=True, text=True)
        return json.loads(cp.stdout) if cp.returncode == 0 and cp.stdout.strip() else None
    p = os.path.join(HERE, rel)
    return json.load(open(p)) if os.path.exists(p) else None


def u(d, *e):
    s = math.sqrt(sum(x * x for x in e))
    return d / s if s else float("inf")


OUT = []
def say(s=""): OUT.append(s); print(s)


# ---------------------------------------------------------------- 기준값(원자료)
def widom_on(rel, key=None):
    d = load(rel, key)
    if d is None:
        return None, "파일 없음"
    probs = []
    if not d.get("finished"): probs.append("finished 없음")
    if d.get("ff_md5") != FF: probs.append(f"ff_md5 {d.get('ff_md5')}")
    rows = {r["charges"]: r for r in d.get("rows", [])}
    for c in ("on", "off"):
        r = rows.get(c)
        if r is None: probs.append(f"{c} 행 없음"); continue
        if r.get("status_CO2") != "ok" or r.get("status_N2") != "ok": probs.append(f"{c} status {r.get('status_CO2')}/{r.get('status_N2')}")
    if probs:
        return None, "; ".join(probs)
    on, off = rows["on"], rows["off"]
    return dict(S=on["selectivity"], Se=on["selectivity_err"], S_off=off["selectivity"], S_off_e=off["selectivity_err"],
                KH=on["KH_CO2"], G=on["selectivity"] / off["selectivity"]), None


REF = {}
for name, rel in (("Cl", "results_magi5_e3_e24c_cl_100_widom_hkhome.json"),
                  ("CN", "results_magi5_e3_e24_cn_100_widom_hkhome.json"),
                  ("모체", "results_magi5_e3_e22_parent_widom_desktop-js1ib6u.json")):
    v, why = widom_on(rel)
    if v is None:
        sys.exit(f"기준값 {name} 읽기 실패: {why}")
    REF[name] = v


# ---------------------------------------------------------------- 새 자료 읽기
def gate0():
    d = load("results_e24g_fit_hkhome.json", "fit") or {}
    return {t: (d[t].get("gate0_pass") if t in d else None) for t in ALL}


def access():
    """태그 → dict(PLD, ch165, pk165, pk182, ok) 또는 None(미도착)."""
    d = load("results_e24g_access_junseok.json", "access")
    out = {}
    if d is None:
        return out, "results_e24g_access_junseok.json 없음"
    for r in d.get("rows", []):
        t = r.get("tag")
        try:
            rc_ok = all(x.get("rc") == 0 and not x.get("stopped_by_guard") for x in r.get("runs", []))
            for k in ("r1.65", "r1.82"):
                for part in ("chan", "block"):
                    x = r[k][part]
                    rc_ok &= (x.get("rc") == 0 and not x.get("stopped_by_guard"))
            out[t] = dict(PLD=r.get("PLD_Df"), ch165=r["r1.65"]["chan"].get("n_channels_chanfile"),
                          pk165=r["r1.65"]["block"].get("pockets"), pk182=r["r1.82"]["block"].get("pockets"),
                          sph165=r["r1.65"]["block"].get("n_spheres"), ok=rc_ok and r.get("PLD_Df") is not None)
        except (KeyError, TypeError) as e:
            out[t] = dict(ok=False, err=f"{type(e).__name__} {e}")
    return out, None


def blocked(tag):
    # 막음 Widom 담당이 데스크탑 → Junseok 으로 바뀜(24109aea) — 두 이름 다 봄, 둘 다 있으면 멈춤(어느 것이 정본인지 사람이 정함)
    cands = [(f, load(f, "bp")) for f in ("results_e24g_blockpockets_junseok.json", "results_e24g_blockpockets_hkhome.json")]
    have = [(f, d) for f, d in cands if d is not None]
    if not have:
        return None, "results_e24g_blockpockets_{junseok,hkhome}.json 없음"
    if len(have) > 1 and any(tag in ((d.get("per_structure") or {})) for _, d in have[1:]) and tag in (have[0][1].get("per_structure") or {}):
        return None, f"막음 파일 둘에 {tag} 가 다 있음 — 정본 지정 필요"
    d = next((d for _, d in have if tag in (d.get("per_structure") or {})), have[0][1])
    v = (d.get("per_structure") or {}).get(tag)
    if v is None:
        return None, f"막음 파일에 {tag} 없음"
    probs = []
    for k, r in (v.get("rows") or {}).items():
        if r.get("status") != "ok" or r.get("returncode") != 0 or not r.get("marker_finished") \
           or not r.get("pockets_blocked_line") or r.get("stderr_not_found") or r.get("n_blocked_reported") != r.get("n_expected"):
            probs.append(k)
    if not d.get("seeds_distinct", False): probs.append("씨앗 겹침")
    if probs or v.get("S_ON_blocked") is None:
        return None, f"막음 관문 문제 {probs}"
    R = v["rows"]
    # 교차: 행의 K_H 비로 다시 냄
    S2 = R["on_CO2@1.65"]["KH"] / R["on_N2@1.82"]["KH"]
    if abs(S2 - v["S_ON_blocked"]) > 1e-6 * max(1, S2):
        return None, f"S_ON_blocked 불일치 {S2} 대 {v['S_ON_blocked']}"
    return dict(S=v["S_ON_blocked"], Se=v["S_ON_blocked_err"]), None


def relax():
    d = load("results_e24g_relax300_hkhome.json", "relax")
    if d is None:
        return {}, "results_e24g_relax300_hkhome.json 없음"
    out = {}
    for t, r in (d.get("rows") or {}).items():
        a = r.get("after") or {}
        ed = r.get("final_EDiff")
        out[t] = dict(status=r.get("status"), PLD=a.get("PLD"), AV=a.get("AV_per_cell"), ED=ed, loops=r.get("outer_loops"),
                      conv=(ed is not None and ed < 1e-4))
    return out, None


def s_on(tag, ACC):
    """등록 규칙대로 쓸 S_ON(주머니 있으면 막음값). 반환 (dict|None, 사유)."""
    w, why = widom_on(f"results_magi5_e3_{tag}_widom_hkhome.json", "widom")
    if w is None:
        return None, f"Widom {why}"
    a = ACC.get(tag)
    if a is None:
        return None, "Zeo++ 미도착 — 주머니 여부 모름(막음값 필요 여부 미정)"
    if not a.get("ok"):
        return None, f"Zeo++ 관문 문제 {a}"
    if a.get("ch165") == 0:
        # 1.65 Å 에서 열린 통로 0 — 막으면 CO₂ 가 들어갈 곳이 없어 S_ON 이 정의되지 않음(CF₃: PLD 3.19 · 통로 0 · 주머니 10)
        return None, f"CO₂ 탐침 통로 0(PLD {a['PLD']}) — S_ON 정의 불가 → 후속 제외"
    pockets = (a["pk165"] or 0) + (a["pk182"] or 0)
    if pockets > 0:
        b, why = blocked(tag)
        if b is None:
            return None, f"주머니 {a['pk165']}·{a['pk182']} → 막음값 필요 · {why}"
        return dict(S=b["S"], Se=b["Se"], src=f"막음(주머니 {a['pk165']}·{a['pk182']}) · 차단 없음 {w['S']:.2f}"), None
    return dict(S=w["S"], Se=w["Se"], src="차단 없음(주머니 0)", G=w["G"], S_off=w["S_off"]), None


# ---------------------------------------------------------------- 판정량
def main():
    say("# E-24g · E-24h 판정 준비 — 등록 §HKHOME 21차 문구 그대로, 자료 완비 전 판정량 없음")
    say(f"ref: {REFS or '작업 트리'} · 기준(원자료) Cl {REF['Cl']['S']:.2f} ± {REF['Cl']['Se']:.2f} · CN {REF['CN']['S']:.2f} ± {REF['CN']['Se']:.2f} · 모체 {REF['모체']['S']:.2f} ± {REF['모체']['Se']:.2f}")
    G0 = gate0()
    ACC, acc_why = access()
    RLX, rlx_why = relax()
    say(f"(0) 관문 통과: {[t for t in ALL if G0.get(t)]} · 탈락: {[t for t in ALL if G0.get(t) is False]} · 모름: {[t for t in ALL if G0.get(t) is None]}")
    if acc_why: say(f"Zeo++: {acc_why}")
    if rlx_why: say(f"UFF4MOF: {rlx_why}")

    # (1) Br 대 Cl
    say("\n## (1) −Br 100: S_ON ≥ Cl + 1.5 단위")
    if not G0.get("e24g_br_100"):
        say("  (0) 탈락 또는 미정 — 판정 대상 아님")
    else:
        s, why = s_on("e24g_br_100", ACC)
        if s is None:
            say(f"  미완비: {why}")
        else:
            x = u(s["S"] - REF["Cl"]["S"], s["Se"], REF["Cl"]["Se"])
            say(f"  Br {s['S']:.2f} ± {s['Se']:.2f} [{s['src']}] − Cl → {x:+.2f} 단위 → **{'성립' if x >= TH else '기각'}**"
                f"{'' if x >= TH else ' → 판정의 뜻: 할로젠 계열에서 Cl 최선'}")
            say("  ⚠ Br 은 관문(0) 이종–H 1.801(문턱 1.8 을 0.001 Å) — 경계 통과 표지")

    # (2a)(2b) C≡CH
    say("\n## (2a)(2b) −C≡CH")
    say("  (0) 탈락 → 판정 대상 없음" if G0.get("e24g_cch_100") is False else "  (0) 통과 — 이 스크립트는 (2a)(2b) 계산을 넣지 않음(등록 (0) 판정상 대상 없음이었음) — 확인 필요")

    # (3) CF3 · n-C3H7
    say("\n## (3) −CF₃ · −n-C₃H₇ 중 하나 이상 (0) 탈락 또는 1.65 Å 통로 < 4")
    hit = [t for t in ("e24g_cf3_100", "e24g_nc3h7_100") if G0.get(t) is False]
    ch = {t: (ACC.get(t) or {}).get("ch165") for t in ("e24g_cf3_100", "e24g_nc3h7_100")}
    if hit:
        say(f"  (0) 탈락 {hit} → **성립**(등록 '적어도 하나') · 서술: 1.65 통로 {ch}")
    elif all(v is not None for v in ch.values()):
        say(f"  통로 {ch} → **{'성립' if any(v < 4 for v in ch.values()) else '기각'}**")
    else:
        say(f"  미완비: 통로 {ch}")

    # (4a) C2H5 50 % 통로 4 · 주머니 0
    say("\n## (4a) −C₂H₅ 50 %: 두 실현 모두 1.65 Å 통로 4 · 주머니 0")
    rows = {t: ACC.get(t) for t in HALF_C2H5}
    if any(v is None or not v.get("ok") for v in rows.values()):
        say("  미완비: Zeo++ ok " + str({t: (v or {}).get("ok") for t, v in rows.items()}))
    else:
        each = {t: (v["ch165"], v["pk165"]) for t, v in rows.items()}
        ok = all(c == 4 and p == 0 for c, p in each.values())
        say(f"  (통로, 주머니)@1.65 {each} → **{'성립' if ok else '기각'}**{'' if ok else ' → 판정의 뜻: C₂H₅ 의 주머니는 희석으로 안 풀림'}")

    # (4b) C2H5 50 % S_ON ≥ 모체 + 1.5
    say("\n## (4b) −C₂H₅ 50 %: 두 실현 모두 S_ON ≥ 모체 + 1.5 단위")
    vals = {t: s_on(t, ACC) for t in HALF_C2H5}
    if any(v[0] is None for v in vals.values()):
        say(f"  미완비: {{{', '.join(f'{t}: {v[1]}' for t, v in vals.items() if v[0] is None)}}}")
    else:
        xs = {t: u(v[0]['S'] - REF['모체']['S'], v[0]['Se'], REF['모체']['Se']) for t, v in vals.items()}
        say("  " + " · ".join(f"{t} {vals[t][0]['S']:.2f} ± {vals[t][0]['Se']:.2f} [{vals[t][0]['src']}] → {x:+.2f}" for t, x in xs.items()))
        say(f"  → **{'성립' if all(x >= TH for x in xs.values()) else '기각'}**")

    # (4c) Cl 50 % UFF4MOF 수렴에서 열림
    say("\n## (4c) −Cl 50 %: UFF4MOF 수렴(EDiff < 1e-4, 상한 300)에서 두 실현 모두 열림(PLD ≥ 3.64 · AV > 0)")
    rr = {t: RLX.get(t) for t in HALF_CL}
    if any(v is None or v["status"] != "ok" or v["PLD"] is None or v["AV"] is None for v in rr.values()):
        say("  미완비: UFF4MOF status " + str({t: (v or {}).get("status") for t, v in rr.items()}))
    else:
        br = {}
        for t, v in rr.items():
            if not v["conv"]:
                br[t] = "판정 불가(수렴 못 함)"
            else:
                br[t] = "열림" if (v["PLD"] >= PLD_MIN and v["AV"] > 0) else "닫힘"
            say(f"  {t}: PLD {v['PLD']:.3f} · AV/셀 {v['AV']} · 루프 {v['loops']} · EDiff {v['ED']:.3g} → {br[t]}")
        if any(b == "닫힘" for b in br.values()):
            verdict = "기각"
        elif all(b == "열림" for b in br.values()):
            verdict = "성립"
        else:
            verdict = "판정 불가(수렴 못 한 실현 있음 — 등록 문구)"
        say(f"  → **{verdict}**")

    # 후속 조건
    say("\n## 후속(S_mix 3씨앗 + 물 4씨앗 + UFF4MOF 상한 300) 진입 조건 — 등록 '판정의 뜻'")
    for t in ("e24g_br_100", "e24g_cf3_100"):
        if not G0.get(t):
            say(f"  {t}: (0) 탈락 · 대상 아님"); continue
        s, why = s_on(t, ACC)
        if s is None:
            say(f"  {t}: " + (f"**제외** — {why}" if "통로 0" in why else f"미완비 — {why}")); continue
        x = u(s["S"] - REF["Cl"]["S"], s["Se"], REF["Cl"]["Se"])
        say(f"  {t}: S_ON {s['S']:.2f} ± {s['Se']:.2f} [{s['src']}] − Cl → {x:+.2f} → **{'진입' if x > -TH else '제외'}**(100 %: Cl 보다 1.5 단위 넘게 낮지 않을 것)"
            + (" ⚠ CF₃ F···O 1.709 Å 표지 — 헤드라인 편입 전 UFF4MOF 에서 접촉 확인(판정 줄)" if t == "e24g_cf3_100" else ""))
    for t in HALF_C2H5 + HALF_CL:
        if not G0.get(t):
            say(f"  {t}: (0) 탈락 · 대상 아님"); continue
        s, why = s_on(t, ACC)
        v = RLX.get(t)
        parts = []
        if s is None:
            parts.append(f"S_ON 미완비 — {why}")
        if v is None or v.get("status") != "ok" or v.get("PLD") is None:
            parts.append("UFF4MOF 미완비")
        if parts:
            say(f"  {t}: " + " · ".join(parts)); continue
        x = u(s["S"] - REF["CN"]["S"], s["Se"], REF["CN"]["Se"])
        opened = v["conv"] and v["PLD"] >= PLD_MIN and v["AV"] > 0
        cond = opened and x > -TH
        say(f"  {t}: UFF4MOF {'수렴' if v['conv'] else '미수렴'} · PLD {v['PLD']:.3f} · AV {v['AV']} → {'열림' if opened else '열림 아님'} · "
            f"S_ON {s['S']:.2f} − CN → {x:+.2f} → **{'진입' if cond else '제외'}**(50 %: UFF4MOF 수렴에서 열림 + CN 보다 1.5 단위 넘게 낮지 않을 것)")
    say("\n(판정 뜻 요약 — 등록) 후속을 거친 후보는 E-23 최종 1위 규칙(S_mix → 물 지수 → 공동)으로 전체 목록 편입 · 헤드라인은 그 규칙으로만 바뀜.")


if __name__ == "__main__":
    main()
