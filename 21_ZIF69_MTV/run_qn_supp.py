# -*- coding: utf-8 -*-
"""§AS (가) Q_st(n) **§-보완** 러너 — 저피복 점(0.01 · 0.02 bar) 36+6작업.

등록 `QSTN_SUPP_REGISTRATION_20260924.md`(자료 0건 09-24 14:2x). 식·고정값은 §AS 와 같고
**압력 두 점만 더합니다.** 한 조성의 여섯 점은 **한 기기**에서 나와야 합니다(§1-1) —
`Q_st` 가 세 온도의 기울기이므로 온도를 기기에 걸쳐 나누면 기기 항이 기울기에 들어갑니다.

    python run_qn_supp.py --only base,saIm025,saIm050            # Junseok
    python run_qn_supp.py --only mslm050,sa50nb50,saIm0583,base  # laptop2 (base 는 §1-2 교차)

이어받기: 결과 JSON 이 있고 **그 안의 `CO2_molkg` 가 null 이 아닐 때만** `cached`.
**파일 존재만으로 건너뛰지 않습니다** — 09-21 `RESUME_ANY_BUG` 와 같은 무늬를 막습니다.
(`run_tnf.py` 자체가 `finished()` 로 'Simulation finished' 를 요구하므로, 표지가 없으면
그 행의 `CO2_molkg` 가 null 로 남습니다.)
"""
import argparse, json, os, subprocess, sys, time
from concurrent.futures import ThreadPoolExecutor, as_completed

# 선행 검사 — `run_tnf.py` 를 **이 파이썬으로** 띄우므로 여기서 numpy 가 되면 자식도 됩니다.
# (09-24 데스크탑 예행에서 conda 밖 python3 로 띄워 42작업이 전부 rc=1 로 탈 뻔했습니다.
#  빨리·크게 죽는 것이 조용히 다 실패하는 것보다 낫습니다.)
try:
    import numpy  # noqa: F401
except ImportError:
    sys.exit('numpy 가 없습니다 — `run_tnf.py` 가 이 파이썬(%s)으로 뜹니다.\n'
             'conda 환경(czeromof 류)의 python 으로 다시 띄우십시오.' % sys.executable)

HERE = os.path.dirname(os.path.abspath(__file__))
FF_MD5 = '8e8ec933f9013c7e932da04dc256efd3'          # 등록 §1 — 기존 72건과 같은 값
TEMPS = [283.0, 298.0, 313.0]
PRESS = [0.01, 0.02]                                  # ← §-보완이 더하는 두 점
ALL = ['base', 'mslm050', 'sa50nb50', 'saIm025', 'saIm050', 'saIm0583']


def tag_of(c, T, p):
    return 'qn_%s_%dK_%.2fbar' % (c, int(T), p)


def out_of(c, T, p):
    return os.path.join(HERE, 'tnf_results_%s.json' % tag_of(c, T, p))


def done(path):
    """완주 판정 — **값이 아니라 표지가 자입니다**(CLAUDE.md §0)."""
    try:
        rows = json.load(open(path, encoding='utf-8'))
    except Exception:
        return False
    if not isinstance(rows, list) or not rows:
        return False
    return all(r.get('CO2_molkg') is not None for r in rows)


def run_one(job):
    c, T, p = job
    out = out_of(c, T, p)
    if done(out):
        return c, T, p, 'cached', 0.0
    cif = os.path.join(HERE, 'charged_v3', '%s_DDEC6.cif' % c)
    if not os.path.exists(cif):
        return c, T, p, 'CIF 없음', 0.0
    t0 = time.time()
    r = subprocess.run(
        [sys.executable, os.path.join(HERE, 'run_tnf.py'),
         '--cif', cif, '--tag', tag_of(c, T, p),
         '--temp', str(T), '--pco2', str(p), '--rh', '0', '--workers', '1'],
        cwd=HERE, capture_output=True, text=True)
    dt = (time.time() - t0) / 60.0
    if not done(out):                                  # rc 를 믿지 않습니다 — 출력을 봅니다
        tail = (r.stderr or r.stdout or '')[-300:].replace('\n', ' ')
        return c, T, p, '미완주 rc=%d %s' % (r.returncode, tail), dt
    return c, T, p, 'ok', dt


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--only', default=','.join(ALL), help='조성 쉼표 구분')
    ap.add_argument('--workers', type=int,
                    default=int(os.environ.get('QN_SUPP_WORKERS', '6')))
    a = ap.parse_args()
    comps = [c.strip() for c in a.only.split(',') if c.strip()]
    bad = [c for c in comps if c not in ALL]
    if bad:
        sys.exit('등록 밖 조성: %s (등록 §1 은 %s)' % (bad, ALL))

    # ⚠ `RASPA_DIR` 은 **`share/raspa` 의 부모**입니다(예: `$HOME/RASPA/simulations`).
    #   09-24 데스크탑이 한 단계 깊게 줘서 172구조가 3분 만에 전부 `[no-output]` 이 났고,
    #   laptop2 는 변수 자체가 비어 여기서 막혔습니다. **막되 고치는 법을 알려 줍니다.**
    rd = os.environ.get('RASPA_DIR', '')
    ffp = os.path.join(rd, 'share', 'raspa',
                       'forcefield', 'UFF_MOF', 'force_field_mixing_rules.def')
    import hashlib
    if not os.path.exists(ffp):
        hint = ''
        for c in (os.path.join(os.path.expanduser('~'), 'RASPA', 'simulations'),
                  os.path.join(os.path.expanduser('~'), 'RASPA')):
            if os.path.exists(os.path.join(c, 'share', 'raspa', 'forcefield',
                                           'UFF_MOF', 'force_field_mixing_rules.def')):
                hint = '\n이 기기에서 맞는 값은 이것으로 보입니다:  export RASPA_DIR=%s' % c
                break
        sys.exit('힘장 파일 없음: %s\n'
                 'RASPA_DIR=%r — **`share/raspa` 의 부모**를 주십시오(한 단계 깊게 주면 안 됩니다).%s'
                 % (ffp, rd, hint))
    m = hashlib.md5(open(ffp, 'rb').read()).hexdigest()
    if m != FF_MD5:
        sys.exit('힘장 관문 실패: %s != %s (등록 §1)' % (m, FF_MD5))
    print('힘장 관문 통과  %s  (RASPA_DIR=%s)' % (m, rd), flush=True)

    jobs = [(c, T, p) for c in comps for T in TEMPS for p in PRESS]
    print('§-보완  조성 %d · 온도 %d · 압력 %s → %d작업 · 워커 %d'
          % (len(comps), len(TEMPS), PRESS, len(jobs), a.workers), flush=True)
    n_ok = n_cache = n_bad = 0
    with ThreadPoolExecutor(max_workers=a.workers) as ex:
        futs = {ex.submit(run_one, j): j for j in jobs}     # submit+as_completed (§5)
        for i, f in enumerate(as_completed(futs), 1):
            c, T, p, st, dt = f.result()
            if st == 'ok':
                n_ok += 1
            elif st == 'cached':
                n_cache += 1
            else:
                n_bad += 1
            print('[%2d/%d] %-10s %3dK %.2fbar  %-10s %5.1f min'
                  % (i, len(jobs), c, int(T), p, st, dt), flush=True)
    print('\n완주 %d · cached %d · 실패 %d' % (n_ok, n_cache, n_bad), flush=True)
    sys.exit(1 if n_bad else 0)


if __name__ == '__main__':
    main()
