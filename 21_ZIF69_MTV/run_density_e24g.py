"""밀도맵 E-28d — E-24g · E-24h 새 치환체 건조 CO₂ 격자, 전하 ON/OFF (2026-09-26). 등록 `ASSIGN_MAGI5B_20260925.md` §HKHOME 21차 후속 E-28d.
`run_density_tpl2.py`(E-28b) 사본 — 바꾼 것: 대상(DENSITY_E24G_TARGETS, 쉼표) · 출력 폴더 density_v3_tpl3/<DENSITY_E24G_SUB> · 막음 파일
(주머니 있는 e24h_c2h5_050a · b 만, Junseok Zeo++ `e24g_zeo_runs/<tag>/block1.65/`). 규약 · 막음 삽입 · 관문은 원판 그대로. 원판 머리말:
밀도맵 E-28b — 새 상위 후보 −Cl(규칙 1위) · −C₂H₅(앞단 강건 1위, **막음**) 건조 CO₂ 격자, 전하 ON/OFF (2026-09-26).

`run_density_tpl.py`(E-28) 와 같은 방식 — `run_density_map` **수정 없이** import, 경로 · 덱만 옮김. 규약 그대로(0.15 bar · 298 K ·
2,000+5,000 · 90³ · DDEC6 · ON/OFF). 바꾼 것 하나: **C₂H₅ 는 닿지 않는 주머니가 있어(E-24c ①) CO₂ 성분에 BlockPockets**
(`e28b_blocks/e24c_c2h5_100_block1.65.block` = Junseok `e24c_zeo_runs/e24c_c2h5_100/block1.65/`, 구 2 × 셀 6 = 12) —
E-24b 판정의 뜻 · E-24c · E-24e 와 같은 막음. `write_input` 을 감싸 성분 절에 두 줄을 넣고 막음 파일을 실행 폴더로 복사.
관문(실행 뒤, 판정 전): 출력에 'Blocking-pocket' file not found 없음 · 막힌 구 수 12(ON · OFF 각각).
등록 `ASSIGN_MAGI5B_20260925.md` §HKHOME 19차 E-28b.
"""
import os
import shutil
import sys

import run_density_map as rd

REAL = os.path.dirname(os.path.abspath(__file__))
OUTD = os.path.join(REAL, "density_v3_tpl3", os.environ.get("DENSITY_E24G_SUB", ""))
os.makedirs(OUTD, exist_ok=True)
rd.HERE = OUTD
rd.OUT = OUTD
rd.CHARGED = os.path.join(REAL, "charged_v3")
rd.MAX_WORKERS = int(os.environ.get("DENSITY_E24G_WORKERS", "4"))
rd.TARGETS = [x for x in os.environ.get("DENSITY_E24G_TARGETS", "").split(",") if x]
BLOCK = {f"{k}_DDEC6": os.path.join(REAL, "e24g_zeo_runs", k, "block1.65", f"{k}_relaxed.block") for k in ("e24h_c2h5_050a", "e24h_c2h5_050b") if k in rd.TARGETS}
ANCHOR = "Component 0 MoleculeName              CO2\n            MoleculeDefinition        TraPPE\n"
_real_write = rd.write_input


def write_input(d, name, na, nb, nc, charges):
    _real_write(d, name, na, nb, nc, charges)
    if name in BLOCK:
        p = os.path.join(d, "simulation.input")
        s = open(p).read()
        assert s.count(ANCHOR) == 1, "성분 절 앵커가 정확히 한 번이 아님 — 막음 삽입 중단"
        s = s.replace(ANCHOR, ANCHOR + f"            BlockPockets              yes\n            BlockPocketsFileName      {name}\n")
        open(p, "w").write(s)
        shutil.copy(BLOCK[name], os.path.join(d, name + ".block"))


rd.write_input = write_input

if __name__ == "__main__":
    print(f"밀도맵 E-28d 건조 — {rd.TARGETS} · 막음 {list(BLOCK)}", flush=True)
    if not rd.TARGETS:
        print("  !! DENSITY_E24G_TARGETS 비어 있음", flush=True); sys.exit(2)
    for t in rd.TARGETS:
        if not os.path.exists(os.path.join(rd.CHARGED, t + "_DDEC6.cif")):
            print("  !! 전하 CIF 없음", t, flush=True); sys.exit(2)
    for k, v in BLOCK.items():
        if not os.path.exists(v):
            print("  !! 막음 파일 없음", v, flush=True); sys.exit(2)
    sys.exit(rd.main())
