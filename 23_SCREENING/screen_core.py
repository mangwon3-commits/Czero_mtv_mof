"""CoRE MOF 스크리닝 — `MOF_Screening.ipynb`(83셀) 정리본.

[무엇]
    CoRE MOF 메타데이터(`CR_meta_data_SI.json`)에서 기하·안정성·수분·Widom 값을 꺼내
    관문을 통과시키고, 우리 ZIF-69 조성(`21_ZIF69_MTV/results_v3.json`)을 같은 축에 얹습니다.

[왜 다시 썼나 — 원본 노트북의 결함 다섯]
    D1 위치 인덱스   `df.iloc[:, 9]` · `widom[0]/widom[1]`. 열 순서가 바뀌면 조용히 틀린 값이 나옵니다.
                     이 저장소는 같은 유형(부착 원자 고정 인덱스 4)으로 08-14 에 v1 치환 결과를 전량 폐기했습니다.
                     확인해 보니 `iloc[:, 9]` 는 **`water` 열**입니다(이름표는 `GEMC_data` 였음).
                     `water = {GEMC, water_classification, Widom}` 이라 값은 맞게 나왔고,
                     `[0]=CO2 · [1]=N2` 순서도 **크기로는 맞습니다**(`WIDOM_ORDER_EVIDENCE`).
                     그러나 **맞은 것과 확인된 것은 다릅니다** — 신판은 이 구조가 평평해져 같은 코드가 곧바로 깨집니다.
                     → 여기서는 **이름으로 찾고, 못 찾으면 예외를 냅니다.**
    D2 맨 except     `except:` 가 **97곳**(`except Exception` 은 별도 11곳) — **실패가 결측으로 보입니다**(CLAUDE.md §0 의 핵심 결함 유형).
                     → 여기서는 실패를 세어 `report()` 에 남기고, 조용히 0/NaN 으로 만들지 않습니다.
    D3 사후 문턱     3중 관문(stable & PLD≥3.3 & weak) → 0개 → 그 뒤에 PLD 창 3.3~3.6 / 3.7~4.2 를 만들고
                     다시 PLD≥3.4 · VF≥0.2 를 더했습니다. **자료를 본 뒤 문턱이 움직였습니다**(§2 위반).
                     → 여기서는 문턱을 `GATES` 한 곳에 모아 **출처(등록 문서/자료를 본 시점)를 같이 적습니다.**
    D4 오차 없음     Widom K_H 점값으로 순위를 매깁니다. 우리 `results_v3.json` 은 같은 양에 `*_err` 가 있습니다.
                     → `rank()` 는 오차 열이 있으면 **1.5배 규칙**(CLAUDE.md §2)을 적용하고, 없으면 "순위 없음" 으로 돌려줍니다.
    D5 임의 가중치   점수 0.6×선택도 + 0.4×용량, 상위 5 % 클리핑. 근거가 "정상 물질 점수가 바닥에 깔리는 것 방지" 였습니다.
                     → 점수화는 **선택 사항**으로 빼고 기본은 원자료 축(K_H, 선택도)을 그대로 씁니다.
    D6 항상 거짓 관문 (2026-09-20 추가 — 원본 zip 을 열고 나서야 잡힘, 가장 큰 것)
                     1순위 `node_stability == 'stable'` 이 **전 레코드에서 거짓**입니다. 그 필드에는 위상 기호
                     (pcu·dia·sql·unstable…)가 들어 있고 `'stable'` 이라는 값 자체가 CR 17,202 건 중 **0건**입니다.
                     원본이 본 "생존자 0명" 은 관문이 엄해서가 아니라 **관문이 성립하지 않아서**였습니다.
                     그 0 을 보고 관문을 버렸으므로, 뒤따른 63+52=115 종은 **안정성 검사를 한 번도 안 거쳤습니다**
                     (실제로 115 중 unstable 6 · mismatch 3 이 들어 있습니다).
                     → CLAUDE.md §0 "나쁜 결과를 보면 검사기부터 의심하라" 가 정확히 이 자리입니다.
                     → 고친 관문으로 다시 걸면 교집합 **6,604종**(위상 미상 통과) / **4,587종**(미상 탈락).
                       노트북의 실제 입력 `CR_meta_data_SI.json`(2,737)만 보면 **754종**입니다(원본 0종).
                       사후 창은 이 모듈이 그대로 재현합니다 — N2-Sieving 63 · High-Flux 52, 노트북 수치와 일치.
                     상세·검증 경로: `ZIP_FINDINGS_20260920.md`

사용:
    python3 screen_core.py --meta data/CR_meta_data_SI.json
    python3 screen_core.py --meta data/CR_meta_data_SI.json --ours ../21_ZIF69_MTV/results_v3.json
"""
import argparse
import collections
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))

# ---------------------------------------------------------------------------
# 문턱 — 한 곳에 모으고, 각각 어디서 왔는지 적습니다 (D3)
# ---------------------------------------------------------------------------
#
# ⚠ 1순위 관문은 2026-09-20 에 **고쳤습니다** — 원본은 항상 거짓이었습니다(D6).
#   `CrystalNets.all_nodes`(신판 `Topology.AllNode`)에 들어 있는 것은 **위상 기호**입니다:
#   unknown 6536 · pcu 1370 · dia 1149 · sql 1011 · unstable 342 · hcb 307 … 고유값 361종.
#   CR 전체 17,202 레코드에서 **`'stable'` 은 0건** — `== 'stable'` 은 통과자가 나올 수 없습니다.
#   (검증: CoRE-MOF-Tools-main.zip / CoREMOF/data/CR.json, ASR+FSR+Ion. ZIP_FINDINGS_20260920.md §3)
#   그래서 "안정" 은 **"unstable/mismatch 가 아님"** 으로 읽습니다.
NODE_BAD = ("unstable", "mismatch")      # 뼈대 판정이 실패했다고 CoRE 가 표시한 값
NODE_UNKNOWN = ("unknown", "unnamed")    # 위상을 못 붙인 것 — 통과/탈락을 **선택**해야 하는 자리

GATES = {
    "node_not_unstable": dict(
        value=NODE_BAD, field="CrystalNets.all_nodes | Topology.AllNode",
        unknown_passes=True,
        source="원본 노트북 1순위를 고친 것(2026-09-20). 원본 `== 'stable'` 은 전 레코드에서 거짓.",
        caveat="`unknown/unnamed` 이 CR 의 38 % 입니다. 통과시키면 교집합 6,604 · 탈락시키면 4,587 — "
               "**어느 쪽을 쓸지 먼저 등록하십시오.** 여기 기본값(통과)은 등록이 아니라 기본값입니다."),
    "PLD_min": dict(
        value=3.3, field="Zeopp.PLD",
        source="원본 노트북 2순위. CO2 운동 지름 3.3 Å.",
        caveat="우리 자료로 반증됨 — MUF-16 은 PLD 3.143 · CO2 탐침 AV 0 인데 "
               "건조 CO2 1.117 mol/kg(모체 0.5839 의 1.9배). "
               "21_ZIF69_MTV/TNF_RESULTS_20260910.md ㉣. 이 관문은 **위상 안에서만** 유효."),
    "water_weak": dict(
        value="weak", field="water.water_classification",
        source="원본 노트북 3순위. CoRE 제공 분류."),
}
# 아래 둘은 **자료를 본 뒤** 만들어진 창입니다. 기술(description)이지 설계 목표가 아닙니다.
WINDOWS_POST_HOC = {
    "N2_sieving": dict(PLD=(3.3, 3.6),
                       note="원본 '매직 윈도우'. 3중 관문이 0개를 낸 뒤 만들어짐."),
    "high_flux": dict(PLD=(3.7, 4.2), LCD_min=5.5,
                      note="원본 '호리병'. 같은 시점에 만들어짐."),
}


class Missing(Exception):
    """필드를 이름으로 못 찾았을 때 — 조용히 넘기지 않습니다 (D1·D2)."""


def dig(rec, path, *, required=True, default=None):
    """`'Zeopp.PLD'` 처럼 **이름으로** 판다. 위치 인덱스를 쓰지 않습니다."""
    cur = rec
    for part in path.split("."):
        if not isinstance(cur, dict) or part not in cur:
            if required:
                raise Missing(path)
            return default
        cur = cur[part]
    return cur


def first_of(rec, paths, *, default=None):
    """스키마가 두 판입니다 — **둘 다 이름으로** 시도하고 먼저 맞는 것을 씁니다.

    옛 판 `CR_meta_data_SI.json`: `Zeopp.PLD` · `CrystalNets.all_nodes` · `water.water_classification`
    신 판 `CoREMOF/data/CR.json`: `PLD`(평평) · `Topology.AllNode` · `WaterClass`
    (신판은 CoRE-MOF-Tools-main.zip 안에 있습니다. 위치가 아니라 이름이 바뀐 것이므로 별칭으로 흡수합니다.)
    """
    for p in paths:
        v = dig(rec, p, required=False, default=None)
        if v is not None:
            return v
    return default


# Widom K_H 가 이 값을 넘으면 **삽입이 발산한 것**으로 봅니다(물리적으로 불가능한 크기).
# CR 실측: ASR 최대 1.877e+22 mmol/g/Pa. 1 Pa 에서 1e22 mol/kg 은 뜻이 없습니다.
# 원본 노트북은 이 행들을 거르지 않고 순위에 넣었습니다. 문턱 자체는 **자료를 보기 전에 고를 수 없으므로**
# 기본은 "거르지 않고 표시만" 입니다 — 거르려면 등록하고 `--widom-max` 로 주십시오.
WIDOM_SANITY_MAX = 1.0          # mmol/g/Pa. 이보다 크면 '발산 의심' 으로 **표시**합니다.

# 순서 [CO2, N2] 에 대해 2026-09-20 에 모은 증거. **스키마 확인은 여전히 아닙니다** — 크기 논증입니다.
WIDOM_ORDER_EVIDENCE = """
  기체 이름은 배포본 어디에도 없습니다(zip 전체에서 "Widom" 2회, 둘 다 단위 문자열 'mmol/g/Pa').
  (a) 물이 아님:  같은 레코드의 water.GEMC(물 등온선, Henry 영역 확인된 626건)와 견주면
                  GEMC물/w0 중앙비 13.6(잔차 0.71 자릿수) · GEMC물/w1 중앙비 134(0.85) — 둘 다 물이 아닙니다.
  (b) 크기가 맞음: 우리 CO2 Widom K_H 217행(중앙 1.09e-04 mmol/g/Pa, 같은 단위)과
                  CoRE w0 중앙 6.4e-05 → **1.7배**,  CoRE w1 중앙 8.1e-06 → **13.5배**.
                  순서가 뒤라면 우리 32조성 전 범위가 CoRE CO2 중앙값 위에 놓여야 합니다 — 그럴 수 없습니다.
  (c) 비의 크기:  w0/w1 중앙 8.26 — CO2/N2 Henry 선택도의 통상 대역(5~50) 안. 뒤집으면 N2 가 CO2 의 8배가 됩니다.
  한계:  힘장이 다릅니다(CoRE UFF+TraPPE / 우리 UFF_MOF+Garcia-Sanchez 2009). 이것은 **자릿수 대조**이지 교정이 아닙니다.
         절대 확인은 CR CIF 몇 개에 CO2·N2 Widom 을 직접 돌려 저장값과 맞추는 것입니다(아직 안 함).
  또한 OMS 가 있으면 w0/w1 이 **줄어듭니다**(6.17 대 9.73) — 고전 힘장이 열린 금속 자리의 CO2 화학을 못 담기 때문으로
  보이며, 이 자료로 OMS 물질의 선택도를 논하지 말아야 할 이유입니다.
"""


def widom_pair(rec, *, co2_key="CO2", n2_key="N2"):
    """Widom 값을 **이름으로** 꺼냅니다.

    원본은 `widom[0]/widom[1]` 로 위치를 믿었습니다. CoRE 스키마가 리스트라면
    순서를 가정하는 대신 **가정했다는 사실을 돌려주어** 호출한 쪽이 검증하게 합니다.
    """
    # 옛 판은 `water` 블록 **안에** 들어 있습니다: water = {GEMC, water_classification, Widom}.
    # (그래서 노트북의 `iloc[:, 9]` 가 실제로는 `water` 열이고, 이름표만 `GEMC_data` 였습니다 — D1.)
    w = first_of(rec, ("water.Widom", "GEMC.Widom", "Widom"))
    if isinstance(w, dict):
        return w.get(co2_key), w.get(n2_key), "by-name"
    if isinstance(w, (list, tuple)) and len(w) >= 2:
        a, b = w[0], w[1]
        # CR 실측: 8,857 ASR 중 4건이 이 모양을 깹니다 — `[None, None]` 2건, `[{id: val}, {id: val}]` 2건.
        # 원본의 `widom[0]/widom[1]` 은 맨 except 에 먹혀 NaN 이 됩니다(D1+D2 합작).
        if isinstance(a, dict) and isinstance(b, dict):
            a, b = next(iter(a.values()), None), next(iter(b.values()), None)
            return a, b, "by-position(UNVERIFIED,unwrapped)"
        if a is None or b is None:
            raise Missing("Widom 값이 None")
        return a, b, "by-position(UNVERIFIED)"
    raise Missing("Widom")


def load_core(path, *, sets=("ASR", "FSR", "Ion")):
    """옛 판과 신 판을 둘 다 읽습니다.

    옛 판 `CR_meta_data_SI.json` : {mof_id: record, ...} 평평한 사전.
    신 판 `CoREMOF/data/CR.json` : {'unit': {...}, 'ASR': {...}, 'FSR': {...}, 'Ion': {...}}
        ASR = All Solvent Removed · FSR = Free Solvent Removed · Ion = 이온성.
        **셋은 같은 골격의 다른 정리판입니다** — 섞으면 한 물질이 여러 번 세어집니다.
        그래서 키에 계열을 붙여 돌려주고, 부르는 쪽이 계열을 나눌 수 있게 합니다.
    """
    with open(path, encoding="utf-8") as fh:
        raw = json.load(fh)
    if not isinstance(raw, dict):
        return {str(i): r for i, r in enumerate(raw)}
    if any(s in raw for s in sets):                      # 신 판
        out = {}
        for s in sets:
            for k, v in (raw.get(s) or {}).items():
                out[f"{s}/{k}"] = v
        return out
    return raw


def extract(core, *, gates=GATES):
    """관문 판정에 필요한 값만 뽑고, **못 뽑은 이유를 센다**(D2)."""
    rows, fails = [], collections.Counter()
    for key, rec in core.items():
        row = {"key": key}
        try:
            pld = first_of(rec, ("Zeopp.PLD", "PLD"))
            if pld is None:
                raise Missing("Zeopp.PLD | PLD")
            row["PLD"] = float(pld)
            row["LCD"] = float(first_of(rec, ("Zeopp.LCD", "LCD")) or 0.0)
            row["VF"] = float(first_of(rec, ("Zeopp.VF", "VF")) or 0.0)
            row["dimension"] = first_of(rec, ("Zeopp.dimension", "Dimension"))
        except (Missing, TypeError, ValueError) as exc:
            fails[f"Zeopp:{exc}"] += 1
            continue
        row["node"] = first_of(rec, ("CrystalNets.all_nodes", "Topology.AllNode"))
        if row["node"] is None:
            fails["all_nodes/AllNode 없음"] += 1
        row["water"] = first_of(rec, ("water.water_classification", "WaterClass"))
        if row["water"] is None:
            fails["water_classification/WaterClass 없음"] += 1
        try:
            kh_co2, kh_n2, how = widom_pair(rec)
            row["KH_CO2"], row["KH_N2"], row["widom_how"] = kh_co2, kh_n2, how
            row["selectivity"] = (kh_co2 / kh_n2) if (kh_co2 and kh_n2) else None
        except Missing:
            fails["Widom 없음"] += 1
            row["KH_CO2"] = row["KH_N2"] = row["selectivity"] = None
            row["widom_how"] = None
        rows.append(row)
    return rows, fails


def apply_gates(rows, gates=GATES):
    """관문을 **하나씩 따로** 세고, 교집합도 셉니다(원본 '병목 진단'의 정리판)."""
    g = gates["node_not_unstable"]
    unknown_ok = g.get("unknown_passes", True)

    def node_ok(r):
        a = r["node"]
        if a is None:
            return False
        if a in NODE_BAD:
            return False
        if a in NODE_UNKNOWN:
            return unknown_ok
        return True

    per = {
        "node_not_unstable": [r for r in rows if node_ok(r)],
        "PLD_min": [r for r in rows if r["PLD"] >= gates["PLD_min"]["value"]],
        "water_weak": [r for r in rows if r["water"] == gates["water_weak"]["value"]],
    }
    passed = [r for r in rows
              if node_ok(r)
              and r["PLD"] >= gates["PLD_min"]["value"]
              and r["water"] == gates["water_weak"]["value"]]
    return per, passed


def rank(rows, key, err_key=None, *, threshold=1.5):
    """오차 열이 있으면 **1.5배 규칙**으로 순위를 매기고, 없으면 순위를 거부합니다(D4).

    CLAUDE.md §2: "차이가 그 1.5배 미만이면 순위를 매기지 않습니다."
    """
    vals = [r for r in rows if r.get(key) is not None]
    vals.sort(key=lambda r: -r[key])
    if not err_key or any(r.get(err_key) is None for r in vals):
        return vals, ("순위 없음 — 오차 열이 없습니다. "
                      "점값 정렬만 돌려줍니다(CLAUDE.md §2: 오차 없이 순위 금지).")
    groups, cur = [], [vals[0]]
    for a, b in zip(vals, vals[1:]):
        d = a[key] - b[key]
        unit = (a[err_key] ** 2 + b[err_key] ** 2) ** 0.5
        if unit > 0 and d >= threshold * unit:
            groups.append(cur); cur = [b]
        else:
            cur.append(b)
    groups.append(cur)
    return groups, f"{len(groups)}덩어리 (문턱 {threshold}×합성 오차)"


def load_ours(path):
    with open(path, encoding="utf-8") as fh:
        d = json.load(fh)
    return d["rows"] if isinstance(d, dict) and "rows" in d else d


def place_ours(ours):
    """우리 조성을 **같은 관문·같은 창**에 넣어 어디 앉는지만 봅니다.

    ⚠ 순위는 안 매깁니다 — CoRE 값과 우리 값은 힘장·전하·프로토콜이 다른
    **다른 계열**입니다(CLAUDE.md §2 "버전을 넘나들며 인용하지 마세요" 의 확장).
    """
    out = {"n": len(ours)}
    out["PLD>=3.3"] = sum(1 for r in ours if (r.get("PLD") or 0) >= 3.3)
    out["PLD>=3.4"] = sum(1 for r in ours if (r.get("PLD") or 0) >= 3.4)
    lo, hi = WINDOWS_POST_HOC["N2_sieving"]["PLD"]
    out["N2_sieving_window"] = [r["name"] for r in ours if lo <= (r.get("PLD") or 0) <= hi]
    lo, hi = WINDOWS_POST_HOC["high_flux"]["PLD"]
    out["high_flux_window"] = [
        r["name"] for r in ours
        if lo <= (r.get("PLD") or 0) <= hi
        and (r.get("LCD") or 0) >= WINDOWS_POST_HOC["high_flux"]["LCD_min"]]
    plds = sorted((r.get("PLD") or 0) for r in ours)
    out["PLD_min_med_max"] = [plds[0], plds[len(plds) // 2], plds[-1]]
    return out


def main():
    ap = argparse.ArgumentParser(description="CoRE MOF 스크리닝 정리본")
    ap.add_argument("--meta", default=os.path.join(HERE, "data", "CR_meta_data_SI.json"))
    ap.add_argument("--ours", default=os.path.join(
        HERE, os.pardir, "21_ZIF69_MTV", "results_v3.json"))
    a = ap.parse_args()

    if os.path.exists(a.ours):
        ours = load_ours(a.ours)
        p = place_ours(ours)
        print(f"\n[우리 조성 {p['n']}개 — CoRE 관문에 얹어 보기]")
        print(f"  PLD >= 3.3  {p['PLD>=3.3']}/{p['n']}   ·   PLD >= 3.4  {p['PLD>=3.4']}/{p['n']}")
        print(f"  PLD 최소/중앙/최대  {p['PLD_min_med_max'][0]:.3f} / "
              f"{p['PLD_min_med_max'][1]:.3f} / {p['PLD_min_med_max'][2]:.3f}")
        print(f"  사후 창 'N2 sieving'(3.3~3.6)  {len(p['N2_sieving_window'])}개 {p['N2_sieving_window']}")
        print(f"  사후 창 'high flux'(3.7~4.2 & LCD>=5.5)  "
              f"{len(p['high_flux_window'])}개 {p['high_flux_window']}")
        groups, note = rank(ours, "selectivity", "selectivity_err")
        print(f"  선택도 순위: {note}")
        if isinstance(groups[0], list):
            for i, g in enumerate(groups[:4], 1):
                print(f"    {i}군: " + ", ".join(
                    f"{r['name']} {r['selectivity']:.1f}±{r['selectivity_err']:.1f}" for r in g))
    else:
        print(f"  (우리 자료 없음: {a.ours})")

    if not os.path.exists(a.meta):
        print(f"\n[CoRE 자료 없음] {a.meta}\n  data/MANIFEST.md 를 보고 내려받으십시오.")
        return 0
    core = load_core(a.meta)
    rows, fails = extract(core)
    per, passed = apply_gates(rows)
    print(f"\n[CoRE {len(core)}개]")
    for k, v in per.items():
        print(f"  {k:12s} {len(v)}개")
    print(f"  3중 관문 교집합  {len(passed)}개")

    # 원본의 사후 창 — **관문 대신** 쓰였습니다. 재현해서 나란히 보여 줍니다(D3·D6).
    w_n2 = WINDOWS_POST_HOC["N2_sieving"]["PLD"]
    w_hf = WINDOWS_POST_HOC["high_flux"]
    weak = [r for r in rows if r["water"] == GATES["water_weak"]["value"]]
    n2 = [r for r in weak if w_n2[0] <= r["PLD"] <= w_n2[1]]
    hf = [r for r in weak if w_hf["PLD"][0] <= r["PLD"] <= w_hf["PLD"][1]
          and (r.get("LCD") or 0) >= w_hf["LCD_min"]]
    print(f"  [사후 창 재현]  N2-Sieving(PLD {w_n2[0]}~{w_n2[1]} & weak) {len(n2)}개 · "
          f"High-Flux(PLD {w_hf['PLD'][0]}~{w_hf['PLD'][1]} & LCD>={w_hf['LCD_min']} & weak) {len(hf)}개")
    bad_n2 = [r for r in n2 if r["node"] in NODE_BAD]
    bad_hf = [r for r in hf if r["node"] in NODE_BAD]
    unk = [r for r in n2 + hf if r["node"] in NODE_UNKNOWN]
    print(f"    그중 뼈대 unstable/mismatch  N2 {len(bad_n2)}개 · HF {len(bad_hf)}개 · 위상 미상 {len(unk)}개"
          f"  ← 창은 뼈대를 안 봅니다(D6)")
    if fails:
        print("  못 뽑은 것(조용히 넘기지 않습니다):")
        for k, v in fails.most_common(8):
            print(f"    {v:6d}  {k}")
    hows = collections.Counter(r["widom_how"] for r in rows if r["widom_how"])
    npos = sum(v for k, v in hows.items() if k and k.startswith("by-position"))
    if npos:
        print(f"  ⚠ Widom 을 **위치로** 읽은 행 {npos}개 — 스키마에 기체 이름이 없습니다(D1).")
        print("    순서 [CO2, N2] 는 **크기로 지지**되지만 스키마 확인은 아닙니다:")
        print(WIDOM_ORDER_EVIDENCE.rstrip())
    return 0


if __name__ == "__main__":
    sys.exit(main())
