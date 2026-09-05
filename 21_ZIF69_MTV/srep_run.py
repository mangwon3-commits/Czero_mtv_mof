"""실행 간 산포 s_rep — base / saIm100 x {CO2, N2} x 5 실현 = 20건.

배정: ASSIGN_LAPTOP2_20260905_SREP.md (데스크탑 9c1a05b, 측정 전 등록).

**폴더 겹침을 피하는 방법**: run_aryl_gcmc.run_one 은 폴더를
`{mode}_{gas}_{cif이름}` 으로 짓고 **끝난 실행을 캐시로 돌려준다.** 같은 구조를
5번 돌리면 5번 다 같은 폴더로 가고 캐시가 첫 결과를 다섯 번 준다 — 09-05 새벽에
당한 세 겹침과 같은 부류다.
그래서 **CIF 를 실현마다 다른 이름으로 복사**한다(`base_r1.cif` ...). 내용은
동일하고 이름만 다르므로 구조·덱은 그대로이고 **폴더만 갈린다.**

사용:  python srep_run.py <구조> <기체> <실현번호>     예: base CO2 1
       인자 없으면 20건 목록만 인쇄(안 돈다).
"""
import os, sys, shutil, time, json

HERE = "/home/leehk/mof_project/21_ZIF69_MTV"
sys.path.insert(0, HERE)
os.chdir(HERE)
import run_aryl_gcmc as rg

STRUCTS = ("base", "saIm100")
GASES = ("CO2", "N2")
REPS = (1, 2, 3, 4, 5)
SRC = os.path.join(HERE, "charged_v3")
STAGE = os.path.join(HERE, "srep_cifs")


def stage_cif(name, rep):
    """같은 구조를 실현별 이름으로 복사 — 폴더 갈림 용도."""
    os.makedirs(STAGE, exist_ok=True)
    src = os.path.join(SRC, f"{name}_DDEC6.cif")
    if not os.path.exists(src):
        raise SystemExit(f"CIF 없음: {src}")
    dst = os.path.join(STAGE, f"{name}_r{rep}_DDEC6.cif")
    if not os.path.exists(dst):
        shutil.copy(src, dst)
    return dst


def main():
    if len(sys.argv) < 4:
        print("20건 목록 (안 돕니다):")
        for s in STRUCTS:
            for g in GASES:
                for r in REPS:
                    print(f"  {s:<8} {g:<4} r{r}   -> "
                          f"aryl_runs/widom_{g}_{s}_r{r}_DDEC6")
        print("\n실행:  python srep_run.py <구조> <기체> <실현>")
        return
    name, gas, rep = sys.argv[1], sys.argv[2], int(sys.argv[3])
    cif = stage_cif(name, rep)
    tag = f"{name}_r{rep}_DDEC6"
    d = os.path.join(rg.RUNS, f"widom_{gas}_{tag}")
    print(f"[시작] {name} {gas} r{rep}", flush=True)
    print(f"  CIF   {cif}", flush=True)
    print(f"  출력  **{d}**", flush=True)   # 의도가 아니라 산출물 경로를 찍는다
    t0 = time.time()
    nm, g_, mode, r_, st = rg.run_one((cif, gas, "widom"))
    dt = time.time() - t0
    kh, ekh = (r_[0], r_[1]) if r_ else (None, None)
    print(f"[끝] {st}  {dt/60:.1f}분   K_H = {kh} +- {ekh}", flush=True)
    out = os.path.join(HERE, "srep_results")
    os.makedirs(out, exist_ok=True)
    with open(os.path.join(out, f"{name}_{gas}_r{rep}.json"), "w") as f:
        json.dump({"struct": name, "gas": gas, "rep": rep, "dir": d,
                   "status": st, "kh": kh, "kh_err": ekh,
                   "minutes": round(dt / 60, 2)}, f, ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()
