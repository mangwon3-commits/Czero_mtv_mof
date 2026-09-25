#!/usr/bin/env python3
"""남은 네 시험(E-26 · E-27 · E-28 · E-29) 마감 검사 — 2026-09-26 클라우드 세션(종합자 HKHOME 보조).

등록(ASSIGN_MAGI5B_20260925.md, 전부 자료 0건 시점)의 예측을 **등록 문구 그대로** 코드로 옮겼다.
설계 규칙: **자료가 다 차기 전에는 판정량을 한 개도 찍지 않는다** — 진행표와 표지 문제만 낸다
(부분 자료의 값을 먼저 보면 규칙을 자료에 맞추게 된다 — SESSION_LOG 09-24 15:15 규칙).
판정문은 종합자가 쓴다. 이 스크립트는 판정 가지와 그 가지의 "판정의 뜻"(등록에 미리 적힌 것)만 보인다.

  python final_close_check.py                     # 작업 트리 파일로
  python final_close_check.py --ref E27=origin/laptop-20260822 --ref E29=origin/junseok-20260822
      # 가지 최종판을 직접 집어 판정(postman 이 실행 중 스냅숏을 master 에 반입하는 문제 — COMMS/desktop 09-25 16:39)

단위 규약(CLAUDE.md §2): RASPA ± 는 95 % CI 그대로, "단위" = d / √(±₁² + ±₂²). 3씨앗 평균의 ± = ±̄/√3.
"""
import json, math, os, statistics as st, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
FF = "8e8ec933f9013c7e932da04dc256efd3"
REFS = {}
for i, a in enumerate(sys.argv):
    if a == "--ref":
        k, v = sys.argv[i + 1].split("=", 1)
        REFS[k] = v


def load(rel, test=None):
    """작업 트리 또는 --ref 로 준 가지에서 JSON 을 읽는다. 없으면 None."""
    ref = REFS.get(test) if test else None
    if ref:
        cp = subprocess.run(["git", "show", f"{ref}:21_ZIF69_MTV/{rel}"], cwd=HERE,
                            capture_output=True, text=True)
        return json.loads(cp.stdout) if cp.returncode == 0 else None
    p = os.path.join(HERE, rel)
    return json.load(open(p)) if os.path.exists(p) else None


def u(d, *errs):
    return d / math.sqrt(sum(e * e for e in errs))


def branch3(x, hi="성립", lo="기각", mid="띠"):
    return hi if x >= 1.5 else (lo if x <= -1.5 else mid)


# ------------------------------------------------------------------ 298 K 기준값(E-23 · E-25 원자료)
def mixrows(p):
    return {r["name"]: r for r in load(p)["rows"]}

def mean3(rows, stem):
    rs = [rows[f"{stem}_s{i}"] for i in (1, 2, 3)]
    return st.mean(r["S_mix"] for r in rs), st.mean(r["S_mix_err"] for r in rs) / math.sqrt(3)

def humid_rows(d):
    return {r["name"]: r for r in d["rows"]}

def humid_stats(d, stem):
    """3씨앗(h1~h3) — WC_TSA 평균 · ±̄/√3 · 씨앗 SD · RH90 물 적재 평균 · CO₂ ads 평균."""
    R = humid_rows(d)
    rs = [R.get(f"{stem}_h{i}") for i in (1, 2, 3)]
    if any(r is None for r in rs):
        return None, f"행 {sum(r is not None for r in rs)}/3"
    for r in rs:
        L = r.get("loadings", {})
        for stg in ("ads", "tsa", "vsa"):
            for comp in ("CO2", "water"):
                if (L.get(stg, {}).get(comp) or {}).get("mol_per_kg") is None:
                    return None, f"{r['name']} {stg} {comp} 없음"
        if (r.get("working_capacity", {}).get("tsa") or {}).get("value") is None:
            return None, f"{r['name']} WC_TSA 없음"
    wc = [r["working_capacity"]["tsa"]["value"] for r in rs]
    wce = [r["working_capacity"]["tsa"]["err"] for r in rs]
    return dict(wc=st.mean(wc), wc_pm=st.mean(wce) / math.sqrt(3), wc_sd=st.stdev(wc),
                wc_vsa=st.mean(r["working_capacity"]["vsa"]["value"] for r in rs),
                water_ads=st.mean(r["loadings"]["ads"]["water"]["mol_per_kg"] for r in rs),
                co2_ads=st.mean(r["loadings"]["ads"]["CO2"]["mol_per_kg"] for r in rs),
                co2_ads_pm=st.mean(r["loadings"]["ads"]["CO2"]["err"] for r in rs) / math.sqrt(3)), None


OUT = []
def say(s=""): OUT.append(s); print(s)


# ------------------------------------------------------------------ E-26
def e26():
    say("## E-26 — 형판-4,8-(CN)₂ 습윤 TSA 작업 용량 (laptop2 10차)")
    d = load("v3w_humid_wc/humid_working_capacity_w2_e24cn_laptop2.json", "E26")
    if d is None:
        say("  자료 없음 — `v3w_humid_wc/humid_working_capacity_w2_e24cn_laptop2.json` 미도착(판정 없음)"); return
    cn, why = humid_stats(d, "e24_cn_100")
    if cn is None:
        say(f"  미완비: {why} — 판정량 안 찍음"); return
    tpl, _ = humid_stats(load("v3w_humid_wc/humid_working_capacity_w2_e22parent_laptop.json"), "e22_parent")
    say("  ⚠ 판정 전 관문은 **실행 폴더**에서만 확인됨(JSON 에 표지 열 없음): 9출력 씨앗 고유 · 'Simulation finished' · "
        "e25_returncode.txt = 0 — laptop2 확인 줄이 있어야 아래를 판정으로 씀")
    x = u(cn["wc"] - tpl["wc"], cn["wc_pm"], tpl["wc_pm"])
    say(f"  (1) WC_TSA CN {cn['wc']:.3f} (±̄/√3 {cn['wc_pm']:.3f} · 씨앗 SD {cn['wc_sd']:.3f}) 대 모체 {tpl['wc']:.3f} "
        f"(±̄/√3 {tpl['wc_pm']:.3f} · SD {tpl['wc_sd']:.3f}) → {x:+.2f} 단위 — **{branch3(x)}**")
    say(f"  (2) 서술: RH90 흡착 단계 물 CN {cn['water_ads']:.4f} 대 모체 {tpl['water_ads']:.4f} mol/kg "
        f"(비 {cn['water_ads']/tpl['water_ads']:.2f}) · WC_VSA CN {cn['wc_vsa']:.3f} 대 {tpl['wc_vsa']:.3f}")
    ch3, _ = humid_stats(load("v3w_humid_wc/humid_working_capacity_w2_e24ch3_laptop.json"), "e24_ch3_100")
    if ch3:
        say(f"  (서술 병기) CH₃ {ch3['wc']:.3f} — CN − CH₃ {u(cn['wc']-ch3['wc'], cn['wc_pm'], ch3['wc_pm']):+.2f} 단위")


# ------------------------------------------------------------------ E-27
def e27():
    say("## E-27 — 결승 후보 작동점 S_mix 323 K (laptop 9차)")
    d = load("results_e27_mix323_laptop.json", "E27")
    if d is None:
        say("  자료 없음"); return
    rows = d["rows"]
    n_ok = sum(r.get("status") == "ok" for r in rows)
    say(f"  진행 {n_ok}/{len(rows)} ok · 파일 note: {d.get('note','')[-40:]}")
    probs = []
    if d.get("protocol", {}).get("T_K") != 323.0: probs.append(f"protocol T_K={d.get('protocol',{}).get('T_K')}")
    for r in rows:
        if r.get("status") != "ok": probs.append(f"{r['name']} {r.get('status')}"); continue
        if r.get("returncode") != 0: probs.append(f"{r['name']} rc={r.get('returncode')}")
        if not r.get("finished"): probs.append(f"{r['name']} finished 없음")
        if r.get("ff_md5") != FF: probs.append(f"{r['name']} ff_md5")
    seeds = [r.get("seed") for r in rows if r.get("seed") is not None]
    if len(seeds) != len(set(seeds)): probs.append("씨앗 겹침")
    if n_ok < len(rows) or len(rows) != 11 or probs:
        say(f"  미완비 또는 표지 문제 — 판정량 안 찍음: {probs[:6]}{' …' if len(probs) > 6 else ''}"); return
    R = {r["name"]: r for r in rows}
    m = {s: mean3(R, s) for s in ("e22_parent", "e24_cn_100", "e24_ch3_100")}
    say("  (1) 323 K 에서 CN · CH₃ 가 각각 모체 + 1.5 단위(±̄/√3 합성) 넘게 위:")
    ok1 = True
    for s in ("e24_cn_100", "e24_ch3_100"):
        x = u(m[s][0] - m["e22_parent"][0], m[s][1], m["e22_parent"][1])
        ok1 &= x > 1.5
        say(f"      {s} {m[s][0]:.2f} ± {m[s][1]:.2f} − 모체 {m['e22_parent'][0]:.2f} ± {m['e22_parent'][1]:.2f} = {x:+.2f} 단위")
    say(f"      → **{'성립' if ok1 else '기각'}**(등록: 어느 하나라도 1.5 단위 안이거나 아래면 기각)")
    say("  (2) 모체 S_mix(323) 가 ZIF e0 둘 모두보다 1.5 단위 넘게 위:")
    ok2 = True
    for z in ("mslm050", "saIm050"):
        x = u(m["e22_parent"][0] - R[z]["S_mix"], m["e22_parent"][1], R[z]["S_mix_err"])
        ok2 &= x > 1.5
        say(f"      모체 − {z} {R[z]['S_mix']:.2f} ± {R[z]['S_mix_err']:.2f} = {x:+.2f} 단위")
    say(f"      → **{'성립' if ok2 else '기각'}**")
    # (3) 서술 — 298 K 기준: 형판 계열 = E-23/E-24 3씨앗 평균 · ZIF = e0(T-J1′ s1 + E-21b s2·s3 평균)
    d23 = mixrows("results_e23_mix_desktop.json"); d24 = mixrows("results_e24_mix_desktop.json")
    d24b = mixrows("results_e24b_mix_desktop.json"); tj = mixrows("results_tj1_mix_laptop.json")
    e21 = mixrows("results_e21b_mix_junseok.json")
    ref298 = {"e22_parent": mean3(d23, "e22_parent")[0], "e24_cn_100": mean3(d24, "e24_cn_100")[0],
              "e24_ch3_100": mean3(d24b, "e24_ch3_100")[0]}
    for z in ("mslm050", "saIm050"):
        ref298[z] = st.mean([tj[z]["S_mix"], e21[f"{z}_s2"]["S_mix"], e21[f"{z}_s3"]["S_mix"]])
    say("  (3) 서술 S_mix(323)/S_mix(298): " + " · ".join(
        f"{k} {(m[k][0] if k in m else R[k]['S_mix'])/v:.3f}" for k, v in ref298.items()))
    say("  ⚠ 이 파일 행의 `S_Henry` 는 **298 K** 값 — `ratio_Smix_over_SHenry` 열은 323/298 을 섞은 비이므로 인용 금지")


# ------------------------------------------------------------------ E-28
def e28():
    say("## E-28 — 형판 계열 건조 · 습윤 밀도 격자 (HKHOME 15차)")
    # (2) 건조: f = (L_on − L_off)/L_on
    dry = load("density_v3_tpl/density_results.json", "E28")
    need = ["e22_parent", "e24_ch3_100", "e24_cn_100"]
    if dry is None:
        say("  (2) 건조 자료 없음 — `density_v3_tpl/density_results.json` 미생성(러너가 10작업 다 끝난 뒤 한 번에 씀)")
    else:
        D = {r["name"]: r for r in dry}
        miss = [n for n in need if n not in D]
        if miss:
            say(f"  (2) 미완비: {miss} 행 없음(러너는 ON·OFF 둘 다 완주한 조성만 씀) — 판정량 안 찍음")
        else:
            F = {}
            for n in need:
                r = D[n]; on, oe, off, fe = r["loading_q_on"], r["loading_q_on_err"], r["loading_q_off"], r["loading_q_off_err"]
                f = (on - off) / on
                F[n] = (f, (off / on) * math.hypot(oe / on, fe / off))
            say("  (2) 정전기 몫 f = (L_on − L_off)/L_on (± 전파): " + " · ".join(f"{n} {F[n][0]:.3f} ± {F[n][1]:.3f}" for n in need))
            xs = {n: u(F["e22_parent"][0] - F[n][0], F["e22_parent"][1], F[n][1]) for n in ("e24_ch3_100", "e24_cn_100")}
            for n, x in xs.items():
                say(f"      f(모체) − f({n}) = {x:+.2f} 단위 — {branch3(x)}")
            allx = list(xs.values())
            verdict = "성립" if all(x >= 1.5 for x in allx) else ("기각" if any(x <= -1.5 for x in allx) else "띠")
            say(f"      → **{verdict}** (등록: 어느 하나라도 1.5 단위 넘게 반대면 기각 · 둘 다 1.5 넘게 순방향이면 성립 · 나머지 띠)")
            say("      ⚠ 0.15 bar 는 헨리 영역 밖 — 띠 · 기각은 '헨리 분해가 0.15 bar 로 안 옮겨짐' 의 증거로 읽음(등록 문구)")
    # (1) 습윤: 격자 실행 CO₂ 적재 대 습윤 WC ads 3씨앗 평균
    wet = {}
    # 1순위: 러너 자체 출력 density_water_v3w/tpl_<이름>/water_results.json(DW_SUB — 등록 E-28 덱) · status ok 만
    for n in need:
        dd = load(f"density_water_v3w/tpl_{n}/water_results.json", "E28") or {}
        r = (dd.get("rows") or {}).get(n)
        if r and r.get("status") == "ok" and r.get("CO2"):
            wet[n] = dict(r, src=f"tpl_{n}/water_results.json")
    # 2순위: extract_density_loadings.py 회수본 loadings_*.json
    dwd = os.path.join(HERE, "density_water_v3w")
    for fn in (sorted(os.listdir(dwd)) if os.path.isdir(dwd) else []):
        if fn.startswith("loadings_") and fn.endswith(".json"):
            dd = load(f"density_water_v3w/{fn}", "E28") or {}
            for k, v in dd.items():
                k2 = k.replace("tpl_", "")
                if k2 in need and k2 not in wet:
                    wet[k2] = dict(v, src=fn)
    wcfile = {"e22_parent": "humid_working_capacity_w2_e22parent_laptop.json",
              "e24_ch3_100": "humid_working_capacity_w2_e24ch3_laptop.json",
              "e24_cn_100": "humid_working_capacity_w2_e24cn_laptop2.json"}
    for n in need:
        if n not in wet:
            say(f"  (1) {n}: 습윤 격자 적재 없음(`density_water_v3w/loadings_*.json` — extract_density_loadings.py 회수 전)"); continue
        wcd = load(f"v3w_humid_wc/{wcfile[n]}", "E26" if n == "e24_cn_100" else None)
        hs, why = humid_stats(wcd, n) if wcd else (None, "WC 파일 없음")
        if hs is None:
            say(f"  (1) {n}: 비교 대상 WC ads 미완비({why})"); continue
        L, Le = wet[n]["CO2"]
        x = u(L - hs["co2_ads"], Le, hs["co2_ads_pm"])
        say(f"  (1) {n}: 격자 CO₂ {L:.3f} ± {Le:.3f} 대 WC ads {hs['co2_ads']:.3f} ± {hs['co2_ads_pm']:.3f} → {x:+.2f} 단위 — "
            f"**{'성립(같은 평형의 그림)' if abs(x) < 1.5 else '기각(이 격자를 WC 상태 그림으로 쓰지 않음)'}**")
    say("  금지(등록): 단일 복셀 자리 주장 · 물 격자로 물 자리 주장(적재 ≈ 0.03 mol/kg)")


# ------------------------------------------------------------------ E-29
def e29():
    say("## E-29 — CH₃ 통로 닫힘은 UFF4MOF 이완 수렴 뒤에도 남는가 (Junseok 15차)")
    d = load("results_e29_relax60_junseok.json", "E29")
    if d is None:
        say("  자료 없음 — Junseok 가지에서 `--ref E29=origin/junseok-20260822` 로 집어 올 것"); return
    rows = d["rows"]
    st_ = {k: v.get("status") for k, v in rows.items()}
    say(f"  진행: {st_}")
    if any(v != "ok" for v in st_.values()):
        say("  미완비 — 판정량 안 찍음"); return
    A = {k: (v.get("after") or {}) for k, v in rows.items()}
    ch = A["e24_ch3_100"]; pld, av = ch.get("PLD"), ch.get("AV_per_cell")
    if pld < 3.3 or av < 20: b1 = "성립"
    elif pld >= 3.64 and av > 20: b1 = "기각"
    else: b1 = "띠"
    say(f"  (1) CH₃ 처리 뒤 PLD {pld:.3f} · AV/셀 {av:.1f} · EDiff {rows['e24_ch3_100'].get('final_EDiff')} · 루프 {rows['e24_ch3_100'].get('outer_loops')} → **{b1}**")
    op = {}
    for t in ("e24_cn_100", "e22_parent"):
        a = A[t]; op[t] = a["PLD"] >= 3.64 and a["AV_per_cell"] > 20
        say(f"  (2) {t}: PLD {a['PLD']:.3f} · AV/셀 {a['AV_per_cell']:.1f} → {'열림' if op[t] else '닫힘'}")
    b2 = "성립" if all(op.values()) else "기각"
    say(f"      → (2) **{b2}**")
    conv = rows["e24_ch3_100"].get("final_EDiff")
    if conv is not None and conv > 1.0:
        say(f"  ⚠ CH₃ 최종 EDiff {conv} — 60 상한에서도 수렴 미달일 수 있음(진동) · 판정 전 표지로 병기")
    if b2 == "기각":
        mean = "처리 자체가 형판 통로를 닫음 → 검증자 표지 무효(CH₃ 만의 문제 아님)"
    elif b1 == "성립":
        mean = "헤드라인 = 「CH₃ 1위는 GFN-FF 고정셀 앞단 조건부 · 앞단에 강건한 설계 1위는 CN」 두 줄 병기(E-23 규칙 순위 불변)"
    elif b1 == "기각":
        mean = "헤드라인 = 「CH₃ 1위 — 두 앞단 모두 열림」"
    else:
        mean = "띠 — 등록의 '판정의 뜻' 에 띠 가지 문구 없음 → 종합자 결정 사항(두 줄 병기 유지가 보수 쪽)"
    say(f"  판정의 뜻(등록에 미리 적힌 것): {mean}")


if __name__ == "__main__":
    say("# 남은 네 시험 마감 검사 — 등록 예측 그대로, 자료 완비 전에는 판정량 없음")
    say(f"ref: {REFS or '작업 트리'}")
    for f in (e26, e27, e28, e29):
        say()
        try:
            f()
        except Exception as ex:   # 한 시험의 형식 문제가 나머지를 막지 않게
            say(f"  !! 검사 실패: {type(ex).__name__}: {ex}")
