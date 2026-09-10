"""T-NF-0q 보충 — **우리 6조성의 물 K_H(Widom)를 이 기기에서** 돕니다.

등록: `TNF0Q_REGISTRATION_20260911.md` (05:10:35). **비교 (가)의 자료는 이 등록보다 뒤에 생깁니다** —
글자 그대로 "계산 전 등록" 이 성립합니다(외부 셋은 §0 대로 "읽기 전 등록" 이었습니다).

**왜 데스크탑 값을 안 쓰나**: ΔH 는 실행 폴더에서 나오는데 그쪽 폴더가 이 기기에 없습니다.
그리고 ΔΔG 와 ΔΔH 를 **같은 실행**에서 뽑아야 장부가 맞습니다 —
남의 K_H 와 제 ΔH 를 섞으면 잔차(−TΔΔS)에 기기 차가 들어갑니다.

**부수 효과**: 같은 조성을 두 기기가 돌게 되므로 `CAND_VERDICT §8-2-1` 처럼 **기기 간 대조**가 생깁니다.
그건 관찰이고 이 판의 판정 대상이 아닙니다.

`run_kh_ext.py` 를 import 해 **대상과 산출 경로만** 바꿉니다. 기본값을 두지 않습니다.

사용:  KHO_WORKERS=6 nice -n 5 ~/miniconda3/envs/czeromof/bin/python run_kh_ours.py
"""
import json, os, socket, sys
from multiprocessing import Pool

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import run_kh_ext as X                                        # noqa: E402
import run_tb2_water_kh as T                                  # noqa: E402
from ff_gate import md5_gate, FF_TAG                          # noqa: E402

# LPT 는 원자 수 순. 전부 2x2x2 라 크기 차가 작습니다.
X.FRAMEWORKS = ['saIm100', 'saIm050', 'nbIm050', 'mbIm050', 'base', 'mbIm025']
X.N_REP = 3
X.RUNS_ROOT = os.path.join(HERE, 'khours_runs')               # 외부 계열과 분리
X.OUT = os.path.join(HERE, 'v3w_water_kh_ours')
T.WORKERS = int(os.environ.get('KHO_WORKERS', 6))


def main():
    ok, _ = md5_gate()
    if not ok:
        print('!! 힘장 파일 관문 실패. 중단.', flush=True); return 2
    import subprocess
    if subprocess.run(['pgrep', '-x', 'simulate'], capture_output=True).returncode == 0:
        print('!! `simulate` 가 이미 돌고 있습니다. 중단.', flush=True); return 4
    for n in X.FRAMEWORKS:
        if not os.path.exists(os.path.join(T.CHARGED, n + '_DDEC6.cif')):
            print(f'!! CIF 없음: {n}', flush=True); return 3
    os.makedirs(X.OUT, exist_ok=True)
    jobs = [(i, n, rep) for i, (n, rep) in
            enumerate((n, rep) for n in X.FRAMEWORKS for rep in range(1, X.N_REP + 1))]
    print(f'T-NF-0q 보충 — 우리 {len(X.FRAMEWORKS)}조성 x 반복 {X.N_REP} = {len(jobs)}건, '
          f'워커 {T.WORKERS}\n  자: T-NF-0k 와 동일 (사이클 {T.CYCLES}/{T.INIT}, '
          f'{T.TEMP} K, 컷오프 {T.CUTOFF})\n  RUNS {X.RUNS_ROOT}\n  OUT  {X.OUT}', flush=True)
    rows = []
    with Pool(T.WORKERS) as p:
        for r in p.imap_unordered(X.one, jobs, chunksize=1):
            rows.append(r)
            print(f"  [{'ok' if r['ok'] else '실패'}] {r['name']:9s} r{r['rep']}  "
                  f"K_H {r['KH_water']}  ± {r['KH_water_err']}  씨앗 {r.get('raspa_seed')}",
                  flush=True)
    collide = {n: s for n in X.FRAMEWORKS
               if len(set(s := [x['raspa_seed'] for x in rows if x['name'] == n])) != len(s)}
    f = os.path.join(X.OUT, f'water_kh_ours_{socket.gethostname().lower()}.json')
    json.dump({'test': 'T-NF-0q 보충', 'registration': 'TNF0Q_REGISTRATION_20260911.md',
               'tag': socket.gethostname().lower(), 'forcefield': FF_TAG,
               'NumberOfInitializationCycles': T.INIT, 'NumberOfCycles': T.CYCLES,
               'temperature_K': T.TEMP, 'cutoff_A': T.CUTOFF,
               'note': ('우리 6조성을 랩탑에서 재실행. 데스크탑 water_kh_ALLw_hkhome_seedfixed 와 '
                        '**같은 조성의 다른 실행**입니다 — 합치지 마십시오. '
                        'ΔΔG 와 ΔΔH 를 같은 실행에서 뽑기 위한 것.'),
               'seed_collision': collide or None,
               'rows': sorted(rows, key=lambda x: (x['name'], x['rep']))},
              open(f, 'w'), ensure_ascii=False, indent=2)
    nok = sum(1 for r in rows if r['ok'])
    print(f"\n[OK] {nok}/{len(jobs)} -> {f}", flush=True)
    print(f"  씨앗: {'**충돌 ' + str(collide) + '**' if collide else '조성 안에서 전부 다름'}", flush=True)
    return 0 if nok == len(jobs) else 1


if __name__ == '__main__':
    sys.exit(main())
