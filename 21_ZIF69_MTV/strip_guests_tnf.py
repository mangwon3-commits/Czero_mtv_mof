#!/usr/bin/env python
"""T-NF 앞단 0.5단계 — **게스트(용매) 조각 제거** (2026-09-19 신설, MUF-16 Co as-synth 용).

등록 `TNF_REGISTRATION_20260910.md §1` 의 "Co 진공 판이 없으면 as-synth 에서 게스트 물
제거; 배위·구조 N–H/COOH 는 유지" 단계입니다. `external_cif/PROVENANCE.md` 09-18 절이
적은 대로 CCDC 1948901 은 **이수화물**(moiety `0.5(C32 H24 Co2 N4 O16), 2(H2O)`)이고
게스트는 O15·O16(+H16A·H16B) 입니다.

## 무엇을 하나 — 감사기의 판정 기준을 그대로 씁니다
`audit_external_cif.guests()` 가 "금속에 닿지 않는 연결성분 = 게스트 후보" 로 세는
그 연결성분 분해를 **똑같이** 돌려, 금속이 없는 성분을 전부 뺍니다. 새 기준을 만들지
않습니다. 그 함수는 후보만 알려 주고 지우지는 않기 때문에 이 파일이 있습니다.

## 손으로 유도하지 않고 확인합니다
지운 뒤 남은 조성이 **기대 골격 조성**과 정확히 같아야 씁니다. 기대값은 SI 의 실험식
(C16H12MnN2O8 의 Co 판 = C16 H12 Co N2 O8, Z=4)에서 오고, 결과 CIF 를 ase 로 다시 읽어
원소별 개수를 셉니다(빌더 규율 — `build_ensemble_025.py` 와 같은 방식). 하나라도 어긋나면
**아무것도 쓰지 않고** 0 이 아닌 값으로 끝납니다.

⚠️ 점유율 0.5 인 O16 은 ase 가 대칭 전개하며 **전부 실재 원자로** 만듭니다(점유율 무시,
CLAUDE.md 08-15 ZIF-67 사고 그대로). 그래서 P1 사본의 물이 12개(4+8)로 보이고, 골격만
남기면 그 문제가 같이 사라집니다. 골격 원자는 전부 점유 1 입니다(PROVENANCE 09-18).

사용:
    python strip_guests_tnf.py --cif external_cif/MUF-16_Co_assynth_CCDC1948901_P1.cif \
        --out external_cif/MUF-16_Co_activated_P1.cif --expect C64H48Co4N8O32
"""
import argparse
import collections
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)


def parse_formula(s):
    import re
    out = collections.Counter()
    for el, n in re.findall(r"([A-Z][a-z]?)(\d*)", s):
        out[el] += int(n) if n else 1
    return dict(out)


def main():
    ap = argparse.ArgumentParser(description="금속에 닿지 않는 연결성분(게스트)을 제거한 CIF 를 쓴다")
    ap.add_argument("--cif", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--expect", required=True, help="기대 골격 조성, 예 C64H48Co4N8O32")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()

    from ase.io import read, write
    from ase.neighborlist import neighbor_list
    import audit_external_cif as AU

    atoms = read(a.cif)
    syms = atoms.get_chemical_symbols()
    uniq = sorted(set(syms))
    missing = [s for s in uniq if s not in AU.COV]
    if missing:
        print("!! 공유결합 반지름 표에 없는 원소:", missing); return 2
    cut = {(x, y): 1.25 * (AU.COV[x] + AU.COV[y]) for x in uniq for y in uniq}
    i, j = neighbor_list("ij", atoms, cut)
    n = len(atoms); parent = list(range(n))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]; x = parent[x]
        return x
    for p, q in zip(i, j):
        rp, rq = find(int(p)), find(int(q))
        if rp != rq: parent[rp] = rq
    comp = collections.defaultdict(list)
    for x in range(n): comp[find(x)].append(x)

    keep, drop = [], []
    for members in comp.values():
        if any(syms[m] in AU.METALS for m in members): keep += members
        else: drop.append(members)
    dropped = collections.Counter()
    for m in drop:
        f = "".join(f"{e}{c}" for e, c in sorted(collections.Counter(syms[x] for x in m).items()))
        dropped[f] += 1
    print(f"  입력 {n} 원자, 연결성분 {len(comp)}개, 금속 없는 성분 {len(drop)}개 제거: {dict(dropped)}")

    fw = atoms[sorted(keep)]
    got = dict(collections.Counter(fw.get_chemical_symbols()))
    exp = parse_formula(a.expect)
    print(f"  남은 골격 {len(fw)} 원자: {got}")
    print(f"  기대       {sum(exp.values())} 원자: {exp}")
    if got != exp:
        print("  !! 조성 불일치 — 쓰지 않습니다."); return 1
    d = neighbor_list("d", fw, 1.5)
    dmin = float(d.min()) if len(d) else float("inf")
    print(f"  최소 원자간 거리 {dmin:.3f} Å (riding X-H 0.82~0.95 는 정상)")
    if dmin < 0.75:
        print("  !! 0.75 Å 미만 쌍이 있습니다 — 겹침 의심, 쓰지 않습니다."); return 1
    if a.dry_run:
        print("  --dry-run: 쓰지 않았습니다."); return 0
    write(a.out, fw)
    chk = read(a.out)
    got2 = dict(collections.Counter(chk.get_chemical_symbols()))
    if got2 != exp:
        os.remove(a.out); print("  !! 다시 읽은 조성이 다릅니다 — 파일 삭제"); return 1
    print(f"  [OK] {a.out}  ({len(chk)} 원자, 다시 읽어 조성 확인)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
