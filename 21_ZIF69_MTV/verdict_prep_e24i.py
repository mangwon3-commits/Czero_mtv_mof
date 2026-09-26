#!/usr/bin/env python3
"""E-24i 판정 준비(클라우드 검증석 cloud 3차 ③) — 등록 `ASSIGN_MAGI5B_20260925.md` §HKHOME 22차(43ec8edc) 문구만으로.
자료 완비 전에는 판정량을 찍지 않음(진행표만). 기준값은 원자료에서 읽음. 표준 파이썬만.

  (0a)(0b) 서술 관문: 둘 다 넘는 후보만 (1)~(3) 에. (0b) 는 `gate0b_check.py`(독립 구현)로 다시 냄.
  (0b') 다섯 모두 (0b) 통과.
  (1) 적어도 하나가 S_ON ≥ 모체(87.80 ± 1.22) + 1.5 단위 — S_ON 은 주머니 있으면 막음값.
  후속 조건(판정의 뜻): S_ON(주머니 있으면 막음값) ≥ 모체 + 1.5 단위.
  (2) E-23 규칙 1위 후보(열린 자리 계열 안 — 후속을 거친 후보)의 S_mix ≥ 모체 75.4(±̄/√3 2.1) + 1.5 단위(±̄/√3 합성).
      E-23 규칙: ① S_mix 에서 누구에게도 1.5 단위 넘게 지지 않는 후보군 → ② 물 지수(낮을수록 위) 1.5 단위 → ③ 공동.

  python verdict_prep_e24i.py [--ref widom=origin/master --ref access=origin/junseok-20260822 ...]
      키: widom · access · bp · mix · water (가지 최종판 직접 집기 — 파일 이름은 글롭)
"""
import glob, json, math, os, statistics as st, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
FF = "8e8ec933f9013c7e932da04dc256efd3"
TAGS = ["e24i_ch3_open", "e24i_cl_open", "e24i_br_open", "e24i_c2h5_open", "e24i_cn_open"]
TH = 1.5
REFS = {}
for i, a in enumerate(sys.argv):
    if a == "--ref":
        k, v = sys.argv[i + 1].split("=", 1)
        REFS[k] = v


def files(pattern, key):
    """패턴에 맞는 파일 이름 → 내용. --ref 가 있으면 그 가지에서."""
    ref = REFS.get(key)
    out = {}
    if ref:
        ls = subprocess.run(["git", "ls-tree", "-r", "--name-only", ref, "21_ZIF69_MTV/"], cwd=HERE, capture_output=True, text=True).stdout.split()
        import fnmatch
        for p in ls:
            b = os.path.basename(p)
            if os.path.dirname(p) == "21_ZIF69_MTV" and fnmatch.fnmatch(b, pattern):
                txt = subprocess.run(["git", "show", f"{ref}:{p}"], cwd=HERE, capture_output=True, text=True).stdout
                try:
                    out[b] = json.loads(txt)
                except ValueError:
                    out[b] = None
    else:
        for p in glob.glob(os.path.join(HERE, pattern)):
            try:
                out[os.path.basename(p)] = json.load(open(p, encoding="utf-8"))
            except ValueError:
                out[os.path.basename(p)] = None
    return out


def u(d, *e):
    s = math.sqrt(sum(x * x for x in e))
    return d / s if s else float("inf")


def widom(d):
    if d is None:
        return None, "파일 읽기 실패"
    probs = []
    if not d.get("finished"): probs.append("finished 없음")
    if d.get("ff_md5") != FF: probs.append(f"ff_md5 {d.get('ff_md5')}")
    rows = {r["charges"]: r for r in d.get("rows", [])}
    for c in ("on", "off"):
        r = rows.get(c)
        if r is None:
            probs.append(f"{c} 행 없음"); continue
        if r.get("status_CO2") != "ok" or r.get("status_N2") != "ok":
            probs.append(f"{c} status {r.get('status_CO2')}/{r.get('status_N2')}")
    if probs:
        return None, "; ".join(probs)
    on, off = rows["on"], rows["off"]
    S2 = on["KH_CO2"] / on["KH_N2"]
    if abs(S2 - on["selectivity"]) > 1e-6 * S2:
        return None, f"S_ON 이 K_H 비와 다름 {S2} 대 {on['selectivity']}"
    return dict(S=on["selectivity"], Se=on["selectivity_err"], KH=on["KH_CO2"], KHe=on["KH_CO2_err"],
                S_off=off["selectivity"], G=on["selectivity"] / off["selectivity"]), None


# ---------------------------------------------------------------- 기준(원자료)
PAR_W, why = widom(json.load(open(os.path.join(HERE, "results_magi5_e3_e22_parent_widom_desktop-js1ib6u.json"))))
if PAR_W is None:
    sys.exit(f"모체 Widom 읽기 실패 {why}")
import final_crosscheck_e23 as F  # noqa: E402  (모체 S_mix 원자료: results_e23_mix_*)
PAR_MIX = dict(S=F.S["tpl"]["mean"], Se=F.S["tpl"]["pm"])
POCKET, BDEN = set(), {}   # 주머니 있는 태그 · 막음 분모 K_H(CO₂ ON @1.65)


def main():
    print(f"# E-24i 판정 준비 — 등록 §HKHOME 22차 문구 · 자료 완비 전 판정량 없음 · ref {REFS}")
    print(f"기준(원자료): 모체 S_ON {PAR_W['S']:.2f} ± {PAR_W['Se']:.2f} · 모체 S_mix {PAR_MIX['S']:.2f} ± {PAR_MIX['Se']:.2f}(±̄/√3)")
    # (0a)(0b)
    fit = (files("results_e24i_fit_*.json", "fit") or {})
    fitd = next(iter(fit.values()), None) or {}
    import gate0b_check as G  # noqa: E402
    from geom_e24h_symmetry_cf3 import read_cif, mat  # noqa: E402
    c0, X0 = read_cif(os.path.join(HERE, "e22_candidates", "E22_ZnDia_parent.cif"))
    M0 = mat(c0); ADJ0 = G.topo(M0, X0)
    g0 = {}
    print("\n## (0a) · (0b)")
    for t in TAGS:
        rp = os.path.join(HERE, "relax_tnf", t + "_relaxed.cif")
        bp = G.find_build(t)
        mine = G.gate(rp, bp, X0, M0, ADJ0) if (bp and os.path.exists(rp)) else None
        a = (fitd.get(t) or {}).get("gate0_pass")
        b_their = ((fitd.get(t) or {}).get("gate0b") or {}).get("pass_0b")
        b_mine = None if (mine is None or "error" in mine) else mine["passed"]
        g0[t] = (a is True) and (b_mine is True)
        print(f"  {t}: (0a) {a} · (0b) 검증석 {b_mine}(최악 {None if not mine or 'error' in mine else mine['worst']}) · 종합자 {b_their}"
              + ("" if b_mine == b_their else "  ⚠ 불일치"))
    print(f"  (0b') 다섯 모두 (0b) 통과 → **{'성립' if all(g0.values()) and len(g0) == 5 else ('기각' if any(v is False for v in g0.values()) else '미완비')}**")
    # Widom
    W = {}
    wf = files("results_magi5_e3_e24i_*_widom_*.json", "widom")
    for t in TAGS:
        c = [d for n, d in wf.items() if n.startswith(f"results_magi5_e3_{t}_widom_")]
        W[t] = widom(c[0]) if len(c) == 1 else (None, "파일 없음" if not c else f"파일 {len(c)}개 — 정본 지정 필요")
    # Zeo++ (주머니)
    acc = {}
    for n, d in files("results_e24i_access_*.json", "access").items():
        for r in (d or {}).get("rows", []):
            try:
                acc[r["tag"]] = dict(ch=r["r1.65"]["chan"].get("n_channels_chanfile"), pk165=r["r1.65"]["block"].get("pockets"),
                                     pk182=r["r1.82"]["block"].get("pockets"), PLD=r.get("PLD_Df"))
            except (KeyError, TypeError):
                acc[r.get("tag")] = None
    bpf = files("results_e24i_blockpockets_*.json", "bp")
    print("\n## (1) · 후속 조건 — S_ON(주머니 있으면 막음값) ≥ 모체 + 1.5 단위")
    son, xs = {}, {}
    global POCKET, BDEN
    for t in TAGS:
        w, why = W[t]
        a = acc.get(t)
        if w is None:
            print(f"  {t}: Widom 미완비 — {why}"); continue
        if a is None:
            print(f"  {t}: 차단 없는 S_ON {w['S']:.2f} ± {w['Se']:.2f}(서술) · Zeo++ 미도착 — 주머니 여부 모름 → 판정량 보류"); continue
        if a.get("ch") == 0:
            print(f"  {t}: CO₂ 탐침 통로 0 → S_ON 정의 불가(제외)"); continue
        if (a.get("pk165") or 0) + (a.get("pk182") or 0) > 0:
            POCKET.add(t)
            v, bwhy = None, "막음 Widom 미도착"
            for n, d in bpf.items():
                s = ((d or {}).get("per_structure") or {}).get(t)
                if not s or s.get("S_ON_blocked") is None:
                    continue
                R = s.get("rows") or {}
                bad = [k for k, r in R.items() if r.get("status") != "ok" or r.get("returncode") != 0 or not r.get("marker_finished")
                       or not r.get("pockets_blocked_line") or r.get("n_blocked_reported") != r.get("n_expected") or r.get("stderr_not_found")]
                if bad or not d.get("seeds_distinct") or not d.get("finished"):
                    bwhy = f"막음 관문 문제 {bad} · 씨앗 고유 {d.get('seeds_distinct')} · finished {d.get('finished')}"; continue
                S2 = R["on_CO2@1.65"]["KH"] / R["on_N2@1.82"]["KH"]
                if abs(S2 - s["S_ON_blocked"]) > 1e-6 * S2:
                    bwhy = f"막음 S_ON 이 K_H 비와 다름 {S2}"; continue
                v = dict(S=s["S_ON_blocked"], Se=s["S_ON_blocked_err"], src=f"막음 · {n} · 막음 수 {R['on_CO2@1.65'].get('n_blocked_reported')}={R['on_CO2@1.65'].get('n_expected')}")
                BDEN[t] = (R["on_CO2@1.65"]["KH"], R["on_CO2@1.65"]["KH_err"])
            if v is None:
                print(f"  {t}: 주머니 {a.get('pk165')}·{a.get('pk182')} — {bwhy}(차단 없는 {w['S']:.2f} 는 서술)"); continue
        else:
            v = dict(S=w["S"], Se=w["Se"], src="차단 없음(주머니 0)")
        x = u(v["S"] - PAR_W["S"], v["Se"], PAR_W["Se"])
        son[t], xs[t] = v, x
        print(f"  {t}: S_ON {v['S']:.2f} ± {v['Se']:.2f} [{v['src']}] − 모체 → {x:+.2f} 단위 → 후속 **{'진입' if x >= TH else '제외'}** · G {w['G']:.3f} · S_OFF {w['S_off']:.1f}")
    if len(son) == 5 or (xs and any(x >= TH for x in xs.values())):
        print(f"  → (1) **{'성립' if any(x >= TH for x in xs.values()) else '기각'}**" + ("" if len(son) == 5 else " (한 후보 이상으로 이미 성립 — 나머지 미완비)"))
    else:
        print("  → (1) 미완비")
    # (2) 후속 S_mix · 물 지수 → E-23 규칙
    mixf = files("results_e24i_*_mix_*.json", "mix")
    watf = files("results_e24i*water*.json", "water")
    MIX, WAT = {}, {}
    for t in TAGS:
        c = [d for n, d in mixf.items() if n.startswith(f"results_e24i_{t}_mix_")]
        if len(c) == 1 and c[0]:
            rows = [r for r in c[0].get("rows", []) if r.get("status") == "ok"]
            if t in POCKET:
                rows = [r for r in rows if all(((r.get("block") or {}).get(g) or {}).get("n_blocked") == (r.get("n_expected") or {}).get(g)
                                               and ((r.get("block") or {}).get(g) or {}).get("blocked_line") for g in ("CO2", "N2"))]
            elif any(r.get("block") for r in rows):
                rows = []   # 주머니 0 인데 막음 실행 — 자가 다름
            if len(rows) == 3 and len({r.get("seed") for r in rows}) == 3:
                s = [r["N_CO2"] / r["N_N2"] * (0.85 / 0.15) for r in rows]
                e = [x * math.hypot(r["N_CO2_err"] / r["N_CO2"], r["N_N2_err"] / r["N_N2"]) for x, r in zip(s, rows)]
                MIX[t] = dict(S=st.mean(s), Se=st.mean(e) / math.sqrt(3), sd=st.stdev(s))
        for n, d in watf.items():
            if t in POCKET:
                # 주머니 있음: 등록 보완(27f32f80) — 물 K_H 는 막음 1.30 · 4씨앗, 분모는 막음 K_H(CO₂ ON @1.65)
                rows = [r for r in (d or {}).get("rows", []) if n.startswith(f"results_e24i_{t}_water_") and r.get("status") == "ok"
                        and abs((r.get("block_radius") or 0) - 1.30) < 1e-6 and r.get("marker_finished")
                        and (r.get("block") or {}).get("n_blocked") == r.get("n_expected")]
                den = BDEN.get(t)
            else:
                rows = [r for r in (d or {}).get("rows", []) if r.get("name") in (t, t + "_DDEC6") and r.get("status") == "ok"
                        and not n.startswith(f"results_e24i_{t}_water_")]
                den = (W[t][0]["KH"], W[t][0]["KHe"]) if W[t][0] is not None else None
            if len(rows) == 4 and den is not None and len({r.get("seed") for r in rows}) == 4:
                k = [r["KH_water"] for r in rows]; ke = [r["KH_water_err"] for r in rows]
                m, me = st.mean(k), st.mean(ke) / 2
                i = m / den[0]
                WAT[t] = dict(idx=i, err=i * math.hypot(me / m, den[1] / den[0]), src=n + (" (막음 1.30 ÷ 막음 분모)" if t in POCKET else " (차단 없음)"))
    print("\n## (2) E-23 규칙 1위(후속 거친 후보) S_mix ≥ 모체 + 1.5 단위")
    fam = [t for t in TAGS if xs.get(t, -9) >= TH]
    if not fam:
        print("  후속 진입 후보 미정(또는 없음) — (1) 뒤"); return
    miss = [t for t in fam if t not in MIX or t not in WAT]
    for t in fam:
        print(f"  {t}: S_mix {('%.2f ± %.2f (SD %.2f)' % (MIX[t]['S'], MIX[t]['Se'], MIX[t]['sd'])) if t in MIX else '미완비'} · "
              f"물 지수 {('%.5f ± %.5f [%s]' % (WAT[t]['idx'], WAT[t]['err'], WAT[t]['src'])) if t in WAT else '미완비'}")
    if miss:
        print(f"  미완비 {miss} — 판정량 보류"); return
    cand = [a for a in fam if all(u(MIX[a]["S"] - MIX[b]["S"], MIX[a]["Se"], MIX[b]["Se"]) > -TH for b in fam if b != a)]
    cand.sort(key=lambda t: WAT[t]["idx"])
    top = [cand[0]] + [t for t in cand[1:] if abs(u(WAT[t]["idx"] - WAT[cand[0]]["idx"], WAT[t]["err"], WAT[cand[0]]["err"])) < TH]
    print(f"  ① 1위 후보군 {cand} → ② 물 지수 → 1위 {top}{' (③ 공동)' if len(top) > 1 else ''}")
    for t in top:
        x = u(MIX[t]["S"] - PAR_MIX["S"], MIX[t]["Se"], PAR_MIX["Se"])
        print(f"  {t}: S_mix {MIX[t]['S']:.2f} − 모체 {PAR_MIX['S']:.2f} → {x:+.2f} 단위 → (2) **{'성립 — 확장 설계 살아남음' if x >= TH else '기각 — 확장 설계 철회'}**")


if __name__ == "__main__":
    main()
